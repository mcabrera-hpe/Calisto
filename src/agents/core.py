"""
Agent core classes for multi-agent conversations.

Simple, minimal implementation focused on getting agents talking.
"""

import os
import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Environment variables
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")


class Agent:
    """
    Simple AI agent that responds using Ollama LLM.
    
    No RAG, no complex tools - just basic conversation.
    """
    
    def __init__(
        self,
        name: str,
        company: str,
        role: str,
        objective: str,
        model: str = DEFAULT_MODEL
    ):
        self.name = name
        self.company = company
        self.role = role
        self.objective = objective
        self.model = model
        
    def _build_system_prompt(self) -> str:
        """Generate system prompt for this agent."""
        return f"""You are {self.name}, a {self.role} at {self.company}.

Your objective: {self.objective}

Guidelines:
- Stay in character as {self.name}
- Be professional and realistic
- Keep responses concise (2-3 sentences)
- Focus on your objective
- Respond naturally as if in a business conversation"""

    def respond(self, conversation_history: List[Dict]) -> tuple[str, float]:
        """
        Generate a response based on conversation history.
        
        Args:
            conversation_history: List of messages with 'agent' and 'message' keys
            
        Returns:
            Tuple of (response message, generation time in seconds)
        """
        # Start timing
        start_time = datetime.now()
        
        # Build messages for Ollama
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        # Add conversation history
        for msg in conversation_history:
            # Determine if this message is from us or others
            if msg['agent'] == self.name:
                role = "assistant"
            else:
                role = "user"
            
            messages.append({
                "role": role,
                "content": msg['message']
            })
        
        # Call Ollama
        logger.info(f"{self.name} generating response...")
        
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "think": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 200
                    }
                },
                timeout=300  # 5 minutes for CPU-only execution
            )
            response.raise_for_status()
            
        except requests.exceptions.Timeout:
            logger.error(f"{self.name}: Request timed out after 300s")
            raise RuntimeError(f"Agent {self.name} timed out waiting for LLM response")
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name}: HTTP error: {e}")
            raise RuntimeError(f"Agent {self.name} failed to connect to LLM: {e}")
        
        # Parse response
        try:
            result = response.json()
            message = result['message']['content'].strip()
            
            if not message:
                logger.error(f"{self.name}: Received empty response")
                raise RuntimeError(f"Agent {self.name} received empty response from LLM")
            
            # Calculate generation time
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()
            
            logger.info(f"{self.name}: {message[:50]}... [SUCCESS] ({generation_time:.2f}s)")
            return message, generation_time
            
        except (KeyError, ValueError) as e:
            logger.error(f"{self.name}: Invalid response format: {e}")
            raise RuntimeError(f"Agent {self.name} received invalid response from LLM")


class HumanAgent:
    """
    Human participant in conversation.
    
    For now, just a placeholder - actual human input handled by UI.
    """
    
    def __init__(self, name: str, company: str, role: str, objective: str):
        self.name = name
        self.company = company
        self.role = role
        self.objective = objective
        self.is_human = True


class MultiAgentOrchestrator:
    """
    Manages multi-agent conversations with round-robin turn-taking.
    
    Simple implementation: agents take turns until max_turns or conversation ends.
    """
    
    def __init__(self, agents: List, max_turns: int = 30):
        """
        Initialize orchestrator.
        
        Args:
            agents: List of Agent or HumanAgent instances
            max_turns: Maximum conversation turns
        """
        self.agents = agents
        self.max_turns = max_turns
        self.conversation_history = []
        
    def run(self, initial_message: Optional[str] = None) -> List[Dict]:
        """
        Run autonomous conversation between agents.
        
        Args:
            initial_message: Optional starting message
            
        Returns:
            List of conversation messages
        """
        logger.info(f"Starting conversation with {len(self.agents)} agents")
        
        # Add initial message if provided
        if initial_message:
            # Assume first agent starts
            self.conversation_history.append({
                "turn": 0,
                "agent": self.agents[0].name,
                "company": self.agents[0].company,
                "role": self.agents[0].role,
                "message": initial_message,
                "timestamp": datetime.now().isoformat()
            })
        
        # Round-robin conversation
        current_agent_index = 1 if initial_message else 0
        
        for turn in range(1, self.max_turns + 1):
            current_agent = self.agents[current_agent_index]
            
            # Skip human agents in autonomous mode
            if isinstance(current_agent, HumanAgent):
                logger.info(f"Skipping human agent: {current_agent.name}")
                current_agent_index = (current_agent_index + 1) % len(self.agents)
                continue
            
            # Generate response
            logger.info(f"Turn {turn}: {current_agent.name} is thinking...")
            
            try:
                response, generation_time = current_agent.respond(self.conversation_history)
                
                # Add to history
                self.conversation_history.append({
                    "turn": turn,
                    "agent": current_agent.name,
                    "company": current_agent.company,
                    "role": current_agent.role,
                    "message": response,
                    "timestamp": datetime.now().isoformat(),
                    "generation_time": generation_time
                })
                
                logger.info(f"Turn {turn}: {current_agent.name} completed successfully ({generation_time:.2f}s)")
                
            except Exception as e:
                logger.error(f"FATAL: Turn {turn} failed: {e}")
                logger.error("Stopping conversation due to error")
                raise  # Re-raise to stop execution
            
            # Check termination
            if self._should_terminate():
                logger.info("Conversation terminated early")
                break
            
            # Next agent
            current_agent_index = (current_agent_index + 1) % len(self.agents)
        
        logger.info(f"Conversation complete: {len(self.conversation_history)} messages")
        return self.conversation_history
    
    def run_streaming(self, initial_message: Optional[str] = None):
        """Generator that yields messages as they're created for real-time UI updates."""
        logger.info(f"Starting streaming conversation with {len(self.agents)} agents")
        
        # Add initial message if provided
        if initial_message:
            msg = {
                "turn": 0,
                "agent": self.agents[0].name,
                "company": self.agents[0].company,
                "role": self.agents[0].role,
                "message": initial_message,
                "timestamp": datetime.now().isoformat()
            }
            self.conversation_history.append(msg)
            yield msg
        
        # Round-robin conversation
        current_agent_index = 1 if initial_message else 0
        
        for turn in range(1, self.max_turns + 1):
            current_agent = self.agents[current_agent_index]
            
            # Skip human agents
            if isinstance(current_agent, HumanAgent):
                current_agent_index = (current_agent_index + 1) % len(self.agents)
                continue
            
            # Generate response
            logger.info(f"Turn {turn}: {current_agent.name} is thinking...")
            
            try:
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
                
                # Yield message for real-time display
                yield msg
                
                logger.info(f"Turn {turn}: {current_agent.name} completed ({generation_time:.2f}s)")
                
            except Exception as e:
                logger.error(f"Turn {turn} failed: {e}")
                raise
            
            # Check termination
            if self._should_terminate():
                logger.info("Conversation terminated early")
                break
            
            # Next agent
            current_agent_index = (current_agent_index + 1) % len(self.agents)
    
    def _should_terminate(self) -> bool:
        """
        Simple termination logic.
        
        For now, just check for deal keywords in last message.
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
