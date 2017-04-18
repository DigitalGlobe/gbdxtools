import pytest

r = pytest.main(["-s", "tests/unit"])
if r:
    raise Exception("There were test failures or errors.")
