"""
GBDX Catalog Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
from gbdxtools import IdahoImage, WV02, WV03_VNIR, LandsatImage, IkonosImage
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.vectors import Vectors
from gbdxtools.ipe.error import UnsupportedImageType

from shapely import wkt
from shapely.geometry import box

class CatalogImage(object):
    def __new__(cls, cat_id, **kwargs):
        return cls._image_by_type(cat_id, **kwargs)

    @classmethod
    def _image_by_type(cls, cat_id, **kwargs):
        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:GBDXCatalogRecord AND id:{}".format(cat_id)
        result = vectors.query(aoi, query=query, count=1)
        if len(result) == 0:
            raise 'Could not find a catalog entry for the given id: {}'.format(cat_id)
        else:
            return cls._image_class(cat_id, result[0], **kwargs)

    @classmethod
    def _image_class(cls, cat_id, rec, **kwargs):
        types = rec['properties']['item_type']
        if 'IDAHOImage' in types:
            return IdahoImage(cat_id, **kwargs)
        elif 'WV02' in types:
            return WV02(cat_id, **kwargs)
        elif 'WV03_VNIR' in types:
            return WV03_VNIR(cat_id, **kwargs)
        elif 'Landsat8' in types:
            return LandsatImage(cat_id, **kwargs)
        #elif 'IKONOS' in types:
        #    return IkonosImage(rec['properties']['attributes']['prefix'], bucket=rec['properties']['attributes']['bucket_name'], **kwargs)
        else: 
            raise UnsupportedImageType('Unsupported image type: {}'.format(str(types)))
