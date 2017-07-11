import uuid
import json
from hashlib import sha256
from itertools import chain
from collections import OrderedDict, defaultdict
import threading

import warnings
warnings.filterwarnings('ignore')

try:
    from io import BytesIO
except ImportError:
    from cStringIO import StringIO as BytesIO

try:
    basestring
except NameError:
    basestring = str

try:
    xrange
except NameError:
    xrange = range

import pycurl
_curl_pool = defaultdict(pycurl.Curl)

import numpy as np

import rasterio
from rasterio.io import MemoryFile

import gbdxtools as gbdx
from gbdxtools.ipe.graph import VIRTUAL_IPE_URL, register_ipe_graph, get_ipe_metadata, get_ipe_graph
from gbdxtools.images.meta import DaskMeta
from gbdxtools.auth import Auth


IPE_TO_DTYPE = {
    "BINARY": "bool",
    "BYTE": "byte",
    "SHORT": "short",
    "UNSIGNED_SHORT": "ushort",
    "INTEGER": "int32",
    "UNSIGNED_INTEGER": "uint32",
    "LONG": "int64",
    "UNSIGNED_LONG": "uint64",
    "FLOAT": "float32",
    "DOUBLE": "float64"
}

NAMESPACE_UUID = uuid.NAMESPACE_DNS


def load_url(url, token, shape=(8, 256, 256)):
    """ Loads a geotiff url inside a thread and returns as an ndarray """
    thread_id = threading.current_thread().ident
    _curl = _curl_pool[thread_id]
    buf = BytesIO()
    _curl.setopt(_curl.URL, url)
    _curl.setopt(pycurl.NOSIGNAL, 1)
    _curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(token)])
    with MemoryFile() as memfile:
        _curl.setopt(_curl.WRITEDATA, memfile)
        _curl.perform()
        try:
            with memfile.open(driver="GTiff") as dataset:
                arr = dataset.read()
        except (TypeError, rasterio.RasterioIOError) as e:
            arr = np.zeros(shape, dtype=np.float32)
            _curl.close()
            del _curl_pool[thread_id]
        return arr


class ContentHashedDict(OrderedDict):
    @property
    def _id(self):
        _id = str(uuid.uuid5(NAMESPACE_UUID, self.__hash__()))
        return _id

    def __hash__(self):
        dup = OrderedDict({k:v for k,v in self.items() if k is not "id"})
        return sha256(str(dup).encode('utf-8')).hexdigest()

    def populate_id(self):
        self.update({"id": self._id})


class Op(DaskMeta):
    def __init__(self, name, interface=None):
        self._operator = name
        self._edges = []
        self._nodes = []

        self._ipe_id = None
        self._ipe_graph = None
        self._ipe_meta = None

        self._interface = interface

    @property
    def _id(self):
        return self._nodes[0]._id

    def __call__(self, *args, **kwargs):
        if len(args) > 0 and all([isinstance(arg, gbdx.images.ipe_image.IpeImage) for arg in args]):
            return self._ipe_image_call(*args, **kwargs)

        self._nodes = [ContentHashedDict({"operator": self._operator,
                                          "_ancestors": [arg._id for arg in args],
                                          "parameters": OrderedDict({k:json.dumps(v, sort_keys=True) if not isinstance(v, basestring) else v for k,v in sorted(kwargs.items(), key=lambda x: x[0])})})]
        for arg in args:
            self._nodes.extend(arg._nodes)

        self._edges = [ContentHashedDict({"index": idx + 1, "source": arg._nodes[0]._id, "destination": self._nodes[0]._id}) for idx, arg in enumerate(args)]
        for arg in args:
            self._edges.extend(arg._edges)

        for e in chain(self._nodes, self._edges):
            e.populate_id()
        return self

    def _ipe_image_call(self, *args, **kwargs):
        out = self(*[arg.ipe for arg in args], **kwargs)
        ipe_img = gbdx.images.ipe_image.IpeImage(out)
        return ipe_img

    def graph(self, conn=None):
        if(self._ipe_id is not None and
           self._ipe_graph is not None):
            return self._ipe_graph

        _nodes = [{k:v for k,v in node.items() if not k.startswith('_')} for node in self._nodes]
        graph =  {
            "edges": self._edges,
            "nodes": _nodes
        }

        if self._interface is not None and conn is None:
            conn = self._interface.gbdx_futures_session

        if conn is not None:
            self._ipe_id = register_ipe_graph(conn, graph)
            self._ipe_graph = graph # get_ipe_graph(conn, self._ipe_id)
            self._ipe_meta = get_ipe_metadata(conn, self._ipe_id, self._id)
            return self._ipe_graph

        return graph

    @property
    def metadata(self):
        assert self.graph() is not None
        if self._ipe_meta is not None:
            return self._ipe_meta
        if self._interface is not None:
            self._ipe_meta = get_ipe_metadata(self._interface.gbdx_futures_session, self._ipe_id, self._id)
        return self._ipe_meta

    @property
    def dask(self):
        token = self._interface.gbdx_connection.access_token
        return {(self.name, 0, y, x): (load_url, url, token, self.chunks) for (y, x), url in self._collect_urls().items()}

    @property
    def name(self):
        return "image-{}".format(self._id)

    @property
    def chunks(self):
        img_md = self.metadata["image"]
        return (img_md["numBands"], img_md["tileYSize"], img_md["tileXSize"])

    @property
    def dtype(self):
        try:
            data_type = self.metadata["image"]["dataType"]
            return IPE_TO_DTYPE[data_type]
        except KeyError:
            raise TypeError("Metadata indicates an unrecognized data type: {}".format(data_type))

    @property
    def shape(self):
        img_md = self.metadata["image"]
        return (img_md["numBands"],
                img_md["imageHeight"] + img_md["imageHeight"] % img_md["tileYSize"],
                img_md["imageWidth"] + img_md["imageWidth"] % img_md["tileXSize"])

    def _ipe_tile(self, x, y, ipe_id, _id):
        return "{}/tile/{}/{}/{}/{}/{}.tif".format(VIRTUAL_IPE_URL, "idaho-virtual", ipe_id, _id, x, y)

    def _collect_urls(self):
        img_md = self.metadata["image"]
        ipe_id = self._ipe_id
        _id = self._id
        return {(y, x): self._ipe_tile(x + img_md["tileXOffset"], y + img_md["tileYOffset"], ipe_id, _id)
                for y in xrange(max(img_md['minTileY'], 0), img_md["maxTileY"])
                for x in xrange(max(img_md['minTileX'], 0), img_md["maxTileX"])}

class Ipe(object):
    #def __init__(self):
    #    self.interface = Auth()

    def __getattr__(self, name):
        return Op(name=name, interface=Auth())
