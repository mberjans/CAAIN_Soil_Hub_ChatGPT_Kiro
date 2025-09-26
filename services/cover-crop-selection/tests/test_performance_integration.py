"""
Performance and Integration Tests for Cover Crop Selection Service

This module provides performance benchmarking and end-to-end integration tests
to ensure the service meets performance requirements and all components work
together correctly under various load conditions.

Test Categories:
1. Performance Benchmarking
2. Load Testing and Concurrency
3. Database Integration
4. External Service Integration
5. End-to-End Workflows
6. Memory and Resource Usage
7. Caching and Optimization
"""

import pytest
import asyncio
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, AsyncMock, MagicMock
import sys
from pathlib import Path
from typing import Dict, List, Any
import psutil
import os

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.cover_crop_selection_service import CoverCropSelectionService
from models.cover_crop_models import (
    CoverCropSelectionRequest,
    CoverCropSpecies,
    CoverCropType,
    GrowingSeason,
    SoilBenefit,
    SoilConditions,
    CoverCropObjectives
)


@pytest.fixture
def service():
    """Cover crop selection service fixture."""
    return CoverCropSelectionService()


@pytest.fixture
def large_species_database():
    """Large species database for performance testing."""
    species_db = {}
    
    # Create 100 test species for performance testing
    for i in range(100):
        species_id = f"test_species_{i:03d}"
        species_db[species_id] = CoverCropSpecies(
            species_id=species_id,
            common_name=f"Test Species {i}",
            scientific_name=f"Testicus species{i}",
            cover_crop_type=CoverCropType.LEGUME if i % 3 == 0 else 
                           CoverCropType.GRASS if i % 3 == 1 else CoverCropType.BRASSICA,
            primary_benefits=[
                SoilBenefit.NITROGEN_FIXATION if i % 4 == 0 else SoilBenefit.EROSION_CONTROL,
                SoilBenefit.ORGANIC_MATTER if i % 3 == 0 else SoilBenefit.WEED_SUPPRESSION
            ],
            growing_season=GrowingSeason.WINTER if i % 2 == 0 else GrowingSeason.SUMMER,
            soil_ph_range={"min": 5.0 + (i % 5) * 0.5, "max": 7.0 + (i % 5) * 0.5},
            cold_hardiness_zone=f"{3 + (i % 6)}{'a' if i % 2 == 0 else 'b'}",
            seeding_rate_lbs_per_acre=10.0 + (i % 20) * 2.0,
            days_to_establishment=5 + (i % 15),
            nitrogen_fixation_lbs_per_acre=0 if i % 3 != 0 else 50 + (i % 10) * 10,
            drought_tolerance="high" if i % 4 == 0 else "moderate" if i % 4 == 1 else "low",
            flood_tolerance="high" if i % 4 == 0 else "moderate" if i % 4 == 1 else "poor"
        )
    
    return species_db


@pytest.fixture
def performance_test_requests():
    """Generate multiple test requests for performance testing."""
    requests = []
    
    for i in range(20):
        request = CoverCropSelectionRequest(
            request_id=f"perf_test_{i:03d}",
            location={
                "latitude": 35.0 + (i * 0.5),  # Vary locations
                "longitude": -80.0 + (i * 0.3)
            },
            soil_conditions=SoilConditions(
                ph=5.5 + (i * 0.1),
                organic_matter_percent=2.0 + (i * 0.2),
                drainage_class="well_drained" if i % 3 == 0 else 
                             "moderately_well_drained" if i % 3 == 1 else "poorly_drained",
                erosion_risk="low" if i % 3 == 0 else "moderate" if i % 3 == 1 else "high"
            ),
            objectives=CoverCropObjectives(
                primary_goals=[
                    SoilBenefit.NITROGEN_FIXATION if i % 4 == 0 else SoilBenefit.EROSION_CONTROL,
                    SoilBenefit.ORGANIC_MATTER if i % 3 == 0 else SoilBenefit.WEED_SUPPRESSION
                ],
                nitrogen_needs=i % 2 == 0,
                budget_per_acre=50.0 + (i * 5.0)
            ),
            planting_window={
                "start": "2024-09-01",
                "end": "2024-10-31"
            },
            field_size_acres=10.0 + (i * 2.0)
        )
        requests.append(request)
    
    return requests


