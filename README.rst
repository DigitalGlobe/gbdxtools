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

gbdxtools is MIT licenced.

Installation is easy::

    pip install gbdxtools

If you have a previous version of gbdxtools installed, then::

    pip install --upgrade gbdxtools

In order to use gbdxtools, you need GBDX credentials. Email geobigdata@digitalglobe.com to get these.

Documentation is hosted here: http://gbdxtools.readthedocs.org/en/latest/. 
Example scripts can be found under the /examples directory of this repo.


Command Line Interface
----------------------

The gbdxtools package includes a Command Line Interface for ease of use.

See the Documentation hosted here: https://github.com/DigitalGlobe/gbdxtools/blob/cli-dev/cli/README.rst


Development
-----------

Clone the repo dev branch::

   git clone -b dev https://github.com/digitalglobe/gbdxtools
   
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

To create a new version::

    bumpversion ( major | minor | patch )
    git push --tags

Don't forget to upload to pypi.

**Contributing**

Please contribute!  Please make pull requests directly to master.  Before making a pull request, please:

* Ensure that all new functionality is covered by unit tests.
* Verify that all unit tests are passing.
* Ensure that all functionality is properly documented.
* Ensure that all functions/classes have proper docstrings so sphinx can autogenerate documentation.
* Fix all versions in setup.py (and requirements.txt)
