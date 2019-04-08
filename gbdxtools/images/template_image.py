"""
GBDX Template Image Interface.

Contact: chris.helm@digitalglobe.com
"""
from gbdxtools.images.rda_image import RDAImage, GraphMeta
from gbdxtools.rda.graph import get_rda_graph_template, get_rda_template_metadata, VIRTUAL_RDA_URL, get_template_stats
from gbdxtools.auth import Auth
from gbdxtools.rda.util import deprecation
from gbdxtools.rda.fetch import easyfetch as load_url
from gbdxtools.rda.util import RDA_TO_DTYPE


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
        self._template_id = template_id
        self._rda_id = template_id
        self._params = kwargs 
        self._node_id = node_id
        self._interface = Auth()
        self._rda_meta = None
        self._rda_stats = None
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

    @property
    def display_stats(self):
        deprecation('The use of display_stats has been deprecated. For scaling imagery use histograms in the image metdata.')
        assert self.graph() is not None
        if self._rda_stats is None:
            self._rda_stats = get_template_stats(self._interface.gbdx_futures_session, self._rda_id, self._id, **self._params)
        return self._rda_stats

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

    @property
    def dask(self):
        token = self._interface.gbdx_connection.access_token
        _chunks = self.chunks
        _name = self.name
        img_md = self.metadata["image"]
        return {(_name, 0, y - img_md['minTileY'], x - img_md['minTileX']): (load_url, url, token, _chunks)
                for (y, x), url in self._collect_urls().items()}

    @property
    def name(self):
        return "image-{}".format(self._id)

    @property
    def chunks(self):
        img_md = self.metadata["image"]
        return (img_md["numBands"], img_md["tileYSize"], img_md["tileXSize"])

    @property
    def dtype(self):
        try:
            data_type = self.metadata["image"]["dataType"]
            return RDA_TO_DTYPE[data_type]
        except KeyError:
            raise TypeError("Metadata indicates an unrecognized data type: {}".format(data_type))

    @property
    def shape(self):
        img_md = self.metadata["image"]
        return (img_md["numBands"],
                (img_md["maxTileY"] - img_md["minTileY"] + 1)*img_md["tileYSize"],
                (img_md["maxTileX"] - img_md["minTileX"] + 1)*img_md["tileXSize"])


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
