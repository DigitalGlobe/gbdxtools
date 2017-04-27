"""
GBDX Vector Services Interface.

Contact: nate.ricklin@digitalglobe.com
"""
#from __future__ import absolute_import
from builtins import object
import six

import requests
from pygeoif import geometry
from geomet import wkt as wkt2geojson
from collections import OrderedDict
import json

from gbdxtools.auth import Auth


class Vectors(object):

    def __init__(self, **kwargs):
        ''' Construct the Vectors interface class

        Returns:
            An instance of the Vectors interface class.
        '''
        interface = Auth(**kwargs)
        self.gbdx_connection = interface.gbdx_connection
        self.logger = interface.logger
        self.query_url = 'https://vector.geobigdata.io/insight-vector/api/vectors/query/paging'
        self.query_index_url = 'https://vector.geobigdata.io/insight-vector/api/index/query/%s/paging'
        self.page_url = 'https://vector.geobigdata.io/insight-vector/api/vectors/paging'
        self.get_url = 'https://vector.geobigdata.io/insight-vector/api/vector/%s/'
        self.create_url = 'https://vector.geobigdata.io/insight-vector/api/vectors'
        self.aggregations_url = 'https://vector.geobigdata.io/insight-vector/api/aggregation'

    def create(self,vectors):
        """
        Create a vectors in the vector service.

        Args:
            vectors: A single geojson vector or a list of geojson vectors.  Each looks like:
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
                       "mascot" : "moth"
                    }
                }
              }

            item_type and ingest_source are required.

        Returns:
            a list of IDs of the vectors created
        """
        if type(vectors) is dict:
            vectors = [vectors]

        # validate they all have item_type and ingest_source in properties
        for vector in vectors:
            if not 'properties' in list(vector.keys()):
                raise Exception('Vector does not contain "properties" field.')

            if not 'item_type' in list(vector['properties'].keys()):
                raise Exception('Vector does not contain "item_type".')

            if not 'ingest_source' in list(vector['properties'].keys()):
                raise Exception('Vector does not contain "ingest_source".')

        r = self.gbdx_connection.post(self.create_url, data=json.dumps(vectors))
        r.raise_for_status()
        return r.json()

    def create_from_wkt(self, wkt, item_type, ingest_source, **attributes):
        '''
        Create a single vector in the vector service

        Args:
            wkt (str): wkt representation of the geometry
            item_type (str): item_type of the vector
            ingest_source (str): source of the vector
            attributes: a set of key-value pairs of attributes

        Returns:
            id (str): string identifier of the vector created
        '''
        # verify the "depth" of the attributes is single layer

        geojson = wkt2geojson.loads(wkt)
        vector = {
            'type': "Feature",
            'geometry': geojson,
            'properties': {
                'item_type': item_type,
                'ingest_source': ingest_source,
                'attributes': attributes
            }
        }

        return self.create(vector)[0]


    def get(self, ID, index='vector-web-s'):
        '''Retrieves a vector.  Not usually necessary because searching is the best way to find & get stuff.

        Args:
            ID (str): ID of the vector object
            index (str): Optional.  Index the object lives in.  defaults to 'vector-web-s'

        Returns:
            record (dict): A dict object identical to the json representation of the catalog record
        '''

        url = self.get_url % index
        r = self.gbdx_connection.get(url + ID)
        r.raise_for_status()
        return r.json()


    def query(self, searchAreaWkt, query, count=100, ttl='5m', index='vector-gbdx-alpha-catalog-v2*'):
        '''
        Perform a vector services query using the QUERY API
        (https://gbdxdocs.digitalglobe.com/docs/vs-query-list-vector-items-returns-default-fields)

        Args:
            searchAreaWkt: WKT Polygon of area to search
            query: Elastic Search query
            count: Maximum number of results to return
            ttl: Amount of time for each temporary vector page to exist

        Returns:
            List of vector results
    
        '''

        return list(self.query_iteratively(searchAreaWkt, query, count, ttl, index))


    def query_iteratively(self, searchAreaWkt, query, count=100, ttl='5m', index='vector-gbdx-alpha-catalog-v2*'):
        '''
        Perform a vector services query using the QUERY API
        (https://gbdxdocs.digitalglobe.com/docs/vs-query-list-vector-items-returns-default-fields)

        Args:
            searchAreaWkt: WKT Polygon of area to search
            query: Elastic Search query
            count: Maximum number of results to return
            ttl: Amount of time for each temporary vector page to exist

        Returns:
            generator of vector results
    
        '''

        search_area_polygon = geometry.from_wkt(searchAreaWkt)
        left, lower, right, upper = search_area_polygon.bounds

        params = {
            "q": query,
            "count": count,
            "ttl": ttl,
            "left": left,
            "right": right,
            "lower": lower,
            "upper": upper
        }

        # initialize paging request
        url = self.query_index_url % index if index else self.query_url
        r = self.gbdx_connection.get(url, params=params)
        r.raise_for_status()
        page = r.json()
        paging_id = page['next_paging_id']
        item_count = int(page['item_count'])
        data = page['data']

        for vector in data:
          yield vector

        # get vectors from each page
        while paging_id and item_count > 0:

          headers = {'Content-Type':'application/x-www-form-urlencoded'}
          data = {
              "pagingId": paging_id,
              "ttl": ttl
          }

          r = self.gbdx_connection.post(self.page_url, headers=headers, data=data)
          r.raise_for_status()
          page = r.json()
          paging_id = page['next_paging_id']
          item_count = int(page['item_count'])
          data = page['data']

          for vector in data:
            yield vector

    def aggregate_query(self, searchAreaWkt, agg_def, query=None, start_date=None, end_date=None, count=10):
        """Aggregates results of a query into buckets defined by the 'agg_def' parameter.  The aggregations are
        represented by dicts containing a 'name' key and a 'terms' key holding a list of the aggregation buckets.
        Each bucket element is a dict containing a 'term' key containing the term used for this bucket, a 'count' key
        containing the count of items that match this bucket, and an 'aggregations' key containing any child
        aggregations.

        Args:
            searchAreaWkt (str): wkt representation of the geometry
            agg_def (str or AggregationDef): the aggregation definitions
            query (str): a valid Elasticsearch query string to constrain the items going into the aggregation
            start_date (str): either an ISO-8601 date string or a 'now' expression (e.g. "now-6d" or just "now")
            end_date (str): either an ISO-8601 date string or a 'now' expression (e.g. "now-6d" or just "now")
            count (int): the number of buckets to include in the aggregations (the top N will be returned)

        Returns:
            results (list): A (usually single-element) list of dict objects containing the aggregation results.
        """

        geojson = wkt2geojson.loads(searchAreaWkt)
        aggs_str = str(agg_def) # could be string or AggregationDef

        params = {
            "count": count,
            "aggs": aggs_str
        }

        if query:
            params['query'] = query
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        r = self.gbdx_connection.post(self.aggregations_url, params=params, json=geojson)
        r.raise_for_status()

        return r.json(object_pairs_hook=OrderedDict)['aggregations']


