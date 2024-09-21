from .config import *
try:
    from .mainconfig import *
except Exception:
    from .testconfig import *
from .logging_config import logger