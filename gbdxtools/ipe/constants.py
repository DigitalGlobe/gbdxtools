'''
Constants for geoio
'''
from osgeo import gdalconst
import numpy as np

##### Numpy <-> Gdal Conversion Dictionaries ##################################
# Numpy data type to the corresponding GDAL data type.
DICT_NP_TO_GDAL = {np.dtype('uint8') : gdalconst.GDT_Byte,
                   np.dtype('uint16') : gdalconst.GDT_UInt16,
                   np.dtype('uint32') : gdalconst.GDT_UInt32,
                   np.dtype('int16') : gdalconst.GDT_Int16,
                   np.dtype('int32') : gdalconst.GDT_Int32,
                   np.dtype('float32') : gdalconst.GDT_Float32,
                   np.dtype('float64') : gdalconst.GDT_Float64
}

# GDAL data type to the corresponding Numpy data type.
DICT_GDAL_TO_NP = {gdalconst.GDT_Byte : np.dtype('uint8'),
                   gdalconst.GDT_UInt16 : np.dtype('uint16'),
                   gdalconst.GDT_UInt32 : np.dtype('uint32'),
                   gdalconst.GDT_Int16 : np.dtype('int16'),
                   gdalconst.GDT_Int32 : np.dtype('int32'),
                   gdalconst.GDT_Float32 : np.dtype('float32'),
                   gdalconst.GDT_Float64 : np.dtype('float64')
}
###############################################################################


##### DigitalGlobe File Suffixes and Search Strings ###########################
# DG meta file endings
# If XML exists, it should contains same info as the rest of the files.
DG_META = ['.XML','.IMD','.RPB','.RAD']

# Various strings that describe the same DigitalGlobe bands
DG_BANDID = {
    'DIR_NAME' : ['PAN','MUL','SWR','CAV'],
    'ENGLISH' : ['PAN','MS','SWIR','CAVIS'],
    'IMDXML' : ['P','Multi','All-S','All-C']
}

# This controls which version of DGAComp is run.  It is used to index the
# dictionary below (DGACOMP)
DGACOMP_INDEX = 0

# Info about DGAComp include the location of the DGAComp idl code
# ToDo: replace with dynamic code
DGACOMP = {
    'VERSION' : ['023'],
    'TARGET' : ['/mnt/tier3/nathan/DGAComp/']
}

# Holder for file endings useful in creating/search for spectral files
#ToDo: Handle the version number in the acomp dir and file suffix
dgcv = DGACOMP['VERSION'][DGACOMP_INDEX]
DG_SPEC = {
    'RAD_IMGS' : ['_Rad'],
    'TOA_IMGS' : ['_TOARef','_TOA'],
    'DGACOMP_IMGS' : ['_DG-AComp_v'+dgcv,'_DGAComp_v'+dgcv],
    'DGACOMP_AOD' : ['_DG-AComp_v'+dgcv+'_AODmap','_DGAComp_v'+dgcv+'_AODmap']
}
###############################################################################

##### DigitalGlobe Band names and aliases #####################################

DG_BAND_NAMES = {
    'QB02_MULTI' :  ['B','G','R','N1'],
    'QB02_P' :      ['P'],
    'IK02_MULTI' :  ['B','G','R','N1'],
    'IK02_P' :      ['P'],
    'GE01_MULTI' :  ['B','G','R','N1'],
    'GE01_P' :      ['P'],
    'WV01_P' :      ['P'],
    'WV02_MULTI' :  ['C','B','G','Y','R','RE','N1','N2'],
    'WV02_MS1' :    ['B','G','R','N1'],
    'WV02_MS2' :    ['C','Y','RE','N2'],
    'WV02_P' :      ['P'],
    'WV03_MULTI' :  ['C','B','G','Y','R','RE','N1','N2'],
    'WV03_MS1' :    ['B','G','R','N1'],
    'WV03_MS2' :    ['C','Y','RE','N2'],
    'WV03_P' :      ['P'],
    'WV03_ALL-S' :  ['S1','S2','S3','S4','S5','S6','S7','S8']
}

# The definition of spectral regions varies between fields and can be debated.
# For these purposes, the following definitions are used:
# XX = Atmospherically opaque region
#
#|---------------VNIR------------------|
#|                    |-----------------------IR-------------------------|
#|----- VIS ----------|-RE-|----NIR----|--SWIR---|XX|-SWIR-|XXXX|--SWIR--|
#|   C  B    G  Y  R    RE   N1     N2   S1          S2/3/4      S5/6/7/8|
#| 0.4 | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 | 1.0 | 1.3 | 1.5 | 1.8 | 2.0 | 2.5 |

