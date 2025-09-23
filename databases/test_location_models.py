#!/usr/bin/env python3
"""
Test Farm Location Models and Database Schema
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024
"""

import pytest
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError

# Import the models we created
from python.location_models import (
    FarmLocationCreate, FarmLocationUpdate, FarmLocation,
    FarmFieldCreate, FarmFieldUpdate, FarmField,
    LocationSource, FieldType, ValidationResult,
    GeocodingRequest, ReverseGeocodingRequest,
    LOCATION_ERRORS
)


class TestLocationModels:
    """Test Pydantic location models."""
    
    def test_farm_location_create_valid(self):
        """Test creating a valid farm location."""
        location_data = {
            "name": "North Field",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "address": "123 Farm Road, Ames, IA",
            "source": "gps"
        }
        
        location = FarmLocationCreate(**location_data)
        
        assert location.name == "North Field"
        assert location.latitude == 42.0308
        assert location.longitude == -93.6319
        assert location.source == LocationSource.GPS
    
    def test_farm_location_invalid_coordinates(self):
        """Test validation of invalid coordinates."""
        # Invalid latitude
        with pytest.raises(ValidationError) as exc_info:
            FarmLocationCreate(
                name="Test Field",
                latitude=91.0,  # Invalid
                longitude=-93.6319,
                source="gps"
            )
        assert "less than or equal to 90" in str(exc_info.value) or "Latitude must be between -90 and 90" in str(exc_info.value)
        
        # Invalid longitude
        with pytest.raises(ValidationError) as exc_info:
            FarmLocationCreate(
                name="Test Field",
                latitude=42.0308,
                longitude=181.0,  # Invalid
                source="gps"
            )
        assert "less than or equal to 180" in str(exc_info.value) or "Longitude must be between -180 and 180" in str(exc_info.value)
    
    def test_farm_location_name_validation(self):
        """Test location name validation."""
        # Empty name
        with pytest.raises(ValidationError):
            FarmLocationCreate(
                name="",
                latitude=42.0308,
                longitude=-93.6319,
                source="gps"
            )
        
        # Name with dangerous characters
        location = FarmLocationCreate(
            name="Test<script>alert('xss')</script>Field",
            latitude=42.0308,
            longitude=-93.6319,
            source="gps"
        )
        # Should be sanitized
        assert "<script>" not in location.name
        assert "Test" in location.name and "Field" in location.name
    
    def test_farm_field_create_valid(self):
        """Test creating a valid farm field."""
        field_data = {
            "location_id": str(uuid.uuid4()),
            "field_name": "Corn Field A",
            "field_type": "crop",
            "size_acres": 80.5,
            "soil_type": "silt loam"
        }
        
        field = FarmFieldCreate(**field_data)
        
        assert field.field_name == "Corn Field A"
        assert field.field_type == FieldType.CROP
        assert field.size_acres == 80.5
        assert field.soil_type == "silt loam"
    
    def test_farm_field_invalid_size(self):
        """Test validation of invalid field size."""
        with pytest.raises(ValidationError):
            FarmFieldCreate(
                location_id=str(uuid.uuid4()),
                field_name="Test Field",
                field_type="crop",
                size_acres=-10.0  # Invalid negative size
            )
    
    def test_geocoding_request_validation(self):
        """Test geocoding request validation."""
        # Valid request
        request = GeocodingRequest(address="123 Main St, Ames, IA")
        assert request.address == "123 Main St, Ames, IA"
        
        # Empty address
        with pytest.raises(ValidationError):
            GeocodingRequest(address="")
        
        # Address with dangerous characters
        request = GeocodingRequest(address="123 Main<script>St")
        assert "<script>" not in request.address
    
    def test_reverse_geocoding_request_validation(self):
        """Test reverse geocoding request validation."""
        # Valid request
        request = ReverseGeocodingRequest(latitude=42.0308, longitude=-93.6319)
        assert request.latitude == 42.0308
        assert request.longitude == -93.6319
        
        # Invalid coordinates
        with pytest.raises(ValidationError):
            ReverseGeocodingRequest(latitude=91.0, longitude=-93.6319)
    
    def test_validation_result_model(self):
        """Test validation result model."""
        from python.location_models import GeographicInfo
        
        geo_info = GeographicInfo(
            county="Story County",
            state="Iowa",
            climate_zone="5a",
            is_agricultural=True
        )
        
        result = ValidationResult(
            valid=True,
            warnings=["Location may be in non-agricultural area"],
            errors=[],
            geographic_info=geo_info
        )
        
        assert result.valid is True
        assert len(result.warnings) == 1
        assert result.geographic_info.county == "Story County"
    
    def test_location_errors_constants(self):
        """Test that location error constants are properly defined."""
        assert "INVALID_COORDINATES" in LOCATION_ERRORS
        assert "GEOCODING_FAILED" in LOCATION_ERRORS
        assert "NON_AGRICULTURAL_AREA" in LOCATION_ERRORS
        
        error = LOCATION_ERRORS["INVALID_COORDINATES"]
        assert error.error_code == "INVALID_COORDINATES"
        assert len(error.suggested_actions) > 0


