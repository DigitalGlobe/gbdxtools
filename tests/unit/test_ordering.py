'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Ordering class
'''

from gbdxtools import Interface
from gbdxtools.ordering import Ordering
import vcr
from auth_mock import get_mock_gbdx_session

# How to use the mock_gbdx_session and vcr to create unit tests:
# 1. Add a new test that is dependent upon actually hitting GBDX APIs.
# 2. Decorate the test with @vcr appropriately
# 3. replace "dummytoken" with a real gbdx token
# 4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
# 5. replace the real gbdx token with "dummytoken" again
# 6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)
mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
gbdx = Interface(gbdx_connection = mock_gbdx_session)

def test_init():
    o = Ordering(gbdx)
    assert isinstance(o, Ordering)

@vcr.use_cassette('tests/unit/cassettes/test_order_single_catid.yaml',filter_headers=['authorization'])
def test_order_single_catid():
	o = Ordering(gbdx)
	order_id = o.order('10400100120FEA00')
	# assert order_id == 'c5cd8157-3001-4a03-a716-4ef673748c7a'
	assert len(order_id) == 36

@vcr.use_cassette('tests/unit/cassettes/test_order_multi_catids.yaml',filter_headers=['authorization'])
def test_order_multi_catids():
	o = Ordering(gbdx)
	order_id = o.order(['10400100120FEA00','101001000DB2FB00'])
	# assert order_id == '2b3ba38e-4d7e-4ef6-ac9d-2e2e0a8ca1e7'
	assert len(order_id) == 36

@vcr.use_cassette('tests/unit/cassettes/test_get_order_status.yaml',filter_headers=['authorization'])
def test_get_order_status():
	o = Ordering(gbdx)
	r = o.status('c5cd8157-3001-4a03-a716-4ef673748c7a')
	print r.keys()
	assert 's3://bucketname/prefixname' in r.keys()

