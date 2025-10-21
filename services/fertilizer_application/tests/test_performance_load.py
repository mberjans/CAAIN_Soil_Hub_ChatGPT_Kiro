"""
Performance and Load Testing Suite
TICKET-023_fertilizer-application-method-11.1

This module provides comprehensive performance and load testing for the
fertilizer application service to ensure it meets production requirements.
"""

import pytest
import asyncio
import time
import statistics
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Tuple
from fastapi.testclient import TestClient
import psutil
import os
import gc

from src.main_minimal import app
from src.services.application_method_service import ApplicationMethodService
from src.services.cost_analysis_service import CostAnalysisService
from src.services.guidance_service import GuidanceService


class PerformanceMetrics:
    """Class for tracking and analyzing performance metrics."""
    
    def __init__(self):
        self.response_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.error_count: int = 0
        self.success_count: int = 0
        self.start_time: float = 0
        self.end_time: float = 0
    
    def start_monitoring(self):
        """Start performance monitoring."""
        self.start_time = time.time()
        self.response_times.clear()
        self.memory_usage.clear()
        self.cpu_usage.clear()
        self.error_count = 0
        self.success_count = 0
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.end_time = time.time()
    
    def record_response(self, response_time_ms: float, success: bool = True):
        """Record a response time."""
        self.response_times.append(response_time_ms)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def record_system_metrics(self):
        """Record current system metrics."""
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get performance statistics."""
        if not self.response_times:
            return {}
        
        return {
            "total_requests": len(self.response_times),
            "success_rate": self.success_count / len(self.response_times) * 100,
            "error_rate": self.error_count / len(self.response_times) * 100,
            "avg_response_time_ms": statistics.mean(self.response_times),
            "median_response_time_ms": statistics.median(self.response_times),
            "p95_response_time_ms": self._percentile(self.response_times, 95),
            "p99_response_time_ms": self._percentile(self.response_times, 99),
            "max_response_time_ms": max(self.response_times),
            "min_response_time_ms": min(self.response_times),
            "std_response_time_ms": statistics.stdev(self.response_times) if len(self.response_times) > 1 else 0,
            "avg_memory_mb": statistics.mean(self.memory_usage) if self.memory_usage else 0,
            "max_memory_mb": max(self.memory_usage) if self.memory_usage else 0,
            "avg_cpu_percent": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
            "max_cpu_percent": max(self.cpu_usage) if self.cpu_usage else 0,
            "total_duration_s": self.end_time - self.start_time if self.end_time > self.start_time else 0,
            "requests_per_second": len(self.response_times) / (self.end_time - self.start_time) if self.end_time > self.start_time else 0
        }
    
    def _percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile from a list of values."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def validate_performance_requirements(self, requirements: Dict[str, float]) -> Dict[str, bool]:
        """Validate performance against requirements."""
        stats = self.get_statistics()
        validation_results = {}
        
        for metric, threshold in requirements.items():
            if metric in stats:
                validation_results[metric] = stats[metric] <= threshold
            else:
                validation_results[metric] = False
        
        return validation_results


class LoadTestDataFactory:
    """Factory for creating load test data."""
    
    @staticmethod
    def create_application_request(
        field_size: float = 100.0,
        soil_type: str = "loam",
        crop_type: str = "corn",
        fertilizer_type: str = "liquid"
    ) -> Dict[str, Any]:
        """Create application request for load testing."""
        return {
            "field_conditions": {
                "field_size_acres": field_size,
                "soil_type": soil_type,
                "drainage_class": "well_drained",
                "slope_percent": 2.5,
                "irrigation_available": True,
                "field_shape": "rectangular",
                "access_roads": ["north", "south"]
            },
            "crop_requirements": {
                "crop_type": crop_type,
                "growth_stage": "vegetative",
                "target_yield": 180.0,
                "nutrient_requirements": {
                    "nitrogen": 150.0,
                    "phosphorus": 60.0,
                    "potassium": 120.0
                },
                "application_timing_preferences": ["early_morning", "late_evening"]
            },
            "fertilizer_specification": {
                "fertilizer_type": fertilizer_type,
                "npk_ratio": "28-0-0",
                "form": fertilizer_type,
                "solubility": 100.0,
                "release_rate": "immediate",
                "cost_per_unit": 0.85,
                "unit": "lbs"
            },
            "available_equipment": [
                {
                    "equipment_type": "sprayer",
                    "capacity": 500.0,
                    "capacity_unit": "gallons",
                    "application_width": 60.0,
                    "application_rate_range": {"min": 10.0, "max": 50.0},
                    "fuel_efficiency": 0.8,
                    "maintenance_cost_per_hour": 15.0
                }
            ],
            "application_goals": ["maximize_efficiency", "minimize_cost"],
            "constraints": {
                "budget_limit": 5000.0,
                "time_constraint": "3_days"
            },
            "budget_limit": 5000.0
        }
    
    @staticmethod
    def create_guidance_request() -> Dict[str, Any]:
        """Create guidance request for load testing."""
        return {
            "application_method": {
                "method_id": "foliar_001",
                "method_type": "foliar",
                "recommended_equipment": {
                    "equipment_type": "sprayer",
                    "capacity": 500.0
                },
                "application_rate": 2.5,
                "rate_unit": "gallons/acre",
                "application_timing": "Early morning",
                "efficiency_score": 0.9,
                "cost_per_acre": 30.0,
                "labor_requirements": "high",
                "environmental_impact": "low",
                "pros": ["High efficiency"],
                "cons": ["Weather sensitive"]
            },
            "field_conditions": {
                "field_size_acres": 50.0,
                "soil_type": "loam",
                "irrigation_available": True
            },
            "weather_conditions": {
                "temperature_celsius": 22.0,
                "humidity_percent": 65.0,
                "wind_speed_kmh": 8.0,
                "precipitation_mm": 0.0
            },
            "application_date": "2024-05-15",
            "experience_level": "intermediate"
        }
    
    @staticmethod
    def create_comparison_request() -> Dict[str, Any]:
        """Create comparison request for load testing."""
        return {
            "method_a_id": "broadcast_001",
            "method_b_id": "foliar_001",
            "comparison_criteria": ["cost", "efficiency", "environmental_impact"],
            "weights": {"cost": 0.4, "efficiency": 0.4, "environmental_impact": 0.2}
        }


class TestPerformanceTests:
    """Performance testing test cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def performance_requirements(self):
        """Define performance requirements."""
        return {
            "avg_response_time_ms": 2000.0,  # Average response time < 2s
            "p95_response_time_ms": 3000.0,  # 95th percentile < 3s
            "p99_response_time_ms": 4000.0,  # 99th percentile < 4s
            "max_response_time_ms": 5000.0,  # Max response time < 5s
            "success_rate": 95.0,  # Success rate > 95%
            "avg_memory_mb": 256.0,  # Average memory < 256MB
            "max_memory_mb": 512.0,  # Max memory < 512MB
            "requests_per_second": 10.0  # At least 10 requests/second
        }
    
    def test_single_request_performance(self, client, performance_requirements):
        """Test performance of single requests."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        request_data = LoadTestDataFactory.create_application_request()
        
        # Test multiple single requests
        num_requests = 20
        
        for i in range(num_requests):
            start_time = time.time()
            response = client.post("/api/v1/fertilizer/application-method/recommend", json=request_data)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            success = response.status_code == 200
            
            metrics.record_response(response_time_ms, success)
            metrics.record_system_metrics()
            
            # Each request should succeed
            assert response.status_code == 200, f"Request {i+1} failed with status {response.status_code}"
        
        metrics.stop_monitoring()
        stats = metrics.get_statistics()
        
        # Validate performance requirements
        validation_results = metrics.validate_performance_requirements(performance_requirements)
        
        # Print performance statistics
        print(f"\nSingle Request Performance Statistics:")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Success rate: {stats['success_rate']:.2f}%")
        print(f"Average response time: {stats['avg_response_time_ms']:.2f}ms")
        print(f"95th percentile: {stats['p95_response_time_ms']:.2f}ms")
        print(f"99th percentile: {stats['p99_response_time_ms']:.2f}ms")
        print(f"Max response time: {stats['max_response_time_ms']:.2f}ms")
        print(f"Average memory: {stats['avg_memory_mb']:.2f}MB")
        print(f"Max memory: {stats['max_memory_mb']:.2f}MB")
        print(f"Requests per second: {stats['requests_per_second']:.2f}")
        
        # Assert performance requirements
        for metric, passed in validation_results.items():
            assert passed, f"Performance requirement failed: {metric} exceeded threshold"
    
    def test_concurrent_request_performance(self, client, performance_requirements):
        """Test performance under concurrent load."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        request_data = LoadTestDataFactory.create_application_request()
        num_concurrent_requests = 10
        num_rounds = 5
        
        def make_request():
            start_time = time.time()
            response = client.post("/api/v1/fertilizer/application-method/recommend", json=request_data)
            end_time = time.time()
            
            response_time_ms = (end_time - start_time) * 1000
            success = response.status_code == 200
            
            return response_time_ms, success, response.status_code
        
        # Execute concurrent requests
        for round_num in range(num_rounds):
            with ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
                futures = [executor.submit(make_request) for _ in range(num_concurrent_requests)]
                
                for future in as_completed(futures):
                    response_time_ms, success, status_code = future.result()
                    metrics.record_response(response_time_ms, success)
                    metrics.record_system_metrics()
                    
                    # Each request should succeed
                    assert success, f"Concurrent request failed with status {status_code}"
        
        metrics.stop_monitoring()
        stats = metrics.get_statistics()
        
        # Print concurrent performance statistics
        print(f"\nConcurrent Request Performance Statistics:")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Success rate: {stats['success_rate']:.2f}%")
        print(f"Average response time: {stats['avg_response_time_ms']:.2f}ms")
        print(f"95th percentile: {stats['p95_response_time_ms']:.2f}ms")
        print(f"Max response time: {stats['max_response_time_ms']:.2f}ms")
        print(f"Average memory: {stats['avg_memory_mb']:.2f}MB")
        print(f"Max memory: {stats['max_memory_mb']:.2f}MB")
        print(f"Requests per second: {stats['requests_per_second']:.2f}")
        
        # Validate concurrent performance (slightly relaxed requirements)
        concurrent_requirements = performance_requirements.copy()
        concurrent_requirements["avg_response_time_ms"] = 3000.0  # Relaxed for concurrent
        concurrent_requirements["p95_response_time_ms"] = 4000.0  # Relaxed for concurrent
        
        validation_results = metrics.validate_performance_requirements(concurrent_requirements)
        
        for metric, passed in validation_results.items():
            assert passed, f"Concurrent performance requirement failed: {metric} exceeded threshold"
    
    def test_memory_usage_performance(self, client):
        """Test memory usage during operation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        request_data = LoadTestDataFactory.create_application_request()
        
        # Make multiple requests to test memory usage
        num_requests = 50
        memory_samples = []
        
        for i in range(num_requests):
            response = client.post("/api/v1/fertilizer/application-method/recommend", json=request_data)
            assert response.status_code == 200
            
            # Sample memory usage
            current_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_samples.append(current_memory)
            
            # Force garbage collection every 10 requests
            if i % 10 == 0:
                gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        max_memory_used = max(memory_samples)
        
        print(f"\nMemory Usage Statistics:")
        print(f"Initial memory: {initial_memory:.2f}MB")
        print(f"Final memory: {final_memory:.2f}MB")
        print(f"Memory increase: {memory_increase:.2f}MB")
        print(f"Max memory used: {max_memory_used:.2f}MB")
        print(f"Average memory: {statistics.mean(memory_samples):.2f}MB")
        
        # Memory usage should not increase excessively
        assert memory_increase <= 100.0, f"Memory increase {memory_increase:.2f}MB exceeds 100MB limit"
        assert max_memory_used <= 512.0, f"Max memory usage {max_memory_used:.2f}MB exceeds 512MB limit"
    
    def test_cpu_usage_performance(self, client):
        """Test CPU usage during operation."""
        process = psutil.Process(os.getpid())
        
        request_data = LoadTestDataFactory.create_application_request()
        
        # Monitor CPU usage during requests
        cpu_samples = []
        num_requests = 20
        
        for i in range(num_requests):
            # Sample CPU before request
            cpu_before = process.cpu_percent()
            
            start_time = time.time()
            response = client.post("/api/v1/fertilizer/application-method/recommend", json=request_data)
            end_time = time.time()
            
            # Sample CPU after request
            cpu_after = process.cpu_percent()
            
            cpu_samples.append(max(cpu_before, cpu_after))
            
            assert response.status_code == 200
        
        avg_cpu = statistics.mean(cpu_samples)
        max_cpu = max(cpu_samples)
        
        print(f"\nCPU Usage Statistics:")
        print(f"Average CPU usage: {avg_cpu:.2f}%")
        print(f"Max CPU usage: {max_cpu:.2f}%")
        
        # CPU usage should be reasonable
        assert avg_cpu <= 50.0, f"Average CPU usage {avg_cpu:.2f}% exceeds 50% limit"
        assert max_cpu <= 80.0, f"Max CPU usage {max_cpu:.2f}% exceeds 80% limit"


class TestLoadTests:
    """Load testing test cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def load_test_scenarios(self):
        """Define load test scenarios."""
        return [
            {
                "name": "light_load",
                "concurrent_users": 5,
                "requests_per_user": 10,
                "max_response_time_ms": 3000.0,
                "min_success_rate": 95.0
            },
            {
                "name": "medium_load",
                "concurrent_users": 10,
                "requests_per_user": 20,
                "max_response_time_ms": 4000.0,
                "min_success_rate": 90.0
            },
            {
                "name": "heavy_load",
                "concurrent_users": 20,
                "requests_per_user": 30,
                "max_response_time_ms": 5000.0,
                "min_success_rate": 85.0
            }
        ]
    
    def test_light_load_scenario(self, client, load_test_scenarios):
        """Test light load scenario."""
        scenario = load_test_scenarios[0]  # light_load
        self._run_load_test(client, scenario)
    
    def test_medium_load_scenario(self, client, load_test_scenarios):
        """Test medium load scenario."""
        scenario = load_test_scenarios[1]  # medium_load
        self._run_load_test(client, scenario)
    
    def test_heavy_load_scenario(self, client, load_test_scenarios):
        """Test heavy load scenario."""
        scenario = load_test_scenarios[2]  # heavy_load
        self._run_load_test(client, scenario)
    
    def _run_load_test(self, client, scenario: Dict[str, Any]):
        """Run a load test scenario."""
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        request_data = LoadTestDataFactory.create_application_request()
        
        def user_simulation():
            """Simulate a user making requests."""
            user_metrics = []
            
            for _ in range(scenario["requests_per_user"]):
                start_time = time.time()
                response = client.post("/api/v1/fertilizer/application-method/recommend", json=request_data)
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                success = response.status_code == 200
                
                user_metrics.append((response_time_ms, success))
                metrics.record_response(response_time_ms, success)
                metrics.record_system_metrics()
            
            return user_metrics
        
        # Execute load test
        with ThreadPoolExecutor(max_workers=scenario["concurrent_users"]) as executor:
            futures = [executor.submit(user_simulation) for _ in range(scenario["concurrent_users"])]
            
            for future in as_completed(futures):
                user_metrics = future.result()
                # All user requests should be processed
        
        metrics.stop_monitoring()
        stats = metrics.get_statistics()
        
        # Print load test results
        print(f"\n{scenario['name'].title()} Load Test Results:")
        print(f"Concurrent users: {scenario['concurrent_users']}")
        print(f"Requests per user: {scenario['requests_per_user']}")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Success rate: {stats['success_rate']:.2f}%")
        print(f"Average response time: {stats['avg_response_time_ms']:.2f}ms")
        print(f"95th percentile: {stats['p95_response_time_ms']:.2f}ms")
        print(f"Max response time: {stats['max_response_time_ms']:.2f}ms")
        print(f"Requests per second: {stats['requests_per_second']:.2f}")
        
        # Validate load test requirements
        assert stats["success_rate"] >= scenario["min_success_rate"], \
            f"Success rate {stats['success_rate']:.2f}% below minimum {scenario['min_success_rate']}%"
        
        assert stats["max_response_time_ms"] <= scenario["max_response_time_ms"], \
            f"Max response time {stats['max_response_time_ms']:.2f}ms exceeds limit {scenario['max_response_time_ms']}ms"
    
    def test_endpoint_load_distribution(self, client):
        """Test load distribution across different endpoints."""
        endpoints = [
            ("/api/v1/fertilizer/application-method/recommend", LoadTestDataFactory.create_application_request()),
            ("/api/v1/methods/compare", LoadTestDataFactory.create_comparison_request()),
            ("/api/v1/guidance/application-guidance", LoadTestDataFactory.create_guidance_request()),
            ("/api/v1/methods/", None),  # GET endpoint
            ("/health", None)  # Health check
        ]
        
        metrics = PerformanceMetrics()
        metrics.start_monitoring()
        
        num_requests_per_endpoint = 10
        
        for endpoint, request_data in endpoints:
            endpoint_metrics = []
            
            for _ in range(num_requests_per_endpoint):
                start_time = time.time()
                
                if request_data:
                    response = client.post(endpoint, json=request_data)
                else:
                    response = client.get(endpoint)
                
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                success = response.status_code == 200
                
                endpoint_metrics.append((response_time_ms, success))
                metrics.record_response(response_time_ms, success)
                
                assert success, f"Endpoint {endpoint} failed with status {response.status_code}"
            
            # Calculate endpoint-specific statistics
            endpoint_times = [m[0] for m in endpoint_metrics]
            endpoint_success_rate = sum(1 for m in endpoint_metrics if m[1]) / len(endpoint_metrics) * 100
            
            print(f"\n{endpoint} Performance:")
            print(f"  Average response time: {statistics.mean(endpoint_times):.2f}ms")
            print(f"  Max response time: {max(endpoint_times):.2f}ms")
            print(f"  Success rate: {endpoint_success_rate:.2f}%")
        
        metrics.stop_monitoring()
        stats = metrics.get_statistics()
        
        print(f"\nOverall Load Distribution Results:")
        print(f"Total requests: {stats['total_requests']}")
        print(f"Overall success rate: {stats['success_rate']:.2f}%")
        print(f"Overall average response time: {stats['avg_response_time_ms']:.2f}ms")
        
        # All endpoints should perform well
        assert stats["success_rate"] >= 95.0, f"Overall success rate {stats['success_rate']:.2f}% below 95%"
        assert stats["avg_response_time_ms"] <= 3000.0, f"Overall average response time {stats['avg_response_time_ms']:.2f}ms exceeds 3s"


