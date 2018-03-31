from gbdxtools.vectors import Vectors

from shapely import wkt
from shapely.geometry import box

band_types = {
    'MS': 'WORLDVIEW_8_BAND',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}


def vendor_id(rec):
    _id = rec['properties']['attributes']['vendorDatasetIdentifier']
    return _id.split(':')[1].split('_')[0]

def vector_services_query(query, aoi=None):
    vectors = Vectors()
    if not aoi:
        aoi = wkt.dumps(box(-180, -90, 180, 90))
    _parts = sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id'])
    return _parts


