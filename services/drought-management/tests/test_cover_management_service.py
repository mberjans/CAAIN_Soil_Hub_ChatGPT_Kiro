"""
Test suite for Cover Management Service

Comprehensive tests for cover crop and mulching management functionality,
including agricultural validation and performance testing.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import date

from src.services.cover_management_service import (
    CoverManagementService,
    CoverManagementRequest,
    CoverManagementResponse,
    CoverCropSpecies,
    MulchMaterial,
    CoverCropType,
    MulchType
)

class TestCoverManagementService:
    """Test suite for CoverManagementService."""
    
    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return CoverManagementService()
    
    @pytest.fixture
    async def initialized_service(self, service):
        """Create and initialize service instance."""
        await service.initialize()
        return service
    
    @pytest.fixture
    def sample_request(self):
        """Create sample cover management request."""
        return CoverManagementRequest(
            field_id=uuid4(),
            field_size_acres=40.0,
            soil_type="clay_loam",
            climate_zone="6a",
            current_crop="corn",
            planting_date=date(2024, 9, 15),
            termination_date=date(2025, 4, 15),
            goals=["nitrogen fixation", "moisture conservation", "weed suppression"],
            budget_constraints=Decimal("2000.00"),
            equipment_available=["drill seeder", "sprayer", "mower"]
        )
    
    @pytest.fixture
    def sample_cover_crop(self):
        """Create sample cover crop species."""
        return CoverCropSpecies(
            species_id=uuid4(),
            common_name="Crimson Clover",
            scientific_name="Trifolium incarnatum",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=10,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=15,
            termination_methods=["mowing", "herbicide", "tillage"],
            benefits=["nitrogen fixation", "erosion control", "weed suppression"]
        )
    
    @pytest.fixture
    def sample_mulch_material(self):
        """Create sample mulch material."""
        return MulchMaterial(
            material_id=uuid4(),
            material_name="Wheat Straw",
            mulch_type=MulchType.ORGANIC,
            cost_per_cubic_yard=Decimal("15.00"),
            application_rate_inches=3,
            moisture_retention_percent=25,
            weed_suppression_percent=80,
            decomposition_rate_months=12,
            soil_health_benefits=["organic matter", "erosion control", "temperature moderation"]
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert not service.initialized
        assert service.cover_crop_database is None
        assert service.mulch_database is None
        
        await service.initialize()
        
        assert service.initialized
        assert service.cover_crop_database is not None
        assert service.mulch_database is not None
        assert len(service.cover_crop_database) > 0
        assert len(service.mulch_database) > 0
    
    @pytest.mark.asyncio
    async def test_service_cleanup(self, initialized_service):
        """Test service cleanup."""
        assert initialized_service.initialized
        
        await initialized_service.cleanup()
        
        assert not initialized_service.initialized
    
    @pytest.mark.asyncio
    async def test_get_cover_management_recommendations(self, initialized_service, sample_request):
        """Test comprehensive cover management recommendations."""
        response = await initialized_service.get_cover_management_recommendations(sample_request)
        
        assert isinstance(response, CoverManagementResponse)
        assert response.recommendation_id is not None
        assert len(response.cover_crop_recommendations) > 0
        assert len(response.mulch_recommendations) > 0
        assert response.implementation_plan is not None
        assert response.expected_benefits is not None
        assert response.cost_analysis is not None
        assert response.timeline is not None
        
        # Validate cover crop recommendations
        for crop in response.cover_crop_recommendations:
            assert isinstance(crop, CoverCropSpecies)
            assert crop.common_name is not None
            assert crop.seeding_rate_lbs_per_acre > 0
        
        # Validate mulch recommendations
        for material in response.mulch_recommendations:
            assert isinstance(material, MulchMaterial)
            assert material.material_name is not None
            assert material.cost_per_cubic_yard > 0
    
    @pytest.mark.asyncio
    async def test_calculate_biomass_production(self, initialized_service, sample_cover_crop):
        """Test biomass production calculation."""
        field_conditions = {
            "soil_quality_score": 0.8,
            "moisture_availability": 0.7,
            "temperature_suitability": 0.9,
            "field_size_acres": 40
        }
        
        biomass_analysis = await initialized_service.calculate_biomass_production(
            sample_cover_crop, field_conditions
        )
        
        assert biomass_analysis["species"] == sample_cover_crop.common_name
        assert biomass_analysis["base_biomass_lbs_per_acre"] == sample_cover_crop.biomass_production_lbs_per_acre
        assert biomass_analysis["adjusted_biomass_lbs_per_acre"] > 0
        assert biomass_analysis["nitrogen_contribution_lbs_per_acre"] >= 0
        assert biomass_analysis["organic_matter_contribution_lbs_per_acre"] > 0
        assert 0 <= biomass_analysis["soil_quality_factor"] <= 1
        assert 0 <= biomass_analysis["moisture_factor"] <= 1
        assert 0 <= biomass_analysis["temperature_factor"] <= 1
    
    @pytest.mark.asyncio
    async def test_assess_moisture_conservation(self, initialized_service, sample_mulch_material):
        """Test moisture conservation assessment."""
        mulch_materials = [sample_mulch_material]
        field_conditions = {
            "field_size_acres": 40,
            "soil_type": "clay_loam",
            "slope_percent": 2
        }
        
        conservation_analysis = await initialized_service.assess_moisture_conservation(
            mulch_materials, field_conditions
        )
        
        assert conservation_analysis["total_moisture_retention_percent"] > 0
        assert conservation_analysis["total_weed_suppression_percent"] > 0
        assert conservation_analysis["estimated_water_savings_inches_per_year"] > 0
        assert conservation_analysis["total_material_cost"] > 0
        assert conservation_analysis["cost_per_acre"] > 0
        assert conservation_analysis["roi_estimate_years"] > 0
    
    def test_climate_suitability_check(self, initialized_service):
        """Test climate suitability validation."""
        # Test cold tolerance check
        cold_tolerant_crop = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Winter Rye",
            scientific_name="Secale cereale",
            crop_type=CoverCropType.GRASS,
            nitrogen_fixation=False,
            biomass_production_lbs_per_acre=4000,
            root_depth_inches=18,
            cold_tolerance_f=5,  # Very cold tolerant
            drought_tolerance=7,
            seeding_rate_lbs_per_acre=25,
            termination_methods=["herbicide", "tillage"],
            benefits=["winter hardiness", "biomass production"]
        )
        
        # Should be suitable for cold zones
        assert initialized_service._is_climate_suitable(cold_tolerant_crop, "5a")
        assert initialized_service._is_climate_suitable(cold_tolerant_crop, "6b")
        
        # Test warm climate crop
        warm_crop = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Buckwheat",
            scientific_name="Fagopyrum esculentum",
            crop_type=CoverCropType.BROADLEAF,
            nitrogen_fixation=False,
            biomass_production_lbs_per_acre=2000,
            root_depth_inches=8,
            cold_tolerance_f=32,  # Not cold tolerant
            drought_tolerance=4,
            seeding_rate_lbs_per_acre=50,
            termination_methods=["mowing", "herbicide"],
            benefits=["quick growth", "pollinator support"]
        )
        
        # Should not be suitable for cold zones
        assert not initialized_service._is_climate_suitable(warm_crop, "5a")
        assert initialized_service._is_climate_suitable(warm_crop, "8a")
    
    def test_goal_alignment_check(self, initialized_service):
        """Test goal alignment validation."""
        legume_crop = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Hairy Vetch",
            scientific_name="Vicia villosa",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3500,
            root_depth_inches=15,
            cold_tolerance_f=5,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=20,
            termination_methods=["herbicide", "tillage"],
            benefits=["high nitrogen fixation", "winter hardiness"]
        )
        
        # Test nitrogen fixation goal
        assert initialized_service._aligns_with_goals(legume_crop, ["nitrogen", "fertility"])
        assert not initialized_service._aligns_with_goals(legume_crop, ["nitrogen"])  # Should still align
        
        # Test biomass goal
        high_biomass_crop = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Annual Ryegrass",
            scientific_name="Lolium multiflorum",
            crop_type=CoverCropType.GRASS,
            nitrogen_fixation=False,
            biomass_production_lbs_per_acre=5000,  # High biomass
            root_depth_inches=18,
            cold_tolerance_f=20,
            drought_tolerance=7,
            seeding_rate_lbs_per_acre=25,
            termination_methods=["herbicide", "tillage"],
            benefits=["biomass production", "erosion control"]
        )
        
        assert initialized_service._aligns_with_goals(high_biomass_crop, ["biomass", "organic matter"])
    
    def test_budget_constraints_check(self, initialized_service):
        """Test budget constraint validation."""
        expensive_crop = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Expensive Cover",
            scientific_name="Test species",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=10,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=100,  # High seeding rate = expensive
            termination_methods=["herbicide"],
            benefits=["test"]
        )
        
        field_size = 40.0
        budget = Decimal("1000.00")  # Low budget
        
        # Should not fit budget
        assert not initialized_service._fits_budget(expensive_crop, budget, field_size)
        
        # Should fit with higher budget
        high_budget = Decimal("5000.00")
        assert initialized_service._fits_budget(expensive_crop, high_budget, field_size)
        
        # Should fit with no budget constraint
        assert initialized_service._fits_budget(expensive_crop, None, field_size)
    
    def test_suitability_scoring(self, initialized_service, sample_request):
        """Test cover crop suitability scoring."""
        field_characteristics = {
            "soil_quality_score": 0.8,
            "moisture_availability": 0.7,
            "temperature_suitability": 0.9
        }
        
        legume_crop = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Test Legume",
            scientific_name="Test legume",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=10,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=15,
            termination_methods=["herbicide"],
            benefits=["nitrogen fixation"]
        )
        
        score = initialized_service._calculate_suitability_score(
            legume_crop, sample_request, field_characteristics
        )
        
        assert score > 0
        assert score <= 10  # Maximum score should be reasonable
        
        # Legume should get nitrogen fixation bonus
        assert score >= 2.0  # Should have nitrogen fixation bonus
    
    def test_mulch_goal_alignment(self, initialized_service):
        """Test mulch material goal alignment."""
        moisture_mulch = MulchMaterial(
            material_id=uuid4(),
            material_name="Moisture Mulch",
            mulch_type=MulchType.ORGANIC,
            cost_per_cubic_yard=Decimal("20.00"),
            application_rate_inches=3,
            moisture_retention_percent=40,  # High moisture retention
            weed_suppression_percent=70,
            decomposition_rate_months=12,
            soil_health_benefits=["moisture retention"]
        )
        
        # Should align with moisture goals
        assert initialized_service._aligns_with_mulch_goals(moisture_mulch, ["moisture", "water"])
        
        # Should not align with low moisture retention
        low_moisture_mulch = MulchMaterial(
            material_id=uuid4(),
            material_name="Low Moisture Mulch",
            mulch_type=MulchType.ORGANIC,
            cost_per_cubic_yard=Decimal("15.00"),
            application_rate_inches=2,
            moisture_retention_percent=10,  # Low moisture retention
            weed_suppression_percent=60,
            decomposition_rate_months=6,
            soil_health_benefits=["organic matter"]
        )
        
        assert not initialized_service._aligns_with_mulch_goals(low_moisture_mulch, ["moisture", "water"])
    
    def test_mulch_budget_constraints(self, initialized_service):
        """Test mulch material budget constraints."""
        expensive_mulch = MulchMaterial(
            material_id=uuid4(),
            material_name="Expensive Mulch",
            mulch_type=MulchType.PLASTIC,
            cost_per_cubic_yard=Decimal("500.00"),  # Very expensive
            application_rate_inches=0.001,
            moisture_retention_percent=40,
            weed_suppression_percent=95,
            decomposition_rate_months=12,
            soil_health_benefits=["temperature control"]
        )
        
        field_size = 40.0
        budget = Decimal("1000.00")  # Low budget
        
        # Should not fit budget
        assert not initialized_service._fits_mulch_budget(expensive_mulch, budget, field_size)
        
        # Should fit with higher budget
        high_budget = Decimal("5000.00")
        assert initialized_service._fits_mulch_budget(expensive_mulch, high_budget, field_size)
    
    def test_mulch_effectiveness_scoring(self, initialized_service, sample_request):
        """Test mulch material effectiveness scoring."""
        field_characteristics = {
            "soil_quality_score": 0.8,
            "moisture_availability": 0.7,
            "temperature_suitability": 0.9
        }
        
        effective_mulch = MulchMaterial(
            material_id=uuid4(),
            material_name="Effective Mulch",
            mulch_type=MulchType.ORGANIC,
            cost_per_cubic_yard=Decimal("25.00"),
            application_rate_inches=3,
            moisture_retention_percent=35,
            weed_suppression_percent=85,
            decomposition_rate_months=12,
            soil_health_benefits=["organic matter", "erosion control", "temperature moderation"]
        )
        
        score = initialized_service._calculate_mulch_effectiveness(
            effective_mulch, sample_request, field_characteristics
        )
        
        assert score > 0
        assert score <= 100  # Maximum score should be reasonable
        
        # Should have good scores for moisture and weed suppression
        assert score >= 20  # Should have decent effectiveness score
    
    @pytest.mark.asyncio
    async def test_implementation_plan_creation(self, initialized_service, sample_request):
        """Test implementation plan creation."""
        cover_crops = [initialized_service.cover_crop_database[0]]
        mulch_materials = [initialized_service.mulch_database[0]]
        
        plan = await initialized_service._create_implementation_plan(
            sample_request, cover_crops, mulch_materials
        )
        
        assert "cover_crop_planning" in plan
        assert "mulching_planning" in plan
        assert "integration_steps" in plan
        
        # Validate cover crop planning
        assert "species_selection" in plan["cover_crop_planning"]
        assert "seeding_timeline" in plan["cover_crop_planning"]
        assert "equipment_needed" in plan["cover_crop_planning"]
        
        # Validate mulching planning
        assert "materials_selected" in plan["mulching_planning"]
        assert "application_timeline" in plan["mulching_planning"]
        
        # Validate integration steps
        assert len(plan["integration_steps"]) > 0
    
    @pytest.mark.asyncio
    async def test_expected_benefits_calculation(self, initialized_service, sample_request):
        """Test expected benefits calculation."""
        cover_crops = [initialized_service.cover_crop_database[0]]
        mulch_materials = [initialized_service.mulch_database[0]]
        field_characteristics = {
            "soil_quality_score": 0.8,
            "moisture_availability": 0.7,
            "temperature_suitability": 0.9
        }
        
        benefits = await initialized_service._calculate_expected_benefits(
            sample_request, cover_crops, mulch_materials, field_characteristics
        )
        
        assert "moisture_conservation" in benefits
        assert "soil_health" in benefits
        assert "weed_management" in benefits
        assert "erosion_control" in benefits
        
        # Validate moisture conservation benefits
        assert benefits["moisture_conservation"]["water_savings_percent"] > 0
        assert benefits["moisture_conservation"]["water_savings_percent"] <= 50
        
        # Validate soil health benefits
        assert benefits["soil_health"]["organic_matter_increase_percent"] > 0
        
        # Validate weed management benefits
        assert benefits["weed_management"]["weed_suppression_percent"] > 0
        assert benefits["weed_management"]["weed_suppression_percent"] <= 90
    
    @pytest.mark.asyncio
    async def test_cost_analysis(self, initialized_service, sample_request):
        """Test cost analysis calculation."""
        cover_crops = [initialized_service.cover_crop_database[0]]
        mulch_materials = [initialized_service.mulch_database[0]]
        
        cost_analysis = await initialized_service._perform_cost_analysis(
            sample_request, cover_crops, mulch_materials
        )
        
        assert "total_implementation_cost" in cost_analysis
        assert "cost_per_acre" in cost_analysis
        assert "cover_crop_costs" in cost_analysis
        assert "mulch_costs" in cost_analysis
        assert "annual_maintenance_cost" in cost_analysis
        assert "estimated_roi_years" in cost_analysis
        
        # Validate costs are positive
        assert cost_analysis["total_implementation_cost"] > 0
        assert cost_analysis["cost_per_acre"] > 0
        assert cost_analysis["annual_maintenance_cost"] > 0
        
        # Validate cost structure
        assert len(cost_analysis["cover_crop_costs"]) > 0
        assert len(cost_analysis["mulch_costs"]) > 0
    
    @pytest.mark.asyncio
    async def test_timeline_creation(self, initialized_service, sample_request):
        """Test timeline creation."""
        cover_crops = [initialized_service.cover_crop_database[0]]
        mulch_materials = [initialized_service.mulch_database[0]]
        
        timeline = await initialized_service._create_timeline(
            sample_request, cover_crops, mulch_materials
        )
        
        assert "preparation_phase" in timeline
        assert "implementation_phase" in timeline
        assert "management_phase" in timeline
        assert "termination_phase" in timeline
        
        # Validate each phase has required fields
        for phase_name, phase_data in timeline.items():
            assert "duration_weeks" in phase_data or "duration_months" in phase_data
            assert "activities" in phase_data
            assert len(phase_data["activities"]) > 0


class TestAgriculturalValidation:
    """Agricultural validation tests for cover management recommendations."""
    
    @pytest.fixture
    async def service(self):
        """Create initialized service for agricultural tests."""
        service = CoverManagementService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    async def test_cover_crop_nitrogen_fixation_accuracy(self, service):
        """Test nitrogen fixation calculations are agriculturally accurate."""
        legume_crop = CoverCropSpecies(
            species_id=uuid4(),
            common_name="Crimson Clover",
            scientific_name="Trifolium incarnatum",
            crop_type=CoverCropType.LEGUME,
            nitrogen_fixation=True,
            biomass_production_lbs_per_acre=3000,
            root_depth_inches=12,
            cold_tolerance_f=10,
            drought_tolerance=6,
            seeding_rate_lbs_per_acre=15,
            termination_methods=["mowing", "herbicide"],
            benefits=["nitrogen fixation"]
        )
        
        field_conditions = {
            "soil_quality_score": 0.8,
            "moisture_availability": 0.8,
            "temperature_suitability": 0.9,
            "field_size_acres": 40
        }
        
        biomass_analysis = await service.calculate_biomass_production(legume_crop, field_conditions)
        
        # Nitrogen contribution should be reasonable (2-4% of biomass)
        nitrogen_percent = (biomass_analysis["nitrogen_contribution_lbs_per_acre"] / 
                          biomass_analysis["adjusted_biomass_lbs_per_acre"]) * 100
        
        assert 1.5 <= nitrogen_percent <= 4.5, f"Nitrogen percentage {nitrogen_percent}% is not agriculturally reasonable"
    
    @pytest.mark.asyncio
    async def test_mulch_moisture_retention_realism(self, service):
        """Test mulch moisture retention values are realistic."""
        mulch_materials = [
            MulchMaterial(
                material_id=uuid4(),
                material_name="Wheat Straw",
                mulch_type=MulchType.ORGANIC,
                cost_per_cubic_yard=Decimal("15.00"),
                application_rate_inches=3,
                moisture_retention_percent=25,
                weed_suppression_percent=80,
                decomposition_rate_months=12,
                soil_health_benefits=["organic matter"]
            )
        ]
        
        field_conditions = {
            "field_size_acres": 40,
            "soil_type": "clay_loam",
            "slope_percent": 2
        }
        
        conservation_analysis = await service.assess_moisture_conservation(mulch_materials, field_conditions)
        
        # Moisture retention should be realistic for organic mulch
        assert 15 <= conservation_analysis["total_moisture_retention_percent"] <= 50
        
        # Water savings should be reasonable
        assert 0.1 <= conservation_analysis["estimated_water_savings_inches_per_year"] <= 2.0
    
    @pytest.mark.asyncio
    async def test_seeding_rate_reasonableness(self, service):
        """Test cover crop seeding rates are agriculturally reasonable."""
        for crop in service.cover_crop_database:
            # Seeding rates should be within reasonable agricultural ranges
            assert 5 <= crop.seeding_rate_lbs_per_acre <= 100, \
                f"Seeding rate {crop.seeding_rate_lbs_per_acre} lbs/acre for {crop.common_name} is not reasonable"
    
    @pytest.mark.asyncio
    async def test_biomass_production_realism(self, service):
        """Test biomass production values are agriculturally realistic."""
        for crop in service.cover_crop_database:
            # Biomass production should be within realistic ranges
            assert 1000 <= crop.biomass_production_lbs_per_acre <= 8000, \
                f"Biomass production {crop.biomass_production_lbs_per_acre} lbs/acre for {crop.common_name} is not realistic"
    
    @pytest.mark.asyncio
    async def test_cost_effectiveness_validation(self, service):
        """Test that cost calculations are agriculturally reasonable."""
        request = CoverManagementRequest(
            field_id=uuid4(),
            field_size_acres=40.0,
            soil_type="clay_loam",
            climate_zone="6a",
            goals=["nitrogen fixation", "moisture conservation"],
            budget_constraints=Decimal("2000.00"),
            equipment_available=["drill seeder", "sprayer"]
        )
        
        response = await service.get_cover_management_recommendations(request)
        
        # Cost per acre should be reasonable for cover crops
        cost_per_acre = response.cost_analysis["cost_per_acre"]
        assert 20 <= float(cost_per_acre) <= 200, \
            f"Cost per acre ${cost_per_acre} is not agriculturally reasonable"
        
        # ROI should be reasonable for agricultural investments
        roi_years = response.cost_analysis["estimated_roi_years"]
        assert 1 <= roi_years <= 10, \
            f"ROI of {roi_years} years is not agriculturally reasonable"


class TestPerformanceRequirements:
    """Performance and reliability tests."""
    
    @pytest.fixture
    async def service(self):
        """Create initialized service for performance tests."""
        service = CoverManagementService()
        await service.initialize()
        return service
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_recommendation_response_time(self, service):
        """Test that recommendations are generated within acceptable time."""
        import time
        
        request = CoverManagementRequest(
            field_id=uuid4(),
            field_size_acres=40.0,
            soil_type="clay_loam",
            climate_zone="6a",
            goals=["nitrogen fixation", "moisture conservation"]
        )
        
        start_time = time.time()
        response = await service.get_cover_management_recommendations(request)
        elapsed_time = time.time() - start_time
        
        # Should respond within 3 seconds
        assert elapsed_time < 3.0, f"Response time {elapsed_time}s exceeds 3s requirement"
        assert response is not None
    
    @pytest.mark.asyncio
    @pytest.mark.performance
    async def test_biomass_calculation_performance(self, service):
        """Test biomass calculation performance."""
        import time
        
        crop = service.cover_crop_database[0]
        field_conditions = {
            "soil_quality_score": 0.8,
            "moisture_availability": 0.7,
            "temperature_suitability": 0.9
        }
        
        start_time = time.time()
        result = await service.calculate_biomass_production(crop, field_conditions)
        elapsed_time = time.time() - start_time
        
        # Should calculate within 1 second
        assert elapsed_time < 1.0, f"Biomass calculation time {elapsed_time}s exceeds 1s requirement"
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_service_reliability(self, service):
        """Test service reliability with multiple concurrent requests."""
        request = CoverManagementRequest(
            field_id=uuid4(),
            field_size_acres=40.0,
            soil_type="clay_loam",
            climate_zone="6a",
            goals=["nitrogen fixation"]
        )
        
        # Test multiple concurrent requests
        tasks = [
            service.get_cover_management_recommendations(request)
            for _ in range(5)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All requests should succeed
        for response in responses:
            assert not isinstance(response, Exception)
            assert isinstance(response, CoverManagementResponse)
    
    @pytest.mark.asyncio
    async def test_error_handling(self, service):
        """Test error handling for invalid inputs."""
        # Test with invalid field ID
        invalid_request = CoverManagementRequest(
            field_id=uuid4(),
            field_size_acres=-10.0,  # Invalid negative size
            soil_type="clay_loam",
            climate_zone="6a",
            goals=["nitrogen fixation"]
        )
        
        # Should handle gracefully
        try:
            response = await service.get_cover_management_recommendations(invalid_request)
            # If it doesn't raise an exception, response should still be valid
            assert isinstance(response, CoverManagementResponse)
        except Exception as e:
            # Should be a reasonable error message
            assert "field_size_acres" in str(e).lower() or "size" in str(e).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])