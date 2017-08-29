# Order a list of cat ids, launch AOP workflow for each one and download locally.

import time

from gbdxtools import Interface

start_time = time.time()

catalog_ids = ['1030010034AFCE00',
               '103001003696B200',
               '105041001126A900',
               '1050410011360600',
               '1050410011360700']

print('Order imagery from GBDX')
gbdx = Interface()
order_id = gbdx.ordering.order(catalog_ids)

# check order status
while True:
    states, locations = zip(*[(order['state'], order['location'])
                              for order in gbdx.ordering.status(order_id)])
    if any(state != 'delivered' for state in states):
        time.sleep(300)
    else:
        break

print('Elapsed time: {} min'.format(round((time.time() - start_time) / 60)))

# where in bucket/prefix to store my AOP'ed imagery
s3_location = 'kostas/yunnanearthquake2014'

# launch AOP workflows
print('Launch AOP workflows')
workflow_ids = [gbdx.workflow.launch_aop_to_s3(location,
                                               s3_location,
                                               enable_acomp='true',
                                               enable_pansharpen='true') for location in locations]

# check workflow status
pending_workflow_ids = workflow_ids
while len(pending_workflow_ids) > 0:
    print('Pending workflows', pending_workflow_ids)
    for workflow_id in pending_workflow_ids:
        result = gbdx.workflow.status(workflow_id)
        if result['state'] == 'complete':
            pending_workflow_ids.remove(workflow_id)
    time.sleep(300)

print('Elapsed time: {} min'.format(round((time.time() - start_time) / 60)))

# download
gbdx.s3.download(s3_location)
