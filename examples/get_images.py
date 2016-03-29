# Order a list of cat ids, launch AOP workflow for each one and download locally.

import json
import time

from gbdxtools import Interface

start_time = time.time()

catalog_ids = ['1030010045539700', '10200100414F0100', '10200100417A8C00']
no_images = len(catalog_ids)

print 'Order imagery from GBDX'
gi = Interface()
order_ids = [gi.order_imagery(catalog_id) for catalog_id in catalog_ids]

# check order status
pending_order_ids = order_ids
locations = []
while len(pending_order_ids)>0:
    print 'Pending orders', pending_order_ids
    for order_id in pending_order_ids:
        result = gi.check_order_status(order_id)
        print result
        location, status = result.keys()[0], result.values()[0]
        if status == 'delivered':
            pending_order_ids.remove(order_id)
            locations.append(location)
    time.sleep(300)   # check every five minutes

print 'Elapsed time: {} min'.format(round((time.time() - start_time)/60))

# where in bucket/prefix to store my AOP'ed imagery
s3_location = 'my_directory'

# launch AOP workflows
print 'Launch AOP workflows'
workflow_ids = [gi.launch_aop_to_s3_workflow(location,
                                             s3_location,
                                             enable_acomp='true') for location in locations]

# check workflow status
pending_workflow_ids = workflow_ids
while len(pending_workflow_ids) > 0:
    print 'Pending workflows', pending_workflow_ids
    for workflow_id in pending_workflow_ids:
        result = gi.check_workflow_status(workflow_id)
        if result['state'] == 'complete':
            pending_workflow_ids.remove(workflow_id)
    time.sleep(300)

print 'Elapsed time: {} min'.format(round((time.time() - start_time)/60))

# download
gi.download_from_s3(s3_location)
