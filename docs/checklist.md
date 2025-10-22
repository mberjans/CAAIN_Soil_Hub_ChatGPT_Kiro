# Job 1: Crop Filtering Enhancement - TDD Checklist

**Service**: Crop Taxonomy Service (Port 8007)  
**Total Tickets**: 15  
**Estimated Timeline**: 4 weeks  
**Related Files**: `docs/tickets-job-1-crop-filtering.md`, `docs/parallel-job-1-crop-filtering.md`

---

## JOB1-001: Setup Crop Filtering Service Directory Structure

### Tasks

- [x] **JOB1-001.1** - Create main service directory
  - Command: `mkdir -p services/crop_taxonomy`
  - Verify: `ls -ld services/crop_taxonomy`

- [x] **JOB1-001.2** - Create source code directories
  - Command: `mkdir -p services/crop_taxonomy/src/{models,services,api,schemas}`
  - Verify: `ls -la services/crop_taxonomy/src/`

- [x] **JOB1-001.3** - Create tests directory
  - Command: `mkdir -p services/crop_taxonomy/tests`
  - Verify: `ls -ld services/crop_taxonomy/tests`

- [x] **JOB1-001.4** - Create migrations directory
  - Command: `mkdir -p services/crop_taxonomy/migrations`
  - Verify: `ls -ld services/crop_taxonomy/migrations`

- [x] **JOB1-001.5** - Create all __init__.py files
  - Command: `touch services/crop_taxonomy/src/__init__.py services/crop_taxonomy/src/models/__init__.py services/crop_taxonomy/src/services/__init__.py services/crop_taxonomy/src/api/__init__.py services/crop_taxonomy/src/schemas/__init__.py services/crop_taxonomy/tests/__init__.py`
  - Verify: `find services/crop_taxonomy -name "__init__.py" | wc -l` (should be 6)

- [x] **JOB1-001.6** - Create virtual environment
  - Command: `cd services/crop_taxonomy && python3 -m venv venv`
  - Verify: `ls services/crop_taxonomy/venv/bin/python`

- [x] **JOB1-001.7** - Activate virtual environment
  - Command: `cd services/crop_taxonomy && source venv/bin/activate`
  - Verify: `which python | grep crop_taxonomy`

- [x] **JOB1-001.8** - Verify directory structure complete
  - Command: `tree services/crop_taxonomy -L 3` (or `find services/crop_taxonomy -type d`)
  - Verify: All directories present

- [x] **JOB1-001.99** - Commit directory structure
  - Command: `git add services/crop_taxonomy && git commit -m "JOB1-001: Setup crop filtering service directory structure"`
  - Verify: `git log -1 --oneline`

---

## JOB1-002: Create Requirements File and Install Dependencies

### Tasks

- [x] **JOB1-002.1** - Create requirements.txt file
  - Path: `services/crop_taxonomy/requirements.txt`
  - Content: fastapi==0.104.1, uvicorn[standard]==0.24.0, sqlalchemy==2.0.23, psycopg2-binary==2.9.9, pydantic==2.5.0, alembic==1.12.1, pytest==7.4.3, pytest-asyncio==0.21.1, pytest-cov==4.1.0, httpx==0.25.1, python-multipart==0.0.6
  - Verify: `cat services/crop_taxonomy/requirements.txt`

- [x] **JOB1-002.2** - Activate virtual environment
  - Command: `cd services/crop_taxonomy && source venv/bin/activate`
  - Verify: `which python | grep crop_taxonomy`

- [x] **JOB1-002.3** - Install dependencies
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pip install -r requirements.txt`
  - Verify: `pip list | grep fastapi`

- [x] **JOB1-002.4** - Verify FastAPI installation
  - Command: `python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"`
  - Verify: Output shows version 0.104.1

- [x] **JOB1-002.5** - Verify SQLAlchemy installation
  - Command: `python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"`
  - Verify: Output shows version 2.0.23

- [x] **JOB1-002.6** - Verify Pydantic installation
  - Command: `python -c "import pydantic; print(f'Pydantic: {pydantic.__version__}')"`
  - Verify: Output shows version 2.5.0

- [x] **JOB1-002.7** - Verify pytest installation
  - Command: `python -c "import pytest; print(f'Pytest: {pytest.__version__}')"`
  - Verify: Output shows version 7.4.3

- [x] **JOB1-002.8** - List all installed packages
  - Command: `pip list`
  - Verify: All required packages present

- [x] **JOB1-002.99** - Commit requirements file
  - Command: `git add services/crop_taxonomy/requirements.txt && git commit -m "JOB1-002: Add requirements.txt with dependencies"`
  - Verify: `git log -1 --oneline`

---

## JOB1-003: Create Database Schema for Crop Filtering Attributes

### Tasks (TDD Workflow)

- [x] **JOB1-003.1.test** - Create test file for filtering models
  - Path: `services/crop_taxonomy/tests/test_filtering_models.py`
  - Create empty test file with imports
  - Verify: `ls services/crop_taxonomy/tests/test_filtering_models.py`

