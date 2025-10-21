# Job 1: Crop Filtering Enhancement - Development Tickets

**Total Tickets**: 15  
**Estimated Timeline**: 4 weeks  
**Service**: Crop Taxonomy Service (Port 8007)  
**Related Plan**: `docs/parallel-job-1-crop-filtering.md`

---

## JOB1-001: Setup Crop Filtering Service Directory Structure

**Priority**: Critical  
**Estimated Effort**: 1 hour  
**Dependencies**: None (Can start immediately)  
**Blocks**: JOB1-002, JOB1-003, JOB1-004, JOB1-005  
**Parallel Execution**: No (must complete first)

**Description**:
Create the complete directory structure for the crop filtering service following the microservices architecture pattern used in existing services.

**Acceptance Criteria**:
- [ ] All directories created under `services/crop-taxonomy/`
- [ ] All `__init__.py` files present in Python packages
- [ ] Virtual environment created and activated
- [ ] requirements.txt file created with all dependencies
- [ ] All dependencies installed successfully

**Technical Details**:

Directory structure to create:
```
services/crop-taxonomy/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── crop_models.py
│   │   └── filtering_models.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crop_search_service.py
│   │   ├── filter_engine.py
│   │   └── preference_manager.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── crop_routes.py
│   └── schemas/
│       ├── __init__.py
│       └── crop_schemas.py
├── tests/
│   ├── __init__.py
│   ├── test_crop_search.py
│   ├── test_filter_engine.py
│   └── test_api.py
├── requirements.txt
└── README.md
```

**Validation Commands**:
```bash
cd /Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro

# Create directory structure
mkdir -p services/crop-taxonomy/src/{models,services,api,schemas}
mkdir -p services/crop-taxonomy/tests

# Create __init__.py files
touch services/crop-taxonomy/src/__init__.py
touch services/crop-taxonomy/src/models/__init__.py
touch services/crop-taxonomy/src/services/__init__.py
touch services/crop-taxonomy/src/api/__init__.py
touch services/crop-taxonomy/src/schemas/__init__.py
touch services/crop-taxonomy/tests/__init__.py

# Verify structure
ls -la services/crop-taxonomy/src/
ls -la services/crop-taxonomy/src/models/
ls -la services/crop-taxonomy/src/services/
ls -la services/crop-taxonomy/src/api/
ls -la services/crop-taxonomy/src/schemas/

# Create and activate virtual environment
cd services/crop-taxonomy
python3 -m venv venv
source venv/bin/activate

# Verify Python environment
python --version
which python
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-1.1

---

## JOB1-002: Create Requirements File and Install Dependencies

**Priority**: Critical  
**Estimated Effort**: 30 minutes  
**Dependencies**: JOB1-001  
**Blocks**: JOB1-003, JOB1-004, JOB1-005  
**Parallel Execution**: No

**Description**:
Create requirements.txt with all necessary dependencies for the crop filtering service and install them in the virtual environment.

**Acceptance Criteria**:
- [ ] requirements.txt file created with correct versions
- [ ] All dependencies installed without errors
- [ ] Can import all major libraries (FastAPI, SQLAlchemy, Pydantic)
- [ ] Virtual environment activated

**Technical Details**:

Create `services/crop-taxonomy/requirements.txt`:
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.1
python-multipart==0.0.6
```

