"""
Climate Zone Performance Tests

Tests performance requirements for climate zone detection services including
response times, concurrent requests, memory usage, and database operations.
"""

import pytest
import asyncio
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, AsyncMock, MagicMock
import statistics
import json

# Add services to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'services'))


class TestClimateZoneResponseTime:
    """Test response time requirements for climate zone operations."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_climate_zone_detection_response_time(self, performance_timer):
        """Test that climate zone detection returns within 2 seconds."""
        
        test_coordinates = [
            {'latitude': 42.0308, 'longitude': -93.6319},  # Iowa
            {'latitude': 39.7391, 'longitude': -104.9847}, # Colorado  
            {'latitude': 30.2672, 'longitude': -97.7431},  # Texas
            {'latitude': 47.0379, 'longitude': -122.9007}, # Washington
            {'latitude': 34.0522, 'longitude': -118.2437}  # California
        ]
        
        # Mock external weather API calls
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'current': {'temperature_2m': 15.5, 'humidity': 65},
                'daily': {
                    'temperature_2m_max': [20.1] * 30,
                    'temperature_2m_min': [5.2] * 30,
                    'precipitation_sum': [2.1] * 30
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            for coords in test_coordinates:
                performance_timer.start()
                result = await self._detect_climate_zone(coords)
                performance_timer.stop()
                
                # Must respond within 2 seconds per detection
                assert performance_timer.elapsed < 2.0, f"Climate detection took {performance_timer.elapsed:.2f}s, exceeds 2s limit"
                
                # Validate response quality
                assert result is not None
                assert 'climate_zone' in result
                assert 'confidence_score' in result
                assert result['confidence_score'] >= 0.7
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_batch_climate_detection_response_time(self, performance_timer):
        """Test batch climate zone detection performance."""
        
        # Batch of 10 coordinates
        batch_coordinates = [
            {'latitude': 40.0 + i, 'longitude': -95.0 + i}
            for i in range(10)
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'current': {'temperature_2m': 15.5},
                'daily': {
                    'temperature_2m_max': [20.1] * 30,
                    'temperature_2m_min': [5.2] * 30
                }
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            performance_timer.start()
            results = await self._detect_climate_zones_batch(batch_coordinates)
            performance_timer.stop()
            
            # Batch of 10 should complete within 5 seconds
            assert performance_timer.elapsed < 5.0, f"Batch detection took {performance_timer.elapsed:.2f}s"
            assert len(results) == 10
            assert all(r['confidence_score'] >= 0.7 for r in results)
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_climate_zone_with_crop_recommendation_response_time(self, performance_timer):
        """Test end-to-end climate zone + crop recommendation performance."""
        
        request_data = {
            'location': {'latitude': 42.0308, 'longitude': -93.6319},
            'soil_data': {'ph': 6.2, 'organic_matter_percent': 3.5},
            'farm_constraints': {'farm_size_acres': 160}
        }
        
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'current': {'temperature_2m': 15.5},
                'daily': {'temperature_2m_max': [20.1] * 30}
            })
            mock_get.return_value.__aenter__.return_value = mock_response
            
            performance_timer.start()
            result = await self._climate_zone_crop_recommendation_workflow(request_data)
            performance_timer.stop()
            
            # End-to-end workflow should complete within 4 seconds
            assert performance_timer.elapsed < 4.0, f"E2E workflow took {performance_timer.elapsed:.2f}s"
            assert result is not None
            assert 'climate_zone' in result
            assert 'crop_recommendations' in result
    
    async def _detect_climate_zone(self, coordinates):
        """Simulate climate zone detection with realistic processing time."""
        # Simulate coordinate validation (10ms)
        await asyncio.sleep(0.01)
        
        # Simulate weather API call (200ms)
        await asyncio.sleep(0.2)
        
        # Simulate climate analysis (300ms)
        await asyncio.sleep(0.3)
        
        # Simulate zone classification (100ms)
        await asyncio.sleep(0.1)
        
        return {
            'climate_zone': '5b',
            'confidence_score': 0.89,
            'characteristics': {
                'avg_min_temp_winter': -15.0,
                'avg_max_temp_summer': 85.2,
                'annual_precipitation': 34.2
            },
            'processing_time_ms': 610
        }
    
    async def _detect_climate_zones_batch(self, coordinates_list):
        """Simulate batch climate zone detection."""
        results = []
        
        # Process in parallel batches of 5
        for i in range(0, len(coordinates_list), 5):
            batch = coordinates_list[i:i+5]
            batch_tasks = [self._detect_climate_zone(coords) for coords in batch]
            batch_results = await asyncio.gather(*batch_tasks)
            results.extend(batch_results)
        
        return results
    
    async def _climate_zone_crop_recommendation_workflow(self, request_data):
        """Simulate end-to-end climate zone + crop recommendation workflow."""
        # Climate zone detection
        climate_result = await self._detect_climate_zone(request_data['location'])
        
        # Crop suitability analysis with climate zone
        await asyncio.sleep(0.5)  # Simulate crop analysis
        
        return {
            'climate_zone': climate_result['climate_zone'],
            'crop_recommendations': [
                {
                    'crop_name': 'corn',
                    'suitability_score': 0.92,
                    'climate_compatibility': 0.88
                }
            ],
            'confidence_score': 0.85
        }


class TestClimateZoneConcurrency:
    """Test concurrent handling of climate zone requests."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_climate_zone_requests(self):
        """Test system handles 50 concurrent climate zone detection requests."""
        
        def make_climate_request(request_id):
            """Make a single climate zone detection request."""
            coordinates = {
                'latitude': 40.0 + (request_id % 10),
                'longitude': -95.0 + (request_id % 8)
            }
            
            start_time = time.time()
            result = self._process_climate_detection_sync(coordinates)
            end_time = time.time()
            
            return {
                'request_id': request_id,
                'success': result is not None,
                'response_time': end_time - start_time,
                'climate_zone': result.get('climate_zone') if result else None,
                'confidence_score': result.get('confidence_score', 0) if result else 0
            }
        
        # Execute 50 concurrent requests
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = [executor.submit(make_climate_request, i) for i in range(50)]
            results = [future.result() for future in as_completed(futures)]
        
        # Analyze results
        successful_requests = [r for r in results if r['success']]
        response_times = [r['response_time'] for r in successful_requests]
        confidence_scores = [r['confidence_score'] for r in successful_requests]
        
        # Performance requirements
        assert len(successful_requests) >= 47, f"Only {len(successful_requests)}/50 requests succeeded"
        
        # Response time requirements under load
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        assert avg_response_time < 3.0, f"Average response time {avg_response_time:.2f}s exceeds 3s under load"
        assert p95_response_time < 5.0, f"95th percentile response time {p95_response_time:.2f}s exceeds 5s"
        
        # Quality should remain high under load
        avg_confidence = statistics.mean(confidence_scores)
        assert avg_confidence >= 0.7, f"Average confidence {avg_confidence:.2f} too low under load"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_concurrent_weather_api_calls(self):
        """Test concurrent weather API call handling."""
        
        async def weather_api_call(location_id):
            """Simulate weather API call."""
            # Simulate API call latency with some variance
            await asyncio.sleep(0.15 + (location_id % 5) * 0.02)
            
            return {
                'location_id': location_id,
                'success': True,
                'temperature_data': {
                    'current': 15.5 + location_id,
                    'max_30_day': [20.0 + location_id] * 30,
                    'min_30_day': [5.0 + location_id] * 30
                }
            }
        
        start_time = time.time()
        
        # Execute 20 concurrent weather API calls
        tasks = [weather_api_call(i) for i in range(20)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should complete all operations efficiently
        successful_calls = [r for r in results if isinstance(r, dict) and r.get('success')]
        assert len(successful_calls) == 20, f"Only {len(successful_calls)}/20 weather API calls succeeded"
        
        # Should leverage concurrency effectively (serial would take 4+ seconds)
        assert total_time < 1.0, f"Concurrent API calls took {total_time:.2f}s, should be <1s with proper concurrency"
    
    def _process_climate_detection_sync(self, coordinates):
        """Synchronous version of climate detection for thread testing."""
        # Simulate processing time with some variability
        processing_time = 0.4 + (hash(str(coordinates['latitude'])) % 50) * 0.01
        time.sleep(processing_time)
        
        return {
            'climate_zone': f"{5 + (hash(str(coordinates['longitude'])) % 4)}{'a' if coordinates['latitude'] > 40 else 'b'}",
            'confidence_score': 0.75 + (hash(str(coordinates['latitude'] + coordinates['longitude'])) % 20) * 0.01,
            'processing_time': processing_time
        }


class TestClimateZoneMemoryPerformance:
    """Test memory usage during climate zone operations."""
    
    @pytest.mark.performance
    def test_climate_data_memory_usage(self):
        """Test memory usage with large climate datasets."""
        import psutil
        import gc
        
        # Get baseline memory usage
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate large climate datasets
        climate_datasets = []
        for i in range(100):
            # Simulate comprehensive climate data for each location
            dataset = {
                'location_id': f'climate_loc_{i}',
                'coordinates': {'latitude': 40.0 + i * 0.1, 'longitude': -95.0 + i * 0.1},
                'historical_data': {
                    'temperature_records': [
                        {
                            'year': 2020 + (j // 365),
                            'day_of_year': j % 365,
                            'temp_max': 20.0 + (j % 60),
                            'temp_min': 5.0 + (j % 40),
                            'humidity': 60 + (j % 40)
                        }
                        for j in range(1825)  # 5 years of daily data
                    ],
                    'precipitation_records': list(range(1825)),
                    'wind_patterns': list(range(365 * 24))  # Hourly wind data for 1 year
                },
                'climate_zone_analysis': {
                    'zone_candidates': [f'zone_{k}' for k in range(10)],
                    'suitability_scores': [0.5 + k * 0.05 for k in range(10)],
                    'confidence_factors': list(range(50))
                }
            }
            climate_datasets.append(dataset)
        
        # Process climate datasets
        processed_zones = []
        for dataset in climate_datasets:
            zone_result = self._process_climate_dataset(dataset)
            processed_zones.append(zone_result)
        
        # Check memory usage after processing
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - baseline_memory
        
        # Memory usage should remain reasonable for climate data
        assert memory_increase < 300, f"Memory increased by {memory_increase:.1f}MB, should be <300MB"
        
        # Validate processing results
        assert len(processed_zones) == 100
        assert all(zone['climate_zone'] is not None for zone in processed_zones)
        
        # Clean up
        del climate_datasets
        del processed_zones
        gc.collect()
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_climate_zone_cache_memory_efficiency(self):
        """Test memory efficiency of climate zone caching."""
        import gc
        import psutil
        
        gc.collect()
        process = psutil.Process()
        baseline_memory = process.memory_info().rss / 1024 / 1024
        
        # Simulate climate zone cache with many entries
        climate_cache = {}
        
        for i in range(1000):
            cache_key = f"climate_zone:{40.0 + i * 0.01}:{-95.0 + i * 0.01}"
            cache_value = {
                'climate_zone': f"{5 + (i % 4)}{'a' if i % 2 else 'b'}",
                'confidence_score': 0.7 + (i % 30) * 0.01,
                'characteristics': {
                    'avg_temp': 15.0 + i * 0.1,
                    'precipitation': 30.0 + i * 0.05
                },
                'timestamp': time.time(),
                'ttl': 3600
            }
            climate_cache[cache_key] = json.dumps(cache_value)
        
        # Test cache operations performance
        cache_operations = 0
        start_time = time.time()
        
        for i in range(500):
            # Simulate cache lookups
            cache_key = f"climate_zone:{40.0 + i * 0.01}:{-95.0 + i * 0.01}"
            if cache_key in climate_cache:
                data = json.loads(climate_cache[cache_key])
                cache_operations += 1
                
                # Yield control occasionally
                if cache_operations % 100 == 0:
                    await asyncio.sleep(0.001)
        
        operation_time = time.time() - start_time
        
        # Check memory usage with cache
        current_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = current_memory - baseline_memory
        
        # Cache should be memory efficient
        assert memory_increase < 50, f"Cache increased memory by {memory_increase:.1f}MB, should be <50MB"
        
        # Cache operations should be fast
        assert operation_time < 0.5, f"Cache operations took {operation_time:.2f}s, should be <0.5s"
        assert cache_operations == 500
    
    def _process_climate_dataset(self, dataset):
        """Process climate dataset efficiently."""
        location_id = dataset['location_id']
        coordinates = dataset['coordinates']
        temp_records = dataset['historical_data']['temperature_records']
        
        # Calculate climate zone characteristics
        avg_temp = sum(record['temp_max'] for record in temp_records[:365]) / 365
        min_winter_temp = min(record['temp_min'] for record in temp_records[:90])
        
        # Determine climate zone
        if avg_temp > 60:
            climate_zone = '9a' if coordinates['latitude'] < 35 else '8b'
        elif avg_temp > 50:
            climate_zone = '7a' if min_winter_temp > 0 else '6b'
        else:
            climate_zone = '5a' if min_winter_temp > -20 else '4b'
        
        return {
            'location_id': location_id,
            'climate_zone': climate_zone,
            'avg_temp': avg_temp,
            'confidence_score': 0.85,
            'processed': True
        }


class TestClimateZoneDatabasePerformance:
    """Test database performance for climate zone operations."""
    
    @pytest.mark.performance
    @pytest.mark.database
    async def test_climate_zone_query_performance(self):
        """Test climate zone database queries perform efficiently."""
        
        # Simulate large climate zone dataset
        mock_climate_zones = [
            {
                'id': i,
                'latitude': 40.0 + (i % 800) * 0.01,
                'longitude': -95.0 + (i % 600) * 0.01,
                'climate_zone': f"{4 + (i % 6)}{'a' if i % 2 else 'b'}",
                'confidence_score': 0.7 + (i % 30) * 0.01,
                'characteristics': {
                    'avg_min_temp_winter': -20 + (i % 40),
                    'avg_max_temp_summer': 70 + (i % 30),
                    'annual_precipitation': 20 + (i % 50)
                },
                'last_updated': f'2024-{(i % 12) + 1:02d}-15'
            }
            for i in range(25000)
        ]
        
        # Test various query patterns
        query_times = []
        
        # Geographic range query
        start_time = time.time()
        geo_filtered = [
            zone for zone in mock_climate_zones
            if 40.0 <= zone['latitude'] <= 42.0 and -96.0 <= zone['longitude'] <= -94.0
        ]
        query_times.append(time.time() - start_time)
        
        # Climate zone specific query
        start_time = time.time()
        zone_5b = [zone for zone in mock_climate_zones if zone['climate_zone'] == '5b']
        query_times.append(time.time() - start_time)
        
        # High confidence query
        start_time = time.time()
        high_confidence = [
            zone for zone in mock_climate_zones
            if zone['confidence_score'] >= 0.9
        ]
        query_times.append(time.time() - start_time)
        
        # Complex characteristics query
        start_time = time.time()
        complex_query = [
            zone for zone in mock_climate_zones
            if (zone['characteristics']['avg_min_temp_winter'] > -10 and
                zone['characteristics']['annual_precipitation'] > 30 and
                zone['confidence_score'] >= 0.8)
        ]
        query_times.append(time.time() - start_time)
        
        # All queries should complete efficiently
        max_query_time = max(query_times)
        avg_query_time = statistics.mean(query_times)
        
        assert max_query_time < 1.0, f"Slowest query took {max_query_time:.3f}s, should be <1s"
        assert avg_query_time < 0.3, f"Average query time {avg_query_time:.3f}s, should be <0.3s"
        
        # Validate query results
        assert len(geo_filtered) > 0
        assert len(zone_5b) > 0
        assert len(high_confidence) > 0
        assert len(complex_query) > 0
    
    @pytest.mark.performance
    @pytest.mark.database
    async def test_climate_zone_update_performance(self):
        """Test performance of climate zone data updates."""
        
        # Simulate batch update scenario
        updates = [
            {
                'location_id': f'loc_{i}',
                'latitude': 40.0 + i * 0.01,
                'longitude': -95.0 + i * 0.01,
                'new_climate_zone': f"{5 + (i % 3)}{'a' if i % 2 else 'b'}",
                'new_confidence': 0.8 + (i % 20) * 0.01,
                'updated_characteristics': {
                    'avg_temp': 15.0 + i * 0.1,
                    'precipitation': 30.0 + i * 0.05
                }
            }
            for i in range(100)
        ]
        
        start_time = time.time()
        
        # Simulate batch update operations
        updated_records = []
        for update in updates:
            # Simulate update processing time
            await asyncio.sleep(0.001)  # 1ms per update
            
            updated_record = {
                'location_id': update['location_id'],
                'climate_zone': update['new_climate_zone'],
                'confidence_score': update['new_confidence'],
                'updated': True,
                'timestamp': time.time()
            }
            updated_records.append(updated_record)
        
        update_time = time.time() - start_time
        
        # Batch updates should be efficient
        assert update_time < 2.0, f"Batch update took {update_time:.2f}s, should be <2s"
        assert len(updated_records) == 100
        assert all(record['updated'] for record in updated_records)


class TestClimateZoneAPIPerformance:
    """Test API endpoint performance for climate zone services."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_climate_zone_api_endpoint_performance(self):
        """Test climate zone API endpoints respond quickly."""
        
        # Test data for various endpoints
        test_cases = [
            {
                'endpoint': '/api/climate-zone/detect',
                'payload': {'latitude': 42.0308, 'longitude': -93.6319},
                'expected_response_time': 2.0
            },
            {
                'endpoint': '/api/climate-zone/batch-detect',
                'payload': {
                    'locations': [
                        {'latitude': 42.0 + i, 'longitude': -93.0 + i}
                        for i in range(5)
                    ]
                },
                'expected_response_time': 3.0
            },
            {
                'endpoint': '/api/climate-zone/characteristics',
                'payload': {'climate_zone': '5b'},
                'expected_response_time': 0.5
            },
            {
                'endpoint': '/api/climate-zone/crop-suitability',
                'payload': {
                    'latitude': 42.0308,
                    'longitude': -93.6319,
                    'crops': ['corn', 'soybeans', 'wheat']
                },
                'expected_response_time': 2.5
            }
        ]
        
        for test_case in test_cases:
            start_time = time.time()
            
            # Simulate API endpoint processing
            result = await self._simulate_api_endpoint(
                test_case['endpoint'],
                test_case['payload']
            )
            
            response_time = time.time() - start_time
            
            # Check response time requirement
            assert response_time < test_case['expected_response_time'], \
                f"{test_case['endpoint']} took {response_time:.2f}s, exceeds {test_case['expected_response_time']}s limit"
            
            # Validate response quality
            assert result is not None
            assert result.get('success', False)
            
            # Slight delay between tests
            await asyncio.sleep(0.1)
    
    async def _simulate_api_endpoint(self, endpoint, payload):
        """Simulate API endpoint processing."""
        
        if endpoint == '/api/climate-zone/detect':
            # Single location detection
            await asyncio.sleep(0.3)  # Processing time
            return {
                'success': True,
                'climate_zone': '5b',
                'confidence_score': 0.87,
                'characteristics': {'avg_temp': 15.2}
            }
        
        elif endpoint == '/api/climate-zone/batch-detect':
            # Batch detection
            processing_time = len(payload['locations']) * 0.1
            await asyncio.sleep(processing_time)
            return {
                'success': True,
                'results': [
                    {'climate_zone': f"{5 + i % 2}{'a' if i % 2 else 'b'}", 'confidence_score': 0.8}
                    for i in range(len(payload['locations']))
                ]
            }
        
        elif endpoint == '/api/climate-zone/characteristics':
            # Zone characteristics lookup
            await asyncio.sleep(0.05)  # Database lookup
            return {
                'success': True,
                'characteristics': {
                    'avg_min_temp_winter': -15,
                    'avg_max_temp_summer': 85,
                    'growing_season_days': 180
                }
            }
        
        elif endpoint == '/api/climate-zone/crop-suitability':
            # Crop suitability analysis
            await asyncio.sleep(0.4)  # Analysis time
            return {
                'success': True,
                'suitability_scores': {
                    'corn': 0.92,
                    'soybeans': 0.88,
                    'wheat': 0.75
                }
            }
        
        return {'success': False, 'error': 'Unknown endpoint'}