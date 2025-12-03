"""
AishIngAnalyzer - Streamlit UI
Complete user interface for cosmetic ingredient safety analysis
"""

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import sys
from pathlib import Path
from PIL import Image
import pytesseract
import pandas as pd
from io import BytesIO
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Tesseract path for Windows
if os.name == 'nt':  # Windows
    # Try common installation paths
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Import backend from correct location (Layer 4: Graph + Memory)
try:
    from src.graph.workflow import run_analysis
    from src.memory import get_session_manager
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Backend import error: {e}")
    BACKEND_AVAILABLE = False
    # Fallback for development
    def run_analysis(**kwargs):
        return {
            "safety_analysis": "Backend not connected yet",
            "research_attempts": 0,
            "analysis_attempts": 0,
            "critic_approved": False,
            "research_confidence": 0.0
        }
    class DummySessionManager:
        def get_or_create_session(self, name): return "dummy"
        def save_user_profile(self, sid, profile): pass
        def add_to_history(self, sid, result): pass
        def get_analysis_history(self, sid, include_longterm=True): return []
    def get_session_manager():
        return DummySessionManager()


def extract_ingredients_from_image(image):
    """Extract ingredient text from uploaded image using OCR"""
    try:
        # Use Tesseract OCR
        text = pytesseract.image_to_string(image)

        # Clean up the text
        text = text.strip()

        # Try to extract ingredient list (usually after "Ingredients:" label)
        if "ingredient" in text.lower():
            # Find everything after "ingredients:"
            match = re.search(r'ingredients?:?\s*(.*)', text, re.IGNORECASE | re.DOTALL)
            if match:
                text = match.group(1)

        return text
    except Exception as e:
        st.error(f"OCR Error: {str(e)}")
        return ""


