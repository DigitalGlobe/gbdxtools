======================================
gbdxtools: Python tools for using GBDX
======================================

[![PyPI version](https://badge.fury.io/py/gbdxtools.svg)](https://badge.fury.io/py/gbdxtools)

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

Clone the repo:

.. highlights::

   git clone git@github.com:kostasthebarbarian/mltools.git
   
   cd mltools

Start a virtual environment::

.. highlights::
   
   virtualenv venv
   
   . venv/bin/activate
 
Install the requirements:

.. highlights::

   pip install -r requirements.txt

