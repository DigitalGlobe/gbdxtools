from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.images.util.image import reproject_params
from gbdxtools.rda.interface import RDA
rda = RDA()

class ModisDriver(RDADaskImageDriver):
    image_option_support = ["proj"]
    __image_option_defaults__ = {"proj": None}

class Modis(RDABaseImage):
    """
     Dask based access to Modis images backed by rda Graphs.
     
     Args:
        catalog_id (str): The Catalog ID for the modis image.
    """
    __Driver__ = ModisDriver

    @property
    def _id(self):
        return self.__rda_id__

    @property
    def _rgb_bands(self):
        return [1,4,3]

    @property
    def _ndvi_bands(self):
         return [1,4]

    @classmethod
    def _build_graph(cls, cat_id, proj=None, **kwargs):
        modis = rda.ModisRead(modisId=cat_id)
        if proj is not None:
            modis = rda.Reproject(modis, **reproject_params(proj))
        return modis