- [x] **JOB1-003.2.test** - Write test for CropFilteringAttributes model creation
  - Path: `services/crop_taxonomy/tests/test_filtering_models.py`
  - Add `test_crop_filtering_attributes_creation()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_filtering_models.py --collect-only`

- [x] **JOB1-003.3.test** - Write test for FarmerPreference model creation
  - Path: `services/crop_taxonomy/tests/test_filtering_models.py`
  - Add `test_farmer_preference_creation()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_filtering_models.py --collect-only`

- [x] **JOB1-003.4.test** - Write test for FilterCombination model creation
  - Path: `services/crop_taxonomy/tests/test_filtering_models.py`
  - Add `test_filter_combination_creation()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_filtering_models.py --collect-only`

- [x] **JOB1-003.5.impl** - Create filtering_models.py file
  - Path: `services/crop_taxonomy/src/models/filtering_models.py`
  - Create empty file with imports
  - Verify: `ls services/crop_taxonomy/src/models/filtering_models.py`

- [x] **JOB1-003.6.impl** - Implement CropFilteringAttributes model
  - Path: `services/crop_taxonomy/src/models/filtering_models.py`
  - Add CropFilteringAttributes class with JSONB columns
  - Verify: `python -c "from src.models.filtering_models import CropFilteringAttributes; print('OK')"`

- [x] **JOB1-003.7.impl** - Add GIN indexes to CropFilteringAttributes
  - Path: `services/crop_taxonomy/src/models/filtering_models.py`
  - Add __table_args__ with GIN indexes for JSONB columns
  - Verify: Check __table_args__ in model definition

- [x] **JOB1-003.8.impl** - Implement FarmerPreference model
  - Path: `services/crop_taxonomy/src/models/filtering_models.py`
  - Add FarmerPreference class with JSONB columns
  - Verify: `python -c "from src.models.filtering_models import FarmerPreference; print('OK')"`

- [x] **JOB1-003.9.impl** - Implement FilterCombination model
  - Path: `services/crop_taxonomy/src/models/filtering_models.py`
  - Add FilterCombination class
  - Verify: `python -c "from src.models.filtering_models import FilterCombination; print('OK')"`

- [x] **JOB1-003.10.impl** - Create database migration SQL file
  - Path: `services/crop_taxonomy/migrations/001_filtering_schema.sql`
  - Write CREATE TABLE statements for all three tables
  - Verify: `cat services/crop_taxonomy/migrations/001_filtering_schema.sql`

- [x] **JOB1-003.11.impl** - Add GIN indexes to migration SQL
  - Path: `services/crop_taxonomy/migrations/001_filtering_schema.sql`
  - Add CREATE INDEX statements for JSONB columns
  - Verify: `grep "CREATE INDEX" services/crop_taxonomy/migrations/001_filtering_schema.sql | wc -l`

- [x] **JOB1-003.12.impl** - Add sample data to migration SQL
  - Path: `services/crop_taxonomy/migrations/001_filtering_schema.sql`
  - Add INSERT statements with sample data
  - Verify: `grep "INSERT INTO" services/crop_taxonomy/migrations/001_filtering_schema.sql`

- [x] **JOB1-003.13.impl** - Run database migration
  - Command: `psql -U postgres -d caain_soil_hub -f services/crop_taxonomy/migrations/001_filtering_schema.sql`
  - Verify: `psql -U postgres -d caain_soil_hub -c "\dt crop_filtering_attributes"`

- [x] **JOB1-003.14.verify** - Verify crop_filtering_attributes table created
  - Command: `psql -U postgres -d caain_soil_hub -c "\d crop_filtering_attributes"`
  - Verify: Table structure matches model

- [x] **JOB1-003.15.verify** - Verify farmer_preferences table created
  - Command: `psql -U postgres -d caain_soil_hub -c "\d farmer_preferences"`
  - Verify: Table structure matches model

- [x] **JOB1-003.16.verify** - Verify filter_combinations table created
  - Command: `psql -U postgres -d caain_soil_hub -c "\d filter_combinations"`
  - Verify: Table structure matches model

- [x] **JOB1-003.17.verify** - Verify GIN indexes created
  - Command: `psql -U postgres -d caain_soil_hub -c "\di idx_pest_resistance_gin"`
  - Verify: Index exists with GIN method

- [x] **JOB1-003.18.verify** - Check sample data inserted
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT COUNT(*) FROM crop_filtering_attributes;"`
  - Verify: Count > 0

