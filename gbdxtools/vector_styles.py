import uuid
import json

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


class VectorStyle(object):

    def __init__(self, opacity=1.0, color='rgb(255,0,0)', translate=None, **kwargs):
        self.opacity = opacity
        self.color = color
        self.translate = translate
        self.type = None

    @staticmethod
    def get_style_value(style_value):
        if isinstance(style_value, StyleExpression):
            return style_value.expression
        else:
            return style_value

    def paint(self):
        """
        Renders a javascript snippet suitable for use as a mapbox-gl style entry

        Returns:
            A dict that can be converted to a mapbox-gl javascript 'paint' snippet
        """
        raise NotImplementedError()


class CircleStyle(VectorStyle):
    """
    Applies styling to a circle layer
    """

    def __init__(self, radius=1.0, **kwargs):
        """ Creates a style entry for a circle layer
        Args:
            radius (int): the radius of the circles (will accept either a float value or
                    a list representing a mapbox-gl conditional expression)
            opacity (float):  the opacity of the circles (will accept either a float value or
                      a list representing a mapbox-gl conditional expression)
            color (str): the color of the circles (will accept either an 'rgb' string, a hex
                   string, or a list representing a mapbox-gl conditional expression)

        Returns:
            A circle style which can be applied to a circle layer
        """
        super(CircleStyle, self).__init__(**kwargs)
        self.radius = radius
        self.type = 'circle'

    def paint(self):
        """
        Renders a javascript snippet suitable for use as a mapbox-gl circle paint entry

        Returns:
            A dict that can be converted to a mapbox-gl javascript paint snippet
        """
        snippet = {
            'circle-radius': VectorStyle.get_style_value(self.radius),
            'circle-opacity': VectorStyle.get_style_value(self.opacity),
            'circle-color': VectorStyle.get_style_value(self.color)
        }
        if self.translate:
            snippet['circle-translate'] = self.translate

        return snippet


class LineStyle(VectorStyle):

    """
    Applies styling to a circle layer
    """

    def __init__(self, cap='butt', join='miter', width=1.0, gap_width=0,
                 blur=0, dasharray=None, **kwargs):
        """ Creates a style entry for a circle layer
        Args:
            cap: the line-ending style ('butt' (default), 'round', or 'square')
            join: the line-joining style ('miter' (default), 'bevel', or 'round')
            width: the width of the line in pixels
            gap_width: the width of the gap between the line and its casing in pixels
            blur: blur value in pixels
            dasharray: list of numbers indicating line widths for a dashed line
            opacity:  the opacity of the circles (will accept either a float value or
                      a list representing a mapbox-gl conditional expression)
            color: the color of the circles (will accept either an 'rgb' string, a hex
                   string, or a list representing a mapbox-gl conditional expression)

        Returns:
            A line style which can be applied to a circle layer
        """
        super(LineStyle, self).__init__(**kwargs)
        self.cap = cap
        self.join = join
        self.width = width
        self.gap_width = gap_width
        self.blur = blur
        self.dasharray = dasharray
        self.type = 'line'

    def paint(self):
        """
        Renders a javascript snippet suitable for use as a mapbox-gl line paint entry

        Returns:
            A dict that can be converted to a mapbox-gl javascript paint snippet
        """
        # TODO Figure out why i cant use some of these props
        snippet = {
            'line-opacity': VectorStyle.get_style_value(self.opacity),
            'line-color': VectorStyle.get_style_value(self.color),
            #'line-cap': self.cap,
            #'line-join': self.join,
            'line-width': VectorStyle.get_style_value(self.width),
            #'line-gap-width': self.gap_width,
            #'line-blur': self.blur,
        }
        if self.translate:
            snippet['line-translate'] = self.translate

        if self.dasharray:
            snippet['line-dasharray'] = VectorStyle.get_style_value(self.dasharray)

        return snippet


