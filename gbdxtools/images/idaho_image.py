from __future__ import print_function
import requests
from gbdxtools.images.meta import GeoDaskWrapper
from gbdxtools.images.ipe_image import IpeImage
from gbdxtools.ipe.util import calc_toa_gain_offset, ortho_params
from gbdxtools.ipe.interface import Ipe
ipe = Ipe()

import skimage.transform as tf
import numpy as np
import math



class IdahoImage(IpeImage):
    """
      Dask based access to IDAHO images via IPE.
    """
    def __new__(cls, idaho_id, **kwargs):
        options = {
            "proj": kwargs.get("proj", "EPSG:4326"),
            "product": kwargs.get("product", "toa_reflectance")
        }

        standard_products = cls._build_standard_products(idaho_id, options["proj"])
        try:
            self = super(IdahoImage, cls).__new__(cls, standard_products.get(options["product"], "toa_reflectance"))
        except KeyError as e:
            print(e)
            print("Specified product not implemented: {}".format(options["product"]))
            raise
        self = self.aoi(**kwargs)
        self.idaho_id = idaho_id
        self._products = standard_products
        return self

    def get_product(self, product):
        return self.__class__(self.idaho_id, proj=self.proj, product=product)

    @staticmethod
    def _build_standard_products(idaho_id, proj):
        dn_op = ipe.IdahoRead(bucketName="idaho-images", imageId=idaho_id, objectStore="S3")
        ortho_op = ipe.Orthorectify(dn_op, **ortho_params(proj))

        # TODO: Switch to direct metadata access (ie remove this block)
        idaho_md = requests.get('http://idaho.timbr.io/{}.json'.format(idaho_id)).json()
        meta = idaho_md["properties"]
        gains_offsets = calc_toa_gain_offset(meta)
        radiance_scales, reflectance_scales, radiance_offsets = zip(*gains_offsets)
        # ---

        toa_reflectance_op = ipe.MultiplyConst(
            ipe.AddConst(
                ipe.MultiplyConst(
                    ipe.Format(ortho_op, dataType="4"),
                    constants=radiance_scales),
                constants=radiance_offsets),
            constants=reflectance_scales)

        return {
            "1b": dn_op,
            "ortho": ortho_op,
            "toa_reflectance": toa_reflectance_op
        }

    def orthorectify(self, **kwargs):
        if 'proj' in kwargs:
            to_proj = kwargs['proj']
            xmin, ymin, xmax, ymax = self._reproject(shape(self), from_proj=self.proj, to_proj=to_proj).bounds
        else:
            xmin, ymin, xmax, ymax = self.bounds
        gsd = max((xmax-xmin)/self.shape[2], (ymax-ymin)/self.shape[1])
        x = np.linspace(xmin, xmax, num=int((xmax-xmin)/gsd))
        y = np.linspace(ymax, ymin, num=int((ymax-ymin)/gsd))
        xv, yv = np.meshgrid(x, y, indexing='xy')
        z = kwargs.get('z', 0)
        if isinstance(z, np.ndarray):
            # TODO: potentially reproject
            z = tf.resize(z[0,:,:], xv.shape)
        im_full = IdahoImage(self.ipe.metadata['image']['imageId'], product='1b')
        transpix = im_full.__geo_transform__.rev(xv, yv, z=z, _type=np.float32)[::-1]

        ymint = math.floor(transpix[0,:,:].min() - 10.0)
        xmint = math.floor(transpix[1,:,:].min() - 10.0)
        ymaxt = math.ceil(transpix[0,:,:].max())
        xmaxt = math.ceil(transpix[1,:,:].max())
        shifted = np.stack([transpix[0,:,:] - int(ymint), transpix[1,:,:] - int(xmint)])

        data = im_full[:,ymint:ymaxt,xmint:xmaxt].read()
        ortho = np.rollaxis(np.dstack([tf.warp(data[b,:,:].squeeze(), shifted, preserve_range=True) for b in xrange(data.shape[0])]), 2, 0)
        return GeoDaskWrapper(ortho, self)


