"""
GBDX Catalog Image Interface.
Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
import json

from gbdxtools.images.drivers import WorldViewDriver, RDADaskImageDriver
from gbdxtools.images.base import RDABaseImage
from gbdxtools import IdahoImage
from gbdxtools.images.util import vector_services_query, vendor_id, band_types
from gbdxtools.rda.interface import RDA
from gbdxtools.rda.error import MissingIdahoImages, AcompUnavailable

rda = RDA()


class WorldViewImage(RDABaseImage):
    __Driver__ = WorldViewDriver
    _parts = None

    @property
    def cat_id(self):
        return self.__rda_id__

    @property
    def parts(self):
        if self._parts is None:
            self._parts = [IdahoImage(rec['properties']['attributes']['idahoImageId'],
                                      proj=self.options["proj"],
                                      bucket=rec['properties']['attributes']['bucketName'],
                                      gsd=self.options["gsd"],
                                      acomp=self.options["acomp"])
                           for rec in self._find_parts(self.cat_id, self.options["band_type"])]
        return self._parts

    @staticmethod
    def _find_parts(cat_id, band_type):
        query = "item_type:IDAHOImage AND attributes.catalogID:{}".format(cat_id)
        _parts = vector_services_query(query)
        if not len(_parts):
            raise MissingIdahoImages('Unable to find IDAHO imagery in the catalog: {}'.format(query))
        _id = vendor_id(_parts[0])
        return [p for p in _parts if vendor_id(p) == _id]

    @classmethod
    def _build_graph(cls, cat_id, band_type="MS", proj="EPSG:4326", gsd=None, acomp=False, **kwargs):
        bands = band_types[band_type]
        gsd = gsd if not None else ""
        correction = "ACOMP" if acomp else kwargs.get("correctionType", "TOAREFLECTANCE")
        graph = rda.Format(rda.DigitalGlobeStrip(catId=cat_id, CRS=proj, GSD=gsd, correctionType=correction, bands=bands, fallbackToTOA=True), dataType="4")
        #raise AcompUnavailable("Cannot apply acomp to this image, data unavailable in bucket: {}".format(_bucket))
        return graph

    @property
    def _rgb_bands(self):
        return [4, 2, 1]

    @property
    def _ndvi_bands(self):
        return [6, 4]

class WV03_SWIR(WorldViewImage):
    @staticmethod
    def _find_parts(cat_id, band_type):
        query = "item_type:IDAHOImage AND attributes.catalogID:{}".format(cat_id)
        return vector_services_query(query)

    @classmethod
    def _build_graph(cls, cat_id, proj="EPSG:4326", gsd=None, acomp=False, **kwargs):
        bands = "SWIR"
        gsd = gsd if not None else ""
        correction = "ACOMP" if acomp else kwargs.get("correctionType", "TOAREFLECTANCE")
        graph = rda.Format(rda.DigitalGlobeStrip(catId=cat_id, CRS=proj, GSD=gsd, correctionType=correction, bands=bands, fallbackToTOA=True), dataType="4")
        return graph

    @property
    def _rgb_bands(self):
        raise NotImplementedError("RGB bands not available in SWIR spectrum")

    @property
    def _ndvi_bands(self):
        raise NotImplementedError("NDVI bands not available in SWIR spectrum")

    def plot(self, **kwargs):
        bands = kwargs.get("bands")
        if bands is not None:
            assert len(bands) == 1, "SWIR supports plotting only a single band at a time"
        if "cmap" in kwargs:
            cmap = kwargs["cmap"]
            del kwargs["cmap"]
        else:
            cmap = "Greys_r"
        self._plot(tfm=self._single_band, cmap=cmap, **kwargs)

    def _single_band(self, **kwargs):
        if "bands" not in kwargs:
            kwargs["bands"] = [0]
        arr = self._read(self, **kwargs)
        return arr[0,:,:]


class WV03_VNIR(WorldViewImage):
    pass

class WV02(WorldViewImage):
    pass

class WV01(WorldViewImage):
    class WV01Driver(RDADaskImageDriver):
        image_option_support = ["proj", "gsd", "band_type", "correctionType"]
        __image_option_defaults__ = {"band_type": "pan", "correctionType": "DN"}

    __Driver__ = WV01Driver

class WV04(WorldViewImage):
    @property
    def _rgb_bands(self):
        return [2,1,0]