- [x] **JOB1-003.19.verify** - Run unit tests for models
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_filtering_models.py -v`
  - Verify: All tests pass

- [x] **JOB1-003.99** - Commit database schema
  - Command: `git add services/crop_taxonomy/src/models/filtering_models.py services/crop_taxonomy/migrations/001_filtering_schema.sql services/crop_taxonomy/tests/test_filtering_models.py && git commit -m "JOB1-003: Create database schema for crop filtering attributes"`
  - Verify: `git log -1 --oneline`

---

## JOB1-004: Create Pydantic Schemas for API Validation

### Tasks (TDD Workflow)

- [x] **JOB1-004.1.test** - Create test file for schemas
  - Path: `services/crop_taxonomy/tests/test_crop_schemas.py`
  - Create empty test file with imports
  - Verify: `ls services/crop_taxonomy/tests/test_crop_schemas.py`

- [x] **JOB1-004.2.test** - Write test for CropFilterRequest schema validation
  - Path: `services/crop_taxonomy/tests/test_crop_schemas.py`
  - Add `test_crop_filter_request_valid()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_schemas.py --collect-only`

- [x] **JOB1-004.3.test** - Write test for CropFilterRequest validation errors
  - Path: `services/crop_taxonomy/tests/test_crop_schemas.py`
  - Add `test_crop_filter_request_invalid_crop_type()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_schemas.py --collect-only`

- [x] **JOB1-004.4.test** - Write test for CropSearchResponse schema
  - Path: `services/crop_taxonomy/tests/test_crop_schemas.py`
  - Add `test_crop_search_response()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_schemas.py --collect-only`

- [x] **JOB1-004.5.impl** - Create crop_schemas.py file
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Create empty file with Pydantic imports
  - Verify: `ls services/crop_taxonomy/src/schemas/crop_schemas.py`

- [x] **JOB1-004.6.impl** - Implement PestResistanceFilter schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add PestResistanceFilter class
  - Verify: `python -c "from src.schemas.crop_schemas import PestResistanceFilter; print('OK')"`

- [x] **JOB1-004.7.impl** - Implement DiseaseResistanceFilter schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add DiseaseResistanceFilter class
  - Verify: `python -c "from src.schemas.crop_schemas import DiseaseResistanceFilter; print('OK')"`

- [x] **JOB1-004.8.impl** - Implement MarketClassFilter schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add MarketClassFilter class
  - Verify: `python -c "from src.schemas.crop_schemas import MarketClassFilter; print('OK')"`

- [x] **JOB1-004.9.impl** - Implement CropFilterRequest schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add CropFilterRequest class with all filter fields
  - Verify: `python -c "from src.schemas.crop_schemas import CropFilterRequest; print('OK')"`

- [x] **JOB1-004.10.impl** - Add crop_type validator to CropFilterRequest
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add @field_validator for crop_type
  - Verify: Check validator in schema definition

- [x] **JOB1-004.11.impl** - Add example to CropFilterRequest schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add Config class with json_schema_extra
  - Verify: Check Config in schema definition

- [x] **JOB1-004.12.impl** - Implement VarietyResult schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add VarietyResult class
  - Verify: `python -c "from src.schemas.crop_schemas import VarietyResult; print('OK')"`

- [x] **JOB1-004.13.impl** - Implement CropSearchResponse schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add CropSearchResponse class
  - Verify: `python -c "from src.schemas.crop_schemas import CropSearchResponse; print('OK')"`

- [x] **JOB1-004.14.impl** - Implement PreferenceUpdate schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add PreferenceUpdate class
  - Verify: `python -c "from src.schemas.crop_schemas import PreferenceUpdate; print('OK')"`

- [x] **JOB1-004.15.impl** - Implement PreferenceResponse schema
  - Path: `services/crop_taxonomy/src/schemas/crop_schemas.py`
  - Add PreferenceResponse class
  - Verify: `python -c "from src.schemas.crop_schemas import PreferenceResponse; print('OK')"`

- [x] **JOB1-004.16.verify** - Test valid CropFilterRequest creation
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && python -c "from src.schemas.crop_schemas import CropFilterRequest; req = CropFilterRequest(crop_type='corn', maturity_days_min=90); print('Valid')"`
  - Verify: No validation errors

- [x] **JOB1-004.17.verify** - Test invalid crop_type validation
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && python -c "from src.schemas.crop_schemas import CropFilterRequest; try: req = CropFilterRequest(crop_type='invalid'); except Exception as e: print('Validation working')"`
  - Verify: Validation error raised

- [x] **JOB1-004.18.verify** - Run unit tests for schemas
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_schemas.py -v`
  - Verify: All tests pass

- [x] **JOB1-004.99** - Commit Pydantic schemas
  - Command: `git add services/crop_taxonomy/src/schemas/crop_schemas.py services/crop_taxonomy/tests/test_crop_schemas.py && git commit -m "JOB1-004: Create Pydantic schemas for API validation"`
  - Verify: `git log -1 --oneline`

---

## JOB1-005: Create Main FastAPI Application Entry Point

### Tasks (TDD Workflow)

- [x] **JOB1-005.1.test** - Create test file for main app
  - Path: `services/crop_taxonomy/tests/test_main.py`
  - Create empty test file with imports
  - Verify: `ls services/crop_taxonomy/tests/test_main.py`

- [x] **JOB1-005.2.test** - Write test for health endpoint
  - Path: `services/crop_taxonomy/tests/test_main.py`
  - Add `test_health_endpoint()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_main.py --collect-only`

- [x] **JOB1-005.3.test** - Write test for root endpoint
  - Path: `services/crop_taxonomy/tests/test_main.py`
  - Add `test_root_endpoint()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_main.py --collect-only`

