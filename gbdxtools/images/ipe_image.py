from __future__ import print_function
from functools import partial
from itertools import groupby
from collections import defaultdict
from contextlib import contextmanager
import os
import os.path
import uuid
import math

from pyproj import Proj

import signal
signal.signal(signal.SIGPIPE, signal.SIG_IGN)

import json
import warnings
warnings.filterwarnings('ignore')

try:
    from io import BytesIO
except ImportError:
    from StringIO import cStringIO as BytesIO

try:
    xrange
except NameError:
    xrange = range

import requests

from shapely.geometry import box, shape
from shapely.wkt import loads
import rasterio
from rasterio.io import MemoryFile
from affine import Affine
try:
    import gdal
except:
    from osgeo import gdal

try:
  from matplotlib import pyplot as plt
  has_pyplot = True
except:
  has_pyplot = False

import dask
import dask.array as da
import dask.bag as db
from dask.delayed import delayed
import numpy as np
from itertools import chain

import threading
num_workers = int(os.environ.get("GBDX_THREADS", 4))
threaded_get = partial(dask.threaded.get, num_workers=num_workers)

import pycurl
_curl_pool = defaultdict(pycurl.Curl)

import requests

from gbdxtools.ipe.vrt import get_cached_vrt, put_cached_vrt, generate_vrt_template
from gbdxtools.ipe.util import calc_toa_gain_offset, timeit, RatPolyTransform
from gbdxtools.ipe.graph import VIRTUAL_IPE_URL, register_ipe_graph, get_ipe_metadata, get_ipe_graph
from gbdxtools.ipe.error import NotFound
from gbdxtools.ipe.interface import Ipe
from gbdxtools.images.meta import DaskImage, DaskMeta
from gbdxtools.auth import Auth
ipe = Ipe()


class IpeImage(DaskImage):
    def __new__(cls, op):
        assert isinstance(op, DaskMeta)
        self = super(IpeImage, cls).create(op)
        self._ipe_op = op
        self._tfm = None
        return self

    @property
    def __daskmeta__(self):
        return self.ipe

    @property
    def __geotransform__(self):
        if self._tfm is None:
            self._tfm = RatPolyTransform.from_rpcs(self.ipe.metadata["rpcs"])
        return self._tfm

    @property
    def ipe(self):
        return self._ipe_op

    def __getitem__(self, geometry):
        pass
