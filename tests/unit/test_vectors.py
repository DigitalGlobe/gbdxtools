'''
Unit tests for the gbdxtools.Vectors class

See tests/readme.md for more about tests
'''

from gbdxtools import Interface
from gbdxtools.vectors import Vectors, AggregationDef, GeohashAggDef, \
                              DateHistogramAggDef, TermsAggDef, AvgAggDef, \
                              SumAggDef, AvgGeoLatAggDef, AvgGeoLonAggDef, CardinalityAggDef
from helpers import mockable_interface, gbdx_vcr 
import unittest
import types
import json

class TestVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gbdx = mockable_interface() 

    def test_init(self):
        c = Vectors()
        self.assertIsInstance(c, Vectors)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_search_1010.yaml')
    def test_vectors_search_paging(self):
        aoi = "POLYGON ((180 -90, 180 90, -180 90, -180 -90, 180 -90))"
        results = self.gbdx.vectors.query(aoi, query="item_type:WV03_VNIR", count=1010)

        self.assertEqual(len(results), 1010)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_search_55.yaml')
    def test_vectors_search_count_small(self):
        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        results = self.gbdx.vectors.query(aoi, query='item_type:WV02', count=55)

        self.assertEqual(len(results), 55)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_search_1.yaml')
    def test_vectors_search_count_single(self):
        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        results = self.gbdx.vectors.query(aoi, query="item_type:WV02", count=1)

        self.assertEqual(len(results), 1)


    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_search_index.yaml')
    def test_vectors_search_index(self):
        aoi = 'POLYGON ((-117.1 37.9, -117.1 38.1, -117.3 38.1, -117.3 37.9, -117.1 37.9))'
        results = self.gbdx.vectors.query(aoi, query="item_type:tweet", index="vector-sma-twitter*", count=100)

        self.assertEqual(len(results), 17)


    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_search_iterate.yaml')
    def test_vectors_search_iteratively(self):
        '''Run the same query directly and through paging'''

        aoi = "POLYGON((17 25, 18 25, 18 24, 17 24, 17 25))"
        query = "item_type:WV02"
        count = 150
        
        generator = self.gbdx.vectors.query_iteratively(aoi, query=query, count=count)
        results = self.gbdx.vectors.query(aoi, query=query, count=count)
        

        self.assertIsInstance(generator, types.GeneratorType)
        self.assertEqual(len(results), count) 
        self.assertEqual(len(list(generator)), len(results)) 

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_create_single.yaml')
    def test_vectors_create_single(self):
        results = self.gbdx.vectors.create({
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
            self.assertEqual(result, '/api/vector/vector-user-provided/e0f25c1c-9078-476b-ac5d-4c7fb08bb79a')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_create_multiple.yaml')
    def test_vectors_create_multiple(self):
        results = self.gbdx.vectors.create([{
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

        self.assertEqual(len(results), 2)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_create_from_wkt.yaml')
    def test_vectors_create_from_wkt(self):
        aoi = "POLYGON((0 3,3 3,3 0,0 0,0 3))"
        result = self.gbdx.vectors.create_from_wkt(
            aoi,
            item_type='test_type_123',
            ingest_source='api',
            attribute1='nothing',
            attribute2='something',
            number=6,
            date='2015-06-06'
        )
        self.assertEqual(result, '488f1b61-a539-447e-bced-e66563040a89')

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_with_default_index.yaml')
    def test_vectors_aggregate_query_with_default_index(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = 'terms:item_type'
        result = self.gbdx.vectors.aggregate_query(wkt, aggs)
        self.assertEqual(len(result), 1)
        self.assertIn('name', result[0])
        self.assertEqual(result[0]['name'],'terms:item_type')
        self.assertIn('terms', result[0])
        self.assertEqual(len(result[0]['terms']), 10)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_with_defined_index.yaml')
    def test_vectors_aggregate_query_with_defined_index(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = 'terms:item_type'
        result = self.gbdx.vectors.aggregate_query(wkt, aggs, index='read-vector-osm-*')
        self.assertEqual(len(result), 1)
        self.assertIn('name', result[0])
        self.assertEqual(result[0]['name'],'terms:item_type')
        self.assertIn('terms', result[0])
        self.assertEqual(len(result[0]['terms']), 10)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_simple.yaml')
    def test_vectors_aggregate_query_agg_string(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = 'terms:ingest_source'
        result = self.gbdx.vectors.aggregate_query(wkt, aggs)
        self.assertEqual(len(result), 1)
        self.assertIn('name', result[0])
        self.assertEqual(result[0]['name'],'terms:ingest_source')
        self.assertIn('terms', result[0])
        self.assertEqual(len(result[0]['terms']), 1)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_simple.yaml')
    def test_vectors_aggregate_query_agg_def(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        aggs = AggregationDef(agg_type='terms', value='ingest_source')
        result = self.gbdx.vectors.aggregate_query(wkt, aggs)
        self.assertEqual(len(result), 1)
        self.assertIn('name', result[0])
        self.assertEqual(result[0]['name'],'terms:ingest_source')
        self.assertIn('terms', result[0])
        self.assertEqual(len(result[0]['terms']), 1)

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_vectors_aggregate_query_complex.yaml')
    def test_vectors_aggregate_query_complex(self):
        wkt = 'POLYGON((-76.65 40.10, -76.65 40.14, -76.55 40.14, -76.55 40.10, -76.65 40.10))'
        child_agg = AggregationDef(agg_type='date_hist', value='month')
        aggs = AggregationDef(agg_type='geohash', value='4', children=child_agg)
        query = 'item_type:tweet'
        start_date = 'now-12M'
        end_date = 'now'
        result = self.gbdx.vectors.aggregate_query(wkt, aggs, index='vector-sma-twitter*', query=query, start_date=start_date, end_date=end_date)
        self.assertEqual(len(result), 1)
        self.assertIn('name', result[0])
        self.assertEqual(result[0]['name'],'geohash:4')
        self.assertIn('terms', result[0])
        terms = result[0]['terms']
        self.assertEqual(len(terms), 1)
        self.assertEqual(terms[0]['term'], 'dr1s')
        self.assertEqual(len(terms[0]['aggregations']), 1)
        self.assertEqual(len(terms[0]['aggregations'][0]['terms']), 2)

    def test_agg_def_repr_no_children(self):
        agg_def = AggregationDef(agg_type='terms', value='ingest_source')
        self.assertEqual(agg_def.__repr__(), 'terms:ingest_source')

    def test_agg_def_repr_with_children(self):
        grandkids = [
            AggregationDef(agg_type='cardinality', value='ingest_source'),
            AggregationDef(agg_type='terms', value='ingest_source')
        ]
        kid = AggregationDef(agg_type='date_hist', value='d', children=grandkids)
        agg_def = AggregationDef(agg_type='geohash', value='4', children=kid)
        self.assertEqual(agg_def.__repr__(), 'geohash:4;date_hist:d;(cardinality:ingest_source,terms:ingest_source)')

    def test_geohash_agg_def_constructor(self):
        agg_def = GeohashAggDef()
        self.assertEqual(agg_def.agg_type, 'geohash')
        self.assertEqual(agg_def.value, '3')

        agg_def = GeohashAggDef('6')
        self.assertEqual(agg_def.agg_type, 'geohash')
        self.assertEqual(agg_def.value, '6')

        child_def = TermsAggDef('item_type')
        agg_def = GeohashAggDef('2', children=child_def)
        self.assertEqual(agg_def.agg_type, 'geohash')
        self.assertEqual(agg_def.value, '2')
        self.assertEqual(agg_def.children, child_def)

    def test_date_hist_agg_def_constructor(self):
        agg_def = DateHistogramAggDef()
        self.assertEqual(agg_def.agg_type, 'date_hist')
        self.assertEqual(agg_def.value, 'M')

        agg_def = DateHistogramAggDef('w')
        self.assertEqual(agg_def.agg_type, 'date_hist')
        self.assertEqual(agg_def.value, 'w')

        child_def = TermsAggDef('item_type')
        agg_def = DateHistogramAggDef('d', children=child_def)
        self.assertEqual(agg_def.agg_type, 'date_hist')
        self.assertEqual(agg_def.value, 'd')
        self.assertEqual(agg_def.children, child_def)

    def test_terms_agg_def_constructor(self):
        agg_def = TermsAggDef('foo')
        self.assertEqual(agg_def.agg_type, 'terms')
        self.assertEqual(agg_def.value, 'foo')

        child_def = DateHistogramAggDef('d')
        agg_def = TermsAggDef('bar', children=child_def)
        self.assertEqual(agg_def.agg_type, 'terms')
        self.assertEqual(agg_def.value, 'bar')
        self.assertEqual(agg_def.children, child_def)

        with self.assertRaises(Exception) as context:
            agg_def = TermsAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_cardinality_agg_def_constructor(self):
        agg_def = CardinalityAggDef('foo')
        self.assertEqual(agg_def.agg_type, 'cardinality')
        self.assertEqual(agg_def.value, 'foo')

        with self.assertRaises(Exception) as context:
            agg_def = CardinalityAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_avg_agg_def_constructor(self):
        agg_def = AvgAggDef('foo')
        self.assertEqual(agg_def.agg_type, 'avg')
        self.assertEqual(agg_def.value, 'foo')

        with self.assertRaises(Exception) as context:
            agg_def = AvgAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_sum_agg_def_constructor(self):
        agg_def = SumAggDef('foo')
        self.assertEqual(agg_def.agg_type, 'sum')
        self.assertEqual(agg_def.value, 'foo')

        with self.assertRaises(Exception) as context:
            agg_def = SumAggDef()

        self.assertTrue('The "field" property cannot be empty.' in str(context.exception))

    def test_avg_geo_lat_agg_def_constructor(self):
        agg_def = AvgGeoLatAggDef()
        self.assertEqual(agg_def.agg_type, 'avg_geo_lat')
        self.assertFalse(agg_def.value)
        self.assertEqual(str(agg_def), 'avg_geo_lat')

    def test_avg_geo_lon_agg_def_constructor(self):
        agg_def = AvgGeoLonAggDef()
        self.assertEqual(agg_def.agg_type, 'avg_geo_lon')
        self.assertFalse(agg_def.value)
        self.assertEqual(str(agg_def), 'avg_geo_lon')