**Validation Commands**:
```bash
cd services/crop-taxonomy
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installations
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"
python -c "import pytest; print(f'Pytest: {pytest.__version__}')"

# List installed packages
pip list
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-1.1

---

## JOB1-003: Create Database Schema for Crop Filtering Attributes

**Priority**: Critical  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB1-002  
**Blocks**: JOB1-006, JOB1-007  
**Parallel Execution**: Can run parallel with JOB1-004, JOB1-005

**Description**:
Create SQLAlchemy models for crop filtering attributes including pest resistance, market classes, certifications, and seed availability. Set up database tables with proper indexes.

**Acceptance Criteria**:
- [ ] `crop_filtering_attributes` table created
- [ ] `farmer_preferences` table created
- [ ] `filter_combinations` table created
- [ ] All JSONB columns have GIN indexes
- [ ] Foreign key relationships established
- [ ] Sample data inserted for testing

**Technical Details**:

Create `services/crop-taxonomy/src/models/filtering_models.py`:
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class CropFilteringAttributes(Base):
    """Extended filtering attributes for crop varieties"""
    __tablename__ = 'crop_filtering_attributes'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    variety_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    
    # Pest and disease resistance (JSONB for flexibility)
    pest_resistance_traits = Column(JSONB, default={})
    disease_resistance_traits = Column(JSONB, default={})
    
    # Market and certification filters
    market_class_filters = Column(JSONB, default={})
    certification_filters = Column(JSONB, default={})
    
    # Seed availability
    seed_availability_filters = Column(JSONB, default={})
    
    # Performance metrics
    yield_stability_score = Column(Integer)
    drought_tolerance_score = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for JSONB queries
    __table_args__ = (
        Index('idx_pest_resistance_gin', 'pest_resistance_traits', postgresql_using='gin'),
        Index('idx_disease_resistance_gin', 'disease_resistance_traits', postgresql_using='gin'),
        Index('idx_market_class_gin', 'market_class_filters', postgresql_using='gin'),
        Index('idx_certification_gin', 'certification_filters', postgresql_using='gin'),
    )

class FarmerPreference(Base):
    """Farmer filtering preferences and history"""
    __tablename__ = 'farmer_preferences'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Preference data
    preferred_filters = Column(JSONB, default={})
    filter_weights = Column(JSONB, default={})
    
    # Learning data
    selected_varieties = Column(JSONB, default=[])
    rejected_varieties = Column(JSONB, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_farmer_pref_user', 'user_id'),
        Index('idx_preferred_filters_gin', 'preferred_filters', postgresql_using='gin'),
    )

class FilterCombination(Base):
    """Popular filter combinations for optimization"""
    __tablename__ = 'filter_combinations'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    combination_hash = Column(String(64), unique=True, nullable=False)
    filters = Column(JSONB, nullable=False)
    usage_count = Column(Integer, default=1)
    avg_result_count = Column(Integer)
    avg_response_time_ms = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_filter_combo_hash', 'combination_hash'),
        Index('idx_filter_combo_usage', 'usage_count'),
    )
```

Create migration SQL file `services/crop-taxonomy/migrations/001_filtering_schema.sql`:
```sql
-- Create crop_filtering_attributes table
CREATE TABLE IF NOT EXISTS crop_filtering_attributes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variety_id UUID NOT NULL UNIQUE,
    pest_resistance_traits JSONB DEFAULT '{}',
    disease_resistance_traits JSONB DEFAULT '{}',
    market_class_filters JSONB DEFAULT '{}',
    certification_filters JSONB DEFAULT '{}',
    seed_availability_filters JSONB DEFAULT '{}',
    yield_stability_score INTEGER,
    drought_tolerance_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_pest_resistance_gin ON crop_filtering_attributes USING GIN(pest_resistance_traits);
CREATE INDEX IF NOT EXISTS idx_disease_resistance_gin ON crop_filtering_attributes USING GIN(disease_resistance_traits);
CREATE INDEX IF NOT EXISTS idx_market_class_gin ON crop_filtering_attributes USING GIN(market_class_filters);
CREATE INDEX IF NOT EXISTS idx_certification_gin ON crop_filtering_attributes USING GIN(certification_filters);

-- Create farmer_preferences table
CREATE TABLE IF NOT EXISTS farmer_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    preferred_filters JSONB DEFAULT '{}',
    filter_weights JSONB DEFAULT '{}',
    selected_varieties JSONB DEFAULT '[]',
    rejected_varieties JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_farmer_pref_user ON farmer_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_preferred_filters_gin ON farmer_preferences USING GIN(preferred_filters);

-- Create filter_combinations table
CREATE TABLE IF NOT EXISTS filter_combinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    combination_hash VARCHAR(64) UNIQUE NOT NULL,
    filters JSONB NOT NULL,
    usage_count INTEGER DEFAULT 1,
    avg_result_count INTEGER,
    avg_response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_filter_combo_hash ON filter_combinations(combination_hash);
CREATE INDEX IF NOT EXISTS idx_filter_combo_usage ON filter_combinations(usage_count);

-- Insert sample data
INSERT INTO crop_filtering_attributes (variety_id, pest_resistance_traits, disease_resistance_traits, market_class_filters, yield_stability_score, drought_tolerance_score)
VALUES 
    (gen_random_uuid(), 
     '{"corn_borer": "resistant", "rootworm": "moderate"}',
     '{"gray_leaf_spot": "resistant", "northern_leaf_blight": "moderate"}',
     '{"market_class": "yellow_dent", "organic_certified": true}',
     85, 75),
    (gen_random_uuid(),
     '{"aphids": "resistant", "corn_earworm": "susceptible"}',
     '{"rust": "resistant", "smut": "resistant"}',
     '{"market_class": "white_corn", "non_gmo": true}',
     90, 80)
ON CONFLICT (variety_id) DO NOTHING;
```

