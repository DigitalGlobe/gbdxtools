'''
Unit tests for the generic image class functionality
'''

import unittest

from helpers import gbdx_vcr, mockable_interface
from helpers import WV02_CATID

from gbdxtools import CatalogImage
from shapely.geometry import shape
from shapely.affinity import translate


class MetaImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_meta_all.yaml')
    def test_image_pxbounds_overlapping(self):
        wv2 = CatalogImage(WV02_CATID)
        _bands, ysize, xsize = wv2.shape
        image_shape = shape(wv2)
        image_bounds = image_shape.bounds
        width = image_bounds[2] - image_bounds[0] 
        clip_area = translate(image_shape, xoff=-0.5 * width)
        xmin, ymin, xmax, ymax = wv2.pxbounds(clip_area, clip=True)
        self.assertEqual(xmin, 0)
        self.assertEqual(ymin, 0)
        self.assertEqual(xmax, xsize/2)
        self.assertEqual(ymax, ysize)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_meta_all.yaml')
    def test_image_pxbounds_disjoint(self):
        wv2 = CatalogImage(WV02_CATID)
        bounds = shape(wv2)
        clip = translate(bounds, xoff=5, yoff=5)
        with self.assertRaises(ValueError):
            clipped = wv2.pxbounds(clip)


    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_meta_all.yaml')
    def test_image_window_at(self):
        wv2 = CatalogImage(WV02_CATID)
        c1 = shape(wv2).centroid
        window = wv2.window_at(c1, (256, 256))
        c2 = shape(window).centroid
        bands, x, y = window.shape
        # check the window is the correct shape
        self.assertEqual(x, 256)
        self.assertEqual(y, 256)
        # make sure the center of the window is within 1 pixel
        # of where it should be
        self.assertTrue(c1.distance(c2) < wv2.metadata['georef']['scaleX'])

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_meta_all.yaml')
    def test_image_window_cover(self):
        """ Window cover should padd the image by 25 pixels and return 9 windows """
        wv2 = CatalogImage(WV02_CATID)
        aoi = wv2.randwindow((275,300))
        coverage = [dsk for dsk in aoi.window_cover((100,100), pad=True)]
        self.assertEqual(len(coverage), 9)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_meta_all.yaml')
    def test_image_window_cover_false(self):
        """ Window cover should not padd the image and return only tiles of 100, 100 (9 windows) """
        wv2 = CatalogImage(WV02_CATID)
        aoi = wv2.randwindow((325,300))
        coverage = [dsk for dsk in aoi.window_cover((100,100), pad=False)]
        self.assertEqual(len(coverage), 9)

    
