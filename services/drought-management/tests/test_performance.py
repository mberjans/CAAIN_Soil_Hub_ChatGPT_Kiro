"""
Performance and Load Tests for Drought Management System

This module contains performance tests, load tests, and stress tests
for the drought management system to ensure it meets performance requirements.

TICKET-014_drought-management-13.1: Performance testing
"""

import pytest
import asyncio
import time
import statistics
import psutil
import os
from datetime import datetime, timedelta
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
import json

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from conftest import performance_test_data


class TestResponseTimePerformance:
    """Test response time performance requirements."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_drought_assessment_response_time(self):
        """Test drought assessment response time under normal load."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # Mock external services for consistent performance testing
        with patch.object(service, '_get_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_data') as mock_soil:
            
            mock_weather.return_value = {"precipitation": 5.0, "temperature": 25.0}
            mock_soil.return_value = {"moisture_content": 0.25}
            
            # Test multiple requests to get average response time
            response_times = []
            num_requests = 10
            
            for _ in range(num_requests):
                start_time = time.time()
                
                await service.assess_drought_risk(
                    farm_location_id=uuid4(),
                    field_id=uuid4(),
                    crop_type="corn"
                )
                
                response_time = time.time() - start_time
                response_times.append(response_time)
            
            # Calculate statistics
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # Performance assertions
            assert avg_response_time < 2.0, f"Average response time {avg_response_time:.3f}s exceeds 2s limit"
            assert max_response_time < 3.0, f"Max response time {max_response_time:.3f}s exceeds 3s limit"
            assert min_response_time < 1.0, f"Min response time {min_response_time:.3f}s exceeds 1s limit"
            
            print(f"Response time stats: avg={avg_response_time:.3f}s, max={max_response_time:.3f}s, min={min_response_time:.3f}s")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_conservation_recommendations_response_time(self):
        """Test conservation recommendations response time."""
        from src.services.moisture_conservation_service import MoistureConservationService
        
        service = MoistureConservationService()
        await service.initialize()
        
        response_times = []
        num_requests = 10
        
        for _ in range(num_requests):
            start_time = time.time()
            
            await service.recommend_conservation_practices(
                field_id=uuid4(),
                soil_type="clay_loam",
                slope_percent=3.0,
                current_practices=[]
            )
            
            response_time = time.time() - start_time
            response_times.append(response_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 1.5, f"Average response time {avg_response_time:.3f}s exceeds 1.5s limit"
        assert max_response_time < 2.5, f"Max response time {max_response_time:.3f}s exceeds 2.5s limit"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_monitoring_setup_response_time(self):
        """Test monitoring setup response time."""
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        service = DroughtMonitoringService()
        await service.initialize()
        
        response_times = []
        num_requests = 10
        
        for _ in range(num_requests):
            start_time = time.time()
            
            monitoring_request = {
                "farm_location_id": uuid4(),
                "field_ids": [uuid4()],
                "monitoring_frequency": "daily",
                "alert_thresholds": {"soil_moisture_low": 30.0},
                "notification_preferences": {"enabled_channels": ["email"]},
                "integration_services": ["weather", "soil"]
            }
            
            await service.setup_monitoring(monitoring_request)
            
            response_time = time.time() - start_time
            response_times.append(response_time)
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 1.0, f"Average response time {avg_response_time:.3f}s exceeds 1s limit"
        assert max_response_time < 2.0, f"Max response time {max_response_time:.3f}s exceeds 2s limit"


class TestConcurrentLoadPerformance:
    """Test system performance under concurrent load."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_drought_assessments(self):
        """Test concurrent drought assessment requests."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # Mock external services
        with patch.object(service, '_get_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_data') as mock_soil:
            
            mock_weather.return_value = {"precipitation": 5.0, "temperature": 25.0}
            mock_soil.return_value = {"moisture_content": 0.25}
            
            # Test concurrent requests
            num_concurrent = 50
            farm_ids = [uuid4() for _ in range(num_concurrent)]
            
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = [
                service.assess_drought_risk(farm_id, uuid4(), "corn")
                for farm_id in farm_ids
            ]
            
            # Execute concurrently
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Performance assertions
            assert len(results) == num_concurrent
            assert total_time < 5.0, f"Total time {total_time:.3f}s exceeds 5s limit for {num_concurrent} concurrent requests"
            
            # Calculate throughput
            throughput = num_concurrent / total_time
            assert throughput >= 10.0, f"Throughput {throughput:.2f} requests/s below 10 requests/s threshold"
            
            print(f"Concurrent performance: {num_concurrent} requests in {total_time:.3f}s, throughput: {throughput:.2f} req/s")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_monitoring_requests(self):
        """Test concurrent monitoring requests."""
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        service = DroughtMonitoringService()
        await service.initialize()
        
        # Mock external dependencies
        with patch.object(service, '_get_historical_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_moisture_data') as mock_soil, \
             patch.object(service, 'drought_indices_calculator') as mock_calc:
            
            mock_weather.return_value = {
                "precipitation": [10.5, 8.2, 12.1, 5.8, 15.3, 7.9, 9.4, 11.2],
                "temperature": [22.5, 24.1, 26.8, 28.3, 25.9, 23.7, 21.4, 19.8]
            }
            mock_soil.return_value = {
                "available_water_capacity": 2.5,
                "field_capacity": 0.35,
                "wilting_point": 0.15,
                "current_moisture": 0.25
            }
            mock_calc.calculate_spi = AsyncMock(return_value=[-0.8, -1.2, -1.5, -1.3])
            mock_calc.calculate_pdsi = AsyncMock(return_value=-1.4)
            mock_calc.calculate_spei = AsyncMock(return_value=[-0.9, -1.1, -1.4, -1.2])
            
            # Test concurrent monitoring requests
            num_concurrent = 30
            farm_ids = [uuid4() for _ in range(num_concurrent)]
            field_ids = [uuid4() for _ in range(num_concurrent)]
            
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = [
                service.calculate_drought_indices(farm_id, field_id)
                for farm_id, field_id in zip(farm_ids, field_ids)
            ]
            
            # Execute concurrently
            results = await asyncio.gather(*tasks)
            total_time = time.time() - start_time
            
            # Performance assertions
            assert len(results) == num_concurrent
            assert total_time < 8.0, f"Total time {total_time:.3f}s exceeds 8s limit for {num_concurrent} concurrent requests"
            
            # Calculate throughput
            throughput = num_concurrent / total_time
            assert throughput >= 4.0, f"Throughput {throughput:.2f} requests/s below 4 requests/s threshold"
            
            print(f"Monitoring performance: {num_concurrent} requests in {total_time:.3f}s, throughput: {throughput:.2f} req/s")


class TestMemoryPerformance:
    """Test memory usage and efficiency."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_during_processing(self):
        """Test memory usage during data processing."""
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        service = DroughtMonitoringService()
        await service.initialize()
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock external dependencies
        with patch.object(service, '_get_historical_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_moisture_data') as mock_soil, \
             patch.object(service, 'drought_indices_calculator') as mock_calc:
            
            # Create large dataset
            large_precipitation_data = [10.5 + i * 0.1 for i in range(1000)]
            large_temperature_data = [22.5 + i * 0.05 for i in range(1000)]
            
            mock_weather.return_value = {
                "precipitation": large_precipitation_data,
                "temperature": large_temperature_data,
                "humidity": [50.0] * 1000,
                "wind_speed": [10.0] * 1000
            }
            mock_soil.return_value = {
                "available_water_capacity": 2.5,
                "field_capacity": 0.35,
                "wilting_point": 0.15,
                "current_moisture": 0.25
            }
            mock_calc.calculate_spi = AsyncMock(return_value=[-0.8, -1.2, -1.5, -1.3])
            mock_calc.calculate_pdsi = AsyncMock(return_value=-1.4)
            mock_calc.calculate_spei = AsyncMock(return_value=[-0.9, -1.1, -1.4, -1.2])
            
            # Process large dataset
            result = await service.calculate_drought_indices(uuid4(), uuid4())
            
            # Get memory usage after processing
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            # Memory assertions
            assert memory_increase < 100, f"Memory increase {memory_increase:.2f}MB exceeds 100MB limit"
            assert final_memory < 500, f"Final memory usage {final_memory:.2f}MB exceeds 500MB limit"
            
            print(f"Memory usage: initial={initial_memory:.2f}MB, final={final_memory:.2f}MB, increase={memory_increase:.2f}MB")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # Mock external services
        with patch.object(service, '_get_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_data') as mock_soil:
            
            mock_weather.return_value = {"precipitation": 5.0, "temperature": 25.0}
            mock_soil.return_value = {"moisture_content": 0.25}
            
            # Get initial memory usage
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Perform repeated operations
            num_iterations = 100
            for i in range(num_iterations):
                await service.assess_drought_risk(
                    farm_location_id=uuid4(),
                    field_id=uuid4(),
                    crop_type="corn"
                )
                
                # Check memory every 20 iterations
                if i % 20 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_increase = current_memory - initial_memory
                    
                    # Allow some memory increase but not excessive
                    assert memory_increase < 50, f"Memory leak detected: {memory_increase:.2f}MB increase after {i} iterations"
            
            # Final memory check
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            total_memory_increase = final_memory - initial_memory
            
            assert total_memory_increase < 100, f"Total memory increase {total_memory_increase:.2f}MB exceeds 100MB limit"
            
            print(f"Memory leak test: {num_iterations} iterations, total increase: {total_memory_increase:.2f}MB")


class TestStressTests:
    """Stress tests for system limits."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_high_load_stress_test(self):
        """Test system behavior under high load."""
        from src.services.drought_assessment_service import DroughtAssessmentService
        
        service = DroughtAssessmentService()
        await service.initialize()
        
        # Mock external services
        with patch.object(service, '_get_weather_data') as mock_weather, \
             patch.object(service, '_get_soil_data') as mock_soil:
            
            mock_weather.return_value = {"precipitation": 5.0, "temperature": 25.0}
            mock_soil.return_value = {"moisture_content": 0.25}
            
            # High load test
            num_requests = 200
            farm_ids = [uuid4() for _ in range(num_requests)]
            
            start_time = time.time()
            
            # Create tasks in batches to avoid overwhelming the system
            batch_size = 50
            all_results = []
            
            for i in range(0, num_requests, batch_size):
                batch_farm_ids = farm_ids[i:i + batch_size]
                tasks = [
                    service.assess_drought_risk(farm_id, uuid4(), "corn")
                    for farm_id in batch_farm_ids
                ]
                
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                all_results.extend(batch_results)
            
            total_time = time.time() - start_time
            
            # Count successful and failed requests
            successful_requests = sum(1 for result in all_results if not isinstance(result, Exception))
            failed_requests = len(all_results) - successful_requests
            
            # Stress test assertions
            assert successful_requests >= num_requests * 0.95, f"Success rate {successful_requests/num_requests:.2%} below 95% threshold"
            assert failed_requests <= num_requests * 0.05, f"Failure rate {failed_requests/num_requests:.2%} above 5% threshold"
            assert total_time < 30.0, f"Total time {total_time:.3f}s exceeds 30s limit"
            
            print(f"Stress test: {successful_requests}/{num_requests} successful, {failed_requests} failed, time: {total_time:.3f}s")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_resource_exhaustion_test(self):
        """Test system behavior when resources are exhausted."""
        from src.services.moisture_conservation_service import MoistureConservationService
        
        service = MoistureConservationService()
        await service.initialize()
        
        # Test with extreme input values
        extreme_conditions = [
            {"slope_percent": 0.1},  # Very flat
            {"slope_percent": 45.0},  # Very steep
            {"soil_moisture": 0.01},  # Very dry
            {"soil_moisture": 0.49},  # Very wet
        ]
        
        for condition in extreme_conditions:
            try:
                result = await service.recommend_conservation_practices(
                    field_id=uuid4(),
                    soil_type="clay_loam",
                    current_practices=[],
                    **condition
                )
                
                # Should still return valid results
                assert result is not None
                assert "recommended_practices" in result
                
            except Exception as e:
                # Should handle extreme conditions gracefully
                assert "invalid" in str(e).lower() or "range" in str(e).lower()


class TestScalabilityTests:
    """Test system scalability."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_data_volume_scalability(self):
        """Test system performance with varying data volumes."""
        from src.services.drought_monitoring_service import DroughtMonitoringService
        
        service = DroughtMonitoringService()
        await service.initialize()
        
        # Test different data volumes
        data_volumes = [100, 500, 1000, 2000]  # Number of data points
        response_times = []
        
        for volume in data_volumes:
            with patch.object(service, '_get_historical_weather_data') as mock_weather, \
                 patch.object(service, '_get_soil_moisture_data') as mock_soil, \
                 patch.object(service, 'drought_indices_calculator') as mock_calc:
                
                # Create data of specified volume
                precipitation_data = [10.5 + i * 0.1 for i in range(volume)]
                temperature_data = [22.5 + i * 0.05 for i in range(volume)]
                
                mock_weather.return_value = {
                    "precipitation": precipitation_data,
                    "temperature": temperature_data,
                    "humidity": [50.0] * volume,
                    "wind_speed": [10.0] * volume
                }
                mock_soil.return_value = {
                    "available_water_capacity": 2.5,
                    "field_capacity": 0.35,
                    "wilting_point": 0.15,
                    "current_moisture": 0.25
                }
                mock_calc.calculate_spi = AsyncMock(return_value=[-0.8, -1.2, -1.5, -1.3])
                mock_calc.calculate_pdsi = AsyncMock(return_value=-1.4)
                mock_calc.calculate_spei = AsyncMock(return_value=[-0.9, -1.1, -1.4, -1.2])
                
                start_time = time.time()
                result = await service.calculate_drought_indices(uuid4(), uuid4())
                response_time = time.time() - start_time
                
                response_times.append((volume, response_time))
                
                assert result is not None
        
        # Analyze scalability
        print("Scalability analysis:")
        for volume, response_time in response_times:
            print(f"  {volume} data points: {response_time:.3f}s")
        
        # Check that response time doesn't increase dramatically with data volume
        small_volume_time = response_times[0][1]  # 100 data points
        large_volume_time = response_times[-1][1]  # 2000 data points
        
        # Response time should not increase more than 5x for 20x data increase
        assert large_volume_time < small_volume_time * 5, f"Response time scaling poor: {large_volume_time:.3f}s vs {small_volume_time:.3f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "performance"])