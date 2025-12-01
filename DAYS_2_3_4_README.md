# AishIngAnalyzer - Days 2, 3, 4 Implementation

## Multi-Agent Cosmetic Ingredient Safety Analyzer

This is the complete implementation of Days 2, 3, and 4 of the AishIngAnalyzer capstone project, featuring a multi-agent AI system powered by Gemini 2.0 Flash, LangGraph, and Qdrant vector database.

---

## Architecture Overview

### Day 2: Agent Architecture (Supervisor + Research)
- **Supervisor Agent**: Central orchestrator with conditional routing logic
- **Research Agent**: Gathers ingredient data from Qdrant vector database
- **State Management**: TypedDict-based state flow through workflow
- **Retry Logic**: Maximum 2 attempts per agent with feedback loop

### Day 3: Analysis + Critic (Full 4-Agent Workflow)
- **Analysis Agent**: Generates personalized safety analysis adapted to user profile
- **Critic Agent**: Multi-gate validation system (completeness, allergen match, consistency, tone)
- **FastMCP Tools**: Custom tools for ingredient lookup, safety scoring, allergen matching
- **Complete Workflow**: Supervisor → Research → Analysis → Critic → END

### Day 4: Memory + Observability + UI
- **Streamlit UI**: User-friendly web interface
- **Session Tracking**: Session IDs for analysis history
- **Workflow Stats**: Research attempts, analysis attempts, critic approval status
- **Download Reports**: Export safety analysis as text files

---

## File Structure

```
AishIngAnalyzer/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── state.py              # State management (TypedDict)
│   │   ├── supervisor.py         # Supervisor Agent (routing logic)
│   │   ├── research_agent.py     # Research Agent (data gathering)
│   │   ├── analysis_agent.py     # Analysis Agent (personalized reports)
│   │   ├── critic_agent.py       # Critic Agent (quality validation)
│   │   └── workflow.py           # LangGraph workflow orchestration
│   ├── tools/
│   │   ├── __init__.py
│   │   └── mcp_tools.py          # FastMCP custom tools
│   └── ui/
│       └── streamlit_app.py      # Streamlit web interface
├── scripts/
│   ├── run_day2_test.py          # Test Day 2 (Supervisor + Research)
│   ├── run_day3_test.py          # Test Day 3 (Full 4-agent workflow)
│   └── run_day4_test.py          # Test Day 4 (Complete system with observability)
├── data/
│   └── processed/
│       └── ingredients_final.json # Ingredient database (77 ingredients)
└── requirements.txt              # Python dependencies
```

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key dependencies:**
- `langgraph==0.0.28` - Multi-agent workflow orchestration
- `google-generativeai==0.3.2` - Gemini 2.0 Flash API
- `qdrant-client==1.7.3` - Vector database client
- `sentence-transformers==2.2.2` - Embeddings (all-MiniLM-L6-v2)
- `streamlit==1.29.0` - Web UI framework
- `langsmith==0.0.77` - Observability (optional)

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
# Gemini API
GOOGLE_API_KEY=your_gemini_api_key_here

# Qdrant Vector Database
QDRANT_URL=your_qdrant_url_here
QDRANT_API_KEY=your_qdrant_api_key_here

# LangSmith (optional - for observability)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=AishIngAnalyzer
```

### 3. Run Tests

**Day 2 Test (Supervisor + Research):**
```bash
python scripts/run_day2_test.py
```

**Day 3 Test (Full 4-Agent Workflow):**
```bash
python scripts/run_day3_test.py
```

**Day 4 Test (Complete System with Observability):**
```bash
python scripts/run_day4_test.py
```

### 4. Launch Streamlit UI

```bash
streamlit run src/ui/streamlit_app.py
```

Then open http://localhost:8501 in your browser.

---

## How It Works

### Workflow Flow

```
User Input
    ↓
Supervisor Agent (routing decision)
    ↓
Research Agent (gather ingredient data from Qdrant)
    ↓
Supervisor Agent (routing decision)
    ↓
Analysis Agent (generate personalized safety analysis)
    ↓
Supervisor Agent (routing decision)
    ↓
Critic Agent (validate quality with multi-gate system)
    ↓
Supervisor Agent (routing decision)
    ↓