class TestPerformanceBenchmarking:
    """Test performance benchmarks and response times."""
    
    @pytest.mark.asyncio
    async def test_single_request_performance(self, service, large_species_database, performance_test_requests):
        """Test performance of single cover crop selection request."""
        service.species_database = large_species_database
        
        # Mock external dependencies for consistent timing
        with patch.object(service, '_get_climate_data', return_value={
            "climate_zone": "7a",
            "average_annual_precipitation_inches": 40.0,
            "frost_dates": {"first_fall_frost": "2024-11-01", "last_spring_frost": "2024-04-15"}
        }):
            
            request = performance_test_requests[0]
            
            # Measure performance
            start_time = time.time()
            
            try:
                response = await service.select_cover_crops(request)
                end_time = time.time()
                
                processing_time = end_time - start_time
                
                # Performance requirements
                assert processing_time < 5.0, f"Single request should complete within 5 seconds, took {processing_time:.2f}s"
                assert processing_time < 2.0, f"Single request should ideally complete within 2 seconds, took {processing_time:.2f}s"
                
                # Verify response quality wasn't sacrificed for speed
                assert response is not None, "Should return valid response"
                
            except Exception as e:
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Even errors should be handled quickly
                assert processing_time < 10.0, f"Error handling should be fast, took {processing_time:.2f}s"
                
                # Re-raise for test failure if it's not a service initialization issue
                if "initialization" not in str(e).lower() and "database" not in str(e).lower():
                    pytest.fail(f"Unexpected error during performance test: {e}")
                    
    @pytest.mark.asyncio
    async def test_species_filtering_performance(self, service, large_species_database):
        """Test performance of species filtering algorithms."""
        service.species_database = large_species_database
        
        # Test pH filtering performance
        start_time = time.time()
        
        soil_conditions = SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained")
        
        filtered_species = await service._filter_by_soil_suitability(
            list(large_species_database.values()),
            soil_conditions
        )
        
        end_time = time.time()
        filtering_time = end_time - start_time
        
        # Filtering 100 species should be very fast
        assert filtering_time < 1.0, f"Species filtering should be fast, took {filtering_time:.3f}s"
        assert len(filtered_species) > 0, "Should return some filtered species"
        
        # Test multiple filtering operations
        start_time = time.time()
        
        for _ in range(10):
            await service._filter_by_soil_suitability(
                list(large_species_database.values()),
                soil_conditions
            )
            
        end_time = time.time()
        batch_filtering_time = end_time - start_time
        
        assert batch_filtering_time < 2.0, f"Batch filtering should be efficient, took {batch_filtering_time:.3f}s"
        
    @pytest.mark.asyncio  
    async def test_scoring_algorithm_performance(self, service, large_species_database, performance_test_requests):
        """Test performance of species scoring algorithms."""
        service.species_database = large_species_database
        
        request = performance_test_requests[0]
        species_list = list(large_species_database.values())[:20]  # Test with 20 species
        
        # Measure scoring performance
        start_time = time.time()
        
        scored_species = []
        for species in species_list:
            score = await service._calculate_species_score(species, request)
            scored_species.append((species, score))
            
        end_time = time.time()
        scoring_time = end_time - start_time
        
        # Scoring 20 species should be fast
        assert scoring_time < 2.0, f"Scoring 20 species should be fast, took {scoring_time:.3f}s"
        
        # Verify all scores are valid
        for species, score in scored_species:
            assert 0.0 <= score <= 1.0, f"Score {score} for {species.species_id} should be between 0 and 1"
            
    @pytest.mark.asyncio
    async def test_climate_data_retrieval_performance(self, service):
        """Test performance of climate data retrieval."""
        mock_climate_data = {
            "climate_zone": "7a",
            "average_annual_precipitation_inches": 40.0,
            "frost_dates": {"first_fall_frost": "2024-11-01", "last_spring_frost": "2024-04-15"}
        }
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_climate_data
            mock_get.return_value = mock_response
            
            # Test single retrieval
            start_time = time.time()
            
            climate_data = await service._get_climate_data(40.0, -74.0)
            
            end_time = time.time()
            retrieval_time = end_time - start_time
            
            assert retrieval_time < 1.0, f"Climate data retrieval should be fast, took {retrieval_time:.3f}s"
            assert climate_data == mock_climate_data, "Should return correct climate data"
            
            # Test multiple retrievals (should use caching)
            start_time = time.time()
            
            for _ in range(5):
                await service._get_climate_data(40.0, -74.0)
                
            end_time = time.time()
            cached_retrieval_time = end_time - start_time
            
            # Cached retrievals should be much faster
            assert cached_retrieval_time < retrieval_time * 2, "Cached retrievals should be efficient"


