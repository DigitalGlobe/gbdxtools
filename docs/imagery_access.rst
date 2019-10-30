Raster Data Access
===========================

The image classes in `gbdxtools` provide access to remote imagery hosted on GBDX. The access is deferred, meaning that images can be initialized and manipulated as NumPy arrays and the actual pixel data is only fetched from the server when compute is necessary.

The available classes are ``CatalogImage``, ``IdahoImage``, ``WV02``, ``WV03_VNIR``, ``IkonosImage``, ``LandsatImage``, ``TmsImage`` and ``DemImage``. Each class behaves in very similar ways and extends the base-class ``RDAImage``. Imagery at DigitalGlobe is stored and processed by a service called `Raster Data Access`, or RDA. This service accepts processing graphs that are capable of running many different operations on an image before serving the pixels. For example, image orthorectification, mosaicking, and pansharpening are all possible via RDA. Users submit graphs to RDA and a new image ID is created. However, the new ID is only a virtual ID, meaning that image tiles are only processed once requested. 

**The image classes in `gbdxtools` attempt to hide the processing, graph creation and tile access from the end-user as much as possible.**


Catalog Images
------------------

``CatalogImage`` uses a `GBDX Catalog ID <http://gbdxdocs.digitalglobe.com/docs/catalog-course>`_ to provide a single point of access to multiple image sources. This class acts as a generic image wrapper which can accept a range of ID types (WorldView, Landsat, Ikonos, etc.). The first thing a ``CatalogImage`` does is query the GBDX Platform to discover metadata about the image type. It will then instantiate the base image class corresponding to the image source. 

The following snippet will initialize a ``WorldviewImage`` from a WorldView 3 catalog ID and print some information about the image:

.. code-block:: python

    from gbdxtools import CatalogImage, WV03_VNIR

    img = CatalogImage('104001001BA7C400')
    print(img.shape, img.bounds)
    print(isinstance(img, WV03_VNIR))

It's worth repeating that a ``CatalogImage`` represents a mosaic of tiles stored on the server and no tiles are fetched until they are needed. 

To prevent massive amounts of data from being transferred, it is recommended to use an Area of Interest (AOI) to subset the data:

.. autocatmeta:: gbdxtools.images.meta.GeoDaskImage.aoi
    :noindex:

.. code-block:: python

    aoi = img.aoi(bbox=[2.28, 48.87, 2.30, 48.89])
    print(aoi)

The AOI is now a cropped portion of the larger catalog image, and still no data has been fetched. We use `Dask Arrays <http://dask.pydata.org/en/latest/array.html>`_ to coordinate the retrieval of data from the server. You can work with Dask arrays very similarly to NumPy arrays except that only when you need to access the underlying data will Dask fetch it in chunks from the server. The image bounding box can also be specified when instantiating the image by passing a ``bbox`` parameter. 

.. code-block:: python

    img = CatalogImage('104001001BA7C400', bbox=[2.28, 48.87, 2.30, 48.89])

`Gbdxtools` offers many different ways to specify the bounds of the image - see `Defining AOIs`_ below

There are two properties on the image classes that can be used to determine the final size of the image. To see the size in bytes, use ``image.nbytes``. The property ``ntiles`` gives the number of image tiles that need to be downloaded to build the image in memory and can be a useful shorthand for image size. 

.. code-block:: python

    print(img.nbytes) # size in bytes
    print(img.ntiles) # size in 256x256 pixel tiles

.. note:: If working with an image results in an out-of-memory error, or the kernel of a Jupyter notebook dying, check the image size to see if it's too large.

To fetch data from the server for the purpose of display or analysis ``CatalogImage`` has a ``read()`` method. The read method calls the server in parallel to fetch all the required pixel data locally and return it as a NumpPy array. In addition, ``read()`` is automatically called when ``plot()`` is called for displaying an image:

.. code-block:: python

    img = CatalogImage('104001001BA7C400', bbox=[2.28, 48.87, 2.30, 48.89])
    img.plot()

    # or call read directly to get a NumPy array:
    nd_array = img.read()
    print(nd_array.shape)

By default, ``CatalogImage`` returns a multispectral image. ``CatalogImage`` can be configured to return the panchromatic using the ``band_type=MS|Pan|pan`` parameter:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.28, 48.87, 2.30, 48.89])
    print(img.shape, img.bounds)

To fetch 8-band pan-sharpened imagery you can pass the ``pansharpen=True|False`` flag:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', pansharpen=True, bbox=[2.28, 48.87, 2.30, 48.89])
    img.plot()

You can also specify projections in the image constructor:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.28, 48.87, 2.30, 48.89], proj='EPSG:3857')
    print(img.shape)

