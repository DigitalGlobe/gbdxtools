"""
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
"""
import os
from gbdxtools import Interface
from gbdxtools import IdahoImage, CatalogImage
from gbdxtools.images.meta import DaskImage
from auth_mock import get_mock_gbdx_session
import vcr
import tempfile
import unittest
import dask.array as da
import numpy as np
import pytest

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


class RdaImageTest(unittest.TestCase):
    _temp_path = None

    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token='dummytoken')
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        #cls.gbdx = Interface()
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_default.yaml', filter_headers=['authorization'])
    def test_basic_ipe_image(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, bucket='rda-images-1')
        self.assertTrue(isinstance(img, IdahoImage))
        assert img.shape == (4, 6510, 6955)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_init_with_aoi2.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_aoi(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, bbox=[113, -6, 111, -7], bucket='rda-images-1')
        assert img.shape == (4, 43724, 87447)
        assert img.proj == 'EPSG:4326'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_proj.yaml', filter_headers=['authorization'])
    def test_ipe_image_with_proj(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, bbox=[113, -6, 111, -7], proj='EPSG:3857', bucket='rda-images-1')
        assert img.shape == (4, 44007, 87447)
        assert img.proj == 'EPSG:3857'

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_with_aoi.yaml', filter_headers=['authorization'])
    def test_ipe_image_aoi(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, bucket='rda-images-1')
        aoi = img.aoi(bbox=[113, -6, 111, -7])
        assert aoi.shape ==  (4, 43724, 87447)
        rgb = aoi[[2,2,1], ...]
        assert isinstance(rgb, da.Array)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_read.yaml', filter_headers=['authorization'])
    def test_ipe_image_read(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, bucket='rda-images-1')
        aoi = img.aoi(bbox=[113, -6, 111, -7])
        assert aoi.shape == (4, 43724, 87447)
        aoi.read = read_mock
        rgb = aoi.read(bands=[2,2,1])
        assert isinstance(rgb, np.ndarray)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_1b.yaml', filter_headers=['authorization'])
    def test_ipe_image_1b(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, product="1b", bbox=[113, -6, 111, -7], bucket='rda-images-1')
        assert isinstance(img.metadata, dict)
        with self.assertRaises(NotImplementedError):
            img._ndvi_bands
        assert img.shape == (4, 43724, 87447)
        assert isinstance(img, da.Array)

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_default.yaml', filter_headers=['authorization'])
    def test_ipe_image_randwindow(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, bucket='rda-images-1')
        raoi = img.randwindow((500, 500))
        assert raoi.shape == (4, 500, 500)
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
    @pytest.mark.skip(reason="warp dropped")
    def test_ipe_image_ortho(self):
        idahoid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = self.gbdx.idaho_image(idahoid, spec='1b', bucket='rda-images-1')
        aoi = img.aoi(bbox=[113, -6, 111, -7])
        assert aoi.shape == (4, 66366, 80056)
        aoi.ortho = read_mock
        ortho = aoi.warp()
        assert isinstance(ortho, DaskImage)

    @my_vcr.use_cassette('tests/unit/cassettes/test_materialize.yaml', filter_headers=['authorization'])
    @pytest.mark.skip(reason="400 error for some reason when getting templata geo metadata")
    def test_rda_materialize(self):
        # TODO: Fix this test
        catid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = CatalogImage(catid)
        aoi = img.randwindow((1000, 1000))
        assert aoi.shape == (4, 1000, 1000)
        job_id = img.materialize(bounds=aoi.bounds)
        status = img.materialize_status(job_id)
        assert status['jobStatus'] == 'processing'

    # Test the payload creation method 
    @my_vcr.use_cassette('tests/unit/cassettes/test_materialize_payload.yaml', filter_headers=['authorization'])
    def test_rda_materialize_payload(self):
        catid = '8c3c4fc6-abcb-4f5f-bce6-d496c1a91676'
        img = CatalogImage(catid)
        pl = img.rda._create_materialize_payload('123', 'node', None, None, 'TILE_STREAM', sample='yes')
        assert pl['outputFormat'] == 'TILE_STREAM'
        assert 'callbackUrl' not in pl
        assert 'cropGeometryWKT' not in pl
        assert pl['imageReference']['nodeId'] == 'node'
        assert pl['imageReference']['templateId'] == '123'
        assert pl['imageReference']['parameters'] == {'sample': 'yes'}

        pl = img.rda._create_materialize_payload('123', 'node', [1,2,3,4], 'sns://yes', 'TIF')
        assert pl['outputFormat'] == 'TIF'
        assert pl['callbackUrl'] == 'sns://yes'
        assert pl['cropGeometryWKT'] == 'POLYGON ((3 2, 3 4, 1 4, 1 2, 3 2))'
        assert pl['imageReference']['nodeId'] == 'node'
        assert pl['imageReference']['templateId'] == '123'
        assert pl['imageReference']['parameters'] == {}
        


