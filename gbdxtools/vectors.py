"""
GBDX Vector Services Interface.

Contact: nate.ricklin@digitalglobe.com
"""
from __future__ import absolute_import
from builtins import object

import requests
from pygeoif import geometry

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

        


    



