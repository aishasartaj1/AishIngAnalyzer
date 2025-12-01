"""
STEP 2: Scraper for incidecoder.com/ingredients
"""

from typing import List, Dict
from pathlib import Path
from .base_scraper import BaseScraper


class IncidecoderScraper(BaseScraper):
    """Scraper for incidecoder.com ingredient database"""
    
    def __init__(self):
        """STEP 2.1: Initialize with incidecoder base URL"""
        super().__init__(
            base_url="https://incidecoder.com",
            rate_limit_seconds=2.0
        )
        self.ingredients_url = f"{self.base_url}/ingredients"
        
    def get_ingredient_links(self, max_pages: int = 20) -> List[str]:
        """
        STEP 2.2: Get list of ingredient page URLs with pagination

        Args:
            max_pages: Maximum number of pages to scrape

        Returns:
            List of ingredient URLs
        """
        links = []

        # STEP 2.3: Scrape multiple pages for more ingredients
        for page_num in range(1, max_pages + 1):
            # Try different URL patterns for pagination
            page_urls = [
                f"{self.ingredients_url}?page={page_num}",
                f"{self.ingredients_url}/page/{page_num}",
                self.ingredients_url if page_num == 1 else None
            ]

            for page_url in page_urls:
                if not page_url:
                    continue

                soup = self.fetch_page(page_url)
                if not soup:
                    continue

                # STEP 2.4: Find all ingredient links
                ingredient_elements = soup.select('a[href*="/ingredients/"]')

                page_links = []
                for elem in ingredient_elements:
                    href = elem.get('href')
                    if href and '/ingredients/' in href and not href.endswith('/ingredients'):
                        full_url = f"{self.base_url}{href}" if href.startswith('/') else href
                        page_links.append(full_url)

                if page_links:
                    links.extend(page_links)
                    self.logger.info(f"Found {len(page_links)} links on page {page_num}")
                    break  # Found working pagination format

            # Stop if no new links found (reached end of pages)
            if page_num > 1 and len(set(links)) == len(set(links[:-len(page_links)]) if page_links else links):
                self.logger.info(f"No new links found. Stopping at page {page_num}")
                break

        unique_links = list(set(links))
        self.logger.info(f"Found {len(unique_links)} total unique ingredient links")
        return unique_links
        
    def parse_ingredient_page(self, url: str) -> Dict:
        """
        STEP 2.5: Parse individual ingredient page
        
        Args:
            url: URL of ingredient page
            
        Returns:
            Dictionary with ingredient data
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}
            
        # STEP 2.6: Extract ingredient name
        name_elem = soup.select_one('h1')
        name = name_elem.text.strip() if name_elem else "Unknown"
        
        # STEP 2.7: Extract purpose/function
        # NOTE: Selectors need adjustment based on actual HTML structure
        purpose_elem = soup.select_one('.function, .what-it-does')
        purpose = purpose_elem.text.strip() if purpose_elem else ""
        
        # STEP 2.8: Extract description
        desc_elem = soup.select_one('.description, .ingredient-description')
        description = desc_elem.text.strip() if desc_elem else ""
        
        # STEP 2.9: Extract concerns/warnings
        concerns = []
        concern_elems = soup.select('.concern, .warning')
        for elem in concern_elems:
            concerns.append(elem.text.strip())
            
        # STEP 2.10: Return structured data
        return {
            'name': name,
            'purpose': purpose,
            'description': description,
            'concerns': concerns if concerns else ["none"],
            'source': 'incidecoder',
            'url': url
        }
        
    def scrape(self, max_ingredients: int = 500) -> List[Dict]:
        """
        STEP 2.11: Main scraping workflow
        
        Args:
            max_ingredients: Maximum number of ingredients to scrape
            
        Returns:
            List of ingredient dictionaries
        """
        self.logger.info("Starting incidecoder scrape...")
        
        # STEP 2.12: Get ingredient links
        links = self.get_ingredient_links()
        links = links[:max_ingredients]
        
        # STEP 2.13: Scrape each ingredient page
        ingredients = []
        for i, link in enumerate(links, 1):
            self.logger.info(f"Scraping {i}/{len(links)}: {link}")
            
            try:
                ingredient = self.parse_ingredient_page(link)
                if ingredient and ingredient.get('name') != "Unknown":
                    ingredients.append(ingredient)
            except Exception as e:
                self.logger.error(f"Error parsing {link}: {e}")
                continue
                
        self.logger.info(f"Successfully scraped {len(ingredients)} ingredients from incidecoder")
        return ingredients