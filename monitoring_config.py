"""
Monitoring configuration for Fraud Detection API
Can be integrated with Prometheus, Grafana, or other monitoring tools
"""

import time
from functools import wraps
from typing import Callable
import logging

logger = logging.getLogger(__name__)

# Metrics storage (in production, use Prometheus or similar)
metrics = {
    "total_requests": 0,
    "total_predictions": 0,
    "total_batch_predictions": 0,
    "total_errors": 0,
    "response_times": [],
    "fraud_detected": 0,
    "non_fraud_detected": 0
}


def track_metrics(func: Callable) -> Callable:
    """Decorator to track API metrics"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        metrics["total_requests"] += 1
        
        try:
            result = await func(*args, **kwargs)
            response_time = time.time() - start_time
            metrics["response_times"].append(response_time)
            
            # Keep only last 1000 response times
            if len(metrics["response_times"]) > 1000:
                metrics["response_times"] = metrics["response_times"][-1000:]
            
            return result
        except Exception as e:
            metrics["total_errors"] += 1
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
    
    return wrapper


def get_metrics_summary() -> dict:
    """Get summary of collected metrics"""
    response_times = metrics["response_times"]
    
    if response_times:
        import statistics
        return {
            "total_requests": metrics["total_requests"],
            "total_predictions": metrics["total_predictions"],
            "total_batch_predictions": metrics["total_batch_predictions"],
            "total_errors": metrics["total_errors"],
            "fraud_detected": metrics["fraud_detected"],
            "non_fraud_detected": metrics["non_fraud_detected"],
            "avg_response_time": statistics.mean(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 20 else None,
            "error_rate": metrics["total_errors"] / metrics["total_requests"] if metrics["total_requests"] > 0 else 0
        }
    else:
        return {
            "total_requests": metrics["total_requests"],
            "total_predictions": metrics["total_predictions"],
            "total_batch_predictions": metrics["total_batch_predictions"],
            "total_errors": metrics["total_errors"],
            "fraud_detected": metrics["fraud_detected"],
            "non_fraud_detected": metrics["non_fraud_detected"],
            "avg_response_time": 0,
            "error_rate": 0
        }


def reset_metrics():
    """Reset all metrics (useful for testing)"""
    global metrics
    metrics = {
        "total_requests": 0,
        "total_predictions": 0,
        "total_batch_predictions": 0,
        "total_errors": 0,
        "response_times": [],
        "fraud_detected": 0,
        "non_fraud_detected": 0
    }

