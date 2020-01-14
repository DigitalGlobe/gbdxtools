'''
Unit tests for the generic image class functionality
'''

import unittest

from helpers import gbdx_vcr, mockable_interface, WV02_CATID

from gbdxtools import CatalogImage


class ImageUtilTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_image_can_acomp.yaml')
    def test_image_acomp_avail(self):
        can_acomp = CatalogImage.acomp_available(WV02_CATID)
        self.assertFalse(can_acomp)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_image_available.yaml')
    def test_is_available(self):
        available = CatalogImage.is_available(WV02_CATID)
        self.assertTrue(available)
