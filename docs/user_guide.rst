Getting started
===============

For this tutorial, we'll use the laterst version of gbdxtools, a python module for GBDX. We'll go over how to set up gbdxtools in your local environment for windows with optional ways to install using different operating systems.  Then we'll explain how to setup your local gbdxtools environment to to access GBDX. 

Get your account credentials
-----------------------

Before we start, you'll need your GBDX username and password.  All operations on GBDX require credentials. You can sign up for a GBDX account at https://www.geobigdata.io/contact-us/. ::

  username = 'youremailagress@mail.com'  
  password = 'ThePasswordYouSetWhenYouActivatedYourAccount.'
  

Insalling gbdxtools
--------------------

For questions or troubleshooting email GBDX-Support@digitalglobe.com.


Installation
-----------------

Conda is the recommended way to install GBDXtools.  From the anaconda comand prompt::

    conda create -n envname python=3.5 rasterio gdal
    conda activate envname
    conda install -c conda-forge -c digitalglobe gbdxtools

Pip can also be used::

    pip install gbdxtools

Troubleshooting
^^^^^^^^^^^^^^^^^

These are various tips to follow if your installation fails.

**Dependencies**

As of GBDXtools version 0.11.3 libcurl and GDAL (>=2.1.0) are required. To install these packages use::

  # Ubuntu users:
  sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
  sudo apt update 
  sudo apt-get install gdal-bin python-gdal python3-gdal libcurl4-openssl-dev

  # Mac Users:
  xcode-select --install # to install libcurl
  brew install https://raw.githubusercontent.com/OSGeo/homebrew-osgeo4mac/master/Formula/gdal2.rb

**Windows Users**

Conda installation should work fine on windows for python version 2.7.  If you are using python 3, you can install with pip, first install some dependencies with conda::

  conda install -c conda-forge scipy
  conda install -c conda-forge scikit-image
  pip install gbdxtools

**pip**

Make sure you have the latest pip version::

   pip install pip --upgrade

**Ubuntu users**

If you run into trouble with the installation of `cryptography`, make sure that the following dependencies are installed::

   sudo apt-get install build-essential libssl-dev libffi-dev python-dev libcurl4-openssl-dev

**Mac OSX Users**

If you run into trouble with the installation of cryptography and see a message that <ffi.h> could not be found, you can run::

	xcode-select --install

