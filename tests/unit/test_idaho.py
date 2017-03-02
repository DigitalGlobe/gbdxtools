'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools.idaho import Idaho
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


class IdahoTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token='dymmytoken')
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    def test_init(self):
        c = Idaho(self.gbdx)
        self.assertTrue(isinstance(c, Idaho))

    @vcr.use_cassette('tests/unit/cassettes/test_idaho_get_images_by_catid_and_aoi.yaml', filter_headers=['authorization'])
    def test_idaho_get_images_by_catid_and_aoi(self):
        i = Idaho(self.gbdx)
        catid = '10400100203F1300'
        aoi_wkt = "POLYGON ((-105.0207996368408345 39.7338828628182839, -105.0207996368408345 39.7365972921260067, -105.0158751010894775 39.7365972921260067, -105.0158751010894775 39.7338828628182839, -105.0207996368408345 39.7338828628182839))"
        results = i.get_images_by_catid_and_aoi(catid=catid, aoi_wkt=aoi_wkt)
        assert len(results['results']) == 2

    @vcr.use_cassette('tests/unit/cassettes/test_idaho_get_images_by_catid.yaml', filter_headers=['authorization'])
    def test_idaho_get_images_by_catid(self):
        i = Idaho(self.gbdx)
        catid = '10400100203F1300'
        results = i.get_images_by_catid(catid=catid)
        assert len(results['results']) == 12

    @vcr.use_cassette('tests/unit/cassettes/test_idaho_describe_images.yaml', filter_headers=['authorization'])
    def test_idaho_describe_images(self):
        i = Idaho(self.gbdx)
        catid = '10400100203F1300'
        description = i.describe_images(i.get_images_by_catid(catid=catid))
        assert description['10400100203F1300']['parts'][1]['PAN']['id'] =='b1f6448b-aecd-4d9b-99ec-9cad8d079043'
