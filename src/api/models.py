"""
Pydantic models for Callisto API request/response schemas.
"""

from pydantic import BaseModel


class ConversationRequest(BaseModel):
    """Request to create a new conversation."""
    scenario: str
    client: str = "Toyota"
    num_agents: int = 2
    max_turns: int = 5


class ConversationResponse(BaseModel):
    """Response with conversation ID."""
    conversation_id: str
