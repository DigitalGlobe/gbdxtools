"""
GBDX Template Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from gbdxtools.images.rda_image import RDAImage, GraphMeta
from gbdxtools.rda.interface import DaskProps
from gbdxtools.rda.graph import get_rda_graph_template, get_rda_template_metadata, VIRTUAL_RDA_URL
from gbdxtools.auth import Auth

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    xrange
except NameError:
    xrange = range

class TemplateMeta(GraphMeta):
    def __init__(self, template_id, node_id=None, **kwargs):
        assert template_id is not None
        self._template_id = template_id
        self._rda_id = template_id
        self._params = kwargs 
        self._node_id = node_id
        self._interface = Auth()
        self._rda_meta = None
        self._graph = None
        self._nid = None

    @property
    def metadata(self):
        assert self.graph() is not None
        if self._rda_meta is not None:
            return self._rda_meta
        if self._interface is not None:
            self._rda_meta = get_rda_template_metadata(self._interface.gbdx_futures_session, self._template_id, nodeId=self._id, **self._params)
        return self._rda_meta

    def graph(self):
        if self._graph is None:
            self._graph = get_rda_graph_template(self._interface.gbdx_connection, self._template_id)
        return self._graph

    def _rda_tile(self, x, y, rda_id, **kwargs):
        qs = urlencode(kwargs)
        return "{}/template/{}/tile/{}/{}?{}".format(VIRTUAL_RDA_URL, rda_id, x, y, qs) 

    def _collect_urls(self):
        img_md = self.metadata["image"]
        rda_id = self._rda_id
        _id = self._id
        return {(y, x): self._rda_tile(x, y, rda_id, nodeId=self._id, **self._params)
                for y in xrange(img_md['minTileY'], img_md["maxTileY"]+1)
                for x in xrange(img_md['minTileX'], img_md["maxTileX"]+1)}

class RDATemplateImage(object):
    '''Creates an image instance matching the template ID with the given params.

    Args:
        template_id (str): The RDA template ID
        node_id (str): the node ID to render as the image (defaults to None) 
        kwargs: Parameters needed to fill the template params

    Returns:
        image (ndarray): An image instance
    '''
    def __new__(cls, template_id, node_id=None, **kwargs):
        return RDAImage(TemplateMeta(template_id, node_id, **kwargs))
