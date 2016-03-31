import pytest

from gbdxtools import Interface
from gbdxtools.s3 import S3

gbdx = Interface()

def test_bucket_init():
    s = S3(gbdx)
    assert isinstance(s, S3)

def test_info():
    s = S3(gbdx)
    assert s.info is not None
    assert "bucket" in s.info.keys()
    assert "prefix" in s.info.keys()
    assert "S3_secret_key" in s.info.keys()
    assert "S3_access_key" in s.info.keys()
    assert "S3_session_token" in s.info.keys()
    
