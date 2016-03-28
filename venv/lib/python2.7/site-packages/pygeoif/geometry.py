# -*- coding: utf-8 -*-
#
#   Copyright (C) 2012  Christian Ledermann
#
#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.

#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.

#   You should have received a copy of the GNU Lesser General Public License
#   along with this library; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import re


class _GeoObject(object):
    """Base Class for Geometry, Feature, and FeatureCollection"""

    def __repr__(self):
        if self._type == 'Point':
            return("Point({0}, {1})".format(self.x, self.y))
        elif self._type == 'LineString':
            instance = "LineString Instance"
            qty = len(self.coords)
            return "<{0} {1} Coords>".format(instance, qty)
        elif self._type == 'LinearRing':
            instance = "LinearRing Instance"
            qty = len(self.coords)
            return "<{0} {1} Coords>".format(instance, qty)
        elif self._type == 'Polygon':
            instance = "Polygon Instance"
            inter_qty = len(self._interiors)
            exter_qty = len(self._exterior.coords)
            return "<{0} {1} Interior {2} Exterior>".format(
                instance, inter_qty, exter_qty)
        elif self._type == 'MultiPoint':
            instance = "MultiPoint Instance"
            qty = len(self)
            return "<{0} {1} Points>".format(instance, qty)
        elif self._type == 'MultiLineString':
            instance = "MultiLineString Instance"
            qty = len(self)
            bounds = self.bounds
            return "<{0} {1} Lines {2} bbox>".format(instance, qty, bounds)
        elif self._type == 'MultiPolygon':
            instance = "MultiPolygon Instance"
            qty = len(self)
            bounds = self.bounds
            return "<{0} {1} Polygons {2} bbox>".format(instance, qty, bounds)
        elif self._type == 'GeometryCollection':
            instance = "GeometryCollection Instance"
            qty = len(self)
            bounds = self.bounds
            return "<{0} {1} Geometries {2} bbox>".format(
                instance, qty, bounds)
        elif self._type == 'Feature':
            instance = "Feature Instance"
            geometry = self._geometry._type
            properties = len(self._properties)
            return "<{0} {1} geometry {2} properties>".format(instance,
                                                              geometry,
                                                              properties)
        elif self._type == 'FeatureCollection':
            instance = 'FeatureCollection Instance'
            qty = len(self)
            bounds = self.bounds
            return '<{0} {1} Features {2} bbox>'.format(instance, qty, bounds)

        else:
            return object.__repr__(self)


class _Geometry(_GeoObject):
    """
    Base Class for geometry objects.

    Inherits from GeoObject
    """
    _type = None
    _coordinates = ()

    @property
    def __geo_interface__(self):
        return {
            'type': self._type,
            'coordinates': tuple(self._coordinates)
            }

    def __str__(self):
        return self.to_wkt()

    @property
    def wkt(self):
        return self.to_wkt()

    def to_wkt(self):
        raise NotImplementedError

    @property
    def geom_type(self):
        return self._type

    @property
    def bounds(self):
        raise NotImplementedError


class Feature(_GeoObject):
    """
    Aggregates a geometry instance with associated user-defined properties.

    Attributes
    ~~~~~~~~~~~
    geometry : object
        A geometry instance
    properties : dict
        A dictionary linking field keys with values
        associated with geometry instance

    Example
    ~~~~~~~~

     >>> p = Point(1.0, -1.0)
     >>> props = {'Name': 'Sample Point', 'Other': 'Other Data'}
     >>> a = Feature(p, props)
     >>> a.properties
     {'Name': 'Sample Point', 'Other': 'Other Data'}
      >>> a.properties['Name']
     'Sample Point'
      """

    _type = 'Feature'
    _properties = None
    _geometry = None
    _feature_id = None

    def __init__(self, geometry, properties={}, feature_id=None, *kwargs):
        self._geometry = geometry
        self._properties = properties
        self._feature_id = feature_id

    @property
    def id(self):
        return self._feature_id

    @property
    def geometry(self):
        return self._geometry

    @property
    def properties(self):
        return self._properties

    @property
    def __geo_interface__(self):
        geo_interface = {'type': self._type,
                         'geometry': self._geometry.__geo_interface__,
                         'properties': self._properties
                         }
        if self._feature_id is None:
            return geo_interface
        else:
            geo_interface['id'] = self._feature_id
            return geo_interface


