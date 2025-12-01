"""
STEP 3: Scraper for cosmeticsinfo.org/ingredients-list
"""

from typing import List, Dict
from .base_scraper import BaseScraper


class CosmeticsinfoScraper(BaseScraper):
    """Scraper for cosmeticsinfo.org ingredient database"""
    
    def __init__(self):
        """STEP 3.1: Initialize with cosmeticsinfo base URL"""
        super().__init__(
            base_url="https://www.cosmeticsinfo.org",
            rate_limit_seconds=2.0
        )
        self.ingredients_url = f"{self.base_url}/ingredients-list"
        
    def get_ingredient_links(self, max_pages: int = 30) -> List[str]:
        """
        STEP 3.2: Get list of ingredient page URLs with pagination

        Args:
            max_pages: Maximum number of pages to scrape

        Returns:
            List of ingredient URLs
        """
        links = []

        # STEP 3.3: Scrape multiple pages
        for page_num in range(1, max_pages + 1):
            # Try different URL patterns
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

                # STEP 3.4: Find all ingredient links
                ingredient_elements = soup.select('a[href*="/ingredient/"]')

                page_links = []
                for elem in ingredient_elements:
                    href = elem.get('href')
                    if href and '/ingredient/' in href:
                        full_url = f"{self.base_url}{href}" if href.startswith('/') else href
                        page_links.append(full_url)

                if page_links:
                    links.extend(page_links)
                    self.logger.info(f"Found {len(page_links)} links on page {page_num}")
                    break

            # Stop if no new links
            if page_num > 1 and len(set(links)) == len(set(links[:-len(page_links)]) if page_links else links):
                self.logger.info(f"No new links found. Stopping at page {page_num}")
                break

        unique_links = list(set(links))
        self.logger.info(f"Found {len(unique_links)} total unique ingredient links from cosmeticsinfo")
        return unique_links
        
    def parse_ingredient_page(self, url: str) -> Dict:
        """
        STEP 3.5: Parse individual ingredient page
        
        Args:
            url: URL of ingredient page
            
        Returns:
            Dictionary with ingredient data
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}
            
        # STEP 3.6: Extract ingredient name
        name_elem = soup.select_one('h1, .ingredient-name')
        name = name_elem.text.strip() if name_elem else "Unknown"
        
        # STEP 3.7: Extract function/purpose
        function_elem = soup.select_one('.function, .ingredient-function')
        purpose = function_elem.text.strip() if function_elem else ""
        
        # STEP 3.8: Extract full description
        desc_elem = soup.select_one('.description, .ingredient-info')
        description = desc_elem.text.strip() if desc_elem else ""
        
        # STEP 3.9: Extract safety info
        safety_elem = soup.select_one('.safety, .safety-info')
        safety_info = safety_elem.text.strip() if safety_elem else ""
        
        # STEP 3.10: Return structured data
        return {
            'name': name,
            'purpose': purpose,
            'description': description,
            'safety_info': safety_info,
            'source': 'cosmeticsinfo',
            'url': url
        }
        
    def scrape(self, max_ingredients: int = 500) -> List[Dict]:
        """
        STEP 3.11: Main scraping workflow
        
        Args:
            max_ingredients: Maximum number of ingredients to scrape
            
        Returns:
            List of ingredient dictionaries
        """
        self.logger.info("Starting cosmeticsinfo scrape...")
        
        # STEP 3.12: Get ingredient links
        links = self.get_ingredient_links()
        links = links[:max_ingredients]
        
        # STEP 3.13: Scrape each ingredient page
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
                
        self.logger.info(f"Successfully scraped {len(ingredients)} ingredients from cosmeticsinfo")
        return ingredients