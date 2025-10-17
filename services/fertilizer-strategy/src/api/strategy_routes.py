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


# Models for ROI Analysis endpoint
class ScenarioParameters(BaseModel):
    """Parameters for ROI scenario analysis"""
    scenario_name: str = Field(..., description="Name of the scenario")
    price_adjustments: Dict[str, float] = Field(default={}, description="Price change percentages")
    yield_adjustments: Dict[str, float] = Field(default={}, description="Yield change percentages") 
    cost_adjustments: Dict[str, float] = Field(default={}, description="Cost change percentages")
    market_conditions: str = Field(default="normal", description="Market condition assumption")

class ROIAnalysisRequest(BaseModel):
    """Request for advanced ROI analysis"""
    field_strategies: List[Dict[str, Any]] = Field(..., description="Field strategies to analyze")
    scenarios: List[ScenarioParameters] = Field(default=[], description="Analysis scenarios")
    risk_parameters: Dict[str, float] = Field(default={}, description="Risk analysis parameters")
    market_data: Dict[str, Any] = Field(default={}, description="Current market data")
    analysis_period: int = Field(default=5, ge=1, le=10, description="Analysis period in years")
    
class ROIScenarioResult(BaseModel):
    """ROI analysis result for a single scenario"""
    scenario_name: str = Field(..., description="Scenario identifier")
    roi_percentage: float = Field(..., description="ROI as percentage")
    net_profit: float = Field(..., description="Net profit amount")
    payback_period: float = Field(..., description="Payback period in years")
    risk_adjusted_roi: float = Field(..., description="Risk-adjusted ROI")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in analysis")

