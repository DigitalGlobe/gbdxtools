
Install Python
--------------

Open up a web browser and paste in this URL to download python:  
```https://www.python.org/ftp/python/2.7.13/python-2.7.13.msi```

Open up the download and make sure you check the box "add python.exe to path".

Install Other Dependencies
--------------

Install gdal:

Open windows powershell (not the cmd utility):

```
curl -outf GDAL-2.1.3-cp27-cp27m-win32.whl https://github.com/DigitalGlobe/gbdxtools-windows-binaries/blob/master/GDAL-2.1.3-cp27-cp27m-win32.whl?raw=true
pip install .\GDAL-2.1.3-cp27-cp27m-win32.whl
```

Install Shapely:

```
curl -outf Shapely-1.5.17-cp27-cp27m-win32.whl https://github.com/DigitalGlobe/gbdxtools-windows-binaries/blob/master/Shapely-1.5.17-cp27-cp27m-win32.whl?raw=true
pip install .\Shapely-1.5.17-cp27-cp27m-win32.whl
```

Install rasterio:

```
curl -outf rasterio-1.0a5-cp27-cp27m-win32.whl https://github.com/DigitalGlobe/gbdxtools-windows-binaries/blob/master/rasterio-1.0a5-cp27-cp27m-win32.whl?raw=true
pip install .\rasterio-1.0a5-cp27-cp27m-win32.whl
```

Install pyproj:

```
curl -outf pyproj-1.9.5.1-cp27-cp27m-win32.whl https://github.com/DigitalGlobe/gbdxtools-windows-binaries/blob/master/pyproj-1.9.5.1-cp27-cp27m-win32.whl?raw=true
pip install .\pyproj-1.9.5.1-cp27-cp27m-win32.whl
```

Install matplotlib:
```
pip install matplotlib
```

Install gbdxtools
--------------
```
pip install gbdxtools
```
