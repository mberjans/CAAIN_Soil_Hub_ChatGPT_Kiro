"""
Agricultural Rule Engine

Centralized rule-based decision system using scikit-learn for agricultural recommendations.
Implements expert-validated agricultural logic with decision trees and rule-based classification.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime, date

# scikit-learn imports
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        SoilTestData,
        LocationData,
        CropData
    )
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        SoilTestData,
        LocationData,
        CropData
    )

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of agricultural rules."""
    CROP_SUITABILITY = "crop_suitability"
    FERTILIZER_RATE = "fertilizer_rate"
    SOIL_MANAGEMENT = "soil_management"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    APPLICATION_TIMING = "application_timing"
    ECONOMIC_OPTIMIZATION = "economic_optimization"


@dataclass
class RuleCondition:
    """Individual rule condition."""
    field: str
    operator: str  # 'eq', 'gt', 'lt', 'gte', 'lte', 'in', 'between'
    value: Union[float, str, List, Tuple]
    weight: float = 1.0


@dataclass
class AgriculturalRule:
    """Agricultural decision rule."""
    rule_id: str
    rule_type: RuleType
    name: str
    description: str
    conditions: List[RuleCondition]
    action: Dict[str, Any]
    confidence: float
    priority: int
    agricultural_source: str
    expert_validated: bool = True
    active: bool = True


@dataclass
class RuleEvaluationResult:
    """Result of rule evaluation."""
    rule_id: str
    matched: bool
    confidence: float
    action: Dict[str, Any]
    explanation: str


