import os
from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.rda.util import ortho_params
from gbdxtools.rda.interface import RDA

rda = RDA()


class RadarsatDriver(RDADaskImageDriver):
    image_option_support = ["proj"]
    __image_option_defaults__ = {"proj": "EPSG:4326"}


class Radarsat(RDABaseImage):
    """
      Dask based access to sentinel2 images backed by rda Graphs.
    """
    __Driver__ = RadarsatDriver

    @property
    def _id(self):
        return self.__rda_id__

    @classmethod
    def _build_graph(cls, record, proj="EPSG:4326", gsd=None, **kwargs):
        try:
            prefix = record['properties']['attributes']['bucketPrefix']
            bucket = record['properties']['attributes']['bucketName']
        except Exception:
            raise AttributeError(
                "Radarsat Record missing bucketPrefix and bucketName. Most likely this is permissions issue.")
        radarsat = rda.Radarsat(path=os.path.join(bucket, prefix))
        if proj is not None:
            params = ortho_params(proj, gsd=gsd)
            radarsat(nodeId="Orthorectify", **params)
        return radarsat