The ``proj='PROJ4 String'`` parameter will reproject imagery into the given projection.

The resolution of the image can be adjusted with the ``gsd`` (Ground Sample Distance) parameter. The value needs to be in the same units as the requested image projection. The image will be resampled using bilinear resampling.

Downsampling is limited to 10 times the resolution of the lowest resolution overview. Upsampling is limited to 10 times the native resolution.

.. warning:: Image resampling methods can change the pixel values depending on the method used. Please be sure that bilinear resampling is appropriate for your analysis. For other resampling methods, see `scikit-image <http://scikit-image.org/docs/dev/api/skimage.transform.html>`_ ``skimage.transform``.

Resampling is commonly used to match resolutions between different images over the same area so they have the same array size for a given area of interest. 

.. code-block:: python

    from gbdxtools import CatalogImage
    # native resolution of this image is 1.1372619475386275e-05
    new_gsd = 1.138e-05
    img = CatalogImage('104001001BA7C400', bbox=[2.28, 48.87, 2.30, 48.89], gsd=new_gsd)
    print(img.shape)

The primary format of the image classes is the NumPy array, but for interoperability we provide a helper method to create GeoTiff files directly from images:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.28, 48.87, 2.30, 48.89], proj='EPSG:3857')
    tif = img.geotiff(path="./output.tif", proj="EPSG:4326")

The above code generates a geotiff on the filesystem with the name ``output.tif`` and the projection ``EPSG:4326``. You can also pass an array of band indices (``bands=[4,2,1]``) to the `geotiff` method: 

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', bbox=[2.28, 48.87, 2.30, 48.89], proj='EPSG:3857')
    tif = img.geotiff(path="./output.tif", proj="EPSG:4326", bands=[4,2,1])

This will create a geotiff on the the filesystem with only the bands `4,2,1` in that order.

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', bbox=[2.28, 48.87, 2.30, 48.87], proj='EPSG:3857')
    tif = img.geotiff(path="./output.tif", proj="EPSG:4326", spec='rgb')

This will create a geotiff of the RGB bands, dynamically adjusted to an 8 bit range.

Atmospheric Compensation
^^^^^^^^^^^^^^^^^^^^^^^^^^

Currently every catalog image fetches data as Top of Atmosphere (TOA) Reflectance values. It is also possible to fetch data processed with Atmospheric Compensation (acomp). Acomp is a process used to remove haze and vapor particles and clarify imagery in a variety of atmospheric conditions. This can improve the image quality and provides more consistent imagery when comparing images over time. To use acomp on a ``CatalogImage`` you can pass ``acomp=True`` to the image constructor. Note: There are many images on the platform that do not yet support ``acomp=True``. These images will throw an error during initialization. To check if a CatalogID can be acomp'd or not a method `CatalogImage.acomp_available(CatalogID)` is provided. This method will check metadata services to determine if acomp is possible or not. 

.. code-block:: python

    from gbdxtools import CatalogImage

    img_acomp = CatalogImage('104001001BA7C400', acomp=True)
    aoi = img_acomp.randwindow((500,500))
    aoi.plot()

To request the image as raw Digital Numbers (DN) with no compensation, you can pass ``correctionType=DN`` to the image constructor.

.. code-block:: python

    from gbdxtools import CatalogImage
    
    img_dn = CatalogImage('104001001BA7C400', correctionType='DN') 
    print(image_dn.shape)

To check if acomp is available for an image:

.. code-block:: python 

    from gbdxtools import CatalogImage

    can_acomp = CatalogImage.acomp_available('104001001BA7C400')
    print(can_acomp) 


Base Image Classes
--------------------------

The following image classes represent different sources of imagery.

Idaho Images
^^^^^^^^^^^^^^^^^^^^^^^

The IdahoImage class behaves in a similar manner as ``CatalogImage`` except it accepts an IDAHO ID instead of a Catalog id:

.. code-block:: python

    from gbdxtools import IdahoImage

    img = IdahoImage('87a5b5a7-5438-44bf-926a-c8c7bc153713')
    print(img.shape)

The methods of ``CatalogImage`` are also available in ``IdahoImage``. However, the band_type and pansharpen parameters are not available. (IDAHO multispectral and panchromatic images are stored separately on the server.)


Landsat Images
^^^^^^^^^^^^^^^^^^^^^^^

GBDX also indexes all Landsat8 images. The images are served from Amazon Web Services. The ``LandsatImage`` class behaves exactly like a ``CatalogImage`` except it accepts a Landsat ID instead of a Catalog ID:

