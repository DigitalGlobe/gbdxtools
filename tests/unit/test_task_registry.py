'''
Contact: dmitry.zviagintsev@digitalglobe.com

Unit test the task registry class
'''

from gbdxtools import Interface
from gbdxtools.task_registry import TaskRegistry
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
    tr = TaskRegistry(gbdx)
    assert isinstance(tr, TaskRegistry)


@vcr.use_cassette('tests/unit/cassettes/test_list_tasks.yaml',filter_headers=['authorization'])
def test_list_tasks():
    tr = TaskRegistry(gbdx)
    taskinfo = tr.list_tasks()
    assert taskinfo is not None
    assert 'HelloGBDX' in taskinfo['tasks']


@vcr.use_cassette('tests/unit/cassettes/test_describe_tasks.yaml',filter_headers=['authorization'])
def test_describe_tasks():
    tr = TaskRegistry(gbdx)
    taskinfo = tr.list_tasks()
    assert len(taskinfo) > 0
    desc = tr.describe_task(taskinfo['tasks'][0])
    assert isinstance(desc, dict)
    assert len(desc['description']) > 0   


@vcr.use_cassette('tests/unit/cassettes/test_register_task.yaml',filter_headers=['authorization'])
def test_register_task():
    tr = TaskRegistry(gbdx)
    task_json = {
        "inputPortDescriptors": [
            {
                "description": "A string input.",
                "name": "inputstring",
                "type": "string"
            }
        ],
        "outputPortDescriptors": [
            {
                "name": "output",
                "type": "string"
            }
        ],
        "containerDescriptors": [
            {
                "type": "DOCKER",
                "command": "",
                "properties": {
                    "image": "test/test-task"
                }
            }
        ],
        "description": "Test task",
        "name": "test-task"
    }

    rv = tr.register(task_json)

    assert 'successfully registered' in rv.lower()


@vcr.use_cassette('tests/unit/cassettes/test_delete_task.yaml',filter_headers=['authorization'])
def test_delete_task():
    tr = TaskRegistry(gbdx)
    taskinfo = tr.list_tasks()
    assert len(taskinfo) > 0
    rv = tr.delete_task(taskinfo['tasks'][0])
    assert 'successfully deleted' in rv.lower()
