Catalog Searches
==========

Catalog Search Overview
-----------------------

The catalog can be searched various ways, generally like this:

.. code-block:: pycon

   results = gbdx.catalog.search( ... args ... )

The results will be a list of items, each of which contains quite a lot of metadata and looks something like this:

.. code-block:: pycon

	{
		"owner": "7b216bd9-6523-4ca9-aa3b-1d8a5994f054",
		"identifier": "101001000281E600",
		"type": "DigitalGlobeAcquisition",
		"properties": {
			"sunElevation": "26.2667",
			"targetAzimuth": "91.47679",
			"sunAzimuth": "162.5099",
			"timestamp": "2003-11-27T00:00:00.000Z",
			"offNadirAngle": "9.0",
			"cloudCover": "6.0",
			"multiResolution": "2.480306149",
			"browseURL": "https://browse.digitalglobe.com/imagefinder/showBrowseMetadata?catalogId=101001000281E600",
			"panResolution": "0.620390713",
			"footprintWkt": "POLYGON ((-112.249662 41.26810813, -112.0471457 41.26691053, -112.0471218 41.21128254, -112.0470635 41.15576778, -112.0470193 41.1002849, -112.0468856 41.04491751, -112.0468263 40.98960299, -112.0468154 40.93429073, -112.0468277 40.87893259, -112.0467612 40.82357493, -112.0466661 40.76815214, -112.0465818 40.71267682, -112.0469022 40.65708733, -112.0468488 40.60141699, -112.0468019 40.54567617, -112.0468795 40.48981261, -112.0471183 40.43378609, -112.0466806 40.37781586, -112.0466431 40.36907251, -112.252435 40.36636078, -112.2522955 40.3751995, -112.2523337 40.4314792, -112.2516845 40.48786638, -112.2504122 40.54429583, -112.2501899 40.60029535, -112.2498266 40.65624682, -112.2495379 40.71204009, -112.2494044 40.76774333, -112.2493635 40.82337556, -112.2493227 40.87893528, -112.2492872 40.93449091, -112.2493008 40.99000069, -112.2492497 41.04548369, -112.2492948 41.10100015, -112.249356 41.15663737, -112.2495337 41.21232543, -112.249662 41.26810813))",
			"catalogID": "101001000281E600",
			"imageBands": "Pan_MS1",
			"sensorPlatformName": "QUICKBIRD02",
			"vendorName": "DigitalGlobe"
		}
	}

You could get a list of catalog IDs by doing this, for example:

.. code-block:: pycon
	
	catalog_ids = [r['identifier'] for r in results]

Search by AOI
-----------------------
Search the catalog by AOI, as defined by a WKT polygon.  All imagery that intersects the polygon will be returned.

.. code-block:: pycon

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"
    results = gbdx.catalog.search(searchAreaWkt=wkt_string)


Search by Dates
-----------------------
The catalog can also be searched by date.  Note that if no search-polygon is supplied, the catalog only supports 
date searches of of one week intervals at a time.


.. code-block:: pycon

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"
    results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                                  startDate="2004-01-01T00:00:00.000Z",
                                  endDate="2012-01-01T00:00:00.000Z")

Search with Filters
-----------------------
You can add filters for any properties in the catalog items you are searching for.  For example, here's how you return only Quickbird 2 
images:

.. code-block:: pycon

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"

	filters = ["sensorPlatformName = 'QUICKBIRD02'"]

    results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                                  startDate="2004-01-01T00:00:00.000Z",
                                  endDate="2012-01-01T00:00:00.000Z",
                                  filters=filters)

Here's a more complicated set of filters that can be applied:

.. code-block:: pycon

	filters = [  
                    "(sensorPlatformName = 'WORLDVIEW01' OR sensorPlatformName ='QUICKBIRD02')",
                    "cloudCover < 10",
                    "offNadirAngle > 10"
               ]

Search by Types
-----------------------
You can search by type as well.  The usual type for Digital Globe Imagery is "DigitalGlobeAcquisition".  
To search only Landsat imagery for example:

.. code-block:: pycon

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"

	types = [ "LandsatAcquisition" ]

    results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                                  startDate="2004-01-01T00:00:00.000Z",
                                  endDate="2012-01-01T00:00:00.000Z",
                                  types=types)


