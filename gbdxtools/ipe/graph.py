import json
from concurrent.futures import Future, wait

VIRTUAL_IPE_URL = "https://idahoapi.geobigdata.io/v1"

from gbdxtools.ipe.error import NotFound, BadRequest

def resolve_if_future(future):
    if isinstance(future, Future):
        return future.result()
    else:
        return future


def get_ipe_graph(conn, graph_id):
    url = "{}/graph/{}".format(VIRTUAL_IPE_URL, graph_id)
    req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return graph_id
    else:
        raise NotFound("No IPE graph found matching id: {}".format(graph_id))


def register_ipe_graph(conn, ipe_graph):
    url = "{}/graph".format(VIRTUAL_IPE_URL)
    res = resolve_if_future(conn.post(url, json.dumps(ipe_graph, sort_keys=True), headers={'Content-Type': 'application/json'}))
    return res.content


def get_ipe_metadata(conn, ipe_id, node='toa_reflectance'):
    #image_response = conn.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/image.json".format(ipe_id, node)).result()
    #georef_response = conn.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/georeferencing.json".format(ipe_id, node)).result()
    #rpcs_response = conn.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/rpcs.json".format(ipe_id, node)).result()

    #image_response = resolve_if_future(image_response)
    #georef_response = resolve_if_future(georef_response)
    #rpcs_response = resolve_if_future(rpcs_response)

    #meta = {"image": image_response.json(), "rpcs": rpcs_response.json() }
    #try:
    #    meta["georef"] = georef_response.json()
    #except:
    #    meta["georef"] = None

    md_response = conn.get(VIRTUAL_IPE_URL + "/metadata/{}/{}/metadata.json".format(ipe_id, node)).result()
    md_json = md_response.json()

    if md_response.status_code != 200 or ('error' in md_json or 'message' in md_json):
        raise BadRequest("Problem fetching image metadata: {}".format(md_response.content))

    meta = {
        "image": md_json["imageMetadata"],
        "georef": md_json.get("imageGeoreferencing", None),
        "rpcs": md_json.get("rpcSensorModel", None)
    }
    return meta
