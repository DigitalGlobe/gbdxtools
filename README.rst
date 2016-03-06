======================================
gbdxtools: Python tools for using GBDX
======================================

.. image:: https://pypip.in/v/gbdxtools/badge.png
    :target: https://crate.io/packages/gbdxtools/
    :alt: Latest PyPI version

gbdxtools is a package for ordering imagery and launching workflows on DigitalGlobe's GBDX platform.

gbdxtools is MIT licenced.

Full documentation is hosted here: http://gbdxtools.readthedocs.org/en/latest/

Installation is easy::

    pip install gbdxtools

In order to use gbdxtools, you need GBDX credentials. Talk to Jordan Winkler (jordan.winkler@digitalglobe.com) 
to get those.

This repo is intended as a useful exercise in elegant open source Python development. 
A presentation which outlines the principles can be found here http://youngpm.github.io/python-brownbag/#1.
The long-term plan is to merge this repo with https://github.com/TDG-Platform/gbdx-py.

DevOps
------

Clone the repo::

   git clone git@github.com:kostasthebarbarian/mltools.git
   
   cd mltools

Start a virtual environment::
   
   virtualenv venv
   
   . venv/bin/activate
 
Install the requirements::

   pip install -r requirements.txt

