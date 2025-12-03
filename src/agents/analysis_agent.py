"""
DAY 3: Analysis Agent - Personalized Safety Analyst
Powered by Gemini 2.0 Flash
"""

import os
from typing import Dict
import google.generativeai as genai
from ..graph.state import AnalysisState


class AnalysisAgent:
    """
    Analysis Agent: Generates personalized safety analysis

    Intelligence:
    • Adapt detail level by user expertise (beginner/intermediate/expert)
    • Cross-reference with user allergies
    • Generate prominent warnings for allergens
    • Self-validate completeness before returning

    Adaptive Behavior:
    • Beginner → Simple, clear language
    • Expert → Technical details and chemical explanations
    • High-risk ingredients → Bold warnings
    • Allergies → AVOID tags prominently displayed
    """

    def __init__(self):
        """Initialize Analysis Agent with Gemini 2.0 Flash"""
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def run(self, state: AnalysisState) -> Dict:
        """
        Generate personalized safety analysis report

        Process:
        1. Get user profile and ingredient data from state
        2. Adapt analysis tone based on expertise level
        3. Cross-reference ingredients with user allergies
        4. Generate warnings for high-risk ingredients
        5. Format as structured report
        6. Self-validate completeness

        Args:
            state: Current workflow state

        Returns:
            Updated state with safety_analysis and analysis_complete flag
        """

        print("\n📊 Analysis Agent: Generating personalized safety analysis...")

        ingredient_data = state.get("ingredient_data", [])
        user_name = state.get("user_name", "User")
        skin_type = state.get("skin_type", "normal")
        allergies = state.get("allergies", [])
        expertise_level = state.get("expertise_level", "beginner")
        analysis_attempts = state.get("analysis_attempts", 0)
        critic_feedback = state.get("critic_feedback")

        if not ingredient_data:
            print("❌ Analysis Agent: No ingredient data to analyze")
            return {
                "analysis_complete": False,
                "analysis_attempts": analysis_attempts + 1,
                "messages": [{
                    "role": "assistant",
                    "content": "No ingredient data available for analysis."
                }]
            }

        # Build analysis prompt
        prompt = self._build_analysis_prompt(
            ingredient_data=ingredient_data,
            user_name=user_name,
            skin_type=skin_type,
            allergies=allergies,
            expertise_level=expertise_level,
            critic_feedback=critic_feedback
        )

        try:
            # Generate analysis using Gemini
            response = self.model.generate_content(prompt)
            safety_analysis = response.text

            print(f"  ✅ Analysis generated ({len(safety_analysis)} characters)")
            print(f"  📝 Adapted for {expertise_level} level user with {skin_type} skin")

            if allergies:
                print(f"  ⚠️  Allergen check: {len(allergies)} allergens cross-referenced")

            return {
                "analysis_complete": True,
                "safety_analysis": safety_analysis,
                "analysis_attempts": analysis_attempts + 1,
                "critic_feedback": None,  # Reset feedback after incorporating it
                "messages": [{
                    "role": "assistant",
                    "content": f"Generated personalized safety analysis for {len(ingredient_data)} ingredients."
                }]
            }

        except Exception as e:
            print(f"❌ Analysis Agent error: {e}")
            return {
                "analysis_complete": False,
                "analysis_attempts": analysis_attempts + 1,
                "messages": [{
                    "role": "assistant",
                    "content": f"Error generating analysis: {str(e)}"
                }]
            }

    def _build_analysis_prompt(
        self,
        ingredient_data: list,
        user_name: str,
        skin_type: str,
        allergies: list,
        expertise_level: str,
        critic_feedback: str = None
    ) -> str:
        """Build analysis prompt adapted to user profile"""

        # Build ingredient summary
        ingredient_summary = "\n".join([
            f"- {ing['name']}: {ing.get('purpose', 'Unknown purpose')} "
            f"(Safety: {ing.get('safety_score', 'N/A')}, Concerns: {', '.join(ing.get('concerns', ['none']))})"
            for ing in ingredient_data
        ])

        # Adapt tone based on expertise
        tone_instruction = {
            "beginner": "Use simple, clear language. Avoid jargon. Focus on practical implications.",
            "intermediate": "Use moderate technical detail. Explain key concepts briefly.",
            "expert": "Use technical terminology. Include chemical mechanisms and research references."
        }.get(expertise_level, "Use clear, accessible language.")

        # Build base prompt
        prompt = f"""You are a cosmetic ingredient safety analyst. Generate a personalized safety analysis report.

USER PROFILE:
- Name: {user_name}
- Skin Type: {skin_type}
- Expertise Level: {expertise_level}
- Allergens/Ingredients to Avoid: {', '.join(allergies) if allergies else 'None'}

INGREDIENTS TO ANALYZE:
{ingredient_summary}

INSTRUCTIONS:
1. {tone_instruction}
2. For EVERY SINGLE ingredient, you MUST provide ALL of the following in a TABLE format:
   - **Ingredient:** [Ingredient Name]
   - **Purpose:** [What this ingredient does - moisturizer, preservative, etc.]
   - **Safety Rating:** [1-10 scale, where 1=safest, 10=most concerning]
   - **Concerns:** [Specific safety concerns or "None known" if safe]
   - **Recommendation:** [SAFE / USE WITH CAUTION / AVOID]
3. Cross-reference ALL ingredients with user's allergen/avoidance list: {', '.join(allergies) if allergies else 'none'}
4. If any ingredient matches the user's list, mark it with "⚠️ ALLERGEN/INGREDIENT TO AVOID" in the Ingredient column and recommend AVOID
   - IMPORTANT: Use the term "Allergen/Ingredient to Avoid" - this covers both true allergies and preference-based avoidance
   - Reason: Some users have true allergies, others just prefer to avoid certain ingredients (e.g., alcohol-free or fragrance-free preference)
5. Adapt recommendations based on skin type ({skin_type})
6. Provide an overall verdict (SAFE TO USE / USE WITH CAUTION / AVOID)
7. Keep the analysis concise and actionable

FORMAT EXAMPLE (FOLLOW THIS EXACTLY):
## Ingredient Analysis

| Ingredient | Purpose | Safety Rating | Concerns | Recommendation |
|------------|---------|---------------|----------|----------------|
| Aqua (Water) | Solvent and base ingredient | 1 | None known | SAFE |
| Glycolic Acid | Chemical exfoliant (AHA) | 4 | Can cause irritation, sun sensitivity | USE WITH CAUTION |
| Fragrance ⚠️ ALLERGEN/INGREDIENT TO AVOID | Adds scent to product | 7 | Potential allergen, irritation | AVOID |

## Allergen/Ingredient Check
[List any ingredients that match user's allergen/avoidance list]

## Overall Verdict
[Safe to use / Use with caution / Avoid - with brief reasoning]

## Recommendations for {skin_type.title()} Skin
[Specific guidance]
"""

        # Add critic feedback if this is a retry
        if critic_feedback:
            prompt += f"\n\nCRITIC FEEDBACK (incorporate these improvements):\n{critic_feedback}\n"

        return prompt
