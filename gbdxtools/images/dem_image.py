from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.util import reproject_params
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

from shapely.geometry import box

class DemImage(IpeImage):
    """
      Dask based access to IDAHO images via IPE.
    """
    def __new__(cls, bbox, **kwargs):
        idaho_id = "dgdem-2016-08-12-f-b193-7aa90f8d11f1"
        options = {
            "proj": kwargs.get("proj", "EPSG:4326")
        }

        standard_products = cls._build_standard_products(idaho_id, bbox, options["proj"])
        try:
            self = super(DemImage, cls).__new__(cls, standard_products.get("dem"))
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self.idaho_id = idaho_id
        self._products = standard_products
        return self

    def get_product(self, product):
        return self.__class__(self.idaho_id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(idaho_id, bbox, proj):
        wkt = box(*bbox).wkt
        dem = ipe.GeospatialCrop(ipe.IdahoRead(bucketName="idaho-dems", imageId=idaho_id, objectStore="S3"), geospatialWKT=str(wkt))
        if proj is not "EPSG:4326":
            dem = ipe.Reproject(dem, **reproject_params(proj))
        return {
            "dem": dem
        }
