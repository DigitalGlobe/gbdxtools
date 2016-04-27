'''
Authors: Donnie Marino

Contact: dmarino@digitalglobe.com

Command Line interface for the GBDX tools suite.
This is intended to mimic the aws cli in that users
won't need to program to access the full functionality
of the GBDX API.

This is a Click application
Click is the 'Command Line Interface Creation Kit'
Learn more at http://click.pocoo.org/5/

Main gbdx command group is cli

Subcommands are click groups

Commands belong to one click group, allows for cli syntax like this:

gbdx workflow list_tasks

gbdx workflow describe_task -n MutualInformationCoregister

gbdx catalog strip_footprint -c 10200100359B2C00

'''

import click
import json
from gbdxtools import Interface

gbdx = Interface()

# report pretty json
def show(js):
    print json.dumps(js, sort_keys=True, indent=4, separators=(',', ': '))

# Main command group
@click.group()
def cli():
    """GBDX Command Line Interface

    example:
        gbdx workflow list_tasks
    """
    pass

@cli.group()
def workflow():
    """GBDX Workflow Interface"""
    pass

@workflow.command()
def list_tasks():
    """List workflow tasks available to the user"""
    show( gbdx.workflow.list_tasks() )
    
@workflow.command()
@click.option('--name','-n',
    help="Name of task to describe")
def describe_task(name):
    """Show the task description json for the task named"""
    show( gbdx.workflow.describe_task(name) )

@workflow.command()
@click.option('--id','-i',
    help="ID of the workflow to status")
def status(id):
    """Display the status information for the workflow ID given"""
    show( gbdx.workflow.status(id) )

   
@cli.group()
def catalog():
    """GBDX Catalog Interface"""
    pass

@catalog.command()
@click.option("--catalog_id", "-c",
    help="Catalog ID of the strip to display")
def strip_footprint(catalog_id):
    """Show the WKT footprint of the strip named"""
    show(gbdx.catalog.get_strip_footprint_wkt(catalog_id))

@cli.group()
def ordering():
    """GBDX Ordering Interface"""
    pass

@ordering.command()
@click.option("--catalog_id", "-c",
    multiple=True,
    help="Catalog ID of the strip to order. May pass multiple times")
def order(catalog_id):
    """Order the catalog ID(s) passed in"""
    if len(catalog_id == 0):
        print "No catalog IDs passed in."
        return
    if len(catalog_id) == 1:
        # pull the one item and just order that
        show( gbdx.ordering.order(catalog_id[0]) )
    else:
        # this is a list with multiple entries
        show( gbdx.ordering.order(catalog_id) )

@ordering.command()
@click.option("--order_id","-o",
    help="Order ID to status")
def status(order_id):
    show( gbdx.ordering.status(id) )


@cli.group()
def s3():
    """GBDX S3 Interface"""
    pass

@s3.command()
def info():
    """Display the s3 information for this GBDX User"""
    show(gbdx.s3.info)


@cli.group()
def idaho():
    """GBDX Idaho Interface"""
    pass

@idaho.command()
@click.option("--catalog_id","-c",
    help="Catalog ID to fetch IDAHO images for")
def get_images_by_catid(catalog_id):
    """Retrieve all IDAHO Images associated with a catalog ID"""
    show(gbdx.idaho.get_images_by_catid(catalog_id))
