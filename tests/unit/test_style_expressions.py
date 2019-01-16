'''
Unit tests for the vector styles and expressions
'''

from gbdxtools import MatchExpression, InterpolateExpression, StepExpression, HeatmapExpression, ZoomExpression
import unittest

class StyleExpressionTests(unittest.TestCase):

    def test_match_exp(self):
        color = MatchExpression(
            property_name='sensor', 
            values={
                'WV03_SWIR': 'aqua',
                'WV03_VNIR': 'olive',
                'WV04': 'blue',
                'WV02': 'orange'
            },
            default_value='#ff0000')
        exp = color.expression
        assert exp[0] == 'match'
        assert exp[1] == ['get', 'sensor']
        assert exp[-1] == '#ff0000'
        assert len(exp) == 11

    def test_step_exp(self):
        color = StepExpression(
            property_name='count',
            stops={
                0: '#F2F12D',
                10: '#EED322',
                100: '#E6B71E'
            })
        exp = color.expression
        assert exp[0] == 'step'
        assert exp[1] == ['get', 'count']
        assert len(exp) == 7

    def test_interp_exp(self):
        color = InterpolateExpression(
            property_name='count',
            stops={
                0: '#F2F12D',
                10: '#EED322',
                100: '#E6B71E'
            })
        exp = color.expression
        assert exp[0] == 'interpolate'
        assert exp[1] == ['linear']
        assert exp[2] == ['get', 'count']
        assert len(exp) == 9

    def test_heatmap_exp(self):
        color = HeatmapExpression(
          stops={
              0: "rgba(33,102,172,0)",
              0.4: "rgb(103,169,207)",
              0.5: "rgb(209,229,240)",
              0.8: "rgb(253,219,199)",
              0.9: "rgb(239,138,98)",
              1: "rgb(178,24,43)"
          })
        exp = color.expression
        assert exp[0] == 'interpolate'
        assert exp[1] == ['linear']
        
    def test_zoom_exp(self):
        zoom = ZoomExpression(
            type=["exponential", 10],
            stops=[0, 1, 9, 5, 12, 10]) 
        exp = zoom.expression
        assert exp[0] == 'interpolate'
        assert exp[1] == ["exponential", 10]
