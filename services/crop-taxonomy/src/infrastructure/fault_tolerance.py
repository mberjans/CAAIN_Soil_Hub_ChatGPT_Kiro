"""
High Availability and Fault Tolerance System

This module implements high availability, fault tolerance, disaster recovery,
and data backup strategies for reliable variety recommendation operations.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
import time
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import aioredis
from aioredis import Redis
import aiohttp
from aiohttp import ClientSession, ClientTimeout
import psutil
import signal
import threading
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"


class FailureType(Enum):
    """Types of failures to handle."""
    SERVICE_UNAVAILABLE = "service_unavailable"
    DATABASE_CONNECTION = "database_connection"
    REDIS_CONNECTION = "redis_connection"
    EXTERNAL_API = "external_api"
    HIGH_MEMORY_USAGE = "high_memory_usage"
    HIGH_CPU_USAGE = "high_cpu_usage"
    DISK_SPACE_LOW = "disk_space_low"
    NETWORK_TIMEOUT = "network_timeout"


class RecoveryStrategy(Enum):
    """Recovery strategies for different failure types."""
    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAKER = "circuit_breaker"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    FAILOVER = "failover"
    RESTART = "restart"


@dataclass
class HealthCheck:
    """Health check configuration."""
    name: str
    check_function: Callable
    interval_seconds: int = 30
    timeout_seconds: int = 5
    failure_threshold: int = 3
    recovery_threshold: int = 2
    enabled: bool = True


@dataclass
class HealthStatus:
    """Health status result."""
    service_name: str
    status: HealthStatus
    last_check: datetime
    response_time_ms: float
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FailureEvent:
    """Failure event record."""
    failure_id: str
    failure_type: FailureType
    service_name: str
    occurred_at: datetime
    error_message: str
    recovery_strategy: RecoveryStrategy
    resolved_at: Optional[datetime] = None
    resolution_time_seconds: Optional[float] = None


@dataclass
class CircuitBreakerState:
    """Circuit breaker state."""
    name: str
    state: str  # "closed", "open", "half_open"
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    success_count: int = 0
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    half_open_max_calls: int = 3


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.name = name
        self.state = CircuitBreakerState(
            name=name,
            state="closed",
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout
        )
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state.state == "open":
                if self._should_attempt_reset():
                    self.state.state = "half_open"
                    self.state.success_count = 0
                else:
                    raise Exception(f"Circuit breaker {self.name} is open")
                    
            try:
                result = await func(*args, **kwargs)
                await self._on_success()
                return result
                
            except Exception as e:
                await self._on_failure()
                raise e
                
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt reset."""
        if not self.state.last_failure_time:
            return True
            
        time_since_failure = (datetime.utcnow() - self.state.last_failure_time).total_seconds()
        return time_since_failure >= self.state.recovery_timeout
        
    async def _on_success(self):
        """Handle successful call."""
        if self.state.state == "half_open":
            self.state.success_count += 1
            if self.state.success_count >= self.state.half_open_max_calls:
                self.state.state = "closed"
                self.state.failure_count = 0
                logger.info(f"Circuit breaker {self.name} closed after successful calls")
        else:
            self.state.failure_count = max(0, self.state.failure_count - 1)
            
    async def _on_failure(self):
        """Handle failed call."""
        self.state.failure_count += 1
        self.state.last_failure_time = datetime.utcnow()
        
        if self.state.failure_count >= self.state.failure_threshold:
            self.state.state = "open"
            logger.warning(f"Circuit breaker {self.name} opened after {self.state.failure_count} failures")
            
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.state


