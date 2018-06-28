import warnings
import os
import errno
import datetime
import time
import math
import json
from functools import wraps, partial
from collections import Sequence
try:
    from itertools import izip
except ImportError:  #python3.x
    izip = zip

import numpy as np
from numpy.linalg import pinv
from skimage.transform._geometric import GeometricTransform

import xml.etree.cElementTree as ET
from xml.dom import minidom
import ephem
from string import Template

from shapely.geometry import shape, box
from shapely.wkt import loads
from shapely import ops
from affine import Affine
import pyproj

from gbdxtools.ipe.graph import VIRTUAL_IPE_URL 
import gbdxtools.ipe.constants as constants

with warnings.catch_warnings():
    warnings.simplefilter("ignore")

IPE_TO_DTYPE = {
    "BINARY": "bool",
    "BYTE": "byte",
    "SHORT": "short",
    "UNSIGNED_SHORT": "ushort",
    "INTEGER": "int32",
    "UNSIGNED_INTEGER": "uint32",
    "LONG": "int64",
    "UNSIGNED_LONG": "uint64",
    "FLOAT": "float32",
    "DOUBLE": "float64"
}

# TODO need to handle diff projections: project WGS84 bounds into image proj
def preview(image, **kwargs):
    try:
        from IPython.display import Javascript, HTML, display
        from gbdxtools import Interface
        gbdx = Interface()
    except:
        print("IPython is required to produce maps.")
        return

    zoom = kwargs.get("zoom", 16)
    bands = kwargs.get("bands")
    if bands is None:
        bands = image._rgb_bands
    wgs84_bounds = kwargs.get("bounds", list(loads(image.ipe_metadata["image"]["imageBoundsWGS84"]).bounds))
    center = kwargs.get("center", list(shape(image).centroid.bounds[0:2]))
    graph_id = image.ipe_id
    node_id = image.ipe.graph()['nodes'][0]['id']

    stats = image.display_stats
    offsets = [stats['offset'][b] for b in bands]
    scales = [stats['scale'][b] for b in bands]

    if image.proj != 'EPSG:4326':
        code = image.proj.split(':')[1]
        conn = gbdx.gbdx_connection
        proj_info = conn.get('https://ughlicoordinates.geobigdata.io/ughli/v1/projinfo/{}'.format(code)).json()
        tfm = partial(pyproj.transform, pyproj.Proj(init='EPSG:4326'), pyproj.Proj(init=image.proj))
        bounds = list(ops.transform(tfm, box(*wgs84_bounds)).bounds)
    else:
        proj_info = {}
        bounds = wgs84_bounds
    
    map_id = "map_{}".format(str(int(time.time())))
    display(HTML(Template('''
       <div id="$map_id"/>
       <link href='https://openlayers.org/en/v4.6.4/css/ol.css' rel='stylesheet' />
       <script src="https://cdn.polyfill.io/v2/polyfill.min.js?features=requestAnimationFrame,Element.prototype.classList,URL"></script>
       <style>body{margin:0;padding:0;}#$map_id{position:relative;top:0;bottom:0;width:100%;height:400px;}</style>
       <style></style>
    ''').substitute({"map_id": map_id}))) 

    js = Template("""
        require.config({
            paths: {
                oljs: 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/4.6.4/ol',
                proj4: 'https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.4.4/proj4'
            }
        });

        require(['oljs', 'proj4'], function(oljs, proj4) {
            oljs.proj.setProj4(proj4)
            var md = $md;
            var georef = $georef;
            var graphId = '$graphId';
            var nodeId = '$nodeId';
            var extents = $bounds; 

            var x1 = md.minTileX * md.tileXSize;
            var y1 = ((md.minTileY + md.numYTiles) * md.tileYSize + md.tileYSize);
            var x2 = ((md.minTileX + md.numXTiles) * md.tileXSize + md.tileXSize);
            var y2 = md.minTileY * md.tileYSize;
            var tileLayerResolutions = [georef.scaleX];

            var url = '$url' + '/tile/';
            url += graphId + '/' + nodeId;
            url += "/{x}/{y}.png?token=$token&display_bands=$bands&display_scales=$scales&display_offsets=$offsets";

            var proj = '$proj';
            var projInfo = $projInfo;
    
            if ( proj !== 'EPSG:4326' ) {
                var proj4def = projInfo["proj4"];
                proj4.defs(proj, proj4def);
                var area = projInfo["area_of_use"];
                var bbox = [area["area_west_bound_lon"], area["area_south_bound_lat"], 
                            area["area_east_bound_lon"], area["area_north_bound_lat"]]
                var projection = oljs.proj.get(proj);
                var fromLonLat = oljs.proj.getTransform('EPSG:4326', projection);
                var extent = oljs.extent.applyTransform(
                    [bbox[0], bbox[1], bbox[2], bbox[3]], fromLonLat);
                projection.setExtent(extent);
            } else {
                var projection = oljs.proj.get(proj);
            }

            var rda = new oljs.layer.Tile({
              title: 'RDA',
              opacity: 1,
              extent: extents,
              source: new oljs.source.TileImage({
                      crossOrigin: null,
                      projection: projection,
                      extent: extents,

                      tileGrid: new oljs.tilegrid.TileGrid({
                          extent: extents,
                          origin: [extents[0], extents[3]],
                          resolutions: tileLayerResolutions,
                          tileSize: [md.tileXSize, md.tileYSize],
                      }),
                      tileUrlFunction: function (coordinate) {
                          if (coordinate === null) return undefined;
                          const x = coordinate[1] + md.minTileX;
                          const y = -(coordinate[2] + 1 - md.minTileY);
                          if (x < md.minTileX || x > md.maxTileX) return undefined;
                          if (y < md.minTileY || y > md.maxTileY) return undefined;
                          return url.replace('{x}', x).replace('{y}', y);
                      }
                  })
            });

            var map = new oljs.Map({
              layers: [ rda ],
              target: '$map_id',
              view: new oljs.View({
                projection: projection,
                center: $center,
                zoom: $zoom
              })
            });
        });
    """).substitute({
        "map_id": map_id,
        "proj": image.proj,
        "projInfo": json.dumps(proj_info),
        "graphId": graph_id,
        "bounds": bounds,
        "bands": ",".join(map(str, bands)),
        "nodeId": node_id,
        "md": json.dumps(image.ipe_metadata["image"]),
        "georef": json.dumps(image.ipe_metadata["georef"]),
        "center": center,
        "zoom": zoom,
        "token": gbdx.gbdx_connection.access_token,
        "scales": ",".join(map(str, scales)),
        "offsets": ",".join(map(str, offsets)),
        "url": VIRTUAL_IPE_URL
    })
    display(Javascript(js))

