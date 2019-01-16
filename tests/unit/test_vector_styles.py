'''
Unit tests for the vector styles and expressions
'''

from gbdxtools.vector_styles import CircleStyle, LineStyle, FillStyle, FillExtrusionStyle, HeatmapStyle
import unittest

class VectorStyleTest(unittest.TestCase):

    def test_circle_style(self):
        s = CircleStyle()
        assert s.opacity == 1.0
        assert s.radius == 1.0
        assert s.color == 'rgb(255,0,0)'
        assert s.translate == None
        assert s.type == 'circle'
        s2 = CircleStyle(radius=5.0, opacity=0.5, color='pink')
        assert s2.opacity == 0.5
        assert s2.radius == 5.0
        assert s2.color == 'pink'
        assert s2.paint() == {'circle-color': 'pink', 'circle-opacity': 0.5, 'circle-radius': 5.0}

    def test_line_style(self):
        s = LineStyle()
        assert s.opacity == 1.0
        assert s.width == 1.0
        assert s.color == 'rgb(255,0,0)'
        assert s.type == 'line'
        s2 = LineStyle(width=5.0, opacity=0.5, color='pink')
        assert s2.opacity == 0.5
        assert s2.width == 5.0
        assert s2.color == 'pink'
        assert s2.paint() == {'line-color': 'pink', 'line-opacity': 0.5, 'line-width': 5.0}

    def test_fill_style(self):
        s = FillStyle()
        assert s.opacity == 0.5
        assert s.color == 'rgb(255,0,0)'
        assert s.outline_color == s.color
        assert s.type == 'fill'
        s2 = FillStyle(opacity=0.25, outline_color='red', color='pink')
        assert s2.opacity == 0.25
        assert s2.outline_color == 'red'
        assert s2.color == 'pink'
        assert s2.paint() == {'fill-color': 'pink', 'fill-opacity': 0.25, 'fill-outline-color': 'red'}

    def test_fill_extrusion_style(self):
        s = FillExtrusionStyle()
        assert s.base == 0
        assert s.height == 0
        assert s.color == 'rgb(255,0,0)'
        assert s.outline_color == s.color
        assert s.type == 'fill-extrusion'
        s2 = FillExtrusionStyle(opacity=0.25, base=10, height=100, color='pink')
        assert s2.opacity == 0.25
        assert s2.base == 10
        assert s2.height == 100
        assert s2.color == 'pink'
        assert s2.paint() == {
            'fill-extrusion-color': 'pink', 
            'fill-extrusion-opacity': 0.25, 
            'fill-extrusion-base': 10,
            'fill-extrusion-height': 100
        }

    def test_heatmap_style(self):
        def_color = ['interpolate',
          ['linear'],
          ['heatmap-density'],
          0, 'rgba(0, 0, 255, 0)',
          0.1, 'royalblue',
          0.3, 'cyan',
          0.5, 'lime',
          0.7, 'yellow',
          1,'red']
        s = HeatmapStyle()
        assert s.opacity == 1.0
        assert s.color == def_color
        assert s.intensity == 1
        assert s.weight == 1
        assert s.radius == 1
        assert s.type == 'heatmap'
        def_color[-1] = 'pink'
        s2 = HeatmapStyle(color=def_color)
        assert s2.color[-1] == def_color[-1]

        

    
