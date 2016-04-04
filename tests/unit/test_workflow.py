'''
Authors: Kostas Stamatiou, Donnie Marino
Contact: kostas.stamatiou@digitalglobe.com

Unit test the workflow class
'''

from gbdxtools import Interface
from gbdxtools.workflow import Workflow
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

def test_init():
    wf = Workflow(gbdx)
    assert isinstance(wf, Workflow)
    assert wf.s3 is not None
    assert wf.gbdx_connection is not None

@vcr.use_cassette('tests/unit/cassettes/test_list_tasks.yaml',filter_headers=['authorization'])
def test_list_tasks():
    wf = Workflow(gbdx)
    taskinfo = wf.list_tasks()
    assert taskinfo is not None
    assert 'HelloGBDX' in taskinfo['tasks']

@vcr.use_cassette('tests/unit/cassettes/test_describe_tasks.yaml',filter_headers=['authorization'])
def test_describe_tasks():
    wf = Workflow(gbdx)
    taskinfo = wf.list_tasks()
    assert len(taskinfo) > 0
    desc = wf.describe_task(taskinfo['tasks'][0])
    assert isinstance(desc, dict)
    assert len(desc['description']) > 0   
