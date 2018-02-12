import dask.array as da
from dask import optimize
import operator

from gbdxtools.ipe.fetch.async.libcurl.select import load_urls as mcfetch
#from gbdxtools.ipe.fetch.async.asyncio.async import load_urls as aiofetch
from gbdxtools.ipe.fetch.threaded.libcurl.easy import load_url as easyfetch

class AsyncFetcher(da.Array):
    __fetcher__ = mcfetch

    @classmethod
    def fetch(cls, *args, **kwargs):
        return cls.__fetcher__(*args, **kwargs)

    @classmethod
    def __dask_optimize__(cls, dsk, keys):
        dsk1, _ = optimize.cull(dsk, keys)
        collection = []
        dsk2 = {}
        for key, val in dsk1.items():
            if isinstance(key, tuple) and key.startswith('image'):
                name, z, x, y = key
                default_fn, url, token, chunks = val
                dsk2[key] = (operator.getitem, "load_urls", (z, x, y))
                collection.append([url, token, (z, x, y)])
            else:
                dsk2[key] = val
        dsk2["load_urls"] = (cls.fetch, collection)
        return da.Array.__dask_optimize__(dsk2, keys)