def reproject_params(proj):
    _params = {}
    if proj is not None:
        _params["Source SRS Code"] = "EPSG:4326"
        _params["Source pixel-to-world transform"] = None
        _params["Dest SRS Code"] = proj
        _params["Dest pixel-to-world transform"] = None
    return _params

def ortho_params(proj, gsd=None):
    params = {}
    if gsd is not None:
        params["Requested GSD"] = str(gsd)
        params["Resampling Kernel"] = "INTERP_BILINEAR"
        params["Grid Size"] = 10
    if proj is not None:
        params["Output Coordinate Reference System"] = proj
        params["Sensor Model"] = None
        params["Elevation Source"] = ""
        params["Output Pixel to World Transform"] = ""
    return params


def calc_toa_gain_offset(meta):
    """
    Compute (gain, offset) tuples for each band of the specified image metadata
    """
    # Set satellite index to look up cal factors
    sat_index = meta['satid'].upper() + "_" + meta['bandid'].upper()

    # Set scale for at sensor radiance
    # Eq is:
    # L = GAIN * DN * (ACF/EBW) + Offset
    # ACF abscal factor from meta data
    # EBW effectiveBandwidth from meta data
    # Gain provided by abscal from const
    # Offset provided by abscal from const
    acf = np.asarray(meta['abscalfactor'])  # Should be nbands length
    ebw = np.asarray(meta['effbandwidth'])  # Should be nbands length
    gain = np.asarray(constants.DG_ABSCAL_GAIN[sat_index])
    scale = (acf / ebw) * gain
    offset = np.asarray(constants.DG_ABSCAL_OFFSET[sat_index])

    e_sun_index = meta['satid'].upper() + "_" + meta['bandid'].upper()
    e_sun = np.asarray(constants.DG_ESUN[e_sun_index])
    sun = ephem.Sun()
    img_obs = ephem.Observer()
    img_obs.lon = meta['latlonhae'][1]
    img_obs.lat = meta['latlonhae'][0]
    img_obs.elevation = meta['latlonhae'][2]
    img_obs.date = datetime.datetime.fromtimestamp(meta['img_datetime_obj_utc']['$date'] / 1000.0).strftime(
        '%Y-%m-%d %H:%M:%S.%f')
    sun.compute(img_obs)
    d_es = sun.earth_distance

    # Pull sun elevation from the image metadata
    # theta_s can be zenith or elevation - the calc below will us either
    # a cos or s in respectively
    # theta_s = float(self.meta_dg.IMD.IMAGE.MEANSUNEL)
    theta_s = 90 - float(meta['mean_sun_el'])
    scale2 = (d_es ** 2 * np.pi) / (e_sun * np.cos(np.deg2rad(theta_s)))

    # Return scaled data
    # Radiance = Scale * Image + offset, Reflectance = Radiance * Scale2
    return zip(scale, scale2, offset)


