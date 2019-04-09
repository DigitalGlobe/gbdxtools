from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import IdahoDriver
from gbdxtools.images.util import vector_services_query
from gbdxtools.rda.interface import RDA

rda = RDA()


class IdahoImage(RDABaseImage):
    """ Image based on IDAHO virtual tiles

        Like a CatalogImage, but takes an IDAHO ID when initialized.
        Band_type and pansharpen arguments are not supported because IDAHO multispectral and panchromatic images are stored separately.

        Args:
            (str): IDAHO ID

        Example:
            >>> img = IdahoImage('87a5b5a7-5438-44bf-926a-c8c7bc153713')
    """
    __Driver__ = IdahoDriver

    @property
    def idaho_id(self):
        return self.__rda_id__

    @classmethod
    def _build_graph(cls, idaho_id, proj=None, bucket="idaho-images", gsd=None, acomp=False, bands="MS", **kwargs):
        if bucket is None:
            vq = "item_type:IDAHOImage AND id:{}".format(idaho_id)
            result = vector_services_query(vq)
            if result:
                bucket = result[0]["properties"]["attributes"]["tileBucketName"]

        gsd = gsd if gsd is not None else ""
        correction = "ACOMP" if acomp else kwargs.get("correctionType")
        spec = kwargs.get('spec')
        if spec == "1b":
            graph = rda.IdahoRead(bucketName=bucket, imageId=idaho_id, objectStore="S3", targetGSD=gsd)
        else:
            graph = rda.DigitalGlobeImage(bucketName=bucket, imageId=idaho_id, bands=bands, CRS=proj,
                                          correctionType=correction, GSD=gsd)

        return graph
