# Test Data Directory

This directory contains sample data files for comprehensive testing of the fertilizer timing optimization system.

## Files

### sample_timing_scenarios.json
Contains realistic fertilizer timing scenarios representing different crops, conditions, and challenges:

- **corn_optimal_spring**: Ideal spring conditions for corn sidedress
- **corn_wet_spring**: Challenging wet spring requiring delayed application
- **soybean_establishment**: Pre-plant fertilization for soybeans
- **wheat_topdress**: Spring nitrogen topdress for winter wheat
- **corn_split_application**: High nitrogen requirement with split strategy
- **high_slope_runoff_risk**: Steep field requiring runoff risk management

### weather_patterns.json
Contains weather forecast patterns for testing weather integration:

- **ideal_spring**: Perfect conditions for application
- **wet_period**: Extended wet period with frequent rainfall
- **windy_period**: High wind conditions affecting application methods
- **drought_conditions**: Extended dry period requiring irrigation

## Usage

These data files are used by the comprehensive test suite to:

1. Validate timing algorithm accuracy with real-world scenarios
2. Test weather integration and adjustment logic
3. Verify constraint handling for various field conditions
4. Ensure agricultural validation against agronomic principles
5. Test edge cases and boundary conditions

## Data Structure

### Timing Scenarios
Each scenario includes:
- Field characteristics (soil type, moisture, slope)
- Fertilizer requirements (N, P, K)
- Expected timing recommendations
- Weather conditions
- Operational constraints

### Weather Patterns
Each pattern includes:
- Multi-day forecast data
- Temperature, precipitation, wind, humidity
- Suitability assessment
- Application recommendations

## Adding New Test Data

When adding new test scenarios:
1. Follow the existing JSON structure
2. Include realistic agronomic values
3. Document the scenario purpose
4. Add corresponding test cases in the test suite
5. Validate against expert agronomic guidelines

## Validation

All test data has been designed to align with:
- 4R Nutrient Stewardship principles
- University extension guidelines
- Environmental best practices
- Operational farming constraints
