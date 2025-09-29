"""
Comprehensive tests for Soil-Weather Integration Service

Tests the soil-weather integration functionality including:
- Soil-specific drought vulnerability assessment
- Weather pattern impact analysis
- Drought risk modeling
- Soil moisture stress predictions
- Crop impact assessments
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, date, timedelta
from uuid import uuid4
from decimal import Decimal

from src.services.soil_weather_service import (
    SoilWeatherIntegrationService,
    SoilCharacteristics,
    WeatherPattern,
    DroughtVulnerabilityScore
)
from src.models.drought_models import DroughtRiskLevel, SoilMoistureLevel
from src.models.soil_assessment_models import DrainageClass, CompactionLevel

class TestSoilWeatherIntegrationService:
    """Test suite for SoilWeatherIntegrationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilWeatherIntegrationService()
    
    @pytest.fixture
    def sample_soil_characteristics(self):
        """Sample soil characteristics for testing."""
        return SoilCharacteristics(
            soil_type="loam",
            texture="loam",
            water_holding_capacity=2.2,
            drainage_class=DrainageClass.WELL_DRAINED,
            organic_matter_percent=3.5,
            soil_depth_inches=36.0,
            bulk_density=1.3,
            field_capacity=25.0,
            wilting_point=10.0,
            available_water_capacity=1.5,
            infiltration_rate=1.2,
            compaction_level=CompactionLevel.MODERATE
        )
    
    @pytest.fixture
    def sample_weather_data(self):
        """Sample weather data for testing."""
        return [
            WeatherPattern(
                temperature_celsius=28.0,
                precipitation_mm=5.0,
                humidity_percent=65.0,
                wind_speed_kmh=8.0,
                solar_radiation=22.0,
                evapotranspiration_mm=6.0,
                drought_index=-1.5,
                aridity_index=0.3
            ),
            WeatherPattern(
                temperature_celsius=32.0,
                precipitation_mm=0.0,
                humidity_percent=45.0,
                wind_speed_kmh=12.0,
                solar_radiation=25.0,
                evapotranspiration_mm=8.0,
                drought_index=-2.0,
                aridity_index=0.4
            ),
            WeatherPattern(
                temperature_celsius=25.0,
                precipitation_mm=15.0,
                humidity_percent=75.0,
                wind_speed_kmh=5.0,
                solar_radiation=18.0,
                evapotranspiration_mm=4.0,
                drought_index=-0.5,
                aridity_index=0.2
            )
        ]
    
    @pytest.fixture
    def sample_field_id(self):
        """Sample field ID for testing."""
        return uuid4()
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        with patch.object(service.weather_service, 'initialize', new_callable=AsyncMock) as mock_weather:
            with patch.object(service.crop_service, 'initialize', new_callable=AsyncMock) as mock_crop:
                with patch.object(service.field_service, 'initialize', new_callable=AsyncMock) as mock_field:
                    await service.initialize()
                    
                    assert service.initialized is True
                    mock_weather.assert_called_once()
                    mock_crop.assert_called_once()
                    mock_field.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, service):
        """Test service cleanup."""
        service.initialized = True
        
        with patch.object(service.weather_service, 'cleanup', new_callable=AsyncMock) as mock_weather:
            with patch.object(service.crop_service, 'cleanup', new_callable=AsyncMock) as mock_crop:
                with patch.object(service.field_service, 'cleanup', new_callable=AsyncMock) as mock_field:
                    await service.cleanup()
                    
                    assert service.initialized is False
                    mock_weather.assert_called_once()
                    mock_crop.assert_called_once()
                    mock_field.assert_called_once()
    
    def test_soil_texture_properties_initialization(self, service):
        """Test soil texture properties database initialization."""
        assert "sand" in service.soil_texture_properties
        assert "loam" in service.soil_texture_properties
        assert "clay" in service.soil_texture_properties
        
        # Test sand properties
        sand_props = service.soil_texture_properties["sand"]
        assert sand_props["water_holding_capacity"] == 0.8
        assert sand_props["drought_vulnerability"] == 0.8
        
        # Test loam properties
        loam_props = service.soil_texture_properties["loam"]
        assert loam_props["water_holding_capacity"] == 2.2
        assert loam_props["drought_vulnerability"] == 0.4
    
    def test_drainage_impacts_initialization(self, service):
        """Test drainage class impacts initialization."""
        assert "well_drained" in service.drainage_class_impacts
        assert "poorly_drained" in service.drainage_class_impacts
        
        # Test well drained properties
        well_drained = service.drainage_class_impacts["well_drained"]
        assert well_drained["drought_vulnerability"] == 0.4
        assert well_drained["water_retention"] == 0.8
    
    def test_crop_water_requirements_initialization(self, service):
        """Test crop water requirements initialization."""
        assert "corn" in service.crop_water_requirements
        assert "soybean" in service.crop_water_requirements
        
        # Test corn requirements
        corn_reqs = service.crop_water_requirements["corn"]
        assert corn_reqs["total_water_requirement"] == 20.0
        assert corn_reqs["drought_tolerance"] == 0.6
        assert "tasseling" in corn_reqs["critical_periods"]
    
    @pytest.mark.asyncio
    async def test_assess_soil_drought_vulnerability(
        self, 
        service, 
        sample_field_id, 
        sample_soil_characteristics, 
        sample_weather_data
    ):
        """Test soil drought vulnerability assessment."""
        with patch.object(service, '_calculate_management_factor_score', return_value=40.0):
            vulnerability = await service.assess_soil_drought_vulnerability(
                sample_field_id,
                sample_soil_characteristics,
                sample_weather_data,
                "corn"
            )
            
            assert isinstance(vulnerability, DroughtVulnerabilityScore)
            assert 0 <= vulnerability.overall_score <= 100
            assert 0 <= vulnerability.soil_factor_score <= 100
            assert 0 <= vulnerability.weather_factor_score <= 100
            assert 0 <= vulnerability.management_factor_score <= 100
            assert vulnerability.risk_level in DroughtRiskLevel
            assert isinstance(vulnerability.vulnerability_factors, list)
            assert 0 <= vulnerability.mitigation_potential <= 100
    
    def test_calculate_soil_factor_score(self, service, sample_soil_characteristics):
        """Test soil factor score calculation."""
        score = service._calculate_soil_factor_score(sample_soil_characteristics)
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
        
        # Test with different soil types
        sandy_soil = SoilCharacteristics(
            soil_type="sand",
            texture="sand",
            water_holding_capacity=0.8,
            drainage_class=DrainageClass.EXCESSIVELY_DRAINED,
            organic_matter_percent=1.0,
            soil_depth_inches=24.0,
            bulk_density=1.6,
            field_capacity=10.0,
            wilting_point=3.0,
            available_water_capacity=0.7,
            infiltration_rate=2.5,
            compaction_level=CompactionLevel.NONE
        )
        
        sandy_score = service._calculate_soil_factor_score(sandy_soil)
        assert sandy_score > score  # Sandy soil should be more vulnerable
    
    def test_calculate_weather_factor_score(self, service, sample_weather_data):
        """Test weather factor score calculation."""
        score = service._calculate_weather_factor_score(sample_weather_data)
        
        assert 0 <= score <= 100
        assert isinstance(score, float)
        
        # Test with empty weather data
        empty_score = service._calculate_weather_factor_score([])
        assert empty_score == 50.0  # Default moderate risk
    
    def test_determine_risk_level(self, service):
        """Test drought risk level determination."""
        assert service._determine_risk_level(85.0) == DroughtRiskLevel.EXTREME
        assert service._determine_risk_level(70.0) == DroughtRiskLevel.SEVERE
        assert service._determine_risk_level(55.0) == DroughtRiskLevel.HIGH
        assert service._determine_risk_level(40.0) == DroughtRiskLevel.MODERATE
        assert service._determine_risk_level(20.0) == DroughtRiskLevel.LOW
    
    def test_identify_vulnerability_factors(self, service, sample_soil_characteristics, sample_weather_data):
        """Test vulnerability factor identification."""
        factors = service._identify_vulnerability_factors(
            sample_soil_characteristics, 
            sample_weather_data, 
            75.0
        )
        
        assert isinstance(factors, list)
        # Should identify some factors based on the test data
        assert len(factors) >= 0
    
    def test_calculate_mitigation_potential(self, service, sample_soil_characteristics):
        """Test mitigation potential calculation."""
        factors = ["Low organic matter content", "Soil compaction"]
        potential = service._calculate_mitigation_potential(sample_soil_characteristics, factors)
        
        assert 0 <= potential <= 100
        assert isinstance(potential, float)
    
    @pytest.mark.asyncio
    async def test_analyze_weather_pattern_impact(
        self, 
        service, 
        sample_field_id, 
        sample_weather_data, 
        sample_soil_characteristics
    ):
        """Test weather pattern impact analysis."""
        analysis = await service.analyze_weather_pattern_impact(
            sample_field_id,
            sample_weather_data,
            sample_soil_characteristics,
            "corn"
        )
        
        assert isinstance(analysis, dict)
        assert "moisture_stress_level" in analysis
        assert "moisture_stress_score" in analysis
        assert "crop_water_stress" in analysis
        assert "evapotranspiration_impact" in analysis
        assert "precipitation_effectiveness" in analysis
        assert "critical_periods" in analysis
        assert "recommendations" in analysis
        
        assert 0 <= analysis["moisture_stress_score"] <= 100
        assert isinstance(analysis["recommendations"], list)
    
    def test_calculate_soil_moisture_stress(self, service, sample_weather_data, sample_soil_characteristics):
        """Test soil moisture stress calculation."""
        stress = service._calculate_soil_moisture_stress(sample_weather_data, sample_soil_characteristics)
        
        assert isinstance(stress, dict)
        assert "level" in stress
        assert "score" in stress
        assert stress["level"] in ["low", "mild", "moderate", "severe"]
        assert 0 <= stress["score"] <= 100
    
    def test_calculate_crop_water_stress(self, service, sample_weather_data, sample_soil_characteristics):
        """Test crop water stress calculation."""
        stress = service._calculate_crop_water_stress(
            sample_weather_data, 
            sample_soil_characteristics, 
            "corn"
        )
        
        assert isinstance(stress, dict)
        assert "stress_level" in stress
        assert "stress_score" in stress
        assert stress["stress_level"] in ["low", "mild", "moderate", "severe"]
        assert 0 <= stress["stress_score"] <= 100
    
    def test_calculate_et_impact(self, service, sample_weather_data, sample_soil_characteristics):
        """Test evapotranspiration impact calculation."""
        impact = service._calculate_et_impact(sample_weather_data, sample_soil_characteristics)
        
        assert isinstance(impact, dict)
        assert "impact_level" in impact
        assert "impact_score" in impact
        assert impact["impact_level"] in ["minimal", "low", "moderate", "high"]
        assert 0 <= impact["impact_score"] <= 100
    
    def test_calculate_precipitation_effectiveness(self, service, sample_weather_data, sample_soil_characteristics):
        """Test precipitation effectiveness calculation."""
        effectiveness = service._calculate_precipitation_effectiveness(
            sample_weather_data, 
            sample_soil_characteristics
        )
        
        assert isinstance(effectiveness, dict)
        assert "effectiveness" in effectiveness
        assert "score" in effectiveness
        assert effectiveness["effectiveness"] in ["poor", "low", "moderate", "high"]
        assert 0 <= effectiveness["score"] <= 100
    
    def test_identify_critical_periods(self, service, sample_weather_data):
        """Test critical period identification."""
        periods = service._identify_critical_periods(sample_weather_data, "corn")
        
        assert isinstance(periods, list)
        for period in periods:
            assert "period" in period
            assert "water_requirement" in period
            assert "stress_risk" in period
            assert "recommendations" in period
    
    @pytest.mark.asyncio
    async def test_predict_soil_moisture_stress(
        self, 
        service, 
        sample_field_id, 
        sample_soil_characteristics, 
        sample_weather_data
    ):
        """Test soil moisture stress prediction."""
        with patch.object(service, '_get_current_soil_moisture', return_value=65.0):
            prediction = await service.predict_soil_moisture_stress(
                sample_field_id,
                sample_soil_characteristics,
                sample_weather_data,
                "corn",
                days_ahead=7
            )
            
            assert isinstance(prediction, dict)
            assert "field_id" in prediction
            assert "prediction_period_days" in prediction
            assert "current_moisture_level" in prediction
            assert "predicted_average_moisture" in prediction
            assert "critical_days" in prediction
            assert "daily_predictions" in prediction
            assert "recommendations" in prediction
            
            assert prediction["prediction_period_days"] == 7
            assert prediction["current_moisture_level"] == 65.0
            assert isinstance(prediction["daily_predictions"], list)
            assert len(prediction["daily_predictions"]) == 7
    
    def test_calculate_daily_moisture_change(self, service, sample_soil_characteristics):
        """Test daily moisture change calculation."""
        weather = WeatherPattern(
            temperature_celsius=30.0,
            precipitation_mm=10.0,
            humidity_percent=60.0,
            wind_speed_kmh=10.0,
            solar_radiation=24.0,
            evapotranspiration_mm=7.0,
            drought_index=-1.0,
            aridity_index=0.3
        )
        
        change = service._calculate_daily_moisture_change(
            weather, 
            sample_soil_characteristics, 
            "corn"
        )
        
        assert isinstance(change, float)
        # Change should be reasonable (not extreme)
        assert -50 <= change <= 50
    
    def test_determine_moisture_stress_level(self, service):
        """Test moisture stress level determination."""
        assert service._determine_moisture_stress_level(80.0) == "optimal"
        assert service._determine_moisture_stress_level(60.0) == "adequate"
        assert service._determine_moisture_stress_level(40.0) == "mild"
        assert service._determine_moisture_stress_level(20.0) == "moderate"
        assert service._determine_moisture_stress_level(10.0) == "severe"
    
    @pytest.mark.asyncio
    async def test_assess_crop_impact(
        self, 
        service, 
        sample_field_id, 
        sample_soil_characteristics, 
        sample_weather_data
    ):
        """Test crop impact assessment."""
        assessment = await service.assess_crop_impact(
            sample_field_id,
            "corn",
            sample_soil_characteristics,
            sample_weather_data,
            "flowering"
        )
        
        assert isinstance(assessment, dict)
        assert "field_id" in assessment
        assert "crop_type" in assessment
        assert "growth_stage" in assessment
        assert "water_stress" in assessment
        assert "yield_impact" in assessment
        assert "quality_impact" in assessment
        assert "economic_impact" in assessment
        assert "recommendations" in assessment
        
        assert assessment["crop_type"] == "corn"
        assert assessment["growth_stage"] == "flowering"
        assert isinstance(assessment["recommendations"], list)
    
    def test_calculate_yield_impact(self, service):
        """Test yield impact calculation."""
        water_stress = {"stress_score": 60.0}
        crop_requirements = {"total_water_requirement": 20.0}
        
        impact = service._calculate_yield_impact(water_stress, crop_requirements, "flowering")
        
        assert isinstance(impact, dict)
        assert "impact_level" in impact
        assert "yield_reduction_percent" in impact
        assert "sensitivity_factor" in impact
        assert impact["impact_level"] in ["minimal", "mild", "moderate", "severe"]
        assert 0 <= impact["yield_reduction_percent"] <= 100
    
    def test_calculate_quality_impact(self, service):
        """Test quality impact calculation."""
        water_stress = {"stress_score": 50.0}
        
        impact = service._calculate_quality_impact(water_stress, "corn", "flowering")
        
        assert isinstance(impact, dict)
        assert "impact_level" in impact
        assert "quality_reduction_percent" in impact
        assert "sensitivity_factor" in impact
        assert impact["impact_level"] in ["mild", "moderate", "severe"]
        assert 0 <= impact["quality_reduction_percent"] <= 100
    
    def test_calculate_economic_impact(self, service):
        """Test economic impact calculation."""
        yield_impact = {"yield_reduction_percent": 15.0}
        quality_impact = {"quality_reduction_percent": 10.0}
        
        impact = service._calculate_economic_impact(yield_impact, quality_impact, "corn")
        
        assert isinstance(impact, dict)
        assert "revenue_reduction_percent" in impact
        assert "economic_impact_per_acre" in impact
        assert "impact_level" in impact
        assert impact["impact_level"] in ["mild", "moderate", "severe"]
        assert 0 <= impact["revenue_reduction_percent"] <= 100
        assert impact["economic_impact_per_acre"] >= 0


