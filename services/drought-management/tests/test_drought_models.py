"""
Test suite for drought management data models.

Tests all Pydantic models for validation, serialization, and business logic.
"""

import pytest
from datetime import datetime, date
from uuid import uuid4
from decimal import Decimal
from pydantic import ValidationError

from src.models.drought_models import (
    DroughtRiskLevel,
    SoilMoistureLevel,
    ConservationPracticeType,
    SoilHealthImpact,
    EquipmentRequirement,
    ConservationPractice,
    WeatherImpact,
    SoilMoistureStatus,
    RecommendedAction,
    WaterSavingsPotential,
    DroughtAssessment,
    DroughtRiskAssessment,
    DroughtAssessmentRequest,
    ConservationPracticeRequest,
    DroughtMonitoringRequest,
    WaterSavingsRequest,
    DroughtAssessmentResponse,
    ConservationPracticeResponse,
    DroughtMonitoringResponse,
    WaterSavingsResponse,
    IrrigationSystemType,
    WaterSourceType,
    IrrigationEfficiencyLevel,
    IrrigationSystemAssessment,
    WaterSourceAssessment,
    IrrigationConstraint,
    IrrigationOptimization,
    IrrigationAssessmentRequest,
    IrrigationScheduleRequest,
    IrrigationOptimizationRequest,
    IrrigationAssessmentResponse,
    IrrigationOptimizationResponse,
    IrrigationScheduleResponse
)


class TestEnums:
    """Test enum values and validation."""
    
    def test_drought_risk_levels(self):
        """Test drought risk level enum values."""
        assert DroughtRiskLevel.LOW == "low"
        assert DroughtRiskLevel.MODERATE == "moderate"
        assert DroughtRiskLevel.HIGH == "high"
        assert DroughtRiskLevel.SEVERE == "severe"
        assert DroughtRiskLevel.EXTREME == "extreme"
    
    def test_soil_moisture_levels(self):
        """Test soil moisture level enum values."""
        assert SoilMoistureLevel.VERY_DRY == "very_dry"
        assert SoilMoistureLevel.DRY == "dry"
        assert SoilMoistureLevel.ADEQUATE == "adequate"
        assert SoilMoistureLevel.MOIST == "moist"
        assert SoilMoistureLevel.SATURATED == "saturated"
    
    def test_conservation_practice_types(self):
        """Test conservation practice type enum values."""
        assert ConservationPracticeType.COVER_CROPS == "cover_crops"
        assert ConservationPracticeType.NO_TILL == "no_till"
        assert ConservationPracticeType.MULCHING == "mulching"
        assert ConservationPracticeType.IRRIGATION_EFFICIENCY == "irrigation_efficiency"
        assert ConservationPracticeType.SOIL_AMENDMENTS == "soil_amendments"
        assert ConservationPracticeType.WATER_HARVESTING == "water_harvesting"
        assert ConservationPracticeType.CROP_ROTATION == "crop_rotation"
        assert ConservationPracticeType.TERRAIN_MODIFICATION == "terrain_modification"


class TestEquipmentRequirement:
    """Test EquipmentRequirement model."""
    
    def test_valid_equipment_requirement(self):
        """Test creating valid equipment requirement."""
        equipment = EquipmentRequirement(
            equipment_type="tractor",
            equipment_name="John Deere 6120R",
            availability=True,
            rental_cost_per_day=Decimal("150.00"),
            purchase_cost=Decimal("85000.00")
        )
        
        assert equipment.equipment_type == "tractor"
        assert equipment.equipment_name == "John Deere 6120R"
        assert equipment.availability is True
        assert equipment.rental_cost_per_day == Decimal("150.00")
        assert equipment.purchase_cost == Decimal("85000.00")
    
    def test_minimal_equipment_requirement(self):
        """Test creating minimal equipment requirement."""
        equipment = EquipmentRequirement(
            equipment_type="spreader",
            equipment_name="Lime Spreader",
            availability=False
        )
        
        assert equipment.equipment_type == "spreader"
        assert equipment.equipment_name == "Lime Spreader"
        assert equipment.availability is False
        assert equipment.rental_cost_per_day is None
        assert equipment.purchase_cost is None


