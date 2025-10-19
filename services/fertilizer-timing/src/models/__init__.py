"""
Models namespace for the fertilizer timing optimization microservice.

Re-exports key strategy models alongside calendar and alert response models.
"""

from .alert_models import TimingAlert, TimingAlertResponse  # noqa: F401
from .calendar_models import SeasonalCalendarEntry, SeasonalCalendarResponse  # noqa: F401
from .program_analysis_models import (  # noqa: F401
    ApplicationTimingDeviation,
    EfficiencyAssessment,
    FertilizerApplicationRecord,
    ImprovementRecommendation,
    LossRiskAssessment,
    NutrientSynchronizationAssessment,
    ProgramAnalysisContext,
    ProgramAnalysisRequest,
    ProgramAssessmentReport,
    SoilTestResult,
    TimingAssessment,
    YieldRecord,
)
from .strategy_integration import (  # noqa: F401
    ApplicationMethod,
    ApplicationTiming,
    CropGrowthStage,
    EquipmentAvailability,
    FertilizerType,
    LaborAvailability,
    SplitApplicationPlan,
    TimingConstraint,
    TimingConstraintType,
    TimingOptimizationRequest,
    TimingOptimizationResult,
    TimingOptimizationSummary,
    WeatherWindow,
    WeatherCondition,
)

__all__ = [
    "ApplicationMethod",
    "ApplicationTiming",
    "CropGrowthStage",
    "EquipmentAvailability",
    "FertilizerType",
    "LaborAvailability",
    "SeasonalCalendarEntry",
    "SeasonalCalendarResponse",
    "SplitApplicationPlan",
    "TimingConstraint",
    "TimingConstraintType",
    "TimingAlert",
    "TimingAlertResponse",
    "TimingOptimizationRequest",
    "TimingOptimizationResult",
    "TimingOptimizationSummary",
    "WeatherWindow",
    "WeatherCondition",
    "ApplicationTimingDeviation",
    "EfficiencyAssessment",
    "FertilizerApplicationRecord",
    "ImprovementRecommendation",
    "LossRiskAssessment",
    "NutrientSynchronizationAssessment",
    "ProgramAnalysisContext",
    "ProgramAnalysisRequest",
    "ProgramAssessmentReport",
    "SoilTestResult",
    "TimingAssessment",
    "YieldRecord",
]
