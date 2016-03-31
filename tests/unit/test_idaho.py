'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Idaho class
'''

from gbdxtools import Interface
from gbdxtools.idaho import Idaho

def test_init():
    i = Idaho(Interface())
    assert isinstance(i, Idaho)

