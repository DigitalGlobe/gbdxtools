User Guide
==========

Getting access to GBDX
-----------------------

All operations on GBDX require credentials. Instantiating an Interface object automatically logs you in:

.. code-block:: pycon

   >>> from gbdxtools import Interface
   >>> gbdx = Interface()

gbdxtools expects a config file to exist at ~/.gbdx-config with your GBDX credentials.  
See formatting for this file here:  https://github.com/tdg-platform/gbdx-auth#ini-file.
To get a GBDX username, password and API key, please email geobigdata@digitalglobe.com. 
For future reference, remember that your credentials are listed in https://gbdx.geobigdata.io/account/user/settings/.


Getting your S3 information
---------------------------

Use the s3 member of the Interface:

.. code-block:: pycon

   >>> gbdx.s3.info
   >>> {u'S3_access_key': u'blah',
 u'S3_secret_key': u'blah',
 u'S3_session_token': u'blah',
 u'bucket': u'gbd-customer-data',
 u'prefix': u'58600248-2927-4523-b44b-5fec3d278c09'}
   >>> item = 'testdata/test1.tif'
   >>> gbdx.s3.download(item)

You can see the contents of your bucket/prefix using this link: http://s3browser-env.elasticbeanstalk.com/login.html.


Ordering imagery
----------------

This guide uses v2 of the GBDX ordering API. Ordering API v1 was set to phase out on 02/25/2016. 

Use the ordering member of the Interface to order and status imagery

To order the image with DG factory catalog id 10400100143FC900:

.. code-block:: pycon

   >>> order_id = gbdx.ordering.order('10400100143FC900')
   >>> print order_id
   u'8bd8f797-11cd-4e3b-8bfa-c592d41af223'

The order_id is unique to your image order and can be used to track the progress of your order.
The ordered image sits in a directory on S3. The output of the following describes where:

.. code-block:: pycon

   >>> gbdx.ordering.status(order_id)
   >>> [{u'acquisition_id': u'10400100120FEA00', u'state': u'delivered', u'location': u's3://bucketname/prefixname'}]


GBDX Workflows
--------------------

Welcome to the magical world of GBDX workflows. Workflows are sequences of tasks performed on a DG image.
You can define workflows consisting of custom tasks. A detailed description of workflows and tasks can be found `here`_.

This example will walk you through launching an aop_to_s3 workflow. 
This workflow applies a series of one or more processing steps to the image you ordered in the previous section and stores the
processed image under your S3 bucket/prefix. 

Use the workflow member of the Interface to interact with the workflow engine and manage workflows.

.. code-block:: pycon

   >>> gbdx = Interface()
   >>> gbdx.workflow.list_tasks()
   {u'tasks': [u'HelloGBDX', u'Downsample', u'protogenRAW', u'protogenUBFP', u'AComp' ...
   >>> gbdx.workflow.describe_task('HelloGBDX')
   {u'containerDescriptors': [{u'type': u'DOCKER', u'command': u'', u'properties': {u'image': u'tdgp/hello_gbdx:latest'}}], u'description': u'Get a personalized greeting to GBDX', u'inputPortDescriptors': [{u'required': True, u'type': u'string', u'description': u'Enter your name here for a personalized greeting to the platform.', u'name': u'your_name'}], u'outputPortDescriptors': [{u'required': True, u'type': u'txt', u'description': u'The output directory of text file', u'name': u'data'}], u'properties': {u'isPublic': True, u'timeout': 7200}, u'name': u'HelloGBDX'}  
 
First, define the location of the ordered image. This is the location you obtained when your order was delivered 
('s3://receiving-dgcs-tdgplatform-com/055093376010_01_003' in the example of the previous section.)

.. code-block:: pycon

   >>> input_location = 's3://receiving-dgcs-tdgplatform-com/055093376010_01_003'

Now define the location under bucket/prefix where the output image will be stored. 
If the directory does not exist, it will automatically be created.

.. code-block:: pycon

   >>> output_location = 'my_directory'

This means that the output image will be stored in s3://bucket/prefix/my_directory.
We now launch an aop_to_s3 workflow that produces a pansharpened image.

.. code-block:: pycon

   >>> workflow_id = gbdx.workflow.launch_aop_to_s3(input_location, output_location, enable_pansharpen='true')
   >>> print workflow_id
   u'4302104652966891585'

The output of this function is the workflow id. 
You can check on the status of this workflow as follows:

.. code-block:: pycon

   >>> gbdx.workflow.status(workflow_id)
   >>> {u'event': u'scheduled', u'state': u'pending'}

.. _`here`: http://gbdxdocs.digitalglobe.com/docs/workflow-api-course

