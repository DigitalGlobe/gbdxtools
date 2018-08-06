import sys, warnings
import functools

def deprecate_module_attr(mod, deprecated):
    """Return a wrapped object that warns about deprecated accesses"""
    deprecated = set(deprecated)
    class Wrapper(object):
        def __getattr__(self, attr):
            if attr in deprecated:
                warnings.warn("Property {} is deprecated".format(attr), DeprecationWarning)

            return getattr(mod, attr)

        def __setattr__(self, attr, value):
            if attr in deprecated:
                warnings.warn("Property {} is deprecated".format(attr), DeprecationWarning)
            return setattr(mod, attr, value)
    return Wrapper()

def deprecate_class(klass, dep_name):
    @functools.wraps(klass)
    def wrappedklass(*args, **kwargs):
        warnings.simplefilter("always", DeprecationWarning)
        warnings.warn("Class {} has been deprecated, use {} instead".format(dep_name, klass.__name__),
                      DeprecationWarning)
        warnings.simplefilter("default", DeprecationWarning)
        return klass(*args, **kwargs)
    return wrappedklass
