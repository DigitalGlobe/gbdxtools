from gbdxtools.images.exceptions import DriverConfigurationError, UnsupportedImageProduct
import collections
import abc
import six


RDA_DEFAULT_OPTIONS = {
    "proj": "ESPG:4326",
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


def update_options(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

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

def install_parser(inst):
    default_options = getattr(inst, "__default_options__", {})
    custom_options = getattr(inst, "__image_option_defaults__", {})
    defaults = update_options(default_options, custom_options)
    p = opf(c.__name__ + "Parser", inst.image_option_support, default_options=defaults)
    setattr(inst, "parser", p)
    setattr(inst, "default_options", defaults)
    return inst


class OptionParserFactory(type):
    def __new__(cls, name, bases, attrs):
        inst = type.__new__(cls, name, bases, attrs)
        if hasattr(inst, "image_option_support") and isinstance(inst.image_option_support, list):
            if inst.image_option_support:
                inst = install_parser(inst)
        return inst

@six.add_metaclass(abc.ABCMeta)
class RDADriverInterface(object):
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

    @property
    def payload(self):
        product = self.options["product"]
        if product not in self.products:
            raise UnsupportedImageProduct("Specified product not supported by {}: {}".format(self.target.__name__,
                                                                                                self.options["product"]))
        return self.products[self.options["product"]]

    @payload.setter
    def payload(self, payload):
        if not isinstance(payload, DaskMeta):
            raise DriverPayloadError("To adapt GeoDaskImage, payload must be DaskMeta instance")
        else:
            self._payload = payload

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
        target.__driver__ = self
        target.__supported_options__ = self.image_option_support
        target.__default_options__ = self.default_options
        return target


class IdahoDriver(RDADaskImageDriver):
    __default_options__ = IDAHO_DEFAULT_OPTIONS
    image_option_support = ["proj", "product", "gsd", "bucket", "acomp"]

    @classmethod
    def configure_options(cls, options):
        if options["acomp"] and options["bucket"] != "idaho-images":
            options["product"] = "acomp"
        else:
            options["product"] = "toa_reflectance"
        return options

class WorldViewDriver(RDADaskImagerDriver):
    __default_options__ = WV_MODERN_OPTIONS
    image_option_support = WV_MODERN_OPTIONS.keys()

    @classmethod
    def configure_options(cls, options):
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
            pan_products = target._build_standard_products(self.rda_id, **options)
            pan = pan_products['acomp'] if options["acomp"] else pan_products['toa_reflectance']
            ms = standard_products['acomp'] if options["acomp"] else standard_products['toa_reflectance']
            standard_products["pansharpened"] = ipe.LocallyProjectivePanSharpen(ms, pan)
        self._products = standard_products
        return standard_products