DG_BAND_ALIASES = {
    # Base Regions
    'VIS'       : ['C','B','G','Y','R'],
    'RE'        : ['RE'],
    'NIR'       : ['N1','N2'],
    'SWIR'      : ['S1','S2','S3','S4','S5','S6','S7','S8'],
    # Combined Regions
    'VNIR'      : ['C','B','G','Y','R','RE','N1','N2'],
    'IR'        : ['RE','N1','N2','S1','S2','S3','S4','S5','S6','S7','S8'],
    # Band Combinations
    'BGRN'      : ['B','G','R','N1'],
    'RGB'       : ['R','G','B'],
    'RGBN'      : ['R','G','B','N1']
}

###############################################################################

##### DigitalGlobe RSR Weighted Band Center Values ############################
DG_WEIGHTED_BAND_CENTERS = {
    'QB02_MULTI' : [478.40,542.89,650.45,803.41],
    'QB02_P' :     [674.58],
    'IK02_MULTI' : [483.07,550.62,663.25,794.37],
    'IK02_P' :     [723.00],
    'GE01_MULTI' : [484.52,547.87,675.20,836.52],
    'GE01_P' :     [631.79],
    'WV01_P' :     [670.17],
    'WV02_MULTI' : [428.58,479.35,548.07,607.78,658.92,723.27,825.06,914.55],
    'WV02_MS1' :   [479.35,548.07,658.92,825.06],
    'WV02_P' :     [651.05],
    'WV03_MULTI' : [427.38,481.92,547.14,604.28,
                    660.11,722.73,824.04,913.65],
    'WV03_MS1' :   [481.92,547.14,
                    660.11,824.04],
    'WV03_P' :     [649.36],
    'WV03_ALL-S' : [1209.06,1571.61,1661.10,1729.54,
                    2163.69,2202.16,2259.32,2329.22]
    # 'WV03_MULTI' : [428.07,482.04,547.17,604.28,
    #                 660.14,722.74,824.04,913.39],
    # 'WV03_P' : [649.89],
    # 'WV03_ALL-S' : [1209.06,1571.61,1661.10,1729.54,
    #                 2163.69,2202.16,2259.32,2329.22]
}
###############################################################################


##### DigitalGlobe ESun Values ################################################
'''
E-SUN - Day 93 (E-S = 1 AU)

Derived from solar curves:
Thuillier 2003  - Column 1
ChKur           - Column 2
WRC             - Column 3

WorldView-3
PAN     1574.41 1578.28 1583.58
COASTAL 1757.89 1743.9  1743.81
BLUE    2004.61 1974.53 1971.48
GREEN   1830.18 1858.1  1856.26
YELLOW  1712.07 1748.87 1749.4
RED     1535.33 1550.58 1555.11
REDEDGE 1348.08 1303.4  1343.95
NIR1    1055.94 1063.92 1071.98
NIR2    858.77  858.632 863.296
SWIR 1  479.019 478.873 494.595
SWIR 2  263.797 257.55  261.494
SWIR 3  225.283 221.448 230.518
SWIR 4  197.552 191.583 196.766
SWIR 5  90.4178 86.5651 80.365
SWIR 6  85.0642 82.0035 74.7211
SWIR 7  76.9507 74.7411 69.043
SWIR 8  68.0988 66.3906 59.8224

WorldView-2
PAN     1571.36 1575.38 1580.76
COASTAL 1773.81 1759.24 1757.77
BLUE    2007.27 1977.4  1974.29
GREEN   1829.62 1857.89 1856.03
YELLOW  1701.85 1738.11 1738.59
RED     1538.85 1554.95 1559.35
REDEDGE 1346.09 1302.19 1342.05
NIR1    1053.21 1061.4  1069.59
NIR2    856.599 856.816 861.201

WorldView-1
PAN 1478.62 1481.48 1487.92

GeoEye-1
PAN     1610.73 1614.88 1619.49
BLUE    1993.18 1966.03 1963.53
GREEN   1828.83 1857.12 1855.25
RED     1491.49 1500.38 1506.29
NIR     1022.58 1029.61 1037.7

IKONOS
PAN     1353.25 1358.59 1364.06
BLUE    1921.26 1902.54 1901.19
GREEN   1803.28 1827.32 1826.04
RED     1517.76 1526.48 1532.48
NIR     1145.8  1150.51 1155.37

QuickBird
PAN     1370.92 1376.3  1381.72
BLUE    1949.59 1926.55 1924.62
GREEN   1823.64 1844.26 1842.81
RED     1553.78 1571.58 1574.65
NIR     1102.85 1107.47 1113.72

CAVIS
Desert Clouds       1718.25 1712.25 1712.92
Aerosol-1           2001.13 1968.46 1966.77
Green               1831.3  1861.44 1858.48
Aerosol-2           1537.38 1554.15 1558.97
Water-1             955.658 955.79  974.37
Water-2             866.791 869.104 864.878
Water-3             807.875 808.077 787.589
NDVI-SWIR           460.196 460.905 478.788
Cirrus              361.412 355.142 363.49
Snow                230.349 226.394 234.085
Aerosol-3           89.1345 85.8585 79.5456
Aerosol-3 Parallax  89.1345 85.8585 79.5456

'''
# ESUN values from the Thuillier column above.
DG_ESUN = {
    'QB02_MULTI' : [1949.59, 1823.64, 1553.78, 1102.85],
    'QB02_P' :     [1370.92],
    'IK02_MULTI' : [1921.26, 1803.28, 1517.76, 1145.8],
    'IK02_P' :     [1353.25],
    'GE01_MULTI' : [1993.18, 1828.83, 1491.49, 1022.58],
    'GE01_P' :     [1610.73],
    'WV01_P' :     [1478.62],
    'WV02_MULTI' : [1773.81, 2007.27, 1829.62, 1701.85,
                    1538.85, 1346.09, 1053.21, 856.599],
    'WV02_MS1' :   [2007.27, 1829.62,
                    1538.85, 1053.21],
    'WV02_P' :     [1571.36],
    'WV03_MULTI' : [1757.89, 2004.61, 1830.18, 1712.07,
                    1535.33, 1348.08, 1055.94, 858.77],
    'WV03_MS1' :   [2004.61, 1830.18,
                    1535.33, 1055.94],
    'WV03_P' :     [1574.41],
    'WV03_ALL-S' : [479.019, 263.797, 225.283, 197.552,
                    90.4178, 85.0642, 76.9507, 68.0988],
    'WV03_ALL-C' : [1718.25,2001.13,1831.3,1537.38,
                    955.658,866.791,807.875,460.196,
                    361.412,230.349,89.1345,89.1345]
}
###############################################################################