def create_pdf_report(analysis_text, user_profile):
    """Create PDF report from analysis"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("AishIngAnalyzer - Safety Analysis Report", styles['Title']))
        story.append(Spacer(1, 12))

        # User Profile
        story.append(Paragraph("User Profile", styles['Heading2']))
        story.append(Paragraph(f"Name: {user_profile.get('name', 'N/A')}", styles['Normal']))
        story.append(Paragraph(f"Skin Type: {user_profile.get('skin_type', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 12))

        # Analysis
        story.append(Paragraph("Safety Analysis", styles['Heading2']))
        # Convert markdown to plain text for PDF
        analysis_plain = analysis_text.replace('#', '').replace('**', '')
        for line in analysis_plain.split('\n'):
            if line.strip():
                story.append(Paragraph(line, styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer
    except ImportError:
        st.warning("PDF export requires 'reportlab'. Install with: pip install reportlab")
        return None
    except Exception as e:
        st.error(f"PDF creation error: {str(e)}")
        return None


def create_csv_export(ingredient_data):
    """Create CSV export of ingredient analysis"""
    try:
        df = pd.DataFrame(ingredient_data)
        return df.to_csv(index=False).encode('utf-8')
    except Exception as e:
        st.error(f"CSV creation error: {str(e)}")
        return None


def main():
    """Main Streamlit application"""

    # Page configuration
    st.set_page_config(
        page_title="AishIngAnalyzer - Skincare Ingredient Checker",
        page_icon="🧴",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        font-size: 4rem;
        font-weight: 700;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .mvp-badge {
        display: inline-block;
        background-color: #10B981;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 1rem;
        font-weight: 600;
        margin-left: 1rem;
    }
    .analyze-button {
        background-color: #4F46E5;
        color: white;
        font-size: 1.2rem;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

    # ==========================================
    # AUTHENTICATION
    # ==========================================

    # Load authentication config
    config_path = Path(__file__).parent.parent / "config" / "auth_config.yaml"
    with open(config_path) as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    # Display login form
    name, authentication_status, username = authenticator.login('Login', 'main')

    if authentication_status == False:
        st.error('Username/password is incorrect')
        st.stop()

    if authentication_status == None:
        st.warning('Please enter your email and password')

        # Registration option
        with st.expander("New user? Register here"):
            try:
                if authenticator.register_user('Register user', preauthorization=False):
                    st.success('User registered successfully')
                    # Save updated config
                    with open(config_path, 'w') as file:
                        yaml.dump(config, file, default_flow_style=False)
            except Exception as e:
                st.error(e)
        st.stop()

    # User is authenticated
    st.sidebar.success(f'Welcome {name}!')
    authenticator.logout('Logout', 'sidebar')

    # Initialize session state
    if 'profile_submitted' not in st.session_state:
        st.session_state.profile_submitted = False
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {}
    if 'ingredient_text' not in st.session_state:
        st.session_state.ingredient_text = ""
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    if 'authenticated_email' not in st.session_state:
        st.session_state.authenticated_email = username

    # Initialize SessionManager (with Redis auto-detection)
    if 'session_manager' not in st.session_state:
        st.session_state.session_manager = get_session_manager()
        if BACKEND_AVAILABLE:
            sm = st.session_state.session_manager
            if hasattr(sm, 'redis_client') and sm.redis_client and sm.redis_client.is_connected():
                st.sidebar.success("✅ Long-term memory: Redis connected")
            else:
                st.sidebar.info("📌 Memory: In-memory only (no Redis)")

    # ==========================================
    # SIDEBAR: USER PROFILE
    # ==========================================
    with st.sidebar:
        st.header("👤 Your Profile")

        # Use authenticated email for profile
        sm = st.session_state.session_manager
        user_email = st.session_state.authenticated_email

        if not st.session_state.profile_submitted:
            with st.form("user_profile_form"):
                st.subheader("Profile Information")

                # Basic Info
                name = st.text_input("Name *", placeholder="Enter your name")

                age_group = st.selectbox(
                    "Age Group *",
                    options=["Select...", "<18", "18-25", "26-35", "36-45", "46-55", "56+"]
                )

                sex = st.selectbox(
                    "Sex",
                    options=["Prefer not to say", "Female", "Male"]
                )

                country = st.selectbox(
                    "Country/Region (Optional)",
                    options=["Select...", "United States", "United Kingdom", "Canada",
                            "Australia", "India", "Other"]
                )

                st.divider()

                # Skin Type
                st.subheader("Skin Type *")
                skin_type = st.selectbox(
                    "Select your skin type",
                    options=["Normal", "Dry", "Oily", "Combination", "Sensitive"]
                )

                st.divider()

                # Skin Concerns
                st.subheader("Skin Concerns")
                concerns = st.multiselect(
                    "Select all that apply",
                    options=[
                        "Acne / Breakouts",
                        "Sensitivity / Redness",
                        "Dryness / Dehydration",
                        "Hyperpigmentation",
                        "Anti-aging",
                        "Large Pores",
                        "Eczema-prone",
                        "None"
                    ]
                )

                st.divider()

                # Allergies / Avoid List
                st.subheader("⚠️ Allergens/Ingredients to Avoid")

                allergies_preset = st.multiselect(
                    "Select allergens or ingredients to avoid",
                    options=[
                        "Fragrance",
                        "Essential Oils",
                        "Alcohol",
                        "Parabens",
                        "Sulfates",
                        "Silicones",
                        "Coconut Derivatives",
                        "Fungal Acne Triggers",
                        "Benzoyl Peroxide",
                        "Retinoids"
                    ],
                    help="Can be true allergies, sensitivities, or preferences (e.g., fragrance-free)"
                )

                allergies_custom = st.text_area(
                    "Custom allergens/ingredients to avoid (one per line)",
                    placeholder="Niacinamide\nVitamin C\nLactic Acid",
                    help="Add specific allergens or ingredients you want to avoid"
                )

                st.divider()

                # Experience Level
                st.subheader("Experience Level")
                expertise_level = st.selectbox(
                    "How familiar are you with skincare ingredients?",
                    options=[
                        "Beginner (simple explanations)",
                        "Intermediate (moderate detail)",
                        "Advanced (technical/derm-style)"
                    ],
                    help="This adjusts the analysis complexity"
                )

                # Submit button
                submitted = st.form_submit_button("✅ Save Profile", use_container_width=True)

                if submitted:
                    # Validation
                    if not name or age_group == "Select...":
                        st.error("⚠️ Please fill in required fields (Name, Age Group)")
                    else:
                        # Parse expertise level
                        expertise_map = {
                            "Beginner (simple explanations)": "beginner",
                            "Intermediate (moderate detail)": "intermediate",
                            "Advanced (technical/derm-style)": "expert"
                        }

                        # Combine allergies
                        all_allergies = allergies_preset.copy()
                        if allergies_custom:
                            custom_list = [a.strip() for a in allergies_custom.split('\n') if a.strip()]
                            all_allergies.extend(custom_list)

                        # Build profile dict
                        profile = {
                            "name": name,
                            "age_group": age_group,
                            "sex": sex,
                            "country": country if country != "Select..." else None,
                            "skin_type": skin_type.lower(),
                            "concerns": concerns,
                            "allergies": all_allergies,
                            "expertise_level": expertise_map[expertise_level]
                        }

                        # Save to Streamlit session state
                        st.session_state.user_profile = profile
                        st.session_state.profile_submitted = True

                        # Save to SessionManager using authenticated email
                        sm = st.session_state.session_manager
                        session_id = sm.get_or_create_session(user_email)
                        sm.save_user_profile(session_id, profile)
                        st.session_state.session_id = session_id

                        st.success("✅ Profile saved to memory!")
                        st.rerun()

        else:
            # Profile is saved, just show edit button
            st.success("✅ Profile saved!")

            if st.button("✏️ Edit Profile", use_container_width=True):
                st.session_state.profile_submitted = False
                st.rerun()

    # ==========================================
    # ANALYSIS HISTORY
    # ==========================================

    if st.session_state.profile_submitted and hasattr(st.session_state, 'session_id'):
        st.sidebar.divider()
        st.sidebar.subheader("📜 Analysis History")

        sm = st.session_state.session_manager
        session_id = st.session_state.session_id

        # Get history (includes both session + Redis if connected)
        history = sm.get_analysis_history(session_id, include_longterm=True)

        if history:
            st.sidebar.success(f"✅ {len(history)} analysis(es) saved")

            # Show recent analyses
            with st.sidebar.expander("View History", expanded=False):
                for i, entry in enumerate(history[:5]):  # Show last 5
                    st.markdown(f"**Analysis {i+1}**")
                    if 'ingredient_names' in entry:
                        ingredients = entry['ingredient_names'][:3]  # First 3
                        st.write(f"🧴 {', '.join(ingredients)}...")
                    if 'timestamp' in entry:
                        from datetime import datetime
                        try:
                            ts = datetime.fromisoformat(entry['timestamp'])
                            st.caption(f"📅 {ts.strftime('%b %d, %I:%M %p')}")
                        except:
                            pass
                    if 'critic_approved' in entry:
                        status = "✅ Approved" if entry['critic_approved'] else "⚠️ Needs Review"
                        st.caption(status)
                    st.divider()

            # Clear history option
            if st.sidebar.button("🗑️ Clear History", use_container_width=True):
                sm.clear_session(session_id)
                # Also clear from Redis if connected
                if hasattr(sm, 'redis_client') and sm.redis_client:
                    user_name = st.session_state.user_profile.get('name')
                    if user_name:
                        sm.redis_client.clear_analysis_history(user_name)
                st.sidebar.success("✅ History cleared!")
                st.rerun()
        else:
            st.sidebar.info("No analyses yet")

    # ==========================================
    # MAIN PAGE: INGREDIENT INPUT & ANALYSIS
    # ==========================================

    # Header
    st.markdown('<h1 class="main-header">AishIngAnalyzer <span class="mvp-badge">MVP</span></h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Cosmetic Ingredient Analyzer 🔬</p>', unsafe_allow_html=True)

    st.divider()

    # Check if profile is completed
    if not st.session_state.profile_submitted:
        st.info("👈 Please complete your profile in the sidebar to get personalized analysis")
        st.stop()

    # ==========================================
    # INPUT METHODS
    # ==========================================

    # Tab selection for input method
    tab1, tab2 = st.tabs(["📝 Paste Ingredients", "📸 Upload Photo"])

    with tab1:
        st.markdown("### Paste the ingredients you'd like to check")

        ingredients_text = st.text_area(
            "",
            placeholder="Water, Glycerin, Niacinamide, Hyaluronic Acid, Retinol, Ceramides...",
            height=200,
            value=st.session_state.ingredient_text,
            label_visibility="collapsed"
        )

        if ingredients_text:
            st.session_state.ingredient_text = ingredients_text

    with tab2:
        st.markdown("### Upload a photo of the ingredient list")

        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            # Display image
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)

            # Extract text with OCR
            if st.button("🔍 Extract Ingredients from Image"):
                with st.spinner("Extracting text from image..."):
                    extracted_text = extract_ingredients_from_image(image)
                    if extracted_text:
                        st.session_state.ingredient_text = extracted_text
                        st.session_state.ocr_extracted = True
                        st.success("✅ Text extracted! Review and edit below if needed.")
                        st.rerun()
                    else:
                        st.error("Could not extract text. Please try a clearer image.")

            # Show extracted text in editable text area (if extraction was done)
            if st.session_state.ingredient_text and st.session_state.get('ocr_extracted', False):
                st.markdown("#### Extracted Ingredients")
                st.info("📝 Review the extracted text below. You can edit it if needed before analyzing.")

                edited_text = st.text_area(
                    "Extracted ingredients (editable):",
                    value=st.session_state.ingredient_text,
                    height=200,
                    label_visibility="collapsed"
                )

                # Update session state with edited text
                if edited_text != st.session_state.ingredient_text:
                    st.session_state.ingredient_text = edited_text

    st.divider()

    # ==========================================
    # ANALYZE BUTTON
    # ==========================================

    # Parse ingredients
    ingredient_text = st.session_state.ingredient_text
    if ingredient_text:
        # Try comma-separated first, then newline-separated
        if "," in ingredient_text:
            ingredient_list = [i.strip() for i in ingredient_text.split(",") if i.strip()]
        else:
            ingredient_list = [i.strip() for i in ingredient_text.split("\n") if i.strip()]

        st.info(f"✓ {len(ingredient_list)} ingredients detected")
    else:
        ingredient_list = []

    # Analyze button
    analyze_disabled = len(ingredient_list) == 0

    if st.button("🔬 Analyze Now", type="primary", disabled=analyze_disabled, use_container_width=True):

        profile = st.session_state.user_profile

        with st.spinner("🤖 Running multi-agent analysis..."):

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            status_text.text("🔬 Research Agent: Gathering ingredient data...")
            progress_bar.progress(25)

            # Run analysis
            try:
                result = run_analysis(
                    ingredient_names=ingredient_list,
                    user_name=profile['name'],
                    skin_type=profile['skin_type'],
                    allergies=profile['allergies'],
                    expertise_level=profile['expertise_level']
                )

                status_text.text("📊 Analysis Agent: Generating personalized report...")
                progress_bar.progress(50)

                status_text.text("🔍 Critic Agent: Validating quality...")
                progress_bar.progress(75)

                status_text.text("✅ Complete!")
                progress_bar.progress(100)

                # Clear progress
                import time
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()

                # ==========================================
                # SAVE TO MEMORY
                # ==========================================

                # Save analysis to SessionManager (short-term + long-term if Redis available)
                if hasattr(st.session_state, 'session_id'):
                    sm = st.session_state.session_manager
                    sm.add_to_history(st.session_state.session_id, result)

                # ==========================================
                # DISPLAY RESULTS
                # ==========================================

                st.divider()
                st.header("📊 Safety Analysis Results")

                if result.get("safety_analysis"):

                    # Display analysis
                    st.markdown(result["safety_analysis"])

                    st.divider()

                    # ==========================================
                    # OBSERVABILITY METRICS
                    # ==========================================

                    with st.expander("📊 Analysis Metrics & Performance", expanded=False):
                        # Calculate duration
                        start_time = result.get("analysis_start_time")
                        end_time = result.get("analysis_end_time")

                        if start_time and end_time:
                            from datetime import datetime
                            start_dt = datetime.fromisoformat(start_time)
                            end_dt = datetime.fromisoformat(end_time)
                            duration_seconds = (end_dt - start_dt).total_seconds()

                            st.metric(
                                label="⏱️ Total Analysis Time",
                                value=f"{duration_seconds:.1f}s"
                            )

                        # Display metrics in columns
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                label="🔄 Research Attempts",
                                value=result.get("research_attempts", 0)
                            )
                            st.metric(
                                label="📝 Analysis Attempts",
                                value=result.get("analysis_attempts", 0)
                            )

                        with col2:
                            qdrant_hits = result.get("qdrant_hits", 0)
                            tavily_hits = result.get("tavily_hits", 0)
                            total_ingredients = qdrant_hits + tavily_hits

                            st.metric(
                                label="🗄️ Qdrant Database Hits",
                                value=f"{qdrant_hits}/{total_ingredients}"
                            )
                            st.metric(
                                label="🌐 Tavily Web Search Hits",
                                value=f"{tavily_hits}/{total_ingredients}"
                            )

                        with col3:
                            st.metric(
                                label="❌ Critic Rejections",
                                value=result.get("total_critic_rejections", 0)
                            )
                            st.metric(
                                label="📊 Research Confidence",
                                value=f"{result.get('research_confidence', 0.0):.0%}"
                            )

                        # Data source breakdown chart
                        if qdrant_hits > 0 or tavily_hits > 0:
                            st.write("**Data Source Breakdown:**")
                            chart_data = {
                                "Qdrant Database": qdrant_hits,
                                "Tavily Web Search": tavily_hits
                            }
                            st.bar_chart(chart_data)

                    st.divider()

                    # ==========================================
                    # EXPORT OPTIONS
                    # ==========================================

                    st.subheader("📥 Export Report")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        # Text export
                        st.download_button(
                            label="📄 Download as TXT",
                            data=result["safety_analysis"],
                            file_name=f"ingredient_analysis_{profile['name'].replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                    with col2:
                        # PDF export
                        pdf_buffer = create_pdf_report(result["safety_analysis"], profile)
                        if pdf_buffer:
                            st.download_button(
                                label="📕 Download as PDF",
                                data=pdf_buffer,
                                file_name=f"ingredient_analysis_{profile['name'].replace(' ', '_')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )

                    with col3:
                        # CSV export (if we have ingredient data)
                        if result.get("ingredient_data"):
                            csv_data = create_csv_export(result["ingredient_data"])
                            if csv_data:
                                st.download_button(
                                    label="📊 Download as CSV",
                                    data=csv_data,
                                    file_name=f"ingredients_{profile['name'].replace(' ', '_')}.csv",
                                    mime="text/csv",
                                    use_container_width=True
                                )

                    # ==========================================
                    # WORKFLOW STATS
                    # ==========================================

                    with st.expander("🔍 Analysis Details"):
                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            st.metric("Research Attempts", result.get("research_attempts", 0))
                        with col2:
                            st.metric("Analysis Attempts", result.get("analysis_attempts", 0))
                        with col3:
                            st.metric("Critic Approved", "✅" if result.get("critic_approved") else "❌")
                        with col4:
                            confidence = result.get("research_confidence", 0.0)
                            st.metric("Research Confidence", f"{confidence:.0%}")

                else:
                    st.error("❌ Analysis could not be completed. Please try again.")

                    if result.get("critic_feedback"):
                        st.warning(f"Feedback: {result['critic_feedback']}")

            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)

    # ==========================================
    # FOOTER
    # ==========================================

    st.divider()

    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.85em; padding: 2rem 0;'>
        🤖 Powered by <b>Gemini 2.0 Flash</b> | Built with <b>LangGraph</b> | Data from <b>Qdrant Vector DB</b><br>
        Multi-Agent System: Supervisor → Research → Analysis → Critic<br><br>
        <i>🔥 {count} ingredients checked in the last 24 hours</i>
    </div>
    """.format(count="405K"), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
