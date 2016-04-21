'''
Authors: Kostas Stamatiou, Donnie Marino

Contact: kostas.stamatiou@digitalglobe.com

Abstraction for the GBDX Ordering interface.
'''

import json

class Ordering:

    def __init__(self, interface):
        '''Instantiate the GBDX Ordering Interface

        Args: 
            interface (Interface): A reference to the GBDX interface.
    
        Returns:
            An instance of the Ordering interface.

        '''
        self.gbdx_connection = interface.gbdx_connection
        self.logger = interface.logger
    
    def order(self, image_catalog_ids):
        '''Orders images from GBDX.

        Args:
            image_catalog_ids (list or string): A list of image catalog ids
            or a single image catalog id.

        Returns:
            order_id (str): The ID of the order placed.
        '''

        # hit ordering api
        self.logger.debug('Place order')
        url = 'https://geobigdata.io/orders/v2/order/'

        # determine if the user inputted a list of image_catalog_ids
        # or a string of one
        if type(image_catalog_ids).__name__ == 'list':
            r = self.gbdx_connection.post(url,
                                          data=json.dumps(image_catalog_ids))
        else:
            r = self.gbdx_connection.post(url,
                                          data=json.dumps([image_catalog_ids]))
        r.raise_for_status()
        order_id = r.json().get("order_id", {})

        return order_id

    def status(self, order_id):
        '''Checks imagery order status. There can be more than one image per
           order and this function returns the status of all images
           within the order.

           Args:
               order_id (str): The ID of the order placed.

           Returns:
               List of dictionaries, one per image. Each dictionary consists 
               of the keys 'acquisition_id', 'location' and 'state'.
        '''

        self.logger.debug('Get status of order ' + order_id)
        url = 'https://geobigdata.io/orders/v2/order/'
        r = self.gbdx_connection.get(url + order_id)
        r.raise_for_status()
        return r.json().get("acquisitions", {})
        