class Point(_Geometry):
    """
    A zero dimensional geometry

    A point has zero length and zero area.

    Attributes
    ----------
    x, y, z : float
        Coordinate values

    Example
    -------

      >>> p = Point(1.0, -1.0)
      >>> print p
      POINT (1.0000000000000000 -1.0000000000000000)
      >>> p.y
      -1.0
      >>> p.x
      1.0
    """

    _type = 'Point'
    _coordinates = None

    def __init__(self, *args):
        """
        Parameters
        ----------
        There are 2 cases:

        1) 1 parameter: this must satisfy the __geo_interface__ protocol
            or be a tuple or list of x, y, [z]
        2) 2 or 3 parameters: x, y, [z] : float
            Easting, northing, and elevation.
        """
        self._coordinates = ()
        if len(args) == 1:
            if hasattr(args[0], '__geo_interface__'):
                if args[0].__geo_interface__['type'] == 'Point':
                    self._coordinates = list(
                        args[0].__geo_interface__['coordinates']
                    )
                else:
                    raise TypeError
            else:
                if isinstance(args[0], (list, tuple)):
                    if 2 <= len(args[0]) <= 3:
                        coords = [float(x) for x in args[0]]
                        self._coordinates = coords
                    else:
                        raise TypeError
                else:
                    raise TypeError
        elif 2 <= len(args) <= 3:
            coords = [float(x) for x in args]
            self._coordinates = coords
        else:
            raise ValueError

    @property
    def x(self):
        """Return x coordinate."""
        return self._coordinates[0]

    @property
    def y(self):
        """Return y coordinate."""
        return self._coordinates[1]

    @property
    def z(self):
        """Return z coordinate."""
        if len(self._coordinates) != 3:
            raise ValueError("This point has no z coordinate.")
        return self._coordinates[2]

    @property
    def coords(self):
        return (tuple(self._coordinates),)

    @coords.setter
    def coords(self, coordinates):
        if isinstance(coordinates, (list, tuple)):
            if 2 <= len(coordinates) <= 3:
                coords = [float(x) for x in coordinates]
                self._coordinates = coords
            else:
                raise TypeError
        else:
            raise TypeError

    @property
    def bounds(self):
        return tuple(self._coordinates + self._coordinates)

    def to_wkt(self):
        coords = str(tuple(self._coordinates)).replace(',', '')
        return self._type.upper() + ' ' + coords


class LineString(_Geometry):
    """
    A one-dimensional figure comprising one or more line segments

    A LineString has non-zero length and zero area. It may approximate a curve
    and need not be straight. Unlike a LinearRing, a LineString is not closed.

        Attributes
    ----------
    geoms : sequence
        A sequence of Points
    """
    _type = 'LineString'
    _geoms = None

    @property
    def __geo_interface__(self):
        if self._type and self._geoms:
            return {
                'type': self._type,
                'coordinates': tuple(self.coords)
            }

    def __init__(self, coordinates):
        """
        Parameters
        ----------
        coordinates : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples
            or a sequence of Points or
            an object that provides the __geo_interface__, including another
            instance of LineString.

        Example
        -------
        Create a line with two segments

          >>> a = LineString([[0, 0], [1, 0], [1, 1]])
        """
        self._geoms = []
        if hasattr(coordinates, '__geo_interface__'):
            gi = coordinates.__geo_interface__
            if (gi['type'] == 'LineString') or (gi['type'] == 'LinearRing'):
                self.coords = gi['coordinates']
            elif gi['type'] == 'Polygon':
                raise TypeError('Use poligon.exterior or polygon.interiors[x]')
            else:
                raise TypeError
        elif isinstance(coordinates, (list, tuple)):
            geoms = []
            for coord in coordinates:
                p = Point(coord)
                l = len(p.coords[0])
                if geoms:
                    if l != l2:
                        raise ValueError
                l2 = l
                geoms.append(p)
            self._geoms = geoms
        else:
            raise TypeError

    @property
    def geoms(self):
        return tuple(self._geoms)

    @property
    def coords(self):
        coordinates = []
        for point in self.geoms:
            coordinates.append(tuple(point.coords[0]))
        return tuple(coordinates)

    @coords.setter
    def coords(self, coordinates):
        if isinstance(coordinates, (list, tuple)):
            geoms = []
            for coord in coordinates:
                p = Point(coord)
                l = len(p.coords[0])
                if geoms:
                    if l != l2:
                        raise ValueError
                l2 = l
                geoms.append(p)
            self._geoms = geoms
        else:
            raise ValueError

    def to_wkt(self):
        wc = [' '.join([str(x) for x in c]) for c in self.coords]
        return self._type.upper() + ' (' + ', '.join(wc) + ')'

    @property
    def bounds(self):
        if self.coords:
            minx = self.coords[0][0]
            miny = self.coords[0][1]
            maxx = self.coords[0][0]
            maxy = self.coords[0][1]
            for coord in self.coords:
                minx = min(coord[0], minx)
                miny = min(coord[1], miny)
                maxx = max(coord[0], maxx)
                maxy = max(coord[1], maxy)
            return (minx, miny, maxx, maxy)


