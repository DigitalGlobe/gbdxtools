API Reference
=======================

Catalog
-----------------------

.. autoclass:: gbdxtools.catalog.Catalog
   :members:

CatalogImage
-----------------------

CatalogImage is a wrapper class that returns the appropriate image class for the catalog ID. This description applies to all of the other RDA-based classes.

CatalogImages are also Dask arrays and support all of their properties and methods. The most commonly used ones are listed here. Some methods are overridden to preserve geospatial information but other work identically.

.. autoclass:: gbdxtools.images.catalog_image.CatalogImage
    :members:

    .. autocatmeta:: gbdxtools.images.meta.GeoDaskImage.aoi
    .. autocatmeta:: gbdxtools.images.meta.GeoDaskImage.geotiff
    .. autocatmeta:: gbdxtools.images.meta.DaskImage.iterwindows
    .. autocatmeta:: gbdxtools.images.meta.GeoDaskImage.map_blocks
    .. autocatmeta:: gbdxtools.images.mixins.geo.PlotMixin.ndvi
    .. autocatmeta:: gbdxtools.images.mixins.geo.PlotMixin.ndwi
    .. autocatmeta:: gbdxtools.images.mixins.geo.PlotMixin.plot
    .. autocatmeta:: gbdxtools.rda.util.preview
    .. autocatmeta:: gbdxtools.images.meta.GeoDaskImage.pxbounds
    .. autocatmeta:: gbdxtools.images.meta.DaskImage.randwindow
    .. autocatmeta:: gbdxtools.images.meta.DaskImage.read
    .. autocatmeta:: gbdxtools.images.mixins.geo.PlotMixin.rgb
    .. autocatmeta:: gbdxtools.images.meta.GeoDaskImage.warp
    .. autocatmeta:: gbdxtools.images.meta.DaskImage.window_at
    .. autocatmeta:: gbdxtools.images.meta.DaskImage.window_cover


Base Image classes
--------------------

IdahoImage
^^^^^^^^^^^^^^

.. autoclass:: gbdxtools.images.idaho_image.IdahoImage
    :undoc-members:


LandsatImage
^^^^^^^^^^^^^^^^

.. autoclass:: gbdxtools.images.landsat_image.LandsatImage
    :undoc-members:


TmsImage
^^^^^^^^^^

.. autoclass:: gbdxtools.images.tms_image.TmsImage
    :undoc-members:


DemImage
^^^^^^^^^^^^

.. autoclass:: gbdxtools.images.dem_image.DemImage
    :undoc-members:


S3Image
^^^^^^^^^^^^^

.. autoclass:: gbdxtools.images.s3Image.S3Image
    :undoc-members:

S3Image
^^^^^^^^^^^^^

.. autoclass:: gbdxtools.images.sentinel2.Sentinel2
    :undoc-members:


Idaho
-----------------------

.. autoclass:: gbdxtools.idaho.Idaho
   :members:

Ordering
-----------------------

.. autoclass:: gbdxtools.ordering.Ordering
   :members:

S3
-----------------------

.. autoclass:: gbdxtools.s3.S3
   :members:

Task
-----------------------

.. autoclass:: gbdxtools.simpleworkflows.Task
   :members:

Task Registry
-----------------------

.. autoclass:: gbdxtools.task_registry.TaskRegistry
   :members:

Vectors
-----------------------

.. autoclass:: gbdxtools.vectors.Vectors
   :members:

Workflows
-----------------------

.. autoclass:: gbdxtools.simpleworkflows.Workflow
   :members:



