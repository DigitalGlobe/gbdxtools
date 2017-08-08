'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import CatalogImage, WV02, WV03_VNIR
from auth_mock import get_mock_gbdx_session
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import rasterio

try:
    from urlparse import urlparse
except: 
    from urllib.parse import urlparse

# How to use the mock_gbdx_session and vcr to create unit tests:
# 1. Add a new test that is dependent upon actually hitting GBDX APIs.
# 2. Decorate the test with @vcr appropriately
# 3. Replace "dummytoken" with a real gbdx token
# 4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
# 5. Replace the real gbdx token with "dummytoken" again
# 6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class CatalogImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token='dymmytoken')
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        #cls.gbdx = Interface()
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_default.yaml', filter_headers=['authorization'])
    def test_basic_catalog_image(self):
        _id = '104001002838EC00'
        img = self.gbdx.catalog_image(_id)
        self.assertTrue(isinstance(img, WV03_VNIR))
        assert img.cat_id == _id
        assert img.shape == (8, 79386, 10889)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_default_aoi.yaml', filter_headers=['authorization'])
    def test_cat_image_with_aoi(self):
        _id = '104001002838EC00'
        img = self.gbdx.catalog_image(_id, bbox=[-85.81455230712892,10.416235163695223,-85.77163696289064,10.457089934231618])
        assert img.cat_id == _id
        assert img.shape == (8, 3036, 3189)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_proj.yaml', filter_headers=['authorization'])
    def test_cat_image_with_proj(self):
        _id = '104001002838EC00'
        img = CatalogImage(_id, bbox=[-85.81455230712892,10.416235163695223,-85.77163696289064,10.457089934231618], proj='EPSG:3857')
        assert img.cat_id == _id
        assert img.shape == (8, 3059, 3160)
        assert img.proj == 'EPSG:3857' 

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_aoi.yaml', filter_headers=['authorization'])
    def test_cat_image_aoi(self):
        _id = '104001002838EC00'
        img = CatalogImage(_id)
        assert img.cat_id == _id
        aoi = img.aoi(bbox=[-85.81455230712892,10.416235163695223,-85.77163696289064,10.457089934231618])
        assert aoi.shape == (8, 3036, 3189)

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_pan_band.yaml', filter_headers=['authorization'])
    def test_catalog_image_panchromatic(self):
        _id = '104001002838EC00'
        img = self.gbdx.catalog_image(_id, band_type='Pan')
        self.assertTrue(isinstance(img, WV03_VNIR))
        assert img.cat_id == _id
        assert img.shape == (1, 317959, 43511)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_pansharpen.yaml', filter_headers=['authorization'])
    def test_catalog_image_pansharpen(self):
        _id = '104001002838EC00'
        img = self.gbdx.catalog_image(_id, pansharpen=True)
        self.assertTrue(isinstance(img, WV03_VNIR))
        assert img.cat_id == _id
        assert img.shape == (8, 317959, 43511)
        assert img.proj == 'EPSG:4326' 

