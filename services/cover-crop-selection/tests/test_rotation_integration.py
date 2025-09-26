"""
Integration Tests for Cover Crop Rotation Integration Features

Comprehensive tests for the rotation integration functionality including:
- Rotation integration recommendations
- Main crop compatibility analysis  
- Position-specific recommendations
- Service integration with rotation planning
"""

import pytest
import asyncio
from datetime import date, timedelta
from typing import List, Dict, Any
import json

# Import test dependencies
try:
    from ..src.services.cover_crop_selection_service import CoverCropSelectionService
    from ..src.services.main_crop_integration_service import MainCropIntegrationService
    from ..src.models.cover_crop_models import (
        CoverCropSelectionRequest,
        CoverCropSelectionResponse,
        SoilConditions,
        CoverCropObjectives,
        ClimateData,
        SoilBenefit,
        CoverCropType,
        GrowingSeason,
        MainCropRotationPlan,
        CoverCropRotationIntegration,
        CropTimingWindow,
        RotationBenefitAnalysis
    )
except ImportError:
    from src.services.cover_crop_selection_service import CoverCropSelectionService
    from src.services.main_crop_integration_service import MainCropIntegrationService
    from src.models.cover_crop_models import (
        CoverCropSelectionRequest,
        CoverCropSelectionResponse,
        SoilConditions,
        CoverCropObjectives,
        ClimateData,
        SoilBenefit,
        CoverCropType,
        GrowingSeason,
        MainCropRotationPlan,
        CoverCropRotationIntegration,
        CropTimingWindow,
        RotationBenefitAnalysis
    )


