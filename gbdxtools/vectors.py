"""
GBDX Vector Services Interface.

Contact: nate.ricklin@digitalglobe.com
"""
#from __future__ import absolute_import
from builtins import object

import requests
from pygeoif import geometry
from geomet import wkt as wkt2geojson
import json

class Vectors(object):

    def __init__(self, interface):
        ''' Construct the Vectors interface class

        Args:
            interface: A reference to the GBDX Interface.

        Returns:
            An instance of the Vectors interface class.
        '''
        self.gbdx_connection = interface.gbdx_connection
        self.logger = interface.logger
        self.query_url = 'https://vector.geobigdata.io/insight-vector/api/vectors/query/items'
        self.get_url = 'https://vector.geobigdata.io/insight-vector/api/vector/%s/'
        self.create_url = 'https://vector.geobigdata.io/insight-vector/api/vectors'

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


    def query(self, searchAreaWkt, query, count=100):
        '''
        Perform a vector services query using the QUERY API
        (https://gbdxdocs.digitalglobe.com/docs/vs-query-list-vector-items-returns-default-fields)

        Args:
            searchAreaWkt: WKT Polygon of area to search
            query: Elastic Search query
            count: Maximum number of results to return

        Returns:
            List of vector results
    
        '''

        search_area_polygon = geometry.from_wkt(searchAreaWkt)
        left, lower, right, upper = search_area_polygon.bounds

        params = {
            "q": query,
            "count": count,
            "left": left,
            "right": right,
            "lower": lower,
            "upper": upper
        }

        r = self.gbdx_connection.get(self.query_url, params=params)
        r.raise_for_status()
        return r.json()

        


    



