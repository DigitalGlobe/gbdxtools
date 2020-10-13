from gbdxtools import Sentinel2, Sentinel1
import vcr
import unittest
from helpers import mockable_interface, gbdx_vcr

class SentinelImageTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface()

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_sentinel_image.yaml', filter_headers=['authorization'])
    def test_sentinel_image(self):
        _id = 'tiles/21/U/VQ/2016/5/23/0'
        img = self.gbdx.sentinel2(_id, bbox=[-58.37816710149235, 48.65691074156554, -56.86087022688015, 49.65456221177575])
        self.assertTrue(isinstance(img, Sentinel2))
        assert img.shape == (4, 11181, 11174)
        assert img.proj == 'EPSG:32621'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_sentinel_image_proj.yaml', filter_headers=['authorization'])
    def test_sentinel_proj(self):
        _id = 'tiles/21/U/VQ/2016/5/23/0'
        img = self.gbdx.sentinel2(_id, bbox=[-58.37816710149235, 48.65691074156554, -56.86087022688015, 49.65456221177575], proj="EPSG:4326")
        self.assertTrue(isinstance(img, Sentinel2))
        assert img.shape == (4, 8841, 13446)
        assert img.proj == 'EPSG:4326'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_sentinel1_image.yaml', filter_headers=['authorization'])
    def test_sentinel1_image(self):
        _id = 'S1A_IW_GRDH_1SDV_20180713T142443_20180713T142508_022777_027819_7A96'
        img = self.gbdx.sentinel1(_id, bbox=[55.2143669128418, 25.184843769649808, 55.24784088134766, 25.226527054781688])
        self.assertTrue(isinstance(img, Sentinel1))
        assert img.shape == (1, 436, 351)
        assert img.proj == 'EPSG:4326'

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_sentinel1_proj.yaml', filter_headers=['authorization'])
    def test_sentinel1_proj(self):
        _id = 'S1A_IW_GRDH_1SDV_20180713T142443_20180713T142508_022777_027819_7A96'
        img = self.gbdx.sentinel1(_id, proj='EPSG:3857')
        self.assertTrue(isinstance(img, Sentinel1))
        assert img.proj == 'EPSG:3857'
 