- [x] **JOB1-005.4.impl** - Create main.py file
  - Path: `services/crop_taxonomy/src/main.py`
  - Create empty file with FastAPI imports
  - Verify: `ls services/crop_taxonomy/src/main.py`

- [x] **JOB1-005.5.impl** - Configure logging
  - Path: `services/crop_taxonomy/src/main.py`
  - Add logging configuration
  - Verify: Check logging setup in file

- [x] **JOB1-005.6.impl** - Create FastAPI app instance
  - Path: `services/crop_taxonomy/src/main.py`
  - Add FastAPI app with title, description, version
  - Verify: `python -c "from src.main import app; print(app.title)"`

- [x] **JOB1-005.7.impl** - Add CORS middleware
  - Path: `services/crop_taxonomy/src/main.py`
  - Add CORSMiddleware configuration
  - Verify: Check middleware in app

- [x] **JOB1-005.8.impl** - Add startup event handler
  - Path: `services/crop_taxonomy/src/main.py`
  - Add @app.on_event("startup") function
  - Verify: Check startup handler in file

- [x] **JOB1-005.9.impl** - Add shutdown event handler
  - Path: `services/crop_taxonomy/src/main.py`
  - Add @app.on_event("shutdown") function
  - Verify: Check shutdown handler in file

- [x] **JOB1-005.10.impl** - Implement health check endpoint
  - Path: `services/crop_taxonomy/src/main.py`
  - Add @app.get("/health") endpoint
  - Verify: Check health endpoint in file

- [x] **JOB1-005.11.impl** - Implement root endpoint
  - Path: `services/crop_taxonomy/src/main.py`
  - Add @app.get("/") endpoint
  - Verify: Check root endpoint in file

- [x] **JOB1-005.12.impl** - Add main block for uvicorn
  - Path: `services/crop_taxonomy/src/main.py`
  - Add if __name__ == "__main__" block
  - Verify: Check main block in file

- [x]! **JOB1-005.13.verify** - Start service manually
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && python src/main.py &`
  - Verify: Service starts without errors

- [x]! **JOB1-005.14.verify** - Test health endpoint
  - Command: `curl http://localhost:8007/health`
  - Verify: Returns {"status": "healthy", ...}

- [x]! **JOB1-005.15.verify** - Test root endpoint
  - Command: `curl http://localhost:8007/`
  - Verify: Returns service information

- [x]! **JOB1-005.16.verify** - Test OpenAPI docs
  - Command: `curl http://localhost:8007/docs`
  - Verify: Returns HTML for Swagger UI

- [x]! **JOB1-005.17.verify** - Stop service
  - Command: `pkill -f "uvicorn src.main:app"`
  - Verify: Service stopped

- [x] **JOB1-005.18.verify** - Run unit tests for main app
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_main.py -v`
  - Verify: All tests pass

- [x] **JOB1-005.99** - Commit main application
  - Command: `git add services/crop_taxonomy/src/main.py services/crop_taxonomy/tests/test_main.py && git commit -m "JOB1-005: Create main FastAPI application entry point"`
  - Verify: `git log -1 --oneline`

---

## JOB1-006: Implement Crop Search Service Core Logic

### Tasks (TDD Workflow)

- [x] **JOB1-006.1.test** - Create test file for crop search service
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Create test file with imports and basic tests
  - Verify: `ls services/crop_taxonomy/tests/test_crop_search.py`

- [x] **JOB1-006.2.test** - Write test for CropSearchService initialization
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_crop_search_service_init()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.3.test** - Write test for basic variety search
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_varieties_basic()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.4.test** - Write test for pest resistance filtering
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_with_pest_resistance()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.5.test** - Write test for disease resistance filtering
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_with_disease_resistance()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.6.test** - Write test for market class filtering
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_with_market_class()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.7.test** - Write test for performance score filtering
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_with_performance_filters()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.8.test** - Write test for pagination
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_pagination()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.9.test** - Write test for sorting
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_sorting()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x] **JOB1-006.10.test** - Write test for response time <2s
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add `test_search_performance()` test method with timing
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [x]! **JOB1-006.11.impl** - Create crop_search_service.py file
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Create empty file with imports
  - Verify: `ls services/crop_taxonomy/src/services/crop_search_service.py`

- [x]! **JOB1-006.12.impl** - Implement CropSearchService class skeleton
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add class with __init__ method
  - Verify: `python -c "from src.services.crop_search_service import CropSearchService; print('OK')"`

- [x] **JOB1-006.13.impl** - Implement search_varieties method signature
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add async search_varieties method
  - Verify: Check method signature in file

- [x] **JOB1-006.14.impl** - Implement _apply_maturity_filters method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _apply_maturity_filters helper method
  - Verify: Check method in file

- [x] **JOB1-006.15.impl** - Implement _apply_pest_resistance_filters method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _apply_pest_resistance_filters with JSONB queries
  - Verify: Check method in file

- [x] **JOB1-006.16.impl** - Implement _apply_disease_resistance_filters method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _apply_disease_resistance_filters with JSONB queries
  - Verify: Check method in file

- [x]! **JOB1-006.17.impl** - Implement _apply_market_class_filters method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _apply_market_class_filters method
  - Verify: Check method in file

- [x] **JOB1-006.18.impl** - Implement _apply_performance_filters method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _apply_performance_filters method
  - Verify: Check method in file

- [x] **JOB1-006.19.impl** - Implement _apply_sorting method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _apply_sorting method
  - Verify: Check method in file

- [x] **JOB1-006.20.impl** - Implement _get_resistance_levels helper
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _get_resistance_levels method
  - Verify: Check method in file

- [x] **JOB1-006.21.impl** - Implement _build_variety_result method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _build_variety_result method
  - Verify: Check method in file

- [x] **JOB1-006.22.impl** - Implement _calculate_relevance method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _calculate_relevance scoring algorithm
  - Verify: Check method in file

- [x] **JOB1-006.23.impl** - Implement _log_filter_combination method
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Add _log_filter_combination for optimization tracking
  - Verify: Check method in file

- [x] **JOB1-006.24.impl** - Complete search_varieties implementation
  - Path: `services/crop_taxonomy/src/services/crop_search_service.py`
  - Wire all helper methods together in search_varieties
  - Verify: Check complete implementation

- [x] **JOB1-006.25.verify** - Run unit tests for crop search service
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_search.py -v`
  - Verify: All tests pass

