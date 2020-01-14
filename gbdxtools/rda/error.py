class BadRequest(Exception):
    pass


class NotAcceptable(Exception):
    pass


class NotFound(Exception):
    pass


class Unauthorized(Exception):
    pass


class Forbidden(Exception):
    pass


class MaxTries(Exception):
    pass

class UnsupportedImageType(Exception):
    pass

class MissingMetadata(Exception):
    pass

class ImageNotAvailable(MissingMetadata):
    pass

class MissingIdahoImages(Exception):
    pass

class AcompUnavailable(Exception):
    pass

class PendingDeprecation(PendingDeprecationWarning):
    pass

class IncompatibleOptions(Exception):
    pass
