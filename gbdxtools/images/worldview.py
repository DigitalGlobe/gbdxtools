"""
GBDX Catalog Image Interface.
Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
import json

from gbdxtools import IdahoImage
from gbdxtools.ipe.util import calc_toa_gain_offset
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.vectors import Vectors
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.error import MissingIdahoImages, AcompUnavailable

from shapely import wkt
from shapely.geometry import box

import requests

ipe = Ipe()

band_types = {
    'MS': 'WORLDVIEW_8_BAND',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

class WVImage(IpeImage):
    _parts = None

    def __new__(cls, cat_id, **kwargs):
        options = {
            "band_type": kwargs.get("band_type", "MS"),
            "product": kwargs.get("product", "toa_reflectance"),
            "proj": kwargs.get("proj", "EPSG:4326"),
            "pansharpen": kwargs.get("pansharpen", False),
            "gsd": kwargs.get("gsd", None),
            "acomp": kwargs.get("acomp", False)
        }

        if options["acomp"]:
            options["product"] = "acomp"

        if options["pansharpen"]:
            options["band_type"] = "MS"
            options["product"] = "pansharpened"

        standard_products = cls._build_standard_products(cat_id,
                                                         options["band_type"],
                                                         options["proj"],
                                                         gsd=options["gsd"],
                                                         acomp=options["acomp"])
        pan_products = cls._build_standard_products(cat_id, "pan", options["proj"], gsd=options["gsd"], acomp=options["acomp"])
        pan = pan_products['acomp'] if options["acomp"] else pan_products['toa_reflectance']
        ms = standard_products['acomp'] if options["acomp"] else standard_products['toa_reflectance']
        standard_products["pansharpened"] = ipe.LocallyProjectivePanSharpen(ms, pan)

        try:
            self = super(WVImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self.cat_id = cat_id
        self._products = standard_products
        self.options = options
        return self

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

    def get_product(self, product):
        return self.__class__(self.cat_id, proj=self.proj, product=product)

    @staticmethod
    def _find_parts(cat_id, band_type):
        def vendor_id(rec):
          _id = rec['properties']['attributes']['vendorDatasetIdentifier']
          return _id.split(':')[1].split('_')[0]

        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        _parts = sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id'])
        if not len(_parts):
            raise MissingIdahoImages('Unable to find IDAHO imagery in the catalog: {}'.format(query))
        _id = vendor_id(_parts[0])
        return [p for p in _parts if vendor_id(p) == _id]

    @classmethod
    def _build_standard_products(cls, cat_id, band_type, proj, gsd=None, acomp=False):
        _parts = cls._find_parts(cat_id, band_type)
        _bucket = _parts[0]['properties']['attributes']['bucketName']

        dn_ops = [ipe.IdahoRead(bucketName=p['properties']['attributes']['bucketName'], imageId=p['properties']['attributes']['idahoImageId'],
                                objectStore="S3") for p in _parts]

        mosaic_params = {"Dest SRS Code": proj}
        if gsd is not None:
            mosaic_params["Requested GSD"] = str(gsd)

        ortho_op = ipe.GeospatialMosaic(*dn_ops, **mosaic_params)

        toa = [ipe.Format(ipe.MultiplyConst(ipe.TOAReflectance(dn), constants=json.dumps([10000])), dataType="1") for dn in dn_ops]
        toa_reflectance_op = ipe.Format(ipe.GeospatialMosaic(*toa, **mosaic_params), dataType="4")

        graph = {"ortho": ortho_op, "toa_reflectance": toa_reflectance_op}

        if acomp:
            if _bucket != 'idaho-images':
                _ops = [ipe.Format(ipe.MultiplyConst(ipe.Acomp(dn), constants=json.dumps([10000])), dataType="1") for dn in dn_ops]
                graph["acomp"] = ipe.Format(ipe.GeospatialMosaic(*_ops, **mosaic_params), dataType="4")
            else:
                raise AcompUnavailable("Cannot apply acomp to this image, data unavailable in bucket: {}".format(_bucket))

        return graph

class WV03_SWIR(WVImage):
    def __new__(cls, cat_id, **kwargs):
        return super(WV03_SWIR, cls).__new__(cls, cat_id, **kwargs)

    @staticmethod
    def _find_parts(cat_id, band_type):
        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{}".format(cat_id)
        return sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id'])

class WV03_VNIR(WVImage):
    def __new__(cls, cat_id, **kwargs):
        return super(WV03_VNIR, cls).__new__(cls, cat_id, **kwargs)


class WV02(WVImage):
    def __new__(cls, cat_id, **kwargs):
        return super(WV02, cls).__new__(cls, cat_id, **kwargs)

class WV01(WVImage):
    def __new__(cls, cat_id, **kwargs):
        options = {
            "band_type": "pan",
            "product": kwargs.get("product", "ortho"),
            "proj": kwargs.get("proj", "EPSG:4326"),
            "gsd": kwargs.get("gsd", None)
        }

        standard_products = cls._build_standard_products(cat_id, options["band_type"], options["proj"], gsd=options["gsd"])
        try:
            self = super(WVImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self.cat_id = cat_id
        self._products = standard_products
        self.options = options
        return self

    @classmethod
    def _build_standard_products(cls, cat_id, band_type, proj, gsd=None):
        _parts = cls._find_parts(cat_id, band_type)
        _id = _parts[0]['properties']['attributes']['idahoImageId']
        dn_ops = [ipe.IdahoRead(bucketName=p['properties']['attributes']['bucketName'], imageId=p['properties']['attributes']['idahoImageId'],
                                objectStore="S3") for p in _parts]
        mosaic_params = {"Dest SRS Code": proj}
        if gsd is not None:
            mosaic_params["Requested GSD"] = str(gsd)
        ortho_op = ipe.GeospatialMosaic(*dn_ops, **mosaic_params)

        return {"ortho": ortho_op}
