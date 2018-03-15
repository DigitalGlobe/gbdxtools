from gbdxtools.images.worldview import WorldViewImage
from gdbxtools.images.geoeye01 import GeoEyeDriver
from gbdxtools.images.util import vector_services_query

band_types = {
    'MS': 'BGRN',
    'Panchromatic': 'PAN',
    'Pan': 'PAN',
    'pan': 'PAN'
}

class QB02Driver(GeoEyeDriver):
    pass

class QB02(WorldViewImage):
    __Driver__ = QB02Driver

    def plot(self, **kwargs):
        kwargs["blm"] = False
        super(QB02, self).plot(**kwargs)

    @property
    def _rgb_bands(self):
        return [2,1,0]

    @staticmethod
    def _find_parts(cat_id, band_type):
        query = "item_type:IDAHOImage AND attributes.catalogID:{} " \
                "AND attributes.colorInterpretation:{}".format(cat_id, band_types[band_type])
        return vector_services_query(query)
