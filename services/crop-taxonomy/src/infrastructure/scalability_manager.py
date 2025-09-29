"""
Comprehensive Scalability Manager for Crop Variety Recommendations

This module implements horizontal scaling, load balancing, auto-scaling,
distributed processing, and capacity planning for the crop variety
recommendation system.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import psutil
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Async and distributed processing imports
import aiohttp
import asyncio
from aiohttp import ClientSession, ClientTimeout
import aioredis
from aioredis import Redis

# Database and caching
from sqlalchemy import create_engine, text, Index, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

# Performance monitoring
from .performance_monitor import performance_monitor, PerformanceMetrics

logger = logging.getLogger(__name__)


class ScalingStrategy(Enum):
    """Scaling strategies for different components."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    AUTO = "auto"
    MANUAL = "manual"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_RESPONSE_TIME = "least_response_time"
    CONSISTENT_HASH = "consistent_hash"


@dataclass
class ServiceInstance:
    """Represents a service instance for load balancing."""
    instance_id: str
    host: str
    port: int
    health_endpoint: str
    weight: int = 1
    is_healthy: bool = True
    last_health_check: Optional[datetime] = None
    response_time_ms: float = 0.0
    active_connections: int = 0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScalingMetrics:
    """Metrics for scaling decisions."""
    cpu_usage: float
    memory_usage: float
    request_rate: float
    response_time_ms: float
    error_rate: float
    queue_length: int
    active_connections: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ScalingDecision:
    """Scaling decision result."""
    action: str  # "scale_up", "scale_down", "no_action"
    target_instances: int
    reason: str
    confidence: float
    estimated_cost_impact: float
    estimated_performance_impact: float


class LoadBalancer:
    """Advanced load balancer with multiple strategies."""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_RESPONSE_TIME):
        self.strategy = strategy
        self.instances: List[ServiceInstance] = []
        self.current_index = 0
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self._health_check_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
    async def add_instance(self, instance: ServiceInstance):
        """Add a service instance to the load balancer."""
        async with self._lock:
            self.instances.append(instance)
            logger.info(f"Added instance {instance.instance_id} to load balancer")
            
    async def remove_instance(self, instance_id: str):
        """Remove a service instance from the load balancer."""
        async with self._lock:
            self.instances = [inst for inst in self.instances if inst.instance_id != instance_id]
            logger.info(f"Removed instance {instance_id} from load balancer")
            
    async def get_next_instance(self) -> Optional[ServiceInstance]:
        """Get the next instance based on the load balancing strategy."""
        async with self._lock:
            healthy_instances = [inst for inst in self.instances if inst.is_healthy]
            if not healthy_instances:
                return None
                
            if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
                instance = healthy_instances[self.current_index % len(healthy_instances)]
                self.current_index += 1
                return instance
                
            elif self.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return min(healthy_instances, key=lambda x: x.active_connections)
                
            elif self.strategy == LoadBalancingStrategy.LEAST_RESPONSE_TIME:
                return min(healthy_instances, key=lambda x: x.response_time_ms)
                
            elif self.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                # Weighted round robin implementation
                total_weight = sum(inst.weight for inst in healthy_instances)
                if total_weight == 0:
                    return healthy_instances[0]
                    
                # Select based on weight
                target_weight = self.current_index % total_weight
                current_weight = 0
                for instance in healthy_instances:
                    current_weight += instance.weight
                    if current_weight > target_weight:
                        self.current_index += 1
                        return instance
                        
            elif self.strategy == LoadBalancingStrategy.CONSISTENT_HASH:
                # Consistent hashing for session affinity
                # Simplified implementation - in production, use a proper consistent hash ring
                return healthy_instances[self.current_index % len(healthy_instances)]
                
        return None
        
    async def start_health_checks(self):
        """Start periodic health checks for all instances."""
        if self._health_check_task:
            return
            
        async def health_check_loop():
            while True:
                try:
                    await self._perform_health_checks()
                    await asyncio.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"Health check error: {e}")
                    await asyncio.sleep(5)
                    
        self._health_check_task = asyncio.create_task(health_check_loop())
        
    async def _perform_health_checks(self):
        """Perform health checks on all instances."""
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=self.health_check_timeout)) as session:
            tasks = []
            for instance in self.instances:
                task = self._check_instance_health(session, instance)
                tasks.append(task)
                
            await asyncio.gather(*tasks, return_exceptions=True)
            
    async def _check_instance_health(self, session: ClientSession, instance: ServiceInstance):
        """Check health of a single instance."""
        try:
            start_time = time.time()
            url = f"http://{instance.host}:{instance.port}{instance.health_endpoint}"
            
            async with session.get(url) as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    instance.is_healthy = True
                    instance.response_time_ms = response_time
                    instance.last_health_check = datetime.utcnow()
                else:
                    instance.is_healthy = False
                    logger.warning(f"Instance {instance.instance_id} health check failed: {response.status}")
                    
        except Exception as e:
            instance.is_healthy = False
            logger.error(f"Health check failed for instance {instance.instance_id}: {e}")


