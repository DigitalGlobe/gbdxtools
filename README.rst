======================================
gbdxtools: Python tools for using GBDX
======================================

.. image:: https://badge.fury.io/py/gbdxtools.svg
    :target: https://badge.fury.io/py/gbdxtools

gbdxtools is a package for ordering imagery and launching workflows on DigitalGlobe's GBDX platform.

gbdxtools is MIT licenced.

Installation is easy::

    pip install gbdxtools

If you have a previous version of gbdxtools install then::

    pip install --upgrade gbdxtools

In order to use gbdxtools, you need GBDX credentials. Email geobigdata@digitalglobe.com to get these.

Documentation is hosted here: http://gbdxtools.readthedocs.org/en/latest/. 
Example scripts can be found under the /examples directory of this repo.


Development
-----------

Clone the repo dev branch::

   git clone -b dev git@github.com:kostasthebarbarian/gbdxtools.git
   
   cd gbdxtools

Start a virtual environment::
   
   virtualenv venv
   
   . venv/bin/activate
 
Install the requirements::

   pip install -r requirements.txt

Please follow this python style guide: https://google.github.io/styleguide/pyguide.html.
80-90 columns is fine. 
