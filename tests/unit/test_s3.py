from gbdxtools import Interface
from gbdxtools.s3 import S3
from auth_mock import get_mock_gbdx_session
import vcr
import os
import tempfile
import unittest

"""
How to use the mock_gbdx_session and vcr to create unit tests:
1. Add a new test that is dependent upon actually hitting GBDX APIs.
2. Decorate the test with @vcr appropriately, supply a yaml file path to gbdxtools/tests/unit/cassettes
    note: a yaml file will be created after the test is run

3. Replace "dummytoken" with a real gbdx token after running test successfully
4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
5. Replace the real gbdx token with "dummytoken" again
6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)
"""

cassette_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cassettes', 'test_s3_download.yaml')

class S3Tests(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        # create mock session, replace dummytoken with real token to create cassette
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    def test_bucket_init(self):
        s = S3()
        assert isinstance(s, S3)

    @vcr.use_cassette('tests/unit/cassettes/test_get_s3creds.yaml', filter_headers=['authorization'])
    def test_get_s3_creds(self):
        s = S3()
        assert s.info is not None
        assert "bucket" in s.info.keys()
        assert "prefix" in s.info.keys()
        assert "S3_secret_key" in s.info.keys()
        assert "S3_access_key" in s.info.keys()
        assert "S3_session_token" in s.info.keys()

    @vcr.use_cassette(cassette_name, filter_headers=['authorization'])
    def test_download(self):
        location = 'nikki/gbdxtools_test_s3'
        s = S3()
        s.download(location, local_dir=self._temp_path)

        assert os.path.isfile(os.path.join(self._temp_path, 'test_dir', 'model.json'))
        assert os.path.isfile(os.path.join(self._temp_path, 'model.json'))
