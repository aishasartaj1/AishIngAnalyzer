"""
DAY 2 Test: Multi-Agent Workflow Demo
Tests Supervisor + Research agents
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.workflow import run_analysis


def main():
    """Test the multi-agent workflow with sample ingredients"""

    print("="*70)
    print("DAY 2 TEST: Multi-Agent Workflow (Supervisor + Research)")
    print("="*70)

    # Test case: Simple ingredient list
    test_ingredients = [
        "Water",
        "Niacinamide",
        "Hyaluronic Acid",
        "Glycerin"
    ]

    # Run analysis
    result = run_analysis(
        ingredient_names=test_ingredients,
        user_name="Test User",
        skin_type="sensitive",
        allergies=["Fragrance"],
        expertise_level="beginner"
    )

    # Display results
    print("\n" + "="*70)
    print("RESULTS:")
    print("="*70)

    if result.get("safety_analysis"):
        print("\n" + result["safety_analysis"])
    else:
        print("\n⚠️ Analysis not completed")

    print("\n" + "="*70)
    print("WORKFLOW STATS:")
    print(f"Research attempts: {result.get('research_attempts', 0)}")
    print(f"Analysis attempts: {result.get('analysis_attempts', 0)}")
    print(f"Critic approved: {result.get('critic_approved', False)}")
    print(f"Workflow complete: {result.get('workflow_complete', False)}")
    print("="*70)


if __name__ == "__main__":
    main()
