"""
Scheduled price update service using APScheduler for daily price collection.
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime, date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
import time

from ..models.price_models import FertilizerProduct, FertilizerType
from .price_tracking_service import FertilizerPriceTrackingService
from ..database.fertilizer_price_db import get_db_session, FertilizerPriceRepository

logger = logging.getLogger(__name__)


class ScheduledPriceUpdater:
    """Service for scheduled fertilizer price updates."""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.price_service = FertilizerPriceTrackingService()
        self.is_running = False
        
        # Configure scheduler event listeners
        self.scheduler.add_listener(self._job_executed, EVENT_JOB_EXECUTED)
        self.scheduler.add_listener(self._job_error, EVENT_JOB_ERROR)
    
    async def start_scheduler(self):
        """Start the scheduler with configured jobs."""
        try:
            # Daily price update at 6:00 AM UTC (market open time)
            self.scheduler.add_job(
                self._daily_price_update,
                CronTrigger(hour=6, minute=0, timezone='UTC'),
                id='daily_price_update',
                name='Daily Fertilizer Price Update',
                max_instances=1,
                coalesce=True
            )
            
            # Hourly price update during market hours (6 AM - 6 PM UTC)
            self.scheduler.add_job(
                self._hourly_price_update,
                CronTrigger(hour='6-18', minute=0, timezone='UTC'),
                id='hourly_price_update',
                name='Hourly Price Update (Market Hours)',
                max_instances=1,
                coalesce=True
            )
            
            # Weekly comprehensive update on Sundays at 2 AM UTC
            self.scheduler.add_job(
                self._weekly_comprehensive_update,
                CronTrigger(day_of_week=6, hour=2, minute=0, timezone='UTC'),
                id='weekly_comprehensive_update',
                name='Weekly Comprehensive Price Update',
                max_instances=1,
                coalesce=True
            )
            
            # Monthly trend analysis update on the 1st at 3 AM UTC
            self.scheduler.add_job(
                self._monthly_trend_analysis,
                CronTrigger(day=1, hour=3, minute=0, timezone='UTC'),
                id='monthly_trend_analysis',
                name='Monthly Trend Analysis Update',
                max_instances=1,
                coalesce=True
            )
            
            # Health check every 5 minutes
            self.scheduler.add_job(
                self._health_check,
                IntervalTrigger(minutes=5),
                id='health_check',
                name='Scheduler Health Check',
                max_instances=1,
                coalesce=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduled price updater started successfully")
            
            # Log scheduled jobs
            jobs = self.scheduler.get_jobs()
            logger.info(f"Scheduled {len(jobs)} jobs:")
            for job in jobs:
                logger.info(f"  - {job.name} (ID: {job.id}) - Next run: {job.next_run_time}")
            
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise
    
    async def stop_scheduler(self):
        """Stop the scheduler."""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown(wait=True)
                self.is_running = False
                logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")
    
    async def _daily_price_update(self):
        """Daily comprehensive price update for all products."""
        start_time = time.time()
        logger.info("Starting daily price update...")
        
        try:
            # Get all fertilizer products
            products = list(FertilizerProduct)
            regions = ["US", "CA", "MX"]  # North American regions
            
            total_updates = 0
            successful_updates = 0
            failed_updates = 0
            
            # Update prices for all products and regions
            for product in products:
                for region in regions:
                    total_updates += 1
                    try:
                        response = await self.price_service.update_price(
                            product, region, force_update=True
                        )
                        
                        if response.success:
                            successful_updates += 1
                            logger.debug(f"Updated {product.value} in {region}: ${response.new_price.price_per_unit}")
                        else:
                            failed_updates += 1
                            logger.warning(f"Failed to update {product.value} in {region}: {response.error_message}")
                            
                    except Exception as e:
                        failed_updates += 1
                        logger.error(f"Error updating {product.value} in {region}: {e}")
            
            # Log summary
            duration = time.time() - start_time
            success_rate = (successful_updates / total_updates * 100) if total_updates > 0 else 0
            
            logger.info(
                f"Daily price update completed: "
                f"{successful_updates}/{total_updates} successful "
                f"({success_rate:.1f}%), {failed_updates} failed, "
                f"duration: {duration:.2f}s"
            )
            
            # Store update statistics
            await self._store_update_statistics(
                "daily_update",
                total_updates,
                successful_updates,
                failed_updates,
                duration
            )
            
        except Exception as e:
            logger.error(f"Error in daily price update: {e}")
    
    async def _hourly_price_update(self):
        """Hourly price update for critical products during market hours."""
        logger.info("Starting hourly price update...")
        
        try:
            # Focus on most traded products
            critical_products = [
                FertilizerProduct.UREA,
                FertilizerProduct.ANHYDROUS_AMMONIA,
                FertilizerProduct.DAP,
                FertilizerProduct.MAP,
                FertilizerProduct.MURIATE_OF_POTASH
            ]
            
            region = "US"  # Focus on US market during trading hours
            
            for product in critical_products:
                try:
                    response = await self.price_service.update_price(
                        product, region, force_update=False  # Use cache if recent
                    )
                    
                    if response.success:
                        logger.debug(f"Hourly update: {product.value} = ${response.new_price.price_per_unit}")
                    else:
                        logger.debug(f"Hourly update skipped for {product.value}: {response.error_message}")
                        
                except Exception as e:
                    logger.warning(f"Error in hourly update for {product.value}: {e}")
            
            logger.info("Hourly price update completed")
            
        except Exception as e:
            logger.error(f"Error in hourly price update: {e}")
    
    async def _weekly_comprehensive_update(self):
        """Weekly comprehensive update including trend analysis."""
        logger.info("Starting weekly comprehensive update...")
        
        try:
            # Update all products
            await self._daily_price_update()
            
            # Generate trend analysis for all products
            products = list(FertilizerProduct)
            regions = ["US", "CA", "MX"]
            
            for product in products:
                for region in regions:
                    try:
                        trend = await self.price_service.get_price_trend(product, region, days=30)
                        if trend:
                            logger.debug(f"Generated trend analysis for {product.value} in {region}")
                    except Exception as e:
                        logger.warning(f"Error generating trend for {product.value} in {region}: {e}")
            
            logger.info("Weekly comprehensive update completed")
            
        except Exception as e:
            logger.error(f"Error in weekly comprehensive update: {e}")
    
    async def _monthly_trend_analysis(self):
        """Monthly comprehensive trend analysis and reporting."""
        logger.info("Starting monthly trend analysis...")
        
        try:
            # Generate comprehensive trend analysis
            products = list(FertilizerProduct)
            regions = ["US", "CA", "MX"]
            
            trend_reports = []
            
            for product in products:
                for region in regions:
                    try:
                        # Get 90-day trend analysis
                        trend = await self.price_service.get_price_trend(product, region, days=90)
                        if trend:
                            trend_reports.append({
                                "product": product.value,
                                "region": region,
                                "trend_direction": trend.trend_direction,
                                "trend_strength": trend.trend_strength,
                                "volatility_30d": trend.volatility_30d,
                                "current_price": trend.current_price
                            })
                    except Exception as e:
                        logger.warning(f"Error in monthly trend analysis for {product.value} in {region}: {e}")
            
            # Log summary
            logger.info(f"Monthly trend analysis completed: {len(trend_reports)} reports generated")
            
            # Store trend analysis summary
            await self._store_trend_analysis_summary(trend_reports)
            
        except Exception as e:
            logger.error(f"Error in monthly trend analysis: {e}")
    
    async def _health_check(self):
        """Health check for the scheduler and price service."""
        try:
            # Check if scheduler is running
            if not self.is_running:
                logger.warning("Scheduler health check: Scheduler is not running")
                return
            
            # Check if price service is responsive
            test_price = await self.price_service.get_current_price(
                FertilizerProduct.UREA, "US", max_age_hours=24
            )
            
            if test_price:
                logger.debug("Scheduler health check: All systems operational")
            else:
                logger.warning("Scheduler health check: Price service not responding")
                
        except Exception as e:
            logger.error(f"Scheduler health check failed: {e}")
    
    async def _store_update_statistics(
        self,
        update_type: str,
        total_updates: int,
        successful_updates: int,
        failed_updates: int,
        duration: float
    ):
        """Store update statistics in database."""
        try:
            async for session in get_db_session():
                # This would store statistics in a dedicated table
                # For now, just log the statistics
                logger.info(
                    f"Update statistics - Type: {update_type}, "
                    f"Total: {total_updates}, Success: {successful_updates}, "
                    f"Failed: {failed_updates}, Duration: {duration:.2f}s"
                )
        except Exception as e:
            logger.warning(f"Could not store update statistics: {e}")
    
    async def _store_trend_analysis_summary(self, trend_reports: List[Dict[str, Any]]):
        """Store trend analysis summary."""
        try:
            # This would store trend analysis in a dedicated table
            # For now, just log the summary
            logger.info(f"Trend analysis summary: {len(trend_reports)} products analyzed")
            
            # Count trends by direction
            trend_counts = {}
            for report in trend_reports:
                direction = report["trend_direction"]
                trend_counts[direction] = trend_counts.get(direction, 0) + 1
            
            logger.info(f"Trend distribution: {trend_counts}")
            
        except Exception as e:
            logger.warning(f"Could not store trend analysis summary: {e}")
    
    def _job_executed(self, event):
        """Handle successful job execution."""
        logger.info(f"Job executed successfully: {event.job_id}")
    
    def _job_error(self, event):
        """Handle job execution errors."""
        logger.error(f"Job execution error: {event.job_id} - {event.exception}")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        if not self.is_running:
            return {"status": "stopped", "jobs": []}
        
        jobs = self.scheduler.get_jobs()
        job_info = []
        
        for job in jobs:
            job_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger)
            })
        
        return {
            "status": "running",
            "jobs": job_info,
            "total_jobs": len(jobs)
        }
    
    async def trigger_manual_update(self, product: FertilizerProduct = None, region: str = "US"):
        """Trigger a manual price update."""
        try:
            if product:
                logger.info(f"Triggering manual update for {product.value} in {region}")
                response = await self.price_service.update_price(product, region, force_update=True)
                return response
            else:
                logger.info("Triggering manual daily update")
                await self._daily_price_update()
                return {"success": True, "message": "Manual daily update completed"}
                
        except Exception as e:
            logger.error(f"Error in manual update: {e}")
            return {"success": False, "error": str(e)}


# Global scheduler instance
scheduler_instance = None


async def get_scheduler() -> ScheduledPriceUpdater:
    """Get the global scheduler instance."""
    global scheduler_instance
    if scheduler_instance is None:
        scheduler_instance = ScheduledPriceUpdater()
    return scheduler_instance


async def start_scheduled_updates():
    """Start the scheduled price updates."""
    scheduler = await get_scheduler()
    await scheduler.start_scheduler()


async def stop_scheduled_updates():
    """Stop the scheduled price updates."""
    global scheduler_instance
    if scheduler_instance:
        await scheduler_instance.stop_scheduler()
        scheduler_instance = None
