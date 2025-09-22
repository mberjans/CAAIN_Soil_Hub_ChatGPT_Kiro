# AFAS Testing Documentation

## Overview

This document describes the comprehensive testing framework for the Autonomous Farm Advisory System (AFAS). The testing strategy ensures agricultural accuracy, system reliability, security, and performance while maintaining high code quality standards.

## Testing Philosophy

### Agricultural Accuracy First
- All agricultural logic must be validated by certified agricultural experts
- Recommendations must align with established extension service guidelines
- Conservative approach when dealing with uncertain agricultural conditions
- Traceability of all agricultural decisions and their sources

### Comprehensive Coverage
- **Unit Tests**: Individual component functionality
- **Integration Tests**: Cross-service workflows and data flow
- **Agricultural Tests**: Domain-specific accuracy validation
- **Performance Tests**: Response time and scalability requirements
- **Security Tests**: Authentication, authorization, and input validation

## Test Structure

```
tests/
├── unit/                           # Unit tests for individual components
│   ├── test_recommendation_engine.py
│   ├── test_data_integration.py
│   └── test_question_router.py
├── integration/                    # Integration and workflow tests
│   ├── test_recommendation_workflows.py
│   └── test_cross_service_integration.py
├── agricultural/                   # Agricultural accuracy tests
│   ├── test_nutrient_calculations.py
│   ├── test_crop_suitability.py
│   └── test_soil_health.py
├── performance/                    # Performance and load tests
│   └── test_system_performance.py
├── security/                      # Security tests
│   ├── test_authentication.py
│   └── test_input_validation.py
└── e2e/                          # End-to-end user scenarios
```

## Running Tests

### Quick Development Tests
```bash
# Run core unit and agricultural tests
python run_tests.py quick

# Run with verbose output
python run_tests.py quick --verbose
```

### Comprehensive Test Suite
```bash
# Run all tests (excluding slow performance tests)
python run_tests.py all

# Run all tests including performance tests
python run_tests.py all --slow --coverage
```

### Specific Test Categories
```bash
# Unit tests only
python run_tests.py unit --coverage

# Integration tests
python run_tests.py integration

# Agricultural accuracy tests
python run_tests.py agricultural

# Performance tests
python run_tests.py performance

# Security tests
python run_tests.py security
```

### Service-Specific Tests
```bash
# Test specific service
python run_tests.py --service recommendation-engine

# Test with verbose output
python run_tests.py --service data-integration --verbose
```

### CI/CD Pipeline Tests
```bash
# Run CI-optimized test suite
python run_tests.py ci
```

## Test Categories

### Unit Tests

**Purpose**: Test individual components in isolation
**Location**: `tests/unit/`
**Markers**: `@pytest.mark.unit`

**Coverage Requirements**:
- Minimum 80% code coverage
- All public methods tested
- Edge cases and error conditions covered
- Agricultural calculation accuracy validated

**Example**:
```python
@pytest.mark.unit
@pytest.mark.agricultural
def test_nitrogen_rate_calculation_iowa_corn(self, fertilizer_service, iowa_corn_farm_data):
    """Test nitrogen rate calculation for Iowa corn."""
    crop_data = {
        'crop_type': 'corn',
        'yield_goal': 180,
        'soil_data': iowa_corn_farm_data['soil_data']
    }
    
    result = fertilizer_service.calculate_nitrogen_rate(crop_data)
    
    # Validate agricultural accuracy
    assert 80 <= result['total_n_rate_lbs_per_acre'] <= 220
    assert result['confidence_score'] >= 0.8
```

### Integration Tests

**Purpose**: Test workflows across multiple services
**Location**: `tests/integration/`
**Markers**: `@pytest.mark.integration`

**Focus Areas**:
- End-to-end recommendation workflows
- Data flow between services
- External API integration
- Error handling and fallbacks

