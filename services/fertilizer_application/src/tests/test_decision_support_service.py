"""
Tests for Decision Support Service.

This module contains comprehensive tests for the decision support system,
including decision trees, expert systems, scenario analysis, and sensitivity analysis.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
from typing import List, Dict, Any

from src.models.application_models import (
    FieldConditions, CropRequirements, FertilizerSpecification, EquipmentSpecification, FertilizerForm, EquipmentType
)
from src.services.decision_support_service import (
    DecisionSupportService, DecisionRule, ScenarioType, DecisionNode, ExpertRule,
    ScenarioResult, SensitivityResult, DecisionMatrix, DecisionSupportResult
)


class TestDecisionSupportService:
    """Test cases for DecisionSupportService."""
    
    @pytest.fixture
    def sample_field_conditions(self):
        """Sample field conditions for testing."""
        return FieldConditions(
            field_size_acres=150.0,
            soil_type="clay",
            soil_ph=6.5,
            organic_matter_percent=3.2,
            slope_percent=2.0,
            drainage_class="well",
            water_body_distance=200.0,
            environmental_regulations="standard"
        )
    
    @pytest.fixture
    def sample_crop_requirements(self):
        """Sample crop requirements for testing."""
        return CropRequirements(
            crop_type="corn",
            growth_stage="vegetative",
            nitrogen_requirement=120.0,
            phosphorus_requirement=40.0,
            potassium_requirement=80.0,
            row_spacing_inches=30.0,
            planting_date="2024-04-15",
            expected_harvest_date="2024-09-15"
        )
    
    @pytest.fixture
    def sample_fertilizer_specification(self):
        """Sample fertilizer specification for testing."""
        return FertilizerSpecification(
            fertilizer_type="liquid",
            npk_ratio="28-0-0",
            form=FertilizerForm.LIQUID,
            solubility=100.0,
            release_rate="immediate",
            cost_per_unit=0.45,
            unit="gallon"
        )
    
    @pytest.fixture
    def sample_equipment(self):
        """Sample equipment for testing."""
        return [
            EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=1000.0,
                capacity_unit="gallons",
                application_width=20.0,
                fuel_efficiency=0.85,
                maintenance_cost_per_hour=25.0
            ),
            EquipmentSpecification(
                equipment_type=EquipmentType.INJECTOR,
                capacity=500.0,
                capacity_unit="gallons",
                application_width=15.0,
                fuel_efficiency=0.95,
                maintenance_cost_per_hour=50.0
            )
        ]
    
    @pytest.fixture
    def decision_support_service(self):
        """Decision support service instance for testing."""
        return DecisionSupportService()
    
    def test_initialization(self, decision_support_service):
        """Test service initialization."""
        assert decision_support_service is not None
        assert hasattr(decision_support_service, 'decision_trees')
        assert hasattr(decision_support_service, 'expert_rules')
        assert hasattr(decision_support_service, 'scenario_templates')
        assert len(decision_support_service.decision_trees) > 0
        assert len(decision_support_service.expert_rules) > 0
        assert len(decision_support_service.scenario_templates) > 0
    
    def test_decision_trees_initialization(self, decision_support_service):
        """Test decision trees initialization."""
        trees = decision_support_service.decision_trees
        
        # Check that we have the expected trees
        assert "field_size_based" in trees
        assert "crop_based" in trees
        
        # Check field_size_based tree structure
        field_tree = trees["field_size_based"]
        assert "root" in field_tree
        assert field_tree["root"].node_id == "field_size"
        assert field_tree["root"].condition == "field_size_acres"
        assert field_tree["root"].threshold == 50.0
        
        # Check crop_based tree structure
        crop_tree = trees["crop_based"]
        assert "root" in crop_tree
        assert crop_tree["root"].node_id == "crop_type"
        assert crop_tree["root"].condition == "crop_type"
    
    def test_expert_rules_initialization(self, decision_support_service):
        """Test expert rules initialization."""
        rules = decision_support_service.expert_rules
        
        assert len(rules) > 0
        
        # Check first rule structure
        first_rule = rules[0]
        assert isinstance(first_rule, ExpertRule)
        assert hasattr(first_rule, 'rule_id')
        assert hasattr(first_rule, 'condition')
        assert hasattr(first_rule, 'conclusion')
        assert hasattr(first_rule, 'confidence')
        assert hasattr(first_rule, 'priority')
        assert hasattr(first_rule, 'description')
        
        # Check that we have rules for different scenarios
        rule_conditions = [rule.condition for rule in rules]
        assert any("field_size_acres" in condition for condition in rule_conditions)
        assert any("soil_type" in condition for condition in rule_conditions)
        assert any("crop_type" in condition for condition in rule_conditions)
    
    def test_scenario_templates_initialization(self, decision_support_service):
        """Test scenario templates initialization."""
        templates = decision_support_service.scenario_templates
        
        assert ScenarioType.BEST_CASE in templates
        assert ScenarioType.WORST_CASE in templates
        assert ScenarioType.MOST_LIKELY in templates
        
        # Check best case template
        best_case = templates[ScenarioType.BEST_CASE]
        assert "description" in best_case
        assert "factors" in best_case
        assert best_case["factors"]["weather"] > 0.8
        assert best_case["factors"]["equipment_performance"] > 0.9
        
        # Check worst case template
        worst_case = templates[ScenarioType.WORST_CASE]
        assert worst_case["factors"]["weather"] < 0.5
        assert worst_case["factors"]["equipment_performance"] < 0.7
    
    @pytest.mark.asyncio
    async def test_provide_decision_support_decision_tree(self, decision_support_service, 
                                                        sample_field_conditions, 
                                                        sample_crop_requirements,
                                                        sample_fertilizer_specification,
                                                        sample_equipment):
        """Test decision support with decision tree rule."""
        result = await decision_support_service.provide_decision_support(
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            available_equipment=sample_equipment,
            decision_rule=DecisionRule.DECISION_TREE,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        assert isinstance(result, DecisionSupportResult)
        assert result.decision_id is not None
        assert result.primary_recommendation is not None
        assert result.confidence_level > 0
        assert result.processing_time_ms > 0
        assert len(result.alternative_recommendations) > 0
        assert len(result.scenario_analysis) > 0
        assert len(result.sensitivity_analysis) > 0
        assert result.explanation is not None
        assert result.risk_assessment is not None
    
    @pytest.mark.asyncio
    async def test_provide_decision_support_expert_system(self, decision_support_service,
                                                         sample_field_conditions,
                                                         sample_crop_requirements,
                                                         sample_fertilizer_specification,
                                                         sample_equipment):
        """Test decision support with expert system rule."""
        result = await decision_support_service.provide_decision_support(
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            available_equipment=sample_equipment,
            decision_rule=DecisionRule.EXPERT_SYSTEM,
            include_scenarios=False,
            include_sensitivity=False
        )
        
        assert isinstance(result, DecisionSupportResult)
        assert result.decision_id is not None
        assert result.primary_recommendation is not None
        assert len(result.expert_rules_applied) > 0
        assert result.scenario_analysis == []
        assert result.sensitivity_analysis == []
    
    @pytest.mark.asyncio
    async def test_provide_decision_support_weighted_sum(self, decision_support_service,
                                                        sample_field_conditions,
                                                        sample_crop_requirements,
                                                        sample_fertilizer_specification,
                                                        sample_equipment):
        """Test decision support with weighted sum rule."""
        result = await decision_support_service.provide_decision_support(
            field_conditions=sample_field_conditions,
            crop_requirements=sample_crop_requirements,
            fertilizer_specification=sample_fertilizer_specification,
            available_equipment=sample_equipment,
            decision_rule=DecisionRule.WEIGHTED_SUM,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        assert isinstance(result, DecisionSupportResult)
        assert result.decision_id is not None
        assert result.primary_recommendation is not None
        assert result.decision_matrix is not None
        assert len(result.decision_matrix.methods) > 0
        assert len(result.decision_matrix.criteria) > 0
    
    @pytest.mark.asyncio
    async def test_apply_decision_tree(self, decision_support_service,
                                      sample_field_conditions,
                                      sample_crop_requirements,
                                      sample_fertilizer_specification,
                                      sample_equipment):
        """Test decision tree application."""
        recommendation, path = await decision_support_service._apply_decision_tree(
            sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert recommendation is not None
        assert isinstance(path, list)
        assert len(path) > 0
        assert all(isinstance(node, DecisionNode) for node in path)
    
    @pytest.mark.asyncio
    async def test_apply_expert_system(self, decision_support_service,
                                      sample_field_conditions,
                                      sample_crop_requirements,
                                      sample_fertilizer_specification,
                                      sample_equipment):
        """Test expert system application."""
        recommendation, rules = await decision_support_service._apply_expert_system(
            sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert recommendation is not None
        assert isinstance(rules, list)
        assert all(isinstance(rule, ExpertRule) for rule in rules)
    
    @pytest.mark.asyncio
    async def test_apply_weighted_sum(self, decision_support_service,
                                     sample_field_conditions,
                                     sample_crop_requirements,
                                     sample_fertilizer_specification,
                                     sample_equipment):
        """Test weighted sum application."""
        recommendation, path = await decision_support_service._apply_weighted_sum(
            sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert recommendation is not None
        assert isinstance(path, list)
        assert len(path) == 1
        assert path[0].node_id == "weighted_sum"
    
    @pytest.mark.asyncio
    async def test_generate_alternatives(self, decision_support_service,
                                        sample_field_conditions,
                                        sample_crop_requirements,
                                        sample_fertilizer_specification,
                                        sample_equipment):
        """Test alternative generation."""
        alternatives = await decision_support_service._generate_alternatives(
            "broadcast", sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert isinstance(alternatives, list)
        assert len(alternatives) <= 3
        assert "broadcast" not in alternatives
        assert all(isinstance(alt, str) for alt in alternatives)
    
    @pytest.mark.asyncio
    async def test_perform_scenario_analysis(self, decision_support_service,
                                            sample_field_conditions,
                                            sample_crop_requirements,
                                            sample_fertilizer_specification,
                                            sample_equipment):
        """Test scenario analysis."""
        scenarios = await decision_support_service._perform_scenario_analysis(
            sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert isinstance(scenarios, list)
        assert len(scenarios) == 3  # best_case, worst_case, most_likely
        
        for scenario in scenarios:
            assert isinstance(scenario, ScenarioResult)
            assert scenario.scenario_type in [ScenarioType.BEST_CASE, ScenarioType.WORST_CASE, ScenarioType.MOST_LIKELY]
            assert isinstance(scenario.method_rankings, list)
            assert isinstance(scenario.key_factors, list)
            assert isinstance(scenario.risk_factors, list)
            assert isinstance(scenario.recommendations, list)
            assert 0 <= scenario.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_perform_sensitivity_analysis(self, decision_support_service,
                                               sample_field_conditions,
                                               sample_crop_requirements,
                                               sample_fertilizer_specification,
                                               sample_equipment):
        """Test sensitivity analysis."""
        sensitivity_results = await decision_support_service._perform_sensitivity_analysis(
            sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert isinstance(sensitivity_results, list)
        assert len(sensitivity_results) > 0
        
        for result in sensitivity_results:
            assert isinstance(result, SensitivityResult)
            assert result.parameter is not None
            assert isinstance(result.base_value, (int, float))
            assert isinstance(result.sensitivity_range, tuple)
            assert len(result.sensitivity_range) == 2
            assert isinstance(result.impact_on_ranking, dict)
            assert isinstance(result.recommendation_change, bool)
    
    @pytest.mark.asyncio
    async def test_create_decision_matrix(self, decision_support_service,
                                         sample_field_conditions,
                                         sample_crop_requirements,
                                         sample_fertilizer_specification,
                                         sample_equipment):
        """Test decision matrix creation."""
        methods = ["broadcast", "band", "injection"]
        
        matrix = await decision_support_service._create_decision_matrix(
            methods, sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert isinstance(matrix, DecisionMatrix)
        assert matrix.methods == methods
        assert len(matrix.criteria) > 0
        assert len(matrix.scores) == len(methods)
        assert len(matrix.weights) == len(matrix.criteria)
        assert len(matrix.weighted_scores) == len(methods)
        assert len(matrix.rankings) == len(methods)
        
        # Check that weights sum to 1
        assert abs(sum(matrix.weights.values()) - 1.0) < 0.01
    
    @pytest.mark.asyncio
    async def test_assess_risks(self, decision_support_service,
                               sample_field_conditions,
                               sample_crop_requirements,
                               sample_fertilizer_specification,
                               sample_equipment):
        """Test risk assessment."""
        risks = await decision_support_service._assess_risks(
            "broadcast", sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert isinstance(risks, dict)
        assert "environmental_risks" in risks
        assert "economic_risks" in risks
        assert "operational_risks" in risks
        assert "weather_risks" in risks
        assert "equipment_risks" in risks
        assert "overall_risk_level" in risks
        assert risks["overall_risk_level"] in ["low", "medium", "high"]
        
        for risk_type in ["environmental_risks", "economic_risks", "operational_risks", "weather_risks", "equipment_risks"]:
            assert isinstance(risks[risk_type], list)
    
    def test_evaluate_condition(self, decision_support_service,
                               sample_field_conditions,
                               sample_crop_requirements,
                               sample_fertilizer_specification,
                               sample_equipment):
        """Test condition evaluation."""
        # Test field size condition
        value = decision_support_service._evaluate_condition(
            "field_size_acres", sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        assert value == sample_field_conditions.field_size_acres
        
        # Test soil type condition
        value = decision_support_service._evaluate_condition(
            "soil_type", sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        assert value == 0.5  # Clay soil
        
        # Test unknown condition
        value = decision_support_service._evaluate_condition(
            "unknown_condition", sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        assert value == 0.5  # Default value
    
    def test_evaluate_expert_rule(self, decision_support_service,
                                  sample_field_conditions,
                                  sample_crop_requirements,
                                  sample_fertilizer_specification,
                                  sample_equipment):
        """Test expert rule evaluation."""
        # Create a test rule
        rule = ExpertRule(
            rule_id="test_rule",
            condition="field_size_acres > 100 AND soil_type == 'clay'",
            conclusion="RECOMMEND band_application",
            confidence=0.9,
            priority=1,
            description="Test rule for large clay fields"
        )
        
        # Test rule that should apply
        applies = decision_support_service._evaluate_expert_rule(
            rule, sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        assert applies is True
        
        # Test rule that shouldn't apply
        rule.condition = "field_size_acres > 200 AND soil_type == 'sandy'"
        applies = decision_support_service._evaluate_expert_rule(
            rule, sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        assert applies is False
    
    @pytest.mark.asyncio
    async def test_score_method_weighted_sum(self, decision_support_service,
                                            sample_field_conditions,
                                            sample_crop_requirements,
                                            sample_fertilizer_specification,
                                            sample_equipment):
        """Test method scoring with weighted sum."""
        score = await decision_support_service._score_method_weighted_sum(
            "broadcast", sample_field_conditions, sample_crop_requirements,
            sample_fertilizer_specification, sample_equipment
        )
        
        assert isinstance(score, float)
        assert 0 <= score <= 1
        
        # Test different methods
        methods = ["broadcast", "band", "injection", "fertigation", "variable_rate"]
        scores = []
        
        for method in methods:
            score = await decision_support_service._score_method_weighted_sum(
                method, sample_field_conditions, sample_crop_requirements,
                sample_fertilizer_specification, sample_equipment
            )
            scores.append(score)
            assert 0 <= score <= 1
        
        # Check that scores are different (not all the same)
        assert len(set(scores)) > 1
    
    @pytest.mark.asyncio
    async def test_score_method_on_criterion(self, decision_support_service,
                                            sample_field_conditions,
                                            sample_crop_requirements,
                                            sample_fertilizer_specification,
                                            sample_equipment):
        """Test method scoring on specific criteria."""
        criteria = ["cost_effectiveness", "application_efficiency", "environmental_impact"]
        
        for criterion in criteria:
            score = await decision_support_service._score_method_on_criterion(
                "broadcast", criterion, sample_field_conditions, sample_crop_requirements,
                sample_fertilizer_specification, sample_equipment
            )
            
            assert isinstance(score, float)
            assert 0 <= score <= 1
    
    def test_generate_parameter_variations(self, decision_support_service):
        """Test parameter variation generation."""
        # Test with non-zero base value
        variations = decision_support_service._generate_parameter_variations(100.0)
        assert isinstance(variations, list)
        assert len(variations) == 5
        assert all(isinstance(v, float) for v in variations)
        assert min(variations) < 100.0 < max(variations)
        
        # Test with zero base value
        variations = decision_support_service._generate_parameter_variations(0.0)
        assert isinstance(variations, list)
        assert len(variations) == 5
        assert all(isinstance(v, float) for v in variations)
    
    def test_find_critical_threshold(self, decision_support_service):
        """Test critical threshold finding."""
        # Test with multiple values
        impact = {"0.5": 0.3, "0.75": 0.5, "1.0": 0.7, "1.25": 0.8, "1.5": 0.9}
        threshold = decision_support_service._find_critical_threshold(impact)
        assert threshold is not None
        assert isinstance(threshold, float)
        
        # Test with single value
        impact = {"1.0": 0.7}
        threshold = decision_support_service._find_critical_threshold(impact)
        assert threshold is None
    
    def test_detect_recommendation_change(self, decision_support_service):
        """Test recommendation change detection."""
        # Test with significant change
        impact = {"0.5": 0.3, "0.75": 0.5, "1.0": 0.7, "1.25": 0.8, "1.5": 0.9}
        changed = decision_support_service._detect_recommendation_change(impact)
        assert changed is True
        
        # Test with minimal change
        impact = {"0.5": 0.7, "0.75": 0.7, "1.0": 0.7, "1.25": 0.7, "1.5": 0.7}
        changed = decision_support_service._detect_recommendation_change(impact)
        assert changed is False
    
    @pytest.mark.asyncio
    async def test_calculate_confidence_level(self, decision_support_service):
        """Test confidence level calculation."""
        # Test with decision tree path
        path = [DecisionNode("test", "test_condition", 0.5, confidence=0.8)]
        confidence = await decision_support_service._calculate_confidence_level(path, [], [], [])
        assert confidence == 0.8
        
        # Test with expert rules
        rules = [ExpertRule("rule1", "condition1", "conclusion1", 0.9, 1, "desc1")]
        confidence = await decision_support_service._calculate_confidence_level([], rules, [], [])
        assert confidence == 0.9
        
        # Test with no factors
        confidence = await decision_support_service._calculate_confidence_level([], [], [], [])
        assert confidence == 0.7  # Default confidence
    
    @pytest.mark.asyncio
    async def test_error_handling(self, decision_support_service):
        """Test error handling in decision support."""
        # Test with invalid field conditions
        with pytest.raises(Exception):
            await decision_support_service.provide_decision_support(
                field_conditions=None,
                crop_requirements=None,
                fertilizer_specification=None,
                available_equipment=[]
            )


class TestDecisionSupportIntegration:
    """Integration tests for decision support system."""
    
    @pytest.mark.asyncio
    async def test_full_decision_support_workflow(self):
        """Test complete decision support workflow."""
        service = DecisionSupportService()
        
        # Create test data
        field_conditions = FieldConditions(
            field_size_acres=200.0,
            soil_type="clay",
            soil_ph=6.0,
            organic_matter_percent=2.5,
            slope_percent=5.0,
            drainage_class="moderate",
            water_body_distance=150.0,
            environmental_regulations="standard"
        )
        
        crop_requirements = CropRequirements(
            crop_type="corn",
            growth_stage="vegetative",
            nitrogen_requirement=150.0,
            phosphorus_requirement=50.0,
            potassium_requirement=100.0,
            row_spacing_inches=30.0,
            planting_date="2024-04-15",
            expected_harvest_date="2024-09-15"
        )
        
        fertilizer_specification = FertilizerSpecification(
            fertilizer_type="liquid",
            npk_ratio="32-0-0",
            form=FertilizerForm.LIQUID,
            solubility=100.0,
            release_rate="immediate",
            cost_per_unit=0.50,
            unit="gallon"
        )
        
        equipment = [
            EquipmentSpecification(
                equipment_type=EquipmentType.SPREADER,
                capacity=1200.0,
                capacity_unit="gallons",
                application_width=25.0,
                fuel_efficiency=0.80,
                maintenance_cost_per_hour=30.0
            )
        ]
        
        # Test decision tree workflow
        result = await service.provide_decision_support(
            field_conditions=field_conditions,
            crop_requirements=crop_requirements,
            fertilizer_specification=fertilizer_specification,
            available_equipment=equipment,
            decision_rule=DecisionRule.DECISION_TREE,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        # Verify comprehensive result
        assert result.decision_id is not None
        assert result.primary_recommendation is not None
        assert len(result.alternative_recommendations) > 0
        assert len(result.scenario_analysis) == 3
        assert len(result.sensitivity_analysis) > 0
        assert result.decision_matrix is not None
        assert result.risk_assessment is not None
        assert result.explanation is not None
        assert 0 <= result.confidence_level <= 1
        assert result.processing_time_ms > 0
        
        # Verify scenario analysis
        scenario_types = [scenario.scenario_type for scenario in result.scenario_analysis]
        assert ScenarioType.BEST_CASE in scenario_types
        assert ScenarioType.WORST_CASE in scenario_types
        assert ScenarioType.MOST_LIKELY in scenario_types
        
        # Verify sensitivity analysis
        for sensitivity in result.sensitivity_analysis:
            assert sensitivity.parameter is not None
            assert isinstance(sensitivity.base_value, (int, float))
            assert len(sensitivity.sensitivity_range) == 2
            assert isinstance(sensitivity.impact_on_ranking, dict)
        
        # Verify decision matrix
        assert len(result.decision_matrix.methods) > 0
        assert len(result.decision_matrix.criteria) > 0
        assert len(result.decision_matrix.rankings) > 0
        
        # Verify risk assessment
        assert "overall_risk_level" in result.risk_assessment
        assert result.risk_assessment["overall_risk_level"] in ["low", "medium", "high"]
