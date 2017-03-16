import json

VIRTUAL_IPE_URL = "http://virtualidaho-env.us-east-1.elasticbeanstalk.com/v1"

def register_ipe_graph(conn, ipe_graph):
    url = "{}/graph".format(VIRTUAL_IPE_URL)
    return conn.post(url, json.dumps(ipe_graph), headers={"Content-Type": "application/json"}).text

def get_ipe_metadata(conn, ipe_id, node='toa_reflectance'):
    meta = {}
    meta['image'] = conn.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/image.json".format(ipe_id, node)).json()
    meta['georef'] = conn.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/georeferencing.json".format(ipe_id, node)).json()
    return meta
