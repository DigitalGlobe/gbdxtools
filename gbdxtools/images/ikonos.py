from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.rda.interface import RDA
from gbdxtools.rda.util import ortho_params
rda = RDA()

band_types = {
    'MS': 'multispectral',
    'ms': 'multispectral',
    'Panchromatic': 'panchromatic',
    'Pan': 'panchromatic',
    'pan': 'panchromatic',
    'thermal': 'thermal'
}

class IkonosDriver(RDADaskImageDriver):
    image_option_support = ["proj", "gsd", "band_type"]
    __image_option_defaults__ = {"gsd": None, "band_type": "MS"}

class IkonosImage(RDABaseImage):
    """
      Dask based access to ikonos images backed by RDA Graphs.
    """
    __Driver__ = IkonosDriver

    @property
    def _record(self):
        return self.__rda_id__

    @property
    def _spec(self):
        return self.options["band_type"]

    @property
    def _gsd(self):
        return self.options["gsd"]

    @property
    def _rgb_bands(self):
        return [2,1,0]

    @classmethod
    def _build_graph(cls, record, band_type="MS", proj="EPSG:4326", gsd=None, **kwargs):
        spec = band_types[band_type]
        prefix = record['properties']['attributes']['bucketPrefix']
        bucket = record['properties']['attributes']['bucketName']
        ikonos = rda.IkonosRead(path="{}/{}/{}_0000000:{}".format(bucket, prefix, prefix, spec))
        params = ortho_params(proj, gsd=gsd)
        ikonos = rda.Orthorectify(ikonos, **params)
        return ikonos
