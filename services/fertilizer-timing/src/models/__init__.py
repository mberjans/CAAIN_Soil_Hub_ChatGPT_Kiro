"""
Models namespace for the fertilizer timing optimization microservice.

Re-exports key strategy models alongside calendar and alert response models.
"""

from .alert_models import TimingAlert, TimingAlertResponse  # noqa: F401
from .calendar_models import SeasonalCalendarEntry, SeasonalCalendarResponse  # noqa: F401
from .constraint_models import (  # noqa: F401
    AlternativeScheduleOption,
    ConstraintStatus,
    OperationalConstraintReport,
    ResourceAllocationPlan,
)
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
    TimingExplanation,
    TimingExplanationRequest,
    YieldRecord,
)
from .weather_integration_models import (  # noqa: F401
    SoilConditionSnapshot,
    WeatherConditionSummary,
    WeatherSoilIntegrationReport,
    WeatherSoilWindow,
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
    "AlternativeScheduleOption",
    "ApplicationMethod",
    "ApplicationTiming",
    "ApplicationTimingDeviation",
    "ConstraintStatus",
    "CropGrowthStage",
    "EfficiencyAssessment",
    "EquipmentAvailability",
    "FertilizerApplicationRecord",
    "FertilizerType",
    "ImprovementRecommendation",
    "LaborAvailability",
    "LossRiskAssessment",
    "NutrientSynchronizationAssessment",
    "OperationalConstraintReport",
    "ProgramAnalysisContext",
    "ProgramAnalysisRequest",
    "ProgramAssessmentReport",
    "ResourceAllocationPlan",
    "SeasonalCalendarEntry",
    "SeasonalCalendarResponse",
    "SoilConditionSnapshot",
    "SoilTestResult",
    "SplitApplicationPlan",
    "TimingAlert",
    "TimingAlertResponse",
    "TimingAssessment",
    "TimingConstraint",
    "TimingConstraintType",
    "TimingExplanation",
    "TimingExplanationRequest",
    "TimingOptimizationRequest",
    "TimingOptimizationResult",
    "TimingOptimizationSummary",
    "WeatherCondition",
    "WeatherConditionSummary",
    "WeatherSoilIntegrationReport",
    "WeatherSoilWindow",
    "WeatherWindow",
    "YieldRecord",
]
