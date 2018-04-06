from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import IdahoDriver
from gbdxtools.images.util import vector_services_query
from gbdxtools.ipe.util import calc_toa_gain_offset, ortho_params
from gbdxtools.ipe.interface import Ipe

from shapely import wkt
from shapely.geometry import box

ipe = Ipe()

class IdahoImage(RDABaseImage):
    """
      Dask based access to IDAHO images via IPE.
    """
    __Driver__ = IdahoDriver

    @property
    def idaho_id(self):
        return self.__rda_id__

    @classmethod
    def _build_standard_products(cls, idaho_id, proj=None, bucket="idaho-images", gsd=None, acomp=False, **kwargs):
        if bucket is None:
            vq = "item_type:IDAHOImage AND id:{}".format(idaho_id)
            result = vector_services_query(vq)
            if result:
               bucket = result[0]["properties"]["attributes"]["tileBucketName"]

        dn_op = ipe.IdahoRead(bucketName=bucket, imageId=idaho_id, objectStore="S3")
        params = ortho_params(proj, gsd=gsd)

        graph = {
            "1b": dn_op,
            "ortho": ipe.Orthorectify(dn_op, **params),
            "acomp": ipe.Format(ipe.Orthorectify(ipe.Acomp(dn_op), **params), dataType="4"),
            "toa_reflectance": ipe.Format(ipe.Orthorectify(ipe.TOAReflectance(dn_op), **params), dataType="4")
        }

        return graph

