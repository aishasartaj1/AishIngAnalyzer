"""
DAY 3: FastMCP Custom Tools
Built with FastMCP for agent tool calling
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from tavily import TavilyClient


class IngredientTools:
    """
    Custom tools for ingredient analysis
    Designed to be exposed via FastMCP server
    """

    def __init__(self):
        """Initialize tools with Qdrant, embedding model, and Tavily"""
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.collection_name = "cosmetic_ingredients"
        self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

        # Initialize Tavily for web search fallback
        tavily_key = os.getenv("TAVILY_API_KEY")
        self.tavily_client = TavilyClient(api_key=tavily_key) if tavily_key else None

    def ingredient_lookup(self, ingredient_name: str) -> Dict:
        """
        Tool 1: Query Qdrant vector database for ingredient information

        Args:
            ingredient_name: Name of ingredient to look up

        Returns:
            {
                "name": str,
                "purpose": str,
                "safety_score": int (1-10),
                "concerns": List[str],
                "description": str,
                "confidence": float (0-1),
                "source": str
            }
        """
        try:
            # Generate embedding for search
            query_vector = self.embedding_model.encode(ingredient_name).tolist()

            # Search Qdrant
            results = self.qdrant_client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=1
            ).points

            if results:
                result = results[0]
                payload = result.payload
                confidence = result.score

                return {
                    "name": payload.get("name", ingredient_name),
                    "purpose": payload.get("purpose", ""),
                    "safety_score": payload.get("safety_score"),
                    "concerns": payload.get("concerns", ["none"]),
                    "description": payload.get("description", ""),
                    "confidence": float(confidence),
                    "source": "qdrant"
                }
            else:
                # No results found
                return {
                    "name": ingredient_name,
                    "purpose": "Unknown",
                    "safety_score": None,
                    "concerns": ["No data available"],
                    "description": "",
                    "confidence": 0.0,
                    "source": "not_found"
                }

        except Exception as e:
            print(f"Error in ingredient_lookup: {e}")
            return {
                "name": ingredient_name,
                "purpose": "Error",
                "safety_score": None,
                "concerns": [f"Lookup error: {str(e)}"],
                "description": "",
                "confidence": 0.0,
                "source": "error"
            }

    def safety_scorer(
        self,
        ingredient_data: Dict,
        user_skin_type: str = "normal",
        user_allergies: List[str] = None
    ) -> Dict:
        """
        Tool 2: Calculate personalized safety score

        Factors:
        - Base safety score from ingredient data
        - User skin type compatibility
        - Allergen matching

        Args:
            ingredient_data: Dict from ingredient_lookup
            user_skin_type: normal, sensitive, oily, dry, combination
            user_allergies: List of user's allergens

        Returns:
            {
                "personalized_score": float (1-10),
                "base_score": int (1-10),
                "adjustments": List[str],
                "recommendation": str (SAFE/CAUTION/AVOID),
                "reasoning": str
            }
        """
        user_allergies = user_allergies or []

        base_score = ingredient_data.get("safety_score")
        ingredient_name = ingredient_data.get("name", "Unknown")
        concerns = ingredient_data.get("concerns", [])

        # Start with base score
        if base_score is None:
            base_score = 5  # Neutral if unknown

        personalized_score = float(base_score)
        adjustments = []
        reasoning_parts = []

        # Adjustment 1: Allergen check
        if self.is_allergen_match(ingredient_name, user_allergies):
            personalized_score = 10  # Maximum concern
            adjustments.append("Allergen match: +5 points")
            reasoning_parts.append(f"ALLERGEN MATCH: {ingredient_name} matches your allergy list")

        # Adjustment 2: Skin type compatibility
        if user_skin_type == "sensitive":
            # Increase score for ingredients with irritation concerns
            if any(concern in str(concerns).lower() for concern in ["irritation", "allergic", "sensitizing"]):
                personalized_score = min(10, personalized_score + 2)
                adjustments.append("Sensitive skin: +2 points for irritation concerns")
                reasoning_parts.append("Higher concern for sensitive skin due to irritation risk")

        # Adjustment 3: Oily skin considerations
        if user_skin_type == "oily":
            if "comedogenic" in str(concerns).lower():
                personalized_score = min(10, personalized_score + 1)
                adjustments.append("Oily skin: +1 point for comedogenic risk")
                reasoning_parts.append("May clog pores on oily skin")

        # Determine recommendation
        if personalized_score >= 8:
            recommendation = "AVOID"
        elif personalized_score >= 5:
            recommendation = "USE WITH CAUTION"
        else:
            recommendation = "SAFE"

        reasoning = "; ".join(reasoning_parts) if reasoning_parts else f"Base safety score: {base_score}/10"

        return {
            "personalized_score": round(personalized_score, 1),
            "base_score": base_score,
            "adjustments": adjustments,
            "recommendation": recommendation,
            "reasoning": reasoning
        }

    def allergen_matcher(self, ingredient_name: str, user_allergies: List[str]) -> Dict:
        """
        Tool 3: Check if ingredient matches user allergies

        Handles:
        - Exact name matching
        - Synonym matching
        - Chemical name variations

        Args:
            ingredient_name: Ingredient to check
            user_allergies: List of user's allergens

        Returns:
            {
                "is_match": bool,
                "matched_allergen": str or None,
                "match_type": str (exact/synonym/chemical)
            }
        """
        is_match, matched_allergen = self.is_allergen_match(ingredient_name, user_allergies)

        if is_match:
            # Determine match type
            if matched_allergen.lower() == ingredient_name.lower():
                match_type = "exact"
            elif matched_allergen.lower() in ingredient_name.lower() or ingredient_name.lower() in matched_allergen.lower():
                match_type = "partial"
            else:
                match_type = "synonym"
        else:
            match_type = None

        return {
            "is_match": is_match,
            "matched_allergen": matched_allergen,
            "match_type": match_type
        }

    def is_allergen_match(self, ingredient_name: str, user_allergies: List[str]) -> tuple:
        """
        Helper: Check if ingredient matches any user allergen

        Returns:
            (is_match: bool, matched_allergen: str or None)
        """
        ingredient_lower = ingredient_name.lower()

        # Common synonym mappings
        synonym_map = {
            "fragrance": ["parfum", "perfume", "fragrance"],
            "parfum": ["fragrance", "perfume", "parfum"],
            "vitamin e": ["tocopherol", "tocopheryl acetate"],
            "alcohol": ["alcohol denat", "ethanol", "ethyl alcohol"],
            "retinol": ["retinyl palmitate", "retinoic acid", "tretinoin"]
        }

        for allergen in user_allergies:
            allergen_lower = allergen.lower()

            # Exact match
            if allergen_lower == ingredient_lower:
                return (True, allergen)

            # Partial match (ingredient contains allergen or vice versa)
            if allergen_lower in ingredient_lower or ingredient_lower in allergen_lower:
                return (True, allergen)

            # Synonym match
            for key, synonyms in synonym_map.items():
                if allergen_lower == key or allergen_lower in synonyms:
                    if any(syn in ingredient_lower for syn in synonyms):
                        return (True, allergen)

        return (False, None)

    def tavily_search(self, ingredient_name: str) -> Dict:
        """
        Tool 4: Web search for ingredients not in database (Fallback)

        Uses Tavily API to search the web for ingredient safety information
        when Qdrant confidence is low (<0.7) or ingredient not found.

        Args:
            ingredient_name: Ingredient to research

        Returns:
            {
                "name": str,
                "purpose": str,
                "safety_score": int (estimated 1-10),
                "concerns": List[str],
                "description": str,
                "confidence": float (0-1),
                "source": str
            }
        """
        if not self.tavily_client:
            print("[WARNING] Tavily API key not configured. Returning placeholder.")
            return {
                "name": ingredient_name,
                "purpose": "Web search unavailable",
                "safety_score": 5,
                "concerns": ["No web search available"],
                "description": "Tavily API key not configured",
                "confidence": 0.3,
                "source": "tavily_unavailable"
            }

        try:
            # Search for ingredient safety information
            search_query = f"{ingredient_name} cosmetic skincare ingredient safety concerns benefits"
            print(f"  🔍 Tavily fallback search: {search_query}")

            response = self.tavily_client.search(
                query=search_query,
                max_results=3,
                search_depth="advanced"
            )

            if not response or "results" not in response or not response["results"]:
                return {
                    "name": ingredient_name,
                    "purpose": "Unknown",
                    "safety_score": 5,
                    "concerns": ["No web results found"],
                    "description": "",
                    "confidence": 0.2,
                    "source": "tavily_no_results"
                }

            # Extract information from top results
            results = response["results"]
            combined_content = " ".join([r.get("content", "") for r in results[:3]])

            # Simple keyword-based analysis (in production, use LLM to parse)
            purpose = "Unknown purpose"
            concerns = []
            safety_score = 5  # Neutral default

            # Extract purpose clues
            if any(word in combined_content.lower() for word in ["moisturizer", "hydrat"]):
                purpose = "Moisturizing agent"
            elif any(word in combined_content.lower() for word in ["preservative", "antimicrobial"]):
                purpose = "Preservative"
            elif any(word in combined_content.lower() for word in ["antioxidant", "vitamin"]):
                purpose = "Antioxidant"
            elif any(word in combined_content.lower() for word in ["surfactant", "cleanser"]):
                purpose = "Cleansing agent"
            elif any(word in combined_content.lower() for word in ["emulsifier", "stabilizer"]):
                purpose = "Emulsifier"
            elif any(word in combined_content.lower() for word in ["fragrance", "scent", "perfume"]):
                purpose = "Fragrance"

            # Detect concerns
            if any(word in combined_content.lower() for word in ["irritat", "sensitiz", "allergic"]):
                concerns.append("potential irritation")
                safety_score = max(6, safety_score)
            if any(word in combined_content.lower() for word in ["toxic", "harmful", "danger"]):
                concerns.append("toxicity concerns")
                safety_score = max(7, safety_score)
            if any(word in combined_content.lower() for word in ["comedogenic", "acne", "clog"]):
                concerns.append("may clog pores")
                safety_score = max(6, safety_score)
            if any(word in combined_content.lower() for word in ["safe", "gentle", "mild"]):
                safety_score = min(3, safety_score)
                if not concerns:
                    concerns.append("generally safe")

            if not concerns:
                concerns = ["insufficient data"]

            # Confidence based on result quality
            confidence = 0.6 if len(results) >= 2 else 0.4

            return {
                "name": ingredient_name,
                "purpose": purpose,
                "safety_score": safety_score,
                "concerns": concerns,
                "description": combined_content[:300] + "..." if len(combined_content) > 300 else combined_content,
                "confidence": confidence,
                "source": "tavily_web_search"
            }

        except Exception as e:
            print(f"[ERROR] Tavily search error: {e}")
            return {
                "name": ingredient_name,
                "purpose": "Search error",
                "safety_score": 5,
                "concerns": [f"Web search error: {str(e)}"],
                "description": "",
                "confidence": 0.1,
                "source": "tavily_error"
            }


# Singleton instance
_tools_instance = None

def get_tools() -> IngredientTools:
    """Get singleton instance of tools"""
    global _tools_instance
    if _tools_instance is None:
        _tools_instance = IngredientTools()
    return _tools_instance
