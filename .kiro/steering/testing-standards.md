# Testing Standards for AFAS

## Overview
This document establishes comprehensive testing standards for the Autonomous Farm Advisory System (AFAS). Testing must ensure agricultural accuracy, system reliability, and farmer safety while maintaining high code quality and performance standards.

## Agricultural Testing Principles

### Agricultural Accuracy First
- **Expert Validation**: All agricultural logic must be validated by certified agricultural professionals
- **Real-World Data**: Use actual farm data and soil test results in testing scenarios
- **Regional Validation**: Test recommendations against known regional best practices
- **Conservative Verification**: Ensure system errs on the side of caution when uncertain
- **Seasonal Context**: Test recommendations across different seasons and growth stages

### Testing Hierarchy
```
1. Agricultural Logic Tests (Highest Priority)
   ├── Nutrient calculation accuracy
   ├── Crop suitability algorithms
   ├── Soil health assessments
   └── Economic optimization models

2. Integration Tests
   ├── End-to-end recommendation workflows
   ├── External API integrations
   ├── Data pipeline validation
   └── Cross-service communication

3. Performance Tests
   ├── Response time requirements
   ├── Concurrent user handling
   ├── Database query optimization
   └── Resource utilization

4. Security Tests
   ├── Authentication and authorization
   ├── Data encryption validation
   ├── Input sanitization
   └── API security testing
```

## Agricultural Logic Testing

