'''
Authors: Marc Pfister
Contact: marc.pfister@maxar.com

Unit tests for the DemImage class
'''

from gbdxtools import DemImage
import unittest
from helpers import mockable_interface, gbdx_vcr

class DEMImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()
        cls.bbox = [-109.72, 43.19, -109.49, 43.34]

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_dem_image.yaml')
    def test_dem_image(self):
        img = DemImage(self.bbox)
        self.assertTrue(isinstance(img, DemImage))
        assert img.shape == (1, 555, 849)
        assert img.proj == 'EPSG:4326'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_dem_image_proj.yaml')
    def test_dem_image_proj(self):
        img = DemImage(self.bbox, proj="EPSG:3857")
        self.assertTrue(isinstance(img, DemImage))
        assert img.proj == 'EPSG:3857'

    
