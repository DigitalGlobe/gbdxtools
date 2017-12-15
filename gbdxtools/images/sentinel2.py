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

class Sentinel2(IpeImage):
    """
      Dask based access to sentinel2 images backed by IPE Graphs.
    """
    def __new__(cls, prefix, **kwargs):
        options = {
            "product": kwargs.get("product", "sentinel"),
            "spec": kwargs.get("spec", "10m")
        }

        standard_products = cls._build_standard_products(prefix, options["spec"], kwargs.get("proj", None))
        print(standard_products)
        try:
            self = super(Sentinel2, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self._id = prefix
        self._spec = options["spec"]
        self._products = standard_products
        return self

    @property
    def _rgb_bands(self):
        return [2,1,0]

    @property
    def _ndvi_bands(self):
        return [6,3]

    def get_product(self, product):
        return self.__class__(self._id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(prefix, spec, proj):
        sentinel = ipe.SentinelRead(SentinelId=prefix, sentinelProductSpec=spec)
        if proj is not None:
            sentinel = ipe.Reproject(sentinel, **reproject_params(proj))
        return {
            "sentinel": sentinel
        }
