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

    def test_image_class_legacy_support(self):
        from gbdxtools import RDAImage
        self.assertTrue(hasattr(RDAImage, "ipe"))

    @my_vcr.use_cassette('tests/unit/cassettes/test_cat_image_wv2.yaml', filter_headers=['authorization'])
    def test_class_instance_legacy_access(self):
        # Test access raises warning
        from gbdxtools import CatalogImage
        wv2 = CatalogImage('1030010076B8F500')
        with self.assertWarns(DeprecationWarning):
            obj = wv2.ipe

        # Test value is expected
        self.assertEqual(wv2.ipe.__module__, "gbdxtools.rda.interface")
        from gbdxtools.rda.interface import Op
        self.assertTrue(isinstance(wv2.ipe, Op))

    def test_module_legacy_support(self):
        # Test warn on module access: ipe
        with self.assertWarns(DeprecationWarning):
            from gbdxtools import ipe
            # Test warn on module attribute access: Ipe
        with self.assertWarns(DeprecationWarning):
            from gbdxtools.ipe.interface import Ipe
            # Test deprecated module attribute is expected: Ipe
        from gbdxtools.ipe.interface import Ipe
        self.assertEqual(Ipe.__name__, "RDA")

        # Test warn on module access: IpeImage
        with self.assertWarns(DeprecationWarning):
            from gbdxtools.images.rda_image import IpeImage

    @my_vcr.use_cassette('tests/unit/cassettes/test_ipe_image_default.yaml', filter_headers=['authorization'])
    def test_package_level_imports(self):
        # Test warning is issued on instantiation: IpeImage
        from gbdxtools import IpeImage
        #TODO: instantiate an IpeImage and check it raises DeprecationWarning






