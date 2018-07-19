import os
import math
try:
    from rio_hist.match import histogram_match
    has_rio = True
except ImportError:
    has_rio = False

import mercantile
from shapely.geometry import box, shape, mapping, asShape

import numpy as np
try:
    from matplotlib import pyplot as plt
    has_pyplot = True
except:
    has_pyplot = False


class PlotMixin(object):
    def base_layer_match(self, blm=False, blm_source=None, **kwargs):
        if blm and "stretch" not in kwargs:
            kwargs["stretch"] = [0,100]
        rgb = self.rgb(**kwargs)
        if not blm:
            return rgb
        bounds = self._reproject(box(*self.bounds), from_proj=self.proj, to_proj="EPSG:4326").bounds
        if blm_source == 'browse':
            from gbdxtools.images.browse_image import BrowseImage
            ref = BrowseImage(self.cat_id, bbox=bounds).read()
        else:
            from gbdxtools.images.tms_image import TmsImage
            tms = TmsImage(zoom=self._calc_tms_zoom(self.affine[0]), bbox=bounds, **kwargs)
            ref = np.rollaxis(tms.read(), 0, 3)
        out = np.dstack([histogram_match(rgb[:,:,idx], ref[:,:,idx].astype(np.double)/255.0)
                        for idx in range(rgb.shape[-1])])
        return out

    def rgb(self, **kwargs):
        if "bands" in kwargs:
            use_bands = kwargs["bands"]
            assert len(use_bands) == 3, 'Plot method only supports single or 3-band outputs'
            del kwargs["bands"]
        else:
            use_bands = self._rgb_bands
        data = self._read(self[use_bands,...], **kwargs)
        data = np.rollaxis(data.astype(np.float32), 0, 3)
        lims = np.percentile(data, kwargs.get("stretch", [2, 98]), axis=(0, 1))
        for x in range(len(data[0,0,:])):
            top = lims[:,x][1]
            bottom = lims[:,x][0]
            data[:,:,x] = (data[:,:,x] - bottom) / float(top - bottom)
        return np.clip(data, 0, 1)

    def ndvi(self, **kwargs):
        data = self._read(self[self._ndvi_bands,...]).astype(np.float32)
        return (data[0,:,:] - data[1,:,:]) / (data[0,:,:] + data[1,:,:])

    def plot(self, spec="rgb", **kwargs):
        if self.shape[0] == 1 or ("bands" in kwargs and len(kwargs["bands"]) == 1):
            if "cmap" in kwargs:
                cmap = kwargs["cmap"]
                del kwargs["cmap"]
            else:
                cmap = "Greys_r"
            self._plot(tfm=self._single_band, cmap=cmap, **kwargs)
        else:
            if spec == "rgb" and self._has_token(**kwargs):
                self._plot(tfm=self.base_layer_match, **kwargs)
            else:
                self._plot(tfm=getattr(self, spec), **kwargs)

    def _has_token(self, **kwargs):
        if "access_token" in kwargs or "MAPBOX_API_KEY" in os.environ:
            return True
        else:
            return False

    def _plot(self, tfm=lambda x: x, **kwargs):
        assert has_pyplot, "To plot images please install matplotlib"
        assert self.shape[1] and self.shape[-1], "No data to plot, dimensions are invalid {}".format(str(self.shape))

        f, ax1 = plt.subplots(1, figsize=(kwargs.get("w", 10), kwargs.get("h", 10)))
        ax1.axis('off')
        ax1.set_title(kwargs.get('title', ''), fontsize=kwargs.get('fontsize', 22))
        plt.imshow(tfm(**kwargs), interpolation='nearest', cmap=kwargs.get("cmap", None))
        plt.show(block=False)

    def _read(self, data, **kwargs):
        if hasattr(data, 'read'):
            return data.read(**kwargs)
        else:
            return data.compute(get=threaded_get)

    def _single_band(self, **kwargs):
        arr = self._read(self, **kwargs)
        return arr[0,:,:]

    def _calc_tms_zoom(self, scale):
        for z in range(15,20):
            b = mercantile.bounds(0,0,z)
            if scale > math.sqrt((b.north - b.south)*(b.east - b.west) / (256*256)):
                return z


class BandMethodsTemplate(object):
    @property
    def _rgb_bands(self):
        raise NotImplementedError("RGB bands undefined for image type {}".format(self.__class__.__name__))

    @property
    def _ndvi_bands(self):
        raise NotImplementedError("NDVI bands undefined for image type {}".format(self.__class__.__name__))

    @property
    def _ndwi_bands(self):
        raise NotImplementedError("NDWI bands undefined for image type {}".format(self.__class__.__name__))
