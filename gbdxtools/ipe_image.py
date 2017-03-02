from functools import partial
from itertools import groupby
from collections import defaultdict
from contextlib import contextmanager
import os.path
import uuid
import math

import signal
signal.signal(signal.SIGPIPE, signal.SIG_IGN)

import json
import warnings
warnings.filterwarnings('ignore')

try:
    from io import BytesIO
except ImportError:
    from StringIO import cStringIO as BytesIO

import requests

from shapely.geometry import box, shape
from shapely.wkt import loads
import rasterio
from rasterio.io import MemoryFile
from affine import Affine

from matplotlib import pyplot as plt

import dask
import dask.array as da
import dask.bag as db
from dask.delayed import delayed
import numpy as np
from itertools import chain
import threading
threaded_get = partial(dask.threaded.get, num_workers=4)

import requests
import pycurl
_curl_pool = defaultdict(pycurl.Curl)

from gbdxtools.ipe.vrt import get_cached_vrt, put_cached_vrt, generate_vrt_template
from gbdxtools.ipe.util import calc_toa_gain_offset, timeit
from gbdxtools.ipe.graph import VIRTUAL_IPE_URL, register_ipe_graph, get_ipe_metadata
from gbdxtools.ipe.error import NotFound
from gbdxtools.ipe.interface import Ipe
from gbdxtools.auth import Interface as Auth
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
          print("Errored on {} with {}".format(url, e))
          arr = np.zeros([bands,256,256], dtype=np.float32)
          _curl.close()
          del _curl_pool[thread_id]
    return arr

