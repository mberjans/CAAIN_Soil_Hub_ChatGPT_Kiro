"""
Tests for Variety Growing Season Service

Comprehensive test suite for the variety growing season analysis service,
including phenology modeling, critical growth stage timing, and risk assessment.

TICKET-005_crop-variety-recommendations-8.2 Testing:
- Growing season analysis functionality
- Phenology prediction accuracy
- Risk assessment validation
- Integration with external services
- API endpoint functionality
"""

import pytest
import asyncio
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any, List

try:
    from src.services.variety_growing_season_service import (
        VarietyGrowingSeasonService,
        variety_growing_season_service
    )
    from src.models.growing_season_models import (
        GrowingSeasonAnalysisRequest,
        GrowingSeasonAnalysisResponse,
        VarietyPhenologyProfile,
        PhenologyStage,
        GrowingDegreeDayParameters,
        SeasonLengthAnalysis,
        TemperatureSensitivityAnalysis,
        PhotoperiodAnalysis,
        CriticalDatePrediction,
        GrowingSeasonCalendar,
        SeasonRiskAssessment,
        GrowthStage,
        TemperatureSensitivity,
        PhotoperiodResponse,
        SeasonRiskLevel,
        PhenologyModelType
    )
except ImportError:
    from services.variety_growing_season_service import (
        VarietyGrowingSeasonService,
        variety_growing_season_service
    )
    from models.growing_season_models import (
        GrowingSeasonAnalysisRequest,
        GrowingSeasonAnalysisResponse,
        VarietyPhenologyProfile,
        PhenologyStage,
        GrowingDegreeDayParameters,
        SeasonLengthAnalysis,
        TemperatureSensitivityAnalysis,
        PhotoperiodAnalysis,
        CriticalDatePrediction,
        GrowingSeasonCalendar,
        SeasonRiskAssessment,
        GrowthStage,
        TemperatureSensitivity,
        PhotoperiodResponse,
        SeasonRiskLevel,
        PhenologyModelType
    )


