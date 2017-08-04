from shapely.geometry import shape
import numpy as np
import skimage.transform as tf

def orthorectify(img, z=0):
    xmin, ymin, xmax, ymax = shape(img).bounds
    data = img.read()
    x, xsamp = np.linspace(xmin, xmax, num=data.shape[-1], retstep=True)
    y, ysamp = np.linspace(ymax, ymin, num=data.shape[1], retstep=True)
    xv, yv = np.meshgrid(x, y, indexing='xy')
    if isinstance(z, np.ndarray):
        z = tf.resize(z[0,:,:], data.shape[1:])
    transpix = img.__geo_transform__.rev(xv, yv, z=z, _type=np.float32)[::-1]
    transpix[0,:,:] -= transpix[0,0,0]
    transpix[1,:,:] -= transpix[1,0,0]
    return np.rollaxis(np.dstack([tf.warp(data[b,:,:].squeeze(), transpix, preserve_range=True) for b in xrange(data.shape[0])]), 2, 0)
    
