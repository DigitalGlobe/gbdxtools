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

import collections
import abc

ipe = Ipe()

band_types = {
    'MS': 'WORLDVIEW_8_BAND',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

RDA_DEFAULT_OPTIONS = {
    "band_type": "MS",
    "proj": "EPSG:4326",
    "pansharpen": False,
    "gsd": None,
    "acomp": False,
    "bucket": "idaho-images",
    "product": "toa_reflectance"
    }

class ImageProductNotSupported(KeyError):
    pass

def vendor_id(rec):
    _id = rec['properties']['attributes']['vendorDatasetIdentifier']
    return _id.split(':')[1].split('_')[0]


def find_parts(cat_id, band_type):
    vectors = Vectors()
    aoi = wkt.dumps(box(-180, -90, 180, 90))
    query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
            "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
    _parts = sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id'])
    return _parts


def option_parser_factory(typename, field_names, default_values=()):
    T = collections.namedtuple(typename, field_names)
    T.__new__.__defaults__ = (None,) * len(T._fields)
    if isinstance(default_values, collections.Mapping):
        prototype = T(**{k: v for k, v in default_values.items() if k in T._fields})
    else:
        prototype = T(*default_values[:len(field_names)])
    T.__new__.__defaults__ = tuple(prototype)
    return T


op = option_parser_factory


class OptionParserFactory(type):
    def __new__(cls, name, bases, attrs):
        inst = type.__new__(cls, name, bases, attrs)
        if hasattr(inst, "_type_options") and isinstance(inst._type_options, list):
            if inst._type_options:
                inst = install_parser(inst)
        return inst

    @staticmethod
    def install_parser(inst):
        p = op(c.__name__, inst._type_options, default_options=getattr(inst, "_default_options", []))
        setattr(inst, "parser", p)
        return inst


@six.add_metaclass(abc.ABCMeta)
class RDADriverInterface(object)
    @abc.abstractmethod
    def parse_options(self, inputs):
        raise NotImplementedError

    @abc.abstractmethod
    def configure_options(self, options):
        raise NotImplementedError

    @abc.abstractmethod
    def run_build_meta(self):
        raise NotImplementedError

    @abc.abstractmethod
    def drive(self, target):
        raise NotImplementedError


@six.add_metaclass(OptionParserFactory)
class RDABaseDriver(RDADriverInterface):
    _default_options = {}
    _type_options = []
    _type_defaults = {}

    def __init__(self, rda_id, **kwargs):
        self.rda_id = rda_id
        _options = self.parse_options(kwargs)
        _options = self.configure_options(_options)
        self._options = options

    def parse_options(self, inputs):
        options = self.parser(**{opt: inputs[opt] for opt in self._type_options})
        return options

    @classmethod
    def configure_options(cls, options):
        return options

    @property
    def products(self):
        return self._products

    @property
    def adaptor(self):
        if not (self.products and self.options):
            raise AttributeError("Configure Image products and Options to generator Dask Meta Adaptor")
        try:
            return self.products[self.options["product"]]
        except KeyError as ke:
            raise ImageProductNotImplemented("Specified product not implemented: {}".format(self.options["product"]))

    def run_build_meta(self, target):
        products = target._build_standard_products(self.rda_id, **self.options)
        self._products = products

    def drive(self, target):
        self.run_build_meta(target)
        return cls


class RDABaseImage(IpeImage):
    def __new__(cls, rda_id, **kwargs):
        cls = cls._Adapter(rda_id, **kwargs).drive(cls)
        self = super(RDABaseImage, cls).__new__(cls, cls.adaptor, **kwargs)
        self = self.aoi(**kwargs)
        return self

    def get_product(self, product):
        pass

class IdahoImage(RDABaseImage):
    _Adapter = IdahoAdapter

    @classmethod
    def _build_standard_products(cls, **kwargs):
        pass

class WVImage(RDABaseImage):

