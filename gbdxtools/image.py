"""
GBDX Catalog Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from __future__ import print_function
import xml.etree.cElementTree as ET
from contextlib import contextmanager
from collections import defaultdict
import os
import json

from shapely.wkt import loads
from shapely.geometry import box, shape
import rasterio
import gdal

from gbdxtools.ipe.vrt import get_cached_vrt, put_cached_vrt, vrt_cache_key, IDAHO_CACHE_DIR
from gbdxtools.ipe.error import NotFound
from gbdxtools.ipe.interface import Ipe
from gbdxtools.ipe_image import IpeImage
from gbdxtools.vectors import Vectors
from gbdxtools.idaho import Idaho

from gbdxtools.auth import Interface

band_types = {
  'MS': 'WORLDVIEW_8_BAND',
  'Panchromatic': 'PAN',
  'Pan': 'PAN'
}

class Image(object):
    """ 
      Strip Image Class 
      Collects metadata on all image parts, groupd pan and ms bands from idaho
    """

    def __init__(self, cat_id, band_type="MS", node="toa_reflectance", **kwargs):
        self.interface = Interface.instance()(**kwargs)
        self.vectors = Vectors()
        self.idaho = Idaho()
        self.ipe = Ipe()
        self.cat_id = cat_id
        self._band_type = band_types[band_type]
        self._node = node
        self._pansharpen = kwargs.get('pansharpen', False)
        self._acomp = kwargs.get('acomp', False)
        if self._pansharpen:
            self._node = 'pansharpened'
        self._level = kwargs.get('level', 0)
        self._fetch_metadata()

    @contextmanager
    def open(self, *args, **kwargs):
        """ A rasterio based context manager for reading the full image VRT """
        with rasterio.open(self.vrt, *args, **kwargs) as src:
            yield src

    @property
    def vrt(self):
        try:
            vrt = get_cached_vrt(self.cat_id, self._node, self._level)
        except NotFound:
            vrt = os.path.join(IDAHO_CACHE_DIR, vrt_cache_key(self.cat_id, self._node, self._level)) 
            _tmp_vrt = gdal.BuildVRT('/vsimem/merged.vrt', self._collect_vrts(), separate=False)
            gdal.Translate(vrt, _tmp_vrt, format='VRT')
        return vrt 

    def aoi(self, bbox, band_type='MS', **kwargs):
        try:
            band_type = band_types[band_type]
        except:
            print('band_type ({}) not supported'.format(band_type))
            return None
        _area = box(*bbox)
        intersections = {}
        for part in self.metadata['properties']['parts']:
            for key, item in part.iteritems():
                geom = box(*item['geometry'].bounds)
                if geom.intersects(_area):
                    intersections[key] = item

        if not len(intersections.keys()):
            print('Failed to find data within the given BBOX')
            return None

        pansharpen = kwargs.get('pansharpen', self._pansharpen)
        if self._node == 'pansharpened' and pansharpen:
            ms = IpeImage(intersections['WORLDVIEW_8_BAND']['properties']['idahoImageId'])
            pan = IpeImage(intersections['PAN']['properties']['idahoImageId'])
            return self._create_pansharpen(ms, pan, bbox=bbox, **kwargs)
        elif band_type in intersections:
            md = intersections[band_type]['properties']
            return IpeImage(md['idahoImageId'], bbox=bbox, **kwargs)
        else:
            print('band_type ({}) did not find a match in this image'.format(band_type))
            return None

    def _query_vectors(self, query, aoi=None):
        if aoi is None:
            aoi = "POLYGON((-180.0 90.0,180.0 90.0,180.0 -90.0,-180.0 -90.0,-180.0 90.0))"
        return self.vectors.query(aoi, query=query)

    def _fetch_metadata(self):
        query = 'item_type:DigitalGlobeAcquisition AND attributes.catalogID:{}'.format(self.cat_id)
        props = self._query_vectors(query)
        if len(props) == 0:
            print('Could not find image metadata for the given catalog id')
            return

        geom = shape(props[0]['geometry'])
        attrs = props[0]['properties']['attributes']
        query = 'item_type:IDAHOImage AND attributes.catalogID:{}'.format(self.cat_id)
        results = self._query_vectors(query)
        
        # group idaho images on identifiers
        grouped = defaultdict(list)
        for idaho in results:
            vid = idaho['properties']['attributes']['vendorDatasetIdentifier']
            grouped[vid].append(idaho)

        # stash parts on metatada
        attrs['parts'] = []
        for key, parts in grouped.iteritems():
            part = {}
            for p in parts:
                attr = p['properties']['attributes']
                part[attr['colorInterpretation']] = {'properties': attr, 'geometry': shape(p['geometry'])}
            attrs['parts'].append(part)

        self.metadata = {'properties': attrs, 'geometry': geom}


    def _collect_vrts(self):
        vrts = []
        for part in self.metadata['properties']['parts']:
            if self._node == 'pansharpened':
                ms = IpeImage(part['WORLDVIEW_8_BAND']['properties']['idahoImageId'])
                pan = IpeImage(part['PAN']['properties']['idahoImageId'])
                img = self._create_pansharpen(ms, pan)
            else:
                md = part[self._band_type]['properties']
                img = IpeImage(md['idahoImageId'])
            
            vrts.append(img.vrt)
        return vrts

    def _create_pansharpen(self, ms, pan, **kwargs):
        ms = self.ipe.Format(self.ipe.MultiplyConst(ms, constants=json.dumps([1000]*8), _intermediate=True), dataType="1", _intermediate=True)
        pan = self.ipe.Format(self.ipe.MultiplyConst(pan, constants=json.dumps([1000]), _intermediate=True), dataType="1", _intermediate=True)
        return self.ipe.LocallyProjectivePanSharpen(ms, pan).aoi(bbox=kwargs.get('bbox', None))
        


if __name__ == '__main__': 
    from gbdxtools import Interface
    import json
    import rasterio
    gbdx = Interface()

    cat_id = '104001001838A000'
    cat_id = '104001000D7A8600'
    img = gbdx.image(cat_id, pansharpen=True)

    #print(json.dumps(img.metadata, indent=4))
    vrt = img.vrt
    with rasterio.open(vrt) as src:
        print(src.meta)
  

    #aoi = img.aoi([-95.06904982030392, 29.7187207124839, -95.06123922765255, 29.723901202069023])
    #with aoi.open() as src:
    #    assert isinstance(src, rasterio.DatasetReader)

