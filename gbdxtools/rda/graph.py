import os
import json
from concurrent.futures import Future
from gbdxtools.rda.error import NotFound, BadRequest

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

VIRTUAL_RDA_URL = os.environ.get("VIRTUAL_RDA_URL", "https://rda.geobigdata.io/v1")

def resolve_if_future(future):
    if isinstance(future, Future):
        return future.result()
    else:
        return future

def get_graph_stats(conn, graph_id, node_id):
    url = "{}/metadata/{}/{}/display_stats.json".format(VIRTUAL_RDA_URL, graph_id, node_id)
    req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("Could not fetch stats for graph/node: {} / {}".format(graph_id, node_id))

def get_template_stats(conn, graph_id, node_id, **kwargs):
    qs = urlencode(kwargs)
    url = "{}/template/{}/display_stats.json?nodeId={}&{}".format(VIRTUAL_RDA_URL, graph_id, node_id, qs)
    req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("Could not fetch stats for graph/node: {} / {}".format(graph_id, node_id))

def get_rda_graph(conn, graph_id):
    url = "{}/graph/{}".format(VIRTUAL_RDA_URL, graph_id)
    req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("No RDA graph found matching id: {}".format(graph_id))

def get_rda_graph_template(conn, template_id):
    url = "{}/template/{}".format(VIRTUAL_RDA_URL, template_id)
    req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("No RDA Template found matching id: {}".format(template_id))


def register_rda_graph(conn, rda_graph):
    url = "{}/graph".format(VIRTUAL_RDA_URL)
    res = resolve_if_future(conn.post(url, json.dumps(rda_graph, sort_keys=True),
                                      headers={'Content-Type': 'application/json'}))
    if res.status_code == 200:
        return res.text
    else:
        raise BadRequest("Problem registering graph: {}".format(res.text))



def get_rda_metadata(conn, rda_id, node='toa_reflectance'):
    md_response = conn.get(VIRTUAL_RDA_URL + "/metadata/{}/{}/metadata.json".format(rda_id, node)).result()
    if md_response.status_code != 200:
        md_json = md_response.json()
        if 'error' in md_json:
            raise BadRequest("RDA error: {}. RDA Graph: {}".format(md_json['error'], rda_id))
        raise BadRequest("Problem fetching image metadata: status {} {}, graph_id: {}".format(md_response.status_code, md_response.reason, rda_id))
    else:
        md_json = md_response.json()
        return {
            "image": md_json["imageMetadata"],
            "georef": md_json.get("imageGeoreferencing", None),
            "rpcs": md_json.get("rpcSensorModel", None)
        }

def get_rda_template_metadata(conn, _id, **kwargs):
    qs = urlencode(kwargs)
    md_response = conn.get(VIRTUAL_RDA_URL + "/template/{}/metadata?{}".format(_id, qs)).result()
    if md_response.status_code != 200:
        md_json = md_response.json()
        if 'error' in md_json:
            raise BadRequest("RDA error: {}. RDA Graph: {}".format(md_json['error'], rda_id))
        raise BadRequest("Problem fetching image metadata: status {} {}, graph_id: {}".format(md_response.status_code, md_response.reason, rda_id))
    else:
        md_json = md_response.json()
        return {
            "image": md_json["imageMetadata"],
            "georef": md_json.get("imageGeoreferencing", None),
            "rpcs": md_json.get("rpcSensorModel", None)
        }