.. code-block:: python

    from gbdxtools import LandsatImage

    img = LandsatImage('LC80370302014268LGN00')
    print(img.shape)
    aoi = img.aoi(bbox=[-109.84, 43.19, -109.59, 43.34])
    print(aoi.shape)
    aoi.plot()


DEM Images
^^^^^^^^^^^^^^^^^^^^^^^

Both the ``DemImage`` and ``TmsImage`` (below) classes behave in a different fashion than the other image classes. The ``DemImage`` class is used to fetch a NumPy array of Digital Elevation Model (DEM) data primarily from the NED/SRTM dataset. This dataset has a resolution of 30m and elevations are orthometric. Since the dataset is static this class uses an Area of Interest (AOI) in place of a catalog id. 

.. code-block:: python

    from gbdxtools import DemImage

    aoi = [5.279273986816407, 60.35854536321686, 5.402183532714844, 60.419106714507116]
    dem = DemImage(aoi)
    print(dem.shape)

Beyond replacing catalog ids for AOIs, the ``DemImage`` class shares all the same methods as the above image classes.

TMS Images
^^^^^^^^^^^^^^^^^^^^^^^

The ``TmsImage`` class is used to access imagery available from a Tile Map Service (TMS). These can be used as a static imagery source that can be an effective source for training Machine Learning algorithms or whenever high-resolution is needed. The zoom level to use can be specified (default is 18). Changing the zoom level will change the resolution of the image.

Subscribers to the new EarthWatch TMS service can use this image class to access EarthWatch base imagery in Python. Use the following configuration, substituting a valid ConnectID string.

.. code-block:: python

    from gbdxtools import TmsImage

    url = r"https://earthwatch.digitalglobe.com/earthservice/tmsaccess/tms/1.0.0/DigitalGlobe:ImageryTileService@EPSG:3857@jpg/{z}/{x}/{y}.jpg?flipy=true&connectId=<connectid>"
    img = TmsImage(url, zoom=13)
    print(img.shape)
    aoi = img.aoi(bbox=[-109.84, 43.19, -109.59, 43.34])
    print(aoi.shape)
    aoi.plot()


S3 Images
^^^^^^^^^^^^^^^^^^^^^^^

Use this class to access data directly from an Amazon S3 bucket, for instance when a GBDX Workflow creates a geotiff file. Server-side processes like pansharpening or atmospheric compensation are not supported with the exception of reprojection. The ``S3Image`` class accepts an "S3 path" instead of an ID.
 
.. code-block:: python

    from gbdxtools import S3Image

    img = S3Image('landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF')
    print(img.shape)


Sentinel2 Images
^^^^^^^^^^^^^^^^^^^^^

Sentinel2 images are accessed through the CatalogImage class. The default behaviour is to access the 10m sensor bands. To access the other sensor groups, pass a ``spec`` parameter with the values ``10m``, ``20m``, or ``60m``.

.. code-block:: python

    from gbdxtools import CatalogImage
    
    img = CatalogImage('e89d5a29-1119-5c0a-a007-a03341d5bc48', spec='20m')
    print(type(img))
    print('Resolution: {}m'.format(img.metadata['georef']['scaleX']))

For more information on the Sentinel2 sensor groups, see the `offical documentation <https://sentinel.esa.int/web/sentinel/user-guides/sentinel-2-msi/resolutions/spatial>`_.

Sentinel2 images also support the ``proj`` parameter for reprojection.

Sentinel1 Images
^^^^^^^^^^^^^^^^^^^^^

Sentinel1 images are accessed through the CatalogImage class similar to Sentinel2 except that Sentinel supports ``polarizations"``. The default polarization is ``VH``, and valid polarizations are ``VH``, ``HV``, ``VV``, and ``HH``.

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('S1A_IW_GRDH_1SDV_20180713T142443_20180713T142508_022777_027819_7A96', polarization='VH')
    print(type(img))
    print('Resolution: {}m'.format(img.metadata['georef']['scaleX']))

Sentinel1 images also support the ``proj`` parameter for reprojection.


RDA Template Images
^^^^^^^^^^^^^^^^^^^^^^^

Any RDA Template can be directly accessed using `RDATemplateImage`. The class takes a template ID as the first argument, an optional node ID as the second argument, and the template parameters passed as keywords. If no node ID is supplied, the image will be generated from the last node.

.. code-block:: python

    from gbdxtools import RDATemplateImage

    img = RDATemplateImage("DigitalGlobeStrip", # template ID
                            None,               # node ID, optional
                            crs="EPSG:4326",    # template parameters as keywords
                            bands="MS", 
                            catalogId="10400E0001DB6A00", 
                            draType=None, 
                            correctionType="DN", 
                            bandSelection="All")


