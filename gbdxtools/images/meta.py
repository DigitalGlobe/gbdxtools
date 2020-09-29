import os
import random
from functools import partial
from itertools import product
from collections import namedtuple
from collections.abc import Container

from gbdxtools.rda.io import to_geotiff
from gbdxtools.rda.util import RatPolyTransform, AffineTransform, pad_safe_positive, pad_safe_negative, RDA_TO_DTYPE, get_proj
from gbdxtools.images.mixins import PlotMixin, BandMethodsTemplate, Deprecations

from shapely import ops, wkt
from shapely.geometry import box, shape, mapping, asShape
from shapely.geometry.base import BaseGeometry

import pyproj
import dask
from dask import optimization
from dask.delayed import delayed
import dask.array as da
import numpy as np

from affine import Affine

threads = int(os.environ.get('GBDX_THREADS', 8))
threaded_get = partial(dask.threaded.get, num_workers=threads)

class DaskMeta(namedtuple("DaskMeta", ["dask", "name", "chunks", "dtype", "shape"])):
    __slots__ = ()
    @classmethod
    def from_darray(cls, darr, new=tuple.__new__, len=len):
        dsk, _ = optimization.cull(darr.dask, darr.__dask_keys__())
        itr = [dsk, darr.name, darr.chunks, darr.dtype, darr.shape]
        return cls._make(itr)

    @property
    def values(self):
        return self._asdict().values()

class DaskImage(da.Array):
    """
    A DaskImage is a 2 or 3 dimension dask array that contains implements the `__daskmeta__` interface.
    """
    def __new__(cls, dm, **kwargs):
        if isinstance(dm, da.Array):
            dm = DaskMeta.from_darray(dm)
        elif isinstance(dm, dict):
            dm = DaskMeta(**dm)
        elif isinstance(dm, DaskMeta):
            pass
        elif dm.__class__.__name__ in ("Op", "GraphMeta", "TmsMeta", "TemplateMeta"):
            itr = [dm.dask, dm.name, dm.chunks, dm.dtype, dm.shape]
            dm = DaskMeta._make(itr)
        else:
            raise ValueError("{} must be initialized with a DaskMeta, a dask array, or a dict with DaskMeta fields".format(cls.__name__))
        self = da.Array.__new__(cls, dm.dask, dm.name, dm.chunks, dtype=dm.dtype, shape=dm.shape)
        if "__geo_transform__" in kwargs:
            self.__geo_transform__ = kwargs["__geo_transform__"]
        if "__geo_interface__" in kwargs:
            self.__geo_interface__ = kwargs["__geo_interface__"]
        return self

    @property
    def __daskmeta__(self):
        return DaskMeta(self)

    def read(self, bands=None, **kwargs):
        """Reads data from a dask array and returns the computed ndarray matching the given bands

        Args:
            bands (list): band indices to read from the image. Returns bands in the order specified in the list of bands.

        Returns:
            ndarray: a numpy array of image data
        """
        arr = self
        if bands is not None:
            arr = self[bands, ...]
        return arr.compute(scheduler=threaded_get)

    def randwindow(self, window_shape):
        """Get a random window of a given shape from within an image

        Args:
            window_shape (tuple): The desired shape of the returned image as (height, width) in pixels.

        Returns:
            image: a new image object of the specified shape and same type
        """
        row = random.randrange(window_shape[0], self.shape[1])
        col = random.randrange(window_shape[1], self.shape[2])
        return self[:, row-window_shape[0]:row, col-window_shape[1]:col]

    def iterwindows(self, count=64, window_shape=(256, 256)):
        """ Iterate over random windows of an image

        Args:
            count (int): the number of the windows to generate. Defaults to 64, if `None` will continue to iterate over random windows until stopped.
            window_shape (tuple): The desired shape of each image as (height, width) in pixels.

        Yields:
            image: an image of the given shape and same type.
        """
        if count is None:
            while True:
                yield self.randwindow(window_shape)
        else:
            for i in range(count):
                yield self.randwindow(window_shape)

    def window_at(self, geom, window_shape):
        """Return a subsetted window of a given size, centered on a geometry object

        Useful for generating training sets from vector training data
        Will throw a ValueError if the window is not within the image bounds

        Args:
            geom (shapely,geometry): Geometry to center the image on
            window_shape (tuple): The desired shape of the image as (height, width) in pixels.

        Returns:
            image: image object of same type
        """
        # Centroids of the input geometry may not be centered on the object.
        # For a covering image we use the bounds instead.
        # This is also a workaround for issue 387.
        y_size, x_size = window_shape[0], window_shape[1]
        bounds = box(*geom.bounds)
        px = ops.transform(self.__geo_transform__.rev, bounds).centroid
        miny, maxy = int(px.y - y_size/2), int(px.y + y_size/2)
        minx, maxx = int(px.x - x_size/2), int(px.x + x_size/2)
        _, y_max, x_max = self.shape
        if minx < 0 or miny < 0 or maxx > x_max or maxy > y_max:
            raise ValueError("Input geometry resulted in a window outside of the image")
        return self[:, miny:maxy, minx:maxx]

    def window_cover(self, window_shape, pad=True):
        """ Iterate over a grid of windows of a specified shape covering an image.

        The image is divided into a grid of tiles of size window_shape. Each iteration returns
        the next window.


        Args:
            window_shape (tuple): The desired shape of each image as (height,
                width) in pixels.
            pad: (bool): Whether or not to pad edge cells. If False, cells that do not
                have the desired shape will not be returned. Defaults to True.

        Yields:
            image: image object of same type.
        """
        size_y, size_x = window_shape[0], window_shape[1]
        _ndepth, _nheight, _nwidth = self.shape
        nheight, _m = divmod(_nheight, size_y)
        nwidth, _n = divmod(_nwidth, size_x)

        img = self
        if pad is True:
            new_height, new_width = _nheight, _nwidth
            if _m != 0:
                new_height = (nheight + 1) * size_y
            if _n != 0:
                new_width = (nwidth + 1) * size_x
            if (new_height, new_width) != (_nheight, _nwidth):
                bounds = box(0, 0, new_width, new_height)
                geom = ops.transform(self.__geo_transform__.fwd, bounds)
                img = self[geom]

        row_lims = range(0, img.shape[1], size_y)
        col_lims = range(0, img.shape[2], size_x)
        for maxy, maxx in product(row_lims, col_lims):
            reg = img[:, maxy:(maxy + size_y), maxx:(maxx + size_x)]
            if pad is False:
                if reg.shape[1:] == window_shape:
                    yield reg
            else:
                yield reg



