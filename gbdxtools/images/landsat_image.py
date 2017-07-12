from __future__ import print_function
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

import numpy as np

class LandsatImage(IpeImage):
    """
      Dask based access to landsat image backed by IPE Graphs.
    """
    def __new__(cls, _id, **kwargs):
        options = {
            "product": kwargs.get("product", "landsat"),
            "spec": kwargs.get("spec", "multispectral")
        }

        standard_products = cls._build_standard_products(_id, options["spec"])
        try:
            self = super(LandsatImage, cls).__new__(cls, standard_products[options["product"]])
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self._id = _id
        self._spec = options["spec"]
        self._products = standard_products
        return self.aoi(**kwargs)

    def rgb(self, **kwargs):
        data = self[[3,2,1],...].read()
        data = np.rollaxis(data.astype(np.float32), 0, 3)
        lims = np.percentile(data, kwargs.get("stretch", [2,98]), axis=(0,1))
        for x in xrange(len(data[0,0,:])):
            top = lims[:,x][1]
            bottom = lims[:,x][0]
            data[:,:,x] = (data[:,:,x]-bottom)/float(top-bottom)
        return np.clip(data,0,1)

    def ndvi(self, **kwargs):
        data = self[[4,3],...].read().astype(np.float32)
        return (data[0,:,:] - data[1,:,:]) / (data[0,:,:] + data[1,:,:])

    def plot(self, spec="rgb", **kwargs): 
        if self.shape[0] == 1:
            super(LandsatImage, self).plot(w=w, h=h, cmap="Greys_r", tfm=lambda x: x[0,:,:])
        else:
            super(LandsatImage, self).plot(tfm=getattr(self, spec), **kwargs)

    def get_product(self, product):
        return self.__class__(self._id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(_id, spec):
        landsat = ipe.LandsatRead(landsatId=_id, productSpec=spec)
        return {
            "landsat": landsat
        }
