'''
Unit tests for the generic image class functionality
'''

from gbdxtools import CatalogImage
from auth_mock import gbdx 
import vcr
import tempfile
import unittest

def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class ImageUtilTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx

    @my_vcr.use_cassette('tests/unit/cassettes/test_image_can_acomp.yaml', filter_headers=['authorization'])
    def test_image_acomp_avail(self):
        can_acomp = CatalogImage.acomp_available('1050410000B1BD00')
        self.assertFalse(can_acomp)
        can_acomp = CatalogImage.acomp_available('104001002ABEA500')
        self.assertTrue(can_acomp)

    @my_vcr.use_cassette('tests/unit/cassettes/test_image_ordered.yaml', filter_headers=['authorization'])
    def test_image_ordered(self):
        ordered = CatalogImage.is_ordered('1050410000B1BD00')
        self.assertFalse(ordered)
        ordered = CatalogImage.is_ordered('104001002ABEA500')
        self.assertTrue(ordered)


