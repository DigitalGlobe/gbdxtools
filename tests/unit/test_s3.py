from gbdxtools import Interface
from gbdxtools.s3 import S3
from auth_mock import gbdx
from moto import mock_s3
import vcr
import os
import tempfile
import unittest
from moto_test_data import pre_load_s3_data


cassette_name = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'cassettes', 'test_s3_download.yaml')


class S3Tests(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

        cls._bucket_name = "testBucket"
        cls._prefix = "testPrefix"
        cls._info = {
            "bucket": cls._bucket_name,
            "prefix": cls._prefix,
            "S3_access_key": "",
            "S3_secret_key": "",
            "S3_session_token": ""
        }
    
    def setUp(self):
        self._mock_s3 = mock_s3()
        self._mock_s3.start()
        pre_load_s3_data(self._bucket_name, self._prefix)
        self.s3 = S3()
        self.s3.info = self._info

    def tearDown(self):
        self._mock_s3.stop()

    def test_bucket_init(self):
        s = S3()
        assert isinstance(s, S3)

    @vcr.use_cassette('tests/unit/cassettes/test_get_s3creds.yaml',
                      filter_headers=['authorization'])
    def test_get_s3_creds(self):
        s = S3()
        assert s.info is not None
        assert "bucket" in s.info.keys()
        assert "prefix" in s.info.keys()
        assert "S3_secret_key" in s.info.keys()
        assert "S3_access_key" in s.info.keys()
        assert "S3_session_token" in s.info.keys()

    def test_s3_list(self):
        """
        See the pre_load_s3_data functions for details on the bucket 
        contents. structure is as follows:

        readme.txt
        images/myimages{0-499}.tif
        scripts/myscripts{0-399}.py
        scripts/subdir/otherscripts{0-109}.sh
        """
        # Test empty string, returns only keys in this "dir", no directories
        assert len(self.s3.list_contents("", delimiter="/")) == 2
        assert len(self.s3.list_contents("")) == 1012
        assert len(self.s3.list_contents("readme.txt")) == 1
        assert len(self.s3.list_contents("/readme.txt")) == 1

        # Test images dir
        assert len(self.s3.list_contents("images/")) == 500
        assert len(self.s3.list_contents("images/", delimiter="/")) == 500

        # Test scripts dir, should exclude "subdir"
        assert len(self.s3.list_contents("scripts/", delimiter="/")) == 400
        assert len(self.s3.list_contents("scripts/")) == 510

    def test_s3_delete(self):
        """
        See the pre_load_s3_data functions for details on the bucket 
        contents. structure is as follows:

        readme.txt
        images/myimages{0-499}.tif
        scripts/myscripts{0-399}.py
        scripts/subdir/otherscripts{0-109}.sh
        """
        # Test delete single file
        assert len(self.s3.list_contents("scripts/subdir/")) == 110
        self.s3.delete("scripts/subdir/otherscripts0.sh")
        assert len(self.s3.list_contents("scripts/subdir/")) == 109

        # Test delete > 1000
        assert len(self.s3.list_contents("")) == 1011
        self.s3.delete("")
        assert len(self.s3.list_contents("")) == 0

    def test_s3_delete_delimiter(self):
        """
        See the pre_load_s3_data functions for details on the bucket 
        contents. structure is as follows:

        readme.txt
        images/myimages{0-499}.tif
        scripts/myscripts{0-399}.py
        scripts/subdir/otherscripts{0-109}.sh
        """
        # Test delete multiple files
        assert len(self.s3.list_contents("scripts/", delimiter="/")) == 400
        self.s3.delete("scripts/", delimiter="/")
        assert len(self.s3.list_contents("scripts/", delimiter="/")) == 0

    #@vcr.use_cassette(cassette_name, filter_headers=['authorization'])
    #def test_download(self):
    #    location = 'gbdxtools/ski_areas.geojson'
    #    s = S3()
    #    s.download(location, local_dir=self._temp_path)
    #    assert os.path.isfile(os.path.join(self._temp_path, 'ski_areas.geojson'))
