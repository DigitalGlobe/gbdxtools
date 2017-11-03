from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.util import reproject_params
ipe = Ipe()

class S3Image(IpeImage):
    """
      Dask based access to geotiffs on s3 backed by IPE Graphs.
    """
    def __new__(cls, path, **kwargs):
        options = {
            "product": kwargs.get("product", "s3")
        }

        path = '/vsis3/{}'.format(path)

        standard_products = cls._build_standard_products(path, kwargs.get("proj", None))
        try:
            self = super(S3Image, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self._path = path
        self._products = standard_products
        return self

    def get_product(self, product):
        return self.__class__(self._path, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(path, proj):
        s3 = ipe.GdalImageRead(path=path)
        if proj is not None:
            s3 = ipe.Reproject(s3, **reproject_params(proj))
        return {
            "s3": s3
        }