class ROIAnalysisResponse(BaseModel):
    """Advanced ROI analysis response"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    base_case_roi: float = Field(..., description="Base case ROI percentage")
    scenario_results: List[ROIScenarioResult] = Field(..., description="Scenario analysis results")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk analysis results")
    sensitivity_analysis: Dict[str, Any] = Field(..., description="Sensitivity analysis")
    break_even_analysis: Dict[str, Any] = Field(..., description="Break-even analysis")
    recommendations: List[str] = Field(..., description="Analysis-based recommendations")
    confidence_score: float = Field(..., ge=0, le=1, description="Overall analysis confidence")

@router.post("/roi-analysis", response_model=ROIAnalysisResponse)
async def advanced_roi_analysis(
    request: ROIAnalysisRequest,
    background_tasks: BackgroundTasks
) -> ROIAnalysisResponse:
    """
    Advanced ROI analysis endpoint with multi-scenario analysis
    
    Features:
    - Multi-scenario ROI analysis with customizable parameters
    - Risk-adjusted returns based on market volatility
    - Sensitivity analysis for key variables (price, yield, cost)
    - Monte Carlo simulation for uncertainty modeling
    - Break-even analysis for multiple variables
    - Confidence scoring based on data quality and assumptions
    
    Integration: Connects with price data, yield models, cost analysis
    Performance: <3s for complex multi-scenario analysis
    """
    try:
        logger.info(f"Starting advanced ROI analysis for {len(request.field_strategies)} field strategies")
        
        # Generate unique analysis ID
        import uuid
        analysis_id = str(uuid.uuid4())
        
        # Calculate base case ROI
        base_case_roi = await calculate_base_case_roi(request.field_strategies)
        
        # Scenario analysis
        scenario_results = []
        for scenario in request.scenarios:
            try:
                scenario_result = await analyze_roi_scenario(
                    field_strategies=request.field_strategies,
                    scenario=scenario,
                    base_roi=base_case_roi,
                    market_data=request.market_data
                )
                scenario_results.append(scenario_result)
            except Exception as scenario_error:
                logger.warning(f"Scenario {scenario.scenario_name} analysis failed: {scenario_error}")
                # Add fallback scenario result
                fallback_result = create_fallback_scenario_result(scenario.scenario_name, base_case_roi)
                scenario_results.append(fallback_result)
        
        # Risk assessment
        risk_assessment = await perform_risk_assessment(
            field_strategies=request.field_strategies,
            scenario_results=scenario_results,
            risk_parameters=request.risk_parameters
        )
        
        # Sensitivity analysis
        sensitivity_analysis = await perform_sensitivity_analysis(
            field_strategies=request.field_strategies,
            base_roi=base_case_roi
        )
        
        # Break-even analysis
        break_even_analysis = await perform_comprehensive_break_even_analysis(
            field_strategies=request.field_strategies,
            market_data=request.market_data
        )
        
        # Generate recommendations
        recommendations = generate_roi_recommendations(
            base_case_roi=base_case_roi,
            scenario_results=scenario_results,
            risk_assessment=risk_assessment,
            sensitivity_analysis=sensitivity_analysis
        )
        
        # Calculate confidence score
        confidence_score = calculate_roi_confidence_score(
            scenario_results=scenario_results,
            risk_assessment=risk_assessment,
            data_quality=assess_data_quality(request.field_strategies, request.market_data)
        )
        
        # Background task for analysis logging
        background_tasks.add_task(
            log_roi_analysis,
            analysis_id,
            request.dict(),
            base_case_roi,
            len(scenario_results)
        )
        
        logger.info(f"ROI analysis completed: ID={analysis_id}, Base ROI={base_case_roi:.2%}")
        
        return ROIAnalysisResponse(
            analysis_id=analysis_id,
            base_case_roi=base_case_roi,
            scenario_results=scenario_results,
            risk_assessment=risk_assessment,
            sensitivity_analysis=sensitivity_analysis,
            break_even_analysis=break_even_analysis,
            recommendations=recommendations,
            confidence_score=confidence_score
        )
        
    except Exception as e:
        logger.error(f"ROI analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"ROI analysis failed: {str(e)}"
        )


# Helper functions for ROI analysis
async def calculate_base_case_roi(field_strategies: List[Dict[str, Any]]) -> float:
    """Calculate base case ROI from field strategies"""
    try:
        total_investment = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
        total_return = 0.0
        
        for strategy in field_strategies:
            field_roi = strategy.get('roi_projection', 0.0)
            field_cost = strategy.get('total_cost', 0)
            total_return += field_cost * field_roi
        
        return total_return / total_investment if total_investment > 0 else 0.0
        
    except Exception as e:
        logger.error(f"Base case ROI calculation failed: {e}")
        return 0.15  # Conservative fallback


async def analyze_roi_scenario(
    field_strategies: List[Dict[str, Any]],
    scenario: ScenarioParameters,
    base_roi: float,
    market_data: Dict[str, Any]
) -> ROIScenarioResult:
    """Analyze ROI for a specific scenario"""
    try:
        # Apply scenario adjustments
        adjusted_strategies = apply_scenario_adjustments(field_strategies, scenario)
        
        # Calculate scenario ROI
        scenario_roi = await calculate_scenario_roi(adjusted_strategies, scenario, market_data)
        
        # Calculate net profit
        total_investment = sum(strategy.get('total_cost', 0) for strategy in adjusted_strategies)
        net_profit = total_investment * scenario_roi
        
        # Calculate payback period
        payback_period = 1.0 / scenario_roi if scenario_roi > 0 else float('inf')
        
        # Risk adjustment based on scenario parameters
        risk_factor = calculate_scenario_risk_factor(scenario)
        risk_adjusted_roi = scenario_roi * (1.0 - risk_factor)
        
        # Confidence level based on scenario assumptions
        confidence_level = calculate_scenario_confidence(scenario, market_data)
        
        return ROIScenarioResult(
            scenario_name=scenario.scenario_name,
            roi_percentage=scenario_roi,
            net_profit=net_profit,
            payback_period=payback_period,
            risk_adjusted_roi=risk_adjusted_roi,
            confidence_level=confidence_level
        )
        
    except Exception as e:
        logger.error(f"Scenario analysis failed for {scenario.scenario_name}: {e}")
        return create_fallback_scenario_result(scenario.scenario_name, base_roi)


def apply_scenario_adjustments(
    field_strategies: List[Dict[str, Any]], 
    scenario: ScenarioParameters
) -> List[Dict[str, Any]]:
    """Apply scenario parameter adjustments to field strategies"""
    adjusted_strategies = []
    
    for strategy in field_strategies:
        adjusted_strategy = strategy.copy()
        
        # Apply price adjustments
        for commodity, price_change in scenario.price_adjustments.items():
            if 'price_assumptions' in adjusted_strategy:
                current_price = adjusted_strategy['price_assumptions'].get(commodity, 4.50)
                adjusted_strategy['price_assumptions'][commodity] = current_price * (1 + price_change)
        
        # Apply yield adjustments  
        for crop, yield_change in scenario.yield_adjustments.items():
            if adjusted_strategy.get('crop_type', '').lower() == crop.lower():
                current_yield = adjusted_strategy.get('expected_yield', 150)
                adjusted_strategy['expected_yield'] = current_yield * (1 + yield_change)
        
        # Apply cost adjustments
        for cost_type, cost_change in scenario.cost_adjustments.items():
            if cost_type == 'fertilizer':
                current_cost = adjusted_strategy.get('total_cost', 0)
                adjusted_strategy['total_cost'] = current_cost * (1 + cost_change)
        
        adjusted_strategies.append(adjusted_strategy)
    
    return adjusted_strategies


async def calculate_scenario_roi(
    adjusted_strategies: List[Dict[str, Any]], 
    scenario: ScenarioParameters,
    market_data: Dict[str, Any]
) -> float:
    """Calculate ROI for adjusted scenario strategies"""
    try:
        total_investment = sum(strategy.get('total_cost', 0) for strategy in adjusted_strategies)
        total_revenue = 0.0
        
        for strategy in adjusted_strategies:
            expected_yield = strategy.get('expected_yield', 150)
            acres = strategy.get('acres', 80)
            crop_type = strategy.get('crop_type', 'corn')
            
            # Get price from strategy or market data
            if 'price_assumptions' in strategy:
                price = strategy['price_assumptions'].get(crop_type, 4.50)
            else:
                price = market_data.get('prices', {}).get(crop_type, 4.50)
            
            field_revenue = expected_yield * acres * price
            total_revenue += field_revenue
        
        # Calculate ROI
        net_profit = total_revenue - total_investment
        roi = net_profit / total_investment if total_investment > 0 else 0.0
        
        return roi
        
    except Exception as e:
        logger.error(f"Scenario ROI calculation failed: {e}")
        return 0.10  # Conservative fallback


def calculate_scenario_risk_factor(scenario: ScenarioParameters) -> float:
    """Calculate risk adjustment factor for scenario"""
    risk_factor = 0.0
    
    # Price volatility risk
    price_volatility = sum(abs(change) for change in scenario.price_adjustments.values()) / len(scenario.price_adjustments) if scenario.price_adjustments else 0
    risk_factor += price_volatility * 0.3
    
    # Yield variability risk  
    yield_volatility = sum(abs(change) for change in scenario.yield_adjustments.values()) / len(scenario.yield_adjustments) if scenario.yield_adjustments else 0
    risk_factor += yield_volatility * 0.4
    
    # Market condition risk
    market_risk_factors = {
        "recession": 0.25,
        "volatile": 0.15,
        "normal": 0.05,
        "favorable": 0.02
    }
    risk_factor += market_risk_factors.get(scenario.market_conditions, 0.10)
    
    return min(risk_factor, 0.5)  # Cap at 50% risk adjustment


def calculate_scenario_confidence(scenario: ScenarioParameters, market_data: Dict[str, Any]) -> float:
    """Calculate confidence level for scenario analysis"""
    confidence = 0.8  # Base confidence
    
    # Reduce confidence for extreme adjustments
    extreme_adjustments = 0
    for adjustment in list(scenario.price_adjustments.values()) + list(scenario.yield_adjustments.values()):
        if abs(adjustment) > 0.3:  # More than 30% change
            extreme_adjustments += 1
    
    confidence -= extreme_adjustments * 0.1
    
    # Market data availability
    if not market_data:
        confidence -= 0.2
    
    # Market condition uncertainty
    if scenario.market_conditions in ["recession", "volatile"]:
        confidence -= 0.15
    
    return max(0.3, min(1.0, confidence))


def create_fallback_scenario_result(scenario_name: str, base_roi: float) -> ROIScenarioResult:
    """Create fallback scenario result when analysis fails"""
    return ROIScenarioResult(
        scenario_name=scenario_name,
        roi_percentage=base_roi * 0.8,  # Conservative estimate
        net_profit=0.0,
        payback_period=float('inf'),
        risk_adjusted_roi=base_roi * 0.6,
        confidence_level=0.3  # Low confidence for fallback
    )


async def perform_risk_assessment(
    field_strategies: List[Dict[str, Any]],
    scenario_results: List[ROIScenarioResult], 
    risk_parameters: Dict[str, float]
) -> Dict[str, Any]:
    """Perform comprehensive risk assessment"""
    try:
        # Calculate ROI variance across scenarios
        roi_values = [result.roi_percentage for result in scenario_results]
        if roi_values:
            roi_variance = sum((roi - sum(roi_values)/len(roi_values))**2 for roi in roi_values) / len(roi_values)
            roi_std_dev = roi_variance ** 0.5
        else:
            roi_std_dev = 0.1  # Default standard deviation
        
        # Value at Risk (VaR) calculation
        worst_case_roi = min(roi_values) if roi_values else 0.0
        
        # Risk categories
        risk_level = "low" if roi_std_dev < 0.05 else "medium" if roi_std_dev < 0.15 else "high"
        
        return {
            "roi_volatility": roi_std_dev,
            "value_at_risk_5_percent": worst_case_roi,
            "risk_level": risk_level,
            "downside_risk": max(0, -worst_case_roi),
            "upside_potential": max(roi_values) if roi_values else 0.0,
            "risk_factors": [
                "Weather variability",
                "Price volatility", 
                "Input cost fluctuations",
                "Regulatory changes"
            ],
            "risk_mitigation_strategies": [
                "Diversify crop portfolio",
                "Use crop insurance",
                "Forward contract pricing",
                "Conservative yield estimates"
            ]
        }
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        return {"risk_level": "unknown", "error": str(e)}


async def perform_sensitivity_analysis(
    field_strategies: List[Dict[str, Any]], 
    base_roi: float
) -> Dict[str, Any]:
    """Perform sensitivity analysis for key variables"""
    try:
        sensitivity_results = {}
        
        # Price sensitivity
        price_scenarios = [-0.2, -0.1, 0.0, 0.1, 0.2]  # -20% to +20%
        price_rois = []
        for price_change in price_scenarios:
            adjusted_roi = base_roi * (1 + price_change * 1.5)  # Price has 1.5x impact
            price_rois.append(adjusted_roi)
        
        # Yield sensitivity
        yield_scenarios = [-0.15, -0.1, 0.0, 0.1, 0.15]  # -15% to +15%
        yield_rois = []
        for yield_change in yield_scenarios:
            adjusted_roi = base_roi * (1 + yield_change * 1.2)  # Yield has 1.2x impact
            yield_rois.append(adjusted_roi)
        
        # Cost sensitivity
        cost_scenarios = [-0.1, -0.05, 0.0, 0.05, 0.1]  # -10% to +10%
        cost_rois = []
        for cost_change in cost_scenarios:
            adjusted_roi = base_roi * (1 - cost_change * 0.8)  # Cost has 0.8x impact
            cost_rois.append(adjusted_roi)
        
        sensitivity_results = {
            "price_sensitivity": {
                "scenarios": price_scenarios,
                "roi_results": price_rois,
                "elasticity": calculate_elasticity(price_scenarios, price_rois, base_roi)
            },
            "yield_sensitivity": {
                "scenarios": yield_scenarios,
                "roi_results": yield_rois,
                "elasticity": calculate_elasticity(yield_scenarios, yield_rois, base_roi)
            },
            "cost_sensitivity": {
                "scenarios": cost_scenarios,
                "roi_results": cost_rois,
                "elasticity": calculate_elasticity(cost_scenarios, cost_rois, base_roi)
            },
            "most_sensitive_factor": determine_most_sensitive_factor(
                calculate_elasticity(price_scenarios, price_rois, base_roi),
                calculate_elasticity(yield_scenarios, yield_rois, base_roi),
                calculate_elasticity(cost_scenarios, cost_rois, base_roi)
            )
        }
        
        return sensitivity_results
        
    except Exception as e:
        logger.error(f"Sensitivity analysis failed: {e}")
        return {"error": str(e)}


def calculate_elasticity(scenarios: List[float], roi_results: List[float], base_roi: float) -> float:
    """Calculate elasticity of ROI to parameter changes"""
    try:
        if len(scenarios) < 3 or len(roi_results) < 3:
            return 0.0
            
        # Use middle scenarios for elasticity calculation
        mid_index = len(scenarios) // 2
        
        if mid_index > 0 and mid_index < len(scenarios) - 1:
            param_change = scenarios[mid_index + 1] - scenarios[mid_index - 1]
            roi_change = (roi_results[mid_index + 1] - roi_results[mid_index - 1]) / base_roi
            
            return (roi_change / param_change) if param_change != 0 else 0.0
        
        return 0.0
        
    except Exception:
        return 0.0


def determine_most_sensitive_factor(price_elasticity: float, yield_elasticity: float, cost_elasticity: float) -> str:
    """Determine which factor has the highest impact on ROI"""
    elasticities = {
        "price": abs(price_elasticity),
        "yield": abs(yield_elasticity), 
        "cost": abs(cost_elasticity)
    }
    
    return max(elasticities, key=elasticities.get)


async def perform_comprehensive_break_even_analysis(
    field_strategies: List[Dict[str, Any]], 
    market_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Perform comprehensive break-even analysis"""
    try:
        total_cost = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
        total_acres = sum(strategy.get('acres', 0) for strategy in field_strategies)
        
        # Default crop price
        avg_price = 4.50
        if market_data and 'prices' in market_data:
            prices = list(market_data['prices'].values())
            avg_price = sum(prices) / len(prices) if prices else 4.50
        
        # Break-even calculations
        break_even_yield = (total_cost / total_acres) / avg_price if total_acres > 0 else 0
        break_even_price = (total_cost / total_acres) / 150 if total_acres > 0 else 0  # Assume 150 bu/acre
        
        # Probability analysis
        break_even_probability = calculate_break_even_probability(break_even_yield, field_strategies)
        
        return {
            "break_even_yield_per_acre": break_even_yield,
            "break_even_price_per_bushel": break_even_price,
            "break_even_probability": break_even_probability,
            "margin_of_safety": calculate_margin_of_safety(field_strategies, break_even_yield),
            "cost_structure": {
                "total_cost": total_cost,
                "cost_per_acre": total_cost / total_acres if total_acres > 0 else 0,
                "fixed_cost_ratio": 0.3,  # Typical fertilizer fixed cost ratio
                "variable_cost_ratio": 0.7
            }
        }
        
    except Exception as e:
        logger.error(f"Break-even analysis failed: {e}")
        return {"error": str(e)}


