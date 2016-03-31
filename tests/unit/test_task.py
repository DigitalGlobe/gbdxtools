'''
Unit tests for the Task class
'''
import json

from gbdxtools.task import Task

def test_plain_init():
    t = Task()
    t.name = "Testtask"
    assert isinstance(t, Task)
    assert t.name is not None
    assert t.name == "Testtask"

def test_init_w_args():
    tname = "TestTasks2023"
    test_cd = ["foo","bar","bat"]
    t = Task(name=tname, container_descriptors=test_cd)
    assert isinstance(t, Task)
    assert t.name == "TestTasks2023"
    assert t.container_descriptors is not None
    assert "bar" in t.container_descriptors

def test_to_json():
    t = Task()
    t.name = "Testin125"
    assert isinstance(t, Task)
    task_json = t.to_json()
    assert task_json is not None
    js_task = json.loads(task_json)
    assert js_task["name"] == "Testin125"
