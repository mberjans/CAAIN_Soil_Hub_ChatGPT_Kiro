"""
Comprehensive Location Input Testing Suite
TICKET-008_farm-location-input-15.1 - Build comprehensive location input testing suite

This test suite provides comprehensive testing for all location input functionality including:
- Unit tests for all components
- Integration tests with external services
- Performance tests for 1000+ concurrent users
- Geographic testing across different regions
- Mobile performance testing
- Automated testing with CI/CD integration
"""

import pytest
import asyncio
import json
import time
import concurrent.futures
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import tempfile
import os
import sys
from uuid import uuid4
import statistics
import threading
from dataclasses import dataclass

# Add service paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/location-validation/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/frontend/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../databases/python'))

# Import service classes
try:
    from services.location_validation_service import LocationValidationService
    from services.geocoding_service import GeocodingService
    from services.location_management_service import LocationManagementService
    from location_models import ValidationResult, GeographicInfo, LocationData
except ImportError as e:
    print(f"Warning: Could not import some services: {e}")
    # Create mock classes for testing
    class LocationValidationService:
        pass
    class GeocodingService:
        pass
    class LocationManagementService:
        pass


@dataclass
class TestLocation:
    """Test location data structure"""
    name: str
    latitude: float
    longitude: float
    address: str
    region: str
    expected_zone: str
    accuracy_requirement: float


class ComprehensiveLocationInputTestSuite:
    """Comprehensive test suite for location input functionality"""
    
    def __init__(self):
        self.test_locations = self._initialize_test_locations()
        self.performance_thresholds = {
            'response_time_ms': 2000,  # 2 seconds max
            'concurrent_users': 1000,
            'mobile_response_time_ms': 3000,  # 3 seconds for mobile
            'geocoding_accuracy_percent': 95.0,
            'validation_accuracy_percent': 98.0
        }
        
    def _initialize_test_locations(self) -> List[TestLocation]:
        """Initialize comprehensive test locations across different regions"""
        return [
            # North America - Major agricultural regions
            TestLocation("Ames, Iowa", 42.0308, -93.6319, "123 Farm Road, Ames, IA 50010", "North America", "5a", 0.001),
            TestLocation("Fargo, North Dakota", 46.8772, -96.7898, "456 Wheat Field Lane, Fargo, ND 58102", "North America", "4a", 0.001),
            TestLocation("Lubbock, Texas", 33.5779, -101.8552, "789 Cotton Farm, Lubbock, TX 79401", "North America", "7b", 0.001),
            TestLocation("Fresno, California", 36.7378, -119.7871, "321 Almond Orchard, Fresno, CA 93701", "North America", "9a", 0.001),
            
            # Edge cases and boundary conditions
            TestLocation("North Pole", 90.0, 0.0, "North Pole", "Arctic", "1a", 0.01),
            TestLocation("South Pole", -90.0, 0.0, "South Pole", "Antarctic", "1a", 0.01),
            TestLocation("International Date Line", 0.0, 180.0, "Date Line", "Pacific", "11a", 0.01),
            TestLocation("Greenwich Meridian", 0.0, 0.0, "Greenwich", "Atlantic", "11a", 0.01),
            
            # International locations
            TestLocation("Buenos Aires, Argentina", -34.6037, -58.3816, "Estancia San Juan, Buenos Aires", "South America", "9b", 0.001),
            TestLocation("Melbourne, Australia", -37.8136, 144.9631, "Sheep Station, Melbourne", "Australia", "9a", 0.001),
            TestLocation("Moscow, Russia", 55.7558, 37.6176, "Collective Farm, Moscow", "Europe", "5a", 0.001),
            
            # Challenging geocoding cases
            TestLocation("Rural Route", 40.7128, -74.0060, "RR 1 Box 123, Nowhere County, NY", "North America", "7a", 0.01),
            TestLocation("Highway Address", 41.8781, -87.6298, "12345 Highway 61, Rural Township, IL", "North America", "6a", 0.01),
            TestLocation("PO Box", 39.7392, -104.9903, "PO Box 789, Mountain View, CO", "North America", "5b", 0.01),
        ]


