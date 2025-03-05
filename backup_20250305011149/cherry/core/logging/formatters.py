import json
import logging
import datetime
import traceback
from typing import Dict, Any, Optional


class ColoredFormatter(logging.Formatter):
    """
    A formatter that adds color to the log output based on log level.
    