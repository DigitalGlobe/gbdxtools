from gbdxtools.images.worldview import WorldViewImage
from gbdxtools.images.drivers import WorldViewDriver
from gbdxtools.images.util import vector_services_query
from gbdxtools.rda.interface import RDA
rda = RDA()

band_types = {
    'MS': 'BGRN',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

class GeoEyeDriver(WorldViewDriver):
    __image_option_defaults__ = {"correctionType": "DN"}


class GE01(WorldViewImage):
    __Driver__ = GeoEyeDriver

    @property
    def _rgb_bands(self):
        return [2,1,0]
