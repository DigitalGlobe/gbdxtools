'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Catalog class
'''

from gbdx_auth import gbdx_auth
from gbdxtools.catalog import Catalog

def test_init():
    gc = gbdx_auth.get_session()
    c = Catalog(gc)
    assert isinstance(c, Catalog)

