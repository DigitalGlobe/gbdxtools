from gbdxtools import Interface
from gbdxtools.s3 import S3
from auth_mock import gbdx
import vcr
import os
import tempfile
import unittest


cassette_name = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cassettes', 'test_s3_download.yaml')

class S3Tests(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
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

    #@vcr.use_cassette(cassette_name, filter_headers=['authorization'])
    #def test_download(self):
    #    location = 'gbdxtools/ski_areas.geojson'
    #    s = S3()
    #    s.download(location, local_dir=self._temp_path)
    #    assert os.path.isfile(os.path.join(self._temp_path, 'ski_areas.geojson'))
