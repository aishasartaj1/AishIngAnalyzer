"""
STEP 1: Base scraper with retry logic, rate limiting, and error handling
"""

import time
import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseScraper:
    """Base class for all scrapers with common functionality"""
    
    def __init__(self, base_url: str, rate_limit_seconds: float = 2.0):
        """
        STEP 1.1: Initialize scraper with base configuration
        
        Args:
            base_url: Base URL for the website to scrape
            rate_limit_seconds: Delay between requests to avoid rate limiting
        """
        self.base_url = base_url
        self.rate_limit = rate_limit_seconds
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.logger = logging.getLogger(self.__class__.__name__)
        self.errors = []
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """
        STEP 1.2: Fetch page with retry logic
        
        Args:
            url: URL to fetch
            
        Returns:
            BeautifulSoup object or None if failed
        """
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # STEP 1.3: Rate limiting to be respectful
            time.sleep(self.rate_limit)
            
            return BeautifulSoup(response.content, 'lxml')
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            self.errors.append({
                'url': url,
                'error': str(e),
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            raise
            
    def save_data(self, data: List[Dict], filepath: Path):
        """
        STEP 1.4: Save scraped data to JSON file
        
        Args:
            data: List of ingredient dictionaries
            filepath: Path to save file
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Saved {len(data)} items to {filepath}")
        
    def save_errors(self, filepath: Path):
        """
        STEP 1.5: Save error log
        
        Args:
            filepath: Path to error log file
        """
        if self.errors:
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.errors, f, indent=2, ensure_ascii=False)
                
            self.logger.warning(f"Saved {len(self.errors)} errors to {filepath}")
            
    def scrape(self) -> List[Dict]:
        """
        STEP 1.6: Main scraping method (to be overridden by child classes)
        
        Returns:
            List of ingredient dictionaries
        """
        raise NotImplementedError("Child class must implement scrape()")