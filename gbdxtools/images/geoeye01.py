from __future__ import print_function
import json
from gbdxtools.images.worldview import WorldViewImage
from gbdxtools.images.drivers import WorldViewDriver
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe.util import ortho_params
from gbdxtools.ipe.error import AcompUnavailable
ipe = Ipe()
from gbdxtools.vectors import Vectors
from shapely import wkt
from shapely.geometry import box

band_types = {
    'MS': 'BGRN',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

class GeoEyeDriver(WorldViewDriver):
    __image_option_defaults__ = {"product": "ortho"}

    def build_payload(self, target):
        standard_products = super(WorldViewDriver, self).build_payload(target, **self.options)
        options = self.options.copy()
        options["band_type"] = "pan"
        pan_products = target._build_standard_products(self.rda_id, **options)
        standard_products["pansharpened"] = ipe.LocallyProjectivePanSharpen(standard_products["ortho"],
                                                                                pan_products["ortho"])
        self._products = standard_products
        return standard_products

class GE01(WorldViewImage):
    __Driver__ = GeoEyeDriver
    def plot(self, **kwargs):
        kwargs["blm"] = False
        super(GE01, self).plot(**kwargs)

    @property
    def _rgb_bands(self):
        return [2,1,0]


