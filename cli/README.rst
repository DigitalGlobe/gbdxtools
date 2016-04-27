==============================================
gbdxtools CLI: Command Line Interface for GBDX
==============================================

The gbdxtools package includes a Command Line Interface for ease of use.

Access to the GBDX API is provided without the need for programming.

**Installation**

The command is 'gbdx' and it is installed when you pip install the gbdxtools package into your virtualenv.

**Usage**

Note: gbdx cli uses the gbdxtools package, which requires GBDX credentials to be present in the users home dir.
In order to use gbdx cli, you need GBDX credentials. Email geobigdata@digitalglobe.com to get these.

Help and usage information are built into the tool, use the --help switch or just throw bad commands to see it.

Note how you can walk through the command group and subcommands to get more specific help.

::

    ]$ gbdx --help
    Usage: gbdx [OPTIONS] COMMAND [ARGS]...

      GBDX Command Line Interface

      example:     gbdx workflow list_tasks

    Options:
      --help  Show this message and exit.

    Commands:
      catalog   GBDX Catalog Interface
      idaho     GBDX Idaho Interface
      ordering  GBDX Ordering Interface
      s3        GBDX S3 Interface
      workflow  GBDX Workflow Interface

    ]$ gbdx workflow --help
    Usage: gbdx workflow [OPTIONS] COMMAND [ARGS]...

      GBDX Workflow Interface

    Options:
      --help  Show this message and exit.

    Commands:
      describe_task  Show the task description json for the task...
      list_tasks     List workflow tasks available to the user
      status         Display the status information for the...

    ]$ gbdx workflow describe_task --help
    Usage: gbdx workflow describe_task [OPTIONS]

      Show the task description json for the task named

    Options:
      -n, --name TEXT  Name of task to describe
      --help           Show this message and exit.

**Examples**

::

    ]$ gbdx workflow list_tasks
    {
    "tasks": [
        "Downsample",
        "protogenRAW",
        "protogenUBFP",
        "AComp",
        "StageDataToS3",
        "FastOrtho",
        ... lots more tasks ...
    ]}

    ]$ gbdx workflow describe_task --name AComp
    {
        "containerDescriptors": [
            {
                "command": "",
                "properties": {
                    "image": "tdgp/acomp:latest"
                },
                "type": "DOCKER"
            }
        ],
        "description": "Runs AComp code on an input 1B image.",
        "inputPortDescriptors": [
            {
        ... more task descriptor json ...
    }
    

**Development**

gbdx cli is a Click application. Learn more about Click at http://click.pocoo.org/5/

Installation is done via the setup.py file in the project's home dir. Look for the entry_points clause.