- [x] **JOB1-006.26.verify** - Test performance requirement <2s
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_search.py::test_search_performance -v`
  - Verify: Test passes with response time <2s

- [x] **JOB1-006.27.verify** - Test JSONB query optimization
  - Command: `psql -U postgres -d caain_soil_hub -c "EXPLAIN ANALYZE SELECT * FROM crop_filtering_attributes WHERE pest_resistance_traits @> '{\"corn_borer\": \"resistant\"}';"`
  - Verify: Query uses GIN index

- [!] **JOB1-006.99** - Commit crop search service
  - Command: `git add services/crop_taxonomy/src/services/crop_search_service.py services/crop_taxonomy/tests/test_crop_search.py && git commit -m "JOB1-006: Implement crop search service core logic"`
  - Verify: `git log -1 --oneline`

---

## JOB1-007: Implement Farmer Preference Manager

### Tasks (TDD Workflow)

- [x] **JOB1-007.1.test** - Create test file for preference manager
  - Path: `services/crop_taxonomy/tests/test_preference_manager.py`
  - Create test file with imports
  - Verify: `ls services/crop_taxonomy/tests/test_preference_manager.py`

- [x] **JOB1-007.2.test** - Write test for saving preferences
  - Path: `services/crop_taxonomy/tests/test_preference_manager.py`
  - Add `test_save_preferences()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_preference_manager.py --collect-only`

- [x] **JOB1-007.3.test** - Write test for loading preferences
  - Path: `services/crop_taxonomy/tests/test_preference_manager.py`
  - Add `test_load_preferences()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_preference_manager.py --collect-only`

- [x] **JOB1-007.4.test** - Write test for learning from selections
  - Path: `services/crop_taxonomy/tests/test_preference_manager.py`
  - Add `test_learn_from_selection()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_preference_manager.py --collect-only`

- [x] **JOB1-007.5.impl** - Create preference_manager.py file
  - Path: `services/crop_taxonomy/src/services/preference_manager.py`
  - Create file with imports
  - Verify: `ls services/crop_taxonomy/src/services/preference_manager.py`

- [x] **JOB1-007.6.impl** - Implement FarmerPreferenceManager class
  - Path: `services/crop_taxonomy/src/services/preference_manager.py`
  - Add class skeleton
  - Verify: `python -c "from src.services.preference_manager import FarmerPreferenceManager; print('OK')"`

- [x] **JOB1-007.7.impl** - Implement save_preferences method
  - Path: `services/crop_taxonomy/src/services/preference_manager.py`
  - Add save_preferences implementation
  - Verify: Check method in file

- [x] **JOB1-007.8.impl** - Implement load_preferences method
  - Path: `services/crop_taxonomy/src/services/preference_manager.py`
  - Add load_preferences implementation
  - Verify: Check method in file

- [x] **JOB1-007.9.impl** - Implement learn_from_selection method
  - Path: `services/crop_taxonomy/src/services/preference_manager.py`
  - Add learning algorithm
  - Verify: Check method in file

- [x] **JOB1-007.10.verify** - Run unit tests for preference manager FAILED - GEMINI FAILED, RETURN LATER
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_preference_manager.py -v`
  - Verify: All tests pass

- [x] **JOB1-007.99** - Commit preference manager
  - Command: `git add services/crop_taxonomy/src/services/preference_manager.py services/crop_taxonomy/tests/test_preference_manager.py && git commit -m "JOB1-007: Implement farmer preference manager"`
  - Verify: `git log -1 --oneline`

---

## JOB1-008: Create API Routes for Crop Search

### Tasks (TDD Workflow)

- [x] **JOB1-008.1.test** - Create test file for crop routes
  - Path: `services/crop_taxonomy/tests/test_crop_routes.py`
  - Create test file with imports
  - Verify: `ls services/crop_taxonomy/tests/test_crop_routes.py`

