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

.. function:: geotiff([path='output.tif', dtype=None, bands=None, proj=None, transform=None, spec=None])

    Creates a geotiff from the image data. To get an 8 bit color balanced image, pass spec='rgb'

    :param path (str): a path to write the geotiff to
    :param dtype (str): a datatype to use for the geotiff ('float32', 'uint16', 'uint8', 'etc')
    :param bands (list): a list of bands to save to the geotiff
    :param proj (str): an EPSG proj string 
    :param transform (dict): an affine transformation to use for the new geotiff
    :param spec (str): spec to use for export - 'rgb' will export rgb bands as uint8 

    :returns path (str): the path to the created geotiff file on disk

.. py:function:: plot([w=10, h=10, bands=None, cmap="Greys_r"], histogram=None, stretch=[2,98], gamma=1.0, blm_source=None)

    Plot the image via matplotlib. Defaults to plotting an RGB image unless the image only has one band.
    Plot width and height refer to the total area of the plot, including margins. Dimensions are 
    specified in inches. The plot will be generated at 72 pixels per inch. In Jupyter extra whitespace
    will be removed so the final plot size will be smaller than the expected dimensions.

    :param w: plot width 
    :param h: plot height
    :param bands (list): A list of bands to plot
    :param cmap (str or cmap): the matplotlib colormap to use in single band plots
    :param histogram (str): see rgb()
    :param stretch (list of numbers): see rgb()
    :param gamma (number): see rgb()

.. py:function:: rgb(histogram=None, stretch=[2,98], gamma=1.0, blm_source=None)

    Returns a uint8 Numpy array of the RGB bands for an image suitable for plotting with libraries like Matplotlib

    Several adjustment methods are available to tune the image appearance.

    Without any parameters, rgb() and plot() will use a contrast stretch over the 2nd and 98th percentil pixel values on each band.

    The parameter histogram='match' will contrast stretch over the minimum and maximum pixel values.
    The parameter histogram='equalize' will perform histogram equalization on the image.
    The parameter histogram='match' will match the image histogram to the same image bounds in the TMS base. Adding the parameter blm_source='browse' will use the Browse imagery instead.
    The parameter 'stretch'=[low, high] will contrast stretch between the low and high values. histogram='minmax' is equivalent to stretch=[0,100].
    The parameter 'gamma'=x will adjust the image gamma. Values of x greater than one will make the midtones brighter, values less than one make the midtones darker.
    If the stretch and gamma parameters are included with a histogram parameter, the stretch and gamma will be applied after the histogram adjustments.

    :param histogram (str): either 'minmax', 'equalize', or 'match'
    :param stretch (list of numbers): a list of low and high cutoffs for contrast stretching
    :param gamma (number): a value for the gamma adjustment
    :param blm_source (str): if set to 'browse' use the Browse service for histogram matching

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



