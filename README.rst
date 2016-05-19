======================================
gbdxtools: Python tools for using GBDX
======================================

.. image:: https://badge.fury.io/py/gbdxtools.svg
    :target: https://badge.fury.io/py/gbdxtools
    
.. image:: https://travis-ci.org/DigitalGlobe/gbdxtools.svg?branch=master
    :target: https://travis-ci.org/DigitalGlobe/gbdxtools
    
.. image:: https://readthedocs.org/projects/gbdxtools/badge/?version=latest
    :target: http://gbdxtools.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

gbdxtools is a package for ordering imagery and launching workflows on DigitalGlobe's GBDX platform.

In order to use gbdxtools, you need GBDX credentials. Email GBDX-Support@digitalglobe.com to get these.

Documentation is hosted here: http://gbdxtools.readthedocs.org/en/latest/. 
Example scripts can be found under the /examples directory of this repo.

See the license file for license rights and limitations (MIT).


Installation
------------

To install the latest stable version on pypi::

    pip install gbdxtools

Optional: you can install the current version of the master branch with::

    pip install git+https://github.com/digitalglobe/gbdxtools

Keep in mind that the master branch is constantly under development. 

**Troubleshooting**

These are various tips to follow if your installation fails.

1) Make sure you have the latest pip version::

   pip install pip --upgrade

2) For Ubuntu users, if you run into trouble with the installation of cryptography, make sure that the following dependencies are installed::

   sudo apt-get install build-essential libssl-dev libffi-dev python-dev

3) Try creating a conda environment and installing gbdxtools within this environment. 

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

   pip install gbdxtools


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

This package uses pytest http://pytest.org/latest/contents.html.

pytest allows for tests to be written using various frameworks, so unittest.TestCase, pytest, and nose style tests will be detected and run.

To run all of the tests::

    py.test tests

If you want only the unit or integration tests do either of::

    py.test tests/integration
    py.test tests/unit

Note: you may have to issue the following in your virtualenv for the tests to find gbdxtools properly::

    pip install -e .

**Create a new version**

To create a new version::

    bumpversion ( major | minor | patch )
    git push --tags

Don't forget to upload to pypi.

**Contributing**

Please contribute! Please make pull requests directly to master. Before making a pull request, please:

* Ensure that all new functionality is covered by unit tests.
* Verify that all unit tests are passing.
* Ensure that all functionality is properly documented.
* Ensure that all functions/classes have proper docstrings so sphinx can autogenerate documentation.
* Fix all versions in setup.py (and requirements.txt)