class LinearRing(LineString):
    """
    A closed one-dimensional geometry comprising one or more line segments

    A LinearRing that crosses itself or touches itself at a single point is
    invalid and operations on it may fail.

    A Linear Ring is self closing
    """
    _type = 'LinearRing'

    def __init__(self, coordinates=None):
        super(LinearRing, self).__init__(coordinates)
        if self._geoms[0].coords != self._geoms[-1].coords:
            self._geoms.append(self._geoms[0])

    @property
    def coords(self):
        if self._geoms[0].coords == self._geoms[-1].coords:
            coordinates = []
            for point in self.geoms:
                coordinates.append(tuple(point.coords[0]))
            return tuple(coordinates)
        else:
            raise ValueError

    @coords.setter
    def coords(self, coordinates):
        LineString.coords.fset(self, coordinates)
        if self._geoms[0].coords != self._geoms[-1].coords:
            self._geoms.append(self._geoms[0])

    def _set_orientation(self, clockwise=False):
        """ sets the orientation of the coordinates in
        clockwise or counterclockwise (default) order"""
        area = signed_area(self.coords)
        if (area >= 0) and clockwise:
            self._geoms = self._geoms[::-1]
        elif (area < 0) and not clockwise:
            self._geoms = self._geoms[::-1]


class Polygon(_Geometry):
    """
    A two-dimensional figure bounded by a linear ring

    A polygon has a non-zero area. It may have one or more negative-space
    "holes" which are also bounded by linear rings. If any rings cross each
    other, the geometry is invalid and operations on it may fail.

    Attributes
    ----------
    exterior : LinearRing
        The ring which bounds the positive space of the polygon.
    interiors : sequence
        A sequence of rings which bound all existing holes.
    """
    _type = 'Polygon'
    _exterior = None
    _interiors = None

    @property
    def __geo_interface__(self):
        if self._interiors:
            coords = [self.exterior.coords]
            for hole in self.interiors:
                coords.append(hole.coords)
            return {
                'type': self._type,
                'coordinates': tuple(coords)
            }
        elif self._exterior:
            return {
                'type': self._type,
                'coordinates': (self._exterior.coords,)
            }

    def __init__(self, shell, holes=None):
        """
        Parameters
        ----------
        shell : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples
            or a LinearRing.
            If a Polygon is passed as shell the holes parameter will be
            ignored
        holes : sequence
            A sequence of objects which satisfy the same requirements as the
            shell parameters above

        Example
        -------
        Create a square polygon with no holes

          >>> coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
          >>> polygon = Polygon(coords)
        """
        if holes:
            self._interiors = []
            for hole in holes:
                if hasattr(hole, '__geo_interface__'):
                    gi = hole.__geo_interface__
                    if gi['type'] == 'LinearRing':
                        self._interiors.append(LinearRing(hole))
                    else:
                        raise TypeError
                elif isinstance(hole, (list, tuple)):
                    self._interiors.append(LinearRing(hole))
        else:
            self._interiors = []
        if hasattr(shell, '__geo_interface__'):
            gi = shell.__geo_interface__
            if gi['type'] == 'LinearRing':
                self._exterior = LinearRing(shell)
            elif gi['type'] == 'Polygon':
                self._exterior = LinearRing(gi['coordinates'][0])
                if len(gi['coordinates']) > 1:
                    # XXX should the holes passed if any be ignored
                    # or added to the polygon?
                    self._interiors = []
                    for hole in gi['coordinates'][1:]:
                        self._interiors.append(LinearRing(hole))
            else:
                raise TypeError
        elif isinstance(shell, (list, tuple)):
            assert isinstance(shell[0], (list, tuple))
            if isinstance(shell[0][0], (list, tuple)):
                # we passed shell and holes in the first parameter
                self._exterior = LinearRing(shell[0])
                if len(shell) > 1:
                    for hole in shell[1:]:
                        self._interiors.append(LinearRing(hole))
            else:
                self._exterior = LinearRing(shell)
        else:
            raise TypeError

    @property
    def exterior(self):
        if self._exterior is not None:
            return self._exterior

    @property
    def interiors(self):
        if self._exterior is not None:
            if self._interiors:
                for interior in self._interiors:
                    yield interior

    @property
    def bounds(self):
        if self.exterior:
            return self.exterior.bounds

    def to_wkt(self):
        ext = [' '.join([str(x) for x in c]) for c in self.exterior.coords]
        ec = ('(' + ', '.join(ext) + ')')
        ic = ''
        for interior in self.interiors:
            ic += ',(' + ', '.join(
                [' '.join([str(x) for x in c]) for c in interior.coords]
            ) + ')'
        return self._type.upper() + '(' + ec + ic + ')'

    def _set_orientation(self, clockwise=False, exterior=True, interiors=True):
        """ sets the orientation of the coordinates in
        clockwise or counterclockwise (default) order"""
        if exterior:
            self.exterior._set_orientation(clockwise)
        if interiors:
            for interior in self.interiors:
                interior._set_orientation(clockwise)


