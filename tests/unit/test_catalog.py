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

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_wkt_only.yaml',filter_headers=['authorization'])
def test_catalog_search_wkt_only():
	c = Catalog(gbdx)
	results = c.search(searchAreaWkt="POLYGON ((30.1 9.9, 30.1 10.1, 29.9 10.1, 29.9 9.9, 30.1 9.9))")
	assert len(results) == 395

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_wkt_and_startDate.yaml',filter_headers=['authorization'])
def test_catalog_search_wkt_and_startDate():
	c = Catalog(gbdx)
	results = c.search(searchAreaWkt="POLYGON ((30.1 9.9, 30.1 10.1, 29.9 10.1, 29.9 9.9, 30.1 9.9))",
		               startDate='2012-01-01T00:00:00.000Z')
	assert len(results) == 317

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_wkt_and_endDate.yaml',filter_headers=['authorization'])
def test_catalog_search_wkt_and_endDate():
	c = Catalog(gbdx)
	results = c.search(searchAreaWkt="POLYGON ((30.1 9.9, 30.1 10.1, 29.9 10.1, 29.9 9.9, 30.1 9.9))",
		               endDate='2012-01-01T00:00:00.000Z')
	assert len(results) == 78

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_startDate_and_endDate_only_more_than_one_week_apart.yaml',filter_headers=['authorization'])
def test_catalog_search_startDate_and_endDate_only_more_than_one_week_apart():
	c = Catalog(gbdx)

	try:
		results = c.search(startDate='2004-01-01T00:00:00.000Z',
					   	endDate='2012-01-01T00:00:00.000Z')
	except Exception as e:
		pass
	else:
		raise Exception('failed test')


@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_startDate_and_endDate_only_less_than_one_week_apart.yaml',filter_headers=['authorization'])
def test_catalog_search_startDate_and_endDate_only_less_than_one_week_apart():
	c = Catalog(gbdx)

	results = c.search(startDate='2008-01-01T00:00:00.000Z',
					   	endDate='2008-01-03T00:00:00.000Z')

	assert len(results) == 759


@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_filters1.yaml',filter_headers=['authorization'])
def test_catalog_search_filters1():
	c = Catalog(gbdx)

	filters = [  
                    "(sensorPlatformName = 'WORLDVIEW01' OR sensorPlatformName ='QUICKBIRD02')",
                    "cloudCover < 10",
                    "offNadirAngle < 10"
                ]

	results = c.search(startDate='2008-01-01T00:00:00.000Z',
					   	endDate='2012-01-03T00:00:00.000Z',
					   	filters=filters,
					   	searchAreaWkt="POLYGON ((30.1 9.9, 30.1 10.1, 29.9 10.1, 29.9 9.9, 30.1 9.9))")

	for result in results:
		assert result['properties']['sensorPlatformName'] in ['WORLDVIEW01','QUICKBIRD02']
		assert float(result['properties']['cloudCover']) < 10
		assert float(result['properties']['offNadirAngle']) < 10

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_filters2.yaml',filter_headers=['authorization'])
def test_catalog_search_filters2():
	c = Catalog(gbdx)

	filters = [  
                    "sensorPlatformName = 'WORLDVIEW03'"
                ]

	results = c.search(filters=filters,
					   searchAreaWkt="POLYGON ((30.1 9.9, 30.1 10.1, 29.9 10.1, 29.9 9.9, 30.1 9.9))")

	for result in results:
		assert result['properties']['sensorPlatformName'] in ['WORLDVIEW03']

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_types1.yaml',filter_headers=['authorization'])
def test_catalog_search_types1():
	c = Catalog(gbdx)

	types = [ "LandsatAcquisition" ]

	results = c.search(types=types,
					   searchAreaWkt="POLYGON ((30.1 9.9, 30.1 10.1, 29.9 10.1, 29.9 9.9, 30.1 9.9))")

	for result in results:
		assert result['type'] == 'LandsatAcquisition'

@vcr.use_cassette('tests/unit/cassettes/test_catalog_search_huge_aoi.yaml',filter_headers=['authorization'])
def test_catalog_search_huge_aoi():
	"""
	Search an AOI the size of utah, broken into multiple smaller searches
	"""
	c = Catalog(gbdx)

	results = c.search(searchAreaWkt = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))")
	
	assert len(results) == 2736

@vcr.use_cassette('tests/unit/cassettes/test_catalog_get_data_location_DG.yaml',filter_headers=['authorization'])
def test_catalog_get_data_location_DG():
	c = Catalog(gbdx)
	s3path = c.get_data_location(catalog_id='1030010045539700')
	assert s3path == 's3://receiving-dgcs-tdgplatform-com/055158926010_01_003/055158926010_01'

@vcr.use_cassette('tests/unit/cassettes/test_catalog_get_data_location_Landsat.yaml',filter_headers=['authorization'])
def test_catalog_get_data_location_Landsat():
	c = Catalog(gbdx)
	s3path = c.get_data_location(catalog_id='LC81740532014364LGN00')
	assert s3path == 's3://landsat-pds/L8/174/053/LC81740532014364LGN00'