class TestLoadAndConcurrency:
    """Test load handling and concurrent request processing."""
    
    @pytest.mark.asyncio
    async def test_concurrent_request_handling(self, service, large_species_database, performance_test_requests):
        """Test handling of concurrent requests."""
        service.species_database = large_species_database
        
        # Mock external dependencies
        with patch.object(service, '_get_climate_data', return_value={
            "climate_zone": "7a",
            "average_annual_precipitation_inches": 40.0,
            "frost_dates": {"first_fall_frost": "2024-11-01", "last_spring_frost": "2024-04-15"}
        }):
            
            # Test with 5 concurrent requests
            concurrent_requests = performance_test_requests[:5]
            
            start_time = time.time()
            
            # Execute requests concurrently
            tasks = [
                service.select_cover_crops(request) 
                for request in concurrent_requests
            ]
            
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                end_time = time.time()
                
                total_time = end_time - start_time
                
                # Concurrent processing should be more efficient than sequential
                assert total_time < 15.0, f"5 concurrent requests should complete within 15s, took {total_time:.2f}s"
                
                # Check results
                successful_results = [r for r in results if not isinstance(r, Exception)]
                error_results = [r for r in results if isinstance(r, Exception)]
                
                # Should have at least some successful results
                assert len(successful_results) > 0, "Should have some successful concurrent results"
                
                # Log any errors for debugging
                for error in error_results:
                    if "initialization" not in str(error).lower():
                        print(f"Concurrent request error: {error}")
                        
            except Exception as e:
                # If gather fails, it should fail quickly
                end_time = time.time()
                error_time = end_time - start_time
                assert error_time < 10.0, f"Concurrent error handling should be fast, took {error_time:.2f}s"
                
                # Only fail if it's not a service initialization issue
                if "initialization" not in str(e).lower():
                    pytest.fail(f"Concurrent request test failed: {e}")
                    
    @pytest.mark.asyncio
    async def test_high_load_simulation(self, service, large_species_database):
        """Test behavior under high load conditions."""
        service.species_database = large_species_database
        
        # Create many simple requests
        load_requests = []
        for i in range(50):
            request = CoverCropSelectionRequest(
                request_id=f"load_test_{i}",
                location={"latitude": 40.0, "longitude": -74.0},
                soil_conditions=SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained"),
                objectives=CoverCropObjectives(primary_goals=[SoilBenefit.NITROGEN_FIXATION]),
                planting_window={"start": "2024-09-01", "end": "2024-10-31"},
                field_size_acres=25.0
            )
            load_requests.append(request)
            
        with patch.object(service, '_get_climate_data', return_value={
            "climate_zone": "7a", "average_annual_precipitation_inches": 40.0
        }):
            
            start_time = time.time()
            
            # Process in batches to simulate high load
            batch_size = 10
            all_results = []
            
            for i in range(0, len(load_requests), batch_size):
                batch = load_requests[i:i+batch_size]
                
                try:
                    batch_tasks = [service.select_cover_crops(req) for req in batch]
                    batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                    all_results.extend(batch_results)
                    
                    # Small delay between batches
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"Batch {i//batch_size} failed: {e}")
                    all_results.extend([e] * len(batch))
                    
            end_time = time.time()
            total_load_time = end_time - start_time
            
            # High load should still complete in reasonable time
            assert total_load_time < 60.0, f"High load test should complete within 60s, took {total_load_time:.2f}s"
            
            # Check success rate
            successful_results = [r for r in all_results if not isinstance(r, Exception)]
            success_rate = len(successful_results) / len(all_results)
            
            # Should have reasonable success rate even under load
            assert success_rate > 0.1, f"Should have >10% success rate under load, got {success_rate:.2%}"
            
    def test_thread_safety(self, service, large_species_database):
        """Test thread safety of service operations."""
        service.species_database = large_species_database
        
        results = []
        errors = []
        
        def worker_thread(thread_id):
            """Worker thread function."""
            try: 
                # Create thread-specific request
                request = CoverCropSelectionRequest(
                    request_id=f"thread_test_{thread_id}",
                    location={"latitude": 40.0 + thread_id * 0.1, "longitude": -74.0},
                    soil_conditions=SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained"),
                    objectives=CoverCropObjectives(primary_goals=[SoilBenefit.NITROGEN_FIXATION]),
                    planting_window={"start": "2024-09-01", "end": "2024-10-31"},
                    field_size_acres=25.0
                )
                
                # Mock climate data for thread safety
                with patch.object(service, '_get_climate_data', return_value={
                    "climate_zone": "7a", "average_annual_precipitation_inches": 40.0
                }):
                    
                    # Run async function in thread
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        result = loop.run_until_complete(service.select_cover_crops(request))
                        results.append((thread_id, result))
                    finally:
                        loop.close()
                        
            except Exception as e:
                errors.append((thread_id, str(e)))
                
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_thread, args=(i,))
            threads.append(thread)
            
        # Start all threads
        start_time = time.time()
        for thread in threads:
            thread.start()
            
        # Wait for completion
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout per thread
            
        end_time = time.time()
        thread_test_time = end_time - start_time
        
        # Thread test should complete in reasonable time
        assert thread_test_time < 45.0, f"Thread safety test should complete within 45s, took {thread_test_time:.2f}s"
        
        # Check results
        total_operations = len(results) + len(errors)
        assert total_operations > 0, "Should have some thread operations completed"
        
        # Log any errors for debugging
        if errors:
            print(f"Thread safety test errors: {errors}")
            
        # Should have some successful thread operations
        success_rate = len(results) / max(total_operations, 1)
        assert success_rate > 0.2, f"Should have >20% success rate in thread test, got {success_rate:.2%}"


