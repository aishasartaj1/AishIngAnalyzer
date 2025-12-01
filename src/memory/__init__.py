"""
LAYER 4: Memory Module
Session management, conversation memory, and Redis persistence
"""

from .session import SessionManager, get_session_manager
from .conversation import (
    ConversationMemory,
    create_conversation_memory_from_state,
    inject_conversation_context
)
from .redis_client import RedisClient, get_redis_client

__all__ = [
    # Session Management
    "SessionManager",
    "get_session_manager",

    # Conversation Memory
    "ConversationMemory",
    "create_conversation_memory_from_state",
    "inject_conversation_context",

    # Redis (Long-term)
    "RedisClient",
    "get_redis_client"
]
