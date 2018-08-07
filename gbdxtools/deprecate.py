import sys, warnings
import functools

class GBDXDeprecation(DeprecationWarning):
    pass

warnings.simplefilter("ignore", DeprecationWarning)
warnings.simplefilter("always", GBDXDeprecation)

def deprecation(message):
    warnings.warn(message, GBDXDeprecation)

def deprecate_module_attr(mod, deprecated):
    """Return a wrapped object that warns about deprecated accesses"""
    deprecated = set(deprecated)
    class Wrapper(object):
        def __getattr__(self, attr):
            if attr in deprecated:
                warnings.warn("Property {} is deprecated".format(attr), GBDXDeprecation)

            return getattr(mod, attr)

        def __setattr__(self, attr, value):
            if attr in deprecated:
                warnings.warn("Property {} is deprecated".format(attr), GBDXDeprecation)
            return setattr(mod, attr, value)
    return Wrapper()

def deprecate_class(klass, dep_name):
    @functools.wraps(klass)
    def wrappedklass(*args, **kwargs):
        warnings.simplefilter("ignore", DeprecationWarning)
        warnings.simplefilter("always", GBDXDeprecation)
        warnings.warn("Class {} has been deprecated, use {} instead".format(dep_name, klass.__name__),
                      GBDXDeprecation)
        warnings.simplefilter("default", GBDXDeprecation)
        return klass(*args, **kwargs)
    return wrappedklass
