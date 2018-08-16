'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import TmsImage
from auth_mock import gbdx
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
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    def test_tms_image_global(self):
        img = self.gbdx.tms_image(zoom=18)
        self.assertTrue(isinstance(img, TmsImage))
        assert img.shape == (3, 67106304, 67108864)
        assert img.proj == 'EPSG:3857'

    def test_tms_image(self):
        # tms z18 tiles 76669, 98727-98730
        # a 1 x 4 chunk of tiles, so 256 x 1024 pixels
        # then offset by 1/2 tile in x and y
        bbox = [-74.71046447753906, 40.53624234037728, -74.70909118652344, 40.54041698756514]
        img = self.gbdx.tms_image(zoom=18, bbox=bbox)
        self.assertTrue(isinstance(img, TmsImage))
        assert img.shape == (3, 1024, 256)
        assert img.proj == 'EPSG:3857'

    def test_tms_image_aoi(self):
        # tms z18 tiles 76669, 98727-98730
        # a 1 x 4 chunk of tiles, so 256 x 1024 pixels
        # then offset by 1/2 tile in x and y
        bbox = [-74.71046447753906, 40.53624234037728, -74.70909118652344, 40.54041698756514]
        img = self.gbdx.tms_image(zoom=18)
        aoi = img.aoi(bbox=bbox)
        self.assertTrue(isinstance(aoi, TmsImage))
        assert aoi.shape == (3, 1024, 256)
        assert aoi.proj == 'EPSG:3857'
