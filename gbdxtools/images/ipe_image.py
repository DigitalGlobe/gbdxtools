from __future__ import print_function
import math

from gbdxtools.images.meta import DaskMeta, GeoDaskImage
from gbdxtools.ipe.util import RatPolyTransform, AffineTransform
from gbdxtools.ipe.interface import DaskProps
from gbdxtools.ipe.graph import get_ipe_graph
from gbdxtools.auth import Auth

from shapely import wkt, ops
from shapely.geometry import box, mapping
from shapely.geometry.base import BaseGeometry

from dask import optimize
import dask.array as da

import numpy as np

try:
    xrange
except NameError:
    xrange = range

class GraphMeta(DaskProps):
    def __init__(self, graph_id, node_id=None, **kwargs):
        assert graph_id is not None
        self._ipe_id = graph_id
        self._node_id = node_id
        self._interface = Auth()
        self._ipe_meta = None
        self._graph = None
        self._nid = None

    @property
    def _id(self):
        if self._nid is not None:
            return self._nid
        elif self._node_id is not None:
            self._nid = self._node_id
        else:
            graph = self.graph()
            self._nid = graph["nodes"][-1]["id"]
        return self._nid

    def graph(self):
        if self._graph is None:
            self._graph = get_ipe_graph(self._interface.gbdx_connection, self._ipe_id)
        return self._graph


class RDAGeoAdapter(object):
    def __init__(self, metadata):
        self.md = metadata
        self.gt = None
        self.gi = None

    @property
    def image(self):
        return self.md["image"]

    @property
    def xshift(self):
        return self.image["minTileX"] * self.image["tileXSize"]

    @property
    def yshift(self):
        return self.image["minTileY"] * self.image["tileYSize"]

    @property
    def minx(self):
        return self.image["minX"] - self.xshift

    @property
    def maxx(self):
        return self.image["maxX"] - self.xshift

    @property
    def miny(self):
        return self.image["minY"] - self.yshift

    @property
    def maxy(self):
        return self.image["maxY"] - self.yshift

    @property
    def tfm(self):
        if self.md["georef"] is None:
            return RatPolyTransform._from_rpcs(self.md["rpcs"])
        else:
            return AffineTransform._from_georef(self.md["georef"])

    @property
    def geo_transform(self):
        if not self.gt:
            self.gt =  self.tfm + (self.xshift, self.yshift)
        return self.gt

    @property
    def geo_interface(self):
        if not self.gi:
            self.gi =  mapping(GeoDaskImage._reproject(wkt.loads(self.image["imageBoundsWGS84"])))
        return self.gi

def rda_image_shift(image):
    minx, maxx = image.__geo__.minx, image.__geo__.maxx
    miny, maxy = image.__geo__.miny, image.__geo__.maxy
    return image[:, miny:maxy, minx:maxx]

class IpeImage(GeoDaskImage):
    _default_proj = "EPSG:4326"

    def __new__(cls, op, **kwargs):
        cls.__geo__ = RDAGeoAdapter(op.metadata)
        cls.__geo_transform__ = cls.__geo__.geo_transform
        cls.__geo_interface__ = cls.__geo__.geo_interface
        cls._ipe_op = op
        self = super(IpeImage, cls).__new__(cls, op)
        return rda_image_shift(self)

    def __getitem__(self, geometry):
        im = super(IpeImage, self).__getitem__(geometry)
        im._ipe_op = self._ipe_op
        return im

    @property
    def __daskmeta__(self):
        return self.ipe

    @property
    def ipe(self):
        return self._ipe_op

    @property
    def ipe_id(self):
        return self.ipe._ipe_id

    @property
    def ipe_metadata(self):
        return self.ipe.metadata

    @property
    def ntiles(self):
        size = float(self.ipe.metadata['image']['tileXSize'])
        return math.ceil((float(self.shape[-1]) / size)) * math.ceil(float(self.shape[1]) / size)

    def read(self, bands=None, quiet=True, **kwargs):
        if not quiet:
            print('Fetching Image... {} {}'.format(self.ntiles, 'tiles' if self.ntiles > 1 else 'tile'))
        return super(IpeImage, self).read(bands=bands)
