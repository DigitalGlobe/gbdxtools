from gbdxtools.vectors import Vectors
from gbdxtools.auth import Auth
from shapely import wkt
from shapely.geometry import box

band_types = {
    'Ms': 'MS',
    'ms': 'MS',
    'MS': 'MS',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN',
    'PAN': 'PAN',
    'PANSHARP': 'PANSHARP',
    'PanSharp': 'PANSHARP',
    'Pansharp': 'PANSHARP'
}

def reproject_params(proj):
    _params = {}
    if proj is not None:
        _params["SourceSRSCode"] = "EPSG:4326"
        _params["DestSRSCode"] = proj
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

def _req_with_retries(conn, url, retries=5):
    for i in range(retries):
        try:
            res = conn.get(url)
            if res.status_code != 502:
                return res
        except:
            pass
    return None

def is_ordered(cat_id):
    """
      Checks to see if a CatalogID has been ordered or not.

      Args:
        catalogID (str): The catalog ID from the platform catalog.
      Returns:
        ordered (bool): Whether or not the image has been ordered
    """
    url = 'https://rda.geobigdata.io/v1/stripMetadata/{}'.format(cat_id)
    auth = Auth()
    r = _req_with_retries(auth.gbdx_connection, url)
    if r is not None:
        return r.status_code == 200
    return False

def can_acomp(cat_id):
    """
      Checks to see if a CatalogID can be atmos. compensated or not.

      Args:
        catalogID (str): The catalog ID from the platform catalog.
      Returns:
        available (bool): Whether or not the image can be acomp'd
    """
    url = 'https://rda.geobigdata.io/v1/stripMetadata/{}/capabilities'.format(cat_id)
    auth = Auth()
    r = _req_with_retries(auth.gbdx_connection, url)
    try: 
        data = r.json()
        return data['acompVersion'] is not None
    except:
        return False


