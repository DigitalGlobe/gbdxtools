from __future__ import print_function
from gbdxtools.images.rda_image import RDAImage
from gbdxtools.rda.interface import RDA
from gbdxtools.rda.util import ortho_params
rda = RDA()

class S3Image(RDAImage):
    """
      Dask based access to geotiffs on s3 backed by RDA Graphs.
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
    def _build_graph(path, proj, gsd=None):
        s3 = rda.GdalImageRead(path=path)
        if proj is not None:
            params = ortho_params(proj, gsd=gsd)
            s3 = rda.Orthorectify(s3, **params)
        return s3