class FillStyle(VectorStyle):

    def __init__(self, color="rgb(255,0,0)", 
                       opacity=.5, 
                       outline_color=None,
                       **kwargs):
        """ Creates a style entry for a circle layer
        Args:
            opacity (float/StyleConditional/list):  the opacity of the circles (will accept either a float value or
                      a list representing a mapbox-gl conditional expression)
            color (str/StyleConditional/list): the color of the circles (will accept either an 'rgb' string, a hex
                   string, or a list representing a mapbox-gl conditional expression)
            outline_color (str/StyleConditional/list): the color of the outline

        Returns:
            A circle style which can be applied to a circle layer
        """
        super(FillStyle, self).__init__(**kwargs)
        self.outline_color = outline_color if outline_color is not None else color
        self.opacity = opacity
        self.color = color
        self.type = 'fill'

    def paint(self):
        """
        Renders a javascript snippet suitable for use as a mapbox-gl circle paint entry

        Returns:
            A dict that can be converted to a mapbox-gl javascript paint snippet
        """
        snippet = {
            'fill-opacity': VectorStyle.get_style_value(self.opacity),
            'fill-color': VectorStyle.get_style_value(self.color),
            'fill-outline-color': VectorStyle.get_style_value(self.outline_color)
        }
        if self.translate:
            snippet['fill-translate'] = self.translate

        return snippet


class StyleExpression(object):
    """
    Represents a mapbox-gl conditional for styling, knowing how
    to turn itself into the appropriate javascript for use in
    styling a layer.
    """

    def _expression_def(self):
        """
        Creates the list values which will be passed as a mapbox-gl
        conditional expression.

        Returns:
            list of values for mapbox-gl conditional
        """
        raise NotImplementedError()

    @property
    def expression(self):
        return self._expression_def()


class MatchExpression(StyleExpression):
    """
    Represents a mapbox-gl "match" conditional expression, where a set of values
    is matched against a property and styling applied based on the match.
    """

    def __init__(self, property_name=None, values=None, default_value=None):
        """
        Creates a match conditional expression, matching against the supplied property
        name in a feature.  Values to match against and the styling to apply for those
        matches are supplied in the 'values' dict.  If the feature property does not
        match any of the values provided, it will be styled with the provided default.

        Parameters:
            property_name (str): the name of the feature property to match values against
            values (dict): key/value pairs for property values and the style value to apply
            default_value (?): default value to apply when no value matches
        """
        self.property_name = property_name
        self.values = values
        self.default_value = default_value

    def _expression_def(self):
        cond = ['match', ['get', self.property_name]]
        for key in self.values:
            cond.append(key)
            cond.append(self.values[key])
        cond.append(self.default_value)
        return cond


class InterpolateExpression(StyleExpression):
    """
    Represents a mapbox-gl "interpolate" expression, creating a smooth set of results
    between provided stops for a given feature property.
    """

    def __init__(self, property_name=None, stops=None, type=None):
        """
        Creates a match conditional expression, matching against the supplied property
        name in a feature.  Values to match against and the styling to apply for those
        matches are supplied in the 'values' dict.  If the feature property does not
        match any of the values provided, it will be styled with the provided default.

        The 'type' params must be a list whose values depend on the interpolation type
        (taken from the mapbox-gl documentation):
            - ["linear"]: interpolates linearly between the pair of stops just less than
                          and just greater than the input.
            - ["exponential", base]: interpolates exponentially between the stops just less
                                     than and just greater than the input. base controls the
                                     rate at which the output increases: higher values make
                                     the output increase more towards the high end of the range. With values close to 1 the output increases linearly.
            - ["cubic-bezier", x1, y1, x2, y2]: interpolates using the cubic bezier curve
                                                defined by the given control points.

        Parameters:
            property_name (str): the name of the feature property to match values against
            stops (dict): key/value pairs for range values and the style value to apply to values in that range
            type (list): interpolation type params
        """
        self.property_name = property_name
        self.stops = stops
        self.type = type

    def _expression_def(self):
        cond = ['interpolate', self.type, ['get', self.property_name]]
        for key in sorted(self.stops):
            cond.append(key)
            cond.append(self.stops[key])
        return cond
