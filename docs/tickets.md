# Job 4: Farm Location Services - Development Tickets

**Total Tickets**: 11  
**Estimated Timeline**: 2-3 weeks  
**Service**: Location Management Service (Port 8009)  
**Related Plan**: `docs/parallel-job-4-location-services.md`

---

## JOB4-001: Setup Location Service Structure

**Priority**: Critical  
**Estimated Effort**: 1 hour  
**Dependencies**: None (Can start immediately)  
**Blocks**: JOB4-002, JOB4-003, JOB4-004  
**Parallel Execution**: No

**Description**:
Create directory structure for location management service.

**Acceptance Criteria**:
- [ ] Directory structure created
- [ ] Virtual environment created

**Validation Commands**:
```bash
mkdir -p services/location-management/src/{models,services,api,schemas}
mkdir -p services/location-management/tests
cd services/location-management
python3 -m venv venv
source venv/bin/activate
```

**Related Tickets**: TICKET-008_farm-location-input-4.1

---

## JOB4-002: Install Dependencies with PostGIS Support

**Priority**: Critical  
**Estimated Effort**: 1 hour  
**Dependencies**: JOB4-001  
**Blocks**: JOB4-003, JOB4-004, JOB4-005  
**Parallel Execution**: No

**Description**:
Install dependencies including GeoAlchemy2 and geopy for geospatial operations.

**Acceptance Criteria**:
- [ ] GeoAlchemy2 installed
- [ ] geopy installed
- [ ] shapely installed
- [ ] PostGIS extension enabled in database

**Validation Commands**:
```bash
pip install -r requirements.txt
python -c "import geoalchemy2; import geopy; import shapely; print('Geospatial libs OK')"
psql -U postgres -d caain_soil_hub -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql -U postgres -d caain_soil_hub -c "SELECT PostGIS_version();"
```

**Related Tickets**: TICKET-008_farm-location-input-4.1

---

## JOB4-003: Create PostGIS Database Schema

**Priority**: Critical  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB4-002  
**Blocks**: JOB4-006  
**Parallel Execution**: Can run parallel with JOB4-004, JOB4-005

**Description**:
Create database schema with PostGIS geometry columns for farm locations and field boundaries.

**Acceptance Criteria**:
- [ ] farm_locations table created with POINT geometry
- [ ] fields table created with POLYGON geometry
- [ ] GIST spatial indexes created
- [ ] Sample data inserted
- [ ] Spatial queries working

**Technical Details**:
See `docs/parallel-job-4-location-services.md` for complete SQL schema.

**Validation Commands**:
```bash
psql -U postgres -d caain_soil_hub -f migrations/004_location_schema.sql
psql -U postgres -d caain_soil_hub -c "SELECT id, name, ST_AsText(coordinates) FROM farm_locations LIMIT 5;"
psql -U postgres -d caain_soil_hub -c "\d farm_locations"
```

**Related Tickets**: TICKET-008_farm-location-input-4.2

---

## JOB4-004: Create Pydantic Schemas

**Priority**: High  
**Estimated Effort**: 2 hours  
**Dependencies**: JOB4-002  
**Blocks**: JOB4-007, JOB4-008  
**Parallel Execution**: Can run parallel with JOB4-003, JOB4-005

**Description**:
Create schemas for location creation, updates, and geospatial queries.

**Acceptance Criteria**:
- [ ] LocationCreate schema created
- [ ] LocationResponse schema created
- [ ] Coordinate validation working
- [ ] Field boundary schemas created

**Related Tickets**: TICKET-008_farm-location-input-4.3

---

## JOB4-005: Create FastAPI Main Application

**Priority**: High  
**Estimated Effort**: 1 hour  
**Dependencies**: JOB4-002  
**Blocks**: JOB4-007, JOB4-008  
**Parallel Execution**: Can run parallel with JOB4-003, JOB4-004

**Description**:
Create main FastAPI app on port 8009.

**Acceptance Criteria**:
- [ ] FastAPI app created
- [ ] Health endpoint working
- [ ] App starts on port 8009

**Validation Commands**:
```bash
uvicorn src.main:app --port 8009 &
curl http://localhost:8009/health
```

**Related Tickets**: TICKET-008_farm-location-input-4.1

---

## JOB4-006: Implement Geocoding Service

**Priority**: Critical  
**Estimated Effort**: 6 hours  
**Dependencies**: JOB4-002, JOB4-003  
**Blocks**: JOB4-007  
**Parallel Execution**: Can run parallel with JOB4-009

