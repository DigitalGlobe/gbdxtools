from gbdxtools.vector_style_expressions import StyleExpression


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

class FillExtrusionStyle(FillStyle):

    def __init__(self, base=0, height=0, **kwargs):
        """ Creates a style entry for extruded polygons (fills)
        Args:
            opacity (float/StyleConditional/list):  the opacity of the circles (will accept either a float value or
                      a list representing a mapbox-gl conditional expression)
            color (str/StyleConditional/list): the color of the circles (will accept either an 'rgb' string, a hex
                   string, or a list representing a mapbox-gl conditional expression)
            base (int/StyleConditional): the height at which to extrude the base of the features. 
                                         must be less than or equal to the height.
            height (int/StyleConditional): the height with which to extrude features. 

        Returns:
            A circle style which can be applied to a circle layer
        """
        super(FillExtrusionStyle, self).__init__(**kwargs)
        self.base = base
        self.height = height
        self.type = 'fill-extrusion'

    def paint(self):
        """
        Renders a javascript snippet suitable for use as a mapbox-gl circle paint entry

        Returns:
            A dict that can be converted to a mapbox-gl javascript paint snippet
        """
        snippet = {
            'fill-extrusion-opacity': VectorStyle.get_style_value(self.opacity),
            'fill-extrusion-color': VectorStyle.get_style_value(self.color),
            'fill-extrusion-base': VectorStyle.get_style_value(self.base),
            'fill-extrusion-height': VectorStyle.get_style_value(self.height)
        }
        if self.translate:
            snippet['fill-extrusion-translate'] = self.translate

        return snippet

class HeatmapStyle(VectorStyle):

    def __init__(self, intensity=1, weight=1, color=None, radius=1, **kwargs):
        """ Creates a style entry for extruded polygons (fills)
        Args:
            opacity (float/StyleConditional/list):  the opacity of the circles (will accept either a float value or
                      a list representing a mapbox-gl conditional expression)
            radius (int): the radius of the circles (will accept either a float value or
                    a list representing a mapbox-gl conditional expression)
            color (str/StyleConditional/list): the color of the circles (will accept either an 'rgb' string, a hex
                   string, or a list representing a mapbox-gl conditional expression)
            intensity (int/StyleConditional): controls the intensity of the heatmap
            weight (int/StyleConditional): how much an individual point contributes to the heatmap

        Returns:
            A circle style which can be applied to a circle layer
        """
        super(HeatmapStyle, self).__init__(**kwargs)
        if color is None:
            self.color = self.default_color
        else:
            self.color = color
        self.intensity = intensity
        self.weight = weight
        self.radius = 1
        self.type = 'heatmap'

    @property
    def default_color(self):
        return [
            "interpolate",
            ["linear"], ["heatmap-density"],
            0, "rgba(0, 0, 255, 0)",
            0.1, "royalblue",
            0.3, "cyan", 
            0.5, "lime",
            0.7, "yellow",
            1, "red"
        ]

    def paint(self):
        """
        Renders a javascript snippet suitable for use as a mapbox-gl circle paint entry

        Returns:
            A dict that can be converted to a mapbox-gl javascript paint snippet
        """
        snippet = {
            'heatmap-radius': VectorStyle.get_style_value(self.radius),
            'heatmap-opacity': VectorStyle.get_style_value(self.opacity),
            'heatmap-color': VectorStyle.get_style_value(self.color),
            'heatmap-intensity': VectorStyle.get_style_value(self.intensity),
            'heatmap-weight': VectorStyle.get_style_value(self.weight)
        }

        return snippet
