from shapely.geometry import shape
import numpy as np
import skimage.transform as tf

def orthorectify(img, z=0):
    # TODO: potientially reproject
    xmin, ymin, xmax, ymax = shape(img).bounds
    data = img.read()
    gsd = max((xmax-xmin)/data.shape[2], (ymax-ymin)/data.shape[1])
    print("gsd:", gsd)
    x = np.linspace(xmin, xmax, num=int((xmax-xmin)/gsd))
    y = np.linspace(ymax, ymin, num=int((ymax-ymin)/gsd))
    xv, yv = np.meshgrid(x, y, indexing='xy')
    if isinstance(z, np.ndarray):
        # TODO: potentially reproject
        z = tf.resize(z[0,:,:], data.shape[1:])
    transpix = img.__geo_transform__.rev(xv, yv, z=z, _type=np.float32)[::-1]
    return np.rollaxis(np.dstack([tf.warp(data[b,:,:].squeeze(), transpix, preserve_range=True) for b in xrange(data.shape[0])]), 2, 0)
