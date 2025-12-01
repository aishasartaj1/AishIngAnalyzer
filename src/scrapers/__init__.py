"""
Web scrapers for ingredient data collection
"""

from .base_scraper import BaseScraper
from .incidecoder_scraper import IncidecoderScraper
from .cosmeticsinfo_scraper import CosmeticsinfoScraper
from .ewg_scraper import EWGScraper
from .merge_data import DataMerger

__all__ = [
    'BaseScraper',
    'IncidecoderScraper', 
    'CosmeticsinfoScraper',
    'EWGScraper',
    'DataMerger'
]