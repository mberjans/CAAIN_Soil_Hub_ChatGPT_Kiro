# Data Models - Crop Variety Recommendations

## Overview

This document describes the data models used in the Crop Variety Recommendations system. The models are designed to support comprehensive variety selection, comparison, and recommendation functionality while maintaining data integrity and performance.

## Core Data Models

### 1. Crop Model

**Purpose**: Represents crop types and their basic characteristics

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CropCategory(str, Enum):
    GRAIN = "grain"
    VEGETABLE = "vegetable"
    FORAGE = "forage"
    FRUIT = "fruit"
    LEGUME = "legume"
    OILSEED = "oilseed"

class Crop(BaseModel):
    """Core crop model with essential characteristics."""
    
    id: str = Field(..., description="Unique crop identifier")
    name: str = Field(..., description="Common crop name")
    scientific_name: str = Field(..., description="Scientific name")
    category: CropCategory = Field(..., description="Crop category")
    family: str = Field(..., description="Plant family")
    description: Optional[str] = Field(None, description="Crop description")
    
    # Growing characteristics
    growing_season_days: Optional[int] = Field(None, description="Typical growing season length")
    planting_season: Optional[str] = Field(None, description="Primary planting season")
    harvest_season: Optional[str] = Field(None, description="Primary harvest season")
    
    # Environmental requirements
    min_temperature_celsius: Optional[float] = Field(None, description="Minimum growing temperature")
    max_temperature_celsius: Optional[float] = Field(None, description="Maximum growing temperature")
    min_precipitation_mm: Optional[float] = Field(None, description="Minimum annual precipitation")
    max_precipitation_mm: Optional[float] = Field(None, description="Maximum annual precipitation")
    
    # Soil requirements
    preferred_ph_min: Optional[float] = Field(None, description="Minimum preferred soil pH")
    preferred_ph_max: Optional[float] = Field(None, description="Maximum preferred soil pH")
    preferred_soil_types: List[str] = Field(default_factory=list, description="Preferred soil types")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether crop is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "corn",
                "name": "Corn",
                "scientific_name": "Zea mays",
                "category": "grain",
                "family": "Poaceae",
                "description": "Major cereal grain crop",
                "growing_season_days": 120,
                "planting_season": "spring",
                "harvest_season": "fall",
                "min_temperature_celsius": 10.0,
                "max_temperature_celsius": 35.0,
                "min_precipitation_mm": 500.0,
                "max_precipitation_mm": 1500.0,
                "preferred_ph_min": 6.0,
                "preferred_ph_max": 7.5,
                "preferred_soil_types": ["clay_loam", "silt_loam"]
            }
        }
```

### 2. Crop Variety Model

**Purpose**: Represents individual crop varieties with detailed characteristics

```python
class MaturityType(str, Enum):
    EARLY = "early"
    MEDIUM = "medium"
    LATE = "late"

class DiseaseResistanceLevel(str, Enum):
    SUSCEPTIBLE = "susceptible"
    MODERATELY_SUSCEPTIBLE = "moderately_susceptible"
    MODERATELY_RESISTANT = "moderately_resistant"
    RESISTANT = "resistant"
    HIGHLY_RESISTANT = "highly_resistant"

