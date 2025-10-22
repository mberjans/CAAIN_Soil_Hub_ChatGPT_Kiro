# Job 5: Weather Impact Analysis - TDD Checklist

**Service**: Weather Service (Port 8010)  
**Total Tickets**: 12  
**Estimated Timeline**: 3-4 weeks  
**Related Files**: `docs/tickets-job-5-weather-analysis.md`, `docs/parallel-job-5-weather-analysis.md`

---

## JOB5-001: Setup Weather Service Structure

### Tasks

- [x] **JOB5-001.1** - Create service directory
  - Command: `mkdir -p services/weather-service/src/{models,services,providers,api,schemas}`
  - Verify: `ls -la services/weather-service/src/`

- [x] **JOB5-001.2** - Create tests and migrations directories
  - Command: `mkdir -p services/weather-service/{tests,migrations}`
  - Verify: `ls -ld services/weather-service/tests`

- [x] **JOB5-001.3** - Create __init__.py files
  - Command: `touch services/weather-service/src/__init__.py services/weather-service/src/{models,services,providers,api,schemas}/__init__.py services/weather-service/tests/__init__.py`
  - Verify: `find services/weather-service/src -name "__init__.py" | wc -l`

- [x] **JOB5-001.4** - Create virtual environment
  - Command: `cd services/weather-service && python3 -m venv venv`
  - Verify: `ls services/weather-service/venv/bin/python`

- [x] **JOB5-001.99** - Commit directory structure
  - Command: `git add services/weather-service && git commit -m "JOB5-001: Setup weather service structure"`
  - Verify: `git log -1 --oneline`

---

## JOB5-002: Install Dependencies with TimescaleDB Support

### Tasks

- [x] **JOB5-002.1** - Create requirements.txt
  - Path: `services/weather-service/requirements.txt`
  - Content: fastapi, uvicorn, sqlalchemy, psycopg2-binary, pydantic, httpx, pandas, pytest, pytest-asyncio, pytest-cov, APScheduler
  - Verify: `cat services/weather-service/requirements.txt`

- [x] **JOB5-002.2** - Install dependencies
  - Command: `cd services/weather-service && source venv/bin/activate && pip install -r requirements.txt`
  - Verify: `pip list | grep httpx`

- [x] **JOB5-002.3** - Verify httpx installation
  - Command: `python -c "import httpx; print('httpx OK')"`
  - Verify: httpx working

- [x] **JOB5-002.4** - Verify pandas installation
  - Command: `python -c "import pandas; print(f'pandas: {pandas.__version__}')"`
  - Verify: pandas version displayed

- [x] **JOB5-002.5** - Verify TimescaleDB extension enabled
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT * FROM pg_extension WHERE extname='timescaledb';"`
  - Verify: TimescaleDB extension present

- [x] **JOB5-002.99** - Commit requirements
  - Command: `git add services/weather-service/requirements.txt && git commit -m "JOB5-002: Add dependencies with TimescaleDB support"`
  - Verify: `git log -1 --oneline`

---

## JOB5-003: Create TimescaleDB Schema for Weather Data

### Tasks (TDD Workflow)

- [x] **JOB5-003.1.test** - Create test file for weather models
  - Path: `services/weather-service/tests/test_weather_models.py`
  - Create test file
  - Verify: `ls services/weather-service/tests/test_weather_models.py`

- [x] **JOB5-003.2.test** - Write test for WeatherStation model
  - Path: `services/weather-service/tests/test_weather_models.py`
  - Add `test_weather_station_creation()` test
  - Verify: `pytest services/weather-service/tests/test_weather_models.py --collect-only`

- [x] **JOB5-003.3.test** - Write test for WeatherObservation model
  - Path: `services/weather-service/tests/test_weather_models.py`
  - Add `test_weather_observation_creation()` test
  - Verify: `pytest services/weather-service/tests/test_weather_models.py --collect-only`

- [x] **JOB5-003.4.impl** - Create weather_models.py
  - Path: `services/weather-service/src/models/weather_models.py`
  - Implement WeatherStation, WeatherObservation, WeatherForecast models
  - Verify: `python -c "from src.models.weather_models import WeatherStation; print('OK')"`

- [ ] **JOB5-003.5.impl** - Create migration SQL
  - Path: `services/weather-service/migrations/005_weather_schema.sql`
  - Write CREATE TABLE statements
  - Verify: `cat services/weather-service/migrations/005_weather_schema.sql`

