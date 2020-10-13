from gbdxtools import Modis 
import vcr
import unittest
from helpers import mockable_interface, gbdx_vcr

class ModisTest(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_modis_image.yaml', filter_headers=['authorization'])
    def test_modis_image(self):
        cat_id = 'MOD09GA.A2017137.h20v15.006.2017139030449'
        img = Modis(cat_id)
        self.assertTrue(isinstance(img, Modis))
        assert img.shape == (7, 2399, 2399)
        assert img.proj == 'EPSG:54008'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_modis_image_proj.yaml', filter_headers=['authorization'])
    def test_modis_proj(self):
        cat_id = 'MOD09GA.A2017137.h20v15.006.2017139030449'
        img = self.gbdx.modis(cat_id, proj="EPSG:4326")
        self.assertTrue(isinstance(img, Modis))
        assert img.shape == (7, 1219, 6546)
        assert img.proj == 'EPSG:4326'
