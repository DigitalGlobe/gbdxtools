Image Classes
==========

Image Class Overview
-----------------------

The image classes in gbdxtools provide access to remote imagery hosted on GBDX. The access is deferred, meaning that images can be initialized
and manipulated as numpy arrays and the actual pixel data is only fetched from the server when compute is necessary.

The available classes are CatalogImage, IdahoImage, WV02, WV03_VNIR, IkonosImage, LandsatImage, TmsImage and DemImage. Each class behaves in very similar ways and extends the base-class "RDAImage". Imagery at DigitalGlobe are stored and processed by a service called Raster Data Access, or RDA. This service accepts processing graphs that are capable of running many different operations on an image before serving the pixels. For example, image orthorectification, mosaicing, and pansharpening are all possible via RDA. Users submit graphs to RDA and a new image id is created. However, the new id is only a virtual id, meaning that image tiles are only processed once requested. 

The image classes in gbdxtools attempt to hide the processing, graph creation and tile access from the end-user as much as possible.  


Catalog Images
-----------------------

CatalogImage uses a GBDX Catalog id (http://gbdxdocs.digitalglobe.com/docs/catalog-course) to aggregate image parts
into a single point of access. CatalogImages act as a generic image wrapper meaning that they can accept a range of 
id types (worldview, landsat, ikonos, etc.). The first thing a CatalogImage does is query the GBDX Platform to 
discover metadata about the image type. It will then instantiate the appropriate image class that matches the image id. 


The following snippet will initialize a CatalogImage from a catalog id for a WorldView3 image and print the shape of the array:

.. code-block:: python

    from gbdxtools import CatalogImage, WV03_VNIR

    img = CatalogImage('104001001BA7C400')
    print(img.shape, img.bounds)
    print(isinstance(img, WV03_VNIR))

It's worth noting that a CatalogImage represents a mosaic of tiles stored on the server and no pixel data
is fetched until you call the `read()` method (which will cause the entire image to be fetched from the server).

To prevent massive amounts of data from being transferred, it is recommended to use an Area of Interest (AOI) to subset the data:

.. code-block:: python

    aoi = img.aoi(bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    print(aoi)

The AOI is now a cropped portion of the larger CatalogImage, and still no data has been fetched. We use Dask Arrays (http://dask.pydata.org/en/latest/array.html) to coordinate
the retrieval of data from the server. You can work with Dask arrays very similarly to numpy arrays except that
when you need to access the underlying data Dask will fetch it in chunks from the server. AOIs can also be passed into the CatalogImage constructor as the `bbox=[...]` parameter. 
When passing `bbox` to the image constructor, `bbox` must be in the form of: `minx, miny, maxx, maxy` (or rather left, lower, right, upper) and be in `EPSG:4326` coordinates (lat/long).   

To fetch data from the server for the purpose of visualizing or accessing properties like min, max, etc. CatalogImage has a `read()` method.
The read method calls the server in parallel to fetch all the required pixel data locally. In addition, `read()` is automatically
called when `plot()` is called for visualizing an image:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    img.plot()

    # or call read directly to get a numpy array:
    nd_array = img.read()
    print(nd_array.shape)

By default, CatalogImage returns a multispectral image. CatalogImage can be configured to return the panchromatic using the `band_type=MS|Pan|pan` parameter:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    print(img.shape, img.bounds)

To fetch 8-band pan-sharpened imagery you can pass the `pansharpen=True|False` flag:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', pansharpen=True, bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    img.plot()

You can also specify projections in the image constructor:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764], proj='EPSG:3857')
    print(img.shape)

The `proj='PROJ4 String'` parameter will project imagery into the given projection.

Each image class' primary format are Numpy arrays, but sometimes other formats are needed. We provide a helper method to create GeoTiff files directly from images:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764], proj='EPSG:3857')
    tif = img.geotiff(path="./output.tif", proj="EPSG:4326")

The above code generates a geotiff on the filesystem with the name `output.tif` and the projection `EPSG:4326`. You can also pass an array of band indices (`bands=[4,2,1]`) to the `geotiff` method like so: 

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764], proj='EPSG:3857')
    tif = img.geotiff(path="./output.tif", proj="EPSG:4326", bands=[4,2,1])

