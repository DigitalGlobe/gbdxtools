import os
from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.rda.util import ortho_params
from gbdxtools.rda.interface import RDA

rda = RDA()


class RadarsatDriver(RDADaskImageDriver):
    image_option_support = ["calibration", "proj"]
    __image_option_defaults__ = {"calibration": "uncalibrated", "proj": "EPSG:4326"}


class Radarsat(RDABaseImage):
    """
      Dask based access to Radarsat images backed by rda Graphs.

     Args:
        catID (str): The Radarsat record from the Radarsat Catalog Item
        calibration (str): Data calibration. Options are 'uncalibrated' (default), 'beta0', 'sigma0' or 'gamma'.
        proj (str): EPSG code for the resulting image.
        gsd (str): Resolution for the resulting image.
    """
    __Driver__ = RadarsatDriver

    @property
    def _id(self):
        return self.__rda_id__

    @property
    def polarization(self):
        return self.options["calibration"]

    @classmethod
    def _build_graph(cls, record, calibration="uncalibrated", proj=None, gsd=None):
        try:
            prefix = record['properties']['attributes']['bucketPrefix']
            bucket = record['properties']['attributes']['bucketName']
        except Exception:
            raise AttributeError(
                "Radarsat Record missing bucketPrefix and bucketName. Most likely this is permissions issue.")
        radarsat = rda.RadarsatTemplate(path=bucket+'/'+prefix, radarsatCalibration=calibration, nodeId="Radarsat2ProductRead")
        if proj is not None:
            params = ortho_params(proj, gsd=gsd)
            radarsat(nodeId="Orthorectify", **params)
        return radarsat
