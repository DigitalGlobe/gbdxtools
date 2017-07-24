"""
GBDX Catalog Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
from gbdxtools import IdahoImage, WVImage, LandsatImage
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.vectors import Vectors

from shapely import wkt
from shapely.geometry import box

class CatalogImage(IpeImage):
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
            return cls._image_class(result[0]['properties']['item_type'])(cat_id, **kwargs)

    @classmethod
    def _image_class(cls, types):
        if 'IDAHOImage' in types:
            return IdahoImage
        if 'WV02' in types or 'WV03_VNIR' in types:
            return WVImage
        elif 'Landsat8' in types:
            return LandsatImage
        else: 
            raise 'Unsupported image type: {}'.format(str(types))
  