**Example**:
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_complete_crop_selection_workflow(self, iowa_corn_farm_data):
    """Test end-to-end crop selection process."""
    # Test complete workflow from input to recommendation
    result = await generate_crop_recommendations(request_data)
    
    assert result['confidence_score'] >= 0.7
    assert 'corn' in [rec['crop_name'] for rec in result['recommendations']]
```

### Agricultural Tests

**Purpose**: Validate agricultural accuracy against expert knowledge
**Location**: `tests/agricultural/`
**Markers**: `@pytest.mark.agricultural`

**Validation Requirements**:
- Expert review of all agricultural logic
- Comparison with extension service guidelines
- Regional variation testing
- Conservative recommendation validation

**Key Test Areas**:
- Nutrient calculation accuracy
- Crop suitability algorithms
- Soil health assessment
- Regional adaptation

**Example**:
```python
@pytest.mark.agricultural
def test_corn_nitrogen_rate_iowa_state_guidelines(self, iowa_corn_scenario):
    """Test N rate calculation matches Iowa State Extension guidelines."""
    # Test against known Iowa State Extension PM 1688 guidelines
    expected_base_rate = 160  # lbs N/acre for 180 bu goal
    expected_legume_credit = 40  # lbs N/acre from previous soybean
    
    result = calculate_nitrogen_rate(iowa_corn_scenario)
    
    assert abs(result['total_n_rate'] - expected_final_rate) <= 10
    assert 'Iowa State University Extension' in result['source']
```

### Performance Tests

**Purpose**: Ensure system meets performance requirements
**Location**: `tests/performance/`
**Markers**: `@pytest.mark.performance`

**Requirements**:
- Recommendations return within 3 seconds
- System handles 1000+ concurrent users
- Database queries complete within acceptable limits
- Memory usage remains reasonable under load

**Example**:
```python
@pytest.mark.performance
async def test_recommendation_response_time(self, performance_timer):
    """Test that recommendations return within 3 seconds."""
    performance_timer.start()
    result = await generate_crop_recommendations(request_data)
    performance_timer.stop()
    
    assert performance_timer.elapsed < 3.0
    assert result['confidence_score'] >= 0.7
```

### Security Tests

**Purpose**: Validate security controls and data protection
**Location**: `tests/security/`
**Markers**: `@pytest.mark.security`

**Security Areas**:
- Authentication and authorization
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- Farm data access controls

**Example**:
```python
@pytest.mark.security
def test_farm_access_authorization(self):
    """Test that users can only access their own farms."""
    user_a = {'user_id': 'user_a', 'farm_ids': ['farm_123']}
    
    assert check_farm_access(user_a, 'farm_123')  # Own farm
    assert not check_farm_access(user_a, 'farm_789')  # Other farm
```

## Test Data and Fixtures

### Agricultural Test Data
The testing framework includes realistic agricultural test data:

- **Iowa Corn Farm**: Typical Midwest corn/soybean operation
- **California Vegetable Farm**: Irrigated vegetable production
- **Problematic Soil**: Challenging conditions for edge case testing

### Shared Fixtures
Located in `conftest.py`:
- Database connections
- Mock external APIs
- Agricultural validation utilities
- Performance monitoring tools

### Test Data Factory
```python
class AgriculturalTestDataFactory:
    @staticmethod
    def create_iowa_corn_farm():
        return {
            'location': {'latitude': 42.0308, 'longitude': -93.6319},
            'soil_data': {'ph': 6.4, 'organic_matter_percent': 3.5},
            'farm_size_acres': 320
        }
