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
