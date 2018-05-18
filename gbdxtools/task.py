import json
import os
from collections import MutableMapping, Mapping


class InputPorts(Mapping):
    def __init__(self, initial_data={}):
        self._ports = {}
        self._vals = {}

        for key, value in initial_data.items():
            self._ports[key] = self._port_template(key, required=True)
            self._vals[key] = value

    @property
    def ports(self):
        return self._ports

    def __getitem__(self, key):
        """
        >>> inputs = InputPorts()
        >>> inputs["nonexistent"]
        Traceback (most recent call last):
        ...
        KeyError: 'nonexistent'
        >>> inputs._vals["nonexistent"] = 0
        >>> inputs["nonexistent"]
        0
        >>> assert "nonexistent" in inputs._ports
        """
        value = self._vals[key]
        if key not in self._ports:
            self._ports[key] = self._port_template(key, required=True)
        return value

    def __iter__(self):
        return iter(self._ports)

    def __delitem__(self, key):
        if key in self._vals:
            del self._vals[key]
        if key in self._ports:
            del self._ports[key]

    def get(self, key, default=None):
        """
        >>> inputs = InputPorts({"one": 1})
        >>> "one" in inputs._ports
        True
        >>> "one" in inputs._vals
        True
        >>> inputs.get("one", 2) == 1
        True
        >>> inputs.get("two", 2) == 2
        True
        >>> "two" in inputs._ports
        True
        >>> "two" in inputs._vals
        False
        """
        if key not in self._ports:
            self._ports[key] = self._port_template(key)
        return self._vals.get(key, default)

    def _port_template(self, name, description="No Description Provided",
                       datatype="string", **kwargs):
        kwargs.update({"name": name, "description": description, "type": datatype})
        return kwargs

    def __contains__(self, key):
        return key in self._ports

    def __len__(self):
        return len(self._ports)


class OutputPorts(InputPorts):
    def __init__(self, work_dir):
        self._ports_dir = os.path.join(work_dir, "output") if work_dir is not None else ''
        super(OutputPorts, self).__init__()
        key = 'task_output'
        self._ports[key] = self._port_template(key, datatype="directory")
        self._vals[key] = os.path.join(self._ports_dir, "task_output")
        self.save()
    
    def __setitem__(self, key, value):
        self._vals[key] = os.path.join(self._ports_dir, 'task_output', value) # TODO make this not use this output dir, and use the pwd 
        self._ports[key] = self._port_template(key, datatype="directory")
        self.save()

    def __delitem__(self, key):
        del self._vals[key]
        del self._ports[key]
        self.save()

    def save(self):
        try:
            os.makedirs(self._ports_dir)
        except Exception as e:
            pass
        try:
            with open(os.path.join(self._ports_dir, "ports.json"), "w") as f:
                json.dump(dict(self), f)
        except Exception as e:
            pass



class TaskEnv(object):
    """
    >>> env = TaskEnv()
    >>> env.inputs.get("catalog_id", "123456789")
    '123456789'
    >>> env.inputs["catalog_id"] == "123456789"
    Traceback (most recent call last):
    ...
    KeyError: 'catalog_id'
    >>> env.outputs["status"] = "Success"
    >>> env.outputs["status"] == "Success"
    True
    >>> env.definition({"name": "test", "description": "test description", "version": "1000"}).keys()
    ['inputPortDescriptors', 'description', 'version', 'outputPortDescriptors', 'name']
    """
    def __init__(self, *args, **kwargs):
        super(TaskEnv, self).__init__(*args, **kwargs)
        WORK_DIR = os.environ.get("GBDX_WORK_DIR", "/mnt/work")
        if not os.path.exists(WORK_DIR):
            WORK_DIR = None

        try:
            with open(os.path.join(WORK_DIR, "input", "ports.json")) as f:
                self.inputs = InputPorts(json.load(f))
        except:
            self.inputs = InputPorts()

        self.outputs = OutputPorts(WORK_DIR)

    def definition(self, task={}):
        assert self.is_valid(task), "Task is not valid.  Correct it before generating definition"
        rec = {"inputPortDescriptors": list(self.inputs.ports.values()),
               "outputPortDescriptors": list(self.outputs.ports.values())}
        rec.update(task)
        return rec

    def is_valid(self, task):
        return True

    def __getattr__(self, key):
        return getattr(os.environ, key)


env = TaskEnv()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
