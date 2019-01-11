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

        Args:
            property_name (str): the name of the feature property to match values against
            values (dict): key/value pairs for property values and the style value to apply
            default_value (str/float): default value to apply when no value matches
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
        Creates an interpolate expression, based on values in the supplied property
        of a feature.  Values indicating range boundaries and the styling to apply to features
        in those ranges are supplied in the 'stops' dict.

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

        Args:
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


class StepExpression(StyleExpression):
    """
    Represents a mapbox-gl "step" expression, creating discrete stepped results
    between provided stops for a given feature property.
    """

    def __init__(self, property_name=None, stops=None):
        """
        Creates a step expression, based on values in the supplied property
        of a feature.  Values indicating range boundaries and the styling to apply to features
        in those ranges are supplied in the 'stops' dict.

        Args:
            property_name (str): the name of the feature property to match values against
            stops (dict): key/value pairs for range values and the style value to apply to values in that range
        """
        self.property_name = property_name
        self.stops = stops

    def _expression_def(self):
        cond = ['step', ['get', self.property_name]]
        keys = list(sorted(self.stops))
        cond.append(self.stops[keys[0]])  # first entry must be the starting style value
        for key in keys[1:]:
            cond.append(key)
            cond.append(self.stops[key])
        return cond

class HeatmapExpression(StyleExpression):
    """
    Represents a mapbox-gl "interpolation" expression using heatmap-density for a pixel rather than a feature property
    in a heatmap layer.  Can only be used in a heatmap style's 'color' property.
    """

    def __init__(self, stops=None, type=None):
        """
        Creates an interpolation expression using heatmap-density for pixels in a heatmap layer.
        Values indicating range boundaries and the styling to apply to features in those ranges are supplied in the
        'stops' dict.

        Args:
            stops (dict): key/value pairs for range values and the style value to apply to values in that range
            type (list): interpolation type params
        """
        self.stops = stops
        self.type = type

    def _expression_def(self):
        cond = ['interpolate', self.type, ['heatmap-density']]
        for key in sorted(self.stops):
            cond.append(key)
            cond.append(self.stops[key])
        return cond

class ZoomExpression(StyleExpression):
    """
    Represents a mapbox-gl "interpolate" expression, using the zoom level as input rather than a property
    on a feature.
    """

    def __init__(self, stops=None, type=None):
        """
        Creates an interpolate expression, based on the map's current zoom level.  Values indicating range
        boundaries and the styling to apply to features in those ranges are supplied in the 'stops' dict.

        Args:
            stops (list): zoom -> value list of zooms and values at specific zooms
            type (list): interpolation type params
        """
        self.stops = stops
        self.type = type

    def _expression_def(self):
        return ['interpolate', self.type, ['zoom']] + self.stops
