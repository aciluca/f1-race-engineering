from pathlib import Path

from config.logging_config import setup_logging
from data.cache.cache_manager import CacheManager


def build_application(project_root: Path) -> CacheManager:
    """
    Initializes the application's core components.

    For now:
    - logging
    - cache root
    """
    setup_logging("INFO")
    
    cache_root = project_root / "cache"
    cache_manager = CacheManager(cache_root=cache_root)
    cache_manager.initialize()
    
    return cache_manager