'''
Authors: Nate Ricklin
Contact: nricklin@digitalglobe.com

Unit tests for the gbdxtools.Vectors class
'''

from gbdxtools import Interface
from gbdxtools.vectors import Vectors
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

class TestVectors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session)

    def test_init(self):
        c = Vectors(self.gbdx)
        self.assertTrue(isinstance(c, Vectors))

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_search.yaml', filter_headers=['authorization'])
    def test_vectors_search(self):
        v = Vectors(self.gbdx)
        aoi = "POLYGON((17.75390625 25.418470119273117,24.08203125 25.418470119273117,24.08203125 19.409611549990895,17.75390625 19.409611549990895,17.75390625 25.418470119273117))"
        results = v.query(aoi, query="item_type:WV03")

        assert len(results) == 100