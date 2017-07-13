import os
import uuid
import threading
from collections import defaultdict, Container
from itertools import chain

import numpy as np
import rasterio
from rasterio.transform import from_bounds as transform_from_bounds
from rasterio.io import MemoryFile

import mercantile
from shapely.geometry import mapping, shape, box
from shapely.geometry.base import BaseGeometry
from shapely import ops

import pycurl
_curl_pool = defaultdict(pycurl.Curl)

from gbdxtools.images.meta import DaskImage, DaskMeta, GeoImage
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.util import AffineTransform

try:
    from io import BytesIO
except ImportError:
    from StringIO import cStringIO as BytesIO


def load_url(url, shape=(3, 256, 256)):
    """ Loads a geotiff url inside a thread and returns as an ndarray """
    thread_id = threading.current_thread().ident
    _curl = _curl_pool[thread_id]
    _curl.setopt(_curl.URL, url)
    _curl.setopt(pycurl.NOSIGNAL, 1)
    with MemoryFile() as memfile:
        _curl.setopt(_curl.WRITEDATA, memfile)
        _curl.perform()
        try:
            with memfile.open(driver="PNG") as dataset:
                arr = dataset.read()
        except (TypeError, rasterio.RasterioIOError) as e:
            arr = np.zeros(shape, dtype=np.float32)
            _curl.close()
            del _curl_pool[thread_id]
        return arr


class EphemeralImage(Exception):
    pass


def raise_aoi_required():
    raise EphemeralImage("Image subset must be specified before it can be made concrete.")


class TmsMeta(DaskMeta):
    def __init__(self, access_token=os.environ.get("DG_MAPS_API_TOKEN"),
                 url="https://api.mapbox.com/v4/digitalglobe.nal0g75k/{z}/{x}/{y}.png",
                 zoom=22, bounds=None):
        self.zoom_level = zoom
        self._token = access_token
        self._name = "image-{}".format(str(uuid.uuid4()))
        self._url_template = url + "?access_token={token}"

        _first_tile = mercantile.Tile(z=self.zoom_level, x=0, y=0)
        _last_tile = mercantile.tile(180, -85.05, self.zoom_level)
        g = box(*mercantile.bounds(_first_tile)).union(box(*mercantile.bounds(_last_tile)))
        self._full_bounds = g.bounds

        # TODO: populate rest of fields automatically
        self._tile_size = 256
        self._nbands = 3
        self._dtype = "uint8"
        self.bounds = self._expand_bounds(bounds)
        print("INIT", bounds, self.bounds)
        self._chunks = tuple([self._nbands] + [self._tile_size, self._tile_size])

    @property
    def bounds(self):
        if self._bounds is None:
            return self._full_bounds
        return self._bounds

    @bounds.setter
    def bounds(self, obj):
        # TODO: set bounds via shapely or bbox, validation
        self._bounds = obj
        if obj is not None:
            self._urls, self._shape = self._collect_urls(self.bounds)

    @property
    def name(self):
        return self._name

    @property
    def dask(self):
        if self._bounds is None:
            return {self._name: (raise_aoi_required, )}
        else:
            urls, shape = self._collect_urls(self.bounds)
            return {(self._name, 0, y, x): (load_url, url, self._chunks) for (y, x), url in urls.items()}

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        if self._bounds is None:
            _tile = mercantile.tile(180, -85.05, self.zoom_level)
            nx = _tile.x * self._tile_size
            ny = _tile.y * self._tile_size
            return tuple([self._nbands] + [ny, nx])
        else:
            return self._shape

    @property
    def chunks(self):
        return self._chunks

    @property
    def __geo_transform__(self):
        tfm = transform_from_bounds(*tuple(e for e in chain(self.bounds, self.shape[2:0:-1])))
        return AffineTransform(tfm, "EPSG:3857")

    def _collect_urls(self, bounds):
        minx, miny, maxx, maxy = self._tile_coords(bounds)
        urls = {(y-miny, x-minx): self._url_template.format(z=self.zoom_level, x=x, y=y, token=self._token)
                                                for y in xrange(miny, maxy + 1) for x in xrange(minx, maxx + 1)}

        return urls, (3, self._tile_size*(maxy-miny+1), self._tile_size*(maxx-minx+1))

    def _expand_bounds(self, bounds):
        if bounds is None:
            return bounds
        min_tile_x, min_tile_y, max_tile_x, max_tile_y = self._tile_coords(bounds)

        ul = box(*mercantile.bounds(mercantile.Tile(z=self.zoom_level, x=min_tile_x, y=max_tile_y)))
        lr = box(*mercantile.bounds(mercantile.Tile(z=self.zoom_level, x=max_tile_x, y=min_tile_y)))

        return ul.union(lr).bounds

    def _tile_coords(self, bounds):
        """ Convert tile coords mins/maxs to lng/lat bounds """
        params = list(bounds) + [[self.zoom_level]]
        tile_coords = [(tile.x, tile.y) for tile in mercantile.tiles(*params)]
        xtiles, ytiles = zip(*tile_coords)
        minx = min(xtiles)
        maxx = max(xtiles)
        miny = min(ytiles)
        maxy = max(ytiles)
        return minx, miny, maxx, maxy


class TmsImage(DaskImage, GeoImage):
    _default_proj = "EPSG:3857"

    def __new__(cls, access_token=os.environ.get("DG_MAPS_API_TOKEN"),
                 url="https://api.mapbox.com/v4/digitalglobe.nal0g75k/{z}/{x}/{y}.png",
                 zoom=22, **kwargs):
        _tms_meta = TmsMeta(access_token=access_token, url=url, zoom=zoom, bounds=kwargs.get("bounds"))
        self = super(TmsImage, cls).create(_tms_meta)
        self._base_args = {"access_token": access_token, "url": url, "zoom": zoom}
        self._tms_meta = _tms_meta
        self.__geo_interface__ = mapping(box(*_tms_meta.bounds))
        self.__geo_transform__ = _tms_meta.__geo_transform__
        return self

    @property
    def __daskmeta__(self):
        return self._tms_meta

    def rgb(self, **kwargs):
        return np.rollaxis(self.read(), 0, 3)

    def plot(self, **kwargs):
        super(TmsImage, self).plot(tfm=self.rgb, **kwargs)

    def aoi(self, **kwargs):
        g = self._parse_geoms(**kwargs)
        return self.__class__(bounds=list(g.bounds), **self._base_args)[g]

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            image = GeoImage.__getitem__(self, geometry)
            image._tms_meta = self._tms_meta
            return image
        else:
            image = super(TmsImage, self).__getitem__(geometry)
            if all([isinstance(e, slice) for e in geometry]) and len(geometry) == len(self.shape):
                # xmin, ymin, xmax, ymax
                g = ops.transform(self.__geo_transform__.fwd,
                                  box(geometry[2].start, geometry[1].start, geometry[2].stop, geometry[1].stop))

                image.__geo_interface__ = mapping(g)
                bounds = g.bounds
                image.__geo_transform__ = self.__geo_transform__ + (bounds[0], bounds[1])
            else:
                image.__geo_interface__ = self.__geo_interface__
                image.__geo_transform__ = self.__geo_transform__
            image._tms_meta = self._tms_meta
            image.__class__ = self.__class__
            return image