class HealthMonitor:
    """Comprehensive health monitoring system."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.health_checks: Dict[str, HealthCheck] = {}
        self.health_status: Dict[str, HealthStatus] = {}
        self.failure_history: List[FailureEvent] = []
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._running = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize health monitoring."""
        try:
            # Register default health checks
            self._register_default_health_checks()
            
            # Initialize circuit breakers
            self._initialize_circuit_breakers()
            
            logger.info("Health monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize health monitor: {e}")
            raise
            
    def _register_default_health_checks(self):
        """Register default health checks."""
        self.register_health_check(
            "system_resources",
            self._check_system_resources,
            interval_seconds=30
        )
        
        self.register_health_check(
            "redis_connection",
            self._check_redis_connection,
            interval_seconds=15
        )
        
        self.register_health_check(
            "database_connection",
            self._check_database_connection,
            interval_seconds=30
        )
        
        self.register_health_check(
            "external_apis",
            self._check_external_apis,
            interval_seconds=60
        )
        
    def _initialize_circuit_breakers(self):
        """Initialize circuit breakers for external services."""
        self.circuit_breakers["redis"] = CircuitBreaker("redis", failure_threshold=3, recovery_timeout=30)
        self.circuit_breakers["database"] = CircuitBreaker("database", failure_threshold=5, recovery_timeout=60)
        self.circuit_breakers["external_api"] = CircuitBreaker("external_api", failure_threshold=3, recovery_timeout=120)
        
    def register_health_check(self, name: str, check_function: Callable, **kwargs):
        """Register a health check."""
        health_check = HealthCheck(name=name, check_function=check_function, **kwargs)
        self.health_checks[name] = health_check
        logger.info(f"Registered health check: {name}")
        
    async def start_monitoring(self):
        """Start health monitoring."""
        if self._running:
            return
            
        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Health monitoring started")
        
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                # Run all health checks
                tasks = []
                for name, health_check in self.health_checks.items():
                    if health_check.enabled:
                        task = asyncio.create_task(self._run_health_check(name, health_check))
                        tasks.append(task)
                        
                # Wait for all checks to complete
                await asyncio.gather(*tasks, return_exceptions=True)
                
                # Check for failures and trigger recovery
                await self._check_for_failures()
                
                # Wait before next check cycle
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)
                
    async def _run_health_check(self, name: str, health_check: HealthCheck):
        """Run a single health check."""
        try:
            start_time = time.time()
            
            # Execute health check with timeout
            result = await asyncio.wait_for(
                health_check.check_function(),
                timeout=health_check.timeout_seconds
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Update health status
            self.health_status[name] = HealthStatus(
                service_name=name,
                status=HealthStatus.HEALTHY if result else HealthStatus.UNHEALTHY,
                last_check=datetime.utcnow(),
                response_time_ms=response_time,
                metrics=result if isinstance(result, dict) else {}
            )
            
        except asyncio.TimeoutError:
            self.health_status[name] = HealthStatus(
                service_name=name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.utcnow(),
                response_time_ms=health_check.timeout_seconds * 1000,
                error_message="Health check timeout"
            )
            
        except Exception as e:
            self.health_status[name] = HealthStatus(
                service_name=name,
                status=HealthStatus.UNHEALTHY,
                last_check=datetime.utcnow(),
                response_time_ms=0.0,
                error_message=str(e)
            )
            
    async def _check_for_failures(self):
        """Check for failures and trigger recovery."""
        for name, status in self.health_status.items():
            if status.status == HealthStatus.UNHEALTHY:
                await self._handle_failure(name, status)
                
    async def _handle_failure(self, service_name: str, status: HealthStatus):
        """Handle service failure."""
        try:
            # Determine failure type
            failure_type = self._determine_failure_type(service_name, status)
            
            # Create failure event
            failure_event = FailureEvent(
                failure_id=str(uuid4()),
                failure_type=failure_type,
                service_name=service_name,
                occurred_at=datetime.utcnow(),
                error_message=status.error_message or "Unknown error",
                recovery_strategy=self._get_recovery_strategy(failure_type)
            )
            
            # Add to failure history
            self.failure_history.append(failure_event)
            
            # Trigger recovery
            await self._trigger_recovery(failure_event)
            
            logger.warning(f"Failure detected in {service_name}: {failure_event.error_message}")
            
        except Exception as e:
            logger.error(f"Failed to handle failure for {service_name}: {e}")
            
    def _determine_failure_type(self, service_name: str, status: HealthStatus) -> FailureType:
        """Determine failure type based on service and error."""
        if "redis" in service_name.lower():
            return FailureType.REDIS_CONNECTION
        elif "database" in service_name.lower():
            return FailureType.DATABASE_CONNECTION
        elif "api" in service_name.lower():
            return FailureType.EXTERNAL_API
        elif "memory" in status.error_message.lower():
            return FailureType.HIGH_MEMORY_USAGE
        elif "cpu" in status.error_message.lower():
            return FailureType.HIGH_CPU_USAGE
        elif "disk" in status.error_message.lower():
            return FailureType.DISK_SPACE_LOW
        elif "timeout" in status.error_message.lower():
            return FailureType.NETWORK_TIMEOUT
        else:
            return FailureType.SERVICE_UNAVAILABLE
            
    def _get_recovery_strategy(self, failure_type: FailureType) -> RecoveryStrategy:
        """Get recovery strategy for failure type."""
        strategy_map = {
            FailureType.REDIS_CONNECTION: RecoveryStrategy.RETRY,
            FailureType.DATABASE_CONNECTION: RecoveryStrategy.RETRY,
            FailureType.EXTERNAL_API: RecoveryStrategy.CIRCUIT_BREAKER,
            FailureType.HIGH_MEMORY_USAGE: RecoveryStrategy.RESTART,
            FailureType.HIGH_CPU_USAGE: RecoveryStrategy.GRACEFUL_DEGRADATION,
            FailureType.DISK_SPACE_LOW: RecoveryStrategy.FAILOVER,
            FailureType.NETWORK_TIMEOUT: RecoveryStrategy.RETRY,
            FailureType.SERVICE_UNAVAILABLE: RecoveryStrategy.FALLBACK
        }
        
        return strategy_map.get(failure_type, RecoveryStrategy.RETRY)
        
    async def _trigger_recovery(self, failure_event: FailureEvent):
        """Trigger recovery based on strategy."""
        try:
            if failure_event.recovery_strategy == RecoveryStrategy.RETRY:
                await self._retry_recovery(failure_event)
            elif failure_event.recovery_strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                await self._circuit_breaker_recovery(failure_event)
            elif failure_event.recovery_strategy == RecoveryStrategy.GRACEFUL_DEGRADATION:
                await self._graceful_degradation_recovery(failure_event)
            elif failure_event.recovery_strategy == RecoveryStrategy.FAILOVER:
                await self._failover_recovery(failure_event)
            elif failure_event.recovery_strategy == RecoveryStrategy.RESTART:
                await self._restart_recovery(failure_event)
            else:
                await self._fallback_recovery(failure_event)
                
        except Exception as e:
            logger.error(f"Recovery failed for {failure_event.service_name}: {e}")
            
    async def _retry_recovery(self, failure_event: FailureEvent):
        """Retry recovery strategy."""
        # Implement retry logic with exponential backoff
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            try:
                await asyncio.sleep(base_delay * (2 ** attempt))
                
                # Attempt to recover the service
                if await self._attempt_service_recovery(failure_event.service_name):
                    failure_event.resolved_at = datetime.utcnow()
                    failure_event.resolution_time_seconds = (failure_event.resolved_at - failure_event.occurred_at).total_seconds()
                    logger.info(f"Service {failure_event.service_name} recovered after {attempt + 1} attempts")
                    return
                    
            except Exception as e:
                logger.warning(f"Retry attempt {attempt + 1} failed for {failure_event.service_name}: {e}")
                
        logger.error(f"Failed to recover {failure_event.service_name} after {max_retries} attempts")
        
    async def _circuit_breaker_recovery(self, failure_event: FailureEvent):
        """Circuit breaker recovery strategy."""
        circuit_breaker = self.circuit_breakers.get(failure_event.service_name)
        if circuit_breaker:
            # Circuit breaker will handle the failure automatically
            logger.info(f"Circuit breaker activated for {failure_event.service_name}")
        else:
            # Fall back to retry
            await self._retry_recovery(failure_event)
            
    async def _graceful_degradation_recovery(self, failure_event: FailureEvent):
        """Graceful degradation recovery strategy."""
        # Reduce service functionality but keep core features working
        logger.info(f"Implementing graceful degradation for {failure_event.service_name}")
        
        # This would implement service-specific degradation logic
        # For example, disable non-essential features, reduce cache TTL, etc.
        
    async def _failover_recovery(self, failure_event: FailureEvent):
        """Failover recovery strategy."""
        # Switch to backup/standby service
        logger.info(f"Implementing failover for {failure_event.service_name}")
        
        # This would implement failover logic
        # For example, switch to backup database, use CDN fallback, etc.
        
    async def _restart_recovery(self, failure_event: FailureEvent):
        """Restart recovery strategy."""
        # Restart the service
        logger.info(f"Restarting service {failure_event.service_name}")
        
        # This would implement service restart logic
        # For example, restart containers, reload configurations, etc.
        
    async def _fallback_recovery(self, failure_event: FailureEvent):
        """Fallback recovery strategy."""
        # Use alternative service or cached data
        logger.info(f"Implementing fallback for {failure_event.service_name}")
        
        # This would implement fallback logic
        # For example, use cached data, switch to alternative API, etc.
        
    async def _attempt_service_recovery(self, service_name: str) -> bool:
        """Attempt to recover a specific service."""
        try:
            # Get the health check for this service
            health_check = self.health_checks.get(service_name)
            if not health_check:
                return False
                
            # Run the health check
            result = await health_check.check_function()
            
            # Update status if successful
            if result:
                self.health_status[service_name].status = HealthStatus.HEALTHY
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Service recovery attempt failed for {service_name}: {e}")
            return False
            
    # Default health check implementations
    async def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Check thresholds
            cpu_healthy = cpu_percent < 80
            memory_healthy = memory.percent < 85
            disk_healthy = disk.percent < 90
            
            overall_healthy = cpu_healthy and memory_healthy and disk_healthy
            
            return {
                "healthy": overall_healthy,
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": disk.percent,
                "cpu_healthy": cpu_healthy,
                "memory_healthy": memory_healthy,
                "disk_healthy": disk_healthy
            }
            
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {"healthy": False, "error": str(e)}
            
    async def _check_redis_connection(self) -> Dict[str, Any]:
        """Check Redis connection health."""
        try:
            start_time = time.time()
            await self.redis.ping()
            response_time = (time.time() - start_time) * 1000
            
            # Check response time threshold
            healthy = response_time < 100  # 100ms threshold
            
            return {
                "healthy": healthy,
                "response_time_ms": response_time,
                "connection_active": True
            }
            
        except Exception as e:
            logger.error(f"Redis connection check failed: {e}")
            return {"healthy": False, "error": str(e)}
            
    async def _check_database_connection(self) -> Dict[str, Any]:
        """Check database connection health."""
        try:
            # This would implement actual database health check
            # For now, return a placeholder
            return {
                "healthy": True,
                "connection_active": True,
                "response_time_ms": 10.0
            }
            
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return {"healthy": False, "error": str(e)}
            
    async def _check_external_apis(self) -> Dict[str, Any]:
        """Check external API health."""
        try:
            # Check critical external APIs
            apis_to_check = [
                "https://httpbin.org/status/200",  # Test API
                # Add actual external APIs here
            ]
            
            healthy_apis = 0
            total_apis = len(apis_to_check)
            
            async with aiohttp.ClientSession(timeout=ClientTimeout(total=5)) as session:
                for api_url in apis_to_check:
                    try:
                        async with session.get(api_url) as response:
                            if response.status == 200:
                                healthy_apis += 1
                    except Exception:
                        pass
                        
            healthy = healthy_apis >= total_apis * 0.8  # 80% threshold
            
            return {
                "healthy": healthy,
                "healthy_apis": healthy_apis,
                "total_apis": total_apis,
                "health_percentage": (healthy_apis / total_apis * 100) if total_apis > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"External APIs check failed: {e}")
            return {"healthy": False, "error": str(e)}
            
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary."""
        try:
            # Calculate overall health
            total_checks = len(self.health_status)
            healthy_checks = sum(1 for status in self.health_status.values() if status.status == HealthStatus.HEALTHY)
            
            overall_health = "healthy" if healthy_checks == total_checks else "degraded" if healthy_checks > total_checks * 0.5 else "unhealthy"
            
            # Get recent failures
            recent_failures = [
                {
                    "service_name": failure.service_name,
                    "failure_type": failure.failure_type.value,
                    "occurred_at": failure.occurred_at.isoformat(),
                    "error_message": failure.error_message,
                    "resolved": failure.resolved_at is not None
                }
                for failure in self.failure_history[-10:]  # Last 10 failures
            ]
            
            # Get circuit breaker states
            circuit_breaker_states = {
                name: {
                    "state": breaker.get_state().state,
                    "failure_count": breaker.get_state().failure_count,
                    "last_failure_time": breaker.get_state().last_failure_time.isoformat() if breaker.get_state().last_failure_time else None
                }
                for name, breaker in self.circuit_breakers.items()
            }
            
            return {
                "overall_health": overall_health,
                "total_checks": total_checks,
                "healthy_checks": healthy_checks,
                "health_percentage": (healthy_checks / total_checks * 100) if total_checks > 0 else 0,
                "service_status": {
                    name: {
                        "status": status.status.value,
                        "last_check": status.last_check.isoformat(),
                        "response_time_ms": status.response_time_ms,
                        "error_message": status.error_message
                    }
                    for name, status in self.health_status.items()
                },
                "recent_failures": recent_failures,
                "circuit_breakers": circuit_breaker_states,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get health summary: {e}")
            return {"error": str(e)}
            
    async def shutdown(self):
        """Shutdown health monitoring."""
        self._running = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
                
        logger.info("Health monitoring shutdown complete")


class DisasterRecovery:
    """Disaster recovery and backup management."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.backup_schedules: Dict[str, Dict[str, Any]] = {}
        self.restore_points: List[Dict[str, Any]] = []
        
    async def initialize(self):
        """Initialize disaster recovery."""
        try:
            # Set up default backup schedules
            self._setup_default_backups()
            
            logger.info("Disaster recovery initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize disaster recovery: {e}")
            raise
            
    def _setup_default_backups(self):
        """Set up default backup schedules."""
        self.backup_schedules = {
            "redis_data": {
                "interval_hours": 6,
                "retention_days": 7,
                "backup_function": self._backup_redis_data
            },
            "database_data": {
                "interval_hours": 24,
                "retention_days": 30,
                "backup_function": self._backup_database_data
            },
            "configuration": {
                "interval_hours": 24,
                "retention_days": 90,
                "backup_function": self._backup_configuration
            }
        }
        
    async def create_backup(self, backup_type: str) -> str:
        """Create a backup."""
        try:
            backup_id = str(uuid4())
            backup_info = {
                "backup_id": backup_id,
                "backup_type": backup_type,
                "created_at": datetime.utcnow().isoformat(),
                "status": "in_progress"
            }
            
            # Execute backup
            backup_function = self.backup_schedules[backup_type]["backup_function"]
            backup_data = await backup_function()
            
            # Store backup metadata
            backup_info.update({
                "status": "completed",
                "size_bytes": len(str(backup_data)),
                "data": backup_data
            })
            
            self.restore_points.append(backup_info)
            
            logger.info(f"Backup {backup_id} created successfully for {backup_type}")
            return backup_id
            
        except Exception as e:
            logger.error(f"Backup creation failed for {backup_type}: {e}")
            raise
            
    async def restore_backup(self, backup_id: str) -> bool:
        """Restore from backup."""
        try:
            # Find backup
            backup_info = None
            for backup in self.restore_points:
                if backup["backup_id"] == backup_id:
                    backup_info = backup
                    break
                    
            if not backup_info:
                raise ValueError(f"Backup {backup_id} not found")
                
            # Restore data
            await self._restore_data(backup_info)
            
            logger.info(f"Backup {backup_id} restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Backup restore failed for {backup_id}: {e}")
            return False
            
    async def _backup_redis_data(self) -> Dict[str, Any]:
        """Backup Redis data."""
        try:
            # Get all keys
            keys = await self.redis.keys("*")
            
            # Get data for each key
            backup_data = {}
            for key in keys:
                key_type = await self.redis.type(key)
                
                if key_type == "string":
                    backup_data[key] = await self.redis.get(key)
                elif key_type == "hash":
                    backup_data[key] = await self.redis.hgetall(key)
                elif key_type == "list":
                    backup_data[key] = await self.redis.lrange(key, 0, -1)
                elif key_type == "set":
                    backup_data[key] = await self.redis.smembers(key)
                elif key_type == "zset":
                    backup_data[key] = await self.redis.zrange(key, 0, -1, withscores=True)
                    
            return backup_data
            
        except Exception as e:
            logger.error(f"Redis backup failed: {e}")
            return {}
            
    async def _backup_database_data(self) -> Dict[str, Any]:
        """Backup database data."""
        # This would implement actual database backup
        # For now, return placeholder
        return {"status": "placeholder", "message": "Database backup not implemented"}
        
    async def _backup_configuration(self) -> Dict[str, Any]:
        """Backup configuration data."""
        # This would implement configuration backup
        # For now, return placeholder
        return {"status": "placeholder", "message": "Configuration backup not implemented"}
        
    async def _restore_data(self, backup_info: Dict[str, Any]):
        """Restore data from backup."""
        backup_type = backup_info["backup_type"]
        
        if backup_type == "redis_data":
            await self._restore_redis_data(backup_info["data"])
        elif backup_type == "database_data":
            await self._restore_database_data(backup_info["data"])
        elif backup_type == "configuration":
            await self._restore_configuration(backup_info["data"])
            
    async def _restore_redis_data(self, data: Dict[str, Any]):
        """Restore Redis data."""
        try:
            # Clear existing data
            await self.redis.flushdb()
            
            # Restore data
            for key, value in data.items():
                if isinstance(value, str):
                    await self.redis.set(key, value)
                elif isinstance(value, dict):
                    await self.redis.hmset(key, value)
                elif isinstance(value, list):
                    for item in value:
                        await self.redis.lpush(key, item)
                        
        except Exception as e:
            logger.error(f"Redis restore failed: {e}")
            raise
            
    async def _restore_database_data(self, data: Dict[str, Any]):
        """Restore database data."""
        # This would implement actual database restore
        pass
        
    async def _restore_configuration(self, data: Dict[str, Any]):
        """Restore configuration data."""
        # This would implement configuration restore
        pass


class FaultToleranceManager:
    """Main fault tolerance manager coordinating all components."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
        self.health_monitor: Optional[HealthMonitor] = None
        self.disaster_recovery: Optional[DisasterRecovery] = None
        
    async def initialize(self):
        """Initialize fault tolerance manager."""
        try:
            # Initialize Redis connection
            self.redis = await aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Redis connection established for fault tolerance manager")
            
            # Initialize components
            self.health_monitor = HealthMonitor(self.redis)
            self.disaster_recovery = DisasterRecovery(self.redis)
            
            await self.health_monitor.initialize()
            await self.disaster_recovery.initialize()
            
            # Start monitoring
            await self.health_monitor.start_monitoring()
            
            logger.info("Fault tolerance manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize fault tolerance manager: {e}")
            raise
            
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health."""
        return await self.health_monitor.get_health_summary()
        
    async def create_emergency_backup(self) -> str:
        """Create emergency backup."""
        return await self.disaster_recovery.create_backup("redis_data")
        
    async def shutdown(self):
        """Shutdown fault tolerance manager."""
        if self.health_monitor:
            await self.health_monitor.shutdown()
            
        if self.redis:
            await self.redis.close()
            
        logger.info("Fault tolerance manager shutdown complete")


# Global fault tolerance manager instance
fault_tolerance_manager = FaultToleranceManager()


async def get_fault_tolerance_manager() -> FaultToleranceManager:
    """Get the global fault tolerance manager instance."""
    if not fault_tolerance_manager.redis:
        await fault_tolerance_manager.initialize()
    return fault_tolerance_manager