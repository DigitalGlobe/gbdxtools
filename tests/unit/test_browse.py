'''
Unit tests for the gbdxtools.BrowseImage class

See tests/readme.md for more about tests
'''

import unittest
from gbdxtools.images.browse_image import BrowseImage

from helpers import mockable_interface, gbdx_vcr, WV02_CATID

class BrowseImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_browse_image.yaml')
    def test_browse_image(self):
        img = BrowseImage(WV02_CATID)
        self.assertTrue(isinstance(img, BrowseImage))
        self.assertEqual(img.shape, (7165, 1368, 3))

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_browse_image_bbox.yaml')
    def test_browse_image_bbox(self):
        img = BrowseImage(WV02_CATID, bbox=[-105.16, 39.06, -105.15, 39.07])
        self.assertTrue(isinstance(img, BrowseImage))
        self.assertEqual(img.shape, (7165, 1368, 3))
        self.assertEqual(img.read().shape, (70, 70, 3))