```

## Agricultural Validation Standards

### Expert Review Process
1. All agricultural logic changes require expert review
2. Test cases must be validated by certified agricultural professionals
3. Regional variations must be tested and validated
4. Conservative approach when recommendations are uncertain

### Extension Service Alignment
- Test against published extension service guidelines
- Reference specific publications (e.g., Iowa State PM 1688)
- Validate calculations match university recommendations
- Ensure regional applicability

### Confidence Scoring
- All recommendations include confidence scores
- Low confidence triggers additional warnings
- Conservative recommendations when data is limited
- Transparent communication of uncertainty

## Performance Requirements

### Response Time Targets
- Crop recommendations: < 3 seconds
- Fertilizer calculations: < 2 seconds
- Soil health assessment: < 1.5 seconds
- Database queries: < 500ms

### Scalability Targets
- 1000+ concurrent users
- 95% success rate under load
- 95th percentile response time < 8 seconds
- Memory usage < 500MB increase under load

### Database Performance
- Soil test queries: < 500ms
- Recommendation history: < 1 second
- Complex analytical queries: < 5 seconds

## Security Testing Standards

### Authentication Testing
- Password hashing security (bcrypt, 12+ rounds)
- JWT token validation and expiration
- Multi-factor authentication (TOTP)
- Session management and timeout
- Account lockout protection

### Authorization Testing
- Farm-level access controls
- Role-based permissions
- Consultant access with farmer consent
- Data filtering by access level

### Input Validation Testing
- SQL injection prevention
- XSS protection
- File upload validation
- Agricultural data range validation
- Coordinate validation

## Continuous Integration

### GitHub Actions Workflow
```yaml
name: AFAS Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements-test.txt
      - name: Run tests
        run: python run_tests.py ci
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

### Test Automation
- Automated test execution on code changes
- Coverage reporting and tracking
- Performance regression detection
- Security vulnerability scanning

## Test Reporting

### Coverage Reports
- HTML coverage reports generated
- Minimum 80% coverage required
- Critical agricultural logic requires 95% coverage

### Performance Reports
- Response time tracking
- Memory usage monitoring
- Database query performance
- Concurrent user handling

### Agricultural Validation Reports
- Expert review documentation
- Extension service alignment verification
- Regional testing results
- Confidence score analysis

## Best Practices

### Writing Tests
1. **Clear Test Names**: Describe what is being tested
2. **Agricultural Context**: Include agricultural reasoning in test descriptions
3. **Realistic Data**: Use actual farm scenarios and data
4. **Edge Cases**: Test boundary conditions and error scenarios
5. **Documentation**: Explain agricultural logic and expected outcomes

### Test Maintenance
1. **Regular Updates**: Keep tests current with agricultural research
2. **Expert Review**: Regular validation by agricultural professionals
3. **Performance Monitoring**: Track test execution time and resource usage
4. **Data Refresh**: Update test data with current agricultural practices

### Debugging Failed Tests
1. **Agricultural Logic**: Verify calculations against extension guidelines
2. **Data Quality**: Check input data for completeness and accuracy
3. **Regional Factors**: Consider geographic and climatic variations
4. **Confidence Levels**: Ensure appropriate uncertainty communication

## Troubleshooting

### Common Issues

**Agricultural Test Failures**:
- Verify calculations against extension service publications
- Check for regional variations in recommendations
- Ensure test data represents realistic farm conditions
- Validate confidence scores are appropriate

**Performance Test Failures**:
- Check for resource leaks or inefficient queries
- Verify external API mocks are properly configured
- Monitor system resources during test execution
- Consider test environment limitations

**Security Test Failures**:
- Verify input validation is comprehensive
- Check authentication and authorization logic
- Ensure proper error handling for security violations
- Validate data access controls are enforced

### Getting Help
- Review test documentation and comments
- Check agricultural reference materials
- Consult with agricultural experts for domain questions
- Use verbose test output for debugging

## Future Enhancements

### Planned Improvements
- Automated agricultural accuracy validation
- Machine learning model testing framework
- Real-time performance monitoring
- Enhanced security testing automation
- Regional variation testing expansion

### Research Integration
- Integration with latest agricultural research
- Automated extension service guideline updates
- Climate change adaptation testing
- Precision agriculture technology validation

This comprehensive testing framework ensures that AFAS maintains the highest standards of agricultural accuracy, system reliability, and security while providing farmers with trustworthy recommendations.