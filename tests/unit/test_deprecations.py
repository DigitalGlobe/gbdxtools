import warnings
import contextlib
import vcr
import unittest


def force(r1, r2):
    return True


my_vcr = vcr.VCR()
my_vcr.register_matcher('force', force)
my_vcr.match_on = ['force']

class TestLegacySupport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @contextlib.contextmanager
    def assertWarns(self, warning, *args, **kwargs):
        """A test that checks if a specified wanring was raised"""
        original_filters = warnings.filters[:]
        warnings.simplefilter('error')
        if len(args) == 0 and len(kwargs) == 0:
            with self.assertRaises(warning):
                yield
        else:
            self.assertRaises(warning, *args, **kwargs)
        warnings.filters = original_filters


    @unittest.skip(reason="This deprecated function was removed")
    @my_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv2.yaml', filter_headers=['authorization'])
    def test_base_layer_match_dep(self):
        # Test access raises warning
        from gbdxtools import CatalogImage
        wv2 = CatalogImage('1030010076B8F500')
        with self.assertWarns(DeprecationWarning):
            obj = wv2.base_layer_match()



