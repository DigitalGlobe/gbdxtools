import gbdxtools

gbdx = gbdxtools.Interface()

W, S, E, N = -95.0990905612707, 29.740773208709868, -95.0925674289465, 29.74662324740119
catid = '104001001838A000'

# Download PAN, MS, PS chips from given rectangle and catid
gbdx.idaho.get_chip(coordinates=[W, S, E, N], catid = catid, chip_type='pan', filename='chip_pan.tif')
gbdx.idaho.get_chip(coordinates=[W, S, E, N], catid = catid, chip_type='ms', filename='chip_ms.tif')
gbdx.idaho.get_chip(coordinates=[W, S, E, N], catid = catid, chip_type='ps', filename='chip_ps.tif')
