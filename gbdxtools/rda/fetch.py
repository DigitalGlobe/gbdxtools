import os
from collections import defaultdict
import threading
from tempfile import NamedTemporaryFile
from time import sleep
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    from functools import lru_cache # python 3
except ImportError:
    from cachetools.func import lru_cache

import imageio
import tifffile

from io import BytesIO

import pycurl
import certifi
import numpy as np

#import warnings
#warnings.filterwarnings('ignore')

try:
    basestring
except NameError:
    basestring = str

try:
    xrange
except NameError:
    xrange = range

MAX_RETRIES = 5
#_curl_pool = defaultdict(pycurl.Curl)


from gbdxtools.auth import Auth
conn = Auth().gbdx_connection

@lru_cache(maxsize=128)
def load_url(url, token, shape=(8, 256, 256)):
    success = False
    for i in xrange(MAX_RETRIES):
        try:
            r = conn.get(url)
            r.raise_for_status()
            memfile = BytesIO(r.content)
            if r.headers['Content-Type'] == 'image/tiff':
                arr = tifffile.imread(memfile)
            else:
                arr = imageio.imread(memfile)
            if len(arr.shape) == 3:
                arr = np.rollaxis(arr, 2, 0)
            else:
                arr = np.expand_dims(arr, axis=0)
            success = True
            return arr
        except Exception as e:
            sleep(2**i)

    if success is False:
        raise TypeError("Unable to download tile {} in {} retries. \n\n Last fetch error: {}".format(url, MAX_RETRIES, e))
    return arr

breakpoint()


@lru_cache(maxsize=128)
def load_url_curl(url, token, shape=(8, 256, 256)):
    """ Loads a geotiff url inside a thread and returns as an ndarray """
    _, ext = os.path.splitext(urlparse(url).path)
    success = False
    for i in xrange(MAX_RETRIES):
        thread_id = threading.current_thread().ident
        _curl = _curl_pool[thread_id]
        _curl.setopt(_curl.URL, url)
        _curl.setopt(pycurl.NOSIGNAL, 1)
        # for Windows local certificate errors
        _curl.setopt(pycurl.CAINFO, certifi.where())
        _curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(token)])
        with NamedTemporaryFile(prefix="gbdxtools", suffix=ext, delete=False) as temp: # TODO: apply correct file extension
            _curl.setopt(_curl.WRITEDATA, temp.file)
            _curl.perform()
            code = _curl.getinfo(pycurl.HTTP_CODE)
            content_type = _curl.getinfo(pycurl.CONTENT_TYPE)

            try:
                if(code != 200):
                    raise TypeError("Request for {} returned unexpected error code: {}".format(url, code))
                temp.file.flush()
                temp.close()
                if content_type == 'image/tiff':
                    arr = tifffile.imread(temp.name)
                else:
                    arr = imageio.imread(temp.name)
                if len(arr.shape) == 3:
                    arr = np.rollaxis(arr, 2, 0)
                else:
                    arr = np.expand_dims(arr, axis=0)
                success = True
                return arr
            except Exception as e:
                _curl.close()
                del _curl_pool[thread_id]
                sleep(2**i)
            finally:
                temp.close()
                os.remove(temp.name)

    if success is False:
        raise TypeError("Unable to download tile {} in {} retries. \n\n Last fetch error: {}".format(url, MAX_RETRIES, e))
    return arr