- [ ] **JOB5-003.6.impl** - Add hypertable creation to migration
  - Path: `services/weather-service/migrations/005_weather_schema.sql`
  - Add SELECT create_hypertable statements
  - Verify: `grep "create_hypertable" services/weather-service/migrations/005_weather_schema.sql`

- [x] **JOB5-003.7.impl** - Add continuous aggregates to migration
  - Path: `services/weather-service/migrations/005_weather_schema.sql`
  - Add CREATE MATERIALIZED VIEW for daily summaries
  - Verify: `grep "MATERIALIZED VIEW" services/weather-service/migrations/005_weather_schema.sql`

- [ ] **JOB5-003.8.impl** - Run migration
  - Command: `psql -U postgres -d caain_soil_hub -f services/weather-service/migrations/005_weather_schema.sql`
  - Verify: `psql -U postgres -d caain_soil_hub -c "\d weather_stations"`

- [ ] **JOB5-003.9.verify** - Verify hypertables created
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT * FROM timescaledb_information.hypertables WHERE hypertable_name IN ('weather_observations', 'weather_forecasts');"`
  - Verify: Both hypertables present

- [ ] **JOB5-003.10.verify** - Verify continuous aggregates created
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT view_name FROM timescaledb_information.continuous_aggregates;"`
  - Verify: Continuous aggregate present

- [ ] **JOB5-003.11.verify** - Run model tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_weather_models.py -v`
  - Verify: All tests pass

- [ ] **JOB5-003.99** - Commit database schema
  - Command: `git add services/weather-service/src/models/ services/weather-service/migrations/ services/weather-service/tests/test_weather_models.py && git commit -m "JOB5-003: Create TimescaleDB schema for weather data"`
  - Verify: `git log -1 --oneline`

---

## JOB5-004: Create Pydantic Schemas

### Tasks (TDD Workflow)

- [ ] **JOB5-004.1.test** - Create test file for schemas
  - Path: `services/weather-service/tests/test_weather_schemas.py`
  - Create test file
  - Verify: `ls services/weather-service/tests/test_weather_schemas.py`

- [ ] **JOB5-004.2.test** - Write test for WeatherRequest schema
  - Path: `services/weather-service/tests/test_weather_schemas.py`
  - Add `test_weather_request_valid()` test
  - Verify: `pytest services/weather-service/tests/test_weather_schemas.py --collect-only`

- [ ] **JOB5-004.3.impl** - Create weather_schemas.py
  - Path: `services/weather-service/src/schemas/weather_schemas.py`
  - Implement WeatherRequest, WeatherResponse, ForecastResponse schemas
  - Verify: `python -c "from src.schemas.weather_schemas import WeatherRequest; print('OK')"`

- [ ] **JOB5-004.4.verify** - Run schema tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_weather_schemas.py -v`
  - Verify: All tests pass

- [ ] **JOB5-004.99** - Commit schemas
  - Command: `git add services/weather-service/src/schemas/ services/weather-service/tests/test_weather_schemas.py && git commit -m "JOB5-004: Create Pydantic schemas"`
  - Verify: `git log -1 --oneline`

---

## JOB5-005: Create FastAPI Main Application

### Tasks (TDD Workflow)

- [ ] **JOB5-005.1.test** - Create test file for main app
  - Path: `services/weather-service/tests/test_main.py`
  - Create test file
  - Verify: `ls services/weather-service/tests/test_main.py`

- [ ] **JOB5-005.2.test** - Write test for health endpoint
  - Path: `services/weather-service/tests/test_main.py`
  - Add `test_health_endpoint()` test
  - Verify: `pytest services/weather-service/tests/test_main.py --collect-only`

- [ ] **JOB5-005.3.impl** - Create main.py
  - Path: `services/weather-service/src/main.py`
  - Create FastAPI app with health endpoint
  - Verify: `python -c "from src.main import app; print(app.title)"`

- [ ] **JOB5-005.4.verify** - Start service on port 8010
  - Command: `cd services/weather-service && source venv/bin/activate && uvicorn src.main:app --port 8010 &`
  - Verify: `curl http://localhost:8010/health`

- [ ] **JOB5-005.5.verify** - Stop service
  - Command: `pkill -f "uvicorn src.main:app --port 8010"`
  - Verify: Service stopped

- [ ] **JOB5-005.99** - Commit main app
  - Command: `git add services/weather-service/src/main.py services/weather-service/tests/test_main.py && git commit -m "JOB5-005: Create FastAPI main application"`
  - Verify: `git log -1 --oneline`