class TestConservationPractice:
    """Test ConservationPractice model."""
    
    def test_valid_conservation_practice(self):
        """Test creating valid conservation practice."""
        practice = ConservationPractice(
            practice_id=uuid4(),
            practice_name="Cover Crop Implementation",
            practice_type=ConservationPracticeType.COVER_CROPS,
            description="Planting winter rye as cover crop",
            implementation_cost=Decimal("25.00"),
            water_savings_percent=15.5,
            soil_health_impact=SoilHealthImpact.POSITIVE,
            equipment_requirements=[],
            implementation_time_days=3,
            maintenance_cost_per_year=Decimal("5.00"),
            effectiveness_rating=8.5
        )
        
        assert practice.practice_name == "Cover Crop Implementation"
        assert practice.practice_type == ConservationPracticeType.COVER_CROPS
        assert practice.water_savings_percent == 15.5
        assert practice.soil_health_impact == SoilHealthImpact.POSITIVE
        assert practice.effectiveness_rating == 8.5
    
    def test_water_savings_validation(self):
        """Test water savings percentage validation."""
        # Valid percentage
        practice = ConservationPractice(
            practice_id=uuid4(),
            practice_name="Test Practice",
            practice_type=ConservationPracticeType.COVER_CROPS,
            description="Test",
            implementation_cost=Decimal("10.00"),
            water_savings_percent=50.0,
            soil_health_impact=SoilHealthImpact.NEUTRAL,
            equipment_requirements=[],
            implementation_time_days=1,
            maintenance_cost_per_year=Decimal("1.00"),
            effectiveness_rating=5.0
        )
        assert practice.water_savings_percent == 50.0
        
        # Invalid percentage - too high
        with pytest.raises(ValidationError):
            ConservationPractice(
                practice_id=uuid4(),
                practice_name="Test Practice",
                practice_type=ConservationPracticeType.COVER_CROPS,
                description="Test",
                implementation_cost=Decimal("10.00"),
                water_savings_percent=150.0,  # Invalid
                soil_health_impact=SoilHealthImpact.NEUTRAL,
                equipment_requirements=[],
                implementation_time_days=1,
                maintenance_cost_per_year=Decimal("1.00"),
                effectiveness_rating=5.0
            )
        
        # Invalid percentage - negative
        with pytest.raises(ValidationError):
            ConservationPractice(
                practice_id=uuid4(),
                practice_name="Test Practice",
                practice_type=ConservationPracticeType.COVER_CROPS,
                description="Test",
                implementation_cost=Decimal("10.00"),
                water_savings_percent=-10.0,  # Invalid
                soil_health_impact=SoilHealthImpact.NEUTRAL,
                equipment_requirements=[],
                implementation_time_days=1,
                maintenance_cost_per_year=Decimal("1.00"),
                effectiveness_rating=5.0
            )


class TestWeatherImpact:
    """Test WeatherImpact model."""
    
    def test_valid_weather_impact(self):
        """Test creating valid weather impact."""
        impact = WeatherImpact(
            temperature_impact="Above average temperatures expected",
            precipitation_impact="Below normal precipitation forecast",
            humidity_impact="Low humidity conditions",
            wind_impact="Moderate wind speeds",
            forecast_confidence=0.85,
            risk_factors=["Heat stress", "Drought conditions"]
        )
        
        assert impact.temperature_impact == "Above average temperatures expected"
        assert impact.precipitation_impact == "Below normal precipitation forecast"
        assert impact.forecast_confidence == 0.85
        assert len(impact.risk_factors) == 2
        assert "Heat stress" in impact.risk_factors
    
    def test_forecast_confidence_validation(self):
        """Test forecast confidence validation."""
        # Valid confidence
        impact = WeatherImpact(
            temperature_impact="Test",
            precipitation_impact="Test",
            humidity_impact="Test",
            wind_impact="Test",
            forecast_confidence=0.5
        )
        assert impact.forecast_confidence == 0.5
        
        # Invalid confidence - too high
        with pytest.raises(ValidationError):
            WeatherImpact(
                temperature_impact="Test",
                precipitation_impact="Test",
                humidity_impact="Test",
                wind_impact="Test",
                forecast_confidence=1.5  # Invalid
            )
        
        # Invalid confidence - negative
        with pytest.raises(ValidationError):
            WeatherImpact(
                temperature_impact="Test",
                precipitation_impact="Test",
                humidity_impact="Test",
                wind_impact="Test",
                forecast_confidence=-0.1  # Invalid
            )


