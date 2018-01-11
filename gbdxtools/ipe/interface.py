import os
import sys
import uuid
import json
from hashlib import sha256
from itertools import chain
from collections import OrderedDict, defaultdict
import threading
from tempfile import NamedTemporaryFile
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    from functools import lru_cache # python 3
except ImportError:
    from cachetools.func import lru_cache

from skimage.io import imread
import pycurl
import numpy as np

import gbdxtools as gbdx
from gbdxtools.ipe.util import IPE_TO_DTYPE
from gbdxtools.ipe.graph import VIRTUAL_IPE_URL, register_ipe_graph, get_ipe_metadata
from gbdxtools.images.meta import DaskMeta
from gbdxtools.auth import Auth

try:
    import signal
    from signal import SIGPIPE, SIG_IGN
except ImportError:
    pass
else:
    signal.signal(SIGPIPE, SIG_IGN)

import warnings
warnings.filterwarnings('ignore')

_curl_pool = defaultdict(pycurl.Curl)
MAX_RETRIES = 5
try:
    basestring
except NameError:
    basestring = str

try:
    xrange
except NameError:
    xrange = range

NAMESPACE_UUID = uuid.NAMESPACE_DNS

def optimize_fetch(dsk, keys=None):
    dsk2 = {}
    if not keys:
        keys = dsk.keys()
    for k in keys:
        if dsk[k][0] is load_url:
            dsk2[k] = (dsk[k][1], (k[1:]))
        else:
            dsk2[k] = dsk[k]
    return dsk2

def load_urls(collection, token, shape=(8,256,256), timeout=0.1):
    mc = pycurl.CurlMulti()
    nhandles = len(collection)
    results = {}
    handles = []
    for url, index in collection:
        _, ext = os.path.splitext(urlparse(url).path)
        _curl = pycurl.Curl()
        _curl.setopt(pycurl.NOSIGNAL, 1)
        _curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(token)])
        _curl.setopt(pycurl.CONNECTTIMEOUT, 30)
        _curl.setopt(pycurl.TIMEOUT, 300)
        _curl.setopt(pycurl.URL, url)
        _curl.fp = NamedTemporaryFile(prefix='gbdxtools', suffix=ext, delete=False)
        _curl.setopt(pycurl.WRITEDATA, _curl.fp.file)
        _curl.url = url
        _curl.index = index

        handles.append(_curl)
        mc.add_handle(_curl)

    while nhandles:
        ret = mc.select(timeout)
        if ret == -1:
            continue
        while True:
            ret, nhandles = mc.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        nqueued, successful, failed = mc.info_read()
        for h in successful:
            h.fp.file.flush()
            h.fp.close()
            print("Success: URL={}, filename={}, info={}".format(h.url, h.fp.name, h.getinfo(pycurl.EFFECTIVE_URL)))
            mc.remove_handle(h)
        for h, errno, errmsg in failed:
            h.fp.file.flush()
            h.fp.close()
            print("Failed: URL={}, filename={}, code={}, message={}".format(h.url, h.fp.name, errno, errmsg))
            mc.remove_handle(h)

    for h in handles:
        try:
            arr = imread(h.fp.name)
            if len(arr) == 3:
                arr = np.rollaxis(arr, 2, 0)
            else:
                arr = np.expand_dims(arr, axis=0)
        except Exception as e:
            print(e)
            arr = np.zeros(shape, dtype=np.float32)
        finally:
            results[h.index] = arr
            h.fp.close()
            os.remove(h.fp.name)
            h.close()
    mc.close()
    return results

@lru_cache(maxsize=128)
def load_url(url, token, shape=(8, 256, 256)):
    """ Loads a geotiff url inside a thread and returns as an ndarray """
    # print("calling load_url ({})".format(url))
    _, ext = os.path.splitext(urlparse(url).path)
    success = False
    for i in xrange(MAX_RETRIES):
        thread_id = threading.current_thread().ident
        _curl = _curl_pool[thread_id]
        _curl.setopt(_curl.URL, url)
        _curl.setopt(pycurl.NOSIGNAL, 1)
        _curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(token)])
        with NamedTemporaryFile(prefix="gbdxtools", suffix=ext, delete=False) as temp: # TODO: apply correct file extension
            _curl.setopt(_curl.WRITEDATA, temp.file)
            _curl.perform()
            code = _curl.getinfo(pycurl.HTTP_CODE)
            try:
                if(code != 200):
                    raise TypeError("Request for {} returned unexpected error code: {}".format(url, code))
                temp.file.flush()
                temp.close()
                arr = imread(temp.name)
                if len(arr.shape) == 3:
                    arr = np.rollaxis(arr, 2, 0)
                else:
                    arr = np.expand_dims(arr, axis=0)
                success = True
                return arr
            except Exception as e:
                print(e)
                _curl.close()
                del _curl_pool[thread_id]
            finally:
                temp.close()
                os.remove(temp.name)

    if success is False:
        arr = np.zeros(shape, dtype=np.float32)
    return arr


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

    def _ipe_image_call(self, *args, **kwargs):
        out = self(*[arg.ipe for arg in args], **kwargs)
        ipe_img = gbdx.images.ipe_image.IpeImage(out)
        return ipe_img

    def graph(self, conn=None):
        if(self._ipe_id is not None and
           self._ipe_graph is not None):
            return self._ipe_graph

        _nodes = [{k:v for k,v in node.items() if not k.startswith('_')} for node in self._nodes]
        graph = {
            "edges": self._edges,
            "nodes": _nodes
        }

        if self._interface is not None and conn is None:
            conn = self._interface.gbdx_futures_session

        if conn is not None:
            self._ipe_id = register_ipe_graph(conn, graph)
            self._ipe_graph = graph
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
            return IPE_TO_DTYPE[data_type]
        except KeyError:
            raise TypeError("Metadata indicates an unrecognized data type: {}".format(data_type))

    @property
    def shape(self):
        img_md = self.metadata["image"]
        return (img_md["numBands"],
                (img_md["maxTileY"] - img_md["minTileY"] + 1)*img_md["tileYSize"],
                (img_md["maxTileX"] - img_md["minTileX"] + 1)*img_md["tileXSize"])

    def _ipe_tile(self, x, y, ipe_id, _id):
        return "{}/tile/{}/{}/{}/{}/{}.tif".format(VIRTUAL_IPE_URL, "idaho-virtual", ipe_id, _id, x, y)

    def _collect_urls(self):
        img_md = self.metadata["image"]
        ipe_id = self._ipe_id
        _id = self._id
        return {(y, x): self._ipe_tile(x, y, ipe_id, _id)
                for y in xrange(img_md['minTileY'], img_md["maxTileY"]+1)
                for x in xrange(img_md['minTileX'], img_md["maxTileX"]+1)}


class Ipe(object):
    def __getattr__(self, name):
        return Op(name=name, interface=Auth())
