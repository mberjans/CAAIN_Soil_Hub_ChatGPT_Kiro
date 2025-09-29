"""
Comprehensive Tests for Scalability Infrastructure

This module tests all scalability components including load balancing,
distributed caching, async processing, capacity planning, and fault tolerance.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import pytest
import asyncio
import time
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import scalability components
from src.infrastructure.scalability_manager import (
    ScalabilityManager, LoadBalancer, AutoScaler, DistributedProcessor,
    ServiceInstance, ScalingMetrics, ScalingDecision
)
from src.infrastructure.distributed_cache import (
    DistributedCache, LocalCache, CacheEntry, CacheLevel
)
from src.infrastructure.async_processor import (
    AsyncProcessor, JobQueue, Job, JobStatus, JobPriority, QueueType
)
from src.infrastructure.capacity_planner import (
    CapacityPlanner, TrafficAnalyzer, ResourcePlanner, CostAnalyzer
)
from src.infrastructure.fault_tolerance import (
    FaultToleranceManager, HealthMonitor, CircuitBreaker, DisasterRecovery
)
from src.infrastructure.scalability_infrastructure import (
    ScalabilityInfrastructure, ScalabilityConfig
)
from src.infrastructure.performance_monitor import (
    PerformanceMonitor, PerformanceMetrics, MetricType
)


class TestScalabilityManager:
    """Test suite for scalability manager."""
    
    @pytest.fixture
    async def scalability_manager(self):
        """Create scalability manager instance."""
        manager = ScalabilityManager()
        await manager.initialize()
        return manager
        
    @pytest.mark.asyncio
    async def test_add_service_instance(self, scalability_manager):
        """Test adding service instances."""
        await scalability_manager.add_service_instance(
            instance_id="test-instance-1",
            host="localhost",
            port=8001,
            health_endpoint="/health",
            weight=1
        )
        
        assert len(scalability_manager.load_balancer.instances) == 1
        instance = scalability_manager.load_balancer.instances[0]
        assert instance.instance_id == "test-instance-1"
        assert instance.host == "localhost"
        assert instance.port == 8001
        
    @pytest.mark.asyncio
    async def test_load_balancer_round_robin(self, scalability_manager):
        """Test round robin load balancing."""
        # Add multiple instances
        for i in range(3):
            await scalability_manager.add_service_instance(
                instance_id=f"instance-{i}",
                host="localhost",
                port=8001 + i
            )
            
        # Test round robin selection
        instances = []
        for _ in range(6):
            instance = await scalability_manager.load_balancer.get_next_instance()
            instances.append(instance.instance_id)
            
        # Should cycle through instances
        expected = ["instance-0", "instance-1", "instance-2", "instance-0", "instance-1", "instance-2"]
        assert instances == expected
        
    @pytest.mark.asyncio
    async def test_auto_scaler_metrics_analysis(self, scalability_manager):
        """Test auto-scaler metrics analysis."""
        # Create test metrics
        metrics = ScalingMetrics(
            cpu_usage=85.0,
            memory_usage=80.0,
            request_rate=100.0,
            response_time_ms=2000.0,
            error_rate=0.05,
            queue_length=50,
            active_connections=25
        )
        
        # Analyze metrics
        decision = await scalability_manager.auto_scaler.analyze_metrics(metrics)
        
        assert decision.action in ["scale_up", "scale_down", "no_action"]
        assert decision.confidence >= 0.0
        assert decision.confidence <= 1.0
        
    @pytest.mark.asyncio
    async def test_distributed_processor(self, scalability_manager):
        """Test distributed processing."""
        def test_function(x, y):
            return x + y
            
        # Submit task
        task_id = await scalability_manager.distributed_processor.submit_task(
            task_id="test-task",
            func=test_function,
            args=(5, 3)
        )
        
        assert task_id == "test-task"
        
        # Wait for completion
        result = await scalability_manager.distributed_processor.wait_for_task(task_id, timeout=10)
        assert result == 8


class TestDistributedCache:
    """Test suite for distributed cache."""
    
    @pytest.fixture
    async def distributed_cache(self):
        """Create distributed cache instance."""
        cache = DistributedCache()
        await cache.initialize()
        return cache
        
    @pytest.mark.asyncio
    async def test_cache_set_get(self, distributed_cache):
        """Test basic cache set/get operations."""
        key = "test-key"
        value = {"test": "data", "number": 42}
        
        # Set value
        await distributed_cache.set(key, value, ttl=3600, data_type="test")
        
        # Get value
        retrieved_value = await distributed_cache.get(key, "test")
        
        assert retrieved_value == value
        
    @pytest.mark.asyncio
    async def test_cache_invalidation(self, distributed_cache):
        """Test cache invalidation by tags."""
        # Set multiple values with tags
        await distributed_cache.set("key1", "value1", tags={"category": "test"})
        await distributed_cache.set("key2", "value2", tags={"category": "test"})
        await distributed_cache.set("key3", "value3", tags={"category": "other"})
        
        # Invalidate by tags
        await distributed_cache.invalidate_by_tags({"category": "test"})
        
        # Check that tagged values are invalidated
        assert await distributed_cache.get("key1", "general") is None
        assert await distributed_cache.get("key2", "general") is None
        assert await distributed_cache.get("key3", "general") == "value3"
        
    @pytest.mark.asyncio
    async def test_local_cache_lru(self, distributed_cache):
        """Test local cache LRU eviction."""
        # Fill cache beyond capacity
        for i in range(1500):  # More than max_size (1000)
            await distributed_cache.local_cache.set(f"key-{i}", f"value-{i}")
            
        # Check that oldest entries were evicted
        assert await distributed_cache.local_cache.get("key-0") is None
        assert await distributed_cache.local_cache.get("key-1499") is not None
        
    @pytest.mark.asyncio
    async def test_cache_stats(self, distributed_cache):
        """Test cache statistics."""
        # Perform some operations
        await distributed_cache.set("key1", "value1")
        await distributed_cache.get("key1")
        await distributed_cache.get("nonexistent")
        
        # Get stats
        stats = await distributed_cache.get_cache_stats()
        
        assert "local_cache" in stats
        assert "redis_cache" in stats
        assert stats["local_cache"]["entries"] > 0


class TestAsyncProcessor:
    """Test suite for async processor."""
    
    @pytest.fixture
    async def async_processor(self):
        """Create async processor instance."""
        processor = AsyncProcessor()
        await processor.initialize()
        return processor
        
    @pytest.mark.asyncio
    async def test_job_submission(self, async_processor):
        """Test job submission."""
        job_id = await async_processor.submit_job(
            job_type="test_job",
            payload={"test": "data"},
            priority=JobPriority.NORMAL
        )
        
        assert job_id is not None
        
        # Check job status
        job = await async_processor.get_job_status(job_id)
        assert job is not None
        assert job["status"] == "pending"
        
    @pytest.mark.asyncio
    async def test_job_processing(self, async_processor):
        """Test job processing."""
        # Register a test handler
        async def test_handler(job):
            return {"result": "success", "processed_data": job.payload}
            
        async_processor.register_handler("test_job", test_handler)
        
        # Submit job
        job_id = await async_processor.submit_job(
            job_type="test_job",
            payload={"test": "data"}
        )
        
        # Start workers
        await async_processor.start_workers()
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Check job status
        job = await async_processor.get_job_status(job_id)
        assert job["status"] in ["completed", "running"]
        
    @pytest.mark.asyncio
    async def test_queue_stats(self, async_processor):
        """Test queue statistics."""
        # Submit some jobs
        for i in range(5):
            await async_processor.submit_job(
                job_type="test_job",
                payload={"index": i}
            )
            
        # Get queue stats
        stats = await async_processor.get_queue_stats()
        
        assert "recommendations" in stats
        assert stats["recommendations"]["pending_jobs"] >= 0


class TestCapacityPlanner:
    """Test suite for capacity planner."""
    
    @pytest.fixture
    async def capacity_planner(self):
        """Create capacity planner instance."""
        planner = CapacityPlanner()
        await planner.initialize()
        return planner
        
    @pytest.mark.asyncio
    async def test_traffic_analysis(self, capacity_planner):
        """Test traffic pattern analysis."""
        traffic_pattern = await capacity_planner.traffic_analyzer.analyze_traffic_patterns(days=7)
        
        assert traffic_pattern.pattern_type is not None
        assert isinstance(traffic_pattern.peak_hours, list)
        assert isinstance(traffic_pattern.peak_days, list)
        assert traffic_pattern.average_requests_per_minute >= 0
        assert traffic_pattern.peak_requests_per_minute >= 0
        
    @pytest.mark.asyncio
    async def test_resource_planning(self, capacity_planner):
        """Test resource planning."""
        from src.infrastructure.capacity_planner import TrafficPattern
        
        # Create test traffic pattern
        traffic_pattern = TrafficPattern(
            pattern_type="daily",
            peak_hours=[9, 10, 11],
            peak_days=[0, 1, 2],
            average_requests_per_minute=50.0,
            peak_requests_per_minute=100.0,
            growth_rate_percent=10.0
        )
        
        # Calculate resource requirements
        resource_metrics = await capacity_planner.resource_planner.calculate_resource_requirements(
            traffic_pattern, current_users=1000, growth_months=6
        )
        
        assert len(resource_metrics) > 0
        for resource_type, metrics in resource_metrics.items():
            assert metrics.current_usage >= 0
            assert metrics.max_capacity >= 0
            assert 0 <= metrics.utilization_percent <= 100
            
    @pytest.mark.asyncio
    async def test_capacity_plan_generation(self, capacity_planner):
        """Test capacity plan generation."""
        plan = await capacity_planner.generate_capacity_plan(
            planning_horizon_months=6,
            current_users=1000
        )
        
        assert "traffic_pattern" in plan
        assert "resource_metrics" in plan
        assert "recommendations" in plan
        assert "cost_analysis" in plan
        assert "generated_at" in plan


class TestFaultTolerance:
    """Test suite for fault tolerance."""
    
    @pytest.fixture
    async def fault_tolerance_manager(self):
        """Create fault tolerance manager instance."""
        manager = FaultToleranceManager()
        await manager.initialize()
        return manager
        
    @pytest.mark.asyncio
    async def test_health_monitoring(self, fault_tolerance_manager):
        """Test health monitoring."""
        # Get health summary
        health = await fault_tolerance_manager.get_system_health()
        
        assert "overall_health" in health
        assert "service_status" in health
        assert "recent_failures" in health
        assert "circuit_breakers" in health
        
    @pytest.mark.asyncio
    async def test_circuit_breaker(self, fault_tolerance_manager):
        """Test circuit breaker functionality."""
        circuit_breaker = CircuitBreaker("test", failure_threshold=3)
        
        # Test successful calls
        async def success_func():
            return "success"
            
        result = await circuit_breaker.call(success_func)
        assert result == "success"
        assert circuit_breaker.state.state == "closed"
        
        # Test failure handling
        async def failure_func():
            raise Exception("test failure")
            
        # Trigger failures
        for _ in range(4):
            try:
                await circuit_breaker.call(failure_func)
            except Exception:
                pass
                
        # Circuit should be open
        assert circuit_breaker.state.state == "open"
        
    @pytest.mark.asyncio
    async def test_disaster_recovery(self, fault_tolerance_manager):
        """Test disaster recovery."""
        # Create backup
        backup_id = await fault_tolerance_manager.create_emergency_backup()
        
        assert backup_id is not None
        
        # Restore backup
        success = await fault_tolerance_manager.disaster_recovery.restore_backup(backup_id)
        assert success is True


class TestScalabilityInfrastructure:
    """Test suite for integrated scalability infrastructure."""
    
    @pytest.fixture
    async def scalability_infrastructure(self):
        """Create scalability infrastructure instance."""
        config = ScalabilityConfig(
            enable_load_balancing=True,
            enable_distributed_cache=True,
            enable_async_processing=True,
            enable_capacity_planning=True,
            enable_fault_tolerance=True
        )
        infrastructure = ScalabilityInfrastructure(config)
        await infrastructure.initialize()
        await infrastructure.start()
        return infrastructure
        
    @pytest.mark.asyncio
    async def test_infrastructure_initialization(self, scalability_infrastructure):
        """Test infrastructure initialization."""
        assert scalability_infrastructure._initialized is True
        assert scalability_infrastructure._running is True
        assert scalability_infrastructure.scalability_manager is not None
        assert scalability_infrastructure.distributed_cache is not None
        assert scalability_infrastructure.async_processor is not None
        assert scalability_infrastructure.capacity_planner is not None
        assert scalability_infrastructure.fault_tolerance_manager is not None
        
    @pytest.mark.asyncio
    async def test_service_instance_management(self, scalability_infrastructure):
        """Test service instance management."""
        await scalability_infrastructure.add_service_instance(
            instance_id="test-instance",
            host="localhost",
            port=8001
        )
        
        assert len(scalability_infrastructure.scalability_manager.load_balancer.instances) == 1
        
    @pytest.mark.asyncio
    async def test_background_job_processing(self, scalability_infrastructure):
        """Test background job processing."""
        job_id = await scalability_infrastructure.submit_background_job(
            job_type="test_job",
            payload={"test": "data"},
            priority="normal"
        )
        
        assert job_id is not None
        
        # Check job status
        status = await scalability_infrastructure.get_job_status(job_id)
        assert status is not None
        
    @pytest.mark.asyncio
    async def test_distributed_caching(self, scalability_infrastructure):
        """Test distributed caching."""
        key = "test-key"
        value = {"test": "data"}
        
        # Set cache
        await scalability_infrastructure.cache_set(key, value, ttl=3600)
        
        # Get cache
        retrieved_value = await scalability_infrastructure.cache_get(key)
        assert retrieved_value == value
        
        # Invalidate cache
        await scalability_infrastructure.cache_invalidate(["test"])
        
    @pytest.mark.asyncio
    async def test_capacity_planning(self, scalability_infrastructure):
        """Test capacity planning."""
        plan = await scalability_infrastructure.generate_capacity_plan(
            planning_horizon_months=6,
            current_users=1000
        )
        
        assert "traffic_pattern" in plan
        assert "resource_metrics" in plan
        assert "recommendations" in plan
        
    @pytest.mark.asyncio
    async def test_system_health(self, scalability_infrastructure):
        """Test system health monitoring."""
        health = await scalability_infrastructure.get_system_health()
        
        assert "overall_health" in health
        assert "service_status" in health
        
    @pytest.mark.asyncio
    async def test_backup_creation(self, scalability_infrastructure):
        """Test backup creation."""
        backup_id = await scalability_infrastructure.create_backup()
        
        assert backup_id is not None
        
    @pytest.mark.asyncio
    async def test_scalability_metrics(self, scalability_infrastructure):
        """Test scalability metrics collection."""
        metrics = await scalability_infrastructure.get_scalability_metrics()
        
        assert "timestamp" in metrics
        assert "components" in metrics
        assert len(metrics["components"]) > 0


class TestPerformanceMonitor:
    """Test suite for performance monitor."""
    
    @pytest.fixture
    async def performance_monitor(self):
        """Create performance monitor instance."""
        monitor = PerformanceMonitor()
        await monitor.initialize()
        await monitor.start_monitoring()
        return monitor
        
    @pytest.mark.asyncio
    async def test_operation_recording(self, performance_monitor):
        """Test operation performance recording."""
        await performance_monitor.record_operation(
            operation="test_operation",
            execution_time_ms=100.0,
            cache_hit=True,
            database_query_count=2
        )
        
        # Check that metrics were recorded
        assert len(performance_monitor.metrics_buffer) > 0
        
    @pytest.mark.asyncio
    async def test_metric_recording(self, performance_monitor):
        """Test custom metric recording."""
        await performance_monitor.record_metric(
            name="test_metric",
            value=42.0,
            metric_type=MetricType.GAUGE
        )
        
        assert "test_metric" in performance_monitor.metric_data
        
    @pytest.mark.asyncio
    async def test_operation_timing_context(self, performance_monitor):
        """Test operation timing context manager."""
        async with performance_monitor.time_operation("context_test") as _:
            await asyncio.sleep(0.1)  # Simulate work
            
        # Check that metrics were recorded
        assert len(performance_monitor.metrics_buffer) > 0
        
    @pytest.mark.asyncio
    async def test_operation_stats(self, performance_monitor):
        """Test operation statistics."""
        # Record some operations
        for i in range(10):
            await performance_monitor.record_operation(
                operation="test_stats",
                execution_time_ms=50.0 + i * 10
            )
            
        # Get stats
        stats = await performance_monitor.get_operation_stats("test_stats", hours=1)
        
        assert "operation" in stats
        assert "data_points" in stats
        assert stats["data_points"] > 0
        
    @pytest.mark.asyncio
    async def test_system_stats(self, performance_monitor):
        """Test system statistics."""
        stats = await performance_monitor.get_system_stats(hours=1)
        
        assert "time_range_hours" in stats
        assert "data_points" in stats
        
    @pytest.mark.asyncio
    async def test_top_slow_operations(self, performance_monitor):
        """Test top slow operations."""
        # Record operations with different execution times
        operations = ["fast_op", "medium_op", "slow_op"]
        times = [10.0, 50.0, 100.0]
        
        for op, time_ms in zip(operations, times):
            await performance_monitor.record_operation(
                operation=op,
                execution_time_ms=time_ms
            )
            
        # Get top slow operations
        slow_ops = await performance_monitor.get_top_slow_operations(limit=3, hours=1)
        
        assert len(slow_ops) > 0
        # Should be sorted by execution time (slowest first)
        assert slow_ops[0]["operation"] == "slow_op"


class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    @pytest.mark.asyncio
    async def test_variety_recommendation_scalability(self):
        """Test variety recommendation with scalability features."""
        from src.infrastructure.scalability_infrastructure import (
            submit_variety_recommendation_job,
            cache_variety_data,
            get_cached_variety_data
        )
        
        # Submit variety recommendation job
        job_id = await submit_variety_recommendation_job(
            crop_id="corn",
            location={"latitude": 40.0, "longitude": -95.0},
            soil_data={"ph": 6.5, "organic_matter": 3.2},
            preferences={"yield_priority": "high"}
        )
        
        assert job_id is not None
        
        # Cache variety data
        variety_data = {
            "variety_id": "corn-variety-1",
            "name": "Test Corn Variety",
            "yield_potential": 180.0,
            "maturity_days": 110
        }
        
        await cache_variety_data("corn-variety-1", variety_data)
        
        # Retrieve cached data
        cached_data = await get_cached_variety_data("corn-variety-1")
        assert cached_data == variety_data
        
    @pytest.mark.asyncio
    async def test_batch_processing_scalability(self):
        """Test batch processing with scalability features."""
        from src.infrastructure.scalability_infrastructure import (
            submit_batch_variety_search_job
        )
        
        # Submit batch search job
        job_id = await submit_batch_variety_search_job(
            queries=["corn varieties", "soybean varieties", "wheat varieties"],
            filters={"yield_potential": {"min": 150}},
            limit=50
        )
        
        assert job_id is not None
        
    @pytest.mark.asyncio
    async def test_capacity_planning_scenario(self):
        """Test capacity planning scenario."""
        from src.infrastructure.scalability_infrastructure import (
            generate_capacity_report
        )
        
        # Generate capacity report
        report = await generate_capacity_report(
            planning_horizon_months=12,
            current_users=5000
        )
        
        assert "traffic_pattern" in report
        assert "resource_metrics" in report
        assert "recommendations" in report
        assert "cost_analysis" in report


# Performance and Load Tests
class TestPerformanceAndLoad:
    """Performance and load tests."""
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self):
        """Test concurrent cache operations."""
        cache = DistributedCache()
        await cache.initialize()
        
        # Perform concurrent operations
        tasks = []
        for i in range(100):
            task = cache.set(f"key-{i}", f"value-{i}")
            tasks.append(task)
            
        await asyncio.gather(*tasks)
        
        # Verify all values were set
        for i in range(100):
            value = await cache.get(f"key-{i}")
            assert value == f"value-{i}"
            
    @pytest.mark.asyncio
    async def test_concurrent_job_submission(self):
        """Test concurrent job submission."""
        processor = AsyncProcessor()
        await processor.initialize()
        
        # Submit jobs concurrently
        tasks = []
        for i in range(50):
            task = processor.submit_job(
                job_type="test_job",
                payload={"index": i}
            )
            tasks.append(task)
            
        job_ids = await asyncio.gather(*tasks)
        
        # Verify all jobs were submitted
        assert len(job_ids) == 50
        assert all(job_id is not None for job_id in job_ids)
        
    @pytest.mark.asyncio
    async def test_load_balancer_performance(self):
        """Test load balancer performance under load."""
        manager = ScalabilityManager()
        await manager.initialize()
        
        # Add multiple instances
        for i in range(10):
            await manager.add_service_instance(
                instance_id=f"instance-{i}",
                host="localhost",
                port=8001 + i
            )
            
        # Test concurrent instance selection
        tasks = []
        for _ in range(100):
            task = manager.load_balancer.get_next_instance()
            tasks.append(task)
            
        instances = await asyncio.gather(*tasks)
        
        # Verify all instances were selected
        assert len(instances) == 100
        assert all(instance is not None for instance in instances)
        
        # Verify load distribution
        instance_counts = {}
        for instance in instances:
            instance_counts[instance.instance_id] = instance_counts.get(instance.instance_id, 0) + 1
            
        # Should have reasonable distribution
        assert len(instance_counts) == 10
        for count in instance_counts.values():
            assert count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])