'''
Unit tests for the generic image class functionality
'''

from gbdxtools import CatalogImage
from shapely.geometry import shape
from shapely.affinity import translate
from auth_mock import gbdx 
import vcr
import tempfile
import unittest


def force(r1, r2):
    return True

my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class MetaImageTest(unittest.TestCase):

    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_meta_pxbounds_overlap.yaml', filter_headers=['authorization'])
    def test_image_pxbounds_overlapping(self):
        wv2 = CatalogImage('1030010076B8F500')
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

    @my_vcr.use_cassette('tests/unit/cassettes/test_meta_pxbounds_disjoint.yaml', filter_headers=['authorization'])
    def test_image_pxbounds_disjoint(self):
        wv2 = CatalogImage('1030010076B8F500')
        bounds = shape(wv2)
        clip = translate(bounds, xoff=5, yoff=5)
        with self.assertRaises(ValueError):
            clipped = wv2.pxbounds(clip)


    @my_vcr.use_cassette('tests/unit/cassettes/test_meta_window_at.yaml', filter_headers=['authorization'])
    def test_image_window_at(self):
        wv2 = CatalogImage('1030010076B8F500')
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

    @my_vcr.use_cassette('tests/unit/cassettes/test_meta_window_cover.yaml', filter_headers=['authorization'])
    def test_image_window_cover(self):
        """ Window cover should padd the image by 25 pixels and return 9 windows """
        wv2 = CatalogImage('1030010076B8F500')
        aoi = wv2.randwindow((275,300))
        coverage = [dsk for dsk in aoi.window_cover((100,100), pad=True)]
        self.assertEqual(len(coverage), 9)

    @my_vcr.use_cassette('tests/unit/cassettes/test_meta_window_cover_false.yaml', filter_headers=['authorization'])
    def test_image_window_cover_false(self):
        """ Window cover should not padd the image and return only tiles of 100, 100 (9 windows) """
        wv2 = CatalogImage('1030010076B8F500')
        aoi = wv2.randwindow((325,300))
        coverage = [dsk for dsk in aoi.window_cover((100,100), pad=False)]
        self.assertEqual(len(coverage), 9)

    
