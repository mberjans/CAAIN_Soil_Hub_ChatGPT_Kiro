# Job 2: Fertilizer Strategy Optimization - TDD Checklist

**Service**: Fertilizer Optimization Service (Port 8008)  
**Total Tickets**: 12  
**Estimated Timeline**: 3-4 weeks  
**Related Files**: `docs/tickets-job-2-fertilizer-optimization.md`, `docs/parallel-job-2-fertilizer-optimization.md`

---

## JOB2-001: Setup Fertilizer Optimization Service Structure

### Tasks

- [x] **JOB2-001.1** - Create service directory
  - Command: `mkdir -p services/fertilizer-optimization/src/{models,services,providers,api,schemas}`
  - Verify: `ls -la services/fertilizer-optimization/src/`

- [x] **JOB2-001.2** - Create tests and migrations directories
  - Command: `mkdir -p services/fertilizer-optimization/{tests,migrations}`
  - Verify: `ls -ld services/fertilizer-optimization/tests`

- [x] **JOB2-001.3** - Create __init__.py files
  - Command: `touch services/fertilizer-optimization/src/__init__.py services/fertilizer-optimization/src/{models,services,providers,api,schemas}/__init__.py services/fertilizer-optimization/tests/__init__.py`
  - Verify: `find services/fertilizer-optimization -name "__init__.py" | wc -l`

- [x] **JOB2-001.4** - Create virtual environment
  - Command: `cd services/fertilizer-optimization && python3 -m venv venv`
  - Verify: `ls services/fertilizer-optimization/venv/bin/python`

- [x] **JOB2-001.99** - Commit directory structure
  - Command: `git add services/fertilizer-optimization && git commit -m "JOB2-001: Setup fertilizer optimization service structure"`
  - Verify: `git log -1 --oneline`

---

## JOB2-002: Install Dependencies

### Tasks

- [x] **JOB2-002.1** - Create requirements.txt
  - Path: `services/fertilizer-optimization/requirements.txt`
  - Content: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, scipy, numpy, pytest, pytest-asyncio, pytest-cov, httpx
  - Verify: `cat services/fertilizer-optimization/requirements.txt`

- [x] **JOB2-002.2** - Install dependencies
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pip install -r requirements.txt`
  - Verify: `pip list | grep scipy`

- [x] **JOB2-002.3** - Verify scipy installation
  - Command: `python -c "import scipy; print(f'scipy: {scipy.__version__}')"`
  - Verify: scipy version displayed

- [x] **JOB2-002.4** - Verify numpy installation
  - Command: `python -c "import numpy; print(f'numpy: {numpy.__version__}')"`
  - Verify: numpy version displayed

- [x] **JOB2-002.99** - Commit requirements
  - Command: `git add services/fertilizer-optimization/requirements.txt && git commit -m "JOB2-002: Add requirements with scipy and numpy"`
  - Verify: `git log -1 --oneline`

---

## JOB2-003: Create Database Schema for Price Tracking

### Tasks (TDD Workflow)

- [x] **JOB2-003.1.test** - Create test file for price models
  - Path: `services/fertilizer-optimization/tests/test_price_models.py`
  - Create test file
  - Verify: `ls services/fertilizer-optimization/tests/test_price_models.py`

- [x] **JOB2-003.2.test** - Write test for FertilizerType model
  - Path: `services/fertilizer-optimization/tests/test_price_models.py`
  - Add `test_fertilizer_type_creation()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_price_models.py --collect-only`

- [x] **JOB2-003.3.test** - Write test for FertilizerPrice model
  - Path: `services/fertilizer-optimization/tests/test_price_models.py`
  - Add `test_fertilizer_price_creation()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_price_models.py --collect-only`

- [x] **JOB2-003.4.impl** - Create price_models.py
  - Path: `services/fertilizer-optimization/src/models/price_models.py`
  - Implement FertilizerType and FertilizerPrice models
  - Verify: `python -c "from src.models.price_models import FertilizerType, FertilizerPrice; print('OK')"`

- [x] **JOB2-003.5.impl** - Create migration SQL
  - Path: `services/fertilizer-optimization/migrations/002_fertilizer_prices_schema.sql`
  - Write CREATE TABLE statements
  - Verify: `cat services/fertilizer-optimization/migrations/002_fertilizer_prices_schema.sql`

- [x] **JOB2-003.6.impl** - Enable TimescaleDB extension
  - Command: `psql -U postgres -d caain_soil_hub -c "CREATE EXTENSION IF NOT EXISTS timescaledb;"`
  - Verify: `psql -U postgres -d caain_soil_hub -c "SELECT * FROM pg_extension WHERE extname='timescaledb';"`

- [x] **JOB2-003.7.impl** - Run migration to create tables
  - Command: `psql -U postgres -d caain_soil_hub -f services/fertilizer-optimization/migrations/002_fertilizer_prices_schema.sql`
  - Verify: `psql -U postgres -d caain_soil_hub -c "\dt fertilizer_types"`

- [x] **JOB2-003.8.impl** - Create hypertable for fertilizer_prices
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT create_hypertable('fertilizer_prices', 'price_date');"`
  - Verify: `psql -U postgres -d caain_soil_hub -c "SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name='fertilizer_prices';"`

