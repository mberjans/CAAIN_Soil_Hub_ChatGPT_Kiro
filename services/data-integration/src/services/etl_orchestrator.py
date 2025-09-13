"""
ETL Orchestrator

Manages scheduled data extraction, transformation, and loading operations
for agricultural data sources.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import json
import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from .data_ingestion_framework import DataIngestionPipeline, IngestionResult

logger = structlog.get_logger(__name__)


class JobStatus(Enum):
    """ETL job status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class JobPriority(Enum):
    """ETL job priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ETLJobConfig:
    """Configuration for an ETL job."""
    job_id: str
    name: str
    description: str
    source_name: str
    operation: str
    parameters: Dict[str, Any]
    schedule_cron: Optional[str] = None  # Cron expression for scheduling
    schedule_interval_minutes: Optional[int] = None  # Interval in minutes
    priority: JobPriority = JobPriority.MEDIUM
    timeout_minutes: int = 30
    retry_attempts: int = 3
    retry_delay_minutes: int = 5
    enabled: bool = True
    depends_on: List[str] = None  # Job IDs this job depends on
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class ETLJobRun:
    """Record of an ETL job execution."""
    job_id: str
    run_id: str
    status: JobStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    error_message: Optional[str] = None
    ingestion_result: Optional[IngestionResult] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.end_time and self.start_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()


class ETLOrchestrator:
    """Orchestrates ETL jobs for agricultural data ingestion."""
    
    def __init__(self, ingestion_pipeline: DataIngestionPipeline):
        self.ingestion_pipeline = ingestion_pipeline
        self.scheduler = AsyncIOScheduler()
        self.jobs: Dict[str, ETLJobConfig] = {}
        self.job_runs: List[ETLJobRun] = []
        self.running_jobs: Dict[str, asyncio.Task] = {}
        self.job_dependencies: Dict[str, List[str]] = {}
        self.metrics = {
            "total_jobs_run": 0,
            "successful_jobs": 0,
            "failed_jobs": 0,
            "average_duration_seconds": 0.0,
            "last_run_time": None
        }
    
    def register_job(self, job_config: ETLJobConfig):
        """Register an ETL job for scheduling."""
        self.jobs[job_config.job_id] = job_config
        
        # Track dependencies
        if job_config.depends_on:
            for dependency in job_config.depends_on:
                if dependency not in self.job_dependencies:
                    self.job_dependencies[dependency] = []
                self.job_dependencies[dependency].append(job_config.job_id)
        
        # Schedule the job if enabled
        if job_config.enabled:
            self._schedule_job(job_config)
        
        logger.info("Registered ETL job", 
                   job_id=job_config.job_id, 
                   name=job_config.name,
                   enabled=job_config.enabled)
    
    def _schedule_job(self, job_config: ETLJobConfig):
        """Schedule a job with the scheduler."""
        try:
            # Remove existing job if it exists
            try:
                self.scheduler.remove_job(job_config.job_id)
            except:
                pass
            
            # Add new job based on schedule type
            if job_config.schedule_cron:
                trigger = CronTrigger.from_crontab(job_config.schedule_cron)
                self.scheduler.add_job(
                    self._execute_job,
                    trigger=trigger,
                    id=job_config.job_id,
                    args=[job_config.job_id],
                    max_instances=1,
                    coalesce=True
                )
            elif job_config.schedule_interval_minutes:
                trigger = IntervalTrigger(minutes=job_config.schedule_interval_minutes)
                self.scheduler.add_job(
                    self._execute_job,
                    trigger=trigger,
                    id=job_config.job_id,
                    args=[job_config.job_id],
                    max_instances=1,
                    coalesce=True
                )
            
            logger.info("Scheduled ETL job", 
                       job_id=job_config.job_id,
                       cron=job_config.schedule_cron,
                       interval=job_config.schedule_interval_minutes)
                       
        except Exception as e:
            logger.error("Failed to schedule ETL job", 
                        job_id=job_config.job_id, error=str(e))
    
    async def start_scheduler(self):
        """Start the ETL scheduler."""
        try:
            self.scheduler.start()
            logger.info("ETL scheduler started")
        except Exception as e:
            logger.error("Failed to start ETL scheduler", error=str(e))
            raise
    
    async def stop_scheduler(self):
        """Stop the ETL scheduler."""
        try:
            self.scheduler.shutdown(wait=True)
            
            # Cancel any running jobs
            for job_id, task in self.running_jobs.items():
                if not task.done():
                    task.cancel()
                    logger.info("Cancelled running ETL job", job_id=job_id)
            
            self.running_jobs.clear()
            logger.info("ETL scheduler stopped")
        except Exception as e:
            logger.error("Error stopping ETL scheduler", error=str(e))
    
    async def _execute_job(self, job_id: str):
        """Execute an ETL job."""
        if job_id not in self.jobs:
            logger.error("Job not found", job_id=job_id)
            return
        
        job_config = self.jobs[job_id]
        
        # Check if job is already running
        if job_id in self.running_jobs and not self.running_jobs[job_id].done():
            logger.warning("Job already running, skipping", job_id=job_id)
            return
        
        # Check dependencies
        if not await self._check_dependencies(job_config):
            logger.info("Job dependencies not met, skipping", job_id=job_id)
            return
        
        # Create and start job execution task
        task = asyncio.create_task(self._run_job_with_retries(job_config))
        self.running_jobs[job_id] = task
        
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Job execution cancelled", job_id=job_id)
        except Exception as e:
            logger.error("Job execution failed", job_id=job_id, error=str(e))
        finally:
            # Clean up completed task
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
    
    async def _check_dependencies(self, job_config: ETLJobConfig) -> bool:
        """Check if job dependencies are satisfied."""
        if not job_config.depends_on:
            return True
        
        # Check if all dependent jobs have completed successfully recently
        for dependency_id in job_config.depends_on:
            recent_runs = [run for run in self.job_runs 
                          if run.job_id == dependency_id 
                          and run.start_time > datetime.utcnow() - timedelta(hours=24)]
            
            if not recent_runs:
                logger.warning("Dependency job has no recent runs", 
                             job_id=job_config.job_id, dependency=dependency_id)
                return False
            
            latest_run = max(recent_runs, key=lambda r: r.start_time)
            if latest_run.status != JobStatus.SUCCESS:
                logger.warning("Dependency job did not complete successfully", 
                             job_id=job_config.job_id, dependency=dependency_id,
                             dependency_status=latest_run.status.value)
                return False
        
        return True
    
    async def _run_job_with_retries(self, job_config: ETLJobConfig):
        """Run a job with retry logic."""
        for attempt in range(job_config.retry_attempts + 1):
            run_id = f"{job_config.job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{attempt}"
            
            job_run = ETLJobRun(
                job_id=job_config.job_id,
                run_id=run_id,
                status=JobStatus.RUNNING,
                start_time=datetime.utcnow(),
                retry_count=attempt
            )
            
            self.job_runs.append(job_run)
            self.metrics["total_jobs_run"] += 1
            
            logger.info("Starting ETL job", 
                       job_id=job_config.job_id, 
                       run_id=run_id,
                       attempt=attempt + 1,
                       max_attempts=job_config.retry_attempts + 1)
            
            try:
                # Execute the job with timeout
                ingestion_result = await asyncio.wait_for(
                    self.ingestion_pipeline.ingest_data(
                        job_config.source_name,
                        job_config.operation,
                        **job_config.parameters
                    ),
                    timeout=job_config.timeout_minutes * 60
                )
                
                # Update job run with results
                job_run.end_time = datetime.utcnow()
                job_run.ingestion_result = ingestion_result
                
                if ingestion_result.success:
                    job_run.status = JobStatus.SUCCESS
                    self.metrics["successful_jobs"] += 1
                    
                    logger.info("ETL job completed successfully", 
                               job_id=job_config.job_id,
                               run_id=run_id,
                               quality_score=ingestion_result.quality_score,
                               cache_hit=ingestion_result.cache_hit)
                    
                    # Trigger dependent jobs
                    await self._trigger_dependent_jobs(job_config.job_id)
                    break
                else:
                    job_run.status = JobStatus.FAILED
                    job_run.error_message = ingestion_result.error_message
                    
                    if attempt < job_config.retry_attempts:
                        logger.warning("ETL job failed, will retry", 
                                     job_id=job_config.job_id,
                                     run_id=run_id,
                                     error=ingestion_result.error_message,
                                     next_attempt=attempt + 2)
                        
                        # Wait before retry
                        await asyncio.sleep(job_config.retry_delay_minutes * 60)
                    else:
                        logger.error("ETL job failed after all retries", 
                                   job_id=job_config.job_id,
                                   run_id=run_id,
                                   error=ingestion_result.error_message)
                        self.metrics["failed_jobs"] += 1
                
            except asyncio.TimeoutError:
                job_run.end_time = datetime.utcnow()
                job_run.status = JobStatus.FAILED
                job_run.error_message = f"Job timed out after {job_config.timeout_minutes} minutes"
                
                if attempt < job_config.retry_attempts:
                    logger.warning("ETL job timed out, will retry", 
                                 job_id=job_config.job_id, run_id=run_id)
                    await asyncio.sleep(job_config.retry_delay_minutes * 60)
                else:
                    logger.error("ETL job timed out after all retries", 
                               job_id=job_config.job_id, run_id=run_id)
                    self.metrics["failed_jobs"] += 1
                
            except Exception as e:
                job_run.end_time = datetime.utcnow()
                job_run.status = JobStatus.FAILED
                job_run.error_message = str(e)
                
                if attempt < job_config.retry_attempts:
                    logger.warning("ETL job error, will retry", 
                                 job_id=job_config.job_id, 
                                 run_id=run_id,
                                 error=str(e))
                    await asyncio.sleep(job_config.retry_delay_minutes * 60)
                else:
                    logger.error("ETL job error after all retries", 
                               job_id=job_config.job_id,
                               run_id=run_id, 
                               error=str(e))
                    self.metrics["failed_jobs"] += 1
        
        # Update metrics
        self.metrics["last_run_time"] = datetime.utcnow().isoformat()
        self._update_average_duration()
    
    async def _trigger_dependent_jobs(self, completed_job_id: str):
        """Trigger jobs that depend on the completed job."""
        dependent_jobs = self.job_dependencies.get(completed_job_id, [])
        
        for dependent_job_id in dependent_jobs:
            if dependent_job_id in self.jobs and self.jobs[dependent_job_id].enabled:
                logger.info("Triggering dependent job", 
                           completed_job=completed_job_id,
                           dependent_job=dependent_job_id)
                
                # Schedule immediate execution
                self.scheduler.add_job(
                    self._execute_job,
                    args=[dependent_job_id],
                    id=f"{dependent_job_id}_triggered_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    max_instances=1
                )
    
    def _update_average_duration(self):
        """Update average job duration metric."""
        completed_runs = [run for run in self.job_runs 
                         if run.status in [JobStatus.SUCCESS, JobStatus.FAILED] 
                         and run.duration_seconds is not None]
        
        if completed_runs:
            total_duration = sum(run.duration_seconds for run in completed_runs)
            self.metrics["average_duration_seconds"] = total_duration / len(completed_runs)
    
    async def run_job_now(self, job_id: str) -> ETLJobRun:
        """Manually trigger a job to run immediately."""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job_config = self.jobs[job_id]
        
        # Check if job is already running
        if job_id in self.running_jobs and not self.running_jobs[job_id].done():
            raise RuntimeError(f"Job {job_id} is already running")
        
        # Execute the job
        task = asyncio.create_task(self._run_job_with_retries(job_config))
        self.running_jobs[job_id] = task
        
        try:
            await task
            
            # Return the latest run for this job
            job_runs = [run for run in self.job_runs if run.job_id == job_id]
            return max(job_runs, key=lambda r: r.start_time)
            
        finally:
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get status information for a job."""
        if job_id not in self.jobs:
            return {"error": f"Job {job_id} not found"}
        
        job_config = self.jobs[job_id]
        
        # Get recent runs
        recent_runs = [run for run in self.job_runs 
                      if run.job_id == job_id 
                      and run.start_time > datetime.utcnow() - timedelta(days=7)]
        
        recent_runs.sort(key=lambda r: r.start_time, reverse=True)
        
        # Check if currently running
        is_running = job_id in self.running_jobs and not self.running_jobs[job_id].done()
        
        # Get next scheduled run
        next_run = None
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
        except:
            pass
        
        return {
            "job_id": job_id,
            "name": job_config.name,
            "enabled": job_config.enabled,
            "is_running": is_running,
            "next_scheduled_run": next_run,
            "recent_runs": [
                {
                    "run_id": run.run_id,
                    "status": run.status.value,
                    "start_time": run.start_time.isoformat(),
                    "end_time": run.end_time.isoformat() if run.end_time else None,
                    "duration_seconds": run.duration_seconds,
                    "error_message": run.error_message,
                    "retry_count": run.retry_count
                }
                for run in recent_runs[:10]  # Last 10 runs
            ]
        }
    
    def get_all_jobs_status(self) -> Dict[str, Any]:
        """Get status for all registered jobs."""
        return {
            "jobs": {job_id: self.get_job_status(job_id) for job_id in self.jobs.keys()},
            "scheduler_running": self.scheduler.running,
            "metrics": self.metrics.copy()
        }
    
    def enable_job(self, job_id: str):
        """Enable a job for scheduling."""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        self.jobs[job_id].enabled = True
        self._schedule_job(self.jobs[job_id])
        logger.info("Enabled ETL job", job_id=job_id)
    
    def disable_job(self, job_id: str):
        """Disable a job from scheduling."""
        if job_id not in self.jobs:
            raise ValueError(f"Job {job_id} not found")
        
        self.jobs[job_id].enabled = False
        
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass
        
        logger.info("Disabled ETL job", job_id=job_id)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get ETL orchestrator metrics."""
        return self.metrics.copy()