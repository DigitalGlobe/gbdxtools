from gbdxtools.images.rda_image import RDAImage
from gbdxtools.rda.interface import RDA

rda = RDA()

class S3Image(RDAImage):
    '''Dask based access to geotiffs on S3.

    Args:
        path (string): path to the geotiff file in S3.
        proj (string): destination EPSG string, e.g. 'EPSG:4326'
            Perform optional reprojection if needed.
        src_proj (string): source EPSG string
            Define the source projection if it can't be automatically determined.

    Example:
        >>> img = S3Image('landsat-pds/c1/L8/139/045/LC08_L1TP_139045_20170304_20170316_01_T1/LC08_L1TP_139045_20170304_20170316_01_T1_B3.TIF')'''

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
        s3 = rda.S3ImageTemplate(path=path)
        params = {
            "Dest pixel-to-world transform": "",
            "Resampling Kernel": "INTERP_BILINEAR",
            "SourceSRSCode": "",
            "Source pixel-to-world transform": "",
            "DestSRSCode": "",
            "Background Values": "[0]"
        }
        if proj is not None:
            params['DestSRSCode'] = proj
            if src_proj is not None:
                params['SourceSRSCode'] = src_proj
            s3 = s3(nodeId="Reproject", **params)
        return s3
