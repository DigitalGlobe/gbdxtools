from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

class LandsatImage(IpeImage):
    """
      Dask based access to landsat image backed by IPE Graphs.
    """
    def __new__(cls, _id, **kwargs):
        options = {
            "product": kwargs.get("product", "landsat"),
            "spec": kwargs.get("spec", "multispectral")
        }

        standard_products = cls._build_standard_products(_id, options["spec"])
        try:
            self = super(LandsatImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self._id = _id
        self._products = standard_products
        return self.aoi(**kwargs)
    
    @property
    def rgb(self):
        return [3,2,1]

    def get_product(self, product):
        return self.__class__(self._id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(_id, spec):
        landsat = ipe.LandsatRead(landsatId=_id, productSpec=spec)
        return {
            "landsat": landsat
        }
