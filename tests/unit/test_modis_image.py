'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Modis 
from auth_mock import gbdx
import vcr
from os.path import join, isfile, dirname, realpath
import unittest
import dask.array as da

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class ModisTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx

    @my_vcr.use_cassette('tests/unit/cassettes/test_modis_image.yaml', filter_headers=['authorization'])
    def test_modis_image(self):
        cat_id = 'MOD09GA.A2017137.h20v15.006.2017139030449'
        img = Modis(cat_id)
        self.assertTrue(isinstance(img, Modis))
        assert img.shape == (7, 2399, 2399)
        assert img.proj == 'EPSG:54008'

    @my_vcr.use_cassette('tests/unit/cassettes/test_modis_image_proj.yaml', filter_headers=['authorization'])
    def test_modis_proj(self):
        cat_id = 'MOD09GA.A2017137.h20v15.006.2017139030449'
        img = self.gbdx.modis(cat_id, proj="EPSG:4326")
        self.assertTrue(isinstance(img, Modis))
        assert img.shape == (7, 1219, 6546)
        assert img.proj == 'EPSG:4326'
