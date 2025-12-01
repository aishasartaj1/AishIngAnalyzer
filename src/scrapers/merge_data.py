"""
STEP 5: Merge data from all sources into single clean dataset
"""

import json
from typing import List, Dict
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataMerger:
    """Merge and clean data from multiple scraping sources"""
    
    def __init__(self):
        """STEP 5.1: Initialize merger"""
        self.logger = logger
        
    def load_json(self, filepath: Path) -> List[Dict]:
        """
        STEP 5.2: Load JSON data file
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            List of dictionaries
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"File not found: {filepath}")
            return []
        except json.JSONDecodeError as e:
            self.logger.error(f"Error decoding {filepath}: {e}")
            return []
            
    def normalize_name(self, name: str) -> str:
        """
        STEP 5.3: Normalize ingredient name for matching
        
        Args:
            name: Raw ingredient name
            
        Returns:
            Normalized name (lowercase, stripped)
        """
        return name.lower().strip()
        
    def merge_sources(
        self,
        incidecoder_data: List[Dict],
        cosmeticsinfo_data: List[Dict],
        ewg_data: List[Dict]
    ) -> List[Dict]:
        """
        STEP 5.4: Merge data from all three sources
        
        Args:
            incidecoder_data: Data from incidecoder.com
            cosmeticsinfo_data: Data from cosmeticsinfo.org
            ewg_data: Data from EWG Skin Deep
            
        Returns:
            List of merged ingredient dictionaries
        """
        self.logger.info("Merging data from all sources...")
        
        # STEP 5.5: Create lookup dictionaries by normalized name
        incidecoder_map = {
            self.normalize_name(item['name']): item 
            for item in incidecoder_data
        }
        
        cosmeticsinfo_map = {
            self.normalize_name(item['name']): item 
            for item in cosmeticsinfo_data
        }
        
        ewg_map = {
            self.normalize_name(item['name']): item 
            for item in ewg_data
        }
        
        # STEP 5.6: Get all unique ingredient names
        all_names = set(
            list(incidecoder_map.keys()) + 
            list(cosmeticsinfo_map.keys()) + 
            list(ewg_map.keys())
        )
        
        self.logger.info(f"Found {len(all_names)} unique ingredients")
        
        # STEP 5.7: Merge data for each ingredient
        merged = []
        
        for name in all_names:
            # STEP 5.8: Get data from each source
            incide_data = incidecoder_map.get(name, {})
            cosmet_data = cosmeticsinfo_map.get(name, {})
            ewg_data_item = ewg_map.get(name, {})
            
            # STEP 5.9: Combine into single record
            merged_item = {
                'name': (
                    incide_data.get('name') or 
                    cosmet_data.get('name') or 
                    ewg_data_item.get('name') or 
                    name.title()
                ),
                'purpose': (
                    incide_data.get('purpose') or 
                    cosmet_data.get('purpose') or 
                    ""
                ),
                'description': (
                    incide_data.get('description') or 
                    cosmet_data.get('description') or 
                    ""
                ),
                'safety_score': ewg_data_item.get('safety_score'),
                'concerns': self._merge_concerns(
                    incide_data.get('concerns', []),
                    ewg_data_item.get('concerns', [])
                ),
                'sources': self._get_sources(incide_data, cosmet_data, ewg_data_item)
            }
            
            # STEP 5.10: Include all ingredients (even if some fields are empty)
            # We at least have the ingredient name from the sources
            merged.append(merged_item)
                
        self.logger.info(f"Merged into {len(merged)} complete ingredient records")
        return merged
        
    def _merge_concerns(self, list1: List[str], list2: List[str]) -> List[str]:
        """
        STEP 5.11: Merge concern lists, remove duplicates
        
        Args:
            list1: First list of concerns
            list2: Second list of concerns
            
        Returns:
            Merged and deduplicated list
        """
        all_concerns = list1 + list2
        # Remove "none" if other concerns exist
        concerns = [c for c in all_concerns if c.lower() != "none"]
        
        if not concerns:
            return ["none"]
            
        return list(set(concerns))
        
    def _get_sources(self, *data_items) -> List[str]:
        """
        STEP 5.12: Get list of sources that contributed data
        
        Args:
            *data_items: Variable number of data dictionaries
            
        Returns:
            List of source names
        """
        sources = []
        for item in data_items:
            if item and item.get('source'):
                sources.append(item['source'])
        return sources
        
    def clean_and_validate(self, data: List[Dict]) -> List[Dict]:
        """
        STEP 5.13: Clean and validate merged data
        
        Args:
            data: List of merged ingredient dictionaries
            
        Returns:
            Cleaned and validated list
        """
        self.logger.info("Cleaning and validating data...")
        
        cleaned = []
        
        for item in data:
            # STEP 5.14: Skip if missing critical fields
            if not item.get('name'):
                continue
                
            # STEP 5.15: Ensure all fields exist
            cleaned_item = {
                'name': item['name'],
                'purpose': item.get('purpose', 'Unknown purpose'),
                'description': item.get('description', ''),
                'safety_score': item.get('safety_score'),  # Can be None
                'concerns': item.get('concerns', ['none']),
                'sources': item.get('sources', [])
            }
            
            cleaned.append(cleaned_item)
            
        self.logger.info(f"Cleaned dataset: {len(cleaned)} valid ingredients")
        return cleaned
        
    def save_merged_data(self, data: List[Dict], output_path: Path):
        """
        STEP 5.16: Save merged data to file
        
        Args:
            data: Merged ingredient data
            output_path: Path to save file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        self.logger.info(f"Saved {len(data)} ingredients to {output_path}")