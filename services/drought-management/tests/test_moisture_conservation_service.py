"""
Test suite for Moisture Conservation Service

Comprehensive tests for moisture conservation practice recommendations,
implementation planning, and cost-benefit analysis functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime

from src.services.moisture_conservation_service import MoistureConservationService
from src.models.drought_models import (
    ConservationPracticeRequest,
    ConservationPracticeResponse,
    ConservationPractice,
    ConservationPracticeType,
    SoilHealthImpact,
    EquipmentRequirement
)


class TestMoistureConservationService:
    """Comprehensive test suite for MoistureConservationService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return MoistureConservationService()

    @pytest.fixture
    def sample_request(self):
        """Create sample conservation practice request."""
        return ConservationPracticeRequest(
            field_id=uuid4(),
            soil_type="clay_loam",
            slope_percent=2.5,
            drainage_class="moderate",
            current_practices=["conventional_tillage"],
            available_equipment=["Tractor", "Planter", "Sprayer"],
            budget_constraint=Decimal("100.00"),
            implementation_timeline="immediate"
        )

    @pytest.fixture
    def sample_field_characteristics(self):
        """Create sample field characteristics."""
        return {
            "soil_type": "clay_loam",
            "slope_percent": 2.5,
            "drainage_class": "moderate",
            "organic_matter_percent": 3.2,
            "field_size_acres": 40.0,
            "current_practices": [],
            "equipment_available": ["Tractor", "Planter", "Sprayer"]
        }

    @pytest.fixture
    def sample_conservation_practice(self):
        """Create sample conservation practice."""
        return ConservationPractice(
            practice_id=uuid4(),
            practice_name="Cover Crops",
            practice_type=ConservationPracticeType.COVER_CROPS,
            description="Planting cover crops to protect soil and retain moisture",
            implementation_cost=Decimal("35.00"),
            water_savings_percent=20.0,
            soil_health_impact=SoilHealthImpact.HIGHLY_POSITIVE,
            equipment_requirements=[
                EquipmentRequirement(
                    equipment_type="Seeder",
                    equipment_name="Seeder",
                    availability=True,
                    rental_cost_per_day=None
                )
            ],
            implementation_time_days=7,
            maintenance_cost_per_year=Decimal("10.00"),
            effectiveness_rating=8.0
        )

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        assert not service.initialized
        assert service.practices_database is None
        
        await service.initialize()
        
        assert service.initialized
        assert service.practices_database is not None
        assert "practices" in service.practices_database

    @pytest.mark.asyncio
    async def test_service_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        assert service.initialized
        
        await service.cleanup()
        assert not service.initialized

    @pytest.mark.asyncio
    async def test_get_conservation_recommendations_success(self, service, sample_request):
        """Test successful conservation practice recommendations."""
        await service.initialize()
        
        with patch.object(service, '_get_field_characteristics', return_value={
            "soil_type": "clay_loam",
            "slope_percent": 2.5,
            "drainage_class": "moderate",
            "organic_matter_percent": 3.2,
            "field_size_acres": 40.0,
            "current_practices": [],
            "equipment_available": ["Tractor", "Planter", "Sprayer"]
        }):
            recommendations = await service.get_conservation_recommendations(sample_request)
            
            assert isinstance(recommendations, list)
            assert len(recommendations) <= 5  # Top 5 recommendations
            
            for recommendation in recommendations:
                assert isinstance(recommendation, ConservationPracticeResponse)
                assert recommendation.practice is not None
                assert recommendation.implementation_plan is not None
                assert recommendation.expected_benefits is not None
                assert recommendation.cost_benefit_analysis is not None

    @pytest.mark.asyncio
    async def test_get_conservation_recommendations_error_handling(self, service, sample_request):
        """Test error handling in conservation recommendations."""
        await service.initialize()
        
        with patch.object(service, '_get_field_characteristics', side_effect=Exception("Database error")):
            with pytest.raises(Exception):
                await service.get_conservation_recommendations(sample_request)

    @pytest.mark.asyncio
    async def test_calculate_conservation_benefits(self, service, sample_field_characteristics):
        """Test conservation benefits calculation."""
        await service.initialize()
        
        field_id = uuid4()
        practices = [
            ConservationPracticeRequest(
                field_id=field_id,
                soil_type="clay_loam",
                slope_percent=2.5,
                drainage_class="moderate",
                current_practices=[],
                available_equipment=["Tractor"],
                budget_constraint=Decimal("100.00"),
                implementation_timeline="immediate"
            )
        ]
        
        with patch.object(service, '_get_field_characteristics', return_value=sample_field_characteristics):
            benefits = await service.calculate_conservation_benefits(field_id, practices)
            
            assert isinstance(benefits, dict)
            assert "field_id" in benefits
            assert "individual_practices" in benefits
            assert "combined_benefits" in benefits
            assert "total_water_savings_percent" in benefits
            assert "total_implementation_cost" in benefits
            assert "implementation_timeline" in benefits
            assert "roi_analysis" in benefits
            assert "recommendations" in benefits

    @pytest.mark.asyncio
    async def test_get_available_practices(self, service):
        """Test getting available conservation practices."""
        await service.initialize()
        
        practices = await service.get_available_practices()
        
        assert isinstance(practices, list)
        assert len(practices) > 0
        
        for practice in practices:
            assert "practice_type" in practice
            assert "name" in practice
            assert "description" in practice
            assert "water_savings_range" in practice
            assert "soil_health_impact" in practice
            assert "implementation_cost_range" in practice
            assert "equipment_required" in practice

    @pytest.mark.asyncio
    async def test_filter_practices_by_field_conditions(self, service, sample_request, sample_field_characteristics):
        """Test filtering practices by field conditions."""
        await service.initialize()
        
        suitable_practices = await service._filter_practices_by_field_conditions(
            sample_request, sample_field_characteristics
        )
        
        assert isinstance(suitable_practices, list)
        
        for practice in suitable_practices:
            assert isinstance(practice, ConservationPractice)
            assert practice.practice_name is not None
            assert practice.practice_type is not None
            assert practice.water_savings_percent >= 0
            assert practice.effectiveness_rating >= 0

    @pytest.mark.asyncio
    async def test_score_practices(self, service, sample_request, sample_field_characteristics):
        """Test practice scoring functionality."""
        await service.initialize()
        
        # Create mock practices
        practices = [
            ConservationPractice(
                practice_id=uuid4(),
                practice_name="Test Practice 1",
                practice_type=ConservationPracticeType.COVER_CROPS,
                description="Test practice",
                implementation_cost=Decimal("50.00"),
                water_savings_percent=25.0,
                soil_health_impact=SoilHealthImpact.HIGHLY_POSITIVE,
                equipment_requirements=[],
                implementation_time_days=7,
                maintenance_cost_per_year=Decimal("10.00"),
                effectiveness_rating=8.0
            )
        ]
        
        scored_practices = await service._score_practices(practices, sample_request, sample_field_characteristics)
        
        assert isinstance(scored_practices, list)
        assert len(scored_practices) == len(practices)
        
        for practice, score in scored_practices:
            assert isinstance(practice, ConservationPractice)
            assert isinstance(score, (int, float))
            assert score >= 0

    @pytest.mark.asyncio
    async def test_create_implementation_plan(self, service, sample_request, sample_field_characteristics, sample_conservation_practice):
        """Test implementation plan creation."""
        await service.initialize()
        
        plan = await service._create_implementation_plan(
            sample_conservation_practice, sample_request, sample_field_characteristics
        )
        
        assert isinstance(plan, dict)
        assert "timeline" in plan
        assert "steps" in plan
        assert "resources_needed" in plan
        assert "cost_breakdown" in plan
        
        assert "preparation" in plan["timeline"]
        assert "implementation" in plan["timeline"]
        assert "establishment" in plan["timeline"]
        
        assert isinstance(plan["steps"], list)
        assert len(plan["steps"]) > 0
        
        assert "equipment" in plan["resources_needed"]
        assert "materials" in plan["resources_needed"]
        assert "labor" in plan["resources_needed"]

    @pytest.mark.asyncio
    async def test_calculate_expected_benefits(self, service, sample_field_characteristics, sample_conservation_practice):
        """Test expected benefits calculation."""
        await service.initialize()
        
        benefits = await service._calculate_expected_benefits(
            sample_conservation_practice, sample_field_characteristics
        )
        
        assert isinstance(benefits, dict)
        assert "water_savings" in benefits
        assert "soil_health" in benefits
        assert "crop_yield" in benefits
        assert "environmental" in benefits
        
        assert "percentage" in benefits["water_savings"]
        assert "gallons_per_year" in benefits["water_savings"]
        assert "cost_savings_per_year" in benefits["water_savings"]
        
        assert "impact" in benefits["soil_health"]
        assert "organic_matter_increase" in benefits["soil_health"]
        assert "erosion_reduction" in benefits["soil_health"]

    @pytest.mark.asyncio
    async def test_perform_cost_benefit_analysis(self, service, sample_field_characteristics, sample_conservation_practice):
        """Test cost-benefit analysis."""
        await service.initialize()
        
        analysis = await service._perform_cost_benefit_analysis(
            sample_conservation_practice, sample_field_characteristics
        )
        
        assert isinstance(analysis, dict)
        assert "total_implementation_cost" in analysis
        assert "annual_maintenance_cost" in analysis
        assert "annual_benefits" in analysis
        assert "net_annual_benefit" in analysis
        assert "roi_percentage" in analysis
        assert "payback_period_years" in analysis
        assert "break_even_point" in analysis
        assert "recommendation" in analysis
        
        assert isinstance(analysis["total_implementation_cost"], Decimal)
        assert isinstance(analysis["annual_benefits"], Decimal)
        assert isinstance(analysis["roi_percentage"], (int, float))

    @pytest.mark.asyncio
    async def test_practice_suitability_checks(self, service, sample_request, sample_field_characteristics):
        """Test practice suitability checking."""
        await service.initialize()
        
        # Test no-till suitability
        is_suitable = await service._is_practice_suitable(
            ConservationPracticeType.NO_TILL, sample_request, sample_field_characteristics
        )
        assert isinstance(is_suitable, bool)
        
        # Test mulching suitability
        is_suitable = await service._is_practice_suitable(
            ConservationPracticeType.MULCHING, sample_request, sample_field_characteristics
        )
        assert isinstance(is_suitable, bool)
        
        # Test irrigation efficiency suitability
        is_suitable = await service._is_practice_suitable(
            ConservationPracticeType.IRRIGATION_EFFICIENCY, sample_request, sample_field_characteristics
        )
        assert isinstance(is_suitable, bool)

    def test_get_implementation_time(self, service):
        """Test implementation time calculation."""
        time_map = {
            ConservationPracticeType.COVER_CROPS: 7,
            ConservationPracticeType.NO_TILL: 3,
            ConservationPracticeType.MULCHING: 5,
            ConservationPracticeType.IRRIGATION_EFFICIENCY: 14,
            ConservationPracticeType.SOIL_AMENDMENTS: 10
        }
        
        for practice_type, expected_time in time_map.items():
            actual_time = service._get_implementation_time(practice_type)
            assert actual_time == expected_time

    def test_get_materials_needed(self, service):
        """Test materials needed calculation."""
        materials_map = {
            ConservationPracticeType.COVER_CROPS: ["Cover crop seed", "Fertilizer"],
            ConservationPracticeType.NO_TILL: ["Herbicide", "No-till planter"],
            ConservationPracticeType.MULCHING: ["Mulch material", "Mulch spreader"],
            ConservationPracticeType.IRRIGATION_EFFICIENCY: ["Drip tape", "Filters", "Sensors"],
            ConservationPracticeType.SOIL_AMENDMENTS: ["Compost", "Organic matter"]
        }
        
        for practice_type, expected_materials in materials_map.items():
            actual_materials = service._get_materials_needed(practice_type)
            assert actual_materials == expected_materials

    @pytest.mark.asyncio
    async def test_get_practice_type_data(self, service):
        """Test getting practice type data."""
        await service.initialize()
        
        for practice_type in ConservationPracticeType:
            data = await service._get_practice_type_data(practice_type)
            
            assert isinstance(data, dict)
            assert "practice_type" in data
            assert "name" in data
            assert "description" in data
            assert "water_savings_range" in data
            assert "soil_health_impact" in data
            assert "implementation_cost_range" in data
            assert "equipment_required" in data
            assert "suitable_conditions" in data
            assert "benefits" in data

    def test_get_suitable_conditions(self, service):
        """Test getting suitable conditions for practice types."""
        for practice_type in ConservationPracticeType:
            conditions = service._get_suitable_conditions(practice_type)
            assert isinstance(conditions, list)
            assert len(conditions) > 0

    def test_get_practice_benefits(self, service):
        """Test getting practice benefits."""
        for practice_type in ConservationPracticeType:
            benefits = service._get_practice_benefits(practice_type)
            assert isinstance(benefits, list)
            assert len(benefits) > 0

    @pytest.mark.asyncio
    async def test_combined_benefits_calculation(self, service, sample_field_characteristics):
        """Test combined benefits calculation for multiple practices."""
        await service.initialize()
        
        practice_benefits = [
            {
                "practice_type": "cover_crops",
                "water_savings_percent": 20.0,
                "implementation_cost": Decimal("1400.00"),
                "soil_health_score": 8.0,
                "annual_benefit": Decimal("400.00")
            },
            {
                "practice_type": "no_till",
                "water_savings_percent": 15.0,
                "implementation_cost": Decimal("0.00"),
                "soil_health_score": 9.0,
                "annual_benefit": Decimal("300.00")
            }
        ]
        
        combined = await service._calculate_combined_benefits(practice_benefits, sample_field_characteristics)
        
        assert isinstance(combined, dict)
        assert "effective_water_savings_percent" in combined
        assert "total_implementation_cost" in combined
        assert "total_annual_benefit" in combined
        assert "net_annual_benefit" in combined
        assert "synergy_factor" in combined
        assert "recommended_combination" in combined

    @pytest.mark.asyncio
    async def test_implementation_timeline_generation(self, service):
        """Test implementation timeline generation."""
        await service.initialize()
        
        practices = [
            ConservationPracticeRequest(
                field_id=uuid4(),
                soil_type="clay_loam",
                slope_percent=2.5,
                drainage_class="moderate",
                current_practices=[],
                available_equipment=["Tractor"],
                budget_constraint=Decimal("100.00"),
                implementation_timeline="immediate"
            ),
            ConservationPracticeRequest(
                field_id=uuid4(),
                soil_type="clay_loam",
                slope_percent=2.5,
                drainage_class="moderate",
                current_practices=[],
                available_equipment=["Tractor"],
                budget_constraint=Decimal("100.00"),
                implementation_timeline="immediate"
            )
        ]
        
        timeline = await service._generate_implementation_timeline(practices)
        
        assert isinstance(timeline, dict)
        assert "phase_1" in timeline
        assert "phase_2" in timeline
        assert "monitoring" in timeline
        
        assert "practices" in timeline["phase_1"]
        assert "timeline" in timeline["phase_1"]
        assert "priority" in timeline["phase_1"]

    @pytest.mark.asyncio
    async def test_roi_analysis_calculation(self, service, sample_field_characteristics):
        """Test ROI analysis calculation."""
        await service.initialize()
        
        total_cost = Decimal("2000.00")
        combined_benefits = {
            "total_annual_benefit": Decimal("800.00")
        }
        
        roi_analysis = await service._calculate_roi_analysis(
            total_cost, combined_benefits, sample_field_characteristics
        )
        
        assert isinstance(roi_analysis, dict)
        assert "total_investment" in roi_analysis
        assert "annual_return" in roi_analysis
        assert "annual_cost" in roi_analysis
        assert "net_annual_return" in roi_analysis
        assert "roi_percentage" in roi_analysis
        assert "payback_period_years" in roi_analysis
        assert "investment_grade" in roi_analysis

    @pytest.mark.asyncio
    async def test_implementation_recommendations_generation(self, service, sample_field_characteristics):
        """Test implementation recommendations generation."""
        await service.initialize()
        
        practices = [
            ConservationPracticeRequest(
                field_id=uuid4(),
                soil_type="clay_loam",
                slope_percent=2.5,
                drainage_class="moderate",
                current_practices=[],
                available_equipment=["Tractor"],
                budget_constraint=Decimal("100.00"),
                implementation_timeline="immediate"
            )
        ]
        
        recommendations = await service._generate_implementation_recommendations(
            practices, sample_field_characteristics
        )
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        for recommendation in recommendations:
            assert isinstance(recommendation, str)
            assert len(recommendation) > 0

    @pytest.mark.asyncio
    async def test_service_error_handling(self, service):
        """Test service error handling."""
        # Test initialization error
        with patch.object(service, '_load_practices_database', side_effect=Exception("Database error")):
            with pytest.raises(Exception):
                await service.initialize()

    @pytest.mark.asyncio
    async def test_conservation_practice_types_coverage(self, service):
        """Test that all conservation practice types are covered."""
        await service.initialize()
        
        available_practices = await service.get_available_practices()
        practice_types = [practice["practice_type"] for practice in available_practices]
        
        # Check that all enum values are covered
        for practice_type in ConservationPracticeType:
            assert practice_type.value in practice_types

    @pytest.mark.asyncio
    async def test_water_savings_percentage_validation(self, service, sample_field_characteristics, sample_conservation_practice):
        """Test water savings percentage validation."""
        await service.initialize()
        
        # Test with valid percentage
        sample_conservation_practice.water_savings_percent = 25.0
        benefits = await service._calculate_expected_benefits(
            sample_conservation_practice, sample_field_characteristics
        )
        
        assert benefits["water_savings"]["percentage"] == 25.0
        
        # Test with edge case (100%)
        sample_conservation_practice.water_savings_percent = 100.0
        benefits = await service._calculate_expected_benefits(
            sample_conservation_practice, sample_field_characteristics
        )
        
        assert benefits["water_savings"]["percentage"] == 100.0

    @pytest.mark.asyncio
    async def test_equipment_availability_scoring(self, service, sample_request, sample_field_characteristics):
        """Test equipment availability scoring in practice scoring."""
        await service.initialize()
        
        # Create practice with equipment requirements
        practice = ConservationPractice(
            practice_id=uuid4(),
            practice_name="Test Practice",
            practice_type=ConservationPracticeType.COVER_CROPS,
            description="Test practice",
            implementation_cost=Decimal("50.00"),
            water_savings_percent=25.0,
            soil_health_impact=SoilHealthImpact.HIGHLY_POSITIVE,
            equipment_requirements=[
                EquipmentRequirement(
                    equipment_type="Seeder",
                    equipment_name="Seeder",
                    availability=True,  # Available
                    rental_cost_per_day=None
                ),
                EquipmentRequirement(
                    equipment_type="Termination Equipment",
                    equipment_name="Termination Equipment",
                    availability=False,  # Not available
                    rental_cost_per_day=Decimal("50.00")
                )
            ],
            implementation_time_days=7,
            maintenance_cost_per_year=Decimal("10.00"),
            effectiveness_rating=8.0
        )
        
        scored_practices = await service._score_practices([practice], sample_request, sample_field_characteristics)
        
        assert len(scored_practices) == 1
        practice, score = scored_practices[0]
        
        # Score should be positive (equipment availability contributes to score)
        assert score > 0