**Validation Commands**:
```bash
cd services/crop-taxonomy

# Run migration
psql -U postgres -d caain_soil_hub -f migrations/001_filtering_schema.sql

# Verify tables created
psql -U postgres -d caain_soil_hub -c "\dt crop_filtering_attributes"
psql -U postgres -d caain_soil_hub -c "\dt farmer_preferences"
psql -U postgres -d caain_soil_hub -c "\dt filter_combinations"

# Verify indexes
psql -U postgres -d caain_soil_hub -c "\di idx_pest_resistance_gin"

# Check sample data
psql -U postgres -d caain_soil_hub -c "SELECT COUNT(*) FROM crop_filtering_attributes;"

# Test Python model
source venv/bin/activate
python -c "from src.models.filtering_models import CropFilteringAttributes, FarmerPreference; print('Models OK')"
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-1.2, TICKET-005_crop-type-filtering-enhancement-2.1

---

## JOB1-004: Create Pydantic Schemas for API Validation

**Priority**: High  
**Estimated Effort**: 2 hours  
**Dependencies**: JOB1-002  
**Blocks**: JOB1-008, JOB1-009  
**Parallel Execution**: Can run parallel with JOB1-003, JOB1-005

**Description**:
Create Pydantic v2 schemas for request/response validation including crop filter requests, search responses, and preference updates.

**Acceptance Criteria**:
- [ ] All request schemas created with proper validation
- [ ] All response schemas created
- [ ] Field validators implemented for complex fields
- [ ] Example values provided in schema documentation
- [ ] Schemas can be imported without errors

**Technical Details**:

Create `services/crop-taxonomy/src/schemas/crop_schemas.py`:
```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class PestResistanceFilter(BaseModel):
    """Pest resistance filtering criteria"""
    pest_name: str = Field(..., description="Name of pest (e.g., 'corn_borer')")
    min_resistance_level: str = Field("moderate", description="Minimum resistance: susceptible, moderate, resistant")

class DiseaseResistanceFilter(BaseModel):
    """Disease resistance filtering criteria"""
    disease_name: str = Field(..., description="Name of disease")
    min_resistance_level: str = Field("moderate", description="Minimum resistance level")

class MarketClassFilter(BaseModel):
    """Market class filtering criteria"""
    market_class: Optional[str] = Field(None, description="Market class (e.g., 'yellow_dent', 'white_corn')")
    organic_certified: Optional[bool] = Field(None, description="Organic certification required")
    non_gmo: Optional[bool] = Field(None, description="Non-GMO required")

