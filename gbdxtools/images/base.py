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
    "proj": "ESPG:4326"
    "gsd": None
    }

IDAHO_DEFAULT_OPTIONS = {
    "proj": "EPSG:4326",
    "gsd": None,
    "acomp": False,
    "bucket": None,
    "product": "toa_reflectance"
    }

WV_DEFAULT_OPTIONS = {
    "proj": "ESPG:4326",
    "gsd": None,
    "band_type": "pan",
    "product": "ortho"
    }

WV_MODERN_OPTIONS = {
    "proj": "ESPG:4326",
    "gsd": None,
    "band_type": "MS",
    "acomp": False,
    "pansharpen": False,
    "product": "toa_reflectance"
    }

class DriverConfigurationError(AttributeError):
    pass

class UnsupportedImageProduct(KeyError):
    pass

def update_options(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def vendor_id(rec):
    _id = rec['properties']['attributes']['vendorDatasetIdentifier']
    return _id.split(':')[1].split('_')[0]

def vector_services_query(query, aoi=None):
    vectors = Vectors()
    if not aoi:
        aoi = wkt.dumps(box(-180, -90, 180, 90))
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


opf = option_parser_factory


class OptionParserFactory(type):
    def __new__(cls, name, bases, attrs):
        inst = type.__new__(cls, name, bases, attrs)
        if hasattr(inst, "image_option_support") and isinstance(inst.image_option_support, list):
            if inst.image_option_support:
                inst = install_parser(inst)
        return inst

    @staticmethod
    def install_parser(inst):
        default_options = getattr(inst, "__default_options__", {})
        custom_options = getattr(inst, "__image_option_defaults__", {})
        defaults = update_options(default_options, custom_options)
        p = opf(c.__name__ + "Parser", inst.image_option_support, default_options=defaults)
        setattr(inst, "parser", p)
        setattr(inst, "default_options", defaults)
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
    def build_payload(self):
        raise NotImplementedError

    @abc.abstractmethod
    def drive(self, target):
        raise NotImplementedError

    @abc.abstractproperty
    def payload(self):
        raise NotImplementedError

@six.add_metaclass(OptionParserFactory)
class RDADaskImageDriver(RDADriverInterface):
    __default_options__ = RDA_DEFAULT_OPTIONS
    __image_option_defaults__ = {}
    image_option_support = []

    def __init__(self, rda_id=None, **kwargs):
        self.rda_id = rda_id
        options = kwagrs.get("rda_options")
        if not options:
            options = self.parse_options(kwargs)
            options = self.configure_options(options)
        self._options = options

    def parse_options(self, inputs):
        options = self.parser(**{opt: inputs[opt] for opt in self.image_option_support})
        return options

    @property
    def options(self):
        if not self._options:
            raise DriverConfigurationError("Image product option not provided")
        if isinstance(self._options, dict):
            return self._options
        return self._options._asdict()

    @property
    def products(self):
        if not self._products:
            raise DriverConfigurationError("Image products not configured")
        return self._products

    @classmethod
    def configure_options(cls, options):
        return options

    @payload.setter
    def payload(self, payload):
        if not isinstance(payload, DaskMeta):
            raise DriverPayloadError("To adapt GeoDaskImage, payload must be DaskMeta instance")
        else:
            self._payload = payload

    @property
    def payload(self):
        product = self.options["product"]
        if product not in self.products:
            raise UnsupportedImageProduct("Specified product not supported by {}: {}".format(self.target.__name__,
                                                                                                self.options["product"]))
        return self.products[self.options["product"]]

    def build_payload(self, target):
        products = target._build_standard_products(self.rda_id, **self.options)
        self._products = products
        return products

    def drive(self, target):
        if not self.rda_id:
            rda_id = getattr(target, "__rda_id__", None)
            if not rda_id:
                raise AttributeError("RDA Image ID not provided")
            self.rda_id = rda_id
        self.build_payload(target)
        target._driver = self
        return target


class IdahoDriver(RDABaseDriver):
    __image_option_defaults__ = IDAHO_DEFAULT_OPTIONS
    image_option_support = ["proj", "product", "gsd", "bucket", "acomp"]

    @classmethod
    def configure_options(cls, options):
        if options["acomp"] and options["bucket"] != "idaho-images":
            options["product"] = "acomp"
        else:
            options["product"] = "toa_reflectance"
        return options

class WorldViewDriver(RDABaseDriver):
    __image_option_defaults__ = WV_MODERN_OPTIONS
    image_option_support = WV_MODERN_OPTIONS.keys()

    @classmethod
    def configure_options(self, options):
        if options["acomp"]:
            options["product"] = "acomp"
        if options["pansharpen"]:
            options["band_type"] = "MS"
            options["product"] = "pansharpened"
        return options

    def build_payload(self, target):
        standard_products = super(WorldViewDriver, self).build_payload(target, **self.options)
        if "pansharpen" in self.image_option_support:
            options = self.options.copy()
            options["band_type"] = "pan"
            pan_products = target._build_standard_products(self.rda_id, **options))
            pan = pan_products['acomp'] if options["acomp"] else pan_products['toa_reflectance']
            ms = standard_products['acomp'] if options["acomp"] else standard_products['toa_reflectance']
            standard_products["pansharpened"] = ipe.LocallyProjectivePanSharpen(ms, pan)
        self._products = standard_products
        return standard_products

