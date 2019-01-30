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
    ''' Write out a geotiff file of the image

    Args:
        path (str): path to write the geotiff file to, default is ./output.tif
        proj (str): EPSG string of projection to reproject to
        spec (str): if set to 'rgb', write out color-balanced 8-bit RGB tif
        bands (list): list of bands to export. If spec='rgb' will default to RGB bands
    
    Returns:
        str: path the geotiff was written to'''
        
    assert has_rasterio, "To create geotiff images please install rasterio" 

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

    if spec is not None and spec.lower() == 'rgb':
        if bands is None:
            bands = arr._rgb_bands
        # skip if already DRA'ed
        if not arr.options['dra']:
            # add the RDA HistogramDRA op to get a RGB 8-bit image
            from gbdxtools.rda.interface import RDA
            rda = RDA()
            dra = rda.HistogramDRA(arr)
            # Reset the bounds and select the bands on the new Dask
            arr = dra.aoi(bbox=arr.bounds)
        arr = arr[bands,...].astype(np.uint8)
        dtype = 'uint8'
    else:
        if bands is not None:
            arr = arr[bands,...]
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
        result.compute(scheduler=threaded_get)
    
    return path
