import gbdxtools
from auth_mock import get_mock_gbdx_session

mock_gbdx_session = get_mock_gbdx_session(token="dummytoken")


def test_init():
    # gi = gbdxtools.Interface(gbdx_connection=mock_gbdx_session)
    # assert isinstance(gi, gbdxtools.Interface)
    pass


def test_init_host(monkeypatch):
    pass
    # test_host = 'test.mydomain.com'
    #
    # def session(config_file):
    #     return None
    #
    # monkeypatch.setattr(gbdxtools.auth.gbdx_auth, 'get_session', session)
    #
    # gbdx = gbdxtools.Interface(host=test_host)
    # assert isinstance(gbdx, gbdxtools.Interface)
    # assert gbdx.root_url == 'https://%s' % test_host
    # assert gbdx.catalog.base_url == 'https://%s/catalog/v2' % test_host
    # assert gbdx.ordering.base_url == 'https://%s/orders/v2' % test_host
    # assert gbdx.idaho.base_url == 'https://%s/catalog/v2' % test_host
    # assert gbdx.s3.base_url == 'https://%s/s3creds/v1' % test_host
    # assert gbdx.task_registry._base_url == 'https://%s/workflows/v1/tasks' % test_host
    # assert gbdx.workflow.base_url == 'https://%s/workflows/v1' % test_host
    # assert gbdx.workflow.workflows_url == 'https://%s/workflows/v1/workflows' % test_host
