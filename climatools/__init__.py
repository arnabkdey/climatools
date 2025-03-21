"""
climatools - A Python package for climate data processing

This package provides tools for downloading, extracting, and processing climate data.
"""

__version__ = '0.1.0'

# Import key functions to be used in the package
from .download.gee_global_daily_download import download_ee_to_drive