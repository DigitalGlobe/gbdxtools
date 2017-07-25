from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

def reproject_params(proj):
    _params = {}
    if proj is not None:
        _params["Source SRS Code"] = "EPSG:4326"
        _params["Source pixel-to-world transform"] = None
        _params["Dest SRS Code"] = proj
        _params["Dest pixel-to-world transform"] = None
    return _params

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
        self._bucket = _bucket
        self._prefix = _prefix
        self._spec = options["spec"]
        self._products = standard_products
        return self.aoi(**kwargs)

    def get_product(self, product):
        return self.__class__(self._bucket, self._prefix, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(bucket, prefix, spec, proj):
        print("{}/{}/{}_0000000".format(bucket, prefix, prefix), spec)
        ikonos = ipe.IkonosRead(path="ikonos-product/po_1298279/po_1298279_0000000:multispectral")
        #ikonos = ipe.IkonosRead(path="{}/{}/{}_0000000:{}".format(bucket, prefix, prefix, spec))
        #if proj is not None:
        #    ikonos = ipe.Reproject(ikonos, **reproject_params(proj))
        #print(ikonos.graph())
        return {
            "ikonos": ikonos
        }
