import sys

from gbdxtools.images.meta import DaskMeta, GeoDaskImage
from gbdxtools.rda.util import RatPolyTransform, AffineTransform, deprecation, get_proj
from gbdxtools.rda.graph import get_rda_graph
from gbdxtools.auth import Auth

from shapely import wkt, ops
from shapely.geometry import mapping

import pyproj
from functools import partial
import math

try:
    xrange
except NameError:
    xrange = range

def _reproject(geo, from_proj, to_proj):
    if from_proj != to_proj:
        from_proj = get_proj(from_proj)
        to_proj = get_proj(to_proj)
        tfm = pyproj.Transformer.from_crs(from_proj, to_proj, always_xy=True)
        return ops.transform(tfm.transform, geo)
    return geo


class GraphMeta(object):
    def __init__(self, graph_id, node_id=None, **kwargs):
        assert graph_id is not None
        self._rda_id = graph_id
        self._node_id = node_id
        self._interface = Auth()
        self._rda_meta = None
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
            self._graph = get_rda_graph(self._interface.gbdx_connection, self._rda_id)
        return self._graph


class RDAGeoAdapter(object):
    def __init__(self, metadata, dfp="EPSG:4326"):
        self.md = metadata
        self.default_proj = dfp
        if 'georef' in metadata and metadata['georef'] is not None:
            self._srs = metadata['georef']['spatialReferenceSystemCode']
        else:
            self._srs = dfp
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
            return RatPolyTransform.from_rpcs(self.md["rpcs"])
        else:
            return AffineTransform.from_georef(self.md["georef"])

    @property
    def geo_transform(self):
        if not self.gt:
            self.gt =  self.tfm + (self.xshift, self.yshift)
        return self.gt

    @property
    def geo_interface(self):
        if not self.gi:
            self.gi =  mapping(_reproject(wkt.loads(self.image["imageBoundsWGS84"]), self.srs, self.default_proj))
        return self.gi

    @property
    def srs(self):
        return self._srs

def rda_image_shift(image):
    minx, maxx = image.__geo__.minx, image.__geo__.maxx
    miny, maxy = image.__geo__.miny, image.__geo__.maxy
    return image[:, miny:maxy, minx:maxx]


class RDAImage(GeoDaskImage):
    _default_proj = "EPSG:4326"

    def __new__(cls, op, **kwargs):
        cls.__geo__ = RDAGeoAdapter(op.metadata, dfp=cls._default_proj)
        cls.__geo_transform__ = cls.__geo__.geo_transform
        cls.__geo_interface__ = cls.__geo__.geo_interface
        cls._rda_op = op
        self = super(RDAImage, cls).__new__(cls, op)
        return rda_image_shift(self)

    def __getitem__(self, geometry):
        im = super(RDAImage, self).__getitem__(geometry)
        if isinstance(im, GeoDaskImage):
            im._rda_op = self._rda_op
        return im

    @property
    def __daskmeta__(self):
        return self.rda

    @property
    def rda(self):
        return self._rda_op

    @property
    def rda_id(self):
        return self.rda._rda_id

    @property
    def metadata(self):
        return self.rda.metadata

    @property
    def ntiles(self):
        size = float(self.rda.metadata['image']['tileXSize'])
        return math.ceil((float(self.shape[-1]) / size)) * math.ceil(float(self.shape[1]) / size)

    def read(self, bands=None, quiet=True, **kwargs):
        if not quiet:
            print('Fetching Image... {} {}'.format(self.ntiles, 'tiles' if self.ntiles > 1 else 'tile'))
        return super(RDAImage, self).read(bands=bands)

    def materialize(self, node=None, bounds=None, callback=None, out_format='TIF', **kwargs):
        """
          Materializes images into gbdx user buckets in s3.
          Note: This method is only available to RDA based image classes. 

          Args:
            node (str): the node in the graph to materialize
            bounds (list): optional bbox for cropping what gets materialized in s3
            out_format (str): VECTOR_TILE, VECTOR, TIF, TILE_STREAM
            callback (str): a callback url like an `sns://`
          Returns:
            job_id (str): the job_id of the materialization 
        """
        kwargs.update({
          "node": node,
          "bounds": bounds,
          "callback": callback,
          "out_format": out_format
        })
        return self.rda._materialize(**kwargs)

    def materialize_status(self, job_id):
        """
          Checks the status of an materialize job.

          Args:
            job_id (str): the node in the graph to materialize
          Returns:
            status (dict): the status of the job  
        """
        return self.rda._materialize_status(job_id)