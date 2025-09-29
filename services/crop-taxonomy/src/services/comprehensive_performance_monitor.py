"""
Comprehensive Performance Monitoring Service

This service provides detailed performance monitoring, metrics collection,
and analytics for the crop variety recommendation system optimization.

TICKET-005_crop-variety-recommendations-14.1: Implement comprehensive variety recommendation performance optimization
"""

import asyncio
import logging
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import psutil
import threading

# Database imports
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Redis imports
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


@dataclass
class PerformanceTarget:
    """Performance target definition."""
    operation: str
    target_time_ms: float
    warning_threshold_ms: float
    critical_threshold_ms: float
    description: str


@dataclass
class SystemMetrics:
    """System-level performance metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    network_io_bytes: int
    timestamp: datetime


@dataclass
class DatabaseMetrics:
    """Database performance metrics."""
    connection_count: int
    active_connections: int
    query_count: int
    average_query_time_ms: float
    slow_query_count: int
    cache_hit_rate: float
    timestamp: datetime


@dataclass
class CacheMetrics:
    """Cache performance metrics."""
    redis_available: bool
    redis_connection_count: int
    local_cache_size: int
    hit_rate: float
    miss_rate: float
    eviction_count: int
    total_requests: int
    timestamp: datetime


@dataclass
class OperationMetrics:
    """Individual operation performance metrics."""
    operation: str
    execution_time_ms: float
    cache_hit: bool
    database_query_count: int
    memory_usage_mb: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


class PerformanceTargets:
    """Performance targets for the variety recommendation system."""
    
    TARGETS = {
        "variety_recommendations": PerformanceTarget(
            operation="variety_recommendations",
            target_time_ms=2000.0,
            warning_threshold_ms=1500.0,
            critical_threshold_ms=2500.0,
            description="Variety recommendation generation"
        ),
        "variety_search": PerformanceTarget(
            operation="variety_search",
            target_time_ms=1000.0,
            warning_threshold_ms=750.0,
            critical_threshold_ms=1500.0,
            description="Variety search operations"
        ),
        "variety_details": PerformanceTarget(
            operation="variety_details",
            target_time_ms=500.0,
            warning_threshold_ms=400.0,
            critical_threshold_ms=750.0,
            description="Variety details retrieval"
        ),
        "variety_comparison": PerformanceTarget(
            operation="variety_comparison",
            target_time_ms=1500.0,
            warning_threshold_ms=1000.0,
            critical_threshold_ms=2000.0,
            description="Variety comparison operations"
        ),
        "batch_operations": PerformanceTarget(
            operation="batch_operations",
            target_time_ms=5000.0,
            warning_threshold_ms=4000.0,
            critical_threshold_ms=7500.0,
            description="Batch operation processing"
        )
    }
    
    @classmethod
    def get_target(cls, operation: str) -> Optional[PerformanceTarget]:
        """Get performance target for an operation."""
        return cls.TARGETS.get(operation)
    
    @classmethod
    def get_all_targets(cls) -> Dict[str, PerformanceTarget]:
        """Get all performance targets."""
        return cls.TARGETS.copy()


class ComprehensivePerformanceMonitor:
    """Comprehensive performance monitoring service."""
    
    def __init__(self, database_url: str = None, redis_url: str = "redis://localhost:6379"):
        """Initialize the comprehensive performance monitor."""
        self.database_url = database_url
        self.redis_url = redis_url
        
        # Metrics storage
        self.operation_metrics: deque = deque(maxlen=10000)  # Keep last 10k operations
        self.system_metrics: deque = deque(maxlen=1000)      # Keep last 1k system snapshots
        self.database_metrics: deque = deque(maxlen=1000)    # Keep last 1k database snapshots
        self.cache_metrics: deque = deque(maxlen=1000)      # Keep last 1k cache snapshots
        
        # Performance targets
        self.targets = PerformanceTargets.get_all_targets()
        
        # Statistics tracking
        self.operation_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "count": 0,
            "total_time": 0.0,
            "min_time": float('inf'),
            "max_time": 0.0,
            "success_count": 0,
            "error_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "db_queries": 0
        })
        
        # Database connection for metrics
        self.db_engine = None
        self.db_session = None
        if database_url:
            self._initialize_database()
        
        # Redis connection for metrics
        self.redis_client = None
        if REDIS_AVAILABLE:
            self._initialize_redis()
        
        # Background monitoring
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        logger.info("Comprehensive performance monitor initialized")
    
    def _initialize_database(self):
        """Initialize database connection for metrics collection."""
        try:
            self.db_engine = create_engine(self.database_url, echo=False)
            self.db_session = sessionmaker(bind=self.db_engine)
            logger.info("Database connection initialized for performance monitoring")
        except Exception as e:
            logger.warning(f"Failed to initialize database connection: {e}")
    
    def _initialize_redis(self):
        """Initialize Redis connection for metrics collection."""
        try:
            self.redis_client = redis.from_url(self.redis_url)
            logger.info("Redis connection initialized for performance monitoring")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis connection: {e}")
    
    def start_monitoring(self, interval_seconds: int = 30):
        """Start background performance monitoring."""
        if self.monitoring_active:
            logger.warning("Performance monitoring is already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(
            self._monitoring_loop(interval_seconds)
        )
        logger.info(f"Background performance monitoring started (interval: {interval_seconds}s)")
    
    def stop_monitoring(self):
        """Stop background performance monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        logger.info("Background performance monitoring stopped")
    
    async def _monitoring_loop(self, interval_seconds: int):
        """Background monitoring loop."""
        while self.monitoring_active:
            try:
                # Collect system metrics
                await self._collect_system_metrics()
                
                # Collect database metrics
                await self._collect_database_metrics()
                
                # Collect cache metrics
                await self._collect_cache_metrics()
                
                # Wait for next interval
                await asyncio.sleep(interval_seconds)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(interval_seconds)
    
    async def _collect_system_metrics(self):
        """Collect system-level performance metrics."""
        try:
            # CPU and memory metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network_io = psutil.net_io_counters()
            network_bytes = network_io.bytes_sent + network_io.bytes_recv
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / (1024 * 1024),
                memory_available_mb=memory.available / (1024 * 1024),
                disk_usage_percent=disk.percent,
                network_io_bytes=network_bytes,
                timestamp=datetime.utcnow()
            )
            
            with self.lock:
                self.system_metrics.append(metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    async def _collect_database_metrics(self):
        """Collect database performance metrics."""
        if not self.db_session:
            return
        
        try:
            with self.db_session() as session:
                # Get connection pool status
                pool_status = session.bind.pool.status()
                
                # Get query statistics (if available)
                query_stats = await self._get_query_statistics(session)
                
                metrics = DatabaseMetrics(
                    connection_count=pool_status.get('size', 0),
                    active_connections=pool_status.get('checkedout', 0),
                    query_count=query_stats.get('query_count', 0),
                    average_query_time_ms=query_stats.get('avg_query_time', 0.0),
                    slow_query_count=query_stats.get('slow_queries', 0),
                    cache_hit_rate=query_stats.get('cache_hit_rate', 0.0),
                    timestamp=datetime.utcnow()
                )
                
                with self.lock:
                    self.database_metrics.append(metrics)
                
        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")
    
    async def _get_query_statistics(self, session) -> Dict[str, Any]:
        """Get query statistics from database."""
        try:
            # Query performance_metrics table if it exists
            result = session.execute(text("""
                SELECT 
                    COUNT(*) as query_count,
                    AVG(execution_time_ms) as avg_query_time,
                    COUNT(CASE WHEN execution_time_ms > 1000 THEN 1 END) as slow_queries,
                    AVG(CASE WHEN cache_hit THEN 1.0 ELSE 0.0 END) as cache_hit_rate
                FROM performance_metrics 
                WHERE timestamp > NOW() - INTERVAL '1 hour'
            """)).fetchone()
            
            if result:
                return {
                    'query_count': result[0] or 0,
                    'avg_query_time': result[1] or 0.0,
                    'slow_queries': result[2] or 0,
                    'cache_hit_rate': result[3] or 0.0
                }
        except Exception:
            pass
        
        return {
            'query_count': 0,
            'avg_query_time': 0.0,
            'slow_queries': 0,
            'cache_hit_rate': 0.0
        }
    
    async def _collect_cache_metrics(self):
        """Collect cache performance metrics."""
        try:
            redis_available = False
            redis_connections = 0
            hit_rate = 0.0
            miss_rate = 0.0
            evictions = 0
            total_requests = 0
            
            if self.redis_client:
                try:
                    # Test Redis connection
                    await self.redis_client.ping()
                    redis_available = True
                    
                    # Get Redis info
                    info = await self.redis_client.info()
                    redis_connections = info.get('connected_clients', 0)
                    
                except Exception:
                    redis_available = False
            
            # Calculate cache metrics from operation stats
            with self.lock:
                total_hits = sum(stats['cache_hits'] for stats in self.operation_stats.values())
                total_misses = sum(stats['cache_misses'] for stats in self.operation_stats.values())
                total_requests = total_hits + total_misses
                
                if total_requests > 0:
                    hit_rate = total_hits / total_requests
                    miss_rate = total_misses / total_requests
            
            metrics = CacheMetrics(
                redis_available=redis_available,
                redis_connection_count=redis_connections,
                local_cache_size=len(self.operation_metrics),
                hit_rate=hit_rate,
                miss_rate=miss_rate,
                eviction_count=evictions,
                total_requests=total_requests,
                timestamp=datetime.utcnow()
            )
            
            with self.lock:
                self.cache_metrics.append(metrics)
                
        except Exception as e:
            logger.error(f"Failed to collect cache metrics: {e}")
    
    def record_operation(self, operation: str, execution_time_ms: float, 
                        cache_hit: bool = False, database_query_count: int = 0,
                        memory_usage_mb: float = 0.0, success: bool = True,
                        error_message: Optional[str] = None):
        """Record an operation's performance metrics."""
        metrics = OperationMetrics(
            operation=operation,
            execution_time_ms=execution_time_ms,
            cache_hit=cache_hit,
            database_query_count=database_query_count,
            memory_usage_mb=memory_usage_mb,
            success=success,
            error_message=error_message,
            timestamp=datetime.utcnow()
        )
        
        with self.lock:
            # Store metrics
            self.operation_metrics.append(metrics)
            
            # Update statistics
            stats = self.operation_stats[operation]
            stats['count'] += 1
            stats['total_time'] += execution_time_ms
            stats['min_time'] = min(stats['min_time'], execution_time_ms)
            stats['max_time'] = max(stats['max_time'], execution_time_ms)
            
            if success:
                stats['success_count'] += 1
            else:
                stats['error_count'] += 1
            
            if cache_hit:
                stats['cache_hits'] += 1
            else:
                stats['cache_misses'] += 1
            
            stats['db_queries'] += database_query_count
        
        # Check performance targets
        self._check_performance_targets(operation, execution_time_ms)
    
    def _check_performance_targets(self, operation: str, execution_time_ms: float):
        """Check if operation meets performance targets."""
        target = self.targets.get(operation)
        if not target:
            return
        
        if execution_time_ms > target.critical_threshold_ms:
            logger.error(
                f"CRITICAL: {operation} exceeded critical threshold: "
                f"{execution_time_ms:.2f}ms > {target.critical_threshold_ms}ms"
            )
        elif execution_time_ms > target.warning_threshold_ms:
            logger.warning(
                f"WARNING: {operation} exceeded warning threshold: "
                f"{execution_time_ms:.2f}ms > {target.warning_threshold_ms}ms"
            )
    
    def get_operation_statistics(self, operation: str = None) -> Dict[str, Any]:
        """Get performance statistics for operations."""
        with self.lock:
            if operation:
                stats = self.operation_stats.get(operation, {})
                if not stats:
                    return {}
                
                return {
                    "operation": operation,
                    "count": stats['count'],
                    "average_time_ms": stats['total_time'] / stats['count'] if stats['count'] > 0 else 0,
                    "min_time_ms": stats['min_time'] if stats['min_time'] != float('inf') else 0,
                    "max_time_ms": stats['max_time'],
                    "success_rate": stats['success_count'] / stats['count'] if stats['count'] > 0 else 0,
                    "error_rate": stats['error_count'] / stats['count'] if stats['count'] > 0 else 0,
                    "cache_hit_rate": stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']) if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0,
                    "average_db_queries": stats['db_queries'] / stats['count'] if stats['count'] > 0 else 0
                }
            else:
                # Return statistics for all operations
                result = {}
                for op, stats in self.operation_stats.items():
                    if stats['count'] > 0:
                        result[op] = {
                            "count": stats['count'],
                            "average_time_ms": stats['total_time'] / stats['count'],
                            "min_time_ms": stats['min_time'] if stats['min_time'] != float('inf') else 0,
                            "max_time_ms": stats['max_time'],
                            "success_rate": stats['success_count'] / stats['count'],
                            "error_rate": stats['error_count'] / stats['count'],
                            "cache_hit_rate": stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses']) if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0,
                            "average_db_queries": stats['db_queries'] / stats['count']
                        }
                return result
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        with self.lock:
            # Get recent metrics (last hour)
            cutoff_time = datetime.utcnow() - timedelta(hours=1)
            recent_operations = [
                op for op in self.operation_metrics 
                if op.timestamp > cutoff_time
            ]
            
            # Calculate summary statistics
            total_operations = len(recent_operations)
            successful_operations = sum(1 for op in recent_operations if op.success)
            cache_hits = sum(1 for op in recent_operations if op.cache_hit)
            
            avg_execution_time = (
                sum(op.execution_time_ms for op in recent_operations) / total_operations
                if total_operations > 0 else 0
            )
            
            # Get system metrics
            recent_system_metrics = [
                m for m in self.system_metrics 
                if m.timestamp > cutoff_time
            ]
            
            avg_cpu = (
                sum(m.cpu_percent for m in recent_system_metrics) / len(recent_system_metrics)
                if recent_system_metrics else 0
            )
            
            avg_memory = (
                sum(m.memory_percent for m in recent_system_metrics) / len(recent_system_metrics)
                if recent_system_metrics else 0
            )
            
            # Performance target compliance
            target_compliance = {}
            for operation, target in self.targets.items():
                op_metrics = [op for op in recent_operations if op.operation == operation]
                if op_metrics:
                    avg_time = sum(op.execution_time_ms for op in op_metrics) / len(op_metrics)
                    target_compliance[operation] = {
                        "target_ms": target.target_time_ms,
                        "actual_avg_ms": avg_time,
                        "compliance_rate": min(1.0, target.target_time_ms / avg_time) if avg_time > 0 else 1.0,
                        "operations_count": len(op_metrics)
                    }
            
            return {
                "summary_period_hours": 1,
                "total_operations": total_operations,
                "successful_operations": successful_operations,
                "success_rate": successful_operations / total_operations if total_operations > 0 else 0,
                "cache_hit_rate": cache_hits / total_operations if total_operations > 0 else 0,
                "average_execution_time_ms": avg_execution_time,
                "system_metrics": {
                    "average_cpu_percent": avg_cpu,
                    "average_memory_percent": avg_memory,
                    "monitoring_active": self.monitoring_active
                },
                "target_compliance": target_compliance,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_performance_alerts(self) -> List[Dict[str, Any]]:
        """Get performance alerts based on thresholds."""
        alerts = []
        
        with self.lock:
            # Check recent operations for alerts
            cutoff_time = datetime.utcnow() - timedelta(minutes=15)
            recent_operations = [
                op for op in self.operation_metrics 
                if op.timestamp > cutoff_time
            ]
            
            # Group by operation
            operations = defaultdict(list)
            for op in recent_operations:
                operations[op.operation].append(op)
            
            # Check each operation type
            for operation, ops in operations.items():
                target = self.targets.get(operation)
                if not target:
                    continue
                
                # Check for critical threshold violations
                critical_violations = [
                    op for op in ops 
                    if op.execution_time_ms > target.critical_threshold_ms
                ]
                
                if critical_violations:
                    alerts.append({
                        "level": "critical",
                        "operation": operation,
                        "message": f"{operation} exceeded critical threshold {len(critical_violations)} times",
                        "threshold_ms": target.critical_threshold_ms,
                        "violations": len(critical_violations),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Check for warning threshold violations
                warning_violations = [
                    op for op in ops 
                    if target.warning_threshold_ms < op.execution_time_ms <= target.critical_threshold_ms
                ]
                
                if warning_violations:
                    alerts.append({
                        "level": "warning",
                        "operation": operation,
                        "message": f"{operation} exceeded warning threshold {len(warning_violations)} times",
                        "threshold_ms": target.warning_threshold_ms,
                        "violations": len(warning_violations),
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        return alerts
    
    async def export_metrics(self, format: str = "json") -> Union[str, Dict[str, Any]]:
        """Export performance metrics in specified format."""
        with self.lock:
            data = {
                "export_timestamp": datetime.utcnow().isoformat(),
                "operation_metrics": [
                    {
                        "operation": op.operation,
                        "execution_time_ms": op.execution_time_ms,
                        "cache_hit": op.cache_hit,
                        "database_query_count": op.database_query_count,
                        "memory_usage_mb": op.memory_usage_mb,
                        "success": op.success,
                        "error_message": op.error_message,
                        "timestamp": op.timestamp.isoformat()
                    }
                    for op in self.operation_metrics
                ],
                "system_metrics": [
                    {
                        "cpu_percent": m.cpu_percent,
                        "memory_percent": m.memory_percent,
                        "memory_used_mb": m.memory_used_mb,
                        "memory_available_mb": m.memory_available_mb,
                        "disk_usage_percent": m.disk_usage_percent,
                        "network_io_bytes": m.network_io_bytes,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in self.system_metrics
                ],
                "operation_statistics": self.get_operation_statistics(),
                "performance_summary": self.get_performance_summary()
            }
        
        if format == "json":
            return data
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_data = "operation,execution_time_ms,cache_hit,success,timestamp\n"
            for op in self.operation_metrics:
                csv_data += f"{op.operation},{op.execution_time_ms},{op.cache_hit},{op.success},{op.timestamp.isoformat()}\n"
            return csv_data
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Singleton instance for global access
comprehensive_performance_monitor: Optional[ComprehensivePerformanceMonitor] = None


def get_comprehensive_performance_monitor(
    database_url: str = None, 
    redis_url: str = "redis://localhost:6379"
) -> ComprehensivePerformanceMonitor:
    """Get or create the global comprehensive performance monitor instance."""
    global comprehensive_performance_monitor
    
    if comprehensive_performance_monitor is None:
        comprehensive_performance_monitor = ComprehensivePerformanceMonitor(
            database_url, redis_url
        )
    
    return comprehensive_performance_monitor