class CropFilterRequest(BaseModel):
    """Request for filtered crop search"""
    crop_type: str = Field(..., description="Crop type (corn, soybean, wheat)")
    
    # Basic filters
    maturity_days_min: Optional[int] = Field(None, ge=0, le=200)
    maturity_days_max: Optional[int] = Field(None, ge=0, le=200)
    
    # Advanced filters
    pest_resistance: Optional[List[PestResistanceFilter]] = Field(None)
    disease_resistance: Optional[List[DiseaseResistanceFilter]] = Field(None)
    market_class: Optional[MarketClassFilter] = Field(None)
    
    # Performance filters
    min_yield_stability: Optional[int] = Field(None, ge=0, le=100)
    min_drought_tolerance: Optional[int] = Field(None, ge=0, le=100)
    
    # Pagination
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    # Sorting
    sort_by: Optional[str] = Field("relevance", description="Sort field")
    sort_order: Optional[str] = Field("desc", description="asc or desc")
    
    @field_validator('crop_type')
    @classmethod
    def validate_crop_type(cls, v):
        allowed = ['corn', 'soybean', 'wheat', 'cotton', 'rice']
        if v.lower() not in allowed:
            raise ValueError(f'crop_type must be one of {allowed}')
        return v.lower()
    
    class Config:
        json_schema_extra = {
            "example": {
                "crop_type": "corn",
                "maturity_days_min": 90,
                "maturity_days_max": 120,
                "pest_resistance": [
                    {"pest_name": "corn_borer", "min_resistance_level": "resistant"}
                ],
                "min_yield_stability": 80,
                "page": 1,
                "page_size": 20
            }
        }

class VarietyResult(BaseModel):
    """Single variety in search results"""
    variety_id: UUID
    variety_name: str
    maturity_days: int
    yield_potential: Optional[float]
    pest_resistance_summary: Dict[str, str]
    disease_resistance_summary: Dict[str, str]
    market_class: Optional[str]
    relevance_score: float = Field(..., ge=0, le=1)

class CropSearchResponse(BaseModel):
    """Response for crop search"""
    varieties: List[VarietyResult]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: Dict[str, Any]
    search_time_ms: int

class PreferenceUpdate(BaseModel):
    """Update farmer preferences"""
    user_id: UUID
    preferred_filters: Dict[str, Any]
    filter_weights: Optional[Dict[str, float]] = Field(None)
    
class PreferenceResponse(BaseModel):
    """Response for preference operations"""
    user_id: UUID
    preferences_saved: bool
    message: str
```

**Validation Commands**:
```bash
cd services/crop-taxonomy
source venv/bin/activate

# Test schema imports
python -c "from src.schemas.crop_schemas import CropFilterRequest, CropSearchResponse; print('Schemas OK')"

# Test schema validation
python << 'EOF'
from src.schemas.crop_schemas import CropFilterRequest

# Valid request
request = CropFilterRequest(
    crop_type="corn",
    maturity_days_min=90,
    maturity_days_max=120
)
print(f"Valid request: {request.crop_type}")

# Test validation error
try:
    invalid = CropFilterRequest(crop_type="invalid_crop")
except Exception as e:
    print(f"Validation working: {type(e).__name__}")

print("Schema validation OK")
EOF
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-1.3

---

## JOB1-005: Create Main FastAPI Application Entry Point

**Priority**: High  
**Estimated Effort**: 1 hour  
**Dependencies**: JOB1-002  
**Blocks**: JOB1-008, JOB1-009  
**Parallel Execution**: Can run parallel with JOB1-003, JOB1-004

**Description**:
Create the main FastAPI application with health check endpoint, CORS middleware, and basic configuration.

**Acceptance Criteria**:
- [ ] FastAPI app created and configured
- [ ] Health check endpoint working
- [ ] CORS middleware configured
- [ ] Database connection configured
- [ ] App can start on port 8007
- [ ] OpenAPI docs accessible at /docs

**Technical Details**:

Create `services/crop-taxonomy/src/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CAAIN Crop Taxonomy Service",
    description="Advanced crop filtering and variety recommendation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Crop Taxonomy Service on port 8007")
    # TODO: Initialize database connection pool
    # TODO: Load ML models if needed

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Crop Taxonomy Service")
    # TODO: Close database connections

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "crop-taxonomy",
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CAAIN Crop Taxonomy Service",
        "docs": "/docs",
        "health": "/health"
    }

# Import and include routers (will be added later)
# from .api import crop_routes
# app.include_router(crop_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
```

