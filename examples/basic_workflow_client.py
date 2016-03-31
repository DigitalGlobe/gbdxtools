from gbdxtools import Interface

gbdx = None

def go():
    print gbdx.workflow.list_tasks()
    print gbdx.workflow.describe_task('HelloGBDX')

if __name__ == "__main__":
    gbdx = Interface()
    go()
