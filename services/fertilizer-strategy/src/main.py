from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from api.price_routes import router as price_router
from api.commodity_price_routes import router as commodity_router
from api.price_impact_routes import router as price_impact_router
from api.roi_routes import router as roi_router
from api.budget_constraint_routes import router as budget_constraint_router
from api.break_even_routes import router as break_even_router
from api.yield_goal_routes import router as yield_goal_router
from api.yield_response_routes import router as yield_response_router
from api.yield_goal_optimization_routes import router as yield_goal_optimization_router
from api.nutrient_optimization_routes import router as nutrient_optimization_router
from api.timing_optimization_routes import router as timing_optimization_router
from api.timing_routes import router as timing_routes_router
from api.application_method_optimization_routes import router as application_method_optimization_router
from api.price_adjustment_routes import router as price_adjustment_router
from api.price_scenario_routes import router as price_scenario_router
from api.price_optimization_alert_routes import router as price_optimization_alert_router
from api.environmental_routes import router as environmental_router
from api.environmental_optimization_routes import router as sustainability_router
from api.strategy_routes import router as strategy_router
from api.strategy_management_routes import router as strategy_management_router
from api.mobile_strategy_tracking_routes import router as mobile_strategy_router
from api.comparison_routes import router as comparison_router
from database.fertilizer_price_db import initialize_database, shutdown_database
from database.commodity_price_db import initialize_commodity_database, shutdown_commodity_database
from services.scheduled_price_updater import start_scheduled_updates, stop_scheduled_updates

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown tasks."""
    # Startup
    logger.info("Starting AFAS Fertilizer Strategy Optimization Service...")
    
    try:
        # Initialize database connections
        await initialize_database()
        await initialize_commodity_database()
        logger.info("Database connections initialized")
        
        # Start scheduled price updates
        await start_scheduled_updates()
        logger.info("Scheduled price updates started")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down AFAS Fertilizer Strategy Optimization Service...")
        
        # Stop scheduled updates
        await stop_scheduled_updates()
        logger.info("Scheduled price updates stopped")
        
        # Shutdown database
        await shutdown_database()
        await shutdown_commodity_database()
        logger.info("Database connections closed")


app = FastAPI(
    title="AFAS Fertilizer Strategy Optimization Service",
    description="Comprehensive fertilizer price tracking, market analysis, and strategy optimization service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(price_router, prefix="/api/v1", tags=["fertilizer-prices"])
app.include_router(commodity_router, prefix="/api/v1", tags=["commodity-prices"])
app.include_router(price_impact_router, prefix="/api/v1", tags=["price-impact-analysis"])
app.include_router(roi_router, prefix="/api/v1", tags=["roi-optimization"])
app.include_router(budget_constraint_router, prefix="/api/v1", tags=["budget-constraint-optimization"])
app.include_router(break_even_router, prefix="/api/v1", tags=["break-even-analysis"])
app.include_router(yield_goal_router, prefix="/api/v1", tags=["yield-goal-management"])
app.include_router(yield_response_router, prefix="/api/v1", tags=["yield-response-curves"])
app.include_router(yield_goal_optimization_router, prefix="/api/v1", tags=["yield-goal-optimization"])
app.include_router(nutrient_optimization_router, prefix="/api/v1", tags=["nutrient-optimization"])
app.include_router(timing_optimization_router, prefix="/api/v1", tags=["timing-optimization"])
app.include_router(timing_routes_router, tags=["timing-routes"])
app.include_router(application_method_optimization_router, prefix="/api/v1", tags=["application-method-optimization"])
app.include_router(price_adjustment_router, prefix="/api/v1", tags=["price-adjustment"])
app.include_router(price_scenario_router, prefix="/api/v1", tags=["price-scenario-modeling"])
app.include_router(price_optimization_alert_router, prefix="/api/v1", tags=["price-optimization-alerts"])
app.include_router(environmental_router, prefix="/api/v1", tags=["regulatory-compliance"])
app.include_router(sustainability_router, prefix="/api/v1", tags=["sustainability-optimization"])
app.include_router(strategy_router, prefix="/api/v1", tags=["strategy-optimization"])
app.include_router(strategy_management_router, prefix="/api/v1", tags=["strategy-management"])
app.include_router(mobile_strategy_router, prefix="/api/v1", tags=["mobile-strategy-tracking"])
app.include_router(comparison_router, tags=["fertilizer-comparison"])

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "service": "fertilizer-strategy-optimization",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "real_time_price_tracking",
            "historical_price_analysis",
            "price_volatility_tracking",
            "regional_price_variations",
            "fertilizer_type_tracking",
            "market_intelligence",
            "price_trend_analysis",
            "commodity_price_integration",
            "economic_optimization",
            "strategy_recommendations",
            "commodity_price_tracking",
            "futures_market_integration",
            "basis_analysis",
            "fertilizer_crop_price_ratios",
            "advanced_price_impact_analysis",
            "sensitivity_analysis",
            "scenario_modeling",
            "risk_assessment",
            "profitability_impact_analysis",
            "advanced_timing_optimization",
            "weather_integrated_timing",
            "crop_growth_stage_optimization",
            "split_application_planning",
            "equipment_constraint_optimization",
            "labor_availability_integration",
            "soil_condition_timing",
            "risk_based_timing_strategies",
            "fertilizer_roi_optimization",
            "multi_objective_optimization",
            "break_even_analysis",
            "comprehensive_break_even_analysis",
            "monte_carlo_simulation",
            "scenario_analysis",
            "sensitivity_analysis",
            "stochastic_modeling",
            "risk_assessment",
            "marginal_return_analysis",
            "yield_response_curves",
            "constraint_handling",
            "genetic_algorithm_optimization",
            "linear_programming_optimization",
            "quadratic_programming_optimization",
            "gradient_descent_optimization",
            "budget_constraint_optimization",
            "multi_objective_optimization",
            "pareto_frontier_analysis",
            "budget_allocation_optimization",
            "constraint_relaxation_analysis",
            "trade_off_analysis",
            "field_priority_optimization",
            "nutrient_allocation_optimization",
            "scenario_comparison",
            "efficiency_frontier_analysis",
            "comprehensive_yield_goal_analysis",
            "historical_yield_trend_analysis",
            "potential_yield_assessment",
            "multi_factor_yield_modeling",
            "yield_goal_recommendations",
            "risk_based_goal_setting",
            "achievement_probability_calculation",
            "goal_validation_and_comparison",
            "soil_weather_management_integration",
            "crop_specific_yield_baselines",
            "limiting_factors_identification",
            "improvement_opportunities_assessment",
            "mitigation_strategy_recommendations",
            "sophisticated_yield_fertilizer_response_curves",
            "advanced_curve_fitting",
            "nutrient_response_curves",
            "interaction_effects",
            "diminishing_returns_modeling",
            "mitscherlich_baule_models",
            "quadratic_plateau_models",
            "linear_plateau_models",
            "exponential_models",
            "optimal_rate_calculations",
            "confidence_intervals",
            "economic_thresholds",
            "model_validation",
            "response_curve_comparison",
            "university_research_integration",
            "field_trial_results",
            "farmer_data_integration",
            "comprehensive_yield_goal_optimization",
            "goal_oriented_fertilizer_planning",
            "economic_constraint_optimization",
            "risk_adjusted_optimization",
            "scenario_analysis_optimization",
            "multi_criteria_optimization",
            "goal_programming_optimization",
            "robust_optimization",
            "stochastic_optimization",
            "genetic_algorithm_optimization",
            "optimal_fertilizer_strategies",
            "goal_achievement_probability",
            "economic_analysis_integration",
            "sensitivity_analysis",
            "comprehensive_scenario_modeling",
            "application_method_optimization",
            "method_selection_optimization",
            "efficiency_optimization",
            "cost_benefit_analysis",
            "environmental_impact_assessment",
            "multi_objective_optimization",
            "constraint_handling",
            "method_comparison",
            "equipment_compatibility",
            "soil_condition_analysis",
            "fertilizer_form_optimization",
            "dynamic_price_adjustment",
            "real_time_price_monitoring",
            "automatic_strategy_adjustments",
            "threshold_based_alerts",
            "economic_impact_assessment",
            "automated_approval_workflows",
            "price_volatility_monitoring",
            "market_shock_detection",
            "trend_reversal_alerts",
            "conservative_adjustment_strategies",
            "aggressive_adjustment_strategies",
            "balanced_adjustment_strategies",
            "comprehensive_price_scenario_modeling",
            "monte_carlo_simulation",
            "stochastic_modeling",
            "sensitivity_analysis",
            "decision_trees",
            "risk_assessment",
            "bull_market_scenarios",
            "bear_market_scenarios",
            "volatile_market_scenarios",
            "seasonal_pattern_scenarios",
            "supply_disruption_scenarios",
            "custom_scenario_modeling",
            "probability_distribution_modeling",
            "geometric_brownian_motion",
            "price_forecasting",
            "scenario_planning",
            "intelligent_price_optimization_alerts",
            "ml_based_alert_optimization",
            "personalized_alert_thresholds",
            "predictive_price_alerts",
            "multi_channel_alert_delivery",
            "false_positive_reduction",
            "alert_performance_optimization",
            "pattern_recognition_alerts",
            "opportunity_detection_alerts",
            "risk_assessment_alerts",
            "timing_optimization_alerts",
            "volatility_monitoring_alerts",
            "trend_reversal_alerts",
            "market_shock_detection_alerts",
            "regulatory_compliance_assessment",
            "environmental_impact_analysis",
            "sustainability_metrics_calculation",
            "automated_violation_detection",
            "compliance_reporting",
            "regulatory_rule_management",
            "violation_tracking",
            "risk_assessment",
            "recommendation_generation",
            "historical_compliance_analysis",
            "statistical_reporting",
            "advanced_sustainability_optimization",
            "multi_objective_optimization",
            "carbon_footprint_tracking",
            "trade_off_analysis",
            "scenario_comparison",
            "genetic_algorithm_optimization",
            "gradient_descent_optimization",
            "environmental_compliance_optimization",
            "sustainability_certification_support",
            "comprehensive_fertilizer_comparison",
            "multi_criteria_decision_analysis",
            "weighted_scoring_comparison",
            "topsis_analysis",
            "ahp_analysis",
            "trade_off_analysis",
            "fertilizer_ranking",
            "cost_effectiveness_scoring",
            "environmental_impact_scoring",
            "nutrient_value_assessment",
            "application_convenience_scoring"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Fertilizer Strategy Optimization Service is running",
        "service": "fertilizer-strategy-optimization",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("FERTILIZER_STRATEGY_PORT", 8009))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)
