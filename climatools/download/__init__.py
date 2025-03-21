"""
Download subpackage for retrieving climate data from various sources.
"""

import ee
import time
from datetime import datetime, timedelta

# Import and expose functions
from .gee_global_daily_download import download_ee_to_drive