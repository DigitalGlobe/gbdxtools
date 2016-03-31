'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdx_auth import gbdx_auth
from gbdxtools.idaho import Idaho

def test_init():
    gc = gbdx_auth.get_session()
    i = Idaho(gc)
    assert isinstance(i, Idaho)

