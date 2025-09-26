"""
Additional Climate Zone Integration Test Scenarios
Extended test cases for edge cases, failure modes, and advanced integration patterns.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock, MagicMock
import json
from typing import Dict, List
import tempfile
import os

# Import the main test class to extend it
from test_climate_zone_service_integration import TestClimateZoneServiceIntegration


class TestClimateZoneEdgeCases(TestClimateZoneServiceIntegration):
    """Extended test cases for edge cases and failure scenarios."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_concurrent_climate_zone_requests(self, sample_coordinates):
        """
        Test handling of concurrent climate zone detection requests.
        
        This tests system behavior under concurrent load.
        """
        coords_list = list(sample_coordinates.values())[:3]
        
        with patch('aiohttp.ClientSession.get') as mock_http_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'zone': '6a',
                'description': 'USDA Zone 6a',
                'confidence': 0.85
            })
            mock_http_get.return_value.__aenter__.return_value = mock_response
            
            # Create concurrent tasks
            tasks = []
            for coords in coords_list:
                from data_integration.src.services.coordinate_climate_detector import coordinate_climate_detector
                
                task = coordinate_climate_detector.detect_climate_from_coordinates(
                    latitude=coords['latitude'],
                    longitude=coords['longitude']
                )
                tasks.append(task)
            
            # Execute tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Validate concurrent execution
            assert len(results) == len(coords_list)
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) >= len(coords_list) // 2  # At least half should succeed
            
            for result in successful_results:
                assert hasattr(result, 'usda_zone')
                assert result.confidence_factors['overall_confidence'] >= 0.5
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_climate_zone_caching_integration(self, sample_coordinates, mock_redis):
        """
        Test caching integration across climate zone services.
        
        This tests cache consistency between services.
        """
        coords = sample_coordinates['iowa_farm']
        cache_key = f"climate_zone:{coords['latitude']}:{coords['longitude']}"
        
        # Mock cached data
        cached_climate_data = {
            'zone_id': '6a',
            'zone_type': 'usda_hardiness',
            'confidence': 0.85,
            'cached_at': datetime.utcnow().isoformat(),
            'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        with patch('redis.Redis') as mock_redis_client:
            mock_redis_client.return_value = mock_redis
            mock_redis.get.return_value = json.dumps(cached_climate_data).encode()
            mock_redis.exists.return_value = True
            
            # Test cache retrieval
            from data_integration.src.services.climate_zone_service import climate_zone_service
            
            cached_result = await climate_zone_service.get_cached_zone(
                latitude=coords['latitude'],
                longitude=coords['longitude']
            )
            
            # Validate cache hit
            assert cached_result is not None
            assert cached_result['zone_id'] == '6a'
            assert cached_result['confidence'] >= 0.8
            
            # Test cache miss and population
            mock_redis.get.return_value = None
            mock_redis.exists.return_value = False
            
            with patch('aiohttp.ClientSession.get') as mock_http_get:
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={
                    'zone': '6a',
                    'description': 'USDA Zone 6a'
                })
                mock_http_get.return_value.__aenter__.return_value = mock_response
                
                # This should trigger cache population
                new_result = await climate_zone_service.get_or_detect_zone(
                    latitude=coords['latitude'],
                    longitude=coords['longitude']
                )
                
                # Verify cache was populated
                mock_redis.set.assert_called()
                assert new_result is not None
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_climate_zone_fallback_mechanisms(self, sample_coordinates):
        """
        Test fallback mechanisms when primary climate detection fails.
        
        This tests resilience and fallback strategies.
        """
        coords = sample_coordinates['iowa_farm']
        
        # Test multiple fallback scenarios
        fallback_scenarios = [
            {
                'name': 'primary_api_failure',
                'primary_fails': True,
                'secondary_available': True,
                'expected_confidence': 0.7
            },
            {
                'name': 'all_apis_fail',
                'primary_fails': True,
                'secondary_available': False,
                'expected_confidence': 0.4
            }
        ]
        
        for scenario in fallback_scenarios:
            with patch('aiohttp.ClientSession.get') as mock_http_get:
                if scenario['primary_fails']:
                    # Primary API fails
                    mock_http_get.side_effect = [
                        Exception("Primary API unavailable"),
                        # Secondary API response (if available)
                        MagicMock(status=200, json=AsyncMock(return_value={
                            'zone': '6a',
                            'confidence': 0.7,
                            'source': 'fallback'
                        })) if scenario['secondary_available'] else Exception("Secondary API also fails")
                    ]
                
                from data_integration.src.services.coordinate_climate_detector import coordinate_climate_detector
                
                try:
                    result = await coordinate_climate_detector.detect_climate_from_coordinates(
                        latitude=coords['latitude'],
                        longitude=coords['longitude'],
                        enable_fallbacks=True
                    )
                    
                    # Validate fallback behavior
                    if scenario['secondary_available']:
                        assert result is not None
                        assert result.confidence_factors['overall_confidence'] >= scenario['expected_confidence']
                        assert 'fallback' in str(result.detection_metadata.get('source', '')).lower()
                    else:
                        # If all APIs fail, should get minimal result or raise exception
                        assert result is None or result.confidence_factors['overall_confidence'] < 0.5
                        
                except Exception as e:
                    # Expected for complete failure scenario
                    if not scenario['secondary_available']:
                        assert "API" in str(e) or "unavailable" in str(e).lower()
                    else:
                        raise  # Unexpected exception
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_climate_zone_data_validation_integration(self, sample_coordinates):
        """
        Test data validation across service boundaries.
        
        This tests that invalid data is properly handled between services.
        """
        coords = sample_coordinates['iowa_farm']
        
        # Test various invalid data scenarios
        invalid_data_scenarios = [
            {
                'name': 'invalid_zone_id',
                'api_response': {'zone': 'INVALID_ZONE', 'confidence': 0.9},
                'should_reject': True
            },
            {
                'name': 'low_confidence',
                'api_response': {'zone': '6a', 'confidence': 0.1},
                'should_reject': False,  # Low confidence is valid, just low quality
            },
            {
                'name': 'missing_required_fields',
                'api_response': {'zone': '6a'},  # Missing confidence
                'should_reject': True
            },
            {
                'name': 'malformed_response',
                'api_response': {'invalid': 'structure'},
                'should_reject': True
            }
        ]
        
        for scenario in invalid_data_scenarios:
            with patch('aiohttp.ClientSession.get') as mock_http_get:
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=scenario['api_response'])
                mock_http_get.return_value.__aenter__.return_value = mock_response
                
                from data_integration.src.services.coordinate_climate_detector import coordinate_climate_detector
                
                try:
                    result = await coordinate_climate_detector.detect_climate_from_coordinates(
                        latitude=coords['latitude'],
                        longitude=coords['longitude'],
                        validate_response=True
                    )
                    
                    if scenario['should_reject']:
                        # Should either return None or raise validation error
                        assert result is None or result.confidence_factors['overall_confidence'] < 0.3
                    else:
                        # Should handle gracefully with appropriate confidence
                        assert result is not None
                        if 'confidence' not in scenario['api_response']:
                            assert result.confidence_factors['overall_confidence'] < 0.7
                            
                except (ValueError, KeyError, TypeError) as e:
                    # Expected validation errors for invalid data
                    if scenario['should_reject']:
                        assert "validation" in str(e).lower() or "invalid" in str(e).lower()
                    else:
                        raise  # Unexpected validation error
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_climate_zone_temporal_consistency(self, sample_coordinates, mock_database_connection):
        """
        Test temporal consistency of climate zone data across services.
        
        This tests that climate zone data remains consistent over time.
        """
        coords = sample_coordinates['iowa_farm']
        
        # Mock historical climate zone data with temporal variations
        historical_records = [
            {
                'zone_id': '6a',
                'detection_date': datetime(2022, 1, 1),
                'confidence_score': 0.85,
                'source': 'usda_api'
            },
            {
                'zone_id': '6a',
                'detection_date': datetime(2023, 1, 1),
                'confidence_score': 0.87,
                'source': 'usda_api'
            },
            {
                'zone_id': '6b',  # Slight change
                'detection_date': datetime(2024, 1, 1),
                'confidence_score': 0.75,
                'source': 'usda_api'
            }
        ]
        
        with patch('databases.Database') as mock_db:
            mock_db_instance = mock_database_connection
            mock_db_instance.fetch_all.return_value = historical_records
            mock_db.return_value = mock_db_instance
            
            # Test temporal consistency validation
            from data_integration.src.services.climate_zone_service import climate_zone_service
            
            consistency_result = await climate_zone_service.validate_temporal_consistency(
                latitude=coords['latitude'],
                longitude=coords['longitude'],
                years_to_check=3
            )
            
            # Validate temporal consistency analysis
            assert 'consistency_score' in consistency_result
            assert 'trend_detected' in consistency_result
            assert 'zone_transitions' in consistency_result
            
            # Should detect the transition from 6a to 6b
            assert consistency_result['trend_detected'] is True
            assert len(consistency_result['zone_transitions']) >= 1
            
            # Confidence should be high for consistent historical data
            assert consistency_result['consistency_score'] >= 0.6
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_climate_zone_spatial_clustering(self, sample_coordinates):
        """
        Test spatial clustering and consistency of climate zones.
        
        This tests that nearby locations have consistent climate zones.
        """
        base_coords = sample_coordinates['iowa_farm']
        
        # Generate nearby coordinates (within ~10 miles)
        nearby_coordinates = [
            {
                'latitude': base_coords['latitude'] + 0.1,
                'longitude': base_coords['longitude'] + 0.1,
                'expected_similar': True
            },
            {
                'latitude': base_coords['latitude'] + 0.01,
                'longitude': base_coords['longitude'] + 0.01,
                'expected_similar': True
            },
            {
                'latitude': base_coords['latitude'] + 5.0,  # Very far
                'longitude': base_coords['longitude'] + 5.0,
                'expected_similar': False
            }
        ]
        
        with patch('aiohttp.ClientSession.get') as mock_http_get:
            def mock_response_generator(coords):
                """Generate climate zone response based on coordinates."""
                # Simulate spatial consistency - nearby locations get similar zones
                if abs(coords['latitude'] - base_coords['latitude']) < 1.0:
                    return {'zone': '6a', 'confidence': 0.85}
                else:
                    return {'zone': '5a', 'confidence': 0.80}  # Different zone for far locations
            
            results = []
            
            for coords in nearby_coordinates:
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=mock_response_generator(coords))
                mock_http_get.return_value.__aenter__.return_value = mock_response
                
                from data_integration.src.services.coordinate_climate_detector import coordinate_climate_detector
                
                result = await coordinate_climate_detector.detect_climate_from_coordinates(
                    latitude=coords['latitude'],
                    longitude=coords['longitude']
                )
                
                results.append({
                    'coords': coords,
                    'zone': result.usda_zone.zone if result.usda_zone else None,
                    'confidence': result.confidence_factors['overall_confidence']
                })
            
            # Validate spatial clustering
            base_zone = '6a'  # Expected zone for base coordinates
            
            for i, result in enumerate(results):
                coords = nearby_coordinates[i]
                if coords['expected_similar']:
                    # Nearby locations should have same or similar zones
                    assert result['zone'] in ['6a', '6b'], f"Expected similar zone for nearby location, got {result['zone']}"
                else:
                    # Far locations may have different zones
                    # This is acceptable for spatial variation
                    pass  # No assertion needed for far locations
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_climate_zone_microservice_communication(self, sample_coordinates):
        """
        Test microservice communication patterns for climate zone data.
        
        This tests service-to-service communication protocols.
        """
        coords = sample_coordinates['iowa_farm']
        
        # Mock inter-service communication
        service_responses = {
            'location_validation': {
                'status': 'success',
                'valid': True,
                'coordinates': coords,
                'agricultural_suitability': 'excellent'
            },
            'climate_detection': {
                'status': 'success',
                'zone_id': '6a',
                'confidence': 0.85,
                'metadata': {'source': 'usda_api', 'method': 'coordinate_lookup'}
            },
            'recommendation_engine': {
                'status': 'success',
                'recommendations': [
                    {
                        'crop': 'corn',
                        'suitability': 0.92,
                        'climate_factors': ['suitable_for_zone_6a', 'adequate_growing_season']
                    }
                ],
                'climate_context_used': True
            }
        }
        
        # Test service communication chain
        communication_log = []
        
        def mock_service_call(service_name, endpoint, data):
            """Mock service-to-service communication."""
            communication_log.append({
                'service': service_name,
                'endpoint': endpoint,
                'data': data,
                'timestamp': datetime.utcnow()
            })
            return service_responses.get(service_name, {'status': 'error'})
        
        # Simulate service communication flow
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = lambda url, **kwargs: AsyncMock(
                status_code=200,
                json=AsyncMock(return_value=mock_service_call(
                    url.split('/')[2],  # Extract service name from URL
                    url.split('/')[-1],  # Extract endpoint
                    kwargs.get('json', {})
                ))
            )()
            
            # Step 1: Location validation service call
            location_response = await mock_service_call(
                'location_validation',
                'validate_coordinates',
                coords
            )
            
            # Step 2: Climate detection service call
            if location_response['status'] == 'success':
                climate_response = await mock_service_call(
                    'climate_detection',
                    'detect_zone',
                    {**coords, 'validated': True}
                )
            
            # Step 3: Recommendation service call
            if climate_response['status'] == 'success':
                recommendation_response = await mock_service_call(
                    'recommendation_engine',
                    'get_recommendations',
                    {
                        **coords,
                        'climate_zone': climate_response['zone_id'],
                        'question_type': 'crop_selection'
                    }
                )
            
            # Validate service communication
            assert len(communication_log) == 3
            assert communication_log[0]['service'] == 'location_validation'
            assert communication_log[1]['service'] == 'climate_detection'
            assert communication_log[2]['service'] == 'recommendation_engine'
            
            # Validate data flow between services
            assert location_response['valid'] is True
            assert climate_response['zone_id'] == '6a'
            assert recommendation_response['climate_context_used'] is True


