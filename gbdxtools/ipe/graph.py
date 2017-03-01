import uuid
import json
import warnings

import requests
from shapely.geometry import Polygon, mapping

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

from gbdxtools.ipe.util import calc_toa_gain_offset, timeit
from gbdxtools.ipe.error import NotFound

VIRTUAL_IPE_URL = "http://virtualidaho-env.us-east-1.elasticbeanstalk.com/v1"
NAMESPACE_UUID = uuid.NAMESPACE_DNS

def register_ipe_graph(ipe_graph):
    url = "{}/graph".format(VIRTUAL_IPE_URL)
    return requests.post(url, json.dumps(ipe_graph), headers={"Content-Type": "application/json"}).text


def create_ipe_graph(idaho_id, meta, pan_md=None):
    pan_props = pan_md["properties"] if pan_md is not None else None
    ipe_graph = json.dumps(generate_ipe_graph(idaho_id, meta["properties"], pan_md=pan_props))
    try:
        url = "{}/graph".format(VIRTUAL_IPE_URL)
        ipe_id = requests.post(url, ipe_graph, headers={"Content-Type": "application/json"}).text
    except Exception:
        raise NotFound("Unable to create IPE graph for Idaho Id: {}".format(idaho_id))
    return ipe_id


def generate_ipe_graph(idaho_id, meta, bucket="idaho-images", suffix="", pan_md=None):
    gains_offsets = calc_toa_gain_offset(meta)
    radiance_scales = [e[0] for e in gains_offsets]
    reflectance_scales = [e[1] for e in gains_offsets]
    radiance_offsets = [e[2] for e in gains_offsets]
    rec = {
      "id": str(uuid.uuid4()),
      "edges": [
        {
          "id": str(uuid.uuid5(NAMESPACE_UUID, "MsSourceImage-MsOrthoImage{}".format(suffix))),
          "index": 1,
            "source": "MsSourceImage{}".format(suffix),
            "destination": "MsOrthoImage{}".format(suffix)
        },
        {
          "id": str(uuid.uuid5(NAMESPACE_UUID, "MsOrthoImage-MsFloatImage{}".format(suffix))),
            "index": 1,
            "source": "MsOrthoImage{}".format(suffix),
            "destination": "MsFloatImage{}".format(suffix)
        },
        {
          "id": str(uuid.uuid5(NAMESPACE_UUID, "MsFloatImage-RadianceGain{}".format(suffix))),
            "index": 1,
            "source": "MsFloatImage{}".format(suffix),
            "destination": "RadianceGain{}".format(suffix)
        },
        {
          "id": str(uuid.uuid5(NAMESPACE_UUID, "RadianceGain-TOARadiance{}".format(suffix))),
          "index": 1,
            "source": "RadianceGain{}".format(suffix),
            "destination": "TOARadiance{}".format(suffix)
        },
        {
          "id": str(uuid.uuid5(NAMESPACE_UUID, "TOARadiance-TOAReflectance{}".format(suffix))),
          "index": 1,
            "source": "TOARadiance{}".format(suffix),
            "destination": "TOAReflectance{}".format(suffix)
        }
      ],
      "nodes": [
        {
          "id": "MsSourceImage{}".format(suffix),
          "operator": "IdahoRead",
          "parameters": {
            "bucketName": bucket,
            "imageId": idaho_id,
            "objectStore": "S3"
          }
        },
        {
            "id": "MsOrthoImage{}".format(suffix),
            "operator": "GridOrthorectify"
        },
        {
            "id": "MsFloatImage{}".format(suffix),
            "operator": "Format",
            "parameters": {
                "dataType": "4"
            }
        },
        {
            "id": "RadianceGain{}".format(suffix),
            "operator": "MultiplyConst",
            "parameters": {
                "constants": json.dumps(radiance_scales)
            }
        },
        {
            "id": "TOARadiance{}".format(suffix),
            "operator": "AddConst",
            "parameters": {
                "constants": json.dumps(radiance_offsets)
            }
        },
        {
            "id": "TOAReflectance{}".format(suffix),
            "operator": "MultiplyConst",
            "parameters": {
                "constants": json.dumps(reflectance_scales)
            }
        }
      ]
    }

    if pan_md is not None:
        pan_id = pan_md["image"]["imageId"]
        pan_graph = generate_ipe_graph(pan_id, pan_md, suffix="-pan")
        rec["nodes"].extend(pan_graph["nodes"])
        rec["edges"].extend(pan_graph["edges"])
        rec["nodes"].extend([{
            "id": "Pansharpened",
            "operator": "LocallyProjectivePanSharpen"
        },
        {
            "id": "ScaleForPansharpening",
            "operator": "MultiplyConst",
            "parameters": {
                "constants": json.dumps([1000]*8)
            }
        },
        {
            "id": "ScaleForPansharpening-pan",
            "operator": "MultiplyConst",
            "parameters": {
                "constants": json.dumps([1000])
            }
        },
        {
            "id": "IntegerImage",
            "operator": "Format",
            "parameters": {
                "dataType": "1"
            }

        },
        {
            "id": "IntegerImage-pan",
            "operator": "Format",
            "parameters": {
                "dataType": "1"
            }
        }])

        rec["edges"].extend([{
            "id": str(uuid.uuid5(NAMESPACE_UUID, "TOAReflectance-ScaleForPansharpening")),
            "index": 1,
            "source": "TOAReflectance",
            "destination": "ScaleForPansharpening"
        },
        {
            "id": str(uuid.uuid5(NAMESPACE_UUID, "TOAReflectance-pan-ScaleForPansharpening-pan")),
            "index": 1,
            "source": "TOAReflectance-pan",
            "destination": "ScaleForPansharpening-pan"
        },
        {
            "id": str(uuid.uuid5(NAMESPACE_UUID, "ScaleForPansharpening-IntegerImage")),
            "index": 1,
            "source": "ScaleForPansharpening",
            "destination": "IntegerImage"
        },
        {
            "id": str(uuid.uuid5(NAMESPACE_UUID, "ScaleForPansharpening-pan-IntegerImage-pan")),
            "index": 1,
            "source": "ScaleForPansharpening-pan",
            "destination": "IntegerImage-pan"
        },
        {
            "id": str(uuid.uuid5(NAMESPACE_UUID, "IntegerImage-Pansharpened")),
            "index": 1,
            "source": "IntegerImage",
            "destination": "Pansharpened"
        },
        {
            "id": str(uuid.uuid5(NAMESPACE_UUID, "IntegerImage-pan-Pansharpened")),
            "index": 2,
            "source": "IntegerImage-pan",
            "destination": "Pansharpened"
        }])
    return rec

def get_ipe_metadata(ipe_id, node='TOAReflectance'):
    meta = {}
    meta['image'] = requests.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/image.json".format(ipe_id, node)).json()
    meta['georef'] = requests.get(VIRTUAL_IPE_URL + "/metadata/idaho-virtual/{}/{}/georeferencing.json".format(ipe_id, node)).json()
    return meta
