import sys
import gbdxtools.rda
from gbdxtools.rda.util import deprecation

deprecation("The module 'gbdxtools.ipe' has been deprecated, functionality has been moved to gbdxtools.rda")

sys.modules[__name__] = sys.modules['gbdxtools.rda']
