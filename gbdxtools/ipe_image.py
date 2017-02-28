from functools import partial, wraps
from itertools import groupby
from collections import defaultdict
from contextlib import contextmanager
from xml.etree import cElementTree as ET
import os.path
import uuid

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

import threading
threaded_get = partial(dask.threaded.get, num_workers=4)

import requests
import pycurl
_curl_pool = defaultdict(pycurl.Curl)

from gbdxtools.ipe.vrt import get_cached_vrt, put_cached_vrt, generate_vrt_template
from gbdxtools.ipe.util import calc_toa_gain_offset
from gbdxtools.ipe.graph import register_ipe_graph
from gbdxtools.ipe.error import NotFound
from gbdxtools.ipe.interface import Ipe
from gbdxtools.auth import Interface
ipe = Ipe()

@delayed
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
        self.interface = Interface.instance()(**kwargs)
        self._idaho_id = idaho_id
        self._node_id = node
        self._level = 0
        self._idaho_md = None
        self._ipe_id = None
        if '_ipe_graphs' in kwargs:
            self._ipe_graphs = kwargs['_ipe_graphs']
        else:
            self._ipe_graphs = self._init_graphs()
        if kwargs.get('_intermediate', False):
            return self 
        self._bounds = self._parse_geoms(**kwargs)
        self._graph_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(self.ipe.graph())))
        self._tile_size = kwargs.get('tile_size', 256)
        with open(self.vrt) as f:
            self._vrt = f.read()
        self._cfg = self._config_dask(bounds=self._bounds)
        super(IpeImage, self).__init__(**self._cfg)

    @property
    def idaho_md(self):
        if self._idaho_md is None:
            self._idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(self._idaho_id)).json()
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
    def vrt(self):
        """ Generates a VRT for the full Idaho image from image metadata and caches locally """
        try:
            vrt = get_cached_vrt(self._idaho_id, self._graph_id, self._level)
        except NotFound:
            template = generate_vrt_template(self.ipe_id, self.ipe_node_id, self._level)
            vrt = put_cached_vrt(self._idaho_id, self._graph_id, self._level, template)

        return vrt

    def read(self, bands=None):
        """ Reads data from a dacsk array and returns the computed ndarray matching the given bands """
        arr = self.compute(get=threaded_get)
        if bands is not None:
            arr = arr[bands, ...]
        return arr

    def aoi(self, **kwargs):
        """ Subsets the IpeImage by the given bounds """
        return IpeImage(self._idaho_id, **kwargs)

    @property
    def metadata(self):
        with self.open() as src:
            meta = src.meta.copy()
            meta.update({
                'width': self.shape[-1],
                'height': self.shape[1]
            })
            if self._bounds is not None:
                (minx, miny, maxx, maxy) = self._bounds
                affine = [c for c in rasterio.transform.from_bounds(minx, miny, maxx, maxy, int(self.shape[-1]), int(self.shape[1]))]
                transform = [affine[2], affine[0], 0.0, affine[5], 0.0, affine[4]]
                meta.update({'transform': Affine.from_gdal(*transform)})

        return meta


    @contextmanager
    def open(self, *args, **kwargs):
        """ A rasterio based context manager for reading the full image VRT """
        with rasterio.open(self.vrt, *args, **kwargs) as src:
            yield src

    def _config_dask(self, bounds=None):
        """ Configures the image as a dask array with a calculated shape and chunk size """
        with self.open() as src:
            nbands = len(src.indexes)
            px_bounds = None
            if bounds is not None:
                window = src.window(*bounds)
                px_bounds = self._pixel_bounds(window, src.block_shapes)
            urls = self._collect_urls(self._vrt, px_bounds=px_bounds)
            cfg = {"shape": tuple([nbands] + [self._tile_size*len(urls[0]), self._tile_size*len(urls)]),
                   "dtype": src.dtypes[0],
                   "chunks": tuple([len(src.block_shapes)] + [self._tile_size, self._tile_size])}
            self._meta = src.meta
        img = self._build_array(urls, bands=nbands, chunks=cfg["chunks"], dtype=cfg["dtype"])
        cfg["name"] = img.name
        cfg["dask"] = img.dask

        return cfg

    def _build_array(self, urls, bands=8, chunks=(1,256,256), dtype=np.float32):
        """ Creates the deferred dask array from a grid of URLs """
        buf = da.concatenate(
            [da.concatenate([da.from_delayed(load_url(url, bands=bands), chunks, dtype) for u, url in enumerate(row)],
                        axis=1) for r, row in enumerate(urls)], axis=2)

        return buf

    def _collect_urls(self, xml, px_bounds=None):
        """
          Finds all intersecting tiles from the source image and intersect a given bounds
          returns a nested list of urls as a grid that represents data chunks in the array
        """
        root = ET.fromstring(xml)
        if px_bounds is not None:
            target = box(*px_bounds)
            for band in root.findall("VRTRasterBand"):
                for source in band.findall("ComplexSource"):
                    rect = source.find("DstRect")
                    xmin, ymin = int(rect.get("xOff")), int(rect.get("yOff"))
                    xmax, ymax = xmin + int(rect.get("xSize")), ymin + int(rect.get("ySize"))
                    if not box(xmin, ymin, xmax, ymax).intersects(target):
                        band.remove(source)

        urls = list(set(item.text for item in root.iter("SourceFilename")
                    if item.text.startswith("http://")))
        chunks = []
        for url in urls:
            head, _ = os.path.splitext(url)
            head, y = os.path.split(head)
            head, x = os.path.split(head)
            head, key = os.path.split(head)
            y = int(y)
            x = int(x)
            chunks.append((x, y, url))

        grid = [[rec[-1] for rec in sorted(it, key=lambda x: x[1])]
                for key, it in groupby(sorted(chunks, key=lambda x: x[0]), lambda x: x[0])]
        return grid

    def _pixel_bounds(self, window, block_shapes, preserve_blocksize=True):
        """ Converts a source window in pixel offsets to pixel bounds for intersecting source tiles """
        if preserve_blocksize:
            window = rasterio.windows.round_window_to_full_blocks(window, block_shapes)
        roi = window.flatten()
        return [roi[0], roi[1], roi[0] + roi[2], roi[1] + roi[3]]

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

        ortho = ipe.GridOrthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=self._idaho_id, objectStore="S3"))
        radiance = ipe.AddConst(ipe.MultiplyConst(ipe.Format(ortho, dataType="4"), constants=radiance_scales), constants=radiance_offsets)
        toa_reflectance = ipe.MultiplyConst(radiance, constants=reflectance_scales)

        return {"ortho": ortho, "radiance": radiance, "toa_reflectance": toa_reflectance}

    def plot(self, stretch=[2,98], w=20, h=10):
        f, ax1 = plt.subplots(1, figsize=(w,w))
        ax1.axis('off')
        if self.metadata['count'] == 1:
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