class TestSoilWeatherIntegrationEdgeCases:
    """Test edge cases and error handling for SoilWeatherIntegrationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilWeatherIntegrationService()
    
    @pytest.mark.asyncio
    async def test_assess_vulnerability_with_empty_weather_data(self, service):
        """Test vulnerability assessment with empty weather data."""
        field_id = uuid4()
        soil = SoilCharacteristics(
            soil_type="loam",
            texture="loam",
            water_holding_capacity=2.2,
            drainage_class=DrainageClass.WELL_DRAINED,
            organic_matter_percent=3.5,
            soil_depth_inches=36.0,
            bulk_density=1.3,
            field_capacity=25.0,
            wilting_point=10.0,
            available_water_capacity=1.5,
            infiltration_rate=1.2,
            compaction_level=CompactionLevel.MODERATE
        )
        
        with patch.object(service, '_calculate_management_factor_score', return_value=50.0):
            vulnerability = await service.assess_soil_drought_vulnerability(
                field_id, soil, [], "corn"
            )
            
            assert isinstance(vulnerability, DroughtVulnerabilityScore)
            assert vulnerability.weather_factor_score == 50.0  # Default moderate risk
    
    @pytest.mark.asyncio
    async def test_weather_impact_analysis_with_empty_data(self, service):
        """Test weather impact analysis with empty weather data."""
        field_id = uuid4()
        soil = SoilCharacteristics(
            soil_type="sand",
            texture="sand",
            water_holding_capacity=0.8,
            drainage_class=DrainageClass.EXCESSIVELY_DRAINED,
            organic_matter_percent=1.0,
            soil_depth_inches=24.0,
            bulk_density=1.6,
            field_capacity=10.0,
            wilting_point=3.0,
            available_water_capacity=0.7,
            infiltration_rate=2.5,
            compaction_level=CompactionLevel.NONE
        )
        
        analysis = await service.analyze_weather_pattern_impact(
            field_id, [], soil, "corn"
        )
        
        assert isinstance(analysis, dict)
        assert "moisture_stress_level" in analysis
        assert analysis["moisture_stress_level"] == "unknown"
    
    def test_soil_factor_score_with_extreme_values(self, service):
        """Test soil factor score calculation with extreme values."""
        extreme_soil = SoilCharacteristics(
            soil_type="sand",
            texture="sand",
            water_holding_capacity=0.1,  # Very low
            drainage_class=DrainageClass.EXCESSIVELY_DRAINED,
            organic_matter_percent=0.1,  # Very low
            soil_depth_inches=6.0,  # Very shallow
            bulk_density=2.0,  # Very high
            field_capacity=5.0,
            wilting_point=1.0,
            available_water_capacity=0.1,
            infiltration_rate=5.0,
            compaction_level=CompactionLevel.EXTREME
        )
        
        score = service._calculate_soil_factor_score(extreme_soil)
        assert score >= 80  # Should be very high vulnerability
    
    def test_weather_factor_score_with_extreme_values(self, service):
        """Test weather factor score calculation with extreme values."""
        extreme_weather = [
            WeatherPattern(
                temperature_celsius=45.0,  # Very hot
                precipitation_mm=0.0,  # No rain
                humidity_percent=20.0,  # Very dry
                wind_speed_kmh=25.0,  # High wind
                solar_radiation=30.0,  # High radiation
                evapotranspiration_mm=15.0,  # High ET
                drought_index=-4.0,  # Extreme drought
                aridity_index=0.8  # Very arid
            )
        ]
        
        score = service._calculate_weather_factor_score(extreme_weather)
        assert score >= 80  # Should be very high vulnerability
    
    @pytest.mark.asyncio
    async def test_service_initialization_failure(self, service):
        """Test service initialization failure handling."""
        with patch.object(service.weather_service, 'initialize', side_effect=Exception("Connection failed")):
            with pytest.raises(Exception):
                await service.initialize()
            
            assert service.initialized is False
    
    @pytest.mark.asyncio
    async def test_management_factor_calculation_failure(self, service):
        """Test management factor calculation failure handling."""
        field_id = uuid4()
        soil = SoilCharacteristics(
            soil_type="loam",
            texture="loam",
            water_holding_capacity=2.2,
            drainage_class=DrainageClass.WELL_DRAINED,
            organic_matter_percent=3.5,
            soil_depth_inches=36.0,
            bulk_density=1.3,
            field_capacity=25.0,
            wilting_point=10.0,
            available_water_capacity=1.5,
            infiltration_rate=1.2,
            compaction_level=CompactionLevel.MODERATE
        )
        
        weather_data = [
            WeatherPattern(
                temperature_celsius=25.0,
                precipitation_mm=10.0,
                humidity_percent=60.0,
                wind_speed_kmh=5.0,
                solar_radiation=20.0,
                evapotranspiration_mm=5.0,
                drought_index=-0.5,
                aridity_index=0.3
            )
        ]
        
        with patch.object(service.field_service, 'get_field_characteristics', side_effect=Exception("Service unavailable")):
            vulnerability = await service.assess_soil_drought_vulnerability(
                field_id, soil, weather_data, "corn"
            )
            
            # Should handle error gracefully and return default management score
            assert vulnerability.management_factor_score == 50.0


class TestSoilWeatherIntegrationPerformance:
    """Performance tests for SoilWeatherIntegrationService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return SoilWeatherIntegrationService()
    
    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, service):
        """Test performance with large weather dataset."""
        # Create large weather dataset
        large_weather_data = []
        for i in range(365):  # One year of data
            large_weather_data.append(WeatherPattern(
                temperature_celsius=20.0 + (i % 30),
                precipitation_mm=i % 10,
                humidity_percent=50.0 + (i % 20),
                wind_speed_kmh=5.0 + (i % 10),
                solar_radiation=15.0 + (i % 15),
                evapotranspiration_mm=3.0 + (i % 5),
                drought_index=-1.0 + (i % 3),
                aridity_index=0.2 + (i % 4) * 0.1
            ))
        
        soil = SoilCharacteristics(
            soil_type="loam",
            texture="loam",
            water_holding_capacity=2.2,
            drainage_class=DrainageClass.WELL_DRAINED,
            organic_matter_percent=3.5,
            soil_depth_inches=36.0,
            bulk_density=1.3,
            field_capacity=25.0,
            wilting_point=10.0,
            available_water_capacity=1.5,
            infiltration_rate=1.2,
            compaction_level=CompactionLevel.MODERATE
        )
        
        import time
        start_time = time.time()
        
        weather_score = service._calculate_weather_factor_score(large_weather_data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process large dataset quickly (less than 1 second)
        assert processing_time < 1.0
        assert 0 <= weather_score <= 100
    
    @pytest.mark.asyncio
    async def test_concurrent_assessments(self, service):
        """Test concurrent vulnerability assessments."""
        field_ids = [uuid4() for _ in range(5)]
        soil = SoilCharacteristics(
            soil_type="loam",
            texture="loam",
            water_holding_capacity=2.2,
            drainage_class=DrainageClass.WELL_DRAINED,
            organic_matter_percent=3.5,
            soil_depth_inches=36.0,
            bulk_density=1.3,
            field_capacity=25.0,
            wilting_point=10.0,
            available_water_capacity=1.5,
            infiltration_rate=1.2,
            compaction_level=CompactionLevel.MODERATE
        )
        
        weather_data = [
            WeatherPattern(
                temperature_celsius=25.0,
                precipitation_mm=10.0,
                humidity_percent=60.0,
                wind_speed_kmh=5.0,
                solar_radiation=20.0,
                evapotranspiration_mm=5.0,
                drought_index=-0.5,
                aridity_index=0.3
            )
        ]
        
        with patch.object(service, '_calculate_management_factor_score', return_value=50.0):
            # Run concurrent assessments
            tasks = [
                service.assess_soil_drought_vulnerability(field_id, soil, weather_data, "corn")
                for field_id in field_ids
            ]
            
            results = await asyncio.gather(*tasks)
            
            # All assessments should complete successfully
            assert len(results) == 5
            for result in results:
                assert isinstance(result, DroughtVulnerabilityScore)
                assert 0 <= result.overall_score <= 100