from __future__ import print_function
import abc
import types
import os
import random
from functools import wraps, partial
from itertools import chain
from collections import Container
from six import add_metaclass
import warnings
import math

from gbdxtools.ipe.io import to_geotiff
from gbdxtools.ipe.util import RatPolyTransform, AffineTransform, pad_safe_positive, pad_safe_negative, IPE_TO_DTYPE, preview

from shapely import ops, wkt
from shapely.geometry import box, shape, mapping
from shapely.geometry.base import BaseGeometry
try:
    from rio_hist.match import histogram_match
except ImportError:
    pass
import mercantile

import skimage.transform as tf

import pyproj
import dask
from dask import sharedict, optimize
from dask.delayed import delayed
import dask.array as da
from dask.base import is_dask_collection
from dask.rewrite import RewriteRule, RuleSet
import numpy as np

import operator
from toolz import valmap

from affine import Affine

try:
    from matplotlib import pyplot as plt
    has_pyplot = True
except:
    has_pyplot = False


@add_metaclass(abc.ABCMeta)
class DaskMeta(object):
    """
    A DaskMeta is an interface for the required attributes for initializing a dask Array
    """
    @abc.abstractproperty
    def dask(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def chunks(self):
        pass

    @abc.abstractproperty
    def dtype(self):
        pass

    @abc.abstractproperty
    def shape(self):
        pass

    def infect(self, target):
        assert isinstance(target, da.Array), "DaskMeta can only be attached to Dask Arrays"
        assert len(target.shape) in [2, 3], "target must be a dask array with 2 or 3 dimensions"
        target.__dict__["__daskmeta__"] = property(lambda s: self, DaskImage.__set_daskmeta__)
        return target

@add_metaclass(abc.ABCMeta)
class DaskImage(da.Array):
    """
    A DaskImage is a 2 or 3 dimension dask array that contains implements the `__daskmeta__` interface.
    """
    @property
    def __daskmeta__(self):
        """ Should return a DaskMeta """
        pass

    @__daskmeta__.setter
    def __set_daskmeta__(self, obj):
        self.__dict__["__daskmeta__"] = property(lambda s: obj, self.__set_daskmeta__)

    @classmethod
    def __subclasshook__(cls, C):
        if cls is DaskImage:
            try:
                if(is_dask_collection(C) and any("__daskmeta__" in B.__dict__ for B in C.__mro__)):
                    return True
            except AttributeError:
                pass
        return NotImplemented

    @staticmethod
    def _cull(dsk, keys=None):
        if not keys:
            return dsk
        elif "token" not in dsk:
            return dsk
        if "token" not in keys:
            keys.append("token")
        dsk1, _ = optimize.cull(dsk, keys)
        return dsk1

    def __getattribute__(self, name):
        fn = object.__getattribute__(self, name)
        if(isinstance(fn, types.MethodType) and
           any(name in C.__dict__ for C in self.__class__.__mro__)):
            @wraps(fn)
            def wrapped(*args, **kwargs):
                result = fn(*args, **kwargs)
                if isinstance(result, da.Array) and len(result.shape) in [2,3]:
                    dsk = self._cull(result.dask, result.__dask_keys__())
                    copy = super(DaskImage, self.__class__).__new__(self.__class__,
                                                                    dsk, result.name, result.chunks,
                                                                    result.dtype, result.shape)
                    copy.__dict__.update(self.__dict__)
                    try:
                        copy.__dict__.update(result.__dict__)
                    except AttributeError:
                        # this means result was an object with __slots__
                        pass
                    return copy
                return result
            return wrapped
        else:
            return fn

    @classmethod
    def create(cls, dm, **kwargs):
        """
        Given a dask meta object, construct a dask array, attach dask meta object.
        """
        assert isinstance(dm, DaskMeta), "argument must be an instance of a DaskMeta subclass"
        with dask.set_options(array_plugins=[dm.infect]):

            return da.Array.__new__(cls, dm.dask, dm.name, dm.chunks, dm.dtype, dm.shape)

    def read(self, bands=None, **kwargs):
        """
        Reads data from a dask array and returns the computed ndarray matching the given bands

        kwargs:
            bands (list): band indices to read from the image. Returns bands in the order specified in the list of bands.

        Returns:
            array (ndarray): a numpy array of image data
        """
        arr = self
        if bands is not None:
            arr = self[bands, ...]
        with dask.set_options(get=dask.get):
            return arr.compute()

    def randwindow(self, window_shape):
        """
        Get a random window of a given shape from withing an image

        kwargs:
            window_shape (tuple): The desired shape of the returned image as (height, width) in pixels.

        Returns:
            image (dask): a new image object of the specified shape
        """
        row = random.randrange(window_shape[0], self.shape[1])
        col = random.randrange(window_shape[1], self.shape[2])
        return self[:, row-window_shape[0]:row, col-window_shape[1]:col]

    def iterwindows(self, count=64, window_shape=(256, 256)):
        """
        Iterate over random windows of an image

        kwargs:
            count (int): the number of the windows to generate. Defaults to 64, if `None` with continue to iterate over random windows until stopped.
            window_shape (tuple): The desired shape of each image as (height, width) in pixels.

        Returns:
            windows (generator): a generator of windows of the given shape
        """
        if count is None:
            while True:
                yield self.randwindow(window_shape)
        else:
            for i in xrange(count):
                yield self.randwindow(window_shape)


@add_metaclass(abc.ABCMeta)
class GeoImage(Container):
    _default_proj = "EPSG:4326"

    # def __geo_interface__(self):
    #     pass

    # def __geo_transform__(self):
    #     pass

    @classmethod
    def __subclasshook__(cls, C):
        # Must be a numpy-like, with __geo_transform__, and __geo_interface__
        if(issubclass(C, DaskImage) or issubclass(C, np.ndarray) and
           any("__geo_transform__" in B.__dict__ for B in C.__mro__) and
           any("__geo_interface__" in B.__dict__ for B in C.__mro__)):
            return True
        return NotImplemented

    @property
    def affine(self):
        """ The geo transform of the image

        Returns:
            affine (dict): The image's affine transform
        """
        # TODO add check for Ratpoly or whatevs
        return self.__geo_transform__._affine

    @property
    def bounds(self):
        """ Access the spatial bounding box of the image

        Returns:
            bounds (list): list of bounds in image projected coordinates (minx, miny, maxx, maxy)
        """
        return shape(self).bounds

    @property
    def proj(self):
        """ The projection of the image """
        return self.__geo_transform__.proj

    def aoi(self, **kwargs):
        """ Subsets the Image by the given bounds

        kwargs:
            bbox: optional. A bounding box array [minx, miny, maxx, maxy]
            wkt: optional. A WKT geometry string
            geojson: optional. A GeoJSON geometry dictionary

        Returns:
            image (ndarray): an image instance
        """
        g = self._parse_geoms(**kwargs)
        if g is None:
            return self
        else:
            return self[g]

    def geotiff(self, **kwargs):
        """ Creates a geotiff on the filesystem

        kwargs:
            path (str): optional. The path to save the geotiff to.
            bands (list): optional. A list of band indices to save to the output geotiff ([4,2,1])
            dtype (str): optional. The data type to assign the geotiff to ("float32", "uint16", etc)
            proj (str): optional. An EPSG proj string to project the image data into ("EPSG:32612")

        Returns:
            path (str): the path to created geotiff
        """
        if 'proj' not in kwargs:
            kwargs['proj'] = self.proj
        return to_geotiff(self, **kwargs)

    def preview(self, **kwargs):
        preview(self, **kwargs)

    def warp(self, dem=None, proj="EPSG:4326", **kwargs):
        """
        Delayed warp across an entire AOI or Image
        creates a new dask image by deferring calls to the warp_geometry on chunks

        kwargs:
            dem (ndarray): optional. A DEM for warping to specific elevation planes
            proj (str): optional. An EPSG proj string to project the image data into ("EPSG:32612")

        Returns:
            image (dask): a warped image as deferred image array (a dask)
        """
        try:
            img_md = self.ipe.metadata["image"]
            x_size = img_md["tileXSize"]
            y_size = img_md["tileYSize"]
        except (AttributeError, KeyError):
            x_size = kwargs.get("chunk_size", 256)
            y_size = kwargs.get("chunk_size", 256)

        # Create an affine transform to convert between real-world and pixels
        if self.proj is None:
            from_proj = "EPSG:4326"
        else:
            from_proj = self.proj

        try:
            # NOTE: this only works on images that have IPE rpcs metadata
            center = wkt.loads(self.ipe.metadata["image"]["imageBoundsWGS84"]).centroid
            g = box(*(center.buffer(self.ipe.metadata["rpcs"]["gsd"] / 2).bounds))
            # print "Input GSD (deg):", self.ipe.metadata["rpcs"]["gsd"]
            tfm = partial(pyproj.transform, pyproj.Proj(init="EPSG:4326"), pyproj.Proj(init=proj))
            gsd = kwargs.get("gsd", ops.transform(tfm, g).area ** 0.5)
            current_bounds = wkt.loads(self.ipe.metadata["image"]["imageBoundsWGS84"]).bounds
        except (AttributeError, KeyError, TypeError):
            tfm = partial(pyproj.transform, pyproj.Proj(init=self.proj), pyproj.Proj(init=proj))
            gsd = kwargs.get("gsd", (ops.transform(tfm, shape(self)).area / (self.shape[1] * self.shape[2])) ** 0.5 )
            current_bounds = self.bounds

        tfm = partial(pyproj.transform, pyproj.Proj(init=from_proj), pyproj.Proj(init=proj))
        itfm = partial(pyproj.transform, pyproj.Proj(init=proj), pyproj.Proj(init=from_proj))
        output_bounds = ops.transform(tfm, box(*current_bounds)).bounds
        gtf = Affine.from_gdal(output_bounds[0], gsd, 0.0, output_bounds[3], 0.0, -1 * gsd)

        ll = ~gtf * (output_bounds[:2])
        ur = ~gtf * (output_bounds[2:])
        x_chunks = int((ur[0] - ll[0]) / x_size) + 1
        y_chunks = int((ll[1] - ur[1]) / y_size) + 1

        num_bands = self.shape[0]

        try:
            dtype = IPE_TO_DTYPE[img_md["dataType"]]
        except:
            dtype = 'uint8'

        daskmeta = {
            "dask": {},
            "chunks": (num_bands, y_size, x_size),
            "dtype": dtype,
            "name": "warp-{}".format(self.name),
            "shape": (num_bands, y_chunks * y_size, x_chunks * x_size)
        }

        def px_to_geom(xmin, ymin):
            xmax = int(xmin + x_size)
            ymax = int(ymin + y_size)
            bounds = list((gtf * (xmin, ymax)) + (gtf * (xmax, ymin)))
            return box(*bounds)

        full_bounds = box(*output_bounds)

        dasks = []
        if isinstance(dem, GeoImage):
            if dem.proj != proj:
                dem = dem.warp(proj=proj, dem=dem)
            dasks.append(dem.dask)

        for y in xrange(y_chunks):
            for x in xrange(x_chunks):
                xmin = x * x_size
                ymin = y * y_size
                geometry = px_to_geom(xmin, ymin)
                daskmeta["dask"][(daskmeta["name"], 0, y, x)] = (self._warp, geometry, gsd, dem, proj, dtype, 5)
        daskmeta["dask"], _ = optimize.cull(sharedict.merge(daskmeta["dask"], *dasks), list(daskmeta["dask"].keys()))

        result = GeoDaskWrapper(daskmeta, self)
        result.__geo_interface__ = mapping(full_bounds)
        result.__geo_transform__ = AffineTransform(gtf, proj)
        return GeoImage.__getitem__(result, box(*output_bounds))

    def _warp(self, geometry, gsd, dem, proj, dtype, buf=0):
        transpix = self._transpix(geometry, gsd, dem, proj)
        xmin, xmax, ymin, ymax = (int(max(transpix[0,:,:].min() - buf, 0)),
                                  int(min(transpix[0,:,:].max() + buf, self.shape[1])),
                                  int(max(transpix[1,:,:].min() - buf, 0)),
                                  int(min(transpix[1,:,:].max() + buf, self.shape[2])))
        transpix[0,:,:] = transpix[0,:,:] - xmin
        transpix[1,:,:] = transpix[1,:,:] - ymin
        data = self[:,xmin:xmax, ymin:ymax].compute(get=dask.get) # read(quiet=True)

        if data.shape[1]*data.shape[2] > 0:
            return np.rollaxis(np.dstack([tf.warp(data[b,:,:], transpix, preserve_range=True, order=3, mode="edge") for b in xrange(data.shape[0])]).astype(dtype), 2, 0)
        else:
            return np.zeros((data.shape[0], transpix.shape[1], transpix.shape[2]))

    def _transpix(self, geometry, gsd, dem, proj):
        xmin, ymin, xmax, ymax = geometry.bounds
        x = np.linspace(xmin, xmax, num=int((xmax-xmin)/gsd))
        y = np.linspace(ymax, ymin, num=int((ymax-ymin)/gsd))
        xv, yv = np.meshgrid(x, y, indexing='xy')

        if self.proj is None:
            from_proj = "EPSG:4326"
        else:
            from_proj = self.proj

        itfm = partial(pyproj.transform, pyproj.Proj(init=proj), pyproj.Proj(init=from_proj))

        xv, yv = itfm(xv, yv) # if that works

        if isinstance(dem, GeoImage):
            g = box(xv.min(), yv.min(), xv.max(), yv.max())
            try:
                dem = dem[g].compute(get=dask.get) # read(quiet=True)
            except AssertionError:
                dem = 0 # guessing this is indexing by a 0 width geometry.

        if isinstance(dem, np.ndarray):
            dem = tf.resize(np.squeeze(dem), xv.shape, preserve_range=True, order=1, mode="edge")

        return self.__geo_transform__.rev(xv, yv, z=dem, _type=np.float32)[::-1]

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
        tfm = partial(pyproj.transform, pyproj.Proj(init=from_proj), pyproj.Proj(init=to_proj))
        return ops.transform(tfm, geometry)


    def _slice_padded(self, bounds):
        pads = (max(-bounds[0], 0), max(-bounds[1], 0),
                max(bounds[2]-self.shape[2], 0), max(bounds[3]-self.shape[1], 0))
        bounds = (max(bounds[0], 0),
                  max(bounds[1], 0),
                  max(min(bounds[2], self.shape[2]), 0),
                  max(min(bounds[3], self.shape[1]), 0))

        # NOTE: image is a dask array that implements daskmeta interface (via op)
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

        image = super(DaskImage, self.__class__).__new__(self.__class__,
                                                         result.dask, result.name, result.chunks,
                                                         result.dtype, result.shape)

        image.__geo_transform__ = self.__geo_transform__ + (bounds[0], bounds[1])
        return image

    def __getitem__(self, geometry):
        g = shape(geometry)

        bounds = ops.transform(self.__geo_transform__.rev, g).bounds
        try:
            assert g in self, "Image does not contain specified geometry {} not in {}".format(g.bounds, self.bounds)
        except AssertionError as ae:
            warnings.warn(ae.args)

        image = self._slice_padded(bounds)
        image.__geo_interface__ = mapping(g)
        return image

    def __contains__(self, g):
        geometry = ops.transform(self.__geo_transform__.rev, g)
        img_bounds = box(0, 0, *self.shape[2:0:-1])
        return img_bounds.contains(geometry)


class DaskMetaWrapper(DaskMeta):
    def __init__(self, dask):
        self.da = dask

    @property
    def dask(self):
        return self.da["dask"]

    @property
    def name(self):
        return self.da["name"]

    @property
    def chunks(self):
        return self.da["chunks"]

    @property
    def dtype(self):
        return self.da["dtype"]

    @property
    def shape(self):
        return self.da["shape"]


# Mixin class that defines plotting methods and rgb/ndvi methods
# used as a mixin to provide access to the plot method on
# GeoDaskWrapper images and ipe images
class PlotMixin(object):
    @property
    def _rgb_bands(self):
        return [4, 2, 1]

    @property
    def _ndvi_bands(self):
        return [6, 4]

    def base_layer_match(self, blm=False, **kwargs):
        rgb = self.rgb(**kwargs)
        if not blm:
            return rgb
        from gbdxtools.images.tms_image import TmsImage
        bounds = self._reproject(box(*self.bounds), from_proj=self.proj, to_proj="EPSG:4326").bounds
        tms = TmsImage(zoom=self._calc_tms_zoom(self.affine[0]), bbox=bounds, **kwargs)
        ref = np.rollaxis(tms.read(), 0, 3)
        out = np.dstack([histogram_match(rgb[:,:,idx], ref[:,:,idx].astype(np.double)/255.0)
                        for idx in xrange(rgb.shape[-1])])
        return out

    def rgb(self, **kwargs):
        data = self._read(self[kwargs.get("bands", self._rgb_bands),...], **kwargs)
        data = np.rollaxis(data.astype(np.float32), 0, 3)
        lims = np.percentile(data, kwargs.get("stretch", [2, 98]), axis=(0, 1))
        for x in xrange(len(data[0,0,:])):
            top = lims[:,x][1]
            bottom = lims[:,x][0]
            data[:,:,x] = (data[:,:,x] - bottom) / float(top - bottom)
        return np.clip(data, 0, 1)

    def ndvi(self, **kwargs):
        data = self._read(self[self._ndvi_bands,...]).astype(np.float32)
        return (data[0,:,:] - data[1,:,:]) / (data[0,:,:] + data[1,:,:])

    def plot(self, spec="rgb", **kwargs):
        if self.shape[0] == 1 or ("bands" in kwargs and len(kwargs["bands"]) == 1):
            if "cmap" in kwargs:
                cmap = kwargs["cmap"]
                del kwargs["cmap"]
            else:
                cmap = "Greys_r"
            self._plot(tfm=self._single_band, cmap=cmap, **kwargs)
        else:
            if spec == "rgb" and self._has_token(**kwargs):
                self._plot(tfm=self.base_layer_match, **kwargs)
            else:
                self._plot(tfm=getattr(self, spec), **kwargs)

    def _has_token(self, **kwargs):
        if "access_token" in kwargs or "MAPBOX_API_KEY" in os.environ:
            return True
        else:
            return False

    def _plot(self, tfm=lambda x: x, **kwargs):
        assert has_pyplot, "To plot images please install matplotlib"
        assert self.shape[1] and self.shape[-1], "No data to plot, dimensions are invalid {}".format(str(self.shape))

        f, ax1 = plt.subplots(1, figsize=(kwargs.get("w", 10), kwargs.get("h", 10)))
        ax1.axis('off')
        plt.imshow(tfm(**kwargs), interpolation='nearest', cmap=kwargs.get("cmap", None))
        plt.show(block=False)

    def _read(self, data, **kwargs):
        if hasattr(data, 'read'):
            return data.read(**kwargs)
        else:
            return data.compute()

    def _single_band(self, **kwargs):
        return self._read(self[0,:,:], **kwargs)

    def _calc_tms_zoom(self, scale):
        for z in range(15,20):
            b = mercantile.bounds(0,0,z)
            if scale > math.sqrt((b.north - b.south)*(b.east - b.west) / (256*256)):
                return z


class GeoDaskWrapper(DaskImage, GeoImage, PlotMixin):
    def __new__(cls, daskmeta, img):
        dm = DaskMetaWrapper(daskmeta)
        self = super(GeoDaskWrapper, cls).create(dm)
        self._dm = dm
        self.__geo_interface__ = img.__geo_interface__
        self.__geo_transform__ = img.__geo_transform__
        return self

    @property
    def __daskmeta__(self):
        return self._dm

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            image = GeoImage.__getitem__(self, geometry)
            return image
        else:
            result = DaskImage.__getitem__(self, geometry)
            image = super(GeoDaskWrapper, self.__class__).__new__(self.__class__,
                                                            result.dask, result.name, result.chunks,
                                                            result.dtype, result.shape)

            if all([isinstance(e, slice) for e in geometry]) and len(geometry) == len(self.shape):
                xmin, ymin, xmax, ymax = geometry[2].start, geometry[1].start, geometry[2].stop, geometry[1].stop
                xmin = 0 if xmin is None else xmin
                ymin = 0 if ymin is None else ymin
                xmax = self.shape[2] if xmax is None else xmax
                ymax = self.shape[1] if ymax is None else ymax

                g = ops.transform(self.__geo_transform__.fwd, box(xmin, ymin, xmax, ymax))
                image.__geo_interface__ = mapping(g)
                image.__geo_transform__ = self.__geo_transform__ + (xmin, ymin)
            else:
                image.__geo_interface__ = self.__geo_interface__
                image.__geo_transform__ = self.__geo_transform__
            return image
