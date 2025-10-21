# Integration Phase - TDD Checklist

**Total Tickets**: 14  
**Estimated Timeline**: 2 weeks  
**Prerequisites**: All Job 1-5 complete  
**Related Files**: `docs/tickets-integration.md`, `docs/integration.md`

---

## INT-001: Pre-Integration Health Check Validation

### Tasks

- [ ] **INT-001.1** - Check Crop Taxonomy Service (Port 8007)
  - Command: `curl http://localhost:8007/health`
  - Verify: Returns {"status": "healthy"}

- [ ] **INT-001.2** - Check Fertilizer Optimization Service (Port 8008)
  - Command: `curl http://localhost:8008/health`
  - Verify: Returns {"status": "healthy"}

- [ ] **INT-001.3** - Check Image Analysis Service (Port 8004)
  - Command: `curl http://localhost:8004/health`
  - Verify: Returns {"status": "healthy"}

- [ ] **INT-001.4** - Check Location Management Service (Port 8009)
  - Command: `curl http://localhost:8009/health`
  - Verify: Returns {"status": "healthy"}

- [ ] **INT-001.5** - Check Weather Service (Port 8010)
  - Command: `curl http://localhost:8010/health`
  - Verify: Returns {"status": "healthy"}

- [ ] **INT-001.6** - Start any missing services
  - Command: Start services that are not running
  - Verify: All 5 services running

- [ ] **INT-001.7** - Check database connections
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT COUNT(*) FROM pg_stat_activity WHERE datname='caain_soil_hub';"`
  - Verify: Database connections active

- [ ] **INT-001.8** - Review service logs for errors
  - Command: Check logs for each service
  - Verify: No critical errors in startup

- [ ] **INT-001.99** - Document health check results
  - Path: `tests/integration/health_check_results.md`
  - Document all health check results
  - Verify: All services healthy

---

## INT-002: API Contract Verification Tests

### Tasks (TDD Workflow)

- [ ] **INT-002.1.test** - Create API contract test file
  - Path: `tests/integration/test_api_contracts.py`
  - Create test file with imports
  - Verify: `ls tests/integration/test_api_contracts.py`

- [ ] **INT-002.2.test** - Write contract test for Crop Taxonomy Service
  - Path: `tests/integration/test_api_contracts.py`
  - Add `test_crop_taxonomy_contract()` test
  - Verify: `pytest tests/integration/test_api_contracts.py --collect-only`

- [ ] **INT-002.3.test** - Write contract test for Fertilizer Optimization Service
  - Path: `tests/integration/test_api_contracts.py`
  - Add `test_fertilizer_optimization_contract()` test
  - Verify: `pytest tests/integration/test_api_contracts.py --collect-only`

- [ ] **INT-002.4.test** - Write contract test for Image Analysis Service
  - Path: `tests/integration/test_api_contracts.py`
  - Add `test_image_analysis_contract()` test
  - Verify: `pytest tests/integration/test_api_contracts.py --collect-only`

- [ ] **INT-002.5.test** - Write contract test for Location Management Service
  - Path: `tests/integration/test_api_contracts.py`
  - Add `test_location_management_contract()` test
  - Verify: `pytest tests/integration/test_api_contracts.py --collect-only`

- [ ] **INT-002.6.test** - Write contract test for Weather Service
  - Path: `tests/integration/test_api_contracts.py`
  - Add `test_weather_service_contract()` test
  - Verify: `pytest tests/integration/test_api_contracts.py --collect-only`

- [ ] **INT-002.7.verify** - Run all contract tests
  - Command: `pytest tests/integration/test_api_contracts.py -v`
  - Verify: All contract tests pass

- [ ] **INT-002.99** - Commit contract tests
  - Command: `git add tests/integration/test_api_contracts.py && git commit -m "INT-002: API contract verification tests"`
  - Verify: `git log -1 --oneline`

---

## INT-003: Create Service Client Libraries

### Tasks (TDD Workflow)

- [ ] **INT-003.1.test** - Create test file for service clients
  - Path: `tests/integration/test_service_clients.py`
  - Create test file
  - Verify: `ls tests/integration/test_service_clients.py`

