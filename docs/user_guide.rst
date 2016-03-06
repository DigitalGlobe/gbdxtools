User Guide
==========

Getting access to GBDX
-----------------------

All operations on GBDX require credentials. Instantiating an Interface object automatically logs you in:

.. code-block:: pycon

   >>> from gbdxtools import Interface
   >>> gi = Interface()

gbdxtools expects a config file to exist at ~/.gbdx-config with your GBDX credentials.  See formatting for this
file here:  https://github.com/tdg-platform/gbdx-auth#ini-file
To get a GBDX username, password and API key talk to Jordan Winkler (jordan.winkler@digitalglobe.com). 
For future reference, remember that your API key is listed in https://gbdx.geobigdata.io/account/user/settings/.

You can hit the GBDX API to order imagery, launch and check the status of workflows, etc.


Getting your S3 bucket and prefix information
---------------------------------------------

Simply call:

.. code-block:: pycon

   >>> gi.get_s3_info()
   >>> Get S3 bucket info
   >>> (u'gbd-customer-data', u'58600248-2927-4523-b44b-5fec3d278c09')

You can see the contents of your bucket/prefix using this link: http://s3browser-env.elasticbeanstalk.com/login.html.


Ordering imagery
----------------

This guide uses v2 of the GBDX ordering API. Ordering API v1 was set to phase out on 02/25/2016. 
 
To order the image with DG factory catalog id 10400100143FC900:

.. code-block:: pycon

   >>> order_id = gi.order_imagery_v2(['10400100143FC900'])
   >>> Place order...
   >>> Order 6dc78d08-9b25-4901-bab0-72f61857a631 placed

The order_id is unique to your image order and can be used to track the progress of your order.
The ordered image sits in a directory on S3. The output of the following describes where:

.. code-block:: pycon

   >>> gi.check_order_status_v2(order_id)
   >>> Get status of order 6dc78d08-9b25-4901-bab0-72f61857a631
   >>> {u's3://receiving-dgcs-tdgplatform-com/055085517010_01_003': u'delivered'}

Before ordering an image, you can check if the image is already on GBDX:

.. code-block:: pycon
   
   >>> gi.has_this_been_ordered('10400100143FC900')
   >>> Check if 10400100143FC900 has been ordered
   >>> 'True'


Launching a workflow
--------------------

Welcome to the magical world of GBDX workflows. Workflows are sequences of tasks performed on an image.
You can define workflows consisting of custom tasks. A detailed description of workflows and tasks can be found `here`_.

This example will walk you through launching an aop_to_s3 workflow. 
This workflow applies a series of one or more processing steps to the image you ordered in the previous section and stores the
processed image in your S3 bucket. 

More detailed explanations will be added here in the future. For the time being, here is the series of steps.

.. code-block:: pycon

   >>> input_location = gi.get_location_of_ordered_imagery(sales_order_number)
   >>> # set your prefered output location; you need to know your S3 bucket and prefix for this
   >>> output_location = 'https://gbd-customer-data/58600248-2927-4523-b44b-5fec3d278c09/kostas/adelaide_pools_2016'
   >>> # run an aop_to_s3 workflow that produces an orthorectified and pansharpened image
   >>> gi.launch_aop_to_s3_workflow(input_location, output_location, enable_pansharpen='true')
   >>> Workflow 4270202770861644904 placed
   >>> u'4270202770861644904'

Your input location is where your ordered imagery sits on s3. Your output location has to be within your assigned s3-bucket/s3-prefix, which is 'gbd-customer-data/58600248-2927-4523-b44b-5fec3d278c09/' in this example. If the directory does not exist, it will automatically be created.

You can check on the status of your workflow as follows:

.. code-block:: pycon

   >>> gi.check_workflow_status('4270202770861644904')
   >>> Get status of workflow: 4270202770861644904
   >>> {u'event': u'scheduled', u'state': u'pending'}

.. _`here`: http://gbdxdocs.digitalglobe.com/docs/workflow-api-course