- [ ] **JOB2-003.9.verify** - Verify tables created
  - Command: `psql -U postgres -d caain_soil_hub -c "\d fertilizer_prices"`
  - Verify: Table structure correct

- [x] **JOB2-003.10.verify** - Run unit tests
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pytest tests/test_price_models.py -v`
  - Verify: All tests pass

- [x] **JOB2-003.99** - Commit database schema
  - Command: `git add services/fertilizer-optimization/src/models/ services/fertilizer-optimization/migrations/ services/fertilizer-optimization/tests/test_price_models.py && git commit -m "JOB2-003: Create TimescaleDB schema for price tracking"`
  - Verify: `git log -1 --oneline`

---

## JOB2-004: Create Pydantic Schemas

### Tasks (TDD Workflow)

- [x] **JOB2-004.1.test** - Create test file for schemas
  - Path: `services/fertilizer-optimization/tests/test_optimization_schemas.py`
  - Create test file
  - Verify: `ls services/fertilizer-optimization/tests/test_optimization_schemas.py`

- [x] **JOB2-004.2.test** - Write test for OptimizationRequest schema
  - Path: `services/fertilizer-optimization/tests/test_optimization_schemas.py`
  - Add `test_optimization_request_valid()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_optimization_schemas.py --collect-only`

- [x] **JOB2-004.3.impl** - Create optimization_schemas.py
  - Path: `services/fertilizer-optimization/src/schemas/optimization_schemas.py`
  - Implement OptimizationRequest, OptimizationResponse, PriceData schemas
  - Verify: `python -c "from src.schemas.optimization_schemas import OptimizationRequest; print('OK')"`

- [x] **JOB2-004.4.verify** - Run schema tests
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pytest tests/test_optimization_schemas.py -v`
  - Verify: All tests pass

- [x] **JOB2-004.99** - Commit schemas
  - Command: `git add services/fertilizer-optimization/src/schemas/ services/fertilizer-optimization/tests/test_optimization_schemas.py && git commit -m "JOB2-004: Create Pydantic schemas"`
  - Verify: `git log -1 --oneline`

---

## JOB2-005: Create FastAPI Main Application

### Tasks (TDD Workflow)

- [x] **JOB2-005.1.test** - Create test file for main app
  - Path: `services/fertilizer-optimization/tests/test_main.py`
  - Create test file
  - Verify: `ls services/fertilizer-optimization/tests/test_main.py`

- [x] **JOB2-005.2.test** - Write test for health endpoint
  - Path: `services/fertilizer-optimization/tests/test_main.py`
  - Add `test_health_endpoint()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_main.py --collect-only`

- [x] **JOB2-005.3.impl** - Create main.py
  - Path: `services/fertilizer-optimization/src/main.py`
  - Create FastAPI app with health endpoint
  - Verify: `python -c "from src.main import app; print(app.title)"`

- [x] **JOB2-005.4.verify** - Start service on port 8008
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && uvicorn src.main:app --port 8008 &`
  - Verify: `curl http://localhost:8008/health`

- [x] **JOB2-005.5.verify** - Stop service
  - Command: `pkill -f "uvicorn src.main:app --port 8008"`
  - Verify: Service stopped

- [x] **JOB2-005.99** - Commit main app
  - Command: `git add services/fertilizer-optimization/src/main.py services/fertilizer-optimization/tests/test_main.py && git commit -m "JOB2-005: Create FastAPI main application"`
  - Verify: `git log -1 --oneline`

---

## JOB2-006: Implement Price Tracking Service

### Tasks (TDD Workflow)

- [x] **JOB2-006.1.test** - Create test file for price tracker
  - Path: `services/fertilizer-optimization/tests/test_price_tracker.py`
  - Create test file
  - Verify: `ls services/fertilizer-optimization/tests/test_price_tracker.py`

- [x] **JOB2-006.2.test** - Write test for MockPriceProvider
  - Path: `services/fertilizer-optimization/tests/test_price_tracker.py`
  - Add `test_mock_price_provider()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_price_tracker.py --collect-only`

- [x] **JOB2-006.3.test** - Write test for FertilizerPriceTracker
  - Path: `services/fertilizer-optimization/tests/test_price_tracker.py`
  - Add `test_price_tracker_fetch()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_price_tracker.py --collect-only`

