import pytest

from gbdxtools import Interface
from gbdxtools.s3 import S3
import vcr
from auth_mock import get_mock_gbdx_session


# How to use the mock_gbdx_session and vcr to create unit tests:
# 1. Add a new test that is dependent upon actually hitting GBDX APIs.
# 2. Decorate the test with @vcr appropriately
# 3. replace "dummytoken" with a real gbdx token
# 4. Run the tests (existing test shouldn't be affected by use of a real token).  This will record a "cassette".
# 5. replace the real gbdx token with "dummytoken" again
# 6. Edit the cassette to remove any possibly sensitive information (s3 creds for example)
mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")
gbdx = Interface(gbdx_connection = mock_gbdx_session)

def test_bucket_init():
    s = S3(gbdx)
    assert isinstance(s, S3)

@vcr.use_cassette('tests/unit/cassettes/test_get_s3creds.yaml',filter_headers=['authorization'])
def test_get_s3_creds():
    s = S3(gbdx)
    assert s.info is not None
    assert "bucket" in s.info.keys()
    assert "prefix" in s.info.keys()
    assert "S3_secret_key" in s.info.keys()
    assert "S3_access_key" in s.info.keys()
    assert "S3_session_token" in s.info.keys()
    
