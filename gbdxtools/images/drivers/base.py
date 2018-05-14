from gbdxtools.ipe.interface import Ipe
from gbdxtools.images.exceptions import *

import collections
import abc
import six

ipe = Ipe()

RDA_DEFAULT_OPTIONS = {
    "proj": "EPSG:4326",
    "gsd": None
    }

IDAHO_DEFAULT_OPTIONS = {
    "proj": "EPSG:4326",
    "gsd": None,
    "acomp": False,
    "bucket": 'idaho-images',
    "correctionType": "TOAREFLECTANCE",
    "bands": "MS",
    "spec": None
    }

WV_DEFAULT_OPTIONS = {
    "proj": "EPSG:4326",
    "gsd": None,
    "band_type": "pan",
    "correctionType": "DN"
    }

WV_MODERN_OPTIONS = {
    "proj": "EPSG:4326",
    "gsd": None,
    "band_type": "MS",
    "acomp": False,
    "pansharpen": False,
    "correctionType": "TOAREFLECTANCE"
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


class OptionParserFactory(type):
    def __new__(cls, name, bases, attrs):
        inst = type.__new__(cls, name, bases, attrs)
        if hasattr(inst, "image_option_support") and isinstance(inst.image_option_support, collections.Iterable):
            if inst.image_option_support:
                inst = cls.install_parser(inst)
        return inst

    @staticmethod
    def install_parser(inst):
        default_options = getattr(inst, "__default_options__", {})
        custom_options = getattr(inst, "__image_option_defaults__", {})
        defaults = update_options(default_options, custom_options)
        p = opf(inst.__name__ + "Parser", inst.image_option_support, default_values=defaults)
        setattr(inst, "parser", p)
        setattr(inst, "default_options", defaults)
        return inst


class RDADriverInterface(object):
    def parse_options(self, inputs):
        raise NotImplementedError

    def configure_options(self, options):
        raise NotImplementedError

    def build_payload(self):
        raise NotImplementedError

    def drive(self, target):
        raise NotImplementedError

    def payload(self):
        raise NotImplementedError

@six.add_metaclass(OptionParserFactory)
class RDADaskImageDriver(RDADriverInterface):
    __default_options__ = RDA_DEFAULT_OPTIONS
    __image_option_defaults__ = {}
    image_option_support = []

    def __init__(self, rda_id=None, **kwargs):
        self.rda_id = rda_id
        options = kwargs.get("rda_options")
        if not options:
            options = self.parse_options(kwargs)
            options = self.configure_options(options._asdict())
        self._options = options

    def parse_options(self, inputs):
        options = self.parser(**{opt: inputs[opt] for opt in self.image_option_support if opt in inputs})
        return options

    @property
    def options(self):
        if not self._options:
            raise DriverConfigurationError("Image options not provided")
        if isinstance(self._options, dict):
            return self._options
        return self._options._asdict()

    @property
    def graph(self):
        if not self._graph:
            raise DriverConfigurationError("Image graph not configured")
        return self._graph

    @classmethod
    def configure_options(cls, options):
        return options

    @property
    def payload(self):
        return self.graph

    @payload.setter
    def payload(self, payload):
        if not isinstance(payload, DaskMeta):
            raise DriverPayloadError("To adapt GeoDaskImage, payload must be DaskMeta instance")
        else:
            self._payload = payload

    def build_payload(self, target):
        # build_graph should always return an rda graph / dask meta
        graph = target._build_graph(self.rda_id, **self.options)
        self._graph = graph
        return graph

    def drive(self, target):
        if not self.rda_id:
            rda_id = getattr(target, "__rda_id__", None)
            if not rda_id:
                raise AttributeError("RDA Image ID not provided")
            self.rda_id = rda_id
        target.__driver__ = self
        target.__rda_id__ = self.rda_id
        target.__supported_options__ = self.image_option_support
        target.__default_options__ = self.default_options
        self.build_payload(target)
        return target


class IdahoDriver(RDADaskImageDriver):
    __default_options__ = IDAHO_DEFAULT_OPTIONS
    image_option_support = ["proj", "correctionType", "gsd", "bucket", "acomp", "spec"]

    @classmethod
    def configure_options(cls, options):
        if options["acomp"] and options["bucket"] != "idaho-images":
            options["correctionType"] = "ACOMP"
        else:
            options["correctionType"] = "TOAREFLECTANCE"
        return options

class WorldViewDriver(RDADaskImageDriver):
    __default_options__ = WV_MODERN_OPTIONS
    image_option_support = WV_MODERN_OPTIONS.keys()

    @classmethod
    def configure_options(cls, options):
        if options["acomp"]:
            options["correctionType"] = "ACOMP"
        if options["pansharpen"]:
            options["band_type"] = "PANSHARP"
        return options
