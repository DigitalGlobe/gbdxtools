import json
import os
from collections import MutableMapping, Mapping


class InputPorts(Mapping):
    def __init__(self, initial_data={}):
        self._ports = {}
        self._vals = {}

        for key, value in initial_data.iteritems():
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

    def get(self, key, default=None):
        """
        >>> inputs = InputPorts({"one": 1})
        >>> "one" in inputs._ports
        True
        >>> "one" in inputs._vals
        True
        >>> inputs["one"] == 1
        True
        >>> inputs.get("one", 2) == 1
        True
        >>> inputs.get("two", 2) == 2
        True
        >>> "two" in inputs._ports
        True
        >>> "two" in inputs._vals
        True
        >>> inputs["two"] == 2
        True
        """
        if key not in self._ports:
            self._ports[key] = self._port_template(key)
        if key not in self._vals:
            self._vals[key] = default
        return self._vals[key]

    def _port_template(self, name, description="No Description Provided",
                       datatype="string", **kwargs):
        kwargs.update({"name": name, "description": description, "type": datatype})
        return kwargs

    def __contains__(self, key):
        return key in self._ports

    def __len__(self):
        return len(self._ports)


class OutputPorts(MutableMapping, InputPorts):
    def __setitem__(self, key, value):
        if key in self._vals:
            raise NotImplementedError("Overwriting a port value is not supported")
        self._vals[key] = value
        self._ports[key] = self._port_template(key)

    def __delitem__(self, key):
        raise NotImplementedError("Ports may not be deleted")


class TaskEnv(object):
    """
    >>> env = TaskEnv()
    >>> env.inputs.get("catalog_id", "123456789")
    '123456789'
    >>> env.inputs["catalog_id"] == "123456789"
    True
    >>> env.outputs["status"] = "Success"
    >>> env.outputs["status"] == "Success"
    True
    >>> env.definition({"name": "test", "description": "test description", "version": "1000"}).keys()
    ['inputPortDescriptors', 'description', 'version', 'outputPortDescriptors', 'name']
    """
    def __init__(self, *args, **kwargs):
        super(TaskEnv, self).__init__(*args, **kwargs)
        WORK_DIR = "/mnt/work"

        try:
            with open(os.path.join(WORK_DIR, "input", "ports.json")) as f:
                self.inputs = InputPorts(json.load(f))
        except:
            self.inputs = InputPorts()

        try:
            with open(os.path.join(WORK_DIR, "output", "ports.json")) as f:
                self.outputs = OutputPorts(json.load(f))
        except:
            self.outputs = OutputPorts()

    def definition(self, task={}):
        assert self.is_valid(task), "Task is not valid.  Correct it before generating definition"
        rec = {"inputPortDescriptors": self.inputs.ports.values(),
               "outputPortDescriptors": self.outputs.ports.values()}
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
