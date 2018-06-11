'''
Unit tests for spatial indices functions
'''
import gbdxtools

token = gbdxtools.Interface().gbdx_connection.token['access_token']


from gbdxtools import CatalogImage
from shapely.geometry import shape
from shapely.affinity import translate
#from auth_mock import gbdx
import vcr
import tempfile
import unittest
import numpy as np
from auth_mock import get_mock_gbdx_session
from gbdxtools import Interface

gbdx = Interface( gbdx_connection = get_mock_gbdx_session(token= token))


def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']


class TestIndices(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_ndvi.yaml', filter_headers=['authorization'])
    def test_ndvi_bands(self):
        _id = '103001006F31E000'
        img = self.gbdx.catalog_image(_id, bbox= [-95.527024269104, 29.200273324360754, -95.50655364990236, 29.2170547703652])
        self.assertEqual(img._ndvi_bands, [6, 4])

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_ndvi.yaml', filter_headers=['authorization'])
    def test_ndwi_bands(self):
        _id = '103001006F31E000'
        img = self.gbdx.catalog_image(_id, bbox=[-95.527024269104, 29.200273324360754, -95.50655364990236, 29.2170547703652])
        self.assertEqual(img._ndwi_bands, [7, 0])

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_ndvi.yaml', filter_headers=['authorization'])
    def test_ndvi_vals(self):
        _id = '103001006F31E000'
        img = self.gbdx.catalog_image(_id, bbox=[-95.527024269104, 29.200273324360754, -95.50655364990236, 29.2170547703652])
        self.assertTrue(not(np.isnan(img.ndvi()).any()))

    @my_vcr.use_cassette('tests/unit/cassettes/test_wv_image_ndvi.yaml', filter_headers=['authorization'])
    def test_ndwi_vals(self):
        _id = '103001006F31E000'
        img = self.gbdx.catalog_image(_id, bbox=[-95.527024269104, 29.200273324360754, -95.50655364990236, 29.2170547703652])
        self.assertTrue(not(np.isnan(img.ndwi()).any()))
