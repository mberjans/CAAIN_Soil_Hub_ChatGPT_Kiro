# Fertilizer Timing Optimization - Test Suite

## Overview

This directory contains the comprehensive test suite for the CAAIN Soil Hub fertilizer timing optimization service. The test suite validates timing algorithms, weather integration, operational constraints, and agricultural best practices.

## Test Files

### Main Test Files

1. **test_fertilizer_timing_comprehensive.py** (1,200+ lines)
   - Comprehensive test suite with 40 test cases
   - Covers all major functional areas
   - Organized into 7 test classes by category
   - Uses pytest and pytest-asyncio frameworks

2. **conftest.py** (600+ lines)
   - Shared test fixtures and utilities
   - Mock service implementations
   - Test data generators
   - Helper functions and validators
   - Performance monitoring utilities

### Test Data

3. **data/sample_timing_scenarios.json**
   - 6 realistic fertilizer timing scenarios
   - Covers multiple crops and conditions
   - Includes challenging edge cases

4. **data/weather_patterns.json**
   - 4 weather forecast patterns
   - Tests various weather conditions
   - Validates weather integration logic

5. **data/README.md**
   - Documentation for test data
   - Usage guidelines
   - Data structure reference

### Documentation

6. **TEST_SUMMARY.md**
   - Comprehensive test suite documentation
   - Coverage analysis and metrics
   - Test execution guide
   - Performance benchmarks
   - Agricultural validation criteria

7. **README.md** (this file)
   - Quick start guide
   - Test structure overview
   - Execution instructions

## Test Categories

### 1. Timing Algorithm Accuracy (5 tests)
Tests validate core timing calculations and optimization algorithms.

**Tests:**
- Optimal timing calculation for corn
- Seasonal adjustment (spring/fall)
- Growth stage synchronization
- Split application timing
- N/P/K timing optimization

### 2. Weather Integration (5 tests)
Tests verify weather data integration and timing adjustments.

**Tests:**
- Weather forecast integration
- Precipitation impact on timing
- Temperature-based adjustments
- Soil moisture considerations
- Weather window identification

### 3. Constraint Handling (5 tests)
Tests validate operational constraint evaluation and accommodation.

**Tests:**
- Equipment availability constraints
- Labor constraints
- Regulatory compliance
- Field condition constraints
- Alternative schedule generation

### 4. Performance and Load (4 tests)
Tests verify system performance under various load conditions.

**Tests:**
- Single request response time (< 3s)
- Concurrent optimization requests
- Load test with 50+ concurrent requests
- Memory usage under sustained load

### 5. Agricultural Validation (6 tests)
Tests ensure alignment with agronomic principles and best practices.

**Tests:**
- Agronomic principles alignment (4R Stewardship)
- Crop-specific timing rules (corn)
- Crop-specific timing rules (soybean)
- Nutrient uptake pattern validation
- Application method compatibility
- Environmental impact considerations

### 6. Edge Cases and Boundaries (8 tests)
Tests validate system behavior with extreme or unusual inputs.

**Tests:**
- Very early planting date
- Very late planting date
- Extreme soil moisture (dry)
- Extreme soil moisture (saturated)
- Zero fertilizer requirements
- Very high fertilizer rates
- No equipment or labor available
- Invalid location coordinates

### 7. Data Validation (7 tests)
Tests verify input/output data structure validation.

**Tests:**
- Timing request validation
- Field ID requirement
- Location validation
- Fertilizer requirements validation
- Optimization result structure
- Application timing structure
- Weather window structure

## Quick Start

### Prerequisites

```bash
# Ensure dependencies are installed
pip install -r requirements.txt

# Additional test dependencies
pip install pytest pytest-asyncio pytest-cov
```

### Running Tests

```bash
# Run all tests
pytest tests/test_fertilizer_timing_comprehensive.py -v

# Run with coverage report
pytest tests/test_fertilizer_timing_comprehensive.py --cov=src --cov-report=html

# Run specific test category
pytest tests/test_fertilizer_timing_comprehensive.py::TestTimingAlgorithmAccuracy -v

# Run excluding slow tests
pytest tests/test_fertilizer_timing_comprehensive.py -m "not slow" -v

# Run with detailed output
pytest tests/test_fertilizer_timing_comprehensive.py -vv -s

# Run and stop on first failure
pytest tests/test_fertilizer_timing_comprehensive.py -x -vv
```

### Viewing Coverage

```bash
# Generate HTML coverage report
pytest tests/test_fertilizer_timing_comprehensive.py --cov=src --cov-report=html

# Open coverage report in browser (Mac)
open htmlcov/index.html

# Open coverage report in browser (Linux)
xdg-open htmlcov/index.html
```

## Test Markers

The test suite uses pytest markers to categorize tests:

- `@pytest.mark.slow` - Long-running tests (>5 seconds)
- `@pytest.mark.integration` - Integration tests requiring external services
- `@pytest.mark.performance` - Performance and load tests
- `@pytest.mark.unit` - Unit tests for isolated components

### Using Markers

```bash
# Run only unit tests
pytest tests/test_fertilizer_timing_comprehensive.py -m "unit" -v

# Run integration tests
pytest tests/test_fertilizer_timing_comprehensive.py -m "integration" -v

# Exclude slow tests
pytest tests/test_fertilizer_timing_comprehensive.py -m "not slow" -v

# Run performance tests only
pytest tests/test_fertilizer_timing_comprehensive.py -m "performance" -v
```

## Test Structure

### Test Organization

```
tests/
├── conftest.py                          # Shared fixtures and utilities
├── test_fertilizer_timing_comprehensive.py  # Main test suite (40 tests)
├── data/
│   ├── sample_timing_scenarios.json     # Test scenarios
│   ├── weather_patterns.json            # Weather test data
│   └── README.md                        # Data documentation
├── TEST_SUMMARY.md                      # Comprehensive documentation
└── README.md                            # This file
```

