import uuid
import json
import copy
from hashlib import sha256
from itertools import chain
import gbdxtools as gbdx
from collections import OrderedDict

try:
    basestring
except NameError:
    basestring = str

from gbdxtools.ipe.graph import VIRTUAL_IPE_URL, register_ipe_graph, get_ipe_metadata, get_ipe_graph

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


def load_url(*args, **kwargs):
    """
    Temporary Dummy Function
    """
    pass


class ContentHashedDict(dict):
    @property
    def _id(self):
        _id = str(uuid.uuid5(NAMESPACE_UUID, self.__hash__()))
        return _id

    def __hash__(self):
        dup = {k:v for k,v in self.items() if k is not "id"}
        return sha256(str(dup).encode('utf-8')).hexdigest()

    def populate_id(self):
        self.update({"id": self._id})


class Op(object):
    def __init__(self, name):
        self._operator = name
        self._edges = []
        self._nodes = []

        self._ipe_id = None
        self._ipe_graph = None
        self._ipe_meta = None

    @property
    def _id(self):
        return self._nodes[0]._id

    def __call__(self, *args, **kwargs):
        if len(args) > 0 and all([isinstance(arg, gbdx.images.idaho_image.IpeImage) for arg in args]):
            return self._ipe_image_call(*args, **kwargs)
        self._nodes = [ContentHashedDict({"operator": self._operator,
                                          "_ancestors": [arg._id for arg in args],
                                          "parameters": {k:json.dumps(v) if not isinstance(v, basestring) else v for k,v in kwargs.items()}})]
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
        key = self._id
        ipe_img = gbdx.images.ipe_image.IpeImage({key: out}, args[0]._gid, node=key)
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
        if conn is not None:
            self._ipe_id = register_ipe_graph(conn, graph)
            self._ipe_graph = get_ipe_graph(conn, self._ipe_id)
            self._ipe_meta = get_ipe_metadata(conn, self._ipe_id, self._id)
            return self._ipe_graph

        return graph

    @property
    def metadata(self):
        # TODO: lookup connection singleton / do something about populating this
        return self._ipe_meta

    @property
    def dask(self):
        return {(self.name, 0, y, x): (load_url, url, self.chunks, "dummy_token") for (y, x), url in self._collect_urls().iteritems()}

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

    def _ipe_tile(self, x, y):
        return "{}/tile/{}/{}/{}/{}/{}.tif".format(VIRTUAL_IPE_URL, "idaho-virtual", self._ipe_id, self._id, x, y)

    def _collect_urls(self):
        img_md = self.metadata["image"]
        return {(y - img_md["minTileY"],
                 x - img_md["minTileX"]): self._ipe_tile(x, y)
                for y in xrange(img_md["minTileX"], img_md["maxTileX"] + 1)
                for x in xrange(img_md["minTileY"], img_md["maxTileY"] + 1)}

class Ipe(object):
    def __getattr__(self, name):
        return Op(name=name)