---

## JOB5-006: Implement Weather Fetcher with Multi-Provider Support

### Tasks (TDD Workflow)

- [ ] **JOB5-006.1.test** - Create test file for weather fetcher
  - Path: `services/weather-service/tests/test_weather_fetcher.py`
  - Create test file
  - Verify: `ls services/weather-service/tests/test_weather_fetcher.py`

- [ ] **JOB5-006.2.test** - Write test for MockWeatherProvider
  - Path: `services/weather-service/tests/test_weather_fetcher.py`
  - Add `test_mock_weather_provider()` test
  - Verify: `pytest services/weather-service/tests/test_weather_fetcher.py --collect-only`

- [ ] **JOB5-006.3.test** - Write test for WeatherFetcher
  - Path: `services/weather-service/tests/test_weather_fetcher.py`
  - Add `test_weather_fetcher_fetch()` test
  - Verify: `pytest services/weather-service/tests/test_weather_fetcher.py --collect-only`

- [ ] **JOB5-006.4.impl** - Create MockWeatherProvider
  - Path: `services/weather-service/src/providers/mock_weather_provider.py`
  - Implement mock provider
  - Verify: `python -c "from src.providers.mock_weather_provider import MockWeatherProvider; print('OK')"`

- [ ] **JOB5-006.5.impl** - Create WeatherFetcher
  - Path: `services/weather-service/src/services/weather_fetcher.py`
  - Implement weather fetcher with multi-provider support
  - Verify: `python -c "from src.services.weather_fetcher import WeatherFetcher; print('OK')"`

- [ ] **JOB5-006.6.impl** - Implement fetch_current_weather method
  - Path: `services/weather-service/src/services/weather_fetcher.py`
  - Add fetch_current_weather with fallback logic
  - Verify: Check method in file

- [ ] **JOB5-006.7.impl** - Implement fetch_forecast method
  - Path: `services/weather-service/src/services/weather_fetcher.py`
  - Add fetch_forecast method
  - Verify: Check method in file

- [ ] **JOB5-006.8.impl** - Implement store_weather_data method
  - Path: `services/weather-service/src/services/weather_fetcher.py`
  - Add method to store data in TimescaleDB
  - Verify: Check method in file

- [ ] **JOB5-006.9.verify** - Run weather fetcher tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_weather_fetcher.py -v`
  - Verify: All tests pass

- [ ] **JOB5-006.99** - Commit weather fetcher
  - Command: `git add services/weather-service/src/services/weather_fetcher.py services/weather-service/src/providers/ services/weather-service/tests/test_weather_fetcher.py && git commit -m "JOB5-006: Implement weather fetcher with multi-provider support"`
  - Verify: `git log -1 --oneline`

---

## JOB5-007: Create Weather API Routes

### Tasks (TDD Workflow)

- [ ] **JOB5-007.1.test** - Create test file for weather routes
  - Path: `services/weather-service/tests/test_weather_routes.py`
  - Create test file
  - Verify: `ls services/weather-service/tests/test_weather_routes.py`

- [ ] **JOB5-007.2.test** - Write test for GET /weather/current endpoint
  - Path: `services/weather-service/tests/test_weather_routes.py`
  - Add `test_get_current_weather()` test
  - Verify: `pytest services/weather-service/tests/test_weather_routes.py --collect-only`

- [ ] **JOB5-007.3.test** - Write test for GET /weather/forecast endpoint
  - Path: `services/weather-service/tests/test_weather_routes.py`
  - Add `test_get_forecast()` test
  - Verify: `pytest services/weather-service/tests/test_weather_routes.py --collect-only`

- [ ] **JOB5-007.4.impl** - Create weather_routes.py
  - Path: `services/weather-service/src/api/weather_routes.py`
  - Create router with weather endpoints
  - Verify: Check router in file

- [ ] **JOB5-007.5.impl** - Implement GET /api/v1/weather/current endpoint
  - Path: `services/weather-service/src/api/weather_routes.py`
  - Add get_current_weather endpoint
  - Verify: Check endpoint in file

- [ ] **JOB5-007.6.impl** - Implement GET /api/v1/weather/forecast endpoint
  - Path: `services/weather-service/src/api/weather_routes.py`
  - Add get_forecast endpoint
  - Verify: Check endpoint in file

- [ ] **JOB5-007.7.impl** - Include router in main app
  - Path: `services/weather-service/src/main.py`
  - Add app.include_router(weather_routes.router)
  - Verify: Check router inclusion

- [ ] **JOB5-007.8.verify** - Test current weather endpoint
  - Command: `curl "http://localhost:8010/api/v1/weather/current?latitude=42.0&longitude=-93.0"`
  - Verify: Returns weather data

- [ ] **JOB5-007.9.verify** - Test forecast endpoint
  - Command: `curl "http://localhost:8010/api/v1/weather/forecast?latitude=42.0&longitude=-93.0&days=7"`
  - Verify: Returns forecast data

- [ ] **JOB5-007.10.verify** - Run API tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_weather_routes.py -v`
  - Verify: All tests pass

