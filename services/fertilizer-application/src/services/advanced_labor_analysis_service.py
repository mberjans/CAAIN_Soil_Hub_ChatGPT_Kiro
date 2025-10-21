"""
Advanced Labor Analysis Service for fertilizer application method optimization.

This service provides sophisticated labor cost analysis, workforce optimization, and labor efficiency
modeling for fertilizer application methods, building on the existing cost analysis service.
"""

import asyncio
import logging
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from uuid import uuid4

from src.models.application_models import (
    ApplicationMethod, FieldConditions, CropRequirements, 
    FertilizerSpecification, EquipmentSpecification
)
from src.services.cost_analysis_service import CostAnalysisService, LaborSkillLevel, SeasonalConstraint

logger = logging.getLogger(__name__)


class LaborEfficiencyMetric(str, Enum):
    """Types of labor efficiency metrics."""
    PRODUCTIVITY_RATE = "productivity_rate"
    QUALITY_SCORE = "quality_score"
    SAFETY_RECORD = "safety_record"
    EQUIPMENT_UTILIZATION = "equipment_utilization"
    CONTINUOUS_IMPROVEMENT = "continuous_improvement"


@dataclass
class LaborEfficiencyScore:
    """Labor efficiency score for a specific application method."""
    method_id: str
    productivity_rate: float  # acres per hour
    quality_score: float  # 0-1 scale for application quality
    safety_score: float  # 0-1 scale for safety compliance
    equipment_utilization: float  # 0-1 scale for equipment usage efficiency
    overall_efficiency: float  # weighted average of all factors
    skill_alignment_score: float  # how well labor skills match method requirements
    training_requirement_score: float  # how much training required


@dataclass
class LaborOptimizationResult:
    """Result of labor optimization analysis."""
    recommended_labor_plan: Dict[str, Any]
    efficiency_metrics: Dict[str, LaborEfficiencyScore]
    cost_per_unit_metrics: Dict[str, float]
    optimization_time_ms: float
    labor_requirements_summary: Dict[str, float]
    risk_assessment: Dict[str, Any]


