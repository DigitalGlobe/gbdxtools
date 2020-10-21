from time import sleep
from io import BytesIO
from functools import lru_cache
import numpy as np
import imageio
import tifffile

from gbdxtools.auth import Auth
conn = Auth().gbdx_connection

# cache tile fetches so we don't re-request tiles from RDA
@lru_cache(maxsize=128)
def load_url(url):
    # try 5 times to get a tile from RDA
    # but sleep an exponentially increasing amount
    # so that RDA autoscaling can catch up
    for i in range(5):
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
            return arr
        except Exception as e:
            sleep(2**i)
    raise TypeError(f"Unable to download tile {url} in 5 retries. \n\n Last fetch error: {e}")