class GeoDaskImage(DaskImage, Container, PlotMixin, BandMethodsTemplate, Deprecations):
    _default_proj = "EPSG:4326"

    def map_blocks(self, *args, **kwargs):
        ''' Queue a deferred function to run on each block of image

        This is identical to Dask's map_block functinos, but returns a GeoDaskImage to preserve
        the geospatial information.

        Args: see dask.Array.map_blocks

        Returns:
            GeoDaskImage: a dask array with the function queued up to run when the image is read
        '''

        darr = super(GeoDaskImage, self).map_blocks(*args, **kwargs)
        return GeoDaskImage(darr, __geo_interface__ = self.__geo_interface__,
                            __geo_transform__ = self.__geo_transform__)

    def rechunk(self, *args, **kwargs):
        darr = super(GeoDaskImage, self).rechunk(*args, **kwargs)
        return GeoDaskImage(darr, __geo_interface__ = self.__geo_interface__,
                            __geo_transform__ = self.__geo_transform__)

    def asShape(self):
        return asShape(self)

    @property
    def affine(self):
        """ The geo transform of the image

        Returns:
            dict: The image's affine transform
        """
        # TODO add check for Ratpoly or whatevs
        return self.__geo_transform__._affine

    @property
    def bounds(self):
        """ Access the spatial bounding box of the image

        Returns:
            list: list of bounds in image projected coordinates (minx, miny, maxx, maxy)
        """
        return shape(self).bounds

    @property
    def proj(self):
        """ The projection of the image """
        # keep EPSG code strings upper case
        return self.__geo_transform__.proj.replace('epsg', 'EPSG')

    def aoi(self, **kwargs):
        """ Subsets the Image by the given bounds

        Args:
            bbox (list): optional. A bounding box array [minx, miny, maxx, maxy]
            wkt (str): optional. A WKT geometry string
            geojson (str): optional. A GeoJSON geometry dictionary

        Returns:
            image: an image instance of the same type
        """
        g = self._parse_geoms(**kwargs)
        if g is None:
            return self
        else:
            return self[g]

    def pxbounds(self, geom, clip=False):
        """ Returns the bounds of a geometry object in pixel coordinates

        Args:
            geom: Shapely geometry object or GeoJSON as Python dictionary or WKT string
            clip (bool): Clip the bounds to the min/max extent of the image

        Returns:
            list: bounds in pixels [min x, min y, max x, max y] clipped to image bounds
        """

        try:
            if isinstance(geom, dict):
                if 'geometry' in geom:
                    geom = shape(geom['geometry'])
                else:
                    geom = shape(geom)
            elif isinstance(geom, BaseGeometry):
                geom = shape(geom)
            else:
                geom = wkt.loads(geom)
        except:
            raise TypeError ("Invalid geometry object")

        # if geometry doesn't overlap the image, return an error
        if geom.disjoint(shape(self)):
            raise ValueError("Geometry outside of image bounds")
        # clip to pixels within the image
        (xmin, ymin, xmax, ymax) = ops.transform(self.__geo_transform__.rev, geom).bounds
        _nbands, ysize, xsize = self.shape
        if clip:
            xmin = max(xmin, 0)
            ymin = max(ymin, 0)
            xmax = min(xmax, xsize)
            ymax = min(ymax, ysize)

        return (xmin, ymin, xmax, ymax)

    def geotiff(self, **kwargs):
        """ Creates a geotiff on the filesystem

        Args:
            path (str): optional, path to write the geotiff file to, default is ./output.tif
            proj (str): optional, EPSG string of projection to reproject to
            spec (str): optional, if set to 'rgb', write out color-balanced 8-bit RGB tif
            bands (list): optional, list of bands to export. If spec='rgb' will default to RGB bands,
                otherwise will export all bands

        Returns:
            str: path the geotiff was written to """

        if 'proj' not in kwargs:
            kwargs['proj'] = self.proj
        return to_geotiff(self, **kwargs)

    def _parse_geoms(self, **kwargs):
        """ Finds supported geometry types, parses them and returns the bbox """
        bbox = kwargs.get('bbox', None)
        wkt_geom = kwargs.get('wkt', None)
        geojson = kwargs.get('geojson', None)
        if bbox is not None:
            g = box(*bbox)
        elif wkt_geom is not None:
            g = wkt.loads(wkt_geom)
        elif geojson is not None:
            g = shape(geojson)
        else:
            return None
        if self.proj is None:
            return g
        else:
            return self._reproject(g, from_proj=kwargs.get('from_proj', 'EPSG:4326'))

    def _reproject(self, geometry, from_proj=None, to_proj=None):
        if from_proj is None:
            from_proj = self._default_proj
        if to_proj is None:
            to_proj = self.proj if self.proj is not None else "EPSG:4326"
        tfm = pyproj.Transformer.from_crs(get_proj(from_proj), get_proj(to_proj), always_xy=True)
        return ops.transform(tfm.transform, geometry)

    def _slice_padded(self, _bounds):
        pads = (max(-_bounds[0], 0), max(-_bounds[1], 0),
                max(_bounds[2]-self.shape[2], 0), max(_bounds[3]-self.shape[1], 0))
        bounds = (max(_bounds[0], 0),
                  max(_bounds[1], 0),
                  max(min(_bounds[2], self.shape[2]), 0),
                  max(min(_bounds[3], self.shape[1]), 0))
        result = self[:, bounds[1]:bounds[3], bounds[0]:bounds[2]]
        if pads[0] > 0:
            dims = (result.shape[0], result.shape[1], pads[0])
            result = da.concatenate([da.zeros(dims, chunks=dims, dtype=result.dtype),
                                     result], axis=2)
        if pads[2] > 0:
            dims = (result.shape[0], result.shape[1], pads[2])
            result = da.concatenate([result,
                                     da.zeros(dims, chunks=dims, dtype=result.dtype)], axis=2)
        if pads[1] > 0:
            dims = (result.shape[0], pads[1], result.shape[2])
            result = da.concatenate([da.zeros(dims, chunks=dims, dtype=result.dtype),
                                     result], axis=1)
        if pads[3] > 0:
            dims = (result.shape[0], pads[3], result.shape[2])
            result = da.concatenate([result,
                                     da.zeros(dims, chunks=dims, dtype=result.dtype)], axis=1)

        return (result, _bounds[0], _bounds[1])

    def __contains__(self, g):
        geometry = ops.transform(self.__geo_transform__.rev, g)
        img_bounds = box(0, 0, *self.shape[2:0:-1])
        return img_bounds.contains(geometry)

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            g = shape(geometry)
            if g.disjoint(shape(self)):
                raise ValueError("AOI does not intersect image: {} not in {}".format(g.bounds, self.bounds))
            bounds = ops.transform(self.__geo_transform__.rev, g).bounds
            result, xmin, ymin = self._slice_padded(bounds)
        else:
            if len(geometry) == 1:
                assert geometry[0] == Ellipsis
                return self

            elif len(geometry) == 2:
                arg0, arg1 = geometry
                if isinstance(arg1, slice):
                    assert arg0 == Ellipsis
                    return self[:, :, arg1.start:arg1.stop]
                elif arg1 == Ellipsis:
                    return self[arg0, :, :]

            elif len(geometry) == 3:
                try:
                    nbands, ysize, xsize = self.shape
                except:
                    ysize, xsize = self.shape
                band_idx, y_idx, x_idx = geometry
                if y_idx == Ellipsis:
                    y_idx = slice(0, ysize)
                if x_idx == Ellipsis:
                    x_idx = slice(0, xsize)
                if not(isinstance(y_idx, slice) and isinstance(x_idx, slice)):
                    di = DaskImage(self)
                    return di.__getitem__(geometry)
                xmin, ymin, xmax, ymax = x_idx.start, y_idx.start, x_idx.stop, y_idx.stop
                xmin = 0 if xmin is None else xmin
                ymin = 0 if ymin is None else ymin
                xmax = xsize if xmax is None else xmax
                ymax = ysize if ymax is None else ymax
                if ymin > ysize and xmin > xsize:
                    raise IndexError("Index completely out of image bounds")

                g = ops.transform(self.__geo_transform__.fwd, box(xmin, ymin, xmax, ymax))
                result = super(GeoDaskImage, self).__getitem__(geometry)

            else:
                return super(GeoDaskImage, self).__getitem__(geometry)

        gi = mapping(g)
        gt = self.__geo_transform__ + (xmin, ymin)
        image = super(GeoDaskImage, self.__class__).__new__(self.__class__, result, __geo_interface__ = gi, __geo_transform__ = gt)
        return image
