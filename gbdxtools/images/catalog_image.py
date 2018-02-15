"""
GBDX Catalog Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
from gbdxtools import WV01, WV02, WV03_SWIR, WV03_VNIR, LandsatImage, IkonosImage, GE01, QB02, Sentinel2
from gbdxtools.images.ipe_image import IpeImage, GraphMeta
from gbdxtools.vectors import Vectors
from gbdxtools.ipe.error import UnsupportedImageType

from shapely import wkt
from shapely.geometry import box
import json
import types as pytypes

class CatalogImage(object):
    '''Creates an image instance matching the type of the Catalog ID.

    Args:
        catalogID (str): The source catalog ID from the platform catalog.
        proj (str): Optional EPSG projection string for the image in the form of "EPSG:4326"
        product (str): One of "ortho" or "toa_reflectance"
        band_type (str): The product spec / band type for the image returned (band_type='MS'|'Pan')
        pansharpen: Whether or not to return a pansharpened image (defaults to False)
        acomp: Perform atmos. compensation on the image

    Returns:
        image (ndarray): An image instance - one of IdahoImage, WV02, WV03_VNIR, LandsatImage, IkonosImage

    Properties:
        :affine: The image affine transformation
        :bounds: Spatial bounds of the image
        :proj: The image projection
    '''
    def __new__(cls, cat_id=None, **kwargs):
        inst = cls._image_by_type(cat_id, **kwargs)
        fplg = kwargs.get("fetch_plugin")
        if fplg:
            for attrname in dir(fplg):
                if isinstance(getattr(fplg, attrname), pytypes.MethodType) and attrname in ("__dask_optimize__", "__fetch__"):
                    setattr(inst, attrname, getattr(fplg, attrname))
        return inst

    @classmethod
    def _image_by_type(cls, cat_id, **kwargs):
        if cat_id is None:
            try:
                return IpeImage(GraphMeta(kwargs["graph_id"], **kwargs))
            except KeyError:
                raise ValueError("Catalog Images must be initiated by a Catalog Id or an RDA Graph Id")
        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:GBDXCatalogRecord AND attributes.catalogID:{}".format(cat_id)
        query += " AND NOT item_type:IDAHOImage AND NOT item_type:DigitalGlobeAcquisition"
        result = vectors.query(aoi, query=query, count=1)
        if len(result) == 0:
            raise Exception('Could not find a catalog entry for the given id: {}'.format(cat_id))
        else:
            return cls._image_class(cat_id, result[0], **kwargs)

    @classmethod
    def _image_class(cls, cat_id, rec, **kwargs):
        types = rec['properties']['item_type']
        if 'WV02' in types:
            return WV02(cat_id, **kwargs)
        elif 'WV01' in types:
            return WV01(cat_id, **kwargs)
        elif 'WV03_VNIR' in types:
            return WV03_VNIR(cat_id, **kwargs)
        elif 'WV03_SWIR' in types:
            return WV03_SWIR(cat_id, **kwargs)
        elif 'Landsat8' in types:
            return LandsatImage(cat_id, **kwargs)
        elif 'GE01' in types:
            return GE01(cat_id, **kwargs)
        elif 'IKONOS' in types:
            return IkonosImage(rec, **kwargs)
        elif 'QB02' in types:
            return QB02(cat_id, **kwargs)
        elif 'SENTINEL2' in types:
            return Sentinel2(rec['properties']['attributes']['bucketPrefix'], **kwargs)
        else:
            raise UnsupportedImageType('Unsupported image type: {}'.format(str(types)))
