"""
Review II Scraper Package

A robust web scraper adapted from e-commerce scraping logic
for Review II requirements.
"""

__version__ = "1.0.0"
__author__ = "Review II Team"

from .scraper_main import ReviewScraper
from .config import Config

__all__ = ['ReviewScraper', 'Config']