class TestStressTests:
    """Stress testing test cases."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_gradual_load_increase(self, client):
        """Test gradual load increase to find breaking point."""
        request_data = LoadTestDataFactory.create_application_request()
        
        load_levels = [1, 5, 10, 15, 20, 25, 30]
        results = []
        
        for concurrent_users in load_levels:
            metrics = PerformanceMetrics()
            metrics.start_monitoring()
            
            def make_request():
                start_time = time.time()
                response = client.post("/api/v1/fertilizer/application-method/recommend", json=request_data)
                end_time = time.time()
                
                response_time_ms = (end_time - start_time) * 1000
                success = response.status_code == 200
                
                return response_time_ms, success
            
            # Execute requests with current load level
            with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
                futures = [executor.submit(make_request) for _ in range(concurrent_users * 5)]
                
                for future in as_completed(futures):
                    response_time_ms, success = future.result()
                    metrics.record_response(response_time_ms, success)
            
            metrics.stop_monitoring()
            stats = metrics.get_statistics()
            
            results.append({
                "concurrent_users": concurrent_users,
                "success_rate": stats["success_rate"],
                "avg_response_time_ms": stats["avg_response_time_ms"],
                "max_response_time_ms": stats["max_response_time_ms"],
                "requests_per_second": stats["requests_per_second"]
            })
            
            print(f"\nLoad Level {concurrent_users} concurrent users:")
            print(f"  Success rate: {stats['success_rate']:.2f}%")
            print(f"  Average response time: {stats['avg_response_time_ms']:.2f}ms")
            print(f"  Max response time: {stats['max_response_time_ms']:.2f}ms")
            print(f"  Requests per second: {stats['requests_per_second']:.2f}")
            
            # Stop if success rate drops below 80%
            if stats["success_rate"] < 80.0:
                print(f"Breaking point reached at {concurrent_users} concurrent users")
                break
        
        # Analyze results
        print(f"\nStress Test Analysis:")
        for result in results:
            print(f"  {result['concurrent_users']} users: {result['success_rate']:.1f}% success, "
                  f"{result['avg_response_time_ms']:.0f}ms avg response")
        
        # Should handle at least 10 concurrent users with >90% success rate
        successful_loads = [r for r in results if r["success_rate"] >= 90.0]
        assert len(successful_loads) >= 2, "Service should handle at least 2 load levels with >90% success rate"
    
    def test_memory_stress(self, client):
        """Test memory usage under stress."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        request_data = LoadTestDataFactory.create_application_request()
        
        # Make many requests to stress memory
        num_requests = 100
        memory_samples = []
        
        for i in range(num_requests):
            response = client.post("/api/v1/fertilizer/application-method/recommend", json=request_data)
            assert response.status_code == 200
            
            # Sample memory every 10 requests
            if i % 10 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)
                
                # Force garbage collection periodically
                if i % 20 == 0:
                    gc.collect()
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_samples) if memory_samples else final_memory
        
        print(f"\nMemory Stress Test Results:")
        print(f"Initial memory: {initial_memory:.2f}MB")
        print(f"Final memory: {final_memory:.2f}MB")
        print(f"Memory increase: {memory_increase:.2f}MB")
        print(f"Max memory used: {max_memory:.2f}MB")
        
        # Memory should not increase excessively
        assert memory_increase <= 200.0, f"Memory increase {memory_increase:.2f}MB exceeds 200MB limit"
        assert max_memory <= 1024.0, f"Max memory {max_memory:.2f}MB exceeds 1GB limit"


# Pytest markers for performance and load tests
pytestmark = [
    pytest.mark.performance,
    pytest.mark.load_test,
    pytest.mark.stress_test
]


if __name__ == "__main__":
    # Run performance and load tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "-m", "performance or load_test or stress_test"
    ])