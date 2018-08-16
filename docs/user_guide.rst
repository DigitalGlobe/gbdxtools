Getting started
===============

Getting access to GBDX
-----------------------

All operations on GBDX require credentials. You can sign up for a GBDX account at https://gbdx.geobigdata.io.
Your GBDX credentials are found under your account profile.

gbdxtools expects a config file to exist at ~/.gbdx-config with your credentials.
(See formatting for this file here:  https://github.com/tdg-platform/gbdx-auth#ini-file.)

Instantiating an Interface object automatically logs you in:

.. code-block:: pycon

   >>> from gbdxtools import Interface
   >>> gbdx = Interface()

For questions or troubleshooting email GBDX-Support@digitalglobe.com.

Getting your S3 information
---------------------------

gbdxtools automatically handles your GBDX account S3 bucket and prefix for you. Note that this bucket will be shared by all users under the GBDX account.

Should you need to know your S3 information for troubleshooting, use the s3 member of the Interface:

.. code-block:: pycon

   >>> gbdx.s3.info
    
    {u'S3_access_key': u'blah',
    'S3_secret_key': u'blah',
    'S3_session_token': u'blah',
    'bucket': u'gbd-customer-data',
    'prefix': u'58600248-2927-4523-b44b-5fec3d278c09'}


To download a file from your S3 bucket, use the s3.download() method:

.. code-block:: pycon

  >>> item = 'testdata/test1.tif'
  >>> gbdx.s3.download(item)

The file path does not need the account bucket or prefix. 

You can see the contents of your bucket/prefix using this link: http://s3browser.geobigdata.io/login.html.


Ordering imagery
----------------

This guide uses v2 of the GBDX ordering API. Ordering API v1 was deprecated on 02/25/2016.

Use the ordering member of the Interface to order imagery and check the status of your order.

To order the image with DG factory catalog id 10400100143FC900:

.. code-block:: pycon

   >>> order_id = gbdx.ordering.order('10400100143FC900')
   >>> print(order_id)
   04aa8df5-8ac8-4b86-8b58-aa55d7353987

The order_id is unique to your image order and can be used to track the progress of your order.
The ordered image sits in a directory on S3. The output of the following describes where:

.. code-block:: pycon

   >>> gbdx.ordering.status(order_id)
   >>> [{u'acquisition_id': u'10400100143FC900',
         u'location': u's3://receiving-dgcs-tdgplatform-com/055093431010_01_003',
         u'state': u'delivered'}]
