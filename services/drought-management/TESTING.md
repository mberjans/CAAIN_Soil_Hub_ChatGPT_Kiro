# Drought Management System - Testing Documentation

## Overview

This document describes the comprehensive testing suite for the Drought Management System, implemented as part of **TICKET-014_drought-management-13.1**.

## Testing Architecture

The testing suite is organized into several categories:

### 1. Unit Tests (`test_drought_management_comprehensive.py`)
- **Purpose**: Test individual components and functions in isolation
- **Coverage**: All service methods, data models, and utility functions
- **Markers**: `@pytest.mark.unit`

### 2. Integration Tests (`test_drought_management_comprehensive.py`)
- **Purpose**: Test interactions between services and external dependencies
- **Coverage**: End-to-end workflows, API integrations, database operations
- **Markers**: `@pytest.mark.integration`

### 3. Agricultural Validation Tests (`test_agricultural_validation.py`)
- **Purpose**: Validate recommendations against known agricultural scenarios and research data
- **Coverage**: Historical drought events, conservation practice effectiveness, crop response models
- **Markers**: `@pytest.mark.agricultural`

### 4. Performance Tests (`test_performance.py`)
- **Purpose**: Test system performance under various load conditions
- **Coverage**: Response times, concurrent requests, memory usage, scalability
- **Markers**: `@pytest.mark.performance`

### 5. Test Data Fixtures (`test_data_fixtures.py`)
- **Purpose**: Provide realistic test data for all test scenarios
- **Coverage**: Farm locations, weather data, soil data, crop information, historical scenarios

## Test Coverage Requirements

- **Minimum Coverage**: 80% code coverage
- **Critical Paths**: 95% coverage for core drought assessment logic
- **Agricultural Validation**: 100% coverage for known scenarios
- **Performance**: All critical paths tested under load

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Check test environment
python run_tests.py --check-env
```

### Test Execution

```bash
# Run all tests with coverage
python run_tests.py --test-type all

# Run specific test types
python run_tests.py --test-type unit
python run_tests.py --test-type integration
python run_tests.py --test-type agricultural
python run_tests.py --test-type performance

# Run specific test file
python run_tests.py --test-type specific --test-file test_agricultural_validation.py

# Generate comprehensive test report
python run_tests.py --test-type report
```

### Direct pytest Usage

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific markers
pytest tests/ -m unit -v
pytest tests/ -m agricultural -v
pytest tests/ -m performance -v

# Run specific test file
pytest tests/test_agricultural_validation.py -v
```

## Test Categories

### Unit Tests

Test individual service methods and functions:

```python
@pytest.mark.unit
@pytest.mark.asyncio
async def test_drought_risk_calculation(self, mock_external_services):
    """Test drought risk calculation with various scenarios."""
    # Test implementation
```

### Integration Tests

Test complete workflows and service interactions:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_drought_management_workflow(self):
    """Test complete drought management workflow."""
    # Test implementation
```

### Agricultural Validation Tests

Validate against known agricultural scenarios:

```python
@pytest.mark.agricultural
@pytest.mark.asyncio
async def test_2012_drought_scenario(self):
    """Test against 2012 drought scenario (severe drought in Midwest)."""
    # Test implementation
```

### Performance Tests

Test system performance and scalability:

```python
@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_assessment_requests(self, performance_test_data):
    """Test system performance under concurrent assessment requests."""
    # Test implementation
