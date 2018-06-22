import unittest
import numpy as np
from gbdxtools.images.mixins.geo import PlotMixin


class PlotMock(np.ndarray, PlotMixin):

    @property
    def _rgb_bands(self):
        return [3,1,2]

    @property
    def _ndvi_bands(self):
        return [6,3]

    def _read(self, arr, **kwargs):
        return arr


class PlotTest(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.zero = np.zeros((8,8,8))
        cls.plotmock = cls.zero.view(PlotMock) 

    def test_plot_rgb(self):
        self.plotmock.plot()

    def test_plot_ndvi(self):
        self.plotmock.plot(spec="ndvi")

    def test_plot_1_band(self):
        self.plotmock.plot(bands=[1])

    def test_plot_3_band(self):
        self.plotmock.plot(bands=[3,2,1])

    def test_plot_4_band_fail(self):
        with self.assertRaises(AssertionError):
            self.plotmock.plot(bands=[4,3,2,1])