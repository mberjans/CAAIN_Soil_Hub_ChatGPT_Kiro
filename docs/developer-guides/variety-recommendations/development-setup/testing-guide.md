# Testing Guide - Crop Variety Recommendations

## Overview

This guide provides comprehensive testing strategies, frameworks, and best practices for the crop variety recommendations system. It covers unit testing, integration testing, performance testing, and agricultural validation testing.

## Testing Philosophy

### 1. Test-Driven Development (TDD)
- Write tests before implementing features
- Red-Green-Refactor cycle
- Tests serve as living documentation
- High confidence in code changes

### 2. Testing Pyramid
```
    ┌─────────────────┐
    │   E2E Tests     │  ← Few, slow, expensive
    │   (10%)         │
    ├─────────────────┤
    │ Integration     │  ← Some, medium speed
    │ Tests (20%)     │
    ├─────────────────┤
    │   Unit Tests    │  ← Many, fast, cheap
    │   (70%)         │
    └─────────────────┘
```

### 3. Agricultural Domain Testing
- Validate agricultural logic with expert knowledge
- Test against real-world farming scenarios
- Ensure recommendations are scientifically sound
- Performance testing for field conditions

## Testing Framework Setup

### 1. Dependencies

```bash
# Install testing dependencies
pip install pytest pytest-asyncio pytest-cov pytest-mock
pip install httpx pytest-httpx
pip install factory-boy faker
pip install pytest-benchmark
pip install pytest-xdist  # For parallel testing
```

### 2. Configuration Files

**pytest.ini:**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    performance: Performance tests
    agricultural: Agricultural validation tests
    slow: Slow running tests
asyncio_mode = auto
```

**conftest.py:**
```python
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database.crop_taxonomy_db import get_db
from src.models.crop_variety_models import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "postgresql://test_user:test_password@localhost:5432/test_variety_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create test client with database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_farm_data():
    """Sample farm data for testing."""
    return {
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "climate_zone": "6a"
        },
        "soil_data": {
            "ph": 6.5,
            "organic_matter_percent": 3.2,
            "drainage": "well_drained",
            "soil_type": "clay_loam"
        },
        "field_size_acres": 100,
        "irrigation_available": True
    }

@pytest.fixture
def sample_user_preferences():
    """Sample user preferences for testing."""
    return {
        "yield_priority": "high",
        "disease_resistance_priority": "medium",
        "maturity_preference": "early",
        "seed_budget": 50000
    }
```

## Unit Testing

### 1. Service Layer Testing

**tests/unit/test_variety_recommendation_service.py:**
```python
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.variety_recommendation_service import VarietyRecommendationService
from src.models.crop_variety_models import VarietyRecommendationRequest