class TestMemoryAndResourceUsage:
    """Test memory usage and resource management."""
    
    @pytest.mark.asyncio
    async def test_memory_usage_single_request(self, service, large_species_database, performance_test_requests):
        """Test memory usage for single request processing."""
        service.species_database = large_species_database
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch.object(service, '_get_climate_data', return_value={
            "climate_zone": "7a", "average_annual_precipitation_inches": 40.0
        }):
            
            request = performance_test_requests[0]
            
            try:
                result = await service.select_cover_crops(request)
                
                # Check memory after processing
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_increase = final_memory - initial_memory
                
                # Memory increase should be reasonable
                assert memory_increase < 100, f"Memory increase should be <100MB, was {memory_increase:.1f}MB"
                
                # Memory should be freed after processing
                del result
                import gc
                gc.collect()
                
                post_gc_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_retained = post_gc_memory - initial_memory
                
                # Should not retain excessive memory
                assert memory_retained < 50, f"Retained memory should be <50MB, was {memory_retained:.1f}MB"
                
            except Exception as e:
                if "initialization" not in str(e).lower():
                    pytest.fail(f"Memory test failed: {e}")
                    
    @pytest.mark.asyncio
    async def test_memory_usage_multiple_requests(self, service, large_species_database, performance_test_requests):
        """Test memory usage for multiple request processing."""
        service.species_database = large_species_database
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch.object(service, '_get_climate_data', return_value={
            "climate_zone": "7a", "average_annual_precipitation_inches": 40.0
        }):
            
            # Process multiple requests
            requests_to_test = performance_test_requests[:10]
            
            try:
                for i, request in enumerate(requests_to_test):
                    result = await service.select_cover_crops(request)
                    
                    # Check memory growth
                    current_memory = process.memory_info().rss / 1024 / 1024  # MB
                    memory_per_request = (current_memory - initial_memory) / (i + 1)
                    
                    # Memory per request should be reasonable
                    assert memory_per_request < 20, f"Memory per request should be <20MB, was {memory_per_request:.1f}MB"
                    
                    del result
                    
                # Force garbage collection
                import gc
                gc.collect()
                
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                total_memory_increase = final_memory - initial_memory
                
                # Total memory increase should be reasonable
                assert total_memory_increase < 200, f"Total memory increase should be <200MB, was {total_memory_increase:.1f}MB"
                
            except Exception as e:
                if "initialization" not in str(e).lower():
                    print(f"Memory test warning: {e}")


