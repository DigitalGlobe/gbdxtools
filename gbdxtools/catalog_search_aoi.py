"""
GBDX Catalog Search Helper Functions.

This set of functions is used for breaking up a large AOI into smaller AOIs to search, because the catalog API 
can only handle 2 square degrees at a time.

"""
from builtins import zip
from builtins import range

from pygeoif import geometry
import json

def point_in_poly(x,y,poly):
    n = len(poly)
    inside = False

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

    return inside

# range() but for float steps
def xfrange(start, stop, step):
    while start < stop:
        yield start
        start += step
    else:
        yield stop

def dedup_records(records):
    # 0.5 seconds for 5k records
    #print "Records: %s" % len(records)
    ids = set( [r['identifier'] for r in records] )
    #print "Ids: %s" % len(ids)

    deduped = []
    for r in records:
        if r['identifier'] in ids:
            deduped.append(r)
            ids = ids - set( [ r['identifier'] ] )

    #print "Deduped: %s" % len(deduped)
    return deduped

def bbox_in_poly(bbox,poly):
    W, S, E, N = bbox.bounds
    points = [(W,N),(E,N),(E,S),(W,S)]
    for p in points:
        if point_in_poly(p[0],p[1], poly.exterior.coords ):
            return True

def records_in_polygon(records,polygon):
    # Filter out the records that are not inside the polygon
    output_records = []
    for record in records:
        recordwkt = record['properties']['footprintWkt']
        record_polygon = geometry.from_wkt(recordwkt)
        if bbox_in_poly(record_polygon,polygon):
            output_records.append(record)

    #print "Filtered in polygon: %s" % len(output_records)
    return output_records

def polygon_from_bounds( bounds ):
    W, S, E, N = bounds
    return geometry.Polygon(  ( (W,N),(E,N),(E,S),(W,S),(W,N) )  )

def search_materials_in_multiple_small_searches(search_request, gbdx_connection):
    D = 1.4  # the size in degrees of the side of a square that we will search

    searchAreaWkt = search_request['searchAreaWkt']
    searchAreaPolygon = geometry.from_wkt(searchAreaWkt)

    W, S, E, N = searchAreaPolygon.bounds
    Ys = [i for i in xfrange(S,N,D)]
    Xs = [i for i in xfrange(W,E,D)]

    # Handle point searches:
    if W == E and N == S:
        Ys = [S, N]
        Xs = [W, E]

    # print Xs
    # print Ys
    # print searchAreaWkt

    records = []
    # Loop pairwise
    row = 0
    col = 0
    for y, y1 in zip(Ys, Ys[1:]):
        row = row + 1
        for x, x1 in zip(Xs, Xs[1:]):
            col = col + 1
            bbox = (x, y, x1, y1)
            subsearchpoly = polygon_from_bounds(bbox)

            # # verify that the subsearchpoly is inside the searchAreaPolygon.  If not break.
            if not bbox_in_poly(subsearchpoly,searchAreaPolygon) and not bbox_in_poly(searchAreaPolygon, subsearchpoly) and not (y == y1 and x == x1):
                pass
            else:

                search_request['searchAreaWkt'] = subsearchpoly.wkt

                url = 'https://geobigdata.io/catalog/v1/search?includeRelationships=false'
                headers = {'Content-Type':'application/json'}
                r = gbdx_connection.post(url, headers=headers, data=json.dumps(search_request))
                r.raise_for_status()

                records = records + r.json()['results']

    records = dedup_records(records)

    # this next line works, but filters too much stuff.  It removes some items intersecting the polygon.
    #records = records_in_polygon(records, searchAreaPolygon)  # this takes quite a while to run, so leave it commented

    return records