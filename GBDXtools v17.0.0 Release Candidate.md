# GBDXtools v17.0.x Release Candidate



GBDXtools v0.17 is coming soon with some major internal changes. Now is the time to test against critical systems. Because of internal changes older versions of GBDXtools will eventually be unable to fetch imagery. You can install and test the v0.17 release candidate the following ways:

- pip: `pip install gbdxtools==0.17.0rc2`
- pipenv: `pipenv install gbdxtools==0.17.0rc2`
- conda: `conda install -c digitalglobe -c digitalglobe/label/rc gbdxtools=0.17.0rc2`
- notebooks: https://staging-notebooks.geobigdata.io/ has v17.0.0rc1 for testing

Windows dependencies have been collected here:

- https://github.com/DigitalGlobe/gbdxtools-windows-dependencies



### Important Changes:

#### Python 2 support

- As announced, GBDXtools will not be tested against Python 2 going forwards
- Portions of v0.17.0 may still function with Python 2
- Python 2 compatibility will be completely removed from v0.17.1

#### Streamlined Installation and Dependencies

- Conda package reduced to 79kb from 10mb
- Removed dependencies to full Dask and SciKit Image packages
- Notebooks will continue to install Pandas (part of Dask) and SciKit Image

#### Graph API sunset

- Older versions of GBDXtools use the deprecated RDA Graph API to access imagery
- The Graph API has been deprecated so GBDXtools now uses the Template API to access imagery
- Any code that uses the `rda = RDA()` pattern to build or modify graphs will need to use templates
- Older versions of GBDXtools will function until the Graph API is turned off in April 2020
- **You will need to migrate to v0.17.x versions to access imagery after April 2020**

#### `Preview()` removed

- The `preview` function does not consitute a preview and triggers data consumption
- The function relied on deprecated RDA functionality and has been deleted

#### `warp`ing removed

- The Dask-delayed `warp()` function has been broken for several years
- Absent demand for a fix, the method has been deleted

#### `.geotiff(spec=rgb)` change in behavior

* `spec=rgb` used to enable DRA on an image object without DRA
* Going forward, the image object will need to be initialized with DRA to write "RGB" geotiffs
* Geotiffs using just RGB _bands_ are possible by passing the RGB bands with the `bands` kwarg
* Consider using the GDAL RDA Driver instead for small areas, and RDA Materialization for large areas

#### Base Layer Matching changes

- BLM functionality depended on Maps API imagery which was deprecated
- BLM will now match to the image's Browse image

#### TMSImage is now bring-your-own-tiles

* TMSImage also depended on deprecated Maps API imagery 
* The class now requires the user specify a TMS service to use

#### PyProj updates

* PyProj has seen major updates, which may cause warnings in code using older classes
* You can now use `CRS(4326)` instead of `Proj('init=EPSG:4326')`

#### More checks and better error messages

- `CatalogImage` does better checking of an image's status and availability
- Specific errors are thrown when images are not available in GBDX
- The checks do slow down initializing `CatalogImages`

#### S3 pagination and prefixes

- S3 calls were limited to 1000 objects
- Now they use pagination
- Improved prefix handling for specifying file paths







