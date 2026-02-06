"""
Multi-agent conversation orchestrator.

Manages round-robin turn-taking between agents.
"""

import logging
from typing import List, Dict, Optional, Generator
from datetime import datetime

from .base import HumanAgent

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Manages multi-agent conversations with round-robin turn-taking.
    
    Simple implementation: agents take turns until max_turns or conversation ends.
    """
    
    def __init__(self, agents: List, max_turns: int = 30) -> None:
        """
        Initialize orchestrator.
        
        Args:
            agents: List of Agent or HumanAgent instances
            max_turns: Maximum conversation turns
        """
        self.agents = agents
        self.max_turns = max_turns
        self.conversation_history = []
    
    def _add_initial_message(self, initial_message: Optional[str]) -> bool:
        """Add initial message to conversation history.
        
        Args:
            initial_message: Starting message content
            
        Returns:
            True if message was added, False otherwise
        """
        if not initial_message:
            return False
            
        self.conversation_history.append({
            "turn": 0,
            "agent": self.agents[0].name,
            "company": self.agents[0].company,
            "role": self.agents[0].role,
            "message": initial_message,
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    def _execute_turn(self, current_agent, turn: int) -> Optional[Dict]:
        """Execute a single conversation turn.
        
        Args:
            current_agent: Agent to generate response
            turn: Current turn number
            
        Returns:
            Message dict if successful, None if agent is human
            
        Raises:
            Exception: If agent response fails
        """
        # Skip human agents in autonomous mode
        if isinstance(current_agent, HumanAgent):
            logger.info(f"Skipping human agent: {current_agent.name}")
            return None
        
        # Generate response
        logger.info(f"Turn {turn}: {current_agent.name} is thinking...")
        
        response, generation_time = current_agent.respond(self.conversation_history)
        
        msg = {
            "turn": turn,
            "agent": current_agent.name,
            "company": current_agent.company,
            "role": current_agent.role,
            "message": response,
            "timestamp": datetime.now().isoformat(),
            "generation_time": generation_time
        }
        
        self.conversation_history.append(msg)
        logger.info(f"Turn {turn}: {current_agent.name} completed ({generation_time:.2f}s)")
        
        return msg
        
    def _should_terminate(self) -> bool:
        """
        Simple termination logic.
        
        For now, just check for deal keywords in last message.
        
        Returns:
            True if conversation should end, False otherwise
        """
        if not self.conversation_history:
            return False
        
        last_message = self.conversation_history[-1]['message'].lower()
        
        # Check for completion keywords
        completion_keywords = [
            "deal", "agreed", "agreement", "signed", "approved",
            "contract", "goodbye", "thank you for your time"
        ]
        
        if any(keyword in last_message for keyword in completion_keywords):
            logger.info(f"Detected completion keyword in: {last_message[:50]}...")
            return True
        
        return False
    
    def run(self, initial_message: Optional[str] = None) -> List[Dict]:
        """
        Run conversation between agents and return full history.
        
        Args:
            initial_message: Optional starting message
            
        Returns:
            List of message dictionaries
        """
        logger.info(f"Starting conversation with {len(self.agents)} agents")
        
        # Add initial message if provided
        self._add_initial_message(initial_message)
        
        # Round-robin conversation
        current_agent_index = 1 if initial_message else 0
        
        for turn in range(1, self.max_turns + 1):
            current_agent = self.agents[current_agent_index]
            
            try:
                msg = self._execute_turn(current_agent, turn)
                
                # Skip if human agent
                if msg is None:
                    current_agent_index = (current_agent_index + 1) % len(self.agents)
                    continue
                
            except Exception as e:
                logger.error(f"Turn {turn} failed: {e}")
                raise
            
            # Check termination
            if self._should_terminate():
                logger.info("Conversation terminated early")
                break
            
            # Next agent
            current_agent_index = (current_agent_index + 1) % len(self.agents)
        
        logger.info(f"Conversation complete: {len(self.conversation_history)} messages")
        return self.conversation_history
    
    def run_streaming(self, initial_message: Optional[str] = None) -> Generator[Dict, None, None]:
        """
        Generator that yields messages as they're created for real-time UI updates.
        
        Args:
            initial_message: Optional starting message
            
        Yields:
            Message dicts as they are generated
        """
        logger.info(f"Starting streaming conversation with {len(self.agents)} agents")
        
        # Add and yield initial message if provided
        if self._add_initial_message(initial_message):
            yield self.conversation_history[0]
        
        # Round-robin conversation
        current_agent_index = 1 if initial_message else 0
        
        for turn in range(1, self.max_turns + 1):
            current_agent = self.agents[current_agent_index]
            
            try:
                msg = self._execute_turn(current_agent, turn)
                
                # Skip if human agent
                if msg is None:
                    current_agent_index = (current_agent_index + 1) % len(self.agents)
                    continue
                
                yield msg
                
            except Exception as e:
                logger.error(f"Turn {turn} failed: {e}")
                raise
            
            # Check termination
            if self._should_terminate():
                logger.info("Conversation terminated early")
                break
            
            # Next agent
            current_agent_index = (current_agent_index + 1) % len(self.agents)
        
        logger.info(f"Conversation complete: {len(self.conversation_history)} messages")
