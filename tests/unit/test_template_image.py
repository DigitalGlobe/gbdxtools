'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import RDAImage
from auth_mock import gbdx
import vcr
import tempfile
import unittest



def force(r1, r2):
    return True


my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']


class TemplateImageTest(unittest.TestCase):
    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_template_image.yaml', filter_headers=['authorization'])
    def test_template_image(self):
        img = self.gbdx.rda_template_image('DigitalGlobeStripTemplate',
                                           catId='e9d158c6-2af0-481d-a1f0-d82b7234db33-inv',
                                           correctionType='AComp',
                                           draType='HistogramDRA',
                                           bands='PanSharp',
                                           bandSelection='RGB',
                                           crs='UTM',
                                           nodeId="SmartBandSelect")
        self.assertTrue(isinstance(img, RDAImage))
        assert img.shape == (3, 116277, 52241)
        assert img.proj == 'EPSG:32632'
