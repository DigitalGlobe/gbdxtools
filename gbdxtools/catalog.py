"""
GBDX Catalog Interface.

Contact: nate.ricklin@digitalglobe.com
"""
from __future__ import absolute_import
from builtins import object

import requests
import json
import datetime
from . import catalog_search_aoi

class Catalog(object):

    def __init__(self, interface):
        ''' Construct the Catalog interface class

        Args:
            interface: A reference to the GBDX Interface.

        Returns:
            An instance of the Catalog interface class.
        '''
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
        url = ('https://geobigdata.io/catalog/v1/record/' 
               + catID + '?includeRelationships=false')

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
        if includeRelationships:
            incR = 'true'
        else:
            incR = 'false'
        url = 'https://geobigdata.io/catalog/v1/record/' + catID + '?includeRelationships='+incR
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
        url = ('https://geobigdata.io/catalog/v1/record/'
               + catID + '?includeRelationships=false')

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
        # There are so far only two possibilities for data we can find in S3: Landsat8 and DG images.
        # We'll do a traverse from the item and use that to determine S3 locations.

        url = 'https://geobigdata.io/catalog/v1/traverse'
        headers = {'Content-Type':'application/json'}
        traverse_body = {
                "rootRecordId": catalog_id,
                "maxdepth": 2,
                "direction": "both",
                "labels": ["_acquisition","_imageFiles"]
        }

        r = self.gbdx_connection.post(url, headers=headers, data=json.dumps(traverse_body))

        # Check for invalid record ID upon traverse:
        if r.status_code == 400:
            if 'rootRecordId does not exist' in r.json()['message']:
                return None

        r.raise_for_status()

        results = r.json()['results']

        if len(results) == 0:
            return None

        catalog_record = [r for r in results if r['identifier'] == catalog_id][0]

        if catalog_record['type'] == "LandsatAcquisition":
            ## get landsat data location
            browse_url = catalog_record['properties']['browseURL']

            # convert a URL that looks like this:
            # 'https://s3-us-west-2.amazonaws.com/landsat-pds/L8/174/053/LC81740532014364LGN00/LC81740532014364LGN00_thumb_large.jpg'
            # into this:
            # 's3://landsat-pds/L8/174/053/LC81740532014364LGN00'
            return 's3://' + '/'.join( browse_url.split('/')[3:8] )

        elif catalog_record['type'] == "DigitalGlobeAcquisition":
            ## Find any ObjectStoreData object, get its s3 bucket & prefix:
            object_store_records = [r for r in results if r['type'] == 'ObjectStoreData']

            # If the traverse didn't find any object store data, return None
            if not object_store_records:
                return None

            # Another hacky thing: let's only grab data in a particular bucket that we know contains good full strips:
            object_store_records = [r for r in object_store_records 
                                        if r['properties']['bucketName'] == 'receiving-dgcs-tdgplatform-com']

            # If we didn't find any records with the correct bucket, return None
            if not object_store_records:
                return None

            object_store_record = object_store_records[0]

            bucket = object_store_record['properties']['bucketName']
            prefix = object_store_record['properties']['objectIdentifier']

            # keep only the first two folders in the s3path:
            # Example:  'a/b/c/d/e'  -->  'a/b'
            prefix = '/'.join(prefix.split('/')[:2])

            return "s3://%s/%s" % (bucket, prefix)




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

        if startDate and endDate and not searchAreaWkt:
            if diff.days > 7:
                raise Exception("startDate and endDate must be at most a week apart if no search polygon is specified.")

        postdata = {  
            "searchAreaWkt": searchAreaWkt,
            "types": types, 
            "startDate": startDate,
            "endDate": endDate,
        }

        if filters:
            postdata['filters'] = filters

        if searchAreaWkt:
            # If we are searching over a polygon, break up the polygon into lots of small polygons of size 2-square degrees
            # and get the results.
            results = catalog_search_aoi.search_materials_in_multiple_small_searches(postdata, self.gbdx_connection)
        else:
            # If we are not searching over a polygon, just do the search directly.
            url = 'https://geobigdata.io/catalog/v1/search?includeRelationships=false'
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
        







