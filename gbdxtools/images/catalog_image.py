"""
GBDX Catalog Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from gbdxtools import WV01, WV02, WV03_SWIR, WV03_VNIR, WV04, LandsatImage, IkonosImage, GE01, QB02, Sentinel2, Sentinel1, Radarsat
from gbdxtools.images.rda_image import RDAImage, GraphMeta
from gbdxtools.rda.error import UnsupportedImageType
from gbdxtools.images.util.image import vector_services_query, can_acomp, is_ordered

from shapely import wkt
from shapely.geometry import box
import json
import types as pytypes


class CatalogImage(object):
    '''Creates an image instance matching the type of the Catalog ID.

    Args:
        catalogID (str): The source catalog ID from the platform catalog.
        proj (str): Optional EPSG projection string for the image in the form of "EPSG:4326"
        dtype (str): The dtype for the returned image (only valid for Worldview). One of: "int8", "int16", "uint16", "int32", "float32", "float64"
        band_type (str): The product spec / band type for the image returned (band_type='MS'|'Pan')
        pansharpen (bool): Whether or not to return a pansharpened image (defaults to False)
        acomp (bool): Perform atmospheric compensation on the image (defaults to False, i.e. Top of Atmosphere value)
        gsd (float): The Ground Sample Distance (GSD) of the image. Must be defined in the same projected units as the image projection.
        dra (bool): Perform Dynamic Range Adjustment (DRA) on the image. DRA will override the dtype and return int8 data.  

    Attributes:
        affine (list): The image affine transformation
        bounds (list): Spatial bounds of the image
        metadata (dict): image metadata
        ntiles (int): the number of tiles composing the image
        nbytes (int): size of the image in bytes
        proj (str): The image projection as EPSG string

    Returns:
        image (ndarray): An image instance - one of IdahoImage, WV02, WV03_VNIR, LandsatImage, IkonosImage
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
    def is_ordered(cls, cat_id):
      """
        Checks to see if a CatalogID has been ordered or not. 

        Args:
          catalogID (str): The catalog ID from the platform catalog.
        Returns:
          ordered (bool): Whether or not the image has been ordered
      """
      return is_ordered(cat_id)

    @classmethod
    def acomp_available(cls, cat_id):
      """
        Checks to see if a CatalogID can be atmos. compensated or not.

        Args:
          catalogID (str): The catalog ID from the platform catalog.
        Returns:
          available (bool): Whether or not the image can be acomp'd
      """
      return can_acomp(cat_id)

    @classmethod
    def _image_by_type(cls, cat_id, **kwargs):
        if cat_id is None:
            try:
                return RDAImage(GraphMeta(**kwargs))
            except KeyError:
                raise ValueError("Catalog Images must be initiated by a Catalog Id or an RDA Graph Id")
        query = "item_type:GBDXCatalogRecord AND (attributes.catalogID.keyword:{} OR id:{})".format(cat_id, cat_id)
        query += " AND NOT item_type:DigitalGlobeAcquisition"
        result = vector_services_query(query, count=1)
        if len(result) == 0:
            raise Exception('Could not find a catalog entry for the given id: {}'.format(cat_id))
        else:
            return cls._image_class(result[0], **kwargs)

    @classmethod
    def _image_class(cls, rec, **kwargs):
        try:
            cat_id = rec['properties']['attributes']['catalogID']
        except:
            cat_id = None
        types = rec['properties']['item_type']
        if 'WV02' in types:
            return WV02(cat_id, **kwargs)
        elif 'WV01' in types:
            return WV01(cat_id, **kwargs)
        elif 'WV03_VNIR' in types:
            return WV03_VNIR(cat_id, **kwargs)
        elif 'WV03_SWIR' in types:
            return WV03_SWIR(cat_id, **kwargs)
        elif 'WV04' in types:
            return WV04(cat_id, **kwargs)
        elif 'Landsat8' in types:
            return LandsatImage(rec['properties']['attributes']['productID'], **kwargs)
        elif 'GE01' in types:
            return GE01(cat_id, **kwargs)
        elif 'IKONOS' in types:
            return IkonosImage(rec, **kwargs)
        elif 'QB02' in types:
            return QB02(cat_id, **kwargs)
        elif 'SENTINEL1' in types:
            return Sentinel1(cat_id, **kwargs)
        elif 'SENTINEL2' in types:
            return Sentinel2(rec['properties']['attributes']['bucketPrefix'], **kwargs)
        elif 'RADARSAT2':
            return Radarsat(rec, **kwargs)
        else:
            raise UnsupportedImageType('Unsupported image type: {}'.format(str(types)))
