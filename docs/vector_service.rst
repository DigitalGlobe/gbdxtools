Vector Service
==========

Vector Services Overview
-----------------------

GBDX Vector Services is an ElasticSearch based store of vectors that can be accessed in various ways.  
See http://gbdxdocs.digitalglobe.com/docs/read-vector-services-overview for complete details.

Typical use-cases involve searching, aggregating, and filtering vectors from multiple sources that have been
curated by Digitalglobe.  Vectors can also be stored and retrieved later for various purposes.

Simple Vector Search
-----------------------

The following snippet will look for all Worldview 3 footprints over Colorado:

.. code-block:: python

    import json, gbdxtools
    gbdx = gbdxtools.Interface()

    # Let's find all the Worldview 3 vector footprints in colorado
    colorado_aoi = "POLYGON((-108.89 40.87,-102.19 40.87,-102.19 37.03,-108.89 37.03,-108.89 40.87))"
    results = gbdx.vectors.query(colorado_aoi, query="item_type:WV03")

It's quite simple to save a geojson file that can be opened in your favorite GIS viewer:

.. code-block:: python

    geojson = {
        'type': 'FeatureCollection',
        'features': results
    }

    with open("vectors.geojson", "w") as f:
        f.write(json.dumps(geojson))

The query can be any valid Elasticsearch query string (see https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html#query-string-syntax).

For example, to find WV03 imagery taken only on a certain date we can do so in a more complicated query string:

.. code-block:: python

    query = "item_type:WV03 AND attributes.ACQDATE:\"2014-05-16\""
    results = gbdx.vectors.query(colorado_aoi, query=query)