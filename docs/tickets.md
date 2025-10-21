# Integration Phase - Development Tickets

**Total Tickets**: 14  
**Estimated Timeline**: 2 weeks  
**Prerequisites**: All Job 1-5 tickets must be complete  
**Related Plan**: `docs/integration.md`

---

## INT-001: Pre-Integration Health Check Validation

**Priority**: Critical  
**Estimated Effort**: 2 hours  
**Dependencies**: JOB1-015, JOB2-012, JOB3-013, JOB4-011, JOB5-012  
**Blocks**: INT-002, INT-003  
**Parallel Execution**: No

**Description**:
Verify all 5 services are running and healthy before starting integration.

**Acceptance Criteria**:
- [ ] All 5 services respond to /health endpoint
- [ ] All services return HTTP 200
- [ ] Database connections healthy
- [ ] No error logs in startup

**Validation Commands**:
```bash
# Check all services
curl http://localhost:8007/health  # Crop Filtering
curl http://localhost:8008/health  # Fertilizer Optimization
curl http://localhost:8004/health  # Image Analysis
curl http://localhost:8009/health  # Location Management
curl http://localhost:8010/health  # Weather Service

# Start any missing services
cd services/crop-taxonomy && source venv/bin/activate && uvicorn src.main:app --port 8007 &
cd services/fertilizer-optimization && source venv/bin/activate && uvicorn src.main:app --port 8008 &
cd services/image-analysis && source venv/bin/activate && uvicorn src.main:app --port 8004 &
cd services/location-management && source venv/bin/activate && uvicorn src.main:app --port 8009 &
cd services/weather-service && source venv/bin/activate && uvicorn src.main:app --port 8010 &
```

**Related Tickets**: All JOB*-015/012/013/011/012 tickets

---

## INT-002: API Contract Verification Tests

**Priority**: Critical  
**Estimated Effort**: 4 hours  
**Dependencies**: INT-001  
**Blocks**: INT-004, INT-005, INT-006  
**Parallel Execution**: No

**Description**:
Create and run API contract tests to verify all services match documented contracts.

**Acceptance Criteria**:
- [ ] Contract tests created for all 5 services
- [ ] All endpoints return expected response structure
- [ ] Required fields present in responses
- [ ] HTTP status codes correct
- [ ] All contract tests passing

**Technical Details**:

Create `tests/integration/test_api_contracts.py` - See integration.md for complete implementation.

**Validation Commands**:
```bash
mkdir -p tests/integration
pytest tests/integration/test_api_contracts.py -v
```

**Related Tickets**: All JOB tickets

---

## INT-003: Create Service Client Libraries

**Priority**: High  
**Estimated Effort**: 6 hours  
**Dependencies**: INT-001  
**Blocks**: INT-004, INT-005, INT-006, INT-007  
**Parallel Execution**: Can run parallel with INT-002

**Description**:
Create client libraries for service-to-service communication.

**Acceptance Criteria**:
- [ ] LocationServiceClient created
- [ ] FertilizerOptimizationClient created
- [ ] CropTaxonomyClient created
- [ ] WeatherServiceClient created
- [ ] All clients tested

**Technical Details**:

Create client files:
- `services/weather-service/src/integrations/location_client.py`
- `services/image-analysis/src/integrations/fertilizer_client.py`
- `services/fertilizer-optimization/src/integrations/crop_client.py`
- `services/recommendation-engine/src/integrations/weather_client.py`

See integration.md for complete implementations.

**Validation Commands**:
```bash
pytest tests/integration/test_service_clients.py -v
```

**Related Tickets**: All JOB tickets

---

## INT-004: Integrate Location Service with Weather Service

**Priority**: Critical  
**Estimated Effort**: 6 hours  
**Dependencies**: INT-002, INT-003, JOB4-011, JOB5-012  
**Blocks**: INT-008  
**Parallel Execution**: Can run parallel with INT-005, INT-006

**Description**:
Integrate location service with weather service so weather data can be fetched for farm locations.

**Acceptance Criteria**:
- [ ] Weather service can fetch farm coordinates from location service
- [ ] Weather data stored with location reference
- [ ] Integration test passing
- [ ] Error handling working

**Technical Details**:

Update `services/weather-service/src/api/weather_routes.py` to use LocationServiceClient.

**Validation Commands**:
```bash
pytest tests/integration/test_location_weather_integration.py -v
```

**Related Tickets**: JOB4-011, JOB5-012

---

## INT-005: Integrate Deficiency Detection with Fertilizer Optimization

**Priority**: Critical  
**Estimated Effort**: 8 hours  
**Dependencies**: INT-002, INT-003, JOB2-012, JOB3-013  
**Blocks**: INT-008  
**Parallel Execution**: Can run parallel with INT-004, INT-006

