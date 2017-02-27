import rasterio

def to_geotiff(image, path=None, proj=None):
    data = image.read()
    meta = image.metadata()
    meta.update({'driver': 'GTiff'})
    if proj is not None:
        meta["crs"] = {'init': proj}
    if path is None:
        path = image._idaho_id + '.tif'
    with rasterio.open(path, "w", **meta) as dst:
        dst.write(data)
