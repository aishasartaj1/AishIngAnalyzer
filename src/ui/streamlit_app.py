"""
DAY 4: Streamlit UI for AishIngAnalyzer
User-friendly interface for ingredient safety analysis
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.agents.workflow import run_analysis


def main():
    """Main Streamlit app"""

    # Page config
    st.set_page_config(
        page_title="AishIngAnalyzer - Cosmetic Ingredient Safety",
        page_icon="🧴",
        layout="wide"
    )

    # Title and description
    st.title("🧴 AishIngAnalyzer")
    st.markdown("### AI-Powered Cosmetic Ingredient Safety Analyzer")
    st.markdown("**Personalized safety analysis using multi-agent AI system**")

    st.divider()

    # Sidebar: User Profile
    with st.sidebar:
        st.header("👤 User Profile")

        user_name = st.text_input("Name", value="User", help="Your name for personalized analysis")

        skin_type = st.selectbox(
            "Skin Type",
            options=["normal", "sensitive", "oily", "dry", "combination"],
            help="Your skin type affects ingredient recommendations"
        )

        expertise_level = st.selectbox(
            "Expertise Level",
            options=["beginner", "intermediate", "expert"],
            help="Adjusts analysis detail level"
        )

        st.subheader("⚠️ Allergies")
        allergies_input = st.text_area(
            "Enter your allergens (one per line)",
            placeholder="Fragrance\nParfum\nAlcohol",
            help="We'll flag any matching ingredients"
        )

        allergies = [a.strip() for a in allergies_input.split("\n") if a.strip()]

        if allergies:
            st.info(f"✓ Tracking {len(allergies)} allergen(s)")

    # Main area: Ingredient Input
    st.header("📋 Ingredient List")

    input_method = st.radio(
        "How would you like to input ingredients?",
        options=["Paste ingredient list", "Type manually"],
        horizontal=True
    )

    if input_method == "Paste ingredient list":
        ingredients_input = st.text_area(
            "Paste ingredients (comma or newline separated)",
            placeholder="Water, Niacinamide, Glycerin, Hyaluronic Acid, Retinol",
            height=150,
            help="Paste your product's ingredient list from the label"
        )

        # Parse ingredients
        if "," in ingredients_input:
            ingredient_names = [i.strip() for i in ingredients_input.split(",") if i.strip()]
        else:
            ingredient_names = [i.strip() for i in ingredients_input.split("\n") if i.strip()]

    else:
        ingredient_names = []
        num_ingredients = st.number_input("Number of ingredients", min_value=1, max_value=50, value=5)

        for i in range(num_ingredients):
            ing = st.text_input(f"Ingredient {i+1}", key=f"ing_{i}")
            if ing.strip():
                ingredient_names.append(ing.strip())

    # Display ingredient count
    if ingredient_names:
        st.success(f"✓ {len(ingredient_names)} ingredients ready for analysis")
        with st.expander("View ingredient list"):
            st.write(ingredient_names)

    st.divider()

    # Analyze button
    if st.button("🔬 Analyze Ingredients", type="primary", disabled=not ingredient_names):
        if not ingredient_names:
            st.error("Please enter at least one ingredient!")
            return

        # Run analysis with progress
        with st.spinner("🤖 Multi-agent analysis in progress..."):
            progress_text = st.empty()
            progress_bar = st.progress(0)

            progress_text.text("🔬 Research Agent: Gathering ingredient data...")
            progress_bar.progress(25)

            try:
                final_state = run_analysis(
                    ingredient_names=ingredient_names,
                    user_name=user_name,
                    skin_type=skin_type,
                    allergies=allergies,
                    expertise_level=expertise_level
                )

                progress_text.text("📊 Analysis Agent: Generating personalized report...")
                progress_bar.progress(50)

                progress_text.text("🔍 Critic Agent: Validating quality...")
                progress_bar.progress(75)

                progress_text.text("✅ Complete!")
                progress_bar.progress(100)

                # Display results
                st.divider()
                st.header("📊 Safety Analysis Results")

                if final_state.get("safety_analysis"):
                    st.markdown(final_state["safety_analysis"])

                    # Download button
                    st.download_button(
                        label="📥 Download Report",
                        data=final_state["safety_analysis"],
                        file_name=f"ingredient_analysis_{user_name.replace(' ', '_')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("Analysis could not be completed. Please try again.")

                # Show workflow stats in expander
                with st.expander("🔍 Workflow Details"):
                    st.json({
                        "research_attempts": final_state.get("research_attempts", 0),
                        "analysis_attempts": final_state.get("analysis_attempts", 0),
                        "critic_approved": final_state.get("critic_approved", False),
                        "research_confidence": final_state.get("research_confidence", 0.0)
                    })

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)

    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.8em;'>
    🤖 Powered by Gemini 2.0 Flash | Built with LangGraph | Data from Qdrant Vector DB<br>
    Multi-Agent System: Supervisor → Research → Analysis → Critic
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
