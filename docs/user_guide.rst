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

    pip install gbdxtools


Upgrading
---------------

In the period between 0.16.7 and 0.17.0 releases there have been significant changes to GBDXtools, Proj, GDAL, and Dask. We highly recommend installing GBDXtools 0.17.1 into a new, clean environment. To upgrade an existing environment the best practice is to uninstall the core dependencies first. We suggest unistalling the following: dask, dask-core, pyproj, proj4, rio-hist, rasterio, and gdal.

Troubleshooting
^^^^^^^^^^^^^^^^^

These are various tips to follow if your installation fails.

**Dependencies**


**Windows Users**

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
