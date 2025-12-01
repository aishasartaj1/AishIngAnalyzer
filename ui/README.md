# AishIngAnalyzer - User Interface Layer

## Streamlit Web Application

Complete web interface for cosmetic ingredient safety analysis with personalized recommendations.

---

## Features

### ✅ Comprehensive User Profile
- **Basic Info**: Name, Age Group, Sex, Country/Region
- **Skin Type**: Normal, Dry, Oily, Combination, Sensitive
- **Skin Concerns**: Multi-select (Acne, Sensitivity, Dryness, Anti-aging, etc.)
- **Allergies/Avoid List**: Predefined options + custom input
- **Experience Level**: Beginner, Intermediate, Advanced

### ✅ Flexible Ingredient Input
- **Paste Text**: Copy ingredient list from product label
- **Upload Photo**: OCR extraction from ingredient photos
- **Smart Parsing**: Handles comma-separated or line-separated lists

### ✅ Multi-Agent Analysis
- Real-time progress tracking
- Personalized safety analysis based on user profile
- Allergen matching with warnings
- Quality validation by Critic agent

### ✅ Export Options
- **TXT**: Plain text report
- **PDF**: Formatted report with user profile
- **CSV**: Structured ingredient data table

### ✅ Responsive UI
- Collapsible profile form (saves in session)
- Clean, modern design inspired by SkinSort
- Mobile-friendly layout

---

## Installation

### 1. Install Dependencies

```bash
pip install streamlit==1.29.0 Pillow==10.1.0 pytesseract==0.3.10 reportlab==4.0.7
```

### 2. Install Tesseract OCR (for image upload)

**Windows:**
```bash
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
# Install and add to PATH
```

**macOS:**
```bash
brew install tesseract
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

---

## Usage

### Run the Streamlit App

```bash
streamlit run ui/streamlit_app.py
```

Or from project root:
```bash
python -m streamlit run ui/streamlit_app.py
```

The app will open at: `http://localhost:8501`

---

## User Flow

### Step 1: Complete Profile (Sidebar)

1. Fill in profile form:
   - Name, Age Group, Sex, Country
   - Skin Type
   - Skin Concerns (multi-select)
   - Allergies/Avoid List (presets + custom)
   - Experience Level

2. Click **"Save Profile"**

3. Profile collapses and shows summary

### Step 2: Input Ingredients (Main Page)

**Option A: Paste Text**
1. Click "📝 Paste Ingredients" tab
2. Copy ingredient list from product
3. Paste into text area

**Option B: Upload Photo**
1. Click "📸 Upload Photo" tab
2. Upload image of ingredient list
3. Click "🔍 Extract Ingredients from Image"
4. Review extracted text in "Paste Ingredients" tab

### Step 3: Analyze

1. Click **"🔬 Analyze Now"** button
2. Watch multi-agent workflow progress:
   - Research Agent: Gathering data
   - Analysis Agent: Generating report
   - Critic Agent: Validating quality

### Step 4: Review Results

- Read **Safety Analysis** report
- Check **Allergen Warnings** (⚠️ flags)
- View **Personalized Recommendations**

### Step 5: Export (Optional)

- Download as **TXT** (plain text)
- Download as **PDF** (formatted report)
- Download as **CSV** (ingredient table)

---

## Profile Fields Reference

### Age Group
- `<18`
- `18-25`
- `26-35`
- `36-45`
- `46-55`
- `56+`

### Skin Type
- **Normal**: Balanced, not too oily or dry
- **Dry**: Flaky, tight, rough texture
- **Oily**: Shiny, enlarged pores, acne-prone
- **Combination**: Oily T-zone, dry cheeks
- **Sensitive**: Redness, irritation, reactive

### Skin Concerns
- Acne / Breakouts
- Sensitivity / Redness
- Dryness / Dehydration
- Hyperpigmentation
- Anti-aging
- Large Pores
- Eczema-prone
- None

### Preset Allergies
- Fragrance
- Essential Oils
- Alcohol
- Parabens
- Sulfates
- Silicones
- Coconut Derivatives
- Fungal Acne Triggers
- Benzoyl Peroxide
- Retinoids

### Experience Level
- **Beginner**: Simple language, no jargon
- **Intermediate**: Moderate technical detail
- **Advanced**: Technical terminology, research references

---

## Session State

The app uses Streamlit session state to persist:

- `profile_submitted`: Whether profile form is completed
- `user_profile`: Saved user profile data
- `ingredient_text`: Current ingredient input text

**To edit profile:** Click "✏️ Edit Profile" button in sidebar

---

## OCR Configuration

### Tesseract Path (if not in PATH)

Add to `streamlit_app.py`:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
```

### Improve OCR Accuracy

1. Use clear, well-lit photos
2. Crop to just ingredient list area
3. Ensure text is horizontal
4. Use high-resolution images

---

## Export Formats

### TXT Export
- Plain text analysis
- Includes all sections
- Preserves markdown formatting

### PDF Export
- Formatted with ReportLab
- Includes user profile header
- Professional layout
- Ready to print/share

### CSV Export
- Structured data table
- Columns: name, purpose, safety_score, concerns, confidence
- Compatible with Excel/Google Sheets

---

## Backend Integration

The UI connects to the multi-agent backend via:

```python
from src.agents.workflow import run_analysis

result = run_analysis(
    ingredient_names=ingredient_list,
    user_name=profile['name'],
    skin_type=profile['skin_type'],
    allergies=profile['allergies'],
    expertise_level=profile['expertise_level']
)
```

**Expected Return:**
```python
{
    "safety_analysis": str,  # Formatted analysis text
    "ingredient_data": List[Dict],  # Structured ingredient data
    "research_attempts": int,
    "analysis_attempts": int,
    "critic_approved": bool,
    "research_confidence": float
}
```

---

## Troubleshooting

### Issue: OCR not working

**Solution:**
1. Install Tesseract: `brew install tesseract` (macOS) or download Windows installer
2. Add to PATH or set path manually in code

### Issue: PDF export not working

**Solution:**
```bash
pip install reportlab==4.0.7
```

### Issue: Profile form won't collapse

**Solution:**
Clear browser cache or restart Streamlit server

### Issue: Backend import error

**Solution:**
Ensure `src/agents/workflow.py` exists and is accessible

---

## Customization

### Change Theme Colors

Edit custom CSS in `streamlit_app.py`:

```python
st.markdown("""
<style>
.main-header {
    color: #YOUR_COLOR;  /* Change header color */
}
</style>
""", unsafe_allow_html=True)
```

### Add More Preset Allergies

In the profile form, add to `allergies_preset` options:

```python
allergies_preset = st.multiselect(
    "Select common allergens",
    options=[
        "Fragrance",
        "Your Custom Option",  # Add here
        ...
    ]
)
```

---

## File Structure

```
ui/
├── streamlit_app.py    # Main Streamlit application
└── README.md           # This file
```

---

## Tech Stack

- **Streamlit** 1.29.0 - Web framework
- **Pillow** 10.1.0 - Image processing
- **pytesseract** 0.3.10 - OCR engine
- **reportlab** 4.0.7 - PDF generation
- **pandas** - CSV export

---

## Future Enhancements

- [ ] Save profile to database (Redis)
- [ ] Analysis history
- [ ] Product recommendations
- [ ] Comparison mode (multiple products)
- [ ] Mobile app version
- [ ] Multi-language support

---

## Contact

For UI-related issues, refer to project documentation or contact the development team.
