"""
Field Management API Tests
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive tests for field management API endpoints.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from datetime import datetime
from uuid import uuid4
import json

# Import the main application
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from main import app
from field_management_service import (
    FieldCreateRequest, FieldUpdateRequest, FieldResponse, 
    FieldListResponse, FieldValidationResult, FieldBoundary, FieldCharacteristics
)

# Create test client
client = TestClient(app)


class TestFieldManagementAPI:
    """Test suite for field management API endpoints."""
    
    @pytest.fixture
    def sample_field_create_request(self):
        """Sample field creation request."""
        return {
            "location_id": str(uuid4()),
            "field_name": "Test Field 1",
            "field_type": "crop",
            "size_acres": 25.5,
            "boundary": {
                "type": "Polygon",
                "coordinates": [[
                    [42.0, -93.0],
                    [42.1, -93.0],
                    [42.1, -92.9],
                    [42.0, -92.9],
                    [42.0, -93.0]
                ]]
            },
            "characteristics": {
                "soil_type": "loam",
                "drainage_class": "good",
                "slope_percent": 5.0,
                "irrigation_available": True,
                "irrigation_type": "center_pivot",
                "access_road": True,
                "previous_crops": ["corn", "soybean"]
            },
            "notes": "Test field for API testing"
        }
    
    @pytest.fixture
    def sample_field_response(self):
        """Sample field response."""
        return {
            "id": str(uuid4()),
            "location_id": str(uuid4()),
            "field_name": "Test Field 1",
            "field_type": "crop",
            "size_acres": 25.5,
            "boundary": {
                "type": "Polygon",
                "coordinates": [[
                    [42.0, -93.0],
                    [42.1, -93.0],
                    [42.1, -92.9],
                    [42.0, -92.9],
                    [42.0, -93.0]
                ]]
            },
            "characteristics": {
                "soil_type": "loam",
                "drainage_class": "good",
                "slope_percent": 5.0,
                "irrigation_available": True,
                "irrigation_type": "center_pivot",
                "access_road": True,
                "previous_crops": ["corn", "soybean"]
            },
            "notes": "Test field for API testing",
            "agricultural_context": {
                "location_climate_zone": "5a",
                "location_county": "Story",
                "location_state": "IA",
                "field_size_category": "medium"
            },
            "soil_suitability": {
                "soil_type": "loam",
                "drainage": "good",
                "workability": "excellent",
                "fertility": "high",
                "suitable_crops": ["corn", "soybean", "wheat"]
            },
            "crop_recommendations": ["corn", "soybean", "wheat"],
            "management_complexity": "low",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def test_create_field_success(self, sample_field_create_request):
        """Test successful field creation."""
        with patch('api.field_routes.field_service.create_field') as mock_create:
            mock_create.return_value = FieldResponse(**self.sample_field_response())
            
            response = client.post("/api/v1/fields/", json=sample_field_create_request)
            
            assert response.status_code == 201
            data = response.json()
            assert data["field_name"] == "Test Field 1"
            assert data["field_type"] == "crop"
            assert data["size_acres"] == 25.5
            assert "agricultural_context" in data
            assert "soil_suitability" in data
            assert "crop_recommendations" in data
    
    def test_create_field_invalid_location_id(self):
        """Test field creation with invalid location ID."""
        request_data = {
            "location_id": "invalid-uuid",
            "field_name": "Test Field",
            "field_type": "crop"
        }
        
        response = client.post("/api/v1/fields/", json=request_data)
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"]["error_code"] == "INVALID_LOCATION_ID"
    
    def test_create_field_validation_error(self, sample_field_create_request):
        """Test field creation with validation error."""
        with patch('api.field_routes.field_service.create_field') as mock_create:
            mock_create.side_effect = ValueError("Field validation failed: Invalid boundary")
            
            response = client.post("/api/v1/fields/", json=sample_field_create_request)
            
            assert response.status_code == 422
            data = response.json()
            assert data["detail"]["error"]["error_code"] == "FIELD_VALIDATION_FAILED"
    
    def test_create_field_service_error(self, sample_field_create_request):
        """Test field creation with service error."""
        with patch('api.field_routes.field_service.create_field') as mock_create:
            mock_create.side_effect = Exception("Database connection failed")
            
            response = client.post("/api/v1/fields/", json=sample_field_create_request)
            
            assert response.status_code == 500
            data = response.json()
            assert data["detail"]["error"]["error_code"] == "FIELD_CREATION_ERROR"
    
    def test_list_fields_success(self):
        """Test successful field listing."""
        with patch('api.field_routes.field_service.list_fields') as mock_list:
            mock_response = FieldListResponse(
                fields=[FieldResponse(**self.sample_field_response())],
                total_count=1,
                page=1,
                page_size=20,
                has_next=False,
                has_previous=False,
                filters_applied={}
            )
            mock_list.return_value = mock_response
            
            response = client.get("/api/v1/fields/")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data["fields"]) == 1
            assert data["total_count"] == 1
            assert data["page"] == 1
    
    def test_list_fields_with_filters(self):
        """Test field listing with filters."""
        with patch('api.field_routes.field_service.list_fields') as mock_list:
            mock_response = FieldListResponse(
                fields=[],
                total_count=0,
                page=1,
                page_size=20,
                has_next=False,
                has_previous=False,
                filters_applied={"field_type": "crop", "soil_type": "loam"}
            )
            mock_list.return_value = mock_response
            
            response = client.get("/api/v1/fields/?field_type=crop&soil_type=loam&size_min=10&size_max=50")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_count"] == 0
            assert "field_type" in data["filters_applied"]
    
    def test_list_fields_invalid_sort(self):
        """Test field listing with invalid sort field."""
        response = client.get("/api/v1/fields/?sort_by=invalid_field")
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"]["error_code"] == "INVALID_SORT_FIELD"
    
    def test_list_fields_invalid_sort_order(self):
        """Test field listing with invalid sort order."""
        response = client.get("/api/v1/fields/?sort_order=invalid_order")
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"]["error_code"] == "INVALID_SORT_ORDER"
    
    def test_get_field_success(self):
        """Test successful field retrieval."""
        field_id = str(uuid4())
        
        with patch('api.field_routes.field_service.get_field') as mock_get:
            mock_get.return_value = FieldResponse(**self.sample_field_response())
            
            response = client.get(f"/api/v1/fields/{field_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["field_name"] == "Test Field 1"
            assert "agricultural_context" in data
    
    def test_get_field_not_found(self):
        """Test field retrieval when field not found."""
        field_id = str(uuid4())
        
        with patch('api.field_routes.field_service.get_field') as mock_get:
            mock_get.return_value = None
            
            response = client.get(f"/api/v1/fields/{field_id}")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"]["error"]["error_code"] == "FIELD_NOT_FOUND"
    
    def test_get_field_invalid_id(self):
        """Test field retrieval with invalid field ID."""
        response = client.get("/api/v1/fields/invalid-uuid")
        
        assert response.status_code == 422
        data = response.json()
        assert data["detail"]["error"]["error_code"] == "INVALID_FIELD_ID"
    
    def test_update_field_success(self):
        """Test successful field update."""
        field_id = str(uuid4())
        update_data = {
            "field_name": "Updated Field Name",
            "size_acres": 30.0,
            "characteristics": {
                "soil_type": "clay_loam",
                "drainage_class": "moderate"
            }
        }
        
        with patch('api.field_routes.field_service.update_field') as mock_update:
            updated_response = self.sample_field_response()
            updated_response["field_name"] = "Updated Field Name"
            updated_response["size_acres"] = 30.0
            mock_update.return_value = FieldResponse(**updated_response)
            
            response = client.put(f"/api/v1/fields/{field_id}", json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["field_name"] == "Updated Field Name"
            assert data["size_acres"] == 30.0
    
    def test_update_field_not_found(self):
        """Test field update when field not found."""
        field_id = str(uuid4())
        update_data = {"field_name": "Updated Field Name"}
        
        with patch('api.field_routes.field_service.update_field') as mock_update:
            mock_update.return_value = None
            
            response = client.put(f"/api/v1/fields/{field_id}", json=update_data)
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"]["error"]["error_code"] == "FIELD_NOT_FOUND"
    
    def test_update_field_validation_error(self):
        """Test field update with validation error."""
        field_id = str(uuid4())
        update_data = {
            "field_type": "invalid_type"
        }
        
        with patch('api.field_routes.field_service.update_field') as mock_update:
            mock_update.side_effect = ValueError("Field validation failed: Invalid field type")
            
            response = client.put(f"/api/v1/fields/{field_id}", json=update_data)
            
            assert response.status_code == 422
            data = response.json()
            assert data["detail"]["error"]["error_code"] == "FIELD_UPDATE_VALIDATION_FAILED"
    
    def test_delete_field_success(self):
        """Test successful field deletion."""
        field_id = str(uuid4())
        
        with patch('api.field_routes.field_service.delete_field') as mock_delete:
            mock_delete.return_value = {
                "success": True,
                "deletion_type": "soft",
                "message": "Field marked as inactive",
                "field_id": field_id,
                "dependencies_found": {"crop_records": 0}
            }
            
            response = client.delete(f"/api/v1/fields/{field_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["deletion_type"] == "soft"
    
    def test_delete_field_hard_delete(self):
        """Test hard delete field."""
        field_id = str(uuid4())
        
        with patch('api.field_routes.field_service.delete_field') as mock_delete:
            mock_delete.return_value = {
                "success": True,
                "deletion_type": "hard",
                "message": "Field permanently deleted",
                "field_id": field_id,
                "dependencies_cleaned": {"crop_records": 0}
            }
            
            response = client.delete(f"/api/v1/fields/{field_id}?hard_delete=true")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["deletion_type"] == "hard"
    
    def test_delete_field_not_found(self):
        """Test field deletion when field not found."""
        field_id = str(uuid4())
        
        with patch('api.field_routes.field_service.delete_field') as mock_delete:
            mock_delete.return_value = {
                "success": False,
                "message": "Field not found"
            }
            
            response = client.delete(f"/api/v1/fields/{field_id}")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"]["error"]["error_code"] == "FIELD_NOT_FOUND"
    
    def test_validate_field_data_success(self, sample_field_create_request):
        """Test successful field validation."""
        with patch('api.field_routes.field_service.validate_field_data') as mock_validate:
            mock_validate.return_value = FieldValidationResult(
                valid=True,
                errors=[],
                warnings=[],
                suggestions=["Consider soil testing for optimal recommendations"],
                agricultural_assessment={
                    "soil_quality": "excellent",
                    "drainage_assessment": "good",
                    "irrigation_needs": "irrigation_available",
                    "management_difficulty": "low"
                },
                optimization_recommendations=["Consider precision agriculture for this field"]
            )
            
            response = client.post("/api/v1/fields/validate", json=sample_field_create_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert len(data["errors"]) == 0
            assert "agricultural_assessment" in data
            assert "optimization_recommendations" in data
    
    def test_validate_field_data_with_errors(self, sample_field_create_request):
        """Test field validation with errors."""
        with patch('api.field_routes.field_service.validate_field_data') as mock_validate:
            mock_validate.return_value = FieldValidationResult(
                valid=False,
                errors=["Field name is required", "Invalid boundary coordinates"],
                warnings=["Steep slope detected"],
                suggestions=["Consider erosion control measures"],
                agricultural_assessment=None,
                optimization_recommendations=[]
            )
            
            response = client.post("/api/v1/fields/validate", json=sample_field_create_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is False
            assert len(data["errors"]) == 2
            assert len(data["warnings"]) == 1
    
    def test_get_agricultural_context_success(self):
        """Test successful agricultural context retrieval."""
        field_id = str(uuid4())
        
        with patch('api.field_routes.field_service.get_field') as mock_get:
            field_response = self.sample_field_response()
            mock_get.return_value = FieldResponse(**field_response)
            
            response = client.get(f"/api/v1/fields/{field_id}/agricultural-context")
            
            assert response.status_code == 200
            data = response.json()
            assert data["field_id"] == field_response["id"]
            assert "agricultural_context" in data
            assert "soil_suitability" in data
            assert "crop_recommendations" in data
            assert "validation_summary" in data
    
    def test_get_agricultural_context_not_found(self):
        """Test agricultural context retrieval when field not found."""
        field_id = str(uuid4())
        
        with patch('api.field_routes.field_service.get_field') as mock_get:
            mock_get.return_value = None
            
            response = client.get(f"/api/v1/fields/{field_id}/agricultural-context")
            
            assert response.status_code == 404
            data = response.json()
            assert data["detail"]["error"]["error_code"] == "FIELD_NOT_FOUND"
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/fields/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "field-management"
        assert "endpoints" in data
        assert len(data["endpoints"]) > 0


class TestFieldBoundaryValidation:
    """Test suite for field boundary validation."""
    
    def test_valid_polygon_boundary(self):
        """Test valid polygon boundary."""
        boundary_data = {
            "type": "Polygon",
            "coordinates": [[
                [42.0, -93.0],
                [42.1, -93.0],
                [42.1, -92.9],
                [42.0, -92.9],
                [42.0, -93.0]  # Closed polygon
            ]]
        }
        
        boundary = FieldBoundary(**boundary_data)
        assert boundary.type == "Polygon"
        assert len(boundary.coordinates) == 1
        assert len(boundary.coordinates[0]) == 5
    
    def test_invalid_polygon_not_closed(self):
        """Test invalid polygon that's not closed."""
        boundary_data = {
            "type": "Polygon",
            "coordinates": [[
                [42.0, -93.0],
                [42.1, -93.0],
                [42.1, -92.9],
                [42.0, -92.9]  # Not closed
            ]]
        }
        
        with pytest.raises(ValueError, match="Polygon ring must be closed"):
            FieldBoundary(**boundary_data)
    
    def test_invalid_coordinates(self):
        """Test invalid coordinates."""
        boundary_data = {
            "type": "Polygon",
            "coordinates": [[
                [200.0, -93.0],  # Invalid latitude
                [42.1, -93.0],
                [42.1, -92.9],
                [42.0, -92.9],
                [42.0, -93.0]
            ]]
        }
        
        with pytest.raises(ValueError, match="Invalid latitude"):
            FieldBoundary(**boundary_data)


