# Job 2: Fertilizer Strategy Optimization - Development Tickets

**Total Tickets**: 12  
**Estimated Timeline**: 3-4 weeks  
**Service**: Fertilizer Optimization Service (Port 8008)  
**Related Plan**: `docs/parallel-job-2-fertilizer-optimization.md`

---

## JOB2-001: Setup Fertilizer Optimization Service Structure

**Priority**: Critical  
**Estimated Effort**: 1 hour  
**Dependencies**: None (Can start immediately)  
**Blocks**: JOB2-002, JOB2-003, JOB2-004  
**Parallel Execution**: No

**Description**:
Create directory structure and initialize service following microservices pattern.

**Acceptance Criteria**:
- [ ] Directory structure created
- [ ] All __init__.py files present
- [ ] Virtual environment created

**Validation Commands**:
```bash
mkdir -p services/fertilizer-optimization/src/{models,services,providers,api,schemas}
mkdir -p services/fertilizer-optimization/tests
cd services/fertilizer-optimization
python3 -m venv venv
source venv/bin/activate
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.1

---

## JOB2-002: Install Dependencies

**Priority**: Critical  
**Estimated Effort**: 30 minutes  
**Dependencies**: JOB2-001  
**Blocks**: JOB2-003, JOB2-004, JOB2-005  
**Parallel Execution**: No

**Description**:
Create requirements.txt and install all dependencies including scipy for optimization.

**Acceptance Criteria**:
- [ ] requirements.txt created
- [ ] All dependencies installed
- [ ] scipy, numpy working

**Validation Commands**:
```bash
pip install -r requirements.txt
python -c "import scipy; import numpy; print('OK')"
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.1

---

## JOB2-003: Create Database Schema for Price Tracking

**Priority**: Critical  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB2-002  
**Blocks**: JOB2-006  
**Parallel Execution**: Can run parallel with JOB2-004, JOB2-005

**Description**:
Create TimescaleDB hypertables for fertilizer price tracking with time series optimization.

**Acceptance Criteria**:
- [ ] fertilizer_types table created
- [ ] fertilizer_prices hypertable created
- [ ] price_trends table created
- [ ] TimescaleDB extension enabled
- [ ] Sample data inserted

**Technical Details**:
See `docs/parallel-job-2-fertilizer-optimization.md` for complete SQL schema.

**Validation Commands**:
```bash
psql -U postgres -d caain_soil_hub -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"
psql -U postgres -d caain_soil_hub -f migrations/002_fertilizer_prices_schema.sql
psql -U postgres -d caain_soil_hub -c "SELECT * FROM fertilizer_types;"
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.1

---

## JOB2-004: Create Pydantic Schemas

**Priority**: High  
**Estimated Effort**: 2 hours  
**Dependencies**: JOB2-002  
**Blocks**: JOB2-007, JOB2-008  
**Parallel Execution**: Can run parallel with JOB2-003, JOB2-005

**Description**:
Create request/response schemas for price tracking and optimization.

**Acceptance Criteria**:
- [ ] OptimizationRequest schema created
- [ ] OptimizationResponse schema created
- [ ] PriceData schemas created
- [ ] Validation working

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.2

---

## JOB2-005: Create FastAPI Main Application

**Priority**: High  
**Estimated Effort**: 1 hour  
**Dependencies**: JOB2-002  
**Blocks**: JOB2-007, JOB2-008  
**Parallel Execution**: Can run parallel with JOB2-003, JOB2-004

**Description**:
Create main FastAPI app with health check on port 8008.

**Acceptance Criteria**:
- [ ] FastAPI app created
- [ ] Health endpoint working
- [ ] App starts on port 8008

**Validation Commands**:
```bash
uvicorn src.main:app --port 8008 &
curl http://localhost:8008/health
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.1

---

## JOB2-006: Implement Price Tracking Service

**Priority**: Critical  
**Estimated Effort**: 1 day  
**Dependencies**: JOB2-003, JOB2-004  
**Blocks**: JOB2-007  
**Parallel Execution**: Can run parallel with JOB2-009

**Description**:
Implement FertilizerPriceTracker with multi-provider support and mock provider for development.

**Acceptance Criteria**:
- [ ] FertilizerPriceTracker class implemented
- [ ] MockPriceProvider working
- [ ] Price storage working
- [ ] Daily update function working
- [ ] Unit tests passing

**Technical Details**:
See `docs/parallel-job-2-fertilizer-optimization.md` for complete implementation.

