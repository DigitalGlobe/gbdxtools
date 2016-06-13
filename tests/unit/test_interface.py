from gbdxtools import Interface
from auth_mock import get_mock_gbdx_session

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

mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")


def test_init():
    gi = Interface(gbdx_connection=mock_gbdx_session)
    assert isinstance(gi, Interface)
