"""
Performance Metrics Tracking
=============================

Track and monitor API and model performance metrics.
"""

import time
from typing import Dict, Optional
from collections import defaultdict
from contextlib import contextmanager

from .logger import get_logger

logger = get_logger(__name__)


class MetricsCollector:
    """Collects and aggregates performance metrics."""
    
    def __init__(self):
        self.request_count = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_count = defaultdict(int)
        self.model_inference_times = defaultdict(list)
    
    def record_request(self, endpoint: str, response_time: float, status_code: int):
        """Record an API request."""
        self.request_count[endpoint] += 1
        self.response_times[endpoint].append(response_time)
        
        if status_code >= 400:
            self.error_count[endpoint] += 1
    
    def record_inference(self, model_name: str, inference_time: float):
        """Record a model inference."""
        self.model_inference_times[model_name].append(inference_time)
    
    def get_stats(self) -> Dict:
        """Get current metrics statistics."""
        stats = {
            "requests": dict(self.request_count),
            "errors": dict(self.error_count),
            "avg_response_times": {},
            "avg_inference_times": {}
        }
        
        # Calculate average response times
        for endpoint, times in self.response_times.items():
            if times:
                stats["avg_response_times"][endpoint] = sum(times) / len(times)
        
        # Calculate average inference times
        for model, times in self.model_inference_times.items():
            if times:
                stats["avg_inference_times"][model] = sum(times) / len(times)
        
        return stats
    
    def reset(self):
        """Reset all metrics."""
        self.request_count.clear()
        self.response_times.clear()
        self.error_count.clear()
        self.model_inference_times.clear()


# Global metrics collector
metrics = MetricsCollector()


@contextmanager
def track_time(operation: str, metric_type: str = "inference"):
    """
    Context manager to track operation time.
    
    Args:
        operation: Name of the operation being tracked
        metric_type: Type of metric ('inference' or 'request')
    
    Example:
        with track_time("sentiment_analysis"):
            result = model.predict(text)
    """
    start_time = time.time()
    try:
        yield
    finally:
        elapsed = time.time() - start_time
        
        if metric_type == "inference":
            metrics.record_inference(operation, elapsed)
        
        logger.debug(f"{operation} completed in {elapsed:.4f}s")
