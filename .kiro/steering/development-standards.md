# Development Standards for AFAS

## Overview
This document establishes development standards, coding conventions, and best practices for the Autonomous Farm Advisory System (AFAS). All team members must follow these guidelines to ensure code quality, maintainability, and agricultural accuracy.

## Code Quality Standards

### General Principles
- **Agricultural Accuracy First** - All code affecting recommendations must be validated by agricultural experts
- **Conservative Approach** - When uncertain about agricultural logic, err on the side of caution
- **Explainable Decisions** - All recommendation logic must be traceable and explainable
- **Data-Driven** - Base recommendations on actual data, not assumptions
- **Regional Awareness** - Consider geographic and climatic variations in all logic
- **Python-First Development** - All services use Python/FastAPI for consistency and agricultural library access

### Code Organization
```
services/
├── question-router/           # Python/FastAPI - Routes questions to appropriate handlers
├── recommendation-engine/     # Python/FastAPI - Core agricultural logic
├── ai-agent/                 # Python/FastAPI - Natural language processing
├── data-integration/         # Python/FastAPI - External data source management
├── image-analysis/           # Python/FastAPI - Computer vision for crop analysis
├── user-management/          # Python/FastAPI - User profiles and authentication
├── frontend/                 # Python (FastAPI+Jinja2 or Streamlit) - Web interface
└── shared/
    ├── models/               # Shared Pydantic data models
    ├── utils/                # Common Python utilities
    ├── agricultural/         # Agricultural calculation libraries (NumPy/SciPy)
    └── validation/           # Data validation utilities (Pydantic)
```

### Naming Conventions

#### Agricultural Domain Naming
```python
# Use standard agricultural terminology
soil_ph_level = 6.5  # Not acidity_level
nitrogen_rate_lbs_per_acre = 120  # Be explicit about units
crop_growth_stage = "V6"  # Use standard growth stage notation
nutrient_sufficiency_range = (20, 40)  # ppm for soil test values

# Function names should reflect agricultural concepts
def calculate_lime_requirement(current_ph, target_ph, soil_type):
    """Calculate lime needed to adjust soil pH"""
    pass

def determine_nitrogen_split_application(total_n_rate, crop_type, growth_stages):
    """Determine optimal nitrogen application timing and rates"""
    pass
```

#### General Naming
```python
# Classes: PascalCase
class SoilTestAnalyzer:
    pass

class CropRecommendationEngine:
    pass

# Functions and variables: snake_case
def analyze_nutrient_deficiency(soil_test_data):
    pass

recommendation_confidence_score = 0.85

# Constants: UPPER_SNAKE_CASE
OPTIMAL_SOIL_PH_RANGE = (6.0, 7.0)
MAX_NITROGEN_RATE_CORN = 200  # lbs/acre
```

### Documentation Standards

#### Agricultural Logic Documentation
```python
def calculate_fertilizer_rate(soil_test_p, crop_type, yield_goal):
    """
    Calculate phosphorus fertilizer rate based on soil test and crop needs.
    
    Agricultural Basis:
    - Uses Mehlich-3 soil test interpretation
    - Based on sufficiency approach for P recommendations
    - Considers crop removal rates and soil buildup/maintenance
    
    Args:
        soil_test_p (float): Soil test P in ppm (Mehlich-3 extraction)
        crop_type (str): Crop type ('corn', 'soybean', 'wheat')
        yield_goal (float): Target yield in bu/acre
        
    Returns:
        dict: {
            'rate_lbs_p2o5_per_acre': float,
            'confidence': float,
            'reasoning': str,
            'source': str  # Reference to extension guidelines
        }
        
    Agricultural References:
    - Iowa State University Extension PM 1688
    - Tri-State Fertilizer Recommendations (Ohio, Indiana, Michigan)
    
    Validation:
    - Reviewed by Dr. Jane Smith, Soil Fertility Specialist, 2024-01-15
    """
    pass
```

#### API Documentation
```python
@app.post("/api/v1/recommendations/crop-selection")
async def get_crop_recommendations(request: CropSelectionRequest):
    """
    Get crop variety recommendations based on soil and climate data.
    
    This endpoint implements Question 1 of the AFAS system:
    "What crop varieties are best suited to my soil type and climate?"
    
    Agricultural Logic:
    - Matches crop requirements to soil pH, drainage, and fertility
    - Considers climate zone, frost dates, and precipitation
    - Ranks varieties by suitability score and yield potential
    
    Request Body:
        location: GPS coordinates or address
        soil_data: pH, texture, drainage class, organic matter
        climate_preferences: drought tolerance, season length
        
    Response:
        recommendations: List of suitable crop varieties
        confidence_scores: Reliability of each recommendation
        explanations: Agricultural reasoning for each recommendation
    """
    pass
```