class CropVariety(BaseModel):
    """Detailed crop variety model with performance characteristics."""
    
    id: str = Field(..., description="Unique variety identifier")
    crop_id: str = Field(..., description="Parent crop identifier")
    name: str = Field(..., description="Variety name")
    company: str = Field(..., description="Seed company")
    description: Optional[str] = Field(None, description="Variety description")
    
    # Maturity and growth
    maturity_days: int = Field(..., description="Days to maturity")
    maturity_type: MaturityType = Field(..., description="Maturity classification")
    plant_height_cm: Optional[float] = Field(None, description="Average plant height")
    
    # Yield characteristics
    yield_potential_min: float = Field(..., description="Minimum yield potential")
    yield_potential_max: float = Field(..., description="Maximum yield potential")
    yield_unit: str = Field(default="bu/acre", description="Yield unit")
    yield_consistency: Optional[float] = Field(None, description="Yield consistency score (0-1)")
    
    # Environmental adaptation
    climate_zones: List[str] = Field(default_factory=list, description="Compatible climate zones")
    drought_tolerance: Optional[float] = Field(None, description="Drought tolerance score (0-1)")
    heat_tolerance: Optional[float] = Field(None, description="Heat tolerance score (0-1)")
    cold_tolerance: Optional[float] = Field(None, description="Cold tolerance score (0-1)")
    
    # Soil adaptation
    soil_ph_min: Optional[float] = Field(None, description="Minimum soil pH")
    soil_ph_max: Optional[float] = Field(None, description="Maximum soil pH")
    soil_types: List[str] = Field(default_factory=list, description="Compatible soil types")
    drainage_preference: Optional[str] = Field(None, description="Drainage preference")
    
    # Disease resistance
    disease_resistance: Dict[str, DiseaseResistanceLevel] = Field(
        default_factory=dict, 
        description="Disease resistance ratings"
    )
    
    # Traits and characteristics
    traits: List[str] = Field(default_factory=list, description="Variety traits")
    special_characteristics: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Special characteristics and notes"
    )
    
    # Economic data
    seed_cost_per_acre: Optional[float] = Field(None, description="Seed cost per acre")
    market_premium: Optional[float] = Field(None, description="Market premium percentage")
    
    # Performance data
    regional_performance: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict, 
        description="Regional performance data"
    )
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, description="Whether variety is active")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "pioneer-1197",
                "crop_id": "corn",
                "name": "Pioneer P1197AM",
                "company": "Pioneer",
                "description": "High-yielding corn hybrid with excellent disease resistance",
                "maturity_days": 105,
                "maturity_type": "medium",
                "plant_height_cm": 260.0,
                "yield_potential_min": 180.0,
                "yield_potential_max": 200.0,
                "yield_unit": "bu/acre",
                "yield_consistency": 0.85,
                "climate_zones": ["5a", "5b", "6a", "6b"],
                "drought_tolerance": 0.8,
                "heat_tolerance": 0.7,
                "cold_tolerance": 0.6,
                "soil_ph_min": 6.0,
                "soil_ph_max": 7.5,
                "soil_types": ["clay_loam", "silt_loam"],
                "drainage_preference": "well_drained",
                "disease_resistance": {
                    "northern_corn_leaf_blight": "resistant",
                    "gray_leaf_spot": "moderately_resistant",
                    "common_rust": "resistant"
                },
                "traits": ["drought_tolerance", "high_yield", "disease_resistance"],
                "seed_cost_per_acre": 85.0,
                "market_premium": 0.05
            }
        }
```

### 3. Farm Data Model

**Purpose**: Represents farm and field characteristics for recommendations

```python
class SoilType(str, Enum):
    CLAY = "clay"
    CLAY_LOAM = "clay_loam"
    SANDY_LOAM = "sandy_loam"
    SILT_LOAM = "silt_loam"
    SAND = "sand"
    SILT = "silt"
    LOAM = "loam"

class DrainageClass(str, Enum):
    POORLY_DRAINED = "poorly_drained"
    MODERATELY_DRAINED = "moderately_drained"
    WELL_DRAINED = "well_drained"
    EXCESSIVELY_DRAINED = "excessively_drained"

