'''
Unit tests for the gbdxtools.images.browse_image.BrowseImage class
'''

from gbdxtools.images.browse_image import BrowseImage
from auth_mock import gbdx
import vcr
import unittest

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class BrowseImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx

    @my_vcr.use_cassette('tests/unit/cassettes/test_browse_image.yaml', filter_headers=['authorization'])
    def test_browse_image(self):
        b = BrowseImage('104001003589D300')
        assert b.image.shape == (985, 972, 3)

    @my_vcr.use_cassette('tests/unit/cassettes/test_browse_image_bbox.yaml', filter_headers=['authorization'])
    def test_browse_image_bbox(self):
        b = BrowseImage('104001003589D300', bbox=[131.06097742810638, -25.342265762436224, 131.06698263831117, -25.33626055223141])
        assert b.read().shape == (43, 43, 3)