class MultiPoint(_Geometry):
    """A collection of one or more points

    Attributes
    ----------
    geoms : sequence
        A sequence of Points
    """

    _geoms = None
    _type = 'MultiPoint'

    @property
    def __geo_interface__(self):
        return {
            'type': self._type,
            'coordinates': tuple([g.coords[0] for g in self._geoms])
        }

    def __init__(self, points):
        """
        Parameters
        ----------
        points : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples or a
            sequence of objects that implement the __geo_interface__,
            including instaces of Point.

        Example
        -------
        Construct a 2 point collection

          >>> ob = MultiPoint([[0.0, 0.0], [1.0, 2.0]])
          >>> len(ob.geoms)
          2
          >>> type(ob.geoms[0]) == Point
          True
        """
        self._geoms = []
        if isinstance(points, (list, tuple)):
            for point in points:
                if hasattr(point, '__geo_interface__'):
                    self._from_geo_interface(point)
                elif isinstance(point, (list, tuple)):
                    p = Point(point)
                    self._geoms.append(p)
                else:
                    raise TypeError
        elif hasattr(points, '__geo_interface__'):
            self._from_geo_interface(points)
        else:
            raise TypeError

    def _from_geo_interface(self, point):
        gi = point.__geo_interface__
        if gi['type'] == 'Point':
            p = Point(point)
            self._geoms.append(p)
        elif gi['type'] == 'LinearRing' or gi['type'] == 'LineString':
            l = LineString(point)
            for coord in l.coords:
                p = Point(coord)
                self._geoms.append(p)
        elif gi['type'] == 'Polygon':
            p = Polygon(point)
            for coord in p.exterior.coords:
                p1 = Point(coord)
                self._geoms.append(p1)
            for interior in p.interiors:
                for coord in interior.coords:
                    p1 = Point(coord)
                    self._geoms.append(p1)
        else:
            raise TypeError

    @property
    def geoms(self):
        return tuple(self._geoms)

    @property
    def bounds(self):
        if self._geoms:
            minx = self.geoms[0].coords[0][0]
            miny = self.geoms[0].coords[0][1]
            maxx = self.geoms[0].coords[0][0]
            maxy = self.geoms[0].coords[0][1]
            for geom in self.geoms:
                minx = min(geom.coords[0][0], minx)
                miny = min(geom.coords[0][1], miny)
                maxx = max(geom.coords[0][0], maxx)
                maxy = max(geom.coords[0][1], maxy)
            return (minx, miny, maxx, maxy)

    def unique(self):
        """ Make Points unique, delete duplicates """
        coords = [geom.coords for geom in self.geoms]
        self._geoms = [Point(coord[0]) for coord in set(coords)]

    def to_wkt(self):
        wc = [' '.join([str(x) for x in c.coords[0]]) for c in self.geoms]
        return self._type.upper() + '(' + ', '.join(wc) + ')'

    def __len__(self):
        if self._geoms:
            return len(self._geoms)
        else:
            return 0


