"""
DAY 4 Test: Complete System with UI Integration
Tests the full pipeline with observability and session tracking
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.agents.workflow import run_analysis


def main():
    """Test the complete system with multiple scenarios"""

    print("="*70)
    print("DAY 4 TEST: Complete Multi-Agent System")
    print("Memory + Observability + Full Workflow")
    print("="*70)

    # Track session info
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"\n📊 Session ID: {session_id}")
    print("="*70)

    # ==========================================
    # TEST SCENARIO 1: Beginner User
    # ==========================================
    print("\n\n" + "="*70)
    print("TEST SCENARIO 1: Beginner User - Simple Product")
    print("="*70)

    test1_ingredients = [
        "Water",
        "Glycerin",
        "Niacinamide",
        "Hyaluronic Acid"
    ]

    result1 = run_analysis(
        ingredient_names=test1_ingredients,
        user_name="Sarah",
        skin_type="normal",
        allergies=[],
        expertise_level="beginner"
    )

    # Display results
    print("\n" + "-"*70)
    print("SCENARIO 1 RESULTS:")
    print("-"*70)
    if result1.get("safety_analysis"):
        print(result1["safety_analysis"])
    print(f"\n✓ Research attempts: {result1.get('research_attempts', 0)}")
    print(f"✓ Analysis attempts: {result1.get('analysis_attempts', 0)}")
    print(f"✓ Critic approved: {result1.get('critic_approved', False)}")

    # ==========================================
    # TEST SCENARIO 2: Sensitive Skin + Allergen
    # ==========================================
    print("\n\n" + "="*70)
    print("TEST SCENARIO 2: Sensitive Skin User with Allergen Match")
    print("="*70)

    test2_ingredients = [
        "Water",
        "Niacinamide",
        "Parfum",  # ALLERGEN!
        "Retinol",
        "Hyaluronic Acid",
        "Glycerin",
        "Alcohol Denat"
    ]

    result2 = run_analysis(
        ingredient_names=test2_ingredients,
        user_name="Aisha",
        skin_type="sensitive",
        allergies=["Fragrance", "Parfum"],
        expertise_level="intermediate"
    )

    # Display results
    print("\n" + "-"*70)
    print("SCENARIO 2 RESULTS:")
    print("-"*70)
    if result2.get("safety_analysis"):
        print(result2["safety_analysis"])
    else:
        print("⚠️ Analysis not completed")
        if result2.get("critic_feedback"):
            print(f"\nCritic Feedback:\n{result2['critic_feedback']}")
    print(f"\n✓ Research attempts: {result2.get('research_attempts', 0)}")
    print(f"✓ Analysis attempts: {result2.get('analysis_attempts', 0)}")
    print(f"✓ Critic approved: {result2.get('critic_approved', False)}")

    # ==========================================
    # TEST SCENARIO 3: Expert User - Complex Formula
    # ==========================================
    print("\n\n" + "="*70)
    print("TEST SCENARIO 3: Expert User - Complex Anti-Aging Formula")
    print("="*70)

    test3_ingredients = [
        "Water",
        "Retinol",
        "Niacinamide",
        "Hyaluronic Acid",
        "Glycerin",
        "Peptides",
        "Vitamin C",
        "Glycolic Acid",
        "Salicylic Acid",
        "Ceramides"
    ]

    result3 = run_analysis(
        ingredient_names=test3_ingredients,
        user_name="Dr. Chen",
        skin_type="combination",
        allergies=["Alcohol"],
        expertise_level="expert"
    )

    # Display results
    print("\n" + "-"*70)
    print("SCENARIO 3 RESULTS:")
    print("-"*70)
    if result3.get("safety_analysis"):
        print(result3["safety_analysis"])
    print(f"\n✓ Research attempts: {result3.get('research_attempts', 0)}")
    print(f"✓ Analysis attempts: {result3.get('analysis_attempts', 0)}")
    print(f"✓ Critic approved: {result3.get('critic_approved', False)}")

    # ==========================================
    # SUMMARY STATISTICS
    # ==========================================
    print("\n\n" + "="*70)
    print("SESSION SUMMARY")
    print("="*70)

    total_ingredients = len(test1_ingredients) + len(test2_ingredients) + len(test3_ingredients)
    total_research_attempts = (
        result1.get('research_attempts', 0) +
        result2.get('research_attempts', 0) +
        result3.get('research_attempts', 0)
    )
    total_analysis_attempts = (
        result1.get('analysis_attempts', 0) +
        result2.get('analysis_attempts', 0) +
        result3.get('analysis_attempts', 0)
    )
    approved_count = sum([
        result1.get('critic_approved', False),
        result2.get('critic_approved', False),
        result3.get('critic_approved', False)
    ])

    print(f"\n📊 Total Scenarios Tested: 3")
    print(f"📊 Total Ingredients Analyzed: {total_ingredients}")
    print(f"📊 Total Research Attempts: {total_research_attempts}")
    print(f"📊 Total Analysis Attempts: {total_analysis_attempts}")
    print(f"📊 Critic Approved: {approved_count}/3 scenarios")
    print(f"📊 Success Rate: {approved_count/3*100:.0f}%")

    print("\n" + "="*70)
    print("DAY 4 TEST COMPLETE")
    print("="*70)

    # Final verdict
    if approved_count == 3:
        print("\n✅ ALL TESTS PASSED: Multi-agent system working correctly!")
    elif approved_count >= 2:
        print(f"\n⚠️  PARTIAL SUCCESS: {approved_count}/3 scenarios approved")
    else:
        print("\n❌ TESTS FAILED: System needs debugging")

    print(f"\n📁 Session ID: {session_id}")
    print("💡 To launch UI: streamlit run src/ui/streamlit_app.py")
    print("="*70)


if __name__ == "__main__":
    main()
