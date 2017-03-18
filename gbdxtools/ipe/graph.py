import json
import requests

#VIRTUAL_IPE_URL = "http://virtualidaho-env.us-east-1.elasticbeanstalk.com/v1"
VIRTUAL_IPE_URL = "http://idaho-api-lb-1256760776.us-east-1.elb.amazonaws.com/v1"

def register_ipe_graph(conn, ipe_graph):
    url = "{}/graph".format(VIRTUAL_IPE_URL)
    return requests.post(url, json.dumps(ipe_graph), headers={"Content-Type": "application/json"}).text


def get_ipe_metadata(conn, ipe_id, node='toa_reflectance'):
    meta = {}
    meta['image'] = requests.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/image.json".format(ipe_id, node)).json()
    meta['georef'] = requests.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/georeferencing.json".format(ipe_id, node)).json()
    return meta
