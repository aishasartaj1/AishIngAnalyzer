# AishIngAnalyzer MVP =,

**Multi-Agent Cosmetic Ingredient Safety Analysis System**

A production-ready AI-powered application that analyzes cosmetic ingredients using a sophisticated multi-agent architecture powered by Google's Gemini 2.0 Flash and LangGraph.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29.0-red.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-0.0.28-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## < Features

### Core Functionality
- **> Multi-Agent Analysis**: 4 specialized AI agents (Supervisor, Research, Analysis, Critic) working collaboratively
- **=, Personalized Safety Reports**: Tailored analysis based on skin type, allergies, and expertise level
- **=� Dual Data Sources**: Qdrant vector database (64 ingredients) + Tavily web search fallback
- ** Quality Assurance**: 5-gate validation system with up to 5 retry attempts
- **=� Persistent Memory**: Redis-powered long-term storage for user profiles and analysis history
- **=� Observability**: Built-in metrics tracking + LangSmith integration for developers

### User Experience
- **= Secure Authentication**: Email/password login with bcrypt hashing
- **=� Table Format**: Clean, scannable ingredient analysis tables
- **=� Multi-Format Export**: Download reports as TXT, PDF, or CSV
- **=� Analysis History**: Access past analyses from any session
- **<� Adaptive Tone**: Beginner, intermediate, or expert-level explanations

---

## <� Architecture

### 5-Layer System

```