Then run "pip install gbdxtools" again. See stackoverflow for discussion on what is going wrong and why this fixes it (http://stackoverflow.com/questions/27328049/missing-usr-include-after-yosemite-and-xcode-install)

If you are running in a virtualenv and run into issues you may need upgrade pip in the virtualenv::

	cd <your_project_folder>
	. venv/bin/activate
	pip install --upgrade pip
	pip install --upgrade gbdxtools
	# you might also need to remove token from your .gbdx-config file
	nano -w ~.gbdx-config
	# then, remove the [gbdx_token] section and json= part

Users installing GBDXtools using ``pip`` on OS X Mojave have encountered::

   __main__.ConfigurationError: Curl is configured to use SSL, but we have not been able to determine which SSL backend it is using. Please see PycURL documentation for how to specify the SSL backend manually.

This solution was reported to work::

   brew install openssl
   PYCURL_SSL_LIBRARY=openssl LDFLAGS="-L/usr/local/opt/openssl/lib" CPPFLAGS="-I/usr/local/opt/openssl/include" pip install --no-cache-dir pycurl
   pip install gbdxtools 

You can run also run a shorter version::

   brew install openssl
   make osx

This assumes you are installing in a fresh environment. If ``pycurl`` or ``gbdxtools`` are already installed they should be uninstalled first.

Other errors related to ``pycurl`` and system libraries may indicate that you have previously used Conda to install ``pycurl``. If you are a Conda user you should use ``conda install gbdxtools`` instead of pip. 
    

**GDAL**

Versions of `gbdxtools` >= 0.11.3 require the GDAL library (>= 2.1.0) to be installed. 

**conda**

If your installation with pip keeps failing, try creating a conda environment and installing `gbdxtools` within this environment. 

For Ubuntu, install conda with the following commands (choose default options at prompt)::

   wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
   bash Miniconda2-latest-Linux-x86_64.sh

For OS X, install conda with the following commands (choose default options at prompt)::

   wget https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh
   bash Miniconda2-latest-MacOSX-x86_64.sh

Make sure that conda is in your path. Then create a conda environment::

   conda create -n env python ipython   
   
Activate the environment::

   source activate env

Upgrade pip (if required)::

   pip install pip --upgrade

Install `gbdxtools`::

   conda install -c digitalglobe  gbdxtools

**Python versions and conda-forge**

A known issue exists, in certain environments, where conda will downgrade python from 3.x to 2.7x when installing `gbdxtools`. If conda does not keep your python version intact when installing `gbdxtools`, you need to::

   conda install -y gbdxtools -c digitalglobe -c conda-forge

Getting Authorized
----------------------

GBDXtools expects a config file to exist at ~/.gbdx-config with your credentials. Instead of a file your credentials can also be stored as the environmental variables GBDX_USERNAME and GBDX_PASSWORD. For more information on the credential file and other ways to manage authorization, see https://github.com/tdg-platform/gbdx-auth#ini-file.  ::

  from gbdxtools import Interface
  gbdx = Interface()

GBDXtools automatically handles authentication and authorization if you have the config file set. If you don't have the config file set you can pass auth directly to the Interface class::

  from gbdxtools import Interface
  gbdx = Interface(username='your.email@mail.com', password='yourpassword')


Search the GBDX catalog
-------------------------

You can search the GBDX catalog by spatial area, by date range, or by both. Use "types" to search by a single type or multiple types. Use filters to refine your data set.

Let's search for acquisitions in a subsection of San Francisco, collected between March 1, 2015 and March 1, 2016, with cloud cover of less than 10%, and an off-nadir angle of less than 20.::

  searchAreaWkt = "POLYGON ((-105.35202026367188 39.48113956424843, -105.35202026367188 40.044848254075546, -104.65988159179688 40.044848254075546, -104.65988159179688 39.48113956424843, -105.35202026367188 39.48113956424843))",
  startDate = "2017-01-01T00:00:00.000Z",
  endDate = "2018-09-01T23:59:59.999Z",
  types = ["DigitalGlobeAcquisition"],
  filters = ["sensorPlatformName = WORLDVIEW03_VNIR AND cloudCover < 20 AND offNadirAngle < 10"]
  results = gbdx.catalog.search(searchAreaWkt=searchAreaWkt,
                          startDate=startDate,
                          endDate=endDate,
                          types=types
			  filters=filters)
			  
Running a search returns a list of metadata items as dictionaries.


Place an order and check its status
--------------------------------------------------

The ordering function lets you order imagery and check your order's status. To place an order, you'll need a list of one or more acquisition catalog IDs. You can get the catalog IDs from the search example above::

  catalogids =    [
    "103001005275AC00",
    "103001004046DC00",
    "10504100106AA800",
    "1020010030936B00",
    "104001000680BA00",
    "102001003648FC00",
    "1010010012956800"
   ]
   order_id = gbdx.ordering.order(catalogids)
   print(order_id)

This request will return an order ID, and order information about each catalog ID. Save the order_id. You'll use it to check the status of your order.::

   gbdx.ordering.status(order_id)
   
This request will return an order ID, and order information about each catalog ID. Save the order_id. You'll use it to check the status of your order.

Submit a task and run a workflow
--------------------------------------------------

A workflow chains together a series of tasks and runs them in the specified order. Running a workflow means creating a series of Task objects with their inputs and outputs and passing them to the Workflow fuction as a list.

Note: All tasks require inputs.
  When a task requires a GBDX S3 location as an input, find the location in the Order response. Location will only be displayed when the state = delivered.
  
For this tutorial, we'll create and run a workflow with one simple task (Getting_Started)::

  Getting_Started: a simple task that only requires "your_name" as an input, and outputs a .txt file.
  
Create and run a workflow
^^^^^^^^^^^^^^^^^

Define and run your workflow::

  data = "s3://receiving-dgcs-tdgplatform-com/054813633050_01_003" # An example of a delivered order
  Getting_Started = gbdx.Task("Getting_Started", your_name="Your Name")
  workflow = gbdx.Workflow([ Getting_Started ])
  workflow.savedata(aoptask.outputs.data, location='getting_started_output')
  workflow.execute()

This workflow example shows the input and output values of the Getting_Started task.

How to find your account ID/prefix
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The GBDX S3 location is the GBDX S3 bucket name and the Prefix name. GBDX uses your account ID as the prefix and "gbd=customer-data" as the bucket.::

 gbdx.s3.info
 {u'S3_access_key': u'blah',
 'S3_secret_key': u'blah',
 'S3_session_token': u'blah',
 'bucket': u'gbd-customer-data',
 'prefix': u'58600248-2927-4523-b44b-5fec3d278c09'}
 
Access the output data from a workflow
-----------------------------------------

To access the information in your customer S3 bucket do::

  gbdx.s3.download(location='getting_started_output/Hello_World.txt', local_dir='C:/output/location')
  
Inside this folder, you'll find a txt file called Hello_World.txt. Open the file to see this successful result!
