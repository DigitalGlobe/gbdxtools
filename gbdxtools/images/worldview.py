"""
GBDX Catalog Image Interface.
Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
import json

from gbdxtools.images.drivers import WorldViewDriver, RDADaskImageDriver
from gbdxtools.images.base import RDABaseImage
from gbdxtools import IdahoImage
from gbdxtools.images.util import vector_services_query, vendor_id, band_types
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.error import MissingIdahoImages, AcompUnavailable

ipe = Ipe()


class WorldViewImage(RDABaseImage):
    __Driver__ = WorldViewDriver
    _parts = None

    @property
    def cat_id(self):
        return self.__rda_id__

    @property
    def parts(self):
        if self._parts is None:
            self._parts = [IdahoImage(rec['properties']['attributes']['idahoImageId'],
                                      product=self.options["product"],
                                      proj=self.options["proj"],
                                      bucket=rec['properties']['attributes']['bucketName'],
                                      gsd=self.options["gsd"],
                                      acomp=self.options["acomp"])
                           for rec in self._find_parts(self.cat_id, self.options["band_type"])]
        return self._parts

    @staticmethod
    def _find_parts(cat_id, band_type):
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        _parts = vector_services_query(query)
        if not len(_parts):
            raise MissingIdahoImages('Unable to find IDAHO imagery in the catalog: {}'.format(query))
        _id = vendor_id(_parts[0])
        return [p for p in _parts if vendor_id(p) == _id]

    @classmethod
    def _build_standard_products(cls, cat_id, band_type="MS", proj="EPSG:4326", gsd=None, acomp=False, **kwargs):
        graph = {}
        _parts = cls._find_parts(cat_id, band_type)
        _bucket = _parts[0]['properties']['attributes']['bucketName']
        dn_ops = [ipe.IdahoRead(bucketName=p['properties']['attributes']['bucketName'],
                                imageId=p['properties']['attributes']['idahoImageId'],
                                objectStore="S3") for p in _parts]

        mosaic_params = {"Dest SRS Code": proj}
        if gsd is not None:
            mosaic_params["Requested GSD"] = str(gsd)

        ortho_op = ipe.GeospatialMosaic(*dn_ops, **mosaic_params)
        graph.update({"ortho": ortho_op})

        if cls.__default_options__.get("product") is "toa_reflectance":
            toa = [ipe.Format(ipe.MultiplyConst(ipe.TOAReflectance(dn), constants=json.dumps([10000])), dataType="1") for dn in dn_ops]
            toa_reflectance_op = ipe.Format(ipe.GeospatialMosaic(*toa, **mosaic_params), dataType="4")
            graph.update({"toa_reflectance": toa_reflectance_op})
        if "acomp" in cls.__supported_options__ and acomp:
            if _bucket != 'idaho-images':
                _ops = [ipe.Format(ipe.MultiplyConst(ipe.Acomp(dn), constants=json.dumps([10000])), dataType="1") for dn in dn_ops]
                graph["acomp"] = ipe.Format(ipe.GeospatialMosaic(*_ops, **mosaic_params), dataType="4")
            else:
                raise AcompUnavailable("Cannot apply acomp to this image, data unavailable in bucket: {}".format(_bucket))

        return graph


class WV03_SWIR(WorldViewImage):
    @staticmethod
    def _find_parts(cat_id, band_type):
        query = "item_type:IDAHOImage AND attributes.catalogID:{}".format(cat_id)
        return vector_services_query(query)

class WV03_VNIR(WorldViewImage):
    pass

class WV02(WorldViewImage):
    pass

class WV01(WorldViewImage):
    class WV01Driver(RDADaskImageDriver):
        image_option_support = ["proj", "gsd", "band_type", "product"]
        __image_option_defaults__ = {"band_type": "pan", "product": "ortho"}

    __Driver__ = WV01Driver