**Description**:
Implement GeocodingService with fallback providers (Nominatim, Google Maps).

**Acceptance Criteria**:
- [ ] GeocodingService class implemented
- [ ] Nominatim provider working
- [ ] Fallback mechanism working
- [ ] Reverse geocoding working
- [ ] Unit tests passing

**Technical Details**:
See `docs/parallel-job-4-location-services.md` for complete implementation.

**Validation Commands**:
```bash
pytest tests/test_geocoding.py -v
```

**Related Tickets**: TICKET-008_farm-location-input-4.3

---

## JOB4-007: Implement Location Service with Geospatial Queries

**Priority**: Critical  
**Estimated Effort**: 1 day  
**Dependencies**: JOB4-003, JOB4-004, JOB4-006  
**Blocks**: JOB4-008  
**Parallel Execution**: No

**Description**:
Implement LocationService with PostGIS spatial queries for nearby farms.

**Acceptance Criteria**:
- [ ] LocationService class implemented
- [ ] Create location working
- [ ] Get user locations working
- [ ] Find nearby locations working (ST_DWithin)
- [ ] GPS validation working
- [ ] Unit tests passing

**Technical Details**:
See `docs/parallel-job-4-location-services.md` for complete implementation.

**Validation Commands**:
```bash
pytest tests/test_location_service.py -v
```

**Related Tickets**: TICKET-008_farm-location-input-4.4, TICKET-008_farm-location-input-5.1

---

## JOB4-008: Create Location API Routes

**Priority**: Critical  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB4-004, JOB4-005, JOB4-007  
**Blocks**: JOB4-009  
**Parallel Execution**: No

**Description**:
Create API endpoints for location CRUD and geospatial queries.

**Acceptance Criteria**:
- [ ] POST /api/v1/locations/ endpoint working
- [ ] GET /api/v1/locations/nearby endpoint working
- [ ] GET /api/v1/locations/{id} endpoint working
- [ ] API tests passing

**Validation Commands**:
```bash
curl -X POST http://localhost:8009/api/v1/locations/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Farm", "address": "Ames, Iowa", "total_acres": 100}'

curl "http://localhost:8009/api/v1/locations/nearby?latitude=42.0&longitude=-93.0&radius_km=50"
```

**Related Tickets**: TICKET-008_farm-location-input-4.1

---

## JOB4-009: Implement Validation Service

**Priority**: High  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB4-006  
**Blocks**: JOB4-010  
**Parallel Execution**: Can run parallel with JOB4-007

**Description**:
Implement LocationValidationService for agricultural suitability checks.

**Acceptance Criteria**:
- [ ] LocationValidationService class implemented
- [ ] Agricultural zone validation working
- [ ] Climate zone detection working
- [ ] Unit tests passing

**Related Tickets**: TICKET-008_farm-location-input-5.2

---

## JOB4-010: Implement Integration Tests

**Priority**: High  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB4-008, JOB4-009  
**Blocks**: JOB4-011  
**Parallel Execution**: No

**Description**:
Create integration tests for API endpoints and geospatial queries.

**Acceptance Criteria**:
- [ ] Integration tests created
- [ ] Geospatial query tests passing
- [ ] Geocoding tests passing
- [ ] All tests passing

**Validation Commands**:
```bash
pytest tests/ -v --cov=src
```

**Related Tickets**: TICKET-008_farm-location-input-6.1

---

## JOB4-011: Final Integration Preparation

**Priority**: Critical  
**Estimated Effort**: 2 hours  
**Dependencies**: JOB4-010  
**Blocks**: None (Ready for integration)  
**Parallel Execution**: No

**Description**:
Final checks and preparation for integration with weather service.

**Acceptance Criteria**:
- [ ] Service runs on port 8009
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Ready for integration with JOB5

**Validation Commands**:
```bash
uvicorn src.main:app --port 8009 &
pytest tests/ -v
curl http://localhost:8009/health
```

**Related Tickets**: TICKET-008_farm-location-input-7.1

---

## Summary

**Total Tickets**: 11  
**Critical Path**: JOB4-001 → JOB4-002 → JOB4-003 → JOB4-006 → JOB4-007 → JOB4-008 → JOB4-010 → JOB4-011  
**Estimated Total Time**: 2-3 weeks  
**Parallel Opportunities**: JOB4-003/004/005, JOB4-006/009


