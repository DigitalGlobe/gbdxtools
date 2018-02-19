try:
    import rasterio
    has_rasterio = True
except:
    has_rasterio = False

try:
    from cytoolz import concatv
except ImportError:
    from toolz import concatv

from functools import partial
import os

import dask
from dask.array.core import insert_to_ooc, sharedict
from dask.base import tokenize
from dask.delayed import Delayed

import numpy as np

threads = int(os.environ.get('GBDX_THREADS', 64))
threaded_get = partial(dask.threaded.get, num_workers=threads)


def store(source, target, compute=True, **kwargs):
    """
      Custom implementation of the Dask's `store`. 
      Simplifies the logic and supports passing threaded_get to new dask's compute.
    """
    store_dsks = insert_to_ooc(source, target)
    store_keys = store_dsks.keys()
    store_dsks_mrg = sharedict.merge(*concatv(
        [store_dsks], [source.dask]
    ))

    name = 'store-' + tokenize(*store_keys)
    dsk = sharedict.merge({name: store_keys}, store_dsks_mrg)
    result = Delayed(name, dsk)

    if compute:
        result.compute(get=threaded_get)
        return None
    else:
        return result

class rio_writer(object):
    def __init__(self, dst):
        self.dst = dst
        
    def __setitem__(self, location, chunk):
        window = ((location[1].start, location[1].stop), 
                  (location[2].start, location[2].stop))
        self.dst.write(chunk, window=window)

def to_geotiff(arr, path='./output.tif', proj=None, bands=None, **kwargs):
    assert has_rasterio, "To create geotiff images please install rasterio" 
    if bands is not None:
        arr = arr[bands,...]

    try:
        img_md = arr.ipe.metadata["image"]
        x_size = img_md["tileXSize"]
        y_size = img_md["tileYSize"]
    except (AttributeError, KeyError):
        x_size = kwargs.get("chunk_size", 256)
        y_size = kwargs.get("chunk_size", 256)

    try:
        tfm = kwargs['transform'] if 'transform' in kwargs else arr.affine
    except:
        tfm = None

    dtype = arr.dtype.name if arr.dtype.name != 'int8' else 'uint8' 

    meta = {
        'width': arr.shape[2],
        'height': arr.shape[1],
        'count': arr.shape[0],
        'dtype': dtype,
        'driver': 'GTiff',
        'transform': tfm
    }
    if proj is not None:
        meta["crs"] = {'init': proj}

    if "tiled" in kwargs and kwargs["tiled"]:
        meta.update(blockxsize=x_size, blockysize=y_size, tiled="yes")

    with rasterio.open(path, "w", **meta) as dst:
        writer = rio_writer(dst)
        store(arr, writer)
    
    return path
