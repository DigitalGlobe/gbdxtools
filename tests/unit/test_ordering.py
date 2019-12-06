"""
Authors: Donnie Marino, Kostas Stamatiou

Unit tests for the gbdxtools.Ordering class
"""

from gbdxtools import Interface
from gbdxtools.ordering import Ordering
from auth_mock import get_mock_gbdx_session
import vcr
import unittest
from mock import Mock, patch


class OrderingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # create mock session, replace dummytoken with real token to create cassette
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)

    def test_init(self):
        o = Ordering()
        assert isinstance(o, Ordering)

    @vcr.use_cassette('tests/unit/cassettes/test_order_single_catid.yaml', filter_headers=['authorization'])
    def test_order_single_catid(self):
        o = Ordering()
        order_id = o.order('10400100120FEA00')
        # assert order_id == 'c5cd8157-3001-4a03-a716-4ef673748c7a'
        assert len(order_id) == 36

    @vcr.use_cassette('tests/unit/cassettes/test_order_multi_catids.yaml', filter_headers=['authorization'])
    def test_order_multi_catids(self):
        o = Ordering()
        order_id = o.order(['10400100120FEA00', '101001000DB2FB00'])
        # assert order_id == '2b3ba38e-4d7e-4ef6-ac9d-2e2e0a8ca1e7'
        assert len(order_id) == 36

    @vcr.use_cassette('tests/unit/cassettes/test_order_batching.yaml', filter_headers=['authorization'])
    def test_order_batching(self):
        o = Ordering()
        order_id = o.order(['10400100120FEA00', '101001000DB2FB00'], batch_size=1)
        # assert order_id == '2b3ba38e-4d7e-4ef6-ac9d-2e2e0a8ca1e7'
        assert len(order_id) == 2
        assert len(order_id[0]) == 36

    @vcr.use_cassette('tests/unit/cassettes/test_get_order_status.yaml', filter_headers=['authorization'])
    def test_get_order_status(self):
        o = Ordering()
        results = o.status('c5cd8157-3001-4a03-a716-4ef673748c7a')
        print(results)
        for result in results:
            assert 'acquisition_id' in result.keys()
            assert 'state' in result.keys()
            assert 'location' in result.keys()

    @vcr.use_cassette('tests/unit/cassettes/test_image_location.yaml', filter_headers=['authorization'])
    def test_order_batching(self):
        o = Ordering()
        res = o.location(['10400100120FEA00', '101001000DB2FB00'], batch_size=1)
        acq_list = res['acquisitions']
        assert len(acq_list) == 2
        for entry in res['acquisitions']:
            assert entry['location'].startswith('s3')

    @vcr.use_cassette('tests/unit/cassettes/test_heartbeat.yaml', filter_headers=['authorization'])
    def test_heartbeat(self):
        o = Ordering()
        assert o.heartbeat() == True

    def test_heartbeat_failure(self):
        # mock requests.get so that we get a result for which response.json() will throw an exception
        with patch('gbdxtools.ordering.requests.get', return_value = False) as mock_within:
            o = Ordering()
            assert o.heartbeat() == False


