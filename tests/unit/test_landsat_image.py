'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import LandsatImage
from auth_mock import gbdx
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import dask.array as da

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

    @my_vcr.use_cassette('tests/unit/cassettes/test_landsat_image.yaml', filter_headers=['authorization'])
    def test_landsat_image(self):
        _id = 'LC80370302014268LGN00'
        img = self.gbdx.landsat_image(_id, bbox=[-109.84, 43.19, -109.59, 43.34])
        self.assertTrue(isinstance(img, LandsatImage))
        assert img.shape == (8, 566, 685)
        assert img.proj == 'EPSG:32612'

    @my_vcr.use_cassette('tests/unit/cassettes/test_landsat_image_pansharp.yaml', filter_headers=['authorization'])
    def test_landsat_image_pansharpen(self):
        _id = 'LC80370302014268LGN00'
        img = self.gbdx.landsat_image(_id, bbox=[-109.84, 43.19, -109.59, 43.34], pansharpen=True)
        self.assertTrue(isinstance(img, LandsatImage))
        assert img.shape == (8, 1131, 1370)
        assert img.proj == 'EPSG:32612'

    @my_vcr.use_cassette('tests/unit/cassettes/test_landsat_image_proj.yaml', filter_headers=['authorization'])
    def test_landsat_image_proj(self):
        _id = 'LC80370302014268LGN00'
        img = self.gbdx.landsat_image(_id, bbox=[-109.84, 43.19, -109.59, 43.34], proj="EPSG:4326")
        self.assertTrue(isinstance(img, LandsatImage))
        assert img.shape == (8, 474, 790)
        assert img.proj == 'EPSG:4326'
