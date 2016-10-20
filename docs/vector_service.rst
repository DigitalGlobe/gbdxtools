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

Vector Creation
-----------------------

The following snippet will insert a polygon into the vector index:

.. code-block:: python

    aoi = "POLYGON((0 3,3 3,3 0,0 0,0 3))"
    results = gbdx.vectors.create_from_wkt(
        aoi,
        item_type='my_arbitrary_item_type',
        ingest_source='arbitrary_ingest_source',
        attribute1='nothing',
        attribute2='something',
        number=6,
        date='2015-06-06'
    )

item_type and ingest_source are required (and make searching and finding this vector easier later).  All other parameters are arbitrary attributes that will be included on the data.

The resulting vector as stored and retrievable looks like this:

.. code-block:: json

    {  
       "geometry":{  
          "type":"Polygon",
          "coordinates":[  
             [  
                [  
                   0.0,
                   3.0
                ],
                [  
                   3.0,
                   3.0
                ],
                [  
                   3.0,
                   0.0
                ],
                [  
                   0.0,
                   0.0
                ],
                [  
                   0.0,
                   3.0
                ]
             ]
          ]
       },
       "type":"Feature",
       "properties":{  
          "name":null,
          "format":null,
          "ingest_date":"2016-10-20T20:08:48Z",
          "text":"",
          "source":null,
          "ingest_attributes":{  
             "_rest_url":"https://vector.geobigdata.io/insight-vector/api/vectors",
             "_rest_user":"nricklin"
          },
          "original_crs":"EPSG:4326",
          "access":{  
             "users":[  
                "_ALL_"
             ],
             "groups":[  
                "_ALL_"
             ]
          },
          "item_type":[  
             "my_arbitrary_item_type"
          ],
          "ingest_source":"arbitrary_ingest_source",
          "attributes":{  
             "date":"2015-06-06",
             "attribute2":"something",
             "attribute1":"nothing",
             "number":"6"
          },
          "id":"5b372eb0-a83e-4b52-a40b-9a6f411b129f",
          "item_date":"2016-10-20T20:08:48Z"
       }
    }