- [ ] **INT-003.2.test** - Write test for LocationServiceClient
  - Path: `tests/integration/test_service_clients.py`
  - Add `test_location_service_client()` test
  - Verify: `pytest tests/integration/test_service_clients.py --collect-only`

- [ ] **INT-003.3.impl** - Create LocationServiceClient
  - Path: `services/weather-service/src/integrations/location_client.py`
  - Implement LocationServiceClient class
  - Verify: `python -c "from services.weather-service.src.integrations.location_client import LocationServiceClient; print('OK')"`

- [ ] **INT-003.4.impl** - Create FertilizerOptimizationClient
  - Path: `services/image-analysis/src/integrations/fertilizer_client.py`
  - Implement FertilizerOptimizationClient class
  - Verify: Check client implementation

- [ ] **INT-003.5.impl** - Create CropTaxonomyClient
  - Path: `services/fertilizer-optimization/src/integrations/crop_client.py`
  - Implement CropTaxonomyClient class
  - Verify: Check client implementation

- [ ] **INT-003.6.impl** - Create WeatherServiceClient
  - Path: `services/recommendation-engine/src/integrations/weather_client.py`
  - Implement WeatherServiceClient class
  - Verify: Check client implementation

- [ ] **INT-003.7.verify** - Run service client tests
  - Command: `pytest tests/integration/test_service_clients.py -v`
  - Verify: All client tests pass

- [ ] **INT-003.99** - Commit service clients
  - Command: `git add services/*/src/integrations/ tests/integration/test_service_clients.py && git commit -m "INT-003: Create service client libraries"`
  - Verify: `git log -1 --oneline`

---

## INT-004: Integrate Location Service with Weather Service

### Tasks (TDD Workflow)

- [ ] **INT-004.1.test** - Create test file for location-weather integration
  - Path: `tests/integration/test_location_weather_integration.py`
  - Create test file
  - Verify: `ls tests/integration/test_location_weather_integration.py`

- [ ] **INT-004.2.test** - Write test for weather data fetch by location
  - Path: `tests/integration/test_location_weather_integration.py`
  - Add `test_fetch_weather_for_location()` test
  - Verify: `pytest tests/integration/test_location_weather_integration.py --collect-only`

- [ ] **INT-004.3.impl** - Update weather service to use LocationServiceClient
  - Path: `services/weather-service/src/api/weather_routes.py`
  - Add location client integration
  - Verify: Check integration in weather routes

- [ ] **INT-004.4.impl** - Add error handling for location service failures
  - Path: `services/weather-service/src/api/weather_routes.py`
  - Add try/except blocks for location client calls
  - Verify: Check error handling

- [ ] **INT-004.5.verify** - Test location-weather integration
  - Command: `pytest tests/integration/test_location_weather_integration.py -v`
  - Verify: Integration test passes

- [ ] **INT-004.6.verify** - Test end-to-end workflow
  - Command: Create location, fetch weather for that location
  - Verify: Workflow completes successfully

- [ ] **INT-004.99** - Commit location-weather integration
  - Command: `git add services/weather-service/ tests/integration/test_location_weather_integration.py && git commit -m "INT-004: Integrate location service with weather service"`
  - Verify: `git log -1 --oneline`

---

## INT-005: Integrate Deficiency Detection with Fertilizer Optimization

### Tasks (TDD Workflow)

- [ ] **INT-005.1.test** - Create test file for deficiency-fertilizer integration
  - Path: `tests/integration/test_deficiency_fertilizer_integration.py`
  - Create test file
  - Verify: `ls tests/integration/test_deficiency_fertilizer_integration.py`

- [ ] **INT-005.2.test** - Write test for complete deficiency-to-recommendation workflow
  - Path: `tests/integration/test_deficiency_fertilizer_integration.py`
  - Add `test_deficiency_to_fertilizer_workflow()` test
  - Verify: `pytest tests/integration/test_deficiency_fertilizer_integration.py --collect-only`

- [ ] **INT-005.3.impl** - Create FertilizerOptimizationClient in image analysis service
  - Path: `services/image-analysis/src/integrations/fertilizer_client.py`
  - Implement client (if not done in INT-003)
  - Verify: Check client implementation

