import warnings
import os
import errno
import datetime
from functools import wraps
from collections import Sequence

import numpy as np

import xml.etree.cElementTree as ET
from xml.dom import minidom
from shapely.geometry import Polygon
import ephem
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

import gbdxtools.ipe.constants as constants

def ortho_params(proj):
    ortho_params = {}
    if proj is not None:
        ortho_params["Output Coordinate Reference System"] = proj
        ortho_params["Sensor Model"] = None
        ortho_params["Elevation Source"] = None
        ortho_params["Output Pixel to World Transform"] = None
    return ortho_params

# StackOverflow: http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def calc_toa_gain_offset(meta):
    """
    Compute (gain, offset) tuples for each band of the specified image metadata
    """
    # Set satellite index to look up cal factors
    sat_index = meta['satid'].upper() + "_" + \
                meta['bandid'].upper()

    # Set scale for at sensor radiance
    # Eq is:
    # L = GAIN * DN * (ACF/EBW) + Offset
    # ACF abscal factor from meta data
    # EBW effectiveBandwidth from meta data
    # Gain provided by abscal from const
    # Offset provided by abscal from const
    acf = np.asarray(meta['abscalfactor']) # Should be nbands length
    ebw = np.asarray(meta['effbandwidth'])  # Should be nbands length
    gain = np.asarray(constants.DG_ABSCAL_GAIN[sat_index])
    scale = (acf/ebw)*(gain)
    offset = np.asarray(constants.DG_ABSCAL_OFFSET[sat_index])

    e_sun_index = meta['satid'].upper() + "_" + \
                  meta['bandid'].upper()
    e_sun = np.asarray(constants.DG_ESUN[e_sun_index])
    sun = ephem.Sun()
    img_obs = ephem.Observer()
    img_obs.lon = meta['latlonhae'][1]
    img_obs.lat = meta['latlonhae'][0]
    img_obs.elevation = meta['latlonhae'][2]
    img_obs.date = datetime.datetime.fromtimestamp(meta['img_datetime_obj_utc']['$date']/1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
    sun.compute(img_obs)
    d_es = sun.earth_distance

    ## Pull sun elevation from the image metadata
    #theta_s can be zenith or elevation - the calc below will us either
    # a cos or s in respectively
    #theta_s = float(self.meta_dg.IMD.IMAGE.MEANSUNEL)
    theta_s = 90-float(meta['mean_sun_el'])
    scale2 = (d_es ** 2 * np.pi) / (e_sun * np.cos(np.deg2rad(theta_s)))

    # Return scaled data
    # Radiance = Scale * Image + offset, Reflectance = Radiance * Scale2
    return zip(scale, scale2, offset)

# http://stackoverflow.com/questions/17402323/use-xml-etree-elementtree-to-write-out-nicely-formatted-xml-files
def prettify(elem):
    """
    Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="\t")

import time

def timeit(func):
    @wraps(func)
    def newfunc(*args, **kwargs):
        startTime = time.time()
        res = func(*args, **kwargs)
        elapsedTime = time.time() - startTime
        print('function [{}] finished in {} seconds'.format(
            func.__name__, elapsedTime))
        return res
    return newfunc


import numpy as np
from numpy.linalg import pinv

class RatPolyTransform(object):
    def __init__(self, A, B, offset, scale, px_offset, px_scale):
        self._A = A
        self._B = B
        self._offset = offset
        self._scale = scale
        self._px_offset = px_offset
        self._px_scale = px_scale
        self._offscl = np.vstack([offset, scale])
        self._offscl_rev = np.vstack([-offset/scale, 1.0/scale])
        self._px_offscl_rev = np.vstack([px_offset, px_scale])
        self._px_offscl = np.vstack([-px_offset/px_scale, 1.0/px_scale])

        self._A_rev = np.dot(pinv(np.dot(np.transpose(A), A)), np.transpose(A))
        # only using the numerator (more dynamic range for the fit?)
        # self._B_rev = np.dot(pinv(np.dot(np.transpose(B), B)), np.transpose(B))

    def fwd(self, lng, lat, z=0):
        coord = np.asarray([lng, lat, z])
        normed = np.sum(self._offscl * np.vstack([np.ones(coord.shape), coord]), axis=0)
        X = self._rpc(normed)
        result = np.dot(self._A, X) / np.dot(self._B, X)
        return np.int32(np.sum(self._px_offscl_rev * np.vstack([np.ones(result.shape), result]), axis=0))


    def rev(self, x, y, z=None):
        coord = np.asarray([x, y])
        normed = np.sum(self._px_offscl * np.vstack([np.ones(coord.shape), coord]), axis=0)
        coord = np.dot(self._A_rev, normed)[[2,1,3]] # likely unstable
        return np.sum(self._offscl_rev * np.vstack([np.ones(coord.shape), coord]), axis=0)

    def _rpc(self, x):
        L, P, H = x[0], x[1], x[2]
        return np.asarray([1.0, L, P, H, L*P, L*H, P*H, L**2, P**2, H**2,
                           L*P*H, L**3, L*(P**2), L*(H**2), (L**2)*P, P**3, P*(H**2),
                           (L**2)*H, (P**2)*H, H**3])

    def __add__(self, other):
        if isinstance(other, Sequence) and len(other) == 2:
            shift = np.asarray(other)
            return RatPolyTransform(self._A, self._B, self._offset, self._scale, self._px_offset + shift, self._px_scale)
        else:
            raise NotImplemented

    def __sub__(self, other):
        try:
            return self.__add__(-other)
        except:
            return self.__add__([-e for e in other])


    @classmethod
    def from_rpcs(cls, rpcs):
        P = np.vstack([np.asarray(rpcs["lineNumCoefs"]),
                       np.asarray(rpcs["sampleNumCoefs"])])
        Q = np.vstack([np.asarray(rpcs["lineDenCoefs"]),
                       np.asarray(rpcs["sampleDenCoefs"])])

        scale = np.asarray([1.0/rpcs["lonScale"],
                            1.0/rpcs["latScale"],
                            1.0/rpcs["heightScale"]])
        offset = np.asarray([-rpcs["lonOffset"],
                             -rpcs["latOffset"],
                             -rpcs["heightOffset"]])*scale

        px_scale = np.asarray([rpcs["lineScale"], rpcs["sampleScale"]])
        px_offset = np.asarray([rpcs["lineOffset"], rpcs["sampleOffset"]])

        return cls(P, Q, offset, scale, px_offset, px_scale)


def shift_func(offset):
    def decorator(wrapped):
        @wraps(wrapped)
        def fn(*args):
            return wrapped(*[arg + offset for arg,offset in zip(args, offset)])
        return fn
    return decorator