**Validation Commands**:
```bash
cd services/crop-taxonomy
source venv/bin/activate

# Start the service
python src/main.py &
SERVICE_PID=$!

# Wait for startup
sleep 3

# Test health endpoint
curl http://localhost:8007/health

# Test root endpoint
curl http://localhost:8007/

# Test OpenAPI docs
curl http://localhost:8007/docs

# Stop service
kill $SERVICE_PID

# Alternative: Use uvicorn directly
uvicorn src.main:app --port 8007 --reload
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-1.1

---

## JOB1-006: Implement Crop Search Service Core Logic

**Priority**: Critical  
**Estimated Effort**: 1 day  
**Dependencies**: JOB1-003, JOB1-004  
**Blocks**: JOB1-008  
**Parallel Execution**: Can run parallel with JOB1-007

**Description**:
Implement the core CropSearchService with multi-criteria filtering, JSONB queries, and relevance scoring. Must achieve <2s response time for complex queries.

**Acceptance Criteria**:
- [ ] CropSearchService class implemented
- [ ] Multi-criteria filtering working
- [ ] JSONB queries optimized with GIN indexes
- [ ] Relevance scoring algorithm implemented
- [ ] Pagination working correctly
- [ ] Response time <2s for complex queries
- [ ] Unit tests passing

**Technical Details**:

Create `services/crop-taxonomy/src/services/crop_search_service.py`:
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Any, Optional
import time
import hashlib
import json
from ..models.filtering_models import CropFilteringAttributes, FilterCombination
from ..schemas.crop_schemas import CropFilterRequest, CropSearchResponse, VarietyResult

class CropSearchService:
    """Advanced crop search with multi-criteria filtering"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def search_varieties(self, filter_request: CropFilterRequest) -> CropSearchResponse:
        """
        Search crop varieties with advanced filtering
        
        Performance requirement: <2s for complex queries
        """
        start_time = time.time()
        
        # Build base query
        query = self.db.query(CropFilteringAttributes)
        
        # Apply filters
        query = self._apply_maturity_filters(query, filter_request)
        query = self._apply_pest_resistance_filters(query, filter_request)
        query = self._apply_disease_resistance_filters(query, filter_request)
        query = self._apply_market_class_filters(query, filter_request)
        query = self._apply_performance_filters(query, filter_request)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply sorting
        query = self._apply_sorting(query, filter_request)
        
        # Apply pagination
        offset = (filter_request.page - 1) * filter_request.page_size
        query = query.offset(offset).limit(filter_request.page_size)
        
        # Execute query
        results = query.all()
        
        # Calculate relevance scores
        varieties = [
            self._build_variety_result(result, filter_request)
            for result in results
        ]
        
        # Calculate response time
        search_time_ms = int((time.time() - start_time) * 1000)
        
        # Log filter combination for optimization
        self._log_filter_combination(filter_request, total_count, search_time_ms)
        
        # Build response
        total_pages = (total_count + filter_request.page_size - 1) // filter_request.page_size
        
        return CropSearchResponse(
            varieties=varieties,
            total_count=total_count,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages,
            filters_applied=filter_request.model_dump(exclude_none=True),
            search_time_ms=search_time_ms
        )
    
    def _apply_maturity_filters(self, query, filter_request: CropFilterRequest):
        """Apply maturity day filters"""
        # Note: This assumes maturity_days exists in a related table
        # For now, we'll skip this filter in the base implementation
        return query
    
    def _apply_pest_resistance_filters(self, query, filter_request: CropFilterRequest):
        """Apply pest resistance filters using JSONB queries"""
        if not filter_request.pest_resistance:
            return query
        
        for pest_filter in filter_request.pest_resistance:
            # JSONB containment query
            query = query.filter(
                CropFilteringAttributes.pest_resistance_traits[pest_filter.pest_name].astext.in_(
                    self._get_resistance_levels(pest_filter.min_resistance_level)
                )
            )
        
        return query
    
    def _apply_disease_resistance_filters(self, query, filter_request: CropFilterRequest):
        """Apply disease resistance filters using JSONB queries"""
        if not filter_request.disease_resistance:
            return query
        
        for disease_filter in filter_request.disease_resistance:
            query = query.filter(
                CropFilteringAttributes.disease_resistance_traits[disease_filter.disease_name].astext.in_(
                    self._get_resistance_levels(disease_filter.min_resistance_level)
                )
            )
        
        return query
    
    def _apply_market_class_filters(self, query, filter_request: CropFilterRequest):
        """Apply market class filters"""
        if not filter_request.market_class:
            return query
        
        market_filter = filter_request.market_class
        
        if market_filter.market_class:
            query = query.filter(
                CropFilteringAttributes.market_class_filters['market_class'].astext == market_filter.market_class
            )
        
        if market_filter.organic_certified is not None:
            query = query.filter(
                CropFilteringAttributes.market_class_filters['organic_certified'].astext == str(market_filter.organic_certified).lower()
            )
        
        if market_filter.non_gmo is not None:
            query = query.filter(
                CropFilteringAttributes.market_class_filters['non_gmo'].astext == str(market_filter.non_gmo).lower()
            )
        
        return query
    
    def _apply_performance_filters(self, query, filter_request: CropFilterRequest):
        """Apply performance score filters"""
        if filter_request.min_yield_stability:
            query = query.filter(
                CropFilteringAttributes.yield_stability_score >= filter_request.min_yield_stability
            )
        
        if filter_request.min_drought_tolerance:
            query = query.filter(
                CropFilteringAttributes.drought_tolerance_score >= filter_request.min_drought_tolerance
            )
        
        return query
    
    def _apply_sorting(self, query, filter_request: CropFilterRequest):
        """Apply sorting"""
        if filter_request.sort_by == "yield_stability":
            if filter_request.sort_order == "desc":
                query = query.order_by(CropFilteringAttributes.yield_stability_score.desc())
            else:
                query = query.order_by(CropFilteringAttributes.yield_stability_score.asc())
        elif filter_request.sort_by == "drought_tolerance":
            if filter_request.sort_order == "desc":
                query = query.order_by(CropFilteringAttributes.drought_tolerance_score.desc())
            else:
                query = query.order_by(CropFilteringAttributes.drought_tolerance_score.asc())
        
        return query
    
    def _get_resistance_levels(self, min_level: str) -> List[str]:
        """Get acceptable resistance levels based on minimum"""
        levels = {
            "susceptible": ["susceptible", "moderate", "resistant"],
            "moderate": ["moderate", "resistant"],
            "resistant": ["resistant"]
        }
        return levels.get(min_level, ["resistant"])
    
    def _build_variety_result(self, result: CropFilteringAttributes, filter_request: CropFilterRequest) -> VarietyResult:
        """Build variety result with relevance score"""
        relevance_score = self._calculate_relevance(result, filter_request)
        
        return VarietyResult(
            variety_id=result.variety_id,
            variety_name=f"Variety {str(result.variety_id)[:8]}",  # Placeholder
            maturity_days=100,  # Placeholder
            yield_potential=180.0,  # Placeholder
            pest_resistance_summary=result.pest_resistance_traits or {},
            disease_resistance_summary=result.disease_resistance_traits or {},
            market_class=result.market_class_filters.get('market_class') if result.market_class_filters else None,
            relevance_score=relevance_score
        )
    
    def _calculate_relevance(self, result: CropFilteringAttributes, filter_request: CropFilterRequest) -> float:
        """Calculate relevance score (0-1)"""
        score = 0.5  # Base score
        
        # Boost for performance scores
        if result.yield_stability_score:
            score += (result.yield_stability_score / 100) * 0.25
        
        if result.drought_tolerance_score:
            score += (result.drought_tolerance_score / 100) * 0.25
        
        return min(score, 1.0)
    
    def _log_filter_combination(self, filter_request: CropFilterRequest, result_count: int, response_time_ms: int):
        """Log filter combination for optimization"""
        filters_dict = filter_request.model_dump(exclude={'page', 'page_size', 'sort_by', 'sort_order'}, exclude_none=True)
        combination_hash = hashlib.sha256(json.dumps(filters_dict, sort_keys=True).encode()).hexdigest()
        
        existing = self.db.query(FilterCombination).filter(
            FilterCombination.combination_hash == combination_hash
        ).first()
        
        if existing:
            existing.usage_count += 1
            existing.avg_result_count = (existing.avg_result_count + result_count) // 2
            existing.avg_response_time_ms = (existing.avg_response_time_ms + response_time_ms) // 2
        else:
            new_combo = FilterCombination(
                combination_hash=combination_hash,
                filters=filters_dict,
                usage_count=1,
                avg_result_count=result_count,
                avg_response_time_ms=response_time_ms
            )
            self.db.add(new_combo)
        
        self.db.commit()
```

