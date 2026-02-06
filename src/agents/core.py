"""
Agent core classes for multi-agent conversations.

This module re-exports classes from base.py and orchestrator.py for backwards compatibility.
Prefer importing from those modules directly in new code.
"""

# Re-export for backwards compatibility
from .base import Agent, HumanAgent
from .orchestrator import MultiAgentOrchestrator

__all__ = ['Agent', 'HumanAgent', 'MultiAgentOrchestrator']
