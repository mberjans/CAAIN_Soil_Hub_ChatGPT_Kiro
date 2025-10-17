"""
Fertilizer Strategy Optimization API Routes

This module provides comprehensive API endpoints for advanced fertilizer strategy optimization,
including multi-field optimization, ROI analysis, break-even calculations, and price trend analysis.

Author: AI Agent
Date: 2025-01-27
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
import logging
import asyncio

# Import existing services
from services.roi_optimizer import roi_optimizer_service
from services.break_even_analysis_service import BreakEvenAnalysisService
from services.price_tracking_service import FertilizerPriceTrackingService
from services.yield_goal_optimization_service import YieldGoalOptimizationService
from services.environmental_optimization_service import SustainabilityOptimizationService

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1/fertilizer", tags=["strategy-optimization"])

# Initialize services
break_even_service = BreakEvenAnalysisService()
price_tracking_service = FertilizerPriceTrackingService()
yield_goal_service = YieldGoalOptimizationService()
sustainability_service = SustainabilityOptimizationService()

# Pydantic models for strategy optimization
class FieldContext(BaseModel):
    """Individual field context for optimization"""
    field_id: str = Field(..., description="Unique field identifier")
    acres: float = Field(..., gt=0, description="Field size in acres")
    soil_tests: Dict[str, float] = Field(..., description="Soil test results (N, P, K, pH)")
    crop_plan: Dict[str, Any] = Field(..., description="Crop and target yield information")
    
    @validator('soil_tests')
    def validate_soil_tests(cls, v):
        required_keys = ['N', 'P', 'K', 'pH']
        for key in required_keys:
            if key not in v:
                raise ValueError(f"Missing required soil test parameter: {key}")
        return v

class BudgetConstraints(BaseModel):
    """Budget constraints for optimization"""
    total_budget: float = Field(..., gt=0, description="Total available budget")
    max_per_acre: float = Field(..., gt=0, description="Maximum spending per acre")

class FarmContext(BaseModel):
    """Farm context for comprehensive optimization"""
    fields: List[FieldContext] = Field(..., min_items=1, description="List of fields to optimize")
    budget_constraints: BudgetConstraints = Field(..., description="Budget limitations")
    equipment_available: List[str] = Field(default=[], description="Available equipment types")

class OptimizationGoals(BaseModel):
    """Optimization goals and priorities"""
    primary_goal: str = Field(..., description="Primary optimization goal")
    yield_priority: float = Field(default=0.8, ge=0, le=1, description="Yield priority weight")
    cost_priority: float = Field(default=0.7, ge=0, le=1, description="Cost priority weight")
    environmental_priority: float = Field(default=0.6, ge=0, le=1, description="Environmental priority weight")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance level")
    
    @validator('primary_goal')
    def validate_primary_goal(cls, v):
        allowed_goals = ['profit_maximization', 'yield_maximization', 'cost_minimization', 'environmental_optimization']
        if v not in allowed_goals:
            raise ValueError(f"Primary goal must be one of: {allowed_goals}")
        return v

class EnvironmentalLimits(BaseModel):
    """Environmental constraints"""
    max_n_rate: float = Field(default=200, description="Maximum nitrogen rate")
    buffer_zones: bool = Field(default=True, description="Buffer zone requirements")

class TimingConstraints(BaseModel):
    """Timing constraints for applications"""
    planting_date: date = Field(..., description="Planned planting date")
    harvest_date: date = Field(..., description="Expected harvest date")

class Constraints(BaseModel):
    """All optimization constraints"""
    environmental_limits: EnvironmentalLimits = Field(default_factory=EnvironmentalLimits)
    timing_constraints: TimingConstraints = Field(..., description="Timing requirements")
    regulatory_compliance: List[str] = Field(default=[], description="Regulatory requirements")

class StrategyOptimizationRequest(BaseModel):
    """Comprehensive strategy optimization request"""
    farm_context: FarmContext = Field(..., description="Farm context and fields")
    optimization_goals: OptimizationGoals = Field(..., description="Optimization objectives")
    constraints: Constraints = Field(..., description="Optimization constraints")

class OptimizedStrategy(BaseModel):
    """Optimized fertilizer strategy response"""
    strategy_id: str = Field(..., description="Unique strategy identifier")
    total_cost: float = Field(..., description="Total strategy cost")
    expected_roi: float = Field(..., description="Expected return on investment")
    field_strategies: List[Dict[str, Any]] = Field(..., description="Per-field strategies")
    economic_analysis: Dict[str, Any] = Field(..., description="Economic analysis results")
    environmental_impact: Dict[str, Any] = Field(..., description="Environmental impact assessment")
    confidence_score: float = Field(..., ge=0, le=1, description="Strategy confidence score")
    optimization_notes: List[str] = Field(default=[], description="Optimization notes and warnings")


@router.post("/optimize-strategy", response_model=OptimizedStrategy)
async def optimize_fertilizer_strategy(
    request: StrategyOptimizationRequest,
    background_tasks: BackgroundTasks
) -> OptimizedStrategy:
    """
    Comprehensive fertilizer strategy optimization endpoint
    
    Performs multi-field optimization considering:
    - Economic objectives (profit/cost/yield maximization)
    - Environmental constraints and sustainability
    - Budget limitations and equipment constraints
    - Timing and regulatory requirements
    
    Returns optimized strategy with detailed analysis and recommendations.
    Performance target: <5s for complex multi-field scenarios
    """
    try:
        logger.info(f"Starting strategy optimization for {len(request.farm_context.fields)} fields")
        
        # Generate unique strategy ID
        import uuid
        strategy_id = str(uuid.uuid4())
        
        # Initialize optimization results
        total_cost = 0.0
        field_strategies = []
        optimization_notes = []
        
        # Process each field
        for field in request.farm_context.fields:
            logger.info(f"Optimizing field {field.field_id}")
            
            try:
                # Perform field-specific optimization
                field_strategy = await optimize_single_field(
                    field=field,
                    goals=request.optimization_goals,
                    constraints=request.constraints,
                    budget_per_acre=request.farm_context.budget_constraints.max_per_acre
                )
                
                field_strategies.append(field_strategy)
                total_cost += field_strategy.get('total_cost', 0.0)
                
            except Exception as field_error:
                logger.error(f"Error optimizing field {field.field_id}: {field_error}")
                optimization_notes.append(f"Field {field.field_id}: {str(field_error)}")
                
                # Create fallback strategy
                fallback_strategy = create_fallback_strategy(field)
                field_strategies.append(fallback_strategy)
                total_cost += fallback_strategy.get('total_cost', 0.0)
        
        # Check budget constraints
        if total_cost > request.farm_context.budget_constraints.total_budget:
            optimization_notes.append("Total cost exceeds budget - applying cost reduction")
            field_strategies, total_cost = apply_budget_constraints(
                field_strategies, 
                request.farm_context.budget_constraints.total_budget
            )
        
        # Calculate ROI using existing service
        try:
            roi_analysis = await calculate_strategy_roi(field_strategies, request.optimization_goals)
            expected_roi = roi_analysis.get('expected_roi', 0.0)
        except Exception as roi_error:
            logger.warning(f"ROI calculation failed: {roi_error}")
            expected_roi = 0.0
            optimization_notes.append("ROI calculation unavailable")
        
        # Environmental impact assessment
        try:
            environmental_impact = await assess_environmental_impact(
                field_strategies, 
                request.constraints.environmental_limits
            )
        except Exception as env_error:
            logger.warning(f"Environmental assessment failed: {env_error}")
            environmental_impact = {"status": "assessment_failed", "error": str(env_error)}
        
        # Economic analysis
        economic_analysis = {
            "total_investment": total_cost,
            "expected_return": total_cost * (1 + expected_roi),
            "break_even_yield": calculate_break_even_yield(field_strategies),
            "payback_period": calculate_payback_period(expected_roi),
            "risk_assessment": assess_strategy_risk(field_strategies, request.optimization_goals.risk_tolerance)
        }
        
        # Calculate confidence score
        confidence_score = calculate_confidence_score(
            field_strategies, 
            len(optimization_notes),
            environmental_impact
        )
        
        # Background task for strategy tracking
        background_tasks.add_task(
            log_optimization_result,
            strategy_id,
            request.dict(),
            total_cost,
            expected_roi
        )
        
        logger.info(f"Strategy optimization completed: ID={strategy_id}, Cost=${total_cost:.2f}, ROI={expected_roi:.2%}")
        
        return OptimizedStrategy(
            strategy_id=strategy_id,
            total_cost=total_cost,
            expected_roi=expected_roi,
            field_strategies=field_strategies,
            economic_analysis=economic_analysis,
            environmental_impact=environmental_impact,
            confidence_score=confidence_score,
            optimization_notes=optimization_notes
        )
        
    except Exception as e:
        logger.error(f"Strategy optimization failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Strategy optimization failed: {str(e)}"
        )


# Helper functions for strategy optimization
async def optimize_single_field(
    field: FieldContext,
    goals: OptimizationGoals,
    constraints: Constraints,
    budget_per_acre: float
) -> Dict[str, Any]:
    """Optimize fertilizer strategy for a single field"""
    try:
        # Extract field parameters
        soil_tests = field.soil_tests
        crop_info = field.crop_plan
        acres = field.acres
        
        # Use existing yield goal optimization service
        yield_optimization = await yield_goal_service.optimize_fertilizer_strategy({
            "field_id": field.field_id,
            "acres": acres,
            "current_soil_levels": soil_tests,
            "target_crop": crop_info.get("crop", "corn"),
            "target_yield": crop_info.get("target_yield", 150),
            "budget_constraint": budget_per_acre * acres,
            "optimization_goal": goals.primary_goal
        })
        
        # Use ROI optimizer for economic analysis
        roi_analysis = await roi_optimizer_service.optimize_fertilizer_roi({
            "field_acres": acres,
            "soil_test_results": soil_tests,
            "target_yield": crop_info.get("target_yield", 150),
            "crop_type": crop_info.get("crop", "corn"),
            "budget_limit": budget_per_acre * acres
        })
        
        # Environmental optimization using sustainability service
        env_optimization = await sustainability_service.optimize_environmental_impact({
            "field_size": acres,
            "soil_conditions": soil_tests,
            "crop_type": crop_info.get("crop", "corn"),
            "environmental_priorities": {
                "nutrient_efficiency": goals.environmental_priority,
                "soil_health": 0.8,
                "water_protection": 0.9
            }
        })
        
        # Combine optimization results
        field_strategy = {
            "field_id": field.field_id,
            "acres": acres,
            "recommended_rates": yield_optimization.get("recommended_rates", {}),
            "application_methods": yield_optimization.get("application_methods", []),
            "timing_schedule": yield_optimization.get("timing_schedule", []),
            "total_cost": roi_analysis.get("total_cost", budget_per_acre * acres * 0.8),
            "expected_yield": yield_optimization.get("expected_yield", crop_info.get("target_yield", 150)),
            "roi_projection": roi_analysis.get("roi_percentage", 0.15),
            "environmental_score": env_optimization.get("environmental_score", 0.7),
            "confidence_level": min(
                yield_optimization.get("confidence", 0.8),
                roi_analysis.get("confidence", 0.8),
                env_optimization.get("confidence", 0.8)
            )
        }
        
        return field_strategy
        
    except Exception as e:
        logger.error(f"Single field optimization failed: {e}")
        # Return basic fallback strategy
        return create_fallback_strategy(field)


def create_fallback_strategy(field: FieldContext) -> Dict[str, Any]:
    """Create a basic fallback strategy when optimization fails"""
    crop_type = field.crop_plan.get("crop", "corn")
    target_yield = field.crop_plan.get("target_yield", 150)
    
    # Basic N-P-K recommendations based on common practices
    basic_rates = {
        "corn": {"N": 1.2, "P": 0.5, "K": 0.8},  # lbs per bushel
        "soybean": {"N": 0.0, "P": 0.8, "K": 1.0},
        "wheat": {"N": 2.0, "P": 0.6, "K": 0.5}
    }
    
    rates = basic_rates.get(crop_type, basic_rates["corn"])
    
    return {
        "field_id": field.field_id,
        "acres": field.acres,
        "recommended_rates": {
            "N": target_yield * rates["N"],
            "P": target_yield * rates["P"], 
            "K": target_yield * rates["K"]
        },
        "application_methods": ["broadcast"],
        "timing_schedule": ["pre_plant"],
        "total_cost": field.acres * 120,  # $120/acre average
        "expected_yield": target_yield * 0.9,  # Conservative estimate
        "roi_projection": 0.10,  # Conservative ROI
        "environmental_score": 0.6,
        "confidence_level": 0.5,  # Low confidence for fallback
        "notes": ["Fallback strategy - optimization service unavailable"]
    }


def apply_budget_constraints(
    field_strategies: List[Dict[str, Any]], 
    total_budget: float
) -> tuple[List[Dict[str, Any]], float]:
    """Apply budget constraints by proportionally reducing costs"""
    current_total = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
    
    if current_total <= total_budget:
        return field_strategies, current_total
    
    # Calculate reduction factor
    reduction_factor = total_budget / current_total
    
    # Apply reduction to each field
    adjusted_strategies = []
    adjusted_total = 0.0
    
    for strategy in field_strategies:
        adjusted_strategy = strategy.copy()
        original_cost = strategy.get('total_cost', 0)
        adjusted_cost = original_cost * reduction_factor
        
        adjusted_strategy['total_cost'] = adjusted_cost
        adjusted_strategy['budget_adjusted'] = True
        adjusted_strategy['reduction_factor'] = reduction_factor
        
        # Adjust rates proportionally
        if 'recommended_rates' in adjusted_strategy:
            for nutrient, rate in adjusted_strategy['recommended_rates'].items():
                adjusted_strategy['recommended_rates'][nutrient] = rate * reduction_factor
        
        adjusted_strategies.append(adjusted_strategy)
        adjusted_total += adjusted_cost
    
    return adjusted_strategies, adjusted_total


async def calculate_strategy_roi(
    field_strategies: List[Dict[str, Any]], 
    goals: OptimizationGoals
) -> Dict[str, Any]:
    """Calculate overall strategy ROI"""
    total_investment = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
    total_expected_return = 0.0
    
    for strategy in field_strategies:
        field_roi = strategy.get('roi_projection', 0.0)
        field_investment = strategy.get('total_cost', 0)
        total_expected_return += field_investment * field_roi
    
    overall_roi = total_expected_return / total_investment if total_investment > 0 else 0.0
    
    return {
        "expected_roi": overall_roi,
        "total_investment": total_investment,
        "total_expected_return": total_expected_return,
        "risk_adjusted_roi": overall_roi * (1.0 - get_risk_factor(goals.risk_tolerance))
    }


def get_risk_factor(risk_tolerance: str) -> float:
    """Get risk adjustment factor based on tolerance level"""
    risk_factors = {
        "low": 0.3,
        "moderate": 0.15,
        "high": 0.05
    }
    return risk_factors.get(risk_tolerance, 0.15)


async def assess_environmental_impact(
    field_strategies: List[Dict[str, Any]], 
    env_limits: EnvironmentalLimits
) -> Dict[str, Any]:
    """Assess environmental impact of strategy"""
    total_n_applied = 0.0
    total_acres = 0.0
    env_scores = []
    
    for strategy in field_strategies:
        acres = strategy.get('acres', 0)
        rates = strategy.get('recommended_rates', {})
        n_rate = rates.get('N', 0)
        
        total_n_applied += n_rate * acres
        total_acres += acres
        env_scores.append(strategy.get('environmental_score', 0.5))
    
    avg_n_rate = total_n_applied / total_acres if total_acres > 0 else 0
    avg_env_score = sum(env_scores) / len(env_scores) if env_scores else 0.5
    
    # Check environmental compliance
    n_compliance = avg_n_rate <= env_limits.max_n_rate
    
    return {
        "average_n_rate": avg_n_rate,
        "n_rate_compliance": n_compliance,
        "environmental_score": avg_env_score,
        "sustainability_rating": "high" if avg_env_score > 0.8 else "medium" if avg_env_score > 0.6 else "low",
        "total_acres": total_acres,
        "buffer_zones_required": env_limits.buffer_zones
    }


def calculate_break_even_yield(field_strategies: List[Dict[str, Any]]) -> float:
    """Calculate break-even yield across all fields"""
    total_cost = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
    total_acres = sum(strategy.get('acres', 0) for strategy in field_strategies)
    
    # Assume average crop price of $4.50/bushel
    avg_price = 4.50
    
    return (total_cost / total_acres) / avg_price if total_acres > 0 else 0


def calculate_payback_period(roi: float) -> float:
    """Calculate payback period in years"""
    return 1.0 / roi if roi > 0 else float('inf')


def assess_strategy_risk(
    field_strategies: List[Dict[str, Any]], 
    risk_tolerance: str
) -> Dict[str, Any]:
    """Assess overall strategy risk"""
    confidence_levels = [strategy.get('confidence_level', 0.5) for strategy in field_strategies]
    avg_confidence = sum(confidence_levels) / len(confidence_levels) if confidence_levels else 0.5
    
    risk_level = "low" if avg_confidence > 0.8 else "medium" if avg_confidence > 0.6 else "high"
    
    return {
        "risk_level": risk_level,
        "confidence_score": avg_confidence,
        "risk_tolerance": risk_tolerance,
        "risk_factors": [
            "Weather variability",
            "Price volatility", 
            "Yield uncertainty"
        ]
    }


def calculate_confidence_score(
    field_strategies: List[Dict[str, Any]], 
    num_warnings: int,
    environmental_impact: Dict[str, Any]
) -> float:
    """Calculate overall confidence score for the strategy"""
    # Base confidence from field strategies
    field_confidences = [strategy.get('confidence_level', 0.5) for strategy in field_strategies]
    base_confidence = sum(field_confidences) / len(field_confidences) if field_confidences else 0.5
    
    # Reduce confidence for warnings
    warning_penalty = min(num_warnings * 0.1, 0.3)
    
    # Environmental compliance bonus
    env_bonus = 0.1 if environmental_impact.get('n_rate_compliance', False) else 0
    
    final_confidence = max(0.0, min(1.0, base_confidence - warning_penalty + env_bonus))
    
    return final_confidence


async def log_optimization_result(
    strategy_id: str,
    request_data: Dict[str, Any],
    total_cost: float,
    expected_roi: float
) -> None:
    """Background task to log optimization results"""
    try:
        logger.info(f"Logging optimization result: {strategy_id}")
        # Here you would typically save to database
        # For now, just log the key metrics
        logger.info(f"Strategy {strategy_id}: Cost=${total_cost:.2f}, ROI={expected_roi:.2%}")
    except Exception as e:
        logger.error(f"Failed to log optimization result: {e}")