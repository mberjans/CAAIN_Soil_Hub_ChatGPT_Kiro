# Job 4: Farm Location Services - TDD Checklist

**Service**: Location Management Service (Port 8009)  
**Total Tickets**: 11  
**Estimated Timeline**: 2-3 weeks  
**Related Files**: `docs/tickets-job-4-location-services.md`, `docs/parallel-job-4-location-services.md`

---

## JOB4-001: Setup Location Service Structure

### Tasks

- [x] **JOB4-001.1** - Create service directory
  - Command: `mkdir -p services/location-management/src/{models,services,api,schemas}`
  - Verify: `ls -la services/location-management/src/`

- [x] **JOB4-001.2** - Create tests and migrations directories
  - Command: `mkdir -p services/location-management/{tests,migrations}`
  - Verify: `ls -ld services/location-management/tests`

- [x] **JOB4-001.3** - Create __init__.py files
  - Command: `touch services/location-management/src/__init__.py services/location-management/src/{models,services,api,schemas}/__init__.py services/location-management/tests/__init__.py`
  - Verify: `find services/location-management/src -name "__init__.py" | wc -l`

- [x] **JOB4-001.4** - Create virtual environment
  - Command: `cd services/location-management && python3 -m venv venv`
  - Verify: `ls services/location-management/venv/bin/python`

- [x] **JOB4-001.99** - Commit directory structure
  - Command: `git add services/location-management && git commit -m "JOB4-001: Setup location service structure"`
  - Verify: `git log -1 --oneline`

---

## JOB4-002: Install Dependencies with PostGIS Support

### Tasks

- [x] **JOB4-002.1** - Create requirements.txt with geospatial libraries
  - Path: `services/location-management/requirements.txt`
  - Content: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, GeoAlchemy2, geopy, shapely, pytest, pytest-asyncio, pytest-cov, httpx
  - Verify: `cat services/location-management/requirements.txt`

- [ ] **JOB4-002.2** - Install dependencies
  - Command: `cd services/location-management && source venv/bin/activate && pip install -r requirements.txt`
  - Verify: `pip list | grep GeoAlchemy2`

- [ ] **JOB4-002.3** - Verify GeoAlchemy2 installation
  - Command: `python -c "import geoalchemy2; print('GeoAlchemy2 OK')"`
  - Verify: GeoAlchemy2 working

- [ ] **JOB4-002.4** - Verify geopy installation
  - Command: `python -c "import geopy; print('geopy OK')"`
  - Verify: geopy working

- [ ] **JOB4-002.5** - Verify shapely installation
  - Command: `python -c "import shapely; print('shapely OK')"`
  - Verify: shapely working

- [ ] **JOB4-002.6** - Enable PostGIS extension
  - Command: `psql -U postgres -d caain_soil_hub -c "CREATE EXTENSION IF NOT EXISTS postgis;"`
  - Verify: `psql -U postgres -d caain_soil_hub -c "SELECT PostGIS_version();"`

- [ ] **JOB4-002.99** - Commit requirements
  - Command: `git add services/location-management/requirements.txt && git commit -m "JOB4-002: Add geospatial dependencies"`
  - Verify: `git log -1 --oneline`

---

## JOB4-003: Create PostGIS Database Schema

### Tasks (TDD Workflow)

- [ ] **JOB4-003.1.test** - Create test file for location models
  - Path: `services/location-management/tests/test_location_models.py`
  - Create test file
  - Verify: `ls services/location-management/tests/test_location_models.py`

- [ ] **JOB4-003.2.test** - Write test for FarmLocation model
  - Path: `services/location-management/tests/test_location_models.py`
  - Add `test_farm_location_creation()` test
  - Verify: `pytest services/location-management/tests/test_location_models.py --collect-only`

- [ ] **JOB4-003.3.test** - Write test for Field model with POLYGON
  - Path: `services/location-management/tests/test_location_models.py`
  - Add `test_field_creation()` test
  - Verify: `pytest services/location-management/tests/test_location_models.py --collect-only`

- [ ] **JOB4-003.4.impl** - Create location_models.py
  - Path: `services/location-management/src/models/location_models.py`
  - Implement FarmLocation and Field models with Geometry columns
  - Verify: `python -c "from src.models.location_models import FarmLocation, Field; print('OK')"`