class AutoScaler:
    """Intelligent auto-scaler with predictive scaling."""
    
    def __init__(self, 
                 min_instances: int = 2,
                 max_instances: int = 10,
                 scale_up_threshold: float = 0.7,
                 scale_down_threshold: float = 0.3,
                 cooldown_period: int = 300):  # 5 minutes
        self.min_instances = min_instances
        self.max_instances = max_instances
        self.scale_up_threshold = scale_up_threshold
        self.scale_down_threshold = scale_down_threshold
        self.cooldown_period = cooldown_period
        self.last_scale_action = None
        self.metrics_history: List[ScalingMetrics] = []
        self.prediction_model = None
        
    async def analyze_metrics(self, metrics: ScalingMetrics) -> ScalingDecision:
        """Analyze metrics and make scaling decision."""
        self.metrics_history.append(metrics)
        
        # Keep only last 100 metrics for analysis
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
            
        # Check cooldown period
        if self.last_scale_action:
            time_since_last_action = (datetime.utcnow() - self.last_scale_action).total_seconds()
            if time_since_last_action < self.cooldown_period:
                return ScalingDecision(
                    action="no_action",
                    target_instances=0,
                    reason="Cooldown period active",
                    confidence=1.0,
                    estimated_cost_impact=0.0,
                    estimated_performance_impact=0.0
                )
                
        # Analyze current metrics
        current_load = self._calculate_load_score(metrics)
        predicted_load = self._predict_future_load()
        
        # Make scaling decision
        if current_load > self.scale_up_threshold or predicted_load > self.scale_up_threshold:
            return await self._decide_scale_up(metrics, predicted_load)
        elif current_load < self.scale_down_threshold and predicted_load < self.scale_down_threshold:
            return await self._decide_scale_down(metrics, predicted_load)
        else:
            return ScalingDecision(
                action="no_action",
                target_instances=0,
                reason="Load within acceptable range",
                confidence=0.8,
                estimated_cost_impact=0.0,
                estimated_performance_impact=0.0
            )
            
    def _calculate_load_score(self, metrics: ScalingMetrics) -> float:
        """Calculate overall load score from metrics."""
        # Weighted combination of different metrics
        cpu_weight = 0.3
        memory_weight = 0.2
        response_time_weight = 0.2
        error_rate_weight = 0.2
        queue_weight = 0.1
        
        # Normalize metrics to 0-1 scale
        cpu_score = min(metrics.cpu_usage / 100.0, 1.0)
        memory_score = min(metrics.memory_usage / 100.0, 1.0)
        response_time_score = min(metrics.response_time_ms / 5000.0, 1.0)  # 5s max
        error_rate_score = min(metrics.error_rate, 1.0)
        queue_score = min(metrics.queue_length / 1000.0, 1.0)  # 1000 max queue
        
        load_score = (
            cpu_score * cpu_weight +
            memory_score * memory_weight +
            response_time_score * response_time_weight +
            error_rate_score * error_rate_weight +
            queue_score * queue_weight
        )
        
        return load_score
        
    def _predict_future_load(self) -> float:
        """Predict future load using simple trend analysis."""
        if len(self.metrics_history) < 5:
            return 0.5  # Default prediction
            
        # Simple linear trend analysis
        recent_metrics = self.metrics_history[-5:]
        load_scores = [self._calculate_load_score(m) for m in recent_metrics]
        
        # Calculate trend
        if len(load_scores) >= 2:
            trend = (load_scores[-1] - load_scores[0]) / len(load_scores)
            predicted_load = load_scores[-1] + trend * 2  # Predict 2 periods ahead
            return max(0.0, min(1.0, predicted_load))
            
        return load_scores[-1] if load_scores else 0.5
        
    async def _decide_scale_up(self, metrics: ScalingMetrics, predicted_load: float) -> ScalingDecision:
        """Decide on scale-up action."""
        # Calculate how many instances we need
        current_instances = len([m for m in self.metrics_history if m.timestamp > datetime.utcnow() - timedelta(minutes=1)])
        target_instances = min(
            self.max_instances,
            max(self.min_instances, int(current_instances * (predicted_load / self.scale_up_threshold)))
        )
        
        confidence = min(0.9, predicted_load)
        cost_impact = (target_instances - current_instances) * 0.1  # Simplified cost model
        performance_impact = max(0.0, 1.0 - predicted_load)
        
        return ScalingDecision(
            action="scale_up",
            target_instances=target_instances,
            reason=f"High load detected: {predicted_load:.2f}",
            confidence=confidence,
            estimated_cost_impact=cost_impact,
            estimated_performance_impact=performance_impact
        )
        
    async def _decide_scale_down(self, metrics: ScalingMetrics, predicted_load: float) -> ScalingDecision:
        """Decide on scale-down action."""
        current_instances = len([m for m in self.metrics_history if m.timestamp > datetime.utcnow() - timedelta(minutes=1)])
        target_instances = max(
            self.min_instances,
            int(current_instances * (predicted_load / self.scale_down_threshold))
        )
        
        confidence = min(0.9, 1.0 - predicted_load)
        cost_impact = (current_instances - target_instances) * -0.1  # Negative cost (savings)
        performance_impact = predicted_load  # Lower performance impact
        
        return ScalingDecision(
            action="scale_down",
            target_instances=target_instances,
            reason=f"Low load detected: {predicted_load:.2f}",
            confidence=confidence,
            estimated_cost_impact=cost_impact,
            estimated_performance_impact=performance_impact
        )


