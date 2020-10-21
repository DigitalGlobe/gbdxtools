How to cut releases
-------------------

1. Github stuff:
-------------

* merge to master
* Update version numbers in `setup.py` and `docs/conf.py`
* ```git push origin master --tags```

2. Verify documentation
--------------
Verify that documentation is building properly: check ```https://readthedocs.org/projects/gbdxtools/builds/```

3. Push to pypi
----------

(You may need to `pip install twine anaconda-client`)

```
rm -rf dist
rm -rf egginfo
python setup.py sdist 
twine upload dist/gbdx...
```