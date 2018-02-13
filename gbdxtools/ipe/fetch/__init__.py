import dask.array as da
from dask import optimize
import operator

from gbdxtools.images.meta import DaskMeta
from gbdxtools.ipe.fetch.async.libcurl.select import load_urls as mcfetch
#from gbdxtools.ipe.fetch.async.asyncio.async import load_urls as aiofetch
from gbdxtools.ipe.fetch.threaded.libcurl.easy import load_url as easyfetch

class BaseFetch(object):
    @classmethod
    def __fetch__(cls, *args, **kwargs):
        return cls.__fetcher__(*args, **kwargs)

    @classmethod
    def __dask_optimize__(cls, *args, **kwargs):
        return da.Array.__dask_optimize__(dsk, keys)

class ThreadedBaseFetch(BaseFetch):
    __fetch_type__ = "threaded"
    @classmethod
    def __dask_optimize__(cls, dsk, keys):
        return da.Array.__dask_optimize__(dsk, keys)

def inject_multifetch(sd):
    key, sli = (sd['key'], sd['slice'])
    if len(key) == 5:
        name, token, z, x, y = key
        if isinstance(name, str) and name.startswith('image'):
            return (operator.getitem, 'load_urls', (z, x, y), sli)
    return (operator.getitem, key, sli)

class AsyncBaseFetch(BaseFetch):
    __fetch_type__ = "async"
    @classmethod
    def __dask_optimize__(cls, dsk, keys):
        dsk1, _ = optimize.cull(dsk, keys)
        dsk1['load_urls'] = (cls.__fetch_, [dsk1[key] for key in dsk1.keys() if isinstance(key[0], str) and key[0].startswith('image')])
        dsk2 = {}
        for key, val in dsk1.items():
            if isinstance(key, tuple) and key[0].startswith('image'):
                name, z, x, y = key
                default_fn, url, token, chunks = val
                dsk2[key] = (operator.getitem, "load_urls", (z, x, y))
                collection.append([url, token, (z, x, y)])
            else:
                dsk2[key] = val
        dsk2["load_urls"] = (cls.__fetch__, collection)
        return da.Array.__dask_optimize__(dsk2, keys)

class EasyCurlFetch(ThreadedBaseFetch):
    __fetcher__ = classmethod(easyfetch)

class MultiCurlFetch(AsyncBaseFetch):
    __fetcher__ = classmethod(mcfetch)

#class AsyncioFetch(AsyncBaseFetch):
#    __fetcher__ = classmethod(aiofetch)
