
'''
Authors: Kostas Stamatiou, Dan Getman, Nate Ricklin, Dahl Winters, Donnie Marino
Contact: kostas.stamatiou@digitalglobe.com


GBDX Catalog Interface
'''

class Catalog():

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