class MultiLineString(_Geometry):
    """
    A collection of one or more line strings

    A MultiLineString has non-zero length and zero area.

    Attributes
    ----------
    geoms : sequence
        A sequence of LineStrings
    """
    _geoms = None
    _type = 'MultiLineString'

    @property
    def __geo_interface__(self):
        return {
            'type': self._type,
            'coordinates': tuple(
                tuple(c for c in g.coords) for g in self.geoms
            )
        }

    def __init__(self, lines):
        """
        Parameters
        ----------
        lines : sequence
            A sequence of line-like coordinate sequences or objects that
            provide the __geo_interface__, including instances of
            LineString.

        Example
        -------
        Construct a collection containing one line string.

          >>> lines = MultiLineString( [[[0.0, 0.0], [1.0, 2.0]]] )
        """
        self._geoms = []
        if isinstance(lines, (list, tuple)):
            for line in lines:
                l = LineString(line)
                self._geoms.append(l)
        elif hasattr(lines, '__geo_interface__'):
            gi = lines.__geo_interface__
            if gi['type'] == 'LinearRing' or gi['type'] == 'LineString':
                l = LineString(gi['coordinates'])
                self._geoms.append(l)
            elif gi['type'] == 'MultiLineString':
                for line in gi['coordinates']:
                    l = LineString(line)
                    self._geoms.append(l)
            else:
                raise TypeError
        else:
            raise TypeError

    @property
    def geoms(self):
        return tuple(self._geoms)

    @property
    def bounds(self):
        if self._geoms:
            minx = self.geoms[0].bounds[0]
            miny = self.geoms[0].bounds[1]
            maxx = self.geoms[0].bounds[2]
            maxy = self.geoms[0].bounds[3]
            for geom in self.geoms:
                minx = min(geom.bounds[0], minx)
                miny = min(geom.bounds[1], miny)
                maxx = max(geom.bounds[2], maxx)
                maxy = max(geom.bounds[3], maxy)
            return (minx, miny, maxx, maxy)

    def to_wkt(self):
        wc = '(' + ', '.join(
            [' '.join([str(x) for x in c]) for c in self.geoms[0].coords]
        ) + ')'
        for lx in self.geoms[1:]:
            wc += ',(' + ', '.join(
                [' '.join([str(x) for x in c]) for c in lx.coords]
            ) + ')'
        return self._type.upper() + '(' + wc + ')'

    def __len__(self):
        if self._geoms:
            return len(self._geoms)
        else:
            return 0


class MultiPolygon(_Geometry):
    """A collection of one or more polygons

    If component polygons overlap the collection is `invalid` and some
    operations on it may fail.

    Attributes
    ----------
    geoms : sequence
        A sequence of `Polygon` instances
    """
    _geoms = None
    _type = 'MultiPolygon'

    @property
    def __geo_interface__(self):
        allcoords = []
        for geom in self.geoms:
            coords = []
            coords.append(tuple(geom.exterior.coords))
            for hole in geom.interiors:
                coords.append(tuple(hole.coords))
            allcoords.append(tuple(coords))
        return {
            'type': self._type,
            'coordinates': tuple(allcoords)
        }

    def __init__(self, polygons):
        """
        Parameters
        ----------
        polygons : sequence
            A sequence of (shell, holes) tuples where shell is the sequence
            representation of a linear ring (see linearring.py) and holes is
            a sequence of such linear rings

        Example
        -------
        Construct a collection from a sequence of coordinate tuples

          >>> ob = MultiPolygon([
          ...     (
          ...     ((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
          ...     [((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))]
          ...)
          ...])
          >>> len(ob.geoms)
          1
          >>> type(ob.geoms[0]) == Polygon
          True
        """
        self._geoms = []
        if isinstance(polygons, (list, tuple)):
            for polygon in polygons:
                if isinstance(polygon, (list, tuple)):
                    p = Polygon(polygon[0], polygon[1])
                    self._geoms.append(p)
                elif hasattr(polygon, '__geo_interface__'):
                    gi = polygon.__geo_interface__
                    p = Polygon(polygon)
                    self._geoms.append(p)
                else:
                    raise ValueError
        elif hasattr(polygons, '__geo_interface__'):
            gi = polygons.__geo_interface__
            if gi['type'] == 'Polygon':
                p = Polygon(polygons)
                self._geoms.append(p)
            elif gi['type'] == 'MultiPolygon':
                for coords in gi['coordinates']:
                    self._geoms.append(Polygon(coords[0], coords[1:]))
            else:
                raise TypeError
        else:
            raise ValueError

    @property
    def geoms(self):
        return tuple(self._geoms)

    @property
    def bounds(self):
        if self._geoms:
            minx = self.geoms[0].bounds[0]
            miny = self.geoms[0].bounds[1]
            maxx = self.geoms[0].bounds[2]
            maxy = self.geoms[0].bounds[3]
            for geom in self.geoms:
                minx = min(geom.bounds[0], minx)
                miny = min(geom.bounds[1], miny)
                maxx = max(geom.bounds[2], maxx)
                maxy = max(geom.bounds[3], maxy)
            return (minx, miny, maxx, maxy)

    def to_wkt(self):
        pc = ''
        for geom in self.geoms:
            ec = '(' + ', '.join(
                [' '.join([str(x) for x in c]) for c in geom.exterior.coords]
            ) + ')'
            ic = ''
            for interior in geom.interiors:
                ic += ',(' + ', '.join(
                    [' '.join([str(x) for x in c]) for c in interior.coords]
                ) + ')'
            pc += '(' + ec + ic + ')'
        return self._type.upper() + '(' + pc + ')'

    def _set_orientation(self, clockwise=False, exterior=True, interiors=True):
        """ sets the orientation of the coordinates in
        clockwise or counterclockwise (default) order for all
        contained polygons"""
        for geom in self.geoms:
            geom._set_orientation(clockwise, exterior, interiors)

    def __len__(self):
        if self._geoms:
            return len(self._geoms)
        else:
            return 0