### Nutrient Recommendation Testing
```python
import pytest
from decimal import Decimal
from datetime import date
from agricultural.recommendations import NitrogenCalculator, PhosphorusCalculator

class TestNitrogenRecommendations:
    """Test nitrogen recommendation accuracy against extension guidelines."""
    
    @pytest.fixture
    def iowa_corn_scenario(self):
        """Standard Iowa corn production scenario."""
        return {
            'crop': 'corn',
            'yield_goal': 180,  # bu/acre
            'soil_data': {
                'organic_matter_percent': 3.5,
                'nitrate_n_ppm': 12,
                'previous_crop': 'soybean',
                'soil_texture': 'silt_loam',
                'test_date': date(2024, 3, 15)
            },
            'location': {
                'state': 'Iowa',
                'county': 'Story',
                'latitude': 42.0308,
                'longitude': -93.6319
            }
        }
    
    def test_corn_nitrogen_rate_iowa_state_guidelines(self, iowa_corn_scenario):
        """Test N rate calculation matches Iowa State Extension guidelines."""
        calculator = NitrogenCalculator()
        result = calculator.calculate_nitrogen_rate(iowa_corn_scenario)
        
        # Iowa State Extension PM 1688 guidelines
        expected_base_rate = 160  # lbs N/acre for 180 bu goal
        expected_legume_credit = 40  # lbs N/acre from previous soybean
        expected_soil_credit = 24  # lbs N/acre from soil test (12 ppm * 2)
        expected_final_rate = expected_base_rate - expected_legume_credit - expected_soil_credit
        
        # Allow 10 lbs/acre tolerance for calculation variations
        assert abs(result['total_n_rate'] - expected_final_rate) <= 10
        assert result['legume_credit'] == expected_legume_credit
        assert result['soil_test_credit'] == expected_soil_credit
        assert result['confidence_score'] >= 0.85
        
        # Verify agricultural reasoning
        assert 'previous legume credit' in result['reasoning'].lower()
        assert 'soil test credit' in result['reasoning'].lower()
        assert result['source'] == 'Iowa State University Extension PM 1688'
    
    def test_nitrogen_rate_with_manure_application(self):
        """Test N rate calculation includes manure nitrogen credit."""
        scenario = {
            'crop': 'corn',
            'yield_goal': 170,
            'soil_data': {
                'organic_matter_percent': 4.2,
                'nitrate_n_ppm': 8,
                'previous_crop': 'corn'
            },
            'manure_application': {
                'type': 'dairy_manure',
                'rate_tons_per_acre': 20,
                'application_date': date(2024, 3, 15),
                'analysis': {
                    'total_nitrogen_percent': 0.5,
                    'available_nitrogen_percent': 0.25
                }
            }
        }
        
        calculator = NitrogenCalculator()
        result = calculator.calculate_nitrogen_rate(scenario)
        
        # Expected manure N credit: 20 tons * 0.25% available N * 20 lbs/ton = 100 lbs N/acre
        expected_manure_credit = 100
        
        assert result['manure_n_credit'] == expected_manure_credit
        assert 'manure nitrogen credit' in result['reasoning'].lower()
        assert result['total_n_rate'] < 150  # Should be reduced due to manure credit
    
    @pytest.mark.parametrize("soil_ph,expected_warning", [
        (5.2, "acidic soil may limit nitrogen efficiency"),
        (8.5, "alkaline soil may affect nitrogen availability"),
        (6.5, None)  # Optimal pH, no warning expected
    ])
    def test_nitrogen_recommendations_ph_warnings(self, soil_ph, expected_warning):
        """Test that pH warnings are included in nitrogen recommendations."""
        scenario = {
            'crop': 'corn',
            'yield_goal': 160,
            'soil_data': {
                'ph': soil_ph,
                'organic_matter_percent': 3.0,
                'nitrate_n_ppm': 10
            }
        }
        
        calculator = NitrogenCalculator()
        result = calculator.calculate_nitrogen_rate(scenario)
        
        if expected_warning:
            assert expected_warning in result['warnings'][0].lower()
        else:
            assert len(result.get('warnings', [])) == 0

class TestPhosphorusRecommendations:
    """Test phosphorus recommendation logic."""
    
    def test_phosphorus_buildup_recommendation(self):
        """Test P buildup recommendation for low soil test P."""
        scenario = {
            'crop': 'corn',
            'yield_goal': 175,
            'soil_data': {
                'phosphorus_ppm': 8,  # Low P level
                'soil_texture': 'silt_loam',
                'test_method': 'mehlich_3'
            }
        }
        
        calculator = PhosphorusCalculator()
        result = calculator.calculate_phosphorus_rate(scenario)
        
        # Low P should trigger buildup recommendation
        assert result['recommendation_type'] == 'buildup'
        assert result['rate_lbs_p2o5_per_acre'] > 40  # Buildup rate
        assert 'below critical level' in result['reasoning'].lower()
        assert result['confidence_score'] >= 0.8
    
    def test_phosphorus_maintenance_recommendation(self):
        """Test P maintenance recommendation for adequate soil test P."""
        scenario = {
            'crop': 'soybean',
            'yield_goal': 55,
            'soil_data': {
                'phosphorus_ppm': 25,  # Adequate P level
                'soil_texture': 'silt_loam',
                'test_method': 'mehlich_3'
            }
        }
        
        calculator = PhosphorusCalculator()
        result = calculator.calculate_phosphorus_rate(scenario)
        
        # Adequate P should trigger maintenance recommendation
        assert result['recommendation_type'] == 'maintenance'
        assert 20 <= result['rate_lbs_p2o5_per_acre'] <= 35  # Maintenance rate
        assert 'adequate level' in result['reasoning'].lower()

class TestCropSuitabilityAlgorithms:
    """Test crop suitability and selection algorithms."""
    
    def test_corn_suitability_iowa_conditions(self):
        """Test corn suitability for typical Iowa conditions."""
        from agricultural.crop_selection import CropSuitabilityAnalyzer
        
        farm_conditions = {
            'location': {'latitude': 42.0, 'longitude': -93.6},
            'soil': {
                'ph': 6.4,
                'organic_matter_percent': 3.5,
                'drainage_class': 'well_drained',
                'texture': 'silt_loam'
            },
            'climate': {
                'hardiness_zone': '5a',
                'growing_degree_days': 2800,
                'average_rainfall_inches': 34
            },
            'farm_size_acres': 320
        }
        
        analyzer = CropSuitabilityAnalyzer()
        result = analyzer.analyze_crop_suitability('corn', farm_conditions)
        
        # Corn should be highly suitable for Iowa conditions
        assert result['suitability_score'] >= 0.85
        assert result['climate_match'] >= 0.9
        assert result['soil_suitability'] >= 0.8
        assert 'well-suited' in result['explanation'].lower()
    
    def test_crop_selection_ranking(self):
        """Test that crop selection properly ranks multiple crops."""
        from agricultural.crop_selection import CropSelector
        
        farm_conditions = {
            'location': {'latitude': 40.5, 'longitude': -89.4},  # Illinois
            'soil': {
                'ph': 6.2,
                'organic_matter_percent': 3.8,
                'phosphorus_ppm': 25,
                'potassium_ppm': 180
            },
            'preferences': {
                'crop_types': ['grain_crops'],
                'risk_tolerance': 'moderate'
            }
        }
        
        selector = CropSelector()
        recommendations = selector.get_crop_recommendations(farm_conditions)
        
        # Should recommend corn and soybean as top choices for Illinois
        crop_names = [rec['crop_name'] for rec in recommendations[:3]]
        assert 'corn' in crop_names
        assert 'soybean' in crop_names
        
        # Recommendations should be sorted by suitability score
        scores = [rec['suitability_score'] for rec in recommendations]
        assert scores == sorted(scores, reverse=True)
        
        # Each recommendation should have required fields
        for rec in recommendations:
            assert 'explanation' in rec
            assert 'confidence_factors' in rec
            assert rec['suitability_score'] >= 0.0
```

