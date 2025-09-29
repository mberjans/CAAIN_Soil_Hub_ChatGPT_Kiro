"""
Comprehensive Scalability Infrastructure Integration

This module integrates all scalability components into a unified system
for the crop variety recommendation service.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import aioredis
from aioredis import Redis

# Import all scalability components
from .scalability_manager import ScalabilityManager, get_scalability_manager
from .distributed_cache import DistributedCache, get_distributed_cache
from .async_processor import AsyncProcessor, get_async_processor
from .capacity_planner import CapacityPlanner, get_capacity_planner
from .fault_tolerance import FaultToleranceManager, get_fault_tolerance_manager

logger = logging.getLogger(__name__)


@dataclass
class ScalabilityConfig:
    """Configuration for scalability infrastructure."""
    redis_url: str = "redis://localhost:6379"
    enable_load_balancing: bool = True
    enable_auto_scaling: bool = True
    enable_distributed_cache: bool = True
    enable_async_processing: bool = True
    enable_capacity_planning: bool = True
    enable_fault_tolerance: bool = True
    max_instances: int = 10
    min_instances: int = 2
    cache_strategy: str = "cache_aside"
    health_check_interval: int = 30
    backup_interval_hours: int = 6


class ScalabilityInfrastructure:
    """Main scalability infrastructure coordinator."""
    
    def __init__(self, config: ScalabilityConfig = None):
        self.config = config or ScalabilityConfig()
        self.redis: Optional[Redis] = None
        self.scalability_manager: Optional[ScalabilityManager] = None
        self.distributed_cache: Optional[DistributedCache] = None
        self.async_processor: Optional[AsyncProcessor] = None
        self.capacity_planner: Optional[CapacityPlanner] = None
        self.fault_tolerance_manager: Optional[FaultToleranceManager] = None
        self._initialized = False
        self._running = False
        
    async def initialize(self):
        """Initialize all scalability components."""
        if self._initialized:
            return
            
        try:
            logger.info("Initializing scalability infrastructure...")
            
            # Initialize Redis connection
            self.redis = await aioredis.from_url(self.config.redis_url)
            await self.redis.ping()
            logger.info("Redis connection established")
            
            # Initialize components based on configuration
            if self.config.enable_load_balancing or self.config.enable_auto_scaling:
                self.scalability_manager = await get_scalability_manager()
                logger.info("Scalability manager initialized")
                
            if self.config.enable_distributed_cache:
                self.distributed_cache = await get_distributed_cache()
                logger.info("Distributed cache initialized")
                
            if self.config.enable_async_processing:
                self.async_processor = await get_async_processor()
                logger.info("Async processor initialized")
                
            if self.config.enable_capacity_planning:
                self.capacity_planner = await get_capacity_planner()
                logger.info("Capacity planner initialized")
                
            if self.config.enable_fault_tolerance:
                self.fault_tolerance_manager = await get_fault_tolerance_manager()
                logger.info("Fault tolerance manager initialized")
                
            self._initialized = True
            logger.info("Scalability infrastructure initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scalability infrastructure: {e}")
            raise
            
    async def start(self):
        """Start all scalability services."""
        if not self._initialized:
            await self.initialize()
            
        if self._running:
            return
            
        try:
            logger.info("Starting scalability services...")
            
            # Start monitoring and auto-scaling
            if self.scalability_manager:
                await self.scalability_manager.start_monitoring()
                
            # Start async processing workers
            if self.async_processor:
                await self.async_processor.start_workers()
                
            self._running = True
            logger.info("Scalability services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start scalability services: {e}")
            raise
            
    async def add_service_instance(self, 
                                 instance_id: str,
                                 host: str,
                                 port: int,
                                 health_endpoint: str = "/health",
                                 weight: int = 1):
        """Add a service instance to the load balancer."""
        if self.scalability_manager:
            await self.scalability_manager.add_service_instance(
                instance_id, host, port, health_endpoint, weight
            )
            logger.info(f"Added service instance {instance_id}")
            
    async def submit_background_job(self, 
                                  job_type: str,
                                  payload: Dict[str, Any],
                                  priority: str = "normal") -> str:
        """Submit a job for background processing."""
        if self.async_processor:
            from .async_processor import JobPriority
            priority_enum = JobPriority[priority.upper()]
            
            job_id = await self.async_processor.submit_job(
                job_type=job_type,
                payload=payload,
                priority=priority_enum
            )
            logger.info(f"Submitted background job {job_id}")
            return job_id
            
        raise RuntimeError("Async processor not available")
        
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a background job."""
        if self.async_processor:
            job = await self.async_processor.get_job_status(job_id)
            if job:
                return {
                    "job_id": job.job_id,
                    "status": job.status.value,
                    "created_at": job.created_at.isoformat(),
                    "started_at": job.started_at.isoformat() if job.started_at else None,
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                    "progress": job.progress,
                    "error": job.error
                }
        return None
        
    async def cache_get(self, key: str, data_type: str = "general") -> Optional[Any]:
        """Get value from distributed cache."""
        if self.distributed_cache:
            return await self.distributed_cache.get(key, data_type)
        return None
        
    async def cache_set(self, key: str, value: Any, ttl: int = 3600, 
                      data_type: str = "general", tags: List[str] = None):
        """Set value in distributed cache."""
        if self.distributed_cache:
            await self.distributed_cache.set(key, value, ttl, data_type, set(tags or []))
            
    async def cache_invalidate(self, tags: List[str]):
        """Invalidate cache entries by tags."""
        if self.distributed_cache:
            await self.distributed_cache.invalidate_by_tags(set(tags))
            
    async def generate_capacity_plan(self, 
                                   planning_horizon_months: int = 6,
                                   current_users: int = 1000) -> Dict[str, Any]:
        """Generate capacity planning report."""
        if self.capacity_planner:
            return await self.capacity_planner.generate_capacity_plan(
                planning_horizon_months, current_users
            )
        return {"error": "Capacity planner not available"}
        
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health."""
        if self.fault_tolerance_manager:
            return await self.fault_tolerance_manager.get_system_health()
        return {"error": "Fault tolerance manager not available"}
        
    async def create_backup(self, backup_type: str = "redis_data") -> str:
        """Create system backup."""
        if self.fault_tolerance_manager:
            return await self.fault_tolerance_manager.create_emergency_backup()
        raise RuntimeError("Fault tolerance manager not available")
        
    async def get_scalability_metrics(self) -> Dict[str, Any]:
        """Get comprehensive scalability metrics."""
        try:
            metrics = {
                "timestamp": datetime.utcnow().isoformat(),
                "components": {}
            }
            
            # Get metrics from each component
            if self.scalability_manager:
                metrics["components"]["scalability_manager"] = {
                    "status": "active",
                    "instances": len(self.scalability_manager.load_balancer.instances),
                    "healthy_instances": len([i for i in self.scalability_manager.load_balancer.instances if i.is_healthy])
                }
                
            if self.distributed_cache:
                cache_stats = await self.distributed_cache.get_cache_stats()
                metrics["components"]["distributed_cache"] = {
                    "status": "active",
                    "stats": cache_stats
                }
                
            if self.async_processor:
                queue_stats = await self.async_processor.get_queue_stats()
                processor_status = self.async_processor.get_status()
                metrics["components"]["async_processor"] = {
                    "status": "active",
                    "queue_stats": queue_stats,
                    "processor_status": processor_status
                }
                
            if self.capacity_planner:
                metrics["components"]["capacity_planner"] = {
                    "status": "active"
                }
                
            if self.fault_tolerance_manager:
                health_summary = await self.fault_tolerance_manager.get_system_health()
                metrics["components"]["fault_tolerance"] = {
                    "status": "active",
                    "overall_health": health_summary.get("overall_health", "unknown")
                }
                
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get scalability metrics: {e}")
            return {"error": str(e)}
            
    async def shutdown(self):
        """Shutdown all scalability components."""
        if not self._running:
            return
            
        logger.info("Shutting down scalability infrastructure...")
        
        try:
            # Shutdown components
            if self.scalability_manager:
                await self.scalability_manager.shutdown()
                
            if self.async_processor:
                await self.async_processor.shutdown()
                
            if self.distributed_cache:
                await self.distributed_cache.shutdown()
                
            if self.fault_tolerance_manager:
                await self.fault_tolerance_manager.shutdown()
                
            # Close Redis connection
            if self.redis:
                await self.redis.close()
                
            self._running = False
            logger.info("Scalability infrastructure shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


# Global scalability infrastructure instance
scalability_infrastructure = ScalabilityInfrastructure()


async def get_scalability_infrastructure() -> ScalabilityInfrastructure:
    """Get the global scalability infrastructure instance."""
    if not scalability_infrastructure._initialized:
        await scalability_infrastructure.initialize()
        await scalability_infrastructure.start()
    return scalability_infrastructure


# Convenience functions for common operations
async def submit_variety_recommendation_job(crop_id: str, 
                                          location: Dict[str, float],
                                          soil_data: Dict[str, Any],
                                          preferences: Dict[str, Any] = None) -> str:
    """Submit a variety recommendation job for background processing."""
    infrastructure = await get_scalability_infrastructure()
    
    payload = {
        "crop_id": crop_id,
        "location": location,
        "soil_data": soil_data,
        "preferences": preferences or {}
    }
    
    return await infrastructure.submit_background_job(
        job_type="variety_recommendation",
        payload=payload,
        priority="normal"
    )


async def submit_batch_variety_search_job(queries: List[str],
                                         filters: Dict[str, Any] = None,
                                         limit: int = 100) -> str:
    """Submit a batch variety search job for background processing."""
    infrastructure = await get_scalability_infrastructure()
    
    payload = {
        "queries": queries,
        "filters": filters or {},
        "limit": limit
    }
    
    return await infrastructure.submit_background_job(
        job_type="batch_variety_search",
        payload=payload,
        priority="low"
    )


async def cache_variety_data(variety_id: str, variety_data: Dict[str, Any], ttl: int = 3600):
    """Cache variety data in distributed cache."""
    infrastructure = await get_scalability_infrastructure()
    
    await infrastructure.cache_set(
        key=f"variety:{variety_id}",
        value=variety_data,
        ttl=ttl,
        data_type="variety_data",
        tags=["variety", "crop_data"]
    )


async def get_cached_variety_data(variety_id: str) -> Optional[Dict[str, Any]]:
    """Get cached variety data."""
    infrastructure = await get_scalability_infrastructure()
    
    return await infrastructure.cache_get(
        key=f"variety:{variety_id}",
        data_type="variety_data"
    )


async def invalidate_variety_cache():
    """Invalidate all variety-related cache entries."""
    infrastructure = await get_scalability_infrastructure()
    
    await infrastructure.cache_invalidate(["variety", "crop_data"])


async def get_system_status() -> Dict[str, Any]:
    """Get comprehensive system status."""
    infrastructure = await get_scalability_infrastructure()
    
    return await infrastructure.get_scalability_metrics()


async def create_system_backup() -> str:
    """Create a system backup."""
    infrastructure = await get_scalability_infrastructure()
    
    return await infrastructure.create_backup()


async def generate_capacity_report(planning_horizon_months: int = 6, 
                                 current_users: int = 1000) -> Dict[str, Any]:
    """Generate capacity planning report."""
    infrastructure = await get_scalability_infrastructure()
    
    return await infrastructure.generate_capacity_plan(
        planning_horizon_months, current_users
    )