class AdvancedLaborAnalysisService:
    """Advanced service for labor cost and efficiency analysis."""
    
    def __init__(self):
        self.cost_analysis_service = CostAnalysisService()
        self.skill_requirement_matrix = self._initialize_skill_matrix()
        
    def _initialize_skill_matrix(self) -> Dict[str, Dict[str, Any]]:
        """Initialize skill requirement matrix for different methods."""
        return {
            "broadcast": {
                "primary_skill": LaborSkillLevel.SEMI_SKILLED,
                "secondary_skills": [LaborSkillLevel.UNSKILLED],
                "training_hours": 4,
                "certification_required": False
            },
            "band": {
                "primary_skill": LaborSkillLevel.SKILLED,
                "secondary_skills": [LaborSkillLevel.SEMI_SKILLED],
                "training_hours": 8,
                "certification_required": True
            },
            "sidedress": {
                "primary_skill": LaborSkillLevel.SKILLED,
                "secondary_skills": [LaborSkillLevel.SEMI_SKILLED],
                "training_hours": 12,
                "certification_required": True
            },
            "foliar": {
                "primary_skill": LaborSkillLevel.HIGHLY_SKILLED,
                "secondary_skills": [LaborSkillLevel.SKILLED],
                "training_hours": 16,
                "certification_required": True
            },
            "injection": {
                "primary_skill": LaborSkillLevel.SKILLED,
                "secondary_skills": [LaborSkillLevel.SEMI_SKILLED],
                "training_hours": 10,
                "certification_required": True
            },
            "drip": {
                "primary_skill": LaborSkillLevel.SEMI_SKILLED,
                "secondary_skills": [LaborSkillLevel.UNSKILLED],
                "training_hours": 6,
                "certification_required": False
            }
        }
    
    async def analyze_labor_efficiency(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, LaborEfficiencyScore]:
        """Analyze labor efficiency for different application methods."""
        start_time = time.time()
        
        efficiency_scores = {}
        
        for method in application_methods:
            efficiency_score = await self._calculate_method_efficiency(
                method, field_conditions, crop_requirements, available_equipment
            )
            efficiency_scores[method.method_id] = efficiency_score
        
        processing_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Labor efficiency analysis completed in {processing_time_ms:.2f}ms")
        
        return efficiency_scores
    
    async def _calculate_method_efficiency(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        available_equipment: List[EquipmentSpecification]
    ) -> LaborEfficiencyScore:
        """Calculate efficiency score for a specific method."""
        
        # Calculate productivity rate (acres per hour)
        productivity_rate = await self._calculate_productivity_rate(
            method, field_conditions, available_equipment
        )
        
        # Calculate quality score based on method and equipment
        quality_score = await self._calculate_quality_score(method, available_equipment)
        
        # Calculate safety score
        safety_score = await self._calculate_safety_score(method)
        
        # Calculate equipment utilization
        equipment_utilization = await self._calculate_equipment_utilization(
            method, available_equipment
        )
        
        # Calculate skill alignment
        skill_alignment_score = await self._calculate_skill_alignment_score(method)
        
        # Calculate training requirement impact
        training_requirement_score = await self._calculate_training_requirement_score(method)
        
        # Calculate weighted overall efficiency
        weights = {
            "productivity": 0.25,
            "quality": 0.25,
            "safety": 0.15,
            "equipment_utilization": 0.15,
            "skill_alignment": 0.10,
            "training_requirement": 0.10
        }
        
        overall_efficiency = (
            weights["productivity"] * productivity_rate / 10 +  # Normalize productivity
            weights["quality"] * quality_score +
            weights["safety"] * safety_score +
            weights["equipment_utilization"] * equipment_utilization +
            weights["skill_alignment"] * skill_alignment_score +
            weights["training_requirement"] * training_requirement_score
        )
        
        return LaborEfficiencyScore(
            method_id=method.method_id,
            productivity_rate=productivity_rate,
            quality_score=quality_score,
            safety_score=safety_score,
            equipment_utilization=equipment_utilization,
            overall_efficiency=overall_efficiency,
            skill_alignment_score=skill_alignment_score,
            training_requirement_score=training_requirement_score
        )
    
    async def _calculate_productivity_rate(
        self,
        method: ApplicationMethod,
        field_conditions: FieldConditions,
        available_equipment: List[EquipmentSpecification]
    ) -> float:
        """Calculate productivity rate (acres per hour) for the method."""
        
        # Base productivity rates by method
        base_rates = {
            "broadcast": 50.0,  # acres per hour
            "band": 30.0,
            "sidedress": 25.0,
            "foliar": 20.0,
            "injection": 35.0,
            "drip": 40.0
        }
        
        base_rate = base_rates.get(method.method_type.value, 30.0)
        
        # Adjust for field conditions
        slope_factor = 1.0
        if field_conditions.slope_percent and field_conditions.slope_percent > 5:
            slope_factor = max(0.5, 1.0 - (field_conditions.slope_percent * 0.02))
        
        # Adjust for equipment
        equipment_factor = 1.0
        compatible_equipment = self._find_compatible_equipment(
            method.recommended_equipment.equipment_type, available_equipment
        )
        if compatible_equipment and compatible_equipment.capacity:
            equipment_factor = min(2.0, compatible_equipment.capacity / 1000.0)
        
        adjusted_rate = base_rate * slope_factor * equipment_factor
        
        return min(adjusted_rate, 100.0)  # Cap at 100 acres per hour
    
    async def _calculate_quality_score(
        self,
        method: ApplicationMethod,
        available_equipment: List[EquipmentSpecification]
    ) -> float:
        """Calculate quality score for the application method."""
        
        # Base quality scores by method
        base_scores = {
            "broadcast": 0.7,
            "band": 0.8,
            "sidedress": 0.9,
            "foliar": 0.95,
            "injection": 0.85,
            "drip": 0.98
        }
        
        base_score = base_scores.get(method.method_type.value, 0.8)
        
        # Adjust for equipment quality
        equipment_quality_factor = 1.0
        compatible_equipment = self._find_compatible_equipment(
            method.recommended_equipment.equipment_type, available_equipment
        )
        if compatible_equipment:
            # Assume newer equipment has better quality
            equipment_quality_factor = min(1.2, base_score + 0.1)
        
        return min(base_score * equipment_quality_factor, 1.0)
    
    async def _calculate_safety_score(self, method: ApplicationMethod) -> float:
        """Calculate safety score for the application method."""
        
        # Base safety scores by method
        base_scores = {
            "broadcast": 0.9,  # Generally safe
            "band": 0.85,      # Moderate risk with attachments
            "sidedress": 0.8,  # Higher risk with growth stage
            "foliar": 0.75,    # Chemical exposure risk
            "injection": 0.7,  # Equipment and chemical risk
            "drip": 0.95       # Low risk
        }
        
        base_score = base_scores.get(method.method_type.value, 0.85)
        
        # Consider environmental conditions
        # This would normally be based on weather data
        weather_risk_factor = 1.0  # Placeholder
        
        return min(base_score * weather_risk_factor, 1.0)
    
    async def _calculate_equipment_utilization(
        self,
        method: ApplicationMethod,
        available_equipment: List[EquipmentSpecification]
    ) -> float:
        """Calculate equipment utilization efficiency."""
        
        compatible_equipment = self._find_compatible_equipment(
            method.recommended_equipment.equipment_type, available_equipment
        )
        
        if not compatible_equipment:
            # No compatible equipment, low utilization
            return 0.3
        
        # Calculate utilization based on equipment capacity and field size
        # This is a simplified calculation
        utilization = min(0.9, 0.5 + (compatible_equipment.capacity or 500) / 2000)
        
        return utilization
    
    async def _calculate_skill_alignment_score(self, method: ApplicationMethod) -> float:
        """Calculate how well labor skills align with method requirements."""
        
        skill_info = self.skill_requirement_matrix.get(method.method_type.value, {})
        primary_skill = skill_info.get("primary_skill", LaborSkillLevel.SEMI_SKILLED)
        
        # For this simplified model, assume perfect alignment
        # In a real system, this would depend on actual worker skills
        if primary_skill == LaborSkillLevel.HIGHLY_SKILLED:
            return 0.7  # Higher skill methods have lower alignment probability
        elif primary_skill == LaborSkillLevel.SKILLED:
            return 0.8
        else:
            return 0.9
    
    async def _calculate_training_requirement_score(self, method: ApplicationMethod) -> float:
        """Calculate score based on training requirements."""
        
        skill_info = self.skill_requirement_matrix.get(method.method_type.value, {})
        training_hours = skill_info.get("training_hours", 8)
        
        # More training required means lower score (more complex)
        # Normalize to 0-1 scale where 0 hours = 1.0 score, 40 hours = 0.3 score
        training_score = max(0.3, 1.0 - (training_hours / 40.0 * 0.7))
        
        return training_score
    
    def _find_compatible_equipment(
        self,
        equipment_type: str,
        available_equipment: List[EquipmentSpecification]
    ) -> Optional[EquipmentSpecification]:
        """Find compatible equipment for the method."""
        for equipment in available_equipment:
            if equipment.equipment_type.value == equipment_type:
                return equipment
        return None
    
    async def perform_labor_optimization(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification],
        seasonal_constraint: Optional[SeasonalConstraint] = None
    ) -> LaborOptimizationResult:
        """Perform comprehensive labor optimization analysis."""
        start_time = time.time()
        
        # Analyze labor efficiency for all methods
        efficiency_scores = await self.analyze_labor_efficiency(
            application_methods, field_conditions, crop_requirements, available_equipment
        )
        
        # Get cost analysis for labor costs
        cost_analysis = await self.cost_analysis_service.analyze_application_costs(
            application_methods, field_conditions, crop_requirements,
            fertilizer_specification, available_equipment
        )
        
        # Calculate labor-specific metrics
        labor_metrics = {}
        for method in application_methods:
            method_cost = next(
                (mc for mc in cost_analysis["method_costs"] if mc["method_id"] == method.method_id),
                {}
            )
            
            efficiency = efficiency_scores.get(method.method_id)
            if efficiency:
                labor_cost = method_cost.get("labor_costs", {}).get("total_cost", 0)
                labor_hours = method_cost.get("labor_costs", {}).get("labor_hours", 1)
                
                cost_per_unit = labor_cost / (field_conditions.field_size_acres or 1) if labor_cost > 0 else 0
                efficiency_per_cost = efficiency.overall_efficiency / (cost_per_unit or 1)
                
                labor_metrics[method.method_id] = {
                    "cost_per_acre": cost_per_unit,
                    "efficiency_per_cost": efficiency_per_cost,
                    "productivity_rate": efficiency.productivity_rate,
                    "overall_efficiency": efficiency.overall_efficiency
                }
        
        # Create recommended labor plan
        recommended_plan = await self._create_recommended_labor_plan(
            application_methods, efficiency_scores, cost_analysis
        )
        
        # Calculate labor requirements summary
        labor_summary = await self._calculate_labor_requirements_summary(
            cost_analysis, field_conditions
        )
        
        # Perform risk assessment
        risk_assessment = await self._perform_labor_risk_assessment(
            efficiency_scores, labor_summary
        )
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return LaborOptimizationResult(
            recommended_labor_plan=recommended_plan,
            efficiency_metrics=efficiency_scores,
            cost_per_unit_metrics=labor_metrics,
            optimization_time_ms=processing_time_ms,
            labor_requirements_summary=labor_summary,
            risk_assessment=risk_assessment
        )
    
    async def _create_recommended_labor_plan(
        self,
        application_methods: List[ApplicationMethod],
        efficiency_scores: Dict[str, LaborEfficiencyScore],
        cost_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create recommended labor plan based on analysis."""
        
        # Rank methods by efficiency-to-cost ratio
        ranked_methods = []
        for method in application_methods:
            efficiency = efficiency_scores.get(method.method_id)
            if efficiency:
                # Find method cost data
                method_cost = next(
                    (mc for mc in cost_analysis["method_costs"] if mc["method_id"] == method.method_id),
                    {}
                )
                
                labor_cost_per_acre = method_cost.get("labor_costs", {}).get("cost_per_acre", 0)
                
                # Calculate efficiency-to-cost ratio
                efficiency_to_cost = efficiency.overall_efficiency / (labor_cost_per_acre or 1)
                
                ranked_methods.append({
                    "method_id": method.method_id,
                    "method_type": method.method_type.value,
                    "efficiency_score": efficiency.overall_efficiency,
                    "labor_cost_per_acre": labor_cost_per_acre,
                    "efficiency_to_cost_ratio": efficiency_to_cost,
                    "priority": efficiency.overall_efficiency - labor_cost_per_acre  # Higher is better
                })
        
        # Sort by priority (highest first)
        ranked_methods.sort(key=lambda x: x["priority"], reverse=True)
        
        return {
            "recommended_method": ranked_methods[0] if ranked_methods else None,
            "method_rankings": ranked_methods,
            "labor_allocation_recommendations": await self._create_labor_allocation_recommendations(
                ranked_methods
            )
        }
    
    async def _create_labor_allocation_recommendations(
        self,
        ranked_methods: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Create labor allocation recommendations."""
        
        recommendations = []
        for i, method in enumerate(ranked_methods):
            recommendations.append({
                "method_id": method["method_id"],
                "allocation_priority": i + 1,  # 1 is highest priority
                "recommendation": f"Use for high-priority applications" if i == 0 else f"Consider for backup/secondary applications",
                "estimated_labor_hours": method["efficiency_score"] * 100,  # Simplified calculation
                "skill_level_required": "Varies"
            })
        
        return recommendations
    
    async def _calculate_labor_requirements_summary(
        self,
        cost_analysis: Dict[str, Any],
        field_conditions: FieldConditions
    ) -> Dict[str, float]:
        """Calculate labor requirements summary."""
        
        total_labor_hours = 0
        total_labor_cost = 0
        avg_labor_cost_per_acre = 0
        
        for method_cost in cost_analysis["method_costs"]:
            labor_cost = method_cost.get("labor_costs", {})
            total_labor_hours += labor_cost.get("labor_hours", 0)
            total_labor_cost += labor_cost.get("total_cost", 0)
        
        if method_cost:
            avg_labor_cost_per_acre = total_labor_cost / field_conditions.field_size_acres
        
        return {
            "total_labor_hours": total_labor_hours,
            "total_labor_cost": total_labor_cost,
            "avg_labor_cost_per_acre": avg_labor_cost_per_acre,
            "labor_intensity": total_labor_hours / max(field_conditions.field_size_acres, 1)
        }
    
    async def _perform_labor_risk_assessment(
        self,
        efficiency_scores: Dict[str, LaborEfficiencyScore],
        labor_summary: Dict[str, float]
    ) -> Dict[str, Any]:
        """Perform labor risk assessment."""
        
        # Analyze risk factors
        high_risk_methods = []
        for method_id, efficiency in efficiency_scores.items():
            if efficiency.overall_efficiency < 0.5 or efficiency.safety_score < 0.7:
                high_risk_methods.append(method_id)
        
        # Determine overall risk level
        avg_efficiency = np.mean([e.overall_efficiency for e in efficiency_scores.values()]) if efficiency_scores else 0.5
        avg_safety = np.mean([e.safety_score for e in efficiency_scores.values()]) if efficiency_scores else 0.8
        
        risk_level = "low"
        if avg_efficiency < 0.6 or avg_safety < 0.75:
            risk_level = "medium"
        if avg_efficiency < 0.4 or avg_safety < 0.6:
            risk_level = "high"
        
        return {
            "overall_risk_level": risk_level,
            "high_risk_methods": high_risk_methods,
            "avg_efficiency_score": avg_efficiency,
            "avg_safety_score": avg_safety,
            "risk_mitigation_recommendations": self._generate_risk_mitigation_recommendations(
                risk_level, high_risk_methods
            )
        }
    
    def _generate_risk_mitigation_recommendations(
        self,
        risk_level: str,
        high_risk_methods: List[str]
    ) -> List[str]:
        """Generate risk mitigation recommendations."""
        
        recommendations = []
        
        if risk_level == "high":
            recommendations.append("Require additional safety training for all operators")
            recommendations.append("Implement additional safety supervision")
            recommendations.append("Consider alternative methods with better safety scores")
        elif risk_level == "medium":
            recommendations.append("Review safety procedures for high-risk methods")
            recommendations.append("Provide refresher training for complex methods")
        
        if high_risk_methods:
            recommendations.append(f"Prioritize training for methods: {', '.join(high_risk_methods)}")
        
        recommendations.append("Regular safety audits and equipment maintenance")
        recommendations.append("Maintain emergency response procedures")
        
        return recommendations
    
    async def calculate_labor_roi(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate return on investment specifically for labor."""
        
        # Get efficiency and cost analysis
        efficiency_scores = await self.analyze_labor_efficiency(
            application_methods, field_conditions, crop_requirements, available_equipment
        )
        
        cost_analysis = await self.cost_analysis_service.analyze_application_costs(
            application_methods, field_conditions, crop_requirements,
            fertilizer_specification, available_equipment
        )
        
        labor_roi = {}
        
        for method in application_methods:
            efficiency = efficiency_scores.get(method.method_id)
            method_cost = next(
                (mc for mc in cost_analysis["method_costs"] if mc["method_id"] == method.method_id),
                {}
            )
            
            if efficiency and method_cost:
                labor_cost = method_cost.get("labor_costs", {}).get("total_cost", 0)
                # Simplified revenue estimation based on efficiency
                estimated_revenue = efficiency.overall_efficiency * 10000  # Placeholder
                
                roi = (estimated_revenue - labor_cost) / labor_cost if labor_cost > 0 else 0
                
                labor_roi[method.method_id] = {
                    "labor_cost": labor_cost,
                    "estimated_revenue": estimated_revenue,
                    "roi": roi,
                    "roi_percentage": roi * 100
                }
        
        return labor_roi
    
    async def calculate_labor_sensitivity_analysis(
        self,
        application_methods: List[ApplicationMethod],
        field_conditions: FieldConditions,
        crop_requirements: CropRequirements,
        fertilizer_specification: FertilizerSpecification,
        available_equipment: List[EquipmentSpecification]
    ) -> Dict[str, Any]:
        """Calculate sensitivity of labor costs to various factors."""
        
        # Run analysis with different labor cost scenarios
        scenarios = [0.8, 0.9, 1.0, 1.1, 1.2]  # 20% variation in labor costs
        sensitivity_results = {}
        
        for method in application_methods:
            method_results = []
            
            for scenario_multiplier in scenarios:
                # Get base analysis
                efficiency_scores = await self.analyze_labor_efficiency(
                    [method], field_conditions, crop_requirements, available_equipment
                )
                
                # Modify labor costs for scenario
                cost_analysis = await self.cost_analysis_service.analyze_application_costs(
                    [method], field_conditions, crop_requirements,
                    fertilizer_specification, available_equipment
                )
                
                # Apply labor cost multiplier
                # This would require temporarily modifying the cost database in a real implementation
                
                scenario_result = {
                    "labor_cost_multiplier": scenario_multiplier,
                    "efficiency_score": efficiency_scores.get(method.method_id, 
                        LaborEfficiencyScore(method.method_id, 1, 1, 1, 1, 1, 1, 1)
                    ).overall_efficiency,
                    "scenario_impact": "To be calculated based on modified costs"
                }
                
                method_results.append(scenario_result)
            
            sensitivity_results[method.method_id] = method_results
        
        return {
            "sensitivity_analysis": sensitivity_results,
            "summary": {
                "methods_analyzed": len(application_methods),
                "scenarios_tested": len(scenarios)
            }
        }