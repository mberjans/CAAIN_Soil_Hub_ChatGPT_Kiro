"""
Comprehensive Application Method Comparison Service for fertilizer application methods.

This service provides detailed comparison between different fertilizer application methods
across multiple criteria including cost, efficiency, environmental impact, labor requirements,
equipment needs, and field suitability.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum

from src.models.application_models import (
    ApplicationMethod, ApplicationMethodType, FieldConditions, 
    CropRequirements, FertilizerSpecification, EquipmentSpecification
)
from src.models.method_models import MethodComparison, ApplicationMethod as MethodModel
from src.services.application_method_service import ApplicationMethodService
from src.services.cost_analysis_service import CostAnalysisService

logger = logging.getLogger(__name__)


class ComparisonCriteria(str, Enum):
    """Available comparison criteria for application methods."""
    COST_EFFECTIVENESS = "cost_effectiveness"
    APPLICATION_EFFICIENCY = "application_efficiency"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    LABOR_REQUIREMENTS = "labor_requirements"
    EQUIPMENT_NEEDS = "equipment_needs"
    FIELD_SUITABILITY = "field_suitability"
    NUTRIENT_USE_EFFICIENCY = "nutrient_use_efficiency"
    TIMING_FLEXIBILITY = "timing_flexibility"
    SKILL_REQUIREMENTS = "skill_requirements"
    WEATHER_DEPENDENCY = "weather_dependency"


@dataclass
class ComparisonResult:
    """Result of method comparison analysis."""
    method_a_score: float
    method_b_score: float
    winner: str
    score_difference: float
    confidence_level: float
    analysis_notes: List[str]


@dataclass
class MultiCriteriaAnalysis:
    """Multi-criteria analysis result."""
    criteria_scores: Dict[str, ComparisonResult]
    weighted_scores: Dict[str, float]
    overall_winner: str
    sensitivity_analysis: Dict[str, Any]
    recommendation_strength: float


class MethodComparisonService:
    """Comprehensive service for comparing fertilizer application methods."""
    
    def __init__(self):
        self.application_service = ApplicationMethodService()
        self.cost_service = CostAnalysisService()
        self._initialize_criteria_weights()
        self._initialize_comparison_matrices()
    
    def _initialize_criteria_weights(self):
        """Initialize default weights for comparison criteria."""
        self.default_weights = {
            ComparisonCriteria.COST_EFFECTIVENESS: 0.20,
            ComparisonCriteria.APPLICATION_EFFICIENCY: 0.25,
            ComparisonCriteria.ENVIRONMENTAL_IMPACT: 0.15,
            ComparisonCriteria.LABOR_REQUIREMENTS: 0.10,
            ComparisonCriteria.EQUIPMENT_NEEDS: 0.10,
            ComparisonCriteria.FIELD_SUITABILITY: 0.10,
            ComparisonCriteria.NUTRIENT_USE_EFFICIENCY: 0.05,
            ComparisonCriteria.TIMING_FLEXIBILITY: 0.02,
            ComparisonCriteria.SKILL_REQUIREMENTS: 0.02,
            ComparisonCriteria.WEATHER_DEPENDENCY: 0.01
        }
    
    def _initialize_comparison_matrices(self):
        """Initialize comparison matrices for different criteria."""
        # Environmental impact scoring (lower is better)
        self.environmental_scores = {
            "very_low": 1.0,
            "low": 0.8,
            "moderate": 0.6,
            "high": 0.4,
            "very_high": 0.2
        }
        
        # Labor intensity scoring (lower is better)
        self.labor_scores = {
            "very_low": 1.0,
            "low": 0.8,
            "medium": 0.6,
            "high": 0.4,
            "very_high": 0.2
        }
        
        # Skill requirements scoring (lower is better)
        self.skill_scores = {
            "unskilled": 1.0,
            "semi_skilled": 0.8,
            "skilled": 0.6,
            "highly_skilled": 0.4,
            "expert": 0.2
        }
        
        # Weather dependency scoring (lower is better)
        self.weather_scores = {
            "independent": 1.0,
            "low": 0.8,
            "moderate": 0.6,
            "high": 0.4,
            "very_high": 0.2
        }
    
    async def compare_methods(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_spec: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        comparison_criteria: Optional[List[str]] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> MethodComparison:
        """
        Perform comprehensive comparison between two application methods.
        
        Args:
            method_a: First application method to compare
            method_b: Second application method to compare
            field_conditions: Field conditions for context
            crop_requirements: Crop requirements for context
            fertilizer_spec: Fertilizer specification for context
            available_equipment: Available equipment for context
            comparison_criteria: Specific criteria to compare (if None, uses all)
            custom_weights: Custom weights for criteria (if None, uses defaults)
            
        Returns:
            MethodComparison with detailed analysis
        """
        start_time = time.time()
        comparison_id = str(uuid4())
        
        try:
            logger.info(f"Starting comprehensive method comparison {comparison_id}")
            
            # Determine criteria to use
            criteria_to_use = comparison_criteria or list(self.default_weights.keys())
            weights = custom_weights or self.default_weights
            
            # Perform multi-criteria analysis
            analysis = await self._perform_multi_criteria_analysis(
                method_a, method_b, field_conditions, crop_requirements,
                fertilizer_spec, available_equipment, criteria_to_use, weights
            )
            
            # Generate detailed comparison
            comparison = await self._generate_comparison_result(
                method_a, method_b, analysis, comparison_id, start_time
            )
            
            logger.info(f"Method comparison completed in {(time.time() - start_time) * 1000:.2f}ms")
            return comparison
            
        except Exception as e:
            logger.error(f"Error in method comparison: {e}")
            raise
    
    async def _perform_multi_criteria_analysis(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_spec: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        criteria: List[str],
        weights: Dict[str, float]
    ) -> MultiCriteriaAnalysis:
        """Perform multi-criteria analysis for method comparison."""
        
        criteria_scores = {}
        weighted_scores = {}
        
        for criterion in criteria:
            # Calculate scores for each criterion
            comparison_result = await self._compare_criterion(
                criterion, method_a, method_b, field_conditions,
                crop_requirements, fertilizer_spec, available_equipment
            )
            
            criteria_scores[criterion] = comparison_result
            
            # Calculate weighted scores
            weight = weights.get(criterion, 0.0)
            weighted_scores[method_a.method_type] = weighted_scores.get(method_a.method_type, 0.0) + comparison_result.method_a_score * weight
            weighted_scores[method_b.method_type] = weighted_scores.get(method_b.method_type, 0.0) + comparison_result.method_b_score * weight
        
        # Determine overall winner
        overall_winner = max(weighted_scores.items(), key=lambda x: x[1])[0]
        
        # Perform sensitivity analysis
        sensitivity_analysis = await self._perform_sensitivity_analysis(
            criteria_scores, weights, method_a.method_type, method_b.method_type
        )
        
        # Calculate recommendation strength
        recommendation_strength = abs(weighted_scores[method_a.method_type] - weighted_scores[method_b.method_type])
        
        return MultiCriteriaAnalysis(
            criteria_scores=criteria_scores,
            weighted_scores=weighted_scores,
            overall_winner=overall_winner,
            sensitivity_analysis=sensitivity_analysis,
            recommendation_strength=recommendation_strength
        )
    
    async def _compare_criterion(
        self,
        criterion: str,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_spec: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> ComparisonResult:
        """Compare methods on a specific criterion."""
        
        if criterion == ComparisonCriteria.COST_EFFECTIVENESS:
            return await self._compare_cost_effectiveness(method_a, method_b, field_conditions)
        elif criterion == ComparisonCriteria.APPLICATION_EFFICIENCY:
            return await self._compare_application_efficiency(method_a, method_b)
        elif criterion == ComparisonCriteria.ENVIRONMENTAL_IMPACT:
            return await self._compare_environmental_impact(method_a, method_b, field_conditions)
        elif criterion == ComparisonCriteria.LABOR_REQUIREMENTS:
            return await self._compare_labor_requirements(method_a, method_b)
        elif criterion == ComparisonCriteria.EQUIPMENT_NEEDS:
            return await self._compare_equipment_needs(method_a, method_b, available_equipment)
        elif criterion == ComparisonCriteria.FIELD_SUITABILITY:
            return await self._compare_field_suitability(method_a, method_b, field_conditions)
        elif criterion == ComparisonCriteria.NUTRIENT_USE_EFFICIENCY:
            return await self._compare_nutrient_use_efficiency(method_a, method_b, crop_requirements)
        elif criterion == ComparisonCriteria.TIMING_FLEXIBILITY:
            return await self._compare_timing_flexibility(method_a, method_b, crop_requirements)
        elif criterion == ComparisonCriteria.SKILL_REQUIREMENTS:
            return await self._compare_skill_requirements(method_a, method_b)
        elif criterion == ComparisonCriteria.WEATHER_DEPENDENCY:
            return await self._compare_weather_dependency(method_a, method_b)
        else:
            raise ValueError(f"Unknown comparison criterion: {criterion}")
    
    async def _compare_cost_effectiveness(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        field_conditions: FieldConditions
    ) -> ComparisonResult:
        """Compare cost effectiveness of methods."""
        
        # Calculate total cost per acre including equipment, labor, and fertilizer
        cost_a = await self._calculate_total_cost(method_a, field_conditions)
        cost_b = await self._calculate_total_cost(method_b, field_conditions)
        
        # Lower cost is better (invert scores)
        score_a = max(0, 1.0 - (cost_a / 100))  # Normalize to 0-1 scale
        score_b = max(0, 1.0 - (cost_b / 100))
        
        winner = "method_a" if cost_a < cost_b else "method_b"
        score_difference = abs(score_a - score_b)
        confidence_level = min(0.95, 0.7 + score_difference * 2)
        
        analysis_notes = [
            f"Method A total cost: ${cost_a:.2f}/acre",
            f"Method B total cost: ${cost_b:.2f}/acre",
            f"Cost difference: ${abs(cost_a - cost_b):.2f}/acre"
        ]
        
        return ComparisonResult(
            method_a_score=score_a,
            method_b_score=score_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_application_efficiency(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod
    ) -> ComparisonResult:
        """Compare application efficiency of methods."""
        
        efficiency_a = method_a.efficiency_score
        efficiency_b = method_b.efficiency_score
        
        winner = "method_a" if efficiency_a > efficiency_b else "method_b"
        score_difference = abs(efficiency_a - efficiency_b)
        confidence_level = min(0.95, 0.8 + score_difference * 2)
        
        analysis_notes = [
            f"Method A efficiency: {efficiency_a:.2f}",
            f"Method B efficiency: {efficiency_b:.2f}",
            f"Efficiency difference: {score_difference:.2f}"
        ]
        
        return ComparisonResult(
            method_a_score=efficiency_a,
            method_b_score=efficiency_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_environmental_impact(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        field_conditions: FieldConditions
    ) -> ComparisonResult:
        """Compare environmental impact of methods."""
        
        # Get environmental impact scores
        impact_a = self.environmental_scores.get(method_a.environmental_impact, 0.6)
        impact_b = self.environmental_scores.get(method_b.environmental_impact, 0.6)
        
        # Adjust based on field conditions (slope, drainage, etc.)
        impact_a = self._adjust_environmental_score(impact_a, field_conditions)
        impact_b = self._adjust_environmental_score(impact_b, field_conditions)
        
        winner = "method_a" if impact_a > impact_b else "method_b"
        score_difference = abs(impact_a - impact_b)
        confidence_level = min(0.95, 0.75 + score_difference * 2)
        
        analysis_notes = [
            f"Method A environmental impact: {method_a.environmental_impact}",
            f"Method B environmental impact: {method_b.environmental_impact}",
            f"Adjusted scores: A={impact_a:.2f}, B={impact_b:.2f}"
        ]
        
        return ComparisonResult(
            method_a_score=impact_a,
            method_b_score=impact_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_labor_requirements(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod
    ) -> ComparisonResult:
        """Compare labor requirements of methods."""
        
        labor_a = self.labor_scores.get(method_a.labor_requirements, 0.6)
        labor_b = self.labor_scores.get(method_b.labor_requirements, 0.6)
        
        winner = "method_a" if labor_a > labor_b else "method_b"
        score_difference = abs(labor_a - labor_b)
        confidence_level = min(0.95, 0.8 + score_difference * 2)
        
        analysis_notes = [
            f"Method A labor intensity: {method_a.labor_requirements}",
            f"Method B labor intensity: {method_b.labor_requirements}",
            f"Labor scores: A={labor_a:.2f}, B={labor_b:.2f}"
        ]
        
        return ComparisonResult(
            method_a_score=labor_a,
            method_b_score=labor_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_equipment_needs(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        available_equipment: List[EquipmentSpecification]
    ) -> ComparisonResult:
        """Compare equipment needs and compatibility."""
        
        # Check equipment compatibility
        compat_a = self._check_equipment_compatibility(method_a, available_equipment)
        compat_b = self._check_equipment_compatibility(method_b, available_equipment)
        
        # Factor in equipment cost and availability
        cost_a = method_a.recommended_equipment.maintenance_cost_per_hour or 0
        cost_b = method_b.recommended_equipment.maintenance_cost_per_hour or 0
        
        # Combine compatibility and cost factors
        score_a = compat_a * (1.0 - min(cost_a / 200, 0.5))  # Cap cost impact at 50%
        score_b = compat_b * (1.0 - min(cost_b / 200, 0.5))
        
        winner = "method_a" if score_a > score_b else "method_b"
        score_difference = abs(score_a - score_b)
        confidence_level = min(0.95, 0.7 + score_difference * 2)
        
        analysis_notes = [
            f"Method A equipment compatibility: {compat_a:.2f}",
            f"Method B equipment compatibility: {compat_b:.2f}",
            f"Equipment costs: A=${cost_a:.2f}/hr, B=${cost_b:.2f}/hr"
        ]
        
        return ComparisonResult(
            method_a_score=score_a,
            method_b_score=score_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_field_suitability(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        field_conditions: FieldConditions
    ) -> ComparisonResult:
        """Compare field suitability of methods."""
        
        # Assess suitability based on field conditions
        suitability_a = self._assess_field_suitability(method_a, field_conditions)
        suitability_b = self._assess_field_suitability(method_b, field_conditions)
        
        winner = "method_a" if suitability_a > suitability_b else "method_b"
        score_difference = abs(suitability_a - suitability_b)
        confidence_level = min(0.95, 0.8 + score_difference * 2)
        
        analysis_notes = [
            f"Method A field suitability: {suitability_a:.2f}",
            f"Method B field suitability: {suitability_b:.2f}",
            f"Field size: {field_conditions.field_size_acres} acres",
            f"Soil type: {field_conditions.soil_type}"
        ]
        
        return ComparisonResult(
            method_a_score=suitability_a,
            method_b_score=suitability_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_nutrient_use_efficiency(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        crop_requirements: CropRequirements
    ) -> ComparisonResult:
        """Compare nutrient use efficiency of methods."""
        
        # Calculate nutrient use efficiency based on method characteristics
        efficiency_a = self._calculate_nutrient_efficiency(method_a, crop_requirements)
        efficiency_b = self._calculate_nutrient_efficiency(method_b, crop_requirements)
        
        winner = "method_a" if efficiency_a > efficiency_b else "method_b"
        score_difference = abs(efficiency_a - efficiency_b)
        confidence_level = min(0.95, 0.75 + score_difference * 2)
        
        analysis_notes = [
            f"Method A nutrient efficiency: {efficiency_a:.2f}",
            f"Method B nutrient efficiency: {efficiency_b:.2f}",
            f"Crop type: {crop_requirements.crop_type}"
        ]
        
        return ComparisonResult(
            method_a_score=efficiency_a,
            method_b_score=efficiency_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_timing_flexibility(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        crop_requirements: CropRequirements
    ) -> ComparisonResult:
        """Compare timing flexibility of methods."""
        
        # Assess timing flexibility based on method characteristics
        flexibility_a = self._assess_timing_flexibility(method_a, crop_requirements)
        flexibility_b = self._assess_timing_flexibility(method_b, crop_requirements)
        
        winner = "method_a" if flexibility_a > flexibility_b else "method_b"
        score_difference = abs(flexibility_a - flexibility_b)
        confidence_level = min(0.95, 0.7 + score_difference * 2)
        
        analysis_notes = [
            f"Method A timing flexibility: {flexibility_a:.2f}",
            f"Method B timing flexibility: {flexibility_b:.2f}",
            f"Growth stage: {crop_requirements.growth_stage}"
        ]
        
        return ComparisonResult(
            method_a_score=flexibility_a,
            method_b_score=flexibility_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_skill_requirements(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod
    ) -> ComparisonResult:
        """Compare skill requirements of methods."""
        
        # This would typically come from method data, using efficiency as proxy
        skill_a = 0.8  # Default skill score
        skill_b = 0.8
        
        winner = "method_a" if skill_a > skill_b else "method_b"
        score_difference = abs(skill_a - skill_b)
        confidence_level = min(0.95, 0.7 + score_difference * 2)
        
        analysis_notes = [
            f"Method A skill requirements: {skill_a:.2f}",
            f"Method B skill requirements: {skill_b:.2f}"
        ]
        
        return ComparisonResult(
            method_a_score=skill_a,
            method_b_score=skill_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _compare_weather_dependency(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod
    ) -> ComparisonResult:
        """Compare weather dependency of methods."""
        
        # Assess weather dependency based on method type
        weather_a = self._assess_weather_dependency(method_a)
        weather_b = self._assess_weather_dependency(method_b)
        
        winner = "method_a" if weather_a > weather_b else "method_b"
        score_difference = abs(weather_a - weather_b)
        confidence_level = min(0.95, 0.8 + score_difference * 2)
        
        analysis_notes = [
            f"Method A weather dependency: {weather_a:.2f}",
            f"Method B weather dependency: {weather_b:.2f}"
        ]
        
        return ComparisonResult(
            method_a_score=weather_a,
            method_b_score=weather_b,
            winner=winner,
            score_difference=score_difference,
            confidence_level=confidence_level,
            analysis_notes=analysis_notes
        )
    
    async def _calculate_total_cost(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions
    ) -> float:
        """Calculate total cost per acre for a method."""
        
        # Base application cost
        base_cost = method.cost_per_acre or 0.0
        
        # Equipment cost (if available)
        equipment_cost = 0.0
        if method.recommended_equipment and method.recommended_equipment.maintenance_cost_per_hour:
            # Estimate hours per acre based on field size and equipment capacity
            hours_per_acre = 1.0 / (method.recommended_equipment.capacity or 10)
            equipment_cost = method.recommended_equipment.maintenance_cost_per_hour * hours_per_acre
        
        # Labor cost
        labor_cost = 0.0
        if method.labor_requirements:
            labor_rates = {"very_low": 5.0, "low": 10.0, "medium": 15.0, "high": 20.0, "very_high": 25.0}
            labor_cost = labor_rates.get(method.labor_requirements, 15.0)
        
        return base_cost + equipment_cost + labor_cost
    
    def _adjust_environmental_score(self, base_score: float, field_conditions: FieldConditions) -> float:
        """Adjust environmental score based on field conditions."""
        
        # Adjust for slope (higher slope = higher runoff risk)
        slope_adjustment = 1.0
        if field_conditions.slope_percent:
            if field_conditions.slope_percent > 5:
                slope_adjustment = 0.8
            elif field_conditions.slope_percent > 2:
                slope_adjustment = 0.9
        
        # Adjust for drainage
        drainage_adjustment = 1.0
        if field_conditions.drainage_class:
            if field_conditions.drainage_class == "poorly_drained":
                drainage_adjustment = 0.8
            elif field_conditions.drainage_class == "moderately_drained":
                drainage_adjustment = 0.9
        
        return base_score * slope_adjustment * drainage_adjustment
    
    def _check_equipment_compatibility(
        self,
        method: ApplicationMethod,
        available_equipment: List[EquipmentSpecification]
    ) -> float:
        """Check equipment compatibility for a method."""
        
        if not available_equipment:
            return 0.0
        
        required_type = method.recommended_equipment.equipment_type
        compatible_equipment = [eq for eq in available_equipment if eq.equipment_type == required_type]
        
        if compatible_equipment:
            return 1.0
        else:
            return 0.0
    
    def _assess_field_suitability(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions
    ) -> float:
        """Assess field suitability for a method."""
        
        suitability = 1.0
        
        # Check field size compatibility
        field_size = field_conditions.field_size_acres
        if field_size < 10:  # Small field
            if method.method_type in [ApplicationMethodType.BROADCAST]:
                suitability *= 0.7  # Broadcast less suitable for small fields
        elif field_size > 1000:  # Very large field
            if method.method_type in [ApplicationMethodType.FOLIAR, ApplicationMethodType.DRIP]:
                suitability *= 0.6  # Foliar/drip less suitable for very large fields
        
        # Check soil type compatibility
        soil_type = field_conditions.soil_type.lower()
        if soil_type == "clay":
            if method.method_type in [ApplicationMethodType.INJECTION]:
                suitability *= 0.8  # Injection harder in clay
        elif soil_type == "sandy":
            if method.method_type in [ApplicationMethodType.BROADCAST]:
                suitability *= 0.8  # Broadcast less efficient in sandy soil
        
        # Check slope compatibility
        if field_conditions.slope_percent:
            if field_conditions.slope_percent > 5:
                if method.method_type in [ApplicationMethodType.BROADCAST]:
                    suitability *= 0.6  # Broadcast problematic on steep slopes
        
        return suitability
    
    def _calculate_nutrient_efficiency(
        self,
        method: ApplicationMethod,
        crop_requirements: CropRequirements
    ) -> float:
        """Calculate nutrient use efficiency for a method."""
        
        # Base efficiency from method
        base_efficiency = method.efficiency_score
        
        # Adjust based on crop type
        crop_type = crop_requirements.crop_type.lower()
        if crop_type in ["corn", "maize"]:
            # Corn responds well to band and sidedress applications
            if method.method_type in [ApplicationMethodType.BAND, ApplicationMethodType.SIDEDRESS]:
                base_efficiency *= 1.1
        elif crop_type in ["soybean", "soy"]:
            # Soybeans benefit from precise placement
            if method.method_type in [ApplicationMethodType.BAND, ApplicationMethodType.INJECTION]:
                base_efficiency *= 1.05
        
        return min(1.0, base_efficiency)
    
    def _assess_timing_flexibility(
        self,
        method: ApplicationMethod,
        crop_requirements: CropRequirements
    ) -> float:
        """Assess timing flexibility for a method."""
        
        # Base flexibility based on method type
        flexibility_scores = {
            ApplicationMethodType.BROADCAST: 0.9,
            ApplicationMethodType.BAND: 0.8,
            ApplicationMethodType.SIDEDRESS: 0.6,
            ApplicationMethodType.FOLIAR: 0.4,
            ApplicationMethodType.INJECTION: 0.7,
            ApplicationMethodType.DRIP: 0.8
        }
        
        base_flexibility = flexibility_scores.get(method.method_type, 0.7)
        
        # Adjust based on growth stage
        growth_stage = crop_requirements.growth_stage.lower()
        if growth_stage in ["emergence", "seedling"]:
            # Early stages have more flexibility
            base_flexibility *= 1.1
        elif growth_stage in ["flowering", "reproductive"]:
            # Later stages have less flexibility
            base_flexibility *= 0.9
        
        return min(1.0, base_flexibility)
    
    def _assess_weather_dependency(self, method: ApplicationMethod) -> float:
        """Assess weather dependency for a method."""
        
        # Weather dependency scores (higher = less dependent)
        weather_scores = {
            ApplicationMethodType.BROADCAST: 0.4,  # Very weather dependent
            ApplicationMethodType.BAND: 0.7,       # Moderately dependent
            ApplicationMethodType.SIDEDRESS: 0.6,  # Moderately dependent
            ApplicationMethodType.FOLIAR: 0.3,     # Very weather dependent
            ApplicationMethodType.INJECTION: 0.8,  # Less dependent
            ApplicationMethodType.DRIP: 0.9        # Least dependent
        }
        
        return weather_scores.get(method.method_type, 0.6)
    
    async def _perform_sensitivity_analysis(
        self,
        criteria_scores: Dict[str, ComparisonResult],
        weights: Dict[str, float],
        method_a_type: str,
        method_b_type: str
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on the comparison."""
        
        sensitivity_results = {}
        
        # Test weight variations
        for criterion, original_weight in weights.items():
            if criterion in criteria_scores:
                # Test ±20% weight variation
                variations = [0.8, 1.0, 1.2]
                results = []
                
                for variation in variations:
                    new_weights = weights.copy()
                    new_weights[criterion] = original_weight * variation
                    
                    # Recalculate weighted scores
                    weighted_a = sum(
                        criteria_scores[c].method_a_score * new_weights[c]
                        for c in criteria_scores.keys()
                    )
                    weighted_b = sum(
                        criteria_scores[c].method_b_score * new_weights[c]
                        for c in criteria_scores.keys()
                    )
                    
                    winner = method_a_type if weighted_a > weighted_b else method_b_type
                    results.append({
                        "weight_variation": variation,
                        "weighted_a": weighted_a,
                        "weighted_b": weighted_b,
                        "winner": winner
                    })
                
                sensitivity_results[criterion] = {
                    "original_weight": original_weight,
                    "variations": results,
                    "sensitive": len(set(r["winner"] for r in results)) > 1
                }
        
        return sensitivity_results
    
    async def _generate_comparison_result(
        self,
        method_a: ApplicationMethod,
        method_b: ApplicationMethod,
        analysis: MultiCriteriaAnalysis,
        comparison_id: str,
        start_time: float
    ) -> MethodComparison:
        """Generate the final comparison result."""
        
        # Convert ApplicationMethod to MethodModel for response
        from models.method_models import ApplicationTiming, ApplicationPrecision, EnvironmentalImpact
        
        # Map application timing string to enum
        timing_mapping = {
            "pre_plant": ApplicationTiming.PRE_PLANT,
            "at_planting": ApplicationTiming.AT_PLANTING,
            "post_emergence": ApplicationTiming.POST_EMERGENCE,
            "sidedress": ApplicationTiming.SIDEDRESS,
            "topdress": ApplicationTiming.TOPDRESS,
            "foliar": ApplicationTiming.FOLIAR,
            "fall": ApplicationTiming.FALL,
            "spring": ApplicationTiming.SPRING,
            "summer": ApplicationTiming.SUMMER
        }
        
        # Map environmental impact string to enum
        env_mapping = {
            "very_low": EnvironmentalImpact.LOW,
            "low": EnvironmentalImpact.LOW,
            "moderate": EnvironmentalImpact.MODERATE,
            "high": EnvironmentalImpact.HIGH,
            "very_high": EnvironmentalImpact.VERY_HIGH
        }
        
        # Map precision level
        precision_mapping = {
            "broadcast": ApplicationPrecision.BROADCAST,
            "band": ApplicationPrecision.BAND,
            "precision": ApplicationPrecision.PRECISION,
            "variable_rate": ApplicationPrecision.VARIABLE_RATE
        }
        
        method_a_model = MethodModel(
            method_id=method_a.method_id,
            method_name=method_a.method_type.value.replace("_", " ").title(),
            method_type=method_a.method_type.value,
            description=f"{method_a.method_type.value} application method",
            application_timing=[timing_mapping.get(method_a.application_timing.lower().replace(" ", "_"), ApplicationTiming.PRE_PLANT)],
            precision_level=precision_mapping.get(method_a.method_type.value, ApplicationPrecision.BAND),
            environmental_impact=env_mapping.get(method_a.environmental_impact or "moderate", EnvironmentalImpact.MODERATE),
            equipment_requirements=[method_a.recommended_equipment.equipment_type.value],
            labor_intensity=method_a.labor_requirements or "medium",
            skill_requirements="skilled",
            cost_per_acre=method_a.cost_per_acre or 0.0,
            efficiency_rating=method_a.efficiency_score,
            suitability_factors={}
        )
        
        method_b_model = MethodModel(
            method_id=method_b.method_id,
            method_name=method_b.method_type.value.replace("_", " ").title(),
            method_type=method_b.method_type.value,
            description=f"{method_b.method_type.value} application method",
            application_timing=[timing_mapping.get(method_b.application_timing.lower().replace(" ", "_"), ApplicationTiming.PRE_PLANT)],
            precision_level=precision_mapping.get(method_b.method_type.value, ApplicationPrecision.BAND),
            environmental_impact=env_mapping.get(method_b.environmental_impact or "moderate", EnvironmentalImpact.MODERATE),
            equipment_requirements=[method_b.recommended_equipment.equipment_type.value],
            labor_intensity=method_b.labor_requirements or "medium",
            skill_requirements="skilled",
            cost_per_acre=method_b.cost_per_acre or 0.0,
            efficiency_rating=method_b.efficiency_score,
            suitability_factors={}
        )
        
        # Generate winner by criteria
        winner_by_criteria = {}
        for criterion, result in analysis.criteria_scores.items():
            winner_by_criteria[criterion] = result.winner
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            method_a_model, method_b_model, analysis
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return MethodComparison(
            method_a=method_a_model,
            method_b=method_b_model,
            comparison_criteria=list(analysis.criteria_scores.keys()),
            method_a_scores={c: r.method_a_score for c, r in analysis.criteria_scores.items()},
            method_b_scores={c: r.method_b_score for c, r in analysis.criteria_scores.items()},
            winner_by_criteria=winner_by_criteria,
            overall_winner=analysis.overall_winner,
            recommendation=recommendation
        )
    
    def _generate_recommendation(
        self,
        method_a: MethodModel,
        method_b: MethodModel,
        analysis: MultiCriteriaAnalysis
    ) -> str:
        """Generate recommendation text based on analysis."""
        
        winner_method = method_a if analysis.overall_winner == method_a.method_type else method_b
        loser_method = method_b if analysis.overall_winner == method_a.method_type else method_a
        
        # Calculate recommendation strength
        strength = analysis.recommendation_strength
        
        if strength > 0.3:
            strength_text = "strongly"
        elif strength > 0.15:
            strength_text = "moderately"
        else:
            strength_text = "slightly"
        
        # Identify key advantages
        advantages = []
        for criterion, result in analysis.criteria_scores.items():
            if result.winner == analysis.overall_winner:
                advantages.append(criterion.replace("_", " "))
        
        advantages_text = ", ".join(advantages[:3])  # Top 3 advantages
        
        recommendation = (
            f"Based on comprehensive analysis, {winner_method.method_name} is {strength_text} "
            f"recommended over {loser_method.method_name}. Key advantages include: {advantages_text}. "
            f"The recommendation confidence is {strength:.1%}."
        )
        
        return recommendation