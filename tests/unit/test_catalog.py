'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Catalog class
'''

from gbdxtools import Interface
from gbdxtools.catalog import Catalog
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
    c = Catalog(gbdx)
    assert isinstance(c, Catalog)

@vcr.use_cassette('tests/unit/cassettes/test_catalog_get_address_coords.yaml',filter_headers=['authorization'])
def test_catalog_get_address_coords():
	c = Catalog(gbdx)
	lat, lng = c.get_address_coords('Boulder, CO')
	assert lat == 40.0149856
	assert lng == -105.2705456

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_point.yaml',filter_headers=['authorization'])
def test_catalog_search_point():
	c = Catalog(gbdx)
	lat = 40.0149856
	lng = -105.2705456
	results = c.search_point(lat,lng)

	assert results['stats']['totalRecords'] == 310

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_address.yaml',filter_headers=['authorization'])
def test_catalog_search_address():
	c = Catalog(gbdx)
	results = c.search_address('Boulder, CO')

	assert results['stats']['totalRecords'] == 310
	