END (if approved) OR Retry (if rejected, max 2 attempts)
```

### State Management

The `AnalysisState` TypedDict flows through the entire workflow:

```python
{
    # User Input
    "user_name": str,
    "skin_type": str,  # normal, sensitive, oily, dry, combination
    "allergies": List[str],
    "expertise_level": str,  # beginner, intermediate, expert
    "ingredient_names": List[str],

    # Research Phase
    "research_complete": bool,
    "ingredient_data": List[Dict],
    "research_confidence": float,

    # Analysis Phase
    "analysis_complete": bool,
    "safety_analysis": Optional[str],

    # Critic Phase
    "critic_approved": bool,
    "critic_feedback": Optional[str],

    # Retry Management
    "research_attempts": int,
    "analysis_attempts": int,
    "max_retries": int,  # Default: 2

    # Workflow Control
    "next_agent": str,  # supervisor, research, analysis, critic, END
    "workflow_complete": bool
}
```

### FastMCP Custom Tools

**Tool 1: ingredient_lookup**
- Queries Qdrant vector database using semantic search
- Returns: name, purpose, safety_score, concerns, description, confidence

**Tool 2: safety_scorer**
- Calculates personalized safety score based on:
  - Base safety score from ingredient data
  - User skin type compatibility
  - Allergen matching
- Returns: personalized_score, recommendation (SAFE/CAUTION/AVOID), reasoning

**Tool 3: allergen_matcher**
- Checks ingredient against user allergies
- Handles exact matches, partial matches, synonym matches
- Returns: is_match, matched_allergen, match_type

**Allergen Synonym Support:**
- Fragrance ↔ Parfum ↔ Perfume
- Vitamin E ↔ Tocopherol ↔ Tocopheryl Acetate
- Alcohol ↔ Alcohol Denat ↔ Ethanol
- Retinol ↔ Retinyl Palmitate ↔ Retinoic Acid ↔ Tretinoin

---

## Test Scenarios

### Day 2 Test
- **Goal**: Test Supervisor + Research agents
- **Ingredients**: Water, Niacinamide, Hyaluronic Acid, Glycerin
- **Expected**: Research agent gathers data, workflow routes correctly

### Day 3 Test
- **Goal**: Test full 4-agent workflow with allergen match
- **Ingredients**: Water, Niacinamide, Parfum (allergen), Retinol, Hyaluronic Acid, Glycerin, Alcohol Denat
- **User**: Aisha with sensitive skin, allergic to Fragrance/Parfum, intermediate expertise
- **Expected**: Critic validates allergen is flagged with ⚠️ ALLERGEN MATCH

### Day 4 Test
- **Goal**: Test complete system with multiple scenarios
- **Scenario 1**: Beginner user with simple product (no allergens)
- **Scenario 2**: Sensitive skin user with allergen match (Parfum)
- **Scenario 3**: Expert user with complex anti-aging formula
- **Expected**: All scenarios complete with session tracking and stats

---

## Features

### Adaptive Analysis by Expertise Level

**Beginner:**
- Simple, clear language
- Avoids jargon
- Focuses on safety basics

**Intermediate:**
- Moderate technical detail
- Explains mechanisms
- Provides context

**Expert:**
- Technical terminology
- Research references
- Detailed chemical analysis

### Skin Type Compatibility

**Sensitive Skin:**
- Higher concern for irritation/allergic ingredients
- +2 safety score for sensitizing ingredients

**Oily Skin:**
- Flags comedogenic ingredients
- +1 safety score for pore-clogging ingredients

**Dry/Normal/Combination:**
- Standard safety analysis

### Critic Multi-Gate Validation

**Gate 1: Completeness Check**
- Ensures ALL ingredients are addressed
- Lists any missing ingredients

**Gate 2: Allergen Match Check**
- Verifies ALL user allergens are flagged with ⚠️
- Lists any missing allergen flags

**Gate 3: Consistency Check**
- Validates safety scores match concern descriptions
- Lists any inconsistencies

**Gate 4: Tone Appropriateness Check**
- Ensures analysis matches user's expertise level
- Lists any tone issues

**Decision:** APPROVE or REJECT with specific feedback

---

## Current Limitations

1. **Ingredient Database**: Currently contains 77 ingredients (planned: 400+)
2. **Tool Placeholders**: Research agent uses placeholder data (will connect to Qdrant in production)
3. **Memory**: Redis session management not yet implemented
4. **Observability**: LangSmith tracing configured but optional

---

## Next Steps

1. **Scale Database**: Increase ingredient database to 400+ entries
2. **Connect Tools**: Integrate Research agent with actual Qdrant queries
3. **Add Redis**: Implement session management for user profile persistence
4. **Deploy**: Host Streamlit app on cloud platform
5. **Evaluation**: Run RAGAS evaluation on analysis quality

---

## Tech Stack

- **LLM**: Gemini 2.0 Flash (google-generativeai)
- **Framework**: LangGraph (multi-agent orchestration)
- **Vector DB**: Qdrant Cloud
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Tools**: FastMCP custom tools
- **UI**: Streamlit
- **Memory**: Redis (planned)
- **Observability**: LangSmith (optional)

---

## Contact

For questions or issues, refer to the project documentation or contact the development team.

**Project**: AishIngAnalyzer Capstone
**Focus**: Multi-Agent AI for Cosmetic Ingredient Safety Analysis
**Powered by**: Gemini 2.0 Flash | LangGraph | Qdrant Vector DB
