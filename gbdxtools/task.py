
task = None

def Taskify(**kwargs):
    global task
    if task is None: # or len(kwargs) > 0:
        task = _Tasker(**kwargs)
    return task

class _Tasker(object):
    def __init__(self, inputs=None, outputs=None):
        self.inputs = Args(inputs)
        self.outputs = Args(outputs)

    def definition(self):
        return {
            'inputs': self.inputs,
            'outputs': self.outputs
        }

class Args(object):
    def __init__(self, vals=None):
        self.vals = {} if vals is None else vals

    def get(self, name, default=None):
        if name not in self.vals:
            self.vals[name] = default
        return self.vals[name]

    def __repr__(self):
        return repr(self.vals)

task = Taskify()