class TestSoilMoistureStatus:
    """Test SoilMoistureStatus model."""
    
    def test_valid_soil_moisture_status(self):
        """Test creating valid soil moisture status."""
        status = SoilMoistureStatus(
            field_id=uuid4(),
            surface_moisture_percent=25.5,
            deep_moisture_percent=45.0,
            available_water_capacity=2.5,
            moisture_level=SoilMoistureLevel.DRY,
            irrigation_recommendation="Consider irrigation within 3-5 days",
            days_until_critical=5
        )
        
        assert status.surface_moisture_percent == 25.5
        assert status.deep_moisture_percent == 45.0
        assert status.available_water_capacity == 2.5
        assert status.moisture_level == SoilMoistureLevel.DRY
        assert status.days_until_critical == 5
    
    def test_moisture_percentage_validation(self):
        """Test moisture percentage validation."""
        # Valid percentages
        status = SoilMoistureStatus(
            field_id=uuid4(),
            surface_moisture_percent=50.0,
            deep_moisture_percent=75.0,
            available_water_capacity=3.0,
            moisture_level=SoilMoistureLevel.ADEQUATE,
            irrigation_recommendation="Adequate moisture"
        )
        assert status.surface_moisture_percent == 50.0
        assert status.deep_moisture_percent == 75.0
        
        # Invalid percentage - too high
        with pytest.raises(ValidationError):
            SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=150.0,  # Invalid
                deep_moisture_percent=75.0,
                available_water_capacity=3.0,
                moisture_level=SoilMoistureLevel.ADEQUATE,
                irrigation_recommendation="Test"
            )
        
        # Invalid percentage - negative
        with pytest.raises(ValidationError):
            SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=50.0,
                deep_moisture_percent=-10.0,  # Invalid
                available_water_capacity=3.0,
                moisture_level=SoilMoistureLevel.ADEQUATE,
                irrigation_recommendation="Test"
            )


class TestRecommendedAction:
    """Test RecommendedAction model."""
    
    def test_valid_recommended_action(self):
        """Test creating valid recommended action."""
        action = RecommendedAction(
            action_id=uuid4(),
            action_type="irrigation_schedule",
            priority="high",
            description="Implement drip irrigation system",
            implementation_timeline="2-3 weeks",
            expected_benefit="25% water savings",
            cost_estimate=Decimal("5000.00"),
            resources_required=["Drip tape", "Installation labor", "Water source connection"]
        )
        
        assert action.action_type == "irrigation_schedule"
        assert action.priority == "high"
        assert action.description == "Implement drip irrigation system"
        assert action.cost_estimate == Decimal("5000.00")
        assert len(action.resources_required) == 3


class TestWaterSavingsPotential:
    """Test WaterSavingsPotential model."""
    
    def test_valid_water_savings_potential(self):
        """Test creating valid water savings potential."""
        savings = WaterSavingsPotential(
            current_water_usage=Decimal("1000.00"),
            potential_savings=Decimal("250.00"),
            savings_percentage=25.0,
            cost_savings_per_year=Decimal("500.00"),
            implementation_cost=Decimal("2000.00"),
            payback_period_years=4.0
        )
        
        assert savings.current_water_usage == Decimal("1000.00")
        assert savings.potential_savings == Decimal("250.00")
        assert savings.savings_percentage == 25.0
        assert savings.payback_period_years == 4.0
    
    def test_savings_percentage_validation(self):
        """Test savings percentage validation."""
        # Valid percentage
        savings = WaterSavingsPotential(
            current_water_usage=Decimal("1000.00"),
            potential_savings=Decimal("100.00"),
            savings_percentage=10.0,
            cost_savings_per_year=Decimal("200.00"),
            implementation_cost=Decimal("1000.00"),
            payback_period_years=5.0
        )
        assert savings.savings_percentage == 10.0
        
        # Invalid percentage - too high
        with pytest.raises(ValidationError):
            WaterSavingsPotential(
                current_water_usage=Decimal("1000.00"),
                potential_savings=Decimal("100.00"),
                savings_percentage=150.0,  # Invalid
                cost_savings_per_year=Decimal("200.00"),
                implementation_cost=Decimal("1000.00"),
                payback_period_years=5.0
            )


