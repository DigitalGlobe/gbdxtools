import click
import json
from gbdxtools import Interface

gbdx = Interface()

# Main command group
@click.group()
def cli():
    """GBDX Command Line Interface

    example:
        gbdx workflow list_tasks
    """
    pass

# Workflow subcommand
@cli.group()
def workflow():
    """Workflow command group"""
    pass

@workflow.command()
def list_tasks():
    """List workflow tasks available to the user"""
    t = gbdx.workflow.list_tasks()
    print json.dumps(t, sort_keys=True, indent=4, separators=(',', ': '))

@workflow.command()
@click.option('--name','-n',
        help="Name of task to describe")
def describe_task(name):
    t = gbdx.workflow.describe_task(name)
    print json.dumps(t, sort_keys=True, indent=4, separators=(',', ': '))

@workflow.command()
@click.option('--id','-i',
        help="ID of the workflow to status")
def status(id):
    status = gbdx.workflow.status(id)
    print json.dumps(status, sort_keys=True, indent=4, separators=(',', ': '))
    
    
