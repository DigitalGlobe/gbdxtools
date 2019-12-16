"""
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
"""
import os

from gbdxtools import Interface
from gbdxtools.idaho import Idaho
from auth_mock import get_mock_gbdx_session
import vcr
import tempfile
import unittest


def force(r1, r2):
    return True


my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class IdahoTest(unittest.TestCase):
    _temp_path = None

    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token='dummytoken')
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        cls._temp_path = tempfile.mkdtemp()
        print("Created: {}".format(cls._temp_path))

    def test_init(self):
        c = Idaho()
        self.assertTrue(isinstance(c, Idaho))

    @my_vcr.use_cassette('tests/unit/cassettes/test_idaho_get_images_by_catid_and_aoi.yaml',
                      filter_headers=['authorization'])
    def test_idaho_get_images_by_catid_and_aoi(self):
        i = Idaho()
        catid = '10400100203F1300'
        aoi_wkt = "POLYGON ((-105.0207996368408345 39.7338828628182839, -105.0207996368408345 39.7365972921260067, -105.0158751010894775 39.7365972921260067, -105.0158751010894775 39.7338828628182839, -105.0207996368408345 39.7338828628182839))"
        results = i.get_images_by_catid_and_aoi(catid=catid, aoi_wkt=aoi_wkt)
        assert len(results['results']) == 2

    @my_vcr.use_cassette('tests/unit/cassettes/test_idaho_get_images_by_catid.yaml', filter_headers=['authorization'])
    def test_idaho_get_images_by_catid(self):
        i = Idaho()
        catid = '10400100203F1300'
        results = i.get_images_by_catid(catid=catid)
        assert len(results['results']) == 12

    @my_vcr.use_cassette('tests/unit/cassettes/test_idaho_describe_images.yaml', filter_headers=['authorization'])
    def test_idaho_describe_images(self):
        i = Idaho()
        catid = '10400100203F1300'
        description = i.describe_images(i.get_images_by_catid(catid=catid))
        assert description['10400100203F1300']['parts'][1]['PAN']['id'] == 'b1f6448b-aecd-4d9b-99ec-9cad8d079043'

    @my_vcr.use_cassette('tests/unit/cassettes/test_idaho_get_chip.yaml', filter_headers=['authorization'])
    def test_idaho_get_chip(self):
        i = Idaho()
        catid = '10400100203F1300'
        filename = os.path.join(self._temp_path, 'chip.tif')
        result = i.get_chip([-105.00032901763916, 39.91207173503864, -104.99874114990234, 39.91310862390189], catid, filename=filename)
        assert result

    @my_vcr.use_cassette('tests/unit/cassettes/test_idaho_get_chip2.yaml', filter_headers=['authorization'])
    def test_idaho_get_chip2(self):
        i = Idaho()
        catid = '10400100384B1B00'
        filename = os.path.join(self._temp_path, 'chip2.tif')
        result = i.get_chip([120.45363429504926, 30.247785383721883, 120.45511487442548, 30.249008773017273], catid, filename=filename)
        assert result