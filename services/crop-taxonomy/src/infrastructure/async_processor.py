"""
Async Processing and Background Job Management System

This module implements async processing, background jobs, queue management,
and batch processing for scalable variety recommendation operations.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union, Callable, TypeVar, Generic
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import aioredis
from aioredis import Redis
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
import pickle
import signal
import threading

logger = logging.getLogger(__name__)

T = TypeVar('T')


class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class JobPriority(Enum):
    """Job priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class QueueType(Enum):
    """Queue types for different job categories."""
    RECOMMENDATIONS = "recommendations"
    DATA_PROCESSING = "data_processing"
    BATCH_OPERATIONS = "batch_operations"
    CLEANUP = "cleanup"
    NOTIFICATIONS = "notifications"


@dataclass
class Job(Generic[T]):
    """Represents a background job."""
    job_id: str
    job_type: str
    queue_type: QueueType
    priority: JobPriority
    payload: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[T] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    tags: List[str] = field(default_factory=list)
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QueueStats:
    """Queue performance statistics."""
    queue_name: str
    pending_jobs: int = 0
    running_jobs: int = 0
    completed_jobs: int = 0
    failed_jobs: int = 0
    avg_processing_time_ms: float = 0.0
    throughput_per_minute: float = 0.0


class JobQueue:
    """Redis-based job queue with priority support."""
    
    def __init__(self, redis: Redis, queue_name: str):
        self.redis = redis
        self.queue_name = queue_name
        self.pending_key = f"queue:{queue_name}:pending"
        self.running_key = f"queue:{queue_name}:running"
        self.completed_key = f"queue:{queue_name}:completed"
        self.failed_key = f"queue:{queue_name}:failed"
        self.job_data_key = f"queue:{queue_name}:jobs"
        
    async def enqueue(self, job: Job[T]) -> str:
        """Add a job to the queue."""
        try:
            # Serialize job data
            job_data = pickle.dumps(job)
            
            # Store job data
            await self.redis.hset(self.job_data_key, job.job_id, job_data)
            
            # Add to pending queue with priority score
            priority_score = job.priority.value
            await self.redis.zadd(self.pending_key, {job.job_id: priority_score})
            
            logger.info(f"Job {job.job_id} enqueued in {self.queue_name}")
            return job.job_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue job {job.job_id}: {e}")
            raise
            
    async def dequeue(self, timeout: int = 10) -> Optional[Job[T]]:
        """Get the next job from the queue."""
        try:
            # Get highest priority job
            result = await self.redis.bzpopmax(self.pending_key, timeout=timeout)
            if not result:
                return None
                
            queue_name, job_id, score = result
            
            # Get job data
            job_data = await self.redis.hget(self.job_data_key, job_id)
            if not job_data:
                logger.warning(f"Job data not found for {job_id}")
                return None
                
            job = pickle.loads(job_data)
            
            # Move to running queue
            await self.redis.zadd(self.running_key, {job_id: time.time()})
            
            # Update job status
            job.status = JobStatus.RUNNING
            job.started_at = datetime.utcnow()
            await self._update_job(job)
            
            return job
            
        except Exception as e:
            logger.error(f"Failed to dequeue job: {e}")
            return None
            
    async def complete_job(self, job_id: str, result: T = None, error: str = None):
        """Mark a job as completed."""
        try:
            # Get job data
            job_data = await self.redis.hget(self.job_data_key, job_id)
            if not job_data:
                logger.warning(f"Job data not found for {job_id}")
                return
                
            job = pickle.loads(job_data)
            
            # Update job status
            job.completed_at = datetime.utcnow()
            if error:
                job.status = JobStatus.FAILED
                job.error = error
                await self.redis.zadd(self.failed_key, {job_id: time.time()})
            else:
                job.status = JobStatus.COMPLETED
                job.result = result
                await self.redis.zadd(self.completed_key, {job_id: time.time()})
                
            # Remove from running queue
            await self.redis.zrem(self.running_key, job_id)
            
            # Update job data
            await self._update_job(job)
            
            logger.info(f"Job {job_id} completed with status {job.status.value}")
            
        except Exception as e:
            logger.error(f"Failed to complete job {job_id}: {e}")
            
    async def retry_job(self, job_id: str, error: str):
        """Retry a failed job."""
        try:
            # Get job data
            job_data = await self.redis.hget(self.job_data_key, job_id)
            if not job_data:
                logger.warning(f"Job data not found for {job_id}")
                return
                
            job = pickle.loads(job_data)
            
            # Check retry limit
            if job.retry_count >= job.max_retries:
                logger.warning(f"Job {job_id} exceeded max retries")
                await self.complete_job(job_id, error=f"Max retries exceeded: {error}")
                return
                
            # Update retry count
            job.retry_count += 1
            job.status = JobStatus.RETRYING
            job.error = error
            
            # Remove from running queue
            await self.redis.zrem(self.running_key, job_id)
            
            # Re-enqueue with lower priority
            job.priority = JobPriority(max(1, job.priority.value - 1))
            await self.enqueue(job)
            
            logger.info(f"Job {job_id} retried (attempt {job.retry_count})")
            
        except Exception as e:
            logger.error(f"Failed to retry job {job_id}: {e}")
            
    async def _update_job(self, job: Job[T]):
        """Update job data in Redis."""
        job_data = pickle.dumps(job)
        await self.redis.hset(self.job_data_key, job.job_id, job_data)
        
    async def get_job(self, job_id: str) -> Optional[Job[T]]:
        """Get job by ID."""
        try:
            job_data = await self.redis.hget(self.job_data_key, job_id)
            if job_data:
                return pickle.loads(job_data)
            return None
        except Exception as e:
            logger.error(f"Failed to get job {job_id}: {e}")
            return None
            
    async def get_queue_stats(self) -> QueueStats:
        """Get queue statistics."""
        try:
            pending_count = await self.redis.zcard(self.pending_key)
            running_count = await self.redis.zcard(self.running_key)
            completed_count = await self.redis.zcard(self.completed_key)
            failed_count = await self.redis.zcard(self.failed_key)
            
            # Calculate average processing time
            completed_jobs = await self.redis.zrange(self.completed_key, 0, -1, withscores=True)
            avg_time = 0.0
            if completed_jobs:
                total_time = 0.0
                for job_id, completion_time in completed_jobs:
                    job = await self.get_job(job_id)
                    if job and job.started_at:
                        processing_time = (job.completed_at - job.started_at).total_seconds()
                        total_time += processing_time
                avg_time = total_time / len(completed_jobs) * 1000  # Convert to ms
                
            return QueueStats(
                queue_name=self.queue_name,
                pending_jobs=pending_count,
                running_jobs=running_count,
                completed_jobs=completed_count,
                failed_jobs=failed_count,
                avg_processing_time_ms=avg_time
            )
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}")
            return QueueStats(queue_name=self.queue_name)