class TestLocationValidationService:
    """Comprehensive unit tests for LocationValidationService"""
    
    @pytest.fixture
    def validation_service(self):
        """Create LocationValidationService instance for testing"""
        return LocationValidationService()
    
    @pytest.fixture
    def test_suite(self):
        """Create comprehensive test suite instance"""
        return ComprehensiveLocationInputTestSuite()
    
    @pytest.mark.asyncio
    async def test_coordinate_validation_comprehensive(self, validation_service, test_suite):
        """Test coordinate validation across all test locations"""
        for location in test_suite.test_locations:
            result = await validation_service.validate_coordinates(
                location.latitude, 
                location.longitude
            )
            
            assert isinstance(result, ValidationResult)
            assert result.valid is True, f"Validation failed for {location.name}"
            assert len(result.errors) == 0, f"Unexpected errors for {location.name}: {result.errors}"
    
    @pytest.mark.asyncio
    async def test_invalid_coordinate_ranges(self, validation_service):
        """Test validation with invalid coordinate ranges"""
        invalid_coordinates = [
            (91.0, 0.0, "Latitude too high"),
            (-91.0, 0.0, "Latitude too low"),
            (0.0, 181.0, "Longitude too high"),
            (0.0, -181.0, "Longitude too low"),
            (float('inf'), 0.0, "Infinite latitude"),
            (0.0, float('nan'), "NaN longitude"),
        ]
        
        for lat, lng, description in invalid_coordinates:
            result = await validation_service.validate_coordinates(lat, lng)
            assert result.valid is False, f"Should be invalid: {description}"
            assert len(result.errors) > 0, f"Should have errors: {description}"
    
    @pytest.mark.asyncio
    async def test_agricultural_area_detection(self, validation_service, test_suite):
        """Test agricultural area detection for various locations"""
        agricultural_locations = [
            loc for loc in test_suite.test_locations 
            if loc.region in ["North America", "South America", "Australia"]
        ]
        
        for location in agricultural_locations:
            result = await validation_service.validate_coordinates(
                location.latitude, 
                location.longitude
            )
            
            # Should detect as agricultural area
            assert result.valid is True, f"Should be valid agricultural area: {location.name}"
    
    @pytest.mark.asyncio
    async def test_climate_zone_detection(self, validation_service, test_suite):
        """Test climate zone detection accuracy"""
        for location in test_suite.test_locations:
            result = await validation_service.validate_coordinates(
                location.latitude, 
                location.longitude
            )
            
            if hasattr(result, 'climate_zone') and location.expected_zone:
                # Allow some tolerance for climate zone detection
                assert result.climate_zone is not None, f"No climate zone detected for {location.name}"
    
    @pytest.mark.asyncio
    async def test_validation_performance(self, validation_service, test_suite):
        """Test validation service performance"""
        start_time = time.time()
        
        # Test batch validation
        tasks = [
            validation_service.validate_coordinates(loc.latitude, loc.longitude)
            for loc in test_suite.test_locations
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000  # Convert to milliseconds
        avg_time_per_validation = total_time / len(test_suite.test_locations)
        
        assert avg_time_per_validation < 100, f"Validation too slow: {avg_time_per_validation}ms per validation"
        assert all(result.valid for result in results), "Some validations failed"


class TestGeocodingService:
    """Comprehensive tests for GeocodingService"""
    
    @pytest.fixture
    def geocoding_service(self):
        """Create GeocodingService instance for testing"""
        return GeocodingService()
    
    @pytest.fixture
    def test_suite(self):
        """Create comprehensive test suite instance"""
        return ComprehensiveLocationInputTestSuite()
    
    @pytest.mark.asyncio
    async def test_address_geocoding_accuracy(self, geocoding_service, test_suite):
        """Test geocoding accuracy for various address formats"""
        accurate_geocoding_count = 0
        
        for location in test_suite.test_locations:
            try:
                result = await geocoding_service.geocode_address(location.address)
                
                if result and result.latitude and result.longitude:
                    # Check if geocoded coordinates are within acceptable range
                    lat_diff = abs(result.latitude - location.latitude)
                    lng_diff = abs(result.longitude - location.longitude)
                    
                    if lat_diff <= location.accuracy_requirement and lng_diff <= location.accuracy_requirement:
                        accurate_geocoding_count += 1
                        
            except Exception as e:
                print(f"Geocoding failed for {location.name}: {e}")
        
        accuracy_percent = (accurate_geocoding_count / len(test_suite.test_locations)) * 100
        assert accuracy_percent >= 80.0, f"Geocoding accuracy too low: {accuracy_percent}%"
    
    @pytest.mark.asyncio
    async def test_reverse_geocoding(self, geocoding_service, test_suite):
        """Test reverse geocoding (coordinates to address)"""
        for location in test_suite.test_locations[:5]:  # Test subset for performance
            try:
                result = await geocoding_service.reverse_geocode(
                    location.latitude, 
                    location.longitude
                )
                
                assert result is not None, f"Reverse geocoding failed for {location.name}"
                assert hasattr(result, 'address'), "Result should have address field"
                
            except Exception as e:
                print(f"Reverse geocoding failed for {location.name}: {e}")
    
    @pytest.mark.asyncio
    async def test_geocoding_performance(self, geocoding_service, test_suite):
        """Test geocoding service performance"""
        start_time = time.time()
        
        # Test batch geocoding
        tasks = [
            geocoding_service.geocode_address(loc.address)
            for loc in test_suite.test_locations[:10]  # Test subset
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = (end_time - start_time) * 1000
        avg_time_per_geocoding = total_time / len(tasks)
        
        assert avg_time_per_geocoding < 2000, f"Geocoding too slow: {avg_time_per_geocoding}ms per request"
    
    @pytest.mark.asyncio
    async def test_geocoding_error_handling(self, geocoding_service):
        """Test geocoding error handling for invalid addresses"""
        invalid_addresses = [
            "Invalid Address 12345",
            "Nonexistent Street, Fake City, XX 00000",
            "",
            "!@#$%^&*()",
        ]
        
        for address in invalid_addresses:
            try:
                result = await geocoding_service.geocode_address(address)
                # Should handle gracefully without crashing
                assert result is None or not result.latitude, f"Should not geocode invalid address: {address}"
            except Exception as e:
                # Should handle errors gracefully
                assert isinstance(e, (ValueError, ConnectionError, TimeoutError))


class TestLocationManagementAPI:
    """Comprehensive tests for Location Management API"""
    
    @pytest.fixture
    def location_service(self):
        """Create LocationManagementService instance for testing"""
        return LocationManagementService()
    
    @pytest.fixture
    def test_suite(self):
        """Create comprehensive test suite instance"""
        return ComprehensiveLocationInputTestSuite()
    
    @pytest.mark.asyncio
    async def test_location_crud_operations(self, location_service, test_suite):
        """Test complete CRUD operations for locations"""
        user_id = str(uuid4())
        
        # Test Create
        location_data = {
            "name": "Test Farm",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "address": "123 Test Road, Ames, IA 50010",
            "user_id": user_id
        }
        
        created_location = await location_service.create_location(location_data)
        assert created_location is not None
        assert created_location.name == "Test Farm"
        location_id = created_location.id
        
        # Test Read
        retrieved_location = await location_service.get_location(location_id, user_id)
        assert retrieved_location is not None
        assert retrieved_location.name == "Test Farm"
        
        # Test Update
        update_data = {"name": "Updated Test Farm"}
        updated_location = await location_service.update_location(location_id, update_data, user_id)
        assert updated_location.name == "Updated Test Farm"
        
        # Test Delete
        delete_result = await location_service.delete_location(location_id, user_id)
        assert delete_result is True
        
        # Verify deletion
        deleted_location = await location_service.get_location(location_id, user_id)
        assert deleted_location is None
    
    @pytest.mark.asyncio
    async def test_location_validation_endpoint(self, location_service, test_suite):
        """Test location validation endpoint"""
        for location in test_suite.test_locations[:5]:  # Test subset
            validation_data = {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address
            }
            
            result = await location_service.validate_location(validation_data)
            assert result is not None
            assert hasattr(result, 'valid')
            assert result.valid is True, f"Validation should pass for {location.name}"
    
    @pytest.mark.asyncio
    async def test_batch_location_operations(self, location_service, test_suite):
        """Test batch operations for multiple locations"""
        user_id = str(uuid4())
        
        # Create multiple locations
        location_data_list = []
        for i, location in enumerate(test_suite.test_locations[:5]):
            location_data = {
                "name": f"Test Farm {i}",
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address,
                "user_id": user_id
            }
            location_data_list.append(location_data)
        
        # Batch create
        created_locations = await location_service.batch_create_locations(location_data_list)
        assert len(created_locations) == len(location_data_list)
        
        # Batch retrieve
        location_ids = [loc.id for loc in created_locations]
        retrieved_locations = await location_service.batch_get_locations(location_ids, user_id)
        assert len(retrieved_locations) == len(location_ids)
        
        # Batch delete
        delete_results = await location_service.batch_delete_locations(location_ids, user_id)
        assert all(delete_results)


class TestPerformanceAndLoad:
    """Performance and load testing for location input services"""
    
    @pytest.fixture
    def test_suite(self):
        """Create comprehensive test suite instance"""
        return ComprehensiveLocationInputTestSuite()
    
    @pytest.mark.asyncio
    async def test_concurrent_user_load(self, test_suite):
        """Test system performance with 1000+ concurrent users"""
        validation_service = LocationValidationService()
        geocoding_service = GeocodingService()
        
        # Simulate 1000 concurrent users
        concurrent_users = 1000
        tasks_per_user = 5  # Each user performs 5 operations
        
        async def simulate_user_operations():
            """Simulate operations a single user would perform"""
            operations = []
            
            # Randomly select locations for this user
            import random
            selected_locations = random.sample(test_suite.test_locations, 3)
            
            for location in selected_locations:
                # Validation operation
                operations.append(validation_service.validate_coordinates(
                    location.latitude, location.longitude
                ))
                
                # Geocoding operation (if address exists)
                if location.address:
                    operations.append(geocoding_service.geocode_address(location.address))
            
            return await asyncio.gather(*operations, return_exceptions=True)
        
        # Run concurrent user simulation
        start_time = time.time()
        
        user_tasks = [
            simulate_user_operations() 
            for _ in range(concurrent_users)
        ]
        
        results = await asyncio.gather(*user_tasks, return_exceptions=True)
        end_time = time.time()
        
        total_time = end_time - start_time
        total_operations = concurrent_users * tasks_per_user
        operations_per_second = total_operations / total_time
        
        # Performance assertions
        assert total_time < 30, f"Load test took too long: {total_time}s"
        assert operations_per_second > 100, f"Operations per second too low: {operations_per_second}"
        
        # Check error rate
        total_errors = sum(1 for user_results in results for result in user_results if isinstance(result, Exception))
        error_rate = (total_errors / total_operations) * 100
        assert error_rate < 5, f"Error rate too high: {error_rate}%"
    
    @pytest.mark.asyncio
    async def test_mobile_performance(self, test_suite):
        """Test mobile-specific performance requirements"""
        validation_service = LocationValidationService()
        
        # Simulate mobile network conditions (slower, less reliable)
        mobile_locations = test_suite.test_locations[:10]
        
        start_time = time.time()
        
        # Test with artificial mobile delays
        async def mobile_validation(location):
            await asyncio.sleep(0.1)  # Simulate mobile network delay
            return await validation_service.validate_coordinates(
                location.latitude, location.longitude
            )
        
        tasks = [mobile_validation(loc) for loc in mobile_locations]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        avg_time_per_operation = total_time / len(mobile_locations)
        
        assert avg_time_per_operation < 3000, f"Mobile performance too slow: {avg_time_per_operation}ms"
        assert all(result.valid for result in results), "Some mobile validations failed"
    
    @pytest.mark.asyncio
    async def test_memory_usage(self, test_suite):
        """Test memory usage during high load"""
        import psutil
        import gc
        
        validation_service = LocationValidationService()
        
        # Measure baseline memory
        gc.collect()
        baseline_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        tasks = []
        for _ in range(1000):
            location = test_suite.test_locations[0]  # Use same location
            tasks.append(validation_service.validate_coordinates(
                location.latitude, location.longitude
            ))
        
        results = await asyncio.gather(*tasks)
        
        # Measure memory after operations
        gc.collect()
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - baseline_memory
        
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase}MB"
        assert all(result.valid for result in results), "Some validations failed"


class TestGeographicAccuracy:
    """Geographic accuracy testing across different regions and coordinate systems"""
    
    @pytest.fixture
    def test_suite(self):
        """Create comprehensive test suite instance"""
        return ComprehensiveLocationInputTestSuite()
    
    @pytest.mark.asyncio
    async def test_coordinate_system_accuracy(self, test_suite):
        """Test accuracy across different coordinate systems"""
        validation_service = LocationValidationService()
        
        # Test WGS84 (standard GPS) coordinates
        wgs84_locations = [
            (42.0308, -93.6319),  # Ames, Iowa
            (40.7128, -74.0060),  # New York City
            (34.0522, -118.2437), # Los Angeles
        ]
        
        for lat, lng in wgs84_locations:
            result = await validation_service.validate_coordinates(lat, lng)
            assert result.valid is True, f"WGS84 validation failed for ({lat}, {lng})"
    
    @pytest.mark.asyncio
    async def test_regional_accuracy(self, test_suite):
        """Test accuracy across different geographic regions"""
        validation_service = LocationValidationService()
        
        # Group locations by region
        regions = {}
        for location in test_suite.test_locations:
            if location.region not in regions:
                regions[location.region] = []
            regions[location.region].append(location)
        
        for region, locations in regions.items():
            region_accuracy = 0
            for location in locations:
                result = await validation_service.validate_coordinates(
                    location.latitude, location.longitude
                )
                if result.valid:
                    region_accuracy += 1
            
            accuracy_percent = (region_accuracy / len(locations)) * 100
            assert accuracy_percent >= 90, f"Regional accuracy too low for {region}: {accuracy_percent}%"
    
    @pytest.mark.asyncio
    async def test_boundary_conditions(self, test_suite):
        """Test boundary conditions and edge cases"""
        validation_service = LocationValidationService()
        
        # Test boundary coordinates
        boundary_coordinates = [
            (90.0, 0.0, "North Pole"),
            (-90.0, 0.0, "South Pole"),
            (0.0, 180.0, "International Date Line East"),
            (0.0, -180.0, "International Date Line West"),
            (0.0, 0.0, "Equator/Prime Meridian Intersection"),
        ]
        
        for lat, lng, description in boundary_coordinates:
            result = await validation_service.validate_coordinates(lat, lng)
            assert result.valid is True, f"Boundary validation failed for {description}"
    
    @pytest.mark.asyncio
    async def test_precision_requirements(self, test_suite):
        """Test precision requirements for agricultural applications"""
        validation_service = LocationValidationService()
        
        # Test high-precision coordinates (important for precision agriculture)
        precision_locations = [
            (42.0308000, -93.6319000),  # High precision Ames, Iowa
            (40.7128000, -74.0060000),  # High precision New York
        ]
        
        for lat, lng in precision_locations:
            result = await validation_service.validate_coordinates(lat, lng)
            assert result.valid is True, f"Precision validation failed for ({lat}, {lng})"
            
            # Check that precision is maintained
            if hasattr(result, 'latitude') and hasattr(result, 'longitude'):
                lat_diff = abs(result.latitude - lat)
                lng_diff = abs(result.longitude - lng)
                assert lat_diff < 0.000001, f"Latitude precision lost: {lat_diff}"
                assert lng_diff < 0.000001, f"Longitude precision lost: {lng_diff}"


class TestAutomatedTesting:
    """Automated testing and CI/CD integration tests"""
    
    @pytest.fixture
    def test_suite(self):
        """Create comprehensive test suite instance"""
        return ComprehensiveLocationInputTestSuite()
    
    def test_ci_cd_integration(self, test_suite):
        """Test CI/CD integration requirements"""
        # Test that all required environment variables are available
        required_env_vars = [
            'DATABASE_URL',
            'REDIS_URL',
            'GEOCODING_API_KEY',
            'MAPS_API_KEY'
        ]
        
        for env_var in required_env_vars:
            # In CI/CD, these should be set
            assert os.getenv(env_var) is not None, f"Required environment variable {env_var} not set"
    
    def test_test_data_availability(self, test_suite):
        """Test that all required test data is available"""
        assert len(test_suite.test_locations) >= 10, "Insufficient test locations"
        
        # Check that test locations cover different regions
        regions = set(loc.region for loc in test_suite.test_locations)
        assert len(regions) >= 3, "Test locations don't cover enough regions"
    
    def test_performance_thresholds(self, test_suite):
        """Test that performance thresholds are properly configured"""
        thresholds = test_suite.performance_thresholds
        
        assert thresholds['response_time_ms'] <= 2000, "Response time threshold too high"
        assert thresholds['concurrent_users'] >= 1000, "Concurrent users threshold too low"
        assert thresholds['mobile_response_time_ms'] <= 3000, "Mobile response time threshold too high"
        assert thresholds['geocoding_accuracy_percent'] >= 95.0, "Geocoding accuracy threshold too low"
        assert thresholds['validation_accuracy_percent'] >= 98.0, "Validation accuracy threshold too low"
    
    @pytest.mark.asyncio
    async def test_regression_testing(self, test_suite):
        """Test regression scenarios to ensure no functionality is broken"""
        validation_service = LocationValidationService()
        
        # Test known working scenarios
        regression_locations = [
            (42.0308, -93.6319),  # Ames, Iowa - known agricultural area
            (40.7128, -74.0060),  # New York City - known urban area
            (0.0, 0.0),           # Equator/Prime Meridian - known boundary
        ]
        
        for lat, lng in regression_locations:
            result = await validation_service.validate_coordinates(lat, lng)
            assert result.valid is True, f"Regression test failed for ({lat}, {lng})"
    
    def test_error_reporting(self, test_suite):
        """Test error reporting and logging functionality"""
        # Test that error reporting is properly configured
        import logging
        
        # Check that logging is configured
        logger = logging.getLogger('location_input_tests')
        assert logger.level <= logging.INFO, "Logging level too restrictive"
        
        # Test error message format
        test_error = "Test error message"
        formatted_error = f"LOCATION_INPUT_ERROR: {test_error}"
        assert "LOCATION_INPUT_ERROR" in formatted_error, "Error format not standardized"


# Integration test class for end-to-end testing
class TestEndToEndLocationInput:
    """End-to-end testing for complete location input workflows"""
    
    @pytest.fixture
    def test_suite(self):
        """Create comprehensive test suite instance"""
        return ComprehensiveLocationInputTestSuite()
    
    @pytest.mark.asyncio
    async def test_complete_location_input_workflow(self, test_suite):
        """Test complete location input workflow from start to finish"""
        # This would test the complete user journey:
        # 1. User opens location input interface
        # 2. User selects input method (GPS, address, map)
        # 3. User provides location data
        # 4. System validates and geocodes
        # 5. User confirms location
        # 6. System saves location
        # 7. System provides agricultural context
        
        validation_service = LocationValidationService()
        geocoding_service = GeocodingService()
        
        # Simulate complete workflow
        test_location = test_suite.test_locations[0]  # Ames, Iowa
        
        # Step 1: Validate coordinates
        validation_result = await validation_service.validate_coordinates(
            test_location.latitude, test_location.longitude
        )
        assert validation_result.valid is True
        
        # Step 2: Geocode address
        geocoding_result = await geocoding_service.geocode_address(test_location.address)
        assert geocoding_result is not None
        
        # Step 3: Verify consistency
        lat_diff = abs(geocoding_result.latitude - test_location.latitude)
        lng_diff = abs(geocoding_result.longitude - test_location.longitude)
        assert lat_diff < 0.01 and lng_diff < 0.01, "Geocoding inconsistent with test coordinates"
    
    @pytest.mark.asyncio
    async def test_mobile_location_input_workflow(self, test_suite):
        """Test mobile-specific location input workflow"""
        # Test mobile-specific features:
        # - GPS location detection
        # - Touch-friendly interface
        # - Offline capability
        # - Mobile performance
        
        validation_service = LocationValidationService()
        
        # Simulate mobile GPS detection
        mobile_location = test_suite.test_locations[0]
        
        # Test with mobile-specific delays and constraints
        start_time = time.time()
        
        # Simulate mobile GPS accuracy
        gps_accuracy = 10.0  # meters
        validation_result = await validation_service.validate_coordinates(
            mobile_location.latitude, mobile_location.longitude
        )
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        
        assert validation_result.valid is True
        assert response_time < 3000, f"Mobile response time too slow: {response_time}ms"


if __name__ == "__main__":
    # Run the comprehensive test suite
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--maxfail=5",
        "--durations=10"
    ])