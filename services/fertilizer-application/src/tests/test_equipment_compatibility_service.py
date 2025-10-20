"""
Unit tests for Equipment Compatibility Service.
"""

import pytest
import asyncio
from src.services.equipment_compatibility_service import EquipmentCompatibilityService
from src.models.equipment_models import (
    Equipment, EquipmentCategory, EquipmentStatus, MaintenanceLevel,
    FertilizerFormulation, ApplicationMethodType, CompatibilityLevel
)


class TestEquipmentCompatibilityService:
    """Test suite for Equipment Compatibility Service."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return EquipmentCompatibilityService()

    @pytest.fixture
    def sample_equipment_spreader(self):
        """Create sample spreader equipment."""
        return Equipment(
            equipment_id="test_spreader_1",
            name="Test Broadcast Spreader",
            category=EquipmentCategory.SPREADING,
            capacity=500.0,
            capacity_unit="cubic_feet",
            status=EquipmentStatus.OPERATIONAL,
            maintenance_level=MaintenanceLevel.BASIC
        )

    @pytest.fixture
    def sample_equipment_sprayer(self):
        """Create sample sprayer equipment."""
        return Equipment(
            equipment_id="test_sprayer_1",
            name="Test Boom Sprayer",
            category=EquipmentCategory.SPRAYING,
            capacity=400.0,
            capacity_unit="gallons",
            status=EquipmentStatus.OPERATIONAL,
            maintenance_level=MaintenanceLevel.INTERMEDIATE
        )

    @pytest.fixture
    def sample_equipment_injector(self):
        """Create sample injection equipment."""
        return Equipment(
            equipment_id="test_injector_1",
            name="Test Injection System",
            category=EquipmentCategory.INJECTION,
            capacity=100.0,
            capacity_unit="gph",
            status=EquipmentStatus.OPERATIONAL,
            maintenance_level=MaintenanceLevel.ADVANCED
        )

    @pytest.mark.asyncio
    async def test_assess_compatibility_granular_spreader(self, service, sample_equipment_spreader):
        """Test compatibility assessment for granular fertilizer with spreader."""
        compatibility_matrix = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={"wind_speed_mph": 5, "temperature_f": 70, "humidity_percent": 50},
            cost_constraints=None
        )

        # Assertions
        assert compatibility_matrix is not None
        assert compatibility_matrix.equipment_id == "test_spreader_1"
        assert compatibility_matrix.fertilizer_type == FertilizerFormulation.GRANULAR
        assert compatibility_matrix.application_method == ApplicationMethodType.BROADCAST
        assert 0.0 <= compatibility_matrix.overall_compatibility_score <= 1.0
        assert compatibility_matrix.compatibility_level in [
            CompatibilityLevel.HIGHLY_COMPATIBLE,
            CompatibilityLevel.COMPATIBLE,
            CompatibilityLevel.MODERATELY_COMPATIBLE
        ]
        assert len(compatibility_matrix.compatibility_factors) == 8
        assert compatibility_matrix.overall_compatibility_score >= 0.7  # Should be highly compatible

    @pytest.mark.asyncio
    async def test_assess_compatibility_liquid_sprayer(self, service, sample_equipment_sprayer):
        """Test compatibility assessment for liquid fertilizer with sprayer."""
        compatibility_matrix = await service.assess_compatibility(
            equipment=sample_equipment_sprayer,
            fertilizer_type=FertilizerFormulation.LIQUID,
            application_method=ApplicationMethodType.FOLIAR,
            field_size_acres=150.0,
            soil_type="clay",
            weather_conditions={"wind_speed_mph": 8, "temperature_f": 75, "humidity_percent": 60},
            cost_constraints=50000.0
        )

        # Assertions
        assert compatibility_matrix is not None
        assert compatibility_matrix.equipment_id == "test_sprayer_1"
        assert compatibility_matrix.fertilizer_type == FertilizerFormulation.LIQUID
        assert compatibility_matrix.overall_compatibility_score >= 0.7
        assert len(compatibility_matrix.compatibility_factors) == 8

    @pytest.mark.asyncio
    async def test_assess_compatibility_incompatible_combination(self, service, sample_equipment_spreader):
        """Test compatibility assessment for incompatible fertilizer-equipment combination."""
        compatibility_matrix = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.LIQUID,  # Incompatible with spreader
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={},
            cost_constraints=None
        )

        # Assertions
        assert compatibility_matrix is not None
        assert compatibility_matrix.overall_compatibility_score < 0.5  # Should have low score
        assert compatibility_matrix.compatibility_level in [
            CompatibilityLevel.POORLY_COMPATIBLE,
            CompatibilityLevel.INCOMPATIBLE
        ]

    @pytest.mark.asyncio
    async def test_compatibility_factors_weights(self, service, sample_equipment_spreader):
        """Test that compatibility factors have correct weights."""
        compatibility_matrix = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={},
            cost_constraints=None
        )

        # Check that all factors are present
        factor_names = [f.factor_name for f in compatibility_matrix.compatibility_factors]
        expected_factors = [
            "fertilizer_type_compatibility",
            "field_size_suitability",
            "soil_type_compatibility",
            "application_rate_capability",
            "weather_resilience",
            "cost_effectiveness",
            "labor_requirements",
            "equipment_availability"
        ]

        for expected in expected_factors:
            assert expected in factor_names

        # Check weights sum to approximately 1.0
        total_weight = sum(f.factor_weight for f in compatibility_matrix.compatibility_factors)
        assert 0.99 <= total_weight <= 1.01

    @pytest.mark.asyncio
    async def test_field_size_scoring(self, service, sample_equipment_spreader):
        """Test field size scoring logic."""
        # Test with optimal field size
        compat_optimal = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,  # Optimal for medium spreader
            soil_type="loam",
            weather_conditions={},
            cost_constraints=None
        )

        # Test with sub-optimal field size
        compat_small = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=10.0,  # Too small
            soil_type="loam",
            weather_conditions={},
            cost_constraints=None
        )

        # Optimal field size should have higher field_size_score
        assert compat_optimal.field_size_score > compat_small.field_size_score

    @pytest.mark.asyncio
    async def test_weather_resilience_scoring(self, service, sample_equipment_sprayer):
        """Test weather resilience scoring."""
        # Test with good weather
        compat_good_weather = await service.assess_compatibility(
            equipment=sample_equipment_sprayer,
            fertilizer_type=FertilizerFormulation.LIQUID,
            application_method=ApplicationMethodType.FOLIAR,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={"wind_speed_mph": 5, "temperature_f": 70, "humidity_percent": 50},
            cost_constraints=None
        )

        # Test with poor weather (high wind)
        compat_poor_weather = await service.assess_compatibility(
            equipment=sample_equipment_sprayer,
            fertilizer_type=FertilizerFormulation.LIQUID,
            application_method=ApplicationMethodType.FOLIAR,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={"wind_speed_mph": 20, "temperature_f": 70, "humidity_percent": 50},
            cost_constraints=None
        )

        # Good weather should have higher weather_score
        assert compat_good_weather.weather_score > compat_poor_weather.weather_score

    @pytest.mark.asyncio
    async def test_recommend_equipment(self, service):
        """Test equipment recommendation functionality."""
        recommendations = await service.recommend_equipment(
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={"wind_speed_mph": 5, "temperature_f": 70},
            cost_constraints=None,
            available_equipment=None,
            top_n=5
        )

        # Assertions
        assert recommendations is not None
        assert len(recommendations) > 0
        assert len(recommendations) <= 5  # Should return at most top_n

        # Check that recommendations are sorted by score
        scores = [rec.overall_score for rec in recommendations]
        assert scores == sorted(scores, reverse=True)

        # Check that each recommendation has required fields
        for i, rec in enumerate(recommendations):
            assert rec.equipment is not None
            assert rec.compatibility_matrix is not None
            assert rec.cost_benefit is not None
            assert rec.ranking == i + 1
            assert len(rec.justification) > 0
            assert len(rec.advantages) > 0
            assert len(rec.implementation_considerations) > 0
            assert len(rec.training_requirements) > 0

    @pytest.mark.asyncio
    async def test_recommend_equipment_with_cost_constraint(self, service):
        """Test equipment recommendation with cost constraints."""
        recommendations = await service.recommend_equipment(
            fertilizer_type=FertilizerFormulation.LIQUID,
            application_method=ApplicationMethodType.FOLIAR,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={},
            cost_constraints=20000.0,  # Budget constraint
            available_equipment=None,
            top_n=5
        )

        # All recommendations should have cost_benefit data
        for rec in recommendations:
            assert rec.cost_benefit is not None
            assert rec.cost_benefit.initial_investment >= 0
            assert rec.cost_benefit.cost_per_acre >= 0

    @pytest.mark.asyncio
    async def test_get_compatibility_matrix_full(self, service):
        """Test getting full compatibility matrix."""
        matrix_data = await service.get_compatibility_matrix_full(
            fertilizer_types=None,  # All types
            equipment_categories=None  # All categories
        )

        # Assertions
        assert matrix_data is not None
        assert "compatibility_matrix" in matrix_data
        assert "fertilizer_types" in matrix_data
        assert "equipment_categories" in matrix_data

        # Check that all fertilizer types are included
        assert len(matrix_data["fertilizer_types"]) > 0

        # Check that compatibility data exists for combinations
        for fert_type in matrix_data["fertilizer_types"]:
            assert fert_type in matrix_data["compatibility_matrix"]

    @pytest.mark.asyncio
    async def test_get_compatibility_matrix_filtered(self, service):
        """Test getting filtered compatibility matrix."""
        matrix_data = await service.get_compatibility_matrix_full(
            fertilizer_types=[FertilizerFormulation.GRANULAR, FertilizerFormulation.LIQUID],
            equipment_categories=[EquipmentCategory.SPREADING, EquipmentCategory.SPRAYING]
        )

        # Should only include specified types
        assert len(matrix_data["fertilizer_types"]) == 2
        assert len(matrix_data["equipment_categories"]) == 2

    @pytest.mark.asyncio
    async def test_optimize_equipment_selection(self, service):
        """Test equipment selection optimization for multiple fields."""
        fields = [
            {
                "size_acres": 100.0,
                "fertilizer_type": FertilizerFormulation.GRANULAR,
                "application_method": ApplicationMethodType.BROADCAST,
                "soil_type": "loam"
            },
            {
                "size_acres": 75.0,
                "fertilizer_type": FertilizerFormulation.LIQUID,
                "application_method": ApplicationMethodType.FOLIAR,
                "soil_type": "clay"
            },
            {
                "size_acres": 50.0,
                "fertilizer_type": FertilizerFormulation.GRANULAR,
                "application_method": ApplicationMethodType.BROADCAST,
                "soil_type": "sandy"
            }
        ]

        optimization_result = await service.optimize_equipment_selection(
            fields=fields,
            budget_constraint=100000.0,
            existing_equipment=None
        )

        # Assertions
        assert optimization_result is not None
        assert "field_requirements" in optimization_result
        assert "equipment_needs" in optimization_result
        assert "recommended_equipment" in optimization_result
        assert "implementation_plan" in optimization_result
        assert "total_cost" in optimization_result
        assert "budget_utilization" in optimization_result

        # Check field requirements
        assert optimization_result["field_requirements"]["total_acres"] == 225.0
        assert optimization_result["field_requirements"]["field_count"] == 3

        # Check that budget is respected
        assert optimization_result["total_cost"] <= 100000.0

    @pytest.mark.asyncio
    async def test_cost_benefit_calculation(self, service, sample_equipment_spreader):
        """Test cost-benefit calculation."""
        cost_benefit = await service._calculate_cost_benefit(
            equipment=sample_equipment_spreader,
            field_size_acres=100.0
        )

        # Assertions
        assert cost_benefit is not None
        assert cost_benefit.initial_investment > 0
        assert cost_benefit.annual_operating_cost > 0
        assert cost_benefit.annual_savings >= 0
        assert cost_benefit.payback_period_years >= 0
        assert cost_benefit.cost_per_acre > 0
        assert cost_benefit.break_even_acres > 0

    @pytest.mark.asyncio
    async def test_compatibility_level_determination(self, service):
        """Test compatibility level determination from scores."""
        # Test highly compatible
        level = service._determine_compatibility_level(0.95)
        assert level == CompatibilityLevel.HIGHLY_COMPATIBLE

        # Test compatible
        level = service._determine_compatibility_level(0.75)
        assert level == CompatibilityLevel.COMPATIBLE

        # Test moderately compatible
        level = service._determine_compatibility_level(0.60)
        assert level == CompatibilityLevel.MODERATELY_COMPATIBLE

        # Test poorly compatible
        level = service._determine_compatibility_level(0.40)
        assert level == CompatibilityLevel.POORLY_COMPATIBLE

        # Test incompatible
        level = service._determine_compatibility_level(0.20)
        assert level == CompatibilityLevel.INCOMPATIBLE

    @pytest.mark.asyncio
    async def test_equipment_type_determination(self, service):
        """Test equipment type determination."""
        # Test small spreader
        equipment = Equipment(
            equipment_id="test",
            name="Test",
            category=EquipmentCategory.SPREADING,
            capacity=150.0,
            status=EquipmentStatus.OPERATIONAL
        )
        eq_type = service._determine_equipment_type(equipment)
        assert eq_type == "broadcast_spreader_small"

        # Test medium spreader
        equipment.capacity = 500.0
        eq_type = service._determine_equipment_type(equipment)
        assert eq_type == "broadcast_spreader_medium"

        # Test large spreader
        equipment.capacity = 1500.0
        eq_type = service._determine_equipment_type(equipment)
        assert eq_type == "broadcast_spreader_large"

    @pytest.mark.asyncio
    async def test_constraints_identification(self, service, sample_equipment_spreader):
        """Test identification of compatibility constraints."""
        constraints = await service._identify_constraints(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0
        )

        # Should return list of constraints
        assert isinstance(constraints, list)

    @pytest.mark.asyncio
    async def test_warnings_identification(self, service, sample_equipment_spreader):
        """Test identification of warnings."""
        # Test with good compatibility
        warnings_good = await service._identify_warnings(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            compatibility_level=CompatibilityLevel.HIGHLY_COMPATIBLE
        )

        # Test with poor compatibility
        warnings_poor = await service._identify_warnings(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.LIQUID,  # Incompatible
            compatibility_level=CompatibilityLevel.INCOMPATIBLE
        )

        # Poor compatibility should have more warnings
        assert len(warnings_poor) >= len(warnings_good)

    @pytest.mark.asyncio
    async def test_equipment_status_impact(self, service):
        """Test that equipment status impacts compatibility."""
        # Operational equipment
        equipment_operational = Equipment(
            equipment_id="test_op",
            name="Operational Equipment",
            category=EquipmentCategory.SPREADING,
            capacity=500.0,
            status=EquipmentStatus.OPERATIONAL,
            maintenance_level=MaintenanceLevel.BASIC
        )

        # Out of service equipment
        equipment_oos = Equipment(
            equipment_id="test_oos",
            name="Out of Service Equipment",
            category=EquipmentCategory.SPREADING,
            capacity=500.0,
            status=EquipmentStatus.OUT_OF_SERVICE,
            maintenance_level=MaintenanceLevel.BASIC
        )

        # Assess both
        compat_operational = await service.assess_compatibility(
            equipment=equipment_operational,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="loam"
        )

        compat_oos = await service.assess_compatibility(
            equipment=equipment_oos,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="loam"
        )

        # Operational should have higher score
        assert compat_operational.overall_compatibility_score > compat_oos.overall_compatibility_score

    @pytest.mark.asyncio
    async def test_edge_cases(self, service, sample_equipment_spreader):
        """Test edge cases and error handling."""
        # Test with very small field
        compat_small = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=0.5,
            soil_type="loam"
        )
        assert compat_small is not None

        # Test with very large field
        compat_large = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=5000.0,
            soil_type="loam"
        )
        assert compat_large is not None

        # Test with minimal weather data
        compat_no_weather = await service.assess_compatibility(
            equipment=sample_equipment_spreader,
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="loam",
            weather_conditions={}
        )
        assert compat_no_weather is not None

    @pytest.mark.asyncio
    async def test_agricultural_validation_scenarios(self, service):
        """Test realistic agricultural scenarios."""
        # Scenario 1: Small farm with granular fertilizer
        recommendations = await service.recommend_equipment(
            fertilizer_type=FertilizerFormulation.GRANULAR,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=25.0,
            soil_type="loam",
            weather_conditions={"wind_speed_mph": 8},
            cost_constraints=10000.0,
            top_n=3
        )
        assert len(recommendations) > 0

        # Scenario 2: Large farm with liquid fertilizer
        recommendations = await service.recommend_equipment(
            fertilizer_type=FertilizerFormulation.LIQUID,
            application_method=ApplicationMethodType.FOLIAR,
            field_size_acres=500.0,
            soil_type="clay",
            weather_conditions={"wind_speed_mph": 5, "temperature_f": 75},
            cost_constraints=100000.0,
            top_n=3
        )
        assert len(recommendations) > 0

        # Scenario 3: Organic fertilizer application
        recommendations = await service.recommend_equipment(
            fertilizer_type=FertilizerFormulation.ORGANIC,
            application_method=ApplicationMethodType.BROADCAST,
            field_size_acres=100.0,
            soil_type="sandy",
            weather_conditions={},
            cost_constraints=None,
            top_n=3
        )
        assert len(recommendations) > 0


class TestEquipmentCompatibilityDatabase:
    """Test suite for Equipment Compatibility Database."""

    @pytest.fixture
    def db(self):
        """Create database instance for testing."""
        from src.database.equipment_compatibility_db import EquipmentCompatibilityDatabase
        return EquipmentCompatibilityDatabase()

    def test_database_initialization(self, db):
        """Test that database initializes correctly."""
        assert db.equipment_catalog is not None
        assert db.compatibility_matrix is not None
        assert db.cost_ranges is not None
        assert db.application_requirements is not None

        # Check that we have equipment types
        assert len(db.equipment_catalog) > 0

    def test_get_equipment_specs(self, db):
        """Test getting equipment specifications."""
        specs = db.get_equipment_specs("broadcast_spreader_medium")
        assert specs is not None
        assert "name" in specs
        assert "category" in specs
        assert "capacity" in specs
        assert "fertilizer_types" in specs

    def test_get_compatibility(self, db):
        """Test getting compatibility information."""
        compat = db.get_compatibility(
            FertilizerFormulation.GRANULAR,
            EquipmentCategory.SPREADING
        )
        assert compat is not None
        assert "compatibility_level" in compat
        assert "score" in compat
        assert compat["score"] > 0.8  # Should be highly compatible

        # Test incompatible combination
        incompat = db.get_compatibility(
            FertilizerFormulation.GRANULAR,
            EquipmentCategory.SPRAYING
        )
        assert incompat is not None
        assert incompat["score"] == 0.0  # Should be incompatible

    def test_get_cost_data(self, db):
        """Test getting cost data."""
        cost_data = db.get_cost_data("broadcast_spreader_medium")
        assert cost_data is not None
        assert "purchase_price" in cost_data
        assert "operating_cost_per_hour" in cost_data
        assert "cost_per_acre" in cost_data

    def test_get_application_requirements(self, db):
        """Test getting application requirements."""
        requirements = db.get_application_requirements(ApplicationMethodType.BROADCAST)
        assert requirements is not None
        assert "fertilizer_types" in requirements
        assert "equipment_categories" in requirements
        assert "precision_level" in requirements

    def test_get_compatible_equipment(self, db):
        """Test getting compatible equipment for fertilizer type."""
        compatible = db.get_all_equipment_for_fertilizer(FertilizerFormulation.GRANULAR)
        assert len(compatible) > 0
        assert any("spreader" in eq.lower() for eq in compatible)

    def test_get_compatible_fertilizers(self, db):
        """Test getting compatible fertilizers for equipment."""
        compatible = db.get_all_fertilizers_for_equipment(EquipmentCategory.SPREADING)
        assert len(compatible) > 0
        assert FertilizerFormulation.GRANULAR in compatible


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
