'''
Authors: Kostas Stamatiou, Donnie Marino
Contact: kostas.stamatiou@digitalglobe.com

Unit test the workflow class
'''

from gbdxtools import Interface
from gbdxtools.workflow import Workflow

def test_init():
    wf = Workflow(Interface())
    assert isinstance(wf, Workflow)
    assert wf.s3 is not None
    assert wf.gbdx_connection is not None
    
def test_list_tasks():
    wf = Workflow(Interface())
    taskinfo = wf.list_tasks()
    assert taskinfo is not None
    assert 'HelloGBDX' in taskinfo['tasks']

def test_describe_tasks():
    wf = Workflow(Interface())
    taskinfo = wf.list_tasks()
    assert len(taskinfo) > 0
    desc = wf.describe_task(taskinfo['tasks'][0])
    assert isinstance(desc, dict)
    assert len(desc['description']) > 0   
