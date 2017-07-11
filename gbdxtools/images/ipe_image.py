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

from gbdxtools.images.meta import DaskMeta, DaskImage
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


class IpeImage(DaskImage, Container):
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
    def affine(self):
        # TODO add check for Ratpoly or whatevs
        return self.__geo_transform__._affine 
        
    @property
    def proj(self):
        return self.__geo_transform__.proj

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


    def aoi(self, **kwargs):
        """ Subsets the IpeImage by the given bounds """
        g = self._parse_geoms(**kwargs)
        if g is None:
            return self
        else:
            return self[g]

    def geotiff(self, **kwargs):
        if 'proj' not in kwargs:
            kwargs['proj'] = self.proj
        return to_geotiff(self, **kwargs)
  
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
        return f, ax1

    def read(self, bands=None):
        """ Reads data from a dask array and returns the computed ndarray matching the given bands """
        print('Fetching Image... {} {}'.format(self.ntiles, 'tiles' if self.ntiles > 1 else 'tile'))
        arr = self
        if bands is not None:
            arr = self[bands, ...]
        return arr.compute(get=threaded_get)


    def _parse_geoms(self, **kwargs):
        """ Finds supported geometry types, parses them and returns the bbox """
        bbox = kwargs.get('bbox', None)
        wkt = kwargs.get('wkt', None)
        geojson = kwargs.get('geojson', None)
        if bbox is not None:
            g =  box(*bbox)
        elif wkt is not None:
            g = wkt.loads(wkt)
        elif geojson is not None:
            g = shape(geojson)
        else:
            return None
        if self.proj is None:
            return g
        else:
            return self._reproject(g)          

    def _reproject(self, geometry, from_proj=None, to_proj=None):
        if from_proj is None:
            from_proj = self._default_proj
        if to_proj is None:
            to_proj = self.proj
        tfm = partial(pyproj.transform, pyproj.Proj(init=from_proj), pyproj.Proj(init=to_proj))
        return ops.transform(tfm, geometry)

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            g = shape(geometry) # convert to proper geometry for the __geo_interface__ case
            assert g in self, "Image does not contain specified geometry"
            bounds = ops.transform(self.__geo_transform__.rev, g).bounds
            image = self[:, bounds[1]:bounds[3], bounds[0]:bounds[2]] # a dask array that implements daskmeta interface (via op)
            image.__geo_interface__ = mapping(g)
            image.__geo_transform__ = self.__geo_transform__ + (bounds[0], bounds[1])
            image._ipe_op = self._ipe_op
            image.__class__ = self.__class__
            return image
        else:
            return super(IpeImage, self).__getitem__(geometry)

    def __contains__(self, geometry):
        return shape(self).contains(geometry)
