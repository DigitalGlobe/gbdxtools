Image Classes
==========

Image Class Overview
-----------------------

The image classes in gbdxtools provide access to remote imagery hosted in GBDX. The access is deferred, meaning that images can initialized
and maniupulated as numpy arrays and are data only fetched from the server when compute is necessary.

The classes are split into 2 types of images: CatalogImages and IdahoImages. CatalogImages use a GBDX Catalog ID (http://gbdxdocs.digitalglobe.com/docs/catalog-course) to aggregate image parts
into a single point of access, and IdahoImages represent a more one-to-one relationship with a given IDAHO Id (http://gbdxdocs.digitalglobe.com/docs/idaho-course).

Catalog Images
-----------------------

The following snippet will init a CatalogImage from a just a CatalogID and print the shape of the array:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400')
    print img.shape

It's worth noting that CatalogImages represent a mosiac of tiles stored on the server and no pixel data
are fetched until you call the images `read()` method (which will cause the entire image to be fetched from the server).

To prevent massive amounts of data from being transferred you'll often use a Area of Interest (aoi) to subset the data:

.. code-block:: python

    aoi = img.aoi(bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    print aoi

The AOI is now a cropped portion of the larger CatalogImage, and still no data have been fetched. We use Dask Arrays (http://dask.pydata.org/en/latest/array.html) to coordinate
the retrieval of data from the server. You can interact Dask arrays in a very similar fashion to how you'd work with Numpy arrays except that
when you need to access the underlying data Dask will fetch it in chunks from the server. AOIs can also be passed into the CatalogImage constructor as the `bbox=[...]` parameter.

To fetch data from the server for the purpose of visualizing or accessing properties like min, max, etc. CatalogImage's have a `read()` method.
The read method calls the server in parallel to fetch down all the data it needs to fulfill the image pixel data. Read is automatically
called for you when you when calling the `plot()` for visualizing images:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    img.plot()

    # or call read directly to get a numpy array:
    nd_array = img.read()
    print nd_array.shape


By default CatalogImages will return MultiSpectral bands for all images, but this can be configured to return the panchromatic using the `band_type=MS|Pan|pan` parameter:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    print img.shape


To fetch data as 8 band pansharpened imagery you can pass the `pansharpen=True|False` flag:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', pansharpen=True, bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    img.plot()

We also provide Rasterio access to imagery by using the `open()` method:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764])
    with img.open() as src:
        print src.meta, src.nblocks

Using this interface you can leverage Rasterio methods for reading data, windowing, and accessing image metadata directly.

You can also specify projections in the image constructor like so:

.. code-block:: python

    from gbdxtools import CatalogImage

    img = CatalogImage('104001001BA7C400', band_type='Pan', bbox=[2.2889757156372075,48.87067123176554,2.301077842712403,48.87705036103764], proj='EPSG:3857')
    print img.shape

The `proj='PROJ4 String'` parameter will project imagery into the given projection.


Idaho Images
-----------------------

The IdahoImage class behaves in a similar manner as CatalogImages except it accepts an IDAHO Id instead:

.. code-block:: python

    from gbdxtools import IdahoImage

    img = IdahoImage('cfa89bc1-6115-4db1-9f43-03f060b52286')
    print img.shape


The same methods that are available to CatalogImages are available in IdahoImages except IdahoImages don't support band_types and pansharpening
as IDAHO IDs represent either a multispectral image OR a panchromatic (they're stored on the server separately).
