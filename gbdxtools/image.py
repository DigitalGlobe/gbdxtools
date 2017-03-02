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

from gbdxtools.auth import Interface
from gbdxtools.ipe.util import calc_toa_gain_offset
from gbdxtools.ipe_image import IpeImage
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

    def __init__(self, cat_id, band_type="MS", node="toa_reflectance", **kwargs):
        self.interface = Interface.instance()(**kwargs)
        self.vectors = Vectors()
        self._gid = cat_id
        self._band_type = band_type
        self._node_id = node
        self._pansharpen = kwargs.get('pansharpen', False)
        self._acomp = kwargs.get('acomp', False)
        if self._pansharpen:
            self._node_id = 'pansharpened'
        self._level = kwargs.get('level', 0)

        self._ipe_id = None
        self._ipe_metadata = None
        self._ipe_graphs = self._init_graphs()

        self._bounds = self._parse_geoms(**kwargs)
        self._graph_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(self.ipe.graph())))
        self._tile_size = kwargs.get('tile_size', 256)

        self._cfg = self._config_dask(bounds=self._bounds)
        super(IpeImage, self).__init__(**self._cfg)


    def _query_vectors(self, query, aoi=None):
        if aoi is None:
            aoi = "POLYGON((-180.0 90.0,180.0 90.0,180.0 -90.0,-180.0 -90.0,-180.0 90.0))"
        return self.vectors.query(aoi, query=query)


    @property
    def metadata(self):
        # TODO this logic should be exposed as a method in the idaho class
        query = 'item_type:DigitalGlobeAcquisition AND attributes.catalogID:{}'.format(self._gid)
        props = self._query_vectors(query)
        if len(props) == 0:
            print('Could not find image metadata for the given catalog id')
            return

        geom = shape(props[0]['geometry'])
        attrs = props[0]['properties']['attributes']
        query = 'item_type:IDAHOImage AND attributes.catalogID:{}'.format(self._gid)
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

        return {'properties': attrs, 'geometry': geom}


    def aoi(self, **kwargs):
        if self._pansharpen and 'pansharpen' not in kwargs:
            kwargs['pansharpen'] = True
        return Image(self._gid, band_type=self._band_type, node=self._node_id, **kwargs)


    def _init_graphs(self):
        graph = {}
        ids = []
        if self._node_id == 'pansharpened' and self._pansharpen:
            return self._pansharpen_graph()
        else: 
            for part in self.metadata['properties']['parts']:
                for k, p in part.iteritems():
                    if k == band_types[self._band_type]:
                        _id = p['properties']['idahoImageId']
                        graph[_id] = ipe.GridOrthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"))
                       
            return self._mosaic(graph)


    def _pansharpen_graph(self):
        pan_graph = {}
        ms_graph = {}
        for part in self.metadata['properties']['parts']:
            for k, p in part.iteritems():
                _id = p['properties']['idahoImageId']
                if k == 'PAN':
                    pan_graph[_id] =  ipe.GridOrthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"))
                else:
                    ms_graph[_id] = ipe.GridOrthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"))

        pan_mosaic = self._mosaic(pan_graph, suffix='-pan')
        pan = ipe.Format(ipe.MultiplyConst(pan_mosaic['toa_reflectance-pan'], constants=json.dumps([1000])), dataType="1")
        ms_mosaic = self._mosaic(ms_graph, suffix='-ms')
        ms = ipe.Format(ipe.MultiplyConst(ms_mosaic['toa_reflectance-ms'], constants=json.dumps([1000]*8)), dataType="1")
        return {'pansharpened': ipe.LocallyProjectivePanSharpen(ms, pan)}

    def _toa(self, meta, _id, suffix=''):
        gains_offsets = calc_toa_gain_offset(meta['properties'])
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
        ortho = ipe.GridOrthorectify(ipe.IdahoRead(bucketName="idaho-images", imageId=_id, objectStore="S3"))
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
