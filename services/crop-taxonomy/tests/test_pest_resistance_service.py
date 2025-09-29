"""
Tests for Pest Resistance Analysis Service

Comprehensive test suite for pest resistance analysis, recommendations, and integrated pest management.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date, datetime, timedelta
from uuid import uuid4

from src.services.pest_resistance_service import PestResistanceAnalysisService
from src.models.pest_resistance_models import (
    PestResistanceRequest,
    PestResistanceResponse,
    PestType,
    PestSeverity,
    PestRiskLevel,
    DataSource,
    ResistanceMechanism,
    ResistanceDurability,
    IPMStrategy
)


class TestPestResistanceAnalysisService:
    """Test suite for PestResistanceAnalysisService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return PestResistanceAnalysisService()

    @pytest.fixture
    def sample_request(self):
        """Create sample pest resistance request."""
        return PestResistanceRequest(
            coordinates=(40.0, -95.0),
            region_radius_km=50.0,
            crop_type="corn",
            analysis_period_days=30,
            include_forecast=True,
            include_historical=True,
            include_management_recommendations=True,
            include_variety_recommendations=True,
            include_timing_guidance=True,
            include_resistance_analysis=True
        )

    @pytest.fixture
    def sample_variety_request(self):
        """Create sample variety analysis request."""
        return PestResistanceRequest(
            coordinates=(40.0, -95.0),
            region_radius_km=50.0,
            crop_type="corn",
            variety_ids=[uuid4(), uuid4()],
            analysis_period_days=30,
            include_forecast=False,
            include_historical=False,
            include_management_recommendations=False,
            include_variety_recommendations=True,
            include_timing_guidance=False,
            include_resistance_analysis=True
        )

    def test_service_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'pest_knowledge')
        assert hasattr(service, 'data_providers')
        assert 'corn' in service.pest_knowledge
        assert 'soybean' in service.pest_knowledge
        assert 'wheat' in service.pest_knowledge

    def test_pest_knowledge_structure(self, service):
        """Test pest knowledge base structure."""
        corn_pests = service.pest_knowledge['corn']
        assert 'corn_rootworm' in corn_pests
        assert 'corn_borer' in corn_pests
        assert 'armyworm' in corn_pests
        
        # Test pest data structure
        rootworm_data = corn_pests['corn_rootworm']
        assert rootworm_data['pest_id'] == 'corn_rootworm'
        assert rootworm_data['pest_name'] == 'Corn Rootworm'
        assert rootworm_data['pest_type'] == PestType.ROOT_WORM
        assert 'life_stages' in rootworm_data
        assert 'damage_symptoms' in rootworm_data
        assert 'environmental_factors' in rootworm_data

    @pytest.mark.asyncio
    async def test_analyze_pest_resistance_basic(self, service, sample_request):
        """Test basic pest resistance analysis."""
        response = await service.analyze_pest_resistance(sample_request)
        
        assert isinstance(response, PestResistanceResponse)
        assert response.request_id is not None
        assert response.analysis_location == sample_request.coordinates
        assert response.analysis_region is not None
        assert response.overall_risk_level is not None
        assert response.data_quality_score >= 0.0
        assert response.data_quality_score <= 1.0
        assert response.processing_time_ms > 0

    @pytest.mark.asyncio
    async def test_analyze_pest_resistance_with_varieties(self, service, sample_variety_request):
        """Test pest resistance analysis with variety analysis."""
        response = await service.analyze_pest_resistance(sample_variety_request)
        
        assert isinstance(response, PestResistanceResponse)
        assert response.variety_analysis is not None
        assert len(response.variety_analysis) > 0
        assert response.recommended_varieties is not None
        assert len(response.recommended_varieties) > 0
        assert response.resistance_analysis is not None

    @pytest.mark.asyncio
    async def test_regional_pest_pressure(self, service):
        """Test regional pest pressure data retrieval."""
        coordinates = (40.0, -95.0)
        radius_km = 50.0
        crop_type = "corn"
        analysis_period_days = 30
        
        regional_pressure = await service._get_regional_pest_pressure(
            coordinates, radius_km, crop_type, analysis_period_days
        )
        
        assert regional_pressure is not None
        assert regional_pressure.coordinates == coordinates
        assert regional_pressure.radius_km == radius_km
        assert regional_pressure.region_id is not None
        assert regional_pressure.region_name is not None
        assert len(regional_pressure.pests) > 0
        assert regional_pressure.overall_risk_level is not None

    @pytest.mark.asyncio
    async def test_variety_pest_resistance_analysis(self, service):
        """Test variety-specific pest resistance analysis."""
        crop_type = "corn"
        variety_ids = [uuid4(), uuid4()]
        
        # Create mock regional pressure
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm"),
            MagicMock(pest_id="corn_borer", pest_name="Corn Borer")
        ]
        
        variety_analysis = await service._analyze_variety_pest_resistance(
            crop_type, variety_ids, regional_pressure
        )
        
        assert variety_analysis is not None
        assert len(variety_analysis) == len(variety_ids)
        
        for analysis in variety_analysis:
            assert analysis.variety_id in variety_ids
            assert analysis.variety_name is not None
            assert analysis.overall_resistance_score >= 0.0
            assert analysis.overall_resistance_score <= 1.0
            assert analysis.pest_risk_level is not None
            assert analysis.suitability_score >= 0.0
            assert analysis.suitability_score <= 1.0

    @pytest.mark.asyncio
    async def test_pest_resistant_varieties(self, service):
        """Test pest-resistant variety recommendations."""
        crop_type = "corn"
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        
        recommendations = await service._get_pest_resistant_varieties(
            crop_type, regional_pressure
        )
        
        assert recommendations is not None
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert recommendation.variety_id is not None
            assert recommendation.variety_name is not None
            assert recommendation.recommendation_score >= 0.0
            assert recommendation.recommendation_score <= 1.0
            assert recommendation.recommendation_reason is not None
            assert len(recommendation.pest_advantages) > 0

    @pytest.mark.asyncio
    async def test_management_recommendations(self, service):
        """Test pest management recommendations generation."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        crop_type = "corn"
        
        recommendations = await service._generate_management_recommendations(
            regional_pressure, crop_type
        )
        
        assert recommendations is not None
        assert recommendations.management_strategy is not None
        assert recommendations.priority_level is not None
        assert recommendations.ipm_strategy is not None
        assert len(recommendations.cultural_practices) > 0
        assert len(recommendations.chemical_recommendations) > 0
        assert len(recommendations.biological_options) > 0
        assert len(recommendations.monitoring_recommendations) > 0
        assert len(recommendations.resistance_management) > 0

    @pytest.mark.asyncio
    async def test_timing_guidance(self, service):
        """Test timing guidance generation."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        crop_type = "corn"
        
        timing_guidance = await service._generate_timing_guidance(
            regional_pressure, crop_type
        )
        
        assert timing_guidance is not None
        assert len(timing_guidance.critical_periods) > 0
        assert len(timing_guidance.optimal_timing) > 0
        assert len(timing_guidance.monitoring_schedule) > 0
        assert len(timing_guidance.action_thresholds) > 0
        assert len(timing_guidance.seasonal_calendar) > 0

    @pytest.mark.asyncio
    async def test_resistance_durability_analysis(self, service):
        """Test resistance durability analysis."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        crop_type = "corn"
        
        resistance_analysis = await service._analyze_resistance_durability(
            regional_pressure, crop_type
        )
        
        assert resistance_analysis is not None
        assert len(resistance_analysis.resistance_durability) > 0
        assert len(resistance_analysis.durability_factors) > 0
        assert len(resistance_analysis.resistance_stacking) > 0
        assert len(resistance_analysis.stacking_benefits) > 0
        assert resistance_analysis.refuge_requirements is not None
        assert len(resistance_analysis.management_implications) > 0

    @pytest.mark.asyncio
    async def test_pest_forecast(self, service):
        """Test pest pressure forecast generation."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        forecast_period_days = 30
        
        forecast = await service._generate_pest_forecast(
            regional_pressure, forecast_period_days
        )
        
        assert forecast is not None
        assert forecast.forecast_period_days == forecast_period_days
        assert forecast.forecast_date is not None
        assert len(forecast.predicted_pests) > 0
        assert forecast.overall_risk_trend is not None
        assert forecast.forecast_confidence >= 0.0
        assert forecast.forecast_confidence <= 1.0

    @pytest.mark.asyncio
    async def test_historical_trends(self, service):
        """Test historical pest trends analysis."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        crop_type = "corn"
        
        trends = await service._analyze_historical_trends(
            regional_pressure, crop_type
        )
        
        assert trends is not None
        assert trends.analysis_period_years > 0
        assert len(trends.trend_data) > 0
        assert trends.overall_trend_direction is not None
        assert trends.trend_significance is not None
        assert len(trends.seasonal_patterns) > 0
        assert len(trends.long_term_changes) > 0

    def test_data_quality_calculation(self, service):
        """Test data quality score calculation."""
        # Create mock regional pressure with different confidence scores
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(confidence_score=0.9, data_source=DataSource.UNIVERSITY_EXTENSION),
            MagicMock(confidence_score=0.7, data_source=DataSource.USDA_SURVEY),
            MagicMock(confidence_score=0.8, data_source=DataSource.RESEARCH_TRIAL)
        ]
        
        quality_score = service._calculate_data_quality_score(regional_pressure)
        
        assert quality_score >= 0.0
        assert quality_score <= 1.0
        assert quality_score > 0.5  # Should be high with good confidence scores

    def test_confidence_level_determination(self, service):
        """Test confidence level determination."""
        assert service._determine_confidence_level(0.9) == "high"
        assert service._determine_confidence_level(0.7) == "moderate"
        assert service._determine_confidence_level(0.4) == "low"

    def test_overall_risk_level_calculation(self, service):
        """Test overall risk level calculation."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(current_severity=PestSeverity.HIGH, risk_level=PestRiskLevel.HIGH),
            MagicMock(current_severity=PestSeverity.MODERATE, risk_level=PestRiskLevel.MODERATE)
        ]
        
        risk_level = service._calculate_overall_risk_level(regional_pressure)
        
        assert risk_level in [PestRiskLevel.LOW, PestRiskLevel.MODERATE, PestRiskLevel.HIGH, PestRiskLevel.VERY_HIGH, PestRiskLevel.CRITICAL]

    def test_severity_to_score_conversion(self, service):
        """Test severity to score conversion."""
        assert service._severity_to_score(PestSeverity.NONE) == 0.0
        assert service._severity_to_score(PestSeverity.TRACE) == 0.2
        assert service._severity_to_score(PestSeverity.LOW) == 0.4
        assert service._severity_to_score(PestSeverity.MODERATE) == 0.6
        assert service._severity_to_score(PestSeverity.HIGH) == 0.8
        assert service._severity_to_score(PestSeverity.SEVERE) == 1.0

    def test_risk_level_to_score_conversion(self, service):
        """Test risk level to score conversion."""
        assert service._risk_level_to_score(PestRiskLevel.VERY_LOW) == 0.1
        assert service._risk_level_to_score(PestRiskLevel.LOW) == 0.3
        assert service._risk_level_to_score(PestRiskLevel.MODERATE) == 0.5
        assert service._risk_level_to_score(PestRiskLevel.HIGH) == 0.7
        assert service._risk_level_to_score(PestRiskLevel.VERY_HIGH) == 0.9
        assert service._risk_level_to_score(PestRiskLevel.CRITICAL) == 1.0

    def test_score_to_risk_level_conversion(self, service):
        """Test score to risk level conversion."""
        assert service._score_to_risk_level(0.95) == PestRiskLevel.CRITICAL
        assert service._score_to_risk_level(0.8) == PestRiskLevel.HIGH
        assert service._score_to_risk_level(0.6) == PestRiskLevel.MODERATE
        assert service._score_to_risk_level(0.4) == PestRiskLevel.LOW
        assert service._score_to_risk_level(0.2) == PestRiskLevel.VERY_LOW

    def test_active_pests_filtering(self, service):
        """Test active pests filtering."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(current_severity=PestSeverity.HIGH),
            MagicMock(current_severity=PestSeverity.NONE),
            MagicMock(current_severity=PestSeverity.MODERATE)
        ]
        
        active_pests = service._get_active_pests(regional_pressure)
        
        assert len(active_pests) == 2  # Only HIGH and MODERATE severity pests
        assert all(pest.current_severity != PestSeverity.NONE for pest in active_pests)

    def test_emerging_threats_filtering(self, service):
        """Test emerging threats filtering."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(trend_direction="increasing"),
            MagicMock(trend_direction="stable"),
            MagicMock(trend_direction="increasing")
        ]
        
        emerging_threats = service._get_emerging_threats(regional_pressure)
        
        assert len(emerging_threats) == 2  # Only increasing trend pests
        assert all(pest.trend_direction == "increasing" for pest in emerging_threats)

    def test_data_sources_extraction(self, service):
        """Test data sources extraction."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(data_source=DataSource.UNIVERSITY_EXTENSION),
            MagicMock(data_source=DataSource.USDA_SURVEY),
            MagicMock(data_source=DataSource.UNIVERSITY_EXTENSION)  # Duplicate
        ]
        
        data_sources = service._get_data_sources(regional_pressure)
        
        assert len(data_sources) == 2  # Should remove duplicates
        assert DataSource.UNIVERSITY_EXTENSION in data_sources
        assert DataSource.USDA_SURVEY in data_sources

    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling in analysis."""
        # Test with invalid coordinates
        invalid_request = PestResistanceRequest(
            coordinates=(200.0, -95.0),  # Invalid latitude
            region_radius_km=50.0,
            crop_type="corn",
            analysis_period_days=30
        )
        
        # Should not raise exception, but handle gracefully
        response = await service.analyze_pest_resistance(invalid_request)
        assert response is not None

    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_request):
        """Test that analysis completes within performance requirements."""
        import time
        
        start_time = time.time()
        response = await service.analyze_pest_resistance(sample_request)
        elapsed_time = time.time() - start_time
        
        # Should complete within 5 seconds (generous for testing)
        assert elapsed_time < 5.0
        assert response.processing_time_ms < 5000

    @pytest.mark.asyncio
    async def test_crop_type_coverage(self, service):
        """Test analysis for different crop types."""
        crop_types = ["corn", "soybean", "wheat"]
        
        for crop_type in crop_types:
            request = PestResistanceRequest(
                coordinates=(40.0, -95.0),
                region_radius_km=50.0,
                crop_type=crop_type,
                analysis_period_days=30
            )
            
            response = await service.analyze_pest_resistance(request)
            assert response is not None
            assert response.analysis_region is not None
            assert len(response.analysis_region.pests) > 0

    @pytest.mark.asyncio
    async def test_analysis_period_variations(self, service):
        """Test analysis with different time periods."""
        periods = [7, 30, 90, 365]
        
        for period in periods:
            request = PestResistanceRequest(
                coordinates=(40.0, -95.0),
                region_radius_km=50.0,
                crop_type="corn",
                analysis_period_days=period
            )
            
            response = await service.analyze_pest_resistance(request)
            assert response is not None
            assert response.analysis_period[1] - response.analysis_period[0] == timedelta(days=period)