class AgriculturalRuleEngine:
    """
    Centralized rule engine for agricultural decision making.
    
    Uses scikit-learn decision trees and expert-validated rules to provide
    consistent, traceable agricultural recommendations.
    """
    
    def __init__(self):
        """Initialize the agricultural rule engine."""
        self.rules: Dict[str, AgriculturalRule] = {}
        self.decision_trees: Dict[str, DecisionTreeClassifier] = {}
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.scalers: Dict[str, StandardScaler] = {}
        
        # Initialize with expert-validated agricultural rules
        self._initialize_agricultural_rules()
        self._build_decision_trees()
    
    def _initialize_agricultural_rules(self):
        """Initialize expert-validated agricultural rules."""
        
        # Crop Suitability Rules
        self._add_crop_suitability_rules()
        
        # Fertilizer Rate Rules
        self._add_fertilizer_rate_rules()
        
        # Soil Management Rules
        self._add_soil_management_rules()
        
        # Nutrient Deficiency Rules
        self._add_nutrient_deficiency_rules()
        
        # Application Timing Rules
        self._add_application_timing_rules()
    
    def _add_crop_suitability_rules(self):
        """Add crop suitability rules based on extension guidelines."""
        
        # Corn suitability rules
        corn_optimal_rule = AgriculturalRule(
            rule_id="corn_optimal_conditions",
            rule_type=RuleType.CROP_SUITABILITY,
            name="Corn Optimal Growing Conditions",
            description="Corn thrives in well-drained soils with pH 6.0-6.8 and adequate fertility",
            conditions=[
                RuleCondition("soil_ph", "between", (6.0, 6.8), weight=0.3),
                RuleCondition("drainage_class", "eq", "well_drained", weight=0.2),
                RuleCondition("organic_matter_percent", "gte", 3.0, weight=0.2),
                RuleCondition("phosphorus_ppm", "gte", 20, weight=0.15),
                RuleCondition("potassium_ppm", "gte", 150, weight=0.15)
            ],
            action={
                "crop": "corn",
                "suitability_score": 0.95,
                "recommendation": "highly_suitable",
                "expected_yield_range": (160, 200)
            },
            confidence=0.95,
            priority=1,
            agricultural_source="Iowa State University Extension PM 1688",
            expert_validated=True
        )
        self.rules[corn_optimal_rule.rule_id] = corn_optimal_rule
        
        # Corn marginal conditions
        corn_marginal_rule = AgriculturalRule(
            rule_id="corn_marginal_conditions",
            rule_type=RuleType.CROP_SUITABILITY,
            name="Corn Marginal Growing Conditions",
            description="Corn can grow but may have reduced yields in suboptimal conditions",
            conditions=[
                RuleCondition("soil_ph", "between", (5.5, 5.9), weight=0.4),
                RuleCondition("organic_matter_percent", "between", (2.0, 2.9), weight=0.3),
                RuleCondition("phosphorus_ppm", "between", (10, 19), weight=0.3)
            ],
            action={
                "crop": "corn",
                "suitability_score": 0.65,
                "recommendation": "marginal_suitable",
                "expected_yield_range": (120, 160),
                "required_amendments": ["lime_application", "phosphorus_buildup"]
            },
            confidence=0.80,
            priority=2,
            agricultural_source="University Extension Soil Management Guidelines"
        )
        self.rules[corn_marginal_rule.rule_id] = corn_marginal_rule
        
        # Soybean suitability rules
        soybean_optimal_rule = AgriculturalRule(
            rule_id="soybean_optimal_conditions",
            rule_type=RuleType.CROP_SUITABILITY,
            name="Soybean Optimal Growing Conditions",
            description="Soybeans prefer well-drained soils with pH 6.0-7.0",
            conditions=[
                RuleCondition("soil_ph", "between", (6.0, 7.0), weight=0.35),
                RuleCondition("drainage_class", "eq", "well_drained", weight=0.25),
                RuleCondition("organic_matter_percent", "gte", 2.5, weight=0.2),
                RuleCondition("potassium_ppm", "gte", 140, weight=0.2)
            ],
            action={
                "crop": "soybean",
                "suitability_score": 0.90,
                "recommendation": "highly_suitable",
                "expected_yield_range": (50, 70),
                "nitrogen_fixation_potential": 60
            },
            confidence=0.92,
            priority=1,
            agricultural_source="Soybean Production Guidelines"
        )
        self.rules[soybean_optimal_rule.rule_id] = soybean_optimal_rule
    
    def _add_fertilizer_rate_rules(self):
        """Add fertilizer rate calculation rules."""
        
        # Nitrogen rate for corn
        corn_nitrogen_rule = AgriculturalRule(
            rule_id="corn_nitrogen_calculation",
            rule_type=RuleType.FERTILIZER_RATE,
            name="Corn Nitrogen Rate Calculation",
            description="Calculate nitrogen rate based on yield goal and soil conditions",
            conditions=[
                RuleCondition("crop_name", "eq", "corn", weight=1.0),
                RuleCondition("yield_goal", "gte", 100, weight=0.3),
                RuleCondition("soil_ph", "gte", 5.5, weight=0.2)
            ],
            action={
                "calculation_method": "yield_based",
                "base_rate_formula": "yield_goal * 1.2",  # 1.2 lbs N per bushel
                "legume_credit": 40,  # lbs N/acre from previous soybean
                "soil_test_credit_factor": 2.0,  # 2 lbs N per ppm nitrate
                "maximum_rate": 200,  # lbs N/acre
                "split_application": True
            },
            confidence=0.90,
            priority=1,
            agricultural_source="Iowa State University N Rate Calculator"
        )
        self.rules[corn_nitrogen_rule.rule_id] = corn_nitrogen_rule
        
        # Phosphorus buildup rule
        phosphorus_buildup_rule = AgriculturalRule(
            rule_id="phosphorus_buildup_strategy",
            rule_type=RuleType.FERTILIZER_RATE,
            name="Phosphorus Buildup Strategy",
            description="Buildup phosphorus application for low soil test levels",
            conditions=[
                RuleCondition("phosphorus_ppm", "lt", 15, weight=0.6),
                RuleCondition("soil_ph", "gte", 5.8, weight=0.4)
            ],
            action={
                "strategy": "buildup",
                "rate_multiplier": 1.5,
                "minimum_rate": 40,  # lbs P2O5/acre
                "application_timing": "fall_preferred",
                "retest_interval": 2  # years
            },
            confidence=0.88,
            priority=1,
            agricultural_source="Phosphorus Management Guidelines"
        )
        self.rules[phosphorus_buildup_rule.rule_id] = phosphorus_buildup_rule
    
    def _add_soil_management_rules(self):
        """Add soil management rules."""
        
        # Lime requirement rule
        lime_requirement_rule = AgriculturalRule(
            rule_id="lime_requirement_calculation",
            rule_type=RuleType.SOIL_MANAGEMENT,
            name="Lime Requirement for pH Adjustment",
            description="Calculate lime requirement based on current and target pH",
            conditions=[
                RuleCondition("soil_ph", "lt", 6.0, weight=0.7),
                RuleCondition("cec_meq_per_100g", "gte", 10, weight=0.3)
            ],
            action={
                "amendment": "agricultural_limestone",
                "calculation_method": "buffer_ph",
                "target_ph": 6.5,
                "rate_formula": "(target_ph - current_ph) * cec * 0.5",
                "application_timing": "fall_preferred",
                "incorporation_required": True
            },
            confidence=0.85,
            priority=1,
            agricultural_source="Soil pH Management Guidelines"
        )
        self.rules[lime_requirement_rule.rule_id] = lime_requirement_rule
        
        # Organic matter improvement rule
        organic_matter_rule = AgriculturalRule(
            rule_id="organic_matter_improvement",
            rule_type=RuleType.SOIL_MANAGEMENT,
            name="Organic Matter Improvement Strategy",
            description="Improve soil organic matter through cover crops and organic amendments",
            conditions=[
                RuleCondition("organic_matter_percent", "lt", 3.0, weight=0.8),
                RuleCondition("soil_texture", "in", ["silt_loam", "clay_loam"], weight=0.2)
            ],
            action={
                "strategy": "multi_year_improvement",
                "cover_crops": ["crimson_clover", "winter_rye"],
                "organic_amendments": ["compost", "aged_manure"],
                "target_increase": 0.1,  # % per year
                "timeline_years": 3
            },
            confidence=0.82,
            priority=2,
            agricultural_source="Soil Health Management Practices"
        )
        self.rules[organic_matter_rule.rule_id] = organic_matter_rule
    
    def _add_nutrient_deficiency_rules(self):
        """Add nutrient deficiency detection rules."""
        
        # Nitrogen deficiency rule
        nitrogen_deficiency_rule = AgriculturalRule(
            rule_id="nitrogen_deficiency_detection",
            rule_type=RuleType.NUTRIENT_DEFICIENCY,
            name="Nitrogen Deficiency Indicators",
            description="Detect nitrogen deficiency based on soil test and visual symptoms",
            conditions=[
                RuleCondition("nitrogen_ppm", "lt", 10, weight=0.6),
                RuleCondition("organic_matter_percent", "lt", 2.5, weight=0.4)
            ],
            action={
                "deficiency": "nitrogen",
                "severity": "moderate_to_severe",
                "immediate_action": "side_dress_application",
                "rate_lbs_per_acre": 30,
                "long_term_strategy": "improve_organic_matter"
            },
            confidence=0.87,
            priority=1,
            agricultural_source="Nutrient Deficiency Diagnosis Guide"
        )
        self.rules[nitrogen_deficiency_rule.rule_id] = nitrogen_deficiency_rule
        
        # Potassium deficiency rule
        potassium_deficiency_rule = AgriculturalRule(
            rule_id="potassium_deficiency_detection",
            rule_type=RuleType.NUTRIENT_DEFICIENCY,
            name="Potassium Deficiency Indicators",
            description="Detect potassium deficiency and recommend correction",
            conditions=[
                RuleCondition("potassium_ppm", "lt", 120, weight=0.7),
                RuleCondition("crop_name", "in", ["corn", "soybean"], weight=0.3)
            ],
            action={
                "deficiency": "potassium",
                "severity": "moderate",
                "correction_rate": 60,  # lbs K2O/acre
                "application_timing": "fall_or_spring",
                "monitoring": "annual_soil_test"
            },
            confidence=0.83,
            priority=2,
            agricultural_source="Potassium Management Guidelines"
        )
        self.rules[potassium_deficiency_rule.rule_id] = potassium_deficiency_rule
    
    def _add_application_timing_rules(self):
        """Add fertilizer application timing rules."""
        
        # Fall nitrogen application rule
        fall_nitrogen_rule = AgriculturalRule(
            rule_id="fall_nitrogen_application",
            rule_type=RuleType.APPLICATION_TIMING,
            name="Fall Nitrogen Application Guidelines",
            description="Conditions for safe fall nitrogen application",
            conditions=[
                RuleCondition("soil_temperature", "lt", 50, weight=0.4),
                RuleCondition("latitude", "gt", 40, weight=0.3),
                RuleCondition("drainage_class", "eq", "well_drained", weight=0.3)
            ],
            action={
                "timing": "fall_application",
                "inhibitor_required": True,
                "maximum_rate_percent": 50,
                "soil_temp_threshold": 50,  # Fahrenheit
                "application_window": "november_december"
            },
            confidence=0.80,
            priority=2,
            agricultural_source="Fall Fertilizer Application Guidelines"
        )
        self.rules[fall_nitrogen_rule.rule_id] = fall_nitrogen_rule
    
    def _build_decision_trees(self):
        """Build scikit-learn decision trees for complex agricultural decisions."""
        
        # Build crop suitability decision tree
        self._build_crop_suitability_tree()
        
        # Build fertilizer rate decision tree
        self._build_fertilizer_rate_tree()
        
        # Build soil management decision tree
        self._build_soil_management_tree()
    
    def _build_crop_suitability_tree(self):
        """Build decision tree for crop suitability assessment."""
        
        # Create synthetic training data based on agricultural knowledge
        training_data = self._generate_crop_suitability_training_data()
        
        if len(training_data) == 0:
            logger.warning("No training data available for crop suitability tree")
            return
        
        df = pd.DataFrame(training_data)
        
        # Prepare features
        feature_columns = ['ph', 'organic_matter', 'phosphorus', 'potassium', 'drainage_score']
        X = df[feature_columns]
        y = df['suitability_class']
        
        # Encode categorical target
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        self.label_encoders['crop_suitability'] = le
        
        # Train decision tree
        dt = DecisionTreeClassifier(
            max_depth=8,
            min_samples_split=10,
            min_samples_leaf=5,
            random_state=42
        )
        dt.fit(X, y_encoded)
        
        self.decision_trees['crop_suitability'] = dt
        
        logger.info("Crop suitability decision tree trained successfully")
    
    def _build_fertilizer_rate_tree(self):
        """Build decision tree for fertilizer rate recommendations."""
        
        # Create training data for fertilizer rates
        training_data = self._generate_fertilizer_rate_training_data()
        
        if len(training_data) == 0:
            logger.warning("No training data available for fertilizer rate tree")
            return
        
        df = pd.DataFrame(training_data)
        
        # Prepare features for nitrogen rate prediction
        feature_columns = ['yield_goal', 'soil_n', 'organic_matter', 'previous_legume', 'ph']
        X = df[feature_columns]
        y = df['nitrogen_rate']
        
        # Train regression tree for nitrogen rates
        dt_regressor = DecisionTreeRegressor(
            max_depth=6,
            min_samples_split=8,
            min_samples_leaf=4,
            random_state=42
        )
        dt_regressor.fit(X, y)
        
        self.decision_trees['nitrogen_rate'] = dt_regressor
        
        logger.info("Fertilizer rate decision tree trained successfully")
    
    def _build_soil_management_tree(self):
        """Build decision tree for soil management recommendations."""
        
        # Create training data for soil management
        training_data = self._generate_soil_management_training_data()
        
        if len(training_data) == 0:
            logger.warning("No training data available for soil management tree")
            return
        
        df = pd.DataFrame(training_data)
        
        # Prepare features
        feature_columns = ['ph', 'organic_matter', 'phosphorus', 'potassium', 'cec']
        X = df[feature_columns]
        y = df['management_priority']
        
        # Encode categorical target
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        self.label_encoders['soil_management'] = le
        
        # Train decision tree
        dt = DecisionTreeClassifier(
            max_depth=7,
            min_samples_split=8,
            min_samples_leaf=4,
            random_state=42
        )
        dt.fit(X, y_encoded)
        
        self.decision_trees['soil_management'] = dt
        
        logger.info("Soil management decision tree trained successfully")
    
    def _generate_crop_suitability_training_data(self) -> List[Dict]:
        """Generate synthetic training data for crop suitability based on agricultural knowledge."""
        
        training_data = []
        
        # Generate data points covering the agricultural parameter space
        ph_values = np.arange(4.5, 8.5, 0.2)
        om_values = np.arange(1.0, 6.0, 0.3)
        p_values = np.arange(5, 80, 5)
        k_values = np.arange(80, 400, 20)
        
        for ph in ph_values:
            for om in om_values[:10]:  # Limit combinations
                for p in p_values[:8]:
                    for k in k_values[:6]:
                        # Determine suitability class based on agricultural knowledge
                        suitability = self._classify_crop_suitability(ph, om, p, k)
                        
                        training_data.append({
                            'ph': ph,
                            'organic_matter': om,
                            'phosphorus': p,
                            'potassium': k,
                            'drainage_score': 1.0,  # Assume well-drained
                            'suitability_class': suitability
                        })
        
        return training_data
    
    def _classify_crop_suitability(self, ph: float, om: float, p: float, k: float) -> str:
        """Classify crop suitability based on soil parameters."""
        
        # Scoring system based on agricultural guidelines
        score = 0
        
        # pH scoring (optimal 6.0-6.8 for corn)
        if 6.0 <= ph <= 6.8:
            score += 30
        elif 5.8 <= ph <= 7.2:
            score += 20
        elif 5.5 <= ph <= 8.0:
            score += 10
        
        # Organic matter scoring
        if om >= 3.5:
            score += 25
        elif om >= 2.5:
            score += 15
        elif om >= 2.0:
            score += 8
        
        # Phosphorus scoring
        if p >= 30:
            score += 25
        elif p >= 20:
            score += 18
        elif p >= 15:
            score += 10
        elif p >= 10:
            score += 5
        
        # Potassium scoring
        if k >= 200:
            score += 20
        elif k >= 150:
            score += 15
        elif k >= 120:
            score += 10
        elif k >= 100:
            score += 5
        
        # Classify based on total score
        if score >= 80:
            return "highly_suitable"
        elif score >= 60:
            return "suitable"
        elif score >= 40:
            return "marginal"
        else:
            return "unsuitable"
    
    def _generate_fertilizer_rate_training_data(self) -> List[Dict]:
        """Generate training data for fertilizer rate calculations."""
        
        training_data = []
        
        # Generate data based on university extension guidelines
        yield_goals = range(100, 220, 10)  # bu/acre
        soil_n_levels = range(5, 40, 3)    # ppm
        om_levels = np.arange(1.5, 5.5, 0.3)
        
        for yield_goal in yield_goals:
            for soil_n in soil_n_levels:
                for om in om_levels[:8]:  # Limit combinations
                    # Calculate N rate based on ISU guidelines
                    base_n = yield_goal * 1.2  # 1.2 lbs N per bushel
                    soil_credit = soil_n * 2   # 2 lbs N per ppm
                    legume_credit = 40 if np.random.random() > 0.5 else 0
                    
                    final_n_rate = max(0, base_n - soil_credit - legume_credit)
                    final_n_rate = min(final_n_rate, 200)  # Cap at 200 lbs/acre
                    
                    training_data.append({
                        'yield_goal': yield_goal,
                        'soil_n': soil_n,
                        'organic_matter': om,
                        'previous_legume': 1 if legume_credit > 0 else 0,
                        'ph': 6.2,  # Assume adequate pH
                        'nitrogen_rate': final_n_rate
                    })
        
        return training_data
    
    def _generate_soil_management_training_data(self) -> List[Dict]:
        """Generate training data for soil management priorities."""
        
        training_data = []
        
        # Generate data covering soil management scenarios
        ph_values = np.arange(4.5, 8.5, 0.3)
        om_values = np.arange(1.0, 6.0, 0.4)
        p_values = np.arange(5, 80, 8)
        k_values = np.arange(80, 400, 30)
        cec_values = np.arange(8, 35, 3)
        
        for ph in ph_values:
            for om in om_values[:8]:
                for p in p_values[:6]:
                    for k in k_values[:5]:
                        for cec in cec_values[:4]:
                            priority = self._determine_management_priority(ph, om, p, k, cec)
                            
                            training_data.append({
                                'ph': ph,
                                'organic_matter': om,
                                'phosphorus': p,
                                'potassium': k,
                                'cec': cec,
                                'management_priority': priority
                            })
        
        return training_data
    
    def _determine_management_priority(self, ph: float, om: float, p: float, k: float, cec: float) -> str:
        """Determine soil management priority based on soil conditions."""
        
        # Priority scoring system
        issues = []
        
        if ph < 5.8:
            issues.append(('lime_application', 3))
        elif ph > 7.5:
            issues.append(('sulfur_application', 2))
        
        if om < 2.5:
            issues.append(('organic_matter_improvement', 2))
        
        if p < 15:
            issues.append(('phosphorus_buildup', 2))
        elif p > 50:
            issues.append(('phosphorus_maintenance', 1))
        
        if k < 120:
            issues.append(('potassium_buildup', 2))
        elif k > 300:
            issues.append(('potassium_maintenance', 1))
        
        if not issues:
            return "maintenance"
        
        # Return highest priority issue
        issues.sort(key=lambda x: x[1], reverse=True)
        return issues[0][0]
    
    def evaluate_rules(self, request: RecommendationRequest, rule_type: RuleType = None) -> List[RuleEvaluationResult]:
        """
        Evaluate agricultural rules against farm data.
        
        Args:
            request: Farm data and recommendation request
            rule_type: Optional filter for specific rule types
            
        Returns:
            List of rule evaluation results
        """
        results = []
        
        # Filter rules by type if specified
        rules_to_evaluate = self.rules.values()
        if rule_type:
            rules_to_evaluate = [r for r in rules_to_evaluate if r.rule_type == rule_type]
        
        for rule in rules_to_evaluate:
            if not rule.active:
                continue
            
            result = self._evaluate_single_rule(rule, request)
            if result.matched:
                results.append(result)
        
        # Sort by confidence and priority
        results.sort(key=lambda x: (x.confidence, -self.rules[x.rule_id].priority), reverse=True)
        
        return results
    
    def _evaluate_single_rule(self, rule: AgriculturalRule, request: RecommendationRequest) -> RuleEvaluationResult:
        """Evaluate a single rule against request data."""
        
        matched_conditions = 0
        total_weight = 0
        explanation_parts = []
        
        for condition in rule.conditions:
            value = self._extract_field_value(condition.field, request)
            condition_met = self._evaluate_condition(condition, value)
            
            total_weight += condition.weight
            if condition_met:
                matched_conditions += condition.weight
                explanation_parts.append(f"{condition.field} meets criteria")
            else:
                explanation_parts.append(f"{condition.field} does not meet criteria")
        
        # Calculate match percentage
        match_percentage = matched_conditions / total_weight if total_weight > 0 else 0
        
        # Rule matches if >= 70% of weighted conditions are met
        matched = match_percentage >= 0.7
        
        # Adjust confidence based on match percentage
        adjusted_confidence = rule.confidence * match_percentage if matched else 0
        
        explanation = f"Rule '{rule.name}': {'; '.join(explanation_parts)}"
        
        return RuleEvaluationResult(
            rule_id=rule.rule_id,
            matched=matched,
            confidence=adjusted_confidence,
            action=rule.action if matched else {},
            explanation=explanation
        )
    
    def _extract_field_value(self, field: str, request: RecommendationRequest) -> Any:
        """Extract field value from request data."""
        
        # Map field names to request data
        field_mapping = {
            'soil_ph': lambda r: r.soil_data.ph if r.soil_data else None,
            'organic_matter_percent': lambda r: r.soil_data.organic_matter_percent if r.soil_data else None,
            'phosphorus_ppm': lambda r: r.soil_data.phosphorus_ppm if r.soil_data else None,
            'potassium_ppm': lambda r: r.soil_data.potassium_ppm if r.soil_data else None,
            'nitrogen_ppm': lambda r: r.soil_data.nitrogen_ppm if r.soil_data else None,
            'cec_meq_per_100g': lambda r: r.soil_data.cec_meq_per_100g if r.soil_data else None,
            'drainage_class': lambda r: r.soil_data.drainage_class if r.soil_data else None,
            'soil_texture': lambda r: r.soil_data.soil_texture if r.soil_data else None,
            'crop_name': lambda r: r.crop_data.crop_name if r.crop_data else None,
            'yield_goal': lambda r: r.crop_data.yield_goal if r.crop_data else None,
            'previous_crop': lambda r: r.crop_data.previous_crop if r.crop_data else None,
            'latitude': lambda r: r.location.latitude if r.location else None,
            'longitude': lambda r: r.location.longitude if r.location else None,
            'farm_size_acres': lambda r: r.farm_profile.farm_size_acres if r.farm_profile else None
        }
        
        if field in field_mapping:
            return field_mapping[field](request)
        
        return None
    
    def _evaluate_condition(self, condition: RuleCondition, value: Any) -> bool:
        """Evaluate a single condition."""
        
        if value is None:
            return False
        
        try:
            if condition.operator == 'eq':
                return value == condition.value
            elif condition.operator == 'gt':
                return float(value) > float(condition.value)
            elif condition.operator == 'lt':
                return float(value) < float(condition.value)
            elif condition.operator == 'gte':
                return float(value) >= float(condition.value)
            elif condition.operator == 'lte':
                return float(value) <= float(condition.value)
            elif condition.operator == 'in':
                return value in condition.value
            elif condition.operator == 'between':
                min_val, max_val = condition.value
                return min_val <= float(value) <= max_val
            else:
                logger.warning(f"Unknown operator: {condition.operator}")
                return False
        except (ValueError, TypeError) as e:
            logger.warning(f"Error evaluating condition: {e}")
            return False
    
    def predict_with_decision_tree(self, tree_name: str, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Make predictions using trained decision trees.
        
        Args:
            tree_name: Name of the decision tree to use
            features: Feature values for prediction
            
        Returns:
            Prediction results with confidence
        """
        if tree_name not in self.decision_trees:
            raise ValueError(f"Decision tree '{tree_name}' not found")
        
        tree = self.decision_trees[tree_name]
        
        try:
            if tree_name == 'crop_suitability':
                return self._predict_crop_suitability(features)
            elif tree_name == 'nitrogen_rate':
                return self._predict_nitrogen_rate(features)
            elif tree_name == 'soil_management':
                return self._predict_soil_management(features)
            else:
                raise ValueError(f"Unknown tree type: {tree_name}")
        
        except Exception as e:
            logger.error(f"Error making prediction with {tree_name}: {e}")
            return {"error": str(e)}
    
    def _predict_crop_suitability(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict crop suitability using decision tree."""
        
        tree = self.decision_trees['crop_suitability']
        le = self.label_encoders['crop_suitability']
        
        # Prepare feature vector
        feature_order = ['ph', 'organic_matter', 'phosphorus', 'potassium', 'drainage_score']
        X = np.array([[features.get(f, 0) for f in feature_order]])
        
        # Make prediction
        prediction = tree.predict(X)[0]
        probabilities = tree.predict_proba(X)[0]
        
        # Decode prediction
        suitability_class = le.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        
        return {
            'suitability_class': suitability_class,
            'confidence': confidence,
            'probabilities': dict(zip(le.classes_, probabilities))
        }
    
    def _predict_nitrogen_rate(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict nitrogen rate using decision tree regressor."""
        
        tree = self.decision_trees['nitrogen_rate']
        
        # Prepare feature vector
        feature_order = ['yield_goal', 'soil_n', 'organic_matter', 'previous_legume', 'ph']
        X = np.array([[features.get(f, 0) for f in feature_order]])
        
        # Make prediction
        predicted_rate = tree.predict(X)[0]
        
        # Calculate confidence based on tree structure (simplified)
        confidence = 0.85  # Would be calculated from tree variance in production
        
        return {
            'nitrogen_rate': max(0, predicted_rate),
            'confidence': confidence,
            'method': 'decision_tree_regression'
        }
    
    def _predict_soil_management(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Predict soil management priority using decision tree."""
        
        tree = self.decision_trees['soil_management']
        le = self.label_encoders['soil_management']
        
        # Prepare feature vector
        feature_order = ['ph', 'organic_matter', 'phosphorus', 'potassium', 'cec']
        X = np.array([[features.get(f, 0) for f in feature_order]])
        
        # Make prediction
        prediction = tree.predict(X)[0]
        probabilities = tree.predict_proba(X)[0]
        
        # Decode prediction
        management_priority = le.inverse_transform([prediction])[0]
        confidence = max(probabilities)
        
        return {
            'management_priority': management_priority,
            'confidence': confidence,
            'probabilities': dict(zip(le.classes_, probabilities))
        }
    
    def add_rule(self, rule: AgriculturalRule) -> bool:
        """
        Add a new agricultural rule to the engine.
        
        Args:
            rule: Agricultural rule to add
            
        Returns:
            True if rule was added successfully
        """
        if rule.rule_id in self.rules:
            logger.warning(f"Rule {rule.rule_id} already exists")
            return False
        
        self.rules[rule.rule_id] = rule
        logger.info(f"Added rule: {rule.rule_id}")
        return True
    
    def update_rule(self, rule_id: str, updated_rule: AgriculturalRule) -> bool:
        """
        Update an existing rule.
        
        Args:
            rule_id: ID of rule to update
            updated_rule: Updated rule data
            
        Returns:
            True if rule was updated successfully
        """
        if rule_id not in self.rules:
            logger.warning(f"Rule {rule_id} not found")
            return False
        
        self.rules[rule_id] = updated_rule
        logger.info(f"Updated rule: {rule_id}")
        return True
    
    def deactivate_rule(self, rule_id: str) -> bool:
        """
        Deactivate a rule without removing it.
        
        Args:
            rule_id: ID of rule to deactivate
            
        Returns:
            True if rule was deactivated successfully
        """
        if rule_id not in self.rules:
            logger.warning(f"Rule {rule_id} not found")
            return False
        
        self.rules[rule_id].active = False
        logger.info(f"Deactivated rule: {rule_id}")
        return True
    
    def get_rule_statistics(self) -> Dict[str, Any]:
        """Get statistics about the rule engine."""
        
        total_rules = len(self.rules)
        active_rules = sum(1 for rule in self.rules.values() if rule.active)
        expert_validated = sum(1 for rule in self.rules.values() if rule.expert_validated)
        
        rule_types = {}
        for rule in self.rules.values():
            rule_type = rule.rule_type.value
            rule_types[rule_type] = rule_types.get(rule_type, 0) + 1
        
        return {
            'total_rules': total_rules,
            'active_rules': active_rules,
            'expert_validated_rules': expert_validated,
            'rule_types': rule_types,
            'decision_trees': list(self.decision_trees.keys()),
            'validation_percentage': (expert_validated / total_rules * 100) if total_rules > 0 else 0
        }