class FarmData(BaseModel):
    """Farm and field data for variety recommendations."""
    
    # Location data
    location: Dict[str, Any] = Field(..., description="Location information")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    climate_zone: Optional[str] = Field(None, description="Climate zone")
    elevation_meters: Optional[float] = Field(None, description="Elevation in meters")
    
    # Field characteristics
    field_size_acres: float = Field(..., gt=0, description="Field size in acres")
    soil_type: SoilType = Field(..., description="Primary soil type")
    drainage: DrainageClass = Field(..., description="Drainage classification")
    slope_percent: Optional[float] = Field(None, description="Field slope percentage")
    
    # Soil properties
    soil_data: Dict[str, Any] = Field(..., description="Soil test data")
    ph: float = Field(..., ge=0, le=14, description="Soil pH")
    organic_matter_percent: Optional[float] = Field(None, description="Organic matter percentage")
    cec: Optional[float] = Field(None, description="Cation exchange capacity")
    phosphorus_ppm: Optional[float] = Field(None, description="Phosphorus in ppm")
    potassium_ppm: Optional[float] = Field(None, description="Potassium in ppm")
    
    # Management factors
    irrigation_available: bool = Field(default=False, description="Irrigation availability")
    tillage_system: Optional[str] = Field(None, description="Tillage system")
    previous_crop: Optional[str] = Field(None, description="Previous crop")
    crop_rotation: Optional[List[str]] = Field(None, description="Crop rotation history")
    
    # Environmental factors
    pest_pressure: Optional[str] = Field(None, description="Pest pressure level")
    disease_history: Optional[List[str]] = Field(None, description="Disease history")
    weather_risks: Optional[List[str]] = Field(None, description="Weather risk factors")
    
    class Config:
        json_schema_extra = {
            "example": {
                "location": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "county": "New York",
                    "state": "NY"
                },
                "latitude": 40.7128,
                "longitude": -74.0060,
                "climate_zone": "6a",
                "elevation_meters": 10.0,
                "field_size_acres": 100.0,
                "soil_type": "clay_loam",
                "drainage": "well_drained",
                "slope_percent": 2.0,
                "soil_data": {
                    "ph": 6.5,
                    "organic_matter_percent": 3.2,
                    "cec": 15.0,
                    "phosphorus_ppm": 25.0,
                    "potassium_ppm": 150.0
                },
                "ph": 6.5,
                "organic_matter_percent": 3.2,
                "cec": 15.0,
                "phosphorus_ppm": 25.0,
                "potassium_ppm": 150.0,
                "irrigation_available": True,
                "tillage_system": "no_till",
                "previous_crop": "soybean",
                "crop_rotation": ["corn", "soybean", "wheat"],
                "pest_pressure": "medium",
                "disease_history": ["gray_leaf_spot"],
                "weather_risks": ["drought", "excessive_rainfall"]
            }
        }
```

### 4. User Preferences Model

**Purpose**: Represents farmer preferences and priorities

```python
class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

class UserPreferences(BaseModel):
    """User preferences for variety recommendations."""
    
    # Yield preferences
    yield_priority: PriorityLevel = Field(default=PriorityLevel.HIGH, description="Yield priority")
    yield_target: Optional[float] = Field(None, description="Target yield")
    yield_consistency_priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM, 
        description="Yield consistency priority"
    )
    
    # Quality preferences
    quality_focus: Optional[List[str]] = Field(None, description="Quality focus areas")
    market_targets: Optional[List[str]] = Field(None, description="Market targets")
    quality_priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Quality priority")
    
    # Risk preferences
    risk_tolerance: PriorityLevel = Field(default=PriorityLevel.MEDIUM, description="Risk tolerance")
    disease_resistance_priority: PriorityLevel = Field(
        default=PriorityLevel.HIGH, 
        description="Disease resistance priority"
    )
    stress_tolerance_priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM, 
        description="Stress tolerance priority"
    )
    
    # Management preferences
    management_intensity: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM, 
        description="Management intensity preference"
    )
    input_cost_sensitivity: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM, 
        description="Input cost sensitivity"
    )
    labor_availability: PriorityLevel = Field(
        default=PriorityLevel.HIGH, 
        description="Labor availability"
    )
    
    # Timing preferences
    maturity_preference: Optional[str] = Field(None, description="Maturity preference")
    planting_window: Optional[Dict[str, Any]] = Field(None, description="Planting window")
    harvest_window: Optional[Dict[str, Any]] = Field(None, description="Harvest window")
    
    # Economic preferences
    seed_budget: Optional[float] = Field(None, description="Seed budget per acre")
    roi_target: Optional[float] = Field(None, description="Target ROI")
    break_even_yield: Optional[float] = Field(None, description="Break-even yield")
    
    # Special requirements
    organic_requirements: bool = Field(default=False, description="Organic requirements")
    gmo_preference: Optional[str] = Field(None, description="GMO preference")
    sustainability_goals: Optional[List[str]] = Field(None, description="Sustainability goals")
    
    class Config:
        json_schema_extra = {
            "example": {
                "yield_priority": "high",
                "yield_target": 180.0,
                "yield_consistency_priority": "medium",
                "quality_focus": ["protein_content", "test_weight"],
                "market_targets": ["feed", "ethanol"],
                "quality_priority": "medium",
                "risk_tolerance": "medium",
                "disease_resistance_priority": "high",
                "stress_tolerance_priority": "medium",
                "management_intensity": "medium",
                "input_cost_sensitivity": "medium",
                "labor_availability": "high",
                "maturity_preference": "medium",
                "seed_budget": 80.0,
                "roi_target": 1.5,
                "break_even_yield": 150.0,
                "organic_requirements": False,
                "gmo_preference": "acceptable",
                "sustainability_goals": ["soil_health", "water_conservation"]
            }
        }
