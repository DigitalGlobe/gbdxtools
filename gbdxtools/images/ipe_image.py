from __future__ import print_function
from functools import partial
from collections import Container

from shapely import wkt, ops
from shapely.geometry import box, shape, mapping
from shapely.geometry.base import BaseGeometry

from gbdxtools.images.meta import DaskMeta, DaskImage
from gbdxtools.ipe.util import RatPolyTransform, shift_func


class IpeImage(DaskImage, Container):
    def __new__(cls, op):
        assert isinstance(op, DaskMeta)
        self = super(IpeImage, cls).create(op)
        self._ipe_op = op
        self.__geo_transform__ = RatPolyTransform.from_rpcs(self.ipe.metadata["rpcs"])
        self.__geo_interface__ = mapping(wkt.loads(self.ipe.metadata["image"]["imageBoundsWGS84"]))
        return self

    @property
    def __daskmeta__(self):
        return self.ipe

    @property
    def ipe(self):
        return self._ipe_op

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            g = shape(geometry) # convert to proper geometry for the __geo_interface__ case
            assert g in self, "Image does not contain specified geometry"
            bounds = ops.transform(self.__geo_transform__.fwd, g).bounds
            image = self[:, bounds[1]:bounds[3], bounds[0]:bounds[2]] # a dask array that implements daskmeta interface (via op)
            image.__geo_interface__ = mapping(g)
            image.__geo_transform__ = self.__geo_transform__ - (bounds[0], bounds[1])
            image.__class__ = self.__class__
            return image
        else:
            return super(IpeImage, self).__getitem__(geometry)

    def __contains__(self, geometry):
        if isinstance(geometry, BaseGeometry):
            return shape(self).contains(geometry)
        else:
            return shape(self).contains(shape(geometry))
