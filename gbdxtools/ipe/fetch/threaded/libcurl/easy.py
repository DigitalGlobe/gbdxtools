import os
from collections import defaultdict
import threading
from tempfile import NamedTemporaryFile
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    from functools import lru_cache # python 3
except ImportError:
    from cachetools.func import lru_cache

from skimage.io import imread
import pycurl
import numpy as np

import warnings
warnings.filterwarnings('ignore')

try:
    basestring
except NameError:
    basestring = str

try:
    xrange
except NameError:
    xrange = range

MAX_RETRIES = 5
_curl_pool = defaultdict(pycurl.Curl)

@lru_cache(maxsize=128)
def load_url(url, token, shape=(8, 256, 256)):
    """ Loads a geotiff url inside a thread and returns as an ndarray """
    _, ext = os.path.splitext(urlparse(url).path)
    success = False
    for i in xrange(MAX_RETRIES):
        thread_id = threading.current_thread().ident
        _curl = _curl_pool[thread_id]
        _curl.setopt(_curl.URL, url)
        _curl.setopt(pycurl.NOSIGNAL, 1)
        _curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(token)])
        with NamedTemporaryFile(prefix="gbdxtools", suffix=ext, delete=False) as temp: # TODO: apply correct file extension
            _curl.setopt(_curl.WRITEDATA, temp.file)
            _curl.perform()
            code = _curl.getinfo(pycurl.HTTP_CODE)
            try:
                if(code != 200):
                    raise TypeError("Request for {} returned unexpected error code: {}".format(url, code))
                temp.file.flush()
                temp.close()
                arr = imread(temp.name)
                if len(arr.shape) == 3:
                    arr = np.rollaxis(arr, 2, 0)
                else:
                    arr = np.expand_dims(arr, axis=0)
                success = True
                return arr
            except Exception as e:
                if "GBDX_DEBUG" in os.environ:
                    print(e)
                _curl.close()
                del _curl_pool[thread_id]
            finally:
                temp.close()
                os.remove(temp.name)

    if success is False:
        arr = np.zeros(shape, dtype=np.float32)
    return arr