This will create a geotiff on the the filesystem with only the bands `4,2,1`.

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764], proj='EPSG:3857')
    tif = img.geotiff(path="./output.tif", proj="EPSG:4326", spec='rgb')

This will create a geotiff of the RGB bands, dynamically adjusted to an 8 bit range.

Atmospheric Compensation
-----------------------

Currently every catalog image fetches data as Top of Atmosphere (TOA) Reflectance values. As of gbdxtools version 0.14.3 its now possible to fetch data that have been processed via Atmospheric Compensation (acomp). Acomp is a process used to remove haze and vapor particles and clarify imagery in a variety of atmospheric conditions. This can be useful for a variety of applications and can provide more consistent imagery when comparing images over time. To use acomp on a CatalogImage you can pass `acomp=True` to the image constructor. Note: There are many images on the platform that do not yet support `acomp=True`, if this is the case such images with throw an error during initialization.

.. code-block:: python

    from gbdxtools import CatalogImage

    img_acomp = CatalogImage('104001001BA7C400', acomp=True)
    aoi = img_acomp.randwindow((500,500))
    aoi.plot()

To request the image as raw Digital Numbers (DN) with no compensation, you can pass `correctionType=DN` to the image constructor.

.. code-block:: python

    from gbdxtools import CatalogImage
    
    img_dn = CatalogImage('104001001BA7C400', correctionType='DN') 
    print(image_dn.shape)

Idaho Images
-----------------------

The IdahoImage class behaves in a similar manner as CatalogImage except it accepts an IDAHO id instead of a Catalog id:

.. code-block:: python

    from gbdxtools import IdahoImage

    img = IdahoImage('87a5b5a7-5438-44bf-926a-c8c7bc153713')
    print(img.shape)

The methods of CatalogImage are also available in IdahoImage. However, the band_type and pansharpen parameters are not available.
(IDAHO multispectral and panchromatic images are stored separately on the server.)


Landsat Images
-----------------------

GBDX also indexes all Landsat8 images and are served up by AWS. The LandsatImage class behaves exactly like a CatalogImage except it accepts a Landsat ID instead of a Catalog ID:

.. code-block:: python

    from gbdxtools import LandsatImage

    img = LandsatImage('LC80370302014268LGN00')
    print(img.shape)
    aoi = img.aoi(bbox=[-109.84, 43.19, -109.59, 43.34])
    print(aoi.shape)
    aoi.plot()


DEM Images
-----------------------

Both the DemImage and TmsImage (below) classes behave in a bit different fashion than the other image classes. The DemImage class is used to fetch a numpy array of Digital Elevation Model (DEM) data from the NED/SRTM dataset. Since the dataset is static this class uses an Area of Interest (AOI) in place of a catalog id. 

.. code-block:: python

    from gbdxtools import DemImage

    aoi = [5.279273986816407, 60.35854536321686, 5.402183532714844, 60.419106714507116]
    dem = DemImage(aoi)
    print(dem.shape)

Beyond replacing catalog ids for AOIs the DemImage class share all the same methods as the above image classes.

TMS Images
-----------------------

The TmsImage class is used to access imagery available from the Maps API. These are global mosiacs of imagery that can be useful for training Machine Learning algorithms or whenever high-resolution is needed. Since the Map API is static, or changes less frequently, these images are best suited when there are no temporal requirements on an analysis. 

.. code-block:: python

    from gbdxtools import TmsImage

    img = TmsImage(zoom=13)
    print(img.shape)
    aoi = img.aoi(bbox=[-109.84, 43.19, -109.59, 43.34])
    print(aoi.shape)
    aoi.plot()


S3 Images
-----------------------

Sometimes it's necessary to access data directly from an Amazon S3 bucket (for instance when a GBDX Workflow creates new geotiff files). To enable exploration of such datasets we've added an `S3Image` class to `gbdxtools`. This class is a bit limited in its capability for running server side processes like pansharpening or atmospheric compensation, but does support reprojection. 
 
.. code-block:: python

    from gbdxtools import S3Image

    img = S3Image('landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF')
    print(img.shape)

Because images living in S3 are not always catalog'd the `S3Image` class accepts an "s3 path". This path is constructed from a `bucket` and `prefix`. In the example above, the bucket is 'landsat-pds' and the prefix is `c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF`. 
