# gbdxtools: Python tools for using GBDX

[![AnacondaCloud](https://anaconda.org/digitalglobe/gbdxtools/badges/version.svg)](https://anaconda.org/digitalglobe/gbdxtools)
[![pypi package](https://badge.fury.io/py/gbdxtools.svg)](https://badge.fury.io/py/gbdxtools)
[![build status](https://travis-ci.org/DigitalGlobe/gbdxtools.svg?branch=master)](https://travis-ci.org/DigitalGlobe/gbdxtools)
[![Documentation Status](https://readthedocs.org/projects/gbdxtools/badge/?version=latest)](http://gbdxtools.readthedocs.org/en/latest/?badge=latest)
[![codecov](https://codecov.io/gh/DigitalGlobe/gbdxtools/branch/master/graph/badge.svg)](https://codecov.io/gh/DigitalGlobe/gbdxtools)

**gbdxtools is a package for ordering imagery and launching workflows on DigitalGlobe's GBDX platform.**

Supported Python versions: `2.7`, `3.3`, `3.4`, `3.5`

**[Documentation](http://gbdxtools.readthedocs.org/en/latest/)**

**[Usage Examples](https://github.com/DigitalGlobe/gbdxtools/tree/master/examples)**

**[License (MIT)](https://github.com/DigitalGlobe/gbdxtools/blob/master/license.md)**


## Announcement

There have been reports of authentication errors while creating a gbdx interface if the file `~/.gbdx-config` is already populated with an access token. In this case, delete everything below and including the line `[gbdx_token]` within `~/.gbdx-config` and create a new gbdx interface. 


## Installing gbdxtools

1. Find your [GBDX API Credentials in your profile](https://gbdx.geobigdata.io/profile). If you don't have a GBDX account, you can [sign up for GBDX](https://gbdx.geobigdata.io).

1. Install the latest stable version from pypi:

        $ pip install gbdxtools

    Optional: you can install the current version of the master branch:

        $ pip install git+https://github.com/digitalglobe/gbdxtools

    Keep in mind that the master branch is constantly under development. 


### Troubleshooting Installation

These are various tips to follow if your installation fails.

* **Dependencies**

    As of gbdxtools version 0.11.3, libcurl and GDAL (>=2.1.0) are required. To install these packages:

        # Ubuntu
        $ sudo add-apt-repository -y ppa:ubuntugis/ubuntugis-unstable
        $ sudo apt update 
        $ sudo apt-get install gdal-bin python-gdal python3-gdal libcurl4-openssl-dev

        # macOS / OSX
        $ xcode-select --install # to install libcurl
        $ brew install https://raw.githubusercontent.com/OSGeo/homebrew-osgeo4mac/master/Formula/gdal-20.rb

* **Windows**

    On windows you can install shapely, gdal, rasterio, and pyproj from wheels. To install these dependencies download the binaries for your system (rasterio and GDAL) and run something like this from the downloads folder:

        $ pip install -U pip
        $ pip install GDAL-2.1.0-cp27-none-win32.whl
        $ pip install rasterio-1.0a3-cp27-none-win32.whl

* **pip**

    Make sure you have the latest pip version::

        $ pip install pip --upgrade

* **Ubuntu**

    If you run into trouble with the installation of `cryptography`, make sure that the following dependencies are installed:

        $ sudo apt-get install build-essential libssl-dev libffi-dev python-dev libcurl4-openssl-dev

* **macOS / OSX**

    If you run into trouble with the installation of cryptography and see a message that `<ffi.h>` could not be found, you can run:

        $ xcode-select --install

    Then run `pip install gbdxtools` again. [See Stackoverflow for discussion on what is going wrong and why this fixes it](http://stackoverflow.com/questions/27328049/missing-usr-include-after-yosemite-and-xcode-install).

* **virtualenv**

    If you are running in a virtualenv and run into issues you may need upgrade pip in the virtualenv:

        $ cd <your_project_folder>
        $ . venv/bin/activate
        $ pip install --upgrade pip
        $ pip install --upgrade gbdxtools
        
    You might also need to remove token from your `.gbdx-config` file
        
        $ nano -w ~.gbdx-config
        
    Then remove the `[gbdx_token]` section and `json=` part
    

* **GDAL**

    Versions of gbdxtools >= 0.11.3 require the GDAL library (>= 2.1.0) to be installed. 

* **conda**

    If your installation with pip keeps failing, try creating a conda environment and installing gbdxtools within this environment. 

    Install conda with the following commands (choose default options at prompt):

        # Ubuntu
        $ wget https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
        $ bash Miniconda2-latest-Linux-x86_64.sh
        
        # macOS / OSX
        $ wget https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh
        $ bash Miniconda2-latest-MacOSX-x86_64.sh

    Make sure that conda is in your path. Then create a conda environment:

        $ conda create -n env python ipython   
   
    Activate the environment:

        $ source activate env

    Upgrade pip (if required):

        $ pip install pip --upgrade

    Install gbdxtools:

        $ pip install gbdxtools


## Contributing to gbdxtools

Please contribute! Every contribution matters to us, including submitting an issue, investigating or fixing a bug, adding a new feature, improving the documentation, or helping to answer questions.

### Environment Setup

1. Clone the repo:

        $ git clone https://github.com/digitalglobe/gbdxtools.git
        $ cd gbdxtools

1. Start a virtual environment:
   
        $ virtualenv venv
        $ . venv/bin/activate
 
1. Install the requirements:

        $ pip install -r requirements.txt

### Python Style Guide

We follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).
80-90 columns is fine.

### Running Tests

This package uses [pytest](http://pytest.org/latest/contents.html).

pytest allows for tests to be written using various frameworks, so unittest.TestCase, pytest, and nose style tests will be detected and run.

To run all of the tests:

    $ py.test tests

If you want only the unit or integration tests do either of:

    $ py.test tests/integration
    $ py.test tests/unit

Note for **virtualenv** users: you may need to run the following command in your virtualenv for the tests to find gbdxtools properly:

    $ pip install -e .
    
### Submitting a Pull Request

Please make pull requests directly to master. Before making a pull request, please:

* [x] Ensure that all new functionality is covered by unit tests.
* [x] Verify that all unit tests are passing.
* [x] Ensure that all functionality is properly documented.
* [x] Ensure that all functions/classes have proper docstrings so sphinx can autogenerate documentation.
* [x] Fix all versions in setup.py (and requirements.txt)

### Publishing a new package version

1. Update `changelog.md` with release notes about the functionality that was **added**, **fixed**, **changed**, **deprecated**, or **removed**.

1. Tag a new version:

        $ bumpversion ( major | minor | patch )
        $ git push --tags

1. Upload to pypi.
