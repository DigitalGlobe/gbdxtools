class VectorLayer(object):
    """ Represents a vector layer created from a geojson source, and knows how
    to render itself as javascript.
    """

    def __init__(self, styles=None, source_name="GBDX_Task_Output", source_def=None):
        """ Abstract constructor for vector layers

        Args:
            styles: list of styles for which to create layers
            source_name: name of data source
        """
        self.styles = styles
        self.source_name = source_name
        self.source_def = source_def

    def render_js(self):
        """
        Renders the list of layers to add to the map
        Returns:
            list of layer entries suitable for use in mapbox-gl 'map.addLayer()' call
        """
        layers = []
        if self.styles:
            styles = self.styles
        else:
            # nothing defined, so give them defaults
            styles = [CircleStyle(), LineStyle(), FillStyle()]

        for style in styles:
            layer = {
                'id': type(style).__name__,
                'type': style.type,
                'source': self.source_def,
                'source-layer': self.source_name,  # TODO: this only applies to tile map
                'paint': style.paint()
            }
            layers.append(layer)

        return layers


class VectorFeatureLayer(VectorLayer):
    """ Represents a vector layer created from a geojson source, and knows how
    to render itself as javascript.
    """
    def __init__(self, **kwargs):
        """ Create a new VectorLayer

        Args:
            styles: A list of style objects to be applied to the layer

        Returns:
            An instance of the VectorLayer
        """
        super(VectorFeatureLayer, self).__init__(**kwargs)
        self.source_def = 'features'
        # TODO: do we want/need to define the features used by map.addSource()?


class VectorTileLayer(VectorLayer):
    """ Represents a vector layer in a tile map, and knows how to render
    itself as javascript.
    """
    def __init__(self, url=None, **kwargs):
        """ Create a new VectorLayer

        Args:
            styles: A list of style objects to be applied to the layer

        Returns:
            An instance of the VectorLayer
        """
        super(VectorTileLayer, self).__init__(**kwargs)
        self.url = url
        self.source_def = {
            'type': 'vector',
            'tiles': [self.url]
        }


class VectorStyle(object):

    def __init__(self, opacity=1.0, color='rgb(255,0,0)', translate=None):
        self.opacity = opacity
        self.color = color
        self.translate = translate
        self.type = None

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
            radius: the radius of the circles (will accept either a float value or
                    a list representing a mapbox-gl conditional expression)
            opacity:  the opacity of the circles (will accept either a float value or
                      a list representing a mapbox-gl conditional expression)
            color: the color of the circles (will accept either an 'rgb' string, a hex
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
            'circle-radius': self.radius,
            'circle-opacity': self.opacity,
            'circle-color': self.color
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
            A circle style which can be applied to a circle layer
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
        snippet = {
            'line-opacity': self.opacity,
            'line-color': self.color,
            'line-cap': self.cap,
            'line-join': self.join,
            'line-width': self.width,
            'line-gap-width': self.gap_width,
            'line-blur': self.blur,
        }
        if self.translate:
            snippet['circle-translate'] = self.translate

        if self.dasharray:
            snippet['line-dasharray'] = self.dasharray

        return snippet


class FillStyle(VectorStyle):

    def __init__(self, outline_color='rgb(255,0,0)', **kwargs):
        """ Creates a style entry for a circle layer
        Args:
            opacity:  the opacity of the circles (will accept either a float value or
                      a list representing a mapbox-gl conditional expression)
            color: the color of the circles (will accept either an 'rgb' string, a hex
                   string, or a list representing a mapbox-gl conditional expression)
            outline_color: the color of the outline

        Returns:
            A circle style which can be applied to a circle layer
        """
        super(FillStyle, self).__init__(**kwargs)
        self.outline_color = outline_color
        self.type = 'fill'

    def paint(self):
        """
        Renders a javascript snippet suitable for use as a mapbox-gl circle paint entry

        Returns:
            A dict that can be converted to a mapbox-gl javascript paint snippet
        """
        snippet = {
            'fill-opacity': self.opacity,
            'fill-color': self.color,
            'fill-outline-color': self.outline_color
        }
        if self.translate:
            snippet['circle-translate'] = self.translate

        return snippet


