from __future__ import print_function
from gbdxtools.images.rda_image import RDAImage
from gbdxtools.rda.interface import RDA
from gbdxtools.rda.util import ortho_params
rda = RDA()

class S3Image(RDAImage):
    """
      Dask based access to geotiffs on S3 backed by RDA Graphs.

    Parameters
    ----------
    path (string): path to the geotiff file in S3.

    proj (string): destination EPSG string, e.g. 'EPSG:4326'
        Perform optional reprojection if needed.

    src_proj (string): source EPSG string
        Define the source projection if it can't be automatically determined.

    """

    def __new__(cls, path, **kwargs):
        path = '/vsis3/{}'.format(path)
        graph = cls._build_graph(path, kwargs.get("proj", None), kwargs.get("src_proj", None))
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
    def _build_graph(path, proj=None, src_proj=None):
        s3 = rda.GdalImageRead(path=path)
        params = {
            "Dest pixel-to-world transform": "",
            "Resampling Kernel": "INTERP_BILINEAR",
            "Source SRS Code": "",
            "Source pixel-to-world transform": "",
            "Dest SRS Code": "",
            "Background Values": "[0]"
        }
        if proj is not None:
            params['Dest SRS Code'] =  proj
            if src_proj is not None:
                params['Source SRS Code'] = src_proj
            s3 = rda.Reproject(s3, **params)
        return s3
