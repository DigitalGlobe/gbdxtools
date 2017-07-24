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
            "pansharpen": kwargs.get("pansharpen", False)
        }

        if options["pansharpen"]:
            options["band_type"] = "MS"
            options["product"] = "pansharpened"

        standard_products = cls._build_standard_products(cat_id, options["band_type"], options["proj"])
        pan_products = cls._build_standard_products(cat_id, "pan", options["proj"])
        pan = ipe.Format(ipe.MultiplyConst(pan_products['toa_reflectance'], constants=json.dumps([1000])), dataType="1")
        ms = ipe.Format(ipe.MultiplyConst(standard_products['toa_reflectance'],
                                          constants=json.dumps([1000]*8)), dataType="1")
        standard_products["pansharpened"] = ipe.LocallyProjectivePanSharpen(ms, pan)

        try:
            self = super(CatalogImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self.cat_id = cat_id
        self._products = standard_products
        self.options = options
        return self.aoi(**kwargs)

    @property
    def parts(self):
        if self._parts is None:
            self._parts = [IdahoImage(rec['properties']['attributes']['idahoImageId'],
                                      product=self.options["product"], proj=self.options["proj"])
                           for rec in self._find_parts(self.cat_id, self.options["band_type"])]
        return self._parts

    def get_product(self, product):
        return self.__class__(self.idaho_id, proj=self.proj, product=product)

    @staticmethod
    def _find_parts(cat_id, band_type):
        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        return sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id'])

    @classmethod
    def _build_standard_products(cls, cat_id, band_type, proj):
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
        ortho_op = ipe.GeospatialMosaic(*dn_ops, **{"Dest SRS Code": proj})

        toa_reflectance_op = ipe.MultiplyConst(
            ipe.AddConst(
                ipe.MultiplyConst(
                    ipe.Format(ortho_op, dataType="4"),
                    constants=radiance_scales),
                constants=radiance_offsets),
            constants=reflectance_scales)

        return {"ortho": ortho_op, "toa_reflectance": toa_reflectance_op}
