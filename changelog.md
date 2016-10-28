0.6.8
-----
* Updated leaflet javascript links in leafletmap_template which is used to create idaho slippy maps

0.6.7
-----
* Add gbdx.vectors.query, gbdx.vectors.create, and gbdx.vectors.create_from_wkt

0.6.6
-----
* simpleworkflows.savedata now uses persist flag
* s3.download maintains directory structure

0.6.5
-----
* Can now set impersonation_allowed flag

0.6.4
-----
* Fixed batch workflow bugs

0.6.3
-----
* Handle case where output port description is absent

0.6.2
-----
* Added support for image location API orders.location()

0.6.1
-----
* handle case of spurious keys in s3.download()

0.6.0
-----
* add TaskRegistry class to Interface

0.5.5
-----
* add format & bands parameters to get_idaho_chip_url() function

0.5.4
-----
* add get_idaho_chip_url function

0.5.3
-----
* bugfix in idaho.describe_idaho_images function (was showing wrong sensorPlatformName)

0.5.2
-----
* Add gbdx.catalog.get() and gbdx.catalog.get_strip_metadata()
* Fix bug in simpleworkflow status

0.5.1
-----
* Fix bumpversioning bug.

0.5.0
-----
* Python 3 support (3.3, 3.4, 3.5)

0.4.0
-----
* Batch workflow creation supported.  When you send in an array of values to a workflow input, a batch workflow is automatically created.

0.3.4
-----
* Fix bug with multiplex port assignment.

0.3.3
-----
* Fix bug with output multiplex ports.  Now the root multiplex port is not added to the workflow launched unless another input from another task explicitly refers to it.

0.3.2
-----
* quick change to catalog.get_most_recent_images(): now it takes a list of catalog results as an argument.

0.3.1
-----
* Added multiplex output support to simpleworkflow tasks.

0.3.0
-----
* catalog.search_address() and catalog.search_point() now take the same search filtering parameters as catalog.search().  As a breaking-change side effect, catalog.search_address() and catalog.search_point() now return a list of results, rather than a result-set dictionary.  Also, rather than a singular 'type' parameter, they now both take a list of types in the 'types' argument.


0.2.10
-----
* Added task timeout control to simepleworkflow tasks.

0.2.9
-----
* Added multiplex input port support to simpleworkflow tasks.


0.2.8
-----
* Added ability to get events from simpleworkflows module: ```workflow.events```

0.2.7
-----
* Correct band ordering in the idaho leaflet map viewer
* Upgrade to gbdx-auth 0.1.3 which fixes a token refresh bug


0.2.6
-----

...
