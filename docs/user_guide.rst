Getting started
===============

Getting Access to GBDX
-----------------------

All operations on GBDX require credentials. You can sign up for a GBDX account at https://gbdx.geobigdata.io. Your GBDX credentials are found under your account profile.

GBDXtools expects a config file to exist at ~/.gbdx-config with your credentials. Instead of a file your credentials can also be stored as the environmental variables GBDX_USERNAME and GBDX_PASSWORD. For more information on the credential file and other ways to manage authorization, see https://github.com/tdg-platform/gbdx-auth#ini-file.

GBDXtools automatically handles authentication and authorization. It is not required to manually log in or start a session.


For questions or troubleshooting email GBDX-Support@digitalglobe.com.


Using Gbdxtools 
-----------------

Local Python Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

As an access library to GBDX APIs, GBDXtools can be run locally. See `Installation`_ below.


Jupyter Notebooks
^^^^^^^^^^^^^^^^^^^^^

GBDXtools has additional features for visualization and mapping in IPython and Jupyter Notebooks. This is the recommended development environment for analysis.


Installation
-----------------

Conda is the recommended way to install GBDXtools::

    conda install -c conda-forge -c digitalglobe gbdxtools

Pip can also be used::

    pip install gbdxtools


Upgrading
---------------

In the period between 0.16.7 and 0.17.0 releases there have been significant changes to GBDXtools, Proj, and Dask. We highly recommend installing GBDXtools 0.17.0 into a new environment. To upgrade an existing environment the best practice is to uninstall the core dependencies first. In Conda we suggest:

   conda remove -y dask dask-core pyproj proj4 pyveda rio-hist gbdxtools rasterio gdal


Troubleshooting
^^^^^^^^^^^^^^^^^

These are various tips to follow if your installation fails.

**Dependencies**

As of GBDXtools version 0.11.3 libcurl and GDAL (>=2.1.0) are required. If installing from source, install these packages using::

  # Ubuntu users:
  sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
  sudo apt update 
  sudo apt-get install gdal-bin python-gdal python3-gdal libcurl4-openssl-dev

  # Mac Users:
  xcode-select --install # to install libcurl
  brew install https://raw.githubusercontent.com/OSGeo/homebrew-osgeo4mac/master/Formula/gdal2.rb
  
Conda will usually manage the dependencies correctly.

**Windows Users**

Conda installation should work fine on Windows:

  conda install -c conda-forge -c digitalglobe gbdxtools

Pip may not get all dependencies correct but should work:

  pip install gbdxtools

Wheels for GBDXtools dependencies are collected here: https://github.com/DigitalGlobe/gbdxtools-windows-dependencies

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

   conda activate env

Upgrade pip (if required)::

   pip install pip --upgrade

Install `gbdxtools`::

   conda install -y gbdxtools -c digitalglobe -c conda-forge



