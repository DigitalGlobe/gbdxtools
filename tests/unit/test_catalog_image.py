'''
Unit tests for the gbdxtools.CatalogImage class
'''

from gbdxtools import Interface
from gbdxtools import *
from gbdxtools.ipe.error import UnsupportedImageType
from auth_mock import get_mock_gbdx_session
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest

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

    @my_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv2.yaml', filter_headers=['authorization'])
    def test_wv2_image(self):
        wv2 = CatalogImage('1030010076B8F500')
        self.assertTrue(isinstance(wv2, WV02))

    @my_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv3.yaml', filter_headers=['authorization'])
    def test_wv3_image(self):
        wv3 = CatalogImage('10400100343F3D00')
        self.assertTrue(isinstance(wv3, WV03_VNIR))

    @my_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv1.yaml', filter_headers=['authorization'])
    def test_wv1_image(self):
        wv1 = CatalogImage('1020010044CEA300')
        self.assertTrue(isinstance(wv1, WV01))

    @my_vcr.use_cassette('tests/unit/cassettes/test_cat_image_landsat.yaml', filter_headers=['authorization'])
    def test_landsat_image(self):
        lsat = CatalogImage('LC80380302013160LGN00')
        self.assertTrue(isinstance(lsat, LandsatImage))
    
    def test_catalog_image_err(self):
        try:
            img = CatalogImage('XXXX')
        except:
            pass

    #@my_vcr.use_cassette('tests/unit/cassettes/test_cat_image_unsupported_type.yaml', filter_headers=['authorization'])
    #def test_catalog_image_unsupported_type(self):
    #    try:
    #        img = CatalogImage('S2A_OPER_MSI_L1C_DS_MPS__20160904T224944_S20160904T180250_N02.04')
    #    except UnsupportedImageType:
    #        pass
    
