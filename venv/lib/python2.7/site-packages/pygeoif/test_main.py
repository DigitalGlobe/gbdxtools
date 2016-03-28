# -*- coding: utf-8 -*-
import unittest
try:
    from pygeoif import geometry
except ImportError:
    import geometry


class BasicTestCase(unittest.TestCase):

    def test_Geometry(self):
        f = geometry._Geometry()
        self.assertRaises(NotImplementedError, lambda: f.bounds)
        self.assertRaises(NotImplementedError, f.to_wkt)

    def test_point(self):
        self.assertRaises(ValueError, geometry.Point)
        p = geometry.Point(0, 1)
        self.assertEqual(p.bounds, (0.0, 1.0, 0.0, 1.0))
        self.assertEqual(p.x, 0.0)
        self.assertEqual(p.y, 1.0)
        self.assertEqual(p.__geo_interface__,
                         {'type': 'Point', 'coordinates': (0.0, 1.0)})
        self.assertRaises(ValueError, lambda: p.z)
        self.assertEqual(p.coords[0], (0.0, 1.0))
        p1 = geometry.Point(0, 1, 2)
        self.assertEqual(p1.x, 0.0)
        self.assertEqual(p1.y, 1.0)
        self.assertEqual(p1.z, 2.0)
        self.assertEqual(p1.coords[0], (0.0, 1.0, 2.0))
        self.assertEqual(p1.__geo_interface__,
                         {'type': 'Point', 'coordinates': (0.0, 1.0, 2.0)})
        p2 = geometry.Point([0, 1])
        self.assertEqual(p2.x, 0.0)
        self.assertEqual(p2.y, 1.0)
        p3 = geometry.Point([0, 1, 2])
        self.assertEqual(p3.x, 0.0)
        self.assertEqual(p3.y, 1.0)
        self.assertEqual(p3.z, 2.0)
        p4 = geometry.Point(p)
        self.assertEqual(p4.x, 0.0)
        self.assertEqual(p4.y, 1.0)
        p5 = geometry.Point(p1)
        self.assertEqual(p5.x, 0.0)
        self.assertEqual(p5.y, 1.0)
        self.assertEqual(p5.z, 2.0)
        self.assertRaises(TypeError, geometry.Point, '1.0, 2.0')
        self.assertRaises(ValueError, geometry.Point, '1.0', 'a')
        self.assertRaises(TypeError, geometry.Point, (0, 1, 2, 3, 4))
        #you may also pass string values as internally they get converted
        #into floats, but this is not recommended
        p6 = geometry.Point('0', '1')
        self.assertEqual(p.__geo_interface__, p6.__geo_interface__)
        p6.coords = [0, 1, 2]
        self.assertEqual(p3.coords, p6.coords)
        self.assertRaises(TypeError, setattr, p6, 'coords', 0)
        self.assertRaises(TypeError, setattr, p6, 'coords', [0])
        f = geometry._Geometry()
        self.assertRaises(TypeError, geometry.Point, f)

    def test_linestring(self):
        l = geometry.LineString([(0, 0), (1, 1)])
        self.assertEqual(l.coords, ((0.0, 0.0), (1.0, 1.0)))
        self.assertEqual(l.coords[:1], ((0.0, 0.0),))
        self.assertEqual(l.bounds, (0.0, 0.0, 1.0, 1.0))
        self.assertEqual(l.__geo_interface__,
                         {'type': 'LineString',
                          'coordinates': ((0.0, 0.0), (1.0, 1.0))})
        self.assertEqual(l.to_wkt(), 'LINESTRING (0.0 0.0, 1.0 1.0)')
        p = geometry.Point(0, 0)
        p1 = geometry.Point(1, 1)
        p2 = geometry.Point(2, 2)
        l1 = geometry.LineString([p, p1, p2])
        self.assertEqual(l1.coords, ((0.0, 0.0), (1.0, 1.0), (2.0, 2.0)))
        l2 = geometry.LineString(l1)
        self.assertEqual(l2.coords, ((0.0, 0.0), (1.0, 1.0), (2.0, 2.0)))
        l.coords = l2.coords
        self.assertEqual(l.__geo_interface__, l2.__geo_interface__)
        self.assertRaises(ValueError, geometry.LineString, [(0, 0, 0), (1, 1)])
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25),
                 (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        po = geometry.Polygon(ext, [int_1, int_2])
        self.assertRaises(TypeError, geometry.LineString, po)
        pt = geometry.Point(0, 1)
        self.assertRaises(TypeError, geometry.LineString, pt)
        self.assertRaises(TypeError, geometry.LineString, 0)
        self.assertRaises(ValueError, setattr, l2, 'coords',
                          ((0, 0), (1, 1, 1)))
        self.assertRaises(ValueError, setattr, l2, 'coords', 0)

    def test_linearring(self):
        r = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        self.assertEqual(r.coords, ((0, 0), (1, 1), (1, 0), (0, 0)))
        self.assertEqual(r.bounds, (0.0, 0.0, 1.0, 1.0))
        l = geometry.LineString(r)
        self.assertEqual(l.coords, ((0, 0), (1, 1), (1, 0), (0, 0)))
        self.assertEqual(r.__geo_interface__, {'type': 'LinearRing',
                                               'coordinates': ((0.0, 0.0),
                                                               (1.0, 1.0),
                                                               (1.0, 0.0),
                                                               (0.0, 0.0))})
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25),
                 (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        p = geometry.Polygon(ext, [int_1, int_2])
        self.assertRaises(TypeError, geometry.LinearRing, p)
        # A LinearRing is self closing
        r2 = geometry.LinearRing([(0, 0), (1, 1), (1, 0)])
        self.assertEqual(r.__geo_interface__, r2.__geo_interface__)
        r3 = geometry.LinearRing(int_1)
        r3.coords = [(0, 0), (1, 1), (1, 0)]
        self.assertEqual(r.__geo_interface__, r3.__geo_interface__)

    def test_polygon(self):
        p = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        self.assertEqual(p.exterior.coords, ((0.0, 0.0), (1.0, 1.0),
                                            (1.0, 0.0), (0.0, 0.0)))
        self.assertEqual(list(p.interiors), [])
        self.assertEqual(p.__geo_interface__, {'type': 'Polygon',
                                               'coordinates': (((0.0, 0.0),
                                                                (1.0, 1.0),
                                                                (1.0, 0.0),
                                                                (0.0, 0.0)),)})
        self.assertEqual(p.bounds, (0.0, 0.0, 1.0, 1.0))
        r = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        p1 = geometry.Polygon(r)
        self.assertEqual(p1.exterior.coords, r.coords)
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        ph1 = geometry.Polygon(e, [i])
        self.assertEqual(ph1.__geo_interface__,
                         geometry.as_shape(ph1).__geo_interface__)
        self.assertEqual(ph1.exterior.coords, tuple(e))
        self.assertEqual(list(ph1.interiors)[0].coords, tuple(i))
        self.assertEqual(ph1.__geo_interface__, {'type': 'Polygon',
                                                 'coordinates': (((0.0, 0.0),
                                                                  (0.0, 2.0),
                                                                  (2.0, 2.0),
                                                                  (2.0, 0.0),
                                                                  (0.0, 0.0)),
                                                                 ((1.0, 0.0),
                                                                  (0.5, 0.5),
                                                                  (1.0, 1.0),
                                                                  (1.5, 0.5),
                                                                  (1.0, 0.0)))
                                                 }
                         )
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25),
                 (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        ph2 = geometry.Polygon(ext, [int_1, int_2])
        self.assertEqual(ph2.exterior.coords, tuple(ext))
        self.assertEqual(list(ph2.interiors)[0].coords, tuple(int_1))
        self.assertEqual(list(ph2.interiors)[1].coords, tuple(int_2))
        self.assertEqual(ph2.__geo_interface__, {'type': 'Polygon',
                                                 'coordinates': (((0.0, 0.0),
                                                                  (0.0, 2.0),
                                                                  (2.0, 2.0),
                                                                  (2.0, 0.0),
                                                                  (0.0, 0.0)),
                                                                 ((0.5, 0.25),
                                                                  (1.5, 0.25),
                                                                  (1.5, 1.25),
                                                                  (0.5, 1.25),
                                                                  (0.5, 0.25)),
                                                                 ((0.5, 1.25),
                                                                  (1.0, 1.25),
                                                                  (1.0, 1.75),
                                                                  (0.5, 1.75),
                                                                  (0.5, 1.25)))
                                                 })
        ph3 = geometry.Polygon(ph2)
        self.assertEqual(ph2.__geo_interface__, ph3.__geo_interface__)
        # if a polygon is passed as constructor holes will be ignored
        # XXX or should holes be added to the polygon?
        ph4 = geometry.Polygon(ph2, [i])
        self.assertEqual(ph2.__geo_interface__, ph4.__geo_interface__)
        coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
        polygon = geometry.Polygon(coords)
        ph5 = geometry.Polygon(
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
             ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))
             ))
        r1 = geometry.LinearRing([(0, 0), (2, 2), (2, 0), (0, 0)])
        r2 = geometry.LinearRing([(0.5, 0.5), (1, 1), (1, 0), (0.5, 0.5)])
        p6 = geometry.Polygon(r1, [r2])
        pt = geometry.Point(0, 1)
        self.assertRaises(TypeError, geometry.Polygon, pt)
        self.assertRaises(TypeError, geometry.Polygon, 0)
        self.assertRaises(TypeError, geometry.Polygon, pt, [pt])

    def test_multipoint(self):
        p0 = geometry.Point(0, 0)
        p1 = geometry.Point(1, 1)
        p2 = geometry.Point(2, 2)
        p3 = geometry.Point(3, 3)
        mp = geometry.MultiPoint(p0)
        self.assertEqual(len(mp.geoms), 1)
        self.assertEqual(mp.geoms[0].x, 0)
        mp1 = geometry.MultiPoint([p0, p1, p2])
        self.assertEqual(len(mp1.geoms), 3)
        self.assertEqual(len(mp1), 3)
        self.assertEqual(mp1.geoms[0].x, 0)
        self.assertEqual(mp1.geoms[1].x, 1)
        self.assertEqual(mp1.geoms[2].x, 2)
        self.assertEqual(mp1.bounds, (0.0, 0.0, 2.0, 2.0))
        l1 = geometry.LineString([p0, p1, p2])
        mp2 = geometry.MultiPoint(l1)
        self.assertEqual(len(mp2.geoms), 3)
        self.assertEqual(mp2.geoms[2].x, 2)
        mp3 = geometry.MultiPoint([l1, p3])
        self.assertEqual(mp3.geoms[3].x, 3)
        self.assertRaises(TypeError, geometry.MultiPoint, [mp1, mp3])
        mp4 = geometry.MultiPoint([p0, p1, p0, p1, p2])
        self.assertEqual(len(mp4.geoms), 5)
        mp4.unique()
        self.assertEqual(len(mp4.geoms), 3)
        mp5 = geometry.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
        self.assertEqual(len(mp5.geoms), 2)
        p = geometry.Polygon(
            (((0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 0.0)),
             ((0.1, 0.1), (0.1, 0.2), (0.2, 0.2), (0.2, 0.1))
             ))
        mp6 = geometry.MultiPoint(p)
        self.assertEqual(mp6.bounds, (0.0, 0.0, 1.0, 1.0))
        self.assertRaises(TypeError, geometry.MultiPoint, [0, 0])
        self.assertRaises(TypeError, geometry.MultiPoint, 0,)

    def test_multilinestring(self):
        ml = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        ml1 = geometry.MultiLineString(ml)
        self.assertEqual(ml.geoms[0].coords, ((0.0, 0.0), (1.0, 2.0)))
        self.assertEqual(ml.bounds, (0.0, 0.0, 1.0, 2.0))
        l = geometry.LineString([(0, 0), (1, 1)])
        l1 = geometry.LineString([(0.0, 0.0), (1.0, 1.0), (2.0, 2.0)])
        ml2 = geometry.MultiLineString([l, l1])
        self.assertEqual(ml2.geoms[0].coords, ((0.0, 0.0), (1.0, 1.0)))
        self.assertEqual(ml2.geoms[1].coords, ((0.0, 0.0), (1.0, 1.0),
                                               (2.0, 2.0)))
        self.assertEqual(len(ml2), 2)
        ml3 = geometry.MultiLineString(l)
        self.assertEqual(ml3.geoms[0].coords, ((0.0, 0.0), (1.0, 1.0)))
        pt = geometry.Point(0, 1)
        self.assertRaises(TypeError, geometry.MultiLineString, pt)
        self.assertRaises(TypeError, geometry.MultiLineString, 0)

    def test_multipolygon(self):
        p = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        ph1 = geometry.Polygon(e, [i])
        mp = geometry.MultiPolygon([p, ph1])
        self.assertEqual(len(mp), 2)
        self.assertTrue(isinstance(mp.geoms[0], geometry.Polygon))
        self.assertTrue(isinstance(mp.geoms[1], geometry.Polygon))
        self.assertEqual(mp.bounds, (0.0, 0.0, 2.0, 2.0))
        mp = geometry.MultiPolygon([(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0),
                                      (1.0, 0.0)), [((0.1, 0.1), (0.1, 0.2),
                                                     (0.2, 0.2), (0.2, 0.1))]
                                     )
                                    ])
        self.assertEqual(len(mp.geoms), 1)
        self.assertTrue(isinstance(mp.geoms[0], geometry.Polygon))
        mp1 = geometry.MultiPolygon(mp)
        self.assertEqual(mp.__geo_interface__, mp1.__geo_interface__)
        mp2 = geometry.MultiPolygon(ph1)
        self.assertRaises(ValueError, geometry.MultiPolygon, 0)
        self.assertRaises(ValueError, geometry.MultiPolygon, [0, 0])
        pt = geometry.Point(0, 1)
        self.assertRaises(TypeError, geometry.MultiPolygon, pt)

    def test_geometrycollection(self):
        self.assertRaises(TypeError, geometry.GeometryCollection)
        self.assertRaises(TypeError, geometry.GeometryCollection, None)
        p = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        ph = geometry.Polygon(e, [i])
        p0 = geometry.Point(0, 0)
        p1 = geometry.Point(-1, -1)
        r = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        l = geometry.LineString([(0, 0), (1, 1)])
        gc = geometry.GeometryCollection([p, ph, p0, p1, r, l])
        self.assertEqual(len(list(gc.geoms)), 6)
        self.assertEqual(len(gc), 6)
        self.assertEqual(gc.bounds, (-1.0, -1.0, 2.0, 2.0))
        self.assertEqual(gc.__geo_interface__,
                         geometry.as_shape(gc).__geo_interface__)
        self.assertEqual(gc.__geo_interface__,
                         geometry.as_shape
                         (gc.__geo_interface__).__geo_interface__)
        f = geometry._Geometry()
        gc1 = geometry.GeometryCollection([p.__geo_interface__, ph, p0, p1, r,
                                           l.__geo_interface__])
        self.assertEqual(gc.__geo_interface__,gc1.__geo_interface__)
        self.assertRaises(NotImplementedError, geometry.GeometryCollection,
                          [p, f])
        mp1 = geometry.MultiPoint([p0, p1])
        self.assertRaises(ValueError, geometry.GeometryCollection, [p, mp1])
        self.assertEqual([p, ph, p0, p1, r, l], [geom for geom in gc])

    def test_mapping(self):
        self.assertEqual(geometry.mapping(geometry.Point(1, 1)),
                         {'type': 'Point', 'coordinates': (1.0, 1.0)})

    def test_signed_area(self):
        a0 = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        a1 = [(0, 0, 1), (0, 2, 2), (2, 2, 3), (2, 0, 4), (0, 0, 1)]
        self.assertEqual(geometry.signed_area(a0), geometry.signed_area(a1))
        a2 = [(0, 0, 1, 3), (0, 2, 2)]
        self.assertRaises(ValueError, geometry.signed_area, a2)


