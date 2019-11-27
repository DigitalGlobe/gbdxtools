from gbdxtools import Interface

gbdx = None

def go():
    print(gbdx.task_registry.list())
    print(gbdx.task_registry.get_definition('HelloGBDX'))

if __name__ == "__main__":
    gbdx = Interface()
    go()
