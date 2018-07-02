from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.images.util import reproject_params
from gbdxtools.rda.interface import RDA
rda = RDA()

class Sentinel2Driver(RDADaskImageDriver):
    image_option_support = ["spec", "proj"]
    __image_option_defaults__ = {"spec": "10m", "proj": None}

class Sentinel2(RDABaseImage):
    """
      Dask based access to sentinel2 images backed by rda Graphs.
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
    def _build_graph(cls, prefix, spec="10m", proj=None, **kwargs):
        sentinel = rda.SentinelRead(SentinelId=prefix, sentinelProductSpec=spec)
        if proj is not None:
            sentinel = rda.Reproject(sentinel, **reproject_params(proj))
        return sentinel