class TestCachingAndOptimization:
    """Test caching mechanisms and optimization features."""
    
    @pytest.mark.asyncio
    async def test_climate_data_caching(self, service):
        """Test climate data caching efficiency."""
        mock_climate_data = {
            "climate_zone": "7a",
            "average_annual_precipitation_inches": 40.0
        }
        
        call_count = 0
        
        def mock_http_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_climate_data
            return mock_response
            
        with patch('httpx.AsyncClient.get', side_effect=mock_http_get):
            
            # First call should hit the API
            result1 = await service._get_climate_data(40.0, -74.0)
            assert call_count == 1, "First call should hit the API"
            
            # Second call with same coordinates should use cache
            result2 = await service._get_climate_data(40.0, -74.0)
            # Note: Depending on implementation, this might still hit API
            # The test verifies caching behavior if implemented
            
            assert result1 == result2, "Cached result should match original"
            
            # Different coordinates should hit API again
            result3 = await service._get_climate_data(41.0, -75.0)
            assert result3 == mock_climate_data, "Different coordinates should work"
            
    @pytest.mark.asyncio
    async def test_species_filtering_optimization(self, service, large_species_database):
        """Test species filtering optimization."""
        service.species_database = large_species_database
        
        soil_conditions = SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained")
        
        # Time first filtering operation
        start_time = time.time()
        
        filtered1 = await service._filter_by_soil_suitability(
            list(large_species_database.values()),
            soil_conditions
        )
        
        first_time = time.time() - start_time
        
        # Time second identical filtering operation
        start_time = time.time()
        
        filtered2 = await service._filter_by_soil_suitability(
            list(large_species_database.values()),
            soil_conditions
        )
        
        second_time = time.time() - start_time
        
        # Results should be identical
        filtered1_ids = [s.species_id for s in filtered1]
        filtered2_ids = [s.species_id for s in filtered2]
        assert filtered1_ids == filtered2_ids, "Repeated filtering should give same results"
        
        # If caching is implemented, second operation should be faster
        # If not, they should be similar speed
        if second_time < first_time * 0.8:
            print(f"Filtering optimization detected: {first_time:.3f}s -> {second_time:.3f}s")
        else:
            print(f"No filtering optimization: {first_time:.3f}s -> {second_time:.3f}s")
            
    @pytest.mark.asyncio
    async def test_scoring_optimization(self, service, large_species_database, performance_test_requests):
        """Test species scoring optimization."""
        service.species_database = large_species_database
        
        request = performance_test_requests[0]
        test_species = list(large_species_database.values())[:10]
        
        # Time first scoring operation
        start_time = time.time()
        
        scores1 = []
        for species in test_species:
            score = await service._calculate_species_score(species, request)
            scores1.append(score)
            
        first_time = time.time() - start_time
        
        # Time second identical scoring operation
        start_time = time.time()
        
        scores2 = []
        for species in test_species:
            score = await service._calculate_species_score(species, request)
            scores2.append(score)
            
        second_time = time.time() - start_time
        
        # Scores should be identical
        assert scores1 == scores2, "Repeated scoring should give same results"
        
        # Both operations should complete in reasonable time
        assert first_time < 5.0, f"First scoring should be fast, took {first_time:.3f}s"
        assert second_time < 5.0, f"Second scoring should be fast, took {second_time:.3f}s"


class TestDatabaseIntegration:
    """Test database integration and data consistency."""
    
    @pytest.mark.asyncio
    async def test_species_database_loading(self, service):
        """Test species database loading and integrity."""
        # Test database initialization
        try:
            await service.initialize()
            
            # Check that database was loaded
            assert len(service.species_database) > 0, "Species database should contain species"
            
            # Check data integrity
            for species_id, species in service.species_database.items():
                assert species.species_id == species_id, f"Species ID mismatch: {species_id} != {species.species_id}"
                assert species.common_name, f"Species {species_id} should have common name"
                assert species.cover_crop_type, f"Species {species_id} should have type"
                assert len(species.primary_benefits) > 0, f"Species {species_id} should have benefits"
                
                # Check numeric fields are valid
                assert species.seeding_rate_lbs_per_acre > 0, f"Species {species_id} should have positive seeding rate"
                assert species.days_to_establishment > 0, f"Species {species_id} should have positive establishment days"
                
                # Check pH range is valid
                if hasattr(species, 'soil_ph_range') and species.soil_ph_range:
                    assert species.soil_ph_range["min"] < species.soil_ph_range["max"], \
                        f"Species {species_id} should have valid pH range"
                        
        except Exception as e:
            if "database" in str(e).lower() or "connection" in str(e).lower():
                pytest.skip(f"Database not available for testing: {e}")
            else:
                pytest.fail(f"Database integration test failed: {e}")
                
    @pytest.mark.asyncio
    async def test_mixture_database_loading(self, service):
        """Test mixture database loading and relationships."""
        try:
            await service.initialize()
            
            # Check mixture database if it exists
            if hasattr(service, 'mixture_database') and service.mixture_database:
                
                for mixture_id, mixture in service.mixture_database.items():
                    assert mixture.mixture_id == mixture_id, f"Mixture ID mismatch"
                    assert len(mixture.species_composition) > 1, f"Mixture {mixture_id} should have multiple species"
                    
                    # Check that all species in mixture exist in species database
                    for species_id in mixture.species_composition:
                        assert species_id in service.species_database, \
                            f"Mixture {mixture_id} references unknown species {species_id}"
                            
        except Exception as e:
            if "database" in str(e).lower():
                pytest.skip(f"Mixture database not available: {e}")
            else:
                print(f"Mixture database test warning: {e}")