**Validation Commands**:
```bash
cd services/crop-taxonomy
source venv/bin/activate

# Test service import
python -c "from src.services.crop_search_service import CropSearchService; print('Service OK')"

# Run unit tests (create test file first)
pytest tests/test_crop_search.py -v
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-2.2, TICKET-005_crop-type-filtering-enhancement-3.1

---

## JOB1-007: Implement Farmer Preference Manager

**Priority**: High
**Estimated Effort**: 6 hours
**Dependencies**: JOB1-003, JOB1-004
**Blocks**: JOB1-010
**Parallel Execution**: Can run parallel with JOB1-006

**Description**:
Implement preference learning system that tracks farmer selections and adapts filter recommendations.

**Acceptance Criteria**:
- [ ] FarmerPreferenceManager class implemented
- [ ] Preference storage working
- [ ] Learning algorithm implemented
- [ ] Filter weight calculation working
- [ ] Unit tests passing

**Technical Details**:

Create `services/crop-taxonomy/src/services/preference_manager.py` - See parallel-job-1 plan for full implementation.

**Validation Commands**:
```bash
pytest tests/test_preference_manager.py -v
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-4.1

---

## JOB1-008: Create API Routes for Crop Search

**Priority**: Critical
**Estimated Effort**: 4 hours
**Dependencies**: JOB1-004, JOB1-005, JOB1-006
**Blocks**: JOB1-011
**Parallel Execution**: Can run parallel with JOB1-009

