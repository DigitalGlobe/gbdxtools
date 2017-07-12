from __future__ import print_function
from functools import partial
from collections import Container
import os
import math

from shapely import wkt, ops
from shapely.geometry import box, shape, mapping
from shapely.geometry.base import BaseGeometry


import numpy as np
import pyproj

from gbdxtools.images.meta import DaskMeta, DaskImage, GeoImage
from gbdxtools.ipe.util import RatPolyTransform, AffineTransform
from gbdxtools.ipe.io import to_geotiff


import dask
import threading
num_workers = int(os.environ.get("GBDX_THREADS", 4))
threaded_get = partial(dask.threaded.get, num_workers=num_workers)

try:
    from matplotlib import pyplot as plt
    has_pyplot = True
except:
    has_pyplot = False


class IpeImage(DaskImage, GeoImage):
    _default_proj = "EPSG:4326"

    def __new__(cls, op):
        assert isinstance(op, DaskMeta)
        self = super(IpeImage, cls).create(op)
        self._ipe_op = op
        if self.ipe.metadata["georef"] is None:
            self.__geo_transform__ = RatPolyTransform.from_rpcs(self.ipe.metadata["rpcs"])
        else:
            self.__geo_transform__ = AffineTransform.from_georef(self.ipe.metadata["georef"])
        self.__geo_interface__ = mapping(self._reproject(wkt.loads(self.ipe.metadata["image"]["imageBoundsWGS84"])))
        return self

    @property
    def __daskmeta__(self):
        return self.ipe

    @property
    def ipe(self):
        return self._ipe_op

    @property
    def ipe_id(self):
        return self.ipe._ipe_id

    @property
    def ntiles(self):
        size = float(self.ipe.metadata['image']['tileXSize'])
        return math.ceil((float(self.shape[-1]) / size)) * math.ceil(float(self.shape[1]) / size)

    def plot(self, stretch=[2,98], w=10, h=10, bands=[4,2,1]):
        assert has_pyplot, "To plot images please install matplotlib"
        assert self.shape[1] and self.shape[-1], "No data to plot, dimensions are invalid {}".format(str(self.shape))

        f, ax1 = plt.subplots(1, figsize=(w,h))
        ax1.axis('off')
        if self.shape[0] == 1:
            plt.imshow(data[0,:,:], cmap="Greys_r")
        else:
            data = self.read()
            data = data[bands,...]
            data = data.astype(np.float32)
            data = np.rollaxis(data, 0, 3)
            lims = np.percentile(data, stretch, axis=(0,1))
            for x in xrange(len(data[0,0,:])):
                top = lims[:,x][1]
                bottom = lims[:,x][0]
                data[:,:,x] = (data[:,:,x]-bottom)/float(top-bottom)
            data = np.clip(data,0,1)
            plt.imshow(data,interpolation='nearest')

        plt.show(block=False)

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            image = GeoImage.__getitem__(self, geometry)
            image._ipe_op = self._ipe_op
            return image
        else:
            return super(IpeImage, self).__getitem__(geometry)

    def read(self, bands=None):
        print('Fetching Image... {} {}'.format(self.ntiles, 'tiles' if self.ntiles > 1 else 'tile'))
        return super(IpeImage, self).read(bands=bands)
