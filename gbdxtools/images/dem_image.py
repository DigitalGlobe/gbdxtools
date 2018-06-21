from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.ipe.util import reproject_params
from gbdxtools.ipe.interface import Ipe

ipe = Ipe()

from shapely.geometry import box

class DemDriver(RDADaskImageDriver):
    image_option_support = ["proj", "bbox"]
    __image_option_defaults__ = {"bbox": None}

class DemImage(RDABaseImage):
    __Driver__ = DemDriver
    __rda_id__ = "dgdem-v20180406-DEFLATED-ca4649c5acb"

    def __post_new_hook__(self, **kwargs):
        self = self.aoi(**kwargs)
        if self.ipe.metadata["image"]["minX"] == -1:
            return self[:, :, 1:-1]
        return self

    @classmethod
    def _build_graph(cls, aoi, proj="EPSG:4326", **kwargs):
        wkt = box(*aoi).wkt
        dem = ipe.GeospatialCrop(ipe.IdahoRead(bucketName="idaho-dems-2018", imageId="dgdem-v20180406-DEFLATED-ca4649c5acb", objectStore="S3"), geospatialWKT=str(wkt))
        if proj is not "EPSG:4326":
            dem = ipe.Reproject(dem, **reproject_params(proj))
        return dem
