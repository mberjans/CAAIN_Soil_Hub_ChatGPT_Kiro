"""
Tests for scheduled price updater service.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta

from ..services.scheduled_price_updater import ScheduledPriceUpdater
from ..models.price_models import FertilizerProduct, FertilizerType
from ..services.price_tracking_service import FertilizerPriceTrackingService


class TestScheduledPriceUpdater:
    """Test suite for scheduled price updater."""

    @pytest.fixture
    def scheduler(self):
        """Create scheduler instance for testing."""
        return ScheduledPriceUpdater()

    @pytest.fixture
    def mock_price_service(self):
        """Mock price tracking service."""
        service = AsyncMock(spec=FertilizerPriceTrackingService)
        return service

    @pytest.mark.asyncio
    async def test_scheduler_initialization(self, scheduler):
        """Test scheduler initializes correctly."""
        assert scheduler.scheduler is not None
        assert scheduler.price_service is not None
        assert scheduler.is_running is False

    @pytest.mark.asyncio
    async def test_start_scheduler(self, scheduler):
        """Test scheduler starts successfully."""
        with patch.object(scheduler.scheduler, 'start'):
            with patch.object(scheduler.scheduler, 'get_jobs', return_value=[]):
                await scheduler.start_scheduler()
                
        assert scheduler.is_running is True

    @pytest.mark.asyncio
    async def test_stop_scheduler(self, scheduler):
        """Test scheduler stops successfully."""
        scheduler.is_running = True
        
        with patch.object(scheduler.scheduler, 'shutdown'):
            await scheduler.stop_scheduler()
                
        assert scheduler.is_running is False

    @pytest.mark.asyncio
    async def test_daily_price_update_success(self, scheduler):
        """Test daily price update with successful updates."""
        # Mock successful price updates
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.new_price.price_per_unit = 450.0
        mock_response.error_message = None
        
        scheduler.price_service.update_price = AsyncMock(return_value=mock_response)
        
        # Mock get_db_session to avoid database dependency
        with patch('src.services.scheduled_price_updater.get_db_session'):
            await scheduler._daily_price_update()
        
        # Verify update_price was called for all products and regions
        expected_calls = len(list(FertilizerProduct)) * 3  # 3 regions
        assert scheduler.price_service.update_price.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_daily_price_update_with_failures(self, scheduler):
        """Test daily price update with some failures."""
        # Mock mixed success/failure responses
        def mock_update_price(product, region, force_update):
            if product == FertilizerProduct.UREA and region == "US":
                response = AsyncMock()
                response.success = False
                response.error_message = "API Error"
                return response
            else:
                response = AsyncMock()
                response.success = True
                response.new_price.price_per_unit = 450.0
                response.error_message = None
                return response
        
        scheduler.price_service.update_price = AsyncMock(side_effect=mock_update_price)
        
        # Mock get_db_session to avoid database dependency
        with patch('src.services.scheduled_price_updater.get_db_session'):
            await scheduler._daily_price_update()
        
        # Verify update_price was called for all products and regions
        expected_calls = len(list(FertilizerProduct)) * 3  # 3 regions
        assert scheduler.price_service.update_price.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_hourly_price_update(self, scheduler):
        """Test hourly price update for critical products."""
        # Mock successful price updates
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.new_price.price_per_unit = 450.0
        mock_response.error_message = None
        
        scheduler.price_service.update_price = AsyncMock(return_value=mock_response)
        
        await scheduler._hourly_price_update()
        
        # Verify update_price was called for critical products only
        expected_calls = 5  # 5 critical products
        assert scheduler.price_service.update_price.call_count == expected_calls

    @pytest.mark.asyncio
    async def test_weekly_comprehensive_update(self, scheduler):
        """Test weekly comprehensive update."""
        # Mock daily update
        scheduler._daily_price_update = AsyncMock()
        
        # Mock trend analysis
        mock_trend = AsyncMock()
        mock_trend.trend_direction = "up"
        mock_trend.trend_strength = "moderate"
        
        scheduler.price_service.get_price_trend = AsyncMock(return_value=mock_trend)
        
        await scheduler._weekly_comprehensive_update()
        
        # Verify daily update was called
        scheduler._daily_price_update.assert_called_once()
        
        # Verify trend analysis was called for all products and regions
        expected_trend_calls = len(list(FertilizerProduct)) * 3  # 3 regions
        assert scheduler.price_service.get_price_trend.call_count == expected_trend_calls

    @pytest.mark.asyncio
    async def test_monthly_trend_analysis(self, scheduler):
        """Test monthly trend analysis."""
        # Mock trend analysis
        mock_trend = AsyncMock()
        mock_trend.trend_direction = "up"
        mock_trend.trend_strength = "moderate"
        mock_trend.volatility_30d = 0.15
        mock_trend.current_price = 450.0
        
        scheduler.price_service.get_price_trend = AsyncMock(return_value=mock_trend)
        
        # Mock get_db_session to avoid database dependency
        with patch('src.services.scheduled_price_updater.get_db_session'):
            await scheduler._monthly_trend_analysis()
        
        # Verify trend analysis was called for all products and regions
        expected_trend_calls = len(list(FertilizerProduct)) * 3  # 3 regions
        assert scheduler.price_service.get_price_trend.call_count == expected_trend_calls

    @pytest.mark.asyncio
    async def test_health_check_success(self, scheduler):
        """Test health check when everything is working."""
        scheduler.is_running = True
        
        # Mock successful price fetch
        mock_price = AsyncMock()
        scheduler.price_service.get_current_price = AsyncMock(return_value=mock_price)
        
        await scheduler._health_check()
        
        # Verify price service was called
        scheduler.price_service.get_current_price.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_scheduler_not_running(self, scheduler):
        """Test health check when scheduler is not running."""
        scheduler.is_running = False
        
        # Should not call price service
        scheduler.price_service.get_current_price = AsyncMock()
        
        await scheduler._health_check()
        
        # Verify price service was not called
        scheduler.price_service.get_current_price.assert_not_called()

    @pytest.mark.asyncio
    async def test_health_check_price_service_failure(self, scheduler):
        """Test health check when price service fails."""
        scheduler.is_running = True
        
        # Mock price service failure
        scheduler.price_service.get_current_price = AsyncMock(return_value=None)
        
        await scheduler._health_check()
        
        # Verify price service was called
        scheduler.price_service.get_current_price.assert_called_once()

    @pytest.mark.asyncio
    async def test_trigger_manual_update_specific_product(self, scheduler):
        """Test manual update for specific product."""
        # Mock successful price update
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.new_price.price_per_unit = 450.0
        
        scheduler.price_service.update_price = AsyncMock(return_value=mock_response)
        
        result = await scheduler.trigger_manual_update(FertilizerProduct.UREA, "US")
        
        # Verify update_price was called with correct parameters
        scheduler.price_service.update_price.assert_called_once_with(
            FertilizerProduct.UREA, "US", force_update=True
        )
        
        assert result == mock_response

    @pytest.mark.asyncio
    async def test_trigger_manual_update_all_products(self, scheduler):
        """Test manual update for all products."""
        # Mock daily update
        scheduler._daily_price_update = AsyncMock()
        
        result = await scheduler.trigger_manual_update(None, "US")
        
        # Verify daily update was called
        scheduler._daily_price_update.assert_called_once()
        
        assert result["success"] is True
        assert "Manual daily update completed" in result["message"]

    @pytest.mark.asyncio
    async def test_trigger_manual_update_error(self, scheduler):
        """Test manual update with error."""
        # Mock price service error
        scheduler.price_service.update_price = AsyncMock(side_effect=Exception("API Error"))
        
        result = await scheduler.trigger_manual_update(FertilizerProduct.UREA, "US")
        
        assert result["success"] is False
        assert "API Error" in result["error"]

    def test_get_scheduler_status_stopped(self, scheduler):
        """Test scheduler status when stopped."""
        scheduler.is_running = False
        
        status = scheduler.get_scheduler_status()
        
        assert status["status"] == "stopped"
        assert status["jobs"] == []

    def test_get_scheduler_status_running(self, scheduler):
        """Test scheduler status when running."""
        scheduler.is_running = True
        
        # Mock scheduler jobs
        mock_job = MagicMock()
        mock_job.id = "test_job"
        mock_job.name = "Test Job"
        mock_job.next_run_time = datetime.now()
        mock_job.trigger = "cron"
        
        scheduler.scheduler.get_jobs = MagicMock(return_value=[mock_job])
        
        status = scheduler.get_scheduler_status()
        
        assert status["status"] == "running"
        assert len(status["jobs"]) == 1
        assert status["jobs"][0]["id"] == "test_job"
        assert status["jobs"][0]["name"] == "Test Job"
        assert status["total_jobs"] == 1

    @pytest.mark.asyncio
    async def test_job_executed_event(self, scheduler):
        """Test job executed event handler."""
        mock_event = MagicMock()
        mock_event.job_id = "test_job"
        
        scheduler._job_executed(mock_event)
        
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_job_error_event(self, scheduler):
        """Test job error event handler."""
        mock_event = MagicMock()
        mock_event.job_id = "test_job"
        mock_event.exception = Exception("Test error")
        
        scheduler._job_error(mock_event)
        
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_store_update_statistics(self, scheduler):
        """Test storing update statistics."""
        # Mock get_db_session to avoid database dependency
        with patch('src.services.scheduled_price_updater.get_db_session'):
            await scheduler._store_update_statistics(
                "test_update", 10, 8, 2, 5.5
            )
        
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_store_trend_analysis_summary(self, scheduler):
        """Test storing trend analysis summary."""
        trend_reports = [
            {"product": "urea", "region": "US", "trend_direction": "up"},
            {"product": "dap", "region": "US", "trend_direction": "down"},
            {"product": "urea", "region": "CA", "trend_direction": "up"}
        ]
        
        # Mock get_db_session to avoid database dependency
        with patch('src.services.scheduled_price_updater.get_db_session'):
            await scheduler._store_trend_analysis_summary(trend_reports)
        
        # Should not raise any exceptions


class TestSchedulerIntegration:
    """Integration tests for scheduler functionality."""

    @pytest.mark.asyncio
    async def test_scheduler_lifecycle(self):
        """Test complete scheduler lifecycle."""
        scheduler = ScheduledPriceUpdater()
        
        # Mock scheduler methods to avoid actual scheduling
        with patch.object(scheduler.scheduler, 'start'):
            with patch.object(scheduler.scheduler, 'get_jobs', return_value=[]):
                await scheduler.start_scheduler()
        
        assert scheduler.is_running is True
        
        # Test status
        status = scheduler.get_scheduler_status()
        assert status["status"] == "running"
        
        # Stop scheduler
        with patch.object(scheduler.scheduler, 'shutdown'):
            await scheduler.stop_scheduler()
        
        assert scheduler.is_running is False

    @pytest.mark.asyncio
    async def test_concurrent_updates(self):
        """Test that concurrent updates are handled properly."""
        scheduler = ScheduledPriceUpdater()
        
        # Mock successful price updates
        mock_response = AsyncMock()
        mock_response.success = True
        mock_response.new_price.price_per_unit = 450.0
        mock_response.error_message = None
        
        scheduler.price_service.update_price = AsyncMock(return_value=mock_response)
        
        # Mock get_db_session to avoid database dependency
        with patch('src.services.scheduled_price_updater.get_db_session'):
            # Run multiple updates concurrently
            tasks = [
                scheduler._daily_price_update(),
                scheduler._hourly_price_update(),
                scheduler._weekly_comprehensive_update()
            ]
            
            await asyncio.gather(*tasks)
        
        # Should complete without errors
        assert True  # If we get here, no exceptions were raised

    @pytest.mark.asyncio
    async def test_error_handling_in_updates(self):
        """Test error handling in update methods."""
        scheduler = ScheduledPriceUpdater()
        
        # Mock price service to raise exceptions
        scheduler.price_service.update_price = AsyncMock(side_effect=Exception("Network error"))
        scheduler.price_service.get_price_trend = AsyncMock(side_effect=Exception("Database error"))
        
        # Mock get_db_session to avoid database dependency
        with patch('src.services.scheduled_price_updater.get_db_session'):
            # These should not raise exceptions
            await scheduler._daily_price_update()
            await scheduler._hourly_price_update()
            await scheduler._weekly_comprehensive_update()
            await scheduler._monthly_trend_analysis()
        
        # Should complete without raising exceptions
        assert True  # If we get here, no exceptions were raised
