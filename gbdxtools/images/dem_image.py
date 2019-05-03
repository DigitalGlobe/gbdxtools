from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.rda.util import reproject_params
from gbdxtools.rda.interface import RDA

rda = RDA()

from shapely.geometry import box


class DemDriver(RDADaskImageDriver):
    image_option_support = ["proj", "bbox"]
    __image_option_defaults__ = {"bbox": None}


class DemImage(RDABaseImage):
    ''' Image class for Digital Elevation Model (DEM) data from the NED/SRTM dataset.

        This class has no Catalog IDs and is created by passing an AOI. It shares most of the same methods as CatalogImage objects.

        Args:
            aoi (list): list of coordinate in BBOX format
            proj (str): (optional) EPSG string of projection reproject to. Native projection is "EPSG:4326" (WGS84)

        Example:
            >>> dem = DemImage(aoi=[5.279, 60.358, 5.402, 60.419])'''

    __Driver__ = DemDriver
    __rda_id__ = "dgdem-v20180406-DEFLATED-ca4649c5acb"

    def __post_new_hook__(self, **kwargs):
        self = self.aoi(**kwargs)
        if self.rda.metadata["image"]["minX"] == -1:
            return self[:, :, 1:-1]
        return self

    @classmethod
    def _build_graph(cls, aoi, proj="EPSG:4326", **kwargs):
        bucket = kwargs.get("bucket", "idaho-dems-2018")
        imageId = kwargs.get("imageId", "dgdem-v20180406-DEFLATED-ca4649c5acb")
        wkt = box(*aoi).wkt
        dem = rda.IdahoTemplate(bucketName=bucket, imageId=imageId, objectStore="S3", geospatialWKT=str(wkt), nodeId="GeospatialCrop")
        if proj is not "EPSG:4326":
            dem = dem(**reproject_params(proj), nodeId="Reproject")
        return dem
