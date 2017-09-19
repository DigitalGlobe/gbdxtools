from __future__ import print_function
import json
from gbdxtools.images.worldview import WVImage
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.util import ortho_params
ipe = Ipe()
from gbdxtools.vectors import Vectors
from shapely import wkt
from shapely.geometry import box

band_types = {
    'MS': 'BGRN',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

class GE01(WVImage):
    def __new__(cls, cat_id, **kwargs):
        options = {
            "band_type": kwargs.get("band_type", "MS"),
            "product": kwargs.get("product", "ortho"),
            "proj": kwargs.get("proj", "EPSG:4326"),
            "pansharpen": kwargs.get("pansharpen", False),
            "gsd": kwargs.get("gsd", None)
        }

        if options["pansharpen"]:
            options["band_type"] = "MS"
            options["product"] = "pansharpened"

        standard_products = cls._build_standard_products(cat_id, options["band_type"], options["proj"], gsd=options["gsd"])
        pan_products = cls._build_standard_products(cat_id, "pan", options["proj"], options["gsd"])
        pan = pan_products['ortho']
        ms = standard_products['ortho']
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

    def plot(self, **kwargs):
        kwargs["blm"] = False
        super(GE01, self).plot(**kwargs)

    @property
    def _rgb_bands(self):
        return [2,1,0]

    @staticmethod
    def _find_parts(cat_id, band_type):
        vectors = Vectors()
        aoi = wkt.dumps(box(-180, -90, 180, 90))
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        return sorted(vectors.query(aoi, query=query), key=lambda x: x['properties']['id']) 

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