- [ ] **INT-005.4.impl** - Add /image-analysis-with-recommendations endpoint
  - Path: `services/image-analysis/src/api/analysis_routes.py`
  - Add new endpoint that calls fertilizer service
  - Verify: Check endpoint in file

- [ ] **INT-005.5.impl** - Implement nutrient requirement calculation from deficiencies
  - Path: `services/image-analysis/src/api/analysis_routes.py`
  - Add logic to convert deficiencies to nutrient requirements
  - Verify: Check calculation logic

- [ ] **INT-005.6.impl** - Add error handling for fertilizer service failures
  - Path: `services/image-analysis/src/api/analysis_routes.py`
  - Add try/except blocks
  - Verify: Check error handling

- [ ] **INT-005.7.verify** - Test deficiency-fertilizer integration
  - Command: `pytest tests/integration/test_deficiency_fertilizer_integration.py -v`
  - Verify: Integration test passes

- [ ] **INT-005.8.verify** - Test with sample image
  - Command: `curl -X POST http://localhost:8004/api/v1/deficiency/image-analysis-with-recommendations -F "image=@tests/fixtures/corn_nitrogen_deficiency.jpg" -F "crop_type=corn" -F "field_acres=100" -F "yield_goal=180"`
  - Verify: Returns deficiency analysis + fertilizer recommendations

- [ ] **INT-005.99** - Commit deficiency-fertilizer integration
  - Command: `git add services/image-analysis/ tests/integration/test_deficiency_fertilizer_integration.py && git commit -m "INT-005: Integrate deficiency detection with fertilizer optimization"`
  - Verify: `git log -1 --oneline`

---

## INT-006: Integrate Crop Filtering with All Services

### Tasks (TDD Workflow)

- [ ] **INT-006.1.test** - Create test file for crop integration
  - Path: `tests/integration/test_crop_integration.py`
  - Create test file
  - Verify: `ls tests/integration/test_crop_integration.py`

- [ ] **INT-006.2.test** - Write test for crop variety data access
  - Path: `tests/integration/test_crop_integration.py`
  - Add `test_crop_variety_access()` test
  - Verify: `pytest tests/integration/test_crop_integration.py --collect-only`

- [ ] **INT-006.3.impl** - Create CropTaxonomyClient for other services
  - Path: `services/fertilizer-optimization/src/integrations/crop_client.py`
  - Implement client (if not done in INT-003)
  - Verify: Check client implementation

- [ ] **INT-006.4.verify** - Test crop integration
  - Command: `pytest tests/integration/test_crop_integration.py -v`
  - Verify: Integration test passes

- [ ] **INT-006.99** - Commit crop integration
  - Command: `git add services/*/src/integrations/ tests/integration/test_crop_integration.py && git commit -m "INT-006: Integrate crop filtering with all services"`
  - Verify: `git log -1 --oneline`

---

## INT-007: Implement Weather-Based Fertilizer Application Timing

### Tasks (TDD Workflow)

- [ ] **INT-007.1.test** - Create test file for weather-fertilizer integration
  - Path: `tests/integration/test_weather_fertilizer_integration.py`
  - Create test file
  - Verify: `ls tests/integration/test_weather_fertilizer_integration.py`

- [ ] **INT-007.2.test** - Write test for application timing recommendations
  - Path: `tests/integration/test_weather_fertilizer_integration.py`
  - Add `test_fertilizer_timing_with_weather()` test
  - Verify: `pytest tests/integration/test_weather_fertilizer_integration.py --collect-only`

- [ ] **INT-007.3.impl** - Add WeatherServiceClient to fertilizer service
  - Path: `services/fertilizer-optimization/src/integrations/weather_client.py`
  - Implement client
  - Verify: Check client implementation

- [ ] **INT-007.4.impl** - Update optimization endpoint to include weather
  - Path: `services/fertilizer-optimization/src/api/optimization_routes.py`
  - Add weather forecast integration
  - Verify: Check weather integration

- [ ] **INT-007.5.impl** - Implement application timing logic
  - Path: `services/fertilizer-optimization/src/services/economic_optimizer.py`
  - Add method to recommend application timing based on weather
  - Verify: Check timing logic