**Description**:
Integrate deficiency detection with fertilizer optimization to provide complete recommendations.

**Acceptance Criteria**:
- [ ] Deficiency detection triggers fertilizer recommendations
- [ ] Nutrient requirements calculated from deficiencies
- [ ] Fertilizer prices fetched automatically
- [ ] Complete workflow tested
- [ ] Integration test passing

**Technical Details**:

Create `services/image-analysis/src/integrations/fertilizer_client.py` - See integration.md for implementation.

Update `services/image-analysis/src/api/analysis_routes.py` to add `/image-analysis-with-recommendations` endpoint.

**Validation Commands**:
```bash
pytest tests/integration/test_deficiency_fertilizer_integration.py -v

# Test end-to-end
curl -X POST http://localhost:8004/api/v1/deficiency/image-analysis-with-recommendations \
  -F "image=@tests/fixtures/corn_nitrogen_deficiency.jpg" \
  -F "crop_type=corn" \
  -F "field_acres=100" \
  -F "yield_goal=180"
```

**Related Tickets**: JOB2-012, JOB3-013

---

## INT-006: Integrate Crop Filtering with All Services

**Priority**: High  
**Estimated Effort**: 6 hours  
**Dependencies**: INT-002, INT-003, JOB1-015  
**Blocks**: INT-008  
**Parallel Execution**: Can run parallel with INT-004, INT-005

**Description**:
Integrate crop filtering service to provide variety data to other services.

**Acceptance Criteria**:
- [ ] Crop variety data accessible from other services
- [ ] Nutrient requirements fetched from crop service
- [ ] Integration tests passing

**Technical Details**:

Create `services/crop-taxonomy/src/integrations/shared_client.py` - See integration.md for implementation.

**Validation Commands**:
```bash
pytest tests/integration/test_crop_integration.py -v
```

**Related Tickets**: JOB1-015

---

## INT-007: Implement Weather-Based Fertilizer Application Timing

**Priority**: Medium  
**Estimated Effort**: 6 hours  
**Dependencies**: INT-004, INT-005, JOB2-012, JOB5-012  
**Blocks**: INT-008  
**Parallel Execution**: Can run parallel with INT-006

**Description**:
Integrate weather service with fertilizer optimization to recommend optimal application timing.

**Acceptance Criteria**:
- [ ] Weather forecast considered in fertilizer recommendations
- [ ] Application timing recommendations provided
- [ ] Rain delay warnings implemented
- [ ] Integration test passing

**Validation Commands**:
```bash
pytest tests/integration/test_weather_fertilizer_integration.py -v
```

**Related Tickets**: JOB2-012, JOB5-012

---

## INT-008: End-to-End Workflow Testing

**Priority**: Critical  
**Estimated Effort**: 1 day  
**Dependencies**: INT-004, INT-005, INT-006, INT-007  
**Blocks**: INT-009  
**Parallel Execution**: No

**Description**:
Test complete farm advisory workflow from farm setup to recommendations.

**Acceptance Criteria**:
- [ ] Complete workflow test created
- [ ] Farm location creation → weather → deficiency → fertilizer → varieties workflow working
- [ ] All integration points tested
- [ ] Test passes consistently

**Technical Details**:

Create `tests/integration/test_complete_workflow.py` - See integration.md for complete implementation.

**Validation Commands**:
```bash
pytest tests/integration/test_complete_workflow.py -v -s
```

**Related Tickets**: All JOB tickets

---

## INT-009: Performance Optimization

**Priority**: High  
**Estimated Effort**: 1 day  
**Dependencies**: INT-008  
**Blocks**: INT-010  
**Parallel Execution**: No

**Description**:
Optimize integrated system to meet performance requirements.

**Acceptance Criteria**:
- [ ] Average response time <3s for complex workflows
- [ ] Database queries optimized
- [ ] No N+1 query problems
- [ ] Performance tests passing
- [ ] Missing indexes added

**Technical Details**:

Create `tests/integration/test_performance.py` - See integration.md for implementation.

**Validation Commands**:
```bash
pytest tests/integration/test_performance.py -v

# Check slow queries
psql -U postgres -d caain_soil_hub -c "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 20;"

# Add missing indexes if needed
psql -U postgres -d caain_soil_hub -c "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fertilizer_prices_date ON fertilizer_prices(price_date DESC);"
```

**Related Tickets**: All JOB tickets

---

## INT-010: Error Handling and Resilience Testing

**Priority**: High  
**Estimated Effort**: 6 hours  
**Dependencies**: INT-009  
**Blocks**: INT-011  
**Parallel Execution**: No

