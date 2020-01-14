'''
Authors: Marc Pfister
Contact: marc.pfister@maxar.com

Unit tests for the Worldview classes
'''

import unittest

from gbdxtools import CatalogImage
from gbdxtools import WV01, WV02, WV03_VNIR, WV03_SWIR, WV04
from gbdxtools.rda.error import AcompUnavailable

from helpers import mockable_interface, gbdx_vcr
from helpers import WV02_CATID, WV03_VNIR_CATID, WV03_SWIR_CATID, WV04_CATID
from helpers import WV02_BBOX

class CatalogImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv_image_default.yaml')
    def test_basic_catalog_image(self):
        img = CatalogImage(WV02_CATID)
        self.assertTrue(isinstance(img, WV02))
        self.assertEqual(img.cat_id, WV02_CATID) 
        self.assertEqual(img.shape, (8, 59907, 11468))
        self.assertEqual(img.proj, 'EPSG:4326')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv_image_acomp.yaml')
    def test_basic_catalog_acomp(self):
        img = CatalogImage(WV02_CATID, acomp=True)
        self.assertTrue(isinstance(img, WV02))
        self.assertEqual(img.cat_id, WV02_CATID)
        self.assertEqual(img.shape, (8, 59907, 11468))
        self.assertEqual(img.proj, 'EPSG:4326')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv_image_default_aoi.yaml')
    def test_cat_image_with_aoi(self):
        img = CatalogImage(WV02_CATID, bbox=WV02_BBOX)
        self.assertEqual(img.cat_id, WV02_CATID)
        self.assertEqual(img.shape, (8, 2323, 2322))
        self.assertEqual(img.proj, 'EPSG:4326')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv_image_proj.yaml')
    def test_cat_image_with_proj(self):
        img = CatalogImage(WV02_CATID, bbox=WV02_BBOX, proj='EPSG:3857')
        self.assertEqual(img.cat_id, WV02_CATID)
        self.assertEqual(img.shape, (8, 3010, 2322))
        self.assertEqual(img.proj, 'EPSG:3857') 

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv_image_aoi.yaml')
    def test_cat_image_aoi(self):
        img = CatalogImage(WV02_CATID)
        self.assertEqual(img.cat_id, WV02_CATID)
        aoi = img.aoi(bbox=WV02_BBOX)
        self.assertEqual(aoi.shape, (8, 2323, 2322))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv_image_pan_band.yaml')
    def test_catalog_image_panchromatic(self):
        img = CatalogImage(WV02_CATID, band_type='Pan')
        self.assertEqual(img.cat_id, WV02_CATID)
        self.assertTrue(isinstance(img, WV02))
        self.assertEqual(img.shape, (1, 239755, 45773))
        self.assertEqual(img.proj, 'EPSG:4326')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv_image_pansharpen.yaml')
    def test_catalog_image_pansharpen(self):
        img = CatalogImage(WV02_CATID, pansharpen=True)
        self.assertTrue(isinstance(img, WV02))
        self.assertEqual(img.cat_id, WV02_CATID)
        self.assertEqual(img.shape, (8, 239755, 45773))
        self.assertEqual(img.proj, 'EPSG:4326')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv3_swir.yaml')
    def test_catalog_image_swir(self):
        img = CatalogImage(WV03_SWIR_CATID)
        self.assertTrue(isinstance(img, WV03_SWIR))
        assert img.cat_id == WV03_SWIR_CATID
        assert img.shape == (8, 3804, 2822)
        assert img.proj == 'EPSG:4326'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv4_image.yaml')
    def test_catalog_image_wv4(self):
        img = CatalogImage(WV04_CATID)
        self.assertTrue(isinstance(img, WV04))
        self.assertEqual(img.shape, (4, 123760, 12792))
        self.assertEqual(img.proj, 'EPSG:4326')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv4_proj.yaml')
    def test_catalog_image_wv4_proj(self):
        img = CatalogImage(WV04_CATID, proj="EPSG:3857")
        self.assertTrue(isinstance(img, WV04))
        self.assertEqual(img.shape, (4, 156535, 12792))
        self.assertEqual(img.proj, 'EPSG:3857')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_wv4_pan.yaml')
    def test_catalog_image_wv4_pan(self):
        img = CatalogImage(WV04_CATID, band_type="pan")
        self.assertTrue(isinstance(img, WV04))
        self.assertEqual(img.shape, (1, 494688, 51014))
        self.assertEqual(img.proj, 'EPSG:4326')

