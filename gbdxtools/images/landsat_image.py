from gbdxtools.images.base import RDABaseImage
from gbdxtools.images.drivers import RDADaskImageDriver
from gbdxtools.images.util.image import reproject_params
from gbdxtools.rda.error import IncompatibleOptions
from gbdxtools.rda.interface import RDA
rda = RDA()

band_types = {
    'MS': 'multispectral',
    'ms': 'multispectral',
    'Panchromatic': 'panchromatic',
    'Pan': 'panchromatic',
    'pan': 'panchromatic',
    'thermal': 'thermal'
}

class LandsatDriver(RDADaskImageDriver):
    __default_options__ = {}
    image_option_support = ["band_type", "proj", "pansharpen"]
    __image_option_defaults__ = {"band_type": "MS", "proj": None, "pansharpen": False}

class LandsatImage(RDABaseImage):
    """
      Dask based access to landsat image backed by rda Graphs.
    """
    __Driver__ = LandsatDriver

    @property
    def _id(self):
        return self.__rda_id__

    @property
    def _spec(self):
        return self.options["band_type"]

    @property
    def _rgb_bands(self):
        return [3,2,1]

    @property
    def _ndvi_bands(self):
        return [4,3]

    @property
    def _ndwi_bands(self):
        return[2,4]

    @classmethod
    def _build_graph(cls, _id, band_type="MS", proj=None, **kwargs):
        spec = band_types[band_type]
        pansharpen = kwargs.get('pansharpen', False)
        if spec == "thermal" and pansharpen:
            raise IncompatibleOptions('Cannot generate a pansharpened thermal Landsat image')

        if pansharpen is True:
            landsat = rda.LandsatPanSharpenTemplate(catalogIdMultispectral=_id, catalogIdPanchromatic=_id)
        else:
            landsat = rda.LandsatTemplate(catalogId=_id, productSpec=spec)
        if proj is not None:
            landsat = landsat(nodeId="Reproject", **reproject_params(proj))
        return landsat
