import sys
import os
import uuid
import json
from hashlib import sha256
from itertools import chain
from collections import OrderedDict

import operator
from functools import partial
import numpy as np
from shapely.geometry import box

import gbdxtools as gbdx
from gbdxtools.rda.util import RDA_TO_DTYPE
from gbdxtools.rda.graph import VIRTUAL_RDA_URL, register_rda_graph, \
                                get_rda_metadata, get_graph_stats, \
                                materialize_template, create_rda_template, \
                                materialize_status
from gbdxtools.auth import Auth
from gbdxtools.rda.fetch import easyfetch as load_url
from gbdxtools.images.meta import DaskMeta

#import warnings
#warnings.filterwarnings('ignore')

try:
    basestring
except NameError:
    basestring = str

try:
    xrange
except NameError:
    xrange = range

NAMESPACE_UUID = uuid.NAMESPACE_DNS

class ContentHashedDict(dict):
    @property
    def _id(self):
        _id = str(uuid.uuid5(NAMESPACE_UUID, self.__hash__()))
        return _id

    def __hash__(self):
        dup = OrderedDict({k:v for k,v in self.items() if k is not "id"})
        return sha256(str(dup).encode('utf-8')).hexdigest()

    def populate_id(self):
        self.update({"id": self._id})


class DaskProps(object):

    def graph(self):
        pass

    @property
    def metadata(self):
        assert self.graph() is not None
        if self._rda_meta is not None:
            return self._rda_meta
        if self._interface is not None:
            self._rda_meta = get_rda_metadata(self._interface.gbdx_futures_session, self._rda_id, self._id)
        return self._rda_meta

    @property
    def display_stats(self):
        assert self.graph() is not None
        if self._rda_stats is None:
            self._rda_stats = get_graph_stats(self._interface.gbdx_futures_session, self._rda_id, self._id)
        return self._rda_stats

    @property
    def dask(self):
        token = self._interface.gbdx_connection.access_token
        _chunks = self.chunks
        _name = self.name
        img_md = self.metadata["image"]
        return {(_name, 0, y - img_md['minTileY'], x - img_md['minTileX']): (load_url, url, token, _chunks)
                for (y, x), url in self._collect_urls().items()}

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
            return RDA_TO_DTYPE[data_type]
        except KeyError:
            raise TypeError("Metadata indicates an unrecognized data type: {}".format(data_type))

    @property
    def shape(self):
        img_md = self.metadata["image"]
        return (img_md["numBands"],
                (img_md["maxTileY"] - img_md["minTileY"] + 1)*img_md["tileYSize"],
                (img_md["maxTileX"] - img_md["minTileX"] + 1)*img_md["tileXSize"])

    def _materialize(self, node=None, bounds=None, callback=None, out_format='TILE_STREAM', **kwargs):
        conn = self._interface.gbdx_futures_session
        graph = self.graph()
        templateId = create_rda_template(conn, graph)
        if node is None:
            node = graph['nodes'][0]['id']
        payload = self._create_materialize_payload(templateId, node, bounds, callback, out_format, **kwargs) 
        return materialize_template(conn, payload)

    def _materialize_status(self, job_id):
        return materialize_status(self._interface.gbdx_futures_session, job_id)

    def _create_materialize_payload(self, templateId, node, bounds, callback, out_format, **kwargs):
        payload = {
            "imageReference": {
                "templateId": templateId,
                "nodeId": node,
                "parameters": kwargs
            },
            "outputFormat": out_format
        }
        if bounds is not None:
            payload["cropGeometryWKT"] = box(*bounds).wkt
        if callback is not None:
            payload["callbackUrl"] = callback
        return payload

    def _rda_tile(self, x, y, rda_id, _id):
        return "{}/tile/{}/{}/{}/{}/{}.tif".format(VIRTUAL_RDA_URL, "idaho-virtual", rda_id, _id, x, y)

    def _collect_urls(self):
        img_md = self.metadata["image"]
        rda_id = self._rda_id
        _id = self._id
        return {(y, x): self._rda_tile(x, y, rda_id, _id)
                for y in xrange(img_md['minTileY'], img_md["maxTileY"]+1)
                for x in xrange(img_md['minTileX'], img_md["maxTileX"]+1)}

class Op(DaskProps):
    def __init__(self, name, interface=None):
        self._operator = name
        self._edges = []
        self._nodes = []

        self._rda_id = None    # The graph ID
        self._rda_graph = None # the RDA graph
        self._rda_meta = None  # Image metadata
        self._rda_stats = None # Display Stats

        self._interface = interface

    @property
    def _id(self):
        return self._nodes[0]._id

    def __call__(self, *args, **kwargs):
        if len(args) > 0 and all([isinstance(arg, gbdx.images.rda_image.RDAImage) for arg in args]):
            return self._rda_image_call(*args, **kwargs)
        self._nodes = [ContentHashedDict({
            "operator": self._operator,
            "_ancestors": [arg._id for arg in args],
            "parameters": OrderedDict({
                k:json.dumps(v, sort_keys=True) if not isinstance(v, basestring) else v
                for k,v in sorted(kwargs.items(), key=lambda x: x[0])})
        })]
        for arg in args:
            self._nodes.extend(arg._nodes)

        self._edges = [ContentHashedDict({"index": idx + 1, "source": arg._nodes[0]._id,
                                          "destination": self._nodes[0]._id})
                       for idx, arg in enumerate(args)]
        for arg in args:
            self._edges.extend(arg._edges)

        for e in chain(self._nodes, self._edges):
            e.populate_id()
        return self

    def _rda_image_call(self, *args, **kwargs):
        out = self(*[arg.rda for arg in args], **kwargs)
        rda_img = gbdx.images.rda_image.RDAImage(out)
        return rda_img

    def graph(self, conn=None):
        if(self._rda_id is not None and
           self._rda_graph is not None):
            return self._rda_graph

        _nodes = [{k:v for k,v in node.items() if not k.startswith('_')} for node in self._nodes]
        graph = {
            "edges": self._edges,
            "nodes": _nodes
        }

        if self._interface is not None and conn is None:
            conn = self._interface.gbdx_futures_session

        if conn is not None:
            self._rda_id = register_rda_graph(conn, graph)
            self._rda_graph = graph
            self._rda_meta = get_rda_metadata(conn, self._rda_id, self._id)
            return self._rda_graph

        return graph

class RDA(object):
    def __getattr__(self, name):
        return Op(name=name, interface=Auth())

# Warn on deprecated module attribute access
from gbdxtools.deprecate import deprecate_module_attr
sys.modules[__name__] = deprecate_module_attr(sys.modules[__name__], deprecated=["Ipe"])
Ipe = RDA


