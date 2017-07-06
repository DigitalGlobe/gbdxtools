"""
GBDX Catalog Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
import xml.etree.cElementTree as ET
from contextlib import contextmanager
from collections import defaultdict
import os
import json
import uuid

from shapely import wkt
from shapely.geometry import box, shape, mapping
import requests

from gbdxtools.auth import Auth
from gbdxtools.ipe.util import calc_toa_gain_offset, ortho_params
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.images.meta import DaskImage
from gbdxtools.vectors import Vectors
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

band_types = {
  'MS': 'WORLDVIEW_8_BAND',
  'Panchromatic': 'PAN',
  'Pan': 'PAN',
  'pan': 'PAN'
}


class CatalogImage(IpeImage):
    def __new__(cls, cat_id, **kwargs):
        options = {
            "band_type": kwargs.get("band_type", "MS"),
            "product": kwargs.get("product", "toa_reflectance"),
            "proj": kwargs.get("proj", "epsg:4326")
        }

        standard_products = cls._build_standard_products(cat_id, options["band_type"], options["proj"])
        print(standard_products.keys())
        try:
            self = super(CatalogImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self.cat_id = cat_id
        self._products = standard_products
        return self

    def get_product(self, product):
        return self.__class__(self.idaho_id, proj=self.proj, product=product)

    @staticmethod
    def _find_parts(cat_id, band_type, _vectors=Vectors()):
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{} AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        return _vectors.query(aoi, query=query)


    @classmethod
    def _build_standard_products(cls, cat_id, band_type, proj):
        selected = defaultdict(list)
        for p in cls._find_parts(cat_id, band_type):
            _id = p['properties']['attributes']['idahoImageId']
            dn_op = ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3")
            ortho_op = ipe.Orthorectify(dn_op, **ortho_params(proj))
            # TODO: Switch to direct metadata access (ie remove this block)
            idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(_id)).json()
            meta = idaho_md["properties"]
            gains_offsets = calc_toa_gain_offset(meta)
            radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
            # ---

            toa_reflectance_op = ipe.MultiplyConst(
                ipe.AddConst(
                    ipe.MultiplyConst(
                        ipe.Format(ortho_op, dataType="4"),
                        constants=radiance_scales),
                    constants=radiance_offsets),
                constants=reflectance_scales)

            selected["dn"].append(dn_op)
            selected["ortho"].append(ortho_op)
            selected["toa_reflectance"].append(toa_reflectance_op)

        return {key:ipe.GeospatialMosaic(*ops) for key, ops in selected.iteritems()}
