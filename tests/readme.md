## Running tests in GBDXtools

The GBDXtools tests use VCRpy to record network interaction. The data representing the server calls are stored in a yaml file called a _cassette_. When a test is run it uses the cassette data to run the test. This speeds up the tests and reduces load on the GBDX and third-party servers. It also means that automated tests can run without needing GBDX access. However, this does mean that if the back-end API changes the VCRpy "cassette" **must** be regenerated. If the test's request content changes VCRpy will force you to generate a new cassette.

To run all tests:

`python -m pytest tests/`

To run one test file:

`python -m pytest tests/unit/test_vectors.py`

To run a specific test in the file:

`python -m pytest tests/unit/test_vectors.py -k "test_vectors_search_paging"`


### New tests vs. old tests

Some tests are old - you can identify them because they import from `gbdx_mock`. Other old tests use a matcher called `FORCE` that forces tests to match to their cassettes. These tests are still functional as long as the API they are accessing hasn't changed.

Changing these tests, and especially updating them to the new test patterns, means the cassettes will have to be regenerated. This means that the values the API returns could be different. So for example, a test that searches a given polygon without a date range will return a growing result count over time. This means the test will need to be updated to a new value, or should find a different way to test.

Tests that run on images will need those images to be available in RDA. There are some image catalog IDs available as constants in the `helpers` module. These IDs should always be available. Whenever possible, use these constants instead of arbitrary catalog IDs.

So in short, if you don't need to update a test file, it's probably best to leave it in the older formats. But if you do need to update a single test, please update the whole file to the new patterns and regenerate new cassettes.

### Regenerating cassettes

- Delete the old cassette file
- Set the `WRITE_CASSETTE` environment variable when you run the test.
  - You can `export WRITE_CASSETTE=True` once, and `unset WRITE_CASSETTE` when you're done.
  - or set it temporarily in the command: `WRITE_CASSETTE=True python -m pytest tests/unit/test_vectors.py`

If the test is an old one using `gbdx_mock` instead of `mockable_interface`, you would need to export `GBDX_MOCK` instead of `WRITE_CASSETTE`. But instead, update the test to use `mockable_interface`, because it doesn't make sense to set `GBDX_MOCK` when you're specifically not mocking the connection.


### Adding new tests to the test files

- If your test requires communicating with GBDX, use a VCRpy decorator, passing the path to where you would like to store the cassette. It is helpful for troubleshooting to have your cassette yaml file name match your test function name, but not necessary.

``` python
@gbdx_vcr.use_cassette('tests/unit/cassettes/test_some_gbdx_thing.yaml')
def test_some_gbdx_thing(self):
    ...
```

### Tests that don't have GBDX or other server interaction

- If there's no server interaction to record, just write the test normally.


### Writing new test files

Copy the structure from other tests. In general, you'll need to follow this pattern:

``` python
import unittest
from helpers import mockable_interface, gbdx_vcr 

class TestSomething(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ''' Set up the class to have a mockable interface for tests to use '''
        cls.gbdx = mockable_interface() 

    @gbdx_vcr.use_cassette('tests/unit/cassettes/test_something.yaml')
    def test_vectors_search_paging(self):
        # use classes that are already bound to an interface session!
        results = self.gbdx.something.some_function()
        self.assertEqual(results, 'some_results')
```
       




