import pytest

from gbdx_auth import gbdx_auth
from gbdxtools.s3 import S3



def test_bucket_init():
    gx_conn = gbdx_auth.get_session()
    s = S3(gx_conn)
    assert isinstance(s, S3)

def test_info():
    gx_conn = gbdx_auth.get_session()
    s = S3(gx_conn)
    assert s.info is not None
    assert "bucket" in s.info.keys()
    assert "prefix" in s.info.keys()
    assert "S3_secret_key" in s.info.keys()
    assert "S3_access_key" in s.info.keys()
    assert "S3_session_token" in s.info.keys()
    
