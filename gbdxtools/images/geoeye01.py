from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.util import ortho_params
ipe = Ipe()

class GE01(IpeImage):
    """
      Dask based access to GeoEye 01 images backed by IPE Graphs.
    """
    def __new__(cls, record, **kwargs):
        options = {
            "product": kwargs.get("product", "ortho")
        }

        standard_products = cls._build_standard_products(record, kwargs.get("proj", None))
        try:
            self = super(GE01, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self._record = record
        self._products = standard_products
        return self

    @property
    def _rgb_bands(self):
        return [2,1,0]

    def get_product(self, product):
        return self.__class__(self._record, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(rec, proj):
        s3path = "/vsis3/{}/{}/{}".format(
                                rec['properties']['attributes']['bucketName'],
                                rec['properties']['attributes']['bucketPrefix'],
                                rec['properties']['attributes']['imageFile']
                            )
        ge = ipe.GdalImageRead(path=s3path)
        ortho = ipe.Orthorectify(ge, **ortho_params(proj))
        return {
            "ortho": ortho
        }
