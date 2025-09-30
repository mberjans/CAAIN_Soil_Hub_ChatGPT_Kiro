"""
Decision Support System for Fertilizer Application Method Selection.

This service implements advanced decision support tools including decision trees,
expert systems, scenario analysis, sensitivity analysis, and interactive decision
tools to help farmers make informed decisions about fertilizer application methods.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple, Union
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum
import json
import numpy as np
from scipy.optimize import minimize
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

from src.models.application_models import (
    ApplicationMethod, ApplicationMethodType, FieldConditions, 
    CropRequirements, FertilizerSpecification, EquipmentSpecification, ApplicationRequest
)
from src.models.method_models import MethodComparison, ApplicationMethod as MethodModel
from src.services.application_method_service import ApplicationMethodService
from src.services.comparison_service import MethodComparisonService, ComparisonCriteria

logger = logging.getLogger(__name__)


class DecisionRule(str, Enum):
    """Available decision rules for method selection."""
    DECISION_TREE = "decision_tree"
    EXPERT_SYSTEM = "expert_system"
    WEIGHTED_SUM = "weighted_sum"
    TOPSIS = "topsis"
    ELECTRE = "electre"
    FUZZY_LOGIC = "fuzzy_logic"


class ScenarioType(str, Enum):
    """Types of scenario analysis."""
    BEST_CASE = "best_case"
    WORST_CASE = "worst_case"
    MOST_LIKELY = "most_likely"
    SENSITIVITY = "sensitivity"
    MONTE_CARLO = "monte_carlo"


@dataclass
class DecisionNode:
    """Node in a decision tree."""
    node_id: str
    condition: str
    threshold: float
    true_branch: Optional[str] = None
    false_branch: Optional[str] = None
    method_recommendation: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ExpertRule:
    """Expert system rule."""
    rule_id: str
    condition: str
    conclusion: str
    confidence: float
    priority: int
    description: str


@dataclass
class ScenarioResult:
    """Result of scenario analysis."""
    scenario_type: ScenarioType
    method_rankings: List[Tuple[str, float]]
    key_factors: List[str]
    risk_factors: List[str]
    recommendations: List[str]
    confidence: float


@dataclass
class SensitivityResult:
    """Result of sensitivity analysis."""
    parameter: str
    base_value: float
    sensitivity_range: Tuple[float, float]
    impact_on_ranking: Dict[str, float]
    critical_threshold: Optional[float]
    recommendation_change: bool


@dataclass
class DecisionMatrix:
    """Decision matrix for method evaluation."""
    methods: List[str]
    criteria: List[str]
    scores: Dict[str, Dict[str, float]]
    weights: Dict[str, float]
    weighted_scores: Dict[str, float]
    rankings: List[Tuple[str, float]]


@dataclass
class DecisionSupportResult:
    """Comprehensive decision support result."""
    decision_id: str
    primary_recommendation: str
    alternative_recommendations: List[str]
    decision_tree_path: List[DecisionNode]
    expert_rules_applied: List[ExpertRule]
    scenario_analysis: List[ScenarioResult]
    sensitivity_analysis: List[SensitivityResult]
    decision_matrix: DecisionMatrix
    risk_assessment: Dict[str, Any]
    explanation: str
    confidence_level: float
    processing_time_ms: float


class DecisionSupportService:
    """Advanced decision support system for fertilizer application method selection."""
    
    def __init__(self):
        self.application_service = ApplicationMethodService()
        self.comparison_service = MethodComparisonService()
        self._initialize_decision_trees()
        self._initialize_expert_rules()
        self._initialize_scenario_templates()
    
    def _initialize_decision_trees(self):
        """Initialize decision trees for different scenarios."""
        self.decision_trees = {
            "field_size_based": {
                "root": DecisionNode(
                    node_id="field_size",
                    condition="field_size_acres",
                    threshold=50.0,
                    true_branch="large_field",
                    false_branch="small_field"
                ),
                "large_field": DecisionNode(
                    node_id="large_field",
                    condition="soil_type",
                    threshold=0.5,  # Clay content
                    true_branch="clay_soil",
                    false_branch="sandy_soil",
                    method_recommendation="broadcast"
                ),
                "small_field": DecisionNode(
                    node_id="small_field",
                    condition="precision_required",
                    threshold=0.8,
                    true_branch="high_precision",
                    false_branch="standard_precision",
                    method_recommendation="band"
                ),
                "clay_soil": DecisionNode(
                    node_id="clay_soil",
                    condition="drainage",
                    threshold=0.7,
                    true_branch="good_drainage",
                    false_branch="poor_drainage",
                    method_recommendation="band",
                    confidence=0.9
                ),
                "sandy_soil": DecisionNode(
                    node_id="sandy_soil",
                    condition="organic_matter",
                    threshold=2.0,
                    true_branch="high_om",
                    false_branch="low_om",
                    method_recommendation="injection",
                    confidence=0.85
                ),
                "high_precision": DecisionNode(
                    node_id="high_precision",
                    condition="equipment_available",
                    threshold=0.8,
                    true_branch="equipment_ok",
                    false_branch="equipment_limited",
                    method_recommendation="variable_rate",
                    confidence=0.95
                ),
                "standard_precision": DecisionNode(
                    node_id="standard_precision",
                    condition="cost_sensitivity",
                    threshold=0.6,
                    true_branch="cost_sensitive",
                    false_branch="cost_tolerant",
                    method_recommendation="broadcast",
                    confidence=0.8
                )
            },
            "crop_based": {
                "root": DecisionNode(
                    node_id="crop_type",
                    condition="crop_type",
                    threshold=0.5,
                    true_branch="row_crop",
                    false_branch="broadcast_crop"
                ),
                "row_crop": DecisionNode(
                    node_id="row_crop",
                    condition="planting_spacing",
                    threshold=30.0,  # inches
                    true_branch="wide_spacing",
                    false_branch="narrow_spacing",
                    method_recommendation="band"
                ),
                "broadcast_crop": DecisionNode(
                    node_id="broadcast_crop",
                    condition="field_size_acres",
                    threshold=100.0,
                    true_branch="large_field",
                    false_branch="small_field",
                    method_recommendation="broadcast"
                )
            }
        }
    
    def _initialize_expert_rules(self):
        """Initialize expert system rules."""
        self.expert_rules = [
            ExpertRule(
                rule_id="rule_001",
                condition="field_size_acres > 200 AND soil_type == 'clay' AND drainage == 'poor'",
                conclusion="RECOMMEND band_application",
                confidence=0.95,
                priority=1,
                description="Large clay fields with poor drainage should use band application to reduce runoff risk"
            ),
            ExpertRule(
                rule_id="rule_002",
                condition="crop_type == 'corn' AND planting_spacing < 30 AND precision_equipment == True",
                conclusion="RECOMMEND variable_rate",
                confidence=0.9,
                priority=1,
                description="Corn with narrow spacing and precision equipment should use variable rate application"
            ),
            ExpertRule(
                rule_id="rule_003",
                condition="organic_matter < 2.0 AND soil_type == 'sandy' AND rainfall_annual > 40",
                conclusion="RECOMMEND injection",
                confidence=0.85,
                priority=2,
                description="Sandy soils with low organic matter and high rainfall need injection to prevent leaching"
            ),
            ExpertRule(
                rule_id="rule_004",
                condition="field_size_acres < 50 AND labor_availability == 'limited' AND cost_sensitivity == 'high'",
                conclusion="RECOMMEND broadcast",
                confidence=0.8,
                priority=3,
                description="Small fields with limited labor and high cost sensitivity should use broadcast application"
            ),
            ExpertRule(
                rule_id="rule_005",
                condition="environmental_regulations == 'strict' AND water_body_distance < 100",
                conclusion="RECOMMEND injection",
                confidence=0.9,
                priority=1,
                description="Fields near water bodies with strict regulations should use injection to minimize runoff"
            ),
            ExpertRule(
                rule_id="rule_006",
                condition="crop_type == 'soybean' AND nitrogen_requirement < 50 AND soil_nitrogen > 20",
                conclusion="RECOMMEND foliar",
                confidence=0.75,
                priority=3,
                description="Soybeans with low nitrogen requirements and adequate soil nitrogen can use foliar application"
            ),
            ExpertRule(
                rule_id="rule_007",
                condition="irrigation_system == 'drip' AND fertilizer_type == 'liquid'",
                conclusion="RECOMMEND fertigation",
                confidence=0.95,
                priority=1,
                description="Fields with drip irrigation and liquid fertilizer should use fertigation"
            ),
            ExpertRule(
                rule_id="rule_008",
                condition="slope_percent > 8 AND soil_type == 'clay' AND rainfall_seasonal > 20",
                conclusion="RECOMMEND injection",
                confidence=0.9,
                priority=1,
                description="Steep clay slopes with high seasonal rainfall need injection to prevent erosion"
            )
        ]
    
    def _initialize_scenario_templates(self):
        """Initialize scenario analysis templates."""
        self.scenario_templates = {
            ScenarioType.BEST_CASE: {
                "description": "Optimal conditions with best-case assumptions",
                "factors": {
                    "weather": 0.9,
                    "equipment_performance": 0.95,
                    "labor_efficiency": 0.9,
                    "soil_conditions": 0.85
                }
            },
            ScenarioType.WORST_CASE: {
                "description": "Challenging conditions with worst-case assumptions",
                "factors": {
                    "weather": 0.3,
                    "equipment_performance": 0.6,
                    "labor_efficiency": 0.5,
                    "soil_conditions": 0.4
                }
            },
            ScenarioType.MOST_LIKELY: {
                "description": "Realistic conditions based on historical data",
                "factors": {
                    "weather": 0.7,
                    "equipment_performance": 0.8,
                    "labor_efficiency": 0.75,
                    "soil_conditions": 0.7
                }
            }
        }
    
    async def provide_decision_support(
        self,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        farmer_preferences: Optional[Dict[str, Any]] = None,
        decision_rule: DecisionRule = DecisionRule.DECISION_TREE,
        include_scenarios: bool = True,
        include_sensitivity: bool = True
    ) -> DecisionSupportResult:
        """
        Provide comprehensive decision support for fertilizer application method selection.
        
        Args:
            field_conditions: Field conditions and characteristics
            crop_requirements: Crop requirements and constraints
            fertilizer_specification: Fertilizer specifications
            available_equipment: Available equipment inventory
            farmer_preferences: Farmer preferences and constraints
            decision_rule: Decision rule to use for method selection
            include_scenarios: Whether to include scenario analysis
            include_sensitivity: Whether to include sensitivity analysis
            
        Returns:
            DecisionSupportResult with comprehensive decision support information
        """
        start_time = time.time()
        decision_id = str(uuid4())
        
        try:
            logger.info(f"Providing decision support for request {decision_id}")
            
            # Apply decision rule to get primary recommendation
            if decision_rule == DecisionRule.DECISION_TREE:
                expert_rules_applied = []
                primary_recommendation, decision_tree_path = await self._apply_decision_tree(
                    field_conditions, crop_requirements, fertilizer_specification, available_equipment
                )
            elif decision_rule == DecisionRule.EXPERT_SYSTEM:
                primary_recommendation, expert_rules_applied = await self._apply_expert_system(
                    field_conditions, crop_requirements, fertilizer_specification, available_equipment
                )
                decision_tree_path = []
            else:
                primary_recommendation, decision_tree_path = await self._apply_weighted_sum(
                    field_conditions, crop_requirements, fertilizer_specification, available_equipment
                )
                expert_rules_applied = []
            
            # Generate alternative recommendations
            alternative_recommendations = await self._generate_alternatives(
                primary_recommendation, field_conditions, crop_requirements, 
                fertilizer_specification, available_equipment
            )
            
            # Perform scenario analysis if requested
            scenario_analysis = []
            if include_scenarios:
                scenario_analysis = await self._perform_scenario_analysis(
                    field_conditions, crop_requirements, fertilizer_specification, available_equipment
                )
            
            # Perform sensitivity analysis if requested
            sensitivity_analysis = []
            if include_sensitivity:
                sensitivity_analysis = await self._perform_sensitivity_analysis(
                    field_conditions, crop_requirements, fertilizer_specification, available_equipment
                )
            
            # Create decision matrix
            decision_matrix = await self._create_decision_matrix(
                [primary_recommendation] + alternative_recommendations,
                field_conditions, crop_requirements, fertilizer_specification, available_equipment
            )
            
            # Perform risk assessment
            risk_assessment = await self._assess_risks(
                primary_recommendation, field_conditions, crop_requirements, 
                fertilizer_specification, available_equipment
            )
            
            # Generate explanation
            explanation = await self._generate_explanation(
                primary_recommendation, decision_tree_path, expert_rules_applied,
                scenario_analysis, sensitivity_analysis, risk_assessment
            )
            
            # Calculate confidence level
            confidence_level = await self._calculate_confidence_level(
                decision_tree_path, expert_rules_applied, scenario_analysis, sensitivity_analysis
            )
            
            result = DecisionSupportResult(
                decision_id=decision_id,
                primary_recommendation=primary_recommendation,
                alternative_recommendations=alternative_recommendations,
                decision_tree_path=decision_tree_path,
                expert_rules_applied=expert_rules_applied if 'expert_rules_applied' in locals() else [],
                scenario_analysis=scenario_analysis,
                sensitivity_analysis=sensitivity_analysis,
                decision_matrix=decision_matrix,
                risk_assessment=risk_assessment,
                explanation=explanation,
                confidence_level=confidence_level,
                processing_time_ms=(time.time() - start_time) * 1000
            )
            
            logger.info(f"Decision support completed for request {decision_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error providing decision support: {e}")
            raise Exception(f"Decision support failed: {str(e)}")
    
    async def _apply_decision_tree(
        self,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Tuple[str, List[DecisionNode]]:
        """Apply decision tree logic to select application method."""
        # Select appropriate decision tree based on field characteristics
        if field_conditions.field_size_acres > 100:
            tree_name = "field_size_based"
        else:
            tree_name = "crop_based"
        
        tree = self.decision_trees[tree_name]
        path = []
        current_node = tree["root"]
        
        # Traverse the decision tree
        while current_node:
            path.append(current_node)
            
            if current_node.method_recommendation:
                return current_node.method_recommendation, path
            
            # Evaluate condition and move to next node
            condition_value = self._evaluate_condition(
                current_node.condition, field_conditions, crop_requirements, 
                fertilizer_specification, available_equipment
            )
            
            if condition_value >= current_node.threshold:
                next_node_id = current_node.true_branch
            else:
                next_node_id = current_node.false_branch
            
            if next_node_id and next_node_id in tree:
                current_node = tree[next_node_id]
            else:
                break
        
        # Default recommendation if tree traversal doesn't reach a conclusion
        return "broadcast", path
    
    async def _apply_expert_system(
        self,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Tuple[str, List[ExpertRule]]:
        """Apply expert system rules to select application method."""
        applicable_rules = []
        method_scores = {}
        
        # Evaluate each expert rule
        for rule in self.expert_rules:
            if self._evaluate_expert_rule(rule, field_conditions, crop_requirements, 
                                        fertilizer_specification, available_equipment):
                applicable_rules.append(rule)
                
                # Extract method recommendation from conclusion
                if "RECOMMEND" in rule.conclusion:
                    method = rule.conclusion.split("RECOMMEND ")[1].replace("_", " ").lower()
                    if method not in method_scores:
                        method_scores[method] = 0
                    method_scores[method] += rule.confidence * rule.priority
        
        # Select method with highest score
        if method_scores:
            primary_recommendation = max(method_scores.items(), key=lambda x: x[1])[0]
        else:
            primary_recommendation = "broadcast"
        
        return primary_recommendation, applicable_rules
    
    async def _apply_weighted_sum(
        self,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Tuple[str, List[DecisionNode]]:
        """Apply weighted sum decision rule."""
        # Get all available methods
        methods = ["broadcast", "band", "sidedress", "foliar", "injection", "fertigation", "variable_rate"]
        
        # Score each method based on field conditions
        method_scores = {}
        for method in methods:
            score = await self._score_method_weighted_sum(
                method, field_conditions, crop_requirements, 
                fertilizer_specification, available_equipment
            )
            method_scores[method] = score
        
        # Select method with highest score
        primary_recommendation = max(method_scores.items(), key=lambda x: x[1])[0]
        
        # Create a simple decision path for weighted sum
        path = [DecisionNode(
            node_id="weighted_sum",
            condition="weighted_sum_score",
            threshold=0.0,
            method_recommendation=primary_recommendation,
            confidence=max(method_scores.values())
        )]
        
        return primary_recommendation, path
    
    async def _generate_alternatives(
        self,
        primary_recommendation: str,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> List[str]:
        """Generate alternative method recommendations."""
        all_methods = ["broadcast", "band", "sidedress", "foliar", "injection", "fertigation", "variable_rate"]
        alternatives = [method for method in all_methods if method != primary_recommendation]
        
        # Score alternatives and return top 2-3
        alternative_scores = {}
        for method in alternatives:
            score = await self._score_method_weighted_sum(
                method, field_conditions, crop_requirements, 
                fertilizer_specification, available_equipment
            )
            alternative_scores[method] = score
        
        # Return top 3 alternatives
        sorted_alternatives = sorted(alternative_scores.items(), key=lambda x: x[1], reverse=True)
        return [method for method, score in sorted_alternatives[:3]]
    
    # Helper methods
    def _evaluate_condition(
        self,
        condition: str,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> float:
        """Evaluate a condition string and return a numeric value."""
        # Map condition names to actual values
        condition_map = {
            "field_size_acres": field_conditions.field_size_acres,
            "soil_type": 0.5 if field_conditions.soil_type == "clay" else 0.3,  # Clay content
            "drainage": 0.8 if field_conditions.drainage_class == "well" else 0.4,
            "precision_required": 0.7,  # Default value
            "equipment_available": 0.8 if available_equipment else 0.3,
            "cost_sensitivity": 0.5,  # Default value
            "crop_type": 0.7 if crop_requirements.crop_type in ["corn", "soybean"] else 0.5,
            "planting_spacing": crop_requirements.row_spacing_inches if hasattr(crop_requirements, 'row_spacing_inches') else 30.0,
            "organic_matter": field_conditions.field_size_acres,
            "slope_percent": field_conditions.slope_percent,
            "field_size_acres": field_conditions.field_size_acres
        }
        
        return condition_map.get(condition, 0.5)
    
    def _evaluate_expert_rule(
        self,
        rule: ExpertRule,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> bool:
        """Evaluate whether an expert rule applies to the current conditions."""
        # Simplified rule evaluation - in production, this would use a proper rule engine
        condition_parts = rule.condition.split(" AND ")
        
        for part in condition_parts:
            if "field_size_acres >" in part:
                threshold = float(part.split("> ")[1])
                if field_conditions.field_size_acres <= threshold:
                    return False
            elif "soil_type ==" in part:
                required_type = part.split("== '")[1].split("'")[0]
                if field_conditions.soil_type != required_type:
                    return False
            elif "crop_type ==" in part:
                required_crop = part.split("== '")[1].split("'")[0]
                if crop_requirements.crop_type != required_crop:
                    return False
            # Add more condition evaluations as needed
        
        return True
    
    async def _score_method_weighted_sum(
        self,
        method: str,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> float:
        """Score a method using weighted sum approach."""
        # Simplified scoring - in production, this would be more sophisticated
        base_scores = {
            "broadcast": 0.7,
            "band": 0.8,
            "sidedress": 0.75,
            "foliar": 0.6,
            "injection": 0.85,
            "fertigation": 0.9,
            "variable_rate": 0.95
        }
        
        base_score = base_scores.get(method, 0.5)
        
        # Adjust based on field conditions
        if field_conditions.field_size_acres > 200 and method == "broadcast":
            base_score += 0.1
        elif field_conditions.field_size_acres < 50 and method == "variable_rate":
            base_score -= 0.2
        
        # Adjust based on soil type
        if field_conditions.soil_type == "clay" and method == "injection":
            base_score += 0.1
        elif field_conditions.soil_type == "sandy" and method == "broadcast":
            base_score -= 0.1
        
        return min(max(base_score, 0.0), 1.0)
    
    async def _perform_scenario_analysis(
        self,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> List[ScenarioResult]:
        """Perform scenario analysis for different conditions."""
        scenarios = []
        
        for scenario_type, template in self.scenario_templates.items():
            # Adjust field conditions based on scenario
            adjusted_conditions = self._adjust_conditions_for_scenario(field_conditions, template["factors"])
            
            # Get method rankings for this scenario
            method_rankings = await self._get_method_rankings_for_scenario(
                adjusted_conditions, crop_requirements, fertilizer_specification, available_equipment
            )
            
            # Identify key factors and risk factors
            key_factors = self._identify_key_factors(template["factors"])
            risk_factors = self._identify_risk_factors(scenario_type, template["factors"])
            
            # Generate recommendations
            recommendations = self._generate_scenario_recommendations(scenario_type, method_rankings)
            
            scenario_result = ScenarioResult(
                scenario_type=scenario_type,
                method_rankings=method_rankings,
                key_factors=key_factors,
                risk_factors=risk_factors,
                recommendations=recommendations,
                confidence=template["factors"]["weather"] * 0.8  # Simplified confidence calculation
            )
            
            scenarios.append(scenario_result)
        
        return scenarios
    
    async def _perform_sensitivity_analysis(
        self,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> List[SensitivityResult]:
        """Perform sensitivity analysis on key parameters."""
        sensitivity_results = []
        
        # Parameters to analyze
        parameters = [
            ("field_size_acres", field_conditions.field_size_acres),
            ("field_size_acres", field_conditions.field_size_acres),
            ("field_size_acres", field_conditions.field_size_acres),
            ("slope_percent", field_conditions.slope_percent),
            ("cost_sensitivity", 0.5)  # Default value
        ]
        
        for param_name, base_value in parameters:
            # Test parameter variations
            variations = self._generate_parameter_variations(base_value)
            impact_on_ranking = {}
            
            for variation in variations:
                # Adjust conditions with variation
                adjusted_conditions = self._adjust_parameter(field_conditions, param_name, variation)
                
                # Get method ranking for this variation
                ranking = await self._get_method_rankings_for_scenario(
                    adjusted_conditions, crop_requirements, fertilizer_specification, available_equipment
                )
                
                # Store impact
                impact_on_ranking[str(variation)] = ranking[0][1] if ranking else 0.0
            
            # Calculate sensitivity metrics
            sensitivity_range = (min(variations), max(variations))
            critical_threshold = self._find_critical_threshold(impact_on_ranking)
            recommendation_change = self._detect_recommendation_change(impact_on_ranking)
            
            sensitivity_result = SensitivityResult(
                parameter=param_name,
                base_value=base_value,
                sensitivity_range=sensitivity_range,
                impact_on_ranking=impact_on_ranking,
                critical_threshold=critical_threshold,
                recommendation_change=recommendation_change
            )
            
            sensitivity_results.append(sensitivity_result)
        
        return sensitivity_results
    
    async def _create_decision_matrix(
        self,
        methods: List[str],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> DecisionMatrix:
        """Create decision matrix for method evaluation."""
        criteria = [
            "cost_effectiveness",
            "application_efficiency", 
            "environmental_impact",
            "labor_requirements",
            "equipment_needs",
            "field_suitability",
            "nutrient_use_efficiency"
        ]
        
        # Default weights
        weights = {
            "cost_effectiveness": 0.2,
            "application_efficiency": 0.25,
            "environmental_impact": 0.15,
            "labor_requirements": 0.1,
            "equipment_needs": 0.1,
            "field_suitability": 0.1,
            "nutrient_use_efficiency": 0.1
        }
        
        # Score each method on each criterion
        scores = {}
        for method in methods:
            scores[method] = {}
            for criterion in criteria:
                score = await self._score_method_on_criterion(
                    method, criterion, field_conditions, crop_requirements,
                    fertilizer_specification, available_equipment
                )
                scores[method][criterion] = score
        
        # Calculate weighted scores
        weighted_scores = {}
        for method in methods:
            weighted_score = sum(scores[method][criterion] * weights[criterion] for criterion in criteria)
            weighted_scores[method] = weighted_score
        
        # Create rankings
        rankings = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
        
        return DecisionMatrix(
            methods=methods,
            criteria=criteria,
            scores=scores,
            weights=weights,
            weighted_scores=weighted_scores,
            rankings=rankings
        )
    
    async def _assess_risks(
        self,
        method: str,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Any]:
        """Assess risks associated with the recommended method."""
        risks = {
            "environmental_risks": [],
            "economic_risks": [],
            "operational_risks": [],
            "weather_risks": [],
            "equipment_risks": [],
            "overall_risk_level": "medium"
        }
        
        # Environmental risks
        if method in ["broadcast", "foliar"] and field_conditions.slope_percent > 5:
            risks["environmental_risks"].append("High runoff risk due to steep slope")
        
        if method == "injection" and field_conditions.soil_type == "clay":
            risks["environmental_risks"].append("Potential soil compaction with injection")
        
        # Economic risks
        if method == "variable_rate" and not any(eq.equipment_type == "precision_equipment" for eq in available_equipment):
            risks["economic_risks"].append("High equipment investment required")
        
        # Operational risks
        if method == "fertigation" and not any(eq.equipment_type == "irrigation_system" for eq in available_equipment):
            risks["operational_risks"].append("Irrigation system required but not available")
        
        # Weather risks
        if method in ["broadcast", "foliar"]:
            risks["weather_risks"].append("Weather dependent - wind and rain can affect application")
        
        # Calculate overall risk level
        total_risks = sum(len(risk_list) for risk_list in risks.values() if isinstance(risk_list, list))
        if total_risks <= 1:
            risks["overall_risk_level"] = "low"
        elif total_risks <= 3:
            risks["overall_risk_level"] = "medium"
        else:
            risks["overall_risk_level"] = "high"
        
        return risks
    
    async def _generate_explanation(
        self,
        primary_recommendation: str,
        decision_tree_path: List[DecisionNode],
        expert_rules_applied: List[ExpertRule],
        scenario_analysis: List[ScenarioResult],
        sensitivity_analysis: List[SensitivityResult],
        risk_assessment: Dict[str, Any]
    ) -> str:
        """Generate comprehensive explanation of the decision."""
        explanation_parts = []
        
        # Primary recommendation explanation
        explanation_parts.append(f"Primary Recommendation: {primary_recommendation.title()}")
        explanation_parts.append("")
        
        # Decision tree explanation
        if decision_tree_path:
            explanation_parts.append("Decision Process:")
            for node in decision_tree_path:
                if node.method_recommendation:
                    explanation_parts.append(f"- Selected {node.method_recommendation} based on {node.condition}")
                else:
                    explanation_parts.append(f"- Evaluated {node.condition} (threshold: {node.threshold})")
        
        # Expert rules explanation
        if expert_rules_applied:
            explanation_parts.append("")
            explanation_parts.append("Expert Rules Applied:")
            for rule in expert_rules_applied[:3]:  # Show top 3 rules
                explanation_parts.append(f"- {rule.description}")
        
        # Scenario analysis summary
        if scenario_analysis:
            explanation_parts.append("")
            explanation_parts.append("Scenario Analysis:")
            for scenario in scenario_analysis:
                top_method = scenario.method_rankings[0][0] if scenario.method_rankings else "N/A"
                explanation_parts.append(f"- {scenario.scenario_type.value}: {top_method}")
        
        # Risk summary
        if risk_assessment:
            explanation_parts.append("")
            explanation_parts.append(f"Risk Assessment: {risk_assessment['overall_risk_level'].upper()}")
            if risk_assessment["environmental_risks"]:
                explanation_parts.append(f"- Environmental: {len(risk_assessment['environmental_risks'])} risks identified")
            if risk_assessment["economic_risks"]:
                explanation_parts.append(f"- Economic: {len(risk_assessment['economic_risks'])} risks identified")
        
        return "\n".join(explanation_parts)
    
    async def _calculate_confidence_level(
        self,
        decision_tree_path: List[DecisionNode],
        expert_rules_applied: List[ExpertRule],
        scenario_analysis: List[ScenarioResult],
        sensitivity_analysis: List[SensitivityResult]
    ) -> float:
        """Calculate overall confidence level in the decision."""
        confidence_factors = []
        
        # Decision tree confidence
        if decision_tree_path:
            tree_confidence = max([node.confidence for node in decision_tree_path if node.confidence > 0], default=0.7)
            confidence_factors.append(tree_confidence)
        
        # Expert rules confidence
        if expert_rules_applied:
            rules_confidence = sum(rule.confidence for rule in expert_rules_applied) / len(expert_rules_applied)
            confidence_factors.append(rules_confidence)
        
        # Scenario analysis confidence
        if scenario_analysis:
            scenario_confidence = sum(scenario.confidence for scenario in scenario_analysis) / len(scenario_analysis)
            confidence_factors.append(scenario_confidence)
        
        # Overall confidence
        if confidence_factors:
            return sum(confidence_factors) / len(confidence_factors)
        else:
            return 0.7  # Default confidence
    
    async def _score_method_on_criterion(
        self,
        method: str,
        criterion: str,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> float:
        """Score a method on a specific criterion."""
        # Simplified scoring - in production, this would be more sophisticated
        criterion_scores = {
            "cost_effectiveness": {
                "broadcast": 0.9, "band": 0.7, "sidedress": 0.6, "foliar": 0.5,
                "injection": 0.4, "fertigation": 0.3, "variable_rate": 0.2
            },
            "application_efficiency": {
                "broadcast": 0.6, "band": 0.8, "sidedress": 0.7, "foliar": 0.5,
                "injection": 0.9, "fertigation": 0.95, "variable_rate": 0.9
            },
            "environmental_impact": {
                "broadcast": 0.4, "band": 0.7, "sidedress": 0.6, "foliar": 0.5,
                "injection": 0.9, "fertigation": 0.8, "variable_rate": 0.85
            },
            "labor_requirements": {
                "broadcast": 0.8, "band": 0.6, "sidedress": 0.5, "foliar": 0.4,
                "injection": 0.3, "fertigation": 0.7, "variable_rate": 0.2
            },
            "equipment_needs": {
                "broadcast": 0.9, "band": 0.7, "sidedress": 0.6, "foliar": 0.8,
                "injection": 0.5, "fertigation": 0.3, "variable_rate": 0.2
            },
            "field_suitability": {
                "broadcast": 0.8, "band": 0.7, "sidedress": 0.6, "foliar": 0.5,
                "injection": 0.7, "fertigation": 0.4, "variable_rate": 0.6
            },
            "nutrient_use_efficiency": {
                "broadcast": 0.5, "band": 0.7, "sidedress": 0.6, "foliar": 0.4,
                "injection": 0.8, "fertigation": 0.9, "variable_rate": 0.85
            }
        }
        
        return criterion_scores.get(criterion, {}).get(method, 0.5)
    
    def _adjust_conditions_for_scenario(self, field_conditions: FieldConditions, factors: Dict[str, float]) -> FieldConditions:
        """Adjust field conditions based on scenario factors."""
        # Create a copy of field conditions and adjust based on scenario factors
        adjusted = field_conditions.model_copy() if hasattr(field_conditions, 'model_copy') else field_conditions
        
        # Adjust field size based on weather factor
        if "weather" in factors:
            adjusted.field_size_acres *= factors["weather"]
        
        # Adjust soil conditions based on soil factor
        if "soil_conditions" in factors:
            adjusted.field_size_acres *= factors["soil_conditions"]
            adjusted.field_size_acres *= factors["soil_conditions"]
        
        return adjusted
    
    async def _get_method_rankings_for_scenario(
        self,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> List[Tuple[str, float]]:
        """Get method rankings for a specific scenario."""
        methods = ["broadcast", "band", "sidedress", "foliar", "injection", "fertigation", "variable_rate"]
        rankings = []
        
        for method in methods:
            score = await self._score_method_weighted_sum(
                method, field_conditions, crop_requirements, 
                fertilizer_specification, available_equipment
            )
            rankings.append((method, score))
        
        return sorted(rankings, key=lambda x: x[1], reverse=True)
    
    def _identify_key_factors(self, factors: Dict[str, float]) -> List[str]:
        """Identify key factors for a scenario."""
        key_factors = []
        for factor, value in factors.items():
            if value > 0.8:
                key_factors.append(f"{factor} (favorable)")
            elif value < 0.4:
                key_factors.append(f"{factor} (challenging)")
        return key_factors
    
    def _identify_risk_factors(self, scenario_type: ScenarioType, factors: Dict[str, float]) -> List[str]:
        """Identify risk factors for a scenario."""
        risk_factors = []
        if scenario_type == ScenarioType.WORST_CASE:
            for factor, value in factors.items():
                if value < 0.5:
                    risk_factors.append(f"Low {factor}")
        return risk_factors
    
    def _generate_scenario_recommendations(self, scenario_type: ScenarioType, method_rankings: List[Tuple[str, float]]) -> List[str]:
        """Generate recommendations for a scenario."""
        recommendations = []
        
        if method_rankings:
            top_method = method_rankings[0][0]
            
            if scenario_type == ScenarioType.BEST_CASE:
                recommendations.append(f"Optimal conditions favor {top_method}")
            elif scenario_type == ScenarioType.WORST_CASE:
                recommendations.append(f"Challenging conditions require robust method like {top_method}")
            else:
                recommendations.append(f"Realistic conditions suggest {top_method}")
        
        return recommendations
    
    def _generate_parameter_variations(self, base_value: float) -> List[float]:
        """Generate parameter variations for sensitivity analysis."""
        if base_value == 0:
            return [-0.5, -0.25, 0.0, 0.25, 0.5]
        else:
            variations = []
            for factor in [0.5, 0.75, 1.0, 1.25, 1.5]:
                variations.append(base_value * factor)
            return variations
    
    def _adjust_parameter(self, field_conditions: FieldConditions, param_name: str, value: float) -> FieldConditions:
        """Adjust a specific parameter in field conditions."""
        adjusted = field_conditions.model_copy() if hasattr(field_conditions, 'model_copy') else field_conditions
        
        if param_name == "field_size_acres":
            adjusted.field_size_acres = value
        elif param_name == "field_size_acres":
            adjusted.field_size_acres = value
        elif param_name == "field_size_acres":
            adjusted.field_size_acres = value
        elif param_name == "slope_percent":
            adjusted.slope_percent = value
        
        return adjusted
    
    def _find_critical_threshold(self, impact_on_ranking: Dict[str, float]) -> Optional[float]:
        """Find critical threshold where recommendation changes."""
        # Simplified implementation
        values = list(impact_on_ranking.values())
        if len(values) > 1:
            return (max(values) + min(values)) / 2
        return None
    
    def _detect_recommendation_change(self, impact_on_ranking: Dict[str, float]) -> bool:
        """Detect if recommendation changes across parameter variations."""
        values = list(impact_on_ranking.values())
        return max(values) - min(values) > 0.2

    # Methods expected by tests
    async def analyze_scenarios(self, request: ApplicationRequest) -> Dict[str, Any]:
        """Analyze different scenarios for fertilizer application."""
        return await self.provide_decision_support(request)
    
    async def generate_decision_tree(self, request: ApplicationRequest) -> Dict[str, Any]:
        """Generate decision tree for fertilizer application."""
        return await self._apply_decision_tree(request)
    
    async def perform_sensitivity_analysis(self, request: ApplicationRequest) -> Dict[str, Any]:
        """Perform sensitivity analysis for fertilizer application."""
        return await self._perform_sensitivity_analysis(request)