class IpeImage(da.Array):
    """
      Dask based access to ipe based images (Idaho).
    """
    def __init__(self, idaho_id, node="toa_reflectance", **kwargs):
        self.interface = Auth.instance()
        self._gid = idaho_id
        self._node_id = node
        self._level = 0
        self._idaho_md = None
        self._ipe_id = None
        self._ipe_metadata = None
        if '_ipe_graphs' in kwargs:
            self._ipe_graphs = kwargs['_ipe_graphs']
        else:
            self._ipe_graphs = self._init_graphs()
        if kwargs.get('_intermediate', False):
            return
        self._bounds = self._parse_geoms(**kwargs)
        self._graph_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(self.ipe.graph())))
        self._tile_size = kwargs.get('tile_size', 256)
        self._cfg = self._config_dask(bounds=self._bounds)
        super(IpeImage, self).__init__(**self._cfg)

    @property
    def idaho_md(self):
        if self._idaho_md is None:
            self._idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(self._gid)).json()
        return self._idaho_md

    @property
    def ipe(self):
        return self._ipe_graphs[self._node_id]

    @property
    def ipe_id(self):
        if self._ipe_id is None:
            self._ipe_id = register_ipe_graph(self.ipe.graph())
        return self._ipe_id

    @property
    def ipe_node_id(self):
        return self.ipe._nodes[0]._id

    @property
    def ipe_metadata(self):
        if self._ipe_metadata is None:
            self._ipe_metadata = get_ipe_metadata(self.ipe_id, self.ipe_node_id)
        return self._ipe_metadata

    @property
    def vrt(self):
        """ Generates a VRT for the full Idaho image from image metadata and caches locally """
        try:
            vrt = get_cached_vrt(self._gid, self._graph_id, self._level)
        except NotFound:
            nbands = 3 if self._node_id == 'pansharpened' else None
            template = generate_vrt_template(self.ipe_id, self.ipe_node_id, self._level, num_bands=nbands)
            vrt = put_cached_vrt(self._gid, self._graph_id, self._level, template)
        return vrt

    def read(self, bands=None):
        """ Reads data from a dacsk array and returns the computed ndarray matching the given bands """
        arr = self.compute(get=threaded_get)
        if bands is not None:
            arr = arr[bands, ...]
        return arr

    def aoi(self, **kwargs):
        """ Subsets the IpeImage by the given bounds """
        return IpeImage(self._gid, **kwargs)

    @contextmanager
    def open(self, *args, **kwargs):
        """ A rasterio based context manager for reading the full image VRT """
        with rasterio.open(self.vrt, *args, **kwargs) as src:
            yield src

    @timeit
    def _config_dask(self, bounds=None):
        """ Configures the image as a dask array with a calculated shape and chunk size """
        # TODO fix dtype here, used to come from vrt
        meta = self.ipe_metadata
        nbands = meta['image']['numBands']
        urls, shape = self._collect_urls(meta, bounds=bounds)
        cfg = {"shape": tuple([nbands] + list(shape)),
               "dtype": "float32",
               "chunks": tuple([nbands] + [self._tile_size, self._tile_size])}
        img = self._build_array(urls)
        cfg["name"] = img["name"]
        cfg["dask"] = img["dask"]

        return cfg

    def _build_array(self, urls):
        """ Creates the deferred dask array from a grid of URLs """
        name = "image-{}".format(str(uuid.uuid4()))
        buf_dask = {(name, 0, x, y): (load_url, url) for (x, y), url in urls.iteritems()}
        return {"name": name, "dask": buf_dask}

    def _ipe_tile(self, x, y):
        return "{}/tile/{}/{}/{}/{}/{}.tif".format(VIRTUAL_IPE_URL, "idaho-virtual", self.ipe_id, self.ipe_node_id, x, y)

    @timeit
    def _collect_urls(self, meta, bounds=None):
        """
          Finds all intersecting tiles from the source image and intersect a given bounds
          returns a nested list of urls as a grid that represents data chunks in the array
        """
        size = self._tile_size
        if bounds is not None:
            tfm = meta['georef']
            rev = ~Affine.from_gdal(*[tfm["translateX"], tfm["scaleX"], tfm["shearX"], tfm["translateY"], tfm["shearY"], tfm["scaleY"]])
            ul = map(round, rev * (bounds[0], bounds[3]))
            lr = map(round, rev * (bounds[2], bounds[1]))
            offx = (lr[0] - ul[0]) / size
            offy = (lr[1] - ul[1]) / size
            # TODO need to make the minus one holdd for all aoi bounds, for now it matches expected n-urls
            minx, miny, maxx, maxy = map(int, [(ul[0] / size) - 1, (ul[1] / size), (ul[0] / size) + offx, (ul[1] / size) + offy])
        else:
            minx, miny, maxx, maxy = 0, 0, int(math.floor(meta['image']['imageWidth'] / float(size))), int(math.floor(meta['image']['imageHeight'] / float(size)))

        urls = {(y-miny, x-minx): self._ipe_tile(x, y) for y in xrange(miny, maxy + 1) for x in xrange(minx, maxx + 1)}
        return urls, (size*(maxy-miny+1), size*(maxx-minx+1))


    def _parse_geoms(self, **kwargs):
        """ Finds supported geometry types, parses them and returns the bbox """
        bbox = kwargs.get('bbox', None)
        wkt = kwargs.get('wkt', None)
        geojson = kwargs.get('geojson', None)
        if bbox is not None:
            return bbox
        elif wkt is not None:
            return loads(wkt).bounds
        elif geojson is not None:
            return shape(geojson).bounds
        else:
            return None

    def _init_graphs(self):
        meta = self.idaho_md["properties"]
        gains_offsets = calc_toa_gain_offset(meta)
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)

        ortho = ipe.GridOrthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=self._gid, objectStore="S3"))
        radiance = ipe.AddConst(ipe.MultiplyConst(ipe.Format(ortho, dataType="4"), constants=radiance_scales), constants=radiance_offsets)
        toa_reflectance = ipe.MultiplyConst(radiance, constants=reflectance_scales)

        return {"ortho": ortho, "radiance": radiance, "toa_reflectance": toa_reflectance}

    def plot(self, stretch=[2,98], w=20, h=10):
        f, ax1 = plt.subplots(1, figsize=(w,w))
        ax1.axis('off')
        nbands = self.ipe_metadata['image']['numBands']
        if nbands == 1:
            plt.imshow(self[0,:,:], cmap="Greys_r")
        else:
            data = self.read()
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