class TestPestResistanceModels:
    """Test suite for pest resistance models."""

    def test_pest_resistance_request_validation(self):
        """Test PestResistanceRequest model validation."""
        # Valid request
        request = PestResistanceRequest(
            coordinates=(40.0, -95.0),
            region_radius_km=50.0,
            crop_type="corn",
            analysis_period_days=30
        )
        assert request.coordinates == (40.0, -95.0)
        assert request.region_radius_km == 50.0
        assert request.crop_type == "corn"
        assert request.analysis_period_days == 30

    def test_pest_resistance_response_structure(self):
        """Test PestResistanceResponse model structure."""
        from src.models.pest_resistance_models import PestResistanceResponse
        
        response = PestResistanceResponse(
            request_id="test-123",
            analysis_period=(date.today(), date.today() + timedelta(days=30)),
            analysis_location=(40.0, -95.0),
            analysis_region=MagicMock(),
            overall_risk_level=PestRiskLevel.MODERATE,
            processing_time_ms=100.0
        )
        
        assert response.request_id == "test-123"
        assert response.overall_risk_level == PestRiskLevel.MODERATE
        assert response.processing_time_ms == 100.0

    def test_pest_type_enum(self):
        """Test PestType enum values."""
        assert PestType.INSECT == "insect"
        assert PestType.CORN_BORER == "corn_borer"
        assert PestType.ROOT_WORM == "root_worm"
        assert PestType.ARMYWORM == "armyworm"

    def test_pest_severity_enum(self):
        """Test PestSeverity enum values."""
        assert PestSeverity.NONE == "none"
        assert PestSeverity.LOW == "low"
        assert PestSeverity.MODERATE == "moderate"
        assert PestSeverity.HIGH == "high"
        assert PestSeverity.SEVERE == "severe"

    def test_pest_risk_level_enum(self):
        """Test PestRiskLevel enum values."""
        assert PestRiskLevel.VERY_LOW == "very_low"
        assert PestRiskLevel.LOW == "low"
        assert PestRiskLevel.MODERATE == "moderate"
        assert PestRiskLevel.HIGH == "high"
        assert PestRiskLevel.VERY_HIGH == "very_high"
        assert PestRiskLevel.CRITICAL == "critical"

    def test_resistance_mechanism_enum(self):
        """Test ResistanceMechanism enum values."""
        assert ResistanceMechanism.ANTIBIOSIS == "antibiosis"
        assert ResistanceMechanism.ANTIXENOSIS == "antixenosis"
        assert ResistanceMechanism.TOLERANCE == "tolerance"
        assert ResistanceMechanism.SYSTEMIC == "systemic"

    def test_resistance_durability_enum(self):
        """Test ResistanceDurability enum values."""
        assert ResistanceDurability.HIGH == "high"
        assert ResistanceDurability.MODERATE == "moderate"
        assert ResistanceDurability.LOW == "low"
        assert ResistanceDurability.VARIABLE == "variable"

    def test_ipm_strategy_enum(self):
        """Test IPMStrategy enum values."""
        assert IPMStrategy.PREVENTIVE == "preventive"
        assert IPMStrategy.SUPPRESSIVE == "suppressive"
        assert IPMStrategy.CURATIVE == "curative"
        assert IPMStrategy.COMBINED == "combined"

    def test_data_source_enum(self):
        """Test DataSource enum values."""
        assert DataSource.UNIVERSITY_EXTENSION == "university_extension"
        assert DataSource.USDA_SURVEY == "usda_survey"
        assert DataSource.FIELD_OBSERVATION == "field_observation"
        assert DataSource.RESEARCH_TRIAL == "research_trial"