class DistributedProcessor:
    """Distributed processing manager for variety recommendations."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or min(32, (os.cpu_count() or 1) + 4)
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers)
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Any] = {}
        
    async def submit_task(self, 
                         task_id: str,
                         func: Callable,
                         *args,
                         use_process: bool = False,
                         **kwargs) -> str:
        """Submit a task for distributed processing."""
        if task_id in self.active_tasks:
            raise ValueError(f"Task {task_id} already exists")
            
        # Choose execution method
        if use_process:
            # Use process pool for CPU-intensive tasks
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(self.process_pool, func, *args, **kwargs)
        else:
            # Use thread pool for I/O-bound tasks
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(self.thread_pool, func, *args, **kwargs)
            
        # Create task and track it
        task = asyncio.create_task(self._execute_task(task_id, future))
        self.active_tasks[task_id] = task
        
        return task_id
        
    async def _execute_task(self, task_id: str, future):
        """Execute a task and handle completion."""
        try:
            result = await future
            self.completed_tasks[task_id] = result
            logger.info(f"Task {task_id} completed successfully")
        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self.completed_tasks[task_id] = {"error": str(e)}
        finally:
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]
                
    async def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        return self.completed_tasks.get(task_id)
        
    async def wait_for_task(self, task_id: str, timeout: float = None) -> Any:
        """Wait for a task to complete."""
        if task_id not in self.active_tasks:
            return self.completed_tasks.get(task_id)
            
        try:
            result = await asyncio.wait_for(self.active_tasks[task_id], timeout=timeout)
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Task {task_id} timed out")
            return None
            
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task."""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            del self.active_tasks[task_id]
            return True
        return False
        
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the distributed processor."""
        return {
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "max_workers": self.max_workers,
            "active_task_ids": list(self.active_tasks.keys())
        }


class ScalabilityManager:
    """Main scalability manager coordinating all scaling components."""
    
    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 database_url: str = None):
        self.redis_url = redis_url
        self.database_url = database_url
        self.load_balancer = LoadBalancer()
        self.auto_scaler = AutoScaler()
        self.distributed_processor = DistributedProcessor()
        self.redis: Optional[Redis] = None
        self.metrics_collector = None
        self._running = False
        
    async def initialize(self):
        """Initialize the scalability manager."""
        try:
            # Initialize Redis connection
            self.redis = await aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Redis connection established for scalability manager")
            
            # Start load balancer health checks
            await self.load_balancer.start_health_checks()
            
            # Initialize metrics collector
            self.metrics_collector = MetricsCollector(self.redis)
            await self.metrics_collector.initialize()
            
            logger.info("Scalability manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scalability manager: {e}")
            raise
            
    async def add_service_instance(self, 
                                 instance_id: str,
                                 host: str,
                                 port: int,
                                 health_endpoint: str = "/health",
                                 weight: int = 1):
        """Add a service instance to the load balancer."""
        instance = ServiceInstance(
            instance_id=instance_id,
            host=host,
            port=port,
            health_endpoint=health_endpoint,
            weight=weight
        )
        await self.load_balancer.add_instance(instance)
        
    async def start_monitoring(self):
        """Start monitoring and auto-scaling."""
        if self._running:
            return
            
        self._running = True
        
        async def monitoring_loop():
            while self._running:
                try:
                    # Collect metrics
                    metrics = await self._collect_system_metrics()
                    
                    # Make scaling decision
                    decision = await self.auto_scaler.analyze_metrics(metrics)
                    
                    # Execute scaling action if needed
                    if decision.action != "no_action":
                        await self._execute_scaling_decision(decision)
                        
                    # Store metrics
                    await self.metrics_collector.store_metrics(metrics)
                    
                    await asyncio.sleep(60)  # Check every minute
                    
                except Exception as e:
                    logger.error(f"Monitoring loop error: {e}")
                    await asyncio.sleep(10)
                    
        asyncio.create_task(monitoring_loop())
        logger.info("Scalability monitoring started")
        
    async def _collect_system_metrics(self) -> ScalingMetrics:
        """Collect system-wide metrics."""
        # Get system metrics
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_usage = memory.percent
        
        # Get application metrics from Redis
        request_rate = await self._get_request_rate()
        response_time_ms = await self._get_avg_response_time()
        error_rate = await self._get_error_rate()
        queue_length = await self._get_queue_length()
        active_connections = await self._get_active_connections()
        
        return ScalingMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            request_rate=request_rate,
            response_time_ms=response_time_ms,
            error_rate=error_rate,
            queue_length=queue_length,
            active_connections=active_connections
        )
        
    async def _get_request_rate(self) -> float:
        """Get current request rate per second."""
        try:
            current_time = datetime.utcnow()
            minute_ago = current_time - timedelta(minutes=1)
            
            # Count requests in the last minute
            request_count = await self.redis.zcount(
                "request_timestamps", 
                minute_ago.timestamp(), 
                current_time.timestamp()
            )
            
            return request_count / 60.0  # requests per second
        except Exception:
            return 0.0
            
    async def _get_avg_response_time(self) -> float:
        """Get average response time."""
        try:
            response_times = await self.redis.lrange("response_times", 0, 99)  # Last 100 requests
            if response_times:
                total_time = sum(float(rt) for rt in response_times)
                return total_time / len(response_times)
            return 0.0
        except Exception:
            return 0.0
            
    async def _get_error_rate(self) -> float:
        """Get current error rate."""
        try:
            total_requests = await self.redis.get("total_requests")
            error_requests = await self.redis.get("error_requests")
            
            if total_requests and error_requests:
                total = int(total_requests)
                errors = int(error_requests)
                return errors / total if total > 0 else 0.0
            return 0.0
        except Exception:
            return 0.0
            
    async def _get_queue_length(self) -> int:
        """Get current queue length."""
        try:
            return await self.redis.llen("task_queue")
        except Exception:
            return 0
            
    async def _get_active_connections(self) -> int:
        """Get number of active connections."""
        try:
            # Count active connections across all instances
            total_connections = 0
            for instance in self.load_balancer.instances:
                total_connections += instance.active_connections
            return total_connections
        except Exception:
            return 0
            
    async def _execute_scaling_decision(self, decision: ScalingDecision):
        """Execute a scaling decision."""
        logger.info(f"Executing scaling decision: {decision.action} to {decision.target_instances} instances")
        
        # In a real implementation, this would:
        # 1. Communicate with container orchestration (Kubernetes, Docker Swarm)
        # 2. Update load balancer configuration
        # 3. Monitor scaling progress
        # 4. Update service discovery
        
        # For now, we'll log the decision and update our internal state
        if decision.action == "scale_up":
            logger.info(f"Scaling up: Adding {decision.target_instances} instances")
        elif decision.action == "scale_down":
            logger.info(f"Scaling down: Removing instances to reach {decision.target_instances}")
            
    async def shutdown(self):
        """Shutdown the scalability manager."""
        self._running = False
        
        # Cancel all active tasks
        for task in self.active_tasks.values():
            task.cancel()
            
        # Close connections
        if self.redis:
            await self.redis.close()
            
        # Shutdown thread pools
        self.distributed_processor.thread_pool.shutdown(wait=True)
        self.distributed_processor.process_pool.shutdown(wait=True)
        
        logger.info("Scalability manager shutdown complete")


class MetricsCollector:
    """Collects and stores scalability metrics."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        
    async def initialize(self):
        """Initialize the metrics collector."""
        # Set up Redis data structures for metrics
        await self.redis.delete("scaling_metrics")
        await self.redis.delete("request_timestamps")
        await self.redis.delete("response_times")
        
    async def store_metrics(self, metrics: ScalingMetrics):
        """Store metrics in Redis."""
        metrics_data = {
            "timestamp": metrics.timestamp.isoformat(),
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "request_rate": metrics.request_rate,
            "response_time_ms": metrics.response_time_ms,
            "error_rate": metrics.error_rate,
            "queue_length": metrics.queue_length,
            "active_connections": metrics.active_connections
        }
        
        # Store in Redis with TTL
        await self.redis.zadd(
            "scaling_metrics",
            {json.dumps(metrics_data): metrics.timestamp.timestamp()}
        )
        
        # Keep only last 1000 metrics
        await self.redis.zremrangebyrank("scaling_metrics", 0, -1001)
        
    async def get_metrics_history(self, hours: int = 24) -> List[ScalingMetrics]:
        """Get metrics history for the specified hours."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        metrics_data = await self.redis.zrangebyscore(
            "scaling_metrics",
            cutoff_time.timestamp(),
            "+inf"
        )
        
        metrics = []
        for data in metrics_data:
            try:
                data_dict = json.loads(data)
                metrics.append(ScalingMetrics(
                    cpu_usage=data_dict["cpu_usage"],
                    memory_usage=data_dict["memory_usage"],
                    request_rate=data_dict["request_rate"],
                    response_time_ms=data_dict["response_time_ms"],
                    error_rate=data_dict["error_rate"],
                    queue_length=data_dict["queue_length"],
                    active_connections=data_dict["active_connections"],
                    timestamp=datetime.fromisoformat(data_dict["timestamp"])
                ))
            except Exception as e:
                logger.warning(f"Failed to parse metrics data: {e}")
                
        return sorted(metrics, key=lambda x: x.timestamp)


# Global scalability manager instance
scalability_manager = ScalabilityManager()


async def get_scalability_manager() -> ScalabilityManager:
    """Get the global scalability manager instance."""
    if not scalability_manager._running:
        await scalability_manager.initialize()
        await scalability_manager.start_monitoring()
    return scalability_manager