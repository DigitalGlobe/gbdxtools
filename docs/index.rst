.. gbdxtools documentation master file, created by
   sphinx-quickstart on Fri Feb 12 16:41:01 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

gbdxtools: Python tools for using GBDX
=======================================

gbdxtools is a package for ordering imagery and launching workflows on DigitalGlobe's GBDX platform.

gbdxtools is MIT licenced.

Installation is easy::

    pip install gbdxtools

Then::

    from gbdxtools import Interface

In order to use gbdxtools, you need GBDX credentials. Talk to Jordan Winkler (jordan.winkler@digitalglobe.com) 
to get those. 

For general information on the GBDX platform and API, see `here`_.

.. _`here`: http://gbdxdocs.digitalglobe.com/docs

.. toctree::
   :maxdepth: 2

   user_guide
   api_docs
