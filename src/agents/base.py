"""
Agent base classes.

Simple AI agents that respond using external LLM API.
"""

import logging
import requests
import urllib3
from typing import List, Dict, Optional
from datetime import datetime

from utils.config import LLM_API_ENDPOINT, LLM_API_TOKEN, DEFAULT_MODEL

# Suppress SSL warnings for internal network API
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)


class Agent:
    """
    Simple AI agent that responds using external LLM API.
    
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
        """Build messages array for OpenAI-compatible API.
        
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
    
    def _call_llm_api(self, messages: List[Dict]) -> Dict:
        """Make HTTP call to external LLM API.
        
        Args:
            messages: Messages array for LLM
            
        Returns:
            Response JSON from API
            
        Raises:
            RuntimeError: If request fails or times out
        """
        logger.info(f"{self.name} generating response...")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_TOKEN}"
        }
        
        try:
            response = requests.post(
                LLM_API_ENDPOINT,
                headers=headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 150,
                    "temperature": 0.7
                },
                timeout=60,  # 1 minute for network API
                verify=False  # Skip SSL verification for internal network
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            logger.error(f"{self.name}: Request timed out after 60s")
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
        result = self._call_llm_api(messages)
        
        # Parse response (OpenAI-compatible format)
        try:
            message = result['choices'][0]['message']['content'].strip()
            
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