- [ ] **JOB4-003.5.impl** - Create migration SQL
  - Path: `services/location-management/migrations/004_location_schema.sql`
  - Write CREATE TABLE statements with PostGIS geometry columns
  - Verify: `cat services/location-management/migrations/004_location_schema.sql`

- [ ] **JOB4-003.6.impl** - Add GIST spatial indexes to migration
  - Path: `services/location-management/migrations/004_location_schema.sql`
  - Add CREATE INDEX statements using GIST
  - Verify: `grep "USING GIST" services/location-management/migrations/004_location_schema.sql`

- [ ] **JOB4-003.7.impl** - Add sample data to migration
  - Path: `services/location-management/migrations/004_location_schema.sql`
  - Add INSERT statements with ST_GeomFromText
  - Verify: `grep "ST_GeomFromText" services/location-management/migrations/004_location_schema.sql`

- [ ] **JOB4-003.8.impl** - Run migration
  - Command: `psql -U postgres -d caain_soil_hub -f services/location-management/migrations/004_location_schema.sql`
  - Verify: `psql -U postgres -d caain_soil_hub -c "\d farm_locations"`

- [ ] **JOB4-003.9.verify** - Verify POINT geometry column
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT column_name, udt_name FROM information_schema.columns WHERE table_name='farm_locations' AND column_name='coordinates';"`
  - Verify: Column type is geometry

- [ ] **JOB4-003.10.verify** - Verify GIST indexes created
  - Command: `psql -U postgres -d caain_soil_hub -c "\di idx_farm_locations_coordinates"`
  - Verify: Index exists with GIST method

- [ ] **JOB4-003.11.verify** - Test spatial query
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT id, name, ST_AsText(coordinates) FROM farm_locations LIMIT 5;"`
  - Verify: Returns location data

- [ ] **JOB4-003.12.verify** - Run model tests
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/test_location_models.py -v`
  - Verify: All tests pass

- [ ] **JOB4-003.99** - Commit database schema
  - Command: `git add services/location-management/src/models/ services/location-management/migrations/ services/location-management/tests/test_location_models.py && git commit -m "JOB4-003: Create PostGIS database schema"`
  - Verify: `git log -1 --oneline`

---

## JOB4-004: Create Pydantic Schemas

### Tasks (TDD Workflow)

- [ ] **JOB4-004.1.test** - Create test file for schemas
  - Path: `services/location-management/tests/test_location_schemas.py`
  - Create test file
  - Verify: `ls services/location-management/tests/test_location_schemas.py`

- [ ] **JOB4-004.2.test** - Write test for LocationCreate schema
  - Path: `services/location-management/tests/test_location_schemas.py`
  - Add `test_location_create_valid()` test
  - Verify: `pytest services/location-management/tests/test_location_schemas.py --collect-only`

- [ ] **JOB4-004.3.test** - Write test for coordinate validation
  - Path: `services/location-management/tests/test_location_schemas.py`
  - Add `test_coordinate_validation()` test
  - Verify: `pytest services/location-management/tests/test_location_schemas.py --collect-only`

- [ ] **JOB4-004.4.impl** - Create location_schemas.py
  - Path: `services/location-management/src/schemas/location_schemas.py`
  - Implement LocationCreate, LocationResponse, NearbySearchRequest schemas
  - Verify: `python -c "from src.schemas.location_schemas import LocationCreate; print('OK')"`

- [ ] **JOB4-004.5.impl** - Add coordinate validators
  - Path: `services/location-management/src/schemas/location_schemas.py`
  - Add @field_validator for latitude/longitude ranges
  - Verify: Check validators in schema

- [ ] **JOB4-004.6.verify** - Run schema tests
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/test_location_schemas.py -v`
  - Verify: All tests pass

- [ ] **JOB4-004.99** - Commit schemas
  - Command: `git add services/location-management/src/schemas/ services/location-management/tests/test_location_schemas.py && git commit -m "JOB4-004: Create Pydantic schemas"`
  - Verify: `git log -1 --oneline`

---

## JOB4-005: Create FastAPI Main Application

### Tasks (TDD Workflow)

- [ ] **JOB4-005.1.test** - Create test file for main app
  - Path: `services/location-management/tests/test_main.py`
  - Create test file
  - Verify: `ls services/location-management/tests/test_main.py`