class TestVarietyGrowingSeasonService:
    """Test suite for VarietyGrowingSeasonService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return VarietyGrowingSeasonService()
    
    @pytest.fixture
    def sample_request(self):
        """Create sample analysis request."""
        return GrowingSeasonAnalysisRequest(
            variety_id="test_variety_001",
            variety_name="Test Corn Variety",
            crop_name="corn",
            location={
                "latitude": 40.0,
                "longitude": -95.0,
                "elevation_ft": 1000
            },
            planting_date=date(2024, 4, 15)
        )
    
    @pytest.fixture
    def sample_phenology_profile(self):
        """Create sample phenology profile."""
        stages = [
            PhenologyStage(
                stage_name=GrowthStage.EMERGENCE,
                stage_code="VE",
                gdd_requirement=0,
                days_from_planting=7,
                description="Seedling emergence"
            ),
            PhenologyStage(
                stage_name=GrowthStage.VEGETATIVE,
                stage_code="V6",
                gdd_requirement=475,
                days_from_planting=30,
                description="6-leaf stage"
            ),
            PhenologyStage(
                stage_name=GrowthStage.FLOWERING,
                stage_code="R1",
                gdd_requirement=1250,
                days_from_planting=65,
                description="Silking"
            ),
            PhenologyStage(
                stage_name=GrowthStage.MATURITY,
                stage_code="R6",
                gdd_requirement=2500,
                days_from_planting=120,
                description="Physiological maturity"
            )
        ]
        
        return VarietyPhenologyProfile(
            variety_id="test_variety_001",
            variety_name="Test Corn Variety",
            crop_name="corn",
            phenology_model_type=PhenologyModelType.THERMAL_TIME,
            gdd_parameters=GrowingDegreeDayParameters(
                base_temperature_c=10.0,
                variety_adjustment_factor=1.0
            ),
            stages=stages,
            total_gdd_requirement=2500,
            days_to_maturity=120,
            temperature_sensitivity=TemperatureSensitivity.SENSITIVE,
            photoperiod_response=PhotoperiodResponse.DAY_NEUTRAL,
            heat_stress_threshold_c=35.0,
            cold_stress_threshold_c=5.0
        )
    
    @pytest.mark.asyncio
    async def test_analyze_growing_season_success(self, service, sample_request):
        """Test successful growing season analysis."""
        
        with patch.object(service, '_get_climate_data', return_value={
            "frost_free_days": 200,
            "growing_degree_days": 2800,
            "average_temperature": 22.0,
            "climate_zone": "6a"
        }):
            result = await service.analyze_growing_season(sample_request)
            
            assert isinstance(result, GrowingSeasonAnalysisResponse)
            assert result.analysis.variety_id == "test_variety_001"
            assert result.analysis.crop_name == "corn"
            assert result.analysis.location == sample_request.location
            assert result.processing_time_ms > 0
            assert result.confidence_score > 0
    
    @pytest.mark.asyncio
    async def test_analyze_growing_season_invalid_crop(self, service):
        """Test analysis with invalid crop name."""
        request = GrowingSeasonAnalysisRequest(
            variety_id="test_variety_001",
            crop_name="invalid_crop",
            location={"latitude": 40.0, "longitude": -95.0}
        )
        
        with pytest.raises(ValueError, match="No phenology data available"):
            await service.analyze_growing_season(request)
    
    @pytest.mark.asyncio
    async def test_get_variety_phenology_profile(self, service):
        """Test phenology profile generation."""
        
        profile = await service._get_variety_phenology_profile(
            "test_variety_001", "Test Variety", "corn"
        )
        
        assert isinstance(profile, VarietyPhenologyProfile)
        assert profile.variety_id == "test_variety_001"
        assert profile.crop_name == "corn"
        assert len(profile.stages) > 0
        assert profile.total_gdd_requirement > 0
        assert profile.days_to_maturity > 0
    
    @pytest.mark.asyncio
    async def test_analyze_season_length(self, service, sample_phenology_profile):
        """Test season length analysis."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        
        with patch.object(service, '_get_climate_data', return_value={
            "frost_free_days": 200,
            "growing_degree_days": 2800
        }):
            analysis = await service._analyze_season_length(sample_phenology_profile, location)
            
            assert isinstance(analysis, SeasonLengthAnalysis)
            assert analysis.minimum_season_length_days > 0
            assert analysis.optimal_season_length_days > analysis.minimum_season_length_days
            assert analysis.heat_unit_requirement == sample_phenology_profile.total_gdd_requirement
            assert analysis.season_length_sufficiency in ["excellent", "adequate", "insufficient"]
    
    @pytest.mark.asyncio
    async def test_analyze_temperature_sensitivity(self, service, sample_phenology_profile):
        """Test temperature sensitivity analysis."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        
        with patch.object(service, '_get_climate_data', return_value={
            "average_temperature": 22.0
        }):
            analysis = await service._analyze_temperature_sensitivity(sample_phenology_profile, location)
            
            assert isinstance(analysis, TemperatureSensitivityAnalysis)
            assert len(analysis.optimal_temperature_range_c) == 2
            assert analysis.minimum_growth_temperature_c < analysis.maximum_growth_temperature_c
            assert 0.0 <= analysis.temperature_adaptation_score <= 1.0
    
    @pytest.mark.asyncio
    async def test_analyze_photoperiod_response(self, service, sample_phenology_profile):
        """Test photoperiod response analysis."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        
        analysis = await service._analyze_photoperiod_response(sample_phenology_profile, location)
        
        assert isinstance(analysis, PhotoperiodAnalysis)
        assert analysis.photoperiod_response_type == sample_phenology_profile.photoperiod_response
        assert analysis.day_length_sensitivity in ["low", "moderate", "high"]
        assert len(analysis.photoperiod_notes) > 0
    
    @pytest.mark.asyncio
    async def test_generate_growing_calendar(self, service, sample_phenology_profile):
        """Test growing season calendar generation."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        planting_date = date(2024, 4, 15)
        
        with patch.object(service, '_get_climate_data', return_value={
            "frost_free_days": 200,
            "growing_degree_days": 2800
        }):
            calendar = await service._generate_growing_calendar(
                sample_phenology_profile, location, planting_date
            )
            
            assert isinstance(calendar, GrowingSeasonCalendar)
            assert calendar.variety_id == sample_phenology_profile.variety_id
            assert calendar.planting_date == planting_date
            assert len(calendar.critical_dates) > 0
            assert len(calendar.growth_stages) > 0
            assert len(calendar.management_windows) > 0
            assert len(calendar.risk_periods) > 0
    
    @pytest.mark.asyncio
    async def test_assess_growing_season_risks(self, service, sample_phenology_profile):
        """Test growing season risk assessment."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        
        # Create mock analyses
        season_length_analysis = SeasonLengthAnalysis(
            minimum_season_length_days=120,
            optimal_season_length_days=150,
            frost_free_period_required_days=120,
            heat_unit_requirement=2500,
            season_length_sufficiency="adequate",
            risk_factors=[]
        )
        
        temperature_analysis = TemperatureSensitivityAnalysis(
            optimal_temperature_range_c=(20.0, 25.0),
            minimum_growth_temperature_c=15.0,
            maximum_growth_temperature_c=30.0,
            temperature_adaptation_score=0.8,
            stress_tolerance_notes=[]
        )
        
        photoperiod_analysis = PhotoperiodAnalysis(
            photoperiod_response_type=PhotoperiodResponse.DAY_NEUTRAL,
            day_length_sensitivity="low",
            photoperiod_notes=[]
        )
        
        risk_assessment = await service._assess_growing_season_risks(
            sample_phenology_profile, location, season_length_analysis,
            temperature_analysis, photoperiod_analysis
        )
        
        assert isinstance(risk_assessment, SeasonRiskAssessment)
        assert risk_assessment.overall_risk_level in [
            SeasonRiskLevel.LOW, SeasonRiskLevel.MODERATE, 
            SeasonRiskLevel.HIGH, SeasonRiskLevel.CRITICAL
        ]
        assert 0.0 <= risk_assessment.risk_score <= 1.0
        assert len(risk_assessment.monitoring_recommendations) > 0
    
    def test_calculate_temperature_score(self, service):
        """Test temperature score calculation."""
        
        # Test optimal temperature
        score = service._calculate_temperature_score(22.0, (20.0, 25.0))
        assert score == 1.0
        
        # Test temperature below optimal
        score = service._calculate_temperature_score(15.0, (20.0, 25.0))
        assert 0.0 <= score < 1.0
        
        # Test temperature above optimal
        score = service._calculate_temperature_score(30.0, (20.0, 25.0))
        assert 0.0 <= score < 1.0
    
    def test_calculate_max_day_length(self, service):
        """Test maximum day length calculation."""
        
        # Test at 40 degrees latitude
        max_day_length = service._calculate_max_day_length(40.0)
        assert 12.0 <= max_day_length <= 18.0  # Reasonable range
    
    def test_calculate_min_day_length(self, service):
        """Test minimum day length calculation."""
        
        # Test at 40 degrees latitude
        min_day_length = service._calculate_min_day_length(40.0)
        assert 6.0 <= min_day_length <= 12.0  # Reasonable range
    
    def test_get_optimal_latitude_range(self, service):
        """Test optimal latitude range calculation."""
        
        # Test short day response
        range_short = service._get_optimal_latitude_range(PhotoperiodResponse.SHORT_DAY)
        assert range_short[0] < range_short[1]
        
        # Test long day response
        range_long = service._get_optimal_latitude_range(PhotoperiodResponse.LONG_DAY)
        assert range_long[0] < range_long[1]
        
        # Test day neutral response
        range_neutral = service._get_optimal_latitude_range(PhotoperiodResponse.DAY_NEUTRAL)
        assert range_neutral[0] < range_neutral[1]
    
    @pytest.mark.asyncio
    async def test_calculate_optimal_planting_date(self, service, sample_phenology_profile):
        """Test optimal planting date calculation."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        
        with patch.object(service, '_get_climate_data', return_value={
            "last_frost_date": date(2024, 4, 15)
        }):
            planting_date = await service._calculate_optimal_planting_date(
                sample_phenology_profile, location
            )
            
            assert isinstance(planting_date, date)
            assert planting_date >= date(2024, 4, 15)  # After last frost
    
    @pytest.mark.asyncio
    async def test_predict_critical_dates(self, service, sample_phenology_profile):
        """Test critical date prediction."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        planting_date = date(2024, 4, 15)
        
        critical_dates = await service._predict_critical_dates(
            sample_phenology_profile, planting_date, location
        )
        
        assert isinstance(critical_dates, list)
        assert len(critical_dates) > 0
        
        for date_prediction in critical_dates:
            assert isinstance(date_prediction, CriticalDatePrediction)
            assert isinstance(date_prediction.predicted_date, date)
            assert 0.0 <= date_prediction.confidence_level <= 1.0
    
    def test_generate_growth_stage_timeline(self, service, sample_phenology_profile):
        """Test growth stage timeline generation."""
        
        planting_date = date(2024, 4, 15)
        timeline = service._generate_growth_stage_timeline(sample_phenology_profile, planting_date)
        
        assert isinstance(timeline, list)
        assert len(timeline) > 0
        
        for stage in timeline:
            assert "stage" in stage
            assert "description" in stage
            assert "date" in stage
            assert "days_from_planting" in stage
    
    def test_generate_management_windows(self, service, sample_phenology_profile):
        """Test management window generation."""
        
        planting_date = date(2024, 4, 15)
        windows = service._generate_management_windows(sample_phenology_profile, planting_date)
        
        assert isinstance(windows, list)
        assert len(windows) > 0
        
        for window in windows:
            assert "window_type" in window
            assert "start_date" in window
            assert "end_date" in window
            assert "activities" in window
            assert "priority" in window
    
    def test_generate_risk_periods(self, service, sample_phenology_profile):
        """Test risk period generation."""
        
        location = {"latitude": 40.0, "longitude": -95.0}
        planting_date = date(2024, 4, 15)
        
        risk_periods = service._generate_risk_periods(
            sample_phenology_profile, planting_date, location
        )
        
        assert isinstance(risk_periods, list)
        
        for period in risk_periods:
            assert "risk_type" in period
            assert "start_date" in period
            assert "end_date" in period
            assert "severity" in period
            assert "description" in period
    
    def test_generate_harvest_window(self, service, sample_phenology_profile):
        """Test harvest window generation."""
        
        planting_date = date(2024, 4, 15)
        harvest_window = service._generate_harvest_window(sample_phenology_profile, planting_date)
        
        assert isinstance(harvest_window, dict)
        assert "optimal_harvest_date" in harvest_window or "harvest_window" in harvest_window
    
    def test_generate_season_summary(self, service, sample_phenology_profile):
        """Test season summary generation."""
        
        critical_dates = [
            CriticalDatePrediction(
                date_type="Test",
                predicted_date=date(2024, 6, 15),
                confidence_level=0.8,
                factors_affecting_date=[],
                management_recommendations=[]
            )
        ]
        
        summary = service._generate_season_summary(sample_phenology_profile, critical_dates)
        
        assert isinstance(summary, dict)
        assert "total_growing_days" in summary
        assert "total_gdd_requirement" in summary
        assert "critical_stages" in summary
    
    def test_calculate_suitability_score(self, service):
        """Test suitability score calculation."""
        
        season_length_analysis = SeasonLengthAnalysis(
            minimum_season_length_days=120,
            optimal_season_length_days=150,
            frost_free_period_required_days=120,
            heat_unit_requirement=2500,
            season_length_sufficiency="excellent",
            risk_factors=[]
        )
        
        temperature_analysis = TemperatureSensitivityAnalysis(
            optimal_temperature_range_c=(20.0, 25.0),
            minimum_growth_temperature_c=15.0,
            maximum_growth_temperature_c=30.0,
            temperature_adaptation_score=0.8,
            stress_tolerance_notes=[]
        )
        
        risk_assessment = SeasonRiskAssessment(
            overall_risk_level=SeasonRiskLevel.LOW,
            risk_score=0.2,
            identified_risks=[],
            mitigation_strategies=[],
            contingency_plans=[],
            monitoring_recommendations=[]
        )
        
        score = service._calculate_suitability_score(
            season_length_analysis, temperature_analysis, risk_assessment
        )
        
        assert 0.0 <= score <= 1.0
    
    def test_generate_key_recommendations(self, service):
        """Test key recommendations generation."""
        
        season_length_analysis = SeasonLengthAnalysis(
            minimum_season_length_days=120,
            optimal_season_length_days=150,
            frost_free_period_required_days=120,
            heat_unit_requirement=2500,
            season_length_sufficiency="adequate",
            risk_factors=[]
        )
        
        temperature_analysis = TemperatureSensitivityAnalysis(
            optimal_temperature_range_c=(20.0, 25.0),
            minimum_growth_temperature_c=15.0,
            maximum_growth_temperature_c=30.0,
            temperature_adaptation_score=0.8,
            stress_tolerance_notes=[]
        )
        
        photoperiod_analysis = PhotoperiodAnalysis(
            photoperiod_response_type=PhotoperiodResponse.DAY_NEUTRAL,
            day_length_sensitivity="low",
            photoperiod_notes=[]
        )
        
        risk_assessment = SeasonRiskAssessment(
            overall_risk_level=SeasonRiskLevel.MODERATE,
            risk_score=0.4,
            identified_risks=[],
            mitigation_strategies=[],
            contingency_plans=[],
            monitoring_recommendations=[]
        )
        
        recommendations = service._generate_key_recommendations(
            season_length_analysis, temperature_analysis, photoperiod_analysis, risk_assessment
        )
        
        assert isinstance(recommendations, list)
    
    def test_generate_warnings(self, service):
        """Test warnings generation."""
        
        season_length_analysis = SeasonLengthAnalysis(
            minimum_season_length_days=120,
            optimal_season_length_days=150,
            frost_free_period_required_days=100,  # Insufficient
            heat_unit_requirement=2500,
            season_length_sufficiency="insufficient",
            risk_factors=["Insufficient frost-free period"]
        )
        
        temperature_analysis = TemperatureSensitivityAnalysis(
            optimal_temperature_range_c=(20.0, 25.0),
            minimum_growth_temperature_c=15.0,
            maximum_growth_temperature_c=30.0,
            temperature_adaptation_score=0.4,  # Low score
            stress_tolerance_notes=[]
        )
        
        risk_assessment = SeasonRiskAssessment(
            overall_risk_level=SeasonRiskLevel.CRITICAL,
            risk_score=0.9,
            identified_risks=[],
            mitigation_strategies=[],
            contingency_plans=[],
            monitoring_recommendations=[]
        )
        
        warnings = service._generate_warnings(
            season_length_analysis, temperature_analysis, risk_assessment
        )
        
        assert isinstance(warnings, list)
        assert len(warnings) > 0  # Should have warnings
    
    def test_calculate_success_probability(self, service):
        """Test success probability calculation."""
        
        suitability_score = 0.8
        risk_assessment = SeasonRiskAssessment(
            overall_risk_level=SeasonRiskLevel.LOW,
            risk_score=0.2,
            identified_risks=[],
            mitigation_strategies=[],
            contingency_plans=[],
            monitoring_recommendations=[]
        )
        
        probability = service._calculate_success_probability(suitability_score, risk_assessment)
        
        assert 0.0 <= probability <= 1.0
        assert probability > 0.5  # Should be high with low risk
    
    def test_get_data_sources_used(self, service):
        """Test data sources used tracking."""
        
        sources = service._get_data_sources_used()
        
        assert isinstance(sources, list)
        assert "phenology_database" in sources
        assert "climate_estimates" in sources
    
    def test_calculate_confidence_score(self, service, sample_phenology_profile):
        """Test confidence score calculation."""
        
        # Create a mock analysis
        analysis = MagicMock()
        analysis.phenology_profile = sample_phenology_profile
        
        confidence = service._calculate_confidence_score(analysis)
        
        assert 0.0 <= confidence <= 1.0


