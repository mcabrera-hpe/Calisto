"""
Agent base classes.

Simple AI agents that respond using Ollama LLM.
"""

import logging
import requests
import sys
import os
from typing import List, Dict, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.config import OLLAMA_URL, DEFAULT_MODEL

logger = logging.getLogger(__name__)


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
        model: Optional[str] = None
    ) -> None:
        """Initialize an agent.
        
        Args:
            name: Agent's name
            company: Company the agent represents
            role: Agent's professional role
            objective: What the agent is trying to achieve
            model: LLM model to use (default from env)
        """
        self.name = name
        self.company = company
        self.role = role
        self.objective = objective
        self.model = model or DEFAULT_MODEL
        
    def _build_system_prompt(self) -> str:
        """Generate system prompt for this agent.
        
        Returns:
            System prompt string
        """
        return f"""You are {self.name}, a {self.role} at {self.company}.

Your objective: {self.objective}

Guidelines:
- Stay in character as {self.name}
- Be professional and realistic
- Keep responses concise (2-3 sentences)
- Focus on your objective
- Respond naturally as if in a business conversation"""

    def _build_messages(self, conversation_history: List[Dict]) -> List[Dict]:
        """Build messages array for Ollama API.
        
        Args:
            conversation_history: List of messages with 'agent' and 'message' keys
            
        Returns:
            Messages array for LLM API call
        """
        messages = [
            {"role": "system", "content": self._build_system_prompt()}
        ]
        
        # Add conversation history
        for msg in conversation_history:
            # Determine if this message is from us or others
            role = "assistant" if msg['agent'] == self.name else "user"
            messages.append({
                "role": role,
                "content": msg['message']
            })
        
        return messages
    
    def _call_ollama(self, messages: List[Dict]) -> Dict:
        """Make HTTP call to Ollama API.
        
        Args:
            messages: Messages array for LLM
            
        Returns:
            Response JSON from Ollama
            
        Raises:
            RuntimeError: If request fails or times out
        """
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
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"{self.name}: Request timed out after 300s")
            raise RuntimeError(f"Agent {self.name} timed out waiting for LLM response")
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name}: HTTP error: {e}")
            raise RuntimeError(f"Agent {self.name} failed to connect to LLM: {e}")

    def respond(self, conversation_history: List[Dict]) -> tuple[str, float]:
        """
        Generate a response based on conversation history.
        
        Args:
            conversation_history: List of messages with 'agent' and 'message' keys
            
        Returns:
            Tuple of (response message, generation time in seconds)
        """
        start_time = datetime.now()
        
        # Build and send request
        messages = self._build_messages(conversation_history)
        result = self._call_ollama(messages)
        
        # Parse response
        try:
            message = result['message']['content'].strip()
            
            if not message:
                logger.error(f"{self.name}: Received empty response")
                raise RuntimeError(f"Agent {self.name} received empty response from LLM")
            
            # Calculate generation time
            generation_time = (datetime.now() - start_time).total_seconds()
            
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
    
    def __init__(self, name: str, company: str, role: str, objective: str) -> None:
        """Initialize a human agent.
        
        Args:
            name: Human's name
            company: Company the human represents
            role: Human's professional role
            objective: What the human is trying to achieve
        """
        self.name = name
        self.company = company
        self.role = role
        self.objective = objective
        self.is_human = True