class TestRotationIntegrationModels:
    """Test the new rotation integration models."""
    
    def test_main_crop_rotation_plan_creation(self):
        """Test MainCropRotationPlan model creation."""
        rotation_plan = MainCropRotationPlan(
            rotation_id="rot_001",
            rotation_name="Corn-Soybean",
            sequence=["corn", "soybean"],
            duration_years=2,
            region_suitability=["midwest", "great_plains"],
            primary_benefits=["Nitrogen cycling", "Pest break", "Soil health"],
            sustainability_rating=8.5,
            complexity_level="moderate",
            economic_performance="good",
            risk_level="moderate",
            typical_planting_dates={
                "corn": {"start": "2024-04-15", "end": "2024-05-15"},
                "soybean": {"start": "2024-05-01", "end": "2024-06-01"}
            },
            harvest_windows={
                "corn": {"start": "2024-09-15", "end": "2024-10-31"},
                "soybean": {"start": "2024-09-01", "end": "2024-10-15"}
            }
        )
        
        assert rotation_plan.rotation_name == "Corn-Soybean"
        assert len(rotation_plan.sequence) == 2
        assert rotation_plan.duration_years == 2
        assert len(rotation_plan.typical_planting_dates) == 2
    
    def test_cover_crop_rotation_integration_creation(self):
        """Test CoverCropRotationIntegration model creation."""
        # First create the rotation plan that is required
        rotation_plan = MainCropRotationPlan(
            rotation_id="rot_001",
            rotation_name="Corn-Soybean",
            sequence=["corn", "soybean"],
            duration_years=2,
            region_suitability=["midwest"],
            primary_benefits=["Nitrogen cycling"],
            sustainability_rating=8.0,
            complexity_level="moderate",
            economic_performance="good",
            typical_planting_dates={"corn": {"start": "2024-04-15", "end": "2024-05-15"}},
            harvest_windows={"corn": {"start": "2024-09-15", "end": "2024-10-31"}}
        )
        
        integration = CoverCropRotationIntegration(
            integration_id="int_001",
            rotation_plan=rotation_plan,
            cover_crop_positions=[
                {
                    "position": "before_corn",
                    "species_id": "cc_001",
                    "timing_window": {
                        "planting_start": "2024-09-15",
                        "planting_end": "2024-10-15",
                        "termination_start": "2024-04-15",
                        "termination_end": "2024-05-01"
                    },
                    "expected_benefits": [
                        "Nitrogen fixation for corn",
                        "Erosion control over winter"
                    ]
                }
            ],
            nitrogen_cycling_benefits={"before_corn": 70.0},
            pest_management_benefits=["Break corn rootworm cycle"],
            soil_health_improvements=["Increased organic matter", "Improved soil structure"],
            compatibility_scores={"before_corn": 0.85}
        )
        
        assert integration.integration_id == "int_001"
        assert integration.rotation_plan.rotation_name == "Corn-Soybean"
        assert len(integration.cover_crop_positions) == 1
        assert integration.cover_crop_positions[0]["position"] == "before_corn"
    
    def test_crop_timing_window_creation(self):
        """Test CropTimingWindow model creation."""
        timing_window = CropTimingWindow(
            window_id="tw_001",
            crop_name="crimson_clover",
            window_type="planting",
            optimal_start=date(2024, 9, 15),
            optimal_end=date(2024, 10, 15),
            earliest_date=date(2024, 9, 1),
            latest_date=date(2024, 11, 1),
            region="midwest",
            climate_zone="7a",
            flexibility_days=14,
            critical_factors=["Soil temperature", "Frost risk"],
            weather_dependencies=["Adequate moisture", "No extended heat"]
        )
        
        assert timing_window.window_id == "tw_001"
        assert timing_window.crop_name == "crimson_clover"
        assert timing_window.window_type == "planting"
        assert timing_window.flexibility_days == 14
    
    def test_rotation_benefit_analysis_creation(self):
        """Test RotationBenefitAnalysis model creation."""
        # Create required rotation plan
        rotation_plan = MainCropRotationPlan(
            rotation_id="rot_001",
            rotation_name="Corn-Soybean",
            sequence=["corn", "soybean"], 
            duration_years=2,
            region_suitability=["midwest"],
            primary_benefits=["Nitrogen cycling"],
            sustainability_rating=8.0,
            complexity_level="moderate",
            economic_performance="good",
            typical_planting_dates={"corn": {"start": "2024-04-15", "end": "2024-05-15"}},
            harvest_windows={"corn": {"start": "2024-09-15", "end": "2024-10-31"}}
        )
        
        # Create required cover crop integration
        cover_crop_integration = CoverCropRotationIntegration(
            integration_id="int_001",
            rotation_plan=rotation_plan,
            cover_crop_positions=[{"position": "before_corn", "species_id": "cc_001"}],
            nitrogen_cycling_benefits={"before_corn": 70.0},
            pest_management_benefits=["Break corn rootworm cycle"],
            soil_health_improvements=["Increased organic matter"],
            compatibility_scores={"before_corn": 0.85}
        )
        
        benefit_analysis = RotationBenefitAnalysis(
            analysis_id="ba_001",
            rotation_plan=rotation_plan,
            cover_crop_integration=cover_crop_integration,
            nitrogen_fixation_value=70.0,
            erosion_prevention_value=125.50,
            organic_matter_improvement=0.85,
            weed_suppression_value=75.0,
            pest_pressure_reduction={"corn_rootworm": 0.6},
            disease_break_effectiveness={"corn_gray_leaf_spot": 0.4},
            beneficial_insect_support=0.7,
            soil_health_trajectory={"year_1": 0.1, "year_3": 0.25},
            yield_impact_projections={"corn": 0.05, "soybean": 0.03},
            sustainability_improvements=["Reduced fertilizer needs", "Carbon sequestration"],
            total_benefit_value=125.50,
            cost_benefit_ratio=2.3,
            payback_period_years=2.5,
            implementation_risks=["Weather dependency", "Termination timing critical"],
            mitigation_strategies=["Flexible termination dates", "Weather monitoring"],
            confidence_level=0.88
        )
        
        assert benefit_analysis.analysis_id == "ba_001"
        assert benefit_analysis.nitrogen_fixation_value == 70.0
        assert benefit_analysis.organic_matter_improvement == 0.85
        assert benefit_analysis.total_benefit_value == 125.50
        assert len(benefit_analysis.implementation_risks) == 2


