======================================
gbdxtools: Python tools for using GBDX
======================================

.. image:: https://anaconda.org/digitalglobe/gbdxtools/badges/version.svg   
    :target: https://anaconda.org/digitalglobe/gbdxtools

.. image:: https://badge.fury.io/py/gbdxtools.svg
    :target: https://badge.fury.io/py/gbdxtools
    
.. image:: https://travis-ci.org/DigitalGlobe/gbdxtools.svg?branch=master
    :target: https://travis-ci.org/DigitalGlobe/gbdxtools
    
.. image:: https://readthedocs.org/projects/gbdxtools/badge/?version=latest
    :target: http://gbdxtools.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status
    
.. image:: https://codecov.io/gh/DigitalGlobe/gbdxtools/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/DigitalGlobe/gbdxtools
    
.. image:: https://pyup.io/repos/github/DigitalGlobe/gbdxtools/shield.svg
     :target: https://pyup.io/repos/github/DigitalGlobe/gbdxtools/
     :alt: Updates
     
.. image:: https://pyup.io/repos/github/DigitalGlobe/gbdxtools/python-3-shield.svg
     :target: https://pyup.io/repos/github/DigitalGlobe/gbdxtools/
     :alt: Python 3



gbdxtools is a package for ordering imagery and launching workflows on DigitalGlobe's GBDX platform.

In order to use gbdxtools, you need GBDX credentials. Email GBDX-Support@digitalglobe.com to get these.

Documentation is hosted here: http://gbdxtools.readthedocs.org/en/latest/. 
Example scripts can be found under the /examples directory of this repo.

Currently, the following Python versions are supported: 2.7, 3.3, 3.4, 3.5

See the license file for license rights and limitations (MIT).

Updates
------------

There have been reports of authentication errors while creating a gbdx interface if the file ~/.gbdx-config is already populated with an access token. In this case, delete everything below and including the line [gbdx_token] within ~/.gbdx-config and create a new gbdx interface. 


Installation
------------

Conda is the recommended way to install gbdxtools::

    conda install -c conda-forge -c digitalglobe gbdxtools

Troubleshooting
~~~~~~~~~~~~~~~

These are various tips to follow if your installation fails.

**Dependencies**

As of gbdxtools version 0.11.3 libcurl and GDAL (>=2.1.0) are required. To install these packages use::

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

Versions of gbdxtools >= 0.11.3 require the GDAL library (>= 2.1.0) to be installed. 

**conda**

If your installation with pip keeps failing, try creating a conda environment and installing gbdxtools within this environment. 

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

Install gbdxtools::

   conda install -c digitalglobe  gbdxtools

**Python versions and conda-forge**

A known issue exists, in certain environments, where conda will downgrade python from 3.x to 2.7x when installing gbdxtools. If conda does not keep your python version intact when installing gbdxtools, you need to::

   conda install -y gbdxtools -c digitalglobe -c conda-forge


Development
-----------

Clone the repo::

   git clone https://github.com/digitalglobe/gbdxtools.git
   
   cd gbdxtools

Start a virtual environment::
   
   virtualenv venv
   
   . venv/bin/activate
 
Install the requirements::

   pip install -r requirements.txt


Please follow this python style guide: https://google.github.io/styleguide/pyguide.html.
80-90 columns is fine.

**Tests**

See the Readme in the tests directory.

Note: you may have to issue the following in your virtualenv for the tests to find gbdxtools properly::

    pip install -e .

**Create a new version**

To create a new version::

    bumpversion ( major | minor | patch )
    git push --tags

Don't forget to update the changelog and upload to pypi.

**Contributing**

Please contribute! Please make pull requests directly to master. Before making a pull request, please:

* Ensure that all new functionality is covered by unit tests.
* Verify that all unit tests are passing.
* Ensure that all functionality is properly documented.
* Ensure that all functions/classes have proper docstrings so sphinx can autogenerate documentation.
* Fix all versions in setup.py (and requirements.txt)