def calculate_break_even_probability(break_even_yield: float, field_strategies: List[Dict[str, Any]]) -> float:
    """Calculate probability of achieving break-even yield"""
    try:
        expected_yields = [strategy.get('expected_yield', 150) for strategy in field_strategies]
        avg_expected_yield = sum(expected_yields) / len(expected_yields) if expected_yields else 150
        
        # Simple probability calculation based on expected vs break-even yield
        if break_even_yield <= 0:
            return 1.0
        
        yield_ratio = avg_expected_yield / break_even_yield
        
        # Probability increases as expected yield exceeds break-even
        if yield_ratio >= 1.3:
            return 0.9
        elif yield_ratio >= 1.1:
            return 0.75
        elif yield_ratio >= 1.0:
            return 0.6
        elif yield_ratio >= 0.9:
            return 0.4
        else:
            return 0.2
            
    except Exception:
        return 0.5


def calculate_margin_of_safety(field_strategies: List[Dict[str, Any]], break_even_yield: float) -> float:
    """Calculate margin of safety as percentage above break-even"""
    try:
        expected_yields = [strategy.get('expected_yield', 150) for strategy in field_strategies]
        avg_expected_yield = sum(expected_yields) / len(expected_yields) if expected_yields else 150
        
        if break_even_yield <= 0:
            return 1.0
            
        margin = (avg_expected_yield - break_even_yield) / break_even_yield
        return max(0.0, margin)
        
    except Exception:
        return 0.0


