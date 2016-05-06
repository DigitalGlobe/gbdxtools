'''
Authors: Donnie Marino, Kostas Stamatiou
Contact: dmarino@digitalglobe.com

Unit tests for the gbdxtools.Catalog class
'''

from gbdxtools import Interface
from gbdxtools.catalog import Catalog
from auth_mock import get_mock_gbdx_session
import vcr
import unittest

"""
How to use the mock_gbdx_session and vcr to create unit tests:
1. Add a new test that is dependent upon actually hitting GBDX APIs.
2. Decorate the test with @vcr appropriately, supply a yaml file path to gbdxtools/tests/unit/cassettes
    note: a yaml file will be created after the test is run

3. Replace "dummytoken" with a real gbdx token after running test successfully
4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
5. Replace the real gbdx token with "dummytoken" again
6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)
"""


class TestCatalog(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)

    def test_init(self):
        c = Catalog(self.gbdx)
        self.assertTrue(isinstance(c, Catalog))

    @vcr.use_cassette('tests/unit/cassettes/test_catalog_get_address_coords.yaml', filter_headers=['authorization'])
    def test_catalog_get_address_coords(self):
        c = Catalog(self.gbdx)
        lat, lng = c.get_address_coords('Boulder, CO')
        self.assertTrue(lat == 40.0149856)
        self.assertTrue(lng == -105.2705456)

    @vcr.use_cassette('tests/unit/cassettes/test_catalog_search_point.yaml', filter_headers=['authorization'])
    def test_catalog_search_point(self):
        c = Catalog(self.gbdx)
        lat = 40.0149856
        lng = -105.2705456
        results = c.search_point(lat, lng)

        self.assertTrue(results['stats']['totalRecords'] == 310)

    @vcr.use_cassette('tests/unit/cassettes/test_catalog_search_address.yaml', filter_headers=['authorization'])
    def test_catalog_search_address(self):
        c = Catalog(self.gbdx)
        results = c.search_address('Boulder, CO')

        self.assertTrue(results['stats']['totalRecords'] == 310)
