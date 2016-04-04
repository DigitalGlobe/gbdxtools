"""
Note: these tests depend on your GBDX credentials existing in env vars or in ~/.gbdx-config, and they
hit GBDX endpoints.  Do not use these as unit tests (e.g. they won't run from travis-ci).
"""

import unittest
from gbdxtools import Interface
from gbdxtools.s3 import S3

class GBDXToolsTests(unittest.TestCase):

    def setUp(self):
        self.gi = Interface()

    def test_instantiate_interface(self):
        self.assertNotEquals(None, self.gi.gbdx_connection)

    def test_s3(self):
        assert isinstance( self.gi.s3, S3)
        self.assertTrue("bucket" in self.gi.s3.info.keys() )
        self.assertTrue("prefix" in self.gi.s3.info.keys() )
        self.assertTrue("S3_secret_key" in self.gi.s3.info.keys() )
        self.assertTrue("S3_access_key" in self.gi.s3.info.keys() )
        self.assertTrue("S3_session_token" in self.gi.s3.info.keys() )
      
