"""
Integration tests for drought management database models.

Tests database operations with the Pydantic models.
"""

import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal
import os
import tempfile

# Mock database URL for testing
TEST_DATABASE_URL = "sqlite:///test_drought.db"

from src.database.drought_db import DroughtServiceDatabase, DroughtAssessment, ConservationPractice, DroughtMonitoring, MonitoringDataPoint, WaterSavings, DroughtAlert, FieldCharacteristics
from src.models.drought_models import (
    DroughtRiskLevel,
    SoilMoistureLevel,
    ConservationPracticeType,
    SoilHealthImpact,
    WeatherImpact,
    SoilMoistureStatus,
    WaterSavingsPotential
)


class TestDatabaseIntegration:
    """Test database integration with Pydantic models."""
    
    @pytest_asyncio.fixture
    async def db(self):
        """Create test database instance."""
        # Use in-memory SQLite for testing
        db = DroughtServiceDatabase("sqlite:///:memory:")
        await db.initialize()
        yield db
        await db.cleanup()
    
    @pytest.mark.asyncio
    async def test_create_drought_assessment(self, db):
        """Test creating drought assessment in database."""
        assessment_data = {
            "id": uuid4(),
            "farm_location_id": uuid4(),
            "field_id": uuid4(),
            "assessment_date": datetime.utcnow(),
            "drought_risk_level": DroughtRiskLevel.HIGH.value,
            "soil_moisture_surface": 15.0,
            "soil_moisture_deep": 25.0,
            "available_water_capacity": 1.0,
            "moisture_level": SoilMoistureLevel.VERY_DRY.value,
            "weather_impact_data": {
                "temperature_impact": "Extreme heat expected",
                "precipitation_impact": "No precipitation forecast",
                "humidity_impact": "Very low humidity",
                "wind_impact": "High winds",
                "forecast_confidence": 0.9,
                "risk_factors": ["Heat stress", "Drought conditions"]
            },
            "confidence_score": 0.9,
            "recommendations": [
                {
                    "action_type": "irrigation",
                    "priority": "high",
                    "description": "Immediate irrigation required"
                }
            ]
        }
        
        assessment = await db.create_drought_assessment(assessment_data)
        
        assert assessment.id == assessment_data["id"]
        assert assessment.farm_location_id == assessment_data["farm_location_id"]
        assert assessment.drought_risk_level == DroughtRiskLevel.HIGH.value
        assert assessment.soil_moisture_surface == 15.0
        assert assessment.confidence_score == 0.9
        assert assessment.weather_impact_data["forecast_confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_create_conservation_practice(self, db):
        """Test creating conservation practice in database."""
        practice_data = {
            "id": uuid4(),
            "field_id": uuid4(),
            "practice_name": "Cover Crop Implementation",
            "practice_type": ConservationPracticeType.COVER_CROPS.value,
            "description": "Planting winter rye as cover crop",
            "implementation_cost": Decimal("25.00"),
            "water_savings_percent": 15.5,
            "soil_health_impact": SoilHealthImpact.POSITIVE.value,
            "equipment_requirements": [
                {
                    "equipment_type": "planter",
                    "equipment_name": "Cover Crop Planter",
                    "availability": True
                }
            ],
            "implementation_time_days": 3,
            "maintenance_cost_per_year": Decimal("5.00"),
            "effectiveness_rating": 8.5,
            "implementation_status": "planned"
        }
        
        practice = await db.create_conservation_practice(practice_data)
        
        assert practice.id == practice_data["id"]
        assert practice.practice_name == "Cover Crop Implementation"
        assert practice.practice_type == ConservationPracticeType.COVER_CROPS.value
        assert practice.water_savings_percent == 15.5
        assert practice.soil_health_impact == SoilHealthImpact.POSITIVE.value
        assert practice.effectiveness_rating == 8.5
        assert len(practice.equipment_requirements) == 1
        assert practice.equipment_requirements[0]["equipment_type"] == "planter"
    
    @pytest.mark.asyncio
    async def test_create_monitoring_config(self, db):
        """Test creating drought monitoring configuration."""
        monitoring_data = {
            "id": uuid4(),
            "farm_location_id": uuid4(),
            "monitoring_frequency": "daily",
            "alert_thresholds": {
                "soil_moisture": 20.0,
                "temperature": 35.0,
                "precipitation": 0.0
            },
            "notification_preferences": {
                "email": True,
                "sms": False,
                "push": True
            },
            "integration_services": ["weather_api", "soil_sensors"],
            "status": "active"
        }
        
        monitoring = await db.create_monitoring_config(monitoring_data)
        
        assert monitoring.id == monitoring_data["id"]
        assert monitoring.farm_location_id == monitoring_data["farm_location_id"]
        assert monitoring.monitoring_frequency == "daily"
        assert monitoring.alert_thresholds["soil_moisture"] == 20.0
        assert monitoring.notification_preferences["email"] is True
        assert len(monitoring.integration_services) == 2
        assert monitoring.status == "active"
    
    @pytest.mark.asyncio
    async def test_create_monitoring_data_point(self, db):
        """Test creating monitoring data point."""
        # First create a monitoring config
        monitoring_data = {
            "id": uuid4(),
            "farm_location_id": uuid4(),
            "monitoring_frequency": "daily",
            "alert_thresholds": {},
            "notification_preferences": {},
            "integration_services": [],
            "status": "active"
        }
        monitoring = await db.create_monitoring_config(monitoring_data)
        
        # Create data point
        data_point_data = {
            "id": uuid4(),
            "monitoring_id": monitoring.id,
            "field_id": uuid4(),
            "data_type": "soil_moisture",
            "data_value": 25.5,
            "data_unit": "percent",
            "additional_data": {
                "depth_cm": 15,
                "sensor_id": "SM001"
            },
            "collection_time": datetime.utcnow(),
            "data_source": "soil_sensor",
            "quality_score": 0.95
        }
        
        data_point = await db.create_monitoring_data_point(data_point_data)
        
        assert data_point.id == data_point_data["id"]
        assert data_point.monitoring_id == monitoring.id
        assert data_point.field_id == data_point_data["field_id"]
        assert data_point.data_type == "soil_moisture"
        assert data_point.data_value == 25.5
        assert data_point.data_unit == "percent"
        assert data_point.additional_data["depth_cm"] == 15
        assert data_point.data_source == "soil_sensor"
        assert data_point.quality_score == 0.95
    
    @pytest.mark.asyncio
    async def test_create_water_savings_record(self, db):
        """Test creating water savings calculation record."""
        savings_data = {
            "id": uuid4(),
            "field_id": uuid4(),
            "calculation_date": datetime.utcnow(),
            "current_water_usage": Decimal("1000.00"),
            "projected_savings": Decimal("250.00"),
            "savings_percentage": 25.0,
            "implementation_cost": Decimal("2000.00"),
            "annual_savings_value": Decimal("500.00"),
            "roi_percentage": 25.0,
            "payback_period_years": 4.0,
            "effectiveness_assumptions": {
                "practice_effectiveness": 0.8,
                "weather_factor": 0.9
            },
            "calculation_metadata": {
                "calculation_method": "water_balance_model",
                "data_sources": ["weather_api", "soil_sensors"]
            }
        }
        
        savings = await db.create_water_savings_record(savings_data)
        
        assert savings.id == savings_data["id"]
        assert savings.field_id == savings_data["field_id"]
        assert savings.current_water_usage == Decimal("1000.00")
        assert savings.projected_savings == Decimal("250.00")
        assert savings.savings_percentage == 25.0
        assert savings.implementation_cost == Decimal("2000.00")
        assert savings.annual_savings_value == Decimal("500.00")
        assert savings.roi_percentage == 25.0
        assert savings.payback_period_years == 4.0
        assert savings.effectiveness_assumptions["practice_effectiveness"] == 0.8
        assert savings.calculation_metadata["calculation_method"] == "water_balance_model"
    
    @pytest.mark.asyncio
    async def test_create_drought_alert(self, db):
        """Test creating drought alert."""
        alert_data = {
            "id": uuid4(),
            "farm_location_id": uuid4(),
            "field_id": uuid4(),
            "alert_type": "soil_moisture_low",
            "severity": "high",
            "message": "Soil moisture below critical threshold",
            "recommendation": "Implement irrigation immediately",
            "alert_data": {
                "current_moisture": 15.0,
                "threshold": 20.0,
                "days_since_rain": 14
            },
            "status": "active",
            "acknowledged": False,
            "resolved": False
        }
        
        alert = await db.create_drought_alert(alert_data)
        
        assert alert.id == alert_data["id"]
        assert alert.farm_location_id == alert_data["farm_location_id"]
        assert alert.alert_type == "soil_moisture_low"
        assert alert.severity == "high"
        assert alert.message == "Soil moisture below critical threshold"
        assert alert.recommendation == "Implement irrigation immediately"
        assert alert.alert_data["current_moisture"] == 15.0
        assert alert.status == "active"
        assert alert.acknowledged is False
        assert alert.resolved is False
    
    @pytest.mark.asyncio
    async def test_create_field_characteristics(self, db):
        """Test creating field characteristics record."""
        characteristics_data = {
            "id": uuid4(),
            "field_id": uuid4(),
            "farm_location_id": uuid4(),
            "field_name": "North Field",
            "field_size_acres": Decimal("40.5"),
            "soil_type": "clay_loam",
            "slope_percent": 3.5,
            "drainage_class": "well_drained",
            "organic_matter_percent": 3.2,
            "climate_zone": "6a",
            "current_irrigation_type": "center_pivot",
            "water_source": "well",
            "energy_cost_per_kwh": Decimal("0.12"),
            "additional_characteristics": {
                "soil_depth": 36,
                "ph_level": 6.8,
                "cec": 15.5
            }
        }
        
        characteristics = await db.create_field_characteristics(characteristics_data)
        
        assert characteristics.id == characteristics_data["id"]
        assert characteristics.field_id == characteristics_data["field_id"]
        assert characteristics.farm_location_id == characteristics_data["farm_location_id"]
        assert characteristics.field_name == "North Field"
        assert characteristics.field_size_acres == Decimal("40.5")
        assert characteristics.soil_type == "clay_loam"
        assert characteristics.slope_percent == 3.5
        assert characteristics.drainage_class == "well_drained"
        assert characteristics.organic_matter_percent == 3.2
        assert characteristics.climate_zone == "6a"
        assert characteristics.current_irrigation_type == "center_pivot"
        assert characteristics.water_source == "well"
        assert characteristics.energy_cost_per_kwh == Decimal("0.12")
        assert characteristics.additional_characteristics["soil_depth"] == 36
        assert characteristics.additional_characteristics["ph_level"] == 6.8
        assert characteristics.additional_characteristics["cec"] == 15.5
    
    @pytest.mark.asyncio
    async def test_get_operations(self, db):
        """Test database get operations."""
        # Create test data
        farm_id = uuid4()
        field_id = uuid4()
        
        assessment_data = {
            "id": uuid4(),
            "farm_location_id": farm_id,
            "field_id": field_id,
            "assessment_date": datetime.utcnow(),
            "drought_risk_level": DroughtRiskLevel.MODERATE.value,
            "soil_moisture_surface": 35.0,
            "soil_moisture_deep": 45.0,
            "available_water_capacity": 2.5,
            "moisture_level": SoilMoistureLevel.ADEQUATE.value,
            "weather_impact_data": {},
            "confidence_score": 0.8,
            "recommendations": []
        }
        assessment = await db.create_drought_assessment(assessment_data)
        
        # Test get assessment by ID
        retrieved_assessment = await db.get_drought_assessment(assessment.id)
        assert retrieved_assessment is not None
        assert retrieved_assessment.id == assessment.id
        assert retrieved_assessment.drought_risk_level == DroughtRiskLevel.MODERATE.value
        
        # Test get farm assessments
        farm_assessments = await db.get_farm_assessments(farm_id)
        assert len(farm_assessments) == 1
        assert farm_assessments[0].id == assessment.id
        
        # Test get field practices
        practice_data = {
            "id": uuid4(),
            "field_id": field_id,
            "practice_name": "No-Till Implementation",
            "practice_type": ConservationPracticeType.NO_TILL.value,
            "description": "Transition to no-till farming",
            "implementation_cost": Decimal("50.00"),
            "water_savings_percent": 20.0,
            "soil_health_impact": SoilHealthImpact.HIGHLY_POSITIVE.value,
            "equipment_requirements": [],
            "implementation_time_days": 5,
            "maintenance_cost_per_year": Decimal("10.00"),
            "effectiveness_rating": 9.0,
            "implementation_status": "planned"
        }
        practice = await db.create_conservation_practice(practice_data)
        
        field_practices = await db.get_field_practices(field_id)
        assert len(field_practices) == 1
        assert field_practices[0].id == practice.id
        assert field_practices[0].practice_name == "No-Till Implementation"
    
    @pytest.mark.asyncio
    async def test_update_field_characteristics(self, db):
        """Test updating field characteristics."""
        # Create initial characteristics
        characteristics_data = {
            "id": uuid4(),
            "field_id": uuid4(),
            "farm_location_id": uuid4(),
            "field_name": "South Field",
            "field_size_acres": Decimal("25.0"),
            "soil_type": "sandy_loam",
            "slope_percent": 2.0,
            "drainage_class": "moderately_well_drained",
            "organic_matter_percent": 2.5,
            "climate_zone": "6b",
            "current_irrigation_type": "drip",
            "water_source": "surface_water",
            "energy_cost_per_kwh": Decimal("0.10"),
            "additional_characteristics": {}
        }
        characteristics = await db.create_field_characteristics(characteristics_data)
        
        # Update characteristics
        update_data = {
            "field_name": "South Field - Updated",
            "organic_matter_percent": 3.0,
            "current_irrigation_type": "center_pivot",
            "additional_characteristics": {
                "soil_depth": 42,
                "ph_level": 7.0
            }
        }
        
        updated_characteristics = await db.update_field_characteristics(
            characteristics.field_id, 
            update_data
        )
        
        assert updated_characteristics is not None
        assert updated_characteristics.field_name == "South Field - Updated"
        assert updated_characteristics.organic_matter_percent == 3.0
        assert updated_characteristics.current_irrigation_type == "center_pivot"
        assert updated_characteristics.additional_characteristics["soil_depth"] == 42
        assert updated_characteristics.additional_characteristics["ph_level"] == 7.0
    
    @pytest.mark.asyncio
    async def test_database_health_check(self, db):
        """Test database health check."""
        health_status = await db.health_check()
        assert health_status is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])