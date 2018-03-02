from gbdxtools import Interface
from auth_mock import get_mock_gbdx_session
import os
import vcr
import tempfile
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

"""
Creates a temporary gbdx-config file so that this test can exercise expiring the token after a 401 endpoint response,
the temp file is cleaned up during garbage collection and or when the file is closed. This needs to be at module level
as the file won't exist after setUpClass returns
"""

data = """
[gbdx]
auth_url = https://geobigdata.io/auth/v1/oauth/token/
client_id = your_client_id
client_secret = your_client_secret
user_name = your_user_name
user_password = your_password
"""

# create temp gbdx-config file
temp = tempfile.NamedTemporaryFile(prefix="gbdx-auth", suffix=".ini", mode="w+t", delete=False)
# write the data
temp.write(data)
temp.seek(0)


class TestAuthRetry(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = {"token_type": "Bearer", "refresh_token": "dummyToken", "access_token": "dummytoken",
                 "scope": ["read", "write"],
                 "expires_in": 604800, "expires_at": 2529702305}

        mock_gbdx_session = get_mock_gbdx_session(token=token)
        cls.gbdx = Interface(gbdx_connection=mock_gbdx_session, config_file=temp.name)

    @vcr.use_cassette('tests/unit/cassettes/test_auth_401_retry.yaml', filter_headers=['authorization'],
                      record_mode='once', decode_compressed_response=True)
    def test_auth_401_retry(self):
        """
        We want to test that on 401, a new token is fetched and the original request is retried
        This is for seamless migration to auth v2
        :return:
        """
        # if this test passes it means the 401 retry worked, see the cassette for details
        self.gbdx.Task("AOP_Strip_Processor")