class TestLocationValidation:
    """Test location validation logic."""
    
    def test_coordinate_precision_limiting(self):
        """Test that coordinates are properly validated for precision."""
        # Very precise coordinates (should be accepted)
        location = FarmLocationCreate(
            name="Precise Field",
            latitude=42.03081234,  # 8 decimal places
            longitude=-93.63191234,  # 8 decimal places
            source="gps"
        )
        
        assert location.latitude == 42.03081234
        assert location.longitude == -93.63191234
    
    def test_agricultural_area_detection_data_structure(self):
        """Test that validation result supports agricultural area detection."""
        from python.location_models import GeographicInfo
        
        geo_info = GeographicInfo(
            county="Story County",
            state="Iowa", 
            climate_zone="5a",
            is_agricultural=True
        )
        
        result = ValidationResult(
            valid=True,
            geographic_info=geo_info
        )
        
        assert result.geographic_info.is_agricultural is True
        assert result.geographic_info.county == "Story County"
    
    def test_source_enumeration(self):
        """Test location source enumeration."""
        assert LocationSource.GPS == "gps"
        assert LocationSource.ADDRESS == "address"
        assert LocationSource.MAP == "map"
        assert LocationSource.CURRENT == "current"
        
        # Test that invalid source raises error
        with pytest.raises(ValidationError):
            FarmLocationCreate(
                name="Test",
                latitude=42.0,
                longitude=-93.0,
                source="invalid_source"
            )
    
    def test_field_type_enumeration(self):
        """Test field type enumeration."""
        assert FieldType.CROP == "crop"
        assert FieldType.PASTURE == "pasture"
        assert FieldType.OTHER == "other"


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_farm_location_json_serialization(self):
        """Test that farm location can be serialized to JSON."""
        location_data = {
            "id": str(uuid.uuid4()),
            "user_id": str(uuid.uuid4()),
            "name": "Test Farm",
            "latitude": 42.0308,
            "longitude": -93.6319,
            "address": "123 Farm Road",
            "county": "Story County",
            "state": "Iowa",
            "climate_zone": "5a",
            "source": "gps",
            "verified": True,
            "accuracy_meters": 5,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        location = FarmLocation(**location_data)
        
        # Should be able to convert to dict
        location_dict = location.model_dump()
        assert location_dict["name"] == "Test Farm"
        assert location_dict["latitude"] == 42.0308
        
        # Should be able to convert to JSON
        location_json = location.model_dump_json()
        assert "Test Farm" in location_json.decode() if isinstance(location_json, bytes) else location_json
    
    def test_farm_field_json_serialization(self):
        """Test that farm field can be serialized to JSON."""
        field_data = {
            "id": str(uuid.uuid4()),
            "location_id": str(uuid.uuid4()),
            "field_name": "Corn Field",
            "field_type": "crop",
            "size_acres": 80.5,
            "soil_type": "silt loam",
            "notes": "Good drainage",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        field = FarmField(**field_data)
        
        # Should be able to convert to dict
        field_dict = field.model_dump()
        assert field_dict["field_name"] == "Corn Field"
        assert field_dict["size_acres"] == 80.5
        
        # Should be able to convert to JSON
        field_json = field.model_dump_json()
        assert "Corn Field" in field_json.decode() if isinstance(field_json, bytes) else field_json


if __name__ == "__main__":
    # Run tests if script is executed directly
    pytest.main([__file__, "-v"])