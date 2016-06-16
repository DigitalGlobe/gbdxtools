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
