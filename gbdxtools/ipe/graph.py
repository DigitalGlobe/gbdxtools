import json
from gbdxtools.ipe.error import NotFound, BadRequest

VIRTUAL_IPE_URL = "https://idahoapi.geobigdata.io/v1"


def get_ipe_graph(conn, graph_id):
    url = "{}/graph/{}".format(VIRTUAL_IPE_URL, graph_id)
    req = conn.get(url)
    if req.status_code == 200:
        return graph_id
    else:
        raise NotFound("No IPE graph found matching id: {}".format(graph_id))


def register_ipe_graph(conn, ipe_graph):
    url = "{}/graph".format(VIRTUAL_IPE_URL)
    res = conn.post(url, json.dumps(ipe_graph), headers={'Content-Type': 'application/json'})
    return res.content


def fetch_metadata(conn, url):
    res = conn.get(url)
    res_json = res.json()
    if res.status_code != 200 or ('error' in res_json or 'message' in res_json):
        raise BadRequest("Problem fetching image metadata: {}".format(res_json.get('error', res.content)))
    else:
        return res_json


def get_ipe_metadata(conn, ipe_id, node='toa_reflectance'):
    meta = dict()
    meta['image'] = fetch_metadata(conn,
                                   VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/image.json".format(ipe_id, node))
    meta['georef'] = fetch_metadata(conn,
                                    VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/georeferencing.json".format(ipe_id,
                                                                                                                 node))
    return meta
