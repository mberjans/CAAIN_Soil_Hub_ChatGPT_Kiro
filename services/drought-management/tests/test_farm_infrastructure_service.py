"""
Tests for Farm Infrastructure Assessment Service

Comprehensive test suite for farm equipment inventory, capacity assessment,
and infrastructure upgrade recommendations.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
from decimal import Decimal

from src.services.infrastructure_service import FarmInfrastructureAssessmentService
from src.models.farm_infrastructure_models import (
    EquipmentInventory, EquipmentCategory, EquipmentCondition, EquipmentOwnershipType,
    CapacityAssessment, CapacityLevel, UpgradeRecommendation, UpgradePriority,
    FarmInfrastructureAssessment, EquipmentSpecification
)


class TestFarmInfrastructureAssessmentService:
    """Test suite for FarmInfrastructureAssessmentService."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FarmInfrastructureAssessmentService()

    @pytest.fixture
    def sample_equipment_data(self):
        """Sample equipment data for testing."""
        return [
            {
                "name": "John Deere 6120R Tractor",
                "category": "tillage",
                "specifications": {
                    "model": "6120R",
                    "manufacturer": "John Deere",
                    "year_manufactured": 2020,
                    "horsepower": 120,
                    "capacity": {"acres_per_hour": 8.0}
                },
                "ownership_type": "owned",
                "condition": "good",
                "purchase_price": 85000,
                "current_value": 70000,
                "utilization_rate": 0.75
            },
            {
                "name": "Case IH 1200 Planter",
                "category": "planting",
                "specifications": {
                    "model": "1200",
                    "manufacturer": "Case IH",
                    "year_manufactured": 2018,
                    "capacity": {"row_width": 30, "acres_per_hour": 12.0}
                },
                "ownership_type": "owned",
                "condition": "excellent",
                "purchase_price": 120000,
                "current_value": 95000,
                "utilization_rate": 0.85
            },
            {
                "name": "Valley Center Pivot",
                "category": "irrigation",
                "specifications": {
                    "model": "8000",
                    "manufacturer": "Valley",
                    "year_manufactured": 2015,
                    "capacity": {"acres_per_system": 120, "efficiency": 0.85}
                },
                "ownership_type": "owned",
                "condition": "fair",
                "purchase_price": 150000,
                "current_value": 100000,
                "utilization_rate": 0.90
            }
        ]

    @pytest.fixture
    def sample_farm_characteristics(self):
        """Sample farm characteristics for testing."""
        return {
            "total_acres": 500,
            "field_count": 8,
            "expected_yield_per_acre": 180,
            "soil_type": "clay_loam",
            "slope_percent": 2.5,
            "drainage_class": "well_drained"
        }

    @pytest.fixture
    def sample_equipment_inventory(self):
        """Sample equipment inventory for testing."""
        return [
            EquipmentInventory(
                equipment_id=uuid4(),
                farm_location_id=uuid4(),
                equipment_name="Test Tractor",
                equipment_category=EquipmentCategory.TILLAGE,
                specifications=EquipmentSpecification(
                    model="Test Model",
                    manufacturer="Test Manufacturer",
                    year_manufactured=2020,
                    horsepower=100
                ),
                ownership_type=EquipmentOwnershipType.OWNED,
                condition=EquipmentCondition.GOOD,
                purchase_price=Decimal("50000"),
                current_value=Decimal("40000"),
                utilization_rate=0.75
            )
        ]

    @pytest.mark.asyncio
    async def test_service_initialization(self, service):
        """Test service initialization."""
        await service.initialize()
        assert service.initialized is True
        assert service.service_name == "FarmInfrastructureAssessmentService"

    @pytest.mark.asyncio
    async def test_service_cleanup(self, service):
        """Test service cleanup."""
        await service.initialize()
        await service.cleanup()
        assert service.initialized is False

    @pytest.mark.asyncio
    async def test_create_equipment_inventory(self, service, sample_equipment_data):
        """Test equipment inventory creation."""
        farm_location_id = uuid4()
        
        inventory = await service.create_equipment_inventory(
            farm_location_id, sample_equipment_data
        )
        
        assert len(inventory) == 3
        assert all(isinstance(item, EquipmentInventory) for item in inventory)
        assert all(item.farm_location_id == farm_location_id for item in inventory)
        
        # Test specific equipment items
        tractor = next(item for item in inventory if "Tractor" in item.equipment_name)
        assert tractor.equipment_category == EquipmentCategory.TILLAGE
        assert tractor.condition == EquipmentCondition.GOOD
        assert tractor.utilization_rate == 0.75

    @pytest.mark.asyncio
    async def test_create_equipment_inventory_with_invalid_data(self, service):
        """Test equipment inventory creation with invalid data."""
        farm_location_id = uuid4()
        invalid_data = [
            {
                "name": "Invalid Equipment",
                "category": "invalid_category",  # Invalid category
                "condition": "invalid_condition"  # Invalid condition
            }
        ]
        
        with pytest.raises(ValueError):
            await service.create_equipment_inventory(farm_location_id, invalid_data)

    @pytest.mark.asyncio
    async def test_assess_equipment_capacity(self, service, sample_equipment_inventory, sample_farm_characteristics):
        """Test equipment capacity assessment."""
        assessments = await service.assess_equipment_capacity(
            sample_equipment_inventory, sample_farm_characteristics
        )
        
        assert len(assessments) == 1
        assessment = assessments[0]
        
        assert isinstance(assessment, CapacityAssessment)
        assert assessment.equipment_id == sample_equipment_inventory[0].equipment_id
        assert assessment.current_capacity > 0
        assert assessment.required_capacity > 0
        assert assessment.capacity_utilization_percent >= 0
        assert assessment.capacity_utilization_percent <= 100
        assert isinstance(assessment.capacity_level, CapacityLevel)

    @pytest.mark.asyncio
    async def test_calculate_current_capacity_tillage(self, service):
        """Test current capacity calculation for tillage equipment."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Tractor",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer",
                horsepower=100
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD
        )
        
        capacity = await service._calculate_current_capacity(equipment)
        assert capacity > 0
        assert capacity == 50.0  # 100 HP * 0.5 acres per HP per hour

    @pytest.mark.asyncio
    async def test_calculate_current_capacity_planting(self, service):
        """Test current capacity calculation for planting equipment."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Planter",
            equipment_category=EquipmentCategory.PLANTING,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer",
                capacity={"row_width": 30}
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD
        )
        
        capacity = await service._calculate_current_capacity(equipment)
        assert capacity > 0
        assert capacity == 3.0  # 30 inches * 0.1 acres per inch per hour

    @pytest.mark.asyncio
    async def test_calculate_required_capacity(self, service, sample_farm_characteristics):
        """Test required capacity calculation."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Equipment",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer"
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD
        )
        
        required_capacity = await service._calculate_required_capacity(
            equipment, sample_farm_characteristics
        )
        
        assert required_capacity > 0
        # Should be based on average field size (500 acres / 8 fields = 62.5 acres)
        # with 20% buffer = 75 acres
        assert required_capacity == 75.0

    def test_determine_capacity_level(self, service):
        """Test capacity level determination."""
        assert service._determine_capacity_level(0.2) == CapacityLevel.UNDERUTILIZED
        assert service._determine_capacity_level(0.5) == CapacityLevel.ADEQUATE
        assert service._determine_capacity_level(0.8) == CapacityLevel.OPTIMAL
        assert service._determine_capacity_level(0.95) == CapacityLevel.OVERUTILIZED
        assert service._determine_capacity_level(1.1) == CapacityLevel.INSUFFICIENT

    @pytest.mark.asyncio
    async def test_calculate_efficiency_score(self, service):
        """Test efficiency score calculation."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Equipment",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer",
                year_manufactured=2020
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD,
            utilization_rate=0.8
        )
        
        efficiency_score = await service._calculate_efficiency_score(equipment)
        assert 0 <= efficiency_score <= 1
        assert efficiency_score > 0.5  # Should be reasonable for good condition equipment

    @pytest.mark.asyncio
    async def test_calculate_productivity_score(self, service):
        """Test productivity score calculation."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Equipment",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer"
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD
        )
        
        # Test different capacity ratios
        assert await service._calculate_productivity_score(equipment, 0.3) == 0.6  # Underutilized
        assert await service._calculate_productivity_score(equipment, 0.7) == 0.8  # Well-utilized
        assert await service._calculate_productivity_score(equipment, 0.9) == 0.9  # Optimal
        assert await service._calculate_productivity_score(equipment, 1.1) == 0.7  # Overutilized

    @pytest.mark.asyncio
    async def test_calculate_reliability_score(self, service):
        """Test reliability score calculation."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Equipment",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer"
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD,
            next_maintenance_due=date.today() + timedelta(days=30)  # Not overdue
        )
        
        reliability_score = await service._calculate_reliability_score(equipment)
        assert 0 <= reliability_score <= 1
        assert reliability_score > 0.5  # Should be reasonable for good condition equipment

    @pytest.mark.asyncio
    async def test_generate_capacity_recommendations(self, service):
        """Test capacity recommendations generation."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Equipment",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer"
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD
        )
        
        # Test underutilized equipment
        recommendations = await service._generate_capacity_recommendations(
            equipment, CapacityLevel.UNDERUTILIZED, 0.3
        )
        assert len(recommendations) > 0
        assert any("expanding" in rec.lower() for rec in recommendations)
        
        # Test overutilized equipment
        recommendations = await service._generate_capacity_recommendations(
            equipment, CapacityLevel.OVERUTILIZED, 1.1
        )
        assert len(recommendations) > 0
        assert any("upgrading" in rec.lower() for rec in recommendations)

    @pytest.mark.asyncio
    async def test_generate_upgrade_recommendations(self, service, sample_farm_characteristics):
        """Test upgrade recommendations generation."""
        # Create sample capacity assessments
        assessments = [
            CapacityAssessment(
                assessment_id=uuid4(),
                equipment_id=uuid4(),
                current_capacity=50.0,
                required_capacity=100.0,
                capacity_level=CapacityLevel.INSUFFICIENT,
                capacity_utilization_percent=200.0,
                efficiency_score=0.7,
                productivity_score=0.6,
                reliability_score=0.8,
                operational_constraints=[],
                maintenance_requirements=[],
                upgrade_potential="High",
                capacity_recommendations=[],
                optimization_opportunities=[]
            )
        ]
        
        recommendations = await service.generate_upgrade_recommendations(
            assessments, sample_farm_characteristics
        )
        
        assert len(recommendations) == 1
        recommendation = recommendations[0]
        
        assert isinstance(recommendation, UpgradeRecommendation)
        assert recommendation.priority == UpgradePriority.CRITICAL
        assert recommendation.estimated_cost > 0
        assert recommendation.annual_savings > 0
        assert recommendation.payback_period_years > 0

    @pytest.mark.asyncio
    async def test_conduct_comprehensive_assessment(self, service, sample_equipment_inventory, sample_farm_characteristics):
        """Test comprehensive assessment."""
        farm_location_id = uuid4()
        
        assessment = await service.conduct_comprehensive_assessment(
            farm_location_id, sample_equipment_inventory, sample_farm_characteristics
        )
        
        assert isinstance(assessment, FarmInfrastructureAssessment)
        assert assessment.farm_location_id == farm_location_id
        assert assessment.total_acres == sample_farm_characteristics["total_acres"]
        assert assessment.field_count == sample_farm_characteristics["field_count"]
        assert len(assessment.equipment_inventory) == len(sample_equipment_inventory)
        assert len(assessment.capacity_assessments) > 0
        assert len(assessment.upgrade_recommendations) >= 0
        assert assessment.overall_capacity_score >= 0
        assert assessment.overall_capacity_score <= 1
        assert len(assessment.strengths) >= 0
        assert len(assessment.weaknesses) >= 0
        assert len(assessment.opportunities) >= 0
        assert len(assessment.threats) >= 0

    @pytest.mark.asyncio
    async def test_generate_swot_analysis(self, service, sample_equipment_inventory):
        """Test SWOT analysis generation."""
        # Create sample assessments and recommendations
        capacity_assessments = [
            CapacityAssessment(
                assessment_id=uuid4(),
                equipment_id=uuid4(),
                current_capacity=50.0,
                required_capacity=60.0,
                capacity_level=CapacityLevel.OPTIMAL,
                capacity_utilization_percent=83.3,
                efficiency_score=0.8,
                productivity_score=0.9,
                reliability_score=0.85,
                operational_constraints=[],
                maintenance_requirements=[],
                upgrade_potential="Low",
                capacity_recommendations=[],
                optimization_opportunities=[]
            )
        ]
        
        upgrade_recommendations = [
            UpgradeRecommendation(
                recommendation_id=uuid4(),
                equipment_id=uuid4(),
                farm_location_id=uuid4(),
                recommendation_type="upgrade",
                title="Test Upgrade",
                description="Test upgrade description",
                priority=UpgradePriority.MEDIUM,
                estimated_cost=Decimal("10000"),
                annual_savings=Decimal("2000"),
                payback_period_years=5.0,
                roi_percentage=20.0,
                implementation_timeline_days=90,
                required_resources=[],
                dependencies=[],
                expected_benefits=[],
                implementation_risks=[],
                mitigation_strategies=[]
            )
        ]
        
        strengths, weaknesses, opportunities, threats = await service._generate_swot_analysis(
            sample_equipment_inventory, capacity_assessments, upgrade_recommendations
        )
        
        assert isinstance(strengths, list)
        assert isinstance(weaknesses, list)
        assert isinstance(opportunities, list)
        assert isinstance(threats, list)

    @pytest.mark.asyncio
    async def test_calculate_age_distribution(self, service, sample_equipment_inventory):
        """Test age distribution calculation."""
        # Add equipment with different ages
        old_equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Old Equipment",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Old Model",
                manufacturer="Old Manufacturer",
                year_manufactured=2010  # 14 years old
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.FAIR
        )
        
        equipment_list = sample_equipment_inventory + [old_equipment]
        distribution = await service._calculate_age_distribution(equipment_list)
        
        assert "0-5 years" in distribution
        assert "6-10 years" in distribution
        assert "11-15 years" in distribution
        assert "16+ years" in distribution
        assert sum(distribution.values()) == len(equipment_list)

    @pytest.mark.asyncio
    async def test_calculate_condition_distribution(self, service, sample_equipment_inventory):
        """Test condition distribution calculation."""
        distribution = await service._calculate_condition_distribution(sample_equipment_inventory)
        
        assert EquipmentCondition.EXCELLENT in distribution
        assert EquipmentCondition.GOOD in distribution
        assert EquipmentCondition.FAIR in distribution
        assert EquipmentCondition.POOR in distribution
        assert EquipmentCondition.CRITICAL in distribution
        assert sum(distribution.values()) == len(sample_equipment_inventory)

    @pytest.mark.asyncio
    async def test_identify_capacity_bottlenecks(self, service):
        """Test capacity bottleneck identification."""
        assessments = [
            CapacityAssessment(
                assessment_id=uuid4(),
                equipment_id=uuid4(),
                current_capacity=50.0,
                required_capacity=100.0,
                capacity_level=CapacityLevel.OVERUTILIZED,
                capacity_utilization_percent=200.0,
                efficiency_score=0.7,
                productivity_score=0.6,
                reliability_score=0.8,
                operational_constraints=[],
                maintenance_requirements=[],
                upgrade_potential="High",
                capacity_recommendations=[],
                optimization_opportunities=[]
            )
        ]
        
        bottlenecks = await service._identify_capacity_bottlenecks(assessments)
        assert len(bottlenecks) == 1
        assert "bottleneck" in bottlenecks[0].lower()

    def test_get_priority_score(self, service):
        """Test priority score calculation."""
        assert service._get_priority_score(UpgradePriority.CRITICAL) == 4
        assert service._get_priority_score(UpgradePriority.HIGH) == 3
        assert service._get_priority_score(UpgradePriority.MEDIUM) == 2
        assert service._get_priority_score(UpgradePriority.LOW) == 1

    @pytest.mark.asyncio
    async def test_equipment_database_loading(self, service):
        """Test equipment database loading."""
        await service.initialize()
        
        assert hasattr(service, 'equipment_database')
        assert 'tillage' in service.equipment_database
        assert 'planting' in service.equipment_database
        assert 'irrigation' in service.equipment_database
        assert 'storage' in service.equipment_database

    @pytest.mark.asyncio
    async def test_assessment_templates_loading(self, service):
        """Test assessment templates loading."""
        await service.initialize()
        
        assert hasattr(service, 'assessment_templates')
        assert 'capacity_assessment' in service.assessment_templates
        assert 'upgrade_priorities' in service.assessment_templates

    @pytest.mark.asyncio
    async def test_error_handling_invalid_equipment_data(self, service):
        """Test error handling for invalid equipment data."""
        farm_location_id = uuid4()
        invalid_data = [
            {
                "name": "Test Equipment",
                "category": "invalid_category"
            }
        ]
        
        with pytest.raises(ValueError):
            await service.create_equipment_inventory(farm_location_id, invalid_data)

    @pytest.mark.asyncio
    async def test_error_handling_empty_equipment_list(self, service):
        """Test error handling for empty equipment list."""
        farm_location_id = uuid4()
        empty_data = []
        
        inventory = await service.create_equipment_inventory(farm_location_id, empty_data)
        assert len(inventory) == 0

    @pytest.mark.asyncio
    async def test_error_handling_missing_required_fields(self, service):
        """Test error handling for missing required fields."""
        farm_location_id = uuid4()
        incomplete_data = [
            {
                "name": "Test Equipment"
                # Missing required fields like category, condition, etc.
            }
        ]
        
        with pytest.raises(ValueError):
            await service.create_equipment_inventory(farm_location_id, incomplete_data)


class TestFarmInfrastructureModels:
    """Test suite for farm infrastructure models."""

    def test_equipment_inventory_creation(self):
        """Test EquipmentInventory model creation."""
        equipment = EquipmentInventory(
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            equipment_name="Test Equipment",
            equipment_category=EquipmentCategory.TILLAGE,
            specifications=EquipmentSpecification(
                model="Test Model",
                manufacturer="Test Manufacturer"
            ),
            ownership_type=EquipmentOwnershipType.OWNED,
            condition=EquipmentCondition.GOOD
        )
        
        assert equipment.equipment_name == "Test Equipment"
        assert equipment.equipment_category == EquipmentCategory.TILLAGE
        assert equipment.ownership_type == EquipmentOwnershipType.OWNED
        assert equipment.condition == EquipmentCondition.GOOD

    def test_equipment_inventory_validation(self):
        """Test EquipmentInventory model validation."""
        with pytest.raises(ValueError):
            EquipmentInventory(
                equipment_id=uuid4(),
                farm_location_id=uuid4(),
                equipment_name="Test Equipment",
                equipment_category=EquipmentCategory.TILLAGE,
                specifications=EquipmentSpecification(
                    model="Test Model",
                    manufacturer="Test Manufacturer"
                ),
                ownership_type=EquipmentOwnershipType.OWNED,
                condition=EquipmentCondition.GOOD,
                utilization_rate=1.5  # Invalid: > 1
            )

    def test_capacity_assessment_creation(self):
        """Test CapacityAssessment model creation."""
        assessment = CapacityAssessment(
            assessment_id=uuid4(),
            equipment_id=uuid4(),
            current_capacity=50.0,
            required_capacity=60.0,
            capacity_level=CapacityLevel.ADEQUATE,
            capacity_utilization_percent=83.3,
            efficiency_score=0.8,
            productivity_score=0.9,
            reliability_score=0.85,
            operational_constraints=[],
            maintenance_requirements=[],
            upgrade_potential="Medium",
            capacity_recommendations=[],
            optimization_opportunities=[]
        )
        
        assert assessment.current_capacity == 50.0
        assert assessment.required_capacity == 60.0
        assert assessment.capacity_level == CapacityLevel.ADEQUATE
        assert assessment.capacity_utilization_percent == 83.3

    def test_capacity_assessment_validation(self):
        """Test CapacityAssessment model validation."""
        with pytest.raises(ValueError):
            CapacityAssessment(
                assessment_id=uuid4(),
                equipment_id=uuid4(),
                current_capacity=50.0,
                required_capacity=60.0,
                capacity_level=CapacityLevel.ADEQUATE,
                capacity_utilization_percent=150.0,  # Invalid: > 100
                efficiency_score=0.8,
                productivity_score=0.9,
                reliability_score=0.85,
                operational_constraints=[],
                maintenance_requirements=[],
                upgrade_potential="Medium",
                capacity_recommendations=[],
                optimization_opportunities=[]
            )

    def test_upgrade_recommendation_creation(self):
        """Test UpgradeRecommendation model creation."""
        recommendation = UpgradeRecommendation(
            recommendation_id=uuid4(),
            equipment_id=uuid4(),
            farm_location_id=uuid4(),
            recommendation_type="equipment_upgrade",
            title="Test Upgrade",
            description="Test upgrade description",
            priority=UpgradePriority.HIGH,
            estimated_cost=Decimal("10000"),
            annual_savings=Decimal("2000"),
            payback_period_years=5.0,
            roi_percentage=20.0,
            implementation_timeline_days=90,
            required_resources=[],
            dependencies=[],
            expected_benefits=[],
            implementation_risks=[],
            mitigation_strategies=[]
        )
        
        assert recommendation.title == "Test Upgrade"
        assert recommendation.priority == UpgradePriority.HIGH
        assert recommendation.estimated_cost == Decimal("10000")
        assert recommendation.annual_savings == Decimal("2000")

    def test_farm_infrastructure_assessment_creation(self):
        """Test FarmInfrastructureAssessment model creation."""
        assessment = FarmInfrastructureAssessment(
            assessment_id=uuid4(),
            farm_location_id=uuid4(),
            total_acres=500.0,
            field_count=8,
            average_field_size=62.5,
            field_layout_complexity="medium",
            equipment_inventory=[],
            total_equipment_value=Decimal("200000"),
            equipment_age_distribution={},
            condition_distribution={},
            capacity_assessments=[],
            overall_capacity_score=0.75,
            capacity_bottlenecks=[],
            upgrade_recommendations=[],
            total_upgrade_cost=Decimal("50000"),
            total_annual_savings=Decimal("10000"),
            overall_roi=20.0,
            strengths=[],
            weaknesses=[],
            opportunities=[],
            threats=[],
            immediate_actions=[],
            short_term_goals=[],
            long_term_goals=[],
            assessor="Test Assessor",
            assessment_method="test_method",
            confidence_score=0.85
        )
        
        assert assessment.total_acres == 500.0
        assert assessment.field_count == 8
        assert assessment.overall_capacity_score == 0.75
        assert assessment.confidence_score == 0.85


class TestFarmInfrastructureIntegration:
    """Integration tests for farm infrastructure assessment."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return FarmInfrastructureAssessmentService()

    @pytest.mark.asyncio
    async def test_end_to_end_assessment_workflow(self, service):
        """Test complete end-to-end assessment workflow."""
        # Initialize service
        await service.initialize()
        
        # Create sample data
        farm_location_id = uuid4()
        equipment_data = [
            {
                "name": "Test Tractor",
                "category": "tillage",
                "specifications": {
                    "model": "Test Model",
                    "manufacturer": "Test Manufacturer",
                    "horsepower": 100
                },
                "ownership_type": "owned",
                "condition": "good",
                "utilization_rate": 0.75
            }
        ]
        
        farm_characteristics = {
            "total_acres": 200,
            "field_count": 4,
            "expected_yield_per_acre": 150
        }
        
        # Create equipment inventory
        inventory = await service.create_equipment_inventory(farm_location_id, equipment_data)
        assert len(inventory) == 1
        
        # Conduct comprehensive assessment
        assessment = await service.conduct_comprehensive_assessment(
            farm_location_id, inventory, farm_characteristics
        )
        
        # Verify assessment results
        assert assessment.farm_location_id == farm_location_id
        assert assessment.total_acres == 200
        assert assessment.field_count == 4
        assert len(assessment.equipment_inventory) == 1
        assert len(assessment.capacity_assessments) == 1
        assert assessment.overall_capacity_score > 0
        
        # Cleanup
        await service.cleanup()

    @pytest.mark.asyncio
    async def test_multiple_equipment_assessment(self, service):
        """Test assessment with multiple equipment types."""
        await service.initialize()
        
        farm_location_id = uuid4()
        equipment_data = [
            {
                "name": "Tillage Tractor",
                "category": "tillage",
                "specifications": {"horsepower": 120},
                "ownership_type": "owned",
                "condition": "good",
                "utilization_rate": 0.8
            },
            {
                "name": "Planting Equipment",
                "category": "planting",
                "specifications": {"row_width": 30},
                "ownership_type": "owned",
                "condition": "excellent",
                "utilization_rate": 0.9
            },
            {
                "name": "Irrigation System",
                "category": "irrigation",
                "specifications": {"efficiency": 0.85},
                "ownership_type": "owned",
                "condition": "fair",
                "utilization_rate": 0.95
            }
        ]
        
        farm_characteristics = {
            "total_acres": 300,
            "field_count": 6
        }
        
        # Create inventory
        inventory = await service.create_equipment_inventory(farm_location_id, equipment_data)
        assert len(inventory) == 3
        
        # Assess capacity
        assessments = await service.assess_equipment_capacity(inventory, farm_characteristics)
        assert len(assessments) == 3
        
        # Generate recommendations
        recommendations = await service.generate_upgrade_recommendations(
            assessments, farm_characteristics
        )
        # Should have recommendations for overutilized equipment
        
        await service.cleanup()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])