- [ ] **JOB1-008.2.test** - Write test for POST /search endpoint
  - Path: `services/crop_taxonomy/tests/test_crop_routes.py`
  - Add `test_search_endpoint()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_routes.py --collect-only`

- [ ] **JOB1-008.3.test** - Write test for invalid request validation
  - Path: `services/crop_taxonomy/tests/test_crop_routes.py`
  - Add `test_search_invalid_request()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_routes.py --collect-only`

- [ ] **JOB1-008.4.impl** - Create crop_routes.py file
  - Path: `services/crop_taxonomy/src/api/crop_routes.py`
  - Create file with FastAPI imports
  - Verify: `ls services/crop_taxonomy/src/api/crop_routes.py`

- [ ] **JOB1-008.5.impl** - Create APIRouter instance
  - Path: `services/crop_taxonomy/src/api/crop_routes.py`
  - Add router = APIRouter()
  - Verify: Check router in file

- [ ] **JOB1-008.6.impl** - Implement POST /search endpoint
  - Path: `services/crop_taxonomy/src/api/crop_routes.py`
  - Add @router.post("/api/v1/crop-taxonomy/search") endpoint
  - Verify: Check endpoint in file

- [ ] **JOB1-008.7.impl** - Add error handling to search endpoint
  - Path: `services/crop_taxonomy/src/api/crop_routes.py`
  - Add try/except blocks
  - Verify: Check error handling in file

- [ ] **JOB1-008.8.impl** - Include router in main app
  - Path: `services/crop_taxonomy/src/main.py`
  - Add app.include_router(crop_routes.router)
  - Verify: Check router inclusion in main.py

- [ ] **JOB1-008.9.verify** - Start service and test endpoint
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && uvicorn src.main:app --port 8007 &`
  - Verify: Service starts

- [ ] **JOB1-008.10.verify** - Test search endpoint with curl
  - Command: `curl -X POST http://localhost:8007/api/v1/crop-taxonomy/search -H "Content-Type: application/json" -d '{"crop_type": "corn", "maturity_days_min": 90, "maturity_days_max": 120}'`
  - Verify: Returns valid response

- [ ] **JOB1-008.11.verify** - Stop service
  - Command: `pkill -f "uvicorn src.main:app"`
  - Verify: Service stopped

- [ ] **JOB1-008.12.verify** - Run unit tests for crop routes
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_routes.py -v`
  - Verify: All tests pass

- [ ] **JOB1-008.99** - Commit API routes
  - Command: `git add services/crop_taxonomy/src/api/crop_routes.py services/crop_taxonomy/src/main.py services/crop_taxonomy/tests/test_crop_routes.py && git commit -m "JOB1-008: Create API routes for crop search"`
  - Verify: `git log -1 --oneline`

---

## JOB1-009: Create API Routes for Preference Management

### Tasks (TDD Workflow)

- [ ] **JOB1-009.1.test** - Write test for POST /preferences endpoint
  - Path: `services/crop_taxonomy/tests/test_crop_routes.py`
  - Add `test_save_preferences_endpoint()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_routes.py --collect-only`

- [ ] **JOB1-009.2.test** - Write test for GET /preferences/{user_id} endpoint
  - Path: `services/crop_taxonomy/tests/test_crop_routes.py`
  - Add `test_get_preferences_endpoint()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_routes.py --collect-only`

- [ ] **JOB1-009.3.impl** - Implement POST /preferences endpoint
  - Path: `services/crop_taxonomy/src/api/crop_routes.py`
  - Add @router.post("/api/v1/preferences") endpoint
  - Verify: Check endpoint in file

- [ ] **JOB1-009.4.impl** - Implement GET /preferences/{user_id} endpoint
  - Path: `services/crop_taxonomy/src/api/crop_routes.py`
  - Add @router.get("/api/v1/preferences/{user_id}") endpoint
  - Verify: Check endpoint in file

- [ ] **JOB1-009.5.verify** - Test preferences endpoints
  - Command: `curl -X POST http://localhost:8007/api/v1/preferences -H "Content-Type: application/json" -d '{"user_id": "test-uuid", "preferred_filters": {"organic_certified": true}}'`
  - Verify: Returns success response

- [ ] **JOB1-009.6.verify** - Run unit tests for preference routes
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_routes.py -v`
  - Verify: All tests pass

- [ ] **JOB1-009.99** - Commit preference routes
  - Command: `git add services/crop_taxonomy/src/api/crop_routes.py services/crop_taxonomy/tests/test_crop_routes.py && git commit -m "JOB1-009: Create API routes for preference management"`
  - Verify: `git log -1 --oneline`

---

## JOB1-010: Implement Unit Tests for Services

### Tasks

- [ ] **JOB1-010.1** - Review test coverage for CropSearchService
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_search.py --cov=src.services.crop_search_service --cov-report=term`
  - Verify: Coverage >80%

