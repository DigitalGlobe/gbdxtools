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
import uuid

from shapely.wkt import loads
from shapely.geometry import box, shape
import requests

from gbdxtools.auth import Auth
from gbdxtools.ipe.util import calc_toa_gain_offset, timeit
from gbdxtools.ipe_image import IpeImage, DaskImage
from gbdxtools.vectors import Vectors
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()


band_types = {
  'MS': 'WORLDVIEW_8_BAND',
  'Panchromatic': 'PAN',
  'Pan': 'PAN',
  'pan': 'PAN'
}

class Image(IpeImage):
    """ 
      Strip Image Class 
      Collects metadata on all image parts, groupd pan and ms bands from idaho
      Inherits from IpeImage and represents a mosiac data set of the full catalog strip
    """
    _properties = None
    _ipe_id = None
    _ipe_metadata = None
    _proj = 'EPSG:4326'

    def __init__(self, cat_id, band_type="MS", node="toa_reflectance", **kwargs):
        self.interface = Auth()
        self.vectors = Vectors()
        self._gid = cat_id
        self._band_type = band_type
        self._node_id = node
        self._pansharpen = kwargs.get('pansharpen', False)
        self._acomp = kwargs.get('acomp', False)
        if 'proj' in kwargs:
            self._proj = kwargs['proj']
        if self._pansharpen:
            self._node_id = 'pansharpened'
        self._level = kwargs.get('level', 0)
        self._ipe_graphs = self._init_graphs()
        self._graph_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(self.ipe.graph())))
        self._tile_size = kwargs.get('tile_size', 256)
        self._cfg = self._config_dask()
        super(IpeImage, self).__init__(**self._cfg)
        bounds = self._parse_geoms(**kwargs)
        if bounds is not None:
            self._cfg = self._aoi_config(bounds)
            super(IpeImage, self).__init__(**self._cfg)


    def _query_vectors(self, query, aoi=None):
        if aoi is None:
            aoi = "POLYGON((-180.0 90.0,180.0 90.0,180.0 -90.0,-180.0 -90.0,-180.0 90.0))"
        return self.vectors.query(aoi, query=query)

    @property
    def properties(self):
        if self._properties is None:
            query = 'item_type:DigitalGlobeAcquisition AND attributes.catalogID:{}'.format(self._gid)
            self._properties = self._query_vectors(query)
        return self._properties
            
    
    @property
    def metadata(self):
        meta = {}
        query = 'item_type:IDAHOImage AND attributes.catalogID:{}'.format(self._gid)
        results = self._query_vectors(query)
        grouped = defaultdict(list)
        for idaho in results:
            vid = idaho['properties']['attributes']['vendorDatasetIdentifier']
            grouped[vid].append(idaho)

        meta['parts'] = []
        for key, parts in grouped.items():
            part = {}
            for p in parts:
                attrs = p['properties']['attributes']
                part[attrs['colorInterpretation']] = {'properties': attrs, 'geometry': shape(p['geometry'])}
            meta['parts'].append(part)

        return meta


    def aoi(self, **kwargs):
        pansharp = False
        if self._pansharpen and 'pansharpen' not in kwargs:
            pansharp = True

        bounds = self._parse_geoms(**kwargs)
        if bounds is None:
            print('AOI bounds not found. Must specify a bbox, wkt, or geojson geometry.')
            return

        #img = Image(self._gid, band_type=self._band_type, node=self._node_id, pansharpen=pansharp)
        cfg = self._aoi_config(bounds)
        return DaskImage(**cfg)


    def _init_graphs(self):
        graph = {}
        ids = []
        if self._node_id == 'pansharpened' and self._pansharpen:
            return self._pansharpen_graph()
        else: 
            for part in self.metadata['parts']:
                for k, p in part.items():
                    if k == band_types[self._band_type]:
                        _id = p['properties']['idahoImageId']
                        graph[_id] = ipe.Orthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"), **self._ortho_params())
                       
            return self._mosaic(graph)

    def _ortho_params(self):
        ortho_params = {}
        if self._proj is not None:
            ortho_params["Output Coordinate Reference System"] = self._proj
            ortho_params["Sensor Model"] = None
            ortho_params["Elevation Source"] = None
            ortho_params["Output Pixel to World Transform"] = None
        return ortho_params

    def _pansharpen_graph(self):
        pan_graph = {}
        ms_graph = {}
        for part in self.metadata['parts']:
            for k, p in part.items():
                _id = p['properties']['idahoImageId']
                if k == 'PAN':
                    pan_graph[_id] =  ipe.Orthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"), **self._ortho_params())
                else:
                    ms_graph[_id] = ipe.Orthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"), **self._ortho_params())

        pan_mosaic = self._mosaic(pan_graph, suffix='-pan')
        pan = ipe.Format(ipe.MultiplyConst(pan_mosaic['toa_reflectance-pan'], constants=json.dumps([1000])), dataType="1")
        ms_mosaic = self._mosaic(ms_graph, suffix='-ms')
        ms = ipe.Format(ipe.MultiplyConst(ms_mosaic['toa_reflectance-ms'], constants=json.dumps([1000]*8)), dataType="1")
        return {'ms_mosaic': ms_mosaic, 'pan_mosiac': pan_mosaic, 'pansharpened': ipe.LocallyProjectivePanSharpen(ms, pan)}


    def _toa(self, meta, _id, suffix=''):
        gains_offsets = calc_toa_gain_offset(meta['properties'])
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
        ortho = ipe.Orthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"))
        radiance = ipe.AddConst(ipe.MultiplyConst(ipe.Format(ortho, dataType="4"), constants=radiance_scales), constants=radiance_offsets)
        return ipe.MultiplyConst(radiance, constants=reflectance_scales)
        

    def _mosaic(self, graph, suffix=''):
        mosaic = ipe.GeospatialMosaic(*graph.values())
        idaho_id = graph.keys()[0]
        meta = requests.get('http://idaho.timbr.io/{}.json'.format(idaho_id)).json()
        gains_offsets = calc_toa_gain_offset(meta['properties'])
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
        radiance = ipe.AddConst(ipe.MultiplyConst(ipe.Format(mosaic, dataType="4"), constants=radiance_scales), constants=radiance_offsets)
        toa = ipe.MultiplyConst(radiance, constants=reflectance_scales)
        graph.update({"mosaic{}".format(suffix): mosaic, "radiance{}".format(suffix): radiance, "toa_reflectance{}".format(suffix): toa})
        return graph
