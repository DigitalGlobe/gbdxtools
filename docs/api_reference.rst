API Reference
=======================

Catalog
-----------------------

.. autoclass:: gbdxtools.catalog.Catalog
   :members:

CatalogImage
-----------------------

.. autoclass:: gbdxtools.images.catalog_image.CatalogImage
   :members:

.. function:: aoi([bbox=None, wkt=None, geojson=None])
   
    Subsets the image with an Area of Interest

    :param bbox (list): a bounding box list (minx, miny, maxx, maxy)
    :param wkt (str): a well-known-text geometry
    :param geojson (dict): a geojson geometry
    :returns image: an image class clipped to the given AOI

.. function:: geotiff([path='output.tif', dtype=None, bands=None, proj=None, transform=None])

    Creates a geotiff from the image data

    :param path (str): a path to write the geotiff to
    :param dtype (str): a datatype to use for the geotiff ('float32', 'uint16', 'uint8', 'etc')
    :param bands (list): a list of bands to save to the geotiff
    :param proj (str): an EPSG proj string 
    :param transform (dict): an affine transformation to use for the new geotiff 

    :returns path (str): the path to the created geotiff file on disk

.. py:function:: plot([w=10, h=10, bands=None, cmap="Greys_r"])

    Plot the image via matplotlib. Defaults to plotting an RGB image unless the image only has one band.

    :param w: plot width
    :param h: plot height
    :param bands: A list of bands to plot
    :param cmap: the matplotlib colormap to use in single band plots

.. py:function:: rgb()

    Returns a uint8 Numpy array of the RGB bands for an image suitable for plotting with libraries like Matplotlib
    
    :returns array (ndarray): A Numpy array of the RGB data 

.. py:function:: ndvi()

    Returns a uint8 Numpy array of the NDVI data values from an image suitable for plotting with libraries like Matplotlib

    :returns array (ndarray): A Numpy array of the NDVI data


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



