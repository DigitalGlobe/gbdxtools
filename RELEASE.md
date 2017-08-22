How to cut releases
-------------------

1. Github stuff:
-------------

* merge to master
* use bumpversion to increment versions appropriately: ```bumpversion patch``` usually.
* ```git push origin master --tags```

2. Verify documentation
--------------
Verify that documentation is building properly: check ```https://readthedocs.org/projects/gbdxtools/builds/```

3. Push to pypi
----------

```
python setup.py sdist upload -r pypi
```

4. Build conda packages
-------------

Build the package
```
conda build -c digitalglobe -c conda-forge .
```

Upload the package for the platform you just built:
```
anaconda upload -u digitalglobe <filename>
```

If the above build fails due to missing dependencies, you may need to make sure that the dependencies are in fact available in conda.  If they are not, push them up to the digitalglobe channel.


5. Repeat for other python versions
---------

