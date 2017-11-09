"""
GBDX Catalog Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
import json

from shapely import wkt
from shapely.geometry import box

import requests

from gbdxtools import IdahoImage
from gbdxtools.ipe.util import calc_toa_gain_offset
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.vectors import Vectors
from gbdxtools.ipe.interface import Ipe
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
            "gsd": kwargs.get("gsd", None)
        }

        if options["pansharpen"]:
            options["band_type"] = "MS"
            options["product"] = "pansharpened"

        standard_products = cls._build_standard_products(cat_id, options["band_type"], options["proj"], gsd=options["gsd"])
        pan_products = cls._build_standard_products(cat_id, "pan", options["proj"], options["gsd"])
        pan = ipe.Format(ipe.MultiplyConst(pan_products['toa_reflectance'], constants=json.dumps([1000])), dataType="1")
        ms = ipe.Format(ipe.MultiplyConst(standard_products['toa_reflectance'],
                                          constants=json.dumps([1000]*8)), dataType="1")
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
                                      product=self.options["product"], proj=self.options["proj"], gsd=self.options["gsd"])
                           for rec in self._find_parts(self.cat_id, self.options["band_type"])]
        return self._parts

    def get_product(self, product):
        return self.__class__(self.cat_id, proj=self.proj, product=product)

    @staticmethod
    def _find_parts(cat_id, band_type):
        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        return sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id'])

    @classmethod
    def _build_standard_products(cls, cat_id, band_type, proj, gsd=None):
        # TODO: Switch to direct metadata access (ie remove this block)
        _parts = cls._find_parts(cat_id, band_type)
        _id = _parts[0]['properties']['attributes']['idahoImageId']
        idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(_id)).json()
        meta = idaho_md["properties"]
        gains_offsets = calc_toa_gain_offset(meta)
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
        # ---

        dn_ops = [ipe.IdahoRead(bucketName="idaho-images", imageId=p['properties']['attributes']['idahoImageId'],
                                objectStore="S3") for p in _parts]
        mosaic_params = {"Dest SRS Code": proj}
        if gsd is not None:
            mosaic_params["Requested GSD"] = str(gsd)
        ortho_op = ipe.GeospatialMosaic(*dn_ops, **mosaic_params)

        radiance_op = ipe.AddConst(
            ipe.MultiplyConst(
                ipe.Format(ortho_op, dataType="4"),
                constants=radiance_scales),
            constants=radiance_offsets)

        toa_reflectance_op = ipe.MultiplyConst(radiance_op,
                                               constants=reflectance_scales)

        return {"ortho": ortho_op, "toa_reflectance": toa_reflectance_op, "radiance": radiance_op}


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
        dn_ops = [ipe.IdahoRead(bucketName="idaho-images", imageId=p['properties']['attributes']['idahoImageId'],
                                objectStore="S3") for p in _parts]
        mosaic_params = {"Dest SRS Code": proj}
        if gsd is not None:
            mosaic_params["Requested GSD"] = str(gsd)
        ortho_op = ipe.GeospatialMosaic(*dn_ops, **mosaic_params)

        return {"ortho": ortho_op}
