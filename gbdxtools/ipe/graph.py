import json
import requests

VIRTUAL_IPE_URL = "https://idahoapi.geobigdata.io/v1"

from gbdxtools.ipe.error import NotFound

def get_ipe_graph(conn, graph_id):
    url = "{}/graph/{}".format(VIRTUAL_IPE_URL, graph_id)
    req = conn.get(url)
    if req.status_code == 200:
        print('FOUND')
        return graph_id 
    else:
        print('NOT FOUND')
        raise NotFound("No IPE graph found matching id: {}".format(graph_id))

def register_ipe_graph(conn, ipe_graph):
    url = "{}/graph".format(VIRTUAL_IPE_URL)
    print('POSTING')
    res = conn.post(url, json.dumps(ipe_graph), headers={'Content-Type': 'application/json'})
    print(res.status_code, res.text)
    print(ipe_graph['id'])
    return ipe_graph['id']

def get_ipe_metadata(conn, ipe_id, node='toa_reflectance'):
    meta = {}
    print('IMAGE', VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/image.json".format(ipe_id, node))
    meta['image'] = conn.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/image.json".format(ipe_id, node)).json()
    meta['georef'] = conn.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/georeferencing.json".format(ipe_id, node)).json()
    return meta
