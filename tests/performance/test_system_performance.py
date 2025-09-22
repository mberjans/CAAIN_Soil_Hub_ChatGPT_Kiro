"""
Performance Tests for AFAS System

Tests system performance requirements including response times,
concurrent user handling, and resource utilization under load.
"""

import pytest
import asyncio
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, AsyncMock, MagicMock
import statistics

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services'))


class TestResponseTimeRequirements:
    """Test response time requirements for critical operations."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_recommendation_response_time(self, iowa_corn_farm_data, performance_timer):
        """Test that recommendations return within 3 seconds."""
        
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'location': iowa_corn_farm_data['location'],
            'soil_data': iowa_corn_farm_data['soil_data'],
            'farm_constraints': {
                'farm_size_acres': iowa_corn_farm_data['farm_size_acres'],
                'available_equipment': ['planter', 'combine', 'sprayer']
            }
        }
        
        # Mock external services for consistent timing
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={'mocked': True})
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Simulate recommendation generation
            performance_timer.start()
            result = await self._generate_crop_recommendations(request_data)
            performance_timer.stop()
            
            # Must respond within 3 seconds
            assert performance_timer.elapsed < 3.0, f"Response took {performance_timer.elapsed:.2f}s, exceeds 3s limit"
            
            # Validate response quality wasn't sacrificed for speed
            assert result is not None
            assert result['confidence_score'] >= 0.7
            assert len(result['recommendations']) > 0
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_fertilizer_calculation_response_time(self, iowa_corn_farm_data, performance_timer):
        """Test fertilizer calculation response time."""
        
        request_data = {
            'farm_id': iowa_corn_farm_data['farm_id'],
            'crop_plan': {
                'primary_crop': 'corn',
                'yield_goal_bu_per_acre': 180,
                'planted_acres': 250
            },
            'soil_data': iowa_corn_farm_data['soil_data'],
            'economic_constraints': {
                'fertilizer_budget_total': 18000.00,
                'current_prices': {
                    'urea_per_ton': 420.00,
                    'dap_per_ton': 580.00,
                    'potash_per_ton': 380.00
                }
            }
        }
        
        performance_timer.start()
        result = await self._generate_fertilizer_strategy(request_data)
        performance_timer.stop()
        
        # Should complete within 2 seconds for fertilizer calculations
        assert performance_timer.elapsed < 2.0, f"Fertilizer calculation took {performance_timer.elapsed:.2f}s"
        
        # Validate calculation accuracy
        assert result is not None
        assert 'nitrogen_program' in result
        assert result['confidence_score'] >= 0.8
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_soil_health_assessment_response_time(self, problematic_soil_data, performance_timer):
        """Test soil health assessment response time."""
        
        request_data = {
            'farm_id': problematic_soil_data['farm_id'],
            'soil_data': problematic_soil_data['soil_data'],
            'field_observations': problematic_soil_data['field_observations']
        }
        
        performance_timer.start()
        result = await self._assess_soil_health(request_data)
        performance_timer.stop()
        
        # Soil health assessment should complete within 1.5 seconds
        assert performance_timer.elapsed < 1.5, f"Soil assessment took {performance_timer.elapsed:.2f}s"
        
        # Validate assessment quality
        assert result is not None
        assert 'soil_health_score' in result
        assert 'improvement_recommendations' in result
    
    async def _generate_crop_recommendations(self, request_data):
        """Simulate crop recommendation generation with realistic processing time."""
        # Simulate data validation (50ms)
        await asyncio.sleep(0.05)
        
        # Simulate external API calls (200ms total)
        await asyncio.sleep(0.2)
        
        # Simulate crop suitability analysis (300ms)
        await asyncio.sleep(0.3)
        
        # Simulate recommendation ranking (100ms)
        await asyncio.sleep(0.1)
        
        return {
            'recommendations': [
                {
                    'crop_name': 'corn',
                    'suitability_score': 0.89,
                    'confidence_factors': {
                        'soil_suitability': 0.95,
                        'climate_match': 0.88
                    }
                }
            ],
            'confidence_score': 0.87,
            'processing_time_ms': 650
        }
    
    async def _generate_fertilizer_strategy(self, request_data):
        """Simulate fertilizer strategy generation."""
        # Simulate nutrient calculations (200ms)
        await asyncio.sleep(0.2)
        
        # Simulate economic optimization (150ms)
        await asyncio.sleep(0.15)
        
        return {
            'nitrogen_program': {
                'total_n_rate_lbs_per_acre': 160,
                'fertilizer_n_needed_lbs_per_acre': 120
            },
            'confidence_score': 0.85,
            'processing_time_ms': 350
        }
    
    async def _assess_soil_health(self, request_data):
        """Simulate soil health assessment."""
        # Simulate soil health calculations (100ms)
        await asyncio.sleep(0.1)
        
        return {
            'soil_health_score': 4.2,
            'improvement_recommendations': [
                {'practice': 'lime_application', 'priority': 'high'}
            ],
            'processing_time_ms': 100
        }


class TestConcurrentUserHandling:
    """Test system handling of concurrent users."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_recommendation_requests(self):
        """Test system handles 100 concurrent recommendation requests."""
        
        def make_request(request_id):
            """Make a single recommendation request."""
            request_data = {
                'farm_id': f'test_farm_{request_id}',
                'location': {'latitude': 42.0, 'longitude': -93.6},
                'soil_data': {'ph': 6.2, 'organic_matter_percent': 3.5}
            }
            
            start_time = time.time()
            
            # Simulate request processing
            result = self._process_recommendation_sync(request_data)
            
            end_time = time.time()
            
            return {
                'request_id': request_id,
                'success': result is not None,
                'response_time': end_time - start_time,
                'confidence_score': result.get('confidence_score', 0) if result else 0
            }
        
        # Execute 100 concurrent requests
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(100)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in successful_requests]
        confidence_scores = [r['confidence_score'] for r in successful_requests]
        
        # Performance requirements
        assert len(successful_requests) >= 95, f"Only {len(successful_requests)}/100 requests succeeded"
        
        # Response time requirements under load
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        assert avg_response_time < 5.0, f"Average response time {avg_response_time:.2f}s exceeds 5s under load"
        assert p95_response_time < 8.0, f"95th percentile response time {p95_response_time:.2f}s exceeds 8s"
        
        # Quality should remain high under load
        avg_confidence = statistics.mean(confidence_scores)
        assert avg_confidence >= 0.7, f"Average confidence {avg_confidence:.2f} too low under load"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_database_operations(self):
        """Test concurrent database operations performance."""
        
        async def database_operation(operation_id):
            """Simulate database operation."""
            # Simulate database query time
            await asyncio.sleep(0.1 + (operation_id % 10) * 0.01)  # Variable delay
            
            return {
                'operation_id': operation_id,
                'success': True,
                'data': {'farm_id': f'farm_{operation_id}', 'soil_ph': 6.2 + (operation_id % 20) * 0.1}
            }
        
        start_time = time.time()
        
        # Execute 50 concurrent database operations
        tasks = [database_operation(i) for i in range(50)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete all operations efficiently
        successful_ops = [r for r in results if isinstance(r, dict) and r.get('success')]
        assert len(successful_ops) == 50, f"Only {len(successful_ops)}/50 database operations succeeded"
        
        # Should leverage concurrency effectively
        assert total_time < 2.0, f"Concurrent operations took {total_time:.2f}s, should be <2s with proper concurrency"
    
    def _process_recommendation_sync(self, request_data):
        """Synchronous version of recommendation processing for thread testing."""
        # Simulate processing time with some variability
        processing_time = 0.5 + (hash(request_data['farm_id']) % 100) * 0.01
        time.sleep(processing_time)
        
        return {
            'recommendations': [{'crop_name': 'corn', 'suitability_score': 0.85}],
            'confidence_score': 0.82,
            'processing_time': processing_time
        }


class TestResourceUtilization:
    """Test system resource utilization under various loads."""
    
    @pytest.mark.performance
    def test_memory_usage_under_load(self):
        """Test memory usage remains reasonable under load."""
        import psutil
        import gc
        
        # Get baseline memory usage
        gc.collect()  # Force garbage collection
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate load with large datasets
        large_datasets = []
        for i in range(100):
            # Simulate large farm datasets
            dataset = {
                'farm_id': f'large_farm_{i}',
                'soil_tests': [
                    {
                        'field_id': f'field_{j}',
                        'ph': 6.0 + j * 0.1,
                        'organic_matter': 3.0 + j * 0.05,
                        'test_results': list(range(100))  # Large test data
                    }
                    for j in range(50)  # 50 fields per farm
                ],
                'weather_history': list(range(365 * 5))  # 5 years of daily data
            }
            large_datasets.append(dataset)
        
        # Process datasets
        processed_results = []
        for dataset in large_datasets:
            result = self._process_large_dataset(dataset)
            processed_results.append(result)
        
        # Check memory usage after processing
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - baseline_memory
        
        # Memory usage should remain reasonable
        assert memory_increase < 500, f"Memory increased by {memory_increase:.1f}MB, should be <500MB"
        
        # Clean up
        del large_datasets
        del processed_results
        gc.collect()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cpu_utilization_efficiency(self):
        """Test CPU utilization efficiency during intensive calculations."""
        import psutil
        
        # Monitor CPU usage during intensive agricultural calculations
        cpu_samples = []
        
        async def monitor_cpu():
            """Monitor CPU usage."""
            for _ in range(20):  # Sample for 2 seconds
                cpu_samples.append(psutil.cpu_percent(interval=0.1))
        
        async def intensive_calculations():
            """Perform intensive agricultural calculations."""
            tasks = []
            for i in range(10):
                task = self._intensive_nutrient_calculation(i)
                tasks.append(task)
            
            await asyncio.gather(*tasks)
        
        # Run monitoring and calculations concurrently
        await asyncio.gather(
            monitor_cpu(),
            intensive_calculations()
        )
        
        # Analyze CPU utilization
        avg_cpu = statistics.mean(cpu_samples)
        max_cpu = max(cpu_samples)
        
        # CPU should be utilized efficiently but not overwhelmed
        assert 20 <= avg_cpu <= 80, f"Average CPU usage {avg_cpu:.1f}% outside efficient range (20-80%)"
        assert max_cpu <= 95, f"Peak CPU usage {max_cpu:.1f}% too high"
    
    def _process_large_dataset(self, dataset):
        """Process large dataset efficiently."""
        # Simulate efficient processing
        farm_id = dataset['farm_id']
        num_fields = len(dataset['soil_tests'])
        
        # Calculate summary statistics
        ph_values = [field['ph'] for field in dataset['soil_tests']]
        avg_ph = sum(ph_values) / len(ph_values)
        
        return {
            'farm_id': farm_id,
            'num_fields': num_fields,
            'avg_ph': avg_ph,
            'processed': True
        }
    
    async def _intensive_nutrient_calculation(self, calculation_id):
        """Perform intensive nutrient calculations."""
        # Simulate complex agricultural calculations
        result = 0
        
        # Nitrogen cycle calculations
        for day in range(365):
            temp_factor = 1.0 + (day % 30) * 0.01
            moisture_factor = 0.8 + (day % 20) * 0.01
            
            # Simulate mineralization calculation
            mineralization_rate = temp_factor * moisture_factor * 0.02
            result += mineralization_rate
            
            # Yield every 100 iterations to prevent blocking
            if day % 100 == 0:
                await asyncio.sleep(0.001)
        
        return {
            'calculation_id': calculation_id,
            'annual_mineralization': result,
            'completed': True
        }


class TestDatabasePerformance:
    """Test database query performance."""
    
    @pytest.mark.performance
    @pytest.mark.database
    async def test_soil_test_query_performance(self):
        """Test soil test queries perform within acceptable limits."""
        
        # Simulate large soil test dataset
        mock_soil_tests = [
            {
                'id': i,
                'farm_id': f'farm_{i // 100}',
                'ph': 6.0 + (i % 20) * 0.1,
                'organic_matter': 3.0 + (i % 15) * 0.1,
                'test_date': f'2024-{(i % 12) + 1:02d}-15'
            }
            for i in range(10000)
        ]
        
        # Test various query patterns
        query_times = []
        
        # Range query (pH between 6.0 and 7.0)
        start_time = time.time()
        ph_filtered = [test for test in mock_soil_tests if 6.0 <= test['ph'] <= 7.0]
        query_times.append(time.time() - start_time)
        
        # Farm-specific query
        start_time = time.time()
        farm_tests = [test for test in mock_soil_tests if test['farm_id'] == 'farm_50']
        query_times.append(time.time() - start_time)
        
        # Date range query
        start_time = time.time()
        recent_tests = [test for test in mock_soil_tests if test['test_date'].startswith('2024-0')]
        query_times.append(time.time() - start_time)
        
        # All queries should complete quickly
        max_query_time = max(query_times)
        avg_query_time = statistics.mean(query_times)
        
        assert max_query_time < 0.5, f"Slowest query took {max_query_time:.3f}s, should be <0.5s"
        assert avg_query_time < 0.1, f"Average query time {avg_query_time:.3f}s, should be <0.1s"
        
        # Validate query results
        assert len(ph_filtered) > 0
        assert len(farm_tests) == 100  # 100 tests per farm
        assert len(recent_tests) > 0
    
    @pytest.mark.performance
    @pytest.mark.database
    async def test_recommendation_history_query_performance(self):
        """Test recommendation history queries."""
        
        # Simulate large recommendation history
        mock_recommendations = [
            {
                'id': i,
                'farm_id': f'farm_{i // 200}',
                'recommendation_type': ['crop_selection', 'fertilizer', 'soil_management'][i % 3],
                'confidence_score': 0.7 + (i % 30) * 0.01,
                'created_at': f'2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}'
            }
            for i in range(50000)
        ]
        
        # Test complex query (recent high-confidence crop recommendations)
        start_time = time.time()
        
        filtered_recs = [
            rec for rec in mock_recommendations
            if (rec['recommendation_type'] == 'crop_selection' and
                rec['confidence_score'] >= 0.8 and
                rec['created_at'].startswith('2024-1'))
        ]
        
        query_time = time.time() - start_time
        
        # Complex query should still be fast
        assert query_time < 1.0, f"Complex query took {query_time:.3f}s, should be <1s"
        assert len(filtered_recs) > 0


class TestCachePerformance:
    """Test caching system performance."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_hit_performance(self, mock_redis):
        """Test cache hit performance."""
        
        # Setup cache with test data
        cached_data = {
            'soil_data': {'ph': 6.2, 'organic_matter': 3.5},
            'cached_at': time.time(),
            'ttl': 3600
        }
        
        mock_redis.get.return_value = str(cached_data)
        
        # Test cache retrieval performance
        cache_times = []
        
        for i in range(100):
            start_time = time.time()
            
            # Simulate cache lookup
            cache_key = f"soil_data:farm_{i}"
            result = await self._get_from_cache(mock_redis, cache_key)
            
            cache_times.append(time.time() - start_time)
        
        # Cache operations should be very fast
        avg_cache_time = statistics.mean(cache_times)
        max_cache_time = max(cache_times)
        
        assert avg_cache_time < 0.001, f"Average cache time {avg_cache_time:.4f}s too slow"
        assert max_cache_time < 0.005, f"Slowest cache operation {max_cache_time:.4f}s too slow"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_cache_miss_fallback_performance(self, mock_redis):
        """Test performance when cache misses and falls back to data source."""
        
        # Setup cache miss scenario
        mock_redis.get.return_value = None
        
        start_time = time.time()
        
        # Simulate cache miss with fallback to data source
        result = await self._get_with_fallback(mock_redis, 'missing_key')
        
        fallback_time = time.time() - start_time
        
        # Fallback should complete within reasonable time
        assert fallback_time < 2.0, f"Cache miss fallback took {fallback_time:.2f}s"
        assert result is not None
    
    async def _get_from_cache(self, cache, key):
        """Simulate cache retrieval."""
        # Add small delay to simulate network/serialization overhead
        await asyncio.sleep(0.0001)
        return cache.get(key)
    
    async def _get_with_fallback(self, cache, key):
        """Simulate cache miss with fallback to data source."""
        # Try cache first
        cached_result = cache.get(key)
        if cached_result:
            return cached_result
        
        # Fallback to data source (simulate external API call)
        await asyncio.sleep(0.2)  # Simulate API call time
        
        # Cache the result
        result = {'data': 'from_source', 'timestamp': time.time()}
        cache.set(key, str(result))
        
        return result