# Agricultural validation tests
class TestAgriculturalValidation:
    """Tests for agricultural accuracy and domain validation."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return PestResistanceAnalysisService()

    @pytest.mark.asyncio
    async def test_corn_belt_pest_accuracy(self, service):
        """Test accuracy for major corn belt pests."""
        # Iowa coordinates - should include corn rootworm, corn borer, armyworm
        request = PestResistanceRequest(
            coordinates=(41.5868, -93.6250),  # Iowa
            region_radius_km=50.0,
            crop_type="corn",
            analysis_period_days=30
        )
        
        response = await service.analyze_pest_resistance(request)
        
        # Should include major corn pests
        pest_names = [pest.pest_name for pest in response.analysis_region.pests]
        assert any("rootworm" in name.lower() for name in pest_names)
        assert any("borer" in name.lower() for name in pest_names)

    @pytest.mark.asyncio
    async def test_soybean_pest_accuracy(self, service):
        """Test accuracy for major soybean pests."""
        # Illinois coordinates - should include soybean aphid, bean leaf beetle
        request = PestResistanceRequest(
            coordinates=(40.0, -89.0),  # Illinois
            region_radius_km=50.0,
            crop_type="soybean",
            analysis_period_days=30
        )
        
        response = await service.analyze_pest_resistance(request)
        
        # Should include major soybean pests
        pest_names = [pest.pest_name for pest in response.analysis_region.pests]
        assert any("aphid" in name.lower() for name in pest_names)
        assert any("beetle" in name.lower() for name in pest_names)

    @pytest.mark.asyncio
    async def test_wheat_pest_accuracy(self, service):
        """Test accuracy for major wheat pests."""
        # Kansas coordinates - should include wheat midge, cereal leaf beetle
        request = PestResistanceRequest(
            coordinates=(39.0, -98.0),  # Kansas
            region_radius_km=50.0,
            crop_type="wheat",
            analysis_period_days=30
        )
        
        response = await service.analyze_pest_resistance(request)
        
        # Should include major wheat pests
        pest_names = [pest.pest_name for pest in response.analysis_region.pests]
        assert any("midge" in name.lower() for name in pest_names)
        assert any("beetle" in name.lower() for name in pest_names)

    def test_resistance_management_validation(self, service):
        """Test resistance management recommendations are agriculturally sound."""
        # Test that resistance management includes key practices
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        
        # This would be called internally by the service
        # We're testing the knowledge base structure
        corn_pests = service.pest_knowledge['corn']
        rootworm_data = corn_pests['corn_rootworm']
        
        assert 'resistance_management' in rootworm_data
        resistance_practices = rootworm_data['resistance_management']
        assert 'refuge requirements' in resistance_practices
        assert 'rotation of Bt traits' in resistance_practices
        assert 'monitoring' in resistance_practices

    def test_ipm_strategy_validation(self, service):
        """Test that IPM strategies are comprehensive and agriculturally sound."""
        regional_pressure = MagicMock()
        regional_pressure.pests = [
            MagicMock(pest_id="corn_rootworm", pest_name="Corn Rootworm")
        ]
        
        # Test pest knowledge includes comprehensive management options
        corn_pests = service.pest_knowledge['corn']
        rootworm_data = corn_pests['corn_rootworm']
        
        assert 'cultural_controls' in rootworm_data
        assert 'chemical_controls' in rootworm_data
        assert 'biological_controls' in rootworm_data
        
        cultural_controls = rootworm_data['cultural_controls']
        assert 'crop rotation' in cultural_controls
        assert 'resistant varieties' in cultural_controls
        
        chemical_controls = rootworm_data['chemical_controls']
        assert 'Bt corn' in chemical_controls
        assert 'seed treatments' in chemical_controls

    def test_pest_life_stage_accuracy(self, service):
        """Test that pest life stage information is accurate."""
        corn_pests = service.pest_knowledge['corn']
        
        # Test corn rootworm life stages
        rootworm_data = corn_pests['corn_rootworm']
        assert 'larvae' in rootworm_data['life_stages']
        assert 'adults' in rootworm_data['life_stages']
        
        # Test corn borer life stages
        borer_data = corn_pests['corn_borer']
        assert 'larvae' in borer_data['life_stages']
        assert 'adults' in borer_data['life_stages']

    def test_damage_symptom_accuracy(self, service):
        """Test that damage symptoms are agriculturally accurate."""
        corn_pests = service.pest_knowledge['corn']
        
        # Test corn rootworm damage symptoms
        rootworm_data = corn_pests['corn_rootworm']
        damage_symptoms = rootworm_data['damage_symptoms']
        assert 'root pruning' in damage_symptoms
        assert 'lodging' in damage_symptoms
        assert 'reduced nutrient uptake' in damage_symptoms
        
        # Test corn borer damage symptoms
        borer_data = corn_pests['corn_borer']
        damage_symptoms = borer_data['damage_symptoms']
        assert 'stalk tunneling' in damage_symptoms
        assert 'ear damage' in damage_symptoms

    def test_environmental_factor_accuracy(self, service):
        """Test that environmental factors are agriculturally accurate."""
        corn_pests = service.pest_knowledge['corn']
        
        # Test corn rootworm environmental factors
        rootworm_data = corn_pests['corn_rootworm']
        env_factors = rootworm_data['environmental_factors']
        
        assert 'temperature' in env_factors
        assert 'humidity' in env_factors
        assert 'soil_moisture' in env_factors
        
        # Temperature should be reasonable for corn rootworm
        temp_range = env_factors['temperature']['range']
        assert '15-35°C' in temp_range

    def test_yield_loss_potential_validation(self, service):
        """Test that yield loss potential values are reasonable."""
        corn_pests = service.pest_knowledge['corn']
        
        for pest_id, pest_data in corn_pests.items():
            yield_loss = pest_data.get('yield_loss_potential')
            if yield_loss is not None:
                # Yield loss should be between 0 and 1 (0% to 100%)
                assert 0.0 <= yield_loss <= 1.0
                # Most pests shouldn't cause more than 50% yield loss
                assert yield_loss <= 0.5