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

from functools import partial



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

    def orthorectify(self, padsize=(2,2), **kwargs):
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
        xpad, ypad =  padsize

        psn = partial(_pad_safe_negative, transpix=transpix, ref_im=im_full)
        psp = partial(_pad_safe_positive, transpix=transpix, ref_im=im_full)
        ymint, xmint = (psn(padsize=ypad, ind=0), psn(padsize=xpad, ind=1))
        ymaxt, xmaxt = (psp(padsize=ypad, ind=0), psp(padsize=xpad, ind=1))

        shifted = np.stack([transpix[0,:,:] - ymint, transpix[1,:,:] - xmint])

        data = im_full[:,ymint:ymaxt,xmint:xmaxt].read()
        ortho = np.rollaxis(np.dstack([tf.warp(data[b,:,:].squeeze(), shifted, preserve_range=True) for b in xrange(data.shape[0])]), 2, 0)
        return GeoDaskWrapper(ortho, self) 

def _pad_safe_negative(padsize=2, transpix=None, ref_im=None, ind=0):
    trans = transpix[ind,:,:].min() - padsize
    if trans < 0.0:
        return 0
    return int(math.floor(trans))

def _pad_safe_positive(padsize=2, transpix=None, ref_im=None, ind=0):
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
