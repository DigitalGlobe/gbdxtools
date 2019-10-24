import sys
from gbdxtools.auth import Auth
from gbdxtools.images.template_image import TemplateMeta

# Warn on deprecated module attribute access
from gbdxtools.deprecate import deprecate_module_attr


class Op(TemplateMeta):
    def __init__(self, name, interface=None, **kwargs):
        super(Op, self).__init__(name=name, **kwargs)
        self._rda_id = None     # The graph ID
        self._rda_graph = None  # the RDA graph
        self._rda_meta = None   # Image metadata
        self._rda_stats = None  # Display Stats

        self._interface = interface

    def __call__(self, *args, **kwargs):
        # update template metadata query params
        for k, v in kwargs.items():
            if v is None:
                v = "null"
            self._params.update({k: v})
        return self


class RDA(object):
    def __getattr__(self, name, **kwargs):
        return Op(name=name, interface=Auth(), **kwargs)