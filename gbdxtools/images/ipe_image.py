from __future__ import print_function
import math

from shapely import wkt, ops
from shapely.geometry import box, mapping
from shapely.geometry.base import BaseGeometry

import numpy as np

from gbdxtools.images.meta import DaskMeta, DaskImage, GeoImage, PlotMixin
from gbdxtools.ipe.util import RatPolyTransform, AffineTransform

try:
    xrange
except NameError:
    xrange = range

class IpeImage(DaskImage, GeoImage, PlotMixin):
    _default_proj = "EPSG:4326"

    def __new__(cls, op):
        assert isinstance(op, DaskMeta)
        self = super(IpeImage, cls).create(op)
        self._ipe_op = op
        if self.ipe.metadata["georef"] is None:
            tfm = RatPolyTransform.from_rpcs(self.ipe.metadata["rpcs"])
        else:
            tfm = AffineTransform.from_georef(self.ipe.metadata["georef"])
        img_md = self.ipe.metadata["image"]
        xshift = img_md["minTileX"]*img_md["tileXSize"]
        yshift = img_md["minTileY"]*img_md["tileYSize"]
        self.__geo_transform__ = tfm + (xshift, yshift)
        self.__geo_interface__ = mapping(self._reproject(wkt.loads(self.ipe.metadata["image"]["imageBoundsWGS84"])))
        minx = img_md["minX"] - xshift
        maxx = img_md["maxX"] - xshift
        miny = img_md["minY"] - yshift
        maxy = img_md["maxY"] - yshift

        return self[:, miny:maxy, minx:maxx]

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
    def ipe_metadata(self):
        return self.ipe.metadata

    @property
    def ntiles(self):
        size = float(self.ipe.metadata['image']['tileXSize'])
        return math.ceil((float(self.shape[-1]) / size)) * math.ceil(float(self.shape[1]) / size)

    def __getitem__(self, geometry):
        if isinstance(geometry, BaseGeometry) or getattr(geometry, "__geo_interface__", None) is not None:
            image = GeoImage.__getitem__(self, geometry)
            image._ipe_op = self._ipe_op
            return image
        else:
            result = super(IpeImage, self).__getitem__(geometry)
            image = super(IpeImage, self.__class__).__new__(self.__class__,
                                                            result.dask, result.name, result.chunks,
                                                            result.dtype, result.shape)

            if all([isinstance(e, slice) for e in geometry]) and len(geometry) == len(self.shape):
                xmin, ymin, xmax, ymax = geometry[2].start, geometry[1].start, geometry[2].stop, geometry[1].stop
                xmin = 0 if xmin is None else xmin
                ymin = 0 if ymin is None else ymin
                xmax = self.shape[2] if xmax is None else xmax
                ymax = self.shape[1] if ymax is None else ymax

                g = ops.transform(self.__geo_transform__.fwd, box(xmin, ymin, xmax, ymax))
                image.__geo_interface__ = mapping(g)
                image.__geo_transform__ = self.__geo_transform__ + (xmin, ymin)
            else:
                image.__geo_interface__ = self.__geo_interface__
                image.__geo_transform__ = self.__geo_transform__
            image._ipe_op = self._ipe_op
            return image

    def read(self, bands=None, quiet=False, **kwargs):
        if not quiet:
            print('Fetching Image... {} {}'.format(self.ntiles, 'tiles' if self.ntiles > 1 else 'tile'))
        return super(IpeImage, self).read(bands=bands)