- [ ] **INT-007.6.verify** - Test weather-fertilizer integration
  - Command: `pytest tests/integration/test_weather_fertilizer_integration.py -v`
  - Verify: Integration test passes

- [ ] **INT-007.99** - Commit weather-fertilizer integration
  - Command: `git add services/fertilizer-optimization/ tests/integration/test_weather_fertilizer_integration.py && git commit -m "INT-007: Implement weather-based fertilizer application timing"`
  - Verify: `git log -1 --oneline`

---

## INT-008: End-to-End Workflow Testing

### Tasks (TDD Workflow)

- [ ] **INT-008.1.test** - Create complete workflow test file
  - Path: `tests/integration/test_complete_workflow.py`
  - Create test file
  - Verify: `ls tests/integration/test_complete_workflow.py`

- [ ] **INT-008.2.test** - Write test for complete farm advisory workflow
  - Path: `tests/integration/test_complete_workflow.py`
  - Add `test_complete_farm_advisory_workflow()` test covering: create farm → get weather → analyze image → get fertilizer recommendations → find crop varieties
  - Verify: `pytest tests/integration/test_complete_workflow.py --collect-only`

- [ ] **INT-008.3.test** - Write test for Iowa corn farm scenario
  - Path: `tests/integration/test_complete_workflow.py`
  - Add `test_iowa_corn_farm_scenario()` test
  - Verify: `pytest tests/integration/test_complete_workflow.py --collect-only`

- [ ] **INT-008.4.test** - Write test for Illinois soybean farm scenario
  - Path: `tests/integration/test_complete_workflow.py`
  - Add `test_illinois_soybean_farm_scenario()` test
  - Verify: `pytest tests/integration/test_complete_workflow.py --collect-only`

- [ ] **INT-008.5.verify** - Run complete workflow tests
  - Command: `pytest tests/integration/test_complete_workflow.py -v -s`
  - Verify: All workflow tests pass

- [ ] **INT-008.6.verify** - Verify all integration points working
  - Command: Review test output for all service interactions
  - Verify: All services communicate successfully

- [ ] **INT-008.99** - Commit end-to-end workflow tests
  - Command: `git add tests/integration/test_complete_workflow.py && git commit -m "INT-008: End-to-end workflow testing"`
  - Verify: `git log -1 --oneline`

---

## INT-009: Performance Optimization

### Tasks

- [ ] **INT-009.1.test** - Create performance test file
  - Path: `tests/integration/test_performance.py`
  - Create test file
  - Verify: `ls tests/integration/test_performance.py`

- [ ] **INT-009.2.test** - Write test for workflow response time <3s
  - Path: `tests/integration/test_performance.py`
  - Add `test_workflow_performance()` test with timing
  - Verify: `pytest tests/integration/test_performance.py --collect-only`

- [ ] **INT-009.3** - Run performance tests
  - Command: `pytest tests/integration/test_performance.py -v`
  - Verify: Identify slow operations

- [ ] **INT-009.4** - Check for slow database queries
  - Command: `psql -U postgres -d caain_soil_hub -c "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20;"`
  - Verify: Identify slow queries

- [ ] **INT-009.5** - Add missing indexes if needed
  - Command: Add indexes for slow queries
  - Verify: Query performance improved

- [ ] **INT-009.6** - Check for N+1 query problems
  - Command: Enable query logging and review
  - Verify: No N+1 patterns

- [ ] **INT-009.7** - Optimize service-to-service calls
  - Command: Review and optimize HTTP client calls
  - Verify: Minimize unnecessary calls

- [ ] **INT-009.8.verify** - Re-run performance tests
  - Command: `pytest tests/integration/test_performance.py -v`
  - Verify: All tests pass with <3s response time

- [ ] **INT-009.99** - Commit performance optimizations
  - Command: `git add services/ tests/integration/test_performance.py && git commit -m "INT-009: Performance optimization"`
  - Verify: `git log -1 --oneline`

---

## INT-010: Error Handling and Resilience Testing

### Tasks (TDD Workflow)

- [ ] **INT-010.1.test** - Create error handling test file
  - Path: `tests/integration/test_error_handling.py`
  - Create test file
  - Verify: `ls tests/integration/test_error_handling.py`

