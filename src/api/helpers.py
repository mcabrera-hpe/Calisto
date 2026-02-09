"""
Helper functions for Callisto API.
"""

from src.agents import Agent
from src.utils.config import DEFAULT_MODEL


def create_agent(index: int, client: str) -> Agent:
    """Factory function to create agents based on index.
    
    Args:
        index: Agent index (0-4)
        client: Client company name
        
    Returns:
        Configured Agent instance
    """
    agent_configs = [
        ("Sarah", "HPE", "Sales Engineer", "Sell servers and close the deal"),
        ("Yuki", client, "IT Procurement Manager", "Get the best price and terms"),
        ("Marcus", client, "Technical Lead", "Ensure technical requirements are met"),
        ("Lisa", "HPE", "Account Manager", "Build relationship and ensure customer satisfaction"),
        ("Ken", client, "CFO", "Minimize costs and maximize ROI")
    ]
    name, company, role, objective = agent_configs[index]
    return Agent(name, company, role, objective, DEFAULT_MODEL)
