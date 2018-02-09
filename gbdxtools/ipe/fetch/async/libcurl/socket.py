import os

import numpy as np
from skimage.io import imread

from tempfile import NamedTemporaryFile
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

import select
import pycurl
try:
    import signal
    from signal import SIGPIPE, SIG_IGN
except ImportError:
    pass
else:
    signal.signal(SIGPIPE, SIG_IGN)


try:
    xrange
except NameError:
    xrange = range

NUM_WORKERS = 5
MAX_RETRIES = 5


def _setup_curl(url, token, index, NOSIGNAL=1, CONNECTTIMEOUT=30, TIMEOUT=300):
    _, ext = os.path.splitext(urlparse(url).path)
    fp = NamedTemporaryFile(prefix='gbdxtools', suffix=ext, delete=False)
    _curl = pycurl.Curl()
    _curl.setopt(pycurl.NOSIGNAL, NOSIGNAL)
    _curl.setopt(pycurl.CONNECTTIMEOUT, CONNECTTIMEOUT)
    _curl.setopt(pycurl.TIMEOUT, TIMEOUT)
    _curl.setopt(pycurl.URL, url)
    _curl.setopt(pycurl.HTTPHEADER, ['Authorization: Bearer {}'.format(token)])
    _curl.setopt(pycurl.WRITEDATA, fp.file)
    _curl.index = index
    _curl.token = token
    _curl.url = url
    return (_curl, fp)

def load_urls(collection, shape=(8,256,256), max_retries=MAX_RETRIES):
    sockets = set()
    socket_events = []
    timeout = 0
    def _fsocket(event, socket, multi, data):
        if event == pycurl.POLL_REMOVE:
            sockets.remove(socket)
        else:
            if socket not in sockets:
                sockets.add(socket)
        socket_events.append((event, multi))

    mc = pycurl.CurlMulti()
    mc.setopt(pycurl.M_SOCKETFUNCTION, _fsocket)
    #mc.setopt(pycurl.M_PIPELINING, True)
    nhandles = len(collection)
    results, cmap = {}, {}
    for url, token, index in collection:
        index = tuple(index)
        _curl, fp = _setup_curl(url, token, index)
        cmap[index] = (_curl, fp)
        mc.add_handle(_curl)

    while (pycurl.E_CALL_MULTI_PERFORM == mc.socket_all()[0]):
        pass

    timeout = mc.timeout()

    nprocessed = 0
    while timeout >= 0:
        (rr, wr, er) = select.select(sockets, sockets, sockets, timeout/1000.0)
        socketSet = set(rr + wr + er)
        if socketSet:
            for s in socketSet:
                while True:
                    (ret, running) = mc.socket_all()
                    if ret != pycurl.E_CALL_MULTI_PERFORM:
                        break
                nq, suc, failed = mc.info_read()
                nprocessed += len(suc)
                for h in suc:
                    _fp = cmap[h.index][-1]
                    _fp.flush()
                    _fp.close()
                    try:
                        arr = imread(_fp.name)
                        if len(arr.shape) == 3:
                            arr = np.rollaxis(arr, 2, 0)
                        else:
                            arr = np.expand_dims(arr, axis=0)
                    except Exception as e:
                        print(e)
                        arr = np.zeros(shape, dtype=np.float32)
                    finally:
                        results[h.index] = arr
                        h.close()
                        mc.remove_handle(h)
                        os.remove(_fp.name)
                for h, err_num, err_msg in failed:
                    print('failed: {}, code={}, msg={}'.format(h.index, err_num, err_msg))
                    _fp = cmap[h.index][-1]
                    _fp.flush()
                    _fp.close()
                    os.remove(_fp.name)
                    h.close()
                    mc.remove_handle(h)
                    _curl, fp = _setup_curl(h.url, h.token, h.index)
                    cmap[h.index] = (_curl, fp)
                    mc.add_handle(_curl)

        else:
            (ret, running) = mc.socket_action(pycurl.SOCKET_TIMEOUT, 0)
        if running == 0:
            break
    mc.close()
    return results
