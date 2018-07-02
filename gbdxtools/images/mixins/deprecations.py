from gbdxtools.rda.util import deprecation


class Deprecations(object):
    @property
    def ipe_id(self):
        deprecation('The use of ipe_id has been deprecated, please use rda_id.')
        return self.rda_id

    @property
    def ipe_metadata(self):
        deprecation('The use of ipe_metadata has been deprecated, please use rda_metadata.')
        return self.rda_metadata
