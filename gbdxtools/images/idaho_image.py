from __future__ import print_function
import requests
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.util import calc_toa_gain_offset, ortho_params
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

class IdahoImage(IpeImage):
    """
      Dask based access to IDAHO images via IPE.
    """
    def __new__(cls, idaho_id, **kwargs):
        idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(idaho_id)).json()
        meta = idaho_md["properties"]
        gains_offsets = calc_toa_gain_offset(meta)
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
        ortho = ipe.Orthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=idaho_id, objectStore="S3"))
        radiance = ipe.AddConst(ipe.MultiplyConst(ipe.Format(ortho, dataType="4"), constants=radiance_scales), constants=radiance_offsets)
        toa_reflectance = ipe.MultiplyConst(radiance, constants=reflectance_scales)
        self = super(IdahoImage, cls).__new__(cls, toa_reflectance)
        self.idaho_id = idaho_id
        return self
