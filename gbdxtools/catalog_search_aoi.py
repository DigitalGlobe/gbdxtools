"""
GBDX Catalog Search Functions.

"""

from pygeoif import geometry
​
def point_in_poly(x,y,poly):
    n = len(poly)
    inside = False
​
    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y
​
    return inside
​
# range() but for float steps
def xfrange(start, stop, step):
    while start < stop:
        yield start
        start += step
    else:
        yield stop
​
def dedup_records(records):
    # 0.5 seconds for 5k records
    print "Records: %s" % len(records)
    ids = set( [r['identifier'] for r in records] )
    print "Ids: %s" % len(ids)
​
    deduped = []
    for r in records:
        if r['identifier'] in ids:
            deduped.append(r)
            ids = ids - set( [ r['identifier'] ] )
​
    print "Deduped: %s" % len(deduped)
    return deduped
    
def bbox_in_poly(bbox,poly):
    W, S, E, N = bbox.bounds
    points = [(W,N),(E,N),(E,S),(W,S)]
    for p in points:
        if point_in_poly(p[0],p[1], poly.exterior.coords ):
            return True
            
def records_in_polygon(records,polygon):
    # Filter out the records that are not inside the polygon
    start_time = time.time()
    output_records = []
    for record in records:
        recordwkt = record['properties']['footprintWkt']
        record_polygon = geometry.from_wkt(recordwkt)
        if bbox_in_poly(record_polygon,polygon):
            output_records.append(record)
​
    end_time = time.time() - start_time
    print "Filtered in polygon: %s" % len(output_records)
    print "Time to filter records in polygon: %s" % end_time
    return output_records
    
def search_materials_in_multiple_small_searches(self, search_request):
    start_time = time.time()
    D = 1.4  # the size in degrees of the side of a square that we will search
    #D = .6
    max_records = 7000 # don't return much more than this number of records
    max_time = 35.0 # Don't run longer than this number of seconds
    catalog_api = self._get_catalog_api()
    searchAreaWkt = search_request['searchAreaWkt']
    searchAreaPolygon = geometry.from_wkt(searchAreaWkt)
​
    W, S, E, N = searchAreaPolygon.bounds
    Ys = [i for i in xfrange(S,N,D)]
    Xs = [i for i in xfrange(W,E,D)]
​
    print Xs
    print Ys
    print searchAreaWkt
​
    totalRecords = 0
    recordsReturned = 0
    typeCounts = Counter()
    records = []
    exit = False
    # Loop pairwise
    row = 0
    col = 0
    for y, y1 in zip(Ys, Ys[1:]):
        row = row + 1
        for x, x1 in zip(Xs, Xs[1:]):
            col = col + 1
            bbox = (x, y, x1, y1)
            subsearchpoly = polygon_from_bounds(bbox)
​
            # # verify that the subsearchpoly is inside the searchAreaPolygon.  If not break.
            if not bbox_in_poly(subsearchpoly,searchAreaPolygon) and not bbox_in_poly(searchAreaPolygon, subsearchpoly):
                print "box not in poly:"
                print col, row
            else:
​
                search_request['searchAreaWkt'] = subsearchpoly.wkt
​
                catalog_search_response_dict = catalog_api.search.post(search_request, includeRelationships="False")
                totalRecords += catalog_search_response_dict['stats']['totalRecords']
                recordsReturned += catalog_search_response_dict['stats']['recordsReturned']
                records = records + catalog_search_response_dict['results']
                typeCounts.update( catalog_search_response_dict['stats']['typeCounts'] )
​
            if totalRecords >= max_records or time.time() - start_time > max_time:
                print "truncating search"
                exit = True
                break
        if exit:
            break
​

    records = dedup_records(records)
    #records = records_in_polygon(records, searchAreaPolygon)  # this takes quite a while to run, so leave it commented
​
​
    ret = {}
    ret['results'] = records
    ret['stats'] = {}
    ret['stats']['totalRecords'] = len(records)
    ret['stats']['recordsReturned'] = len(records)
    ret['stats']['typeCounts'] = generate_typecounts(records,typeCounts)
    ret['searchTag'] = None
    return ret