'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import GE01, CatalogImage
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

@pytest.mark.skip(reason="Catalog Id's must be of Product type, not Acquisition")
class GE01ImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_geoeye_image.yaml', filter_headers=['authorization'])
    def test_geoeye_image(self):
        _id = '1050010009569E00'
        img = self.gbdx.catalog_image(_id) #, bbox=[-109.84, 43.19, -109.59, 43.34])
        self.assertTrue(isinstance(img, GE01))
        assert img.shape == (4, 57316, 11688)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_geoeye_acomp.yaml', filter_headers=['authorization'])
    def test_geoeye_acomp(self):
        _id = '1050010009569E00'
        try:
            img = self.gbdx.catalog_image(_id, acomp=True) #, bbox=[-109.84, 43.19, -109.59, 43.34])
            self.assertTrue(isinstance(img, GE01))
            assert img.shape == (4, 57316, 11688)
            assert img.proj == 'EPSG:4326'
        except AcompUnavailable:
            pass

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