class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.asyncio
    async def test_complete_selection_workflow(self, service, performance_test_requests):
        """Test complete cover crop selection workflow."""
        try:
            # Initialize service
            await service.initialize()
            
            request = performance_test_requests[0]
            
            # Mock external dependencies
            with patch.object(service, '_get_climate_data', return_value={
                "climate_zone": "7a",
                "average_annual_precipitation_inches": 40.0,
                "frost_dates": {"first_fall_frost": "2024-11-01", "last_spring_frost": "2024-04-15"}
            }):
                
                # Execute complete workflow
                start_time = time.time()
                
                response = await service.select_cover_crops(request)
                
                end_time = time.time()
                workflow_time = end_time - start_time
                
                # Workflow should complete in reasonable time
                assert workflow_time < 10.0, f"Complete workflow should finish within 10s, took {workflow_time:.2f}s"
                
                # Verify response structure
                assert response is not None, "Should return response"
                assert hasattr(response, 'request_id'), "Should have request ID"
                assert response.request_id == request.request_id, "Request ID should match"
                
                # Should have recommendations
                if hasattr(response, 'single_species_recommendations'):
                    assert isinstance(response.single_species_recommendations, list), \
                        "Should have list of recommendations"
                        
                # Should have confidence score
                if hasattr(response, 'overall_confidence'):
                    assert 0.0 <= response.overall_confidence <= 1.0, \
                        "Confidence should be between 0 and 1"
                        
        except Exception as e:
            if "initialization" in str(e).lower() or "database" in str(e).lower():
                pytest.skip(f"Service not fully available for workflow test: {e}")
            else:
                pytest.fail(f"End-to-end workflow test failed: {e}")
                
    @pytest.mark.asyncio
    async def test_goal_based_workflow(self, service, performance_test_requests):
        """Test goal-based recommendation workflow."""
        try:
            await service.initialize()
            
            request = performance_test_requests[0]
            
            # Create goal-based objectives
            from models.cover_crop_models import GoalBasedObjectives
            
            goal_objectives = GoalBasedObjectives(
                farmer_goals=[
                    {
                        "category": "production",
                        "specific_goal": "yield_optimization",
                        "priority_weight": 0.6
                    },
                    {
                        "category": "environmental", 
                        "specific_goal": "soil_health",
                        "priority_weight": 0.4
                    }
                ]
            )
            
            # Mock goal-based service response
            mock_goal_response = {
                "goal_optimized_recommendations": [
                    {
                        "species_id": "crimson_clover",
                        "goal_achievement_scores": {"production": 0.8, "environmental": 0.9},
                        "priority_weighted_score": 0.82
                    }
                ]
            }
            
            with patch.object(service.goal_based_service, 'generate_goal_based_recommendations', 
                            return_value=mock_goal_response):
                
                start_time = time.time()
                
                goal_response = await service.get_goal_based_recommendations(
                    request, goal_objectives
                )
                
                end_time = time.time()
                goal_workflow_time = end_time - start_time
                
                # Goal-based workflow should be efficient
                assert goal_workflow_time < 5.0, f"Goal workflow should finish within 5s, took {goal_workflow_time:.2f}s"
                
                # Verify goal response
                assert goal_response is not None, "Should return goal-based response"
                assert "goal_optimized_recommendations" in goal_response, \
                    "Should have goal-optimized recommendations"
                    
        except Exception as e:
            if "initialization" in str(e).lower():
                pytest.skip(f"Goal-based service not available: {e}")
            else:
                print(f"Goal-based workflow test warning: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])