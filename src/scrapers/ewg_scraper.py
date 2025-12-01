"""
STEP 4: Scraper for EWG Skin Deep safety scores
"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper


class EWGScraper(BaseScraper):
    """Scraper for EWG Skin Deep database (safety scores)"""
    
    def __init__(self):
        """STEP 4.1: Initialize with EWG base URL"""
        super().__init__(
            base_url="https://www.ewg.org",
            rate_limit_seconds=2.0
        )
        self.search_url = f"{self.base_url}/skindeep/search"
        
    def search_ingredient(self, ingredient_name: str) -> Optional[str]:
        """
        STEP 4.2: Search for ingredient and get detail page URL

        Args:
            ingredient_name: Name of ingredient to search

        Returns:
            URL of ingredient detail page or None
        """
        try:
            # STEP 4.3: Perform search using EWG's search URL
            search_params = {'search': ingredient_name}
            response = self.session.get(
                self.search_url,
                params=search_params,
                timeout=10
            )
            response.raise_for_status()

            # STEP 4.4: Parse search results
            soup = BeautifulSoup(response.content, 'lxml')

            # STEP 4.5: Find ingredient links from search results
            # EWG shows ingredient cards with links to /skindeep/ingredients/
            ingredient_links = soup.select('a[href*="/skindeep/ingredients/"]')

            if ingredient_links:
                href = ingredient_links[0].get('href')
                full_url = f"{self.base_url}{href}" if href.startswith('/') else href
                self.logger.info(f"Found EWG URL for {ingredient_name}: {full_url}")
                return full_url

            self.logger.warning(f"No EWG results found for: {ingredient_name}")
            return None

        except Exception as e:
            self.logger.error(f"Error searching for {ingredient_name}: {e}")
            return None
            
    def parse_ingredient_page(self, url: str) -> Dict:
        """
        STEP 4.6: Parse EWG ingredient page for safety score

        Args:
            url: URL of ingredient page

        Returns:
            Dictionary with safety data
        """
        soup = self.fetch_page(url)
        if not soup:
            return {}

        # STEP 4.7: Extract ingredient name from h1 or title
        name_elem = soup.select_one('h1')
        name = name_elem.text.strip() if name_elem else "Unknown"

        # STEP 4.8: Extract safety score (1-10)
        # The score appears in a large colored circle/badge
        # Try multiple selectors to find the score
        safety_score = None

        # Look for the score in various possible locations
        score_selectors = [
            'div[class*="score"] h2',  # Score in heading
            'div[class*="rating"] h2',
            'span[class*="score"]',
            'div[class*="hazard"] h2',
        ]

        for selector in score_selectors:
            score_elem = soup.select_one(selector)
            if score_elem:
                score_text = score_elem.text.strip()
                try:
                    # Extract first digit found
                    safety_score = int(''.join(filter(str.isdigit, score_text))[:1])
                    if 1 <= safety_score <= 10:
                        break
                except (ValueError, IndexError):
                    continue

        # STEP 4.9: Extract description and concerns
        description_elem = soup.select_one('p')
        description = description_elem.text.strip() if description_elem else ""

        concerns = []
        concern_elems = soup.select('div[class*="concern"] li, div[class*="hazard"] li')
        for elem in concern_elems:
            concern_text = elem.text.strip()
            if concern_text and len(concern_text) > 2:
                concerns.append(concern_text)

        # STEP 4.10: Return structured data
        return {
            'name': name,
            'safety_score': safety_score,
            'description': description[:200] if description else "",  # First 200 chars
            'concerns': concerns if concerns else ["none"],
            'source': 'ewg',
            'url': url
        }
        
    def scrape_for_ingredients(self, ingredient_names: List[str]) -> List[Dict]:
        """
        STEP 4.11: Search and scrape EWG data for list of ingredients
        
        Args:
            ingredient_names: List of ingredient names to look up
            
        Returns:
            List of ingredient dictionaries with safety scores
        """
        self.logger.info(f"Starting EWG scrape for {len(ingredient_names)} ingredients...")
        
        results = []
        
        # STEP 4.12: Search and scrape each ingredient
        for i, name in enumerate(ingredient_names, 1):
            self.logger.info(f"Searching EWG {i}/{len(ingredient_names)}: {name}")
            
            try:
                # STEP 4.13: Search for ingredient
                detail_url = self.search_ingredient(name)
                
                if detail_url:
                    # STEP 4.14: Parse detail page
                    ingredient_data = self.parse_ingredient_page(detail_url)
                    if ingredient_data:
                        results.append(ingredient_data)
                else:
                    self.logger.warning(f"No EWG data found for: {name}")
                    
            except Exception as e:
                self.logger.error(f"Error processing {name}: {e}")
                continue
                
        self.logger.info(f"Successfully scraped {len(results)} ingredients from EWG")
        return results