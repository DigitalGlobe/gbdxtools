try:
    import rasterio
    has_rasterio = True
except:
    has_rasterio = False

from functools import partial
import os

import dask
from dask.array import store

import numpy as np

threads = int(os.environ.get('GBDX_THREADS', 64))
threaded_get = partial(dask.threaded.get, num_workers=threads)

class rio_writer(object):
    def __init__(self, dst):
        self.dst = dst
        
    def __setitem__(self, location, chunk):
        window = ((location[1].start, location[1].stop), 
                  (location[2].start, location[2].stop))
        self.dst.write(chunk, window=window)

def to_geotiff(arr, path='./output.tif', proj=None, spec=None, bands=None, **kwargs):
    assert has_rasterio, "To create geotiff images please install rasterio" 
    if bands is not None:
        arr = arr[bands,...]

    try:
        img_md = arr.rda.metadata["image"]
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

    if spec.lower() == 'rgb':

        def stretchblock(offsets, scales, bands, block):
            if len(block[:,0,0]) != 3:
                return block
            for x in range(3):
                offset = offsets[bands[x]] 
                scale = scales[bands[x]] 
                block[x,:,:] = block[x,:,:] * scale + offset 
            return np.clip(block, 0, 255)
                
        arr = arr[arr._rgb_bands,...]
        offsets = arr.display_stats['offset']
        scales = arr.display_stats['scale']
        stretch = partial(stretchblock, offsets, scales, arr._rgb_bands)
        arr = arr.map_blocks(stretch)
        arr = arr.astype(np.uint8)
        dtype = 'uint8'

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
        result = store(arr, writer, compute=False)
        result.compute(get=threaded_get)
    
    return path
