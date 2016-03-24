User Guide
==========

Getting access to GBDX
-----------------------

All operations on GBDX require credentials. Instantiating an Interface object automatically logs you in:

.. code-block:: pycon

   >>> from gbdxtools import Interface
   >>> gi = Interface()

gbdxtools expects a config file to exist at ~/.gbdx-config with your GBDX credentials.  
See formatting for this file here:  https://github.com/tdg-platform/gbdx-auth#ini-file.
To get a GBDX username, password and API key, please email geobigdata@digitalglobe.com . 
For future reference, remember that your credentials are listed in https://gbdx.geobigdata.io/account/user/settings/.


Getting your S3 information
---------------------------

Simply call:

.. code-block:: pycon

   >>> gi.get_s3_info()
   >>> Obtained S3 credentials
   >>> {u'S3_access_key': u'blah',
 u'S3_secret_key': u'blah',
 u'S3_session_token': u'blah',
 u'bucket': u'gbd-customer-data',
 u'prefix': u'58600248-2927-4523-b44b-5fec3d278c09'}

You can see the contents of your bucket/prefix using this link: http://s3browser-env.elasticbeanstalk.com/login.html.


Ordering imagery
----------------

This guide uses v2 of the GBDX ordering API. Ordering API v1 was set to phase out on 02/25/2016. 
 
To order the image with DG factory catalog id 10400100143FC900:

.. code-block:: pycon

   >>> order_id = gi.order_imagery(['10400100143FC900'])
   >>> Place order
   >>> print order_id
   >>> 8bd8f797-11cd-4e3b-8bfa-c592d41af223

The order_id is unique to your image order and can be used to track the progress of your order.
The ordered image sits in a directory on S3. The output of the following describes where:

.. code-block:: pycon

   >>> gi.check_order_status(order_id)
   >>> Get status of order 8bd8f797-11cd-4e3b-8bfa-c592d41af223
   >>> {u's3://receiving-dgcs-tdgplatform-com/055093376010_01_003': u'delivered'}


Launching a workflow
--------------------

Welcome to the magical world of GBDX workflows. Workflows are sequences of tasks performed on a DG image.
You can define workflows consisting of custom tasks. A detailed description of workflows and tasks can be found `here`_.

This example will walk you through launching an aop_to_s3 workflow. 
This workflow applies a series of one or more processing steps to the image you ordered in the previous section and stores the
processed image in your S3 bucket. 

First, define the location of the ordered image:

.. code-block:: pycon

   >>> input_location = 's3://receiving-dgcs-tdgplatform-com/055093376010_01_003'

Now define the location where the output image will be stored. This HAS to be a directory under bucket/prefix.
If the directory does not exist, it will automatically be created.

.. code-block:: pycon

   >>> s3_info = gi.get_s3_info()
   >>> output_location = 's3://' + s3_info['bucket'] + '/' + s3_info['prefix'] + '/' + 'my_directory'

We launch an aop_to_s3 workflow that produces a pansharpened image.

.. code-block:: pycon

   >>> gi.launch_aop_to_s3_workflow(input_location, output_location, enable_pansharpen='true')
   >>> Launch workflow
   >>> u'4283225389760382164'

The output of this function is the workflow id. 
You can check on the status of this workflow as follows:

.. code-block:: pycon

   >>> gi.check_workflow_status('4283225389760382164')
   >>> Get status of workflow: 4283225389760382164
   >>> {u'event': u'scheduled', u'state': u'pending'}

.. _`here`: http://gbdxdocs.digitalglobe.com/docs/workflow-api-course