### Soil Health Assessment Testing
```python
class TestSoilHealthAssessment:
    """Test soil health assessment algorithms."""
    
    def test_soil_health_score_calculation(self):
        """Test soil health score calculation accuracy."""
        from agricultural.soil_health import SoilHealthAnalyzer
        
        soil_data = {
            'ph': 6.5,
            'organic_matter_percent': 3.2,
            'bulk_density': 1.3,
            'aggregate_stability': 85,
            'biological_activity': 'high',
            'nutrient_levels': {
                'phosphorus_ppm': 22,
                'potassium_ppm': 165
            }
        }
        
        analyzer = SoilHealthAnalyzer()
        result = analyzer.calculate_soil_health_score(soil_data)
        
        # Good soil conditions should score 7-8 out of 10
        assert 7.0 <= result['overall_score'] <= 8.5
        assert result['ph_score'] >= 8.0  # Optimal pH
        assert result['organic_matter_score'] >= 7.0  # Good OM level
        assert len(result['improvement_recommendations']) <= 2  # Few improvements needed
    
    def test_soil_health_improvement_recommendations(self):
        """Test soil health improvement recommendations."""
        from agricultural.soil_health import SoilHealthAnalyzer
        
        poor_soil_data = {
            'ph': 5.2,  # Too acidic
            'organic_matter_percent': 1.8,  # Too low
            'bulk_density': 1.6,  # Compacted
            'nutrient_levels': {
                'phosphorus_ppm': 8,  # Low
                'potassium_ppm': 85   # Low
            }
        }
        
        analyzer = SoilHealthAnalyzer()
        result = analyzer.calculate_soil_health_score(poor_soil_data)
        
        # Poor soil should have low score and multiple recommendations
        assert result['overall_score'] <= 5.0
        assert len(result['improvement_recommendations']) >= 3
        
        # Should recommend lime for pH
        lime_rec = next((rec for rec in result['improvement_recommendations'] 
                        if rec['practice'] == 'lime_application'), None)
        assert lime_rec is not None
        assert lime_rec['priority'] == 'high'
```

## Integration Testing

