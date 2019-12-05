"""
GBDX Vector Services Interface.

Contact: nate.ricklin@digitalglobe.com
"""
#from __future__ import absolute_import
from string import Template
from builtins import object
import six

from imageio import imsave

import base64
from io import BytesIO
import dask.array as da

import requests
from shapely.wkt import loads as load_wkt
from collections import OrderedDict
import json, time, os

from shapely.ops import cascaded_union
from shapely.geometry import shape, box, mapping

from gbdxtools.vector_layers import VectorGeojsonLayer, VectorTileLayer, \
                                    ImageLayer
from gbdxtools.map_templates import BaseTemplate
from gbdxtools.auth import Auth


class Vectors(object):
    default_index = 'vector-gbdx-alpha-catalog-v2-*'

    def __init__(self, **kwargs):
        ''' Construct the Vectors interface class

        Returns:
            An instance of the Vectors interface class.
        '''
        interface = Auth(**kwargs)
        self.gbdx_connection = interface.gbdx_connection
        self.logger = interface.logger
        self.query_url = 'https://vector.geobigdata.io/insight-vector/api/vectors/query/items'
        self.query_index_url = 'https://vector.geobigdata.io/insight-vector/api/index/query/%s/items'
        self.query_page_url = 'https://vector.geobigdata.io/insight-vector/api/vectors/query/paging'
        self.query_index_page_url = 'https://vector.geobigdata.io/insight-vector/api/index/query/%s/paging'
        self.page_url = 'https://vector.geobigdata.io/insight-vector/api/vectors/paging'
        self.get_url = 'https://vector.geobigdata.io/insight-vector/api/vector/%s/'
        self.create_url = 'https://vector.geobigdata.io/insight-vector/api/vectors'
        self.aggregations_url = 'https://vector.geobigdata.io/insight-vector/api/aggregation'
        self.aggregations_by_index_url = 'https://vector.geobigdata.io/insight-vector/api/index/aggregation/%s'

    def create(self, vectors, index=None):
        """ Create a vectors in the vector service.

        Args:
            vectors: A single geojson vector or a list of geojson vectors. Item_type and ingest_source are required.
            index (str): optional index to write to, defaults to 'vector-user-provided'

        Returns:
            (dict): key 'SuccessfulItemIds' is a list of succesfully created feature URLs
                    key 'errorMessages' is a list of failed feature error messages

        Example:
            >>> vectors.create(
            ...     {
            ...         "type": "Feature",
            ...         "geometry": {
            ...             "type": "Point",
            ...             "coordinates": [1.0,1.0]
            ...         },
            ...         "properties": {
            ...             "text" : "item text",
            ...             "name" : "item name",
            ...             "item_type" : "type",
            ...             "ingest_source" : "source",
            ...             "attributes" : {
            ...                 "latitude" : 1,
            ...                 "institute_founded" : "2015-07-17",
            ...                 "mascot" : "moth"
            ...             }
            ...         }
            ...     }
            ... )

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

        url = self.create_url
        if index is not None:
            url = '%s/%s/' % (url, index)
        r = self.gbdx_connection.post(url, data=json.dumps(vectors))
        r.raise_for_status()
        return r.json()

    def create_from_wkt(self, wkt, item_type, ingest_source, index=None, **attributes):
        '''
        Create a single vector in the vector service

        Args:
            wkt (str): wkt representation of the geometry
            item_type (str): item_type of the vector
            ingest_source (str): source of the vector
            attributes: a set of key-value pairs of attributes
            index (str): optional index to write to, defaults to 'vector-user-provided'

        Returns:
            (str): feature ID
        '''
        # verify the "depth" of the attributes is single layer

        geojson = load_wkt(wkt).__geo_interface__
        vector = {
            'type': "Feature",
            'geometry': geojson,
            'properties': {
                'item_type': item_type,
                'ingest_source': ingest_source,
                'attributes': attributes
            }
        }

        results =  self.create(vector, index=index)
        if len(results['errorMessages']) == 0:
            item = results['successfulItemIds'][0]
            return item.split('/')[-1]
        else:
            raise Exception(results['errorMessages'][0])

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


    def query(self, searchAreaWkt, query, count=100, ttl='5m', index=default_index):
        '''
        Perform a vector services query using the QUERY API
        (https://gbdxdocs.digitalglobe.com/docs/vs-query-list-vector-items-returns-default-fields)

        ElasticSearch spatial indexing has some slop in it and can return some features that are 
        near to but not overlapping the search geometry. If you need precise overlapping of the
        search API you will need to run a geometric check on each result.

        Args:
            searchAreaWkt: WKT Polygon of area to search
            query: Elastic Search query
            count: Maximum number of results to return, default is 100
            ttl: Amount of time for each temporary vector page to exist

        Returns:
            List of vector results
    
        '''
        if count < 1000:
            # issue a single page query
            search_area_polygon = load_wkt(searchAreaWkt)
            geojson = json.dumps(mapping(search_area_polygon))

            params = {
                "q": query,
                "count": min(count,1000),
            }

            url = self.query_index_url % index if index else self.query_url
            r = self.gbdx_connection.post(url, data=geojson, params=params)
            r.raise_for_status()
            return r.json()

        else:
            return list(self.query_iteratively(searchAreaWkt, query, count, ttl, index))


    def query_iteratively(self, searchAreaWkt, query, count=100, ttl='5m', index=default_index):
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

        search_area_polygon = load_wkt(searchAreaWkt)
        geojson = json.dumps(mapping(search_area_polygon))

        params = {
            "q": query,
            "count": min(count,1000),
            "ttl": ttl,
        }

        # initialize paging request
        url = self.query_index_page_url % index if index else self.query_page_url
        r = self.gbdx_connection.post(url, params=params, data=geojson)
        r.raise_for_status()
        page = r.json()
        paging_id = page['next_paging_id']
        item_count = int(page['item_count'])
        data = page['data']

        num_results = 0
        for vector in data:
          num_results += 1
          if num_results > count: break
          yield vector

        if num_results == count:
          return


        # get vectors from each page
        while paging_id and item_count > 0 and num_results < count:

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
              num_results += 1
              if num_results > count: break
              yield vector

    def aggregate_query(self, searchAreaWkt, agg_def, query=None, start_date=None, end_date=None, count=10, index=default_index):
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
            index (str): the index (or alias or wildcard index expression) to run aggregations against, set to None for the entire set of vector indexes

        Returns:
            results (list): A (usually single-element) list of dict objects containing the aggregation results.
        """

        geojson = load_wkt(searchAreaWkt).__geo_interface__
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

        url = self.aggregations_by_index_url % index if index else self.aggregations_url

        r = self.gbdx_connection.post(url, params=params, json=geojson)
        r.raise_for_status()

        return r.json(object_pairs_hook=OrderedDict)['aggregations']

    def tilemap(self, query, styles={}, bbox=[-180,-90,180,90], zoom=16, 
                      api_key=os.environ.get('MAPBOX_API_KEY', None), 
                      image=None, image_bounds=None,
                      index="vector-user-provided", name="GBDX_Task_Output", **kwargs):
        """
          Renders a mapbox gl map from a vector service query
        """
        try:
            from IPython.display import display
        except:
            print("IPython is required to produce maps.")
            return

        assert api_key is not None, "No Mapbox API Key found. You can either pass in a token or set the MAPBOX_API_KEY environment variable."

        wkt = box(*bbox).wkt
        features = self.query(wkt, query, index=index)

        union = cascaded_union([shape(f['geometry']) for f in features])
        lon, lat = union.centroid.coords[0]
        url = 'https://vector.geobigdata.io/insight-vector/api/mvt/{z}/{x}/{y}?';
        url += 'q={}&index={}'.format(query, index);

        if styles is not None and not isinstance(styles, list):
            styles = [styles]

        map_id = "map_{}".format(str(int(time.time())))
        map_data = VectorTileLayer(url, source_name=name, styles=styles, **kwargs)
        image_layer = self._build_image_layer(image, image_bounds)

        template = BaseTemplate(map_id, **{
            "lat": lat,
            "lon": lon,
            "zoom": zoom,
            "datasource": json.dumps(map_data.datasource),
            "layers": json.dumps(map_data.layers),
            "image_layer": image_layer,
            "mbkey": api_key,
            "token": self.gbdx_connection.access_token
        })
        
        template.inject() 


    def map(self, features=None, query=None, styles=None,
                  bbox=[-180,-90,180,90], zoom=10, center=None, 
                  image=None, image_bounds=None, cmap='viridis',
                  api_key=os.environ.get('MAPBOX_API_KEY', None), **kwargs):
        """
          Renders a mapbox gl map from a vector service query or a list of geojson features

          Args:
            features (list): a list of geojson features
            query (str): a VectorServices query 
            styles (list): a list of VectorStyles to apply to the features  
            bbox (list): a bounding box to query for features ([minx, miny, maxx, maxy])
            zoom (int): the initial zoom level of the map
            center (list): a list of [lat, lon] used to center the map
            api_key (str): a valid Mapbox API key
            image (dict): a CatalogImage or a ndarray
            image_bounds (list): a list of bounds for image positioning 
            Use outside of GBDX Notebooks requires a MapBox API key, sign up for free at https://www.mapbox.com/pricing/
            Pass the key using the `api_key` keyword or set an environmental variable called `MAPBOX API KEY`
            cmap (str): MatPlotLib colormap to use for rendering single band images (default: viridis)
        """
        try:
            from IPython.display import display
        except:
            print("IPython is required to produce maps.")
            return

        assert api_key is not None, "No Mapbox API Key found. You can either pass in a key or set the MAPBOX_API_KEY environment variable. Use outside of GBDX Notebooks requires a MapBox API key, sign up for free at https://www.mapbox.com/pricing/"
        if features is None and query is not None:
            wkt = box(*bbox).wkt
            features = self.query(wkt, query, index=None)
        elif features is None and query is None and image is None:
            print('Must provide either a list of features or a query or an image')
            return

        if styles is not None and not isinstance(styles, list):
            styles = [styles]

        geojson = {"type":"FeatureCollection", "features": features}

        if center is None and features is not None:
            union = cascaded_union([shape(f['geometry']) for f in features])
            lon, lat = union.centroid.coords[0]
        elif center is None and image is not None:
            try:
                lon, lat = shape(image).centroid.coords[0]
            except:
                lon, lat = box(*image_bounds).centroid.coords[0]
        else:
            lat, lon = center

        map_id = "map_{}".format(str(int(time.time())))
        map_data = VectorGeojsonLayer(geojson, styles=styles, **kwargs)
        image_layer = self._build_image_layer(image, image_bounds, cmap)

        template = BaseTemplate(map_id, **{
            "lat": lat, 
            "lon": lon, 
            "zoom": zoom,
            "datasource": json.dumps(map_data.datasource),
            "layers": json.dumps(map_data.layers),
            "image_layer": image_layer,
            "mbkey": api_key,
            "token": 'dummy'
        })
        template.inject()

    def _build_image_layer(self, image, image_bounds, cmap='viridis'):
        if image is not None:
            if isinstance(image, da.Array):
                if len(image.shape) == 2 or \
                    (image.shape[0] == 1 and len(image.shape) == 3):
                    arr = image.compute()
                else:
                    arr = image.rgb()
                coords = box(*image.bounds)
            else:
                assert image_bounds is not None, "Must pass image_bounds with ndarray images"
                arr = image
                coords = box(*image_bounds)
            b64 = self._encode_image(arr, cmap)
            return ImageLayer(b64, self._polygon_coords(coords))
        else:
            return 'false';

    def _polygon_coords(self, g):
        c = list(map(list, list(g.exterior.coords)))
        return [c[2], c[1], c[0], c[3]]

    def _encode_image(self, arr, cmap):
        io = BytesIO()
        imsave(io, arr, cmap=cmap)
        io.seek(0)
        img_str = base64.b64encode(io.getvalue()).decode()
        return 'data:image/{};base64,{}'.format('png', img_str)

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

