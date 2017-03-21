from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

class LandsatImage(IpeImage):
    """
      Dask based access to landsat image backed by IPE Graphs.
    """
    def __init__(self, _id, node="landsat", **kwargs):
        self._gid = _id
        self._spec = kwargs.get('spec', 'multispectral')
        if '_ipe_graphs' in kwargs:
            self._ipe_graphs = kwargs['_ipe_graphs']
        else:
            self._ipe_graphs = self._init_graphs()
        if 'proj' in kwargs:
            self._proj = kwargs['proj']
        super(LandsatImage, self).__init__(self._ipe_graphs, self._gid, node=node, dtype="uint16", tile_size="512", **kwargs)
        self._proj = self.ipe_metadata['georef']['spatialReferenceSystemCode']


    def _init_graphs(self):
        landsat = ipe.LandsatRead(landsatId=self._gid, productSpec=self._spec)
        return {"landsat": landsat}