### End-to-End Workflow Testing
```python
@pytest.mark.integration
class TestRecommendationWorkflows:
    """Test complete recommendation workflows."""
    
    async def test_complete_crop_selection_workflow(self, test_client):
        """Test end-to-end crop selection process."""
        # Step 1: Create farm profile
        farm_data = {
            'farmer_name': 'Test Farmer',
            'location': {
                'latitude': 42.0308,
                'longitude': -93.6319,
                'address': 'Ames, Iowa'
            },
            'farm_size_acres': 320,
            'primary_crops': ['corn', 'soybean']
        }
        
        farm_response = await test_client.post('/api/v1/farms', json=farm_data)
        assert farm_response.status_code == 201
        farm_id = farm_response.json()['farm_id']
        
        # Step 2: Submit soil test
        soil_test_data = {
            'farm_id': farm_id,
            'field_name': 'North Field',
            'test_results': {
                'ph': 6.2,
                'organic_matter_percent': 3.8,
                'phosphorus_ppm': 25,
                'potassium_ppm': 180,
                'test_date': '2024-03-15'
            }
        }
        
        soil_response = await test_client.post('/api/v1/soil-tests', json=soil_test_data)
        assert soil_response.status_code == 201
        
        # Step 3: Request crop recommendations
        recommendation_request = {
            'farm_id': farm_id,
            'question_type': 'crop_selection',
            'additional_data': {
                'climate_preferences': {
                    'drought_tolerance': 'medium',
                    'season_length': 'full_season'
                }
            }
        }
        
        rec_response = await test_client.post('/api/v1/recommendations/generate', 
                                            json=recommendation_request)
        assert rec_response.status_code == 200
        
        # Validate recommendation quality
        recommendations = rec_response.json()
        assert recommendations['confidence_score'] >= 0.8
        assert len(recommendations['recommendations']) >= 2
        
        # Should recommend corn and soybean for Iowa
        crop_names = [rec['crop_name'] for rec in recommendations['recommendations']]
        assert 'corn' in crop_names
        assert 'soybean' in crop_names
        
        # Each recommendation should have agricultural reasoning
        for rec in recommendations['recommendations']:
            assert len(rec['explanation']) > 50
            assert 'soil' in rec['explanation'].lower()
            assert rec['confidence_factors']['soil_suitability'] > 0.7
    
    async def test_fertilizer_recommendation_workflow(self, test_client):
        """Test fertilizer recommendation workflow with economic optimization."""
        # Setup farm with soil test data
        farm_setup = await self._setup_test_farm(test_client)
        farm_id = farm_setup['farm_id']
        
        # Request fertilizer strategy
        fertilizer_request = {
            'farm_id': farm_id,
            'crop_plan': {
                'primary_crop': 'corn',
                'yield_goal': 180,
                'planted_acres': 250
            },
            'economic_constraints': {
                'fertilizer_budget': 18000.00,
                'current_prices': {
                    'urea_per_ton': 420.00,
                    'dap_per_ton': 580.00,
                    'potash_per_ton': 380.00
                }
            }
        }
        
        response = await test_client.post('/api/v1/recommendations/fertilizer-strategy',
                                        json=fertilizer_request)
        
        assert response.status_code == 200
        strategy = response.json()
        
        # Validate economic optimization
        assert strategy['economic_analysis']['expected_roi_percent'] > 200
        assert strategy['fertilizer_strategy']['total_cost'] <= fertilizer_request['economic_constraints']['fertilizer_budget']
        
        # Validate agricultural accuracy
        n_program = strategy['fertilizer_strategy']['nitrogen_program']
        assert 120 <= n_program['total_n_rate_lbs_per_acre'] <= 180  # Reasonable N rate
        assert n_program['legume_credit_lbs_per_acre'] > 0  # Should account for previous soybean
```

### External API Integration Testing
```python
@pytest.mark.integration
class TestExternalAPIIntegrations:
    """Test integration with external agricultural data sources."""
    
    async def test_weather_api_integration(self):
        """Test weather API integration and fallback mechanisms."""
        from services.data_integration.weather_service import WeatherService
        
        weather_service = WeatherService()
        
        # Test primary API
        location = {'latitude': 42.0308, 'longitude': -93.6319}
        weather_data = await weather_service.get_current_weather(location)
        
        assert weather_data is not None
        assert 'temperature' in weather_data
        assert 'precipitation' in weather_data
        assert 'humidity' in weather_data
        
        # Test forecast data
        forecast = await weather_service.get_forecast(location, days=7)
        assert len(forecast) == 7
        assert all('date' in day and 'temperature' in day for day in forecast)
    
    async def test_soil_database_integration(self):
        """Test soil database integration."""
        from services.data_integration.soil_service import SoilDataService
        
        soil_service = SoilDataService()
        
        # Test soil survey data retrieval
        location = {'latitude': 42.0308, 'longitude': -93.6319}
        soil_info = await soil_service.get_soil_survey_data(location)
        
        assert soil_info is not None
        assert 'soil_series' in soil_info
        assert 'drainage_class' in soil_info
        assert 'typical_ph_range' in soil_info
        
        # Validate data quality
        assert 3.0 <= soil_info['typical_ph_range']['min'] <= 10.0
        assert 3.0 <= soil_info['typical_ph_range']['max'] <= 10.0
    
    @pytest.mark.slow
    async def test_crop_database_integration(self):
        """Test crop variety database integration."""
        from services.data_integration.crop_service import CropDataService
        
        crop_service = CropDataService()
        
        # Test crop variety lookup
        varieties = await crop_service.get_crop_varieties('corn', region='midwest')
        
        assert len(varieties) > 0
        for variety in varieties[:5]:  # Check first 5 varieties
            assert 'variety_name' in variety
            assert 'maturity_days' in variety
            assert 'yield_potential' in variety
            assert variety['maturity_days'] > 0
            assert variety['yield_potential'] > 0
```

