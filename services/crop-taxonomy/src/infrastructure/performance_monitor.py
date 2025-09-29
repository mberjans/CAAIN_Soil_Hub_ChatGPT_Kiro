"""
Performance Monitoring System

This module implements comprehensive performance monitoring for the
crop variety recommendation system.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import aioredis
from aioredis import Redis
import psutil
import threading
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of performance metrics."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    operation: str
    execution_time_ms: float
    cache_hit: bool = False
    database_query_count: int = 0
    redis_query_count: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    error_count: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricData:
    """Individual metric data point."""
    name: str
    value: float
    metric_type: MetricType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)


class PerformanceMonitor:
    """Comprehensive performance monitoring system."""
    
    def __init__(self, redis: Redis = None):
        self.redis = redis
        self.metrics_buffer: List[PerformanceMetrics] = []
        self.metric_data: Dict[str, List[MetricData]] = {}
        self.buffer_size = 1000
        self.flush_interval = 30  # seconds
        self._running = False
        self._flush_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize the performance monitor."""
        try:
            if self.redis:
                await self.redis.ping()
                logger.info("Performance monitor initialized with Redis")
            else:
                logger.info("Performance monitor initialized without Redis")
                
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {e}")
            raise
            
    async def start_monitoring(self):
        """Start performance monitoring."""
        if self._running:
            return
            
        self._running = True
        self._flush_task = asyncio.create_task(self._flush_loop())
        logger.info("Performance monitoring started")
        
    async def stop_monitoring(self):
        """Stop performance monitoring."""
        self._running = False
        
        if self._flush_task:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
                
        # Flush remaining metrics
        await self._flush_metrics()
        logger.info("Performance monitoring stopped")
        
    async def record_operation(self, 
                             operation: str,
                             execution_time_ms: float,
                             cache_hit: bool = False,
                             database_query_count: int = 0,
                             redis_query_count: int = 0,
                             error_count: int = 0,
                             metadata: Dict[str, Any] = None):
        """Record an operation's performance metrics."""
        try:
            # Get system metrics
            memory_usage = psutil.virtual_memory().used / (1024 * 1024)  # MB
            cpu_usage = psutil.cpu_percent()
            
            metrics = PerformanceMetrics(
                operation=operation,
                execution_time_ms=execution_time_ms,
                cache_hit=cache_hit,
                database_query_count=database_query_count,
                redis_query_count=redis_query_count,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                error_count=error_count,
                metadata=metadata or {}
            )
            
            async with self._lock:
                self.metrics_buffer.append(metrics)
                
                # Flush if buffer is full
                if len(self.metrics_buffer) >= self.buffer_size:
                    await self._flush_metrics()
                    
        except Exception as e:
            logger.error(f"Failed to record operation metrics: {e}")
            
    async def record_metric(self, 
                          name: str,
                          value: float,
                          metric_type: MetricType = MetricType.GAUGE,
                          tags: Dict[str, str] = None):
        """Record a custom metric."""
        try:
            metric_data = MetricData(
                name=name,
                value=value,
                metric_type=metric_type,
                tags=tags or {}
            )
            
            async with self._lock:
                if name not in self.metric_data:
                    self.metric_data[name] = []
                    
                self.metric_data[name].append(metric_data)
                
                # Keep only last 1000 data points per metric
                if len(self.metric_data[name]) > 1000:
                    self.metric_data[name] = self.metric_data[name][-1000:]
                    
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            
    @asynccontextmanager
    async def time_operation(self, operation: str, **metadata):
        """Context manager for timing operations."""
        start_time = time.time()
        start_memory = psutil.virtual_memory().used
        
        try:
            yield
        except Exception as e:
            await self.record_operation(
                operation=operation,
                execution_time_ms=(time.time() - start_time) * 1000,
                error_count=1,
                metadata={**metadata, "error": str(e)}
            )
            raise
        else:
            await self.record_operation(
                operation=operation,
                execution_time_ms=(time.time() - start_time) * 1000,
                metadata=metadata
            )
            
    async def _flush_loop(self):
        """Background task to flush metrics periodically."""
        while self._running:
            try:
                await asyncio.sleep(self.flush_interval)
                await self._flush_metrics()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Flush loop error: {e}")
                
    async def _flush_metrics(self):
        """Flush metrics to storage."""
        try:
            async with self._lock:
                if not self.metrics_buffer:
                    return
                    
                metrics_to_flush = self.metrics_buffer.copy()
                self.metrics_buffer.clear()
                
            # Store metrics in Redis if available
            if self.redis:
                await self._store_metrics_in_redis(metrics_to_flush)
                
            # Store metrics in memory for analysis
            await self._store_metrics_in_memory(metrics_to_flush)
            
        except Exception as e:
            logger.error(f"Failed to flush metrics: {e}")
            
    async def _store_metrics_in_redis(self, metrics: List[PerformanceMetrics]):
        """Store metrics in Redis."""
        try:
            for metric in metrics:
                # Store as time series data
                timestamp = metric.timestamp.timestamp()
                
                # Store operation metrics
                await self.redis.zadd(
                    f"metrics:operations:{metric.operation}",
                    {json.dumps({
                        "execution_time_ms": metric.execution_time_ms,
                        "cache_hit": metric.cache_hit,
                        "database_query_count": metric.database_query_count,
                        "redis_query_count": metric.redis_query_count,
                        "memory_usage_mb": metric.memory_usage_mb,
                        "cpu_usage_percent": metric.cpu_usage_percent,
                        "error_count": metric.error_count,
                        "metadata": metric.metadata
                    }): timestamp}
                )
                
                # Store system metrics
                await self.redis.zadd(
                    "metrics:system:memory",
                    {metric.memory_usage_mb: timestamp}
                )
                
                await self.redis.zadd(
                    "metrics:system:cpu",
                    {metric.cpu_usage_percent: timestamp}
                )
                
            # Clean up old metrics (keep last 24 hours)
            cutoff_time = (datetime.utcnow() - timedelta(hours=24)).timestamp()
            
            for metric in metrics:
                await self.redis.zremrangebyscore(
                    f"metrics:operations:{metric.operation}",
                    "-inf",
                    cutoff_time
                )
                
            await self.redis.zremrangebyscore("metrics:system:memory", "-inf", cutoff_time)
            await self.redis.zremrangebyscore("metrics:system:cpu", "-inf", cutoff_time)
            
        except Exception as e:
            logger.error(f"Failed to store metrics in Redis: {e}")
            
    async def _store_metrics_in_memory(self, metrics: List[PerformanceMetrics]):
        """Store metrics in memory for analysis."""
        try:
            # Group metrics by operation
            for metric in metrics:
                operation = metric.operation
                if operation not in self.metric_data:
                    self.metric_data[operation] = []
                    
                # Convert to MetricData format
                metric_data = MetricData(
                    name=f"{operation}_execution_time",
                    value=metric.execution_time_ms,
                    metric_type=MetricType.TIMER,
                    tags={"operation": operation}
                )
                
                self.metric_data[operation].append(metric_data)
                
                # Keep only last 1000 data points
                if len(self.metric_data[operation]) > 1000:
                    self.metric_data[operation] = self.metric_data[operation][-1000:]
                    
        except Exception as e:
            logger.error(f"Failed to store metrics in memory: {e}")
            
    async def get_operation_stats(self, operation: str, hours: int = 24) -> Dict[str, Any]:
        """Get statistics for a specific operation."""
        try:
            if self.redis:
                return await self._get_operation_stats_from_redis(operation, hours)
            else:
                return await self._get_operation_stats_from_memory(operation, hours)
                
        except Exception as e:
            logger.error(f"Failed to get operation stats: {e}")
            return {}
            
    async def _get_operation_stats_from_redis(self, operation: str, hours: int) -> Dict[str, Any]:
        """Get operation stats from Redis."""
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
            
            # Get metrics data
            metrics_data = await self.redis.zrangebyscore(
                f"metrics:operations:{operation}",
                cutoff_time,
                "+inf"
            )
            
            if not metrics_data:
                return {"operation": operation, "data_points": 0}
                
            # Parse and analyze metrics
            execution_times = []
            cache_hits = 0
            database_queries = 0
            redis_queries = 0
            errors = 0
            
            for data in metrics_data:
                try:
                    metric_data = json.loads(data)
                    execution_times.append(metric_data["execution_time_ms"])
                    
                    if metric_data["cache_hit"]:
                        cache_hits += 1
                        
                    database_queries += metric_data["database_query_count"]
                    redis_queries += metric_data["redis_query_count"]
                    errors += metric_data["error_count"]
                    
                except Exception as e:
                    logger.warning(f"Failed to parse metric data: {e}")
                    continue
                    
            # Calculate statistics
            if execution_times:
                avg_time = sum(execution_times) / len(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)
                p95_time = sorted(execution_times)[int(len(execution_times) * 0.95)]
                p99_time = sorted(execution_times)[int(len(execution_times) * 0.99)]
            else:
                avg_time = min_time = max_time = p95_time = p99_time = 0.0
                
            return {
                "operation": operation,
                "data_points": len(metrics_data),
                "time_range_hours": hours,
                "execution_time_ms": {
                    "average": avg_time,
                    "minimum": min_time,
                    "maximum": max_time,
                    "p95": p95_time,
                    "p99": p99_time
                },
                "cache_hit_rate": (cache_hits / len(metrics_data)) * 100 if metrics_data else 0,
                "total_database_queries": database_queries,
                "total_redis_queries": redis_queries,
                "total_errors": errors,
                "error_rate": (errors / len(metrics_data)) * 100 if metrics_data else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get operation stats from Redis: {e}")
            return {}
            
    async def _get_operation_stats_from_memory(self, operation: str, hours: int) -> Dict[str, Any]:
        """Get operation stats from memory."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get metrics data
            metrics_data = self.metric_data.get(operation, [])
            recent_metrics = [
                m for m in metrics_data 
                if m.timestamp >= cutoff_time
            ]
            
            if not recent_metrics:
                return {"operation": operation, "data_points": 0}
                
            # Calculate statistics
            values = [m.value for m in recent_metrics]
            avg_value = sum(values) / len(values)
            min_value = min(values)
            max_value = max(values)
            p95_value = sorted(values)[int(len(values) * 0.95)]
            p99_value = sorted(values)[int(len(values) * 0.99)]
            
            return {
                "operation": operation,
                "data_points": len(recent_metrics),
                "time_range_hours": hours,
                "value": {
                    "average": avg_value,
                    "minimum": min_value,
                    "maximum": max_value,
                    "p95": p95_value,
                    "p99": p99_value
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get operation stats from memory: {e}")
            return {}
            
    async def get_system_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get system-wide performance statistics."""
        try:
            if self.redis:
                return await self._get_system_stats_from_redis(hours)
            else:
                return await self._get_system_stats_from_memory(hours)
                
        except Exception as e:
            logger.error(f"Failed to get system stats: {e}")
            return {}
            
    async def _get_system_stats_from_redis(self, hours: int) -> Dict[str, Any]:
        """Get system stats from Redis."""
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
            
            # Get memory metrics
            memory_data = await self.redis.zrangebyscore(
                "metrics:system:memory",
                cutoff_time,
                "+inf"
            )
            
            # Get CPU metrics
            cpu_data = await self.redis.zrangebyscore(
                "metrics:system:cpu",
                cutoff_time,
                "+inf"
            )
            
            # Calculate statistics
            memory_values = [float(m) for m in memory_data]
            cpu_values = [float(c) for c in cpu_data]
            
            memory_stats = {
                "average_mb": sum(memory_values) / len(memory_values) if memory_values else 0,
                "minimum_mb": min(memory_values) if memory_values else 0,
                "maximum_mb": max(memory_values) if memory_values else 0
            }
            
            cpu_stats = {
                "average_percent": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "minimum_percent": min(cpu_values) if cpu_values else 0,
                "maximum_percent": max(cpu_values) if cpu_values else 0
            }
            
            return {
                "time_range_hours": hours,
                "memory_usage": memory_stats,
                "cpu_usage": cpu_stats,
                "data_points": {
                    "memory": len(memory_values),
                    "cpu": len(cpu_values)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get system stats from Redis: {e}")
            return {}
            
    async def _get_system_stats_from_memory(self, hours: int) -> Dict[str, Any]:
        """Get system stats from memory."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Get all metrics data
            all_metrics = []
            for operation_metrics in self.metric_data.values():
                recent_metrics = [
                    m for m in operation_metrics 
                    if m.timestamp >= cutoff_time
                ]
                all_metrics.extend(recent_metrics)
                
            if not all_metrics:
                return {"time_range_hours": hours, "data_points": 0}
                
            # Calculate overall statistics
            values = [m.value for m in all_metrics]
            avg_value = sum(values) / len(values)
            min_value = min(values)
            max_value = max(values)
            
            return {
                "time_range_hours": hours,
                "overall_performance": {
                    "average_value": avg_value,
                    "minimum_value": min_value,
                    "maximum_value": max_value
                },
                "data_points": len(all_metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to get system stats from memory: {e}")
            return {}
            
    async def get_top_slow_operations(self, limit: int = 10, hours: int = 24) -> List[Dict[str, Any]]:
        """Get top slowest operations."""
        try:
            if self.redis:
                return await self._get_top_slow_operations_from_redis(limit, hours)
            else:
                return await self._get_top_slow_operations_from_memory(limit, hours)
                
        except Exception as e:
            logger.error(f"Failed to get top slow operations: {e}")
            return []
            
    async def _get_top_slow_operations_from_redis(self, limit: int, hours: int) -> List[Dict[str, Any]]:
        """Get top slow operations from Redis."""
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours)).timestamp()
            
            # Get all operation keys
            operation_keys = await self.redis.keys("metrics:operations:*")
            
            slow_operations = []
            
            for key in operation_keys:
                operation = key.replace("metrics:operations:", "")
                
                # Get metrics data
                metrics_data = await self.redis.zrangebyscore(key, cutoff_time, "+inf")
                
                if not metrics_data:
                    continue
                    
                # Calculate average execution time
                execution_times = []
                for data in metrics_data:
                    try:
                        metric_data = json.loads(data)
                        execution_times.append(metric_data["execution_time_ms"])
                    except Exception:
                        continue
                        
                if execution_times:
                    avg_time = sum(execution_times) / len(execution_times)
                    slow_operations.append({
                        "operation": operation,
                        "average_execution_time_ms": avg_time,
                        "data_points": len(execution_times)
                    })
                    
            # Sort by average execution time
            slow_operations.sort(key=lambda x: x["average_execution_time_ms"], reverse=True)
            
            return slow_operations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top slow operations from Redis: {e}")
            return []
            
    async def _get_top_slow_operations_from_memory(self, limit: int, hours: int) -> List[Dict[str, Any]]:
        """Get top slow operations from memory."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            slow_operations = []
            
            for operation, metrics in self.metric_data.items():
                recent_metrics = [
                    m for m in metrics 
                    if m.timestamp >= cutoff_time
                ]
                
                if recent_metrics:
                    values = [m.value for m in recent_metrics]
                    avg_value = sum(values) / len(values)
                    
                    slow_operations.append({
                        "operation": operation,
                        "average_value": avg_value,
                        "data_points": len(recent_metrics)
                    })
                    
            # Sort by average value
            slow_operations.sort(key=lambda x: x["average_value"], reverse=True)
            
            return slow_operations[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get top slow operations from memory: {e}")
            return []


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


async def get_performance_monitor(redis: Redis = None) -> PerformanceMonitor:
    """Get the global performance monitor instance."""
    if not performance_monitor._running:
        if redis:
            performance_monitor.redis = redis
        await performance_monitor.initialize()
        await performance_monitor.start_monitoring()
    return performance_monitor