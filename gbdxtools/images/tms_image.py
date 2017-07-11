import os
import uuid
import threading
import mercantile
from collections import defaultdict

import numpy as np
import rasterio
from rasterio.transform import from_bounds as transform_from_bounds

from gbdxtools.images.meta import DaskImage, DaskMeta
from gbdxtools.ipe.util import AffineTransform

try:
    from io import BytesIO
except ImportError:
    from StringIO import cStringIO as BytesIO

import gdal

def load_url(url, bands=3):
    try:
        src = gdal.Open('/vsicurl/{}'.format(url))
        arr = src.ReadAsArray()
    except:
        arr = np.zeros([bands,256,256], dtype=np.float32)
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

        # TODO: populate rest of fields automatically
        self._tile_size = 256
        self._nbands = 3
        self._dtype = "uint8"

        self.bounds = None

    @property
    def bounds(self):
        if self._bounds is None:
            # TODO: return web mercator complete bounds
            pass
        return self._bounds

    @bounds.setter
    def __set_bounds__(self, obj):
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
            return {(self._name, 0, x, y): (load_url, url) for (x, y), url in urls.items()}

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
        return tuple([self._nbands] + [self._tile_size, self._tile_size])

    @property
    def __geo_transform__(self):
        tfm = transform_from_bounds(*(self.bounds + self.shape[2:0:-1]))
        return AffineTransform(tfm, "EPSG:3857")

    def _collect_urls(self, bounds):
        minx, miny, maxx, maxy = self._tile_coords(bounds)
        urls = {(y-miny, x-minx): self._url_template.format(z=self.zoom_level, x=x, y=y, token=self._token)
                                                for y in xrange(miny, maxy + 1) for x in xrange(minx, maxx + 1)}

        return urls, (self._tile_size*(maxy-miny+1), self._tile_size*(maxx-minx+1))

    def _tile_coords(self, bounds):
        """ Convert tile coords mins/maxs to lng/lat bounds """
        params = bounds + [[self.zoom_level]]
        tile_coords = [(tile.x, tile.y) for tile in mercantile.tiles(*params)]
        xtiles, ytiles = zip(*tile_coords)
        minx = min(xtiles)
        maxx = max(xtiles)
        miny = min(ytiles)
        maxy = max(ytiles)
        return minx, miny, maxx, maxy



class TmsImage(DaskImage, Container):
    def __new__(cls, access_token=os.environ.get("DG_MAPS_API_TOKEN"),
                 url="https://api.mapbox.com/v4/digitalglobe.nal0g75k/{z}/{x}/{y}.png",
                 zoom=22, **kwargs):
        _tms_meta = TmsMeta(access_token=access_token, url=url, zoom=zoom, bounds=kwargs.get("bounds"))
        self = super(TmsImage, cls).create(_tms_meta)
        self._tms_meta = _tms_meta
        self.__geo_interface__ = mapping(box(*_tms_meta.bounds))
        self.__geo_transform__ = _tms_meta.__geo_transform__
        return self

    @property
    def __daskmeta__(self):
        self._tms_meta
