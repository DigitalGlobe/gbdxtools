from gbdxtools.images.worldview import WorldViewImage
from gbdxtools.images.drivers import WorldViewDriver
from gbdxtools.images.util import vector_services_query
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

band_types = {
    'MS': 'BGRN',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

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

<<<<<<< HEAD
=======
class GE01(WorldViewImage):
    __Driver__ = GeoEyeDriver

>>>>>>> dev
    @property
    def _rgb_bands(self):
        return [2,1,0]

    @staticmethod
    def _find_parts(cat_id, band_type):
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        return vector_services_query(query)