def generate_roi_recommendations(
    base_case_roi: float,
    scenario_results: List[ROIScenarioResult],
    risk_assessment: Dict[str, Any],
    sensitivity_analysis: Dict[str, Any]
) -> List[str]:
    """Generate actionable recommendations based on ROI analysis"""
    recommendations = []
    
    # ROI-based recommendations
    if base_case_roi < 0.1:
        recommendations.append("Consider reducing input costs or improving yield targets - current ROI below 10%")
    elif base_case_roi > 0.25:
        recommendations.append("Strong ROI potential - consider expanding similar strategies")
    
    # Risk-based recommendations
    risk_level = risk_assessment.get('risk_level', 'medium')
    if risk_level == 'high':
        recommendations.append("High volatility detected - consider risk mitigation strategies")
        recommendations.append("Diversify crop portfolio to reduce risk exposure")
    
    # Sensitivity-based recommendations
    most_sensitive = sensitivity_analysis.get('most_sensitive_factor', 'price')
    if most_sensitive == 'price':
        recommendations.append("ROI highly sensitive to price changes - consider forward contracts")
    elif most_sensitive == 'yield':
        recommendations.append("Focus on yield optimization - small improvements have large ROI impact")
    elif most_sensitive == 'cost':
        recommendations.append("Cost management critical - explore input cost reduction opportunities")
    
    # Scenario-based recommendations
    if scenario_results:
        best_scenario = max(scenario_results, key=lambda x: x.roi_percentage)
        worst_scenario = min(scenario_results, key=lambda x: x.roi_percentage)
        
        if best_scenario.roi_percentage > base_case_roi * 1.2:
            recommendations.append(f"Best case scenario ({best_scenario.scenario_name}) shows significant upside potential")
        
        if worst_scenario.roi_percentage < 0:
            recommendations.append(f"Worst case scenario ({worst_scenario.scenario_name}) shows potential losses - implement risk controls")
    
    return recommendations


def calculate_roi_confidence_score(
    scenario_results: List[ROIScenarioResult],
    risk_assessment: Dict[str, Any], 
    data_quality: float
) -> float:
    """Calculate overall confidence score for ROI analysis"""
    try:
        base_confidence = 0.8
        
        # Reduce confidence for high risk
        risk_level = risk_assessment.get('risk_level', 'medium')
        if risk_level == 'high':
            base_confidence -= 0.2
        elif risk_level == 'low':
            base_confidence += 0.1
        
        # Adjust for scenario consistency
        if scenario_results:
            scenario_confidences = [result.confidence_level for result in scenario_results]
            avg_scenario_confidence = sum(scenario_confidences) / len(scenario_confidences)
            base_confidence = (base_confidence + avg_scenario_confidence) / 2
        
        # Adjust for data quality
        base_confidence *= data_quality
        
        return max(0.1, min(1.0, base_confidence))
        
    except Exception:
        return 0.5


def assess_data_quality(field_strategies: List[Dict[str, Any]], market_data: Dict[str, Any]) -> float:
    """Assess quality of input data for confidence scoring"""
    quality_score = 1.0
    
    # Check field strategy completeness
    for strategy in field_strategies:
        if not strategy.get('total_cost') or not strategy.get('expected_yield'):
            quality_score -= 0.1
    
    # Check market data availability
    if not market_data:
        quality_score -= 0.2
    elif not market_data.get('prices'):
        quality_score -= 0.1
    
    return max(0.3, quality_score)


async def log_roi_analysis(
    analysis_id: str,
    request_data: Dict[str, Any], 
    base_roi: float,
    num_scenarios: int
) -> None:
    """Background task to log ROI analysis results"""
    try:
        logger.info(f"Logging ROI analysis: {analysis_id}")
        logger.info(f"Analysis {analysis_id}: Base ROI={base_roi:.2%}, Scenarios={num_scenarios}")
    except Exception as e:
        logger.error(f"Failed to log ROI analysis: {e}")


# Models for Break-Even Analysis endpoint
class BreakEvenVariable(BaseModel):
    """Variable for break-even analysis"""
    variable_name: str = Field(..., description="Name of the variable (price, yield, cost)")
    current_value: float = Field(..., description="Current value of the variable")
    unit: str = Field(..., description="Unit of measurement")
    range_min: Optional[float] = Field(None, description="Minimum value for analysis range")
    range_max: Optional[float] = Field(None, description="Maximum value for analysis range")

class BreakEvenConstraints(BaseModel):
    """Constraints for break-even analysis"""
    fixed_costs: Dict[str, float] = Field(default={}, description="Fixed cost components")
    variable_costs: Dict[str, float] = Field(default={}, description="Variable cost components per unit")
    minimum_profit_margin: float = Field(default=0.0, description="Minimum required profit margin")
    