```

### 5. Variety Recommendation Model

**Purpose**: Represents the output of variety recommendation requests

```python
class SuitabilityLevel(str, Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    EXCELLENT = "excellent"

class VarietyRecommendation(BaseModel):
    """Variety recommendation result."""
    
    variety_id: str = Field(..., description="Variety identifier")
    variety_name: str = Field(..., description="Variety name")
    company: str = Field(..., description="Seed company")
    rank: int = Field(..., description="Recommendation rank")
    
    # Suitability assessment
    suitability: SuitabilityLevel = Field(..., description="Overall suitability")
    confidence: float = Field(..., ge=0, le=1, description="Recommendation confidence")
    match_score: float = Field(..., ge=0, le=1, description="Overall match score")
    
    # Performance predictions
    predicted_yield: Optional[float] = Field(None, description="Predicted yield")
    yield_advantage: Optional[str] = Field(None, description="Yield advantage")
    yield_risk: Optional[str] = Field(None, description="Yield risk assessment")
    
    # Adaptation analysis
    climate_adaptation: Dict[str, Any] = Field(default_factory=dict, description="Climate adaptation")
    soil_adaptation: Dict[str, Any] = Field(default_factory=dict, description="Soil adaptation")
    regional_performance: Dict[str, Any] = Field(default_factory=dict, description="Regional performance")
    
    # Risk assessment
    risk_factors: List[str] = Field(default_factory=list, description="Risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Mitigation strategies")
    
    # Economic analysis
    economic_analysis: Dict[str, Any] = Field(default_factory=dict, description="Economic analysis")
    seed_cost_per_acre: Optional[float] = Field(None, description="Seed cost per acre")
    expected_roi: Optional[float] = Field(None, description="Expected ROI")
    break_even_yield: Optional[float] = Field(None, description="Break-even yield")
    
    # Explanation and justification
    explanation: str = Field(..., description="Recommendation explanation")
    key_benefits: List[str] = Field(default_factory=list, description="Key benefits")
    considerations: List[str] = Field(default_factory=list, description="Important considerations")
    
    # Supporting data
    supporting_evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence")
    data_sources: List[str] = Field(default_factory=list, description="Data sources")
    
    class Config:
        json_schema_extra = {
            "example": {
                "variety_id": "pioneer-1197",
                "variety_name": "Pioneer P1197AM",
                "company": "Pioneer",
                "rank": 1,
                "suitability": "excellent",
                "confidence": 0.92,
                "match_score": 0.95,
                "predicted_yield": 185.0,
                "yield_advantage": "+12%",
                "yield_risk": "low",
                "climate_adaptation": {
                    "zone_compatibility": "excellent",
                    "temperature_tolerance": "high",
                    "drought_tolerance": "high"
                },
                "soil_adaptation": {
                    "ph_compatibility": "excellent",
                    "soil_type_match": "good",
                    "drainage_preference": "well_drained"
                },
                "risk_factors": ["high_seed_cost"],
                "mitigation_strategies": ["bulk_purchasing", "early_ordering"],
                "economic_analysis": {
                    "seed_cost_per_acre": 85.0,
                    "expected_roi": 1.8,
                    "break_even_yield": 150.0
                },
                "explanation": "This variety offers excellent yield potential with strong disease resistance, making it ideal for your field conditions.",
                "key_benefits": [
                    "High yield potential",
                    "Excellent disease resistance",
                    "Good drought tolerance",
                    "Strong regional performance"
                ],
                "considerations": [
                    "Higher seed cost",
                    "Requires good management",
                    "Best suited for well-drained soils"
                ]
            }
        }
```

## Request/Response Models

### 1. Recommendation Request Model

```python
class VarietyRecommendationRequest(BaseModel):
    """Request model for variety recommendations."""
    
    crop_id: str = Field(..., description="Crop type identifier")
    farm_data: FarmData = Field(..., description="Farm and field data")
    user_preferences: Optional[UserPreferences] = Field(None, description="User preferences")
    max_recommendations: int = Field(default=20, ge=1, le=100, description="Maximum recommendations")
    include_explanations: bool = Field(default=True, description="Include detailed explanations")
    include_economic_analysis: bool = Field(default=True, description="Include economic analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_id": "corn",
                "farm_data": {
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "field_size_acres": 100.0,
                    "soil_type": "clay_loam",
                    "drainage": "well_drained",
                    "ph": 6.5,
                    "organic_matter_percent": 3.2,
                    "irrigation_available": True
                },
                "user_preferences": {
                    "yield_priority": "high",
                    "disease_resistance_priority": "high",
                    "seed_budget": 80.0
                },
                "max_recommendations": 10,
                "include_explanations": True,
                "include_economic_analysis": True
            }
        }