## Testing Standards

### Agricultural Logic Testing
```python
class TestNitrogenRecommendations:
    """Test nitrogen recommendation logic against known standards."""
    
    def test_corn_nitrogen_rate_calculation(self):
        """Test N rate calculation for corn matches extension guidelines."""
        # Test data from Iowa State Extension
        soil_data = {
            'organic_matter': 3.5,  # %
            'previous_crop': 'soybean',
            'soil_test_n': 12,  # ppm nitrate
            'yield_goal': 180  # bu/acre
        }
        
        result = calculate_nitrogen_rate('corn', soil_data)
        
        # Should match ISU recommendations within 10 lbs/acre
        expected_rate = 140  # lbs N/acre from ISU guidelines
        assert abs(result['rate_lbs_n_per_acre'] - expected_rate) <= 10
        assert result['confidence'] >= 0.8
        assert 'previous legume credit' in result['reasoning'].lower()
    
    def test_nitrogen_rate_with_manure_credit(self):
        """Test N rate calculation includes manure nitrogen credit."""
        soil_data = {
            'organic_matter': 4.2,
            'manure_application': {
                'type': 'dairy_manure',
                'rate_tons_per_acre': 20,
                'application_date': '2024-03-15'
            }
        }
        
        result = calculate_nitrogen_rate('corn', soil_data)
        
        # Should reduce N recommendation due to manure credit
        assert result['manure_n_credit'] > 0
        assert 'manure nitrogen credit' in result['reasoning'].lower()
```

### Integration Testing
```python
class TestCropRecommendationWorkflow:
    """Test complete crop recommendation workflow."""
    
    @pytest.mark.integration
    async def test_complete_crop_selection_workflow(self):
        """Test end-to-end crop selection process."""
        # Simulate farmer input
        farmer_data = {
            'location': {'lat': 42.0308, 'lon': -93.6319},  # Ames, Iowa
            'soil_test': {
                'ph': 6.2,
                'organic_matter': 3.8,
                'phosphorus_ppm': 25,
                'potassium_ppm': 180
            },
            'farm_size': 320,  # acres
            'equipment': ['planter', 'combine', 'sprayer']
        }
        
        # Process through system
        response = await client.post("/api/v1/recommendations/crop-selection", 
                                   json=farmer_data)
        
        # Validate response
        assert response.status_code == 200
        recommendations = response.json()['recommendations']
        
        # Should recommend corn and soybean for Iowa conditions
        crop_names = [rec['crop_name'] for rec in recommendations]
        assert 'corn' in crop_names
        assert 'soybean' in crop_names
        
        # Each recommendation should have agricultural reasoning
        for rec in recommendations:
            assert rec['confidence_score'] > 0.7
            assert len(rec['explanation']) > 50
            assert 'soil pH' in rec['explanation'].lower()
```

### Performance Testing
```python
class TestPerformanceRequirements:
    """Ensure system meets performance requirements."""
    
    @pytest.mark.performance
    def test_recommendation_response_time(self):
        """Recommendations must return within 3 seconds."""
        start_time = time.time()
        
        response = client.post("/api/v1/recommendations/fertilizer-rate", 
                             json=sample_farm_data)
        
        response_time = time.time() - start_time
        assert response_time < 3.0
        assert response.status_code == 200
    
    @pytest.mark.load
    def test_concurrent_user_handling(self):
        """System must handle 1000+ concurrent users."""
        # Load testing with locust or similar tool
        pass
```

## Error Handling Standards