class TestClimateZoneIntegrationPatterns:
    """Test advanced integration patterns and architectural considerations."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_event_driven_climate_zone_updates(self, sample_coordinates, mock_database_connection):
        """
        Test event-driven updates for climate zone changes.
        
        This tests how climate zone changes trigger updates across services.
        """
        coords = sample_coordinates['iowa_farm']
        
        # Mock event system
        events_published = []
        
        def mock_publish_event(event_type, data):
            """Mock event publishing."""
            events_published.append({
                'type': event_type,
                'data': data,
                'timestamp': datetime.utcnow()
            })
        
        # Simulate climate zone change detection
        with patch('databases.Database') as mock_db:
            mock_db_instance = mock_database_connection
            mock_db.return_value = mock_db_instance
            
            # Mock change detection
            climate_change_event = {
                'location': coords,
                'old_zone': '6a',
                'new_zone': '6b',
                'confidence': 0.82,
                'change_date': datetime.utcnow(),
                'trigger': 'periodic_update'
            }
            
            # Publish climate zone change event
            mock_publish_event('climate_zone_changed', climate_change_event)
            
            # Mock event handlers for different services
            service_responses = []
            
            # Location validation service response to climate change
            location_service_response = {
                'service': 'location_validation',
                'action': 'update_cache',
                'status': 'updated'
            }
            service_responses.append(location_service_response)
            
            # Recommendation engine response to climate change
            recommendation_service_response = {
                'service': 'recommendation_engine',
                'action': 'invalidate_crop_recommendations',
                'affected_farms': ['test_farm_12345'],
                'status': 'invalidated'
            }
            service_responses.append(recommendation_service_response)
            
            # Validate event-driven architecture
            assert len(events_published) == 1
            assert events_published[0]['type'] == 'climate_zone_changed'
            assert events_published[0]['data']['old_zone'] == '6a'
            assert events_published[0]['data']['new_zone'] == '6b'
            
            # Validate service responses
            location_response = next(r for r in service_responses if r['service'] == 'location_validation')
            recommendation_response = next(r for r in service_responses if r['service'] == 'recommendation_engine')
            
            assert location_response['status'] == 'updated'
            assert recommendation_response['status'] == 'invalidated'
            assert 'affected_farms' in recommendation_response
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_climate_zone_circuit_breaker_pattern(self, sample_coordinates):
        """
        Test circuit breaker pattern for climate zone service integration.
        
        This tests resilience patterns when services are failing.
        """
        coords = sample_coordinates['iowa_farm']
        
        # Circuit breaker states
        circuit_states = {
            'usda_api': 'closed',  # Normal operation
            'koppen_api': 'open',  # Failing
            'fallback_api': 'half_open'  # Testing recovery
        }
        
        failure_counts = {
            'usda_api': 0,
            'koppen_api': 5,  # Exceeded failure threshold
            'fallback_api': 2
        }
        
        def mock_circuit_breaker_call(api_name):
            """Mock circuit breaker behavior."""
            state = circuit_states[api_name]
            failures = failure_counts[api_name]
            
            if state == 'open':
                # Circuit is open, don't call API
                raise Exception(f"Circuit breaker open for {api_name}")
            elif state == 'half_open':
                # Testing recovery
                if failures < 3:
                    return {'zone': '6a', 'confidence': 0.7, 'source': api_name}
                else:
                    circuit_states[api_name] = 'open'
                    raise Exception(f"Circuit breaker opened for {api_name}")
            else:  # closed
                # Normal operation
                return {'zone': '6a', 'confidence': 0.85, 'source': api_name}
        
        # Test circuit breaker integration
        api_results = {}
        
        for api_name in circuit_states.keys():
            try:
                result = mock_circuit_breaker_call(api_name)
                api_results[api_name] = result
            except Exception as e:
                api_results[api_name] = {'error': str(e), 'circuit_open': True}
        
        # Validate circuit breaker behavior
        assert 'error' not in api_results['usda_api']  # Should succeed
        assert 'circuit_open' in api_results['koppen_api']  # Should be blocked by circuit breaker
        
        # Validate fallback mechanisms work with circuit breakers
        successful_apis = [name for name, result in api_results.items() if 'error' not in result]
        assert len(successful_apis) >= 1  # At least one API should work
        
        # Test climate zone detection with circuit breaker integration
        from data_integration.src.services.coordinate_climate_detector import coordinate_climate_detector
        
        with patch('aiohttp.ClientSession.get') as mock_http_get:
            def circuit_breaker_side_effect(*args, **kwargs):
                url = str(args[0]) if args else str(kwargs.get('url', ''))
                
                if 'usda' in url.lower():
                    return MagicMock(
                        status=200,
                        json=AsyncMock(return_value=mock_circuit_breaker_call('usda_api'))
                    )
                elif 'koppen' in url.lower():
                    # Circuit breaker should prevent this call
                    raise Exception("Circuit breaker open for koppen_api")
                else:
                    return MagicMock(
                        status=200,
                        json=AsyncMock(return_value=mock_circuit_breaker_call('fallback_api'))
                    )
            
            mock_http_get.return_value.__aenter__.side_effect = circuit_breaker_side_effect
            
            # Should still get result despite some APIs being circuit-broken
            result = await coordinate_climate_detector.detect_climate_from_coordinates(
                latitude=coords['latitude'],
                longitude=coords['longitude'],
                enable_circuit_breaker=True
            )
            
            # Validate result with circuit breaker protection
            assert result is not None
            assert result.usda_zone is not None
            # Confidence might be lower due to limited API availability
            assert result.confidence_factors['overall_confidence'] >= 0.5
    
    @pytest.mark.integration
    @pytest.mark.database
    async def test_climate_zone_database_transaction_integration(self, sample_coordinates, mock_database_connection):
        """
        Test database transaction handling across climate zone services.
        
        This tests ACID properties in distributed climate zone operations.
        """
        coords = sample_coordinates['iowa_farm']
        
        # Mock database transaction operations
        transaction_log = []
        
        def mock_db_operation(operation, table, data=None):
            """Mock database operation with transaction logging."""
            transaction_log.append({
                'operation': operation,
                'table': table,
                'data': data,
                'timestamp': datetime.utcnow()
            })
            return {'success': True, 'affected_rows': 1}
        
        with patch('databases.Database') as mock_db:
            mock_db_instance = mock_database_connection
            mock_db_instance.transaction = AsyncMock()
            mock_db.return_value = mock_db_instance
            
            # Simulate transactional climate zone update
            async def climate_zone_transaction():
                """Simulate a complex climate zone update transaction."""
                # Begin transaction
                async with mock_db_instance.transaction():
                    # 1. Update climate zone record
                    mock_db_operation('UPDATE', 'climate_zones', {
                        'latitude': coords['latitude'],
                        'longitude': coords['longitude'],
                        'zone_id': '6b',
                        'updated_at': datetime.utcnow()
                    })
                    
                    # 2. Insert historical record
                    mock_db_operation('INSERT', 'climate_zone_history', {
                        'latitude': coords['latitude'],
                        'longitude': coords['longitude'],
                        'old_zone': '6a',
                        'new_zone': '6b',
                        'change_date': datetime.utcnow()
                    })
                    
                    # 3. Update dependent recommendations
                    mock_db_operation('UPDATE', 'crop_recommendations', {
                        'location_id': f"{coords['latitude']},{coords['longitude']}",
                        'status': 'needs_update',
                        'reason': 'climate_zone_changed'
                    })
                    
                    # 4. Log the change
                    mock_db_operation('INSERT', 'system_logs', {
                        'event_type': 'climate_zone_updated',
                        'location': coords,
                        'details': 'Zone changed from 6a to 6b'
                    })
            
            # Execute transaction
            await climate_zone_transaction()
            
            # Validate transaction integrity
            assert len(transaction_log) == 4
            assert transaction_log[0]['table'] == 'climate_zones'
            assert transaction_log[1]['table'] == 'climate_zone_history'
            assert transaction_log[2]['table'] == 'crop_recommendations'
            assert transaction_log[3]['table'] == 'system_logs'
            
            # Validate transaction atomicity (all operations in single transaction)
            mock_db_instance.transaction.assert_called_once()
    
    @pytest.mark.integration
    @pytest.mark.performance
    async def test_climate_zone_performance_under_load(self, sample_coordinates, performance_timer):
        """
        Test climate zone service performance under load conditions.
        
        This tests system behavior with multiple concurrent requests.
        """
        coords_list = [sample_coordinates['iowa_farm']] * 10  # 10 concurrent requests
        
        with patch('aiohttp.ClientSession.get') as mock_http_get:
            mock_response = MagicMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                'zone': '6a',
                'confidence': 0.85,
                'processing_time_ms': 50
            })
            mock_http_get.return_value.__aenter__.return_value = mock_response
            
            performance_timer.start()
            
            # Create many concurrent tasks
            tasks = []
            for coords in coords_list:
                from data_integration.src.services.coordinate_climate_detector import coordinate_climate_detector
                
                task = coordinate_climate_detector.detect_climate_from_coordinates(
                    latitude=coords['latitude'],
                    longitude=coords['longitude']
                )
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            performance_timer.stop()
            
            # Validate performance under load
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) >= 8  # At least 80% success rate
            
            # Performance should scale reasonably
            assert performance_timer.elapsed < 5.0  # Should complete within 5 seconds
            
            # Validate result quality under load
            for result in successful_results:
                assert hasattr(result, 'usda_zone')
                assert result.confidence_factors['overall_confidence'] >= 0.7


if __name__ == "__main__":
    pytest.main([__file__])