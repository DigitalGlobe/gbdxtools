from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.util import ortho_params
ipe = Ipe()

class IkonosImage(IpeImage):
    """
      Dask based access to ikonos images backed by IPE Graphs.
    """
    def __new__(cls, prefix, bucket='ikonos-product', **kwargs):
        options = {
            "product": kwargs.get("product", "ikonos"),
            "spec": kwargs.get("spec", "multispectral")
        }

        standard_products = cls._build_standard_products(bucket, prefix, options["spec"], kwargs.get("proj", None))
        try:
            self = super(IkonosImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self._bucket = bucket
        self._prefix = prefix
        self._spec = options["spec"]
        self._products = standard_products
        return self

    def get_product(self, product):
        return self.__class__(self._bucket, self._prefix, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(bucket, prefix, spec, proj):
        ikonos = ipe.IkonosRead(path="{}/{}/{}_0000000:{}".format(bucket, prefix, prefix, spec))
        ikonos = ipe.Orthorectify(ikonos, **ortho_params(proj))
        return {
            "ikonos": ikonos
        }
