"""
Pydantic models for The Grid API request/response schemas.
"""

from typing import List, Dict, Union, Optional
from pydantic import BaseModel


class CustomAgent(BaseModel):
    """Custom agent definition."""
    name: str
    company: str
    role: str
    objective: str


class ConversationRequest(BaseModel):
    """Request to create a new conversation."""
    scenario: str
    client: str = "Toyota"
    num_agents: int = 2
    max_turns: int = 5


class ConversationResponse(BaseModel):
    """Response with conversation ID."""
    conversation_id: str


class AssistantChatRequest(BaseModel):
    """Request to chat with Grid assistant."""
    message: str
    history: List[Dict[str, str]] = []


class ScenarioStartRequest(BaseModel):
    """Request to start a scenario with selected agents."""
    scenario: str
    client: str
    agents: List[Union[str, Dict[str, str]]]  # Agent names from library OR custom agent definitions
    max_turns: int = 5