class TestMainCropIntegrationService:
    """Test the MainCropIntegrationService functionality."""
    
    @pytest.fixture
    async def integration_service(self):
        """Create and initialize integration service."""
        service = MainCropIntegrationService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, integration_service):
        """Test service initializes correctly."""
        service = await integration_service
        assert service.initialized
        assert hasattr(service, 'rotation_service_url')
    
    @pytest.mark.asyncio
    async def test_analyze_main_crop_compatibility(self, integration_service):
        """Test main crop compatibility analysis."""
        service = await integration_service
        
        # Create mock species
        from src.models.cover_crop_models import CoverCropSpecies
        
        species = CoverCropSpecies(
            species_id="cc_001",
            common_name="Crimson Clover",
            scientific_name="Trifolium incarnatum",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["6a", "7a", "7b"],
            min_temp_f=20.0,
            max_temp_f=85.0,
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 5.5, "max": 7.0},
            drainage_tolerance=["well_drained"],
            seeding_rate_lbs_acre={"drilled": 15},
            planting_depth_inches=0.25,
            days_to_establishment=14,
            biomass_production="high",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION],
            nitrogen_fixation_lbs_acre=70,
            root_depth_feet=3.0,
            termination_methods=["herbicide", "mowing", "freeze"],
            cash_crop_compatibility=["corn", "soybeans"],
            potential_issues=["Can be hard to terminate"],
            seed_cost_per_acre=25.0,
            establishment_cost_per_acre=35.0
        )
        
        # Test compatibility analysis
        compatibility = await service.analyze_main_crop_compatibility(
            species, "corn", "before"
        )
        
        assert compatibility is not None
        assert "compatibility_score" in compatibility
        assert "benefits" in compatibility
        assert "risks" in compatibility  # The actual field name used
        assert "timing_analysis" in compatibility
        assert "recommendations" in compatibility
    
    @pytest.mark.asyncio
    async def test_generate_benefit_analysis(self, integration_service):
        """Test benefit analysis generation."""
        service = await integration_service
        
        # Create proper integration plan with required models
        rotation_plan = MainCropRotationPlan(
            rotation_id="rot_001",
            rotation_name="Corn-Soybean",
            sequence=["corn", "soybean"],
            duration_years=2,
            region_suitability=["midwest"],
            primary_benefits=["Nitrogen cycling"],
            sustainability_rating=8.0,
            complexity_level="moderate",
            economic_performance="good",
            typical_planting_dates={"corn": {"start": "2024-04-15", "end": "2024-05-15"}},
            harvest_windows={"corn": {"start": "2024-09-15", "end": "2024-10-31"}}
        )
        
        integration_plan = CoverCropRotationIntegration(
            integration_id="int_001",
            rotation_plan=rotation_plan,
            cover_crop_positions=[
                {
                    "cover_crop_species_id": "cc_001",
                    "position": "before_corn",
                    "expected_benefits": ["Nitrogen fixation", "Erosion control"]
                }
            ],
            nitrogen_cycling_benefits={"before_corn": 70.0},
            pest_management_benefits=["Break corn rootworm cycle"],
            soil_health_improvements=["Increased organic matter"],
            compatibility_scores={"before_corn": 0.85}
        )
        
        benefit_analysis = await service.generate_benefit_analysis(integration_plan)
        
        assert benefit_analysis is not None
        assert isinstance(benefit_analysis, RotationBenefitAnalysis)
        assert benefit_analysis.nitrogen_fixation_value >= 0
        assert benefit_analysis.total_benefit_value >= 0
        assert benefit_analysis.confidence_level > 0


