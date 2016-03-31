'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Ordering class
'''

from gbdxtools import Interface
from gbdxtools.ordering import Ordering

def test_init():
    o = Ordering(Interface())
    assert isinstance(o, Ordering)
