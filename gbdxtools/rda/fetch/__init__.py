import dask.array as da
from dask import optimization
import operator

from gbdxtools.images.meta import DaskMeta
from gbdxtools.rda.fetch.async.libcurl.select import load_urls as mcfetch
#from gbdxtools.rda.fetch.async.asyncio.async import load_urls as aiofetch
from gbdxtools.rda.fetch.threaded.libcurl.easy import load_url as easyfetch

class BaseFetch(object):
    @staticmethod
    def __fetch__(*args, **kwargs):
        raise NotImplementedError

    @classmethod
    def __dask_optimize__(cls, *args, **kwargs):
        return da.Array.__dask_optimize__(dsk, keys)

class ThreadedBaseFetch(BaseFetch):
    __fetch_type__ = "threaded"
    @classmethod
    def __dask_optimize__(cls, dsk, keys):
        return da.Array.__dask_optimize__(dsk, keys)

class AsyncBaseFetch(BaseFetch):
    __fetch_type__ = "async"
    @classmethod
    def __dask_optimize__(cls, dsk, keys):
        dsk1, _ = optimization.cull(dsk, keys)
        dsk2 = {}
        coll = []
        for key, val in dsk1.items():
            if isinstance(key, tuple) and key[0].startswith('image'):
                name, z, x, y = key
                dfn, url, token, chunk = val
                dsk2[key] = (operator.getitem, "load_urls", (z, x, y))
                coll.append([url, token, (z, x, y)])
            else:
                dsk2[key] = val
        dsk2['load_urls'] = (cls.__fetch__, coll)
        return dsk2

class EasyCurlFetch(ThreadedBaseFetch):
    __fetch__ = staticmethod(easyfetch)

class MultiCurlFetch(AsyncBaseFetch):
    __fetch__ = staticmethod(mcfetch)

#class AsyncioFetch(AsyncBaseFetch):
#    __fetcher__ = classmethod(aiofetch)
