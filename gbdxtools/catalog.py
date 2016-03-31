
'''
Authors: Kostas Stamatiou, Dan Getman, Nate Ricklin, Dahl Winters, Donnie Marino
Contact: kostas.stamatiou@digitalglobe.com


GBDX Catalog Interface
'''

class Catalog():

    def __init__(self, connection):
        ''' Construct the Catalog interface class
            Args:
                connection: a ref to the GBDX Connection

            Returns:
                an instance of the Catalog interface class
        '''
        self.gbdx_connection = connection


    def get_strip_footprint_wkt(self, catID):
        '''Retrieves the strip footprint WKT string given a cat ID.

        Args:
            catID (str): The source catalog ID from the platform catalog.

        Returns:
            footprint (str): A POLYGON of coordinates.
        '''

        print 'Retrieving strip footprint'
        url = ('https://geobigdata.io/catalog/v1/record/' 
               + catID + '?includeRelationships=false')

        r = self.gbdx_connection.get(url)
        if r.status_code == 200:
            footprint = r.json()['properties']['footprintWkt']
            return footprint
        elif r.status_code == 404:
            print 'Strip not found: %s' % catID
            r.raise_for_status()
        else:
            print 'There was a problem retrieving catid: %s' % catID
            r.raise_for_status()


