from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.ipe.util import reproject_params
from gbdxtools.ipe.interface import Ipe

ipe = Ipe()

from shapely.geometry import box

class DemDriver(RDADaskImageDriver):
    image_option_support = ["proj", "bbox", "product"]
    __image_option_defaults__ = {"bbox": None, "product": "dem"}

class DemImage(RDABaseImage):
    __Driver__ = DemDriver
    __rda_id__ = "dgdem-2016-08-12-f-b193-7aa90f8d11f1"

    def __post_new_hook__(self, **kwargs):
        self = self.aoi(**kwargs)
        if self.ipe.metadata["image"]["minX"] == -1:
            return self[:, :, 1:-1]
        return self

    @classmethod
    def _build_standard_products(cls, idaho_id, bbox=None, proj="EPSG:4326", **kwargs):
        wkt = box(*bbox).wkt
        dem = ipe.GeospatialCrop(ipe.IdahoRead(bucketName="idaho-dems", imageId=idaho_id, objectStore="S3"), geospatialWKT=str(wkt))
        if proj is not "EPSG:4326":
            dem = ipe.Reproject(dem, **reproject_params(proj))
        return {
            "dem": dem
        }