```

### 2. Recommendation Response Model

```python
class VarietyRecommendationResponse(BaseModel):
    """Response model for variety recommendations."""
    
    request_id: str = Field(..., description="Unique request identifier")
    crop_id: str = Field(..., description="Crop type identifier")
    recommendations: List[VarietyRecommendation] = Field(..., description="Variety recommendations")
    total_varieties_evaluated: int = Field(..., description="Total varieties evaluated")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "request_id": "req_12345",
                "crop_id": "corn",
                "recommendations": [
                    {
                        "variety_id": "pioneer-1197",
                        "variety_name": "Pioneer P1197AM",
                        "company": "Pioneer",
                        "rank": 1,
                        "suitability": "excellent",
                        "confidence": 0.92,
                        "match_score": 0.95
                    }
                ],
                "total_varieties_evaluated": 150,
                "processing_time_ms": 1250.0,
                "metadata": {
                    "cache_hit": False,
                    "data_sources": ["crop_taxonomy", "climate_zone", "market_price"],
                    "algorithm_version": "1.2.0"
                }
            }
        }
```

## Database Schema

### 1. PostgreSQL Tables

```sql
-- Crops table
CREATE TABLE crops (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(150),
    category VARCHAR(50) NOT NULL,
    family VARCHAR(50),
    description TEXT,
    growing_season_days INTEGER,
    planting_season VARCHAR(50),
    harvest_season VARCHAR(50),
    min_temperature_celsius DECIMAL(5,2),
    max_temperature_celsius DECIMAL(5,2),
    min_precipitation_mm DECIMAL(8,2),
    max_precipitation_mm DECIMAL(8,2),
    preferred_ph_min DECIMAL(3,1),
    preferred_ph_max DECIMAL(3,1),
    preferred_soil_types TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Crop varieties table
CREATE TABLE crop_varieties (
    id VARCHAR(100) PRIMARY KEY,
    crop_id VARCHAR(50) REFERENCES crops(id),
    name VARCHAR(150) NOT NULL,
    company VARCHAR(100),
    description TEXT,
    maturity_days INTEGER NOT NULL,
    maturity_type VARCHAR(20),
    plant_height_cm DECIMAL(6,2),
    yield_potential_min DECIMAL(8,2),
    yield_potential_max DECIMAL(8,2),
    yield_unit VARCHAR(20) DEFAULT 'bu/acre',
    yield_consistency DECIMAL(3,2),
    climate_zones TEXT[],
    drought_tolerance DECIMAL(3,2),
    heat_tolerance DECIMAL(3,2),
    cold_tolerance DECIMAL(3,2),
    soil_ph_min DECIMAL(3,1),
    soil_ph_max DECIMAL(3,1),
    soil_types TEXT[],
    drainage_preference VARCHAR(50),
    disease_resistance JSONB,
    traits TEXT[],
    special_characteristics JSONB,
    seed_cost_per_acre DECIMAL(8,2),
    market_premium DECIMAL(5,4),
    regional_performance JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Variety recommendations table
CREATE TABLE variety_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(100) NOT NULL,
    crop_id VARCHAR(50) REFERENCES crops(id),
    variety_id VARCHAR(100) REFERENCES crop_varieties(id),
    farm_data JSONB NOT NULL,
    user_preferences JSONB,
    rank INTEGER NOT NULL,
    suitability VARCHAR(20) NOT NULL,
    confidence DECIMAL(3,2) NOT NULL,
    match_score DECIMAL(3,2) NOT NULL,
    predicted_yield DECIMAL(8,2),
    yield_advantage VARCHAR(20),
    yield_risk VARCHAR(20),
    climate_adaptation JSONB,
    soil_adaptation JSONB,
    regional_performance JSONB,
    risk_factors TEXT[],
    mitigation_strategies TEXT[],
    economic_analysis JSONB,
    explanation TEXT,
    key_benefits TEXT[],
    considerations TEXT[],
    supporting_evidence JSONB,
    data_sources TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_crop_varieties_crop_id ON crop_varieties(crop_id);
CREATE INDEX idx_crop_varieties_climate_zones ON crop_varieties USING GIN(climate_zones);
CREATE INDEX idx_crop_varieties_soil_types ON crop_varieties USING GIN(soil_types);
CREATE INDEX idx_crop_varieties_traits ON crop_varieties USING GIN(traits);
CREATE INDEX idx_variety_recommendations_request_id ON variety_recommendations(request_id);
CREATE INDEX idx_variety_recommendations_crop_id ON variety_recommendations(crop_id);
CREATE INDEX idx_variety_recommendations_created_at ON variety_recommendations(created_at);
```

### 2. MongoDB Collections

```javascript
// Variety characteristics collection
db.variety_characteristics.createIndex({ "variety_id": 1 });
db.variety_characteristics.createIndex({ "traits": 1 });
db.variety_characteristics.createIndex({ "performance_metrics": 1 });

// Recommendation explanations collection
db.recommendation_explanations.createIndex({ "request_id": 1 });
db.recommendation_explanations.createIndex({ "variety_id": 1 });
db.recommendation_explanations.createIndex({ "created_at": 1 });

// User preferences collection
db.user_preferences.createIndex({ "user_id": 1 });
db.user_preferences.createIndex({ "farm_id": 1 });
db.user_preferences.createIndex({ "updated_at": 1 });
```

## Data Validation

### 1. Input Validation

```python
from pydantic import validator, root_validator

class FarmData(BaseModel):
    # ... existing fields ...
    
    @validator('ph')
    def validate_ph(cls, v):
        if not 0 <= v <= 14:
            raise ValueError('pH must be between 0 and 14')
        return v
    
    @validator('organic_matter_percent')
    def validate_organic_matter(cls, v):
        if v is not None and not 0 <= v <= 100:
            raise ValueError('Organic matter percentage must be between 0 and 100')
        return v
    
    @root_validator
    def validate_coordinates(cls, values):
        lat = values.get('latitude')
        lng = values.get('longitude')
        
        if lat is not None and lng is not None:
            # Validate coordinate ranges
            if not -90 <= lat <= 90:
                raise ValueError('Latitude must be between -90 and 90')
            if not -180 <= lng <= 180:
                raise ValueError('Longitude must be between -180 and 180')
        
        return values
```

### 2. Business Logic Validation

```python
class VarietyRecommendationEngine:
    def validate_recommendation_request(self, request: VarietyRecommendationRequest) -> bool:
        """Validate recommendation request against business rules."""
        
        # Check crop exists and is active
        crop = self.crop_repository.get_by_id(request.crop_id)
        if not crop or not crop.is_active:
            raise ValueError(f"Crop {request.crop_id} not found or inactive")
        
        # Validate farm data completeness
        if not request.farm_data.latitude or not request.farm_data.longitude:
            raise ValueError("Location coordinates are required")
        
        # Validate soil data
        if not request.farm_data.ph:
            raise ValueError("Soil pH is required")
        
        # Validate field size
        if request.farm_data.field_size_acres <= 0:
            raise ValueError("Field size must be greater than 0")
        
        return True
```

## Data Relationships

### 1. Entity Relationships

```
Crop (1) ──→ (N) CropVariety
CropVariety (1) ──→ (N) VarietyRecommendation
FarmData (1) ──→ (N) VarietyRecommendation
UserPreferences (1) ──→ (N) VarietyRecommendation
```

### 2. Data Dependencies

- **CropVariety** depends on **Crop** for basic crop information
- **VarietyRecommendation** depends on **CropVariety** for variety characteristics
- **VarietyRecommendation** depends on **FarmData** for field conditions
- **VarietyRecommendation** depends on **UserPreferences** for ranking criteria

## Performance Considerations

### 1. Indexing Strategy

- **Primary Keys**: Clustered indexes for fast lookups
- **Foreign Keys**: Non-clustered indexes for joins
- **Array Fields**: GIN indexes for array operations
- **JSON Fields**: GIN indexes for JSON queries
- **Composite Indexes**: For multi-column queries

### 2. Query Optimization

- **Selective Queries**: Use WHERE clauses to limit data
- **Join Optimization**: Use appropriate join types
- **Aggregation**: Use database aggregation functions
- **Caching**: Cache frequently accessed data

### 3. Data Partitioning

- **Time-based Partitioning**: Partition by creation date
- **Geographic Partitioning**: Partition by region
- **Crop-based Partitioning**: Partition by crop type

## Data Migration

### 1. Schema Migrations

```python
# Alembic migration example
def upgrade():
    # Add new columns
    op.add_column('crop_varieties', sa.Column('drought_tolerance', sa.Float()))
    op.add_column('crop_varieties', sa.Column('heat_tolerance', sa.Float()))
    
    # Create new indexes
    op.create_index('idx_varieties_drought_tolerance', 'crop_varieties', ['drought_tolerance'])
    
    # Update existing data
    op.execute("UPDATE crop_varieties SET drought_tolerance = 0.5 WHERE drought_tolerance IS NULL")

def downgrade():
    # Remove indexes
    op.drop_index('idx_varieties_drought_tolerance', 'crop_varieties')
    
    # Remove columns
    op.drop_column('crop_varieties', 'heat_tolerance')
    op.drop_column('crop_varieties', 'drought_tolerance')
```

### 2. Data Transformation

```python
class DataTransformer:
    def transform_legacy_variety_data(self, legacy_data: Dict[str, Any]) -> CropVariety:
        """Transform legacy variety data to new format."""
        
        return CropVariety(
            id=legacy_data['variety_id'],
            crop_id=legacy_data['crop_type'],
            name=legacy_data['variety_name'],
            company=legacy_data.get('company', 'Unknown'),
            maturity_days=legacy_data['maturity_days'],
            yield_potential_min=legacy_data['min_yield'],
            yield_potential_max=legacy_data['max_yield'],
            # Transform other fields as needed
        )
```

## Data Quality

### 1. Data Validation Rules

- **Required Fields**: Ensure all required fields are present
- **Data Types**: Validate data types and formats
- **Ranges**: Validate numeric ranges and constraints
- **Relationships**: Validate foreign key relationships
- **Business Rules**: Validate against business logic

### 2. Data Cleaning

- **Duplicate Detection**: Identify and remove duplicates
- **Outlier Detection**: Identify and handle outliers
- **Missing Data**: Handle missing data appropriately
- **Data Standardization**: Standardize data formats
- **Data Enrichment**: Enhance data with additional sources

### 3. Data Monitoring

- **Data Quality Metrics**: Monitor data quality indicators
- **Data Freshness**: Monitor data update frequency
- **Data Completeness**: Monitor data completeness rates
- **Data Accuracy**: Monitor data accuracy through validation
- **Data Consistency**: Monitor data consistency across sources