class WKTTestCase(unittest.TestCase):

    # valid and supported WKTs
    wkt_ok = ['POINT(6 10)',
              'POINT M (1 1 80)',
              'LINESTRING(3 4,10 50,20 25)',
              'LINESTRING (30 10, 10 30, 40 40)',
              'MULTIPOLYGON (((10 10, 10 20, 20 20, 20 15, 10 10)),'
              '((60 60, 70 70, 80 60, 60 60 )))',
              '''MULTIPOLYGON (((40 40, 20 45, 45 30, 40 40)),
              ((20 35, 45 20, 30 5, 10 10, 10 30, 20 35),
              (30 20, 20 25, 20 15, 30 20)))''',
              '''MULTIPOLYGON (((30 20, 10 40, 45 40, 30 20)),
              ((15 5, 40 10, 10 20, 5 10, 15 5)))''',
              'MULTIPOLYGON(((0 0,10 0,10 10,0 10,0 0)),'
              '((5 5,7 5,7 7,5 7, 5 5)))',
              'GEOMETRYCOLLECTION(POINT(10 10), POINT(30 30), '
              'LINESTRING(15 15, 20 20))', ]

    # these are valid WKTs but not supported
    wkt_fail = ['POINT ZM (1 1 5 60)', 'POINT EMPTY', 'MULTIPOLYGON EMPTY']



    def test_point(self):
        p = geometry.from_wkt('POINT (0.0 1.0)')
        self.assertEqual(isinstance(p, geometry.Point), True)
        self.assertEqual(p.x, 0.0)
        self.assertEqual(p.y, 1.0)
        self.assertEqual(p.to_wkt(), 'POINT (0.0 1.0)')
        self.assertEqual(p.to_wkt(), p.wkt)
        self.assertEqual(str(p), 'POINT (0.0 1.0)')
        self.assertEqual(p.geom_type, 'Point')

    def test_linestring(self):
        l = geometry.from_wkt('LINESTRING(-72.991 46.177,-73.079 46.16,'
                              '-73.146 46.124,-73.177 46.071,-73.164 46.044)')
        self.assertEqual(l.to_wkt(), 'LINESTRING (-72.991 46.177, '
                                     '-73.079 46.16, -73.146 46.124, '
                                     '-73.177 46.071, -73.164 46.044)')
        self.assertEqual(isinstance(l, geometry.LineString), True)

    def test_linearring(self):
        r = geometry.from_wkt('LINEARRING (0 0,0 1,1 0,0 0)')
        self.assertEqual(isinstance(r, geometry.LinearRing), True)
        self.assertEqual(r.to_wkt(), 'LINEARRING (0.0 0.0, 0.0 1.0, '
                                     '1.0 0.0, 0.0 0.0)')

    def test_polygon(self):
        p = geometry.from_wkt('POLYGON((-91.611 76.227,-91.543 76.217,'
                              '-91.503 76.222,-91.483 76.221,-91.474 76.211,'
                              '-91.484 76.197,-91.512 76.193,-91.624 76.2,'
                              '-91.638 76.202,-91.647 76.211,-91.648 76.218,'
                              '-91.643 76.221,-91.636 76.222,-91.611 76.227))')
        self.assertEqual(p.exterior.coords[0][0], -91.611)
        self.assertEqual(p.exterior.coords[0], p.exterior.coords[-1])
        self.assertEqual(len(p.exterior.coords), 14)
        p = geometry.from_wkt('POLYGON((1 1,5 1,5 5,1 5,1 1),(2 2, 3 2, '
                              '3 3, 2 3,2 2))')
        self.assertEqual(p.exterior.coords[0], p.exterior.coords[-1])
        self.assertEqual(p.exterior.coords[0], (1.0, 1.0))
        self.assertEqual(len(list(p.interiors)), 1)
        self.assertEqual(list(p.interiors)[0].coords,
                        ((2.0, 2.0), (3.0, 2.0), (3.0, 3.0), (2.0, 3.0),
                         (2.0, 2.0)))
        self.assertEqual(p.to_wkt(), 'POLYGON((1.0 1.0, 5.0 1.0, 5.0 5.0, '
                                     '1.0 5.0, 1.0 1.0),(2.0 2.0, 3.0 2.0, '
                                     '3.0 3.0, 2.0 3.0, 2.0 2.0))')
        p = geometry.from_wkt('POLYGON ((30 10, 10 20, 20 40, 40 40, 30 10))')
        self.assertEqual(p.exterior.coords[0], p.exterior.coords[-1])
        p = geometry.from_wkt('''POLYGON ((35 10, 10 20, 15 40, 45 45, 35 10),
            (20 30, 35 35, 30 20, 20 30))''')
        self.assertEqual(p.exterior.coords[0], p.exterior.coords[-1])


    def test_multipoint(self):
        p = geometry.from_wkt('MULTIPOINT(3.5 5.6,4.8 10.5)')
        self.assertEqual(isinstance(p, geometry.MultiPoint), True)
        self.assertEqual(p.geoms[0].x, 3.5)
        self.assertEqual(p.geoms[1].y, 10.5)
        self.assertEqual(p.to_wkt(), 'MULTIPOINT(3.5 5.6, 4.8 10.5)')
        p = geometry.from_wkt('MULTIPOINT ((10 40), (40 30), '
                              '(20 20), (30 10))')
        self.assertEqual(isinstance(p, geometry.MultiPoint), True)
        self.assertEqual(p.geoms[0].x, 10.0)
        self.assertEqual(p.geoms[3].y, 10.0)
        p = geometry.from_wkt('MULTIPOINT (10 40, 40 30, 20 20, 30 10)')
        self.assertEqual(isinstance(p, geometry.MultiPoint), True)
        self.assertEqual(p.geoms[0].x, 10.0)
        self.assertEqual(p.geoms[3].y, 10.0)


    def test_multilinestring(self):
        p = geometry.from_wkt('MULTILINESTRING((3 4,10 50,20 25),'
                              '(-5 -8,-10 -8,-15 -4))')
        self.assertEqual(p.geoms[0].coords, (((3, 4), (10, 50), (20, 25))))
        self.assertEqual(p.geoms[1].coords, (((-5, -8), (-10, -8), (-15, -4))))
        self.assertEqual(p.to_wkt(), 'MULTILINESTRING((3.0 4.0, 10.0 50.0, '
                                     '20.0 25.0),(-5.0 -8.0, '
                                     '-10.0 -8.0, -15.0 -4.0))')
        p = geometry.from_wkt('''MULTILINESTRING ((10 10, 20 20, 10 40),
            (40 40, 30 30, 40 20, 30 10))''')

    def test_multipolygon(self):
        p = geometry.from_wkt('MULTIPOLYGON(((0 0,10 20,30 40,0 0),'
                              '(1 1,2 2,3 3,1 1)),'
                              '((100 100,110 110,120 120,100 100)))')
        #two polygons: the first one has an interior ring
        self.assertEqual(len(p.geoms), 2)
        self.assertEqual(p.geoms[0].exterior.coords,
                        ((0.0, 0.0), (10.0, 20.0), (30.0, 40.0), (0.0, 0.0)))
        self.assertEqual(list(p.geoms[0].interiors)[0].coords,
                        ((1.0, 1.0), (2.0, 2.0), (3.0, 3.0), (1.0, 1.0)))
        self.assertEqual(p.geoms[1].exterior.coords,
                        ((100.0, 100.0), (110.0, 110.0), (120.0, 120.0),
                         (100.0, 100.0)))
        self.assertEqual(p.to_wkt(), 'MULTIPOLYGON(((0.0 0.0, 10.0 20.0, '
                                     '30.0 40.0, 0.0 0.0),'
                                     '(1.0 1.0, 2.0 2.0, 3.0 3.0, 1.0 1.0))'
                                     '((100.0 100.0, 110.0 110.0,'
                                     ' 120.0 120.0, 100.0 100.0)))')
        p = geometry.from_wkt('MULTIPOLYGON(((1 1,5 1,5 5,1 5,1 1),'
                              '(2 2, 3 2, 3 3, 2 3,2 2)),((3 3,6 2,6 4,3 3)))')
        self.assertEqual(len(p.geoms), 2)
        p = geometry.from_wkt("MULTIPOLYGON (((30 20, 10 40, 45 40, 30 20)),"
                              "((15 5, 40 10, 10 20, 5 10, 15 5)))")
        self.assertEqual(p.__geo_interface__, {'type': 'MultiPolygon',
                                               'coordinates':
                        ((((30.0, 20.0), (10.0, 40.0), (45.0, 40.0),
                           (30.0, 20.0)),), (((15.0, 5.0), (40.0, 10.0),
                                              (10.0, 20.0), (5.0, 10.0),
                                              (15.0, 5.0)),))})

    def test_geometrycollection(self):
        gc = geometry.from_wkt('GEOMETRYCOLLECTION(POINT(4 6), '
                               'LINESTRING(4 6,7 10))')
        self.assertEqual(len(list(gc.geoms)), 2)
        self.assertTrue(isinstance(list(gc.geoms)[0], geometry.Point))
        self.assertTrue(isinstance(list(gc.geoms)[1], geometry.LineString))
        self.assertEqual(gc.to_wkt(), 'GEOMETRYCOLLECTION (POINT (4.0 6.0), '
                                      'LINESTRING (4.0 6.0, 7.0 10.0))')

    def test_wkt_ok(self):
        for wkt in self.wkt_ok:
            geometry.from_wkt(wkt)

    def test_wkt_fail(self):
        for wkt in self.wkt_fail:
            self.assertRaises(Exception, geometry.from_wkt, wkt)



