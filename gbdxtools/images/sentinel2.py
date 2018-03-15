from gbdxtools.images import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
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

class Sentinel2Driver(RDADaskImageDriver):
    image_support_options = ["spec", "product"]
    __image_default_options__ = {"spec": "10m", "product": "sentinel"}

class Sentinel2(RDABaseImage):
    """
      Dask based access to sentinel2 images backed by IPE Graphs.
    """
    __Driver__ = Sentinel2Driver

    @property
    def _id(self):
        return self.__rda_id__

    @property
    def _spec(self):
        return self.options["spec"]

    @property
    def _rgb_bands(self):
        return [2,1,0]

    @property
    def _ndvi_bands(self):
        return [6,3]

    @classmethod
    def _build_standard_products(cls, prefix, spec, proj):
        sentinel = ipe.SentinelRead(SentinelId=prefix, sentinelProductSpec=spec)
        if proj is not None:
            sentinel = ipe.Reproject(sentinel, **reproject_params(proj))
        return {
            "sentinel": sentinel
        }
