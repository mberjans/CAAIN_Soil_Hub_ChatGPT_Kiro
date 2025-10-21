# Parallel Job 1: Crop Type Filtering Enhancement

**TICKET-005: Enhanced Crop Classification and Filtering System**  
**Estimated Timeline**: 3-4 weeks  
**Priority**: High  
**Can Start**: Immediately (No blocking dependencies)

## Executive Summary

This job implements advanced crop filtering capabilities including comprehensive taxonomy, multi-criteria filtering, farmer preference learning, and intelligent result ranking. This work is **completely independent** of other parallel jobs and can proceed without blocking.

## Related Tickets from Checklist

- **TICKET-005_crop-type-filtering-1.1**: Develop comprehensive crop taxonomy ✅ (Validate existing)
- **TICKET-005_crop-type-filtering-1.2**: Extend crop filtering attributes model ✅ (Validate existing)
- **TICKET-005_crop-type-filtering-1.3**: Implement advanced crop attribute tagging system ✅ (Validate existing)
- **TICKET-005_crop-type-filtering-1.4**: Create crop preference profiles system ✅ (Validate existing)
- **TICKET-005_crop-type-filtering-2.1**: Enhance existing crop search service with advanced filtering
- **TICKET-005_crop-type-filtering-2.2**: Implement dynamic filter combination engine
- **TICKET-005_crop-type-filtering-2.3**: Create intelligent filter result ranking and visualization
- **TICKET-005_crop-type-filtering-3.1**: Implement comprehensive farmer preference storage
- **TICKET-005_crop-type-filtering-3.2**: Develop preference learning and adaptation system
- **TICKET-005_crop-type-filtering-3.3**: Create preference-based recommendation enhancement engine
- **TICKET-005_crop-type-filtering-4.1**: Extend existing crop taxonomy API with advanced filtering endpoints

## Technical Stack

```yaml
Languages: Python 3.11+
Framework: FastAPI
Database: PostgreSQL with JSONB, GIN indexes
ORM: SQLAlchemy 2.0+
Validation: Pydantic v2
Testing: pytest, pytest-asyncio, pytest-cov
Caching: Redis (optional for this phase)
```

## Service Architecture

**Service Location**: `services/crop-taxonomy/`  
**Port**: 8007 (new service) or extend existing recommendation-engine  
**Reference Pattern**: Follow `services/recommendation-engine/` structure

```
services/crop-taxonomy/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── models/
│   │   ├── __init__.py
│   │   ├── crop_filtering_models.py
│   │   ├── preference_models.py
│   │   └── taxonomy_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crop_search_service.py
│   │   ├── filter_engine.py
│   │   ├── result_processor.py
│   │   ├── preference_manager.py
│   │   ├── preference_learning.py
│   │   └── crop_attribute_service.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── search_routes.py
│   │   ├── filter_routes.py
│   │   └── preference_routes.py
│   └── schemas/
│       ├── __init__.py
│       ├── search_schemas.py
│       ├── filter_schemas.py
│       └── preference_schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_crop_search.py
│   ├── test_filter_engine.py
│   ├── test_preference_learning.py
│   └── test_api_endpoints.py
├── requirements.txt
└── README.md
```

## Week 1: Foundation & Data Models (Days 1-5)

### Day 1-2: Service Structure Setup

**Step 1: Create Service Directory**
```bash
# Execute from repository root
mkdir -p services/crop-taxonomy/src/{models,services,api,schemas}
mkdir -p services/crop-taxonomy/tests
touch services/crop-taxonomy/src/__init__.py
touch services/crop-taxonomy/src/main.py
touch services/crop-taxonomy/requirements.txt
```

**Step 2: Create requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
```

**Step 3: Install Dependencies**
```bash
cd services/crop-taxonomy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Validation Command**:
```bash
pip list | grep -E "fastapi|sqlalchemy|pydantic"
# Should show all packages installed
```

### Day 2-3: Database Schema Implementation

**File**: `services/crop-taxonomy/src/models/crop_filtering_models.py`

