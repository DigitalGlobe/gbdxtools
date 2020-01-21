import os
import json
import time
from concurrent.futures import Future
from gbdxtools.rda.error import NotFound, BadRequest
import warnings
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

def req_with_retries(conn, url, retries=5):
    for i in range(retries):
        try:
            res = resolve_if_future(conn.get(url))
            if res.status_code != 502:
                return res
            elif res.status_code == 501:
                raise Exception('501 Auth error')
        except:
            pass
        time.sleep(0.5 * (i + 1))
    raise Exception('RDA is overloaded')


def get_graph_stats(conn, graph_id, node_id):
    warnings.warn('Graph API is deprecated')
    url = "{}/metadata/{}/{}/display_stats.json".format(VIRTUAL_RDA_URL, graph_id, node_id)
    req = req_with_retries(conn, url)
    #req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("Could not fetch stats for graph/node: {} / {}".format(graph_id, node_id))

def get_template_stats(conn, template_id, **kwargs):
    qs = urlencode(kwargs)
    url = "{}/template/{}/display_stats.json?{}".format(VIRTUAL_RDA_URL, template_id, qs)
    req = req_with_retries(conn, url)
    #req = resolve_if_future(conn.get(url))
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("Could not fetch stats for template/args: {} / {}".format(template_id, kwargs))

def get_rda_graph(conn, graph_id):
    warnings.warn('Graph API is deprecated')
    url = "{}/graph/{}".format(VIRTUAL_RDA_URL, graph_id)
    #req = resolve_if_future(conn.get(url))
    req = req_with_retries(conn, url)
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("No RDA graph found matching id: {}".format(graph_id))


def get_rda_graph_template(conn, template_id):
    # search for template metadata for template ID
    try:
        template_id = _search_for_rda_template(conn, template_id)
    except:
        pass
    url = "{}/template/{}".format(VIRTUAL_RDA_URL, template_id)
    #req = resolve_if_future(conn.get(url))
    req = req_with_retries(conn, url)
    if req.status_code == 200:
        return req.json()
    else:
        raise NotFound("No RDA Template found matching name or id: {}".format(template_id))


def _search_for_rda_template(conn, template_name):
    """
    Searches for template by name, eventually RDA will have named templates and this method goes away.
    :param conn:
    :param template_name:
    :return:
    """
    url = "{}/template/metadata/search?free-text={}".format(VIRTUAL_RDA_URL, template_name)
    #req = resolve_if_future(conn.get(url))
    req = req_with_retries(conn, url)
    if req.status_code == 200:
        request_json = req.json()
        # make sure list is not empty
        if request_json is not None:
            # make sure list contains 1 entry
            for template in request_json:
                if template.get("name") == template_name:
                    # parse template Id
                    return template.get("templateId")

    # if anything fails, raise as we should always get a template Id
    raise Exception("Error fetching template Id")


def register_rda_graph(conn, rda_graph):
    warnings.warn('Graph API is deprecated')
    url = "{}/graph".format(VIRTUAL_RDA_URL)
    res = resolve_if_future(conn.post(url, json.dumps(rda_graph, sort_keys=True),
                                      headers={'Content-Type': 'application/json'}))
    if res.status_code == 200:
        return res.text
    else:
        raise BadRequest("Problem registering graph: {}".format(res.text))



def get_rda_metadata(conn, rda_id, node='toa_reflectance'):
    warnings.warn('Graph API is deprecated')
    url = VIRTUAL_RDA_URL + "/metadata/{}/{}/metadata.json".format(rda_id, node)
    md_response = req_with_retries(conn, url)
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
    url = VIRTUAL_RDA_URL + "/template/{}/metadata?{}".format(_id, qs)
    md_response = req_with_retries(conn, url)
    if md_response.status_code != 200:
        md_json = md_response.json()
        if 'error' in md_json:
            raise BadRequest("RDA error: {}. RDA Graph: {}".format(md_json['error'], _id))
        raise BadRequest("Problem fetching image metadata: status {} {}, graph_id: {}".format(md_response.status_code, md_response.reason, _id))
    else:
        md_json = md_response.json()
        return {
            "image": md_json["imageMetadata"],
            "georef": md_json.get("imageGeoreferencing", None),
            "rpcs": md_json.get("rpcSensorModel", None)
        }

def create_rda_template(conn, graph):
    r = conn.post("{}/template".format(VIRTUAL_RDA_URL), json=graph).result()
    r.raise_for_status()
    return r.json()['id']

def materialize_template(conn, payload):
    r = conn.post("{}/template/materialize".format(VIRTUAL_RDA_URL), json=payload).result()
    r.raise_for_status()
    return r.json()['jobId']

def materialize_status(conn, job_id):
    r = conn.get("{}/template/materialize/status/{}".format(VIRTUAL_RDA_URL, job_id)).result()
    r.raise_for_status()
    return r.json()['status']