class GeometryCollection(_Geometry):
    """A heterogenous collection of geometries (Points, LineStrings,
       LinearRings, and Polygons)

    Attributes
    ----------
    geoms : sequence
        A sequence of geometry instances

    Please note:
    GEOMETRYCOLLECTION isn't supported by the Shapefile format. And this sub-
    class isn't generally supported by ordinary GIS sw (viewers and so on). So
    it's very rarely used in the real GIS professional world.

    Example
    -------

    Initialize Geometries and construct a GeometryCollection

    >>> from pygeoif import geometry
    >>> p = geometry.Point(1.0, -1.0)
    >>> p2 = geometry.Point(1.0, -1.0)
    >>> geoms = [p, p2]
    >>> c = geometry.GeometryCollection(geoms)
    >>> c.__geo_interface__
    {'type': 'GeometryCollection',
    'geometries': [{'type': 'Point', 'coordinates': (1.0, -1.0)},
    {'type': 'Point', 'coordinates': (1.0, -1.0)}]}
    """
    _type = 'GeometryCollection'
    _geoms = None

    _allowed_geomtries = (Point, LineString, LinearRing, Polygon)

    @property
    def __geo_interface__(self):
        gifs = []
        for geom in self._geoms:
            gifs.append(geom.__geo_interface__)
        return {'type': self._type, 'geometries': gifs}

    def __init__(self, geometries):
        self._geoms = []
        if isinstance(geometries, (list, tuple)):
            for geometry in geometries:
                if isinstance(geometry, self._allowed_geomtries):
                    self._geoms.append(geometry)
                elif isinstance(as_shape(geometry), self._allowed_geomtries):
                    self._geoms.append(as_shape(geometry))
                else:
                    raise ValueError
        else:
            raise TypeError

    @property
    def geoms(self):
        for geom in self._geoms:
            if isinstance(geom, self._allowed_geomtries):
                yield geom
            else:
                raise ValueError("Illegal geometry type.")

    @property
    def bounds(self):
        if self._geoms:
            minx = self._geoms[0].bounds[0]
            miny = self._geoms[0].bounds[1]
            maxx = self._geoms[0].bounds[2]
            maxy = self._geoms[0].bounds[3]
            for geom in self.geoms:
                minx = min(geom.bounds[0], minx)
                miny = min(geom.bounds[1], miny)
                maxx = max(geom.bounds[2], maxx)
                maxy = max(geom.bounds[3], maxy)
            return (minx, miny, maxx, maxy)

    def to_wkt(self):
        wkts = []
        for geom in self.geoms:
            wkts.append(geom.to_wkt())
        return 'GEOMETRYCOLLECTION (%s)' % ', '.join(wkts)

    def __len__(self):
        if self._geoms:
            return len(self._geoms)
        else:
            return 0

    def __iter__(self):
        return iter(self._geoms)


