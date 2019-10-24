'''
Unit tests for the gbdxtools.Vectors class
'''

from gbdxtools import Interface
from gbdxtools.vectors import Vectors, AggregationDef, GeohashAggDef, \
                              DateHistogramAggDef, TermsAggDef, AvgAggDef, \
                              SumAggDef, AvgGeoLatAggDef, AvgGeoLonAggDef, CardinalityAggDef
from auth_mock import get_mock_gbdx_session
import vcr
import unittest
import types
import json

"""
How to use the mock_gbdx_session and vcr to create unit tests:
1. Add a new test that is dependent upon actually hitting GBDX APIs.
2. Decorate the test with @vcr appropriately, supply a yaml file path to gbdxtools/tests/unit/cassettes
    note: a yaml file will be created after the test is run

3. Replace "dummytoken" with a real gbdx token after running test successfully
4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
5. Replace the real gbdx token with "dummytoken" again
6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)
"""

class TestVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)
        #cls.gbdx = Interface()

    def test_init(self):
        c = Vectors()
        self.assertTrue(isinstance(c, Vectors))

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search_1010.yaml', filter_headers=['authorization'], match_on=['method', 'scheme', 'host', 'port', 'path'])
    def test_vectors_search_paging(self):
        v = Vectors()
        aoi = "POLYGON ((180 -90, 180 90, -180 90, -180 -90, 180 -90))"
        results = v.query(aoi, query="item_type:WV03_VNIR", count=1010)

        assert len(results) == 1010

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search_1000.yaml', filter_headers=['authorization'], match_on=['method', 'scheme', 'host', 'port', 'path'])
    def test_vectors_search(self):
        v = Vectors()
        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        results = v.query(aoi, query='item_type:WV02', count=1000)

        assert len(results) == 218 

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search_55.yaml', filter_headers=['authorization'], match_on=['method', 'scheme', 'host', 'port', 'path'])
    def test_vectors_search_count_small(self):
        v = Vectors()
        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        results = v.query(aoi, query='item_type:WV02', count=55)

        assert len(results) == 55

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search_1.yaml', filter_headers=['authorization'], match_on=['method', 'scheme', 'host', 'port', 'path'])
    def test_vectors_search_count_single(self):
        v = Vectors()
        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        results = v.query(aoi, query="item_type:WV02", count=1)

        assert len(results) == 1

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search_310.yaml', filter_headers=['authorization'], match_on=['method', 'scheme', 'host', 'port', 'path'])
    def test_vectors_search_count_equal_to_num_records(self):
        v = Vectors()
        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        results = v.query(aoi, query="item_type:WV02", count=218)

        assert len(results) == 218

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search_index.yaml', filter_headers=['authorization'], match_on=['method', 'scheme', 'host', 'port', 'path'])
    def test_vectors_search_index(self):
        v = Vectors()
        aoi = "POLYGON((17.75390625 25.418470119273117,24.08203125 25.418470119273117,24.08203125 19.409611549990895,17.75390625 19.409611549990895,17.75390625 25.418470119273117))"
        aoi = 'POLYGON ((-117.1142580000000066 37.9875040000000013, -117.1142580000000066 38.1431979999999982, -117.3339840000000009 38.1431979999999982, -117.3339840000000009 37.9875040000000013, -117.1142580000000066 37.9875040000000013))'
        results = v.query(aoi, query="item_type:tweet", index="vector-sma-twitter*", count=1000)

        assert len(results) == 114

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search_interate.yaml', filter_headers=['authorization'], match_on=['method', 'scheme', 'host', 'port', 'path'])
    def test_vectors_search_iteratively(self):
        v = Vectors()
        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        g = v.query_iteratively(aoi, query="item_type:WV02", count=1000)

        count = 0
        for vector in g:
          count += 1

        assert isinstance(g, types.GeneratorType)
        assert count == 218 

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_create_single.yaml', filter_headers=['authorization'])
    def test_vectors_create_single(self):
        v = Vectors()
        results = v.create({
            "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.0,1.0]
                },
                "properties": {
                    "text" : "item text",
                    "name" : "item name",
                    "item_type" : "type",
                    "ingest_source" : "source",
                    "attributes" : {
                       "latitude" : 1,
                       "institute_founded" : "2015-07-17",
                       "mascot" : "moth"
                    }
                }
          })

        for result in results['successfulItemIds']:
            assert result == '/api/vector/vector-user-provided/7411195a-ea4d-428a-bc3c-b92b0e5aa057'

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_create_multiple.yaml', filter_headers=['authorization'])
    def test_vectors_create_multiple(self):
        v = Vectors()
        results = v.create([{
            "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.0,1.0]
                },
                "properties": {
                    "text" : "item text",
                    "name" : "item name",
                    "item_type" : "type",
                    "ingest_source" : "source",
                    "attributes" : {
                       "latitude" : 1,
                       "institute_founded" : "2015-07-17",
                       "mascot" : "moth"
                    }
                }
          },
          {
            "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.0,1.0]
                },
                "properties": {
                    "text" : "item text",
                    "name" : "item name",
                    "item_type" : "type",
                    "ingest_source" : "source",
                    "attributes" : {
                       "latitude" : 1,
                       "institute_founded" : "2015-07-17",
                       "mascot" : "asdfadsfadf"
                    }
                }
          }])

        assert len(results) == 2

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_create_from_wkt.yaml', filter_headers=['authorization'])
    def test_vectors_create_from_wkt(self):
        v = Vectors()

        aoi = "POLYGON((0 3,3 3,3 0,0 0,0 3))"
        result = v.create_from_wkt(
            aoi,
            item_type='test_type_123',
            ingest_source='api',
            attribute1='nothing',
            attribute2='something',
            number=6,
            date='2015-06-06'
        )
        assert result == '2bfe706c-6247-482a-b53c-e55efab08330'

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_with_default_index.yaml', filter_headers=['authorization'])
    def test_vectors_aggregate_query_with_default_index(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = 'terms:item_type'
        v = Vectors()
        result = v.aggregate_query(wkt, aggs)
        assert len(result) == 1
        assert 'name' in result[0]
        assert result[0]['name'] == 'terms:item_type'
        assert 'terms' in result[0]
        assert len(result[0]['terms']) == 10

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_with_defined_index.yaml', filter_headers=['authorization'])
    def test_vectors_aggregate_query_with_defined_index(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = 'terms:item_type'
        v = Vectors()
        result = v.aggregate_query(wkt, aggs, index='read-vector-osm-*')
        assert len(result) == 1
        assert 'name' in result[0]
        assert result[0]['name'] == 'terms:item_type'
        assert 'terms' in result[0]
        assert len(result[0]['terms']) == 10

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_simple.yaml', filter_headers=['authorization'])
    def test_vectors_aggregate_query_agg_string(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = 'terms:ingest_source'
        v = Vectors()
        result = v.aggregate_query(wkt, aggs)
        assert len(result) == 1
        assert 'name' in result[0]
        assert result[0]['name'] == 'terms:ingest_source'
        assert 'terms' in result[0]
        assert len(result[0]['terms']) == 1

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_simple.yaml', filter_headers=['authorization'])
    def test_vectors_aggregate_query_agg_def(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = AggregationDef(agg_type='terms', value='ingest_source')
        v = Vectors()
        result = v.aggregate_query(wkt, aggs)
        assert len(result) == 1
        assert 'name' in result[0]
        assert result[0]['name'] == 'terms:ingest_source'
        assert 'terms' in result[0]
        assert len(result[0]['terms']) == 1

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_complex.yaml', filter_headers=['authorization'])
    def test_vectors_aggregate_query_complex(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        child_agg = AggregationDef(agg_type='date_hist', value='month')
        aggs = AggregationDef(agg_type='geohash', value='4', children=child_agg)
        v = Vectors()
        query = 'item_type:tweet'
        start_date = 'now-2M'
        end_date = 'now'
        result = v.aggregate_query(wkt, aggs, index='vector-sma-twitter*', query=query, start_date=start_date, end_date=end_date)
        assert len(result) == 1
        assert 'name' in result[0]
        assert result[0]['name'] == 'geohash:4'
        assert 'terms' in result[0]
        terms = result[0]['terms']
        assert len(terms) == 2 
        assert terms[0]['term'] == 'dr1s'
        assert len(terms[0]['aggregations']) == 1
        assert len(terms[0]['aggregations'][0]['terms']) == 5

    def test_agg_def_repr_no_children(self):
        agg_def = AggregationDef(agg_type='terms', value='ingest_source')
        assert agg_def.__repr__() == 'terms:ingest_source'

    def test_agg_def_repr_with_children(self):
        grandkids = [
            AggregationDef(agg_type='cardinality', value='ingest_source'),
            AggregationDef(agg_type='terms', value='ingest_source')
        ]
        kid = AggregationDef(agg_type='date_hist', value='d', children=grandkids)
        agg_def = AggregationDef(agg_type='geohash', value='4', children=kid)
        assert agg_def.__repr__() == 'geohash:4;date_hist:d;(cardinality:ingest_source,terms:ingest_source)'

    def test_geohash_agg_def_constructor(self):
        agg_def = GeohashAggDef()
        assert agg_def.agg_type == 'geohash'
        assert agg_def.value == '3'

        agg_def = GeohashAggDef('6')
        assert agg_def.agg_type == 'geohash'
        assert agg_def.value == '6'

        child_def = TermsAggDef('item_type')
        agg_def = GeohashAggDef('2', children=child_def)
        assert agg_def.agg_type == 'geohash'
        assert agg_def.value == '2'
        assert agg_def.children == child_def

    def test_date_hist_agg_def_constructor(self):
        agg_def = DateHistogramAggDef()
        assert agg_def.agg_type == 'date_hist'
        assert agg_def.value == 'M'

        agg_def = DateHistogramAggDef('w')
        assert agg_def.agg_type == 'date_hist'
        assert agg_def.value == 'w'

        child_def = TermsAggDef('item_type')
        agg_def = DateHistogramAggDef('d', children=child_def)
        assert agg_def.agg_type == 'date_hist'
        assert agg_def.value == 'd'
        assert agg_def.children == child_def

    def test_terms_agg_def_constructor(self):
        agg_def = TermsAggDef('foo')
        assert agg_def.agg_type == 'terms'
        assert agg_def.value == 'foo'

        child_def = DateHistogramAggDef('d')
        agg_def = TermsAggDef('bar', children=child_def)
        assert agg_def.agg_type == 'terms'
        assert agg_def.value == 'bar'
        assert agg_def.children == child_def

        with self.assertRaises(Exception) as context:
            agg_def = TermsAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_cardinality_agg_def_constructor(self):
        agg_def = CardinalityAggDef('foo')
        assert agg_def.agg_type == 'cardinality'
        assert agg_def.value == 'foo'

        with self.assertRaises(Exception) as context:
            agg_def = CardinalityAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_avg_agg_def_constructor(self):
        agg_def = AvgAggDef('foo')
        assert agg_def.agg_type == 'avg'
        assert agg_def.value == 'foo'

        with self.assertRaises(Exception) as context:
            agg_def = AvgAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_sum_agg_def_constructor(self):
        agg_def = SumAggDef('foo')
        assert agg_def.agg_type == 'sum'
        assert agg_def.value == 'foo'

        with self.assertRaises(Exception) as context:
            agg_def = SumAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_avg_geo_lat_agg_def_constructor(self):
        agg_def = AvgGeoLatAggDef()
        assert agg_def.agg_type == 'avg_geo_lat'
        assert not agg_def.value
        assert str(agg_def) == 'avg_geo_lat'

    def test_avg_geo_lon_agg_def_constructor(self):
        agg_def = AvgGeoLonAggDef()
        assert agg_def.agg_type == 'avg_geo_lon'
        assert not agg_def.value
        assert str(agg_def) == 'avg_geo_lon'