Defining AOIs
--------------

In addition to using the ``.aoi()`` method, the image bounding box can be specified when instantiating the image by passing a ``bbox`` parameter.  When passing `bbox`` to the image constructor, the list must be in the form of: `minx, miny, maxx, maxy` (or rather left, lower, right, upper) and be in `EPSG:4326` coordinates (lat/long).  

.. code-block:: python

    img = CatalogImage('104001001BA7C400', bbox=[2.28, 48.87, 2.30, 48.89])

Image AOIs can also be defined by slicing with a geometry object. The image will be cropped to the bounds of the geometry.

.. code-block:: python

    from shapely.geometry import box
    img = CatalogImage('104001001BA7C400')
    # create a polygon geometry object of the bounding box
    bbox = box(2.28, 48.87, 2.30, 48.89)
    # slice the image using the polygon
    # this is equivalent to the img.aoi(...) example above
    aoi = img[bbox]
    print(aoi)

Because the image objects store the data as NumPy arrays, they also support basic array slicing:

.. code-block:: python

    sliced = img[:, 100:200, 300:400]
    print(sliced.shape)

Image objects store their geospatial information and also support the `Python geospatial interface <https://gist.github.com/sgillies/2217756>`_. You can easily get the bounds and projection of an object, and access the bounds as a geometry object:

.. code-block:: python

    print(img.bounds) # a list of bounds, like the bbox parameter
    print(img.proj) # an EPSG string
    
    from shapely.geometry import shape
    print(img.__geo_interface__) # a geojson-like Python dictionary
    print(shape(img).area) # shape() returns a Shapely object for geometry operations


Chip Generation
^^^^^^^^^^^^^^^^^^^

There are also several methods to generate fixed-size chips. The following two methods are useful for machine learning applications. The first will generate a chip centered on a input geometry. The second tiles an image into a grid of smaller chips.

.. automethod:: gbdxtools.images.meta.DaskImage.window_at
.. automethod:: gbdxtools.images.meta.DaskImage.window_cover

Random chips
^^^^^^^^^^^^^^^
These two methods generate windows in random locations and are convenient for generating test images in a given image strip without having to generate bounding boxes:

.. automethod:: gbdxtools.images.meta.DaskImage.randwindow
.. automethod:: gbdxtools.images.meta.DaskImage.iterwindows

.. note:: When an image object is subset to an AOI, the cropped data is discarded. It is not possible to expand the AOI by applying a larger bounding box. You must recreate the original image object and recrop instead.


Visualizing Imagery
---------------------

If run in iPython or Jupyter Notebooks, `gbdxtools` can show images using the MatPlotLib library. The most basic example is:

.. code-block:: python

    img.plot()

The ``plot`` method simplifies building a MatPlotLib plot and chooses sensible default options. Without arguments this method
will default to showing the RGB bands of the image. If the image only has a single band it will default the ``Grey_r`` colormap.

Options available for plotting:

* ``w,h`` : width and height of the plot, in inches at 72 dpi. This includes default borders and spacing. If the image is shown in Jupyter the outside whitespace will be automatically cropped to save size, resulting in a smaller sized image than expected. Default is ``w=10, h=10``.
* ``bands``: list of bands to use for plotting, such as ``bands=[4,2,1]``. Defaults to the image's natural RGB bands. This option is useful for generating pseudocolor images when passed a list of three bands. If only a single band is provided, a colormapped plot will be generated instead.
* ``title``: the title for the plot, if not specified no title is displayed.
* ``fontsize``: the font size for the title, in points. Default is 22.
* ``cmap``: MatPlotLib colormap to use for single band images. Default is ``cmap='Grey_R'``.
* ``histogram``, ``stretch``, and ``gamma``: These options provides several options for dynamic range adjustment of the image to convert the source imagery to an appropriate range needed for plotting. The default if none of these three options are specified is ``stretch=[2,98]``.

    * ``histogram``: adjust the histogram of the image:

        * ``histogram='equalize'``: performs histogram equalization on the image.
        * ``histogram='minmax'``: stretch the pixel range to the minimum and maximum input pixel values. Equivalent to ``stretch=[0,100]``.
        * ``histogram='match'``: match the histogram to the Maps API imagery. Pass the additional keyword ``blm_source='browse'`` to match to the Browse Service (image thumbnail) instead.
        * ``histogram='ignore'``: Skip dynamic range adjustment, in the event the image is already correctly balanced and the values are in the correct range.

    * ``stretch``: Stretch the histogram between two percentile values of the source image's dynamic range.
    * ``gamma``: Adjust the image gamma. Values greater than 1 will brighten the image midtones, values less than 1 will darken the midtones. Default is ``gamma=1.0``.

  Plots generated with the ``histogram`` options of ``'match'`` and ``'equalize'`` can be combined with the ``stretch`` and ``gamma`` options. The stretch and gamma adjustments will be applied after the histogram adjustments.

  To create more advanced plots in MatPlotLib you can create a NumPy array ready for plotting using the ``image.rgb()`` method, which mirrors the ``histogram``, ``stretch``, ``gamma``, and ``bands`` options listed above for ``plot()``. The array would then be added to the plot using the ``matplotlib.pyplot.imshow`` method.