class RatPolyTransform(GeometricTransform):
    def __init__(self, A, B, offset, scale, px_offset, px_scale, gsd=None, proj=None, default_z=0):
        self.proj = proj
        self._A = A
        self._B = B
        self._offset = offset
        self._scale = scale
        self._px_offset = px_offset
        self._px_scale = px_scale
        self._gsd = gsd
        self._offscl = np.vstack([offset, scale])
        self._offscl_rev = np.vstack([-offset/scale, 1.0/scale])
        self._px_offscl_rev = np.vstack([px_offset, px_scale])
        self._px_offscl = np.vstack([-px_offset/px_scale, 1.0/px_scale])

        self._default_z = default_z

        self._A_rev = np.dot(pinv(np.dot(np.transpose(A), A)), np.transpose(A))
        # only using the numerator (more dynamic range for the fit?)
        # self._B_rev = np.dot(pinv(np.dot(np.transpose(B), B)), np.transpose(B))

    @property
    def gsd(self):
        return self._gsd

    def rev(self, lng, lat, z=None, _type=np.int32):
        if z is None:
            z = self._default_z

        if all(isinstance(var, (int, float, tuple)) for var in [lng, lat]):
            lng, lat = (np.array([lng]), np.array([lat]))
        if not all(isinstance(var, np.ndarray) for var in [lng, lat]):
            raise ValueError("lng, lat inputs must be of type int, float, tuple or numpy.ndarray")
        if not isinstance(z, np.ndarray):
            z = np.zeros_like(lng) + z
        coord = np.dstack([lng, lat, z])
        offset, scale = np.vsplit(self._offscl, 2)
        normed = coord * scale + offset
        X = self._rpc(normed)
        result = np.rollaxis(np.inner(self._A, X) / np.inner(self._B, X), 0, 3)
        rev_offset, rev_scale = np.vsplit(self._px_offscl_rev, 2)
        # needs to return x/y
        return  np.rint(np.rollaxis(result * rev_scale + rev_offset, 2)).squeeze().astype(_type)[::-1]

    def fwd(self, x, y, z=None):
        if isinstance(x, (Sequence, np.ndarray)):
            if z is None:
                z = [None]*len(x)
            return  np.transpose(np.asarray([self.fwd(x_i, y_i, z_i) for x_i, y_i, z_i in izip(x, y, z)]))
        coord = np.asarray([x, y])
        normed = np.sum(self._px_offscl * np.vstack([np.ones(coord.shape), coord]), axis=0)
        coord = np.dot(self._A_rev, normed)[[1,2,3]] # likely unstable
        return np.sum(self._offscl_rev * np.vstack([np.ones(coord.shape), coord]), axis=0)

    def __call__(self, coords):
        assert isinstance(coords, np.ndarray)
        try:
            d0, d1 = coords.shape
            assert d1 ==2
        except (ValueError, AssertionError):
            raise NotImplementedError("input coords must be [N x 2] dimension numpy array")
        if d1 != 2:
            raise NotImplementedError("input coords must be [N x 2] dimension numpy array")

        xarr, yarr = np.hsplit(coords, 2)
        res = self.fwd(xarr, yarr)
        return res

    def inverse(self, coords):
        pass

    def residuals(self, src, dst):
        pass

    def _rpc(self, x):
        L, P, H = np.dsplit(x, 3)
        return np.dstack([np.ones((x.shape[0], x.shape[1]), dtype=np.float32), L, P, H, L*P, L*H, P*H, L**2, P**2, H**2,
                           L*P*H, L**3, L*(P**2), L*(H**2), (L**2)*P, P**3, P*(H**2),
                           (L**2)*H, (P**2)*H, H**3])

    def __add__(self, other):
        if isinstance(other, Sequence) and len(other) == 2:
            shift = np.asarray(other)
            # shift is an x/y px_offset needs to be y/x
            return RatPolyTransform(self._A, self._B, self._offset, self._scale,
                                    self._px_offset - shift[::-1], self._px_scale,
                                    self.gsd, self.proj, self._default_z)
        else:
            raise NotImplemented

    def __sub__(self, other):
        try:
            return self.__add__(-other)
        except:
            return self.__add__([-e for e in other])

    @classmethod
    def from_rpcs(cls, rpcs):
        P = np.vstack([np.asarray(rpcs["lineNumCoefs"]),
                       np.asarray(rpcs["sampleNumCoefs"])])
        Q = np.vstack([np.asarray(rpcs["lineDenCoefs"]),
                       np.asarray(rpcs["sampleDenCoefs"])])

        scale = np.asarray([1.0/rpcs["lonScale"],
                            1.0/rpcs["latScale"],
                            1.0/rpcs["heightScale"]])
        offset = np.asarray([-rpcs["lonOffset"],
                             -rpcs["latOffset"],
                             -rpcs["heightOffset"]])*scale

        px_scale = np.asarray([rpcs["lineScale"], rpcs["sampleScale"]])
        px_offset = np.asarray([rpcs["lineOffset"], rpcs["sampleOffset"]])

        return cls(P, Q, offset, scale, px_offset, px_scale, rpcs["gsd"], rpcs["spatialReferenceSystem"],
                   rpcs["heightOffset"])

    @classmethod
    def from_affine(cls, affine):
        pass