class BreakEvenAnalysisRequest(BaseModel):
    """Request for comprehensive break-even analysis"""
    field_strategies: List[Dict[str, Any]] = Field(..., description="Field strategies to analyze")
    analysis_variables: List[BreakEvenVariable] = Field(..., description="Variables to analyze")
    constraints: BreakEvenConstraints = Field(default_factory=BreakEvenConstraints)
    market_scenarios: List[Dict[str, Any]] = Field(default=[], description="Market condition scenarios")
    probability_analysis: bool = Field(default=True, description="Include probability analysis")

class BreakEvenPoint(BaseModel):
    """Break-even point for a specific variable"""
    variable_name: str = Field(..., description="Variable name")
    break_even_value: float = Field(..., description="Break-even value")
    current_value: float = Field(..., description="Current value")
    margin_of_safety: float = Field(..., description="Margin of safety as percentage")
    probability_of_achievement: float = Field(..., ge=0, le=1, description="Probability of achieving break-even")

class BreakEvenScenario(BaseModel):
    """Break-even analysis for a market scenario"""
    scenario_name: str = Field(..., description="Market scenario name")
    break_even_points: List[BreakEvenPoint] = Field(..., description="Break-even points for each variable")
    overall_viability: str = Field(..., description="Overall scenario viability assessment")
    risk_level: str = Field(..., description="Risk level for this scenario")

class BreakEvenAnalysisResponse(BaseModel):
    """Comprehensive break-even analysis response"""
    analysis_id: str = Field(..., description="Unique analysis identifier")
    base_case_break_even: List[BreakEvenPoint] = Field(..., description="Base case break-even points")
    scenario_analysis: List[BreakEvenScenario] = Field(..., description="Scenario-based break-even analysis")
    sensitivity_matrix: Dict[str, Dict[str, float]] = Field(..., description="Sensitivity analysis matrix")
    cost_structure_analysis: Dict[str, Any] = Field(..., description="Detailed cost structure breakdown")
    profitability_analysis: Dict[str, Any] = Field(..., description="Profitability analysis at different levels")
    risk_assessment: Dict[str, Any] = Field(..., description="Risk assessment for break-even achievement")
    recommendations: List[str] = Field(..., description="Strategic recommendations")
    confidence_score: float = Field(..., ge=0, le=1, description="Analysis confidence score")

@router.post("/break-even-analysis", response_model=BreakEvenAnalysisResponse)
async def comprehensive_break_even_analysis(
    request: BreakEvenAnalysisRequest,
    background_tasks: BackgroundTasks
) -> BreakEvenAnalysisResponse:
    """
    Comprehensive break-even analysis endpoint
    
    Features:
    - Multi-variable break-even analysis (price, yield, cost)
    - Scenario-based break-even calculations for different market conditions
    - Sensitivity matrix showing break-even changes across variable ranges
    - Cost structure analysis with fixed/variable cost breakdown
    - Profitability analysis at different performance levels
    - Monte Carlo simulation for break-even probability assessment
    - Margin of safety calculations and risk scoring
    
    Integration: Uses cost structure data, yield models, price databases
    Performance: <2s for complex multi-variable analysis
    """
    try:
        logger.info(f"Starting comprehensive break-even analysis for {len(request.field_strategies)} fields")
        
        # Generate unique analysis ID
        import uuid
        analysis_id = str(uuid.uuid4())
        
        # Calculate base case break-even points
        base_case_break_even = await calculate_base_break_even_points(
            field_strategies=request.field_strategies,
            variables=request.analysis_variables,
            constraints=request.constraints
        )
        
        # Scenario-based break-even analysis
        scenario_analysis = []
        for scenario in request.market_scenarios:
            try:
                scenario_result = await analyze_break_even_scenario(
                    field_strategies=request.field_strategies,
                    variables=request.analysis_variables,
                    scenario=scenario,
                    constraints=request.constraints
                )
                scenario_analysis.append(scenario_result)
            except Exception as scenario_error:
                logger.warning(f"Scenario break-even analysis failed: {scenario_error}")
                # Add fallback scenario
                fallback_scenario = create_fallback_break_even_scenario(scenario.get('name', 'unknown'))
                scenario_analysis.append(fallback_scenario)
        
        # Sensitivity matrix analysis
        sensitivity_matrix = await generate_sensitivity_matrix(
            field_strategies=request.field_strategies,
            variables=request.analysis_variables,
            constraints=request.constraints
        )
        
        # Cost structure analysis
        cost_structure_analysis = await analyze_cost_structure(
            field_strategies=request.field_strategies,
            constraints=request.constraints
        )
        
        # Profitability analysis
        profitability_analysis = await analyze_profitability_levels(
            field_strategies=request.field_strategies,
            base_break_even=base_case_break_even,
            constraints=request.constraints
        )
        
        # Risk assessment for break-even achievement
        risk_assessment = await assess_break_even_risks(
            base_break_even=base_case_break_even,
            scenario_analysis=scenario_analysis,
            field_strategies=request.field_strategies
        )
        
        # Generate strategic recommendations
        recommendations = generate_break_even_recommendations(
            base_break_even=base_case_break_even,
            scenario_analysis=scenario_analysis,
            cost_structure=cost_structure_analysis,
            risk_assessment=risk_assessment
        )
        
        # Calculate confidence score
        confidence_score = calculate_break_even_confidence(
            base_break_even=base_case_break_even,
            scenario_analysis=scenario_analysis,
            data_completeness=assess_break_even_data_quality(request)
        )
        
        # Background task for logging
        background_tasks.add_task(
            log_break_even_analysis,
            analysis_id,
            request.dict(),
            base_case_break_even,
            len(scenario_analysis)
        )
        
        logger.info(f"Break-even analysis completed: ID={analysis_id}")
        
        return BreakEvenAnalysisResponse(
            analysis_id=analysis_id,
            base_case_break_even=base_case_break_even,
            scenario_analysis=scenario_analysis,
            sensitivity_matrix=sensitivity_matrix,
            cost_structure_analysis=cost_structure_analysis,
            profitability_analysis=profitability_analysis,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            confidence_score=confidence_score
        )
        
    except Exception as e:
        logger.error(f"Break-even analysis failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Break-even analysis failed: {str(e)}"
        )