- [ ] **JOB5-007.99** - Commit weather routes
  - Command: `git add services/weather-service/src/api/weather_routes.py services/weather-service/tests/test_weather_routes.py && git commit -m "JOB5-007: Create weather API routes"`
  - Verify: `git log -1 --oneline`

---

## JOB5-008: Implement Impact Analyzer

### Tasks (TDD Workflow)

- [ ] **JOB5-008.1.test** - Create test file for impact analyzer
  - Path: `services/weather-service/tests/test_impact_analyzer.py`
  - Create test file
  - Verify: `ls services/weather-service/tests/test_impact_analyzer.py`

- [ ] **JOB5-008.2.test** - Write test for planting conditions analysis
  - Path: `services/weather-service/tests/test_impact_analyzer.py`
  - Add `test_analyze_planting_conditions()` test
  - Verify: `pytest services/weather-service/tests/test_impact_analyzer.py --collect-only`

- [ ] **JOB5-008.3.test** - Write test for soil temperature estimation
  - Path: `services/weather-service/tests/test_impact_analyzer.py`
  - Add `test_estimate_soil_temperature()` test
  - Verify: `pytest services/weather-service/tests/test_impact_analyzer.py --collect-only`

- [ ] **JOB5-008.4.impl** - Create impact_analyzer.py
  - Path: `services/weather-service/src/services/impact_analyzer.py`
  - Create WeatherImpactAnalyzer class
  - Verify: `python -c "from src.services.impact_analyzer import WeatherImpactAnalyzer; print('OK')"`

- [ ] **JOB5-008.5.impl** - Implement analyze_planting_conditions method
  - Path: `services/weather-service/src/services/impact_analyzer.py`
  - Add analyze_planting_conditions with crop-specific thresholds
  - Verify: Check method in file

- [ ] **JOB5-008.6.impl** - Implement estimate_soil_temperature method
  - Path: `services/weather-service/src/services/impact_analyzer.py`
  - Add soil temperature estimation algorithm
  - Verify: Check method in file

- [ ] **JOB5-008.7.impl** - Implement crop-specific thresholds
  - Path: `services/weather-service/src/services/impact_analyzer.py`
  - Add threshold data for corn, soybean, wheat
  - Verify: Check thresholds in file

- [ ] **JOB5-008.8.verify** - Run impact analyzer tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_impact_analyzer.py -v`
  - Verify: All tests pass

- [ ] **JOB5-008.99** - Commit impact analyzer
  - Command: `git add services/weather-service/src/services/impact_analyzer.py services/weather-service/tests/test_impact_analyzer.py && git commit -m "JOB5-008: Implement impact analyzer"`
  - Verify: `git log -1 --oneline`

---

## JOB5-009: Create Impact Analysis API Routes

### Tasks (TDD Workflow)

- [ ] **JOB5-009.1.test** - Write test for impact analysis endpoint
  - Path: `services/weather-service/tests/test_weather_routes.py`
  - Add `test_analyze_planting_endpoint()` test
  - Verify: `pytest services/weather-service/tests/test_weather_routes.py --collect-only`

- [ ] **JOB5-009.2.impl** - Implement POST /api/v1/weather/analyze-planting endpoint
  - Path: `services/weather-service/src/api/weather_routes.py`
  - Add analyze_planting endpoint
  - Verify: Check endpoint in file

- [ ] **JOB5-009.3.verify** - Test impact analysis endpoint
  - Command: `curl -X POST http://localhost:8010/api/v1/weather/analyze-planting -H "Content-Type: application/json" -d '{"latitude": 42.0, "longitude": -93.0, "crop_type": "corn"}'`
  - Verify: Returns impact analysis

