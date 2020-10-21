'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import S3Image, CatalogImage
import vcr
import unittest
from helpers import mockable_interface, gbdx_vcr

class S3ImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_s3_image.yaml', filter_headers=['authorization'])
    def test_s3_image(self):
        _path = 'landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF'
        img = self.gbdx.s3_image(_path) 
        self.assertTrue(isinstance(img, S3Image))
        assert img.shape == (1, 7770, 7610)
        assert img.proj == 'EPSG:32645'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_s3_image_proj.yaml', filter_headers=['authorization'])
    def test_s3_image_proj(self):
        _path = 'landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF'
        img = self.gbdx.s3_image(_path, proj="EPSG:4326")
        self.assertTrue(isinstance(img, S3Image))
        assert img.shape == (1, 7541, 7901)
        assert img.proj == 'EPSG:4326'


    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_s3_image_proj_src.yaml', filter_headers=['authorization'])
    def test_s3_image_proj_src(self):
        _path = 'landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF'
        img = self.gbdx.s3_image(_path, proj="EPSG:4326", src_proj="EPSG:32645")
        self.assertTrue(isinstance(img, S3Image))
        assert img.shape == (1, 7541, 7901)
        assert img.proj == 'EPSG:4326'