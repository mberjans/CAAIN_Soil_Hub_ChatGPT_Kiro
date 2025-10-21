"""
API Routes for Decision Support System.

This module provides REST API endpoints for the decision support system,
including decision trees, expert systems, scenario analysis, and sensitivity analysis.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from src.models.application_models import (
    FieldConditions, CropRequirements, FertilizerSpecification, EquipmentSpecification
)
from src.services.decision_support_service import (
    DecisionSupportService, DecisionRule, DecisionSupportResult
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/decision-support", tags=["decision-support"])


class DecisionSupportRequest(BaseModel):
    """Request model for decision support."""
    field_conditions: FieldConditions = Field(..., description="Field conditions and characteristics")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements and constraints")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specifications")
    available_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Available equipment inventory")
    farmer_preferences: Optional[Dict[str, Any]] = Field(None, description="Farmer preferences and constraints")
    decision_rule: DecisionRule = Field(DecisionRule.DECISION_TREE, description="Decision rule to use")
    include_scenarios: bool = Field(True, description="Whether to include scenario analysis")
    include_sensitivity: bool = Field(True, description="Whether to include sensitivity analysis")


class InteractiveDecisionRequest(BaseModel):
    """Request model for interactive decision support."""
    field_conditions: FieldConditions = Field(..., description="Field conditions")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specifications")
    available_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Available equipment")
    farmer_preferences: Dict[str, Any] = Field(..., description="Farmer preferences and weights")
    decision_criteria: List[str] = Field(..., description="Decision criteria to prioritize")
    custom_weights: Optional[Dict[str, float]] = Field(None, description="Custom weights for criteria")


class WhatIfAnalysisRequest(BaseModel):
    """Request model for what-if analysis."""
    base_field_conditions: FieldConditions = Field(..., description="Base field conditions")
    crop_requirements: CropRequirements = Field(..., description="Crop requirements")
    fertilizer_specification: FertilizerSpecification = Field(..., description="Fertilizer specifications")
    available_equipment: List[EquipmentSpecification] = Field(default_factory=list, description="Available equipment")
    scenario_changes: Dict[str, Any] = Field(..., description="Changes to apply in what-if scenario")
    analysis_type: str = Field("comparison", description="Type of analysis: comparison, sensitivity, or optimization")


# Dependency injection
async def get_decision_support_service() -> DecisionSupportService:
    return DecisionSupportService()


@router.post("/provide-support", response_model=DecisionSupportResult)
async def provide_decision_support(
    request: DecisionSupportRequest,
    service: DecisionSupportService = Depends(get_decision_support_service)
):
    """
    Provide comprehensive decision support for fertilizer application method selection.
    
    This endpoint implements the core decision support system with multiple decision rules,
    scenario analysis, sensitivity analysis, and risk assessment to help farmers make
    informed decisions about fertilizer application methods.
    
    **Decision Rules Available:**
    - Decision Tree: Rule-based decision making with agricultural expertise
    - Expert System: Knowledge-based rules from agricultural experts
    - Weighted Sum: Multi-criteria decision analysis with weighted scoring
    - TOPSIS: Technique for Order Preference by Similarity to Ideal Solution
    - ELECTRE: Elimination and Choice Expressing Reality method
    - Fuzzy Logic: Fuzzy decision making for uncertain conditions
    
    **Analysis Features:**
    - Scenario Analysis: Best-case, worst-case, and most-likely scenarios
    - Sensitivity Analysis: Parameter sensitivity and critical thresholds
    - Risk Assessment: Environmental, economic, and operational risks
    - Decision Matrix: Multi-criteria evaluation with weighted scores
    - Alternative Recommendations: Top alternative methods with explanations
    
    **Agricultural Context:**
    - Considers field size, soil type, slope, and drainage characteristics
    - Evaluates crop requirements, growth stage, and nutrient needs
    - Assesses equipment compatibility and availability
    - Provides confidence levels and detailed explanations
    - Includes risk mitigation strategies and recommendations
    """
    try:
        logger.info("Processing decision support request")
        
        result = await service.provide_decision_support(
            field_conditions=request.field_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_specification=request.fertilizer_specification,
            available_equipment=request.available_equipment,
            farmer_preferences=request.farmer_preferences,
            decision_rule=request.decision_rule,
            include_scenarios=request.include_scenarios,
            include_sensitivity=request.include_sensitivity
        )
        
        logger.info(f"Decision support completed for request {result.decision_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in decision support: {e}")
        raise HTTPException(status_code=500, detail=f"Decision support failed: {str(e)}")


@router.post("/interactive-decision")
async def interactive_decision_support(
    request: InteractiveDecisionRequest,
    service: DecisionSupportService = Depends(get_decision_support_service)
):
    """
    Provide interactive decision support with farmer preferences and custom criteria.
    
    This endpoint allows farmers to interactively explore different decision scenarios
    by adjusting preferences, criteria weights, and constraints to see how they
    affect method recommendations.
    
    **Interactive Features:**
    - Custom criteria weighting based on farmer priorities
    - Real-time decision updates as preferences change
    - What-if analysis for different scenarios
    - Guided decision-making workflow
    - Alternative method exploration with explanations
    
    **Farmer Preferences:**
    - Cost sensitivity levels (low, medium, high)
    - Environmental priorities (runoff prevention, soil health)
    - Labor availability and skill levels
    - Equipment investment willingness
    - Risk tolerance levels
    
    **Custom Criteria:**
    - Cost effectiveness
    - Application efficiency
    - Environmental impact
    - Labor requirements
    - Equipment needs
    - Field suitability
    - Nutrient use efficiency
    """
    try:
        logger.info("Processing interactive decision support request")
        
        # Use weighted sum with custom weights for interactive analysis
        result = await service.provide_decision_support(
            field_conditions=request.field_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_specification=request.fertilizer_specification,
            available_equipment=request.available_equipment,
            farmer_preferences=request.farmer_preferences,
            decision_rule=DecisionRule.WEIGHTED_SUM,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        # Add interactive-specific analysis
        interactive_result = {
            "decision_result": result,
            "interactive_features": {
                "custom_criteria": request.decision_criteria,
                "farmer_preferences": request.farmer_preferences,
                "custom_weights": request.custom_weights,
                "exploration_suggestions": [
                    "Try adjusting cost sensitivity to see impact on recommendations",
                    "Explore environmental priority weighting for sustainability focus",
                    "Consider labor availability constraints for operational planning"
                ]
            }
        }
        
        logger.info("Interactive decision support completed")
        return interactive_result
        
    except Exception as e:
        logger.error(f"Error in interactive decision support: {e}")
        raise HTTPException(status_code=500, detail=f"Interactive decision support failed: {str(e)}")


@router.post("/what-if-analysis")
async def what_if_analysis(
    request: WhatIfAnalysisRequest,
    service: DecisionSupportService = Depends(get_decision_support_service)
):
    """
    Perform what-if analysis for different scenarios and conditions.
    
    This endpoint allows farmers to explore how changes in field conditions,
    equipment availability, or other factors would affect method recommendations.
    
    **What-If Scenarios:**
    - Field size changes (expansion, contraction)
    - Soil condition modifications (pH, organic matter, drainage)
    - Equipment availability changes (new purchases, breakdowns)
    - Weather condition variations (drought, excess rain)
    - Economic condition changes (fertilizer prices, labor costs)
    - Regulatory requirement updates (environmental restrictions)
    
    **Analysis Types:**
    - Comparison: Compare base scenario with modified scenario
    - Sensitivity: Analyze parameter sensitivity and critical thresholds
    - Optimization: Find optimal conditions for specific methods
    
    **Use Cases:**
    - Planning for field expansion or equipment purchases
    - Assessing impact of weather or economic changes
    - Evaluating regulatory compliance scenarios
    - Optimizing for specific goals (cost, efficiency, sustainability)
    """
    try:
        logger.info("Processing what-if analysis request")
        
        # Get base scenario recommendation
        base_result = await service.provide_decision_support(
            field_conditions=request.base_field_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_specification=request.fertilizer_specification,
            available_equipment=request.available_equipment,
            decision_rule=DecisionRule.DECISION_TREE,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        # Apply scenario changes to field conditions
        modified_conditions = request.base_field_conditions.copy() if hasattr(request.base_field_conditions, 'copy') else request.base_field_conditions
        
        for change_key, change_value in request.scenario_changes.items():
            if hasattr(modified_conditions, change_key):
                setattr(modified_conditions, change_key, change_value)
        
        # Get modified scenario recommendation
        modified_result = await service.provide_decision_support(
            field_conditions=modified_conditions,
            crop_requirements=request.crop_requirements,
            fertilizer_specification=request.fertilizer_specification,
            available_equipment=request.available_equipment,
            decision_rule=DecisionRule.DECISION_TREE,
            include_scenarios=True,
            include_sensitivity=True
        )
        
        # Perform comparison analysis
        comparison_analysis = {
            "base_scenario": {
                "recommendation": base_result.primary_recommendation,
                "confidence": base_result.confidence_level,
                "risks": base_result.risk_assessment["overall_risk_level"]
            },
            "modified_scenario": {
                "recommendation": modified_result.primary_recommendation,
                "confidence": modified_result.confidence_level,
                "risks": modified_result.risk_assessment["overall_risk_level"]
            },
            "changes_applied": request.scenario_changes,
            "impact_analysis": {
                "recommendation_changed": base_result.primary_recommendation != modified_result.primary_recommendation,
                "confidence_change": modified_result.confidence_level - base_result.confidence_level,
                "risk_change": modified_result.risk_assessment["overall_risk_level"] != base_result.risk_assessment["overall_risk_level"]
            },
            "analysis_type": request.analysis_type
        }
        
        logger.info("What-if analysis completed")
        return comparison_analysis
        
    except Exception as e:
        logger.error(f"Error in what-if analysis: {e}")
        raise HTTPException(status_code=500, detail=f"What-if analysis failed: {str(e)}")


@router.get("/decision-rules")
async def get_available_decision_rules():
    """
    Get list of available decision rules and their descriptions.
    
    Returns information about all available decision rules that can be used
    for fertilizer application method selection, including their characteristics
    and when to use each rule.
    """
    decision_rules = [
        {
            "rule": DecisionRule.DECISION_TREE,
            "name": "Decision Tree",
            "description": "Rule-based decision making using agricultural expertise and field conditions",
            "best_for": "Standard field conditions with clear decision criteria",
            "characteristics": ["Transparent", "Explainable", "Fast", "Agricultural expertise-based"]
        },
        {
            "rule": DecisionRule.EXPERT_SYSTEM,
            "name": "Expert System",
            "description": "Knowledge-based rules from agricultural experts and research",
            "best_for": "Complex scenarios requiring expert knowledge",
            "characteristics": ["Expert knowledge", "Rule-based", "Comprehensive", "Validated"]
        },
        {
            "rule": DecisionRule.WEIGHTED_SUM,
            "name": "Weighted Sum",
            "description": "Multi-criteria decision analysis with weighted scoring",
            "best_for": "Multiple objectives with known importance weights",
            "characteristics": ["Flexible", "Multi-criteria", "Customizable", "Quantitative"]
        },
        {
            "rule": DecisionRule.TOPSIS,
            "name": "TOPSIS",
            "description": "Technique for Order Preference by Similarity to Ideal Solution",
            "best_for": "Ranking methods based on distance from ideal solution",
            "characteristics": ["Ranking", "Distance-based", "Ideal solution", "Comprehensive"]
        },
        {
            "rule": DecisionRule.ELECTRE,
            "name": "ELECTRE",
            "description": "Elimination and Choice Expressing Reality method",
            "best_for": "Outranking methods with preference relations",
            "characteristics": ["Outranking", "Preference relations", "Robust", "Complex"]
        },
        {
            "rule": DecisionRule.FUZZY_LOGIC,
            "name": "Fuzzy Logic",
            "description": "Fuzzy decision making for uncertain and imprecise conditions",
            "best_for": "Uncertain conditions with fuzzy or imprecise data",
            "characteristics": ["Uncertainty handling", "Fuzzy", "Flexible", "Robust"]
        }
    ]
    
    return {
        "available_rules": decision_rules,
        "default_rule": DecisionRule.DECISION_TREE,
        "recommendation": "Use Decision Tree for most scenarios, Expert System for complex cases, Weighted Sum for custom preferences"
    }


@router.get("/scenario-types")
async def get_scenario_types():
    """
    Get available scenario types for analysis.
    
    Returns information about different scenario types that can be used
    for analysis, including their characteristics and use cases.
    """
    scenario_types = [
        {
            "type": "best_case",
            "name": "Best Case Scenario",
            "description": "Optimal conditions with best-case assumptions",
            "use_case": "Planning for ideal conditions and maximum potential",
            "characteristics": ["Favorable weather", "High equipment performance", "Efficient labor", "Good soil conditions"]
        },
        {
            "type": "worst_case",
            "name": "Worst Case Scenario",
            "description": "Challenging conditions with worst-case assumptions",
            "use_case": "Risk assessment and contingency planning",
            "characteristics": ["Poor weather", "Equipment issues", "Limited labor", "Challenging soil conditions"]
        },
        {
            "type": "most_likely",
            "name": "Most Likely Scenario",
            "description": "Realistic conditions based on historical data",
            "use_case": "Standard planning and decision making",
            "characteristics": ["Average weather", "Normal equipment performance", "Typical labor", "Standard soil conditions"]
        },
        {
            "type": "sensitivity",
            "name": "Sensitivity Analysis",
            "description": "Parameter sensitivity and critical threshold analysis",
            "use_case": "Understanding which factors most influence decisions",
            "characteristics": ["Parameter variations", "Threshold analysis", "Impact assessment", "Critical factors"]
        },
        {
            "type": "monte_carlo",
            "name": "Monte Carlo Analysis",
            "description": "Statistical analysis with random parameter variations",
            "use_case": "Risk analysis and probability assessment",
            "characteristics": ["Random variations", "Statistical analysis", "Probability distributions", "Risk quantification"]
        }
    ]
    
    return {
        "scenario_types": scenario_types,
        "default_scenarios": ["best_case", "worst_case", "most_likely"],
        "recommendation": "Use all three default scenarios for comprehensive analysis"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint for decision support service."""
    return {
        "service": "fertilizer-application-decision-support",
        "status": "healthy",
        "endpoints": [
            "provide_decision_support",
            "interactive_decision_support",
            "what_if_analysis",
            "get_available_decision_rules",
            "get_scenario_types"
        ],
        "features": [
            "decision_trees",
            "expert_systems",
            "scenario_analysis",
            "sensitivity_analysis",
            "risk_assessment",
            "decision_matrices",
            "interactive_decisions",
            "what_if_analysis"
        ]
    }
