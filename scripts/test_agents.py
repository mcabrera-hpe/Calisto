#!/usr/bin/env python3
"""
Simple test script to verify agents can talk to each other.

Run: docker-compose exec app python scripts/test_agents.py
"""

import sys
import time
import logging

sys.path.insert(0, '/app/src')

from utils.config import DEFAULT_MODEL
from utils.logging_config import setup_logging

# Set up logging to see what's happening
setup_logging()

from agents.core import Agent, MultiAgentOrchestrator

logger = logging.getLogger(__name__)

def main() -> None:
    """Test basic agent conversation functionality.
    
    Creates two agents (HPE sales and Toyota procurement) and runs
    a simple 1-turn conversation to verify the system is working.
    """
    logger.info("=" * 60)
    logger.info("Testing Agent Conversation")
    logger.info("=" * 60)
    
    # Create two simple agents
    agent1 = Agent(
        name="Sarah",
        company="HPE",
        role="Sales Engineer",
        objective="Sell servers to the client",
        model=DEFAULT_MODEL
    )
    
    agent2 = Agent(
        name="Yuki",
        company="Toyota",
        role="IT Procurement Manager",
        objective="Get the best price for servers",
        model=DEFAULT_MODEL
    )
    
    logger.info(f"Agent 1: {agent1.name} - {agent1.role} at {agent1.company}")
    logger.info(f"Agent 2: {agent2.name} - {agent2.role} at {agent2.company}")
    
    # Create orchestrator
    orchestrator = MultiAgentOrchestrator(
        agents=[agent1, agent2],
        max_turns=1  # Just 1 turn to test if it works
    )
    
    # Run conversation
    logger.info("Starting conversation...")
    
    initial_message = "Hello! We're looking to purchase new servers for our data center. What can you offer?"
    
    start_time = time.time()
    conversation = orchestrator.run(initial_message=initial_message)
    end_time = time.time()
    
    duration = end_time - start_time
    
    # Display results
    logger.info("=" * 60)
    logger.info("Conversation Complete")
    logger.info("=" * 60)
    
    for msg in conversation:
        logger.info(f"[Turn {msg['turn']}] {msg['agent']} ({msg['company']}):")
        logger.info(f"{msg['message']}")
    
    # Format duration nicely
    if duration >= 60:
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        duration_str = f"{minutes}:{seconds:02d}m"
    else:
        duration_str = f"{duration:.1f}s"
    
    logger.info("")
    logger.info(f"Total messages: {len(conversation)}")
    logger.info(f"Conversation took: {duration_str}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()
