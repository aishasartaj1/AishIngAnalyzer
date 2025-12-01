"""
LAYER 4: Conversation Memory (Short-term Memory)
Manages conversation history and context for LangGraph workflow
"""

from typing import List, Dict, Optional
from datetime import datetime


class ConversationMemory:
    """
    Conversation Memory for LangGraph State

    Manages:
    - Message history (user/assistant exchanges)
    - Context tracking (what was discussed)
    - Follow-up question handling
    - Multi-turn conversation support

    This is SHORT-TERM MEMORY that lives within the LangGraph state.
    """

    def __init__(self, max_messages: int = 50):
        """
        Initialize conversation memory

        Args:
            max_messages: Maximum messages to keep in memory
        """
        self.messages: List[Dict] = []
        self.max_messages = max_messages

    def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add message to conversation history

        Args:
            role: 'user', 'assistant', or 'system'
            content: Message content
            metadata: Optional metadata (agent_name, tool_calls, etc.)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        self.messages.append(message)

        # Trim if exceeded max
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def add_user_message(self, content: str):
        """Add user message"""
        self.add_message(role="user", content=content)

    def add_assistant_message(
        self,
        content: str,
        agent_name: Optional[str] = None
    ):
        """
        Add assistant message

        Args:
            content: Response content
            agent_name: Name of agent that generated response
        """
        metadata = {}
        if agent_name:
            metadata["agent_name"] = agent_name

        self.add_message(
            role="assistant",
            content=content,
            metadata=metadata
        )

    def add_system_message(self, content: str):
        """Add system message"""
        self.add_message(role="system", content=content)

    def get_messages(self) -> List[Dict]:
        """Get all messages"""
        return self.messages.copy()

    def get_recent_messages(self, n: int = 10) -> List[Dict]:
        """
        Get recent N messages

        Args:
            n: Number of recent messages to retrieve

        Returns:
            List of recent messages
        """
        return self.messages[-n:]

    def get_messages_by_role(self, role: str) -> List[Dict]:
        """
        Get messages filtered by role

        Args:
            role: 'user', 'assistant', or 'system'

        Returns:
            List of messages with specified role
        """
        return [msg for msg in self.messages if msg["role"] == role]

    def get_context_summary(self) -> str:
        """
        Generate a summary of conversation context

        Returns:
            String summary of key discussion points
        """
        if not self.messages:
            return "No conversation history"

        # Extract key information
        user_messages = self.get_messages_by_role("user")
        assistant_messages = self.get_messages_by_role("assistant")

        summary_parts = [
            f"Messages: {len(self.messages)} total",
            f"User queries: {len(user_messages)}",
            f"Assistant responses: {len(assistant_messages)}"
        ]

        # Add topics discussed (from user messages)
        if user_messages:
            latest_query = user_messages[-1]["content"][:100]
            summary_parts.append(f"Latest query: {latest_query}...")

        return " | ".join(summary_parts)

    def format_for_prompt(
        self,
        include_system: bool = True,
        max_messages: int = 10
    ) -> str:
        """
        Format conversation history for LLM prompt

        Args:
            include_system: Whether to include system messages
            max_messages: Maximum messages to include

        Returns:
            Formatted string for prompt injection
        """
        recent_messages = self.get_recent_messages(max_messages)

        formatted_lines = []
        for msg in recent_messages:
            role = msg["role"]

            # Skip system messages if not included
            if role == "system" and not include_system:
                continue

            content = msg["content"]
            timestamp = msg["timestamp"]

            # Format differently based on role
            if role == "user":
                formatted_lines.append(f"USER [{timestamp}]: {content}")
            elif role == "assistant":
                agent = msg.get("metadata", {}).get("agent_name", "Assistant")
                formatted_lines.append(f"{agent.upper()} [{timestamp}]: {content}")
            elif role == "system":
                formatted_lines.append(f"SYSTEM: {content}")

        return "\n\n".join(formatted_lines)

    def clear(self):
        """Clear all messages"""
        self.messages = []

    def to_dict(self) -> Dict:
        """
        Convert to dictionary for serialization

        Returns:
            Dictionary representation
        """
        return {
            "messages": self.messages,
            "max_messages": self.max_messages,
            "message_count": len(self.messages)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ConversationMemory':
        """
        Create from dictionary

        Args:
            data: Dictionary representation

        Returns:
            ConversationMemory instance
        """
        memory = cls(max_messages=data.get("max_messages", 50))
        memory.messages = data.get("messages", [])
        return memory

    def __len__(self) -> int:
        """Get message count"""
        return len(self.messages)

    def __repr__(self) -> str:
        """String representation"""
        return f"<ConversationMemory: {len(self.messages)} messages>"


def create_conversation_memory_from_state(state: Dict) -> ConversationMemory:
    """
    Create ConversationMemory from LangGraph state

    Args:
        state: LangGraph state dictionary

    Returns:
        ConversationMemory instance populated from state
    """
    memory = ConversationMemory()

    # Extract messages from state
    if "messages" in state:
        messages = state["messages"]
        for msg in messages:
            if isinstance(msg, dict):
                memory.messages.append(msg)

    return memory


def inject_conversation_context(
    state: Dict,
    prompt: str,
    max_context_messages: int = 5
) -> str:
    """
    Inject conversation context into prompt

    Useful for giving agents access to conversation history.

    Args:
        state: LangGraph state
        prompt: Original prompt
        max_context_messages: Max messages to include as context

    Returns:
        Enhanced prompt with conversation context
    """
    memory = create_conversation_memory_from_state(state)

    if len(memory) == 0:
        # No conversation history, return original prompt
        return prompt

    # Add conversation context
    context = memory.format_for_prompt(
        include_system=False,
        max_messages=max_context_messages
    )

    enhanced_prompt = f"""CONVERSATION HISTORY:
{context}

CURRENT REQUEST:
{prompt}
"""

    return enhanced_prompt
