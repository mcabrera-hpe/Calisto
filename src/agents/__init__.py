"""
Agent classes for multi-agent conversations.

Public API: Agent, HumanAgent, MultiAgentOrchestrator
"""

from .base import Agent, HumanAgent
from .orchestrator import MultiAgentOrchestrator

__all__ = ['Agent', 'HumanAgent', 'MultiAgentOrchestrator']