class TestDroughtAssessment:
    """Test DroughtAssessment model."""
    
    def test_valid_drought_assessment(self):
        """Test creating valid drought assessment."""
        assessment = DroughtAssessment(
            assessment_id=uuid4(),
            farm_location_id=uuid4(),
            drought_risk_level=DroughtRiskLevel.HIGH,
            soil_moisture_status=SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=20.0,
                deep_moisture_percent=35.0,
                available_water_capacity=1.5,
                moisture_level=SoilMoistureLevel.DRY,
                irrigation_recommendation="Immediate irrigation needed"
            ),
            weather_forecast_impact=WeatherImpact(
                temperature_impact="High temperatures expected",
                precipitation_impact="No significant precipitation",
                humidity_impact="Low humidity",
                wind_impact="Moderate winds",
                forecast_confidence=0.8,
                risk_factors=["Heat stress"]
            ),
            current_practices=[],
            recommended_actions=[],
            water_savings_potential=WaterSavingsPotential(
                current_water_usage=Decimal("800.00"),
                potential_savings=Decimal("200.00"),
                savings_percentage=25.0,
                cost_savings_per_year=Decimal("400.00"),
                implementation_cost=Decimal("1500.00"),
                payback_period_years=3.75
            ),
            confidence_score=0.85
        )
        
        assert assessment.drought_risk_level == DroughtRiskLevel.HIGH
        assert assessment.confidence_score == 0.85
        assert assessment.soil_moisture_status.moisture_level == SoilMoistureLevel.DRY
        assert assessment.water_savings_potential.savings_percentage == 25.0
    
    def test_confidence_score_validation(self):
        """Test confidence score validation."""
        # Valid confidence score
        assessment = DroughtAssessment(
            assessment_id=uuid4(),
            farm_location_id=uuid4(),
            drought_risk_level=DroughtRiskLevel.MODERATE,
            soil_moisture_status=SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=50.0,
                deep_moisture_percent=60.0,
                available_water_capacity=3.0,
                moisture_level=SoilMoistureLevel.ADEQUATE,
                irrigation_recommendation="Adequate moisture"
            ),
            weather_forecast_impact=WeatherImpact(
                temperature_impact="Normal",
                precipitation_impact="Normal",
                humidity_impact="Normal",
                wind_impact="Normal",
                forecast_confidence=0.7,
                risk_factors=[]
            ),
            current_practices=[],
            recommended_actions=[],
            water_savings_potential=WaterSavingsPotential(
                current_water_usage=Decimal("500.00"),
                potential_savings=Decimal("50.00"),
                savings_percentage=10.0,
                cost_savings_per_year=Decimal("100.00"),
                implementation_cost=Decimal("500.00"),
                payback_period_years=5.0
            ),
            confidence_score=0.7
        )
        assert assessment.confidence_score == 0.7
        
        # Invalid confidence score - too high
        with pytest.raises(ValidationError):
            DroughtAssessment(
                assessment_id=uuid4(),
                farm_location_id=uuid4(),
                drought_risk_level=DroughtRiskLevel.MODERATE,
                soil_moisture_status=SoilMoistureStatus(
                    field_id=uuid4(),
                    surface_moisture_percent=50.0,
                    deep_moisture_percent=60.0,
                    available_water_capacity=3.0,
                    moisture_level=SoilMoistureLevel.ADEQUATE,
                    irrigation_recommendation="Adequate moisture"
                ),
                weather_forecast_impact=WeatherImpact(
                    temperature_impact="Normal",
                    precipitation_impact="Normal",
                    humidity_impact="Normal",
                    wind_impact="Normal",
                    forecast_confidence=0.7,
                    risk_factors=[]
                ),
                current_practices=[],
                recommended_actions=[],
                water_savings_potential=WaterSavingsPotential(
                    current_water_usage=Decimal("500.00"),
                    potential_savings=Decimal("50.00"),
                    savings_percentage=10.0,
                    cost_savings_per_year=Decimal("100.00"),
                    implementation_cost=Decimal("500.00"),
                    payback_period_years=5.0
                ),
                confidence_score=1.5  # Invalid
            )


