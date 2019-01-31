'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import Sentinel2, Sentinel1
from auth_mock import gbdx
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
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


class SentinelImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_sentinel_image.yaml', filter_headers=['authorization'])
    def test_sentinel_image(self):
        _id = 'tiles/21/U/VQ/2016/5/23/0'
        img = self.gbdx.sentinel2(_id, bbox=[-58.37816710149235, 48.65691074156554, -56.86087022688015, 49.65456221177575])
        self.assertTrue(isinstance(img, Sentinel2))
        assert img.shape == (4, 11181, 11174)
        assert img.proj == 'EPSG:32621'

    @my_vcr.use_cassette('tests/unit/cassettes/test_sentinel_image_proj.yaml', filter_headers=['authorization'])
    def test_sentinel_proj(self):
        _id = 'tiles/21/U/VQ/2016/5/23/0'
        img = self.gbdx.sentinel2(_id, bbox=[-58.37816710149235, 48.65691074156554, -56.86087022688015, 49.65456221177575], proj="EPSG:4326")
        self.assertTrue(isinstance(img, Sentinel2))
        assert img.shape == (4, 8841, 13446)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_sentinel1_image.yaml', filter_headers=['authorization'])
    def test_sentinel1_image(self):
        _id = 'S1A_IW_GRDH_1SDV_20180713T142443_20180713T142508_022777_027819_7A96'
        img = self.gbdx.sentinel1(_id, bbox=[55.2143669128418, 25.184843769649808, 55.24784088134766, 25.226527054781688])
        self.assertTrue(isinstance(img, Sentinel1))
        assert img.shape == (1, 436, 351)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_sentinel1_proj.yaml', filter_headers=['authorization'])
    def test_sentinel1_proj(self):
        _id = 'S1A_IW_GRDH_1SDV_20180713T142443_20180713T142508_022777_027819_7A96'
        img = self.gbdx.sentinel1(_id, proj='EPSG:3857')
        self.assertTrue(isinstance(img, Sentinel1))
        assert img.proj == 'EPSG:3857'
 
