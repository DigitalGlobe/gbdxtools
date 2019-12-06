'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import DemImage
from auth_mock import gbdx
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import dask.array as da

try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class IpeImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_dem_image.yaml', filter_headers=['authorization'])
    def test_dem_image(self):
        bbox = [-109.72, 43.19, -109.49, 43.34]
        img = self.gbdx.dem_image(bbox)
        self.assertTrue(isinstance(img, DemImage))
        assert img.shape == (1, 555, 849)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_dem_image_proj.yaml', filter_headers=['authorization'])
    def test_dem_image_proj(self):
        bbox = [-109.72, 43.19, -109.49, 43.34]
        img = self.gbdx.dem_image(bbox, proj="EPSG:3857")
        self.assertTrue(isinstance(img, DemImage))
        assert img.proj == 'EPSG:3857'

    
