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

import requests
import pycurl
_curl_pool = defaultdict(pycurl.Curl)

from gbdxtools.ipe.vrt import get_cached_vrt, put_cached_vrt, generate_vrt_template
from gbdxtools.ipe.util import calc_toa_gain_offset, timeit
from gbdxtools.ipe.graph import VIRTUAL_IPE_URL, register_ipe_graph, get_ipe_metadata, get_ipe_graph
from gbdxtools.ipe.error import NotFound
from gbdxtools.ipe.interface import Ipe
from gbdxtools.auth import Auth
ipe = Ipe()

def load_url(url, bands=8):
    """ Loads a geotiff url inside a thread and returns as an ndarray """
    thread_id = threading.current_thread().ident
    _curl = _curl_pool[thread_id]
    buf = BytesIO()
    _curl.setopt(_curl.URL, url)
    _curl.setopt(_curl.WRITEDATA, buf)
    _curl.setopt(pycurl.NOSIGNAL, 1)
    _curl.perform()

    with MemoryFile(buf.getvalue()) as memfile:
      try:
          with memfile.open(driver="GTiff") as dataset:
              arr = dataset.read()
      except (TypeError, rasterio.RasterioIOError) as e:
          arr = np.zeros([bands,256,256], dtype=np.float32)
          _curl.close()
          del _curl_pool[thread_id]
    return arr

class DaskImage(da.Array):
    def __init__(self, **kwargs):
        super(DaskImage, self).__init__(**kwargs)
        self.nchips = math.ceil((float(self.shape[-1]) / 256.0) * (float(self.shape[1]) / 256.0))

    def read(self, bands=None):
        """ Reads data from a dask array and returns the computed ndarray matching the given bands """
        print('Fetching Image... {} {}'.format(self.nchips, 'tiles' if self.nchips > 1 else 'tile'))
        arr = self.compute(get=threaded_get)
        if bands is not None:
            arr = arr[bands, ...]
        return arr

    def plot(self, arr=None, stretch=[2,98], w=20, h=10):
        if not has_pyplot:
            print('To plot images please install matplotlib')
            return

        if not self.shape[1] or not self.shape[-1]:
            print('No data to plot, dimensions are invalid {}'.format(str(self.shape)))
            return
        f, ax1 = plt.subplots(1, figsize=(w,h))
        ax1.axis('off')
        data = arr if arr is not None else self.read()
        if self.shape[0] == 1:
            plt.imshow(data[0,:,:], cmap="Greys_r")
        else:
            data = data[[4,2,1],...]
            data = data.astype(np.float32)
            data = np.rollaxis(data, 0, 3)
            lims = np.percentile(data,stretch,axis=(0,1))
            for x in xrange(len(data[0,0,:])):
                top = lims[:,x][1]
                bottom = lims[:,x][0]
                data[:,:,x] = (data[:,:,x]-bottom)/float(top-bottom)
            data = np.clip(data,0,1)
            plt.imshow(data,interpolation='nearest')
        plt.show(block=False)



