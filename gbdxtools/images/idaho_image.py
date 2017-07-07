from __future__ import print_function
import requests
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.util import calc_toa_gain_offset, ortho_params
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

class IdahoImage(IpeImage):
    """
      Dask based access to IDAHO images via IPE.
    """
    def __new__(cls, idaho_id, **kwargs):
        options = {
            "proj": kwargs.get("proj", "EPSG:4326"),
            "product": kwargs.get("product", "toa_reflectance")
        }

        standard_products = cls._build_standard_products(idaho_id, options["proj"])
        try:
            self = super(IdahoImage, cls).__new__(cls, standard_products.get(options["product"], "toa_reflectance"))
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self.idaho_id = idaho_id
        self._products = standard_products
        return self.aoi(**kwargs)

    def get_product(self, product):
        return self.__class__(self.idaho_id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(idaho_id, proj):
        dn_op = ipe.IdahoRead(bucketName="idaho-images", imageId=idaho_id, objectStore="S3")
        ortho_op = ipe.Orthorectify(dn_op,  **ortho_params(proj))

        # TODO: Switch to direct metadata access (ie remove this block)
        idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(idaho_id)).json()
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

        return {
            "dn": dn_op,
            "ortho": ortho_op,
            "toa_reflectance": toa_reflectance_op
        }