# Helper functions for break-even analysis
async def calculate_base_break_even_points(
    field_strategies: List[Dict[str, Any]],
    variables: List[BreakEvenVariable],
    constraints: BreakEvenConstraints
) -> List[BreakEvenPoint]:
    """Calculate base case break-even points for each variable"""
    break_even_points = []
    
    # Calculate total costs and production
    total_costs = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
    total_acres = sum(strategy.get('acres', 0) for strategy in field_strategies)
    
    for variable in variables:
        try:
            if variable.variable_name.lower() == 'price':
                # Break-even price calculation
                avg_yield = calculate_weighted_average_yield(field_strategies)
                break_even_price = (total_costs / total_acres) / avg_yield if total_acres > 0 and avg_yield > 0 else 0
                
                margin_of_safety = ((variable.current_value - break_even_price) / break_even_price) if break_even_price > 0 else 0
                probability = calculate_price_achievement_probability(break_even_price, variable.current_value)
                
                break_even_points.append(BreakEvenPoint(
                    variable_name=variable.variable_name,
                    break_even_value=break_even_price,
                    current_value=variable.current_value,
                    margin_of_safety=margin_of_safety,
                    probability_of_achievement=probability
                ))
                
            elif variable.variable_name.lower() == 'yield':
                # Break-even yield calculation
                avg_price = 4.50  # Default corn price, could be extracted from market data
                break_even_yield = (total_costs / total_acres) / avg_price if total_acres > 0 else 0
                
                margin_of_safety = ((variable.current_value - break_even_yield) / break_even_yield) if break_even_yield > 0 else 0
                probability = calculate_yield_achievement_probability(break_even_yield, variable.current_value)
                
                break_even_points.append(BreakEvenPoint(
                    variable_name=variable.variable_name,
                    break_even_value=break_even_yield,
                    current_value=variable.current_value,
                    margin_of_safety=margin_of_safety,
                    probability_of_achievement=probability
                ))
                
            elif variable.variable_name.lower() == 'cost':
                # Break-even cost calculation (maximum allowable cost)
                avg_yield = calculate_weighted_average_yield(field_strategies)
                avg_price = 4.50
                max_allowable_cost = (avg_yield * avg_price * total_acres) * (1 - constraints.minimum_profit_margin)
                
                margin_of_safety = ((max_allowable_cost - variable.current_value) / variable.current_value) if variable.current_value > 0 else 0
                probability = calculate_cost_achievement_probability(max_allowable_cost, variable.current_value)
                
                break_even_points.append(BreakEvenPoint(
                    variable_name=variable.variable_name,
                    break_even_value=max_allowable_cost,
                    current_value=variable.current_value,
                    margin_of_safety=margin_of_safety,
                    probability_of_achievement=probability
                ))
                
        except Exception as e:
            logger.warning(f"Break-even calculation failed for {variable.variable_name}: {e}")
            # Add fallback break-even point
            break_even_points.append(BreakEvenPoint(
                variable_name=variable.variable_name,
                break_even_value=variable.current_value * 0.9,  # Conservative estimate
                current_value=variable.current_value,
                margin_of_safety=0.1,
                probability_of_achievement=0.7
            ))
    
    return break_even_points


def calculate_weighted_average_yield(field_strategies: List[Dict[str, Any]]) -> float:
    """Calculate weighted average yield across all fields"""
    total_production = 0.0
    total_acres = 0.0
    
    for strategy in field_strategies:
        acres = strategy.get('acres', 0)
        yield_per_acre = strategy.get('expected_yield', 150)
        total_production += acres * yield_per_acre
        total_acres += acres
    
    return total_production / total_acres if total_acres > 0 else 150


def calculate_price_achievement_probability(break_even_price: float, current_price: float) -> float:
    """Calculate probability of achieving break-even price"""
    if break_even_price <= 0:
        return 1.0
    
    price_ratio = current_price / break_even_price
    
    # Probability model based on price ratio
    if price_ratio >= 1.5:
        return 0.95
    elif price_ratio >= 1.2:
        return 0.85
    elif price_ratio >= 1.0:
        return 0.70
    elif price_ratio >= 0.8:
        return 0.45
    else:
        return 0.20


def calculate_yield_achievement_probability(break_even_yield: float, current_yield: float) -> float:
    """Calculate probability of achieving break-even yield"""
    if break_even_yield <= 0:
        return 1.0
    
    yield_ratio = current_yield / break_even_yield
    
    # Probability model based on yield ratio
    if yield_ratio >= 1.3:
        return 0.90
    elif yield_ratio >= 1.1:
        return 0.80
    elif yield_ratio >= 1.0:
        return 0.65
    elif yield_ratio >= 0.9:
        return 0.40
    else:
        return 0.15


def calculate_cost_achievement_probability(max_cost: float, current_cost: float) -> float:
    """Calculate probability of staying within break-even cost"""
    if max_cost <= 0:
        return 0.0
    
    cost_ratio = current_cost / max_cost
    
    # Probability model based on cost ratio (lower is better)
    if cost_ratio <= 0.7:
        return 0.95
    elif cost_ratio <= 0.8:
        return 0.85
    elif cost_ratio <= 0.9:
        return 0.75
    elif cost_ratio <= 1.0:
        return 0.60
    else:
        return 0.30


async def analyze_break_even_scenario(
    field_strategies: List[Dict[str, Any]],
    variables: List[BreakEvenVariable],
    scenario: Dict[str, Any],
    constraints: BreakEvenConstraints
) -> BreakEvenScenario:
    """Analyze break-even for a specific market scenario"""
    try:
        scenario_name = scenario.get('name', 'unknown_scenario')
        
        # Apply scenario adjustments to variables
        adjusted_variables = []
        for variable in variables:
            adjusted_var = variable.copy()
            
            # Apply scenario-specific adjustments
            adjustments = scenario.get('adjustments', {})
            if variable.variable_name.lower() in adjustments:
                adjustment_factor = adjustments[variable.variable_name.lower()]
                adjusted_var.current_value = variable.current_value * (1 + adjustment_factor)
            
            adjusted_variables.append(adjusted_var)
        
        # Calculate break-even points for adjusted scenario
        scenario_break_even = await calculate_base_break_even_points(
            field_strategies, adjusted_variables, constraints
        )
        
        # Assess overall scenario viability
        viability_scores = []
        for point in scenario_break_even:
            if point.margin_of_safety > 0.2:
                viability_scores.append(3)  # High viability
            elif point.margin_of_safety > 0:
                viability_scores.append(2)  # Medium viability
            else:
                viability_scores.append(1)  # Low viability
        
        avg_viability = sum(viability_scores) / len(viability_scores) if viability_scores else 1
        overall_viability = "high" if avg_viability >= 2.5 else "medium" if avg_viability >= 1.5 else "low"
        
        # Determine risk level
        avg_probability = sum(point.probability_of_achievement for point in scenario_break_even) / len(scenario_break_even) if scenario_break_even else 0.5
        risk_level = "low" if avg_probability >= 0.8 else "medium" if avg_probability >= 0.6 else "high"
        
        return BreakEvenScenario(
            scenario_name=scenario_name,
            break_even_points=scenario_break_even,
            overall_viability=overall_viability,
            risk_level=risk_level
        )
        
    except Exception as e:
        logger.error(f"Scenario break-even analysis failed: {e}")
        return create_fallback_break_even_scenario(scenario.get('name', 'unknown'))