##### DigitalGlobe Absolute Cal ###############################################
DG_ABSCAL_GAIN = {
    'QB02_P' :     [0.876],
    'QB02_MULTI' : [1.121,1.084,1.068,1.024],
    'IK02_P' :     [0.907],
    'IK02_MULTI' : [1.073,0.990,0.940,1.043],
    'GE01_P' :     [0.978],
    'GE01_MULTI' : [1.059,1.001,1.009,1.011],
    'WV01_P' :     [1.016],
    'WV02_P' :     [0.960],
    'WV02_MULTI' : [1.146,1.003,0.953,0.965,
                    0.969,1.003,0.981,1.037],
    'WV02_MS1' :   [1.003,0.953,
                    0.969,0.981],
    'WV03_P' :     [0.923],
    'WV03_MULTI' : [0.863,0.905,0.907,0.938,
                    0.945,0.980,0.982,0.954],
    'WV03_MS1' :   [0.905,0.907,
                    0.945,0.982],
    'WV03_ALL-S' : [1.160,1.184,1.173,1.187,
                    1.286,1.336,1.340,1.392],
#     'WV03_ALL-C' : [0.949,1.06,1.272,1.04,
#                     1.177,1.182,1.009,1.363,
#                     1.082,1.148,0.855,0.825]
}

DG_ABSCAL_OFFSET = {
    'QB02_P' :     [-2.157],
    'QB02_MULTI' : [-5.427,-4.779,-3.492,-5.096],
    'IK02_P' :     [-4.461],
    'IK02_MULTI' : [-9.699,-7.937,-4.767,-8.869],
    'GE01_P' :     [-1.948],
    'GE01_MULTI' : [-6.590,-4.352,-3.222,-4.085],
    'WV01_P' :     [-3.932],
    'WV02_P' :     [-2.957],
    'WV02_MULTI' : [-10.474,-7.795,-4.047,-3.467,
                    -2.257,-4.103,-3.081,-2.818],
    'WV02_MS1' :   [-7.795,-4.047,
                    -2.257,-3.081],
    'WV03_P' :     [-1.700],
    'WV03_MULTI' : [-7.154,-4.189,-3.287,-1.816,
                    -1.350,-2.617,-3.752,-1.507],
    'WV03_MS1' :   [-4.189,-3.287,
                    -1.350,-3.752],
    'WV03_ALL-S' : [-4.479,-2.248,-1.806,-1.507,
                    -0.622,-0.605,-0.423,-0.302],
#     'WV03_ALL-C' : [11.322,10.891,6.574,13.468,
#                     -5.88,1.95,5.689,-6.815,
#                     0.178,-0.673,0.167,0.400]
}
###############################################################################
