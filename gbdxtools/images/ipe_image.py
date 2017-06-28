from __future__ import print_function
from functools import partial
from collections import Container

from shapely import wkt, ops
from shapely.geometry import box, shape, mapping
from shapely.geometry.base import BaseGeometry

import pyproj

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
    def proj(self):
        return self.__geo_transform__.proj

    @property
    def __daskmeta__(self):
        return self.ipe

    @property
    def ipe(self):
        return self._ipe_op

    def aoi(self, **kwargs):
        """ Subsets the IpeImage by the given bounds """
        g = self._parse_geoms(**kwargs)
        assert (g is not None) and (g in self), 'AOI bounds not found. Must specify a bbox, wkt, or geojson geometry that is within the image'
        return self[g]

    def _parse_geoms(self, **kwargs):
        """ Finds supported geometry types, parses them and returns the bbox """
        bbox = kwargs.get('bbox', None)
        wkt = kwargs.get('wkt', None)
        geojson = kwargs.get('geojson', None)
        proj = kwargs.get('proj', "EPSG:4326")
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
            tfm = partial(pyproj.transform, pyproj.Proj(init=proj), pyproj.Proj(init=self.proj))
            return ops.transform(tfm, g)

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
        return shape(self).contains(shape(geometry))
