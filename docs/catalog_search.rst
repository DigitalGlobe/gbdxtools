Catalog Service
==================

Catalog Search Overview
-----------------------

The catalog can be searched various ways. The general pattern is:

.. code-block:: python

   results = gbdx.catalog.search( ... args ... )

Running a search returns a list of metadata items. An example of item metadata is:

.. code-block:: json

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

To reduce the list of results to just Catalog IDs:

.. code-block:: python
	
	catalog_ids = [r['identifier'] for r in results]

Running Searches
------------------------

Search by AOI
^^^^^^^^^^^^^^^
Search the catalog by AOI, as defined by a WKT polygon.  All imagery that intersects the polygon will be returned.

.. code-block:: python

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"
	results = gbdx.catalog.search(searchAreaWkt=wkt_string)


Search by Dates
^^^^^^^^^^^^^^^^
The catalog can also be searched by date.  Note that if no search-polygon is supplied, the catalog only supports 
date searches of one-week intervals at a time.


.. code-block:: python

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"
	results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                                  startDate="2004-01-01T00:00:00.000Z",
                                  endDate="2012-01-01T00:00:00.000Z")

Search with Filters
^^^^^^^^^^^^^^^^^^^^^^^
You can add filters for any of the properties in the catalog items.  For example, to return only Quickbird 2 
images:

.. code-block:: python

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"

	filters = ["sensorPlatformName = 'QUICKBIRD02'"]

	results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                                  startDate="2004-01-01T00:00:00.000Z",
                                  endDate="2012-01-01T00:00:00.000Z",
                                  filters=filters)

Multiple filters can be combined in the query:

.. code-block:: python

	filters = [  
		"(sensorPlatformName = 'WORLDVIEW01' OR sensorPlatformName ='QUICKBIRD02')",
		"cloudCover < 10",
		"offNadirAngle > 10"
	]

Search by Types
^^^^^^^^^^^^^^^^^^
You can search by item type as well.  The usual type for Digital Globe imagery is "DigitalGlobeAcquisition".  
To limit the search to only Landsat imagery:

.. code-block:: python

	wkt_string = "POLYGON((-113.88427734375 40.36642741921034,-110.28076171875 40.36642741921034,-110.28076171875 37.565262680889965,-113.88427734375 37.565262680889965,-113.88427734375 40.36642741921034))"

	types = [ "LandsatAcquisition" ]

	results = gbdx.catalog.search(searchAreaWkt=wkt_string,
                                  startDate="2004-01-01T00:00:00.000Z",
                                  endDate="2012-01-01T00:00:00.000Z",
                                  types=types)

Getting Metadata Info by Catalog ID
---------------------------------------------
To access the metadata record from the catalog for a given Catalog ID:

.. code-block:: pycon

	record = gbdx.catalog.get('1050410011360700')
	record
	>>> {   u'identifier': u'1050410011360700',
    >>> u'owner': u'7b216bd9-6523-4ca9-aa3b-1d8a5994f054',
    >>> u'properties': {   u'available': u'true',
    >>>                    u'browseURL': u'https://browse.digitalglobe.com/imagefinder/showBrowseMetadata?catalogId=1050410011360700',
    >>>                    u'catalogID': u'1050410011360700',
    >>>                    u'cloudCover': u'3.0',
    >>>                    u'footprintWkt': u'POLYGON ((103.20588 27.19044, 103.214232 27.189864, 103.230936 27.189432, 103.26852 27.188136, 103.300632 27.186984, 103.33116 27.185976, 103.388616 27.18324, 103.388904 27.170712, 103.388184 27.16236, 103.388616 27.15516, 103.389912 27.143208, 103.390488 27.123624, 103.390344 27.112824, 103.38876 27.104184, 103.389192 27.09684, 103.390632 27.079704, 103.390488 27.071208, 103.389912 27.062712, 103.390632 27.039672, 103.390344 27.035352, 103.387176 27.01764, 103.38516 27.00684, 103.383144 27.006696, 103.339656 27.008568, 103.323528 27.00972, 103.321656 27.00972, 103.304664 27.011448, 103.297176 27.01188, 103.279176 27.013464, 103.263192 27.014184, 103.232088 27.017064, 103.214664 27.018072, 103.197672 27.019512, 103.198392 27.028296, 103.198824 27.037224, 103.198248 27.042696, 103.19796 27.05652, 103.197528 27.062424, 103.199976 27.079272, 103.199112 27.087336, 103.200408 27.097704, 103.200696 27.112104, 103.1994 27.120888, 103.20012 27.131544, 103.202136 27.146952, 103.20516 27.160632, 103.205448 27.168984, 103.205016 27.18036, 103.205448 27.187128, 103.20588 27.19044))',
    >>>                    u'imageBands': u'Pan_MS1',
    >>>                    u'multiResolution': u'1.92278111',
    >>>                    u'offNadirAngle': u'23.0',
    >>>                    u'panResolution': u'0.480095029',
    >>>                    u'sensorPlatformName': u'GEOEYE01',
    >>>                    u'sunAzimuth': u'131.3206',
    >>>                    u'sunElevation': u'69.3045',
    >>>                    u'targetAzimuth': u'102.357414',
    >>>                    u'timestamp': u'2014-08-20T00:00:00.000Z',
    >>>                    u'vendorName': u'DigitalGlobe'},
    >>> u'type': u'DigitalGlobeAcquisition'}

