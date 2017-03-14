"""
GBDX Ordering Interface.

Contact: kostas.stamatiou@digitalglobe.com
"""
from builtins import zip
from builtins import object
import requests
import json

from gbdxtools.auth import Auth

class Ordering(object):

    def __init__(self, **kwargs):
        '''Instantiate the GBDX Ordering Interface

           Returns:
               An instance of the Ordering interface.
        '''
        interface = Auth(**kwargs)
        self.base_url = '%s/orders/v2' % interface.root_url
        self.gbdx_connection = interface.gbdx_connection
        self.logger = interface.logger
    

    def order(self, image_catalog_ids, batch_size=100):
        '''Orders images from GBDX.

           Args:
               image_catalog_ids (str or list): A single catalog id or a list of 
                                                catalog ids.
               batch_size (int): The image_catalog_ids will be split into 
                                 batches of batch_size. The ordering API max 
                                 batch size is 100, if batch_size is greater 
                                 than 100 it will be truncated.

           Returns:
               order_ids (str or list): If one batch, returns a string. If more
                                        than one batch, returns a list of order ids, 
                                        one for each batch.
        '''
        def _order_single_batch(url_, ids, results_list):
            r = self.gbdx_connection.post(url_, data=json.dumps(ids))
            r.raise_for_status()
            order_id = r.json().get("order_id")
            if order_id:
                results_list.append(order_id)

        self.logger.debug('Place order')
        url = '%s/order' % self.base_url

        batch_size = min(100, batch_size)
        
        if not isinstance(image_catalog_ids, list):
            image_catalog_ids = [image_catalog_ids]

        sanitized_ids = list(set((id for id in (_id.strip() for _id in image_catalog_ids) if id)))

        res = []
        # Use itertool batch recipe
        acq_ids_by_batch = zip(*([iter(sanitized_ids)] * batch_size))
        for ids_batch in acq_ids_by_batch:
            _order_single_batch(url, ids_batch, res)

        # Order reminder
        remain_count = len(sanitized_ids) % batch_size
        if remain_count > 0:
            _order_single_batch(url, sanitized_ids[-remain_count:], res)

        if len(res) == 1:
            return res[0]
        elif len(res)>1:
            return res

    def status(self, order_id):
        '''Checks imagery order status. There can be more than one image per
           order and this function returns the status of all images
           within the order.

           Args:
               order_id (str): The id of the order placed.

           Returns:
               List of dictionaries, one per image. Each dictionary consists
               of the keys 'acquisition_id', 'location' and 'state'.
        '''

        self.logger.debug('Get status of order ' + order_id)
        url = '%(base_url)s/order/%(order_id)s' % {
            'base_url': self.base_url, 'order_id': order_id
        }
        r = self.gbdx_connection.get(url)
        r.raise_for_status()
        return r.json().get("acquisitions", {})

    def heartbeat(self):
        '''
        Check the heartbeat of the ordering API

        Args: None

        Returns:  True or False
        '''
        url = '%s/heartbeat' % self.base_url
        # Auth is not required to hit the heartbeat
        r = requests.get(url) 

        try:
            return r.json() == "ok"
        except:
            return False


    def location(self, image_catalog_ids, batch_size=100):
        def _process_single_batch(url_, ids, results_dict):
            query_string = 'acquisitionIds=[' + ','.join(['"{}"'.format(id_) for id_ in ids]) + ']'
            r = self.gbdx_connection.get(url_, params=query_string)
            r.raise_for_status()
            results_dict['acquisitions'].extend(r.json()['acquisitions'])

        url = '%s/location' % self.base_url

        batch_size = min(100, batch_size)

        if not isinstance(image_catalog_ids, list):
            image_catalog_ids = [image_catalog_ids]

        sanitized_ids = list(set((stripped_id for stripped_id in (_id.strip() for _id in image_catalog_ids) if stripped_id)))

        res = {'acquisitions': []}
        # Use itertool batch recipe
        acq_ids_by_batch = zip(*([iter(sanitized_ids)] * batch_size))
        for ids_batch in acq_ids_by_batch:
            _process_single_batch(url, ids_batch, res)

        # Process reminder
        remain_count = len(sanitized_ids) % batch_size
        if remain_count > 0:
            _process_single_batch(url, sanitized_ids[-remain_count:], res)

        return res
