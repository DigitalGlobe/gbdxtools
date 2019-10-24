'''
Unit tests for the generic image class functionality
'''

from gbdxtools import CatalogImage
from shapely.geometry import shape
from shapely.affinity import translate
from auth_mock import gbdx 
import vcr
import tempfile
import unittest

import numpy as np 

def mock_fetch(*args, **kwargs):
    return np.ones((8,256,256))

def apply_mock(dsk):
    for k,v in dsk.dask.dicts.items():
        for k2, v2 in v.items():
            if k2[0].split('-')[0] == 'image':
                dsk.dask.dicts[k][k2] = (mock_fetch,)
    return dsk
            
def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class ImageFetchTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_fetch.yaml', filter_headers=['authorization'])
    def test_image_fetch(self):
        wv2 = CatalogImage('1030010076B8F500')
        aoi = wv2.aoi(bbox=[-104.98815365500539, 39.71459029774345, -104.98317715482573, 39.71956679792311])
        aoi = apply_mock(aoi)
        arr = aoi.read()
        self.assertEqual(arr.shape, aoi.shape)
        rgb = aoi.rgb()
        self.assertEqual(rgb.shape, (256,256,3))
        ndvi = aoi.ndvi()
        self.assertEqual(ndvi.shape, (256,256))