- [ ] **INT-010.2.test** - Write test for service failure scenarios
  - Path: `tests/integration/test_error_handling.py`
  - Add `test_service_failure_handling()` test
  - Verify: `pytest tests/integration/test_error_handling.py --collect-only`

- [ ] **INT-010.3.test** - Write test for timeout handling
  - Path: `tests/integration/test_error_handling.py`
  - Add `test_timeout_handling()` test
  - Verify: `pytest tests/integration/test_error_handling.py --collect-only`

- [ ] **INT-010.4.test** - Write test for fallback mechanisms
  - Path: `tests/integration/test_error_handling.py`
  - Add `test_fallback_mechanisms()` test
  - Verify: `pytest tests/integration/test_error_handling.py --collect-only`

- [ ] **INT-010.5.verify** - Run error handling tests
  - Command: `pytest tests/integration/test_error_handling.py -v`
  - Verify: All error handling tests pass

- [ ] **INT-010.6** - Review error messages for clarity
  - Command: Review error responses from all services
  - Verify: Error messages are informative

- [ ] **INT-010.99** - Commit error handling tests
  - Command: `git add tests/integration/test_error_handling.py && git commit -m "INT-010: Error handling and resilience testing"`
  - Verify: `git log -1 --oneline`

---

## INT-011: Integration Test Suite Completion

### Tasks

- [ ] **INT-011.1** - Run full integration test suite
  - Command: `pytest tests/integration/ -v`
  - Verify: All integration tests pass

- [ ] **INT-011.2** - Generate integration test coverage report
  - Command: `pytest tests/integration/ --cov=services --cov-report=html`
  - Verify: Coverage >70%

- [ ] **INT-011.3** - Review coverage report
  - Command: `open htmlcov/index.html`
  - Verify: Identify untested integration points

- [ ] **INT-011.4** - Add missing integration tests
  - Path: `tests/integration/`
  - Add tests for uncovered integration points
  - Verify: Coverage improved

- [ ] **INT-011.5** - Re-run full test suite
  - Command: `pytest tests/integration/ -v --cov=services`
  - Verify: All tests pass, coverage >70%

- [ ] **INT-011.99** - Commit integration test suite
  - Command: `git add tests/integration/ && git commit -m "INT-011: Integration test suite completion"`
  - Verify: `git log -1 --oneline`

---

## INT-012: Agricultural Expert Review

### Tasks

- [ ] **INT-012.1** - Create real-world scenario test file
  - Path: `tests/integration/test_real_world_scenarios.py`
  - Create test file
  - Verify: `ls tests/integration/test_real_world_scenarios.py`

- [ ] **INT-012.2** - Implement Iowa corn farm scenario
  - Path: `tests/integration/test_real_world_scenarios.py`
  - Add test for Iowa corn farm with nitrogen deficiency
  - Verify: `pytest tests/integration/test_real_world_scenarios.py::test_iowa_corn_farm --collect-only`

- [ ] **INT-012.3** - Implement Illinois soybean farm scenario
  - Path: `tests/integration/test_real_world_scenarios.py`
  - Add test for Illinois soybean farm with iron chlorosis
  - Verify: `pytest tests/integration/test_real_world_scenarios.py::test_illinois_soybean_farm --collect-only`

- [ ] **INT-012.4** - Implement Kansas wheat farm scenario
  - Path: `tests/integration/test_real_world_scenarios.py`
  - Add test for Kansas wheat farm with drought stress
  - Verify: `pytest tests/integration/test_real_world_scenarios.py::test_kansas_wheat_farm --collect-only`

- [ ] **INT-012.5** - Run real-world scenario tests
  - Command: `pytest tests/integration/test_real_world_scenarios.py -v`
  - Verify: All scenarios pass

- [ ] **INT-012.6** - Validate crop recommendations with expert
  - Review crop variety recommendations for accuracy
  - Verify: Recommendations are agriculturally sound

- [ ] **INT-012.7** - Validate fertilizer calculations with expert
  - Review N-P-K calculations and ROI estimates
  - Verify: Calculations are accurate

- [ ] **INT-012.8** - Validate weather impact assessments with expert
  - Review planting condition recommendations
  - Verify: Assessments are accurate