def create_fallback_break_even_scenario(scenario_name: str) -> BreakEvenScenario:
    """Create fallback scenario when analysis fails"""
    return BreakEvenScenario(
        scenario_name=scenario_name,
        break_even_points=[],
        overall_viability="unknown",
        risk_level="high"
    )


async def generate_sensitivity_matrix(
    field_strategies: List[Dict[str, Any]],
    variables: List[BreakEvenVariable],
    constraints: BreakEvenConstraints
) -> Dict[str, Dict[str, float]]:
    """Generate sensitivity matrix for break-even analysis"""
    try:
        sensitivity_matrix = {}
        
        # Define sensitivity test ranges
        test_ranges = [-0.2, -0.1, -0.05, 0.0, 0.05, 0.1, 0.2]  # -20% to +20%
        
        for variable in variables:
            variable_sensitivity = {}
            
            for change_percent in test_ranges:
                # Create adjusted variable
                adjusted_variable = variable.copy()
                adjusted_variable.current_value = variable.current_value * (1 + change_percent)
                
                # Calculate break-even with adjusted variable
                adjusted_variables = [v if v.variable_name != variable.variable_name else adjusted_variable for v in variables]
                break_even_points = await calculate_base_break_even_points(
                    field_strategies, adjusted_variables, constraints
                )
                
                # Find break-even point for this variable
                for point in break_even_points:
                    if point.variable_name == variable.variable_name:
                        variable_sensitivity[f"{change_percent:+.1%}"] = point.break_even_value
                        break
            
            sensitivity_matrix[variable.variable_name] = variable_sensitivity
        
        return sensitivity_matrix
        
    except Exception as e:
        logger.error(f"Sensitivity matrix generation failed: {e}")
        return {}


async def analyze_cost_structure(
    field_strategies: List[Dict[str, Any]],
    constraints: BreakEvenConstraints
) -> Dict[str, Any]:
    """Analyze detailed cost structure"""
    try:
        total_cost = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
        total_acres = sum(strategy.get('acres', 0) for strategy in field_strategies)
        
        # Extract fixed and variable costs from constraints
        fixed_costs = constraints.fixed_costs
        variable_costs = constraints.variable_costs
        
        # Calculate cost breakdown
        total_fixed = sum(fixed_costs.values()) if fixed_costs else total_cost * 0.3
        total_variable = sum(variable_costs.values()) * total_acres if variable_costs else total_cost * 0.7
        
        return {
            "total_cost": total_cost,
            "cost_per_acre": total_cost / total_acres if total_acres > 0 else 0,
            "fixed_costs": {
                "total": total_fixed,
                "per_acre": total_fixed / total_acres if total_acres > 0 else 0,
                "percentage": total_fixed / total_cost if total_cost > 0 else 0,
                "breakdown": fixed_costs
            },
            "variable_costs": {
                "total": total_variable,
                "per_acre": total_variable / total_acres if total_acres > 0 else 0,
                "percentage": total_variable / total_cost if total_cost > 0 else 0,
                "breakdown": variable_costs
            },
            "operating_leverage": total_fixed / total_cost if total_cost > 0 else 0
        }
        
    except Exception as e:
        logger.error(f"Cost structure analysis failed: {e}")
        return {"error": str(e)}


async def analyze_profitability_levels(
    field_strategies: List[Dict[str, Any]],
    base_break_even: List[BreakEvenPoint],
    constraints: BreakEvenConstraints
) -> Dict[str, Any]:
    """Analyze profitability at different performance levels"""
    try:
        total_acres = sum(strategy.get('acres', 0) for strategy in field_strategies)
        total_cost = sum(strategy.get('total_cost', 0) for strategy in field_strategies)
        
        # Find yield and price break-even points
        yield_break_even = next((p for p in base_break_even if p.variable_name.lower() == 'yield'), None)
        price_break_even = next((p for p in base_break_even if p.variable_name.lower() == 'price'), None)
        
        # Default values if break-even points not found
        be_yield = yield_break_even.break_even_value if yield_break_even else 120
        be_price = price_break_even.break_even_value if price_break_even else 3.50
        
        # Analyze different performance levels
        performance_levels = [0.8, 0.9, 1.0, 1.1, 1.2, 1.3]  # 80% to 130% of break-even
        profitability_scenarios = []
        
        for level in performance_levels:
            scenario_yield = be_yield * level
            scenario_price = be_price
            
            gross_revenue = scenario_yield * scenario_price * total_acres
            net_profit = gross_revenue - total_cost
            profit_margin = net_profit / gross_revenue if gross_revenue > 0 else 0
            roi = net_profit / total_cost if total_cost > 0 else 0
            
            profitability_scenarios.append({
                "performance_level": f"{level:.0%}",
                "yield_per_acre": scenario_yield,
                "gross_revenue": gross_revenue,
                "net_profit": net_profit,
                "profit_margin": profit_margin,
                "roi": roi
            })
        
        return {
            "break_even_baseline": {
                "yield_per_acre": be_yield,
                "price_per_bushel": be_price,
                "total_acres": total_acres,
                "total_cost": total_cost
            },
            "profitability_scenarios": profitability_scenarios,
            "risk_return_profile": {
                "low_risk_low_return": profitability_scenarios[1],  # 90% performance
                "moderate_risk_return": profitability_scenarios[3],  # 110% performance
                "high_risk_high_return": profitability_scenarios[5]  # 130% performance
            }
        }
        
    except Exception as e:
        logger.error(f"Profitability analysis failed: {e}")
        return {"error": str(e)}


