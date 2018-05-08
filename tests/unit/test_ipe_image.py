"""
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
"""
import os
from gbdxtools import Interface
from gbdxtools import IdahoImage
from gbdxtools.ipe.graph import get_ipe_graph
from gbdxtools.images.meta import DaskImage
from auth_mock import get_mock_gbdx_session, gbdx
import vcr
import tempfile
import unittest
import dask.array as da
import numpy as np


def force(r1, r2):
    return True


my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']


def read_mock(**kwargs):
    return np.zeros((8,100,100)).astype(np.float32)

# How to use the mock_gbdx_session and vcr to create unit tests:
# 1. Add a new test that is dependent upon actually hitting GBDX APIs.
# 2. Decorate the test with @vcr appropriately
# 3. Replace "dummytoken" with a real gbdx token
# 4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
# 5. Replace the real gbdx token with "dummytoken" again
# 6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)


class IpeImageTest(unittest.TestCase):
    _temp_path = None

    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token='dummytoken')
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        #cls.gbdx = Interface()
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_get_graph.yaml', filter_headers=['authorization'])
    def test_get_graph(self):
        graphid = 'ba79f76782438c70087765c35f413def88f92b73627227830a531cddbfa2ed1a'
        json = get_ipe_graph(self.gbdx.gbdx_connection, graphid)
        assert json['id'] == graphid

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_default.yaml', filter_headers=['authorization'])
    def test_basic_ipe_image(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid)
        self.assertTrue(isinstance(img, IdahoImage))
        assert img.shape == (8, 11120, 10735)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_missing_product.yaml', filter_headers=['authorization'])
    def test_ipe_image_unsupported(self):
        try:
            idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
            img = self.gbdx.idaho_image(idahoid, product="no_product")
        except:
            pass

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_init_with_aoi2.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_aoi(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid, bbox=[-85.79713384556237, 10.859474119490333, 
                                                   -85.79366000529654, 10.86341028280643])
        assert img.shape == (8, 292, 258)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_proj.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_proj(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid, bbox=[-85.79713384556237, 10.859474119490333, 
                                                   -85.79366000529654, 10.86341028280643], proj='EPSG:3857')
        assert img.shape == (8, 298, 258)
        assert img.proj == 'EPSG:3857'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_aoi.yaml', filter_headers=['authorization'])
    def test_ipe_image_aoi(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid)
        aoi = img.aoi(bbox=[-85.79713384556237, 10.859474119490333, -85.79366000529654, 10.86341028280643])
        assert aoi.shape == (8, 292, 258)
        rgb = aoi[[4,2,1], ...]
        assert isinstance(rgb, da.Array)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_read.yaml', filter_headers=['authorization'])
    def test_ipe_image_read(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid)
        aoi = img.aoi(bbox=[-85.79713384556237, 10.859474119490333, -85.79366000529654, 10.86341028280643])
        assert aoi.shape == (8, 292, 258)
        aoi.read = read_mock
        rgb = aoi.read(bands=[4,2,1])
        assert isinstance(rgb, np.ndarray)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_1b.yaml', filter_headers=['authorization'])
    def test_ipe_image_1b(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid, product="1b", bbox=[-85.79713384556237, 10.859474119490333, -85.79366000529654, 10.86341028280643])
        assert isinstance(img.ipe_metadata, dict)
        assert img._ndvi_bands == [6, 4]
        assert img.shape == (8, 292, 258)
        assert isinstance(img, da.Array)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_default.yaml', filter_headers=['authorization'])
    def test_ipe_image_randwindow(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid)
        raoi = img.randwindow((500,500))
        assert raoi.shape == (8, 500, 500)
        aois = [a for a in img.iterwindows(count=5)]
        assert len(aois) == 5

    #@my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_rgb.yaml', filter_headers=['authorization'])
    #def test_ipe_image_rgb(self):
    #    idahoid = '179269b9-fdb3-49d8-bb62-d15de54ad15d'
    #    img = self.gbdx.idaho_image(idahoid)
    #    aoi = img.aoi(bbox=[-110.85299491882326,32.167148499672855,-110.84870338439943,32.170236308395644])
    #    aoi.rgb = read_mock
    #    rgb = aoi.rgb()
    #    assert isinstance(rgb, np.ndarray)
    
    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_ortho.yaml', filter_headers=['authorization'])
    def test_ipe_image_ortho(self):
        idahoid = '09d5acaf-12d4-4c67-adbb-cda26cbd2187'
        img = self.gbdx.idaho_image(idahoid, product='1b')
        aoi = img.aoi(bbox=[-85.79713384556237, 10.859474119490333, -85.79366000529654, 10.86341028280643])
        assert aoi.shape == (8, 292, 258)
        aoi.ortho = read_mock
        ortho = aoi.warp()
        assert isinstance(ortho, DaskImage)
