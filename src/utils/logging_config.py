"""
Shared logging configuration for The Grid.

Provides a consistent logging setup across all scripts and modules.
"""

import logging


def setup_logging(level: int = logging.INFO) -> None:
    """
    Configure logging with consistent format.
    
    Args:
        level: Logging level (default: INFO)
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