class TestVarietyRecommendationService:
    @pytest.fixture
    def service(self):
        return VarietyRecommendationService()
    
    @pytest.fixture
    def mock_request(self, sample_farm_data, sample_user_preferences):
        return VarietyRecommendationRequest(
            crop_id="corn",
            farm_data=sample_farm_data,
            user_preferences=sample_user_preferences,
            max_recommendations=10
        )
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_recommendations_success(self, service, mock_request):
        """Test successful variety recommendations."""
        # Mock database response
        mock_varieties = [
            {
                "id": "pioneer-1197",
                "name": "Pioneer P1197AM",
                "company": "Pioneer",
                "yield_potential": "185 bu/acre",
                "maturity_days": 105,
                "confidence": 0.92,
                "disease_resistance": "high"
            }
        ]
        
        with patch.object(service.db, 'get_varieties_by_criteria') as mock_get_varieties:
            mock_get_varieties.return_value = mock_varieties
            
            result = await service.get_recommendations(mock_request)
            
            assert len(result) == 1
            assert result[0]["name"] == "Pioneer P1197AM"
            assert result[0]["confidence"] == 0.92
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_get_recommendations_no_results(self, service, mock_request):
        """Test recommendations when no varieties match criteria."""
        with patch.object(service.db, 'get_varieties_by_criteria') as mock_get_varieties:
            mock_get_varieties.return_value = []
            
            result = await service.get_recommendations(mock_request)
            
            assert len(result) == 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_calculate_confidence_score(self, service):
        """Test confidence score calculation."""
        variety_data = {
            "yield_potential": "185 bu/acre",
            "disease_resistance": "high",
            "maturity_days": 105,
            "climate_match": True,
            "soil_match": True
        }
        
        confidence = service.calculate_confidence_score(variety_data)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.8  # Should be high for good match
    
    @pytest.mark.unit
    def test_validate_farm_data(self, service):
        """Test farm data validation."""
        valid_data = {
            "location": {"latitude": 40.7128, "longitude": -74.0060},
            "soil_data": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        assert service.validate_farm_data(valid_data) == True
        
        invalid_data = {
            "location": {"latitude": 200.0, "longitude": -74.0060},  # Invalid latitude
            "soil_data": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        assert service.validate_farm_data(invalid_data) == False
```

### 2. Database Layer Testing

**tests/unit/test_database_operations.py:**
```python
import pytest
from src.database.crop_taxonomy_db import CropTaxonomyDatabase
from src.models.crop_variety_models import CropVarietyDB

class TestCropTaxonomyDatabase:
    @pytest.fixture
    def db(self, db_session):
        return CropTaxonomyDatabase(db_session)
    
    @pytest.mark.unit
    def test_get_varieties_by_crop(self, db):
        """Test retrieving varieties by crop type."""
        # Add test data
        test_variety = CropVarietyDB(
            variety_name="Test Corn Variety",
            crop_id=1,
            company="Test Company",
            maturity_days=105,
            yield_potential_min=180,
            yield_potential_max=200,
            yield_unit="bu/acre"
        )
        db.session.add(test_variety)
        db.session.commit()
        
        # Test retrieval
        varieties = db.get_varieties_by_crop("corn")
        
        assert len(varieties) >= 1
        assert any(v.variety_name == "Test Corn Variety" for v in varieties)
    
    @pytest.mark.unit
    def test_get_varieties_by_criteria(self, db):
        """Test retrieving varieties by multiple criteria."""
        criteria = {
            "crop_id": "corn",
            "maturity_min": 100,
            "maturity_max": 110,
            "yield_min": 180
        }
        
        varieties = db.get_varieties_by_criteria(criteria)
        
        assert isinstance(varieties, list)
        # Verify all returned varieties meet criteria
        for variety in varieties:
            assert 100 <= variety.maturity_days <= 110
            assert variety.yield_potential_min >= 180
```

### 3. Model Testing

**tests/unit/test_models.py:**
```python
import pytest
from pydantic import ValidationError
from src.models.crop_variety_models import (
    VarietyRecommendationRequest,
    FarmData,
    UserPreferences,
    VarietyRecommendation
)

class TestModels:
    @pytest.mark.unit
    def test_variety_recommendation_request_valid(self, sample_farm_data, sample_user_preferences):
        """Test valid variety recommendation request."""
        request = VarietyRecommendationRequest(
            crop_id="corn",
            farm_data=sample_farm_data,
            user_preferences=sample_user_preferences
        )
        
        assert request.crop_id == "corn"
        assert request.farm_data.location.latitude == 40.7128
    
    @pytest.mark.unit
    def test_variety_recommendation_request_invalid_crop(self, sample_farm_data):
        """Test invalid crop ID."""
        with pytest.raises(ValidationError):
            VarietyRecommendationRequest(
                crop_id="invalid_crop",
                farm_data=sample_farm_data
            )
    
    @pytest.mark.unit
    def test_farm_data_validation(self):
        """Test farm data validation."""
        # Valid farm data
        valid_data = {
            "location": {"latitude": 40.7128, "longitude": -74.0060},
            "soil_data": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        farm_data = FarmData(**valid_data)
        assert farm_data.location.latitude == 40.7128
        
        # Invalid latitude
        invalid_data = {
            "location": {"latitude": 200.0, "longitude": -74.0060},
            "soil_data": {"ph": 6.5, "organic_matter_percent": 3.2}
        }
        
        with pytest.raises(ValidationError):
            FarmData(**invalid_data)
```

## Integration Testing

### 1. API Integration Tests

**tests/integration/test_api_endpoints.py:**
```python
import pytest
from httpx import AsyncClient

class TestVarietyAPI:
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_recommendations_endpoint(self, client, sample_farm_data):
        """Test variety recommendations endpoint."""
        response = await client.post(
            "/api/v1/varieties/recommend",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "crop_id": "corn",
                "farm_data": sample_farm_data,
                "max_recommendations": 5
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5
        
        # Verify response structure
        if data:
            recommendation = data[0]
            assert "id" in recommendation
            assert "name" in recommendation
            assert "confidence" in recommendation
            assert 0.0 <= recommendation["confidence"] <= 1.0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_compare_varieties_endpoint(self, client):
        """Test variety comparison endpoint."""
        response = await client.post(
            "/api/v1/varieties/compare",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "variety_ids": ["pioneer-1197", "dekalb-5678"],
                "comparison_criteria": ["yield_potential", "disease_resistance"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "varieties" in data
        assert len(data["varieties"]) == 2
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_filter_varieties_endpoint(self, client):
        """Test variety filtering endpoint."""
        response = await client.post(
            "/api/v1/varieties/filter",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "crop_id": "corn",
                "filters": {
                    "maturity_range": {"min": 100, "max": 115},
                    "yield_potential_min": 180
                }
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "filtered_varieties" in data
        assert isinstance(data["filtered_varieties"], list)
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_authentication_required(self, client, sample_farm_data):
        """Test that authentication is required."""
        response = await client.post(
            "/api/v1/varieties/recommend",
            json={
                "crop_id": "corn",
                "farm_data": sample_farm_data
            }
        )
        
        assert response.status_code == 401
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_invalid_request_data(self, client):
        """Test handling of invalid request data."""
        response = await client.post(
            "/api/v1/varieties/recommend",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "crop_id": "invalid_crop",
                "farm_data": {
                    "location": {"latitude": 200.0, "longitude": -74.0060}
                }
            }
        )
        
        assert response.status_code == 422
```

### 2. Database Integration Tests

**tests/integration/test_database_integration.py:**
```python
import pytest
from src.database.crop_taxonomy_db import CropTaxonomyDatabase

class TestDatabaseIntegration:
    @pytest.mark.integration
    def test_database_connection(self, db_session):
        """Test database connection."""
        db = CropTaxonomyDatabase(db_session)
        assert db.test_connection() == True
    
    @pytest.mark.integration
    def test_variety_crud_operations(self, db_session):
        """Test CRUD operations on varieties."""
        db = CropTaxonomyDatabase(db_session)
        
        # Create
        variety_data = {
            "variety_name": "Test Integration Variety",
            "crop_id": 1,
            "company": "Test Company",
            "maturity_days": 105,
            "yield_potential_min": 180,
            "yield_potential_max": 200,
            "yield_unit": "bu/acre"
        }
        
        variety_id = db.create_variety(variety_data)
        assert variety_id is not None
        
        # Read
        variety = db.get_variety_by_id(variety_id)
        assert variety.variety_name == "Test Integration Variety"
        
        # Update
        updated_data = {"maturity_days": 110}
        db.update_variety(variety_id, updated_data)
        
        updated_variety = db.get_variety_by_id(variety_id)
        assert updated_variety.maturity_days == 110
        
        # Delete
        db.delete_variety(variety_id)
        deleted_variety = db.get_variety_by_id(variety_id)
        assert deleted_variety is None
```

## Performance Testing

### 1. Load Testing

**tests/performance/test_load_performance.py:**
```python
import pytest
import asyncio
import time
from httpx import AsyncClient

class TestLoadPerformance:
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_recommendations(self, client, sample_farm_data):
        """Test system performance under concurrent load."""
        async def make_request():
            response = await client.post(
                "/api/v1/varieties/recommend",
                headers={"Authorization": "Bearer test-api-key"},
                json={
                    "crop_id": "corn",
                    "farm_data": sample_farm_data,
                    "max_recommendations": 10
                }
            )
            return response.status_code == 200
        
        # Test with 50 concurrent requests
        start_time = time.time()
        tasks = [make_request() for _ in range(50)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all requests succeeded
        assert all(results)
        
        # Verify response time is acceptable
        total_time = end_time - start_time
        assert total_time < 10.0  # Should complete within 10 seconds
        
        # Calculate average response time
        avg_response_time = total_time / 50
        assert avg_response_time < 2.0  # Average response time under 2 seconds
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_response_time_requirements(self, client, sample_farm_data):
        """Test that response times meet requirements."""
        start_time = time.time()
        
        response = await client.post(
            "/api/v1/varieties/recommend",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "crop_id": "corn",
                "farm_data": sample_farm_data,
                "max_recommendations": 20
            }
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Response time under 2 seconds
```

### 2. Memory and Resource Testing

**tests/performance/test_resource_usage.py:**
```python
import pytest
import psutil
import os
from src.services.variety_recommendation_service import VarietyRecommendationService

class TestResourceUsage:
    @pytest.mark.performance
    def test_memory_usage(self, sample_farm_data, sample_user_preferences):
        """Test memory usage during recommendations."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        service = VarietyRecommendationService()
        
        # Simulate multiple recommendations
        for _ in range(100):
            # This would be an async call in real implementation
            pass
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024
```

## Agricultural Validation Testing

### 1. Expert Knowledge Validation

**tests/agricultural/test_expert_validation.py:**
```python
import pytest
from src.services.variety_recommendation_service import VarietyRecommendationService

class TestAgriculturalValidation:
    @pytest.fixture
    def service(self):
        return VarietyRecommendationService()
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_corn_belt_recommendations(self, service):
        """Test recommendations for major corn belt region."""
        # Iowa coordinates - major corn belt
        farm_data = {
            "location": {"latitude": 41.5868, "longitude": -93.6250},
            "soil_data": {"ph": 6.2, "organic_matter_percent": 3.5},
            "field_size_acres": 200,
            "irrigation_available": False
        }
        
        request = VarietyRecommendationRequest(
            crop_id="corn",
            farm_data=farm_data,
            max_recommendations=10
        )
        
        recommendations = await service.get_recommendations(request)
        
        # Verify recommendations are appropriate for corn belt
        assert len(recommendations) > 0
        
        for rec in recommendations:
            # Maturity should be appropriate for corn belt (100-120 days)
            assert 100 <= rec.maturity_days <= 120
            
            # Yield potential should be realistic for corn belt
            yield_value = float(rec.yield_potential.split()[0])
            assert 150 <= yield_value <= 250
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_ph_soil_compatibility(self, service):
        """Test that recommendations consider soil pH compatibility."""
        # Test with acidic soil
        acidic_farm_data = {
            "location": {"latitude": 40.7128, "longitude": -74.0060},
            "soil_data": {"ph": 5.2, "organic_matter_percent": 2.8},
            "field_size_acres": 100
        }
        
        request = VarietyRecommendationRequest(
            crop_id="corn",
            farm_data=acidic_farm_data
        )
        
        recommendations = await service.get_recommendations(request)
        
        # Recommendations should consider soil pH
        for rec in recommendations:
            # Should include pH-related traits or recommendations
            assert any("acid" in trait.lower() or "ph" in trait.lower() 
                      for trait in rec.traits)
    
    @pytest.mark.agricultural
    def test_climate_zone_accuracy(self, service):
        """Test climate zone detection accuracy."""
        # Test known coordinates
        test_cases = [
            (40.7128, -74.0060, "6a"),  # New York
            (41.8781, -87.6298, "6a"),  # Chicago
            (33.4484, -112.0740, "9b"), # Phoenix
        ]
        
        for lat, lng, expected_zone in test_cases:
            zone = service.detect_climate_zone(lat, lng)
            assert zone == expected_zone
```

### 2. Real-World Scenario Testing

**tests/agricultural/test_real_world_scenarios.py:**
```python
import pytest

class TestRealWorldScenarios:
    @pytest.mark.agricultural
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_drought_tolerant_varieties(self, client):
        """Test recommendations for drought-prone areas."""
        # Texas Panhandle - known for drought
        farm_data = {
            "location": {"latitude": 35.2220, "longitude": -101.8313},
            "soil_data": {"ph": 7.1, "organic_matter_percent": 1.8},
            "field_size_acres": 500,
            "irrigation_available": False
        }
        
        response = await client.post(
            "/api/v1/varieties/recommend",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "crop_id": "corn",
                "farm_data": farm_data,
                "user_preferences": {
                    "drought_tolerance_priority": "high"
                }
            }
        )
        
        assert response.status_code == 200
        recommendations = response.json()
        
        # Should prioritize drought-tolerant varieties
        for rec in recommendations:
            assert "drought" in rec.traits.lower() or rec.drought_tolerance == "high"
    
    @pytest.mark.agricultural
    @pytest.mark.asyncio
    async def test_organic_farming_compatibility(self, client):
        """Test recommendations for organic farming."""
        farm_data = {
            "location": {"latitude": 44.9778, "longitude": -93.2650},
            "soil_data": {"ph": 6.8, "organic_matter_percent": 4.2},
            "field_size_acres": 80,
            "farming_type": "organic"
        }
        
        response = await client.post(
            "/api/v1/varieties/recommend",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "crop_id": "corn",
                "farm_data": farm_data,
                "user_preferences": {
                    "organic_compatible": True
                }
            }
        )
        
        assert response.status_code == 200
        recommendations = response.json()
        
        # Should recommend organic-compatible varieties
        for rec in recommendations:
            assert rec.organic_compatible == True
```

## End-to-End Testing

### 1. Complete User Workflow Testing

**tests/e2e/test_user_workflows.py:**
```python
import pytest
from httpx import AsyncClient

class TestUserWorkflows:
    @pytest.mark.e2e
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_complete_variety_selection_workflow(self, client):
        """Test complete variety selection workflow."""
        # Step 1: Get initial recommendations
        farm_data = {
            "location": {"latitude": 40.7128, "longitude": -74.0060},
            "soil_data": {"ph": 6.5, "organic_matter_percent": 3.2},
            "field_size_acres": 100
        }
        
        response = await client.post(
            "/api/v1/varieties/recommend",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "crop_id": "corn",
                "farm_data": farm_data,
                "max_recommendations": 10
            }
        )
        
        assert response.status_code == 200
        recommendations = response.json()
        assert len(recommendations) > 0
        
        # Step 2: Compare top varieties
        variety_ids = [rec["id"] for rec in recommendations[:3]]
        
        response = await client.post(
            "/api/v1/varieties/compare",
            headers={"Authorization": "Bearer test-api-key"},
            json={
                "variety_ids": variety_ids,
                "comparison_criteria": ["yield_potential", "disease_resistance", "maturity_days"]
            }
        )
        
        assert response.status_code == 200
        comparison = response.json()
        assert len(comparison["varieties"]) == 3
        
        # Step 3: Get detailed information for selected variety
        selected_variety_id = variety_ids[0]
        
        response = await client.get(
            f"/api/v1/varieties/{selected_variety_id}/details",
            headers={"Authorization": "Bearer test-api-key"}
        )
        
        assert response.status_code == 200
        variety_details = response.json()
        assert variety_details["id"] == selected_variety_id
        assert "characteristics" in variety_details
        assert "disease_resistance" in variety_details
```

## Test Data Management

### 1. Test Data Factories

**tests/factories/variety_factories.py:**
```python
import factory
from factory.fuzzy import FuzzyFloat, FuzzyInteger, FuzzyChoice
from src.models.crop_variety_models import CropVarietyDB

class CropVarietyFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = CropVarietyDB
        sqlalchemy_session_persistence = "commit"
    
    variety_name = factory.Sequence(lambda n: f"Test Variety {n}")
    crop_id = FuzzyInteger(1, 10)
    company = FuzzyChoice(["Pioneer", "DeKalb", "Syngenta", "Bayer"])
    maturity_days = FuzzyInteger(90, 130)
    yield_potential_min = FuzzyFloat(150.0, 200.0)
    yield_potential_max = FuzzyFloat(200.0, 250.0)
    yield_unit = "bu/acre"
    climate_zones = factory.List([FuzzyChoice(["5a", "5b", "6a", "6b", "7a"])])
    soil_ph_min = FuzzyFloat(5.5, 6.0)
    soil_ph_max = FuzzyFloat(7.0, 7.5)
    soil_types = factory.List([FuzzyChoice(["clay_loam", "silt_loam", "sandy_loam"])])

class FarmDataFactory(factory.Factory):
    class Meta:
        model = dict
    
    location = factory.Dict({
        "latitude": FuzzyFloat(35.0, 45.0),
        "longitude": FuzzyFloat(-100.0, -80.0)
    })
    soil_data = factory.Dict({
        "ph": FuzzyFloat(5.5, 7.5),
        "organic_matter_percent": FuzzyFloat(2.0, 5.0)
    })
    field_size_acres = FuzzyFloat(50.0, 500.0)
    irrigation_available = FuzzyChoice([True, False])
```

### 2. Test Data Cleanup

**tests/utils/test_data_cleanup.py:**
```python
import pytest
from sqlalchemy import text

@pytest.fixture(autouse=True)
def cleanup_test_data(db_session):
    """Clean up test data after each test."""
    yield
    
    # Clean up test data
    db_session.execute(text("DELETE FROM variety_recommendations WHERE variety_name LIKE 'Test%'"))
    db_session.execute(text("DELETE FROM crop_varieties WHERE variety_name LIKE 'Test%'"))
    db_session.commit()
```

## Continuous Integration

### 1. GitHub Actions Workflow

**.github/workflows/test.yml:**
```yaml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_variety_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:6
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio pytest-cov
    
    - name: Run unit tests
      run: pytest tests/unit/ -v --cov=src --cov-report=xml
    
    - name: Run integration tests
      run: pytest tests/integration/ -v
    
    - name: Run agricultural validation tests
      run: pytest tests/agricultural/ -v -m agricultural
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Best Practices

### 1. Test Organization
- Group tests by functionality, not by file structure
- Use descriptive test names that explain the scenario
- Keep tests independent and isolated
- Use fixtures for common test data

### 2. Test Data
- Use factories for generating test data
- Avoid hardcoded test data when possible
- Clean up test data after each test
- Use realistic test data that reflects real-world scenarios

### 3. Performance Testing
- Test under realistic load conditions
- Monitor resource usage during tests
- Set appropriate performance thresholds
- Test both individual operations and complete workflows

### 4. Agricultural Validation
- Validate recommendations against expert knowledge
- Test edge cases and boundary conditions
- Include real-world farming scenarios
- Ensure recommendations are scientifically sound

### 5. Maintenance
- Keep tests up to date with code changes
- Remove obsolete tests
- Refactor tests when functionality changes
- Monitor test execution time and optimize slow tests

## Troubleshooting

### Common Test Issues

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql
   
   # Check test database exists
   psql -h localhost -U test_user -d test_variety_db
   ```

2. **Async Test Issues**
   ```python
   # Ensure pytest-asyncio is installed
   pip install pytest-asyncio
   
   # Use proper async test decorators
   @pytest.mark.asyncio
   async def test_async_function():
       pass
   ```

3. **Fixture Scope Issues**
   ```python
   # Use appropriate fixture scopes
   @pytest.fixture(scope="function")  # Default
   @pytest.fixture(scope="class")
   @pytest.fixture(scope="module")
   @pytest.fixture(scope="session")
   ```

4. **Mock Issues**
   ```python
   # Ensure proper mock setup
   with patch.object(service, 'method') as mock_method:
       mock_method.return_value = expected_value
       # Test code here
   ```

### Debugging Tests

```python
# Add debug prints
def test_debug_example():
    result = some_function()
    print(f"Debug: result = {result}")
    assert result == expected_value

# Use pytest debugging options
# pytest tests/ -v -s --pdb
```

This comprehensive testing guide ensures that the crop variety recommendations system is thoroughly tested across all dimensions - functionality, performance, integration, and agricultural accuracy.