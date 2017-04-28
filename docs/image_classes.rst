Image Classes
==========

Image Class Overview
-----------------------

The image classes in gbdxtools provide access to remote imagery hosted on GBDX. The access is deferred, meaning that images can be initialized
and manipulated as numpy arrays and the actual pixel data is only fetched from the server when compute is necessary.

The classes are two: CatalogImage and IdahoImage. CatalogImage uses a GBDX Catalog id (http://gbdxdocs.digitalglobe.com/docs/catalog-course) to aggregate image parts
into a single point of access. IdahoImage represents a one-to-one relationship with a given IDAHO id (http://gbdxdocs.digitalglobe.com/docs/idaho-course).

Catalog Images
-----------------------

The following snippet will initialize a CatalogImage from a catalog id and print the shape of the array:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400')
    print img.shape

It's worth noting that a CatalogImage represents a mosaic of tiles stored on the server and no pixel data
is fetched until you call the `read()` method (which will cause the entire image to be fetched from the server).

To prevent massive amounts of data from being transferred, it is recommended to use an Area of Interest (AOI) to subset the data:

.. code-block:: python

    aoi = img.aoi(bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    print aoi

The AOI is now a cropped portion of the larger CatalogImage, and still no data has been fetched. We use Dask Arrays (http://dask.pydata.org/en/latest/array.html) to coordinate
the retrieval of data from the server. You can work with Dask arrays very similarly to numpy arrays except that
when you need to access the underlying data Dask will fetch it in chunks from the server. AOIs can also be passed into the CatalogImage constructor as the `bbox=[...]` parameter.

To fetch data from the server for the purpose of visualizing or accessing properties like min, max, etc. CatalogImage has a `read()` method.
The read method calls the server in parallel to fetch all the required pixel data locally. In addition, `read()` is automatically
called when `plot()` is called for visualizing an image:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    img.plot()

    # or call read directly to get a numpy array:
    nd_array = img.read()
    print nd_array.shape

By default, CatalogImage returns a multispectral image. CatalogImage can be configured to return the panchromatic using the `band_type=MS|Pan|pan` parameter:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    print img.shape

To fetch 8-band pan-sharpened imagery you can pass the `pansharpen=True|False` flag:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', pansharpen=True, bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    img.plot()

We also provide rasterio access to imagery by using the `open()` method:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    with img.open() as src:
        print src.meta, src.nblocks

Using this interface you can leverage rasterio methods for reading data, windowing, and accessing image metadata directly.

You can also specify projections in the image constructor:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764], proj='EPSG:3857')
    print img.shape

The `proj='PROJ4 String'` parameter will project imagery into the given projection.


Idaho Images
-----------------------

The IdahoImage class behaves in a similar manner as CatalogImage except it accepts an IDAHO id instead of a Catalog id:

.. code-block:: python

    from gbdxtools import IdahoImage

    img = IdahoImage('cfa89bc1-6115-4db1-9f43-03f060b52286')
    print img.shape


The methods of CatalogImage are also available in IdahoImage. However, the band_type and pansharpen parameters are not available.
(IDAHO multispectral and panchromatic images are stored separately on the server.)
