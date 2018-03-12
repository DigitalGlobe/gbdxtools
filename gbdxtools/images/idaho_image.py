from __future__ import print_function
import requests
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.util import calc_toa_gain_offset, ortho_params
from gbdxtools.ipe.interface import Ipe
from gbdxtools.vectors import Vectors

from shapely import wkt
from shapely.geometry import box

ipe = Ipe()

class IdahoImage(IpeImage):
    """
      Dask based access to IDAHO images via IPE.
    """
    def __new__(cls, idaho_id, **kwargs):
        options = {
            "proj": kwargs.get("proj", "EPSG:4326"),
            "product": kwargs.get("product", "toa_reflectance"),
            "gsd": kwargs.get("gsd", None),
            "bucket": kwargs.get("bucket", None),
            "acomp": kwargs.get("acomp", False)
        }
        if options["acomp"] and options["bucket"] != "idaho-images":
            options["product"] = "acomp"
        else:
            options["product"] = "toa_reflectance" 

        standard_products = cls._build_standard_products(idaho_id, options["proj"], bucket=options["bucket"], gsd=options["gsd"], acomp=options["acomp"])
        try:
            self = super(IdahoImage, cls).__new__(cls, standard_products.get(options["product"], "toa_reflectance"))
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self.options = options
        self.idaho_id = idaho_id
        self._products = standard_products
        return self

    def get_product(self, product):
        return self.__class__(self.idaho_id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(idaho_id, proj, bucket=None, gsd=None, acomp=False):
        if bucket is None:
            vectors = Vectors()
            aoi = wkt.dumps(box(-180, -90, 180, 90))
            query = "item_type:IDAHOImage AND id:{}".format(idaho_id)
            result = vectors.query(aoi, query=query)
            if len(result):
                bucket = result[0]["properties"]["attributes"]["tileBucketName"]

        dn_op = ipe.IdahoRead(bucketName=bucket, imageId=idaho_id, objectStore="S3")
        params = ortho_params(proj, gsd=gsd)

        graph = {
            "1b": dn_op,
            "ortho": ipe.Orthorectify(dn_op, **params),
            "acomp": ipe.Format(ipe.Orthorectify(ipe.Acomp(dn_op), **params), dataType="4"),
            "toa_reflectance": ipe.Format(ipe.Orthorectify(ipe.TOAReflectance(dn_op), **params), dataType="4")
        }

        return graph
