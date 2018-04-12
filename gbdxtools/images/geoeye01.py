from gbdxtools.images.worldview import WorldViewImage
from gbdxtools.images.drivers import WorldViewDriver
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

class GeoEyeDriver(WorldViewDriver):
    __image_option_defaults__ = {"product": "ortho"}

    def build_payload(self, target):
        standard_products = super(WorldViewDriver, self).build_payload(target)
        options = self.options.copy()
        options["band_type"] = "pan"
        pan_products = target._build_standard_products(self.rda_id, **options)
        standard_products["pansharpened"] = ipe.LocallyProjectivePanSharpen(standard_products["ortho"],
                                                                                pan_products["ortho"])
        self._products = standard_products
        return standard_products

class GE01(WorldViewImage):
    __Driver__ = GeoEyeDriver

    @property
    def _rgb_bands(self):
        return [2,1,0]


