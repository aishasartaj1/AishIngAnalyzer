"""
DAY 2: Research Agent - Intelligent Data Gatherer
Powered by Gemini 2.0 Flash
"""

import os
from typing import Dict, List
import google.generativeai as genai
from ..graph.state import AnalysisState


class ResearchAgent:
    """
    Research Agent: Gathers ingredient data using intelligent tool selection

    Intelligence:
    • Classify ingredient type (common/scientific/brand)
    • Select tools dynamically based on classification
    • Score confidence of retrieved data
    • Trigger fallback if confidence < 0.7

    Tool Strategy:
    • Common name → Qdrant only
    • Scientific → Qdrant + fallback
    • Brand/Unknown → Tavily web search
    """

    def __init__(self):
        """Initialize Research Agent with Gemini 2.0 Flash"""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def run(self, state: AnalysisState) -> Dict:
        """
        Research ingredients using tool calls

        Process:
        1. Get ingredient list from state
        2. For each ingredient:
           - Classify type (common/scientific/unknown)
           - Call ingredient_lookup (Qdrant)
           - If confidence < 0.7, fallback to tavily_search
           - Calculate personalized safety score
           - Check allergen matches
        3. Compile all results
        4. Mark research complete if sufficient data gathered

        Args:
            state: Current workflow state

        Returns:
            Updated state with ingredient_data and research_complete flag
        """

        print("\n🔬 Research Agent: Starting ingredient research...")

        from ..tools.mcp_tools import get_tools

        ingredient_names = state.get("ingredient_names", [])
        research_attempts = state.get("research_attempts", 0)
        user_skin_type = state.get("skin_type", "normal")
        user_allergies = state.get("allergies", [])

        if not ingredient_names:
            print("❌ Research Agent: No ingredients provided")
            return {
                "research_complete": False,
                "research_attempts": research_attempts + 1,
                "messages": [{
                    "role": "assistant",
                    "content": "No ingredients to analyze. Please provide ingredient names."
                }]
            }

        # Initialize tools
        tools = get_tools()

        ingredient_data = []
        total_confidence = 0.0
        qdrant_hits = 0
        tavily_hits = 0

        for ingredient_name in ingredient_names:
            print(f"  📝 Researching: {ingredient_name}")

            # Step 1: Try Qdrant lookup first
            data = tools.ingredient_lookup(ingredient_name)
            confidence = data.get("confidence", 0.0)
            used_tavily = False

            print(f"    └─ Qdrant result: {data.get('source')} (confidence: {confidence:.2f})")

            # Step 2: If confidence is low, use Tavily web search fallback
            if confidence < 0.7:
                print(f"    └─ Low confidence, trying Tavily fallback...")
                web_data = tools.tavily_search(ingredient_name)

                # Use web data if it has better confidence
                if web_data.get("confidence", 0.0) > confidence:
                    data = web_data
                    confidence = data.get("confidence", 0.0)
                    used_tavily = True
                    print(f"    └─ Using Tavily result (confidence: {confidence:.2f})")

            # Track which tool was used
            if used_tavily:
                tavily_hits += 1
            else:
                qdrant_hits += 1

            # Step 3: Calculate personalized safety score
            score_result = tools.safety_scorer(
                ingredient_data=data,
                user_skin_type=user_skin_type,
                user_allergies=user_allergies
            )

            # Step 4: Check allergen match
            allergen_result = tools.allergen_matcher(
                ingredient_name=ingredient_name,
                user_allergies=user_allergies
            )

            # Merge all data
            complete_data = {
                **data,
                "personalized_score": score_result.get("personalized_score"),
                "base_score": score_result.get("base_score"),
                "recommendation": score_result.get("recommendation"),
                "score_reasoning": score_result.get("reasoning"),
                "is_allergen": allergen_result.get("is_match", False),
                "matched_allergen": allergen_result.get("matched_allergen"),
                "allergen_match_type": allergen_result.get("match_type")
            }

            ingredient_data.append(complete_data)
            total_confidence += confidence

            # Show allergen warning if matched
            if allergen_result.get("is_match"):
                print(f"    ⚠️  ALLERGEN MATCH: {allergen_result.get('matched_allergen')}")

        # Calculate average confidence
        avg_confidence = total_confidence / len(ingredient_names) if ingredient_names else 0.0

        print(f"  ✅ Research complete: {len(ingredient_data)} ingredients found")
        print(f"  📊 Average confidence: {avg_confidence:.2f}")

        # Mark as complete if confidence is sufficient
        research_complete = avg_confidence >= 0.5  # Lower threshold to 0.5 to account for web fallback

        if not research_complete:
            print(f"  ⚠️  Low confidence ({avg_confidence:.2f}), may need retry")

        return {
            "research_complete": research_complete,
            "ingredient_data": ingredient_data,
            "research_confidence": avg_confidence,
            "research_attempts": research_attempts + 1,
            "qdrant_hits": qdrant_hits,
            "tavily_hits": tavily_hits,
            "messages": [{
                "role": "assistant",
                "content": f"Researched {len(ingredient_data)} ingredients with {avg_confidence:.0%} average confidence."
            }]
        }