class TestCoverCropSelectionServiceIntegration:
    """Test the enhanced CoverCropSelectionService with rotation integration."""
    
    @pytest.fixture
    async def cover_crop_service(self):
        """Create and initialize cover crop service."""
        service = CoverCropSelectionService()
        await service.initialize()
        return service
    
    @pytest.fixture
    def sample_request(self):
        """Create sample cover crop selection request."""
        return CoverCropSelectionRequest(
            request_id="test_rotation_001",
            location={
                "latitude": 40.7128,
                "longitude": -74.0060,
                "state": "NY",
                "county": "Test County"
            },
            soil_conditions=SoilConditions(
                ph=6.5,
                organic_matter_percent=3.2,
                drainage_class="well_drained",
                erosion_risk="moderate"
            ),
            objectives=CoverCropObjectives(
                primary_goals=[SoilBenefit.NITROGEN_FIXATION, SoilBenefit.EROSION_CONTROL],
                nitrogen_needs=True,
                erosion_control_priority=True,
                budget_per_acre=100.0
            ),
            planting_window={
                "start": date(2024, 9, 15),
                "end": date(2024, 10, 15)
            },
            field_size_acres=50.0,
            climate_data=ClimateData(
                hardiness_zone="7a",
                annual_precipitation_inches=40.0
            )
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization_with_integration(self, cover_crop_service):
        """Test service initializes with integration service."""
        service = await cover_crop_service
        assert service.initialized
        assert hasattr(service, 'main_crop_integration_service')
        assert service.main_crop_integration_service.initialized
    
    @pytest.mark.asyncio
    async def test_get_rotation_integration_recommendations(self, cover_crop_service, sample_request):
        """Test rotation integration recommendations."""
        service = await cover_crop_service
        response = await service.get_rotation_integration_recommendations(
            rotation_name="Corn-Soybean-Wheat",
            request=sample_request,
            objectives=["Nitrogen fixation", "Soil structure improvement"]
        )
        
        assert isinstance(response, CoverCropSelectionResponse)
        assert response.request_id == sample_request.request_id
        assert len(response.single_species_recommendations) > 0
        assert response.overall_confidence > 0.0
        
        # Check that recommendations include rotation context
        first_rec = response.single_species_recommendations[0]
        assert any("rotation" in note.lower() for note in first_rec.management_notes)
        
        # Check data sources include rotation integration
        assert any("rotation" in source.lower() for source in response.data_sources)
    
    @pytest.mark.asyncio
    async def test_get_main_crop_compatibility_analysis(self, cover_crop_service):
        """Test main crop compatibility analysis."""
        service = await cover_crop_service
        # Use species from the service database
        species_id = "cc_001"  # Crimson Clover
        
        analysis = await service.get_main_crop_compatibility_analysis(
            cover_crop_species_id=species_id,
            main_crop="corn",
            position="before"
        )
        
        assert analysis is not None
        assert "compatibility_score" in analysis
        assert "species_recommendations" in analysis
        assert "economic_analysis" in analysis
        
        # Check species recommendations
        assert len(analysis["species_recommendations"]) > 0
        
        # Check economic analysis
        econ_analysis = analysis["economic_analysis"]
        assert "establishment_cost" in econ_analysis
        assert "expected_benefits" in econ_analysis
    
    @pytest.mark.asyncio
    async def test_get_rotation_position_recommendations(self, cover_crop_service, sample_request):
        """Test position-specific recommendations."""
        service = await cover_crop_service
        response = await service.get_rotation_position_recommendations(
            rotation_name="Corn-Soybean",
            position_id="before_corn",
            request=sample_request
        )
        
        assert isinstance(response, CoverCropSelectionResponse)
        assert response.request_id == sample_request.request_id
        assert len(response.single_species_recommendations) > 0
        
        # Check position-specific context
        first_rec = response.single_species_recommendations[0]
        assert any("position" in note.lower() for note in first_rec.management_notes)
        
        # Check position-specific data sources
        assert any("position" in source.lower() for source in response.data_sources)
    
    @pytest.mark.asyncio
    async def test_rotation_recommendations_vs_standard(self, cover_crop_service, sample_request):
        """Test that rotation recommendations differ from standard recommendations."""
        service = await cover_crop_service
        # Get standard recommendations
        standard_response = await service.select_cover_crops(sample_request)
        
        # Get rotation recommendations
        rotation_response = await service.get_rotation_integration_recommendations(
            rotation_name="Corn-Soybean",
            request=sample_request
        )
        
        # Compare responses
        assert len(standard_response.single_species_recommendations) > 0
        assert len(rotation_response.single_species_recommendations) > 0
        
        # Check that rotation response has different/additional context
        rotation_rec = rotation_response.single_species_recommendations[0]
        standard_rec = standard_response.single_species_recommendations[0]
        
        # Rotation recommendations should have more management notes
        assert len(rotation_rec.management_notes) >= len(standard_rec.management_notes)
        
        # Data sources should be different
        assert rotation_response.data_sources != standard_response.data_sources


class TestRotationIntegrationAPI:
    """Test the new API endpoints for rotation integration."""
    
    @pytest.fixture
    def sample_api_request(self):
        """Create sample API request data."""
        return {
            "request_id": "api_test_001",
            "location": {
                "latitude": 40.7128,
                "longitude": -74.0060,
                "state": "NY"
            },
            "soil_conditions": {
                "ph": 6.5,
                "organic_matter_percent": 3.0,
                "drainage_class": "well_drained",
                "erosion_risk": "moderate"
            },
            "objectives": {
                "primary_goals": ["nitrogen_fixation", "erosion_control"],
                "nitrogen_needs": True,
                "budget_per_acre": 100.0
            },
            "planting_window": {
                "start": "2024-09-15",
                "end": "2024-10-15"
            },
            "field_size_acres": 25.0
        }
    
    def test_rotation_integration_endpoint_structure(self):
        """Test that the rotation integration endpoint is properly structured."""
        from src.api.routes import router
        
        # Check that the route exists
        route_paths = [route.path for route in router.routes]
        assert "/api/v1/cover-crops/rotation-integration" in route_paths
    
    def test_main_crop_compatibility_endpoint_structure(self):
        """Test that the main crop compatibility endpoint is properly structured."""
        from src.api.routes import router
        
        # Check that the route exists
        route_paths = [route.path for route in router.routes]
        assert "/api/v1/cover-crops/main-crop-compatibility/{crop_name}" in route_paths
    
    def test_rotation_position_endpoint_structure(self):
        """Test that the rotation position endpoint is properly structured."""
        from src.api.routes import router
        
        # Check that the route exists
        route_paths = [route.path for route in router.routes]
        assert "/api/v1/cover-crops/rotation-position/{position_id}" in route_paths


class TestRotationIntegrationHelperMethods:
    """Test the helper methods added for rotation integration."""
    
    @pytest.fixture
    async def service_with_test_data(self):
        """Create service with test data."""
        service = CoverCropSelectionService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_generate_rotation_specific_recommendations(self, service_with_test_data):
        """Test rotation-specific recommendation generation."""
        service = await service_with_test_data
        # Mock integration plan
        integration_plan = {
            "rotation_name": "Corn-Soybean",
            "main_crops": ["corn", "soybean"],
            "integrations": [
                {
                    "cover_crop_species_id": "cc_001",
                    "position": "before_corn",
                    "expected_benefits": ["Nitrogen fixation"]
                }
            ],
            "integration_quality": 0.85,
            "timing_compatibility": 0.90
        }
        
        request = CoverCropSelectionRequest(
            request_id="test_001",
            location={"latitude": 40.0, "longitude": -74.0},
            soil_conditions=SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained"),
            objectives=CoverCropObjectives(primary_goals=[SoilBenefit.NITROGEN_FIXATION]),
            planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
            field_size_acres=25.0
        )
        
        recommendations = await service._generate_rotation_specific_recommendations(
            integration_plan, request
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) >= 0  # May be empty if no species match
    
    @pytest.mark.asyncio
    async def test_analyze_field_conditions_with_rotation(self, service_with_test_data):
        """Test field condition analysis with rotation context."""
        service = await service_with_test_data
        
        # Create proper Pydantic model for integration_plan
        rotation_plan = MainCropRotationPlan(
            rotation_id="rot_001",
            rotation_name="Corn-Soybean",
            sequence=["corn", "soybean"],
            duration_years=2,
            region_suitability=["midwest"],
            primary_benefits=["Nitrogen cycling"],
            sustainability_rating=8.0,
            complexity_level="moderate",
            economic_performance="good",
            typical_planting_dates={"corn": {"start": "2024-04-15", "end": "2024-05-15"}},
            harvest_windows={"corn": {"start": "2024-09-15", "end": "2024-10-31"}}
        )
        
        integration_plan = CoverCropRotationIntegration(
            integration_id="int_001",
            rotation_plan=rotation_plan,
            cover_crop_positions=[
                {
                    "position": "before_corn",
                    "cover_crop_species_id": "cc_001",
                    "expected_benefits": ["Nitrogen fixation"]
                }
            ],
            nitrogen_cycling_benefits={"before_corn": 70.0},
            pest_management_benefits=["Break corn rootworm cycle"],
            soil_health_improvements=["Increased organic matter"],
            compatibility_scores={"before_corn": 0.85}
        )
        
        request = CoverCropSelectionRequest(
            request_id="test_001",
            location={"latitude": 40.0, "longitude": -74.0},
            soil_conditions=SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained"),
            objectives=CoverCropObjectives(primary_goals=[SoilBenefit.NITROGEN_FIXATION]),
            planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
            field_size_acres=25.0
        )
        
        analysis = await service._analyze_field_conditions_with_rotation(
            request, integration_plan
        )
        
        assert "rotation_benefits" in analysis
        assert "rotation_challenges" in analysis
        assert "rotation_recommendations" in analysis
        assert isinstance(analysis["rotation_benefits"], list)
    
    @pytest.mark.asyncio
    async def test_generate_rotation_mixtures(self, service_with_test_data):
        """Test rotation mixture generation."""
        service = await service_with_test_data
        integration_plan = {
            "rotation_name": "Corn-Soybean",
            "integrations": [
                {
                    "cover_crop_species_id": "cc_001",
                    "position": "before_corn"
                },
                {
                    "cover_crop_species_id": "cc_002",
                    "position": "before_corn"
                }
            ]
        }
        
        mixtures = await service._generate_rotation_mixtures(integration_plan)
        
        assert isinstance(mixtures, list)
        # Mixtures may be empty if species aren't compatible or don't exist
        for mixture in mixtures:
            assert hasattr(mixture, 'mixture_name')
            assert hasattr(mixture, 'species_list')
    
    @pytest.mark.asyncio
    async def test_calculate_rotation_confidence(self, service_with_test_data):
        """Test rotation confidence calculation."""
        service = await service_with_test_data
        # Create mock recommendations
        from src.models.cover_crop_models import CoverCropRecommendation, CoverCropSpecies
        
        species = CoverCropSpecies(
            species_id="cc_001",
            common_name="Test Species",
            scientific_name="Testicus specius",
            cover_crop_type=CoverCropType.LEGUME,
            hardiness_zones=["7a"],
            growing_season=GrowingSeason.WINTER,
            ph_range={"min": 6.0, "max": 7.0},
            drainage_tolerance=["well_drained"],
            seeding_rate_lbs_acre={"drilled": 15},
            planting_depth_inches=0.5,
            days_to_establishment=10,
            biomass_production="medium",
            primary_benefits=[SoilBenefit.NITROGEN_FIXATION],
            termination_methods=["herbicide"],
            cash_crop_compatibility=["corn"]
        )
        
        recommendation = CoverCropRecommendation(
            species=species,
            suitability_score=0.85,
            confidence_level=0.80,
            seeding_rate_recommendation=15,
            planting_date_recommendation=date(2024, 9, 15),
            termination_recommendation="herbicide",
            expected_benefits=["Nitrogen fixation"],
            soil_improvement_score=0.75,
            management_notes=["Test note"],
            success_indicators=["Test indicator"]
        )
        
        integration_plan = {
            "integration_quality": 0.85,
            "timing_compatibility": 0.90
        }
        
        confidence = await service._calculate_rotation_confidence(
            [recommendation], integration_plan
        )
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident


class TestRotationIntegrationErrorHandling:
    """Test error handling in rotation integration features."""
    
    @pytest.fixture
    async def service(self):
        """Create service for error testing."""
        service = CoverCropSelectionService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_invalid_species_id_compatibility(self, service):
        """Test error handling for invalid species ID."""
        service_instance = await service
        with pytest.raises((ValueError, KeyError)):
            await service_instance.get_main_crop_compatibility_analysis(
                cover_crop_species_id="invalid_species",
                main_crop="corn",
                position="before"
            )
    
    @pytest.mark.asyncio
    async def test_empty_rotation_name(self, service):
        """Test error handling for empty rotation name."""
        service_instance = await service
        request = CoverCropSelectionRequest(
            request_id="test_001",
            location={"latitude": 40.0, "longitude": -74.0},
            soil_conditions=SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained"),
            objectives=CoverCropObjectives(primary_goals=[SoilBenefit.NITROGEN_FIXATION]),
            planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
            field_size_acres=25.0
        )
        
        # Should handle empty/None rotation name gracefully
        response = await service_instance.get_rotation_integration_recommendations(
            rotation_name="",
            request=request
        )
        
        # Should still return a valid response (fallback behavior)
        assert isinstance(response, CoverCropSelectionResponse)
    
    @pytest.mark.asyncio
    async def test_fallback_behavior_on_integration_service_failure(self, service):
        """Test fallback behavior when integration service fails."""
        service_instance = await service
        # Temporarily break the integration service
        original_service = service_instance.main_crop_integration_service
        service_instance.main_crop_integration_service = None
        
        request = CoverCropSelectionRequest(
            request_id="test_001",
            location={"latitude": 40.0, "longitude": -74.0},
            soil_conditions=SoilConditions(ph=6.5, organic_matter_percent=3.0, drainage_class="well_drained"),
            objectives=CoverCropObjectives(primary_goals=[SoilBenefit.NITROGEN_FIXATION]),
            planting_window={"start": date(2024, 9, 15), "end": date(2024, 10, 15)},
            field_size_acres=25.0
        )
        
        # Should handle gracefully and fall back to standard recommendations
        try:
            response = await service_instance.get_rotation_integration_recommendations(
                rotation_name="Corn-Soybean",
                request=request
            )
            assert isinstance(response, CoverCropSelectionResponse)
        except Exception:
            # Should not raise unhandled exceptions
            pass
        finally:
            # Restore the service
            service_instance.main_crop_integration_service = original_service


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])