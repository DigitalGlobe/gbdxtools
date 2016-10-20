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

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_create_single.yaml', filter_headers=['authorization'])
    def test_vectors_create_single(self):
        v = Vectors(self.gbdx)
        results = v.create({
            "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.0,1.0]
                },
                "properties": {
                    "text" : "item text",
                    "name" : "item name",
                    "item_type" : "type",
                    "ingest_source" : "source",
                    "attributes" : {
                       "latitude" : 1,
                       "institute_founded" : "2015-07-17",
                       "mascot" : "moth"
                    }
                }
          })

        for result in results:
            assert result == '/insight-vector/api/vector/vector-web-s/ce0699f3-bef8-402f-a18e-d149dc2f5f90'

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_create_multiple.yaml', filter_headers=['authorization'])
    def test_vectors_create_multiple(self):
        v = Vectors(self.gbdx)
        results = v.create([{
            "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.0,1.0]
                },
                "properties": {
                    "text" : "item text",
                    "name" : "item name",
                    "item_type" : "type",
                    "ingest_source" : "source",
                    "attributes" : {
                       "latitude" : 1,
                       "institute_founded" : "2015-07-17",
                       "mascot" : "moth"
                    }
                }
          },
          {
            "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [1.0,1.0]
                },
                "properties": {
                    "text" : "item text",
                    "name" : "item name",
                    "item_type" : "type",
                    "ingest_source" : "source",
                    "attributes" : {
                       "latitude" : 1,
                       "institute_founded" : "2015-07-17",
                       "mascot" : "asdfadsfadf"
                    }
                }
          }])

        assert len(results) == 2

    @vcr.use_cassette('tests/unit/cassettes/test_vectors_create_from_wkt.yaml', filter_headers=['authorization'])
    def test_vectors_create_from_wkt(self):
        v = Vectors(self.gbdx)

        aoi = "POLYGON((0 3,3 3,3 0,0 0,0 3))"
        result = v.create_from_wkt(
            aoi,
            item_type='test_type_123',
            ingest_source='api',
            attribute1='nothing',
            attribute2='something',
            number=6,
            date='2015-06-06'
        )
        assert result == '/insight-vector/api/vector/vector-web-s/b1af66c3-2e41-4696-9924-6ab264336692'








