from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from src.api.application_routes import router as application_router
from src.api.method_routes import router as method_router
from src.api.guidance_routes import router as guidance_router
from src.api.equipment_routes import router as equipment_router
from src.api.efficiency_routes import router as efficiency_router
from src.api.monitoring_routes import router as monitoring_router
from src.api.real_time_monitoring_routes import router as real_time_monitoring_router
from src.api.iot_sensor_routes import router as iot_sensor_router
from src.api.crop_response_routes import router as crop_response_router
from src.api.crop_integration_routes import router as crop_integration_router
from src.api.decision_support_routes import router as decision_support_router
from src.api.economic_optimization_routes import router as economic_optimization_router
from src.api.validation_routes import router as validation_router
from src.api.fertilizer_routes import router as fertilizer_router
from src.api.advanced_application_routes import router as advanced_application_router
from src.api.integration_routes import router as integration_router
from src.api.analytics_routes import router as analytics_router
from src.api.priority_constraint_routes import router as priority_constraint_router
from src.api.goal_based_routes import router as goal_based_router
from src.api.adaptive_learning_routes import router as adaptive_learning_router
from src.api.advanced_labor_analysis_routes import router as advanced_labor_analysis_router
from src.database.fertilizer_db import initialize_database, shutdown_database

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
    logger.info("Starting AFAS Fertilizer Application Service...")
    
    try:
        # Initialize database connections
        await initialize_database()
        logger.info("Database connections initialized")
        
        yield
        
    finally:
        # Shutdown
        logger.info("Shutting down AFAS Fertilizer Application Service...")
        await shutdown_database()
        logger.info("Database connections closed")


app = FastAPI(
    title="AFAS Fertilizer Application Service",
    description="Comprehensive fertilizer application method selection, equipment assessment, and guidance service",
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
app.include_router(application_router, prefix="/api/v1", tags=["application"])
app.include_router(method_router, prefix="/api/v1", tags=["methods"])
app.include_router(guidance_router, prefix="/api/v1", tags=["guidance"])
app.include_router(equipment_router, prefix="/api/v1", tags=["equipment-assessment"])
app.include_router(efficiency_router, prefix="/api/v1", tags=["equipment-efficiency"])
app.include_router(monitoring_router, prefix="/api/v1", tags=["performance-monitoring"])
app.include_router(real_time_monitoring_router, prefix="/api/v1", tags=["real-time-monitoring"])
app.include_router(iot_sensor_router, prefix="/api/v1", tags=["iot-sensors"])
app.include_router(crop_response_router, prefix="/api/v1", tags=["crop-response"])
app.include_router(crop_integration_router, prefix="/api/v1", tags=["crop-integration"])
app.include_router(decision_support_router, prefix="/api/v1", tags=["decision-support"])
app.include_router(economic_optimization_router, prefix="/api/v1", tags=["economic-optimization"])
app.include_router(validation_router, prefix="/api/v1", tags=["algorithm-validation"])
app.include_router(fertilizer_router, prefix="/api/v1", tags=["fertilizer-application-methods"])
app.include_router(advanced_application_router, prefix="/api/v1", tags=["advanced-application-management"])
app.include_router(integration_router, tags=["caain-integration"])
app.include_router(analytics_router, tags=["analytics"])
app.include_router(priority_constraint_router, prefix="/api/v1", tags=["priority-constraints"])
app.include_router(goal_based_router, prefix="/api/v1", tags=["goal-based-recommendations"])
app.include_router(adaptive_learning_router, prefix="/api/v1", tags=["adaptive-learning"])
app.include_router(advanced_labor_analysis_router, prefix="/api/v1", tags=["advanced-labor-analysis"])

@app.get("/health")
async def health_check():
    """Basic health check endpoint."""
    return {
        "service": "fertilizer-application",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "application_method_selection",
            "equipment_assessment",
            "equipment_efficiency_analysis",
            "performance_monitoring",
            "real_time_monitoring",
            "real_time_adjustments",
            "real_time_alerts",
            "application_rate_monitoring",
            "coverage_monitoring",
            "weather_monitoring",
            "quality_control",
            "iot_sensor_integration",
            "equipment_telemetry",
            "timing_optimization",
            "route_optimization",
            "maintenance_optimization",
            "cost_analysis",
            "application_guidance",
            "method_optimization",
            "equipment_compatibility",
            "caain_integration",
            "cross_service_communication",
            "data_synchronization",
            "farm_size_assessment",
            "crop_response_optimization",
            "yield_impact_prediction",
            "method_effectiveness_ranking",
            "crop_type_integration",
            "growth_stage_integration",
            "crop_method_compatibility",
            "crop_nutrient_requirements",
            "decision_support_system",
            "decision_trees",
            "expert_systems",
            "scenario_analysis",
            "sensitivity_analysis",
            "interactive_decisions",
            "what_if_analysis",
            "economic_optimization",
            "linear_programming",
            "dynamic_programming",
            "stochastic_optimization",
            "genetic_algorithms",
            "simulated_annealing",
            "particle_swarm_optimization",
            "scenario_modeling",
            "investment_planning",
            "risk_assessment",
            "monte_carlo_simulation",
            "advanced_application_planning",
            "multi_field_coordination",
            "seasonal_planning",
            "resource_optimization",
            "real_time_optimization",
            "dynamic_optimization",
            "performance_prediction",
            "algorithm_validation",
            "cross_validation",
            "field_validation",
            "expert_validation",
            "outcome_validation",
            "performance_tracking",
            "continuous_improvement",
            "model_training",
            "performance_optimization",
            "production_monitoring",
            "analytics_reporting",
            "user_engagement_tracking",
            "recommendation_effectiveness",
            "agricultural_impact_assessment",
            "system_performance_analytics",
            "usage_pattern_analysis",
            "comprehensive_reporting",
            "goal_based_recommendations",
            "multi_objective_optimization",
            "pareto_optimization",
            "constraint_satisfaction",
            "goal_prioritization",
            "adaptive_learning",
            "outcome_tracking",
            "farmer_feedback_integration",
            "ml_model_training",
            "regional_adaptation",
            "farm_specific_learning",
            "seasonal_adjustment",
            "continuous_improvement",
            "advanced_labor_analysis",
            "labor_efficiency_analysis",
            "labor_productivity_optimization",
            "labor_roi_analysis",
            "labor_sensitivity_analysis"
        ]
    }

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "message": "AFAS Fertilizer Application Service is running",
        "service": "fertilizer-application",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    port = int(os.getenv("FERTILIZER_APPLICATION_PORT", 8008))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)