class TestRequestModels:
    """Test request models."""
    
    def test_drought_assessment_request(self):
        """Test DroughtAssessmentRequest model."""
        request = DroughtAssessmentRequest(
            farm_location_id=uuid4(),
            field_id=uuid4(),
            crop_type="corn",
            growth_stage="V6",
            soil_type="clay_loam",
            irrigation_available=True,
            include_forecast=True,
            assessment_depth_days=30
        )
        
        assert request.crop_type == "corn"
        assert request.growth_stage == "V6"
        assert request.soil_type == "clay_loam"
        assert request.irrigation_available is True
        assert request.assessment_depth_days == 30
    
    def test_conservation_practice_request(self):
        """Test ConservationPracticeRequest model."""
        request = ConservationPracticeRequest(
            field_id=uuid4(),
            soil_type="sandy_loam",
            slope_percent=5.0,
            drainage_class="well_drained",
            current_practices=["conventional_till"],
            available_equipment=["tractor", "planter"],
            budget_constraint=Decimal("100.00"),
            implementation_timeline="immediate"
        )
        
        assert request.soil_type == "sandy_loam"
        assert request.slope_percent == 5.0
        assert request.drainage_class == "well_drained"
        assert len(request.current_practices) == 1
        assert len(request.available_equipment) == 2
        assert request.budget_constraint == Decimal("100.00")
    
    def test_drought_monitoring_request(self):
        """Test DroughtMonitoringRequest model."""
        request = DroughtMonitoringRequest(
            farm_location_id=uuid4(),
            field_ids=[uuid4(), uuid4()],
            monitoring_frequency="daily",
            alert_thresholds={"soil_moisture": 20.0, "temperature": 35.0},
            notification_preferences={"email": True, "sms": False},
            integration_services=["weather_api", "soil_sensors"]
        )
        
        assert len(request.field_ids) == 2
        assert request.monitoring_frequency == "daily"
        assert request.alert_thresholds["soil_moisture"] == 20.0
        assert request.notification_preferences["email"] is True
        assert len(request.integration_services) == 2


class TestResponseModels:
    """Test response models."""
    
    def test_drought_assessment_response(self):
        """Test DroughtAssessmentResponse model."""
        assessment = DroughtAssessment(
            assessment_id=uuid4(),
            farm_location_id=uuid4(),
            drought_risk_level=DroughtRiskLevel.MODERATE,
            soil_moisture_status=SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=40.0,
                deep_moisture_percent=55.0,
                available_water_capacity=2.5,
                moisture_level=SoilMoistureLevel.ADEQUATE,
                irrigation_recommendation="Monitor conditions"
            ),
            weather_forecast_impact=WeatherImpact(
                temperature_impact="Normal",
                precipitation_impact="Normal",
                humidity_impact="Normal",
                wind_impact="Normal",
                forecast_confidence=0.8,
                risk_factors=[]
            ),
            current_practices=[],
            recommended_actions=[],
            water_savings_potential=WaterSavingsPotential(
                current_water_usage=Decimal("600.00"),
                potential_savings=Decimal("60.00"),
                savings_percentage=10.0,
                cost_savings_per_year=Decimal("120.00"),
                implementation_cost=Decimal("600.00"),
                payback_period_years=5.0
            ),
            confidence_score=0.8
        )
        
        response = DroughtAssessmentResponse(
            assessment=assessment,
            recommendations=[],
            next_steps=["Monitor soil moisture", "Check weather forecast"],
            monitoring_schedule={"frequency": "daily", "parameters": ["soil_moisture", "temperature"]}
        )
        
        assert response.assessment.drought_risk_level == DroughtRiskLevel.MODERATE
        assert len(response.next_steps) == 2
        assert response.monitoring_schedule["frequency"] == "daily"


