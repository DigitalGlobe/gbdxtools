'''
Unit tests for the generic image class functionality
'''

from gbdxtools import CatalogImage
from auth_mock import gbdx
import vcr
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
    def test_is_available_in_gbdx(self):
        ordered = CatalogImage.is_available_in_gbdx('104001002ABEA500')
        self.assertFalse(ordered)
        ordered = CatalogImage.is_available_in_gbdx('1030010076B8F500')
        self.assertTrue(ordered)

    @my_vcr.use_cassette('tests/unit/cassettes/test_is_available_in_rda.yaml', filter_headers=['authorization'])
    def test_is_available_in_rda(self):
        """
        Test that is_ordered checks RDA for strip metadata
        :return:
        """
        ordered = CatalogImage.is_ordered('1050410000B1BD00')
        self.assertFalse(ordered)
        ordered = CatalogImage.is_ordered('104001002ABEA500')
        self.assertTrue(ordered)

    @my_vcr.use_cassette('tests/unit/cassettes/test_image_ordered_fails_with_non_dg_cat_id.yaml', filter_headers=['authorization'])
    def test_image_ordered_fails_with_non_dg_cat_id(self):
        """
        Test that a non DG cat Id raises exception when checking `is_ordered` method
        :return:
        """
        with self.assertRaises(Exception):
            # landsat is not a DG catalog Id
            CatalogImage.is_available_in_gbdx('LC80380302013160LGN00')
