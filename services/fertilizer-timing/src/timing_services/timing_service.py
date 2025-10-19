"""
Timing optimization adapter for the fertilizer timing microservice.

This module bridges the fertilizer strategy optimization engine into the
microservice, exposing convenient async methods suitable for API routes.
"""

from pathlib import Path
from typing import Dict, List

from models import (
    ApplicationTiming,
    SplitApplicationPlan,
    TimingOptimizationRequest,
    TimingOptimizationResult,
    WeatherWindow,
)
from utils.module_loader import get_strategy_src_dir, load_strategy_module

_STRATEGY_SRC_DIR = get_strategy_src_dir()
_SERVICE_PATH = _STRATEGY_SRC_DIR / "services" / "timing_optimization_service.py"

_SERVICE_MODULE = load_strategy_module(
    "services.fertilizer_strategy.src.services.timing_optimization_service",
    Path(_SERVICE_PATH)
)

FertilizerTimingOptimizer = getattr(_SERVICE_MODULE, "FertilizerTimingOptimizer")


class TimingOptimizationAdapter:
    """
    Adapter around the fertilizer strategy timing optimizer.

    Exposes async helper methods with descriptive names used by API routers.
    """

    def __init__(self) -> None:
        self._optimizer = FertilizerTimingOptimizer()

    async def optimize(self, request: TimingOptimizationRequest) -> TimingOptimizationResult:
        """Run full optimization for the provided request."""
        return await self._optimizer.optimize_timing(request)

    async def analyze_weather_windows(self, request: TimingOptimizationRequest) -> List[WeatherWindow]:
        """Delegate to the optimizer's weather analysis."""
        return await self._optimizer._analyze_weather_windows(request)  # pylint: disable=protected-access

    async def determine_crop_stages(
        self, request: TimingOptimizationRequest
    ) -> Dict[str, str]:
        """Return crop growth stage timeline as ISO date strings."""
        stages = await self._optimizer._determine_crop_growth_stages(request)  # pylint: disable=protected-access
        timeline: Dict[str, str] = {}
        for stage_date, stage in stages.items():
            timeline[stage.value] = stage_date.strftime("%Y-%m-%d")
        return timeline

    async def optimize_split_applications(
        self, request: TimingOptimizationRequest
    ) -> List[SplitApplicationPlan]:
        """Generate split application plans."""
        result = await self.optimize(request)
        return result.split_plans

    async def quick_optimize(self, request: TimingOptimizationRequest) -> TimingOptimizationResult:
        """Alias for optimize, kept for semantic clarity."""
        return await self.optimize(request)

    async def summarize(
        self, request: TimingOptimizationRequest
    ) -> Dict[str, ApplicationTiming]:
        """
        Provide a mapping of fertilizer type to primary application recommendation.
        """
        result = await self.optimize(request)
        summary: Dict[str, ApplicationTiming] = {}
        for timing in result.optimal_timings:
            fertilizer_key = timing.fertilizer_type
            if fertilizer_key not in summary:
                summary[fertilizer_key] = timing
        return summary


__all__ = ["TimingOptimizationAdapter"]