class AggregationDef(object):

    def __init__(self, agg_type=None, value=None, children=None):
        """Constructs an aggregation definition.  Possible 'agg_type' values include:
         'geohash', 'date_hist', 'terms', 'avg', 'sum', 'cardinality' , 'avg_geo_lat', 'avg_geo_lon'.
         The 'value' parameter is specific to whichever aggregation type is specified.  For more,
         detail, please see the VectorServices aggregation REST API documentation.

        Args:
            agg_type(str): the aggregation type to define
            value(str): a value to supplement the type, often indicating how to divide up buckets
            children(str or AggregationDef): any child aggregations to be run on each bucket

        Returns:
            the created AggregationDef
        """
        self.agg_type = agg_type
        self.value = value
        self.children = children

    def __repr__(self):
        """Creates a string representation of an aggregation definition suitable for use in VectorServices calls

        Returns:
            A string representation of an aggregation definition suitable for use in VectorServices calls

        """
        if self.value:
            base = '%s:%s' % (self.agg_type, self.value)
        else:
            base = '%s' % self.agg_type

        if self.children:
            if isinstance(self.children, six.string_types):
                return '%s;%s' % (base, self.children)
            elif isinstance(self.children, AggregationDef):
                return '%s;%s' % (base, self.children.__repr__())
            else: # assume it's iterable
                kids = []
                for child in self.children:
                    kids.append(child.__repr__())
                kids_str = '(%s)' % ','.join(kids)
                return '%s;%s' % (base, kids_str)
        else:
            return base


class GeohashAggDef(AggregationDef):

    def __init__(self, hash_length='3', **kwargs):
        super(GeohashAggDef, self).__init__('geohash', hash_length, **kwargs)


class DateHistogramAggDef(AggregationDef):

    def __init__(self, bucket_period='M', **kwargs):
        super(DateHistogramAggDef, self).__init__('date_hist', bucket_period, **kwargs)


class FieldBasedAggDef(AggregationDef):

    def __init__(self, agg_type, field=None, **kwargs):

        if not field:
            raise Exception('The "field" property cannot be empty.')

        super(FieldBasedAggDef, self).__init__(agg_type, field, **kwargs)


class TermsAggDef(FieldBasedAggDef):

    def __init__(self, field=None, **kwargs):
        super(TermsAggDef, self).__init__('terms', field, **kwargs)


class CardinalityAggDef(FieldBasedAggDef):

    def __init__(self, field=None):
        super(CardinalityAggDef, self).__init__('cardinality', field)


class AvgAggDef(FieldBasedAggDef):

    def __init__(self, field=None):
        super(AvgAggDef, self).__init__('avg', field)


class SumAggDef(FieldBasedAggDef):

    def __init__(self, field=None):
        super(SumAggDef, self).__init__('sum', field)


class AvgGeoLatAggDef(AggregationDef):

    def __init__(self):
        super(AvgGeoLatAggDef, self).__init__('avg_geo_lat')


class AvgGeoLonAggDef(AggregationDef):

    def __init__(self):
        super(AvgGeoLonAggDef, self).__init__('avg_geo_lon')