- [ ] **JOB1-010.2** - Add missing edge case tests for CropSearchService
  - Path: `services/crop_taxonomy/tests/test_crop_search.py`
  - Add tests for edge cases (empty results, invalid filters, etc.)
  - Verify: `pytest services/crop_taxonomy/tests/test_crop_search.py --collect-only`

- [ ] **JOB1-010.3** - Review test coverage for FarmerPreferenceManager
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_preference_manager.py --cov=src.services.preference_manager --cov-report=term`
  - Verify: Coverage >80%

- [ ] **JOB1-010.4** - Add missing edge case tests for FarmerPreferenceManager
  - Path: `services/crop_taxonomy/tests/test_preference_manager.py`
  - Add tests for edge cases
  - Verify: `pytest services/crop_taxonomy/tests/test_preference_manager.py --collect-only`

- [ ] **JOB1-010.5** - Run all service tests
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_search.py tests/test_preference_manager.py -v`
  - Verify: All tests pass

- [ ] **JOB1-010.6** - Generate coverage report
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/ --cov=src --cov-report=html`
  - Verify: Coverage >80%

- [ ] **JOB1-010.99** - Commit additional tests
  - Command: `git add services/crop_taxonomy/tests/ && git commit -m "JOB1-010: Implement comprehensive unit tests for services"`
  - Verify: `git log -1 --oneline`

---

## JOB1-011: Implement Integration Tests for API

### Tasks (TDD Workflow)

- [ ] **JOB1-011.1.test** - Create integration test file
  - Path: `services/crop_taxonomy/tests/test_api.py`
  - Create test file with TestClient imports
  - Verify: `ls services/crop_taxonomy/tests/test_api.py`

- [ ] **JOB1-011.2.test** - Write integration test for search workflow
  - Path: `services/crop_taxonomy/tests/test_api.py`
  - Add `test_search_workflow_integration()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_api.py --collect-only`

- [ ] **JOB1-011.3.test** - Write integration test for preference workflow
  - Path: `services/crop_taxonomy/tests/test_api.py`
  - Add `test_preference_workflow_integration()` test method
  - Verify: `pytest services/crop_taxonomy/tests/test_api.py --collect-only`

- [ ] **JOB1-011.4.test** - Write performance integration test
  - Path: `services/crop_taxonomy/tests/test_api.py`
  - Add `test_search_performance_integration()` test with timing
  - Verify: `pytest services/crop_taxonomy/tests/test_api.py --collect-only`

- [ ] **JOB1-011.5.verify** - Run integration tests
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_api.py -v`
  - Verify: All tests pass

- [ ] **JOB1-011.6.verify** - Verify performance requirement
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_api.py::test_search_performance_integration -v`
  - Verify: Response time <2s

- [ ] **JOB1-011.99** - Commit integration tests
  - Command: `git add services/crop_taxonomy/tests/test_api.py && git commit -m "JOB1-011: Implement integration tests for API"`
  - Verify: `git log -1 --oneline`

---

## JOB1-012: Performance Optimization and Indexing

### Tasks

- [ ] **JOB1-012.1** - Run EXPLAIN ANALYZE on pest resistance query
  - Command: `psql -U postgres -d caain_soil_hub -c "EXPLAIN ANALYZE SELECT * FROM crop_filtering_attributes WHERE pest_resistance_traits @> '{\"corn_borer\": \"resistant\"}';"`
  - Verify: Query uses idx_pest_resistance_gin index

- [ ] **JOB1-012.2** - Run EXPLAIN ANALYZE on disease resistance query
  - Command: `psql -U postgres -d caain_soil_hub -c "EXPLAIN ANALYZE SELECT * FROM crop_filtering_attributes WHERE disease_resistance_traits @> '{\"rust\": \"resistant\"}';"`
  - Verify: Query uses idx_disease_resistance_gin index

- [ ] **JOB1-012.3** - Run EXPLAIN ANALYZE on market class query
  - Command: `psql -U postgres -d caain_soil_hub -c "EXPLAIN ANALYZE SELECT * FROM crop_filtering_attributes WHERE market_class_filters @> '{\"organic_certified\": true}';"`
  - Verify: Query uses idx_market_class_gin index

- [ ] **JOB1-012.4** - Check for missing indexes
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE tablename = 'crop_filtering_attributes';"`
  - Verify: Review statistics for optimization opportunities

- [ ] **JOB1-012.5** - Add any missing indexes if needed
  - Command: `psql -U postgres -d caain_soil_hub -c "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_yield_stability ON crop_filtering_attributes(yield_stability_score DESC);"`
  - Verify: Index created