**Description**:
Create FastAPI routes for crop search endpoint with proper error handling and validation.

**Acceptance Criteria**:
- [ ] POST /api/v1/crop-taxonomy/search endpoint working
- [ ] Request validation working
- [ ] Error handling implemented
- [ ] Response format correct
- [ ] API tests passing

**Validation Commands**:
```bash
curl -X POST http://localhost:8007/api/v1/crop-taxonomy/search \
  -H "Content-Type: application/json" \
  -d '{"crop_type": "corn", "maturity_days_min": 90, "maturity_days_max": 120}'
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-3.2

---

## JOB1-009: Create API Routes for Preference Management

**Priority**: High
**Estimated Effort**: 3 hours
**Dependencies**: JOB1-004, JOB1-005, JOB1-007
**Blocks**: JOB1-011
**Parallel Execution**: Can run parallel with JOB1-008

**Description**:
Create API routes for farmer preference management.

**Acceptance Criteria**:
- [ ] POST /api/v1/preferences endpoint working
- [ ] GET /api/v1/preferences/{user_id} endpoint working
- [ ] API tests passing

**Validation Commands**:
```bash
curl -X POST http://localhost:8007/api/v1/preferences \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test-uuid", "preferred_filters": {"organic_certified": true}}'
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-4.2

---

## JOB1-010: Implement Unit Tests for Services

**Priority**: High
**Estimated Effort**: 1 day
**Dependencies**: JOB1-006, JOB1-007
**Blocks**: JOB1-013
**Parallel Execution**: Can run parallel with JOB1-008, JOB1-009

