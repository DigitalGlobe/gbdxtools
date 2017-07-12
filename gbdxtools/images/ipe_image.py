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

    @property
    def rgb(self):
        return [4,2,1]

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            image = GeoImage.__getitem__(self, geometry)
            image._ipe_op = self._ipe_op
            return image
        else:
            image = super(IpeImage, self).__getitem__(geometry)
            image.__geo_interface__ = self.__geo_interface__
            image.__geo_transform__ = self.__geo_transform__
            image._ipe_op = self._ipe_op
            image.__class__ = self.__class__ 
            return image

    def read(self, bands=None):
        print('Fetching Image... {} {}'.format(self.ntiles, 'tiles' if self.ntiles > 1 else 'tile'))
        return super(IpeImage, self).read(bands=bands)
