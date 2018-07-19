'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import Radarsat, CatalogImage
from auth_mock import gbdx
import vcr
import unittest

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class RadarsatImageTest(unittest.TestCase):
    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx

    @my_vcr.use_cassette('tests/unit/cassettes/test_radarsat_image.yaml', filter_headers=['authorization'])
    def test_radarsat_image(self):
        _id = '610476'
        img = self.gbdx.catalog_image(_id)
        self.assertTrue(isinstance(img, Radarsat))
        assert img.shape == (1, 42104, 38482)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_radarsat_image_proj.yaml', filter_headers=['authorization'])
    def test_radarsat_image_proj(self):
        _id = '610476'
        img = self.gbdx.catalog_image(_id, proj="EPSG:3857")
        self.assertTrue(isinstance(img, Radarsat))
        assert img.shape == (1, 59725, 56016)
        assert img.proj == 'EPSG:3857'