class FeatureCollection(_GeoObject):
    """A heterogenous collection of Features

    Attributes
    ----------
    features : sequence
        A sequence of feature instances


    Example
    -------

    >>> from pygeoif import geometry
    >>> p = geometry.Point(1.0, -1.0)
    >>> props = {'Name': 'Sample Point', 'Other': 'Other Data'}
    >>> a = geometry.Feature(p, props)
    >>> p2 = geometry.Point(1.0, -1.0)
    >>> props2 = {'Name': 'Sample Point2', 'Other': 'Other Data2'}
    >>> b = geometry.Feature(p2, props2)
    >>> features = [a, b]
    >>> c = geometry.FeatureCollection(features)
    >>> c.__geo_interface__
    {'type': 'FeatureCollection',
     'features': [{'geometry': {'type': 'Point', 'coordinates': (1.0, -1.0)},
     'type': 'Feature',
     'properties': {'Other': 'Other Data', 'Name': 'Sample Point'}},
    {'geometry': {'type': 'Point', 'coordinates': (1.0, -1.0)},
     'type': 'Feature',
     'properties': {'Other': 'Other Data2', 'Name': 'Sample Point2'}}]}
    """
    _type = 'FeatureCollection'
    _features = None

    @property
    def __geo_interface__(self):
        gifs = []
        for feature in self._features:
            gifs.append(feature.__geo_interface__)
        return {'type': self._type, 'features': gifs}

    def __init__(self, features):
        self._features = []
        if isinstance(features, (list, tuple)):
            for feature in features:
                if isinstance(feature, Feature):
                    self._features.append(feature)
                else:
                    raise ValueError
        else:
            raise TypeError

    @property
    def features(self):
        for feature in self._features:
            if isinstance(feature, Feature):
                yield feature
            else:
                raise ValueError("Illegal type.")

    @property
    def bounds(self):
        if self._features:
            minx = self._features[0].geometry.bounds[0]
            miny = self._features[0].geometry.bounds[1]
            maxx = self._features[0].geometry.bounds[2]
            maxy = self._features[0].geometry.bounds[3]
            for feature in self.features:
                minx = min(feature.geometry.bounds[0], minx)
                miny = min(feature.geometry.bounds[1], miny)
                maxx = max(feature.geometry.bounds[2], maxx)
                maxy = max(feature.geometry.bounds[3], maxy)
            return (minx, miny, maxx, maxy)

    def __len__(self):
        if self._features:
            return len(self._features)
        else:
            return 0

    def __iter__(self):
        return iter(self._features)


def signed_area(coords):
    """Return the signed area enclosed by a ring using the linear time
    algorithm at http://www.cgafaq.info/wiki/Polygon_Area. A value >= 0
    indicates a counter-clockwise oriented ring.
    """
    if len(coords[0]) == 2:
        xs, ys = map(list, zip(*coords))
    elif len(coords[0]) == 3:
        xs, ys, zs = map(list, zip(*coords))
    else:
        raise ValueError
    xs.append(xs[1])
    ys.append(ys[1])
    return sum(xs[i]*(ys[i+1]-ys[i-1]) for i in range(1, len(coords)))/2.0


def orient(polygon, sign=1.0):
    s = float(sign)
    rings = []
    ring = polygon.exterior
    if signed_area(ring.coords)/s >= 0.0:
        rings.append(ring.coords)
    else:
        rings.append(list(ring.coords)[::-1])
    for ring in polygon.interiors:
        if signed_area(ring.coords)/s <= 0.0:
            rings.append(ring.coords)
        else:
            rings.append(list(ring.coords)[::-1])
    return Polygon(rings[0], rings[1:])


def as_shape(geometry):
    """ creates a pygeoif geometry from an object that
    provides the __geo_interface__ or a dictionary that
    is __geo_interface__ compatible"""
    gi = None
    if isinstance(geometry, dict):
        is_geometryCollection = geometry['type'] == 'GeometryCollection'
        is_feature = geometry['type'] == 'Feature'
        if ('coordinates' in geometry) and ('type' in geometry):
            gi = geometry
        elif is_geometryCollection and 'geometries' in geometry:
            gi = geometry
        elif is_feature:
            gi = geometry
    elif hasattr(geometry, '__geo_interface__'):
        gi = geometry.__geo_interface__
    else:
        try:
            # maybe we can convert it into a valid __geo_interface__ dict
            cdict = dict(geometry)
            is_geometryCollection = cdict['type'] == 'GeometryCollection'
            if ('coordinates' in cdict) and ('type' in cdict):
                gi = cdict
            elif is_geometryCollection and 'geometries' in cdict:
                gi = cdict
        except:
            pass
    if gi:
        ft = gi['type']
        if ft == 'GeometryCollection':
            geometries = []
            for fi in gi['geometries']:
                geometries.append(as_shape(fi))
            return GeometryCollection(geometries)
        if ft == 'Feature':
            return Feature(as_shape(gi['geometry']),
                           properties=gi.get('properties', {}),
                           feature_id=gi.get('id', None))
        if ft == 'FeatureCollection':
            features = []
            for fi in gi['features']:
                features.append(as_shape(fi))
            return FeatureCollection(features)
        coords = gi['coordinates']
        if ft == 'Point':
            return Point(coords)
        elif ft == 'LineString':
            return LineString(coords)
        elif ft == 'LinearRing':
            return LinearRing(coords)
        elif ft == 'Polygon':
            return Polygon(coords)
        elif ft == 'MultiPoint':
            return MultiPoint(coords)
        elif ft == 'MultiLineString':
            return MultiLineString(coords)
        elif ft == 'MultiPolygon':
            polygons = []
            for icoords in coords:
                polygons.append(Polygon(icoords[0], icoords[1:]))
            return MultiPolygon(polygons)
        else:
            raise NotImplementedError
    else:
        raise TypeError('Object does not implement __geo_interface__')