- [ ] **JOB5-009.4.verify** - Run API tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_weather_routes.py -v`
  - Verify: All tests pass

- [ ] **JOB5-009.99** - Commit impact analysis routes
  - Command: `git add services/weather-service/src/api/weather_routes.py services/weather-service/tests/test_weather_routes.py && git commit -m "JOB5-009: Create impact analysis API routes"`
  - Verify: `git log -1 --oneline`

---

## JOB5-010: Implement Historical Pattern Analyzer

### Tasks (TDD Workflow)

- [ ] **JOB5-010.1.test** - Write test for historical pattern analysis
  - Path: `services/weather-service/tests/test_historical_analyzer.py`
  - Add `test_analyze_historical_patterns()` test
  - Verify: `pytest services/weather-service/tests/test_historical_analyzer.py --collect-only`

- [ ] **JOB5-010.2.impl** - Create historical_analyzer.py
  - Path: `services/weather-service/src/services/historical_analyzer.py`
  - Create HistoricalAnalyzer class
  - Verify: `python -c "from src.services.historical_analyzer import HistoricalAnalyzer; print('OK')"`

- [ ] **JOB5-010.3.impl** - Implement pattern detection using continuous aggregates
  - Path: `services/weather-service/src/services/historical_analyzer.py`
  - Add analyze_patterns method using TimescaleDB continuous aggregates
  - Verify: Check method in file

- [ ] **JOB5-010.4.verify** - Run historical analyzer tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_historical_analyzer.py -v`
  - Verify: All tests pass

- [ ] **JOB5-010.99** - Commit historical analyzer
  - Command: `git add services/weather-service/src/services/historical_analyzer.py services/weather-service/tests/test_historical_analyzer.py && git commit -m "JOB5-010: Implement historical pattern analyzer"`
  - Verify: `git log -1 --oneline`

---

## JOB5-011: Implement Integration Tests

### Tasks

- [ ] **JOB5-011.1** - Create integration test file
  - Path: `services/weather-service/tests/test_api_integration.py`
  - Create test file
  - Verify: `ls services/weather-service/tests/test_api_integration.py`

- [ ] **JOB5-011.2** - Write end-to-end weather workflow test
  - Path: `services/weather-service/tests/test_api_integration.py`
  - Add `test_weather_workflow()` test
  - Verify: `pytest services/weather-service/tests/test_api_integration.py --collect-only`

- [ ] **JOB5-011.3** - Run integration tests
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/test_api_integration.py -v`
  - Verify: All tests pass

- [ ] **JOB5-011.4** - Generate coverage report
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/ --cov=src --cov-report=html`
  - Verify: Coverage >80%

- [ ] **JOB5-011.99** - Commit integration tests
  - Command: `git add services/weather-service/tests/test_api_integration.py && git commit -m "JOB5-011: Implement integration tests"`
  - Verify: `git log -1 --oneline`

---

## JOB5-012: Final Integration Preparation

### Tasks

- [ ] **JOB5-012.1** - Start service on port 8010
  - Command: `cd services/weather-service && source venv/bin/activate && uvicorn src.main:app --port 8010 &`
  - Verify: `curl http://localhost:8010/health`

- [ ] **JOB5-012.2** - Run full test suite
  - Command: `cd services/weather-service && source venv/bin/activate && pytest tests/ -v`
  - Verify: All tests pass

- [ ] **JOB5-012.3** - Create README
  - Path: `services/weather-service/README.md`
  - Add service documentation
  - Verify: `cat services/weather-service/README.md`

- [ ] **JOB5-012.4** - Tag service as ready
  - Command: `git tag -a weather-service-v1.0.0 -m "Weather Service ready for integration"`
  - Verify: `git tag -l`

- [ ] **JOB5-012.99** - Final commit
  - Command: `git add services/weather-service/ && git commit -m "JOB5-012: Final integration preparation - Weather Service complete"`
  - Verify: `git log -1 --oneline`

- [ ] **JOB5-012.100** - Push to repository
  - Command: `git push origin main && git push --tags`
  - Verify: `git status`

---

## Job 5 Summary

**Total Tasks**: ~110+ granular tasks  
**Completion Criteria**:
- ✅ All 12 tickets complete
- ✅ All tests passing (>80% coverage)
- ✅ Service running on port 8010
- ✅ TimescaleDB time series working
- ✅ Weather API integration working
- ✅ Impact analysis working
- ✅ Documentation complete
- ✅ Ready for integration with JOB4


