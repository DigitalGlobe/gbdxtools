from __future__ import print_function
import xml.etree.cElementTree as ET
from string import Template
import os
import os.path
from itertools import product

try:
    xrange
except NameError:
    xrange = range

from gbdxtools.ipe.graph import VIRTUAL_IPE_URL, get_ipe_metadata
from gbdxtools.ipe.util import mkdir_p
from gbdxtools.ipe.error import NotFound

# TODO: this need to be complete
DTLOOKUP = {
    "UNSIGNED_SHORT": "UInt16",
    "UNSIGNED_INT": "UInt16",
    "BYTE": "Byte",
    "FLOAT": "Float32"
}

NODE_DATA_TYPES = {
    "MsSourceImage": "UInt16",
    "MsOrthoImage": "UInt16",
    "MsOrthoImage-pan": "UInt16",
    "Pansharpened": "UInt16",
    "IntegerImage": "UInt16",
    "IntegerImage-pan": "UInt16"
}

IDAHO_CACHE_DIR = os.environ.get("IDAHO_CACHE_DIR", "/tmp/idaho-cache")
if not os.path.exists(IDAHO_CACHE_DIR):
    mkdir_p(IDAHO_CACHE_DIR)


def generate_vrt_template(conn, ipe_id, node, level, num_bands=None):
    meta = get_ipe_metadata(conn, ipe_id, node=node)
    image_md = meta['image']
    if num_bands is None:
        num_bands = image_md["numBands"]
    tfm = meta['georef']
    tile_size_x = image_md['tileXSize']
    tile_size_y = image_md['tileYSize']

    vrt = ET.Element("VRTDataset",
                     {"rasterXSize": str(image_md["imageWidth"]), "rasterYSize": str(image_md["imageHeight"])})
    ET.SubElement(vrt, "SRS").text = tfm["spatialReferenceSystemCode"]
    ET.SubElement(vrt, "GeoTransform").text = ", ".join(map(str, [tfm["translateX"],
                                                                  tfm["scaleX"],
                                                                  tfm["shearX"],
                                                                  tfm["translateY"],
                                                                  tfm["shearY"],
                                                                  tfm["scaleY"]]))

    for i in xrange(num_bands):
        bidx = i + 1
        band = ET.SubElement(vrt, "VRTRasterBand",
                             {"dataType": NODE_DATA_TYPES.get(node, "Float32"), "band": str(bidx)})
        for x, y in product(xrange(image_md['numXTiles']), xrange(image_md['numYTiles'])):
            src = ET.SubElement(band, "ComplexSource")
            ET.SubElement(src,
                          "SourceFilename").text = "{baseurl}/tile/{bucket}/{ipe_graph_id}/{node}/{x}/{y}.tif".format(
                baseurl=VIRTUAL_IPE_URL,
                bucket="idaho-virtual",
                ipe_graph_id=ipe_id,
                node=node,
                x=x,
                y=y) + "$query"
            ET.SubElement(src, "SourceBand").text = str(bidx)
            ET.SubElement(src, "SrcRect", {"xOff": str(image_md["tileXOffset"]), "yOff": str(image_md["tileYOffset"]),
                                           "xSize": str(tile_size_x), "ySize": str(tile_size_y)})
            ET.SubElement(src, "DstRect", {"xOff": str(x * tile_size_x), "yOff": str(y * tile_size_y),
                                           "xSize": str(tile_size_x), "ySize": str(tile_size_y)})

            ET.SubElement(src, "SourceProperties", {"RasterXSize": str(tile_size_x), "RasterYSize": str(tile_size_y),
                                                    "BlockXSize": "256", "BlockYSize": "256",
                                                    "DataType": DTLOOKUP.get(meta["image"]["dataType"], "Float32")})
    return ET.tostring(vrt, 'utf-8')


def vrt_cache_key(idaho_id, node, level):
    return "{idaho_id}/{node}/{level}.vrt.xml".format(idaho_id=idaho_id, node=node, level=str(level))


def get_cached_vrt(idaho_id, node, level):
    cache_key = vrt_cache_key(idaho_id, node, level)
    cache_path = os.path.join(IDAHO_CACHE_DIR, cache_key)
    try:
        d = os.path.dirname(cache_path)
        if not os.path.exists(d):
            mkdir_p(d)
        with open(cache_path) as f:
            f.read()
        return cache_path
    except IOError:
        raise NotFound("VRT template for key '{}' not found in cache".format(cache_key))


def put_cached_vrt(idaho_id, node, level, template):
    try:
        cache_key = vrt_cache_key(idaho_id, node, level)
        cache_path = os.path.join(IDAHO_CACHE_DIR, cache_key)
        d = os.path.dirname(cache_path)
        if not os.path.exists(d):
            mkdir_p(d)
        with open(cache_path, "w") as f:
            f.write(Template(template.decode('utf-8')).substitute(query=""))
        return cache_path
    except Exception as e:
        print("VRT could not be cached", e)
        pass
