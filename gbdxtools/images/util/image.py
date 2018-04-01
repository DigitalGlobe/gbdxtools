from gbdxtools.vectors import Vectors

from shapely import wkt
from shapely.geometry import box

band_types = {
    'MS': 'WORLDVIEW_8_BAND',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

def reproject_params(proj):
    _params = {}
    if proj is not None:
        _params["Source SRS Code"] = "EPSG:4326"
        _params["Source pixel-to-world transform"] = None
        _params["Dest SRS Code"] = proj
        _params["Dest pixel-to-world transform"] = None
    return _params

def vendor_id(rec):
    _id = rec['properties']['attributes']['vendorDatasetIdentifier']
    return _id.split(':')[1].split('_')[0]

def vector_services_query(query, aoi=None, **kwargs):
    vectors = Vectors()
    if not aoi:
        aoi = wkt.dumps(box(-180, -90, 180, 90))
    _parts = sorted(vectors.query(aoi, query=query, **kwargs), key=lambda x: x['properties']['id'])
    return _parts