- [ ] **JOB4-005.2.test** - Write test for health endpoint
  - Path: `services/location-management/tests/test_main.py`
  - Add `test_health_endpoint()` test
  - Verify: `pytest services/location-management/tests/test_main.py --collect-only`

- [ ] **JOB4-005.3.impl** - Create main.py
  - Path: `services/location-management/src/main.py`
  - Create FastAPI app with health endpoint
  - Verify: `python -c "from src.main import app; print(app.title)"`

- [ ] **JOB4-005.4.verify** - Start service on port 8009
  - Command: `cd services/location-management && source venv/bin/activate && uvicorn src.main:app --port 8009 &`
  - Verify: `curl http://localhost:8009/health`

- [ ] **JOB4-005.5.verify** - Stop service
  - Command: `pkill -f "uvicorn src.main:app --port 8009"`
  - Verify: Service stopped

- [ ] **JOB4-005.99** - Commit main app
  - Command: `git add services/location-management/src/main.py services/location-management/tests/test_main.py && git commit -m "JOB4-005: Create FastAPI main application"`
  - Verify: `git log -1 --oneline`

---

## JOB4-006: Implement Geocoding Service

### Tasks (TDD Workflow)

- [ ] **JOB4-006.1.test** - Create test file for geocoding service
  - Path: `services/location-management/tests/test_geocoding.py`
  - Create test file
  - Verify: `ls services/location-management/tests/test_geocoding.py`

- [ ] **JOB4-006.2.test** - Write test for forward geocoding
  - Path: `services/location-management/tests/test_geocoding.py`
  - Add `test_geocode_address()` test
  - Verify: `pytest services/location-management/tests/test_geocoding.py --collect-only`

- [ ] **JOB4-006.3.test** - Write test for reverse geocoding
  - Path: `services/location-management/tests/test_geocoding.py`
  - Add `test_reverse_geocode()` test
  - Verify: `pytest services/location-management/tests/test_geocoding.py --collect-only`

- [ ] **JOB4-006.4.test** - Write test for fallback mechanism
  - Path: `services/location-management/tests/test_geocoding.py`
  - Add `test_geocoding_fallback()` test
  - Verify: `pytest services/location-management/tests/test_geocoding.py --collect-only`

- [ ] **JOB4-006.5.impl** - Create geocoding_service.py
  - Path: `services/location-management/src/services/geocoding_service.py`
  - Create GeocodingService class
  - Verify: `python -c "from src.services.geocoding_service import GeocodingService; print('OK')"`

- [ ] **JOB4-006.6.impl** - Implement Nominatim provider
  - Path: `services/location-management/src/services/geocoding_service.py`
  - Add Nominatim geocoder initialization
  - Verify: Check geocoder in __init__

- [ ] **JOB4-006.7.impl** - Implement geocode_address method
  - Path: `services/location-management/src/services/geocoding_service.py`
  - Add geocode_address with fallback logic
  - Verify: Check method in file

- [ ] **JOB4-006.8.impl** - Implement reverse_geocode method
  - Path: `services/location-management/src/services/geocoding_service.py`
  - Add reverse_geocode method
  - Verify: Check method in file

