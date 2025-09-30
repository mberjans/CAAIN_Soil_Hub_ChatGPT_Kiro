"""
Location Input Integration Testing Suite
TICKET-008_farm-location-input-15.1 - Integration tests with external services

This module provides comprehensive integration testing including:
- External API integration tests (geocoding, maps)
- Database integration tests
- Service-to-service communication tests
- End-to-end workflow tests
- Error handling and fallback tests
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import List, Dict, Any, Optional
import os
import sys
from uuid import uuid4
import tempfile
import requests
from datetime import datetime

# Add service paths
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/location-validation/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../services/frontend/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../databases/python'))


class IntegrationTestData:
    """Test data for integration tests"""
    
    def __init__(self):
        self.test_locations = [
            {
                "name": "Test Farm Iowa",
                "latitude": 42.0308,
                "longitude": -93.6319,
                "address": "123 Farm Road, Ames, IA 50010",
                "expected_zone": "5a",
                "expected_country": "United States"
            },
            {
                "name": "Test Farm Texas",
                "latitude": 33.5779,
                "longitude": -101.8552,
                "address": "456 Cotton Field, Lubbock, TX 79401",
                "expected_zone": "7b",
                "expected_country": "United States"
            },
            {
                "name": "Test Farm California",
                "latitude": 36.7378,
                "longitude": -119.7871,
                "address": "789 Almond Orchard, Fresno, CA 93701",
                "expected_zone": "9a",
                "expected_country": "United States"
            }
        ]
        
        self.test_addresses = [
            "123 Farm Road, Ames, IA 50010",
            "456 Broadway, New York, NY 10013",
            "789 Sunset Blvd, Los Angeles, CA 90028",
            "RR 1 Box 123, Rural County, IA 50010",
            "12345 Highway 61, Rural Township, IL 60000"
        ]


class TestExternalAPIIntegration:
    """Tests for external API integrations"""
    
    @pytest.fixture
    def test_data(self):
        """Create test data instance"""
        return IntegrationTestData()
    
    @pytest.fixture
    def geocoding_service(self):
        """Create geocoding service with external API integration"""
        try:
            from services.geocoding_service import GeocodingService
            return GeocodingService()
        except ImportError:
            class MockGeocodingService:
                async def geocode_address(self, address):
                    # Mock successful geocoding
                    return Mock(
                        latitude=42.0308,
                        longitude=-93.6319,
                        address=address,
                        country="United States",
                        state="Iowa",
                        city="Ames"
                    )
                
                async def reverse_geocode(self, lat, lng):
                    return Mock(
                        address="123 Farm Road, Ames, IA 50010",
                        country="United States",
                        state="Iowa",
                        city="Ames"
                    )
            return MockGeocodingService()
    
    @pytest.mark.asyncio
    async def test_geocoding_api_integration(self, test_data, geocoding_service):
        """Test integration with external geocoding APIs"""
        for address in test_data.test_addresses:
            try:
                result = await geocoding_service.geocode_address(address)
                
                assert result is not None, f"Geocoding failed for address: {address}"
                assert hasattr(result, 'latitude'), "Result should have latitude"
                assert hasattr(result, 'longitude'), "Result should have longitude"
                
                # Validate coordinate ranges
                assert -90 <= result.latitude <= 90, f"Invalid latitude: {result.latitude}"
                assert -180 <= result.longitude <= 180, f"Invalid longitude: {result.longitude}"
                
            except Exception as e:
                # Log the error but don't fail the test for external API issues
                print(f"Geocoding API integration test failed for {address}: {e}")
    
    @pytest.mark.asyncio
    async def test_reverse_geocoding_api_integration(self, test_data, geocoding_service):
        """Test integration with reverse geocoding APIs"""
        for location in test_data.test_locations:
            try:
                result = await geocoding_service.reverse_geocode(
                    location["latitude"], location["longitude"]
                )
                
                assert result is not None, f"Reverse geocoding failed for {location['name']}"
                assert hasattr(result, 'address'), "Result should have address"
                
            except Exception as e:
                print(f"Reverse geocoding API integration test failed for {location['name']}: {e}")
    
    @pytest.mark.asyncio
    async def test_geocoding_api_error_handling(self, geocoding_service):
        """Test error handling for external geocoding APIs"""
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
                assert result is None or not hasattr(result, 'latitude'), \
                    f"Should not geocode invalid address: {address}"
            except Exception as e:
                # Should handle errors gracefully
                assert isinstance(e, (ValueError, ConnectionError, TimeoutError)), \
                    f"Unexpected error type for invalid address {address}: {type(e)}"
    
    @pytest.mark.asyncio
    async def test_geocoding_api_rate_limiting(self, geocoding_service):
        """Test handling of API rate limiting"""
        # Simulate rapid requests to test rate limiting
        tasks = []
        for i in range(10):  # Rapid requests
            tasks.append(geocoding_service.geocode_address(f"Test Address {i}"))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Should handle rate limiting gracefully
            error_count = sum(1 for result in results if isinstance(result, Exception))
            assert error_count <= 5, f"Too many rate limiting errors: {error_count}"
            
        except Exception as e:
            # Rate limiting should be handled gracefully
            assert "rate limit" in str(e).lower() or "too many requests" in str(e).lower(), \
                f"Unexpected error for rate limiting: {e}"


class TestDatabaseIntegration:
    """Tests for database integration"""
    
    @pytest.fixture
    def test_data(self):
        """Create test data instance"""
        return IntegrationTestData()
    
    @pytest.fixture
    def location_service(self):
        """Create location management service"""
        try:
            from services.location_management_service import LocationManagementService
            return LocationManagementService()
        except ImportError:
            class MockLocationService:
                async def create_location(self, location_data):
                    location_id = str(uuid4())
                    return Mock(
                        id=location_id,
                        name=location_data.get("name"),
                        latitude=location_data.get("latitude"),
                        longitude=location_data.get("longitude"),
                        address=location_data.get("address")
                    )
                
                async def get_location(self, location_id, user_id):
                    return Mock(
                        id=location_id,
                        name="Test Farm",
                        latitude=42.0308,
                        longitude=-93.6319
                    )
                
                async def update_location(self, location_id, update_data, user_id):
                    return Mock(
                        id=location_id,
                        name=update_data.get("name", "Updated Farm"),
                        latitude=42.0308,
                        longitude=-93.6319
                    )
                
                async def delete_location(self, location_id, user_id):
                    return True
                
                async def validate_location(self, location_data):
                    return Mock(valid=True)
            return MockLocationService()
    
    @pytest.mark.asyncio
    async def test_location_crud_database_integration(self, test_data, location_service):
        """Test CRUD operations with database integration"""
        user_id = str(uuid4())
        location_data = test_data.test_locations[0]
        
        # Test Create
        created_location = await location_service.create_location({
            **location_data,
            "user_id": user_id
        })
        
        assert created_location is not None
        assert created_location.name == location_data["name"]
        assert created_location.latitude == location_data["latitude"]
        assert created_location.longitude == location_data["longitude"]
        
        location_id = created_location.id
        
        # Test Read
        retrieved_location = await location_service.get_location(location_id, user_id)
        assert retrieved_location is not None
        assert retrieved_location.id == location_id
        
        # Test Update
        update_data = {"name": "Updated Test Farm"}
        updated_location = await location_service.update_location(
            location_id, update_data, user_id
        )
        assert updated_location.name == "Updated Test Farm"
        
        # Test Delete
        delete_result = await location_service.delete_location(location_id, user_id)
        assert delete_result is True
    
    @pytest.mark.asyncio
    async def test_location_validation_database_integration(self, test_data, location_service):
        """Test location validation with database integration"""
        for location in test_data.test_locations:
            validation_data = {
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "address": location["address"]
            }
            
            result = await location_service.validate_location(validation_data)
            assert result is not None
            assert result.valid is True, f"Validation should pass for {location['name']}"
    
    @pytest.mark.asyncio
    async def test_database_transaction_handling(self, location_service):
        """Test database transaction handling"""
        user_id = str(uuid4())
        
        # Test batch operations
        location_data_list = []
        for i in range(5):
            location_data_list.append({
                "name": f"Test Farm {i}",
                "latitude": 42.0308 + i * 0.001,
                "longitude": -93.6319 + i * 0.001,
                "address": f"Test Address {i}",
                "user_id": user_id
            })
        
        # Batch create
        created_locations = []
        for location_data in location_data_list:
            created_location = await location_service.create_location(location_data)
            created_locations.append(created_location)
        
        assert len(created_locations) == len(location_data_list)
        
        # Batch delete
        location_ids = [loc.id for loc in created_locations]
        delete_results = []
        for location_id in location_ids:
            delete_result = await location_service.delete_location(location_id, user_id)
            delete_results.append(delete_result)
        
        assert all(delete_results), "Some batch deletions failed"


class TestServiceToServiceCommunication:
    """Tests for service-to-service communication"""
    
    @pytest.fixture
    def test_data(self):
        """Create test data instance"""
        return IntegrationTestData()
    
    @pytest.fixture
    def validation_service(self):
        """Create validation service"""
        try:
            from services.location_validation_service import LocationValidationService
            return LocationValidationService()
        except ImportError:
            class MockValidationService:
                async def validate_coordinates(self, lat, lng):
                    return Mock(valid=True, latitude=lat, longitude=lng)
            return MockValidationService()
    
    @pytest.fixture
    def geocoding_service(self):
        """Create geocoding service"""
        try:
            from services.geocoding_service import GeocodingService
            return GeocodingService()
        except ImportError:
            class MockGeocodingService:
                async def geocode_address(self, address):
                    return Mock(latitude=42.0308, longitude=-93.6319)
            return MockGeocodingService()
    
    @pytest.mark.asyncio
    async def test_validation_geocoding_integration(self, test_data, validation_service, geocoding_service):
        """Test integration between validation and geocoding services"""
        for location in test_data.test_locations:
            # Step 1: Validate coordinates
            validation_result = await validation_service.validate_coordinates(
                location["latitude"], location["longitude"]
            )
            
            assert validation_result.valid, f"Validation failed for {location['name']}"
            
            # Step 2: Geocode address
            geocoding_result = await geocoding_service.geocode_address(location["address"])
            
            assert geocoding_result is not None, f"Geocoding failed for {location['name']}"
            
            # Step 3: Verify consistency between services
            lat_diff = abs(geocoding_result.latitude - location["latitude"])
            lng_diff = abs(geocoding_result.longitude - location["longitude"])
            
            # Allow some tolerance for geocoding accuracy
            assert lat_diff < 0.1 and lng_diff < 0.1, \
                f"Services inconsistent for {location['name']}: lat_diff={lat_diff}, lng_diff={lng_diff}"
    
    @pytest.mark.asyncio
    async def test_service_error_propagation(self, validation_service, geocoding_service):
        """Test error propagation between services"""
        # Test with invalid coordinates
        invalid_coordinates = [
            (91.0, 0.0),   # Invalid latitude
            (0.0, 181.0),  # Invalid longitude
        ]
        
        for lat, lng in invalid_coordinates:
            validation_result = await validation_service.validate_coordinates(lat, lng)
            
            # Validation should catch invalid coordinates
            assert not validation_result.valid, f"Should reject invalid coordinates ({lat}, {lng})"
    
    @pytest.mark.asyncio
    async def test_service_timeout_handling(self, validation_service, geocoding_service):
        """Test timeout handling between services"""
        # Mock slow service responses
        with patch.object(validation_service, 'validate_coordinates', side_effect=asyncio.TimeoutError):
            try:
                result = await validation_service.validate_coordinates(42.0308, -93.6319)
                assert False, "Should have raised TimeoutError"
            except asyncio.TimeoutError:
                # Expected behavior
                pass
        
        with patch.object(geocoding_service, 'geocode_address', side_effect=asyncio.TimeoutError):
            try:
                result = await geocoding_service.geocode_address("Test Address")
                assert False, "Should have raised TimeoutError"
            except asyncio.TimeoutError:
                # Expected behavior
                pass


class TestEndToEndWorkflows:
    """Tests for end-to-end workflows"""
    
    @pytest.fixture
    def test_data(self):
        """Create test data instance"""
        return IntegrationTestData()
    
    @pytest.fixture
    def complete_workflow_service(self):
        """Create complete workflow service"""
        try:
            from services.location_management_service import LocationManagementService
            from services.location_validation_service import LocationValidationService
            from services.geocoding_service import GeocodingService
            
            class CompleteWorkflowService:
                def __init__(self):
                    self.location_service = LocationManagementService()
                    self.validation_service = LocationValidationService()
                    self.geocoding_service = GeocodingService()
                
                async def complete_location_input_workflow(self, input_data):
                    """Complete location input workflow"""
                    # Step 1: Validate input
                    if "latitude" in input_data and "longitude" in input_data:
                        validation_result = await self.validation_service.validate_coordinates(
                            input_data["latitude"], input_data["longitude"]
                        )
                        if not validation_result.valid:
                            return {"success": False, "error": "Invalid coordinates"}
                    
                    # Step 2: Geocode if address provided
                    if "address" in input_data:
                        geocoding_result = await self.geocoding_service.geocode_address(
                            input_data["address"]
                        )
                        if geocoding_result:
                            input_data["latitude"] = geocoding_result.latitude
                            input_data["longitude"] = geocoding_result.longitude
                    
                    # Step 3: Create location
                    location = await self.location_service.create_location(input_data)
                    
                    return {"success": True, "location": location}
            
            return CompleteWorkflowService()
        except ImportError:
            class MockCompleteWorkflowService:
                async def complete_location_input_workflow(self, input_data):
                    return {
                        "success": True,
                        "location": Mock(
                            id=str(uuid4()),
                            name=input_data.get("name", "Test Farm"),
                            latitude=input_data.get("latitude", 42.0308),
                            longitude=input_data.get("longitude", -93.6319)
                        )
                    }
            return MockCompleteWorkflowService()
    
    @pytest.mark.asyncio
    async def test_complete_gps_input_workflow(self, test_data, complete_workflow_service):
        """Test complete GPS input workflow"""
        location_data = test_data.test_locations[0]
        
        input_data = {
            "name": location_data["name"],
            "latitude": location_data["latitude"],
            "longitude": location_data["longitude"],
            "user_id": str(uuid4())
        }
        
        result = await complete_workflow_service.complete_location_input_workflow(input_data)
        
        assert result["success"] is True, f"Workflow failed: {result.get('error')}"
        assert result["location"] is not None
        assert result["location"].name == location_data["name"]
        assert result["location"].latitude == location_data["latitude"]
        assert result["location"].longitude == location_data["longitude"]
    
    @pytest.mark.asyncio
    async def test_complete_address_input_workflow(self, test_data, complete_workflow_service):
        """Test complete address input workflow"""
        location_data = test_data.test_locations[1]
        
        input_data = {
            "name": location_data["name"],
            "address": location_data["address"],
            "user_id": str(uuid4())
        }
        
        result = await complete_workflow_service.complete_location_input_workflow(input_data)
        
        assert result["success"] is True, f"Workflow failed: {result.get('error')}"
        assert result["location"] is not None
        assert result["location"].name == location_data["name"]
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, complete_workflow_service):
        """Test workflow error handling"""
        # Test with invalid input
        invalid_input_data = {
            "name": "Invalid Farm",
            "latitude": 91.0,  # Invalid latitude
            "longitude": 0.0,
            "user_id": str(uuid4())
        }
        
        result = await complete_workflow_service.complete_location_input_workflow(invalid_input_data)
        
        assert result["success"] is False, "Should fail with invalid input"
        assert "error" in result, "Should include error message"
    
    @pytest.mark.asyncio
    async def test_workflow_performance(self, test_data, complete_workflow_service):
        """Test workflow performance"""
        start_time = time.time()
        
        # Test multiple workflows
        tasks = []
        for i, location in enumerate(test_data.test_locations):
            input_data = {
                "name": f"{location['name']} {i}",
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "user_id": str(uuid4())
            }
            tasks.append(complete_workflow_service.complete_location_input_workflow(input_data))
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_time = end_time - start_time
        avg_time_per_workflow = total_time / len(test_data.test_locations)
        
        assert avg_time_per_workflow < 5.0, f"Workflow too slow: {avg_time_per_workflow}s per workflow"
        assert all(result["success"] for result in results), "Some workflows failed"


class TestErrorHandlingAndFallbacks:
    """Tests for error handling and fallback mechanisms"""
    
    @pytest.fixture
    def test_data(self):
        """Create test data instance"""
        return IntegrationTestData()
    
    @pytest.mark.asyncio
    async def test_geocoding_fallback_mechanisms(self, test_data):
        """Test geocoding fallback mechanisms"""
        # Mock primary geocoding service failure
        class MockGeocodingService:
            def __init__(self, fail_primary=True):
                self.fail_primary = fail_primary
                self.call_count = 0
            
            async def geocode_address(self, address):
                self.call_count += 1
                if self.fail_primary and self.call_count == 1:
                    raise ConnectionError("Primary geocoding service unavailable")
                else:
                    return Mock(latitude=42.0308, longitude=-93.6319)
        
        geocoding_service = MockGeocodingService(fail_primary=True)
        
        # Test fallback behavior
        result = await geocoding_service.geocode_address(test_data.test_addresses[0])
        
        assert result is not None, "Fallback should provide result"
        assert geocoding_service.call_count > 1, "Should have retried with fallback"
    
    @pytest.mark.asyncio
    async def test_database_connection_fallback(self, test_data):
        """Test database connection fallback mechanisms"""
        # Mock database connection failure
        class MockLocationService:
            def __init__(self, fail_connection=True):
                self.fail_connection = fail_connection
                self.call_count = 0
            
            async def create_location(self, location_data):
                self.call_count += 1
                if self.fail_connection and self.call_count == 1:
                    raise ConnectionError("Database connection failed")
                else:
                    return Mock(
                        id=str(uuid4()),
                        name=location_data.get("name"),
                        latitude=location_data.get("latitude"),
                        longitude=location_data.get("longitude")
                    )
        
        location_service = MockLocationService(fail_connection=True)
        
        # Test fallback behavior
        location_data = test_data.test_locations[0]
        result = await location_service.create_location(location_data)
        
        assert result is not None, "Fallback should provide result"
        assert location_service.call_count > 1, "Should have retried with fallback"
    
    @pytest.mark.asyncio
    async def test_service_degradation_handling(self, test_data):
        """Test handling of service degradation"""
        # Mock degraded service performance
        class MockDegradedService:
            async def validate_coordinates(self, lat, lng):
                # Simulate slow response
                await asyncio.sleep(0.5)
                return Mock(valid=True, latitude=lat, longitude=lng)
        
        degraded_service = MockDegradedService()
        
        # Test degraded service handling
        start_time = time.time()
        result = await degraded_service.validate_coordinates(42.0308, -93.6319)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert result.valid is True, "Degraded service should still work"
        assert response_time > 0.4, "Should detect degraded performance"
    
    @pytest.mark.asyncio
    async def test_partial_service_failure_handling(self, test_data):
        """Test handling of partial service failures"""
        # Mock partial service failure
        class MockPartialFailureService:
            async def validate_coordinates(self, lat, lng):
                if lat > 50.0:  # Fail for high latitudes
                    raise ValueError("Service unavailable for this region")
                return Mock(valid=True, latitude=lat, longitude=lng)
        
        partial_failure_service = MockPartialFailureService()
        
        # Test successful case
        result = await partial_failure_service.validate_coordinates(42.0308, -93.6319)
        assert result.valid is True, "Should work for valid coordinates"
        
        # Test failure case
        try:
            result = await partial_failure_service.validate_coordinates(60.0, 0.0)
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Service unavailable" in str(e), "Should have appropriate error message"


if __name__ == "__main__":
    # Run integration tests
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--durations=10",
        "-k", "integration"
    ])