class TestGrowingSeasonModelsValidator:
    """Test suite for GrowingSeasonModelsValidator."""
    
    def test_validate_temperature_range(self):
        """Test temperature range validation."""
        
        # Valid range
        assert GrowingSeasonModelsValidator.validate_temperature_range(15.0, 25.0) == True
        
        # Invalid range (min > max)
        assert GrowingSeasonModelsValidator.validate_temperature_range(25.0, 15.0) == False
        
        # Invalid range (too cold)
        assert GrowingSeasonModelsValidator.validate_temperature_range(-60.0, 25.0) == False
        
        # Invalid range (too hot)
        assert GrowingSeasonModelsValidator.validate_temperature_range(15.0, 70.0) == False
    
    def test_validate_gdd_parameters(self):
        """Test GDD parameters validation."""
        
        from models.growing_season_models import GrowingDegreeDayParameters
        
        # Valid parameters
        valid_params = GrowingDegreeDayParameters(
            base_temperature_c=10.0,
            upper_threshold_c=30.0
        )
        assert GrowingSeasonModelsValidator.validate_gdd_parameters(valid_params) == True
        
        # Invalid base temperature
        invalid_base = GrowingDegreeDayParameters(
            base_temperature_c=40.0,
            upper_threshold_c=30.0
        )
        assert GrowingSeasonModelsValidator.validate_gdd_parameters(invalid_base) == False
        
        # Invalid upper threshold
        invalid_upper = GrowingDegreeDayParameters(
            base_temperature_c=10.0,
            upper_threshold_c=5.0
        )
        assert GrowingSeasonModelsValidator.validate_gdd_parameters(invalid_upper) == False
    
    def test_validate_phenology_stages(self):
        """Test phenology stages validation."""
        
        from models.growing_season_models import PhenologyStage, GrowthStage
        
        # Valid stages
        valid_stages = [
            PhenologyStage(
                stage_name=GrowthStage.EMERGENCE,
                stage_code="VE",
                gdd_requirement=0,
                days_from_planting=7,
                description="Emergence"
            ),
            PhenologyStage(
                stage_name=GrowthStage.MATURITY,
                stage_code="R6",
                gdd_requirement=2500,
                days_from_planting=120,
                description="Maturity"
            )
        ]
        assert GrowingSeasonModelsValidator.validate_phenology_stages(valid_stages) == True
        
        # Missing required stages
        incomplete_stages = [
            PhenologyStage(
                stage_name=GrowthStage.VEGETATIVE,
                stage_code="V6",
                gdd_requirement=475,
                days_from_planting=30,
                description="Vegetative"
            )
        ]
        assert GrowingSeasonModelsValidator.validate_phenology_stages(incomplete_stages) == False
        
        # Empty stages
        assert GrowingSeasonModelsValidator.validate_phenology_stages([]) == False


