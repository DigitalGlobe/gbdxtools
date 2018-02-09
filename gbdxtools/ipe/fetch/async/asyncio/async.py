import asyncio
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass
import aiohttp
from concurrent.futures import CancelledError, TimeoutError

import numpy as np
from skimage.io import imread

from tempfile import NamedTemporaryFile
import os

MAX_RETRIES = 5
MAX_CONNECTIONS = 100
TIMEOUT = 20

def on_fail(shape=(8, 256, 256), dtype=np.float32):
    return np.zeros(shape, dtype=dtype)

def bytes_to_array(bstring):
    if bstring is None:
        return onfail()
    try:
        fd = NamedTemporaryFile(prefix='gbdxtools', suffix='.tif', delete=False)
        fd.file.write(bstring)
        fd.file.flush()
        fd.close()
        arr = imread(fd.name)
        if len(arr.shape) == 3:
            arr = np.rollaxis(arr, 2, 0)
        else:
            arr = np.expand_dims(arr, axis=0)
    except Exception as e:
        arr = on_fail()
    finally:
        fd.close()
        os.remove(fd.name)
    return arr

async def consume_reqs(qreq, qres, session, max_tries=5):
    await asyncio.sleep(0.1)
    while True:
        try:
            url, index, tries = await qreq.get()
            tries += 1
            async with session.get(url) as response:
                response.raise_for_status()
                bstring = await response.read()
                await qres.put([index, bstring])
                qreq.task_done()
        except CancelledError as ce:
            break
        except Exception as e:
            if tries < max_tries:
                await asyncio.sleep(0.1)
                await qreq.put([url, index, tries])
                qreq.task_done()
            else:
                await qres.put([index, None])
                qreq.task_done()

async def produce_reqs(qreq, reqs):
    for req in reqs:
        await qreq.put(req)

async def process(qres):
    results = {}
    while True:
        try:
            index, payload = await qres.get()
            if not payload:
                arr = on_fail()
            else:
                arr = await loop.run_in_executor(None, bytes_to_array, payload)
            results[index] = arr
            qres.task_done()
        except CancelledError as ce:
            break
    return results

async def fetch(reqs, session, nconn, batch_size=2000, nprocs=10):
    results = {}
    qreq, qres = asyncio.Queue(maxsize=batch_size), asyncio.Queue()
    consumers = [asyncio.ensure_future(consume_reqs(qreq, qres, session)) for _ in range(nconn)]
    producer = await produce_reqs(qreq, reqs)
    processors = [asyncio.ensure_future(process(qres)) for _ in range(nprocs)]
    await qreq.join()
    await qres.join()
    for fut in consumers:
        fut.cancel()
    for fut in processors:
        fut.cancel()
        results.update(fut.result)
    return results

async def run_fetch(reqs, nconn, headers, loop):
    with aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(limit=nconn), headers=headers) as session:
        results = await fetch(reqs, session, nconn)

def load_urls(collection, shape=(8,256,256), max_retries=MAX_RETRIES, loop=None):
    reqs = []
    for url, token, index in collection:
        reqs.append([url, tuple(index), 0])
    headers = {"Authorization": "Bearer {}".format(token)}
    if not loop:
        loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_fetch(reqs, len(reqs), headers, loop))
    loop.run_until_complete(asyncio.sleep(0))
    loop.close()
    return results

