'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import QB02, CatalogImage
from gbdxtools.rda.error import AcompUnavailable
from auth_mock import gbdx
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import pytest
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


@pytest.mark.skip(reason="Catalog Id's must be of Product type, not Acquisition")
class GE01ImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_quickbird_image.yaml', filter_headers=['authorization'])
    def test_quickbird_image(self):
        _id = '1010010002B93F00'
        img = self.gbdx.catalog_image(_id)
        self.assertTrue(isinstance(img, QB02))
        assert img.shape == (4, 37520, 9850)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_quickbird_acomp.yaml', filter_headers=['authorization'])
    def test_quickbird_image_acomp(self):
        try:
            _id = '1010010012D04200'
            img = self.gbdx.catalog_image(_id, acomp=True)
        except AcompUnavailable:
            pass

    @my_vcr.use_cassette('tests/unit/cassettes/test_quickbird_image_proj.yaml', filter_headers=['authorization'])
    def test_quickbird_image_proj(self):
        _id = '1010010012D04200'
        img = self.gbdx.catalog_image(_id, proj="EPSG:3857")
        self.assertTrue(isinstance(img, QB02))
        assert img.shape == (4, 42504, 8469)
        assert img.proj == 'EPSG:3857'

    @my_vcr.use_cassette('tests/unit/cassettes/test_quickbird_image_pan.yaml', filter_headers=['authorization'])
    def test_quickbird_image_pan(self):
        _id = '1010010012D04200'
        img = self.gbdx.catalog_image(_id, band_type="pan", bbox=[125.259159043295, 40.43603914103845, 125.27301998472511, 40.44990008246856])
        self.assertTrue(isinstance(img, QB02))
        assert img.shape == (1, 1999, 1998)

    @my_vcr.use_cassette('tests/unit/cassettes/test_quickbird_image_pansharpen.yaml', filter_headers=['authorization'])
    def test_quickbird_image_pansharpen(self):
        _id = '1010010012D04200'
        img = self.gbdx.catalog_image(_id, pansharpen=True, bbox=[125.259159043295, 40.43603914103845, 125.27301998472511, 40.44990008246856])
        self.assertTrue(isinstance(img, QB02))
        assert img.shape == (4, 1999, 1998)