@pytest.mark.integration
class TestGrowingSeasonServiceIntegration:
    """Integration tests for growing season service."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self):
        """Test end-to-end growing season analysis."""
        
        service = VarietyGrowingSeasonService()
        
        request = GrowingSeasonAnalysisRequest(
            variety_id="corn_variety_001",
            variety_name="Pioneer P1234",
            crop_name="corn",
            location={
                "latitude": 42.0,
                "longitude": -93.0,
                "elevation_ft": 1000
            },
            planting_date=date(2024, 4, 20)
        )
        
        # Mock external services
        with patch.object(service, '_get_climate_data', return_value={
            "frost_free_days": 180,
            "growing_degree_days": 2600,
            "average_temperature": 20.0,
            "climate_zone": "5a"
        }):
            result = await service.analyze_growing_season(request)
            
            # Verify complete analysis
            assert result.analysis.variety_id == "corn_variety_001"
            assert result.analysis.crop_name == "corn"
            assert result.analysis.suitability_score > 0
            assert result.analysis.success_probability > 0
            assert len(result.analysis.key_recommendations) > 0
            assert result.confidence_score > 0
            assert result.processing_time_ms > 0
    
    @pytest.mark.asyncio
    async def test_multiple_crop_analysis(self):
        """Test analysis for multiple crop types."""
        
        service = VarietyGrowingSeasonService()
        
        crops = ["corn", "soybean", "wheat", "tomato"]
        
        for crop in crops:
            request = GrowingSeasonAnalysisRequest(
                variety_id=f"{crop}_variety_001",
                crop_name=crop,
                location={"latitude": 40.0, "longitude": -95.0}
            )
            
            with patch.object(service, '_get_climate_data', return_value={
                "frost_free_days": 200,
                "growing_degree_days": 2500,
                "average_temperature": 20.0
            }):
                result = await service.analyze_growing_season(request)
                
                assert result.analysis.crop_name == crop
                assert result.analysis.phenology_profile.total_gdd_requirement > 0
                assert result.analysis.phenology_profile.days_to_maturity > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])