.. note:: `gbdxtools` stores the bands in the first array axis `(3, 1200, 1600)`, while MatPlotLib expects the bands in the third axis `(1200, 1600, 3)`. To rearrage an image array for custom plotting you will need to run ``numpy.rollaxis(image_array, 3, 0)`` first.


Ordering Imagery
---------------------------

WorldView 2 and 3 imagery is initially stored in an archive until it's needed. To "order" an image means to request the image be moved from the archive to a location accessible through GBDX. The term "order" within GBDX does not mean requesting a satellite acquire an image, or purchasing an image or rights to an image.

This guide uses v2 of the GBDX ordering API. Ordering API v1 was deprecated on 02/25/2016.

Use the ordering member of the Interface to order imagery and check the status of your order.

To order the image with DG factory catalog ID 10400100143FC900:

.. code-block:: pycon

   >>> order_id = gbdx.ordering.order('10400100143FC900')
   >>> print(order_id)
   04aa8df5-8ac8-4b86-8b58-aa55d7353987

The order_id is unique to your image order and can be used to track the progress of your order.
The ordered image sits in a directory on S3. The order status and output image location can be found using:

.. code-block:: pycon

   >>> gbdx.ordering.status(order_id)
   >>> [{u'acquisition_id': u'10400100143FC900',
         u'location': u's3://receiving-dgcs-tdgplatform-com/055093431010_01_003',
         u'state': u'delivered'}]

Its possible to determine if an image has already been ordered by calling the `CatalogImage.is_ordered(CatalogID)` method:

.. code-block:: python

    from gbdxtools import CatalogImage

    ordered = CatalogImage.is_ordered('104001001BA7C400')
    print(ordered)


Advanced Topics
-----------------

Mapping functions over Dask arrays
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The underlying data structure of the image classes is a Dask array, which defers its computation until the pixels are needed. After fetching the pixel data it returns a NumPy array. Dask supports queuing up many standard functions such as addition and multiplication. Those functions are run on each block as the pixels are loaded.

If have a custom function that expects a NumPy array you would lose the functionality of the image object after running your function::

    from SomeImageLibrary import CoolFilter
    image = CatalogImage(....)
    filtered = CoolFilter(image.read())
    filtered.geotiff() # Errors - NumPy array has no geotiff method!

Dask has a map_blocks() method that can queue up any function that can run blockwise. `Gbdxtools` overrides this method so it works the same but returns another image object. So the above example can be done as::

    from SomeImageLibrary import CoolFilter
    image = CatalogImage(....)  
    filtered = image.map_blocks(CoolFilter) # queue the filter to run when the data is loaded
    filtered.geotiff() # Works

.. note:: The function applied by map_blocks() has to be able to run on each tile independently. It will have no access the to other tiles or other information about the overall image state unless they are precomputed and passed to the function.

Bootstrapping NumPy arrays to GeoDaskImages
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When you have a function that can not be run blockwise over the image tiles, there is a second way to retain some of the image object functionality. It's possible to bootstrap a NumPy array back into a simplified image object by using some of the lower level image metaclasses::

    # starting with a similar situation
    from SomeImageLibrary import AwesomeFilter
    image = CatalogImage(...)
    filtered = AwesomeFilter(image.read()) # returns a NumPy array

    # we'll also need to import
    from gbdxtools.images.meta import GeoDaskImage
    import dask.array as da
    import numpy as np

    # convert the array to a Dask array. A chunk size of 256 will work fine.
    filtered_dask = da.from_array(filtered, 256)

    # bootstrap a GeoDaskImage from the rgb Dask array and the original image's geo parameters
    geo_filtered = GeoDaskImage(filtered_dask, __geo_interface__=image.__geo_interface__, __geo_transform__=image.__geo_transform__)

    # export
    geo_filtered.geotiff(path='filtered.tif')

.. note:: The bootstrapped image must be the same size and location as the source image. It cannot be resampled to a different resolution or cropped.