wkt_regex = re.compile(r'^(SRID=(?P<srid>\d+);)?'
                       r'(?P<wkt>'
                       r'(?P<type>POINT|LINESTRING|LINEARRING|POLYGON|'
                       r'MULTIPOINT|MULTILINESTRING|MULTIPOLYGON|'
                       r'GEOMETRYCOLLECTION)'
                       r'[ACEGIMLONPSRUTYZ\d,\.\-\(\) ]+)$',
                       re.I
                       )

gcre = re.compile(r'POINT|LINESTRING|LINEARRING|POLYGON')

outer = re.compile("\((.+)\)")
inner = re.compile("\([^)]*\)")
mpre = re.compile("\(\((.+?)\)\)")


def from_wkt(geo_str):
    """
    Create a geometry from its WKT representation
    """

    wkt = geo_str.strip()
    wkt = ' '.join([l.strip() for l in wkt.splitlines()])
    wkt = wkt_regex.match(wkt).group('wkt')
    ftype = wkt_regex.match(wkt).group('type')
    outerstr = outer.search(wkt)
    coordinates = outerstr.group(1)
    if ftype == 'POINT':
        coords = coordinates.split()
        return Point(coords)
    elif ftype == 'LINESTRING':
        coords = coordinates.split(',')
        return LineString([c.split() for c in coords])
    elif ftype == 'LINEARRING':
        coords = coordinates.split(',')
        return LinearRing([c.split() for c in coords])
    elif ftype == 'POLYGON':
        coords = []
        for interior in inner.findall(coordinates):
            coords.append((interior[1:-1]).split(','))
        if len(coords) > 1:
            # we have a polygon with holes
            exteriors = []
            for ext in coords[1:]:
                exteriors.append([c.split() for c in ext])
        else:
            exteriors = None
        return Polygon([c.split() for c in coords[0]], exteriors)

    elif ftype == 'MULTIPOINT':
        coords1 = coordinates.split(',')
        coords = []
        for coord in coords1:
            if '(' in coord:
                coord = coord[coord.find('(') + 1: coord.rfind(')')]
            coords.append(coord.strip())
        return MultiPoint([c.split() for c in coords])
    elif ftype == 'MULTILINESTRING':
        coords = []
        for lines in inner.findall(coordinates):
            coords.append([c.split() for c in lines[1:-1].split(',')])
        return MultiLineString(coords)
    elif ftype == 'MULTIPOLYGON':
        polygons = []
        m = mpre.split(coordinates)
        for polygon in m:
            if len(polygon) < 3:
                continue
            coords = []
            for interior in inner.findall('(' + polygon + ')'):
                coords.append((interior[1:-1]).split(','))
            if len(coords) > 1:
                # we have a polygon with holes
                exteriors = []
                for ext in coords[1:]:
                    exteriors.append([c.split() for c in ext])
            else:
                exteriors = None
            polygons.append(Polygon([c.split() for c in coords[0]], exteriors))
        return MultiPolygon(polygons)
    elif ftype == 'GEOMETRYCOLLECTION':
        gc_types = gcre.findall(coordinates)
        gc_coords = gcre.split(coordinates)[1:]
        assert(len(gc_types) == len(gc_coords))
        geometries = []
        for (gc_type, gc_coord) in zip(gc_types, gc_coords):
            gc_wkt = gc_type + gc_coord[:gc_coord.rfind(')') + 1]
            geometries.append(from_wkt(gc_wkt))
        return GeometryCollection(geometries)
    else:
        raise NotImplementedError


def mapping(ob):
    return ob.__geo_interface__
