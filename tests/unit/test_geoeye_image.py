'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import GE01, CatalogImage
from auth_mock import get_mock_gbdx_session
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import rasterio
import dask.array as da

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

# How to use the mock_gbdx_session and vcr to create unit tests:
# 1. Add a new test that is dependent upon actually hitting GBDX APIs.
# 2. Decorate the test with @vcr appropriately
# 3. Replace "dummytoken" with a real gbdx token
# 4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
# 5. Replace the real gbdx token with "dummytoken" again
# 6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)


class GE01ImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token='dymmytoken')
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        #cls.gbdx = Interface()
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_geoeye_image.yaml', filter_headers=['authorization'])
    def test_geoeye_image(self):
        _id = '1050010009569E00'
        img = self.gbdx.catalog_image(_id) #, bbox=[-109.84, 43.19, -109.59, 43.34])
        self.assertTrue(isinstance(img, GE01))
        assert img.shape == (4, 57316, 11688)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_geoeye_image_proj.yaml', filter_headers=['authorization'])
    def test_geoeye_image_proj(self):
        _id = '1050010009569E00'
        img = self.gbdx.catalog_image(_id, proj="EPSG:3857")
        self.assertTrue(isinstance(img, GE01))
        assert img.shape == (4, 64283, 10256)
        assert img.proj == 'EPSG:3857'

    @my_vcr.use_cassette('tests/unit/cassettes/test_geoeye_image_pan.yaml', filter_headers=['authorization'])
    def test_geoeye_image_pan(self):
        _id = '1050010009569E00'
        img = self.gbdx.catalog_image(_id, band_type="pan")
        self.assertTrue(isinstance(img, GE01))
        assert img.shape == (1, 229379, 46782)

    @my_vcr.use_cassette('tests/unit/cassettes/test_geoeye_image_pansharpen.yaml', filter_headers=['authorization'])
    def test_geoeye_image_pansharpen(self):
        _id = '1050010009569E00'
        img = self.gbdx.catalog_image(_id, pansharpen=True)
        self.assertTrue(isinstance(img, GE01))
        assert img.shape == (4, 229379, 46782)
