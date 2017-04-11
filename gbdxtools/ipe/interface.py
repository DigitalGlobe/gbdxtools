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

NAMESPACE_UUID = uuid.NAMESPACE_DNS

class ContentHashedDict(dict):
    @property
    def _id(self):
        _id = str(uuid.uuid5(NAMESPACE_UUID, self.__hash__()))
        return _id

    def __hash__(self):
        dup = {k:v for k,v in self.items() if k is not "id" and not k.startswith('_')}
        out_str = "".join([e for e in sorted(str(dup)) if e != " "]).strip()
        return sha256(out_str.encode('utf-8')).hexdigest()

    def populate_id(self):
        self.update({"id": self._id})


class Op(object):
    def __init__(self, name):
        self._operator = name
        self._edges = []
        self._nodes = []

    @property
    def _id(self):
        _nodes_str = "".join([e for e in sorted(json.dumps(self._nodes)) if e != " "]).strip()
        return str(uuid.uuid5(NAMESPACE_UUID, _nodes_str))

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

    def graph(self):
        _nodes = [{k:v for k,v in node.items() if not k.startswith('_')} for node in self._nodes]
        return {
            "id": self._id,
            "edges": self._edges,
            "nodes": _nodes
        }

class Ipe(object):
    def __getattr__(self, name):
        return Op(name=name)