- [ ] **INT-012.9** - Document expert feedback
  - Path: `tests/integration/expert_review_results.md`
  - Document all feedback and required changes
  - Verify: Feedback documented

- [ ] **INT-012.10** - Implement expert feedback changes
  - Make necessary changes based on feedback
  - Verify: Changes implemented

- [ ] **INT-012.99** - Commit expert review results
  - Command: `git add tests/integration/test_real_world_scenarios.py tests/integration/expert_review_results.md && git commit -m "INT-012: Agricultural expert review"`
  - Verify: `git log -1 --oneline`

---

## INT-013: Documentation and Deployment Guide

### Tasks

- [ ] **INT-013.1** - Create integration architecture document
  - Path: `docs/integration-architecture.md`
  - Document service integration architecture
  - Verify: `cat docs/integration-architecture.md`

- [ ] **INT-013.2** - Document API integration points
  - Path: `docs/api-integration-points.md`
  - Document all service-to-service API calls
  - Verify: `cat docs/api-integration-points.md`

- [ ] **INT-013.3** - Create deployment guide
  - Path: `docs/deployment-guide.md`
  - Document deployment steps for all services
  - Verify: `cat docs/deployment-guide.md`

- [ ] **INT-013.4** - Create troubleshooting guide
  - Path: `docs/troubleshooting.md`
  - Document common issues and solutions
  - Verify: `cat docs/troubleshooting.md`

- [ ] **INT-013.5** - Update main README
  - Path: `README.md`
  - Update with integration information
  - Verify: `cat README.md`

- [ ] **INT-013.99** - Commit documentation
  - Command: `git add docs/ README.md && git commit -m "INT-013: Documentation and deployment guide"`
  - Verify: `git log -1 --oneline`

---

## INT-014: Final Integration Sign-Off

### Tasks

- [ ] **INT-014.1** - Verify all services running
  - Command: Check health endpoints for all 5 services
  - Verify: All services healthy

- [ ] **INT-014.2** - Run full test suite (unit + integration)
  - Command: `pytest tests/ -v --cov=services --cov-report=html`
  - Verify: All tests pass

- [ ] **INT-014.3** - Verify performance requirements met
  - Command: `pytest tests/integration/test_performance.py -v`
  - Verify: All workflows <3s

- [ ] **INT-014.4** - Verify agricultural expert approval
  - Review expert sign-off documentation
  - Verify: Expert approval obtained

- [ ] **INT-014.5** - Verify documentation complete
  - Review all documentation files
  - Verify: Documentation is complete and accurate

- [ ] **INT-014.6** - Run end-to-end workflow one final time
  - Command: `pytest tests/integration/test_complete_workflow.py -v -s`
  - Verify: Complete workflow passes

- [ ] **INT-014.7** - Tag integration as complete
  - Command: `git tag -a integration-v1.0.0 -m "Integration phase complete - CAAIN Soil Hub ready for production"`
  - Verify: `git tag -l`

- [ ] **INT-014.8** - Create final integration report
  - Path: `docs/integration-report.md`
  - Document integration results, test coverage, performance metrics
  - Verify: `cat docs/integration-report.md`

- [ ] **INT-014.99** - Final commit
  - Command: `git add docs/integration-report.md && git commit -m "INT-014: Final integration sign-off - System ready for production"`
  - Verify: `git log -1 --oneline`

- [ ] **INT-014.100** - Push to repository
  - Command: `git push origin main && git push --tags`
  - Verify: `git status`

---

## Integration Phase Summary

**Total Tasks**: ~140+ granular tasks  
**Completion Criteria**:
- ✅ All 14 integration tickets complete
- ✅ All 5 services integrated and communicating
- ✅ All integration tests passing (>70% coverage)
- ✅ Performance requirements met (<3s for complex workflows)
- ✅ Agricultural expert approval obtained
- ✅ Error handling and resilience verified
- ✅ Documentation complete
- ✅ System ready for production deployment

**Success Metrics**:
- ✅ End-to-end workflows complete successfully
- ✅ No critical bugs in production scenarios
- ✅ All services running and healthy
- ✅ Integration test coverage >70%
- ✅ Performance benchmarks met
- ✅ Agricultural validation passed


