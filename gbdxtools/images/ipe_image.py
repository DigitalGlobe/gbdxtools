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


class IpeImage(GeoDaskImage):
    _default_proj = "EPSG:4326"

    def __new__(cls, op, **kwargs):
        if op is not None:
            assert isinstance(op, DaskMeta)
        elif "graph_id" in kwargs:
            op = GraphMeta(**kwargs)
        self = super(IpeImage, cls).__new__(cls, op, **kwargs)
        self._ipe_op = op
        if self.ipe.metadata["georef"] is None:
            tfm = RatPolyTransform.from_rpcs(self.ipe.metadata["rpcs"])
        else:
            tfm = AffineTransform.from_georef(self.ipe.metadata["georef"])
        img_md = self.ipe.metadata["image"]
        xshift = img_md["minTileX"]*img_md["tileXSize"]
        yshift = img_md["minTileY"]*img_md["tileYSize"]
        self.__geo_transform__ = tfm + (xshift, yshift)
        self.__geo_interface__ = mapping(self._reproject(wkt.loads(self.ipe.metadata["image"]["imageBoundsWGS84"])))
        minx = img_md["minX"] - xshift
        maxx = img_md["maxX"] - xshift
        miny = img_md["minY"] - yshift
        maxy = img_md["maxY"] - yshift
        return self[:, miny:maxy, minx:maxx]

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
