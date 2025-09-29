"""
Comprehensive Test Suite for Tillage Transition Planning Service

Tests for tillage transition planning, practice adaptation,
troubleshooting support, and success monitoring functionality.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, date

from src.services.tillage_transition_planning_service import TillageTransitionPlanningService
from src.models.tillage_models import (
    TillageSystem,
    TillageOptimizationRequest,
    SoilType,
    CropType,
    TillageEquipment
)


class TestTillageTransitionPlanningService:
    """Comprehensive test suite for tillage transition planning service."""

    @pytest.fixture
    def service(self):
        """Create service instance for testing."""
        return TillageTransitionPlanningService()

    @pytest.fixture
    def sample_field_conditions(self):
        """Create sample field conditions for testing."""
        return TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.CONVENTIONAL,
            soil_type=SoilType.LOAM,
            soil_texture="Loam soil",
            field_size_acres=100.0,
            slope_percent=5.0,
            drainage_class="moderate",
            organic_matter_percent=3.0,
            compaction_level="moderate",
            crop_rotation=[CropType.CORN, CropType.SOYBEAN],
            equipment_available=[TillageEquipment.MOLDBOARD_PLOW],
            irrigation_available=True,
            cover_crop_usage=False,
            water_conservation_priority=8.0,
            soil_health_priority=7.0,
            labor_availability=6.0,
            budget_constraints=Decimal('75000')
        )

    @pytest.fixture
    def sample_transition_preferences(self):
        """Create sample transition preferences."""
        return {
            "transition_duration_preference": "gradual",
            "risk_tolerance": "medium",
            "budget_constraints": 75000,
            "equipment_preference": "purchase",
            "training_preference": "comprehensive"
        }

    @pytest.mark.asyncio
    async def test_create_comprehensive_transition_plan_success(self, service, sample_field_conditions, sample_transition_preferences):
        """Test successful creation of comprehensive transition plan."""
        
        # Test transition from conventional to no-till
        transition_plan = await service.create_comprehensive_transition_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions,
            sample_transition_preferences
        )
        
        # Verify plan structure
        assert "plan_id" in transition_plan
        assert "current_system" in transition_plan
        assert "target_system" in transition_plan
        assert "feasibility_assessment" in transition_plan
        assert "transition_timeline" in transition_plan
        assert "practice_adaptation_plan" in transition_plan
        assert "troubleshooting_support" in transition_plan
        assert "monitoring_framework" in transition_plan
        assert "educational_plan" in transition_plan
        assert "expert_consultation_plan" in transition_plan
        assert "peer_networking_plan" in transition_plan
        assert "extension_integration_plan" in transition_plan
        assert "equipment_dealer_plan" in transition_plan
        assert "cost_analysis" in transition_plan
        assert "risk_mitigation_plan" in transition_plan
        assert "implementation_checklist" in transition_plan
        
        # Verify plan content
        assert transition_plan["current_system"] == TillageSystem.CONVENTIONAL
        assert transition_plan["target_system"] == TillageSystem.NO_TILL
        assert transition_plan["feasibility_assessment"]["feasibility_score"] > 0
        assert transition_plan["transition_timeline"]["total_duration_years"] > 0

    @pytest.mark.asyncio
    async def test_assess_transition_feasibility_high_feasibility(self, service, sample_field_conditions):
        """Test feasibility assessment for high feasibility scenario."""
        
        # Modify field conditions for high feasibility
        sample_field_conditions.soil_type = SoilType.LOAM
        sample_field_conditions.organic_matter_percent = 4.0
        sample_field_conditions.slope_percent = 8.0
        sample_field_conditions.budget_constraints = Decimal('100000')
        
        feasibility = await service._assess_transition_feasibility(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert feasibility["feasibility_score"] >= 70
        assert feasibility["feasibility_level"] in ["high", "medium"]
        assert "feasibility_factors" in feasibility
        assert "challenges" in feasibility
        assert "recommendations" in feasibility

    @pytest.mark.asyncio
    async def test_assess_transition_feasibility_low_feasibility(self, service, sample_field_conditions):
        """Test feasibility assessment for low feasibility scenario."""
        
        # Modify field conditions for low feasibility
        sample_field_conditions.soil_type = SoilType.CLAY
        sample_field_conditions.organic_matter_percent = 1.0
        sample_field_conditions.budget_constraints = Decimal('20000')
        
        feasibility = await service._assess_transition_feasibility(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert feasibility["feasibility_score"] < 70
        assert feasibility["feasibility_level"] in ["low", "medium"]
        assert len(feasibility["challenges"]) > 0
        assert len(feasibility["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_generate_transition_timeline_no_till(self, service, sample_field_conditions, sample_transition_preferences):
        """Test transition timeline generation for no-till system."""
        
        timeline = await service._generate_transition_timeline(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions,
            sample_transition_preferences
        )
        
        assert timeline["total_duration_years"] >= 2
        assert len(timeline["phases"]) == timeline["total_duration_years"]
        assert "seasonal_activities" in timeline
        assert "milestones" in timeline
        assert "critical_success_factors" in timeline
        
        # Verify phase structure
        for phase in timeline["phases"]:
            assert "year" in phase
            assert "phase_name" in phase
            assert "phase_type" in phase
            assert "objectives" in phase
            assert "key_activities" in phase
            assert "success_metrics" in phase
            assert "support_resources" in phase

    @pytest.mark.asyncio
    async def test_create_practice_adaptation_plan(self, service, sample_field_conditions):
        """Test practice adaptation plan creation."""
        
        timeline = {
            "total_duration_years": 3,
            "phases": [{"year": 1}, {"year": 2}, {"year": 3}]
        }
        
        adaptation_plan = await service._create_practice_adaptation_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions,
            timeline
        )
        
        assert "adaptation_strategies" in adaptation_plan
        assert "practice_modifications" in adaptation_plan
        assert "timing_adjustments" in adaptation_plan
        assert "equipment_modifications" in adaptation_plan
        assert "management_changes" in adaptation_plan
        
        # Verify adaptation strategies
        assert len(adaptation_plan["adaptation_strategies"]) > 0
        assert len(adaptation_plan["practice_modifications"]) > 0

    @pytest.mark.asyncio
    async def test_create_troubleshooting_support_plan(self, service, sample_field_conditions):
        """Test troubleshooting support plan creation."""
        
        troubleshooting_plan = await service._create_troubleshooting_support_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert "common_issues" in troubleshooting_plan
        assert "prevention_strategies" in troubleshooting_plan
        assert "diagnostic_tools" in troubleshooting_plan
        assert "solution_resources" in troubleshooting_plan
        assert "expert_contacts" in troubleshooting_plan
        assert "emergency_procedures" in troubleshooting_plan

    @pytest.mark.asyncio
    async def test_create_success_monitoring_framework(self, service, sample_field_conditions):
        """Test success monitoring framework creation."""
        
        monitoring_framework = await service._create_success_monitoring_framework(
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert "key_performance_indicators" in monitoring_framework
        assert "monitoring_schedule" in monitoring_framework
        assert "data_collection_methods" in monitoring_framework
        assert "benchmarking_criteria" in monitoring_framework
        assert "reporting_templates" in monitoring_framework
        assert "success_thresholds" in monitoring_framework

    @pytest.mark.asyncio
    async def test_create_educational_resources_plan(self, service, sample_field_conditions):
        """Test educational resources plan creation."""
        
        educational_plan = await service._create_educational_resources_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert "learning_modules" in educational_plan
        assert "training_schedule" in educational_plan
        assert "certification_opportunities" in educational_plan
        assert "online_resources" in educational_plan
        assert "workshop_recommendations" in educational_plan
        assert "peer_learning_opportunities" in educational_plan

    @pytest.mark.asyncio
    async def test_create_expert_consultation_plan(self, service, sample_field_conditions):
        """Test expert consultation plan creation."""
        
        consultation_plan = await service._create_expert_consultation_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert "expert_contacts" in consultation_plan
        assert "consultation_schedule" in consultation_plan
        assert "specialized_services" in consultation_plan
        assert "cost_estimates" in consultation_plan
        assert "consultation_topics" in consultation_plan
        assert "follow_up_plan" in consultation_plan

    @pytest.mark.asyncio
    async def test_create_peer_networking_plan(self, service, sample_field_conditions):
        """Test peer networking plan creation."""
        
        networking_plan = await service._create_peer_networking_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert "peer_contacts" in networking_plan
        assert "networking_events" in networking_plan
        assert "mentorship_opportunities" in networking_plan
        assert "study_groups" in networking_plan
        assert "field_days" in networking_plan
        assert "online_communities" in networking_plan

    @pytest.mark.asyncio
    async def test_create_extension_integration_plan(self, service, sample_field_conditions):
        """Test extension integration plan creation."""
        
        extension_plan = await service._create_extension_integration_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert "extension_contacts" in extension_plan
        assert "available_programs" in extension_plan
        assert "cost_share_opportunities" in extension_plan
        assert "technical_assistance" in extension_plan
        assert "research_trials" in extension_plan
        assert "demonstration_sites" in extension_plan

    @pytest.mark.asyncio
    async def test_create_equipment_dealer_plan(self, service, sample_field_conditions):
        """Test equipment dealer plan creation."""
        
        dealer_plan = await service._create_equipment_dealer_plan(
            TillageSystem.NO_TILL,
            sample_field_conditions
        )
        
        assert "recommended_dealers" in dealer_plan
        assert "equipment_specifications" in dealer_plan
        assert "financing_options" in dealer_plan
        assert "leasing_opportunities" in dealer_plan
        assert "maintenance_services" in dealer_plan
        assert "training_programs" in dealer_plan

    def test_determine_feasibility_level(self, service):
        """Test feasibility level determination."""
        
        assert service._determine_feasibility_level(85) == "high"
        assert service._determine_feasibility_level(70) == "medium"
        assert service._determine_feasibility_level(50) == "low"

    def test_calculate_transition_difficulty(self, service):
        """Test transition difficulty calculation."""
        
        # Test different transition scenarios
        assert service._calculate_transition_difficulty(
            TillageSystem.CONVENTIONAL, TillageSystem.REDUCED_TILL
        ) == "low"
        
        assert service._calculate_transition_difficulty(
            TillageSystem.CONVENTIONAL, TillageSystem.STRIP_TILL
        ) == "medium"
        
        assert service._calculate_transition_difficulty(
            TillageSystem.CONVENTIONAL, TillageSystem.NO_TILL
        ) == "high"

    def test_identify_critical_success_factors(self, service):
        """Test critical success factors identification."""
        
        factors = service._identify_critical_success_factors(TillageSystem.NO_TILL)
        assert len(factors) > 0
        assert "Proper soil drainage" in factors
        assert "Effective weed management" in factors

    def test_initialize_transition_templates(self, service):
        """Test transition templates initialization."""
        
        assert TillageSystem.NO_TILL in service.transition_templates
        assert TillageSystem.STRIP_TILL in service.transition_templates
        
        no_till_template = service.transition_templates[TillageSystem.NO_TILL]
        assert "duration_years" in no_till_template
        assert "phases" in no_till_template
        assert "key_activities" in no_till_template

    def test_initialize_troubleshooting_database(self, service):
        """Test troubleshooting database initialization."""
        
        assert TillageSystem.NO_TILL in service.troubleshooting_database
        
        no_till_issues = service.troubleshooting_database[TillageSystem.NO_TILL]
        assert "weed_pressure" in no_till_issues
        assert "soil_compaction" in no_till_issues
        assert "slow_emergence" in no_till_issues

    def test_initialize_educational_resources(self, service):
        """Test educational resources initialization."""
        
        assert TillageSystem.NO_TILL in service.educational_resources
        assert TillageSystem.STRIP_TILL in service.educational_resources
        
        no_till_resources = service.educational_resources[TillageSystem.NO_TILL]
        assert len(no_till_resources) > 0
        assert "No-Till Farming Fundamentals" in no_till_resources

    def test_initialize_expert_contacts(self, service):
        """Test expert contacts initialization."""
        
        assert TillageSystem.NO_TILL in service.expert_contacts
        assert TillageSystem.STRIP_TILL in service.expert_contacts
        
        no_till_experts = service.expert_contacts[TillageSystem.NO_TILL]
        assert len(no_till_experts) > 0
        assert "name" in no_till_experts[0]
        assert "specialty" in no_till_experts[0]

    def test_initialize_peer_network(self, service):
        """Test peer network initialization."""
        
        assert TillageSystem.NO_TILL in service.peer_network_contacts
        
        no_till_peers = service.peer_network_contacts[TillageSystem.NO_TILL]
        assert len(no_till_peers) > 0
        assert "name" in no_till_peers[0]
        assert "farm" in no_till_peers[0]
        assert "experience" in no_till_peers[0]

    @pytest.mark.asyncio
    async def test_create_yearly_phase_no_till_year_1(self, service, sample_field_conditions, sample_transition_preferences):
        """Test yearly phase creation for no-till year 1."""
        
        phase = await service._create_yearly_phase(
            1, TillageSystem.CONVENTIONAL, TillageSystem.NO_TILL,
            sample_field_conditions, sample_transition_preferences
        )
        
        assert phase["year"] == 1
        assert phase["phase_name"] == "Planning and Preparation"
        assert phase["phase_type"] == "planning"
        assert len(phase["objectives"]) > 0
        assert len(phase["key_activities"]) > 0
        assert len(phase["success_metrics"]) > 0
        assert len(phase["support_resources"]) > 0

    @pytest.mark.asyncio
    async def test_create_yearly_phase_no_till_year_2(self, service, sample_field_conditions, sample_transition_preferences):
        """Test yearly phase creation for no-till year 2."""
        
        phase = await service._create_yearly_phase(
            2, TillageSystem.CONVENTIONAL, TillageSystem.NO_TILL,
            sample_field_conditions, sample_transition_preferences
        )
        
        assert phase["year"] == 2
        assert phase["phase_name"] == "Initial Implementation"
        assert phase["phase_type"] == "implementation"
        assert len(phase["objectives"]) > 0
        assert len(phase["key_activities"]) > 0

    @pytest.mark.asyncio
    async def test_create_yearly_phase_no_till_year_3(self, service, sample_field_conditions, sample_transition_preferences):
        """Test yearly phase creation for no-till year 3."""
        
        phase = await service._create_yearly_phase(
            3, TillageSystem.CONVENTIONAL, TillageSystem.NO_TILL,
            sample_field_conditions, sample_transition_preferences
        )
        
        assert phase["year"] == 3
        assert phase["phase_name"] == "Full Implementation and Optimization"
        assert phase["phase_type"] == "optimization"
        assert len(phase["objectives"]) > 0
        assert len(phase["key_activities"]) > 0

    @pytest.mark.asyncio
    async def test_calculate_comprehensive_transition_costs(self, service):
        """Test comprehensive transition cost calculation."""
        
        timeline = {"total_duration_years": 3}
        practice_plan = {"adaptation_strategies": ["test"]}
        equipment_plan = [{"estimated_cost": Decimal('50000')}]
        
        costs = await service._calculate_comprehensive_transition_costs(
            timeline, practice_plan, equipment_plan
        )
        
        assert "equipment" in costs
        assert "training" in costs
        assert "consultation" in costs
        assert "total" in costs
        assert costs["total"] > 0

    @pytest.mark.asyncio
    async def test_create_risk_mitigation_plan(self, service, sample_field_conditions):
        """Test risk mitigation plan creation."""
        
        feasibility = {"feasibility_score": 75}
        
        risk_plan = await service._create_risk_mitigation_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions,
            feasibility
        )
        
        assert "risks" in risk_plan
        assert "mitigation_strategies" in risk_plan
        assert "contingency_plans" in risk_plan
        assert len(risk_plan["risks"]) > 0

    @pytest.mark.asyncio
    async def test_create_implementation_checklist(self, service):
        """Test implementation checklist creation."""
        
        timeline = {"phases": [{"year": 1}]}
        practice_plan = {"adaptation_strategies": ["test"]}
        
        checklist = await service._create_implementation_checklist(
            timeline, practice_plan
        )
        
        assert len(checklist) > 0
        for item in checklist:
            assert "task" in item
            assert "timeline" in item
            assert "status" in item

    @pytest.mark.asyncio
    async def test_error_handling_invalid_systems(self, service, sample_field_conditions, sample_transition_preferences):
        """Test error handling for invalid tillage systems."""
        
        with pytest.raises(Exception):
            await service.create_comprehensive_transition_plan(
                "invalid_system",
                TillageSystem.NO_TILL,
                sample_field_conditions,
                sample_transition_preferences
            )

    @pytest.mark.asyncio
    async def test_performance_requirements(self, service, sample_field_conditions, sample_transition_preferences):
        """Test that transition plan creation meets performance requirements."""
        
        import time
        start_time = time.time()
        
        transition_plan = await service.create_comprehensive_transition_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            sample_field_conditions,
            sample_transition_preferences
        )
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time (5 seconds)
        assert elapsed_time < 5.0
        assert transition_plan["processing_time_ms"] > 0


class TestTillageTransitionPlanningIntegration:
    """Integration tests for tillage transition planning service."""

    @pytest.mark.asyncio
    async def test_full_transition_workflow(self):
        """Test complete transition workflow from assessment to implementation."""
        
        service = TillageTransitionPlanningService()
        
        # Create field conditions
        field_conditions = TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.CONVENTIONAL,
            soil_type=SoilType.LOAM,
            soil_texture="Loam soil",
            field_size_acres=150.0,
            slope_percent=6.0,
            drainage_class="moderate",
            organic_matter_percent=3.5,
            compaction_level="moderate",
            crop_rotation=[CropType.CORN, CropType.SOYBEAN],
            water_conservation_priority=9.0,
            soil_health_priority=8.0,
            labor_availability=7.0,
            budget_constraints=Decimal('100000')
        )
        
        transition_preferences = {
            "transition_duration_preference": "gradual",
            "risk_tolerance": "low",
            "budget_constraints": 100000
        }
        
        # Step 1: Assess feasibility
        feasibility = await service._assess_transition_feasibility(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            field_conditions
        )
        
        assert feasibility["feasibility_score"] > 0
        
        # Step 2: Create comprehensive plan
        transition_plan = await service.create_comprehensive_transition_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.NO_TILL,
            field_conditions,
            transition_preferences
        )
        
        # Step 3: Verify plan completeness
        assert transition_plan["feasibility_assessment"]["feasibility_score"] == feasibility["feasibility_score"]
        assert len(transition_plan["transition_timeline"]["phases"]) > 0
        assert len(transition_plan["practice_adaptation_plan"]["adaptation_strategies"]) > 0
        assert len(transition_plan["troubleshooting_support"]["common_issues"]) > 0
        assert len(transition_plan["monitoring_framework"]["key_performance_indicators"]) > 0

    @pytest.mark.asyncio
    async def test_different_tillage_system_transitions(self):
        """Test transitions between different tillage systems."""
        
        service = TillageTransitionPlanningService()
        
        field_conditions = TillageOptimizationRequest(
            field_id=uuid4(),
            current_tillage_system=TillageSystem.CONVENTIONAL,
            soil_type=SoilType.SANDY_LOAM,
            soil_texture="Sandy loam soil",
            field_size_acres=200.0,
            slope_percent=4.0,
            drainage_class="good",
            organic_matter_percent=2.5,
            compaction_level="low",
            crop_rotation=[CropType.CORN, CropType.SOYBEAN],
            water_conservation_priority=7.0,
            soil_health_priority=6.0,
            labor_availability=8.0,
            budget_constraints=Decimal('80000')
        )
        
        # Test conventional to strip-till
        strip_till_plan = await service.create_comprehensive_transition_plan(
            TillageSystem.CONVENTIONAL,
            TillageSystem.STRIP_TILL,
            field_conditions,
            {}
        )
        
        assert strip_till_plan["target_system"] == TillageSystem.STRIP_TILL
        assert strip_till_plan["transition_timeline"]["total_duration_years"] <= 2
        
        # Test strip-till to no-till
        field_conditions.current_tillage_system = TillageSystem.STRIP_TILL
        
        no_till_plan = await service.create_comprehensive_transition_plan(
            TillageSystem.STRIP_TILL,
            TillageSystem.NO_TILL,
            field_conditions,
            {}
        )
        
        assert no_till_plan["target_system"] == TillageSystem.NO_TILL
        assert no_till_plan["transition_timeline"]["total_duration_years"] <= 2


class TestTillageTransitionPlanningValidation:
    """Validation tests for tillage transition planning service."""

    def test_agricultural_validation_no_till_transition(self):
        """Test agricultural validation for no-till transition."""
        
        service = TillageTransitionPlanningService()
        
        # Test that no-till transition includes proper considerations
        no_till_template = service.transition_templates[TillageSystem.NO_TILL]
        assert no_till_template["duration_years"] >= 2  # Should be gradual
        
        # Test troubleshooting database includes no-till specific issues
        no_till_issues = service.troubleshooting_database[TillageSystem.NO_TILL]
        assert "weed_pressure" in no_till_issues
        assert "soil_compaction" in no_till_issues
        
        # Test educational resources are comprehensive
        no_till_education = service.educational_resources[TillageSystem.NO_TILL]
        assert "No-Till Farming Fundamentals" in no_till_education
        assert "Cover Crop Management" in no_till_education

    def test_equipment_compatibility_validation(self):
        """Test equipment compatibility validation."""
        
        service = TillageTransitionPlanningService()
        
        # Test that equipment recommendations consider soil types
        assert service._calculate_transition_difficulty(
            TillageSystem.CONVENTIONAL, TillageSystem.NO_TILL
        ) == "high"
        
        # Test that strip-till is easier transition
        assert service._calculate_transition_difficulty(
            TillageSystem.CONVENTIONAL, TillageSystem.STRIP_TILL
        ) == "medium"

    @pytest.mark.asyncio
    async def test_cost_validation(self):
        """Test cost validation for transition planning."""
        
        service = TillageTransitionPlanningService()
        
        timeline = {"total_duration_years": 3}
        practice_plan = {"adaptation_strategies": ["test"]}
        equipment_plan = [{"estimated_cost": Decimal('50000')}]
        
        costs = await service._calculate_comprehensive_transition_costs(
            timeline, practice_plan, equipment_plan
        )
        
        # Verify cost structure is reasonable
        assert costs["equipment"] > 0
        assert costs["training"] > 0
        assert costs["consultation"] > 0
        assert costs["total"] >= costs["equipment"] + costs["training"] + costs["consultation"]