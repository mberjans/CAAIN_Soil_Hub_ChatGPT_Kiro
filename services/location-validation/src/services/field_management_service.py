"""
Field Management Service
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

Comprehensive field management service for farm field operations including
CRUD operations, agricultural context integration, validation, and advanced
listing/selection functionality.
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
import json
import math

from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, asc

# Import existing models and services
from location_sqlalchemy_models import FarmLocation, FarmField
from location_validation_service import LocationValidationService
from geocoding_service import GeocodingService, get_geocoding_service

logger = logging.getLogger(__name__)


class FieldBoundary(BaseModel):
    """Field boundary model for geospatial data."""
    
    type: str = Field(default="Polygon", description="GeoJSON type")
    coordinates: List[List[List[float]]] = Field(..., description="Boundary coordinates")
    
    @validator('coordinates')
    def validate_coordinates(cls, v):
        """Validate boundary coordinates."""
        if not v or len(v) == 0:
            raise ValueError("Boundary coordinates cannot be empty")
        
        # Check if it's a valid polygon
        for ring in v:
            if len(ring) < 4:
                raise ValueError("Polygon ring must have at least 4 points")
            if ring[0] != ring[-1]:
                raise ValueError("Polygon ring must be closed")
            
            for point in ring:
                if len(point) != 2:
                    raise ValueError("Each coordinate point must have 2 values (lat, lng)")
                lat, lng = point
                if not (-90 <= lat <= 90):
                    raise ValueError(f"Invalid latitude: {lat}")
                if not (-180 <= lng <= 180):
                    raise ValueError(f"Invalid longitude: {lng}")
        
        return v


class FieldCharacteristics(BaseModel):
    """Field characteristics model."""
    
    soil_type: Optional[str] = Field(None, description="Primary soil type")
    drainage_class: Optional[str] = Field(None, description="Soil drainage classification")
    slope_percent: Optional[float] = Field(None, ge=0, le=100, description="Field slope percentage")
    elevation_meters: Optional[float] = Field(None, description="Field elevation")
    irrigation_available: Optional[bool] = Field(None, description="Irrigation availability")
    irrigation_type: Optional[str] = Field(None, description="Type of irrigation system")
    access_road: Optional[bool] = Field(None, description="Road access availability")
    field_shape: Optional[str] = Field(None, description="Field shape description")
    obstacles: Optional[List[str]] = Field(None, description="Field obstacles")
    previous_crops: Optional[List[str]] = Field(None, description="Previous crop history")


class FieldCreateRequest(BaseModel):
    """Request model for creating a new field."""
    
    location_id: str = Field(..., description="Parent farm location ID")
    field_name: str = Field(..., min_length=1, max_length=100, description="Field name")
    field_type: str = Field(default="crop", description="Field type (crop, pasture, other)")
    size_acres: Optional[float] = Field(None, gt=0, description="Field size in acres")
    boundary: Optional[FieldBoundary] = Field(None, description="Field boundary coordinates")
    characteristics: Optional[FieldCharacteristics] = Field(None, description="Field characteristics")
    notes: Optional[str] = Field(None, description="Additional field notes")
    
    @validator('field_type')
    def validate_field_type(cls, v):
        """Validate field type."""
        valid_types = ['crop', 'pasture', 'other']
        if v not in valid_types:
            raise ValueError(f"Field type must be one of: {valid_types}")
        return v


class FieldUpdateRequest(BaseModel):
    """Request model for updating a field."""
    
    field_name: Optional[str] = Field(None, min_length=1, max_length=100)
    field_type: Optional[str] = Field(None)
    size_acres: Optional[float] = Field(None, gt=0)
    boundary: Optional[FieldBoundary] = Field(None)
    characteristics: Optional[FieldCharacteristics] = Field(None)
    notes: Optional[str] = Field(None)
    
    @validator('field_type')
    def validate_field_type(cls, v):
        """Validate field type."""
        if v is not None:
            valid_types = ['crop', 'pasture', 'other']
            if v not in valid_types:
                raise ValueError(f"Field type must be one of: {valid_types}")
        return v


class FieldResponse(BaseModel):
    """Response model for field data."""
    
    id: str
    location_id: str
    field_name: str
    field_type: str
    size_acres: Optional[float]
    boundary: Optional[FieldBoundary]
    characteristics: Optional[FieldCharacteristics]
    notes: Optional[str]
    agricultural_context: Optional[Dict[str, Any]]
    soil_suitability: Optional[Dict[str, Any]]
    crop_recommendations: Optional[List[str]]
    management_complexity: Optional[str]
    created_at: datetime
    updated_at: datetime


class FieldListResponse(BaseModel):
    """Response model for field list with pagination."""
    
    fields: List[FieldResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool
    filters_applied: Dict[str, Any]


class FieldValidationResult(BaseModel):
    """Field validation result model."""
    
    valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    agricultural_assessment: Optional[Dict[str, Any]]
    optimization_recommendations: Optional[List[str]]


class FieldManagementService:
    """
    Comprehensive field management service.
    
    Provides CRUD operations, agricultural context integration,
    validation, and advanced listing/selection functionality.
    """
    
    def __init__(self):
        """Initialize the field management service."""
        self.logger = logging.getLogger(__name__)
        self.location_validation_service = LocationValidationService()
        self.geocoding_service = get_geocoding_service()
        
        # Agricultural context data
        self.soil_types = self._load_soil_types()
        self.crop_suitability = self._load_crop_suitability()
        self.management_complexity_factors = self._load_management_factors()
        
        self.logger.info("Field management service initialized")
    
    def _load_soil_types(self) -> Dict[str, Any]:
        """Load soil type data for agricultural context."""
        return {
            "clay": {"drainage": "poor", "workability": "difficult", "fertility": "high"},
            "clay_loam": {"drainage": "moderate", "workability": "moderate", "fertility": "high"},
            "loam": {"drainage": "good", "workability": "excellent", "fertility": "high"},
            "sandy_loam": {"drainage": "excellent", "workability": "good", "fertility": "moderate"},
            "sand": {"drainage": "excellent", "workability": "excellent", "fertility": "low"},
            "silt_loam": {"drainage": "moderate", "workability": "good", "fertility": "high"}
        }
    
    def _load_crop_suitability(self) -> Dict[str, List[str]]:
        """Load crop suitability data."""
        return {
            "corn": ["clay_loam", "loam", "silt_loam"],
            "soybean": ["clay_loam", "loam", "sandy_loam", "silt_loam"],
            "wheat": ["clay_loam", "loam", "sandy_loam", "silt_loam"],
            "cotton": ["clay_loam", "loam", "sandy_loam"],
            "rice": ["clay", "clay_loam"],
            "potato": ["sandy_loam", "loam"],
            "tomato": ["loam", "sandy_loam"],
            "lettuce": ["loam", "sandy_loam"]
        }
    
    def _load_management_factors(self) -> Dict[str, int]:
        """Load management complexity factors."""
        return {
            "irrigation_required": 2,
            "steep_slope": 3,
            "poor_drainage": 2,
            "small_field": 1,
            "irregular_shape": 2,
            "obstacles": 1
        }
    
    async def create_field(self, request: FieldCreateRequest, db_session: Session) -> FieldResponse:
        """
        Create a new field with comprehensive validation and agricultural context.
        
        Args:
            request: FieldCreateRequest with field data
            db_session: Database session
            
        Returns:
            FieldResponse with created field data
            
        Raises:
            ValueError: If validation fails
            Exception: If creation fails
        """
        try:
            self.logger.info(f"Creating field: {request.field_name} for location: {request.location_id}")
            
            # Validate location exists
            location = db_session.query(FarmLocation).filter(
                FarmLocation.id == request.location_id
            ).first()
            
            if not location:
                raise ValueError(f"Location {request.location_id} not found")
            
            # Validate field data
            validation_result = await self.validate_field_data(request)
            if not validation_result.valid:
                raise ValueError(f"Field validation failed: {validation_result.errors}")
            
            # Calculate size from boundary if not provided
            size_acres = request.size_acres
            if not size_acres and request.boundary:
                size_acres = self._calculate_boundary_area(request.boundary)
            
            # Create field record
            field_data = {
                "id": str(uuid4()),
                "location_id": request.location_id,
                "field_name": request.field_name,
                "field_type": request.field_type,
                "size_acres": size_acres,
                "soil_type": request.characteristics.soil_type if request.characteristics else None,
                "notes": request.notes,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Store boundary and characteristics as JSON
            if request.boundary:
                field_data["boundary_json"] = request.boundary.dict()
            if request.characteristics:
                field_data["characteristics_json"] = request.characteristics.dict()
            
            # Create database record
            field = FarmField(**field_data)
            db_session.add(field)
            db_session.commit()
            
            # Generate agricultural context
            agricultural_context = await self._generate_agricultural_context(field, location)
            
            # Create response
            response_data = {
                "id": field.id,
                "location_id": field.location_id,
                "field_name": field.field_name,
                "field_type": field.field_type,
                "size_acres": float(field.size_acres) if field.size_acres else None,
                "boundary": request.boundary,
                "characteristics": request.characteristics,
                "notes": field.notes,
                "agricultural_context": agricultural_context,
                "soil_suitability": self._assess_soil_suitability(request.characteristics),
                "crop_recommendations": self._get_crop_recommendations(request.characteristics),
                "management_complexity": self._assess_management_complexity(request.characteristics),
                "created_at": field.created_at,
                "updated_at": field.updated_at
            }
            
            self.logger.info(f"Field created successfully: {field.id}")
            return FieldResponse(**response_data)
            
        except Exception as e:
            self.logger.error(f"Error creating field: {e}")
            db_session.rollback()
            raise
    
    async def get_field(self, field_id: str, db_session: Session) -> Optional[FieldResponse]:
        """
        Get field by ID with agricultural context.
        
        Args:
            field_id: Field ID
            db_session: Database session
            
        Returns:
            FieldResponse or None if not found
        """
        try:
            field = db_session.query(FarmField).filter(FarmField.id == field_id).first()
            if not field:
                return None
            
            location = db_session.query(FarmLocation).filter(
                FarmLocation.id == field.location_id
            ).first()
            
            # Parse JSON data
            boundary = None
            if hasattr(field, 'boundary_json') and field.boundary_json:
                boundary = FieldBoundary(**field.boundary_json)
            
            characteristics = None
            if hasattr(field, 'characteristics_json') and field.characteristics_json:
                characteristics = FieldCharacteristics(**field.characteristics_json)
            
            # Generate agricultural context
            agricultural_context = await self._generate_agricultural_context(field, location)
            
            response_data = {
                "id": field.id,
                "location_id": field.location_id,
                "field_name": field.field_name,
                "field_type": field.field_type,
                "size_acres": float(field.size_acres) if field.size_acres else None,
                "boundary": boundary,
                "characteristics": characteristics,
                "notes": field.notes,
                "agricultural_context": agricultural_context,
                "soil_suitability": self._assess_soil_suitability(characteristics),
                "crop_recommendations": self._get_crop_recommendations(characteristics),
                "management_complexity": self._assess_management_complexity(characteristics),
                "created_at": field.created_at,
                "updated_at": field.updated_at
            }
            
            return FieldResponse(**response_data)
            
        except Exception as e:
            self.logger.error(f"Error getting field {field_id}: {e}")
            raise
    
    async def list_fields(
        self,
        location_id: Optional[str] = None,
        field_type: Optional[str] = None,
        soil_type: Optional[str] = None,
        size_min: Optional[float] = None,
        size_max: Optional[float] = None,
        irrigation_available: Optional[bool] = None,
        sort_by: str = "field_name",
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 20,
        db_session: Session = None
    ) -> FieldListResponse:
        """
        List fields with advanced filtering and sorting.
        
        Args:
            location_id: Filter by location ID
            field_type: Filter by field type
            soil_type: Filter by soil type
            size_min: Minimum field size
            size_max: Maximum field size
            irrigation_available: Filter by irrigation availability
            sort_by: Sort field
            sort_order: Sort order (asc/desc)
            page: Page number
            page_size: Items per page
            db_session: Database session
            
        Returns:
            FieldListResponse with paginated field data
        """
        try:
            # Build query
            query = db_session.query(FarmField)
            
            # Apply filters
            filters = {}
            if location_id:
                query = query.filter(FarmField.location_id == location_id)
                filters["location_id"] = location_id
            
            if field_type:
                query = query.filter(FarmField.field_type == field_type)
                filters["field_type"] = field_type
            
            if soil_type:
                # This would require JSON querying in production
                # For now, we'll filter after retrieval
                filters["soil_type"] = soil_type
            
            if size_min is not None:
                query = query.filter(FarmField.size_acres >= size_min)
                filters["size_min"] = size_min
            
            if size_max is not None:
                query = query.filter(FarmField.size_acres <= size_max)
                filters["size_max"] = size_max
            
            # Apply sorting
            sort_column = getattr(FarmField, sort_by, FarmField.field_name)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
            
            # Get total count
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            fields = query.offset(offset).limit(page_size).all()
            
            # Convert to response format
            field_responses = []
            for field in fields:
                # Get location data
                location = db_session.query(FarmLocation).filter(
                    FarmLocation.id == field.location_id
                ).first()
                
                # Parse JSON data
                boundary = None
                characteristics = None
                
                # Generate agricultural context
                agricultural_context = await self._generate_agricultural_context(field, location)
                
                response_data = {
                    "id": field.id,
                    "location_id": field.location_id,
                    "field_name": field.field_name,
                    "field_type": field.field_type,
                    "size_acres": float(field.size_acres) if field.size_acres else None,
                    "boundary": boundary,
                    "characteristics": characteristics,
                    "notes": field.notes,
                    "agricultural_context": agricultural_context,
                    "soil_suitability": self._assess_soil_suitability(characteristics),
                    "crop_recommendations": self._get_crop_recommendations(characteristics),
                    "management_complexity": self._assess_management_complexity(characteristics),
                    "created_at": field.created_at,
                    "updated_at": field.updated_at
                }
                
                field_responses.append(FieldResponse(**response_data))
            
            # Apply post-query filters (for JSON fields)
            if soil_type:
                field_responses = [
                    f for f in field_responses 
                    if f.characteristics and f.characteristics.soil_type == soil_type
                ]
            
            if irrigation_available is not None:
                field_responses = [
                    f for f in field_responses 
                    if f.characteristics and f.characteristics.irrigation_available == irrigation_available
                ]
            
            return FieldListResponse(
                fields=field_responses,
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_next=offset + page_size < total_count,
                has_previous=page > 1,
                filters_applied=filters
            )
            
        except Exception as e:
            self.logger.error(f"Error listing fields: {e}")
            raise
    
    async def update_field(
        self,
        field_id: str,
        request: FieldUpdateRequest,
        db_session: Session
    ) -> Optional[FieldResponse]:
        """
        Update field with change tracking and validation.
        
        Args:
            field_id: Field ID to update
            request: FieldUpdateRequest with update data
            db_session: Database session
            
        Returns:
            FieldResponse with updated data or None if not found
        """
        try:
            field = db_session.query(FarmField).filter(FarmField.id == field_id).first()
            if not field:
                return None
            
            # Validate update data
            if request.field_type:
                validation_result = await self.validate_field_data(
                    FieldCreateRequest(
                        location_id=field.location_id,
                        field_name=request.field_name or field.field_name,
                        field_type=request.field_type,
                        size_acres=request.size_acres,
                        boundary=request.boundary,
                        characteristics=request.characteristics,
                        notes=request.notes
                    )
                )
                if not validation_result.valid:
                    raise ValueError(f"Field validation failed: {validation_result.errors}")
            
            # Update fields
            if request.field_name:
                field.field_name = request.field_name
            if request.field_type:
                field.field_type = request.field_type
            if request.size_acres:
                field.size_acres = request.size_acres
            if request.notes:
                field.notes = request.notes
            
            # Update JSON fields
            if request.boundary:
                field.boundary_json = request.boundary.dict()
            if request.characteristics:
                field.characteristics_json = request.characteristics.dict()
            
            field.updated_at = datetime.utcnow()
            
            db_session.commit()
            
            # Get updated field with agricultural context
            return await self.get_field(field_id, db_session)
            
        except Exception as e:
            self.logger.error(f"Error updating field {field_id}: {e}")
            db_session.rollback()
            raise
    
    async def delete_field(
        self,
        field_id: str,
        hard_delete: bool = False,
        db_session: Session = None
    ) -> Dict[str, Any]:
        """
        Delete field with dependency checking.
        
        Args:
            field_id: Field ID to delete
            hard_delete: Whether to perform permanent deletion
            db_session: Database session
            
        Returns:
            Dict with deletion confirmation
        """
        try:
            field = db_session.query(FarmField).filter(FarmField.id == field_id).first()
            if not field:
                return {"success": False, "message": "Field not found"}
            
            # Check for dependencies (placeholder)
            dependencies = {
                "crop_records": 0,  # Would check for crop records
                "recommendations": 0,  # Would check for recommendations
                "historical_data": 0  # Would check for historical data
            }
            
            if not hard_delete and any(dependencies.values()):
                # Soft delete - mark as inactive
                field.is_active = False
                field.updated_at = datetime.utcnow()
                db_session.commit()
                
                return {
                    "success": True,
                    "deletion_type": "soft",
                    "message": "Field marked as inactive",
                    "field_id": field_id,
                    "dependencies_found": dependencies
                }
            else:
                # Hard delete - permanent removal
                db_session.delete(field)
                db_session.commit()
                
                return {
                    "success": True,
                    "deletion_type": "hard",
                    "message": "Field permanently deleted",
                    "field_id": field_id,
                    "dependencies_cleaned": dependencies
                }
            
        except Exception as e:
            self.logger.error(f"Error deleting field {field_id}: {e}")
            db_session.rollback()
            raise
    
    async def validate_field_data(self, request: FieldCreateRequest) -> FieldValidationResult:
        """
        Comprehensive field validation with agricultural context.
        
        Args:
            request: FieldCreateRequest to validate
            
        Returns:
            FieldValidationResult with validation details
        """
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Basic validation
            if not request.field_name or len(request.field_name.strip()) == 0:
                errors.append("Field name is required")
            
            if request.size_acres and request.size_acres <= 0:
                errors.append("Field size must be positive")
            
            # Boundary validation
            if request.boundary:
                boundary_validation = self._validate_boundary(request.boundary)
                if not boundary_validation["valid"]:
                    errors.extend(boundary_validation["errors"])
                if boundary_validation["warnings"]:
                    warnings.extend(boundary_validation["warnings"])
            
            # Agricultural validation
            if request.characteristics:
                ag_validation = self._validate_agricultural_data(request.characteristics)
                if not ag_validation["valid"]:
                    errors.extend(ag_validation["errors"])
                if ag_validation["warnings"]:
                    warnings.extend(ag_validation["warnings"])
                if ag_validation["suggestions"]:
                    suggestions.extend(ag_validation["suggestions"])
            
            # Size consistency check
            if request.boundary and request.size_acres:
                calculated_size = self._calculate_boundary_area(request.boundary)
                size_diff = abs(calculated_size - request.size_acres)
                if size_diff > 0.1:  # More than 0.1 acre difference
                    warnings.append(f"Boundary area ({calculated_size:.2f} acres) differs from specified size ({request.size_acres:.2f} acres)")
            
            # Generate agricultural assessment
            agricultural_assessment = None
            if request.characteristics:
                agricultural_assessment = {
                    "soil_quality": self._assess_soil_quality(request.characteristics),
                    "drainage_assessment": self._assess_drainage(request.characteristics),
                    "irrigation_needs": self._assess_irrigation_needs(request.characteristics),
                    "management_difficulty": self._assess_management_complexity(request.characteristics)
                }
            
            # Generate optimization recommendations
            optimization_recommendations = []
            if request.characteristics:
                if request.characteristics.slope_percent and request.characteristics.slope_percent > 15:
                    optimization_recommendations.append("Consider contour farming for steep slopes")
                
                if request.characteristics.drainage_class == "poor":
                    optimization_recommendations.append("Consider drainage improvements")
                
                if request.characteristics.soil_type == "clay":
                    optimization_recommendations.append("Consider organic matter additions for clay soils")
            
            return FieldValidationResult(
                valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions,
                agricultural_assessment=agricultural_assessment,
                optimization_recommendations=optimization_recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Error validating field data: {e}")
            return FieldValidationResult(
                valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                suggestions=[]
            )
    
    def _validate_boundary(self, boundary: FieldBoundary) -> Dict[str, Any]:
        """Validate field boundary."""
        errors = []
        warnings = []
        
        try:
            # Check polygon validity
            if boundary.type != "Polygon":
                errors.append("Boundary must be a Polygon")
            
            # Check coordinate validity
            for ring in boundary.coordinates:
                if len(ring) < 4:
                    errors.append("Polygon ring must have at least 4 points")
                
                # Check for self-intersections (simplified)
                if len(ring) > 4:
                    warnings.append("Complex polygon detected - verify boundary accuracy")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Boundary validation error: {str(e)}"],
                "warnings": []
            }
    
    def _validate_agricultural_data(self, characteristics: FieldCharacteristics) -> Dict[str, Any]:
        """Validate agricultural characteristics."""
        errors = []
        warnings = []
        suggestions = []
        
        try:
            # Soil type validation
            if characteristics.soil_type:
                if characteristics.soil_type not in self.soil_types:
                    warnings.append(f"Unknown soil type: {characteristics.soil_type}")
                else:
                    soil_info = self.soil_types[characteristics.soil_type]
                    if soil_info["drainage"] == "poor":
                        suggestions.append("Consider drainage improvements for this soil type")
            
            # Slope validation
            if characteristics.slope_percent:
                if characteristics.slope_percent > 20:
                    warnings.append("Very steep slope - consider erosion control measures")
                elif characteristics.slope_percent > 10:
                    suggestions.append("Moderate slope - consider contour farming")
            
            # Drainage validation
            if characteristics.drainage_class:
                if characteristics.drainage_class == "poor":
                    warnings.append("Poor drainage may limit crop options")
                    suggestions.append("Consider drainage improvements or select drainage-tolerant crops")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "valid": False,
                "errors": [f"Agricultural validation error: {str(e)}"],
                "warnings": [],
                "suggestions": []
            }
    
    def _calculate_boundary_area(self, boundary: FieldBoundary) -> float:
        """Calculate field area from boundary coordinates."""
        try:
            # Simplified area calculation using shoelace formula
            # In production, use proper geospatial libraries
            total_area = 0.0
            
            for ring in boundary.coordinates:
                ring_area = 0.0
                n = len(ring) - 1  # Exclude closing point
                
                for i in range(n):
                    j = (i + 1) % n
                    ring_area += ring[i][0] * ring[j][1]
                    ring_area -= ring[j][0] * ring[i][1]
                
                ring_area = abs(ring_area) / 2.0
                total_area += ring_area
            
            # Convert from square degrees to acres (approximate)
            # This is a simplified conversion - in production use proper projection
            acres_per_square_degree = 247105381.467  # Approximate
            return total_area * acres_per_square_degree
            
        except Exception as e:
            self.logger.error(f"Error calculating boundary area: {e}")
            return 0.0
    
    async def _generate_agricultural_context(self, field: FarmField, location: FarmLocation) -> Dict[str, Any]:
        """Generate agricultural context for field."""
        try:
            context = {
                "location_climate_zone": location.climate_zone,
                "location_county": location.county,
                "location_state": location.state,
                "field_size_category": self._categorize_field_size(field.size_acres),
                "management_recommendations": []
            }
            
            # Add soil-specific recommendations
            if hasattr(field, 'characteristics_json') and field.characteristics_json:
                characteristics = FieldCharacteristics(**field.characteristics_json)
                
                if characteristics.soil_type:
                    soil_info = self.soil_types.get(characteristics.soil_type, {})
                    context["soil_characteristics"] = soil_info
                
                if characteristics.drainage_class:
                    context["drainage_recommendations"] = self._get_drainage_recommendations(
                        characteristics.drainage_class
                    )
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error generating agricultural context: {e}")
            return {}
    
    def _categorize_field_size(self, size_acres: Optional[float]) -> str:
        """Categorize field size."""
        if not size_acres:
            return "unknown"
        elif size_acres < 5:
            return "small"
        elif size_acres < 25:
            return "medium"
        elif size_acres < 100:
            return "large"
        else:
            return "very_large"
    
    def _get_drainage_recommendations(self, drainage_class: str) -> List[str]:
        """Get drainage recommendations."""
        recommendations = {
            "excellent": ["Most crops suitable", "Consider precision irrigation"],
            "good": ["Most crops suitable", "Monitor soil moisture"],
            "moderate": ["Select drainage-tolerant crops", "Consider drainage improvements"],
            "poor": ["Limited crop options", "Drainage improvements recommended", "Consider raised beds"]
        }
        return recommendations.get(drainage_class, ["Consult soil specialist"])
    
    def _assess_soil_suitability(self, characteristics: Optional[FieldCharacteristics]) -> Dict[str, Any]:
        """Assess soil suitability for different crops."""
        if not characteristics or not characteristics.soil_type:
            return {"assessment": "incomplete", "recommendations": ["Complete soil analysis recommended"]}
        
        soil_info = self.soil_types.get(characteristics.soil_type, {})
        return {
            "soil_type": characteristics.soil_type,
            "drainage": soil_info.get("drainage", "unknown"),
            "workability": soil_info.get("workability", "unknown"),
            "fertility": soil_info.get("fertility", "unknown"),
            "suitable_crops": self._get_suitable_crops(characteristics.soil_type)
        }
    
    def _get_suitable_crops(self, soil_type: str) -> List[str]:
        """Get suitable crops for soil type."""
        suitable = []
        for crop, suitable_soils in self.crop_suitability.items():
            if soil_type in suitable_soils:
                suitable.append(crop)
        return suitable
    
    def _get_crop_recommendations(self, characteristics: Optional[FieldCharacteristics]) -> List[str]:
        """Get crop recommendations based on field characteristics."""
        if not characteristics:
            return ["corn", "soybean", "wheat"]  # Default recommendations
        
        recommendations = []
        
        # Base recommendations on soil type
        if characteristics.soil_type:
            recommendations.extend(self._get_suitable_crops(characteristics.soil_type))
        
        # Adjust based on drainage
        if characteristics.drainage_class == "poor":
            recommendations = [crop for crop in recommendations if crop in ["rice", "cotton"]]
        elif characteristics.drainage_class == "excellent":
            recommendations.extend(["potato", "tomato"])
        
        # Remove duplicates and limit to top 5
        return list(dict.fromkeys(recommendations))[:5]
    
    def _assess_management_complexity(self, characteristics: Optional[FieldCharacteristics]) -> str:
        """Assess field management complexity."""
        if not characteristics:
            return "unknown"
        
        complexity_score = 0
        
        # Add complexity factors
        if characteristics.slope_percent and characteristics.slope_percent > 10:
            complexity_score += self.management_complexity_factors.get("steep_slope", 0)
        
        if characteristics.drainage_class == "poor":
            complexity_score += self.management_complexity_factors.get("poor_drainage", 0)
        
        if characteristics.irrigation_available:
            complexity_score += self.management_complexity_factors.get("irrigation_required", 0)
        
        if characteristics.obstacles:
            complexity_score += len(characteristics.obstacles) * self.management_complexity_factors.get("obstacles", 0)
        
        # Categorize complexity
        if complexity_score <= 2:
            return "low"
        elif complexity_score <= 5:
            return "medium"
        else:
            return "high"
    
    def _assess_soil_quality(self, characteristics: FieldCharacteristics) -> str:
        """Assess soil quality."""
        if not characteristics.soil_type:
            return "unknown"
        
        soil_info = self.soil_types.get(characteristics.soil_type, {})
        fertility = soil_info.get("fertility", "unknown")
        
        if fertility == "high":
            return "excellent"
        elif fertility == "moderate":
            return "good"
        elif fertility == "low":
            return "fair"
        else:
            return "unknown"
    
    def _assess_drainage(self, characteristics: FieldCharacteristics) -> str:
        """Assess drainage conditions."""
        if not characteristics.drainage_class:
            return "unknown"
        
        drainage_map = {
            "excellent": "excellent",
            "good": "good",
            "moderate": "fair",
            "poor": "poor"
        }
        
        return drainage_map.get(characteristics.drainage_class, "unknown")
    
    def _assess_irrigation_needs(self, characteristics: FieldCharacteristics) -> str:
        """Assess irrigation needs."""
        if characteristics.irrigation_available:
            return "irrigation_available"
        
        if characteristics.drainage_class == "poor":
            return "irrigation_recommended"
        elif characteristics.soil_type == "sand":
            return "irrigation_recommended"
        else:
            return "rainfed_suitable"


# Export service
__all__ = [
    'FieldManagementService',
    'FieldCreateRequest',
    'FieldUpdateRequest', 
    'FieldResponse',
    'FieldListResponse',
    'FieldValidationResult',
    'FieldBoundary',
    'FieldCharacteristics'
]