**Description**:
Create comprehensive unit tests for CropSearchService and FarmerPreferenceManager.

**Acceptance Criteria**:
- [ ] Test coverage >80%
- [ ] All service methods tested
- [ ] Edge cases covered
- [ ] Mock database working
- [ ] All tests passing

**Validation Commands**:
```bash
pytest tests/ -v --cov=src --cov-report=html
open htmlcov/index.html
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-5.1

---

## JOB1-011: Implement Integration Tests for API

**Priority**: High
**Estimated Effort**: 6 hours
**Dependencies**: JOB1-008, JOB1-009
**Blocks**: JOB1-013
**Parallel Execution**: Can run parallel with JOB1-010

**Description**:
Create integration tests for API endpoints with real database.

**Acceptance Criteria**:
- [ ] API integration tests created
- [ ] Database fixtures working
- [ ] End-to-end workflows tested
- [ ] Performance tests included
- [ ] All tests passing

**Validation Commands**:
```bash
pytest tests/test_api.py -v
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-5.2

---

## JOB1-012: Performance Optimization and Indexing

**Priority**: Medium
**Estimated Effort**: 4 hours
**Dependencies**: JOB1-010, JOB1-011
**Blocks**: JOB1-013
**Parallel Execution**: No

**Description**:
Optimize database queries and ensure <2s response time requirement is met.

**Acceptance Criteria**:
- [ ] All queries <2s for complex filters
- [ ] EXPLAIN ANALYZE shows index usage
- [ ] No N+1 query problems
- [ ] Performance tests passing

**Validation Commands**:
```bash
psql -U postgres -d caain_soil_hub -c "EXPLAIN ANALYZE SELECT * FROM crop_filtering_attributes WHERE pest_resistance_traits @> '{\"corn_borer\": \"resistant\"}';"
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-6.1

---

## JOB1-013: Create Service Documentation

**Priority**: Medium
**Estimated Effort**: 3 hours
**Dependencies**: JOB1-010, JOB1-011, JOB1-012
**Blocks**: None
**Parallel Execution**: No

**Description**:
Create comprehensive README and API documentation.

**Acceptance Criteria**:
- [ ] README.md created with setup instructions
- [ ] API documentation complete
- [ ] Code examples provided
- [ ] Architecture diagram included

**Validation Commands**:
```bash
cat services/crop-taxonomy/README.md
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-7.1

---

## JOB1-014: Agricultural Expert Review

**Priority**: High
**Estimated Effort**: 4 hours
**Dependencies**: JOB1-013
**Blocks**: JOB1-015
**Parallel Execution**: No

**Description**:
Prepare service for agricultural expert review with test scenarios.

**Acceptance Criteria**:
- [ ] Test scenarios documented
- [ ] Sample queries prepared
- [ ] Results validated against agricultural knowledge
- [ ] Expert feedback incorporated

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-8.1

---

## JOB1-015: Final Integration and Deployment Preparation

**Priority**: Critical
**Estimated Effort**: 4 hours
**Dependencies**: JOB1-014
**Blocks**: None (Ready for integration phase)
**Parallel Execution**: No

**Description**:
Final checks and preparation for integration with other services.

**Acceptance Criteria**:
- [ ] Service runs on port 8007
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for integration testing
- [ ] Mock endpoints for dependencies created

**Validation Commands**:
```bash
# Start service
uvicorn src.main:app --port 8007 &

# Run full test suite
pytest tests/ -v --cov=src

# Check health
curl http://localhost:8007/health
```

**Related Tickets**: TICKET-005_crop-type-filtering-enhancement-9.1

---

## Summary

**Total Tickets**: 15
**Critical Path**: JOB1-001 → JOB1-002 → JOB1-003 → JOB1-006 → JOB1-008 → JOB1-011 → JOB1-012 → JOB1-013 → JOB1-014 → JOB1-015
**Estimated Total Time**: 4 weeks
**Parallel Opportunities**: JOB1-003/004/005, JOB1-006/007, JOB1-008/009/010, JOB1-010/011