- [ ] **JOB1-012.6** - Run performance test suite
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/test_crop_search.py::test_search_performance -v`
  - Verify: All queries <2s

- [ ] **JOB1-012.7** - Check for N+1 query problems
  - Command: Enable SQLAlchemy query logging and review logs
  - Verify: No N+1 patterns detected

- [ ] **JOB1-012.99** - Commit performance optimizations
  - Command: `git add services/crop_taxonomy/migrations/ && git commit -m "JOB1-012: Performance optimization and indexing"`
  - Verify: `git log -1 --oneline`

---

## JOB1-013: Create Service Documentation

### Tasks

- [ ] **JOB1-013.1** - Create README.md file
  - Path: `services/crop_taxonomy/README.md`
  - Add service overview, setup instructions
  - Verify: `cat services/crop_taxonomy/README.md`

- [ ] **JOB1-013.2** - Document API endpoints
  - Path: `services/crop_taxonomy/README.md`
  - Add API endpoint documentation with examples
  - Verify: Check API docs in README

- [ ] **JOB1-013.3** - Add code examples
  - Path: `services/crop_taxonomy/README.md`
  - Add usage examples for each endpoint
  - Verify: Check examples in README

- [ ] **JOB1-013.4** - Document database schema
  - Path: `services/crop_taxonomy/README.md`
  - Add schema documentation
  - Verify: Check schema docs in README

- [ ] **JOB1-013.5** - Add troubleshooting section
  - Path: `services/crop_taxonomy/README.md`
  - Add common issues and solutions
  - Verify: Check troubleshooting section

- [ ] **JOB1-013.99** - Commit documentation
  - Command: `git add services/crop_taxonomy/README.md && git commit -m "JOB1-013: Create service documentation"`
  - Verify: `git log -1 --oneline`

---

## JOB1-014: Agricultural Expert Review

### Tasks

- [ ] **JOB1-014.1** - Create test scenarios document
  - Path: `services/crop_taxonomy/docs/test_scenarios.md`
  - Document test scenarios for expert review
  - Verify: `cat services/crop_taxonomy/docs/test_scenarios.md`

- [ ] **JOB1-014.2** - Prepare sample queries for corn varieties
  - Create sample queries for corn with different filters
  - Verify: Queries return reasonable results

- [ ] **JOB1-014.3** - Prepare sample queries for soybean varieties
  - Create sample queries for soybean with different filters
  - Verify: Queries return reasonable results

- [ ] **JOB1-014.4** - Validate pest resistance classifications
  - Review pest resistance data with agricultural knowledge
  - Verify: Classifications are accurate

- [ ] **JOB1-014.5** - Validate disease resistance classifications
  - Review disease resistance data with agricultural knowledge
  - Verify: Classifications are accurate

- [ ] **JOB1-014.6** - Document expert feedback
  - Path: `services/crop_taxonomy/docs/expert_review.md`
  - Document feedback and required changes
  - Verify: `cat services/crop_taxonomy/docs/expert_review.md`

- [ ] **JOB1-014.7** - Implement expert feedback changes
  - Make necessary changes based on feedback
  - Verify: Changes implemented

- [ ] **JOB1-014.99** - Commit expert review documentation
  - Command: `git add services/crop_taxonomy/docs/ && git commit -m "JOB1-014: Agricultural expert review and validation"`
  - Verify: `git log -1 --oneline`

---

## JOB1-015: Final Integration and Deployment Preparation

### Tasks

- [ ] **JOB1-015.1** - Start service on port 8007
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && uvicorn src.main:app --port 8007 &`
  - Verify: `curl http://localhost:8007/health`

- [ ] **JOB1-015.2** - Run full test suite
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/ -v --cov=src`
  - Verify: All tests pass, coverage >80%

- [ ] **JOB1-015.3** - Test all API endpoints manually
  - Test /health, /, /search, /preferences endpoints
  - Verify: All endpoints working

- [ ] **JOB1-015.4** - Create mock endpoints for dependencies
  - Document which external services are mocked
  - Verify: Service runs independently

- [ ] **JOB1-015.5** - Generate final coverage report
  - Command: `cd services/crop_taxonomy && source venv/bin/activate && pytest tests/ --cov=src --cov-report=html`
  - Verify: `open services/crop_taxonomy/htmlcov/index.html`

- [ ] **JOB1-015.6** - Review and update documentation
  - Review README.md for completeness
  - Verify: Documentation is complete

- [ ] **JOB1-015.7** - Create deployment checklist
  - Path: `services/crop_taxonomy/DEPLOYMENT.md`
  - Document deployment steps
  - Verify: `cat services/crop_taxonomy/DEPLOYMENT.md`

- [ ] **JOB1-015.8** - Tag service as ready for integration
  - Command: `git tag -a crop-taxonomy-v1.0.0 -m "Crop Taxonomy Service ready for integration"`
  - Verify: `git tag -l`

- [ ] **JOB1-015.99** - Final commit for Job 1
  - Command: `git add services/crop_taxonomy/ && git commit -m "JOB1-015: Final integration and deployment preparation - Crop Taxonomy Service complete"`
  - Verify: `git log -1 --oneline`

- [ ] **JOB1-015.100** - Push to repository
  - Command: `git push origin main && git push --tags`
  - Verify: `git status`

---

## Job 1 Summary

**Total Tasks**: ~200+ granular tasks
**Completion Criteria**:
- ✅ All 15 tickets complete
- ✅ All tests passing (>80% coverage)
- ✅ Service running on port 8007
- ✅ Performance requirements met (<2s)
- ✅ Agricultural expert validation complete
- ✅ Documentation complete
- ✅ Ready for integration phase