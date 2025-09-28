"""Performance monitoring and optimization tracking for crop filtering system."""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
import asyncio
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Data class for storing performance metrics."""
    operation: str
    execution_time_ms: float
    cache_hit: bool
    database_query_count: int
    memory_usage_mb: float
    timestamp: datetime
    additional_data: Optional[Dict[str, Any]] = None

class PerformanceMonitor:
    """Performance monitoring service for crop filtering operations."""
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.operation_count: Dict[str, int] = {}
        self.total_execution_time: Dict[str, float] = {}
        self.cache_hit_rate: Dict[str, float] = {}
        self.operation_history: Dict[str, List[PerformanceMetrics]] = {}
        self.history_limit = 50
    
    def start_timer(self) -> float:
        """Start a timer for performance measurement."""
        return time.time()
    
    def stop_timer(self, start_time: float) -> float:
        """Stop the timer and return elapsed time in milliseconds."""
        elapsed_time = (time.time() - start_time) * 1000
        return elapsed_time
    
    def record_operation(self, operation: str, execution_time_ms: float, cache_hit: bool = False, 
                        database_query_count: int = 0, memory_usage_mb: float = 0.0, 
                        additional_data: Optional[Dict[str, Any]] = None):
        """Record performance metrics for an operation."""
        metric = PerformanceMetrics(
            operation=operation,
            execution_time_ms=execution_time_ms,
            cache_hit=cache_hit,
            database_query_count=database_query_count,
            memory_usage_mb=memory_usage_mb,
            timestamp=datetime.utcnow(),
            additional_data=additional_data
        )
        
        # Store the latest metric for the operation
        self.metrics[operation] = metric
        
        # Update aggregated statistics
        if operation not in self.operation_count:
            self.operation_count[operation] = 0
            self.total_execution_time[operation] = 0.0
            
        self.operation_count[operation] += 1
        self.total_execution_time[operation] += execution_time_ms
        
        if operation not in self.operation_history:
            self.operation_history[operation] = []
        history_list = self.operation_history[operation]
        history_list.append(metric)
        while len(history_list) > self.history_limit:
            history_list.pop(0)

        # Calculate cache hit rate for filter operations
        if "filter" in operation.lower() or "search" in operation.lower():
            cache_hits = 0
            total_ops = self.operation_count[operation]
            history_index = 0
            while history_index < len(history_list):
                if history_list[history_index].cache_hit:
                    cache_hits += 1
                history_index += 1
            if total_ops > 0:
                self.cache_hit_rate[operation] = cache_hits / total_ops
            else:
                self.cache_hit_rate[operation] = 0.0
    
    def get_average_execution_time(self, operation: str) -> float:
        """Get average execution time for an operation."""
        count = self.operation_count.get(operation, 0)
        total_time = self.total_execution_time.get(operation, 0.0)
        return total_time / count if count > 0 else 0.0
    
    def get_cache_hit_rate(self, operation: str) -> float:
        """Get cache hit rate for an operation."""
        return self.cache_hit_rate.get(operation, 0.0)
    
    def get_bottleneck_operations(self, threshold_ms: float = 100.0) -> Dict[str, float]:
        """Identify operations that exceed the performance threshold."""
        bottlenecks = {}
        for operation, avg_time in self.total_execution_time.items():
            count = self.operation_count[operation]
            if count > 0:
                avg_time = avg_time / count
                if avg_time > threshold_ms:
                    bottlenecks[operation] = avg_time
        return bottlenecks

    def get_recent_history(self, operation: str, limit: int = 10) -> List[PerformanceMetrics]:
        """Return recent metrics for an operation."""
        history = self.operation_history.get(operation, [])
        recent: List[PerformanceMetrics] = []
        index = len(history) - limit
        if index < 0:
            index = 0
        while index < len(history):
            recent.append(history[index])
            index += 1
        return recent

    def get_top_operations(self, limit: int = 5) -> List[tuple]:
        """Return operations with highest average execution time."""
        top_operations: List[tuple] = []
        for operation, total_time in self.total_execution_time.items():
            count = self.operation_count.get(operation, 0)
            if count == 0:
                continue
            average_time = total_time / count
            insertion_index = 0
            while insertion_index < len(top_operations):
                if average_time > top_operations[insertion_index][1]:
                    break
                insertion_index += 1
            top_operations.insert(insertion_index, (operation, average_time))
            while len(top_operations) > limit:
                top_operations.pop()
        return top_operations

    def reset_metrics(self) -> None:
        """Reset all collected metrics."""
        self.metrics.clear()
        self.operation_count.clear()
        self.total_execution_time.clear()
        self.cache_hit_rate.clear()
        self.operation_history.clear()
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "operations": {},
            "summary": {
                "total_operations": sum(self.operation_count.values()),
                "average_cache_hit_rate": sum(self.cache_hit_rate.values()) / len(self.cache_hit_rate) if self.cache_hit_rate else 0.0,
                "bottleneck_operations_count": len(self.get_bottleneck_operations(100.0))
            }
        }
        
        for operation in self.operation_count.keys():
            report["operations"][operation] = {
                "count": self.operation_count[operation],
                "average_execution_time_ms": self.get_average_execution_time(operation),
                "cache_hit_rate": self.get_cache_hit_rate(operation),
                "total_execution_time_ms": self.total_execution_time[operation]
            }
        
        return report
    
    async def monitor_with_benchmark(self, operation_name: str, func, *args, **kwargs):
        """Execute a function with performance monitoring and benchmarking."""
        start_time = self.start_timer()
        
        # Execute the function
        result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        # Record performance metrics
        execution_time = self.stop_timer(start_time)
        
        # Extract cache hit information if available in kwargs
        cache_hit = kwargs.get('cache_hit', False)
        
        self.record_operation(
            operation=operation_name,
            execution_time_ms=execution_time,
            cache_hit=cache_hit,
            database_query_count=kwargs.get('db_queries', 0),
            memory_usage_mb=kwargs.get('memory_usage', 0.0),
            additional_data=kwargs.get('additional_data', {})
        )
        
        # Log performance warnings
        if execution_time > 1000:  # More than 1 second
            logger.warning(f"Slow operation detected: {operation_name} took {execution_time:.2f}ms")
        elif execution_time > 500:  # More than 0.5 seconds
            logger.info(f"Moderately slow operation: {operation_name} took {execution_time:.2f}ms")
        
        return result

# Singleton instance
performance_monitor = PerformanceMonitor()
