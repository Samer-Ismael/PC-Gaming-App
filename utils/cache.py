"""
Simple caching utility for metrics to improve performance
"""
import time
from typing import Any, Optional, Dict
from threading import Lock

class MetricsCache:
    """Thread-safe cache for system metrics"""
    
    def __init__(self, ttl: float = 0.5):
        self.cache: Dict[str, tuple[Any, float]] = {}
        self.ttl = ttl
        self.lock = Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired"""
        with self.lock:
            if key in self.cache:
                value, timestamp = self.cache[key]
                if time.time() - timestamp < self.ttl:
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value with current timestamp"""
        with self.lock:
            self.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cached values"""
        with self.lock:
            self.cache.clear()

# Global cache instance
metrics_cache = MetricsCache()

