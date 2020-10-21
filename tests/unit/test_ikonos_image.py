'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import IkonosImage, CatalogImage
import vcr
import unittest
from helpers import mockable_interface, gbdx_vcr


class GE01ImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_ikonos_image.yaml', filter_headers=['authorization'])
    def test_ikonos_image(self):
        _id = '2001110218231680000010116110'
        img = self.gbdx.catalog_image(_id, bbox=[-111.96084176146779, 36.627666371883, -111.91772282506821, 36.670785308282575])
        self.assertTrue(isinstance(img, IkonosImage))
        assert img.shape == (4, 1500, 1500)
        assert img.proj == 'EPSG:4326'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_ikonos_image_pansharpen.yaml', filter_headers=['authorization'])
    def test_ikonos_image_pansharpen(self):
        _id = '2013052717574940000011621174'
        img = self.gbdx.catalog_image(_id, pansharpen=True, bbox=[-104.89514954388144, 39.59212288111695, -104.87939038753511, 39.60903377365575])
        self.assertTrue(isinstance(img, IkonosImage))
        assert img.shape == (4, 2353, 2193)
        assert img.proj == 'EPSG:4326'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_ikonos_image_proj.yaml', filter_headers=['authorization'])
    def test_ikonos_image_proj(self):
        _id = '2001110218231680000010116110'
        img = self.gbdx.catalog_image(_id, proj="EPSG:3857")
        self.assertTrue(isinstance(img, IkonosImage))
        assert img.shape == (4, 33624, 4870)
        assert img.proj == 'EPSG:3857'