## Performance Testing

### Response Time Testing
```python
@pytest.mark.performance
class TestPerformanceRequirements:
    """Test system performance requirements."""
    
    def test_recommendation_response_time(self, test_client):
        """Test that recommendations return within 3 seconds."""
        import time
        
        request_data = {
            'farm_id': 'test_farm',
            'location': {'latitude': 42.0, 'longitude': -93.6},
            'soil_data': {
                'ph': 6.2,
                'organic_matter_percent': 3.5,
                'phosphorus_ppm': 25,
                'potassium_ppm': 180
            }
        }
        
        start_time = time.time()
        response = test_client.post('/api/v1/recommendations/crop-selection',
                                  json=request_data)
        response_time = time.time() - start_time
        
        assert response.status_code == 200
        assert response_time < 3.0  # Must respond within 3 seconds
        
        # Validate response quality wasn't sacrificed for speed
        data = response.json()
        assert data['confidence_score'] >= 0.7
        assert len(data['recommendations']) > 0
    
    @pytest.mark.load
    def test_concurrent_recommendation_requests(self):
        """Test system handles concurrent users."""
        import asyncio
        import aiohttp
        
        async def make_request(session, request_id):
            """Make a single recommendation request."""
            request_data = {
                'farm_id': f'test_farm_{request_id}',
                'location': {'latitude': 42.0, 'longitude': -93.6},
                'soil_data': {'ph': 6.2, 'organic_matter_percent': 3.5}
            }
            
            async with session.post('/api/v1/recommendations/crop-selection',
                                  json=request_data) as response:
                return await response.json(), response.status
        
        async def run_concurrent_test():
            """Run 100 concurrent requests."""
            async with aiohttp.ClientSession() as session:
                tasks = [make_request(session, i) for i in range(100)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # All requests should succeed
                successful_requests = [r for r in results if not isinstance(r, Exception)]
                assert len(successful_requests) >= 95  # Allow 5% failure rate
                
                # Response quality should remain high under load
                for data, status in successful_requests:
                    if status == 200:
                        assert data['confidence_score'] >= 0.7
        
        asyncio.run(run_concurrent_test())
```

### Database Performance Testing
```python
@pytest.mark.performance
class TestDatabasePerformance:
    """Test database query performance."""
    
    def test_soil_test_query_performance(self, db_session):
        """Test soil test queries perform within acceptable limits."""
        import time
        
        # Create test data
        self._create_test_soil_data(db_session, num_records=10000)
        
        # Test query performance
        start_time = time.time()
        results = db_session.query(SoilTest).filter(
            SoilTest.ph.between(6.0, 7.0),
            SoilTest.organic_matter > 3.0
        ).limit(100).all()
        query_time = time.time() - start_time
        
        assert query_time < 0.5  # Query should complete in <500ms
        assert len(results) > 0
    
    def test_recommendation_history_query_performance(self, db_session):
        """Test recommendation history queries."""
        # Test with large dataset
        self._create_test_recommendations(db_session, num_records=50000)
        
        start_time = time.time()
        recent_recommendations = db_session.query(Recommendation).filter(
            Recommendation.created_at >= datetime.now() - timedelta(days=30)
        ).order_by(Recommendation.created_at.desc()).limit(50).all()
        query_time = time.time() - start_time
        
        assert query_time < 1.0  # Complex query should complete in <1s
        assert len(recent_recommendations) > 0
```

