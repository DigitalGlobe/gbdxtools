'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Ordering class
'''

from gbdx_auth import gbdx_auth
from gbdxtools.ordering import Ordering

def test_init():
    gc = gbdx_auth.get_session()
    o = Ordering(gc)
    assert isinstance(o, Ordering)