- [ ] **JOB4-006.9.verify** - Run geocoding tests
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/test_geocoding.py -v`
  - Verify: All tests pass

- [ ] **JOB4-006.99** - Commit geocoding service
  - Command: `git add services/location-management/src/services/geocoding_service.py services/location-management/tests/test_geocoding.py && git commit -m "JOB4-006: Implement geocoding service"`
  - Verify: `git log -1 --oneline`

---

## JOB4-007: Implement Location Service with Geospatial Queries

### Tasks (TDD Workflow)

- [ ] **JOB4-007.1.test** - Create test file for location service
  - Path: `services/location-management/tests/test_location_service.py`
  - Create test file
  - Verify: `ls services/location-management/tests/test_location_service.py`

- [ ] **JOB4-007.2.test** - Write test for create_location
  - Path: `services/location-management/tests/test_location_service.py`
  - Add `test_create_location()` test
  - Verify: `pytest services/location-management/tests/test_location_service.py --collect-only`

- [ ] **JOB4-007.3.test** - Write test for find_nearby_locations (ST_DWithin)
  - Path: `services/location-management/tests/test_location_service.py`
  - Add `test_find_nearby_locations()` test
  - Verify: `pytest services/location-management/tests/test_location_service.py --collect-only`

- [ ] **JOB4-007.4.test** - Write test for GPS validation
  - Path: `services/location-management/tests/test_location_service.py`
  - Add `test_gps_validation()` test
  - Verify: `pytest services/location-management/tests/test_location_service.py --collect-only`

- [ ] **JOB4-007.5.impl** - Create location_service.py
  - Path: `services/location-management/src/services/location_service.py`
  - Create LocationService class
  - Verify: `python -c "from src.services.location_service import LocationService; print('OK')"`

- [ ] **JOB4-007.6.impl** - Implement create_location method
  - Path: `services/location-management/src/services/location_service.py`
  - Add create_location with geocoding integration
  - Verify: Check method in file

- [ ] **JOB4-007.7.impl** - Implement get_user_locations method
  - Path: `services/location-management/src/services/location_service.py`
  - Add get_user_locations method
  - Verify: Check method in file

- [ ] **JOB4-007.8.impl** - Implement find_nearby_locations with ST_DWithin
  - Path: `services/location-management/src/services/location_service.py`
  - Add find_nearby_locations using PostGIS ST_DWithin
  - Verify: Check ST_DWithin query in method

- [ ] **JOB4-007.9.impl** - Implement GPS validation
  - Path: `services/location-management/src/services/location_service.py`
  - Add _validate_gps_coordinates method
  - Verify: Check validation in method

- [ ] **JOB4-007.10.verify** - Run location service tests
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/test_location_service.py -v`
  - Verify: All tests pass

- [ ] **JOB4-007.99** - Commit location service
  - Command: `git add services/location-management/src/services/location_service.py services/location-management/tests/test_location_service.py && git commit -m "JOB4-007: Implement location service with geospatial queries"`
  - Verify: `git log -1 --oneline`

---

## JOB4-008: Create Location API Routes

### Tasks (TDD Workflow)

- [ ] **JOB4-008.1.test** - Create test file for location routes
  - Path: `services/location-management/tests/test_location_routes.py`
  - Create test file
  - Verify: `ls services/location-management/tests/test_location_routes.py`

- [ ] **JOB4-008.2.test** - Write test for POST /locations endpoint
  - Path: `services/location-management/tests/test_location_routes.py`
  - Add `test_create_location_endpoint()` test
  - Verify: `pytest services/location-management/tests/test_location_routes.py --collect-only`

- [ ] **JOB4-008.3.test** - Write test for GET /locations/nearby endpoint
  - Path: `services/location-management/tests/test_location_routes.py`
  - Add `test_nearby_locations_endpoint()` test
  - Verify: `pytest services/location-management/tests/test_location_routes.py --collect-only`

- [ ] **JOB4-008.4.impl** - Create location_routes.py
  - Path: `services/location-management/src/api/location_routes.py`
  - Create router with location endpoints
  - Verify: Check router in file

- [ ] **JOB4-008.5.impl** - Implement POST /api/v1/locations/ endpoint
  - Path: `services/location-management/src/api/location_routes.py`
  - Add create_location endpoint
  - Verify: Check endpoint in file

- [ ] **JOB4-008.6.impl** - Implement GET /api/v1/locations/nearby endpoint
  - Path: `services/location-management/src/api/location_routes.py`
  - Add nearby_locations endpoint
  - Verify: Check endpoint in file

- [ ] **JOB4-008.7.impl** - Implement GET /api/v1/locations/{id} endpoint
  - Path: `services/location-management/src/api/location_routes.py`
  - Add get_location endpoint
  - Verify: Check endpoint in file

- [ ] **JOB4-008.8.impl** - Include router in main app
  - Path: `services/location-management/src/main.py`
  - Add app.include_router(location_routes.router)
  - Verify: Check router inclusion

- [ ] **JOB4-008.9.verify** - Test create location endpoint
  - Command: `curl -X POST http://localhost:8009/api/v1/locations/ -H "Content-Type: application/json" -d '{"name": "Test Farm", "address": "Ames, Iowa", "total_acres": 100}'`
  - Verify: Returns created location

- [ ] **JOB4-008.10.verify** - Test nearby locations endpoint
  - Command: `curl "http://localhost:8009/api/v1/locations/nearby?latitude=42.0&longitude=-93.0&radius_km=50"`
  - Verify: Returns nearby locations

