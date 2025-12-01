"""
STEP 8: Main script to run entire Day 1 workflow
"""

import sys
from pathlib import Path
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scrapers import (
    IncidecoderScraper,
    CosmeticsinfoScraper,
    EWGScraper,
    DataMerger
)
from src.embeddings import EmbeddingGenerator, QdrantUploader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """STEP 8.1: Execute complete Day 1 pipeline"""
    
    # Define paths
    base_dir = Path(__file__).parent.parent
    raw_dir = base_dir / 'data' / 'raw'
    processed_dir = base_dir / 'data' / 'processed'
    errors_dir = base_dir / 'data' / 'errors'
    
    logger.info("="*50)
    logger.info("DAY 1: DATA ACQUISITION & VECTOR DB SETUP")
    logger.info("="*50)
    
    # ===== STEP 1: Scrape Incidecoder =====
    logger.info("\n[1/8] Scraping incidecoder.com...")
    incide_scraper = IncidecoderScraper()
    incide_data = incide_scraper.scrape(max_ingredients=500)
    incide_scraper.save_data(incide_data, raw_dir / 'incidecoder_raw.json')
    incide_scraper.save_errors(errors_dir / 'incidecoder_errors.json')
    
    # ===== STEP 2: Scrape Cosmeticsinfo =====
    logger.info("\n[2/8] Scraping cosmeticsinfo.org...")
    cosmet_scraper = CosmeticsinfoScraper()
    cosmet_data = cosmet_scraper.scrape(max_ingredients=500)
    cosmet_scraper.save_data(cosmet_data, raw_dir / 'cosmeticsinfo_raw.json')
    cosmet_scraper.save_errors(errors_dir / 'cosmeticsinfo_errors.json')
    
    # ===== STEP 3: Scrape EWG for safety scores =====
    logger.info("\n[3/8] Scraping EWG Skin Deep...")
    # Get unique ingredient names from both sources
    all_names = list(set(
        [item['name'] for item in incide_data] +
        [item['name'] for item in cosmet_data]
    ))[:300]  # Limit to 300 for EWG (slower site)
    
    ewg_scraper = EWGScraper()
    ewg_data = ewg_scraper.scrape_for_ingredients(all_names)
    ewg_scraper.save_data(ewg_data, raw_dir / 'ewg_raw.json')
    ewg_scraper.save_errors(errors_dir / 'ewg_errors.json')
    
    # ===== STEP 4: Merge all data =====
    logger.info("\n[4/8] Merging data from all sources...")
    merger = DataMerger()
    merged_data = merger.merge_sources(incide_data, cosmet_data, ewg_data)
    
    # ===== STEP 5: Clean and validate =====
    logger.info("\n[5/8] Cleaning and validating data...")
    clean_data = merger.clean_and_validate(merged_data)
    merger.save_merged_data(clean_data, processed_dir / 'ingredients_final.json')
    
    # ===== STEP 6: Generate embeddings =====
    logger.info("\n[6/8] Generating embeddings...")
    embedder = EmbeddingGenerator()
    data_with_embeddings = embedder.generate_embeddings(clean_data)
    embedder.save_embeddings(
        data_with_embeddings,
        processed_dir / 'ingredients_with_embeddings.json'
    )
    
    # ===== STEP 7: Upload to Qdrant =====
    logger.info("\n[7/8] Uploading to Qdrant Cloud...")
    uploader = QdrantUploader()
    uploader.create_collection(vector_size=384)
    uploader.upload_embeddings(data_with_embeddings)
    
    # ===== STEP 8: Test search =====
    logger.info("\n[8/8] Testing vector search...")
    uploader.test_search("niacinamide for skin brightening", top_k=3)
    
    # ===== SUMMARY =====
    logger.info("\n" + "="*50)
    logger.info("DAY 1 COMPLETE!")
    logger.info("="*50)
    logger.info(f"Total ingredients collected: {len(clean_data)}")
    logger.info(f"Data saved to: {processed_dir / 'ingredients_final.json'}")
    logger.info(f"Qdrant collection: cosmetic_ingredients")
    logger.info("\nNext: Day 2 - Build multi-agent system with LangGraph")


if __name__ == "__main__":
    main()