**Validation Commands**:
```bash
pytest tests/test_price_tracker.py -v
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.1, TICKET-006_fertilizer-strategy-optimization-1.2

---

## JOB2-007: Create Price API Routes

**Priority**: High  
**Estimated Effort**: 3 hours  
**Dependencies**: JOB2-004, JOB2-005, JOB2-006  
**Blocks**: JOB2-010  
**Parallel Execution**: Can run parallel with JOB2-008

**Description**:
Create API endpoints for fetching current prices and triggering updates.

**Acceptance Criteria**:
- [ ] GET /api/v1/prices/fertilizer-current endpoint working
- [ ] POST /api/v1/prices/update-prices endpoint working
- [ ] API tests passing

**Validation Commands**:
```bash
curl http://localhost:8008/api/v1/prices/fertilizer-current
curl -X POST http://localhost:8008/api/v1/prices/update-prices
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.3

---

## JOB2-008: Implement Economic Optimizer

**Priority**: Critical  
**Estimated Effort**: 1.5 days  
**Dependencies**: JOB2-004, JOB2-005  
**Blocks**: JOB2-009  
**Parallel Execution**: Can run parallel with JOB2-006, JOB2-007

**Description**:
Implement multi-objective optimization using scipy.optimize for cost-effective fertilizer strategies.

**Acceptance Criteria**:
- [ ] EconomicOptimizer class implemented
- [ ] Multi-objective optimization working
- [ ] ROI calculation implemented
- [ ] Environmental impact assessment working
- [ ] Unit tests passing

**Technical Details**:
See `docs/parallel-job-2-fertilizer-optimization.md` for complete implementation with scipy.

**Validation Commands**:
```bash
pytest tests/test_economic_optimizer.py -v
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-1.3, TICKET-006_fertilizer-strategy-optimization-2.1

---

## JOB2-009: Create Optimization API Routes

**Priority**: Critical  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB2-004, JOB2-005, JOB2-008  
**Blocks**: JOB2-010  
**Parallel Execution**: Can run parallel with JOB2-007

**Description**:
Create API endpoint for fertilizer strategy optimization.

**Acceptance Criteria**:
- [ ] POST /api/v1/optimization/optimize-strategy endpoint working
- [ ] Request validation working
- [ ] Response includes recommendations and ROI
- [ ] API tests passing

**Validation Commands**:
```bash
curl -X POST http://localhost:8008/api/v1/optimization/optimize-strategy \
  -H "Content-Type: application/json" \
  -d '{"field_acres": 100, "nutrient_requirements": {"N": 150, "P": 60, "K": 40}, "yield_goal_bu_acre": 180, "available_fertilizers": [...]}'
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-2.2

---

## JOB2-010: Implement Integration Tests

**Priority**: High  
**Estimated Effort**: 6 hours  
**Dependencies**: JOB2-007, JOB2-009  
**Blocks**: JOB2-011  
**Parallel Execution**: No

**Description**:
Create comprehensive integration tests for API endpoints.

**Acceptance Criteria**:
- [ ] API integration tests created
- [ ] End-to-end optimization workflow tested
- [ ] Price tracking tested
- [ ] All tests passing

**Validation Commands**:
```bash
pytest tests/ -v --cov=src
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-3.1

---

## JOB2-011: Agricultural Validation and Documentation

**Priority**: High  
**Estimated Effort**: 4 hours  
**Dependencies**: JOB2-010  
**Blocks**: JOB2-012  
**Parallel Execution**: No

**Description**:
Validate optimization algorithms with agricultural expert and create documentation.

**Acceptance Criteria**:
- [ ] Nutrient calculations validated
- [ ] ROI assumptions documented
- [ ] README created
- [ ] API documentation complete

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-4.1

---

## JOB2-012: Final Integration Preparation

**Priority**: Critical  
**Estimated Effort**: 3 hours  
**Dependencies**: JOB2-011  
**Blocks**: None (Ready for integration)  
**Parallel Execution**: No

**Description**:
Final checks and preparation for integration with other services.

**Acceptance Criteria**:
- [ ] Service runs on port 8008
- [ ] All tests passing
- [ ] Mock endpoints for dependencies
- [ ] Ready for integration

**Validation Commands**:
```bash
uvicorn src.main:app --port 8008 &
pytest tests/ -v
curl http://localhost:8008/health
```

**Related Tickets**: TICKET-006_fertilizer-strategy-optimization-5.1

---

## Summary

**Total Tickets**: 12  
**Critical Path**: JOB2-001 → JOB2-002 → JOB2-003 → JOB2-006 → JOB2-007 → JOB2-010 → JOB2-011 → JOB2-012  
**Estimated Total Time**: 3-4 weeks  
**Parallel Opportunities**: JOB2-003/004/005, JOB2-006/008, JOB2-007/009


