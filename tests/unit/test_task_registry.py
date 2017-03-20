'''
Contact: dmitry.zviagintsev@digitalglobe.com

Unit test the task registry class
'''
import os

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
gbdx = Interface(gbdx_connection=mock_gbdx_session)


def test_init():
    tr = TaskRegistry()
    assert isinstance(tr, TaskRegistry)


@vcr.use_cassette('tests/unit/cassettes/test_list_tasks.yaml', filter_headers=['authorization'])
def test_list_tasks():
    tr = TaskRegistry()
    task_list = tr.list()
    assert task_list is not None
    assert 'HelloGBDX' in task_list


@vcr.use_cassette('tests/unit/cassettes/test_describe_tasks.yaml', filter_headers=['authorization'])
def test_describe_tasks():
    tr = TaskRegistry()
    task_list = tr.list()
    assert len(task_list) > 0
    desc = tr.get_definition(task_list[0])
    assert isinstance(desc, dict)
    assert len(desc['description']) > 0


@vcr.use_cassette('tests/unit/cassettes/test_register_task.yaml', filter_headers=['authorization'])
def _test_register_task(task_json=None, filename=None):
    tr = TaskRegistry()

    if task_json:
        rv = tr.register(task_json)
    else:
        rv = tr.register(filename)

    assert 'successfully registered' in rv.lower()


def _task_json():
    return {
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
                    "image": "test/gbdxtools-test-task"
                }
            }
        ],
        "description": "Test task",
        "name": "gbdxtools-test-task",
        "version": "0.0.1"
    }


def test_register_task_from_json():
    task_json = _task_json()

    _test_register_task(task_json=task_json)


def test_register_task_from_file():
    filename = os.path.abspath(os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "data", "gbdxtools_test_task.json"
    ))

    _test_register_task(filename=filename)


@vcr.use_cassette('tests/unit/cassettes/test_update_task.yaml', filter_headers=['authorization'])
def test_update_task_definition():
    # Note that this test requires the task to be registered all ready.
    # If updating the VCR yaml cassette, manually register the gbdxtools-test-task above,
    # Deleting it once the VCR cassette has been created.
    tr = TaskRegistry()

    updated_task = _task_json()
    output_ports = updated_task['outputPortDescriptors']
    updated_task['outputPortDescriptors'] = output_ports + [{"name": "output%s" % len(output_ports), "type": "string"}]

    task_name = '%s:%s' % (updated_task['name'], updated_task['version'])

    r = tr.update(task_name, updated_task)

    assert r['outputPortDescriptors'] == updated_task['outputPortDescriptors']


def test_register_fails_when_both_json_and_file():
    tr = TaskRegistry()

    try:
        tr.register(task_json={'any': 'thing'}, json_filename="any")
    except Exception as e:
        if "Both task json and filename can't be provided." in str(e):
            pass
        else:
            raise


def test_register_fails_when_both_json_and_file_none():
    tr = TaskRegistry()

    try:
        tr.register(task_json=None, json_filename=None)
    except Exception as e:
        if "Both task json and filename can't be none." in str(e):
            pass
        else:
            raise


@vcr.use_cassette('tests/unit/cassettes/test_delete_task.yaml',filter_headers=['authorization'])
def test_delete_task():
    tr = TaskRegistry()
    tasks = tr.list()
    if not 'gbdxtools-test-task' in tasks:
        test_list_tasks()
    rv = tr.delete('gbdxtools-test-task')
    assert 'successfully deleted' in rv.lower()