class TestIrrigationModels:
    """Test irrigation-related models."""
    
    def test_irrigation_system_assessment(self):
        """Test IrrigationSystemAssessment model."""
        assessment = IrrigationSystemAssessment(
            system_type=IrrigationSystemType.CENTER_PIVOT,
            current_efficiency=0.75,
            efficiency_level=IrrigationEfficiencyLevel.MODERATE,
            water_distribution_uniformity=0.80,
            pressure_consistency=0.85,
            coverage_area_percent=95.0,
            maintenance_status="good",
            age_years=8,
            estimated_water_loss_percent=15.0,
            energy_efficiency_score=0.70,
            overall_score=78.5
        )
        
        assert assessment.system_type == IrrigationSystemType.CENTER_PIVOT
        assert assessment.current_efficiency == 0.75
        assert assessment.efficiency_level == IrrigationEfficiencyLevel.MODERATE
        assert assessment.coverage_area_percent == 95.0
        assert assessment.age_years == 8
        assert assessment.overall_score == 78.5
    
    def test_water_source_assessment(self):
        """Test WaterSourceAssessment model."""
        assessment = WaterSourceAssessment(
            source_type=WaterSourceType.WELL,
            available_capacity_gpm=500.0,
            water_quality_score=0.90,
            reliability_score=0.85,
            cost_per_gallon=Decimal("0.002"),
            seasonal_variation_percent=20.0,
            sustainability_score=0.80,
            regulatory_compliance=True,
            pumping_capacity_gpm=450.0,
            storage_capacity_gallons=10000.0
        )
        
        assert assessment.source_type == WaterSourceType.WELL
        assert assessment.available_capacity_gpm == 500.0
        assert assessment.water_quality_score == 0.90
        assert assessment.cost_per_gallon == Decimal("0.002")
        assert assessment.regulatory_compliance is True
        assert assessment.storage_capacity_gallons == 10000.0
    
    def test_irrigation_optimization(self):
        """Test IrrigationOptimization model."""
        optimization = IrrigationOptimization(
            optimization_type="system_upgrade",
            description="Upgrade to variable rate irrigation",
            potential_water_savings_percent=20.0,
            potential_cost_savings_per_year=Decimal("2000.00"),
            implementation_cost=Decimal("15000.00"),
            payback_period_years=7.5,
            implementation_timeline_days=30,
            priority_level="medium",
            equipment_requirements=[]
        )
        
        assert optimization.optimization_type == "system_upgrade"
        assert optimization.potential_water_savings_percent == 20.0
        assert optimization.potential_cost_savings_per_year == Decimal("2000.00")
        assert optimization.payback_period_years == 7.5
        assert optimization.priority_level == "medium"


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_conservation_practice_serialization(self):
        """Test ConservationPractice serialization."""
        practice = ConservationPractice(
            practice_id=uuid4(),
            practice_name="No-Till Implementation",
            practice_type=ConservationPracticeType.NO_TILL,
            description="Transition to no-till farming",
            implementation_cost=Decimal("50.00"),
            water_savings_percent=20.0,
            soil_health_impact=SoilHealthImpact.HIGHLY_POSITIVE,
            equipment_requirements=[],
            implementation_time_days=5,
            maintenance_cost_per_year=Decimal("10.00"),
            effectiveness_rating=9.0
        )
        
        # Test JSON serialization
        json_data = practice.model_dump()
        assert json_data["practice_name"] == "No-Till Implementation"
        assert json_data["practice_type"] == "no_till"
        assert json_data["water_savings_percent"] == 20.0
        assert json_data["soil_health_impact"] == "highly_positive"
        
        # Test JSON deserialization
        practice_from_json = ConservationPractice(**json_data)
        assert practice_from_json.practice_name == practice.practice_name
        assert practice_from_json.practice_type == practice.practice_type
        assert practice_from_json.water_savings_percent == practice.water_savings_percent
    
    def test_drought_assessment_serialization(self):
        """Test DroughtAssessment serialization."""
        assessment = DroughtAssessment(
            assessment_id=uuid4(),
            farm_location_id=uuid4(),
            drought_risk_level=DroughtRiskLevel.HIGH,
            soil_moisture_status=SoilMoistureStatus(
                field_id=uuid4(),
                surface_moisture_percent=15.0,
                deep_moisture_percent=25.0,
                available_water_capacity=1.0,
                moisture_level=SoilMoistureLevel.VERY_DRY,
                irrigation_recommendation="Immediate irrigation required"
            ),
            weather_forecast_impact=WeatherImpact(
                temperature_impact="Extreme heat expected",
                precipitation_impact="No precipitation forecast",
                humidity_impact="Very low humidity",
                wind_impact="High winds",
                forecast_confidence=0.9,
                risk_factors=["Heat stress", "Drought conditions", "Wind erosion"]
            ),
            current_practices=[],
            recommended_actions=[],
            water_savings_potential=WaterSavingsPotential(
                current_water_usage=Decimal("1200.00"),
                potential_savings=Decimal("300.00"),
                savings_percentage=25.0,
                cost_savings_per_year=Decimal("600.00"),
                implementation_cost=Decimal("2000.00"),
                payback_period_years=3.33
            ),
            confidence_score=0.9
        )
        
        # Test JSON serialization
        json_data = assessment.model_dump()
        assert json_data["drought_risk_level"] == "high"
        assert json_data["confidence_score"] == 0.9
        assert json_data["soil_moisture_status"]["moisture_level"] == "very_dry"
        assert json_data["water_savings_potential"]["savings_percentage"] == 25.0
        
        # Test JSON deserialization
        assessment_from_json = DroughtAssessment(**json_data)
        assert assessment_from_json.drought_risk_level == assessment.drought_risk_level
        assert assessment_from_json.confidence_score == assessment.confidence_score
        assert assessment_from_json.soil_moisture_status.moisture_level == assessment.soil_moisture_status.moisture_level


if __name__ == "__main__":
    pytest.main([__file__, "-v"])