class IpeImage(DaskImage):
    _ipe_id = None
    _ipe_metadata = None
    _proj = "EPSG:4326"

    def __init__(self, ipe_graph, gid, node="toa_reflectance", **kwargs):
        self.interface = Auth()
        self._gid = gid
        self._node_id = node
        self._dtype = kwargs.get("dtype", "float32")
        if self._node_id == "pansharpened":
            self._dtype = "uint16"
        if "proj" in kwargs:
            self._proj = kwargs["proj"]
        self._ipe_graphs = ipe_graph
        self._tile_size = kwargs.get("tile_size", 256)
        self._cfg = self._config_dask()
        super(IpeImage, self).__init__(**self._cfg)
        bounds = self._parse_geoms(**kwargs)
        if bounds is not None: 
            _cfg = self._aoi_config(bounds)
            super(IpeImage, self).__init__(**_cfg)

    @property
    def ipe(self):
        return self._ipe_graphs[self._node_id]

    @property
    def ipe_id(self):
        if self._ipe_id is None:
            graph = self.ipe.graph()
            try:
                self._ipe_id = get_ipe_graph(self.interface.gbdx_connection, graph['id'])
            except NotFound:
                self._ipe_id = register_ipe_graph(self.interface.gbdx_connection, graph)
        return self._ipe_id

    @property
    def ipe_node_id(self):
        return self.ipe._nodes[0]._id

    @property
    def ipe_metadata(self):
        if self._ipe_metadata is None:
            self._ipe_metadata = get_ipe_metadata(self.interface.gbdx_connection, self.ipe_id, self.ipe_node_id)
        return self._ipe_metadata

    @property
    def vrt(self):
        """ Generates a VRT for the full Idaho image from image metadata and caches locally """
        try:
            vrt = get_cached_vrt(self._gid, self.ipe_id, self._level)
        except NotFound:
            nbands = 3 if self._node_id == 'pansharpened' else None
            template = generate_vrt_template(self.interface.gbdx_connection, self.ipe_id, self.ipe_node_id, self._level, num_bands=nbands)
            vrt = put_cached_vrt(self._gid, self.ipe_id, self._level, template)
        return vrt

    def aoi(self, **kwargs):
        """ Subsets the IpeImage by the given bounds """
        bounds = self._parse_geoms(**kwargs)
        if bounds is None:
            print('AOI bounds not found. Must specify a bbox, wkt, or geojson geometry.')
            return
        cfg = self._aoi_config(bounds, **kwargs)
        return DaskImage(**cfg)

    def _aoi_config(self, bounds, **kwargs):
        tfm = self.ipe_metadata['georef']
        xform = Affine.from_gdal(*[tfm["translateX"], tfm["scaleX"], tfm["shearX"], tfm["translateY"], tfm["shearY"], tfm["scaleY"]])
        args = list(bounds) + [xform]
        roi = rasterio.windows.from_bounds(*args, boundless=True)
        y_start = max(0, roi.row_off)
        y_stop = roi.row_off + roi.num_rows
        x_start = max(0, roi.col_off)
        x_stop = roi.col_off + roi.num_cols
        aoi = self[:, y_start:y_stop, x_start:x_stop]
        return {
            "shape": aoi.shape,
            "dtype": kwargs.get("dtype", aoi.dtype),
            "chunks": aoi._chunks,
            "name": aoi.name,
            "dask": aoi.dask
        }

    @contextmanager
    def open(self, *args, **kwargs):
        """ A rasterio based context manager for reading the full image VRT """
        with rasterio.open(self.vrt, *args, **kwargs) as src:
            yield src

    def _config_dask(self):
        """ Configures the image as a dask array with a calculated shape and chunk size """
        meta = self.ipe_metadata
        nbands = meta['image']['numBands']
        urls, shape = self._collect_urls(meta)
        img = self._build_array(urls)
        cfg = {"shape": tuple([nbands] + list(shape)),
               "dtype": self._dtype,
               "chunks": tuple([nbands] + [self._tile_size, self._tile_size])}
        cfg["name"] = img["name"]
        cfg["dask"] = img["dask"]

        return cfg


    def _build_array(self, urls):
        """ Creates the deferred dask array from a grid of URLs """
        name = "image-{}".format(str(uuid.uuid4()))
        buf_dask = {(name, 0, x, y): (load_url, url) for (x, y), url in urls.items()}
        return {"name": name, "dask": buf_dask}

    def _ipe_tile(self, x, y):
        return "{}/tile/{}/{}/{}/{}/{}.tif".format(VIRTUAL_IPE_URL, "idaho-virtual", self.ipe_id, self.ipe_node_id, x, y)

    def _collect_urls(self, meta):
        """
          Finds all intersecting tiles from the source image and intersect a given bounds
          returns a nested list of urls as a grid that represents data chunks in the array
        """
        size = self._tile_size
        minx, miny, maxx, maxy = 0, 0, int(math.floor(meta['image']['imageWidth'] / float(size))), int(math.floor(meta['image']['imageHeight'] / float(size)))
        urls = {(y-miny, x-minx): self._ipe_tile(x, y) for y in xrange(miny, maxy + 1) for x in xrange(minx, maxx + 1)}
        return urls, (size*(maxy-miny+1), size*(maxx-minx+1))

    def _parse_geoms(self, **kwargs):
        """ Finds supported geometry types, parses them and returns the bbox """
        bbox = kwargs.get('bbox', None)
        wkt = kwargs.get('wkt', None)
        geojson = kwargs.get('geojson', None)
        bounds = None
        if bbox is not None:
            bounds = bbox
        elif wkt is not None:
            bounds = loads(wkt).bounds
        elif geojson is not None:
            bounds = shape(geojson).bounds
        return self._project_bounds(bounds)


    def _project_bounds(self, bounds):
        if bounds is None:
            return None
        if self._proj != 'EPSG:4326':
            p = Proj(init=self._proj)
            bounds = sum((p(bounds[0], bounds[1]), p(bounds[2],bounds[3])), ())
        return bounds