class TestMoistureConservationServiceIntegration:
    """Integration tests for MoistureConservationService."""

    @pytest.fixture
    def service(self):
        """Create service instance for integration testing."""
        return MoistureConservationService()

    @pytest.mark.asyncio
    async def test_full_workflow_integration(self, service):
        """Test complete workflow from request to recommendations."""
        await service.initialize()
        
        # Create comprehensive request
        request = ConservationPracticeRequest(
            field_id=uuid4(),
            soil_type="sandy_loam",
            slope_percent=5.0,
            drainage_class="good",
            current_practices=["conventional_tillage"],
            available_equipment=["Tractor", "Planter", "Sprayer", "Seeder"],
            budget_constraint=Decimal("200.00"),
            implementation_timeline="immediate"
        )
        
        # Get recommendations
        recommendations = await service.get_conservation_recommendations(request)
        
        # Verify recommendations
        assert len(recommendations) > 0
        assert len(recommendations) <= 5
        
        # Test benefit calculation for recommended practices
        practice_requests = [request]  # Simplified for testing
        benefits = await service.calculate_conservation_benefits(request.field_id, practice_requests)
        
        assert benefits["field_id"] == request.field_id
        assert "total_water_savings_percent" in benefits
        assert "roi_analysis" in benefits
        
        # Test available practices
        available_practices = await service.get_available_practices()
        assert len(available_practices) > 0
        
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_service_lifecycle(self, service):
        """Test complete service lifecycle."""
        # Initial state
        assert not service.initialized
        
        # Initialize
        await service.initialize()
        assert service.initialized
        
        # Use service
        practices = await service.get_available_practices()
        assert len(practices) > 0
        
        # Cleanup
        await service.cleanup()
        assert not service.initialized

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, service):
        """Test handling of concurrent requests."""
        await service.initialize()
        
        # Create multiple requests
        requests = [
            ConservationPracticeRequest(
                field_id=uuid4(),
                soil_type="clay_loam",
                slope_percent=2.5,
                drainage_class="moderate",
                current_practices=[],
                available_equipment=["Tractor"],
                budget_constraint=Decimal("100.00"),
                implementation_timeline="immediate"
            )
            for _ in range(5)
        ]
        
        # Process requests concurrently
        tasks = [
            service.get_conservation_recommendations(request)
            for request in requests
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify all requests completed successfully
        assert len(results) == 5
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0
        
        await service.cleanup()


class TestMoistureConservationServicePerformance:
    """Performance tests for MoistureConservationService."""

    @pytest.fixture
    def service(self):
        """Create service instance for performance testing."""
        return MoistureConservationService()

    @pytest.mark.asyncio
    async def test_response_time_requirements(self, service):
        """Test that response times meet requirements."""
        await service.initialize()
        
        request = ConservationPracticeRequest(
            field_id=uuid4(),
            soil_type="clay_loam",
            slope_percent=2.5,
            drainage_class="moderate",
            current_practices=[],
            available_equipment=["Tractor"],
            budget_constraint=Decimal("100.00"),
            implementation_timeline="immediate"
        )
        
        import time
        start_time = time.time()
        
        recommendations = await service.get_conservation_recommendations(request)
        
        elapsed_time = time.time() - start_time
        
        # Should respond within 3 seconds (as per requirements)
        assert elapsed_time < 3.0, f"Response time {elapsed_time}s exceeds 3s requirement"
        assert len(recommendations) > 0
        
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_memory_usage(self, service):
        """Test memory usage during operation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        await service.initialize()
        
        # Perform multiple operations
        for _ in range(10):
            request = ConservationPracticeRequest(
                field_id=uuid4(),
                soil_type="clay_loam",
                slope_percent=2.5,
                drainage_class="moderate",
                current_practices=[],
                available_equipment=["Tractor"],
                budget_constraint=Decimal("100.00"),
                implementation_timeline="immediate"
            )
            
            await service.get_conservation_recommendations(request)
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024, f"Memory increase {memory_increase / 1024 / 1024:.1f}MB exceeds 50MB limit"
        
        await service.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])