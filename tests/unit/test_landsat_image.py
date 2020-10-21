'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import LandsatImage
import vcr
import unittest
from helpers import mockable_interface, gbdx_vcr


class IpeImageTest(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_landsat_image.yaml', filter_headers=['authorization'])
    def test_landsat_image(self):
        _id = 'LC80370302014268LGN00'
        img = self.gbdx.landsat_image(_id, bbox=[-109.84, 43.19, -109.59, 43.34])
        self.assertTrue(isinstance(img, LandsatImage))
        assert img.shape == (8, 566, 685)
        assert img.proj == 'EPSG:32612'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_landsat_image_pansharp.yaml', filter_headers=['authorization'])
    def test_landsat_image_pansharpen(self):
        _id = 'LC80370302014268LGN00'
        img = self.gbdx.landsat_image(_id, bbox=[-109.84, 43.19, -109.59, 43.34], pansharpen=True)
        self.assertTrue(isinstance(img, LandsatImage))
        assert img.shape == (8, 1131, 1370)
        assert img.proj == 'EPSG:32612'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_landsat_image_proj.yaml', filter_headers=['authorization'])
    def test_landsat_image_proj(self):
        _id = 'LC80370302014268LGN00'
        img = self.gbdx.landsat_image(_id, bbox=[-109.84, 43.19, -109.59, 43.34], proj="EPSG:4326")
        self.assertTrue(isinstance(img, LandsatImage))
        assert img.shape == (8, 474, 790)
        assert img.proj == 'EPSG:4326'
