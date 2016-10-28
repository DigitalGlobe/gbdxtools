import gbdxtools
gbdx = gbdxtools.Interface()

wkt = "POLYGON((0 3,3 3,3 0,0 0,0 3))"       # Any WKT that defines the vector
results = gbdx.vectors.create_from_wkt(
	wkt,
	item_type='my_original_type',            # item_type is required
	ingest_source='api',                     # ingest_source is required
	attribute1='nothing',                    # All other parameters are interpreted as attributes
	attribute2='something',
	number=6,
	date='2015-06-06'
)

# The resulting vector can be searched for like:
search_aoi = "POLYGON((1 4,4 4,4 1,1 1,1 4))" 
results = gbdx.vectors.query(aoi, query="item_type:my_original_type")


# The resulting polygon looks like this:
# [  
#    {  
#       "geometry":{  
#          "type":"Polygon",
#          "coordinates":[  
#             [  
#                [  
#                   0.0,
#                   3.0
#                ],
#                [  
#                   3.0,
#                   3.0
#                ],
#                [  
#                   3.0,
#                   0.0
#                ],
#                [  
#                   0.0,
#                   0.0
#                ],
#                [  
#                   0.0,
#                   3.0
#                ]
#             ]
#          ]
#       },
#       "type":"Feature",
#       "properties":{  
#          "name":null,
#          "format":null,
#          "ingest_date":"2016-10-20T20:08:48Z",
#          "text":"",
#          "source":null,
#          "ingest_attributes":{  
#             "_rest_url":"https://vector.geobigdata.io/insight-vector/api/vectors",
#             "_rest_user":"nricklin"
#          },
#          "original_crs":"EPSG:4326",
#          "access":{  
#             "users":[  
#                "_ALL_"
#             ],
#             "groups":[  
#                "_ALL_"
#             ]
#          },
#          "item_type":[  
#             "my_original_type"
#          ],
#          "ingest_source":"api",
#          "attributes":{  
#             "date":"2015-06-06",
#             "attribute2":"something",
#             "attribute1":"nothing",
#             "number":"6"
#          },
#          "id":"5b372eb0-a83e-4b52-a40b-9a6f411b129f",
#          "item_date":"2016-10-20T20:08:48Z"
#       }
#    }
# ]