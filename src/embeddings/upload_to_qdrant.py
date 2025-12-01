"""
STEP 7: Upload embeddings to Qdrant vector database
"""

import json
import os
from typing import List, Dict
from pathlib import Path
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantUploader:
    """Upload embeddings to Qdrant Cloud"""
    
    def __init__(self, collection_name: str = "cosmetic_ingredients"):
        """
        STEP 7.1: Initialize Qdrant client
        
        Args:
            collection_name: Name of the Qdrant collection
        """
        self.logger = logger
        self.collection_name = collection_name
        
        # STEP 7.2: Connect to Qdrant Cloud
        self.logger.info("Connecting to Qdrant Cloud...")
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.logger.info("Connected to Qdrant successfully")
        
    def create_collection(self, vector_size: int = 384):
        """
        STEP 7.3: Create Qdrant collection
        
        Args:
            vector_size: Size of embedding vectors (384 for all-MiniLM-L6-v2)
        """
        try:
            # STEP 7.4: Check if collection exists
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name in collection_names:
                self.logger.info(f"Collection {self.collection_name} already exists")
                # STEP 7.5: Delete and recreate for fresh start
                self.client.delete_collection(self.collection_name)
                self.logger.info("Deleted existing collection")
                
            # STEP 7.6: Create new collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                )
            )
            self.logger.info(f"Created collection: {self.collection_name}")
            
        except Exception as e:
            self.logger.error(f"Error creating collection: {e}")
            raise
            
    def upload_embeddings(self, ingredients_with_embeddings: List[Dict]):
        """
        STEP 7.7: Upload ingredient embeddings to Qdrant
        
        Args:
            ingredients_with_embeddings: List of ingredients with embeddings
        """
        self.logger.info(f"Uploading {len(ingredients_with_embeddings)} ingredients to Qdrant...")
        
        # STEP 7.8: Prepare points for upload
        points = []
        
        for idx, ingredient in enumerate(ingredients_with_embeddings):
            # STEP 7.9: Create point with embedding and metadata
            point = PointStruct(
                id=idx,
                vector=ingredient['embedding'],
                payload={
                    'name': ingredient['name'],
                    'purpose': ingredient['purpose'],
                    'description': ingredient['description'],
                    'safety_score': ingredient.get('safety_score'),
                    'concerns': ingredient['concerns'],
                    'sources': ingredient.get('sources', []),
                    'embedding_text': ingredient.get('embedding_text', '')
                }
            )
            points.append(point)
            
        # STEP 7.10: Upload in batches for efficiency
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
            self.logger.info(f"Uploaded batch {i//batch_size + 1}/{(len(points)-1)//batch_size + 1}")
            
        self.logger.info("Upload complete!")
        
    def test_search(self, query: str, top_k: int = 3):
        """
        STEP 7.11: Test vector search
        
        Args:
            query: Search query
            top_k: Number of results to return
        """
        from sentence_transformers import SentenceTransformer
        
        self.logger.info(f"Testing search for: {query}")
        
        # STEP 7.12: Generate query embedding
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_vector = model.encode(query).tolist()
        
        # STEP 7.13: Search Qdrant
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k
        ).points
        
        # STEP 7.14: Display results
        self.logger.info(f"Found {len(results)} results:")
        for i, result in enumerate(results, 1):
            self.logger.info(f"{i}. {result.payload['name']} (score: {result.score:.3f})")
            self.logger.info(f"   Purpose: {result.payload['purpose']}")