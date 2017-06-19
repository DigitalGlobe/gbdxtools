import abc
import types
from functools import wraps

from six import add_metaclass
import dask.array as da
import dask

add_metaclass(abc.ABCMeta)
class DaskMeta(object):
    """
    A DaskMeta is an interface for the required attributes for initializing a dask Array
    """
    @abc.abstractproperty
    def dask(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def chunks(self):
        pass

    @abc.abstractproperty
    def dtype(self):
        pass

    @abc.abstractproperty
    def shape(self):
        pass

    def infect(self, target):
        assert isinstance(target, da.Array), "DaskMeta can only be attached to Dask Arrays"
        assert len(target.shape) in [2, 3], "target must be a dask array with 2 or 3 dimensions"
        target.__dict__["__daskmeta__"] = property(lambda s: self, DaskImage.__set_daskmeta__)
        return target


@add_metaclass(abc.ABCMeta)
class DaskImage(da.Array):
    """
    A DaskImage is a 2 or 3 dimension dask array that contains implements the `__daskmeta__` interface.
    """

    @abc.abstractproperty
    def __daskmeta__(self):
        """ Should return a DaskMeta """
        pass

    @__daskmeta__.setter
    def __set_daskmeta__(self, obj):
        self.__dict__["__daskmeta__"] = property(lambda s: obj, self.__set_daskmeta__)

    @classmethod
    def __subclasshook__(cls, C):
        if cls is DaskImage:
            try:
                if(issubclass(C, da.Array)
                   and any("__daskmeta__" in B.__dict__ for B in C.__mro__)):
                    return True
            except AttributeError:
                pass
        return NotImplemented

    def __getattribute__(self, name):
        fn = object.__getattribute__(self, name)
        if(isinstance(fn, types.MethodType)
           and any(name in C.__dict__ for C in self.__class__.__mro__)):
            @wraps(fn)
            def wrapped(*args, **kwargs):
                result = fn(*args, **kwargs)
                if isinstance(result, da.Array):
                    self.__daskmeta__.infect(result)
                return result
            return wrapped
        else:
            return fn

    @classmethod
    def create(cls, dm):
        """
        Given a dask meta object, construct a dask array, attach dask meta object.
        """
        assert isinstance(dm, DaskMeta), "argument must be an instance of a DaskMeta subclass"
        with dask.set_options(array_plugins=[dm.infect]):
            obj = da.Array(dm.dask, dm.name, dm.chunks, dm.dtype, dm.shape)
            obj.__class__ = cls
            return obj
