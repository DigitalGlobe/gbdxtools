import os
import math
try:
    from rio_hist.match import histogram_match as rio_match
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

    def rgb(self, **kwargs):
        if "bands" in kwargs:
            use_bands = kwargs["bands"]
            assert len(use_bands) == 3, 'Plot method only supports single or 3-band outputs'
            del kwargs["bands"]
        else:
            use_bands = self._rgb_bands
        if kwargs.get('blm') == True:
            return self.histogram_match(use_bands, **kwargs)
        if "histogram" not in kwargs:
            if "stretch" not in kwargs:
                kwargs['stretch'] = [2,98]
            return self.histogram_stretch(use_bands, **kwargs)
        elif kwargs["histogram"] == "equalize":
            return self.histogram_equalize(use_bands, **kwargs)
        elif kwargs["histogram"] == "match":
            return self.histogram_match(use_bands, **kwargs)
        elif kwargs["histogram"] == "minmax":
            return self.histogram_stretch(use_bands, stretch=[0, 100], **kwargs)
        else:
            raise KeyError('Unknown histogram parameter, use "equalize", "match", or "minmax"')

    def histogram_equalize(self, use_bands, **kwargs):
        ''' Equalize and the histogram and normalize value range
            Equalization is on all three bands, not per-band'''
        data = self._read(self[use_bands,...], **kwargs)
        data = np.rollaxis(data.astype(np.float32), 0, 3)
        flattened = data.flatten()
        if 0 in data:
            masked = np.ma.masked_values(data, 0).compressed()
            image_histogram, bin_edges = np.histogram(masked, 256)
        else:
            image_histogram, bin_edges = np.histogram(flattened, 256)
        bins = (bin_edges[:-1] + bin_edges[1:]) / 2.0
        cdf = image_histogram.cumsum() 
        cdf = cdf / float(cdf[-1])
        image_equalized = np.interp(flattened, bins, cdf).reshape(data.shape)
        if 'stretch' in kwargs or 'gamma' in kwargs:
            return self._histogram_stretch(image_equalized, **kwargs)
        else:
            return image_equalized

    def histogram_match(self, use_bands, blm_source=None, **kwargs):
        ''' Match the histogram to existing imagery '''
        assert has_rio, "To match image histograms please install rio_hist"
        data = self._read(self[use_bands,...], **kwargs)
        data = np.rollaxis(data.astype(np.float32), 0, 3)
        if 0 in data:
            data = np.ma.masked_values(data, 0)
        bounds = self._reproject(box(*self.bounds), from_proj=self.proj, to_proj="EPSG:4326").bounds
        if blm_source == 'browse':
            from gbdxtools.images.browse_image import BrowseImage
            ref = BrowseImage(self.cat_id, bbox=bounds).read()
        else:
            from gbdxtools.images.tms_image import TmsImage
            tms = TmsImage(zoom=self._calc_tms_zoom(self.affine[0]), bbox=bounds, **kwargs)
            ref = np.rollaxis(tms.read(), 0, 3)
        out = np.dstack([rio_match(data[:,:,idx], ref[:,:,idx].astype(np.double)/255.0)
                        for idx in range(data.shape[-1])])
        if 'stretch' in kwargs or 'gamma' in kwargs:
            return self._histogram_stretch(out, **kwargs)
        else:
            return out

    def histogram_stretch(self, use_bands, **kwargs):
        ''' entry point for contrast stretching '''
        data = self._read(self[use_bands,...], **kwargs)
        data = np.rollaxis(data.astype(np.float32), 0, 3)
        return self._histogram_stretch(data, **kwargs)

    def _histogram_stretch(self, data, **kwargs):
        ''' perform a contrast stretch and/or gamma adjustment '''
        for x in range(len(data[0,0,:])):
            band = data[:,:,x]
            if 0 in band:
                band = np.ma.masked_values(band, 0).compressed()
            lims = np.percentile(band, kwargs.get("stretch", [0,100]))
            top = lims[1]
            bottom = lims[0]
            data[:,:,x] = (data[:,:,x] - bottom) / float(top - bottom) * 255.0
        data = np.clip(data, 0, 255).astype("uint8")
        if "gamma" in kwargs:
            invGamma = 1.0 / kwargs['gamma']
            lut = np.array([((i / 255.0) ** invGamma) * 255
		            for i in np.arange(0, 256)]).astype("uint8")
            data = np.take(lut, data)
        return data

    def ndvi(self, **kwargs):
        """
        Calculates Normalized Difference Vegetation Index using NIR and Red of an image.

        Returns: numpy array with ndvi values
        """
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
                self._plot(tfm=self.rgb, **kwargs)
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
