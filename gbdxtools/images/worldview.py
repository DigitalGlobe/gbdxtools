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
from gbdxtools.ipe.error import MissingMetadata, MissingIdahoImages

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


def rda_factory(klass, _id, **kwargs):
    klass = (klassfactory(_id, **kwargs))
    prod = klass._build_standard_products(_id, **options)
    return klass(DaskMeta._make([prod.dask, prod.name, prod.chunks, prod.dtype, prod.shape]), **kwargs)

rda_options = ["band_type",
               "product",
               "proj",
               "pansharpen",
               "gsd",
               "acomp",
               "bucket"
               ]


class BaseImageFactory(object):
    defaults = {"band_type": "MS",
                "product": "toa_reflectance",
                "proj": "EPSG:4326",
                "pansharpen": False,
                "gsd": None,
                "acomp": False,
                "bucket": "idaho-images"
                }
    def __init__(self, _id, options):
        for attrname in rda_options:
            attrval = options.get(attrname, self.defaults[attrname])
            setattr(self, attrname, attrval)
        self._id = _id

    @property
    def options(self):
        return {attrname: getattr(self, attrname) for attrname in rda_options}

    def get_product(self, product):
        return self.__class__(self._id, proj=self.proj, product=product)

    def build_standard_products(self):
        return self._build_standard_products(self._id, **self.options)


class WVImageFactory(BaseImageFactory):
    _parts = None

    def __init__(self, _id, options):
        options = self._preprocess(options)
        super(WVImageFactory, self).__init__(_id, options)

    @property
    def cat_id(self):
        return self._id

    @classmethod
    def _preprocess(cls, options):
        if options.get("acomp"):
            options["product"] = "acomp"
            if options["pansharpen"]:
                options["band_type"] = "MS"
                options["product"] = "pansharpened"
        return options


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
            self = super(WVImage, cls).__new__(cls, standard_products[options["product"]], **kwargs)
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
        toa_reflectance_op = ipe.GeospatialMosaic(*toa, **mosaic_params)

        if acomp and _bucket != 'idaho-images':
            _ops = [ipe.Format(ipe.MultiplyConst(ipe.Acomp(dn), constants=json.dumps([10000])), dataType="1") for dn in dn_ops]
            acomp_op = ipe.GeospatialMosaic(*_ops, **mosaic_params)
        else:
            acomp_op = toa_reflectance_op

        return {"ortho": ortho_op, "toa_reflectance": toa_reflectance_op, "acomp": acomp_op}

class WV03_SWIR(WVImage):
    @staticmethod
    def _find_parts(cat_id, band_type):
        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{}".format(cat_id)
        return sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id'])

class WV03_VNIR(WVImage):
    pass

class WV02(WVImage):
    pass

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
