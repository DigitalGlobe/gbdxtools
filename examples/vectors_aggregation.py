import gbdxtools
from gbdxtools.vectors import TermsAggDef, GeohashAggDef

gbdx = gbdxtools.Interface()

# Let's look in colorado
colorado_aoi = "POLYGON((-108.89 40.87,-102.19 40.87,-102.19 37.03,-108.89 37.03,-108.89 40.87))"

# Let's limit our search to the OSM indexes
search_index = 'read-vector-osm-*'

# Let's find things that match 'transportation' somewhere in a text field
query = 'transportation'

# let's get 5 geohash buckets with the top 5 item_type values in each
child_agg = TermsAggDef('item_type')
agg = GeohashAggDef('3', children=child_agg)
result = gbdx.vectors.aggregate_query(colorado_aoi, agg, query, index=search_index, count=5)

# the result has a single-element list containing the top-level aggregation
for entry in result[0]['terms']:  # the 'terms' field contains our buckets
    geohash_str = entry['term']  # the 'term' entry contains our geohash
    print geohash_str
    child_aggs = entry[ 'aggregations']  # the 'aggregations' field contains the child aggregations for the 'item_type' values

    # since the child aggregations have the same structure, we can walk it the same way.
    # let's create a dict of item_types and their counts
    for child in child_aggs:
        types = {bucket['term']: bucket['count'] for bucket in child['terms']}

    # we could do something cool with these, but for now we'll just print them
    for item_type in types:
        print '\t%s:%s' % (item_type, types[item_type])
