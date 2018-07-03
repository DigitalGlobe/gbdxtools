from __future__ import print_function

from gbdxtools.images.rda_image import RDAImage


class RDABaseImage(RDAImage):
    __rda_id__ = None
    def __new__(cls, rda_id=None, **kwargs):
        cls = cls.__Driver__(rda_id=rda_id, **kwargs).drive(cls)
        self = super(RDABaseImage, cls).__new__(cls, cls.__driver__.payload, **kwargs)
        return self.__post_new_hook__(**kwargs)

    def __post_new_hook__(self, **kwargs):
        return self.aoi(**kwargs)

    @property
    def options(self):
        return self.__driver__.options

    @property
    def _graph(self):
        return self.__driver__.graph
