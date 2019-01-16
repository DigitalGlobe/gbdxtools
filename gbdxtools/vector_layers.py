import uuid
import json

from gbdxtools.vector_styles import CircleStyle, LineStyle, FillStyle


class VectorLayer(object):
    """ Abstract constructor for a vector layer knowing how to render itself as javascript.

        Args:
            styles (list): list of styles for which to create layers
    """

    def __init__(self, styles=None, **kwargs):
        self.source_id = uuid.uuid4().hex
        if styles is not None:
            self.styles = styles
        else:
            # nothing defined, so give them defaults
            self.styles = [CircleStyle(**kwargs), LineStyle(**kwargs), FillStyle(**kwargs)]

    def _layer_def(self, style):
        """ Constructs a layer def with the proper fields
            - implemented in subclasses

            Returns:
                layer (dict): a layer json dict used for adding to maps
        """
        raise NotImplementedError()

    def _datasource_def(self):
        """ Constructs a datasource def appropriate for the layer type
            - implemented in subclasses

            Returns
                datasource (dict): a datasource json dict used for adding data to maps
        """
        raise NotImplementedError()

    @property
    def datasource(self):
        """ Renders the datasource to add to the map, referenced by the layers
            created by this layer instance.

            Returns:
                datasource (dict): a datasource json dict used for adding data to maps
        """
        return {'id': self.source_id, 'data': self._datasource_def()}

    @property
    def layers(self):
        """ Renders the list of layers to add to the map.

            Returns:
                layers (list): list of layer entries suitable for use in mapbox-gl 'map.addLayer()' call
        """
        layers = [self._layer_def(style) for style in self.styles]
        return layers


class VectorGeojsonLayer(VectorLayer):
    """ Represents a vector layer created from a geojson source

        Args:
            geojson (dict): a list of geojson features to render
            styles (list): A list of style objects to be applied to the layer
    """
    def __init__(self, geojson, **kwargs):
        super(VectorGeojsonLayer, self).__init__(**kwargs)
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
    """ Represents a vector tile layer in a tile map

        Args:
            url (str): a vector tile url template
            source_name (str): the name of the source layer in the vector tiles
            styles (list): A list of style objects to be applied to the layer
    """
    def __init__(self, url=None, source_layer_name='GBDX_Task_Output', **kwargs):
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
    """ A layer for rendering images and image arrays to slippy maps

        Args:
            image (str): a vector tile url template
            coordinates: the coordinate bounds (list of polygon corners) for placing the image

        Returns:
            An string of the layer definition
    """
    def __new__(self, image, coordinates):
        return json.dumps({
            "id": uuid.uuid4().hex,
            "type": "raster",
            "source": {
                "type": "image",
                "url": image,
                "coordinates": coordinates
            }
        })