### Agricultural Data Validation
```python
class SoilTestValidator:
    """Validate soil test data for agricultural reasonableness."""
    
    @staticmethod
    def validate_soil_ph(ph_value):
        """Validate soil pH is within reasonable range."""
        if not isinstance(ph_value, (int, float)):
            raise ValidationError("Soil pH must be numeric")
        
        if ph_value < 3.0 or ph_value > 10.0:
            raise ValidationError(
                f"Soil pH {ph_value} is outside reasonable range (3.0-10.0). "
                "Please verify soil test results."
            )
        
        if ph_value < 4.5:
            warnings.warn(
                f"Extremely acidic soil (pH {ph_value}). "
                "Consider lime application and retest."
            )
        
        return True
    
    @staticmethod
    def validate_nutrient_levels(nutrient_data):
        """Validate nutrient levels are reasonable."""
        ranges = {
            'phosphorus_ppm': (0, 200),
            'potassium_ppm': (0, 800),
            'organic_matter_percent': (0, 15)
        }
        
        for nutrient, (min_val, max_val) in ranges.items():
            if nutrient in nutrient_data:
                value = nutrient_data[nutrient]
                if not min_val <= value <= max_val:
                    raise ValidationError(
                        f"{nutrient} value {value} is outside typical range "
                        f"({min_val}-{max_val}). Please verify test results."
                    )
```

### Graceful Degradation
```python
async def get_weather_data(location):
    """Get weather data with fallback options."""
    try:
        # Primary weather service
        return await primary_weather_api.get_data(location)
    except WeatherAPIError:
        try:
            # Fallback to secondary service
            return await secondary_weather_api.get_data(location)
        except WeatherAPIError:
            # Use historical averages as last resort
            logger.warning(f"Weather APIs unavailable for {location}, using historical data")
            return get_historical_weather_averages(location)
```

## Security Standards

### Data Protection
```python
# Encrypt sensitive farm data
@encrypt_field
class FarmProfile(BaseModel):
    farmer_name: str
    location: EncryptedField[Location]  # GPS coordinates
    soil_test_results: EncryptedField[Dict]  # Sensitive farm data
    financial_data: EncryptedField[Dict]  # Cost and revenue data
    
    # Non-sensitive data can remain unencrypted
    farm_size_acres: float
    primary_crops: List[str]
```

### API Security
```python
@require_authentication
@rate_limit(requests_per_minute=60)
async def get_recommendations(request: RecommendationRequest, 
                            current_user: User = Depends(get_current_user)):
    """Secure endpoint for getting recommendations."""
    
    # Validate user has access to this farm
    if not user_has_farm_access(current_user, request.farm_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Log access for audit trail
    audit_logger.info(f"User {current_user.id} requested recommendations for farm {request.farm_id}")
    
    return await generate_recommendations(request)
```

## Logging and Monitoring

### Agricultural Decision Logging
```python
import structlog

agri_logger = structlog.get_logger("agricultural_decisions")

def log_recommendation_decision(recommendation_type, input_data, output_data, confidence):
    """Log agricultural recommendation decisions for audit and improvement."""
    agri_logger.info(
        "recommendation_generated",
        recommendation_type=recommendation_type,
        input_summary={
            'soil_ph': input_data.get('soil_ph'),
            'crop_type': input_data.get('crop_type'),
            'location_zone': input_data.get('climate_zone')
        },
        output_summary={
            'primary_recommendation': output_data.get('primary_recommendation'),
            'confidence_score': confidence,
            'reasoning_category': output_data.get('reasoning_category')
        },
        timestamp=datetime.utcnow().isoformat()
    )
```

### Performance Monitoring
```python
from prometheus_client import Counter, Histogram, Gauge

# Agricultural-specific metrics
recommendation_requests = Counter('afas_recommendations_total', 
                                'Total recommendation requests', 
                                ['question_type', 'region'])

recommendation_confidence = Histogram('afas_recommendation_confidence',
                                    'Confidence scores of recommendations',
                                    ['question_type'])

active_farms = Gauge('afas_active_farms', 'Number of active farm profiles')

# Usage in code
@monitor_agricultural_performance
async def generate_crop_recommendation(farm_data):
    recommendation_requests.labels(
        question_type='crop_selection',
        region=farm_data.get('region', 'unknown')
    ).inc()
    
    result = await process_recommendation(farm_data)
    
    recommendation_confidence.labels(
        question_type='crop_selection'
    ).observe(result.confidence_score)
    
    return result
```

## Code Review Checklist

### Agricultural Accuracy Review
- [ ] **Expert Validation**: Has an agricultural expert reviewed the logic?
- [ ] **Reference Documentation**: Are agricultural sources cited and current?
- [ ] **Regional Applicability**: Does the logic work across different regions?
- [ ] **Units Consistency**: Are all units clearly specified and consistent?
- [ ] **Safety Considerations**: Are safety warnings included where appropriate?

