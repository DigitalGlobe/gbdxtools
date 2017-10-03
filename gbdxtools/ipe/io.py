import rasterio
import numpy as np

def chunk_to_slice(n, size):
    start = n * 256
    end = start + size
    return start, end

def to_geotiff(arr, path='./output.tif', proj=None, dtype=None, bands=None, **kwargs):
    if dtype is not None:
        dtype = np.dtype(dtype)
    c,h,w = arr.shape
    try:
        tfm = kwargs['transform'] if 'transform' in kwargs else arr.affine
    except:
        tfm = None
    meta = {
        'width': w,
        'height': h,
        'count': c,
        'dtype': arr.dtype.name if dtype is None else dtype.name,
        'driver': 'GTiff',
        'transform': tfm
    }
    if proj is not None:
        meta["crs"] = {'init': proj}
    with rasterio.open(path, "w", **meta) as dst:
        bs, ys, xs = arr.chunks
        for i, y in enumerate(ys):
            for j, x in enumerate(xs):
                ystart,yend = chunk_to_slice(i, y)
                xstart,xend = chunk_to_slice(j, x)
                region = arr[:, ystart:yend, xstart:xend]
                data = region.read(bands=bands, quiet=1)
                if dtype is not None:
                    data = (data - data.min()) * (float(np.iinfo(dtype).max) * data.max())
                    data = data.astype(dtype)
                dst.write(data, window=((ystart, yend), (xstart, xend)))
    return path