class AsyncProcessor:
    """Main async processor managing background jobs and queues."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
        self.queues: Dict[QueueType, JobQueue] = {}
        self.workers: Dict[str, asyncio.Task] = {}
        self.job_handlers: Dict[str, Callable] = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        self._running = False
        self._shutdown_event = asyncio.Event()
        
    async def initialize(self):
        """Initialize the async processor."""
        try:
            # Initialize Redis connection
            self.redis = await aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Redis connection established for async processor")
            
            # Initialize queues
            for queue_type in QueueType:
                self.queues[queue_type] = JobQueue(self.redis, queue_type.value)
                
            # Register default job handlers
            self._register_default_handlers()
            
            logger.info("Async processor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize async processor: {e}")
            raise
            
    def _register_default_handlers(self):
        """Register default job handlers."""
        self.job_handlers.update({
            "variety_recommendation": self._handle_variety_recommendation,
            "batch_variety_search": self._handle_batch_variety_search,
            "data_cleanup": self._handle_data_cleanup,
            "cache_warmup": self._handle_cache_warmup,
            "report_generation": self._handle_report_generation
        })
        
    async def start_workers(self, num_workers_per_queue: int = 2):
        """Start background workers for each queue."""
        if self._running:
            return
            
        self._running = True
        
        for queue_type in QueueType:
            for i in range(num_workers_per_queue):
                worker_name = f"{queue_type.value}_worker_{i}"
                worker_task = asyncio.create_task(
                    self._worker_loop(queue_type, worker_name)
                )
                self.workers[worker_name] = worker_task
                
        logger.info(f"Started {len(self.workers)} background workers")
        
    async def _worker_loop(self, queue_type: QueueType, worker_name: str):
        """Worker loop for processing jobs."""
        logger.info(f"Worker {worker_name} started")
        
        while self._running:
            try:
                # Get next job
                job = await self.queues[queue_type].dequeue(timeout=5)
                if not job:
                    continue
                    
                logger.info(f"Worker {worker_name} processing job {job.job_id}")
                
                # Process job
                await self._process_job(job, worker_name)
                
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_name} cancelled")
                break
            except Exception as e:
                logger.error(f"Worker {worker_name} error: {e}")
                await asyncio.sleep(1)
                
        logger.info(f"Worker {worker_name} stopped")
        
    async def _process_job(self, job: Job[T], worker_name: str):
        """Process a single job."""
        try:
            # Get job handler
            handler = self.job_handlers.get(job.job_type)
            if not handler:
                await self.queues[job.queue_type].complete_job(
                    job.job_id, 
                    error=f"Unknown job type: {job.job_type}"
                )
                return
                
            # Execute job with timeout
            try:
                result = await asyncio.wait_for(
                    handler(job),
                    timeout=job.timeout_seconds
                )
                await self.queues[job.queue_type].complete_job(job.job_id, result)
                
            except asyncio.TimeoutError:
                await self.queues[job.queue_type].retry_job(
                    job.job_id,
                    f"Job timeout after {job.timeout_seconds} seconds"
                )
                
        except Exception as e:
            logger.error(f"Job processing error for {job.job_id}: {e}")
            await self.queues[job.queue_type].retry_job(job.job_id, str(e))
            
    async def submit_job(self, 
                        job_type: str,
                        payload: Dict[str, Any],
                        queue_type: QueueType = QueueType.RECOMMENDATIONS,
                        priority: JobPriority = JobPriority.NORMAL,
                        tags: List[str] = None,
                        timeout_seconds: int = 300,
                        max_retries: int = 3) -> str:
        """Submit a job for background processing."""
        job_id = str(uuid4())
        
        job = Job(
            job_id=job_id,
            job_type=job_type,
            queue_type=queue_type,
            priority=priority,
            payload=payload,
            tags=tags or [],
            timeout_seconds=timeout_seconds,
            max_retries=max_retries
        )
        
        await self.queues[queue_type].enqueue(job)
        return job_id
        
    async def get_job_status(self, job_id: str) -> Optional[Job[T]]:
        """Get job status by ID."""
        for queue in self.queues.values():
            job = await queue.get_job(job_id)
            if job:
                return job
        return None
        
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        for queue in self.queues.values():
            # Check if job is in pending queue
            score = await queue.redis.zscore(queue.pending_key, job_id)
            if score is not None:
                await queue.redis.zrem(queue.pending_key, job_id)
                await queue.complete_job(job_id, error="Job cancelled")
                return True
        return False
        
    async def get_queue_stats(self) -> Dict[str, QueueStats]:
        """Get statistics for all queues."""
        stats = {}
        for queue_type, queue in self.queues.items():
            stats[queue_type.value] = await queue.get_queue_stats()
        return stats
        
    def register_handler(self, job_type: str, handler: Callable):
        """Register a custom job handler."""
        self.job_handlers[job_type] = handler
        logger.info(f"Registered handler for job type: {job_type}")
        
    # Default job handlers
    async def _handle_variety_recommendation(self, job: Job[T]) -> Dict[str, Any]:
        """Handle variety recommendation job."""
        try:
            # Import here to avoid circular imports
            from ..services.variety_recommendation_service import VarietyRecommendationService
            
            service = VarietyRecommendationService()
            payload = job.payload
            
            # Generate recommendations
            recommendations = await service.get_variety_recommendations(
                crop_id=payload.get("crop_id"),
                location=payload.get("location"),
                soil_data=payload.get("soil_data"),
                preferences=payload.get("preferences", {})
            )
            
            return {
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat(),
                "job_id": job.job_id
            }
            
        except Exception as e:
            logger.error(f"Variety recommendation job failed: {e}")
            raise
            
    async def _handle_batch_variety_search(self, job: Job[T]) -> Dict[str, Any]:
        """Handle batch variety search job."""
        try:
            from ..services.crop_search_service import CropSearchService
            
            service = CropSearchService()
            payload = job.payload
            
            # Process batch search
            results = await service.batch_search_varieties(
                search_queries=payload.get("queries", []),
                filters=payload.get("filters", {}),
                limit=payload.get("limit", 100)
            )
            
            return {
                "results": results,
                "total_queries": len(payload.get("queries", [])),
                "processed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Batch variety search job failed: {e}")
            raise
            
    async def _handle_data_cleanup(self, job: Job[T]) -> Dict[str, Any]:
        """Handle data cleanup job."""
        try:
            payload = job.payload
            cleanup_type = payload.get("type", "cache")
            
            if cleanup_type == "cache":
                # Clean up expired cache entries
                from .distributed_cache import get_distributed_cache
                cache = await get_distributed_cache()
                
                # This would implement cache cleanup logic
                cleaned_count = 0  # Placeholder
                
                return {
                    "cleanup_type": cleanup_type,
                    "cleaned_entries": cleaned_count,
                    "cleaned_at": datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Data cleanup job failed: {e}")
            raise
            
    async def _handle_cache_warmup(self, job: Job[T]) -> Dict[str, Any]:
        """Handle cache warmup job."""
        try:
            payload = job.payload
            cache_keys = payload.get("keys", [])
            
            # Warm up cache with frequently accessed data
            warmed_count = 0
            for key in cache_keys:
                # This would implement cache warming logic
                warmed_count += 1
                
            return {
                "warmed_keys": warmed_count,
                "warmed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Cache warmup job failed: {e}")
            raise
            
    async def _handle_report_generation(self, job: Job[T]) -> Dict[str, Any]:
        """Handle report generation job."""
        try:
            payload = job.payload
            report_type = payload.get("type", "summary")
            
            # Generate report
            report_data = {
                "type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "data": payload.get("data", {})
            }
            
            return report_data
            
        except Exception as e:
            logger.error(f"Report generation job failed: {e}")
            raise
            
    async def shutdown(self):
        """Shutdown the async processor."""
        logger.info("Shutting down async processor...")
        
        self._running = False
        
        # Cancel all workers
        for worker_name, worker_task in self.workers.items():
            worker_task.cancel()
            
        # Wait for workers to finish
        if self.workers:
            await asyncio.gather(*self.workers.values(), return_exceptions=True)
            
        # Shutdown thread pools
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)
        
        # Close Redis connection
        if self.redis:
            await self.redis.close()
            
        logger.info("Async processor shutdown complete")


# Global async processor instance
async_processor = AsyncProcessor()


async def get_async_processor() -> AsyncProcessor:
    """Get the global async processor instance."""
    if not async_processor.redis:
        await async_processor.initialize()
        await async_processor.start_workers()
    return async_processor