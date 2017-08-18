"""
GBDX Catalog Interface.

Contact: nate.ricklin@digitalglobe.com
"""
from __future__ import absolute_import
from builtins import object

import requests
import json
import datetime

from gbdxtools.auth import Auth
from gbdxtools.ordering import Ordering

class Catalog(object):

    def __init__(self, **kwargs):
        ''' Construct the Catalog interface class

        Returns:
            An instance of the Catalog interface class.
        '''
        interface = Auth(**kwargs)
        self.base_url = '%s/catalog/v2' % interface.root_url
        self.gbdx_connection = interface.gbdx_connection
        self.logger = interface.logger

    def get_strip_footprint_wkt(self, catID):
        '''Retrieves the strip footprint WKT string given a cat ID.

        Args:
            catID (str): The source catalog ID from the platform catalog.

        Returns:
            footprint (str): A POLYGON of coordinates.
        '''

        self.logger.debug('Retrieving strip footprint')
        url = '%(base_url)s/record/%(catID)s?includeRelationships=false' % {
            'base_url': self.base_url, 'catID': catID
        }

        r = self.gbdx_connection.get(url)
        if r.status_code == 200:
            footprint = r.json()['properties']['footprintWkt']
            return footprint
        elif r.status_code == 404:
            self.logger.debug('Strip not found: %s' % catID)
            r.raise_for_status()
        else:
            self.logger.debug('There was a problem retrieving catid: %s' % catID)
            r.raise_for_status()

    def get(self, catID, includeRelationships=False):
        '''Retrieves the strip footprint WKT string given a cat ID.

        Args:
            catID (str): The source catalog ID from the platform catalog.
            includeRelationships (bool): whether to include graph links to related objects.  Default False.

        Returns:
            record (dict): A dict object identical to the json representation of the catalog record
        '''
        url = '%(base_url)s/record/%(catID)s' % {
            'base_url': self.base_url, 'catID': catID
        }
        r = self.gbdx_connection.get(url)
        r.raise_for_status()
        return r.json()


    def get_strip_metadata(self, catID):
        '''Retrieves the strip catalog metadata given a cat ID.

        Args:
            catID (str): The source catalog ID from the platform catalog.

        Returns:
            metadata (dict): A metadata dictionary .

            TODO: have this return a class object with interesting information exposed.
        '''

        self.logger.debug('Retrieving strip catalog metadata')
        url = '%(base_url)s/record/%(catID)s?includeRelationships=false' % {
            'base_url': self.base_url, 'catID': catID
        }
        r = self.gbdx_connection.get(url)
        if r.status_code == 200:
            return r.json()['properties']
        elif r.status_code == 404:
            self.logger.debug('Strip not found: %s' % catID)
            r.raise_for_status()
        else:
            self.logger.debug('There was a problem retrieving catid: %s' % catID)
            r.raise_for_status()


    def get_address_coords(self, address):
        ''' Use the google geocoder to get latitude and longitude for an address string

        Args:
            address: any address string

        Returns:
            A tuple of (lat,lng)
        '''
        url = "https://maps.googleapis.com/maps/api/geocode/json?&address=" + address
        r = requests.get(url)
        r.raise_for_status()
        results = r.json()['results']
        lat = results[0]['geometry']['location']['lat']
        lng = results[0]['geometry']['location']['lng']
        return lat, lng

    def search_address(self, address, filters=None, startDate=None, endDate=None, types=None):
        ''' Perform a catalog search over an address string

        Args:
            address: any address string
            filters: Array of filters.  Optional.  Example:
            [  
                "(sensorPlatformName = 'WORLDVIEW01' OR sensorPlatformName ='QUICKBIRD02')",
                "cloudCover < 10",
                "offNadirAngle < 10"
            ]
            startDate: string.  Optional.  Example: "2004-01-01T00:00:00.000Z"
            endDate: string.  Optional.  Example: "2004-01-01T00:00:00.000Z"
            types: Array of types to search for.  Optional.  Example (and default):  ["Acquisition"]

        Returns:
            catalog search resultset
        '''
        lat, lng = self.get_address_coords(address)
        return self.search_point(lat,lng, filters=filters, startDate=startDate, endDate=endDate, types=types)

    #def search_point(self, lat, lng, type="Acquisition")
    def search_point(self, lat, lng, filters=None, startDate=None, endDate=None, types=None, type=None):
        ''' Perform a catalog search over a specific point, specified by lat,lng

        Args:
            lat: latitude
            lng: longitude
            filters: Array of filters.  Optional.  Example:
            [  
                "(sensorPlatformName = 'WORLDVIEW01' OR sensorPlatformName ='QUICKBIRD02')",
                "cloudCover < 10",
                "offNadirAngle < 10"
            ]
            startDate: string.  Optional.  Example: "2004-01-01T00:00:00.000Z"
            endDate: string.  Optional.  Example: "2004-01-01T00:00:00.000Z"
            types: Array of types to search for.  Optional.  Example (and default):  ["Acquisition"]

        Returns:
            catalog search resultset
        '''
        searchAreaWkt = "POLYGON ((%s %s, %s %s, %s %s, %s %s, %s %s))" % (lng, lat,lng,lat,lng,lat,lng,lat,lng,lat)
        return self.search(searchAreaWkt=searchAreaWkt, filters=filters, startDate=startDate, endDate=endDate, types=types)

    def get_data_location(self, catalog_id):
        """
        Find and return the S3 data location given a catalog_id.

        Args:
            catalog_id: The catalog ID

        Returns:
            A string containing the s3 location of the data associated with a catalog ID.  Returns
            None if the catalog ID is not found, or if there is no data yet associated with it.
        """

        try:
            record = self.get(catalog_id)
        except:
            return None

        # Handle Landsat8
        if 'Landsat8' in record['type'] and 'LandsatAcquisition' in record['type']:
            bucket = record['properties']['bucketName']
            prefix = record['properties']['bucketPrefix']
            return 's3://' + bucket + '/' + prefix

        # Handle DG Acquisition
        if 'DigitalGlobeAcquisition' in record['type']:
            o = Ordering()
            res = o.location([catalog_id])
            return res['acquisitions'][0]['location']

        return None

    def search(self, searchAreaWkt=None, filters=None, startDate=None, endDate=None, types=None):
        ''' Perform a catalog search

        Args:
            searchAreaWkt: WKT Polygon of area to search.  Optional.
            filters: Array of filters.  Optional.  Example:
            [  
                "(sensorPlatformName = 'WORLDVIEW01' OR sensorPlatformName ='QUICKBIRD02')",
                "cloudCover < 10",
                "offNadirAngle < 10"
            ]
            startDate: string.  Optional.  Example: "2004-01-01T00:00:00.000Z"
            endDate: string.  Optional.  Example: "2004-01-01T00:00:00.000Z"
            types: Array of types to search for.  Optional.  Example (and default):  ["Acquisition"]

        Returns:
            catalog search resultset
        '''
        # Default to search for Acquisition type objects.
        if not types:
            types = ['Acquisition']

        # validation:  we must have either a WKT or one-week of time window
        if startDate:
            startDateTime = datetime.datetime.strptime(startDate, '%Y-%m-%dT%H:%M:%S.%fZ')

        if endDate:
            endDateTime = datetime.datetime.strptime(endDate, '%Y-%m-%dT%H:%M:%S.%fZ')

        if startDate and endDate:
            diff = endDateTime - startDateTime
            if diff.days < 0:
                raise Exception("startDate must come before endDate.")

        postdata = {  
            "searchAreaWkt": searchAreaWkt,
            "types": types, 
            "startDate": startDate,
            "endDate": endDate,
        }

        if filters:
            postdata['filters'] = filters

        if searchAreaWkt:
            postdata['searchAreaWkt'] = searchAreaWkt

        url = '%(base_url)s/search' % {
            'base_url': self.base_url
        }
        headers = {'Content-Type':'application/json'}
        r = self.gbdx_connection.post(url, headers=headers, data=json.dumps(postdata))
        r.raise_for_status()
        results = r.json()['results']
        
        return results

    def get_most_recent_images(self, results, types=[], sensors=[], N=1):
        ''' Return the most recent image 

        Args:
            results: a catalog resultset, as returned from a search
            types: array of types you want. optional.
            sensors: array of sensornames. optional.
            N: number of recent images to return.  defaults to 1.

        Returns:
            single catalog item, or none if not found

        '''
        if not len(results):
            return None

        # filter on type
        if types:
            results = [r for r in results if r['type'] in types]

        # filter on sensor
        if sensors:
            results = [r for r in results if r['properties'].get('sensorPlatformName') in sensors]


        # sort by date:
        #sorted(results, key=results.__getitem__('properties').get('timestamp'))
        newlist = sorted(results, key=lambda k: k['properties'].get('timestamp'), reverse=True) 
        return newlist[:N]
        







