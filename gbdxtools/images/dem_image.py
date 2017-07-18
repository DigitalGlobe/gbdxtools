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


class DemImage(IpeImage):
    """
      Dask based access to IDAHO images via IPE.
    """
    def __new__(cls, **kwargs):
        idaho_id = "dgdem-2016-08-12-f-b193-7aa90f8d11f1"
        options = {
            "proj": kwargs.get("proj", "EPSG:4326")
        }

        standard_products = cls._build_standard_products(idaho_id, options["proj"])
        try:
            self = super(DemImage, cls).__new__(cls, standard_products.get("dem"))
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
        dem = ipe.IdahoRead(bucketName="idaho-dems", imageId=idaho_id, objectStore="S3")
        if proj is not "EPSG:4326":
            dem = ipe.Reproject(dem, **reproject_params(proj))
        return {
            "dem": dem
        }
