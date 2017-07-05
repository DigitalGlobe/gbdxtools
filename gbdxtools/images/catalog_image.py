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


class CatalogImage(DaskImage):
    def __new__(cls, cat_id, **kwargs):
        options = {
            "band_type": kwargs.get("band_type", "MS"),
            "product": kwargs.get("product", "toa_reflectance"),
            "proj": kwargs.get("proj", "epsg:4326")
        }

    @staticmethod
    def _find_parts(cat_id, band_type):
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{} AND "




    @classmethod
    def _build_standard_products(cls, cat_id, band_type, proj):
        parts = cls.fetch_parts(cat_id)
        for part in self.metadata['parts']:
            for k, p in part.items():
                if k == band_types[band_type]:
                    _id = p['properties']['idahoImageId']
                    dn_op = ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3")
                    ortho_op = ipe.Orthorectify(dn_op) # , **ortho_params(proj))

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

    @staticmethod
    def _query_vectors(query, aoi=None):
        if aoi is None:
            aoi = wkt.dumps(box(-180, -90, 180, 90))
        try:
            return Vectors().query(aoi, query=query)
        except:
            raise Exception('Unable to query for image properties, the service may be currently down.')

    @staticmethod
    def fetch_parts(cat_id):
        meta = {}
        query = 'item_type:IDAHOImage AND attributes.catalogID:{}'.format(cat_id)
        results = CatalogImage._query_vectors(query)
        grouped = defaultdict(list)
        for idaho in results:
            vid = idaho['properties']['attributes']['vendorDatasetIdentifier']
            grouped[vid].append(idaho)

        meta['parts'] = []
        for key, parts in grouped.items():
            part = {}
            for p in parts:
                attrs = p['properties']['attributes']
                part[attrs['colorInterpretation']] = {'properties': attrs, 'geometry': shape(p['geometry'])}
            meta['parts'].append(part)

        return meta
