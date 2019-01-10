import uuid
import json

from gbdxtools.vector_styles import CircleStyle, LineStyle, FillStyle


class VectorLayer(object):
    """ Represents a vector layer created from a geojson source, and knows how
    to render itself as javascript.
    """

    def __init__(self, styles=None, **kwargs):
        """ Abstract constructor for vector layers

        Args:
            styles (list): list of styles for which to create layers
        """
        self.source_id = uuid.uuid4().hex
        if styles is not None:
            self.styles = styles
        else:
            # nothing defined, so give them defaults
            self.styles = [CircleStyle(**kwargs), LineStyle(**kwargs), FillStyle(**kwargs)]

    def _layer_def(self, style):
        """
        Constructs a layer def with the proper fields
            - implemented in subclasses
        Returns:
            layer (dict): a layer json dict used for adding to maps
        """
        raise NotImplementedError()

    def _datasource_def(self):
        """
        Constructs a datasource def appropriate for the layer type
            - implemented in subclasses
        Returns
            datasource (dict): a datasource json dict used for adding data to maps
        """
        raise NotImplementedError()

    @property
    def datasource(self):
        """
        Renders the datasource to add to the map, referenced by the layers
        created by this layer instance.

        Returns:
            datasource (dict): a datasource json dict used for adding data to maps
        """
        return {'id': self.source_id, 'data': self._datasource_def()}

    @property
    def layers(self):
        """
        Renders the list of layers to add to the map
        Returns:
            list of layer entries suitable for use in mapbox-gl 'map.addLayer()' call
        """
        layers = []
        layers = [self._layer_def(style) for style in self.styles]
        return layers


class VectorFeatureLayer(VectorLayer):
    """ Represents a vector layer created from a geojson source, and knows how
    to render itself as javascript.
    """
    def __init__(self, geojson, **kwargs):
        """ Create a new VectorLayer

        Args:
            geojson (dict): a list of geojson features to render
            styles (list): A list of style objects to be applied to the layer

        Returns:
            An instance of the VectorLayer
        """
        super(VectorFeatureLayer, self).__init__(**kwargs)
        self.geojson = geojson

    def _datasource_def(self):
        return {'type': 'geojson', 'data': self.geojson}

    def _layer_def(self, style):
        return {
            'id': type(style).__name__, # TODO - make this unique in the various styles
            'type': style.type,
            'source': self.source_id,
            'paint': style.paint()
        }



class VectorTileLayer(VectorLayer):
    """ Represents a vector layer in a tile map, and knows how to render
    itself as javascript.
    """
    def __init__(self, url=None, source_layer_name='GBDX_Task_Output', **kwargs):
        """ Create a new VectorLayer

        Args:
            url (str): a vector tile url template
            source_name (str): the name of the source layer in the vector tiles
            styles (list): A list of style objects to be applied to the layer

        Returns:
            An instance of the VectorLayer
        """
        super(VectorTileLayer, self).__init__(**kwargs)
        self.url = url
        self.source_layer_name = source_layer_name

    def _datasource_def(self):
        return {'type': 'vector', 'tiles': [self.url]}

    def _layer_def(self, style):
        return {
            'id': type(style).__name__, # TODO - make this unique in the various styles
            'type': style.type,
            'source': self.source_id,
            'source-layer':  self.source_layer_name,
            'paint': style.paint()
        }

class ImageLayer(object):
    """
      A layer for rendering images and image arrays to slippy maps
    """
    def __new__(self, image, coordinates):
        """ Create a new ImageLayer

        Args:
            image (str): a vector tile url template
            coordinates: the coordinate bounds (list of polygon corners) for placing the image
        Returns:
            An string of the layer definition
        """
        return json.dumps({
            "id": uuid.uuid4().hex,
            "type": "raster",
            "source": {
                "type": "image",
                "url": image,
                "coordinates": coordinates
            }
        })

