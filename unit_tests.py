import pytest
r = pytest.main("tests/unit")
if r:
	raise Exception("There were test failures or errors.")