- [ ] **JOB4-008.11.verify** - Run API tests
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/test_location_routes.py -v`
  - Verify: All tests pass

- [ ] **JOB4-008.99** - Commit API routes
  - Command: `git add services/location-management/src/api/location_routes.py services/location-management/tests/test_location_routes.py && git commit -m "JOB4-008: Create location API routes"`
  - Verify: `git log -1 --oneline`

---

## JOB4-009: Implement Validation Service

### Tasks (TDD Workflow)

- [ ] **JOB4-009.1.test** - Write test for agricultural zone validation
  - Path: `services/location-management/tests/test_validation_service.py`
  - Add `test_validate_agricultural_zone()` test
  - Verify: `pytest services/location-management/tests/test_validation_service.py --collect-only`

- [ ] **JOB4-009.2.impl** - Create validation_service.py
  - Path: `services/location-management/src/services/validation_service.py`
  - Create LocationValidationService class
  - Verify: `python -c "from src.services.validation_service import LocationValidationService; print('OK')"`

- [ ] **JOB4-009.3.impl** - Implement agricultural zone validation
  - Path: `services/location-management/src/services/validation_service.py`
  - Add validate_agricultural_zone method
  - Verify: Check method in file

- [ ] **JOB4-009.4.verify** - Run validation tests
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/test_validation_service.py -v`
  - Verify: All tests pass

- [ ] **JOB4-009.99** - Commit validation service
  - Command: `git add services/location-management/src/services/validation_service.py services/location-management/tests/test_validation_service.py && git commit -m "JOB4-009: Implement validation service"`
  - Verify: `git log -1 --oneline`

---

## JOB4-010: Implement Integration Tests

### Tasks

- [ ] **JOB4-010.1** - Create integration test file
  - Path: `services/location-management/tests/test_api_integration.py`
  - Create test file
  - Verify: `ls services/location-management/tests/test_api_integration.py`

- [ ] **JOB4-010.2** - Write end-to-end location workflow test
  - Path: `services/location-management/tests/test_api_integration.py`
  - Add `test_location_workflow()` test
  - Verify: `pytest services/location-management/tests/test_api_integration.py --collect-only`

- [ ] **JOB4-010.3** - Write geospatial query integration test
  - Path: `services/location-management/tests/test_api_integration.py`
  - Add `test_geospatial_queries()` test
  - Verify: `pytest services/location-management/tests/test_api_integration.py --collect-only`

- [ ] **JOB4-010.4** - Run integration tests
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/test_api_integration.py -v`
  - Verify: All tests pass

- [ ] **JOB4-010.5** - Generate coverage report
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/ --cov=src --cov-report=html`
  - Verify: Coverage >80%

- [ ] **JOB4-010.99** - Commit integration tests
  - Command: `git add services/location-management/tests/test_api_integration.py && git commit -m "JOB4-010: Implement integration tests"`
  - Verify: `git log -1 --oneline`

---

## JOB4-011: Final Integration Preparation

### Tasks

- [ ] **JOB4-011.1** - Start service on port 8009
  - Command: `cd services/location-management && source venv/bin/activate && uvicorn src.main:app --port 8009 &`
  - Verify: `curl http://localhost:8009/health`

- [ ] **JOB4-011.2** - Run full test suite
  - Command: `cd services/location-management && source venv/bin/activate && pytest tests/ -v`
  - Verify: All tests pass

- [ ] **JOB4-011.3** - Create README
  - Path: `services/location-management/README.md`
  - Add service documentation
  - Verify: `cat services/location-management/README.md`

- [ ] **JOB4-011.4** - Tag service as ready
  - Command: `git tag -a location-management-v1.0.0 -m "Location Management Service ready for integration"`
  - Verify: `git tag -l`

- [ ] **JOB4-011.99** - Final commit
  - Command: `git add services/location-management/ && git commit -m "JOB4-011: Final integration preparation - Location Management Service complete"`
  - Verify: `git log -1 --oneline`

- [ ] **JOB4-011.100** - Push to repository
  - Command: `git push origin main && git push --tags`
  - Verify: `git status`

---

## Job 4 Summary

**Total Tasks**: ~100+ granular tasks  
**Completion Criteria**:
- ✅ All 11 tickets complete
- ✅ All tests passing (>80% coverage)
- ✅ Service running on port 8009
- ✅ PostGIS geospatial queries working
- ✅ Geocoding working
- ✅ Documentation complete
- ✅ Ready for integration with JOB5


