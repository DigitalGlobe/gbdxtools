======================================
gbdxtools: Python tools for using GBDX
======================================

.. image:: https://badge.fury.io/py/gbdxtools.svg
    :target: https://badge.fury.io/py/gbdxtools

gbdxtools is a package for ordering imagery and launching workflows on DigitalGlobe's GBDX platform.

gbdxtools is MIT licenced.

Full documentation is hosted here: http://gbdxtools.readthedocs.org/en/latest/

Installation is easy::

    pip install gbdxtools

If you have a previous version of gbdxtools install then::

    pip install --upgrade gbdxtools

In order to use gbdxtools, you need GBDX credentials. Email geobigdata@digitalglobe.com to get these.

This repo is intended as a useful exercise in elegant open source Python development. 
A presentation which outlines the principles can be found here http://youngpm.github.io/python-brownbag/#1.
The long-term plan is to merge this repo with https://github.com/TDG-Platform/gbdx-py.


Development
-----------

Clone the repo::

   git clone git@github.com:kostasthebarbarian/gbdxtools.git
   
   cd gbdxtools

Start a virtual environment::
   
   virtualenv venv
   
   . venv/bin/activate
 
Install the requirements::

   pip install -r requirements.txt

Please follow this python style guide: https://google.github.io/styleguide/pyguide.html.
80-90 columns is fine. 