class AsShapeTestCase(unittest.TestCase):

    def test_point(self):
        f = geometry.Point(0, 1)
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)

    def test_linestring(self):
        f = geometry.LineString([(0, 0), (1, 1)])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)


    def test_linearring(self):
        f = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)

    def test_polygon(self):
        f = geometry.Polygon([(0, 0), (1, 1), (1, 0), (0, 0)])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)
        e = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        i = [(1, 0), (0.5, 0.5), (1, 1), (1.5, 0.5), (1, 0)]
        f = geometry.Polygon(e, [i])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25),
                 (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        f = geometry.Polygon(ext, [int_1, int_2])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)



    def test_multipoint(self):
        f = geometry.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)

    def test_multilinestring(self):
        f = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)
        self.assertEqual((0, 0, 1, 2), f.bounds)

    def test_multipolygon(self):
        f = geometry.MultiPolygon([(((0.0, 0.0), (0.0, 1.0), (1.0, 1.0),
                                     (1.0, 0.0)), [((0.1, 0.1), (0.1, 0.2),
                                                    (0.2, 0.2), (0.2, 0.1))])
                                   ])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)

    def test_geometrycollection(self):
        p = geometry.Point(0, 1)
        l = geometry.LineString([(0, 0), (1, 1)])
        f = geometry.GeometryCollection([p, l])
        s = geometry.as_shape(f)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)
        self.assertEqual(f.__geo_interface__['geometries'][0],
                         p.__geo_interface__)
        self.assertEqual(f.__geo_interface__['geometries'][1],
                         l.__geo_interface__)

    def test_nongeo(self):
        self.assertRaises(TypeError, geometry.as_shape, 'a')

    def test_notimplemented(self):
        f = geometry._Geometry()
        self.assertRaises(NotImplementedError, geometry.as_shape, f)

    def test_dict_asshape(self):
        f = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        s = geometry.as_shape(f.__geo_interface__)
        self.assertEqual(f.__geo_interface__, s.__geo_interface__)