class TestFieldCharacteristicsValidation:
    """Test suite for field characteristics validation."""
    
    def test_valid_characteristics(self):
        """Test valid field characteristics."""
        characteristics_data = {
            "soil_type": "loam",
            "drainage_class": "good",
            "slope_percent": 5.0,
            "irrigation_available": True,
            "irrigation_type": "center_pivot",
            "access_road": True,
            "previous_crops": ["corn", "soybean"]
        }
        
        characteristics = FieldCharacteristics(**characteristics_data)
        assert characteristics.soil_type == "loam"
        assert characteristics.drainage_class == "good"
        assert characteristics.slope_percent == 5.0
        assert characteristics.irrigation_available is True
    
    def test_invalid_slope_percent(self):
        """Test invalid slope percentage."""
        characteristics_data = {
            "soil_type": "loam",
            "slope_percent": 150.0  # Invalid slope
        }
        
        with pytest.raises(ValueError):
            FieldCharacteristics(**characteristics_data)


class TestFieldCreateRequestValidation:
    """Test suite for field creation request validation."""
    
    def test_valid_field_create_request(self):
        """Test valid field creation request."""
        request_data = {
            "location_id": str(uuid4()),
            "field_name": "Test Field",
            "field_type": "crop",
            "size_acres": 25.5
        }
        
        request = FieldCreateRequest(**request_data)
        assert request.field_name == "Test Field"
        assert request.field_type == "crop"
        assert request.size_acres == 25.5
    
    def test_invalid_field_type(self):
        """Test invalid field type."""
        request_data = {
            "location_id": str(uuid4()),
            "field_name": "Test Field",
            "field_type": "invalid_type"
        }
        
        with pytest.raises(ValueError, match="Field type must be one of"):
            FieldCreateRequest(**request_data)
    
    def test_invalid_size_acres(self):
        """Test invalid size in acres."""
        request_data = {
            "location_id": str(uuid4()),
            "field_name": "Test Field",
            "field_type": "crop",
            "size_acres": -10.0  # Invalid negative size
        }
        
        with pytest.raises(ValueError):
            FieldCreateRequest(**request_data)


if __name__ == "__main__":
    pytest.main([__file__])