### Key Classes and Utilities

#### From conftest.py:
- `MockWeatherService` - Mock weather data provider
- `MockSoilService` - Mock soil data provider
- `MockForecastDay` - Weather forecast day model
- `PerformanceMonitor` - Performance metrics tracker
- Various fixtures for common test data

#### From test_fertilizer_timing_comprehensive.py:
- `TestDataFactory` - Creates realistic test data objects
- `_TimingOptimizationAdapterStub` - Mock timing service
- 7 test classes organized by category

## Writing New Tests

### Template for New Test

```python
@pytest.mark.asyncio
async def test_new_functionality(self):
    """
    Test description explaining what is being validated.

    This test verifies that [specific functionality] works correctly
    under [specific conditions].
    """
    # Arrange - Set up test data
    request = TestDataFactory.create_timing_request(
        crop_type="corn",
        planting_date=date(2024, 5, 1),
    )

    # Act - Execute the functionality
    service = YourService()
    result = await service.your_method(request)

    # Assert - Verify expected outcomes
    assert result is not None
    assert result.some_property == expected_value
```

### Best Practices

1. **Use Descriptive Names**: Test names should clearly describe what is being tested
2. **Follow AAA Pattern**: Arrange, Act, Assert structure
3. **Test One Thing**: Each test should validate a single behavior
4. **Use Fixtures**: Leverage conftest.py fixtures for common test data
5. **Document Tests**: Include docstrings explaining test purpose
6. **Handle Async**: Use `@pytest.mark.asyncio` for async tests
7. **Clean Up**: Ensure tests don't leave side effects

## Test Data

### Using Sample Scenarios

```python
import json
from pathlib import Path

# Load sample scenarios
test_data_dir = Path(__file__).parent / "data"
with open(test_data_dir / "sample_timing_scenarios.json") as f:
    scenarios = json.load(f)

# Use in test
corn_scenario = next(
    s for s in scenarios["scenarios"]
    if s["id"] == "corn_optimal_spring"
)
```

### Using Weather Patterns

```python
# Load weather patterns
with open(test_data_dir / "weather_patterns.json") as f:
    weather_data = json.load(f)

# Use in test
ideal_spring = next(
    p for p in weather_data["weather_patterns"]
    if p["id"] == "ideal_spring"
)
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: |
          pytest tests/test_fertilizer_timing_comprehensive.py \
            --cov=src \
            --cov-report=xml \
            --cov-report=term-missing
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Performance Benchmarks

### Expected Performance

| Metric | Target | Test Validation |
|--------|--------|-----------------|
| Single Request | < 3 seconds | test_response_time_single_request |
| 10 Concurrent | < 5 seconds avg | test_concurrent_optimization_requests |
| Throughput | > 10 req/sec | test_load_test_500_concurrent_optimizations |
| Memory | Stable | test_memory_usage_under_load |

## Agricultural Validation

### 4R Nutrient Stewardship

Tests validate alignment with the 4R framework:

1. **Right Time**: Growth stage synchronization, weather windows
2. **Right Rate**: Application rate validation, split applications
3. **Right Place**: Field condition assessment, trafficability
4. **Right Source**: Fertilizer type appropriateness, method compatibility

### Crop-Specific Guidelines

- **Corn**: V4-V6 sidedress timing, split applications for high N
- **Soybean**: Reduced N requirements, nodulation considerations
- **Wheat**: Spring topdress timing, sulfur supplementation

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# Ensure src directory is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### Async Test Failures
```bash
# Ensure pytest-asyncio is installed
pip install pytest-asyncio

# Check pytest.ini has asyncio mode configured
```

#### Fixture Not Found
```bash
# Ensure conftest.py is in tests directory
# Check fixture scope (function, class, module, session)
```

#### Mock Service Issues
```bash
# Verify stub modules are properly initialized
# Check sys.modules configuration in test file
```

## Coverage Goals

### Current Coverage: ~65%
### Target Coverage: >90%

### Coverage by Module

| Module | Current | Target |
|--------|---------|--------|
| timing_services/ | ~60% | 90% |
| services/constraint_service.py | ~75% | 95% |
| services/weather_integration_service.py | ~65% | 90% |
| services/crop_integration_service.py | ~50% | 85% |
| models/ | ~80% | 95% |

## Contributing

### Adding New Tests

1. **Identify Gap**: Find functionality not covered by existing tests
2. **Write Test**: Follow template and best practices above
3. **Add Documentation**: Update TEST_SUMMARY.md with new test details
4. **Verify Coverage**: Ensure coverage improves
5. **Submit PR**: Include test rationale and expected outcomes

### Improving Existing Tests

1. **Review Failures**: Analyze why tests fail
2. **Enhance Stubs**: Improve mock service implementations
3. **Add Scenarios**: Expand test data coverage
4. **Update Documentation**: Reflect changes in TEST_SUMMARY.md

## Support and Resources

### Documentation
- [TEST_SUMMARY.md](./TEST_SUMMARY.md) - Comprehensive test documentation
- [data/README.md](./data/README.md) - Test data documentation
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)

### Agricultural Resources
- [4R Nutrient Stewardship](http://www.nutrientstewardship.com/)
- [University Extension Guidelines](https://extension.org/)
- [NRCS Conservation Practice Standards](https://www.nrcs.usda.gov/wps/portal/nrcs/main/national/technical/cp/ncps/)

### Code Quality
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [Python Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## License

This test suite is part of the CAAIN Soil Hub project and follows the same license as the main project.

---

**Last Updated**: October 19, 2024
**Test Suite Version**: 1.0
**Maintained By**: CAAIN Soil Hub Development Team