class RDABaseImage(IpeImage):
    def __new__(cls, rda_id, **kwargs):
        cls = cls._Driver(rda_id, **kwargs).drive(cls)
        self = super(RDABaseImage, cls).__new__(cls, cls._driver.payload, **kwargs)
        return self.__post_new_hook__(**kwargs)

    def __post_new_hook__(self, **kwargs):
        return self.aoi(**kwargs)

    def __default_options__(self):
        return self._driver.default_options

    @property
    def __rda_id__(self):
        return self._driver.rda_id

    @property
    def options(self):
        return self._driver.options

    @property
    def _products(self):
        return self._driver.products

    def get_product(self, product):
        return self.__class__(self.__rda_id__, proj=self.options["proj"], product=product)


class IdahoImage(RDABaseImage):
    _Driver = IdahoDriver

    @property
    def idaho_id(self):
        return self._adapter.rda_id

    @staticmethod
    def _build_standard_products(idaho_id, **options):
        if bucket is None:
            vq = "item_type:IDAHOImage AND id:{}".format(idaho_id)
            result = vector_services_query(vq)
            if result:
                bucket = result[0]["properties"]["attributes"]["tileBucketName"]

        dn_op = ipe.IdahoRead(bucketName=bucket, imageId=idaho_id, objectStore="S3")
        params = ortho_params(proj, gsd=gsd)

        graph = {
            "1b": dn_op,
            "ortho": ipe.Orthorectify(dn_op, **params),
            "acomp": ipe.Format(ipe.Orthorectify(ipe.Acomp(dn_op), **params), dataType="4"),
            "toa_reflectance": ipe.Format(ipe.Orthorectify(ipe.TOAReflectance(dn_op), **params), dataType="4")
        }

        return graph

class WorldViewImage(RDABaseImage):
    _Driver = WVDriver
    _parts = None

    @property
    def cat_id(self):
        return self.__rda_id__

    @property
    def parts(self):
        if self._parts is None:
            self._parts = [IdahoImage(rec['properties']['attributes']['idahoImageId'],
                                      product=self.options["product"],
                                      proj=self.options["proj"],
                                      bucket=rec['properties']['attributes']['bucketName'],
                                      gsd=self.options["gsd"],
                                      acomp=self.options["acomp"])
                           for rec in self._find_parts(self.cat_id, self.options["band_type"])]
        return self._parts

    @staticmethod
    def _find_parts(cat_id, band_type):
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        _parts = vector_services_query(query)
        if not len(_parts):
            raise MissingIdahoImages('Unable to find IDAHO imagery in the catalog: {}'.format(query))
        _id = vendor_id(_parts[0])
        return [p for p in _parts if vendor_id(p) == _id]

    @classmethod
    def _build_standard_products(cls, cat_id, **options):
        graph = {}
        _parts = cls._find_parts(cat_id, band_type)
        _bucket = _parts[0]['properties']['attributes']['bucketName']
        dn_ops = [ipe.IdahoRead(bucketName=p['properties']['attributes']['bucketName'],
                                imageId=p['properties']['attributes']['idahoImageId'],
                                objectStore="S3") for p in _parts]

        mosaic_params = {"Dest SRS Code": proj}
        if gsd is not None:
            mosaic_params["Requested GSD"] = str(gsd)

        ortho_op = ipe.GeospatialMosaic(*dn_ops, **mosaic_params)
        graph.update{"ortho": ortho_op}

        if cls.__type_defaults__.get("product") is "toa_reflectance":
            toa = [ipe.Format(ipe.MultiplyConst(ipe.TOAReflectance(dn), constants=json.dumps([10000])), dataType="1") for dn in dn_ops]
            toa_reflectance_op = ipe.Format(ipe.GeospatialMosaic(*toa, **mosaic_params), dataType="4")
            graph.update({"toa_reflectance": toa_reflectance_op})
        if "acomp" in cls.__type_options__ and acomp:
            if _bucket != 'idaho-images':
                _ops = [ipe.Format(ipe.MultiplyConst(ipe.Acomp(dn), constants=json.dumps([10000])), dataType="1") for dn in dn_ops]
                graph["acomp"] = ipe.Format(ipe.GeospatialMosaic(*_ops, **mosaic_params), dataType="4")
            else:
                raise AcompUnavailable("Cannot apply acomp to this image, data unavailable in bucket: {}".format(_bucket))

        return graph


class WV01(WorldViewImage):
    pass

class WV02(WorldViewImage):
    pass

