"""
STEP 6: Generate embeddings for ingredient descriptions
"""

import json
from typing import List, Dict
from pathlib import Path
import logging
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generate embeddings for ingredient text data"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        STEP 6.1: Initialize embedding model
        
        Args:
            model_name: Name of sentence-transformers model
        """
        self.logger = logger
        self.logger.info(f"Loading embedding model: {model_name}")
        
        # STEP 6.2: Load pre-trained model
        self.model = SentenceTransformer(model_name)
        self.logger.info("Model loaded successfully")
        
    def create_embedding_text(self, ingredient: Dict) -> str:
        """
        STEP 6.3: Create combined text for embedding
        
        Args:
            ingredient: Ingredient dictionary
            
        Returns:
            Combined text string
        """
        # STEP 6.4: Combine relevant fields for rich embeddings
        parts = [
            f"Ingredient: {ingredient['name']}",
            f"Purpose: {ingredient['purpose']}",
            f"Description: {ingredient['description']}"
        ]
        
        # STEP 6.5: Add concerns if they exist
        if ingredient.get('concerns') and ingredient['concerns'] != ['none']:
            concerns_text = ", ".join(ingredient['concerns'])
            parts.append(f"Concerns: {concerns_text}")
            
        return " | ".join(parts)
        
    def generate_embeddings(self, ingredients: List[Dict]) -> List[Dict]:
        """
        STEP 6.6: Generate embeddings for all ingredients
        
        Args:
            ingredients: List of ingredient dictionaries
            
        Returns:
            List of ingredients with embeddings added
        """
        self.logger.info(f"Generating embeddings for {len(ingredients)} ingredients...")
        
        results = []
        
        # STEP 6.7: Generate embeddings with progress bar
        for ingredient in tqdm(ingredients, desc="Creating embeddings"):
            # STEP 6.8: Create text to embed
            text = self.create_embedding_text(ingredient)
            
            # STEP 6.9: Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            
            # STEP 6.10: Add embedding to ingredient data
            ingredient_with_embedding = ingredient.copy()
            ingredient_with_embedding['embedding'] = embedding.tolist()
            ingredient_with_embedding['embedding_text'] = text
            
            results.append(ingredient_with_embedding)
            
        self.logger.info("Embeddings generated successfully")
        return results
        
    def save_embeddings(self, data: List[Dict], output_path: Path):
        """
        STEP 6.11: Save data with embeddings
        
        Args:
            data: Ingredients with embeddings
            output_path: Path to save file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
            
        self.logger.info(f"Saved embeddings to {output_path}")