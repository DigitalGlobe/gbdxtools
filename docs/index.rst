
gbdxtools: Python tools for using GBDX
=======================================

`Gbdxtools` is a package to simplify interaction with DigitalGlobe's GBDX platform and integrate GBDX data into
Python's mature analysis ecosystem. 

GBDX Platform
----------------

`GBDX <https://gbdxdocs.digitalglobe.com/>`_ is DigitalGlobe's online platform to access imagery, search data, and run analysis. Its functionality can be broken into four areas:

* Raster Data Access

    *Access to 100+ PB of DigitalGlobe satellite imagery plus Landsat, Sentinel, and other sources.*

* Image Catalog

    *Search and filter image metadata to find imagery.*

* Vector Services

    *Search and store vector data. Includes image footprints, OpenStreetMap, NaturalEarth, and other datasets.*

* GBDX Workflows

    *Build analysis tools and run them at scale.*


Python Gbdxtools
--------------------

`Gbdxtools` extends the access to these services with additional functionality for analysis and visualization. It can be thought of as having three layers:

* A core API library to abstract GBDX services

* Image classes that wrap all of the API calls, manage the geospatial metadata, and return NumPy arrays. These classes are based on `Dask <http://dask.pydata.org/>`_ arrays which defer the server calls until the image data is needed. 

* Simple visualization and analysis methods such as one-line plotting (using Matplotlib).

CLI RdaTools
----------------

Some GBDX functionality is also available through the command line with https://github.com/DigitalGlobe/rdatools. The CLI tool is useful for building simple workflows with other command lines tools like gdal_translate or JQ. RdaTools is a statically linked Go executable and binaries should run on most systems.


`gbdxtools` is MIT licenced.

The recommended installation method is with Anaconda::

    conda install -c conda-forge -c digitalglobe gbdxtools

`Gbdxtools` can also be installed with pip::

    pip install gbdxtools

* `Gbdxtools` github repository: https://github.com/DigitalGlobe/gbdxtools
* For general information on the GBDX platform and API visit http://gbdxdocs.digitalglobe.com.
* For a varied collection of gbdxtools examples see http://github.com/platformstories/notebooks.

Contents
------------
.. toctree::
   :maxdepth: 2

   user_guide
   imagery_access
   catalog_search
   vector_service
   running_workflows
   api_reference
