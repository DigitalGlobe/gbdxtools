'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import S3Image, CatalogImage
from auth_mock import get_mock_gbdx_session
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


class S3ImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        #mock_gbdx_session = get_mock_gbdx_session(token='dymmytoken')
        #cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        cls.gbdx = Interface()
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_s3_image.yaml', filter_headers=['authorization'])
    def test_s3_image(self):
        _path = 'landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF'
        img = self.gbdx.s3_image(_path) 
        self.assertTrue(isinstance(img, S3Image))
        assert img.shape == (1, 7770, 7610)
        assert img.proj == 'EPSG:32645'

    @my_vcr.use_cassette('tests/unit/cassettes/test_s3_image_proj.yaml', filter_headers=['authorization'])
    def test_s3_image_proj(self):
        _path = 'landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF'
        img = self.gbdx.s3_image(_path, proj="EPSG:4326")
        self.assertTrue(isinstance(img, S3Image))
        assert img.shape == (1, 7541, 7901)
        assert img.proj == 'EPSG:4326'

