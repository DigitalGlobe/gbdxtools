User Guide
==========

Getting an access token
-----------------------

All operations on GBDX require an access token. This is obtained as follows:

.. code-block:: pycon

   >>> from gbdx_tools import gbdx_interface as gi
   >>> access_token = gi.get_access_token(username, password, api_key)

To get a GBDX username, password and API key talk to Jordan Winkler (jordan.winkler@digitalglobe.com). 
For future reference, remember that your API key is listed in https://gbdx.geobigdata.io/account/user/settings/.

Once the access token is obtained, you can hit the GBDX API to order imagery, launch and check the status of workflows, etc.


Getting your S3 bucket and prefix information
---------------------------------------------

Simply call:

.. code-block:: pycon

   >>> gi.get_s3_info(access_token)
   >>> Get S3 bucket info
   >>> (u'gbd-customer-data', u'58600248-2927-4523-b44b-5fec3d278c09')

You can see the contents of your bucket/prefix using this link: http://s3browser-env.elasticbeanstalk.com/login.html.


Ordering imagery
----------------

(Note: this guide uses v1 of the GBDX ordering API. Ordering API v2 is scheduled to deploy 02/25/2016. 
Changes will need to be made to this section to accommodate Ordering API v2.)
 
To order the image with DG factory catalog id 10400100143FC900:

.. code-block:: pycon

   >>> sales_order_number = gi.order_imagery(['10400100143FC900'], access_token)
   >>> Place order...
   >>> Order 055045505 placed
   >>> print sales_order_number	
   >>> 055045505

The sales order number is unique to your image order and can be used to track the progress of your order

.. code-block:: pycon

   >>> gi.check_order_status(sales_order_number, access_token)
   >>> Get status of order 055045505
   >>> Order 055045505: done
   >>> 'done'

Before ordering an image, you can check if the image is already on GBDX:

.. code-block:: pycon
   
   >>> gi.has_this_been_ordered('10400100143FC900', access_token)
   >>> Check if 10400100143FC900 has been ordered
   >>> 'True'

The ordered image sits in a directory on S3. Here is how you can find where:

.. code-block:: pycon
   
   >>> gi.get_location_of_ordered_imagery(sales_order_number, access_token)
   >>> u'https://receiving-dgcs-tdgplatform-com/055045505010_01_003'


Launching a workflow
--------------------

Welcome to the magical world of GBDX workflows. Workflows are sequences of tasks performed on an image.
You can define workflows consisting of custom tasks. A detailed description of workflows and tasks can be found `here`_.

This example will walk you through launching an aop_to_s3 workflow. 
This workflow applies a series of one or more processing steps to the image you ordered in the previous section and stores the
processed image in your S3 bucket. 

More detailed explanations will be added here in the future. For the time being, here is the series of steps.

.. code-block:: pycon

   >>> input_location = gi.get_location_of_ordered_imagery(sales_order_number, access_token)
   >>> # set your prefered output location; you need to know your S3 bucket and prefix for this
   >>> output_location = 'https://gbd-customer-data/58600248-2927-4523-b44b-5fec3d278c09/kostas/adelaide_pools_2016'
   >>> # run an aop_to_s3 workflow that produces an orthorectified and pansharpened image
   >>> gi.launch_aop_to_s3_workflow(input_location, output_location, access_token, enable_pansharpen='true')
   >>> Workflow 4270202770861644904 placed
   >>> u'4270202770861644904'

Your input location is where your ordered imagery sits on s3. Your output location has to be within your assigned s3-bucket/s3-prefix, which is 'gbd-customer-data/58600248-2927-4523-b44b-5fec3d278c09/' in this example. If the directory does not exist, it will automatically be created.

You can check on the status of your workflow as follows:

.. code-block:: pycon

   >>> gi.check_workflow_status('4270202770861644904', access_token)
   >>> Get status of workflow: 4270202770861644904
   >>> {u'event': u'scheduled', u'state': u'pending'}

.. _`here`: http://gbdxdocs.digitalglobe.com/docs/workflow-api-course



