'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import TmsImage
from auth_mock import get_mock_gbdx_session
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import dask.array as da

try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

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


class TmsImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token='dymmytoken')
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        #cls.gbdx = Interface()
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    def test_tms_image(self):
        img = self.gbdx.tms_image(zoom=18, bbox=[-105.00444889068605, 39.75399710099606, -104.9962091445923, 39.75431683540881])
        self.assertTrue(isinstance(img, TmsImage))
        assert img.shape == (3, 78, 1316)
        assert img.proj == 'EPSG:3857'

    def test_tms_image_global(self):
        img = self.gbdx.tms_image(zoom=18)
        self.assertTrue(isinstance(img, TmsImage))
        assert img.shape == (3, 67106304, 67108864)
        assert img.proj == 'EPSG:3857'

    def test_tms_image_aoi(self):
        img = self.gbdx.tms_image(zoom=18)
        aoi = img.aoi(bbox=[-105.00444889068605, 39.75299710099606, -104.9962091445923, 39.75431683540881])
        self.assertTrue(isinstance(aoi, TmsImage))
        assert aoi.shape == (3, 320, 1316)
        assert aoi.proj == 'EPSG:3857'
