"""
LAYER 4: State Management for LangGraph Multi-Agent Workflow
Defines the state schema that flows through the entire system
"""

from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph import add_messages


class AnalysisState(TypedDict):
    """
    State object that flows through the multi-agent workflow

    This is the SHORT-TERM MEMORY that persists during a single analysis session.
    It tracks all intermediate states, agent decisions, and workflow progress.

    Tracks:
    - User profile and preferences
    - Ingredient list to analyze
    - Research data gathered
    - Analysis results
    - Validation status
    - Retry counts
    - Conversation history
    """

    # ==========================================
    # USER INPUT (from UI Layer)
    # ==========================================
    user_name: str
    skin_type: str  # normal, sensitive, oily, dry, combination
    allergies: List[str]
    expertise_level: str  # beginner, intermediate, expert
    ingredient_names: List[str]

    # ==========================================
    # CONVERSATION MEMORY (short-term)
    # ==========================================
    messages: Annotated[List[Dict], add_messages]
    # Format: [{"role": "user/assistant", "content": str, "timestamp": str}]

    session_id: str  # Unique session identifier

    # ==========================================
    # RESEARCH PHASE
    # ==========================================
    research_complete: bool
    ingredient_data: List[Dict]  # Raw data from tools
    # Format: [{"name": str, "purpose": str, "safety_score": int,
    #          "concerns": List[str], "confidence": float, "source": str}]
    research_confidence: float  # Overall confidence score (0.0-1.0)

    # ==========================================
    # ANALYSIS PHASE
    # ==========================================
    analysis_complete: bool
    safety_analysis: Optional[str]  # Final formatted analysis report

    # ==========================================
    # CRITIC PHASE
    # ==========================================
    critic_approved: bool
    critic_feedback: Optional[str]

    # ==========================================
    # RETRY MANAGEMENT
    # ==========================================
    research_attempts: int
    analysis_attempts: int
    max_retries: int  # Default: 2

    # ==========================================
    # WORKFLOW CONTROL
    # ==========================================
    next_agent: str  # supervisor, research, analysis, critic, END
    workflow_complete: bool

    # ==========================================
    # OBSERVABILITY METRICS
    # ==========================================
    analysis_start_time: Optional[str]  # ISO timestamp when analysis started
    analysis_end_time: Optional[str]  # ISO timestamp when analysis completed
    qdrant_hits: int  # Number of ingredients found in Qdrant
    tavily_hits: int  # Number of ingredients requiring Tavily fallback
    total_critic_rejections: int  # Number of times critic rejected analysis

    # ==========================================
    # METADATA (for memory layer)
    # ==========================================
    created_at: Optional[str]  # ISO timestamp
    updated_at: Optional[str]  # ISO timestamp


def create_initial_state(
    ingredient_names: List[str],
    user_name: str = "User",
    skin_type: str = "normal",
    allergies: List[str] = None,
    expertise_level: str = "beginner",
    session_id: str = None
) -> AnalysisState:
    """
    Create initial state for a new analysis workflow

    This initializes the SHORT-TERM MEMORY for a single session.

    Args:
        ingredient_names: List of ingredient names to analyze
        user_name: User's name
        skin_type: User's skin type
        allergies: List of allergens
        expertise_level: User's expertise level
        session_id: Unique session identifier

    Returns:
        Initial AnalysisState with default values
    """
    from datetime import datetime
    import uuid

    now = datetime.now().isoformat()  # Use local time instead of UTC

    return {
        # User input
        "user_name": user_name,
        "skin_type": skin_type,
        "allergies": allergies or [],
        "expertise_level": expertise_level,
        "ingredient_names": ingredient_names,

        # Conversation memory
        "messages": [],
        "session_id": session_id or str(uuid.uuid4()),

        # Research phase
        "research_complete": False,
        "ingredient_data": [],
        "research_confidence": 0.0,

        # Analysis phase
        "analysis_complete": False,
        "safety_analysis": None,

        # Critic phase
        "critic_approved": False,
        "critic_feedback": None,

        # Retry management
        "research_attempts": 0,
        "analysis_attempts": 0,
        "max_retries": 2,

        # Workflow control
        "next_agent": "research",
        "workflow_complete": False,

        # Observability metrics
        "analysis_start_time": now,
        "analysis_end_time": None,
        "qdrant_hits": 0,
        "tavily_hits": 0,
        "total_critic_rejections": 0,

        # Metadata
        "created_at": now,
        "updated_at": now
    }
