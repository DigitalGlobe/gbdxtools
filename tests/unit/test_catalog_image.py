'''
Unit tests for the gbdxtools.CatalogImage class

See tests/readme.md for more about tests
'''

from gbdxtools import Interface
from gbdxtools import *
from gbdxtools.rda.error import UnsupportedImageType
from auth_mock import gbdx 
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest

from helpers import mockable_interface, gbdx_vcr, \
    WV02_CATID, \
    WV03_VNIR_CATID, \
    WV04_CATID, \
    LANDSAT_ID, \
    SENTINEL_ID

class CatalogImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface() 
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv2.yaml')
    def test_wv2_image(self):
        wv2 = self.gbdx.catalog_image(WV02_CATID)
        self.assertTrue(isinstance(wv2, WV02))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv3.yaml')
    def test_wv3_image(self):
        wv3 = self.gbdx.catalog_image(WV03_VNIR_CATID)
        self.assertTrue(isinstance(wv3, WV03_VNIR))

    @unittest.skip("Need reliable WV01 cat id") 
    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv1.yaml')
    def test_wv1_image(self):
        wv1 = self.gbdx.catalog_image('1020010044CEA300')
        self.assertTrue(isinstance(wv1, WV01))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_landsat.yaml')
    def test_landsat_image(self):
        lsat = self.gbdx.catalog_image(LANDSAT_ID)
        self.assertTrue(isinstance(lsat, LandsatImage))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_sentinel.yaml')
    def test_landsat_image(self):
        sentinel = self.gbdx.catalog_image(SENTINEL_ID)
        self.assertTrue(isinstance(sentinel, Sentinel2))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv4.yaml')
    def test_wv4_image(self):
        wv4 = self.gbdx.catalog_image(WV04_CATID)
        self.assertTrue(isinstance(wv4, WV04))
    
    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_cat_image_unsupported_type.yaml')
    def test_catalog_image_unsupported_type(self):
        with self.assertRaises(Exception) as context:
            img = CatalogImage('MONA_LISA')