class AffineTransform(GeometricTransform):
    def __init__(self, affine, proj=None):
        self._affine = affine
        self._iaffine = None
        self.proj = proj

    def rev(self, lng, lat, z=0, _type=np.int32):
        if self._iaffine is None:
            self._iaffine = ~self._affine
        return np.rint(np.asarray(self._iaffine * (lng, lat))).astype(_type)

    def fwd(self, x, y, z=0):
        return self._affine * (x, y)

    def __call__(self, coords):
        assert isinstance(coords, np.ndarray) and len(coords.shape) == 2 and coords.shape[1] == 2
        _coords = np.copy(coords)
        self._affine.itransform(_coords)
        return _coords

    def inverse(self, coords):
        assert isinstance(coords, np.ndarray) and len(coords.shape) == 2 and coords.shape[1] == 2
        if self._iaffine is None:
            self._iaffine = ~self._affine
        _coords = np.copy(coords)
        self._iaffine.itransform(_coords)
        return _coords

    def residuals(self, src, dst):
        return super(AffineTransform, self).residuals(src, dst)

    def __add__(self, other):
        if isinstance(other, Sequence) and len(other) == 2:
            shift = np.asarray(other)
            return AffineTransform(self._affine * Affine.translation(shift[0], shift[1]), proj=self.proj)
        else:
            raise NotImplemented

    def __sub__(self, other):
        try:
            return self.__add__(-other)
        except:
            return self.__add__([-e for e in other])

    @classmethod
    def from_georef(cls, georef):
        tfm = Affine.from_gdal(georef["translateX"], georef["scaleX"], georef["shearX"],
                               georef["translateY"], georef["shearY"], georef["scaleY"])
        return cls(tfm, proj=georef["spatialReferenceSystemCode"])

def pad_safe_negative(padsize=2, transpix=None, ref_im=None, ind=0):
    trans = transpix[ind,:,:].min() - padsize
    if trans < 0.0:
        trans = transpix[ind,:,:].min()
    return int(math.floor(trans))

def pad_safe_positive(padsize=2, transpix=None, ref_im=None, ind=0):
    trans = transpix[ind,:,:].max() + padsize
    if len(ref_im.shape) == 3:
        critical = ref_im.shape[ind + 1]
    elif len(ref_im.shape) == 2:
        critical = ref_im.shape[ind]
    else:
        raise NotImplementedError("Padding supported only for reference images of shape (L, W) or (Nbands, L, W)")
    if trans > critical:
        return critical
    return int(math.ceil(trans))
