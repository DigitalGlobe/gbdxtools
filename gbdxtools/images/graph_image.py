from __future__ import print_function
from gbdxtools.images.meta import DaskMeta 
from gbdxtools.ipe.interface import DaskProps
from gbdxtools.ipe.graph import get_ipe_graph
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.auth import Auth

class GraphMeta(DaskProps, DaskMeta):
    def __init__(self, graph_id, node_id=None, **kwargs):
        assert graph_id is not None
        self._ipe_id = graph_id
        self._node_id = node_id
        self._interface = Auth()
        self._ipe_meta = None
        self._graph = None
        self._nid = None

    @property
    def _id(self):
        if self._node_id is not None and self._nid is None:
            self._nid = self._node_id
        else:
            graph = self.graph()
            self._nid = graph["nodes"][-1]["id"]
        return self._nid

    def graph(self):
        if self._graph is None:
            self._graph = get_ipe_graph(self._interface.gbdx_connection, self._ipe_id)
        return self._graph


def GraphImage(graph, node):
    assert graph is not None
    return IpeImage(None, graph_id=graph, node_id=node)