You can also include relationship information to find associated data and products:

.. code-block:: pycon

	record = gbdx.catalog.get('1050410011360700', includeRelationships=True)
	record
	>>> {   u'identifier': u'1050410011360700',
    >>> u'inEdges': {   u'_acquisition': [   {   u'fromObjectId': u'98c00c48-0015-4673-8a17-62e69e9899a0',
    >>>                                          u'identifier': u'281e842d-6706-4e80-8f4c-00d217eb25c2',
    >>>                                          u'label': u'_acquisition',
    >>>                                          u'toObjectId': u'1050410011360700'},
    >>>                                      {   u'fromObjectId': u'cb7b8668-0883-487d-b862-89d02b8674af',
    >>>                                          u'identifier': u'fe7635e1-02b9-4350-8dd3-1b98ec12450f',
    >>>                                          u'label': u'_acquisition',
    >>>                                          u'toObjectId': u'1050410011360700'},
    >>>                                      {   u'fromObjectId': u'10284854-5024-42d8-8c6c-fb1720592ba3',
    >>>                                          u'identifier': u'cf9bf35e-fd2a-4827-8fa6-03de08f796cd',
    >>>                                          u'label': u'_acquisition',
    >>>                                          u'toObjectId': u'1050410011360700'},
    >>>                                      {   u'fromObjectId': u'713baa24-c30c-4358-a487-6c561da866eb',
    >>>                                          u'identifier': u'3096ee31-152e-4e30-af42-6728ff03e342',
    >>>                                          u'label': u'_acquisition',
    >>>                                          u'toObjectId': u'1050410011360700'}]},
    >>> u'owner': u'7b216bd9-6523-4ca9-aa3b-1d8a5994f054',
    >>> u'properties': {   u'available': u'true',
    >>>                    u'browseURL': u'https://browse.digitalglobe.com/imagefinder/showBrowseMetadata?catalogId=1050410011360700',
    >>>                    u'catalogID': u'1050410011360700',
    >>>                    u'cloudCover': u'3.0',
    >>>                    u'footprintWkt': u'POLYGON ((103.20588 27.19044, 103.214232 27.189864, 103.230936 27.189432, 103.26852 27.188136, 103.300632 27.186984, 103.33116 27.185976, 103.388616 27.18324, 103.388904 27.170712, 103.388184 27.16236, 103.388616 27.15516, 103.389912 27.143208, 103.390488 27.123624, 103.390344 27.112824, 103.38876 27.104184, 103.389192 27.09684, 103.390632 27.079704, 103.390488 27.071208, 103.389912 27.062712, 103.390632 27.039672, 103.390344 27.035352, 103.387176 27.01764, 103.38516 27.00684, 103.383144 27.006696, 103.339656 27.008568, 103.323528 27.00972, 103.321656 27.00972, 103.304664 27.011448, 103.297176 27.01188, 103.279176 27.013464, 103.263192 27.014184, 103.232088 27.017064, 103.214664 27.018072, 103.197672 27.019512, 103.198392 27.028296, 103.198824 27.037224, 103.198248 27.042696, 103.19796 27.05652, 103.197528 27.062424, 103.199976 27.079272, 103.199112 27.087336, 103.200408 27.097704, 103.200696 27.112104, 103.1994 27.120888, 103.20012 27.131544, 103.202136 27.146952, 103.20516 27.160632, 103.205448 27.168984, 103.205016 27.18036, 103.205448 27.187128, 103.20588 27.19044))',
    >>>                    u'imageBands': u'Pan_MS1',
    >>>                    u'multiResolution': u'1.92278111',
    >>>                    u'offNadirAngle': u'23.0',
    >>>                    u'panResolution': u'0.480095029',
    >>>                    u'sensorPlatformName': u'GEOEYE01',
    >>>                    u'sunAzimuth': u'131.3206',
    >>>                    u'sunElevation': u'69.3045',
    >>>                    u'targetAzimuth': u'102.357414',
    >>>                    u'timestamp': u'2014-08-20T00:00:00.000Z',
    >>>                    u'vendorName': u'DigitalGlobe'},
    >>> u'type': u'DigitalGlobeAcquisition'}

Finding Data Location by Catalog ID
---------------------------------------
The location of the physical data for a given Catalog ID can be found using:

.. code-block:: pycon

	s3path = gbdx.catalog.get_data_location(catalog_id='1030010045539700')
	s3path
	>>> 's3://receiving-dgcs-tdgplatform-com/055158926010_01_003/055158926010_01'

This also works with Landsat data:

.. code-block:: pycon

	s3path = gbdx.catalog.get_data_location(catalog_id='LC81740532014364LGN00')
	s3path
	>>> 's3://landsat-pds/L8/174/053/LC81740532014364LGN00'



