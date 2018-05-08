from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.util import reproject_params
ipe = Ipe()

class S3Image(IpeImage):
    """
      Dask based access to geotiffs on s3 backed by IPE Graphs.
    """
    def __new__(cls, path, **kwargs):
        path = '/vsis3/{}'.format(path)
        graph = cls._build_graph(path, kwargs.get("proj", None))
        try:
            self = super(S3Image, cls).__new__(cls, graph)
        except KeyError as e:
            print(e)
            raise
        self = self.aoi(**kwargs)
        self._path = path
        self._graph = graph
        return self

    @staticmethod
    def _build_graph(path, proj):
        s3 = ipe.GdalImageRead(path=path)
        if proj is not None:
            s3 = ipe.Reproject(s3, **reproject_params(proj))
        return s3
