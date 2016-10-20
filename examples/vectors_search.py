import json, gbdxtools
gbdx = gbdxtools.Interface()

# Let's find all the Worldview 3 vector footprints in colorado
colorado_aoi = "POLYGON((-108.89 40.87,-102.19 40.87,-102.19 37.03,-108.89 37.03,-108.89 40.87))"
results = gbdx.vectors.query(colorado_aoi, query="item_type:WV03")

geojson = {
	'type': 'FeatureCollection',
	'features': results
}

with open("vectors.geojson", "w") as f:
	f.write(json.dumps(geojson))

# Now open the geojson in your favorite viewer