**Description**:
Test error handling across service boundaries and implement circuit breakers.

**Acceptance Criteria**:
- [ ] Service failures handled gracefully
- [ ] Fallback mechanisms working
- [ ] Error messages informative
- [ ] Timeout handling working
- [ ] Resilience tests passing

**Validation Commands**:
```bash
pytest tests/integration/test_error_handling.py -v
```

**Related Tickets**: All JOB tickets

---

## INT-011: Integration Test Suite Completion

**Priority**: High  
**Estimated Effort**: 4 hours  
**Dependencies**: INT-010  
**Blocks**: INT-012  
**Parallel Execution**: No

**Description**:
Complete integration test suite with >70% coverage.

**Acceptance Criteria**:
- [ ] Integration test coverage >70%
- [ ] All critical workflows tested
- [ ] Performance tests included
- [ ] All tests passing

**Validation Commands**:
```bash
pytest tests/integration/ -v --cov=services --cov-report=html
open htmlcov/index.html
```

**Related Tickets**: All JOB tickets

---

## INT-012: Agricultural Expert Review

**Priority**: Critical  
**Estimated Effort**: 1 day  
**Dependencies**: INT-011  
**Blocks**: INT-013  
**Parallel Execution**: No

**Description**:
Conduct agricultural expert review of integrated system with real-world scenarios.

**Acceptance Criteria**:
- [ ] Real-world scenarios tested
- [ ] Crop recommendations validated
- [ ] Fertilizer calculations verified
- [ ] Weather impact assessments reviewed
- [ ] Expert feedback incorporated

**Technical Details**:

Test scenarios:
1. Iowa Corn Farm - Nitrogen deficiency
2. Illinois Soybean Farm - Iron chlorosis
3. Kansas Wheat Farm - Drought stress

See integration.md for complete scenario descriptions.

**Validation Commands**:
```bash
# Run real-world scenario tests
pytest tests/integration/test_real_world_scenarios.py -v
```

**Related Tickets**: All JOB tickets

---

## INT-013: Documentation and Deployment Guide

**Priority**: High  
**Estimated Effort**: 6 hours  
**Dependencies**: INT-012  
**Blocks**: INT-014  
**Parallel Execution**: No

**Description**:
Create comprehensive documentation for integrated system.

**Acceptance Criteria**:
- [ ] Integration architecture documented
- [ ] API integration points documented
- [ ] Deployment guide created
- [ ] Troubleshooting guide created
- [ ] User documentation updated

**Validation Commands**:
```bash
cat docs/integration-architecture.md
cat docs/deployment-guide.md
cat docs/troubleshooting.md
```

**Related Tickets**: All JOB tickets

---

## INT-014: Final Integration Sign-Off

**Priority**: Critical  
**Estimated Effort**: 4 hours  
**Dependencies**: INT-013  
**Blocks**: None (Integration complete)  
**Parallel Execution**: No

**Description**:
Final validation and sign-off for integrated system.

**Acceptance Criteria**:
- [ ] All services running and healthy
- [ ] All integration tests passing
- [ ] Performance requirements met
- [ ] Agricultural expert approval obtained
- [ ] Documentation complete
- [ ] Ready for production deployment

**Validation Commands**:
```bash
# Run full test suite
pytest tests/ -v --cov=services --cov-report=html

# Check all services
for port in 8007 8008 8004 8009 8010; do
  echo "Checking port $port..."
  curl http://localhost:$port/health
done

# Run end-to-end workflow
pytest tests/integration/test_complete_workflow.py -v -s
```

**Related Tickets**: All JOB and INT tickets

---

## Summary

**Total Tickets**: 14  
**Critical Path**: INT-001 → INT-002 → INT-003 → INT-004 → INT-008 → INT-009 → INT-010 → INT-011 → INT-012 → INT-013 → INT-014  
**Estimated Total Time**: 2 weeks  
**Parallel Opportunities**: INT-002/003, INT-004/005/006/007

## Success Criteria

Integration is successful when:

✅ All services running and healthy  
✅ End-to-end workflows complete successfully  
✅ Performance requirements met (<3s for complex workflows)  
✅ Agricultural expert validates recommendations  
✅ Integration tests pass with >70% coverage  
✅ No critical bugs in production scenarios  
✅ Documentation complete  
✅ Ready for production deployment

## Cross-Job Dependencies Summary

- **INT-004**: Depends on JOB4-011, JOB5-012
- **INT-005**: Depends on JOB2-012, JOB3-013
- **INT-006**: Depends on JOB1-015
- **INT-007**: Depends on JOB2-012, JOB5-012
- **INT-008**: Depends on all JOB tickets (JOB1-015, JOB2-012, JOB3-013, JOB4-011, JOB5-012)


