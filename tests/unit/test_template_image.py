'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools import RDAImage
from auth_mock import gbdx
import vcr
from os.path import join, isfile, dirname, realpath
import tempfile
import unittest
import dask.array as da

from gbdxtools.images.idaho_image import IdahoImage


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


class TemplateImageTest(unittest.TestCase):
    _temp_path = None

    @classmethod
    def setUpClass(cls):
        cls.gbdx = gbdx
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_template_image.yaml', filter_headers=['authorization'])
    def test_template_image(self):
        img = self.gbdx.rda_template_image('DigitalGlobeStrip',
                                           catalogId='e9d158c6-2af0-481d-a1f0-d82b7234db33-inv',
                                           correctionType='AComp',
                                           draType='HistogramDRA',
                                           bands='PanSharp',
                                           bandSelection='RGB',
                                           crs='UTM')
        self.assertTrue(isinstance(img, RDAImage))
        assert img.shape == (3, 95278, 42775)
        assert img.proj == 'EPSG:32632'

    @my_vcr.use_cassette('tests/unit/cassettes/test_template_image_idaho.yaml', filter_headers=['authorization'])
    def test_template_image_idaho(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid,
                                    bucket='idaho-images')
        self.assertTrue(isinstance(img, IdahoImage))
        assert img.shape == (8, 11120, 10735)
        assert img.proj == 'EPSG:4326'
