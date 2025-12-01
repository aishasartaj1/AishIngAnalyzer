"""
DAY 3 Test: Full 4-Agent Workflow Demo
Tests Supervisor + Research + Analysis + Critic
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.workflow import run_analysis


def main():
    """Test the complete 4-agent workflow"""

    print("="*70)
    print("DAY 3 TEST: Full 4-Agent Workflow")
    print("Supervisor → Research → Analysis → Critic")
    print("="*70)

    # Test case: Realistic cosmetic product
    test_ingredients = [
        "Water",
        "Niacinamide",
        "Parfum",  # Potential allergen
        "Retinol",
        "Hyaluronic Acid",
        "Glycerin",
        "Alcohol Denat"
    ]

    # Test with user who has fragrance allergy
    result = run_analysis(
        ingredient_names=test_ingredients,
        user_name="Aisha",
        skin_type="sensitive",
        allergies=["Fragrance", "Parfum"],
        expertise_level="intermediate"
    )

    # Display results
    print("\n" + "="*70)
    print("SAFETY ANALYSIS REPORT:")
    print("="*70)

    if result.get("safety_analysis"):
        print("\n" + result["safety_analysis"])
    else:
        print("\n⚠️ Analysis not completed")
        if result.get("critic_feedback"):
            print(f"\nCritic Feedback:\n{result['critic_feedback']}")

    print("\n" + "="*70)
    print("WORKFLOW STATS:")
    print(f"✓ Research attempts: {result.get('research_attempts', 0)}")
    print(f"✓ Analysis attempts: {result.get('analysis_attempts', 0)}")
    print(f"✓ Critic approved: {result.get('critic_approved', False)}")
    print(f"✓ Research confidence: {result.get('research_confidence', 0.0):.2%}")
    print(f"✓ Workflow complete: {result.get('workflow_complete', False)}")
    print("="*70)

    # Test verdict
    if result.get("critic_approved"):
        print("\n✅ TEST PASSED: Analysis approved by critic!")
    else:
        print("\n⚠️ TEST INCOMPLETE: Analysis needs improvements or max retries reached")


if __name__ == "__main__":
    main()
