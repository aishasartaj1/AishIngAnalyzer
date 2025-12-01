"""
LAYER 4: Redis Client for Long-term Memory
Persistent storage for user profiles and analysis history across sessions
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import redis
from redis.exceptions import RedisError


class RedisClient:
    """
    Redis Client for Long-term Memory

    Stores:
    - User profiles (persists across sessions)
    - Analysis history (unlimited retention)
    - User preferences
    - Past queries and results

    Redis Keys Structure:
    - user:{user_name}:profile - User profile data
    - user:{user_name}:history - Analysis history (list)
    - user:{user_name}:preferences - User preferences
    - session:{session_id} - Temporary session data (TTL: 1 hour)
    """

    def __init__(
        self,
        host: str = None,
        port: int = None,
        password: str = None,
        db: int = 0,
        decode_responses: bool = True,
        redis_url: str = None
    ):
        """
        Initialize Redis client

        Args:
            host: Redis host (defaults to env REDIS_HOST)
            port: Redis port (defaults to env REDIS_PORT or 6379)
            password: Redis password (defaults to env REDIS_PASSWORD)
            db: Redis database number
            decode_responses: Decode responses to strings
            redis_url: Redis URL (defaults to env REDIS_URL)
                      Format: redis://user:password@host:port/db
        """
        # Check if REDIS_URL is provided (takes priority)
        redis_url = redis_url or os.getenv("REDIS_URL")

        if redis_url:
            # Use REDIS_URL connection string
            try:
                self.client = redis.from_url(
                    redis_url,
                    decode_responses=decode_responses,
                    socket_connect_timeout=5
                )
                # Test connection
                self.client.ping()
                # Extract host for display
                self.host = redis_url.split("@")[-1].split(":")[0] if "@" in redis_url else "Redis Cloud"
                self.port = None
                print(f"[OK] Redis connected via URL: {self.host}")
            except RedisError as e:
                print(f"[WARNING] Redis connection failed: {e}")
                print("[INFO] Long-term memory disabled. Using in-memory only.")
                self.client = None
        else:
            # Use individual connection parameters
            self.host = host or os.getenv("REDIS_HOST", "localhost")
            self.port = port or int(os.getenv("REDIS_PORT", 6379))
            self.password = password or os.getenv("REDIS_PASSWORD")
            self.db = db

            try:
                self.client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    db=self.db,
                    decode_responses=decode_responses,
                    socket_connect_timeout=5
                )
                # Test connection
                self.client.ping()
                print(f"[OK] Redis connected: {self.host}:{self.port}")
            except RedisError as e:
                print(f"[WARNING] Redis connection failed: {e}")
                print("[INFO] Long-term memory disabled. Using in-memory only.")
                self.client = None

    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        if self.client is None:
            return False
        try:
            return self.client.ping()
        except RedisError:
            return False

    # ==========================================
    # USER PROFILE METHODS
    # ==========================================

    def save_user_profile(self, user_name: str, profile: Dict):
        """
        Save user profile (long-term storage)

        Args:
            user_name: User's name
            profile: Profile data dict
        """
        if not self.is_connected():
            return

        try:
            key = f"user:{user_name}:profile"
            profile_json = json.dumps(profile)
            self.client.set(key, profile_json)
            print(f"[OK] Saved profile for {user_name}")
        except Exception as e:
            print(f"[ERROR] Error saving profile: {e}")

    def get_user_profile(self, user_name: str) -> Optional[Dict]:
        """
        Get user profile

        Args:
            user_name: User's name

        Returns:
            Profile dict or None
        """
        if not self.is_connected():
            return None

        try:
            key = f"user:{user_name}:profile"
            profile_json = self.client.get(key)
            if profile_json:
                return json.loads(profile_json)
            return None
        except Exception as e:
            print(f"[ERROR] Error getting profile: {e}")
            return None

    def delete_user_profile(self, user_name: str):
        """Delete user profile"""
        if not self.is_connected():
            return

        try:
            key = f"user:{user_name}:profile"
            self.client.delete(key)
            print(f"[OK] Deleted profile for {user_name}")
        except Exception as e:
            print(f"[ERROR] Error deleting profile: {e}")

    # ==========================================
    # ANALYSIS HISTORY METHODS
    # ==========================================

    def add_analysis_to_history(
        self,
        user_name: str,
        analysis_result: Dict
    ):
        """
        Add analysis to user's history (long-term)

        Args:
            user_name: User's name
            analysis_result: Analysis workflow result
        """
        if not self.is_connected():
            return

        try:
            key = f"user:{user_name}:history"

            # Create history entry
            history_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "session_id": analysis_result.get("session_id"),
                "ingredient_names": analysis_result.get("ingredient_names", []),
                "safety_analysis": analysis_result.get("safety_analysis"),
                "critic_approved": analysis_result.get("critic_approved", False),
                "research_confidence": analysis_result.get("research_confidence", 0.0)
            }

            # Push to list (most recent first)
            self.client.lpush(key, json.dumps(history_entry))

            # Trim to last 100 analyses (optional limit)
            self.client.ltrim(key, 0, 99)

            print(f"[OK] Added analysis to history for {user_name}")
        except Exception as e:
            print(f"[ERROR] Error adding to history: {e}")

    def get_analysis_history(
        self,
        user_name: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get user's analysis history

        Args:
            user_name: User's name
            limit: Max number of entries to return

        Returns:
            List of analysis results (most recent first)
        """
        if not self.is_connected():
            return []

        try:
            key = f"user:{user_name}:history"
            # Get most recent entries
            entries = self.client.lrange(key, 0, limit - 1)

            history = []
            for entry_json in entries:
                try:
                    history.append(json.loads(entry_json))
                except json.JSONDecodeError:
                    continue

            return history
        except Exception as e:
            print(f"[ERROR] Error getting history: {e}")
            return []

    def get_analysis_count(self, user_name: str) -> int:
        """Get total number of analyses for user"""
        if not self.is_connected():
            return 0

        try:
            key = f"user:{user_name}:history"
            return self.client.llen(key)
        except Exception as e:
            print(f"[ERROR] Error getting count: {e}")
            return 0

    def clear_analysis_history(self, user_name: str):
        """Clear user's analysis history"""
        if not self.is_connected():
            return

        try:
            key = f"user:{user_name}:history"
            self.client.delete(key)
            print(f"[OK] Cleared history for {user_name}")
        except Exception as e:
            print(f"[ERROR] Error clearing history: {e}")

    # ==========================================
    # USER PREFERENCES METHODS
    # ==========================================

    def save_user_preferences(self, user_name: str, preferences: Dict):
        """
        Save user preferences

        Args:
            user_name: User's name
            preferences: Preferences dict
        """
        if not self.is_connected():
            return

        try:
            key = f"user:{user_name}:preferences"
            prefs_json = json.dumps(preferences)
            self.client.set(key, prefs_json)
            print(f"[OK] Saved preferences for {user_name}")
        except Exception as e:
            print(f"[ERROR] Error saving preferences: {e}")

    def get_user_preferences(self, user_name: str) -> Optional[Dict]:
        """Get user preferences"""
        if not self.is_connected():
            return None

        try:
            key = f"user:{user_name}:preferences"
            prefs_json = self.client.get(key)
            if prefs_json:
                return json.loads(prefs_json)
            return None
        except Exception as e:
            print(f"[ERROR] Error getting preferences: {e}")
            return None

    # ==========================================
    # SESSION CACHE METHODS (short-lived)
    # ==========================================

    def cache_session(
        self,
        session_id: str,
        session_data: Dict,
        ttl: int = 3600  # 1 hour
    ):
        """
        Cache session data temporarily

        Args:
            session_id: Session identifier
            session_data: Session data dict
            ttl: Time-to-live in seconds (default: 1 hour)
        """
        if not self.is_connected():
            return

        try:
            key = f"session:{session_id}"
            data_json = json.dumps(session_data)
            self.client.setex(key, ttl, data_json)
        except Exception as e:
            print(f"[ERROR] Error caching session: {e}")

    def get_cached_session(self, session_id: str) -> Optional[Dict]:
        """Get cached session data"""
        if not self.is_connected():
            return None

        try:
            key = f"session:{session_id}"
            data_json = self.client.get(key)
            if data_json:
                return json.loads(data_json)
            return None
        except Exception as e:
            print(f"[ERROR] Error getting cached session: {e}")
            return None

    # ==========================================
    # ANALYTICS METHODS
    # ==========================================

    def get_all_users(self) -> List[str]:
        """Get list of all users with profiles"""
        if not self.is_connected():
            return []

        try:
            keys = self.client.keys("user:*:profile")
            # Extract user names from keys
            users = [key.split(":")[1] for key in keys]
            return users
        except Exception as e:
            print(f"[ERROR] Error getting users: {e}")
            return []

    def get_total_analyses_count(self) -> int:
        """Get total number of analyses across all users"""
        if not self.is_connected():
            return 0

        try:
            users = self.get_all_users()
            total = sum(self.get_analysis_count(user) for user in users)
            return total
        except Exception as e:
            print(f"[ERROR] Error getting total count: {e}")
            return 0

    # ==========================================
    # UTILITY METHODS
    # ==========================================

    def flush_all(self):
        """⚠️ WARNING: Delete all data in Redis database"""
        if not self.is_connected():
            return

        try:
            self.client.flushdb()
            print("[WARNING] All Redis data flushed!")
        except Exception as e:
            print(f"[ERROR] Error flushing data: {e}")

    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            print("[OK] Redis connection closed")

    def __repr__(self) -> str:
        """String representation"""
        status = "connected" if self.is_connected() else "disconnected"
        return f"<RedisClient: {status} @ {self.host}:{self.port}>"


# Singleton instance
_redis_client = None


def get_redis_client() -> RedisClient:
    """
    Get global Redis client instance

    Returns:
        RedisClient singleton
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
