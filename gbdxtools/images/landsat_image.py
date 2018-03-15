from __future__ import print_function
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

class LandsatDriver(RDADaskImageDriver):
    __default_options__ = {}
    image_option_support = ["spec", "product"]
    __image_option_defaults__ = {"spec": "multispectral", "product": "landsat"}

class LandsatImage(RDABaseImage):
    """
      Dask based access to landsat image backed by IPE Graphs.
    """
    __Driver__ = LandsatDriver

    @property
    def _id(self):
        return self.__rda_id__

    @property
    def _spec(self):
        return self.options["spec"]

    @property
    def _rgb_bands(self):
        return [3,2,1]

    @property
    def _ndvi_bands(self):
        return [4,3]

    @staticmethod
    def _build_standard_products(_id, spec, proj):
        landsat = ipe.LandsatRead(landsatId=_id, productSpec=spec)
        if proj is not None:
            landsat = ipe.Reproject(landsat, **reproject_params(proj))
        return {
            "landsat": landsat
        }
