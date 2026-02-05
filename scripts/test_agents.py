#!/usr/bin/env python3
"""
Simple test script to verify agents can talk to each other.

Run: docker-compose exec app python scripts/test_agents.py
"""

import sys
import os
import logging

sys.path.insert(0, '/app/src')

# Get model from environment (same as core.py and app.py)
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from agents.core import Agent, MultiAgentOrchestrator

def main():
    print("=" * 60)
    print("Testing Agent Conversation")
    print("=" * 60)
    
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
    
    print(f"\nAgent 1: {agent1.name} - {agent1.role} at {agent1.company}")
    print(f"Agent 2: {agent2.name} - {agent2.role} at {agent2.company}")
    print()
    
    # Create orchestrator
    orchestrator = MultiAgentOrchestrator(
        agents=[agent1, agent2],
        max_turns=1  # Just 1 turn to test if it works
    )
    
    # Run conversation
    print("Starting conversation...\n")
    
    initial_message = "Hello! We're looking to purchase new servers for our data center. What can you offer?"
    
    conversation = orchestrator.run(initial_message=initial_message)
    
    # Display results
    print("\n" + "=" * 60)
    print("Conversation Complete")
    print("=" * 60)
    
    for msg in conversation:
        print(f"\n[Turn {msg['turn']}] {msg['agent']} ({msg['company']}):")
        print(f"{msg['message']}")
        print(f"Time: {msg['timestamp']}")
    
    print(f"\n\nTotal messages: {len(conversation)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
