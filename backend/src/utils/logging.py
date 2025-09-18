"""
Logging utilities for TalentSync backend
"""
import logging
import sys
from ..utils.config import config


def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    return logger


logger = setup_logging()