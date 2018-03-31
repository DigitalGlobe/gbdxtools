from __future__ import print_function
from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.util import ortho_params
ipe = Ipe()

class IkonosDriver(RDADaskImageDriver):
    image_option_support = ["proj", "gsd", "spec", "product"]
    __image_option_defauts__ = {"gsd": None, "spec": "multispectral", "product": "ikonos"}

class IkonosImage(RDABaseImage):
    """
      Dask based access to ikonos images backed by IPE Graphs.
    """
    __Driver__ = IkonosDriver

    @property
    def _record(self):
        return self.__rda_id__

    @property
    def _spec(self):
        return self.options["spec"]

    @property
    def _gsd(self):
        return self.options["gsd"]

    @property
    def _rgb_bands(self):
        return [2,1,0]

    @staticmethod
    def _build_standard_products(record, spec, proj, gsd=None):
        prefix = record['properties']['attributes']['bucketPrefix']
        bucket = record['properties']['attributes']['bucketName']
        ikonos = ipe.IkonosRead(path="{}/{}/{}_0000000:{}".format(bucket, prefix, prefix, spec))
        params = ortho_params(proj, gsd=gsd)
        ikonos = ipe.Orthorectify(ikonos, **params)
        return {
            "ikonos": ikonos
        }
