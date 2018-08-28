Getting started
===============

Getting Access to GBDX
-----------------------

All operations on GBDX require credentials. You can sign up for a GBDX account at https://gbdx.geobigdata.io. Your GBDX credentials are found under your account profile.

`Gbdxtools` expects a config file to exist at ~/.gbdx-config with your credentials. Instead of a file your credentials can also be stored as the environmental variables GBDX_USERNAME and GBDX_PASSWORD. For more information on the credential file and other ways to manage authorization, see https://github.com/tdg-platform/gbdx-auth#ini-file.

`Gbdxtools` automatically handles authentication and authorization. It is not required to manually log in or start a session.


For questions or troubleshooting email GBDX-Support@digitalglobe.com.


Using Gbdxtools 
-----------------

Local Python Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^

As an access library to GBDX APIs, `gbdxtools` can be run locally. See `Installation`_ below.


Jupyter Notebooks
^^^^^^^^^^^^^^^^^^^^^

`Gbdxtools` has additional features for visualization and mapping in IPython and Jupyter Notebooks. This is the recommended development environment for analysis.


GBDX Notebooks
^^^^^^^^^^^^^^^^^

DigitalGlobe also offers GBDX Notebooks, a hosted instance of Jupyter Notebooks that provides a ready-to-go development environment. The platform also features sharing of notebooks, map-based image searching, and other features. For more information, see https://notebooks.geobigdata.io/.

Installation
-----------------

Conda is the recommended way to install `gbdxtools`::

    conda install -c conda-forge -c digitalglobe gbdxtools

Pip can also be used::

    pip install gbdxtools

Troubleshooting
^^^^^^^^^^^^^^^^^

These are various tips to follow if your installation fails.

**Dependencies**

As of `gbdxtools` version 0.11.3 libcurl and GDAL (>=2.1.0) are required. To install these packages use::

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



