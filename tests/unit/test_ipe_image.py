"""
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
"""

from gbdxtools import Interface
from gbdxtools import IdahoImage
from gbdxtools.ipe.graph import get_ipe_graph
from gbdxtools.images.meta import DaskImage
from auth_mock import get_mock_gbdx_session
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
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid)
        self.assertTrue(isinstance(img, IdahoImage))
        assert img.shape == (8, 10290, 14625)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_missing_product.yaml', filter_headers=['authorization'])
    def test_ipe_image_unsupported(self):
        try:
            idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
            img = self.gbdx.idaho_image(idahoid, product="no_product")
        except:
            pass

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_get_product.yaml', filter_headers=['authorization'])
    def test_ipe_image_get_product(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid)
        ortho = img.get_product('ortho')
        self.assertTrue(isinstance(ortho, IdahoImage))
        assert img.shape == (8, 10290, 14625)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_init_with_aoi2.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_aoi(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid, bbox=[-74.01626586914064, 45.394592696926615, -73.91601562500001,
                                                   45.43363548747066])
        assert img.shape == (8, 3168, 8134)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_proj.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_proj(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid, bbox=[-74.01626586914064, 45.394592696926615, -73.91601562500001,
                                                   45.43363548747066], proj='EPSG:3857')
        assert img.shape == (8, 4513, 8134)
        assert img.proj == 'EPSG:3857'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_aoi.yaml', filter_headers=['authorization'])
    def test_ipe_image_aoi(self):
        idahoid = '1ec49348-8950-49ff-bd71-ea2e4d8754ac'
        img = self.gbdx.idaho_image(idahoid)
        aoi = img.aoi(bbox=[-74.01626586914064,45.394592696926615,-73.91601562500001,45.43363548747066])
        assert aoi.shape == (8, 3168, 8134)
        rgb = aoi[[4,2,1], ...]
        assert isinstance(rgb, da.Array)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_read.yaml', filter_headers=['authorization'])
    def test_ipe_image_read(self):
        idahoid = '179269b9-fdb3-49d8-bb62-d15de54ad15d'
        img = self.gbdx.idaho_image(idahoid)
        aoi = img.aoi(bbox=[-110.85299491882326,32.167148499672855,-110.84870338439943,32.170236308395644])
        assert aoi.shape == (8, 172, 239)
        aoi.read = read_mock
        rgb = aoi.read(bands=[4,2,1])
        assert isinstance(rgb, np.ndarray)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_1b.yaml', filter_headers=['authorization'])
    def test_ipe_image_1b(self):
        idahoid = '179269b9-fdb3-49d8-bb62-d15de54ad15d'
        img = self.gbdx.idaho_image(idahoid, product="1b", bbox=[-110.85299491882326,32.167148499672855,-110.84870338439943,32.170236308395644])
        #assert img.ipe_id == '414c35956f15a521d35012ec2cb60a8ee2fa7492e7b5f0fa0c6999a580543749'
        assert isinstance(img.ipe_metadata, dict)
        assert img._ndvi_bands == [7, 4]
        assert img.shape == (8, 176, 203)
        assert isinstance(img, da.Array)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_rgb.yaml', filter_headers=['authorization'])
    def test_ipe_image_rgb(self):
        idahoid = '179269b9-fdb3-49d8-bb62-d15de54ad15d'
        img = self.gbdx.idaho_image(idahoid)
        aoi = img.aoi(bbox=[-110.85299491882326,32.167148499672855,-110.84870338439943,32.170236308395644])
        aoi.rgb = read_mock
        rgb = aoi.rgb()
        assert isinstance(rgb, np.ndarray)
    
    #@my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_ortho.yaml', filter_headers=['authorization'])
    #def test_ipe_image_ortho(self):
    #    idahoid = '179269b9-fdb3-49d8-bb62-d15de54ad15d'
    #    img = self.gbdx.idaho_image(idahoid, product='1b')
    #    aoi = img.aoi(bbox=[-110.85299491882326,32.167148499672855,-110.84870338439943,32.170236308395644])
    #    assert aoi.shape == (8, 176, 203)
    #    aoi.ortho = read_mock
    #    ortho = aoi.orthorectify()
    #    assert isinstance(ortho, DaskImage)

    #@my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_geotiff.yaml', filter_headers=['authorization'])
    #def test_ipe_image_geotiff(self):
    #    idahoid = '179269b9-fdb3-49d8-bb62-d15de54ad15d'
    #    img = self.gbdx.idaho_image(idahoid, bbox=[-110.85299491882326,32.167148499672855,-110.84870338439943,32.170236308395644])
    #    tif = img.geotiff(path='/tmp/tmp.tif', dtype='uint16')
    #    with rasterio.open(tif) as src:
    #        assert [round(x, 3) for x in list(src.bounds)] == [-110.853, 32.167, -110.849, 32.17]
    #        assert src.meta['width'] == 239
    #        assert src.meta['height'] == 172
    #        assert src.meta['dtype'] == 'uint16'
