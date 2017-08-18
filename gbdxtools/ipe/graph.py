import os
import json
from concurrent.futures import Future
from gbdxtools.ipe.error import NotFound, BadRequest

VIRTUAL_IPE_URL = os.environ.get("VIRTUAL_IPE_URL", "https://idahoapi.geobigdata.io/v1")


def resolve_if_future(future):
    if isinstance(future, Future):
        return future.result()
    else:
        return future


def get_ipe_graph(conn, graph_id):
    url = "{}/graph/{}".format(VIRTUAL_IPE_URL, graph_id)
    req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("No IPE graph found matching id: {}".format(graph_id))


def register_ipe_graph(conn, ipe_graph):
    url = "{}/graph".format(VIRTUAL_IPE_URL)
    res = resolve_if_future(conn.post(url, json.dumps(ipe_graph, sort_keys=True),
                                      headers={'Content-Type': 'application/json'}))
    if res.status_code == 200:
        return res.content
    else:
        raise BadRequest("Problem registering graph: {}".format(res.content))



def get_ipe_metadata(conn, ipe_id, node='toa_reflectance'):
    md_response = conn.get(VIRTUAL_IPE_URL + "/metadata/{}/{}/metadata.json".format(ipe_id, node)).result()
    if md_response.status_code != 200:
        raise BadRequest("Problem fetching image metadata: status {} / {}".format(md_response.status_code, md_response.reason))
    else:
        md_json = md_response.json()
        return {
            "image": md_json["imageMetadata"],
            "georef": md_json.get("imageGeoreferencing", None),
            "rpcs": md_json.get("rpcSensorModel", None)
        }
