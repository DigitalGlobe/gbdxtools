from __future__ import print_function
import requests
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.util import calc_toa_gain_offset, ortho_params
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

class IdahoImage(IpeImage):
    """
      Dask based access to ipe based images (Idaho).
    """
    _idaho_md = None
  
    def __init__(self, idaho_id, node="toa_reflectance", **kwargs):
        self._gid = idaho_id
        self._level = 0
        if 'proj' in kwargs:
            self._proj = kwargs['proj']
        if '_ipe_graphs' in kwargs:
            self._ipe_graphs = kwargs['_ipe_graphs']
        else:
            self._ipe_graphs = self._init_graphs()

        super(IdahoImage, self).__init__(self._ipe_graphs, idaho_id, node=node, **kwargs)


    @property
    def idaho_md(self):
        if self._idaho_md is None:
            self._idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(self._gid)).json()
        return self._idaho_md

    def _init_graphs(self):
        meta = self.idaho_md["properties"]
        gains_offsets = calc_toa_gain_offset(meta)
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
        ortho = ipe.Orthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=self._gid, objectStore="S3"), **ortho_params(self._proj))
        radiance = ipe.AddConst(ipe.MultiplyConst(ipe.Format(ortho, dataType="4"), constants=radiance_scales), constants=radiance_offsets)
        toa_reflectance = ipe.MultiplyConst(radiance, constants=reflectance_scales)
        return {"ortho": ortho, "radiance": radiance, "toa_reflectance": toa_reflectance}