```python
from sqlalchemy import Column, Integer, String, DECIMAL, ARRAY, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Crop(Base):
    """Main crop entity"""
    __tablename__ = 'crops'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    scientific_name = Column(String(150))
    category = Column(String(50))  # grain, vegetable, forage, etc.
    family = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    varieties = relationship("CropVariety", back_populates="crop")
    filtering_attributes = relationship("CropFilteringAttributes", back_populates="crop")

class CropVariety(Base):
    """Crop variety with detailed characteristics"""
    __tablename__ = 'crop_varieties'
    
    id = Column(Integer, primary_key=True)
    crop_id = Column(Integer, ForeignKey('crops.id'), nullable=False)
    variety_name = Column(String(150), nullable=False)
    maturity_days = Column(Integer)
    yield_potential_min = Column(DECIMAL(8, 2))
    yield_potential_max = Column(DECIMAL(8, 2))
    yield_unit = Column(String(20))
    climate_zones = Column(ARRAY(Text))  # Array of compatible zones
    soil_ph_min = Column(DECIMAL(3, 1))
    soil_ph_max = Column(DECIMAL(3, 1))
    soil_types = Column(ARRAY(Text))  # Array of suitable soil types
    disease_resistance = Column(JSONB)  # Flexible disease resistance data
    characteristics = Column(JSONB)  # Additional variety traits
    seed_companies = Column(JSONB)  # Availability information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    crop = relationship("Crop", back_populates="varieties")

class CropFilteringAttributes(Base):
    """Extended filtering attributes for advanced search"""
    __tablename__ = 'crop_filtering_attributes'
    
    id = Column(Integer, primary_key=True)
    crop_id = Column(Integer, ForeignKey('crops.id'), nullable=False)
    variety_id = Column(Integer, ForeignKey('crop_varieties.id'))
    
    # Advanced filtering fields (from TICKET-005_crop-type-filtering-1.2)
    pest_resistance_traits = Column(JSONB)  # {"corn_borer": "high", "aphids": "moderate"}
    market_class_filters = Column(JSONB)  # {"organic_eligible": true, "non_gmo": true}
    certification_filters = Column(JSONB)  # {"usda_organic": true, "non_gmo_project": false}
    seed_availability_filters = Column(JSONB)  # {"availability": "high", "lead_time_days": 14}
    
    # Agricultural characteristics
    drought_tolerance = Column(String(20))  # low, moderate, high
    heat_tolerance = Column(String(20))
    cold_tolerance = Column(String(20))
    management_complexity = Column(String(20))  # low, moderate, high
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    crop = relationship("Crop", back_populates="filtering_attributes")

class CropAttributeTag(Base):
    """Attribute tagging system (TICKET-005_crop-type-filtering-1.3)"""
    __tablename__ = 'crop_attribute_tags'
    
    id = Column(Integer, primary_key=True)
    tag_name = Column(String(100), nullable=False, unique=True)
    tag_category = Column(String(50))  # growth_habit, pest_resistance, market_class, etc.
    parent_tag_id = Column(Integer, ForeignKey('crop_attribute_tags.id'))  # Hierarchical tags
    description = Column(Text)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for hierarchy
    children = relationship("CropAttributeTag", backref="parent", remote_side=[id])

class CropTagAssociation(Base):
    """Many-to-many relationship between crops/varieties and tags"""
    __tablename__ = 'crop_tag_associations'
    
    id = Column(Integer, primary_key=True)
    crop_id = Column(Integer, ForeignKey('crops.id'))
    variety_id = Column(Integer, ForeignKey('crop_varieties.id'))
    tag_id = Column(Integer, ForeignKey('crop_attribute_tags.id'), nullable=False)
    confidence = Column(DECIMAL(3, 2), default=1.0)  # Auto-tagging confidence
    is_manual = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class FarmerCropPreference(Base):
    """Farmer preference profiles (TICKET-005_crop-type-filtering-1.4)"""
    __tablename__ = 'farmer_crop_preferences'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    preference_category = Column(String(50), nullable=False)  # crop_types, management_style, risk_tolerance
    preference_data = Column(JSONB, nullable=False)
    weight = Column(DECIMAL(3, 2), default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

**Database Migration SQL** (save as `migrations/001_crop_filtering_schema.sql`):
```sql
-- Create crops table
CREATE TABLE IF NOT EXISTS crops (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    scientific_name VARCHAR(150),
    category VARCHAR(50),
    family VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create crop_varieties table
CREATE TABLE IF NOT EXISTS crop_varieties (
    id SERIAL PRIMARY KEY,
    crop_id INTEGER REFERENCES crops(id) ON DELETE CASCADE,
    variety_name VARCHAR(150) NOT NULL,
    maturity_days INTEGER,
    yield_potential_min DECIMAL(8,2),
    yield_potential_max DECIMAL(8,2),
    yield_unit VARCHAR(20),
    climate_zones TEXT[],
    soil_ph_min DECIMAL(3,1),
    soil_ph_max DECIMAL(3,1),
    soil_types TEXT[],
    disease_resistance JSONB,
    characteristics JSONB,
    seed_companies JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create crop_filtering_attributes table
CREATE TABLE IF NOT EXISTS crop_filtering_attributes (
    id SERIAL PRIMARY KEY,
    crop_id INTEGER REFERENCES crops(id) ON DELETE CASCADE,
    variety_id INTEGER REFERENCES crop_varieties(id) ON DELETE CASCADE,
    pest_resistance_traits JSONB,
    market_class_filters JSONB,
    certification_filters JSONB,
    seed_availability_filters JSONB,
    drought_tolerance VARCHAR(20),
    heat_tolerance VARCHAR(20),
    cold_tolerance VARCHAR(20),
    management_complexity VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_varieties_crop_id ON crop_varieties(crop_id);
CREATE INDEX idx_varieties_climate_zones ON crop_varieties USING GIN(climate_zones);
CREATE INDEX idx_varieties_soil_types ON crop_varieties USING GIN(soil_types);
CREATE INDEX idx_filtering_crop_id ON crop_filtering_attributes(crop_id);
CREATE INDEX idx_filtering_variety_id ON crop_filtering_attributes(variety_id);

-- GIN indexes for JSONB columns
CREATE INDEX idx_varieties_disease_resistance ON crop_varieties USING GIN(disease_resistance);
CREATE INDEX idx_filtering_pest_resistance ON crop_filtering_attributes USING GIN(pest_resistance_traits);
CREATE INDEX idx_filtering_market_class ON crop_filtering_attributes USING GIN(market_class_filters);

-- Create crop_attribute_tags table
CREATE TABLE IF NOT EXISTS crop_attribute_tags (
    id SERIAL PRIMARY KEY,
    tag_name VARCHAR(100) NOT NULL UNIQUE,
    tag_category VARCHAR(50),
    parent_tag_id INTEGER REFERENCES crop_attribute_tags(id),
    description TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create crop_tag_associations table
CREATE TABLE IF NOT EXISTS crop_tag_associations (
    id SERIAL PRIMARY KEY,
    crop_id INTEGER REFERENCES crops(id) ON DELETE CASCADE,
    variety_id INTEGER REFERENCES crop_varieties(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES crop_attribute_tags(id) ON DELETE CASCADE,
    confidence DECIMAL(3,2) DEFAULT 1.0,
    is_manual BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create farmer_crop_preferences table
CREATE TABLE IF NOT EXISTS farmer_crop_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    preference_category VARCHAR(50) NOT NULL,
    preference_data JSONB NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_preferences_user_id ON farmer_crop_preferences(user_id);
CREATE INDEX idx_preferences_category ON farmer_crop_preferences(preference_category);
```

**Validation Command**:
```bash
# Apply migration (adjust connection string)
psql -U postgres -d caain_soil_hub -f migrations/001_crop_filtering_schema.sql

# Verify tables created
psql -U postgres -d caain_soil_hub -c "\dt crop*"
psql -U postgres -d caain_soil_hub -c "\dt farmer_crop_preferences"
```

### Day 3-4: Pydantic Schemas

**File**: `services/crop-taxonomy/src/schemas/search_schemas.py`

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ToleranceLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class ManagementComplexity(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"

class CropFilterRequest(BaseModel):
    """Advanced multi-criteria filter request"""

    # Climate and location filters
    climate_zones: Optional[List[str]] = Field(None, description="USDA hardiness zones")
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)

    # Soil filters
    soil_ph_range: Optional[Dict[str, float]] = Field(None, description="{'min': 6.0, 'max': 7.5}")
    soil_types: Optional[List[str]] = Field(None, description="clay, loam, sand, etc.")

    # Crop characteristics
    maturity_days_range: Optional[Dict[str, int]] = Field(None, description="{'min': 90, 'max': 120}")
    drought_tolerance: Optional[List[ToleranceLevel]] = None
    heat_tolerance: Optional[List[ToleranceLevel]] = None
    cold_tolerance: Optional[List[ToleranceLevel]] = None

    # Pest and disease
    pest_resistance: Optional[List[str]] = Field(None, description="['corn_borer', 'aphids']")
    disease_resistance: Optional[List[str]] = Field(None, description="['rust', 'blight']")

    # Market and certification
    market_class: Optional[List[str]] = Field(None, description="['organic_eligible', 'non_gmo']")
    certifications: Optional[List[str]] = Field(None, description="['usda_organic', 'non_gmo_project']")

    # Management
    management_complexity: Optional[List[ManagementComplexity]] = None

    # User preferences
    user_preferences: Optional[Dict[str, Any]] = Field(None, description="User preference overrides")

    # Pagination and sorting
    sort_by: str = Field("suitability_score", description="Field to sort by")
    limit: int = Field(50, ge=1, le=500)
    offset: int = Field(0, ge=0)

    @validator('soil_ph_range')
    def validate_ph_range(cls, v):
        if v and ('min' in v and 'max' in v):
            if v['min'] > v['max']:
                raise ValueError('min pH must be less than max pH')
            if not (0 <= v['min'] <= 14 and 0 <= v['max'] <= 14):
                raise ValueError('pH values must be between 0 and 14')
        return v

class CropVarietyResponse(BaseModel):
    """Crop variety response with filtering metadata"""

    id: int
    crop_id: int
    crop_name: str
    variety_name: str
    maturity_days: Optional[int]
    yield_potential_min: Optional[float]
    yield_potential_max: Optional[float]
    yield_unit: Optional[str]
    climate_zones: List[str]
    soil_ph_min: Optional[float]
    soil_ph_max: Optional[float]
    soil_types: List[str]

    # Filtering attributes
    drought_tolerance: Optional[str]
    heat_tolerance: Optional[str]
    pest_resistance_traits: Optional[Dict[str, str]]
    market_class_filters: Optional[Dict[str, bool]]

    # Scoring
    suitability_score: float = Field(..., description="Overall suitability score 0-1")
    confidence: float = Field(..., description="Recommendation confidence 0-1")

    # Metadata
    match_reasons: List[str] = Field(default_factory=list, description="Why this variety matched")
    warnings: List[str] = Field(default_factory=list, description="Potential concerns")

    class Config:
        from_attributes = True

class CropSearchResponse(BaseModel):
    """Search response with metadata"""

    total_results: int
    returned_results: int
    filters_applied: Dict[str, Any]
    varieties: List[CropVarietyResponse]
    processing_time_ms: float
    suggestions: Optional[List[str]] = Field(None, description="Alternative search suggestions")
```

**File**: `services/crop-taxonomy/src/schemas/preference_schemas.py`

```python
from pydantic import BaseModel, Field, UUID4
from typing import Dict, Any, Optional, List
from datetime import datetime

class PreferenceCreate(BaseModel):
    """Create farmer preference"""

    user_id: UUID4
    preference_category: str = Field(..., description="crop_types, management_style, risk_tolerance, market_focus")
    preference_data: Dict[str, Any] = Field(..., description="Flexible preference data")
    weight: float = Field(1.0, ge=0.0, le=1.0, description="Preference weight")

class PreferenceUpdate(BaseModel):
    """Update farmer preference"""

    preference_data: Optional[Dict[str, Any]] = None
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)

class PreferenceResponse(BaseModel):
    """Farmer preference response"""

    id: UUID4
    user_id: UUID4
    preference_category: str
    preference_data: Dict[str, Any]
    weight: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PreferenceLearningRequest(BaseModel):
    """Request to learn from user selections"""

    user_id: UUID4
    selected_varieties: List[int] = Field(..., description="Variety IDs user selected")
    rejected_varieties: Optional[List[int]] = Field(None, description="Variety IDs user rejected")
    context: Optional[Dict[str, Any]] = Field(None, description="Selection context")

class PreferenceLearningResponse(BaseModel):
    """Response from preference learning"""

    preferences_updated: int
    new_preferences_created: int
    confidence_improvements: Dict[str, float]
    learned_patterns: List[str]
```

**Validation Command**:
```bash
# Test schema imports
cd services/crop-taxonomy
python -c "from src.schemas.search_schemas import CropFilterRequest, CropSearchResponse; print('Schemas OK')"
python -c "from src.schemas.preference_schemas import PreferenceCreate; print('Preference schemas OK')"
```

## Week 2: Core Services Implementation (Days 6-10)

### Day 6-7: Crop Search Service

**File**: `services/crop-taxonomy/src/services/crop_search_service.py`

```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Any, Optional
import time
from ..models.crop_filtering_models import Crop, CropVariety, CropFilteringAttributes
from ..schemas.search_schemas import CropFilterRequest, CropVarietyResponse, CropSearchResponse

class CropSearchService:
    """Enhanced crop search with advanced filtering (TICKET-005_crop-type-filtering-2.1)"""

    def __init__(self, db: Session):
        self.db = db

    async def search_varieties(self, filter_request: CropFilterRequest) -> CropSearchResponse:
        """
        Multi-criteria crop variety search with intelligent filtering

        Performance requirement: <2s for complex queries
        """
        start_time = time.time()

        # Build base query
        query = self.db.query(CropVariety, Crop, CropFilteringAttributes).join(
            Crop, CropVariety.crop_id == Crop.id
        ).outerjoin(
            CropFilteringAttributes, CropVariety.id == CropFilteringAttributes.variety_id
        )

        # Apply filters
        query = self._apply_climate_filters(query, filter_request)
        query = self._apply_soil_filters(query, filter_request)
        query = self._apply_characteristic_filters(query, filter_request)
        query = self._apply_pest_disease_filters(query, filter_request)
        query = self._apply_market_filters(query, filter_request)

        # Get total count before pagination
        total_count = query.count()

        # Apply pagination
        query = query.offset(filter_request.offset).limit(filter_request.limit)

        # Execute query
        results = query.all()

        # Score and rank results
        scored_varieties = []
        for variety, crop, filtering_attrs in results:
            score = self._calculate_suitability_score(variety, crop, filtering_attrs, filter_request)
            variety_response = self._build_variety_response(variety, crop, filtering_attrs, score)
            scored_varieties.append(variety_response)

        # Sort by score
        scored_varieties.sort(key=lambda x: x.suitability_score, reverse=True)

        processing_time = (time.time() - start_time) * 1000

        return CropSearchResponse(
            total_results=total_count,
            returned_results=len(scored_varieties),
            filters_applied=filter_request.dict(exclude_none=True),
            varieties=scored_varieties,
            processing_time_ms=processing_time,
            suggestions=self._generate_suggestions(scored_varieties, filter_request) if len(scored_varieties) == 0 else None
        )

    def _apply_climate_filters(self, query, filter_request: CropFilterRequest):
        """Apply climate zone filters"""
        if filter_request.climate_zones:
            # Use PostgreSQL array overlap operator
            query = query.filter(CropVariety.climate_zones.overlap(filter_request.climate_zones))
        return query

    def _apply_soil_filters(self, query, filter_request: CropFilterRequest):
        """Apply soil-related filters"""
        if filter_request.soil_ph_range:
            min_ph = filter_request.soil_ph_range.get('min')
            max_ph = filter_request.soil_ph_range.get('max')
            if min_ph is not None and max_ph is not None:
                query = query.filter(
                    and_(
                        CropVariety.soil_ph_min <= max_ph,
                        CropVariety.soil_ph_max >= min_ph
                    )
                )

        if filter_request.soil_types:
            query = query.filter(CropVariety.soil_types.overlap(filter_request.soil_types))

        return query

    def _apply_characteristic_filters(self, query, filter_request: CropFilterRequest):
        """Apply crop characteristic filters"""
        if filter_request.maturity_days_range:
            min_days = filter_request.maturity_days_range.get('min')
            max_days = filter_request.maturity_days_range.get('max')
            if min_days is not None:
                query = query.filter(CropVariety.maturity_days >= min_days)
            if max_days is not None:
                query = query.filter(CropVariety.maturity_days <= max_days)

        if filter_request.drought_tolerance:
            tolerance_values = [t.value for t in filter_request.drought_tolerance]
            query = query.filter(CropFilteringAttributes.drought_tolerance.in_(tolerance_values))

        if filter_request.management_complexity:
            complexity_values = [c.value for c in filter_request.management_complexity]
            query = query.filter(CropFilteringAttributes.management_complexity.in_(complexity_values))

        return query

    def _apply_pest_disease_filters(self, query, filter_request: CropFilterRequest):
        """Apply pest and disease resistance filters"""
        if filter_request.pest_resistance:
            # JSONB query for pest resistance
            for pest in filter_request.pest_resistance:
                query = query.filter(
                    CropFilteringAttributes.pest_resistance_traits[pest].astext.in_(['moderate', 'high'])
                )

        if filter_request.disease_resistance:
            # JSONB query for disease resistance
            for disease in filter_request.disease_resistance:
                query = query.filter(
                    CropVariety.disease_resistance[disease].astext.in_(['moderate', 'high'])
                )

        return query

    def _apply_market_filters(self, query, filter_request: CropFilterRequest):
        """Apply market class and certification filters"""
        if filter_request.market_class:
            for market_attr in filter_request.market_class:
                query = query.filter(
                    CropFilteringAttributes.market_class_filters[market_attr].astext == 'true'
                )

        if filter_request.certifications:
            for cert in filter_request.certifications:
                query = query.filter(
                    CropFilteringAttributes.certification_filters[cert].astext == 'true'
                )

        return query

    def _calculate_suitability_score(
        self,
        variety: CropVariety,
        crop: Crop,
        filtering_attrs: Optional[CropFilteringAttributes],
        filter_request: CropFilterRequest
    ) -> float:
        """
        Calculate suitability score based on how well variety matches filters
        Score range: 0.0 to 1.0
        """
        score = 0.5  # Base score
        max_bonus = 0.5

        # Climate zone match (20% weight)
        if filter_request.climate_zones and variety.climate_zones:
            overlap = set(filter_request.climate_zones) & set(variety.climate_zones)
            if overlap:
                score += 0.2 * (len(overlap) / len(filter_request.climate_zones))

        # Soil pH match (15% weight)
        if filter_request.soil_ph_range and variety.soil_ph_min and variety.soil_ph_max:
            requested_min = filter_request.soil_ph_range.get('min', 0)
            requested_max = filter_request.soil_ph_range.get('max', 14)
            overlap_range = min(variety.soil_ph_max, requested_max) - max(variety.soil_ph_min, requested_min)
            if overlap_range > 0:
                score += 0.15 * min(overlap_range / 2.0, 1.0)  # Normalize to 2 pH units

        # Tolerance characteristics (15% weight)
        if filtering_attrs:
            tolerance_matches = 0
            tolerance_checks = 0

            if filter_request.drought_tolerance and filtering_attrs.drought_tolerance:
                tolerance_checks += 1
                if filtering_attrs.drought_tolerance in [t.value for t in filter_request.drought_tolerance]:
                    tolerance_matches += 1

            if tolerance_checks > 0:
                score += 0.15 * (tolerance_matches / tolerance_checks)

        return min(score, 1.0)

    def _build_variety_response(
        self,
        variety: CropVariety,
        crop: Crop,
        filtering_attrs: Optional[CropFilteringAttributes],
        score: float
    ) -> CropVarietyResponse:
        """Build variety response with all metadata"""

        match_reasons = []
        warnings = []

        # TODO: Add logic to populate match_reasons and warnings

        return CropVarietyResponse(
            id=variety.id,
            crop_id=variety.crop_id,
            crop_name=crop.name,
            variety_name=variety.variety_name,
            maturity_days=variety.maturity_days,
            yield_potential_min=variety.yield_potential_min,
            yield_potential_max=variety.yield_potential_max,
            yield_unit=variety.yield_unit,
            climate_zones=variety.climate_zones or [],
            soil_ph_min=variety.soil_ph_min,
            soil_ph_max=variety.soil_ph_max,
            soil_types=variety.soil_types or [],
            drought_tolerance=filtering_attrs.drought_tolerance if filtering_attrs else None,
            heat_tolerance=filtering_attrs.heat_tolerance if filtering_attrs else None,
            pest_resistance_traits=filtering_attrs.pest_resistance_traits if filtering_attrs else None,
            market_class_filters=filtering_attrs.market_class_filters if filtering_attrs else None,
            suitability_score=score,
            confidence=0.8,  # TODO: Calculate actual confidence
            match_reasons=match_reasons,
            warnings=warnings
        )

    def _generate_suggestions(self, results: List[CropVarietyResponse], filter_request: CropFilterRequest) -> List[str]:
        """Generate alternative search suggestions when no results found"""
        suggestions = []

        if not results:
            suggestions.append("Try expanding your climate zone range")
            suggestions.append("Consider relaxing soil pH requirements")
            suggestions.append("Remove some pest resistance filters")

        return suggestions
```

**Validation Command**:
```bash
python -c "from src.services.crop_search_service import CropSearchService; print('CropSearchService OK')"
```

### Day 8-9: Filter Engine and Preference Services

**File**: `services/crop-taxonomy/src/services/filter_engine.py`

```python
from typing import List, Dict, Any, Set
from ..schemas.search_schemas import CropFilterRequest

class FilterCombinationEngine:
    """Dynamic filter combination engine (TICKET-005_crop-type-filtering-2.2)"""

    def __init__(self):
        self.filter_dependencies = self._build_filter_dependencies()
        self.filter_presets = self._build_filter_presets()

    def suggest_filters(self, current_filters: CropFilterRequest, location: Dict[str, float] = None) -> List[Dict[str, Any]]:
        """Suggest additional filters based on current selection and location"""
        suggestions = []

        # Location-based suggestions
        if location and 'latitude' in location:
            climate_suggestion = self._suggest_climate_filters(location['latitude'], location['longitude'])
            if climate_suggestion:
                suggestions.append(climate_suggestion)

        # Dependency-based suggestions
        if current_filters.drought_tolerance:
            suggestions.append({
                "filter": "soil_types",
                "values": ["sandy_loam", "loam"],
                "reason": "Sandy soils complement drought-tolerant varieties"
            })

        return suggestions

    def detect_conflicts(self, filter_request: CropFilterRequest) -> List[Dict[str, str]]:
        """Detect contradictory filter combinations"""
        conflicts = []

        # Check pH vs crop type conflicts
        if filter_request.soil_ph_range:
            min_ph = filter_request.soil_ph_range.get('min', 0)
            max_ph = filter_request.soil_ph_range.get('max', 14)

            if min_ph > 7.5 and filter_request.market_class and 'organic_eligible' in filter_request.market_class:
                conflicts.append({
                    "conflict": "High pH may limit organic amendment options",
                    "severity": "warning"
                })

        return conflicts

    def apply_preset(self, preset_name: str) -> CropFilterRequest:
        """Apply predefined filter preset"""
        if preset_name in self.filter_presets:
            return CropFilterRequest(**self.filter_presets[preset_name])
        raise ValueError(f"Unknown preset: {preset_name}")

    def _build_filter_dependencies(self) -> Dict[str, List[str]]:
        """Define filter dependencies"""
        return {
            "drought_tolerance": ["soil_types", "climate_zones"],
            "organic_eligible": ["pest_resistance", "disease_resistance"],
            "high_yield": ["management_complexity", "soil_ph_range"]
        }

    def _build_filter_presets(self) -> Dict[str, Dict[str, Any]]:
        """Define common filter presets"""
        return {
            "organic_farming": {
                "market_class": ["organic_eligible", "non_gmo"],
                "pest_resistance": ["moderate", "high"],
                "management_complexity": ["moderate", "high"]
            },
            "drought_prone": {
                "drought_tolerance": ["moderate", "high"],
                "soil_types": ["sandy_loam", "loam"],
                "management_complexity": ["low", "moderate"]
            },
            "high_value_crops": {
                "market_class": ["specialty", "organic_eligible"],
                "management_complexity": ["moderate", "high"]
            }
        }

    def _suggest_climate_filters(self, lat: float, lng: float) -> Dict[str, Any]:
        """Suggest climate filters based on location"""
        # Simplified climate zone suggestion
        if 40 <= lat <= 45:
            return {
                "filter": "climate_zones",
                "values": ["5a", "5b", "6a", "6b"],
                "reason": "Typical zones for your latitude"
            }
        return None
```

**File**: `services/crop-taxonomy/src/services/preference_manager.py`

```python
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from uuid import UUID
from ..models.crop_filtering_models import FarmerCropPreference
from ..schemas.preference_schemas import PreferenceCreate, PreferenceUpdate, PreferenceResponse

class FarmerPreferenceManager:
    """Comprehensive farmer preference storage (TICKET-005_crop-type-filtering-3.1)"""

    def __init__(self, db: Session):
        self.db = db

    async def create_preference(self, preference: PreferenceCreate) -> PreferenceResponse:
        """Create new farmer preference"""
        db_preference = FarmerCropPreference(
            user_id=preference.user_id,
            preference_category=preference.preference_category,
            preference_data=preference.preference_data,
            weight=preference.weight
        )
        self.db.add(db_preference)
        self.db.commit()
        self.db.refresh(db_preference)
        return PreferenceResponse.from_orm(db_preference)

    async def get_user_preferences(self, user_id: UUID) -> List[PreferenceResponse]:
        """Get all preferences for a user"""
        preferences = self.db.query(FarmerCropPreference).filter(
            FarmerCropPreference.user_id == user_id
        ).all()
        return [PreferenceResponse.from_orm(p) for p in preferences]

    async def update_preference(self, preference_id: UUID, update: PreferenceUpdate) -> PreferenceResponse:
        """Update existing preference"""
        db_preference = self.db.query(FarmerCropPreference).filter(
            FarmerCropPreference.id == preference_id
        ).first()

        if not db_preference:
            raise ValueError(f"Preference {preference_id} not found")

        if update.preference_data is not None:
            db_preference.preference_data = update.preference_data
        if update.weight is not None:
            db_preference.weight = update.weight

        self.db.commit()
        self.db.refresh(db_preference)
        return PreferenceResponse.from_orm(db_preference)

    async def delete_preference(self, preference_id: UUID) -> bool:
        """Delete preference"""
        result = self.db.query(FarmerCropPreference).filter(
            FarmerCropPreference.id == preference_id
        ).delete()
        self.db.commit()
        return result > 0
```

## Week 3: API Implementation & Testing (Days 11-15)

### Day 11-12: API Endpoints

**File**: `services/crop-taxonomy/src/api/search_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..schemas.search_schemas import CropFilterRequest, CropSearchResponse
from ..services.crop_search_service import CropSearchService
from ..services.filter_engine import FilterCombinationEngine

router = APIRouter(prefix="/api/v1/crop-taxonomy", tags=["crop-search"])

# Dependency to get database session
def get_db():
    # TODO: Implement database session dependency
    pass

@router.post("/search", response_model=CropSearchResponse)
async def search_crops(
    filter_request: CropFilterRequest,
    db: Session = Depends(get_db)
):
    """
    Advanced multi-criteria crop variety search

    **Performance**: <2s response time for complex queries
    **Supports**: 10,000+ crop varieties

    Example request:
    ```json
    {
      "climate_zones": ["5a", "5b", "6a"],
      "soil_ph_range": {"min": 6.0, "max": 7.5},
      "drought_tolerance": ["moderate", "high"],
      "market_class": ["organic_eligible"],
      "limit": 50
    }
    ```
    """
    try:
        service = CropSearchService(db)
        results = await service.search_varieties(filter_request)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/filter-options")
async def get_filter_options(
    latitude: Optional[float] = Query(None, ge=-90, le=90),
    longitude: Optional[float] = Query(None, ge=-180, le=180),
    db: Session = Depends(get_db)
):
    """
    Get available filter options based on location

    Returns dynamic filter values with counts
    """
    # TODO: Implement filter options retrieval
    return {
        "climate_zones": ["5a", "5b", "6a", "6b"],
        "soil_types": ["clay", "loam", "sandy_loam", "sand"],
        "drought_tolerance": ["low", "moderate", "high"]
    }

@router.post("/filter-suggestions")
async def get_filter_suggestions(
    current_filters: CropFilterRequest,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
):
    """Get intelligent filter suggestions"""
    engine = FilterCombinationEngine()
    location = {"latitude": latitude, "longitude": longitude} if latitude and longitude else None
    suggestions = engine.suggest_filters(current_filters, location)
    return {"suggestions": suggestions}

@router.post("/filter-conflicts")
async def detect_filter_conflicts(filter_request: CropFilterRequest):
    """Detect contradictory filter combinations"""
    engine = FilterCombinationEngine()
    conflicts = engine.detect_conflicts(filter_request)
    return {"conflicts": conflicts}
```

### Day 13-14: Unit Tests

**File**: `services/crop-taxonomy/tests/test_crop_search.py`

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.crop_filtering_models import Base, Crop, CropVariety, CropFilteringAttributes
from src.services.crop_search_service import CropSearchService
from src.schemas.search_schemas import CropFilterRequest

# Test database setup
TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost/test_crop_taxonomy"

@pytest.fixture(scope="function")
def db_session():
    """Create test database session"""
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_crops(db_session):
    """Create sample crop data"""
    # Create corn crop
    corn = Crop(name="Corn", scientific_name="Zea mays", category="grain", family="Poaceae")
    db_session.add(corn)
    db_session.commit()

    # Create corn variety
    variety = CropVariety(
        crop_id=corn.id,
        variety_name="Pioneer 1234",
        maturity_days=110,
        yield_potential_min=180.0,
        yield_potential_max=220.0,
        yield_unit="bu/acre",
        climate_zones=["5a", "5b", "6a"],
        soil_ph_min=6.0,
        soil_ph_max=7.5,
        soil_types=["loam", "clay_loam"]
    )
    db_session.add(variety)
    db_session.commit()

    # Create filtering attributes
    attrs = CropFilteringAttributes(
        crop_id=corn.id,
        variety_id=variety.id,
        drought_tolerance="moderate",
        heat_tolerance="high",
        management_complexity="moderate",
        pest_resistance_traits={"corn_borer": "high", "aphids": "moderate"},
        market_class_filters={"organic_eligible": True, "non_gmo": True}
    )
    db_session.add(attrs)
    db_session.commit()

    return {"crop": corn, "variety": variety, "attrs": attrs}

@pytest.mark.asyncio
async def test_basic_search(db_session, sample_crops):
    """Test basic crop search"""
    service = CropSearchService(db_session)

    filter_request = CropFilterRequest(
        climate_zones=["5a", "6a"],
        limit=10
    )

    result = await service.search_varieties(filter_request)

    assert result.total_results >= 1
    assert len(result.varieties) >= 1
    assert result.varieties[0].crop_name == "Corn"

@pytest.mark.asyncio
async def test_ph_range_filter(db_session, sample_crops):
    """Test soil pH range filtering"""
    service = CropSearchService(db_session)

    filter_request = CropFilterRequest(
        soil_ph_range={"min": 6.5, "max": 7.0},
        limit=10
    )

    result = await service.search_varieties(filter_request)

    assert result.total_results >= 1
    for variety in result.varieties:
        assert variety.soil_ph_min <= 7.0
        assert variety.soil_ph_max >= 6.5

@pytest.mark.asyncio
async def test_performance_requirement(db_session, sample_crops):
    """Test that search completes in <2 seconds"""
    service = CropSearchService(db_session)

    filter_request = CropFilterRequest(
        climate_zones=["5a", "5b", "6a"],
        soil_ph_range={"min": 6.0, "max": 7.5},
        drought_tolerance=["moderate", "high"],
        limit=50
    )

    result = await service.search_varieties(filter_request)

    assert result.processing_time_ms < 2000, f"Search took {result.processing_time_ms}ms, exceeds 2s requirement"

@pytest.mark.asyncio
async def test_suitability_scoring(db_session, sample_crops):
    """Test suitability score calculation"""
    service = CropSearchService(db_session)

    filter_request = CropFilterRequest(
        climate_zones=["5a"],
        soil_ph_range={"min": 6.0, "max": 7.0},
        limit=10
    )

    result = await service.search_varieties(filter_request)

    assert len(result.varieties) > 0
    for variety in result.varieties:
        assert 0.0 <= variety.suitability_score <= 1.0
        assert 0.0 <= variety.confidence <= 1.0
```

**Validation Command**:
```bash
cd services/crop-taxonomy
pytest tests/test_crop_search.py -v --cov=src/services/crop_search_service
```

## Week 4: Integration & Documentation (Days 16-20)

### Day 16-17: FastAPI Application Setup

**File**: `services/crop-taxonomy/src/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import search_routes, preference_routes

app = FastAPI(
    title="CAAIN Crop Taxonomy Service",
    description="Advanced crop filtering and preference management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search_routes.router)
# app.include_router(preference_routes.router)  # TODO: Implement

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "crop-taxonomy"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CAAIN Crop Taxonomy Service",
        "version": "1.0.0",
        "docs": "/docs"
    }
```

**Start Service**:
```bash
cd services/crop-taxonomy
uvicorn src.main:app --reload --port 8007
```

**Validation**:
```bash
curl http://localhost:8007/health
curl http://localhost:8007/docs  # Open in browser
```

### Day 18-19: Integration Testing

**File**: `services/crop-taxonomy/tests/test_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_health_endpoint():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_search_endpoint():
    """Test search API endpoint"""
    request_data = {
        "climate_zones": ["5a", "6a"],
        "soil_ph_range": {"min": 6.0, "max": 7.5},
        "limit": 10
    }

    response = client.post("/api/v1/crop-taxonomy/search", json=request_data)
    assert response.status_code == 200

    data = response.json()
    assert "total_results" in data
    assert "varieties" in data
    assert "processing_time_ms" in data

def test_filter_suggestions():
    """Test filter suggestions endpoint"""
    request_data = {
        "climate_zones": ["5a"],
        "limit": 10
    }

    response = client.post(
        "/api/v1/crop-taxonomy/filter-suggestions",
        json=request_data,
        params={"latitude": 41.8781, "longitude": -87.6298}
    )
    assert response.status_code == 200
    assert "suggestions" in response.json()
```

## Definition of Done

### Functional Requirements
- [ ] All database tables created and indexed
- [ ] CropSearchService implements multi-criteria filtering
- [ ] FilterCombinationEngine provides intelligent suggestions
- [ ] FarmerPreferenceManager handles CRUD operations
- [ ] All API endpoints return correct responses
- [ ] Performance requirement met: <2s for complex queries

### Testing Requirements
- [ ] Unit test coverage >80%
- [ ] All integration tests passing
- [ ] Performance tests validate <2s requirement
- [ ] Agricultural validation: Test with real crop data

### Documentation
- [ ] API documentation in /docs endpoint
- [ ] README with setup instructions
- [ ] Code comments for complex algorithms

### Integration Points
- [ ] Mock climate zone service for testing
- [ ] Mock user management service for preferences
- [ ] Document API contracts for integration phase

## Agricultural Expert Review Checkpoints

**Flag for Human Review**:
1. Suitability scoring algorithm accuracy
2. Filter conflict detection logic
3. Crop characteristic data validation
4. Preference learning patterns

## Common Pitfalls

1. **JSONB Query Performance**: Ensure GIN indexes on all JSONB columns
2. **Array Overlap Queries**: Use PostgreSQL array operators correctly
3. **Scoring Algorithm**: Validate weights sum to reasonable values
4. **Null Handling**: Handle missing filtering attributes gracefully

## Next Steps for Integration

This service will integrate with:
- **Climate Zone Service** (Job 5): For location-based filtering
- **User Management**: For preference storage
- **Recommendation Engine**: For enhanced crop recommendations

Mock these services during development using the patterns in `tests/test_integration.py`.