class OrientationTestCase(unittest.TestCase):

    def test_linearring(self):
        f = geometry.LinearRing([(0, 0), (1, 1), (1, 0), (0, 0)])
        coords = f.coords
        f._set_orientation(False)
        self.assertEqual(f.coords, coords[::-1])
        f._set_orientation(True)
        self.assertEqual(f.coords, coords)

    def test_polygon(self):
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25),
                 (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        p = geometry.Polygon(ext, [int_1, int_2])
        self.assertEqual(list(p.exterior.coords), ext)
        interiors = list(p.interiors)
        self.assertEqual(list(interiors[0].coords), int_1)
        self.assertEqual(list(interiors[1].coords), int_2)
        p._set_orientation(False)
        self.assertEqual(list(p.exterior.coords), ext[::-1])
        interiors = list(p.interiors)
        self.assertEqual(list(interiors[0].coords), int_1)
        self.assertEqual(list(interiors[1].coords), int_2)
        p._set_orientation(True)
        self.assertEqual(list(p.exterior.coords), ext)
        interiors = list(p.interiors)
        self.assertEqual(list(interiors[0].coords), int_1[::-1])
        self.assertEqual(list(interiors[1].coords), int_2[::-1])
        p._set_orientation(False, interiors=False)
        self.assertEqual(list(p.exterior.coords), ext[::-1])
        interiors = list(p.interiors)
        self.assertEqual(list(interiors[0].coords), int_1[::-1])
        self.assertEqual(list(interiors[1].coords), int_2[::-1])
        p._set_orientation(True)
        p._set_orientation(False, exterior=False)
        self.assertEqual(list(p.exterior.coords), ext)
        interiors = list(p.interiors)
        self.assertEqual(list(interiors[0].coords), int_1)
        self.assertEqual(list(interiors[1].coords), int_2)

    def test_multipolygon(self):
        e0 = ((0.0, 0.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0))
        p = geometry.Polygon(e0)
        e1 = ((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0))
        i1 = ((1.0, 0.0), (0.5, 0.5), (1.0, 1.0), (1.5, 0.5), (1.0, 0.0))
        ph1 = geometry.Polygon(e1, [i1])
        mp = geometry.MultiPolygon([p, ph1])
        self.assertEqual(mp.geoms[0].exterior.coords, e0)
        self.assertEqual(mp.geoms[1].exterior.coords, e1)
        self.assertEqual(list(mp.geoms[1].interiors)[0].coords, i1)
        mp._set_orientation(True)
        self.assertEqual(mp.geoms[0].exterior.coords, e0)
        self.assertEqual(mp.geoms[1].exterior.coords, e1)
        self.assertEqual(list(mp.geoms[1].interiors)[0].coords, i1)
        mp._set_orientation(False)
        self.assertEqual(mp.geoms[0].exterior.coords, e0[::-1])
        self.assertEqual(mp.geoms[1].exterior.coords, e1[::-1])
        self.assertEqual(list(mp.geoms[1].interiors)[0].coords, i1[::-1])
        mp._set_orientation(True, exterior=False)
        self.assertEqual(mp.geoms[0].exterior.coords, e0[::-1])
        self.assertEqual(mp.geoms[1].exterior.coords, e1[::-1])
        self.assertEqual(list(mp.geoms[1].interiors)[0].coords, i1)
        mp._set_orientation(False)
        mp._set_orientation(True, interiors=False)
        self.assertEqual(list(mp.geoms[1].interiors)[0].coords, i1[::-1])
        self.assertEqual(mp.geoms[0].exterior.coords, e0)
        self.assertEqual(mp.geoms[1].exterior.coords, e1)


    def test_orient(self):
        ext = [(0, 0), (0, 2), (2, 2), (2, 0), (0, 0)]
        int_1 = [(0.5, 0.25), (1.5, 0.25), (1.5, 1.25), (0.5, 1.25), (0.5, 0.25)]
        int_2 = [(0.5, 1.25), (1, 1.25), (1, 1.75), (0.5, 1.75), (0.5, 1.25)]
        p = geometry.Polygon(ext, [int_1, int_2])
        p1 = geometry.orient(p, 1)
        self.assertEqual(list(p1.exterior.coords), ext[::-1])
        interiors = list(p1.interiors)
        self.assertEqual(list(interiors[0].coords), int_1[::-1])
        self.assertEqual(list(interiors[1].coords), int_2[::-1])
        p2 = geometry.orient(p, -1)
        self.assertEqual(list(p2.exterior.coords), ext)
        interiors = list(p2.interiors)
        self.assertEqual(list(interiors[0].coords), int_1)
        self.assertEqual(list(interiors[1].coords), int_2)


class ReprMethodTestCase(unittest.TestCase):

    def setUp(self):
        self.geometry = geometry._Geometry()
        self.point = geometry.Point(0, 1)
        self.linestring = geometry.LineString([[0, 0], [1, 0], [1, 1]])
        self.linearring = geometry.LinearRing([[0, 0], [1, 0], [1, 1],
                                               [0, 0]])
        self.coords_1 = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
        self.polygon = geometry.Polygon(self.coords_1)
        self.multipoint = geometry.MultiPoint([[0.0, 0.0], [1.0, 2.0]])
        self.multiline = geometry.MultiLineString([[[0.0, 0.0], [1.0, 2.0]]])
        self.multipoly = geometry.MultiPolygon([(((0.0, 0.0), (0.0, 1.0),
                                                 (1.0, 1.0), (1.0, 0.0)),
                                               [((0.1, 0.1), (0.1, 0.2),
                                                 (0.2, 0.2), (0.2, 0.1))])])
        self.geo_collect = geometry.GeometryCollection([self.point,
                                                        self.linestring,
                                                        self.linearring])
        self.feature = geometry.Feature(self.point, {'a': 1, 'b': 2})
        self.feature_list = [self.feature, self.feature]
        self.fc = geometry.FeatureCollection(self.feature_list)

    def test_repr(self):
        pointchk = "Point(0.0, 1.0)"
        l_stringchk = "<LineString Instance 3 Coords>"
        l_ringchk = "<LinearRing Instance 4 Coords>"
        polychk = "<Polygon Instance 0 Interior 5 Exterior>"
        m_pointchk = "<MultiPoint Instance 2 Points>"
        ml_stringchk = "<MultiLineString Instance 1 Lines {0} bbox>".format(self.multiline.bounds)
        m_polychk = "<MultiPolygon Instance 1 Polygons {0} bbox>".format(self.multipoly.bounds)
        gc_chk = "<GeometryCollection Instance 3 Geometries {0} bbox>".format(self.geo_collect.bounds)
        fc_chk = "<FeatureCollection Instance 2 Features {0} bbox>".format(self.fc.bounds)
        self.assertEquals(self.point.__repr__(), pointchk)
        self.assertEquals(self.linestring.__repr__(), l_stringchk)
        self.assertEquals(self.linearring.__repr__(), l_ringchk)
        self.assertEquals(self.polygon.__repr__(), polychk)
        self.assertEquals(self.multipoint.__repr__(), m_pointchk)
        self.assertEquals(self.multiline.__repr__(), ml_stringchk)
        self.assertEquals(self.multipoly.__repr__(), m_polychk)
        self.assertEquals(self.geo_collect.__repr__(), gc_chk)
        self.assertEquals(self.geometry.__repr__()[0:34], 
                          '<pygeoif.geometry._Geometry object')
        self.assertEquals(self.feature.__repr__(),
                          '<Feature Instance Point geometry 2 properties>')
        self.assertEquals(self.fc.__repr__(), fc_chk)


class FeatureTestCase(unittest.TestCase):

    def setUp(self):
        self.a = geometry.Polygon(((0., 0.), (0., 1.),
                                   (1., 1.), (1., 0.), (0., 0.)))
        self.b = geometry.Polygon(((0., 0.), (0., 2.),
                                   (2., 1.), (2., 0.), (0., 0.)))
        self.f1 = geometry.Feature(self.a)
        self.f2 = geometry.Feature(self.b)
        self.f3 = geometry.Feature(self.a, feature_id='1')
        self.fc = geometry.FeatureCollection([self.f1, self.f2])

    def test_feature(self):
        self.assertRaises(TypeError, geometry.Feature)
        self.assertEqual(self.f1.__geo_interface__,
                         geometry.as_shape(self.f1).__geo_interface__)
        self.assertEqual(self.f1.__geo_interface__,
                         {'type': 'Feature',
                          'geometry': {'type': 'Polygon',
                                       'coordinates': (((0.0, 0.0), (0.0, 1.0),
                                                        (1.0, 1.0), (1.0, 0.0),
                                                        (0.0, 0.0)),),
                                       },
                          'properties': {}
                          })
        self.f1.properties['coords'] = {}
        self.f1.properties['coords']['cube'] = (0, 0, 0)
        self.assertEqual(self.f1.__geo_interface__,
                         {'type': 'Feature',
                          'geometry': {'type': 'Polygon',
                                       'coordinates': (((0.0, 0.0), (0.0, 1.0),
                                                        (1.0, 1.0), (1.0, 0.0),
                                                        (0.0, 0.0)),),
                                       },
                          'properties': {'coords': {'cube': (0, 0, 0)}}
                          })
        self.assertEqual(self.f1.geometry.bounds, (0.0, 0.0, 1.0, 1.0))
        del self.f1.properties['coords']

    def test_feature_with_id(self):
        self.assertEqual(self.f3.id, '1')
        self.assertEqual(self.f3.__geo_interface__,
                         {'type': 'Feature',
                          'geometry': {'type': 'Polygon',
                                       'coordinates': (((0.0, 0.0), (0.0, 1.0),
                                                        (1.0, 1.0), (1.0, 0.0),
                                                        (0.0, 0.0)),),
                                       },
                          'id': '1',
                          'properties': {}
                          })
        self.assertEqual(self.f3.__geo_interface__,
                         geometry.as_shape(self.f3).__geo_interface__)

    def test_featurecollection(self):
        self.assertRaises(TypeError, geometry.FeatureCollection)
        self.assertRaises(TypeError, geometry.FeatureCollection, None)
        self.assertEqual(len(list(self.fc.features)), 2)
        self.assertEqual(len(self.fc), 2)
        self.assertEqual(self.fc.bounds, (0.0, 0.0, 2.0, 2.0))
        self.assertEqual(self.fc.__geo_interface__,
                         geometry.as_shape(self.fc).__geo_interface__)
        self.assertEqual([self.f1, self.f2], [feature for feature in self.fc])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BasicTestCase))
    suite.addTest(unittest.makeSuite(WKTTestCase))
    suite.addTest(unittest.makeSuite(AsShapeTestCase))
    suite.addTest(unittest.makeSuite(OrientationTestCase))
    suite.addTest(unittest.makeSuite(ReprMethodTestCase))
    suite.addTest(unittest.makeSuite(FeatureTestCase))
    return suite

if __name__ == '__main__':
    unittest.main()
