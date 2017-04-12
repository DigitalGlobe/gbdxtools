import gbdxtools
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
    gi = gbdxtools.Interface(gbdx_connection=mock_gbdx_session)
    assert isinstance(gi, gbdxtools.Interface)


def test_init_host(monkeypatch):
    test_host = 'test.mydomain.com'

    def session(config_file):
        return None

    monkeypatch.setattr(gbdxtools.auth.gbdx_auth, 'get_session', session)

    gbdx = gbdxtools.Interface(host=test_host)
    assert isinstance(gbdx, gbdxtools.Interface)
    assert gbdx.root_url == 'https://%s' % test_host
    assert gbdx.catalog.base_url == 'https://%s/catalog/v2' % test_host
    assert gbdx.ordering.base_url == 'https://%s/orders/v2' % test_host
    assert gbdx.idaho.base_url == 'https://%s/catalog/v2' % test_host
    assert gbdx.s3.base_url == 'https://%s/s3creds/v1' % test_host
    assert gbdx.task_registry._base_url == 'https://%s/workflows/v1/tasks' % test_host
    assert gbdx.workflow.base_url == 'https://%s/workflows/v1' % test_host
    assert gbdx.workflow.workflows_url == 'https://%s/workflows/v1/workflows' % test_host
