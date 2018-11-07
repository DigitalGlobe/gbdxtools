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

import pycurl

from skimage.io import imread
import numpy as np

import os
from collections import deque
try:
    import signal
    from signal import SIGPIPE, SIG_IGN
except ImportError:
    pass
else:
    signal.signal(SIGPIPE, SIG_IGN)

NUM_WORKERS = 5
MAX_RETRIES = 5

def _on_fail(shape=(8, 256, 256), dtype=np.float32):
    return np.zeros(shape, dtype=dtype)

def _load_data(fp):
    try:
        arr = imread(fp)
        if len(arr.shape) == 3:
            arr = np.rollaxis(arr, 2, 0)
        else:
            arr = np.expand_dims(arr, axis=0)
    except Exception as e:
        arr = _on_fail()
    finally:
        os.remove(fp)
    return arr

def _init_curl(NOSIGNAL=1, CONNECTTIMEOUT=120, TIMEOUT=300):
    _curl = pycurl.Curl()
    _curl.setopt(pycurl.NOSIGNAL, NOSIGNAL)
    _curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTTIMEOUT)
    _curl.setopt(pycurl.TIMEOUT, TIMEOUT)
    return _curl

def _load_curl(url, token, index, _curl):
    _, ext = os.path.splitext(urlparse(url).path)
    fd = NamedTemporaryFile(prefix='gbdxtools', suffix=ext, delete=False)
    _curl.setopt(pycurl.WRITEDATA, fd.file)
    _curl.setopt(pycurl.URL, url)
    _curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(token)])
    _curl.index = index
    _curl.token = token
    _curl.url = url
    _curl.fd = fd
    return _curl

def _fd_handler(fd, delete=True):
    fd.flush()
    fd.close()
    if delete:
        os.remove(fd.name)

def _cleanup(crec, cmulti):
    for _curl in crec:
        _curl.close()
    cmulti.close()

def load_urls(collection, max_workers=64, max_retries=MAX_RETRIES, shape=(8,256,256),
              NOSIGNAL=1, CONNECTTIMEOUT=120, TIMEOUT=300):
    ntasks = len(collection)
    taskq = deque(collection)
    crec = [_init_curl() for _ in range(min(max_workers, ntasks))]
    curlq = deque(crec)
    runcount = defaultdict(int)
    results = defaultdict(_on_fail)

    cmulti = pycurl.CurlMulti()
    nprocessed = 0
    while ntasks > nprocessed:
        while taskq and curlq:
            url, token, index = taskq.popleft()
            index = tuple(index)
            _curl = curlq.popleft()
            _curl = _load_curl(url, token, index, _curl)

            # increment attempt number and add to multi
            runcount[index] += 1
            cmulti.add_handle(_curl)

        while True:
            ret, nhandles = cmulti.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break

        while True:
            nq, suc, failed = cmulti.info_read()
            for _curl in suc:
                results[_curl.index] = _curl.fd.name
                _fd_handler(_curl.fd, delete=False)
                _curl.fd = None
                cmulti.remove_handle(_curl)
                curlq.append(_curl)
                nprocessed += 1
            for _curl, err_num, err_msg in failed:
                _fd_handler(_curl.fd)
                _curl.fd = None
                if runcount[_curl.index] < max_retries:
                    taskq.append([_curl.url, _curl.token, _curl.index])
                else:
                    nprocessed += 1
                cmulti.remove_handle(_curl)
                curlq.append(_curl)
            if nq == 0:
                break

    _cleanup(crec, cmulti)
    return {idx: _load_data(results[idx]) if idx in results else _on_fail() for idx in runcount.keys()}