```

## Test Data

### Historical Drought Scenarios

The test suite includes validation against known historical drought events:

- **2012 Midwest Drought**: Severe drought with 25% yield loss
- **2017 California Drought**: Moderate drought with irrigation
- **2019 Texas Drought**: Severe drought with 18% yield loss

### Conservation Practice Data

Validation against agricultural research data:

- **Cover Crops**: 12-18% water savings, 15% soil health improvement
- **No-Till**: 20-30% water savings, 25% soil health improvement
- **Mulching**: 15-25% water savings, 20% soil health improvement

### Crop Response Models

Validation against crop physiology research:

- **Corn**: Critical stages VT, R1, R2 with specific sensitivity factors
- **Soybeans**: Critical stages R1, R2, R3 with yield sensitivity data
- **Wheat**: Critical stages with drought tolerance characteristics

## Performance Benchmarks

### Response Time Requirements

- **Drought Assessment**: < 2 seconds average, < 3 seconds maximum
- **Conservation Recommendations**: < 1.5 seconds average, < 2.5 seconds maximum
- **Monitoring Setup**: < 1 second average, < 2 seconds maximum

### Concurrent Load Requirements

- **Concurrent Assessments**: 50 requests in < 5 seconds
- **Monitoring Requests**: 30 requests in < 8 seconds
- **Throughput**: Minimum 10 requests/second for assessments

### Memory Requirements

- **Memory Increase**: < 100MB during large dataset processing
- **Memory Leaks**: < 50MB increase after 100 iterations
- **Final Memory**: < 500MB total usage

## CI/CD Integration

### GitHub Actions Workflow

The test suite is integrated with GitHub Actions for automated testing:

```yaml
name: Drought Management System Tests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
```

### Test Matrix

- **Python Versions**: 3.11, 3.12
- **Test Types**: Unit, Integration, Agricultural, Performance
- **Coverage**: Minimum 80% code coverage
- **Security**: Bandit and Safety scans

## Test Reports

### Coverage Reports

- **Terminal**: Real-time coverage during test execution
- **HTML**: Detailed coverage report in `htmlcov/index.html`
- **XML**: Coverage data for CI/CD integration

### Performance Reports

- **Response Times**: Detailed timing for all operations
- **Memory Usage**: Memory consumption tracking
- **Throughput**: Requests per second measurements

### Agricultural Validation Reports

- **Scenario Validation**: Results against historical drought events
- **Research Compliance**: Validation against agricultural research data
- **Expert Review**: Flagged items for agricultural expert review

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src` directory is in Python path
2. **Mock Failures**: Check mock configurations in `conftest.py`
3. **Performance Failures**: Verify system resources and test environment
4. **Agricultural Validation Failures**: Review test data against current research

### Debug Mode

```bash
# Run tests with debug output
pytest tests/ -v -s --tb=long

# Run specific test with debug
pytest tests/test_agricultural_validation.py::TestDroughtScenarioValidation::test_2012_midwest_drought -v -s
```

### Test Environment Setup

```bash
# Check environment
python run_tests.py --check-env

# Install missing dependencies
pip install -r requirements-test.txt

# Verify test files
ls -la tests/
```

## Contributing

### Adding New Tests

1. **Follow Naming Conventions**: `test_*.py` for test files
2. **Use Appropriate Markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
3. **Include Docstrings**: Describe test purpose and expected behavior
4. **Use Fixtures**: Leverage `conftest.py` fixtures for common test data
5. **Validate Agricultural Data**: Ensure new tests align with agricultural research

### Test Data Updates

1. **Historical Scenarios**: Update with new drought events and research
2. **Conservation Practices**: Include latest agricultural research findings
3. **Crop Models**: Update with new crop physiology research
4. **Performance Benchmarks**: Adjust based on system improvements

## Quality Assurance

### Pre-commit Checks

- **Code Quality**: Flake8 linting
- **Test Coverage**: Minimum 80% coverage
- **Performance**: Response time requirements met
- **Agricultural Validation**: All known scenarios pass

### Expert Review Process

- **Agricultural Logic**: Flag complex agricultural calculations for expert review
- **Validation Results**: Review agricultural validation test results
- **Research Compliance**: Ensure test data aligns with current research
- **Recommendation Accuracy**: Validate recommendation quality

## Monitoring and Maintenance

### Regular Updates

- **Monthly**: Update agricultural research data
- **Quarterly**: Review and update performance benchmarks
- **Annually**: Comprehensive test suite review and updates

### Test Maintenance

- **Test Data**: Keep test data current with agricultural research
- **Performance Benchmarks**: Adjust based on system improvements
- **Coverage Goals**: Maintain and improve test coverage
- **Documentation**: Keep testing documentation current

---

**TICKET-014_drought-management-13.1**: Comprehensive drought management testing suite implementation complete.

For questions or issues with the testing suite, please refer to the test logs or contact the development team.