### Technical Review
- [ ] **Code Quality**: Follows naming conventions and documentation standards
- [ ] **Test Coverage**: >80% test coverage with agricultural validation tests
- [ ] **Error Handling**: Graceful handling of invalid or missing data
- [ ] **Performance**: Meets response time requirements (<3 seconds)
- [ ] **Security**: Proper authentication, authorization, and data protection

### User Experience Review
- [ ] **Plain Language**: Explanations use farmer-friendly language
- [ ] **Actionable Advice**: Recommendations are specific and implementable
- [ ] **Confidence Communication**: Uncertainty is appropriately communicated
- [ ] **Mobile Compatibility**: Works well on mobile devices in field conditions

## Deployment Standards

### Environment Configuration
```yaml
# production.yml
environment:
  - AGRICULTURAL_EXPERT_VALIDATION=required
  - RECOMMENDATION_CONFIDENCE_THRESHOLD=0.8
  - ENABLE_CONSERVATIVE_MODE=true
  - SOIL_TEST_MAX_AGE_YEARS=3
  - WEATHER_DATA_FALLBACK_ENABLED=true

# staging.yml  
environment:
  - AGRICULTURAL_EXPERT_VALIDATION=optional
  - RECOMMENDATION_CONFIDENCE_THRESHOLD=0.7
  - ENABLE_CONSERVATIVE_MODE=true
  - MOCK_EXTERNAL_APIS=true
```

### Database Migration Standards
```python
# migrations must preserve agricultural data integrity
def upgrade():
    """Add new nutrient recommendation table."""
    # Always backup before schema changes affecting agricultural data
    op.execute("CREATE BACKUP OF agricultural_recommendations")
    
    op.create_table('nutrient_recommendations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('farm_id', sa.Integer, sa.ForeignKey('farms.id')),
        sa.Column('nutrient_type', sa.String(50), nullable=False),
        sa.Column('recommended_rate', sa.Float, nullable=False),
        sa.Column('rate_units', sa.String(20), nullable=False),  # Always specify units
        sa.Column('confidence_score', sa.Float, nullable=False),
        sa.Column('agricultural_source', sa.String(200)),  # Track recommendation source
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow)
    )
    
    # Validate data integrity after migration
    op.execute("SELECT validate_agricultural_data()")
```

## Continuous Integration Requirements

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: agricultural-validation
        name: Validate Agricultural Logic
        entry: python scripts/validate_agricultural_logic.py
        language: python
        files: ^(.*agricultural.*|.*recommendation.*)\.py$
        
      - id: unit-conversion-check
        name: Check Unit Consistency
        entry: python scripts/check_units.py
        language: python
        files: \.py$
```

### CI Pipeline
```yaml
# .github/workflows/ci.yml
name: AFAS CI Pipeline

on: [push, pull_request]

jobs:
  agricultural-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Agricultural Expert Validation
        run: |
          python -m pytest tests/agricultural/ -v
          python scripts/validate_recommendations.py
          
  integration-tests:
    runs-on: ubuntu-latest
    steps:
      - name: Test with Real Farm Data
        run: |
          python -m pytest tests/integration/ -v --farm-data-samples=100
```

## Python Technology Stack Standards

### Core Technologies
- **Backend Framework**: FastAPI for all services (consistent async/await patterns)
- **Data Validation**: Pydantic models for all API requests/responses
- **Database ORM**: SQLAlchemy for PostgreSQL, Motor for MongoDB
- **Testing**: pytest with pytest-asyncio for async testing
- **Documentation**: FastAPI automatic OpenAPI generation

### Agricultural Python Libraries
- **Scientific Computing**: NumPy, SciPy, Pandas for data processing
- **Machine Learning**: scikit-learn, TensorFlow/PyTorch for ML models
- **NLP**: spaCy, NLTK for natural language processing
- **Optimization**: OR-Tools for agricultural optimization problems
- **Visualization**: Matplotlib, Plotly for data visualization

### Frontend Options
- **Traditional Web**: FastAPI + Jinja2 templates + Bootstrap
- **Data Dashboard**: Streamlit for rapid agricultural dashboard development
- **API Documentation**: FastAPI automatic Swagger/ReDoc generation

### Development Tools
- **Process Management**: uvicorn with --reload for development
- **Code Quality**: black (formatting), flake8 (linting), mypy (type checking)
- **Dependency Management**: pip with requirements.txt per service
- **Environment Management**: Python venv for service isolation

This development standards document ensures that all code maintains agricultural accuracy while meeting technical excellence standards using a consistent Python technology stack. Regular updates should incorporate new agricultural research and farmer feedback.