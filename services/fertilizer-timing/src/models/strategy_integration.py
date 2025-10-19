"""
Strategy integration models for the fertilizer timing microservice.

This module reuses the existing fertilizer strategy timing models by loading
them dynamically through the module loader utility. This avoids duplicating
domain logic while providing clean re-exports for the microservice.
"""

from pathlib import Path
from typing import Any, Type

from utils.module_loader import get_strategy_src_dir, load_strategy_module

_STRATEGY_SRC_DIR = get_strategy_src_dir()
_MODELS_PATH = _STRATEGY_SRC_DIR / "models" / "timing_optimization_models.py"

_MODELS_MODULE = load_strategy_module(
    "services.fertilizer_strategy.src.models.timing_optimization_models",
    Path(_MODELS_PATH)
)


def _export(name: str) -> Type[Any]:
    """Retrieve an attribute from the strategy models module."""
    if not hasattr(_MODELS_MODULE, name):
        raise AttributeError(f"{name} not found in strategy timing models")
    return getattr(_MODELS_MODULE, name)


TimingOptimizationRequest = _export("TimingOptimizationRequest")
TimingOptimizationResult = _export("TimingOptimizationResult")
ApplicationTiming = _export("ApplicationTiming")
SplitApplicationPlan = _export("SplitApplicationPlan")
WeatherWindow = _export("WeatherWindow")
WeatherCondition = _export("WeatherCondition")
TimingOptimizationSummary = _export("TimingOptimizationSummary")
EquipmentAvailability = _export("EquipmentAvailability")
LaborAvailability = _export("LaborAvailability")
TimingConstraint = _export("TimingConstraint")
TimingConstraintType = _export("TimingConstraintType")
CropGrowthStage = _export("CropGrowthStage")
ApplicationMethod = _export("ApplicationMethod")
FertilizerType = _export("FertilizerType")


__all__ = [
    "ApplicationMethod",
    "ApplicationTiming",
    "CropGrowthStage",
    "EquipmentAvailability",
    "FertilizerType",
    "LaborAvailability",
    "SplitApplicationPlan",
    "TimingConstraint",
    "TimingConstraintType",
    "TimingOptimizationRequest",
    "TimingOptimizationResult",
    "TimingOptimizationSummary",
    "WeatherWindow",
    "WeatherCondition",
]
