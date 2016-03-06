"""
Note: these tests depend on your GBDX credentials existing in env vars or in ~/.gbdx-config, and they
hit GBDX endpoints.  Do not use these as unit tests (e.g. they won't run from travis-ci).
"""

import unittest
from gbdxtools import Interface

class GBDXToolsTests(unittest.TestCase):

    def test_instantiate_interface(self):
        gi = Interface()
        self.assertNotEquals(None, gi.gbdx_connection)

    def test_get_s3tmp_cred(self):
        gi = Interface()
        s3creds = gi.get_s3tmp_cred()
        self.assertTrue("bucket" in s3creds.keys() )
        self.assertTrue("prefix" in s3creds.keys() )
        self.assertTrue("S3_secret_key" in s3creds.keys() )
        self.assertTrue("S3_access_key" in s3creds.keys() )
        self.assertTrue("S3_session_token" in s3creds.keys() )
      
def get_suite():
    return unittest.TestLoader().loadTestsFromTestCase(GBDXToolsTests)

if __name__ == "__main__":
    unittest.main()