- [x] **JOB2-006.4.impl** - Create MockPriceProvider
  - Path: `services/fertilizer-optimization/src/providers/mock_price_provider.py`
  - Implement mock provider
  - Verify: `python -c "from src.providers.mock_price_provider import MockPriceProvider; print('OK')"`

- [x] **JOB2-006.5.impl** - Create FertilizerPriceTracker
  - Path: `services/fertilizer-optimization/src/services/price_tracker.py`
  - Implement price tracker with multi-provider support
  - Verify: `python -c "from src.services.price_tracker import FertilizerPriceTracker; print('OK')"`

- [x] **JOB2-006.6.verify** - Run price tracker tests
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pytest tests/test_price_tracker.py -v`
  - Verify: All tests pass

- [x] **JOB2-006.99** - Commit price tracker
  - Command: `git add services/fertilizer-optimization/src/services/price_tracker.py services/fertilizer-optimization/src/providers/ services/fertilizer-optimization/tests/test_price_tracker.py && git commit -m "JOB2-006: Implement price tracking service"`
  - Verify: `git log -1 --oneline`

---

## JOB2-007: Create Price API Routes

### Tasks (TDD Workflow)

- [x] **JOB2-007.1.test** - Create test file for price routes
  - Path: `services/fertilizer-optimization/tests/test_price_routes.py`
  - Create test file
  - Verify: `ls services/fertilizer-optimization/tests/test_price_routes.py`

- [x] **JOB2-007.2.test** - Write test for GET /prices/fertilizer-current
  - Path: `services/fertilizer-optimization/tests/test_price_routes.py`
  - Add `test_get_current_prices()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_price_routes.py --collect-only`

- [x] **JOB2-007.3.impl** - Create price_routes.py
  - Path: `services/fertilizer-optimization/src/api/price_routes.py`
  - Implement GET /api/v1/prices/fertilizer-current endpoint
  - Verify: Check endpoint in file

- [x] **JOB2-007.4.impl** - Include router in main app
  - Path: `services/fertilizer-optimization/src/main.py`
  - Add app.include_router(price_routes.router)
  - Verify: Check router inclusion

- [x] **JOB2-007.5.verify** - Test price endpoint
  - Command: `curl http://localhost:8008/api/v1/prices/fertilizer-current`
  - Verify: Returns price data

- [x] **JOB2-007.99** - Commit price routes
  - Command: `git add services/fertilizer-optimization/src/api/price_routes.py services/fertilizer-optimization/tests/test_price_routes.py && git commit -m "JOB2-007: Create price API routes"`
  - Verify: `git log -1 --oneline`

---

## JOB2-008: Implement Economic Optimizer

### Tasks (TDD Workflow)

- [x] **JOB2-008.1.test** - Create test file for optimizer
  - Path: `services/fertilizer-optimization/tests/test_economic_optimizer.py`
  - Create test file
  - Verify: `ls services/fertilizer-optimization/tests/test_economic_optimizer.py`

- [x] **JOB2-008.2.test** - Write test for optimization algorithm
  - Path: `services/fertilizer-optimization/tests/test_economic_optimizer.py`
  - Add `test_optimize_fertilizer_strategy()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_economic_optimizer.py --collect-only`

- [x] **JOB2-008.3.test** - Write test for ROI calculation
  - Path: `services/fertilizer-optimization/tests/test_economic_optimizer.py`
  - Add `test_calculate_roi()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_economic_optimizer.py --collect-only`

- [x] **JOB2-008.4.impl** - Create EconomicOptimizer class
  - Path: `services/fertilizer-optimization/src/services/economic_optimizer.py`
  - Implement optimizer with scipy.optimize
  - Verify: `python -c "from src.services.economic_optimizer import EconomicOptimizer; print('OK')"`

- [x] **JOB2-008.5.impl** - Implement multi-objective optimization
  - Path: `services/fertilizer-optimization/src/services/economic_optimizer.py`
  - Add optimize_fertilizer_strategy method
  - Verify: Check method in file

- [x] **JOB2-008.6.impl** - Implement ROI calculation
  - Path: `services/fertilizer-optimization/src/services/economic_optimizer.py`
  - Add calculate_roi method
  - Verify: Check method in file

