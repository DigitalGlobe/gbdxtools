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

class LandsatImage(IpeImage):
    """
      Dask based access to landsat image backed by IPE Graphs.
    """
    def __new__(cls, _id, **kwargs):
        options = {
            "product": kwargs.get("product", "landsat"),
            "spec": kwargs.get("spec", "multispectral")
        }

        standard_products = cls._build_standard_products(_id, options["spec"], kwargs.get("proj", None))
        try:
            self = super(LandsatImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self._id = _id
        self._spec = options["spec"]
        self._products = standard_products
        return self

    @property
    def _rgb_bands(self):
        return [3,2,1]

    @property
    def _ndvi_bands(self):
        return [4,3]

    def get_product(self, product):
        return self.__class__(self._id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(_id, spec, proj):
        landsat = ipe.LandsatRead(landsatId=_id, productSpec=spec)
        if proj is not None:
            landsat = ipe.Reproject(landsat, **reproject_params(proj))
        return {
            "landsat": landsat
        }