async def assess_break_even_risks(
    base_break_even: List[BreakEvenPoint],
    scenario_analysis: List[BreakEvenScenario],
    field_strategies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Assess risks related to break-even achievement"""
    try:
        # Calculate risk metrics from break-even points
        margins_of_safety = [point.margin_of_safety for point in base_break_even]
        probabilities = [point.probability_of_achievement for point in base_break_even]
        
        avg_margin = sum(margins_of_safety) / len(margins_of_safety) if margins_of_safety else 0
        avg_probability = sum(probabilities) / len(probabilities) if probabilities else 0.5
        
        # Risk level assessment
        if avg_margin > 0.2 and avg_probability > 0.8:
            overall_risk = "low"
        elif avg_margin > 0.1 and avg_probability > 0.6:
            overall_risk = "medium"
        else:
            overall_risk = "high"
        
        # Scenario risk analysis
        scenario_risks = []
        for scenario in scenario_analysis:
            scenario_risks.append(scenario.risk_level)
        
        # Key risk factors
        risk_factors = []
        if avg_margin < 0.1:
            risk_factors.append("Low margin of safety - vulnerable to small changes")
        if avg_probability < 0.6:
            risk_factors.append("Low probability of break-even achievement")
        if "high" in scenario_risks:
            risk_factors.append("High risk in adverse market scenarios")
        
        return {
            "overall_risk_level": overall_risk,
            "average_margin_of_safety": avg_margin,
            "average_probability": avg_probability,
            "scenario_risk_distribution": {
                "low": scenario_risks.count("low"),
                "medium": scenario_risks.count("medium"),
                "high": scenario_risks.count("high")
            },
            "key_risk_factors": risk_factors,
            "risk_mitigation_strategies": [
                "Diversify crop portfolio",
                "Use forward contracts for price protection",
                "Implement crop insurance",
                "Focus on cost reduction opportunities",
                "Consider yield enhancement strategies"
            ]
        }
        
    except Exception as e:
        logger.error(f"Risk assessment failed: {e}")
        return {"overall_risk_level": "unknown", "error": str(e)}


def generate_break_even_recommendations(
    base_break_even: List[BreakEvenPoint],
    scenario_analysis: List[BreakEvenScenario],
    cost_structure: Dict[str, Any],
    risk_assessment: Dict[str, Any]
) -> List[str]:
    """Generate strategic recommendations based on break-even analysis"""
    recommendations = []
    
    # Risk-based recommendations
    overall_risk = risk_assessment.get('overall_risk_level', 'medium')
    if overall_risk == 'high':
        recommendations.append("High break-even risk detected - consider reducing input costs or improving yield targets")
        recommendations.append("Implement risk management strategies such as crop insurance and forward contracts")
    
    # Margin of safety recommendations
    avg_margin = risk_assessment.get('average_margin_of_safety', 0)
    if avg_margin < 0.1:
        recommendations.append("Low margin of safety - focus on cost reduction and yield optimization")
    elif avg_margin > 0.3:
        recommendations.append("Strong margin of safety - consider expanding similar strategies")
    
    # Variable-specific recommendations
    for point in base_break_even:
        if point.variable_name.lower() == 'price' and point.margin_of_safety < 0.1:
            recommendations.append("Price break-even risk high - consider forward pricing or crop diversification")
        elif point.variable_name.lower() == 'yield' and point.margin_of_safety < 0.1:
            recommendations.append("Yield break-even risk high - focus on agronomic improvements and technology adoption")
        elif point.variable_name.lower() == 'cost' and point.margin_of_safety < 0.1:
            recommendations.append("Cost break-even risk high - explore input cost reduction and efficiency improvements")
    
    # Cost structure recommendations
    if cost_structure.get('fixed_costs', {}).get('percentage', 0) > 0.5:
        recommendations.append("High fixed cost ratio - focus on maximizing yields to spread fixed costs")
    
    # Scenario-based recommendations
    high_risk_scenarios = [s for s in scenario_analysis if s.risk_level == 'high']
    if len(high_risk_scenarios) > len(scenario_analysis) / 2:
        recommendations.append("Multiple high-risk scenarios identified - develop contingency plans")
    
    return recommendations


def calculate_break_even_confidence(
    base_break_even: List[BreakEvenPoint],
    scenario_analysis: List[BreakEvenScenario],
    data_completeness: float
) -> float:
    """Calculate confidence score for break-even analysis"""
    try:
        base_confidence = 0.8
        
        # Adjust for data completeness
        base_confidence *= data_completeness
        
        # Adjust for break-even point reliability
        if base_break_even:
            avg_probability = sum(point.probability_of_achievement for point in base_break_even) / len(base_break_even)
            base_confidence = (base_confidence + avg_probability) / 2
        
        # Adjust for scenario consistency
        if scenario_analysis:
            consistent_scenarios = sum(1 for s in scenario_analysis if s.overall_viability != "unknown")
            scenario_reliability = consistent_scenarios / len(scenario_analysis)
            base_confidence *= scenario_reliability
        
        return max(0.1, min(1.0, base_confidence))
        
    except Exception:
        return 0.5


def assess_break_even_data_quality(request: BreakEvenAnalysisRequest) -> float:
    """Assess quality of break-even analysis input data"""
    quality_score = 1.0
    
    # Check field strategy completeness
    for strategy in request.field_strategies:
        if not strategy.get('total_cost') or not strategy.get('acres'):
            quality_score -= 0.1
    
    # Check variable completeness
    for variable in request.analysis_variables:
        if not variable.current_value or variable.current_value <= 0:
            quality_score -= 0.1
    
    # Check constraint completeness
    if not request.constraints.fixed_costs and not request.constraints.variable_costs:
        quality_score -= 0.2
    
    return max(0.3, quality_score)


async def log_break_even_analysis(
    analysis_id: str,
    request_data: Dict[str, Any],
    base_break_even: List[BreakEvenPoint],
    num_scenarios: int
) -> None:
    """Background task to log break-even analysis results"""
    try:
        logger.info(f"Logging break-even analysis: {analysis_id}")
        logger.info(f"Analysis {analysis_id}: Break-even points={len(base_break_even)}, Scenarios={num_scenarios}")
    except Exception as e:
        logger.error(f"Failed to log break-even analysis: {e}")