## Security Testing

### Authentication and Authorization Testing
```python
@pytest.mark.security
class TestSecurityRequirements:
    """Test security requirements."""
    
    def test_unauthenticated_access_denied(self, test_client):
        """Test that unauthenticated requests are denied."""
        response = test_client.get('/api/v1/farms/123/recommendations')
        assert response.status_code == 401
        
        response = test_client.post('/api/v1/recommendations/crop-selection',
                                  json={'farm_id': '123'})
        assert response.status_code == 401
    
    def test_farm_access_authorization(self, test_client, authenticated_user):
        """Test that users can only access their own farms."""
        # Create farm for user A
        farm_a = test_client.post('/api/v1/farms', 
                                json={'farmer_name': 'User A'},
                                headers=authenticated_user['headers'])
        farm_a_id = farm_a.json()['farm_id']
        
        # Try to access farm A with user B credentials
        user_b_headers = self._get_user_b_headers()
        response = test_client.get(f'/api/v1/farms/{farm_a_id}',
                                 headers=user_b_headers)
        assert response.status_code == 403
    
    def test_sensitive_data_encryption(self, db_session):
        """Test that sensitive farm data is encrypted."""
        from models.farm import Farm
        
        # Create farm with sensitive data
        farm = Farm(
            farmer_name='Test Farmer',
            location={'latitude': 42.0308, 'longitude': -93.6319},
            financial_data={'annual_revenue': 250000}
        )
        db_session.add(farm)
        db_session.commit()
        
        # Check that sensitive fields are encrypted in database
        raw_data = db_session.execute(
            "SELECT location, financial_data FROM farms WHERE id = :id",
            {'id': farm.id}
        ).fetchone()
        
        # Encrypted fields should not contain readable data
        assert 'latitude' not in str(raw_data.location)
        assert 'annual_revenue' not in str(raw_data.financial_data)
```

### Input Validation Testing
```python
@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization."""
    
    def test_sql_injection_prevention(self, test_client):
        """Test SQL injection prevention."""
        malicious_input = {
            'farm_id': "'; DROP TABLE farms; --",
            'location': {'latitude': 42.0, 'longitude': -93.6},
            'soil_data': {'ph': 6.2}
        }
        
        response = test_client.post('/api/v1/recommendations/crop-selection',
                                  json=malicious_input)
        
        # Should return validation error, not execute SQL
        assert response.status_code == 422
        assert 'invalid' in response.json()['error']['error_message'].lower()
    
    def test_agricultural_data_validation(self, test_client):
        """Test agricultural data validation."""
        invalid_soil_data = {
            'farm_id': 'test_farm',
            'soil_data': {
                'ph': 15.0,  # Invalid pH
                'organic_matter_percent': -5.0,  # Invalid negative value
                'phosphorus_ppm': 'not_a_number'  # Invalid type
            }
        }
        
        response = test_client.post('/api/v1/recommendations/crop-selection',
                                  json=invalid_soil_data)
        
        assert response.status_code == 422
        error_details = response.json()['error']
        assert 'ph' in error_details['agricultural_context'].lower()
        assert 'outside reasonable range' in error_details['error_message']
```

## Test Data Management

