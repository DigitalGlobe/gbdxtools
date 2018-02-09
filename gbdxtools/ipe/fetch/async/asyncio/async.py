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
from io import BytesIO

try:
    from urlparse import urlparse, urlsplit
except ImportError:
    from urllib.parse import urlparse, urlsplit

MAX_TRIES = 5
MAX_CONNECTIONS = 100
TIMEOUT = 20

async def consume(q, session):
    await asyncio.sleep(0.1)
    while True:
        try:
            req = await q.get()
            async with session.get(req.url) as response:
                response.raise_for_status()
                result = await response.read()
                req._response = response
                q.task_done()
        except CancelledError as ce:
            break
        except Exception as e:
            req.exceptions.append(e)
            if req.has_retries:
                await asyncio.sleep(0.2)
                await q.put(req)
                q.task_done()
            else:
                q.task_done()

async def produce(q, reqs):
    for req in reqs:
        await q.put(req)

async def fetch(reqmap, session, nconn, batch_size=2000):
    q = asyncio.Queue(maxsize=batch_size)
    consumers = [asyncio.ensure_future(consume(q, session)) for _ in range(nconn)]
    producer = await produce(q, reqmap.values())
    await q.join()
    for fut in consumers:
        fut.cancel()
    return reqmap

async def run_fetch(reqmap, nconn, loop):
    with aiohttp.ClientSession(loop=loop, connector=aiohttp.TCPConnector(limit=nconn), headers=headers) as session:
        results = await fetch(reqmap, session, nconn)
    return results
