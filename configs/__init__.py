from .config import *

try:
    if PRODUCTION_MODE:
        from .prod_config import *
    else:
        from .dev_config import *
except Exception:
    from .test_config import *
from .logging_config import logger