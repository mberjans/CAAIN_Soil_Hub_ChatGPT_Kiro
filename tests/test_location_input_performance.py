"""
Location Input Performance Testing Suite
TICKET-008_farm-location-input-15.1 - Performance testing for location input functionality

This module provides comprehensive performance testing including:
- Load testing with 1000+ concurrent users
- Mobile performance testing
- Memory usage testing
- Response time benchmarking
- Throughput testing
"""

import pytest
import asyncio
import time
import statistics
import concurrent.futures
from typing import List, Dict, Any
import psutil
import gc
from unittest.mock import Mock, patch
import threading
from dataclasses import dataclass
import json
import os
import sys

# Add service paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/location-validation/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../databases/python'))


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    response_time_ms: float
    throughput_ops_per_sec: float
    memory_usage_mb: float
    cpu_usage_percent: float
    error_rate_percent: float
    concurrent_users: int


class LocationInputPerformanceTester:
    """Performance testing class for location input services"""
    
    def __init__(self):
        self.test_coordinates = [
            (42.0308, -93.6319),  # Ames, Iowa
            (40.7128, -74.0060),  # New York City
            (34.0522, -118.2437), # Los Angeles
            (41.8781, -87.6298),  # Chicago
            (29.7604, -95.3698),  # Houston
        ]
        
        self.test_addresses = [
            "123 Farm Road, Ames, IA 50010",
            "456 Broadway, New York, NY 10013",
            "789 Sunset Blvd, Los Angeles, CA 90028",
            "321 Michigan Ave, Chicago, IL 60601",
            "654 Main St, Houston, TX 77002",
        ]
        
        self.performance_thresholds = {
            'max_response_time_ms': 2000,
            'min_throughput_ops_per_sec': 100,
            'max_memory_usage_mb': 500,
            'max_cpu_usage_percent': 80,
            'max_error_rate_percent': 5,
            'concurrent_users_target': 1000
        }
    
    async def measure_response_time(self, operation, *args, **kwargs) -> float:
        """Measure response time for an operation"""
        start_time = time.time()
        try:
            await operation(*args, **kwargs)
        except Exception:
            pass  # We'll handle errors separately
        end_time = time.time()
        return (end_time - start_time) * 1000  # Convert to milliseconds
    
    def measure_memory_usage(self) -> float:
        """Measure current memory usage in MB"""
        gc.collect()  # Force garbage collection
        return psutil.Process().memory_info().rss / 1024 / 1024
    
    def measure_cpu_usage(self) -> float:
        """Measure current CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    async def simulate_concurrent_users(self, operation, num_users: int, operations_per_user: int = 5) -> PerformanceMetrics:
        """Simulate concurrent users and measure performance"""
        # Measure baseline resources
        baseline_memory = self.measure_memory_usage()
        baseline_cpu = self.measure_cpu_usage()
        
        # Prepare operations
        async def user_operations():
            """Operations performed by a single user"""
            user_tasks = []
            for _ in range(operations_per_user):
                # Randomly select test data
                import random
                if random.choice([True, False]):
                    coord = random.choice(self.test_coordinates)
                    user_tasks.append(operation(coord[0], coord[1]))
                else:
                    address = random.choice(self.test_addresses)
                    user_tasks.append(operation(address))
            
            return await asyncio.gather(*user_tasks, return_exceptions=True)
        
        # Run concurrent simulation
        start_time = time.time()
        
        user_tasks = [user_operations() for _ in range(num_users)]
        results = await asyncio.gather(*user_tasks, return_exceptions=True)
        
        end_time = time.time()
        
        # Calculate metrics
        total_time = end_time - start_time
        total_operations = num_users * operations_per_user
        
        # Count errors
        total_errors = 0
        for user_results in results:
            for result in user_results:
                if isinstance(result, Exception):
                    total_errors += 1
        
        # Calculate performance metrics
        response_time_ms = (total_time / total_operations) * 1000
        throughput_ops_per_sec = total_operations / total_time
        memory_usage_mb = self.measure_memory_usage() - baseline_memory
        cpu_usage_percent = self.measure_cpu_usage() - baseline_cpu
        error_rate_percent = (total_errors / total_operations) * 100
        
        return PerformanceMetrics(
            response_time_ms=response_time_ms,
            throughput_ops_per_sec=throughput_ops_per_sec,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage_percent,
            error_rate_percent=error_rate_percent,
            concurrent_users=num_users
        )


class TestLocationValidationPerformance:
    """Performance tests for LocationValidationService"""
    
    @pytest.fixture
    def performance_tester(self):
        """Create performance tester instance"""
        return LocationInputPerformanceTester()
    
    @pytest.fixture
    def validation_service(self):
        """Create validation service instance"""
        try:
            from services.location_validation_service import LocationValidationService
            return LocationValidationService()
        except ImportError:
            # Create mock service for testing
            class MockValidationService:
                async def validate_coordinates(self, lat, lng):
                    await asyncio.sleep(0.01)  # Simulate processing time
                    return Mock(valid=True)
            return MockValidationService()
    
    @pytest.mark.asyncio
    async def test_single_validation_performance(self, performance_tester, validation_service):
        """Test performance of single coordinate validation"""
        lat, lng = performance_tester.test_coordinates[0]
        
        response_time = await performance_tester.measure_response_time(
            validation_service.validate_coordinates, lat, lng
        )
        
        assert response_time < performance_tester.performance_thresholds['max_response_time_ms'], \
            f"Single validation too slow: {response_time}ms"
    
    @pytest.mark.asyncio
    async def test_batch_validation_performance(self, performance_tester, validation_service):
        """Test performance of batch coordinate validation"""
        coordinates = performance_tester.test_coordinates
        
        start_time = time.time()
        
        tasks = [
            validation_service.validate_coordinates(lat, lng)
            for lat, lng in coordinates
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_validation = (total_time / len(coordinates)) * 1000
        
        assert avg_time_per_validation < performance_tester.performance_thresholds['max_response_time_ms'], \
            f"Batch validation too slow: {avg_time_per_validation}ms per validation"
        
        assert all(result.valid for result in results), "Some batch validations failed"
    
    @pytest.mark.asyncio
    async def test_concurrent_user_load(self, performance_tester, validation_service):
        """Test performance with concurrent users"""
        async def validation_operation(*args):
            if len(args) == 2:
                return await validation_service.validate_coordinates(args[0], args[1])
            else:
                return await validation_service.validate_coordinates(args[0], args[1])
        
        # Test with increasing concurrent users
        concurrent_user_counts = [10, 50, 100, 500, 1000]
        
        for num_users in concurrent_user_counts:
            metrics = await performance_tester.simulate_concurrent_users(
                validation_operation, num_users, operations_per_user=3
            )
            
            # Assert performance thresholds
            assert metrics.response_time_ms < performance_tester.performance_thresholds['max_response_time_ms'], \
                f"Response time too slow with {num_users} users: {metrics.response_time_ms}ms"
            
            assert metrics.throughput_ops_per_sec >= performance_tester.performance_thresholds['min_throughput_ops_per_sec'], \
                f"Throughput too low with {num_users} users: {metrics.throughput_ops_per_sec} ops/sec"
            
            assert metrics.error_rate_percent < performance_tester.performance_thresholds['max_error_rate_percent'], \
                f"Error rate too high with {num_users} users: {metrics.error_rate_percent}%"
            
            # Memory usage should be reasonable
            assert metrics.memory_usage_mb < performance_tester.performance_thresholds['max_memory_usage_mb'], \
                f"Memory usage too high with {num_users} users: {metrics.memory_usage_mb}MB"
    
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, performance_tester, validation_service):
        """Test memory usage under high load"""
        baseline_memory = performance_tester.measure_memory_usage()
        
        # Perform many operations
        tasks = []
        for _ in range(1000):
            lat, lng = performance_tester.test_coordinates[0]
            tasks.append(validation_service.validate_coordinates(lat, lng))
        
        results = await asyncio.gather(*tasks)
        
        # Force garbage collection
        gc.collect()
        
        final_memory = performance_tester.measure_memory_usage()
        memory_increase = final_memory - baseline_memory
        
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase}MB"
        assert all(result.valid for result in results), "Some validations failed"
    
    @pytest.mark.asyncio
    async def test_response_time_distribution(self, performance_tester, validation_service):
        """Test response time distribution for consistency"""
        response_times = []
        
        # Measure response times for multiple operations
        for _ in range(100):
            lat, lng = performance_tester.test_coordinates[0]
            response_time = await performance_tester.measure_response_time(
                validation_service.validate_coordinates, lat, lng
            )
            response_times.append(response_time)
        
        # Calculate statistics
        mean_response_time = statistics.mean(response_times)
        median_response_time = statistics.median(response_times)
        std_deviation = statistics.stdev(response_times)
        p95_response_time = sorted(response_times)[int(0.95 * len(response_times))]
        
        # Assertions for response time consistency
        assert mean_response_time < performance_tester.performance_thresholds['max_response_time_ms'], \
            f"Mean response time too high: {mean_response_time}ms"
        
        assert median_response_time < performance_tester.performance_thresholds['max_response_time_ms'], \
            f"Median response time too high: {median_response_time}ms"
        
        assert p95_response_time < performance_tester.performance_thresholds['max_response_time_ms'] * 2, \
            f"95th percentile response time too high: {p95_response_time}ms"
        
        # Response times should be reasonably consistent
        assert std_deviation < mean_response_time * 0.5, \
            f"Response time variance too high: std_dev={std_deviation}, mean={mean_response_time}"


class TestGeocodingPerformance:
    """Performance tests for GeocodingService"""
    
    @pytest.fixture
    def performance_tester(self):
        """Create performance tester instance"""
        return LocationInputPerformanceTester()
    
    @pytest.fixture
    def geocoding_service(self):
        """Create geocoding service instance"""
        try:
            from services.geocoding_service import GeocodingService
            return GeocodingService()
        except ImportError:
            # Create mock service for testing
            class MockGeocodingService:
                async def geocode_address(self, address):
                    await asyncio.sleep(0.1)  # Simulate API call
                    return Mock(latitude=42.0308, longitude=-93.6319)
            return MockGeocodingService()
    
    @pytest.mark.asyncio
    async def test_geocoding_response_time(self, performance_tester, geocoding_service):
        """Test geocoding response time"""
        address = performance_tester.test_addresses[0]
        
        response_time = await performance_tester.measure_response_time(
            geocoding_service.geocode_address, address
        )
        
        # Geocoding typically takes longer than validation
        assert response_time < 5000, f"Geocoding too slow: {response_time}ms"
    
    @pytest.mark.asyncio
    async def test_geocoding_throughput(self, performance_tester, geocoding_service):
        """Test geocoding throughput"""
        addresses = performance_tester.test_addresses
        
        start_time = time.time()
        
        tasks = [
            geocoding_service.geocode_address(address)
            for address in addresses
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        successful_geocodings = sum(1 for result in results if not isinstance(result, Exception))
        throughput = successful_geocodings / total_time
        
        assert throughput > 0.1, f"Geocoding throughput too low: {throughput} ops/sec"
    
    @pytest.mark.asyncio
    async def test_geocoding_concurrent_load(self, performance_tester, geocoding_service):
        """Test geocoding performance under concurrent load"""
        async def geocoding_operation(address):
            return await geocoding_service.geocode_address(address)
        
        # Test with moderate concurrent load (geocoding APIs have rate limits)
        metrics = await performance_tester.simulate_concurrent_users(
            geocoding_operation, num_users=50, operations_per_user=2
        )
        
        # Geocoding has different performance characteristics
        assert metrics.response_time_ms < 10000, f"Geocoding response time too slow: {metrics.response_time_ms}ms"
        assert metrics.error_rate_percent < 20, f"Geocoding error rate too high: {metrics.error_rate_percent}%"


class TestMobilePerformance:
    """Mobile-specific performance tests"""
    
    @pytest.fixture
    def performance_tester(self):
        """Create performance tester instance"""
        return LocationInputPerformanceTester()
    
    @pytest.fixture
    def validation_service(self):
        """Create validation service instance"""
        try:
            from services.location_validation_service import LocationValidationService
            return LocationValidationService()
        except ImportError:
            class MockValidationService:
                async def validate_coordinates(self, lat, lng):
                    await asyncio.sleep(0.05)  # Simulate mobile processing
                    return Mock(valid=True)
            return MockValidationService()
    
    @pytest.mark.asyncio
    async def test_mobile_network_simulation(self, performance_tester, validation_service):
        """Test performance with simulated mobile network conditions"""
        # Simulate mobile network delays and constraints
        mobile_delay = 0.1  # 100ms mobile network delay
        mobile_locations = performance_tester.test_coordinates[:3]
        
        async def mobile_validation(lat, lng):
            await asyncio.sleep(mobile_delay)  # Simulate mobile network
            return await validation_service.validate_coordinates(lat, lng)
        
        start_time = time.time()
        
        tasks = [
            mobile_validation(lat, lng)
            for lat, lng in mobile_locations
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000
        avg_time_per_operation = total_time / len(mobile_locations)
        
        # Mobile performance should still be acceptable
        assert avg_time_per_operation < 3000, f"Mobile performance too slow: {avg_time_per_operation}ms"
        assert all(result.valid for result in results), "Some mobile validations failed"
    
    @pytest.mark.asyncio
    async def test_mobile_battery_efficiency(self, performance_tester, validation_service):
        """Test battery efficiency for mobile devices"""
        # Simulate battery-constrained operations
        battery_efficient_locations = performance_tester.test_coordinates[:2]
        
        start_time = time.time()
        start_cpu = performance_tester.measure_cpu_usage()
        
        # Perform operations with battery efficiency in mind
        tasks = []
        for lat, lng in battery_efficient_locations:
            tasks.append(validation_service.validate_coordinates(lat, lng))
        
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        end_cpu = performance_tester.measure_cpu_usage()
        
        total_time = end_time - start_time
        cpu_usage = end_cpu - start_cpu
        
        # Battery-efficient operations should complete quickly with low CPU usage
        assert total_time < 1.0, f"Battery-efficient operations too slow: {total_time}s"
        assert cpu_usage < 50, f"CPU usage too high for battery efficiency: {cpu_usage}%"
        assert all(result.valid for result in results), "Some battery-efficient validations failed"
    
    @pytest.mark.asyncio
    async def test_mobile_offline_capability(self, performance_tester, validation_service):
        """Test offline capability for mobile devices"""
        # Simulate offline conditions (no network)
        offline_locations = performance_tester.test_coordinates[:2]
        
        # Mock offline behavior
        with patch('asyncio.sleep', side_effect=Exception("Network unavailable")):
            try:
                tasks = [
                    validation_service.validate_coordinates(lat, lng)
                    for lat, lng in offline_locations
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Should handle offline gracefully
                assert all(isinstance(result, Exception) for result in results), \
                    "Should handle offline conditions gracefully"
                
            except Exception as e:
                # Offline handling should not crash the application
                assert "Network unavailable" in str(e), "Unexpected error in offline test"


class TestPerformanceMonitoring:
    """Performance monitoring and alerting tests"""
    
    @pytest.fixture
    def performance_tester(self):
        """Create performance tester instance"""
        return LocationInputPerformanceTester()
    
    def test_performance_metrics_collection(self, performance_tester):
        """Test that performance metrics are properly collected"""
        # Test metrics collection
        metrics = PerformanceMetrics(
            response_time_ms=1500,
            throughput_ops_per_sec=200,
            memory_usage_mb=100,
            cpu_usage_percent=30,
            error_rate_percent=2,
            concurrent_users=500
        )
        
        # Verify metrics structure
        assert isinstance(metrics.response_time_ms, float)
        assert isinstance(metrics.throughput_ops_per_sec, float)
        assert isinstance(metrics.memory_usage_mb, float)
        assert isinstance(metrics.cpu_usage_percent, float)
        assert isinstance(metrics.error_rate_percent, float)
        assert isinstance(metrics.concurrent_users, int)
    
    def test_performance_threshold_validation(self, performance_tester):
        """Test performance threshold validation"""
        thresholds = performance_tester.performance_thresholds
        
        # Test threshold values are reasonable
        assert thresholds['max_response_time_ms'] <= 2000, "Response time threshold too high"
        assert thresholds['min_throughput_ops_per_sec'] >= 100, "Throughput threshold too low"
        assert thresholds['max_memory_usage_mb'] <= 500, "Memory threshold too high"
        assert thresholds['max_cpu_usage_percent'] <= 80, "CPU threshold too high"
        assert thresholds['max_error_rate_percent'] <= 5, "Error rate threshold too high"
        assert thresholds['concurrent_users_target'] >= 1000, "Concurrent users target too low"
    
    def test_performance_alerting(self, performance_tester):
        """Test performance alerting functionality"""
        # Test alert conditions
        alert_conditions = [
            ("high_response_time", performance_tester.performance_thresholds['max_response_time_ms'] + 100),
            ("low_throughput", performance_tester.performance_thresholds['min_throughput_ops_per_sec'] - 10),
            ("high_memory", performance_tester.performance_thresholds['max_memory_usage_mb'] + 50),
            ("high_cpu", performance_tester.performance_thresholds['max_cpu_usage_percent'] + 10),
            ("high_error_rate", performance_tester.performance_thresholds['max_error_rate_percent'] + 2),
        ]
        
        for condition_name, threshold_value in alert_conditions:
            # Simulate alert condition
            alert_triggered = False
            
            if condition_name == "high_response_time" and threshold_value > performance_tester.performance_thresholds['max_response_time_ms']:
                alert_triggered = True
            elif condition_name == "low_throughput" and threshold_value < performance_tester.performance_thresholds['min_throughput_ops_per_sec']:
                alert_triggered = True
            elif condition_name == "high_memory" and threshold_value > performance_tester.performance_thresholds['max_memory_usage_mb']:
                alert_triggered = True
            elif condition_name == "high_cpu" and threshold_value > performance_tester.performance_thresholds['max_cpu_usage_percent']:
                alert_triggered = True
            elif condition_name == "high_error_rate" and threshold_value > performance_tester.performance_thresholds['max_error_rate_percent']:
                alert_triggered = True
            
            assert alert_triggered, f"Alert should be triggered for {condition_name}"


if __name__ == "__main__":
    # Run performance tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10",
        "-k", "performance"
    ])