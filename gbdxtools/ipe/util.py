import warnings
import os
import errno
import datetime

import numpy as np

import xml.etree.cElementTree as ET
from xml.dom import minidom
from shapely.geometry import Polygon
import ephem
with warnings.catch_warnings():
    warnings.simplefilter("ignore")

import gbdxtools.ipe.constants as constants


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
import functools

def timeit(func):
    @functools.wraps(func)
    def newfunc(*args, **kwargs):
        startTime = time.time()
        res = func(*args, **kwargs)
        elapsedTime = time.time() - startTime
        print('function [{}] finished in {} seconds'.format(
            func.__name__, elapsedTime))
        return res
    return newfunc
