'''
Unit tests for the gbdxtools.CatalogImage class

See tests/readme.md for more about tests
'''

import unittest

from gbdxtools import WV01, WV02, WV03_VNIR, WV04, LandsatImage, Sentinel2

from gbdxtools import CatalogImage

from helpers import mockable_interface, gbdx_vcr, \
    WV01_CATID, \
    WV02_CATID, \
    WV03_VNIR_CATID, \
    WV04_CATID, \
    LANDSAT_ID, \
    SENTINEL_ID

class CatalogImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface() 

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv2.yaml')
    def test_wv2_image(self):
        wv2 = CatalogImage(WV02_CATID)
        self.assertTrue(isinstance(wv2, WV02))

    @unittest.skip("Waiting for image to reorder") 
    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv3.yaml')
    def test_wv3_image(self):
        wv3 = CatalogImage(WV03_VNIR_CATID)
        self.assertTrue(isinstance(wv3, WV03_VNIR))

    @unittest.skip("Waiting for image to reorder") 
    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv1.yaml')
    def test_wv1_image(self):
        wv1 = CatalogImage(WV01_CATID)
        self.assertTrue(isinstance(wv1, WV01))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_landsat.yaml')
    def test_landsat_image(self):
        lsat = CatalogImage(LANDSAT_ID)
        self.assertTrue(isinstance(lsat, LandsatImage))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_sentinel.yaml')
    def test_sentinel2_image(self):
        sentinel = CatalogImage(SENTINEL_ID)
        self.assertTrue(isinstance(sentinel, Sentinel2))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv4.yaml')
    def test_wv4_image(self):
        wv4 = CatalogImage(WV04_CATID)
        self.assertTrue(isinstance(wv4, WV04))
    
    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_unsupported_type.yaml')
    def test_catalog_image_unsupported_type(self):
        with self.assertRaises(Exception) as context:
            img = CatalogImage('MONA_LISA')
