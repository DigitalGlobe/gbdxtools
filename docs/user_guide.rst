Getting started
===============

Getting access to GBDX
-----------------------

All operations on GBDX require credentials. 
gbdxtools expects a config file to exist at ~/.gbdx-config with your GBDX credentials.  
(See formatting for this file here:  https://github.com/tdg-platform/gbdx-auth#ini-file.)

Instantiating an Interface object automatically logs you in:

.. code-block:: pycon

   >>> from gbdxtools import Interface
   >>> gbdx = Interface()

To get a GBDX username, password and API key, please email GBDX-Support@digitalglobe.com. 
For future reference, remember that your credentials are listed in https://gbdx.geobigdata.io/profile.


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

This guide uses v2 of the GBDX ordering API. Ordering API v1 was deprecated on 02/25/2016. 

Use the ordering member of the Interface to order imagery and check the status of your order.

To order the image with DG factory catalog id 10400100143FC900:

.. code-block:: pycon

   >>> order_id = gbdx.ordering.order('10400100143FC900')
   >>> print order_id
   04aa8df5-8ac8-4b86-8b58-aa55d7353987

The order_id is unique to your image order and can be used to track the progress of your order.
The ordered image sits in a directory on S3. The output of the following describes where:

.. code-block:: pycon

   >>> gbdx.ordering.status(order_id)
   >>> [{u'acquisition_id': u'10400100143FC900',
         u'location': u's3://receiving-dgcs-tdgplatform-com/055093431010_01_003',
         u'state': u'delivered'}]