### Agricultural Test Data Sets
```python
class AgriculturalTestDataFactory:
    """Factory for creating realistic agricultural test data."""
    
    @staticmethod
    def create_iowa_corn_farm():
        """Create typical Iowa corn/soybean farm data."""
        return {
            'location': {
                'latitude': 42.0308,
                'longitude': -93.6319,
                'state': 'Iowa',
                'county': 'Story'
            },
            'soil_data': {
                'ph': 6.4,
                'organic_matter_percent': 3.5,
                'phosphorus_ppm': 28,
                'potassium_ppm': 165,
                'soil_texture': 'silt_loam',
                'drainage_class': 'well_drained',
                'test_date': '2024-03-15'
            },
            'farm_characteristics': {
                'size_acres': 320,
                'primary_crops': ['corn', 'soybean'],
                'equipment': ['planter', 'combine', 'sprayer'],
                'irrigation': False
            },
            'management_history': {
                'tillage_system': 'no_till',
                'cover_crops': True,
                'rotation': ['corn', 'soybean']
            }
        }
    
    @staticmethod
    def create_california_vegetable_farm():
        """Create California vegetable farm data."""
        return {
            'location': {
                'latitude': 36.7783,
                'longitude': -119.4179,
                'state': 'California',
                'county': 'Fresno'
            },
            'soil_data': {
                'ph': 7.2,
                'organic_matter_percent': 2.8,
                'phosphorus_ppm': 45,
                'potassium_ppm': 220,
                'soil_texture': 'sandy_loam',
                'drainage_class': 'well_drained'
            },
            'farm_characteristics': {
                'size_acres': 80,
                'primary_crops': ['tomatoes', 'lettuce', 'broccoli'],
                'irrigation': True,
                'irrigation_type': 'drip'
            }
        }
    
    @staticmethod
    def create_problematic_soil_scenario():
        """Create challenging soil conditions for testing edge cases."""
        return {
            'soil_data': {
                'ph': 5.1,  # Very acidic
                'organic_matter_percent': 1.2,  # Very low
                'phosphorus_ppm': 4,  # Deficient
                'potassium_ppm': 65,  # Low
                'bulk_density': 1.7,  # Compacted
                'drainage_class': 'poorly_drained'
            },
            'field_observations': {
                'compaction_issues': True,
                'erosion_signs': 'severe',
                'standing_water': True
            }
        }
```

## Continuous Testing Integration

### Agricultural Validation Pipeline
```yaml
# .github/workflows/agricultural-validation.yml
name: Agricultural Validation Pipeline

on:
  pull_request:
    paths:
      - 'services/recommendation-engine/**'
      - 'services/agricultural/**'
      - 'tests/agricultural/**'

jobs:
  agricultural-accuracy-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt
      
      - name: Run Agricultural Logic Tests
        run: |
          pytest tests/agricultural/ -v --cov=agricultural --cov-report=xml
          
      - name: Validate Against Extension Guidelines
        run: |
          python scripts/validate_against_extension_data.py
          
      - name: Check Agricultural References
        run: |
          python scripts/check_agricultural_sources.py
          
      - name: Expert Review Required
        if: contains(github.event.pull_request.changed_files, 'agricultural/')
        run: |
          echo "Agricultural logic changes detected. Expert review required."
          # Add label for expert review
          gh pr edit ${{ github.event.number }} --add-label "needs-agricultural-expert-review"
```

### Test Reporting and Metrics
```python
# Custom pytest plugin for agricultural testing metrics
import pytest
from datetime import datetime

class AgriculturalTestReporter:
    """Custom test reporter for agricultural accuracy metrics."""
    
    def __init__(self):
        self.agricultural_tests = []
        self.accuracy_scores = []
        self.expert_validations = []
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """Collect agricultural test results."""
        outcome = yield
        report = outcome.get_result()
        
        if hasattr(item, 'function') and hasattr(item.function, 'agricultural_test'):
            self.agricultural_tests.append({
                'test_name': item.name,
                'status': report.outcome,
                'duration': report.duration,
                'accuracy_score': getattr(report, 'accuracy_score', None),
                'expert_validated': getattr(report, 'expert_validated', False)
            })
    
    def generate_agricultural_report(self):
        """Generate agricultural testing summary report."""
        total_tests = len(self.agricultural_tests)
        passed_tests = len([t for t in self.agricultural_tests if t['status'] == 'passed'])
        expert_validated = len([t for t in self.agricultural_tests if t['expert_validated']])
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_agricultural_tests': total_tests,
            'passed_tests': passed_tests,
            'pass_rate': passed_tests / total_tests if total_tests > 0 else 0,
            'expert_validated_tests': expert_validated,
            'expert_validation_rate': expert_validated / total_tests if total_tests > 0 else 0,
            'average_accuracy_score': sum(self.accuracy_scores) / len(self.accuracy_scores) if self.accuracy_scores else 0
        }
        
        return report
```

This comprehensive testing framework ensures that the AFAS system maintains the highest standards of agricultural accuracy while meeting all technical requirements for reliability, performance, and security.