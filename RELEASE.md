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

(You may need to `pip install twine anaconda-client`)

```
rm -rf dist
rm -rf egginfo
python setup.py sdist 
twine upload dist/gbdx...
```

4. Build Conda packages
-------------

Update the SHA in meta.yaml, using value from PyPi or use `openssl dgst -sha256 dist/gbdx...`

Clean up old builds:
```
conda build purge
```

Build the package
```
conda build -c digitalglobe -c conda-forge --no-include-recipe .
```

Upload the package for the platform you just built:
```
anaconda upload -u digitalglobe <filename>
```


To upload a package for beta testing:
```
anaconda upload -u digitalglobe --label beta <filename>
```

If the above build fails due to missing dependencies, you may need to make sure that the dependencies are in fact available in Conda.  If they are not, push them up to the digitalglobe channel.

