from __future__ import print_function
from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.ipe.util import reproject_params
from gbdxtools.ipe.interface import Ipe

ipe = Ipe()

from shapely.geometry import box

class DemDriver(RDADaskImageDriver):
    image_option_support = ["proj", "bbox"]
    @property
    def payload(self):
        p = self.products.get["dem"]
        if not p:
            raise AttributeError("DemImage initialized with bbox=None")
        return p

class DemImage(RDABaseImage):
    """
      Dask based access to IDAHO images via IPE.
    """

    __Driver__ = DemDriver
    __rda_id__ = "dgdem-2016-08-12-f-b193-7aa90f8d11f1"

    def __post_new_hook__(self, **kwargs):
        self = self.aoi(**kwargs)
        if self.ipe.metadata["image"]["minX"] == -1:
            return self[:, :, 1:-1]
        return self

    @classmethod
    def _build_standard_products(cls, idaho_id, **kwargs):
        wkt = box(*bbox).wkt
        dem = ipe.GeospatialCrop(ipe.IdahoRead(bucketName="idaho-dems", imageId=idaho_id, objectStore="S3"), geospatialWKT=str(wkt))
        if proj is not "EPSG:4326":
            dem = ipe.Reproject(dem, **reproject_params(proj))
        return {
            "dem": dem
        }
