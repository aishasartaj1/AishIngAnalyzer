"""
LAYER 4: Session Management (Short-term + Long-term Memory)
Manages user sessions with optional Redis persistence
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid


class SessionManager:
    """
    Session Manager for Short-term and Long-term Memory

    Manages active user sessions in-memory with optional Redis persistence.

    Short-term (in-memory):
    - Current session state
    - Conversation history for active session
    - Temporary analysis data

    Long-term (Redis, optional):
    - User profiles across sessions
    - Complete analysis history
    - User preferences

    If Redis is available, automatically syncs to long-term storage.
    If Redis is unavailable, falls back to in-memory only.
    """

    def __init__(self, redis_client=None, use_redis: bool = True):
        """
        Initialize session manager

        Args:
            redis_client: Optional RedisClient instance
            use_redis: Whether to use Redis for long-term storage
        """
        self.sessions: Dict[str, Dict] = {}  # session_id -> session_data
        self.user_sessions: Dict[str, str] = {}  # user_name -> session_id

        # Redis integration (optional)
        self.redis_client = redis_client
        self.use_redis = use_redis

        if self.use_redis and self.redis_client is None:
            # Try to auto-initialize Redis
            try:
                from .redis_client import get_redis_client
                self.redis_client = get_redis_client()
            except Exception as e:
                print(f"⚠️ Could not initialize Redis: {e}")
                print("📌 Running in memory-only mode")
                self.use_redis = False

    def get_or_create_session(self, user_name: str) -> str:
        """
        Get existing session or create new one for user

        Args:
            user_name: User's name

        Returns:
            session_id: Unique session identifier
        """
        # Check if user has active session
        if user_name in self.user_sessions:
            session_id = self.user_sessions[user_name]

            # Check if session is still active (within last hour)
            if self._is_session_active(session_id):
                return session_id

        # Create new session
        session_id = str(uuid.uuid4())
        self.user_sessions[user_name] = session_id

        # Initialize session data
        self.sessions[session_id] = {
            "session_id": session_id,
            "user_name": user_name,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "conversation_history": [],
            "analysis_history": [],
            "user_profile": {}
        }

        return session_id

    def _is_session_active(self, session_id: str) -> bool:
        """
        Check if session is still active (within last hour)

        Args:
            session_id: Session identifier

        Returns:
            bool: True if session is active
        """
        if session_id not in self.sessions:
            return False

        session = self.sessions[session_id]
        last_activity = datetime.fromisoformat(session["last_activity"])
        time_diff = datetime.utcnow() - last_activity

        # Session expires after 1 hour of inactivity
        return time_diff < timedelta(hours=1)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """
        Get session data

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)

    def update_session_activity(self, session_id: str):
        """
        Update session's last activity timestamp

        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()

    def save_user_profile(self, session_id: str, profile: Dict):
        """
        Save user profile to session (and Redis if available)

        Args:
            session_id: Session identifier
            profile: User profile data
        """
        if session_id in self.sessions:
            self.sessions[session_id]["user_profile"] = profile
            self.update_session_activity(session_id)

            # Sync to Redis (long-term)
            if self.use_redis and self.redis_client and self.redis_client.is_connected():
                user_name = self.sessions[session_id].get("user_name")
                if user_name:
                    self.redis_client.save_user_profile(user_name, profile)

    def get_user_profile(self, session_id: str) -> Optional[Dict]:
        """
        Get user profile from session

        Args:
            session_id: Session identifier

        Returns:
            User profile or None
        """
        session = self.get_session(session_id)
        if session:
            return session.get("user_profile")
        return None

    def add_to_history(self, session_id: str, analysis_result: Dict):
        """
        Add analysis result to session history (and Redis if available)

        Args:
            session_id: Session identifier
            analysis_result: Analysis workflow result
        """
        if session_id not in self.sessions:
            return

        history_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "ingredient_names": analysis_result.get("ingredient_names", []),
            "safety_analysis": analysis_result.get("safety_analysis"),
            "critic_approved": analysis_result.get("critic_approved", False),
            "research_confidence": analysis_result.get("research_confidence", 0.0)
        }

        # Add to in-memory session history
        self.sessions[session_id]["analysis_history"].append(history_entry)
        self.update_session_activity(session_id)

        # Sync to Redis (long-term)
        if self.use_redis and self.redis_client and self.redis_client.is_connected():
            user_name = self.sessions[session_id].get("user_name")
            if user_name:
                self.redis_client.add_analysis_to_history(user_name, analysis_result)

    def get_analysis_history(self, session_id: str, include_longterm: bool = True) -> List[Dict]:
        """
        Get analysis history for session

        Args:
            session_id: Session identifier
            include_longterm: Include long-term history from Redis

        Returns:
            List of analysis results (session + Redis if available)
        """
        session = self.get_session(session_id)
        if not session:
            return []

        # Get current session history
        session_history = session.get("analysis_history", [])

        # Add long-term history from Redis
        if include_longterm and self.use_redis and self.redis_client and self.redis_client.is_connected():
            user_name = session.get("user_name")
            if user_name:
                redis_history = self.redis_client.get_analysis_history(user_name, limit=50)
                # Merge and deduplicate
                all_history = session_history + redis_history
                # Remove duplicates based on timestamp
                seen = set()
                unique_history = []
                for entry in all_history:
                    ts = entry.get("timestamp")
                    if ts not in seen:
                        seen.add(ts)
                        unique_history.append(entry)
                return sorted(unique_history, key=lambda x: x.get("timestamp", ""), reverse=True)

        return session_history

    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for session

        Args:
            session_id: Session identifier

        Returns:
            List of conversation messages
        """
        session = self.get_session(session_id)
        if session:
            return session.get("conversation_history", [])
        return []

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):
        """
        Add message to conversation history

        Args:
            session_id: Session identifier
            role: 'user' or 'assistant'
            content: Message content
        """
        if session_id not in self.sessions:
            return

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.sessions[session_id]["conversation_history"].append(message)
        self.update_session_activity(session_id)

    def clear_session(self, session_id: str):
        """
        Clear session data (end session)

        Args:
            session_id: Session identifier
        """
        if session_id in self.sessions:
            # Remove from user mapping
            user_name = self.sessions[session_id].get("user_name")
            if user_name in self.user_sessions:
                del self.user_sessions[user_name]

            # Remove session
            del self.sessions[session_id]

    def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        active_count = 0
        for session_id in list(self.sessions.keys()):
            if self._is_session_active(session_id):
                active_count += 1
            else:
                # Clean up expired session
                self.clear_session(session_id)
        return active_count

    def __repr__(self) -> str:
        """String representation"""
        active_sessions = self.get_active_sessions_count()
        return f"<SessionManager: {active_sessions} active sessions>"


# Singleton instance for global access
_session_manager = None


def get_session_manager() -> SessionManager:
    """
    Get global session manager instance

    Returns:
        SessionManager singleton
    """
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
