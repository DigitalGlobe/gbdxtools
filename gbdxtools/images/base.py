# BossTiles

# A framework for distributed consumtion and processing of earth imagery
# This framework was designed to provide a  source-agnostic geoimage
# access pipeline driven by an api that provides highly parallel geoimage processing
# methods driven by dask arrays.

# Top level interface is defined by image source classes that define a core
# standard access pattern for the various product types offered defined by the
# source. The access pattern  was designed to be easy to create new data sources
# via a plugin interface that generates source adaptors that take product
# templates and  metadata access classes to generate instances of core
# GeoDaskImage

# To build source access pattern, create an image template that defines
from __future__ import print_function
import json

from gbdxtools import IdahoImage
from gbdxtools.ipe.util import calc_toa_gain_offset
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.vectors import Vectors
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.error import MissingIdahoImages, AcompUnavailable

from shapely import wkt
from shapely.geometry import box

import requests


import abc

ipe = Ipe()

band_types = {
    'MS': 'WORLDVIEW_8_BAND',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

def vendor_id(rec):
    _id = rec['properties']['attributes']['vendorDatasetIdentifier']
    return _id.split(':')[1].split('_')[0]

DEFAULT_OPTIONS = {
    "band_type": "MS",
    "proj": "EPG:4326",
    "pansharpen": False,
    "gsd": None,
    "acomp": False,
    "bucket": "idaho-images"
    }

class ImageProductNotImplemented(KeyError):
    pass

class RDAImageTemplate(object):
    __default_options__ = DEFAULT_OPTIONS
    __products = None

    def get_product(self, product):
        return self.__class__(self.__rda_id__, product)

    @property
    def _product(self):
        try:
            return self._products[self.options["product"]]
        except KeyError as ke:
            raise ImageProductNotImplemented("Specified product not implemented: {}".format(self.options["product"]))

    @property
    def _products(self):
        if not self.__products:
            self.__products = self._set_standard_products(self._rda_id, **self.options)
        return self.__products

    @classmethod
    def _set_standard_products(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def _build_standard_products(cls, **kwargs):
        raise NotImplementedError

    @classmethod
    def _configure_options(cls, **kwargs):
        raise NotImplementedError

class RDABaseImage(IpeImage, RDAImageTemplate):
    def __new__(cls, rda_id, **kwargs):
        cls._rda_id = rda_id
        cls._configure_options(**kwargs)
        cls._set_standard_products(rda_id, **kwargs)
        self = super(RDABaseImage, cls).__new__(cls, cls._product)
        return self.aoi(**kwargs)

    @classmethod
    def __post_create(cls, image, **kwargs):
        return image.aoi(**kwargs)