- [x] **JOB2-008.7.verify** - Run optimizer tests
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pytest tests/test_economic_optimizer.py -v`
  - Verify: All tests pass

- [x] **JOB2-008.99** - Commit economic optimizer
  - Command: `git add services/fertilizer-optimization/src/services/economic_optimizer.py services/fertilizer-optimization/tests/test_economic_optimizer.py && git commit -m "JOB2-008: Implement economic optimizer with scipy"`
  - Verify: `git log -1 --oneline`

---

## JOB2-009: Create Optimization API Routes

### Tasks (TDD Workflow)

- [x] **JOB2-009.1.test** - Write test for optimization endpoint
  - Path: `services/fertilizer-optimization/tests/test_optimization_routes.py`
  - Add `test_optimize_strategy_endpoint()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_optimization_routes.py --collect-only`

- [x] **JOB2-009.2.impl** - Create optimization_routes.py
  - Path: `services/fertilizer-optimization/src/api/optimization_routes.py`
  - Implement POST /api/v1/optimization/optimize-strategy endpoint
  - Verify: Check endpoint in file

- [x] **JOB2-009.3.verify** - Test optimization endpoint
  - Command: `curl -X POST http://localhost:8008/api/v1/optimization/optimize-strategy -H "Content-Type: application/json" -d '{"field_acres": 100, "nutrient_requirements": {"N": 150}, "yield_goal_bu_acre": 180}'`
  - Verify: Returns optimization results

- [x] **JOB2-009.99** - Commit optimization routes
  - Command: `git add services/fertilizer-optimization/src/api/optimization_routes.py services/fertilizer-optimization/tests/test_optimization_routes.py && git commit -m "JOB2-009: Create optimization API routes"`
  - Verify: `git log -1 --oneline`

---

## JOB2-010: Implement Integration Tests

### Tasks

- [x] **JOB2-010.1** - Create integration test file
  - Path: `services/fertilizer-optimization/tests/test_api_integration.py`
  - Create test file
  - Verify: `ls services/fertilizer-optimization/tests/test_api_integration.py`

- [x] **JOB2-010.2** - Write end-to-end optimization workflow test
  - Path: `services/fertilizer-optimization/tests/test_api_integration.py`
  - Add `test_optimization_workflow()` test
  - Verify: `pytest services/fertilizer-optimization/tests/test_api_integration.py --collect-only`

- [ ] **JOB2-010.3** - Run integration tests
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pytest tests/test_api_integration.py -v`
  - Verify: All tests pass

- [ ] **JOB2-010.4** - Generate coverage report
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pytest tests/ --cov=src --cov-report=html`
  - Verify: Coverage >80%

- [ ] **JOB2-010.99** - Commit integration tests
  - Command: `git add services/fertilizer-optimization/tests/test_api_integration.py && git commit -m "JOB2-010: Implement integration tests"`
  - Verify: `git log -1 --oneline`

---

## JOB2-011: Agricultural Validation and Documentation

### Tasks

- [ ] **JOB2-011.1** - Validate nutrient calculations
  - Review N-P-K calculations with agricultural knowledge
  - Verify: Calculations are accurate

- [ ] **JOB2-011.2** - Document ROI assumptions
  - Path: `services/fertilizer-optimization/docs/roi_assumptions.md`
  - Document assumptions used in ROI calculations
  - Verify: `cat services/fertilizer-optimization/docs/roi_assumptions.md`

- [ ] **JOB2-011.3** - Create README
  - Path: `services/fertilizer-optimization/README.md`
  - Add service overview and API documentation
  - Verify: `cat services/fertilizer-optimization/README.md`

- [ ] **JOB2-011.99** - Commit documentation
  - Command: `git add services/fertilizer-optimization/README.md services/fertilizer-optimization/docs/ && git commit -m "JOB2-011: Agricultural validation and documentation"`
  - Verify: `git log -1 --oneline`

---

## JOB2-012: Final Integration Preparation

### Tasks

- [ ] **JOB2-012.1** - Start service on port 8008
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && uvicorn src.main:app --port 8008 &`
  - Verify: `curl http://localhost:8008/health`

- [ ] **JOB2-012.2** - Run full test suite
  - Command: `cd services/fertilizer-optimization && source venv/bin/activate && pytest tests/ -v`
  - Verify: All tests pass

- [ ] **JOB2-012.3** - Tag service as ready
  - Command: `git tag -a fertilizer-optimization-v1.0.0 -m "Fertilizer Optimization Service ready for integration"`
  - Verify: `git tag -l`

- [ ] **JOB2-012.99** - Final commit
  - Command: `git add services/fertilizer-optimization/ && git commit -m "JOB2-012: Final integration preparation - Fertilizer Optimization Service complete"`
  - Verify: `git log -1 --oneline`

- [ ] **JOB2-012.100** - Push to repository
  - Command: `git push origin main && git push --tags`
  - Verify: `git status`

---

## Job 2 Summary

**Total Tasks**: ~120+ granular tasks  
**Completion Criteria**:
- ✅ All 12 tickets complete
- ✅ All tests passing (>80% coverage)
- ✅ Service running on port 8008
- ✅ TimescaleDB price tracking working
- ✅ scipy optimization working
- ✅ Documentation complete
- ✅ Ready for integration phase


