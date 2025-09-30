"""
Field Management Service Tests
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive tests for field management service functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime
from uuid import uuid4

from field_management_service import (
    FieldManagementService,
    FieldCreateRequest,
    FieldUpdateRequest,
    FieldResponse,
    FieldListResponse,
    FieldValidationResult,
    FieldBoundary,
    FieldCharacteristics
)


class TestFieldManagementService:
    """Test suite for field management service."""
    
    @pytest.fixture
    def field_service(self):
        """Field management service instance."""
        return FieldManagementService()
    
    @pytest.fixture
    def sample_field_create_request(self):
        """Sample field creation request."""
        return FieldCreateRequest(
            location_id=str(uuid4()),
            field_name="Test Field 1",
            field_type="crop",
            size_acres=25.5,
            boundary=FieldBoundary(
                type="Polygon",
                coordinates=[[
                    [42.0, -93.0],
                    [42.1, -93.0],
                    [42.1, -92.9],
                    [42.0, -92.9],
                    [42.0, -93.0]
                ]]
            ),
            characteristics=FieldCharacteristics(
                soil_type="loam",
                drainage_class="good",
                slope_percent=5.0,
                irrigation_available=True,
                irrigation_type="center_pivot",
                access_road=True,
                previous_crops=["corn", "soybean"]
            ),
            notes="Test field for service testing"
        )
    
    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        session = MagicMock()
        session.query.return_value.filter.return_value.first.return_value = None
        session.add.return_value = None
        session.commit.return_value = None
        session.rollback.return_value = None
        return session
    
    @pytest.fixture
    def mock_location(self):
        """Mock farm location."""
        location = MagicMock()
        location.id = str(uuid4())
        location.climate_zone = "5a"
        location.county = "Story"
        location.state = "IA"
        return location
    
    @pytest.fixture
    def mock_field(self):
        """Mock farm field."""
        field = MagicMock()
        field.id = str(uuid4())
        field.location_id = str(uuid4())
        field.field_name = "Test Field"
        field.field_type = "crop"
        field.size_acres = 25.5
        field.soil_type = "loam"
        field.notes = "Test field"
        field.created_at = datetime.utcnow()
        field.updated_at = datetime.utcnow()
        field.boundary_json = None
        field.characteristics_json = None
        return field
    
    @pytest.mark.asyncio
    async def test_create_field_success(self, field_service, sample_field_create_request, mock_db_session, mock_location):
        """Test successful field creation."""
        # Mock location exists
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_location
        
        # Mock field creation
        mock_field = MagicMock()
        mock_field.id = str(uuid4())
        mock_field.location_id = sample_field_create_request.location_id
        mock_field.field_name = sample_field_create_request.field_name
        mock_field.field_type = sample_field_create_request.field_type
        mock_field.size_acres = sample_field_create_request.size_acres
        mock_field.soil_type = sample_field_create_request.characteristics.soil_type
        mock_field.notes = sample_field_create_request.notes
        mock_field.created_at = datetime.utcnow()
        mock_field.updated_at = datetime.utcnow()
        mock_field.boundary_json = None
        mock_field.characteristics_json = None
        
        with patch.object(field_service, '_generate_agricultural_context') as mock_context:
            mock_context.return_value = {
                "location_climate_zone": "5a",
                "location_county": "Story",
                "location_state": "IA",
                "field_size_category": "medium"
            }
            
            with patch.object(field_service, '_assess_soil_suitability') as mock_soil:
                mock_soil.return_value = {
                    "soil_type": "loam",
                    "drainage": "good",
                    "workability": "excellent",
                    "fertility": "high",
                    "suitable_crops": ["corn", "soybean", "wheat"]
                }
                
                with patch.object(field_service, '_get_crop_recommendations') as mock_crops:
                    mock_crops.return_value = ["corn", "soybean", "wheat"]
                    
                    with patch.object(field_service, '_assess_management_complexity') as mock_complexity:
                        mock_complexity.return_value = "low"
                        
                        # Mock the database add and commit
                        mock_db_session.add.return_value = None
                        mock_db_session.commit.return_value = None
                        
                        # Create field
                        result = await field_service.create_field(sample_field_create_request, mock_db_session)
                        
                        assert isinstance(result, FieldResponse)
                        assert result.field_name == "Test Field 1"
                        assert result.field_type == "crop"
                        assert result.size_acres == 25.5
                        assert result.agricultural_context is not None
                        assert result.soil_suitability is not None
                        assert result.crop_recommendations is not None
                        assert result.management_complexity == "low"
    
    @pytest.mark.asyncio
    async def test_create_field_location_not_found(self, field_service, sample_field_create_request, mock_db_session):
        """Test field creation when location not found."""
        # Mock location not found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Location .* not found"):
            await field_service.create_field(sample_field_create_request, mock_db_session)
    
    @pytest.mark.asyncio
    async def test_create_field_validation_failed(self, field_service, sample_field_create_request, mock_db_session, mock_location):
        """Test field creation with validation failure."""
        # Mock location exists
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_location
        
        # Mock validation failure
        with patch.object(field_service, 'validate_field_data') as mock_validate:
            mock_validate.return_value = FieldValidationResult(
                valid=False,
                errors=["Invalid boundary coordinates"],
                warnings=[],
                suggestions=[]
            )
            
            with pytest.raises(ValueError, match="Field validation failed"):
                await field_service.create_field(sample_field_create_request, mock_db_session)
    
    @pytest.mark.asyncio
    async def test_get_field_success(self, field_service, mock_db_session, mock_field, mock_location):
        """Test successful field retrieval."""
        field_id = str(uuid4())
        
        # Mock field exists
        mock_field.id = field_id
        mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_field, mock_location]
        
        with patch.object(field_service, '_generate_agricultural_context') as mock_context:
            mock_context.return_value = {"test": "context"}
            
            with patch.object(field_service, '_assess_soil_suitability') as mock_soil:
                mock_soil.return_value = {"test": "soil"}
                
                with patch.object(field_service, '_get_crop_recommendations') as mock_crops:
                    mock_crops.return_value = ["corn", "soybean"]
                    
                    with patch.object(field_service, '_assess_management_complexity') as mock_complexity:
                        mock_complexity.return_value = "medium"
                        
                        result = await field_service.get_field(field_id, mock_db_session)
                        
                        assert isinstance(result, FieldResponse)
                        assert result.id == field_id
                        assert result.field_name == "Test Field"
    
    @pytest.mark.asyncio
    async def test_get_field_not_found(self, field_service, mock_db_session):
        """Test field retrieval when field not found."""
        field_id = str(uuid4())
        
        # Mock field not found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = await field_service.get_field(field_id, mock_db_session)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_list_fields_success(self, field_service, mock_db_session, mock_field, mock_location):
        """Test successful field listing."""
        # Mock fields query
        mock_query = MagicMock()
        mock_query.count.return_value = 1
        mock_query.offset.return_value.limit.return_value.all.return_value = [mock_field]
        mock_db_session.query.return_value.filter.return_value.order_by.return_value = mock_query
        
        # Mock location query
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_location
        
        with patch.object(field_service, '_generate_agricultural_context') as mock_context:
            mock_context.return_value = {"test": "context"}
            
            with patch.object(field_service, '_assess_soil_suitability') as mock_soil:
                mock_soil.return_value = {"test": "soil"}
                
                with patch.object(field_service, '_get_crop_recommendations') as mock_crops:
                    mock_crops.return_value = ["corn"]
                    
                    with patch.object(field_service, '_assess_management_complexity') as mock_complexity:
                        mock_complexity.return_value = "low"
                        
                        result = await field_service.list_fields(
                            page=1,
                            page_size=20,
                            db_session=mock_db_session
                        )
                        
                        assert isinstance(result, FieldListResponse)
                        assert len(result.fields) == 1
                        assert result.total_count == 1
                        assert result.page == 1
                        assert result.page_size == 20
    
    @pytest.mark.asyncio
    async def test_update_field_success(self, field_service, mock_db_session, mock_field):
        """Test successful field update."""
        field_id = str(uuid4())
        update_request = FieldUpdateRequest(
            field_name="Updated Field Name",
            size_acres=30.0
        )
        
        # Mock field exists
        mock_field.id = field_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_field
        
        with patch.object(field_service, 'get_field') as mock_get_field:
            updated_field = FieldResponse(
                id=field_id,
                location_id=str(uuid4()),
                field_name="Updated Field Name",
                field_type="crop",
                size_acres=30.0,
                boundary=None,
                characteristics=None,
                notes=None,
                agricultural_context={},
                soil_suitability={},
                crop_recommendations=[],
                management_complexity="low",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            mock_get_field.return_value = updated_field
            
            result = await field_service.update_field(field_id, update_request, mock_db_session)
            
            assert isinstance(result, FieldResponse)
            assert result.field_name == "Updated Field Name"
            assert result.size_acres == 30.0
    
    @pytest.mark.asyncio
    async def test_update_field_not_found(self, field_service, mock_db_session):
        """Test field update when field not found."""
        field_id = str(uuid4())
        update_request = FieldUpdateRequest(field_name="Updated Field Name")
        
        # Mock field not found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = await field_service.update_field(field_id, update_request, mock_db_session)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_delete_field_soft_delete(self, field_service, mock_db_session, mock_field):
        """Test soft field deletion."""
        field_id = str(uuid4())
        
        # Mock field exists
        mock_field.id = field_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_field
        
        result = await field_service.delete_field(field_id, hard_delete=False, db_session=mock_db_session)
        
        assert result["success"] is True
        assert result["deletion_type"] == "soft"
        assert result["field_id"] == field_id
    
    @pytest.mark.asyncio
    async def test_delete_field_hard_delete(self, field_service, mock_db_session, mock_field):
        """Test hard field deletion."""
        field_id = str(uuid4())
        
        # Mock field exists
        mock_field.id = field_id
        mock_db_session.query.return_value.filter.return_value.first.return_value = mock_field
        
        result = await field_service.delete_field(field_id, hard_delete=True, db_session=mock_db_session)
        
        assert result["success"] is True
        assert result["deletion_type"] == "hard"
        assert result["field_id"] == field_id
    
    @pytest.mark.asyncio
    async def test_delete_field_not_found(self, field_service, mock_db_session):
        """Test field deletion when field not found."""
        field_id = str(uuid4())
        
        # Mock field not found
        mock_db_session.query.return_value.filter.return_value.first.return_value = None
        
        result = await field_service.delete_field(field_id, db_session=mock_db_session)
        
        assert result["success"] is False
        assert result["message"] == "Field not found"
    
    @pytest.mark.asyncio
    async def test_validate_field_data_success(self, field_service, sample_field_create_request):
        """Test successful field validation."""
        result = await field_service.validate_field_data(sample_field_create_request)
        
        assert isinstance(result, FieldValidationResult)
        assert result.valid is True
        assert len(result.errors) == 0
        assert "agricultural_assessment" in result.__dict__
        assert "optimization_recommendations" in result.__dict__
    
    @pytest.mark.asyncio
    async def test_validate_field_data_with_errors(self, field_service):
        """Test field validation with errors."""
        # Create invalid request
        invalid_request = FieldCreateRequest(
            location_id=str(uuid4()),
            field_name="",  # Invalid empty name
            field_type="crop",
            size_acres=-10.0  # Invalid negative size
        )
        
        result = await field_service.validate_field_data(invalid_request)
        
        assert isinstance(result, FieldValidationResult)
        assert result.valid is False
        assert len(result.errors) > 0
    
    def test_validate_boundary_valid(self, field_service):
        """Test valid boundary validation."""
        boundary = FieldBoundary(
            type="Polygon",
            coordinates=[[
                [42.0, -93.0],
                [42.1, -93.0],
                [42.1, -92.9],
                [42.0, -92.9],
                [42.0, -93.0]
            ]]
        )
        
        result = field_service._validate_boundary(boundary)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_boundary_invalid(self, field_service):
        """Test invalid boundary validation."""
        boundary = FieldBoundary(
            type="Polygon",
            coordinates=[[
                [42.0, -93.0],
                [42.1, -93.0],
                [42.1, -92.9],
                [42.0, -92.9]  # Not closed
            ]]
        )
        
        result = field_service._validate_boundary(boundary)
        
        assert result["valid"] is False
        assert len(result["errors"]) > 0
    
    def test_validate_agricultural_data_valid(self, field_service):
        """Test valid agricultural data validation."""
        characteristics = FieldCharacteristics(
            soil_type="loam",
            drainage_class="good",
            slope_percent=5.0,
            irrigation_available=True
        )
        
        result = field_service._validate_agricultural_data(characteristics)
        
        assert result["valid"] is True
        assert len(result["errors"]) == 0
    
    def test_validate_agricultural_data_with_warnings(self, field_service):
        """Test agricultural data validation with warnings."""
        characteristics = FieldCharacteristics(
            soil_type="clay",
            drainage_class="poor",
            slope_percent=25.0  # Very steep slope
        )
        
        result = field_service._validate_agricultural_data(characteristics)
        
        assert result["valid"] is True
        assert len(result["warnings"]) > 0
        assert len(result["suggestions"]) > 0
    
    def test_calculate_boundary_area(self, field_service):
        """Test boundary area calculation."""
        boundary = FieldBoundary(
            type="Polygon",
            coordinates=[[
                [42.0, -93.0],
                [42.1, -93.0],
                [42.1, -92.9],
                [42.0, -92.9],
                [42.0, -93.0]
            ]]
        )
        
        area = field_service._calculate_boundary_area(boundary)
        
        assert isinstance(area, float)
        assert area > 0
    
    def test_categorize_field_size(self, field_service):
        """Test field size categorization."""
        assert field_service._categorize_field_size(2.5) == "small"
        assert field_service._categorize_field_size(15.0) == "medium"
        assert field_service._categorize_field_size(50.0) == "large"
        assert field_service._categorize_field_size(150.0) == "very_large"
        assert field_service._categorize_field_size(None) == "unknown"
    
    def test_assess_soil_suitability(self, field_service):
        """Test soil suitability assessment."""
        characteristics = FieldCharacteristics(soil_type="loam")
        
        result = field_service._assess_soil_suitability(characteristics)
        
        assert "soil_type" in result
        assert "drainage" in result
        assert "workability" in result
        assert "fertility" in result
        assert "suitable_crops" in result
    
    def test_get_crop_recommendations(self, field_service):
        """Test crop recommendations."""
        characteristics = FieldCharacteristics(
            soil_type="loam",
            drainage_class="good"
        )
        
        recommendations = field_service._get_crop_recommendations(characteristics)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert len(recommendations) <= 5  # Limited to top 5
    
    def test_assess_management_complexity(self, field_service):
        """Test management complexity assessment."""
        # Low complexity
        characteristics_low = FieldCharacteristics(
            slope_percent=5.0,
            drainage_class="good",
            irrigation_available=False
        )
        
        complexity_low = field_service._assess_management_complexity(characteristics_low)
        assert complexity_low in ["low", "medium", "high"]
        
        # High complexity
        characteristics_high = FieldCharacteristics(
            slope_percent=20.0,
            drainage_class="poor",
            irrigation_available=True,
            obstacles=["rocky", "wet_areas"]
        )
        
        complexity_high = field_service._assess_management_complexity(characteristics_high)
        assert complexity_high in ["low", "medium", "high"]
    
    def test_assess_soil_quality(self, field_service):
        """Test soil quality assessment."""
        characteristics = FieldCharacteristics(soil_type="loam")
        
        quality = field_service._assess_soil_quality(characteristics)
        
        assert quality in ["excellent", "good", "fair", "unknown"]
    
    def test_assess_drainage(self, field_service):
        """Test drainage assessment."""
        characteristics = FieldCharacteristics(drainage_class="good")
        
        drainage = field_service._assess_drainage(characteristics)
        
        assert drainage in ["excellent", "good", "fair", "poor", "unknown"]
    
    def test_assess_irrigation_needs(self, field_service):
        """Test irrigation needs assessment."""
        # Irrigation available
        characteristics_available = FieldCharacteristics(irrigation_available=True)
        needs_available = field_service._assess_irrigation_needs(characteristics_available)
        assert needs_available == "irrigation_available"
        
        # Poor drainage
        characteristics_poor = FieldCharacteristics(
            irrigation_available=False,
            drainage_class="poor"
        )
        needs_poor = field_service._assess_irrigation_needs(characteristics_poor)
        assert needs_poor == "irrigation_recommended"
        
        # Sandy soil
        characteristics_sandy = FieldCharacteristics(
            irrigation_available=False,
            soil_type="sand"
        )
        needs_sandy = field_service._assess_irrigation_needs(characteristics_sandy)
        assert needs_sandy == "irrigation_recommended"
        
        # Rainfed suitable
        characteristics_rainfed = FieldCharacteristics(
            irrigation_available=False,
            drainage_class="good",
            soil_type="loam"
        )
        needs_rainfed = field_service._assess_irrigation_needs(characteristics_rainfed)
        assert needs_rainfed == "rainfed_suitable"


if __name__ == "__main__":
    pytest.main([__file__])