"""
Timing reasoning and explanation service for fertilizer application planning.

Builds educational, farmer-friendly explanations that describe why specific
timing recommendations were generated and how weather, crop physiology, soil,
and operational factors influenced the decision.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Dict, List, Optional

from models import (
    ApplicationTiming,
    TimingOptimizationResult,
    WeatherCondition,
)
from models.program_analysis_models import (
    ProgramAnalysisContext,
    TimingAssessment,
    TimingExplanation,
)

logger = logging.getLogger(__name__)


class TimingExplanationService:
    """
    Build structured explanations for fertilizer timing recommendations.

    The service converts optimization outputs into narrative insights that can be
    surfaced in APIs, UI layers, or higher level AI explanation services.
    """

    def __init__(self) -> None:
        self._educational_library = self._build_educational_library()
        self._knowledge_references = self._build_knowledge_references()
        logger.info("TimingExplanationService initialized")

    def build_explanation(
        self,
        optimization_result: TimingOptimizationResult,
        context: Optional[ProgramAnalysisContext],
        timing_assessment: Optional[TimingAssessment],
    ) -> TimingExplanation:
        """
        Construct a comprehensive timing explanation from optimization outputs.

        Args:
            optimization_result: Result returned by the timing optimizer.
            context: Field and crop context used for the optimization.
            timing_assessment: Assessment of actual program timing alignment.

        Returns:
            TimingExplanation capturing reasoning, trade-offs, and guidance.
        """
        try:
            summary_text = self._build_summary(optimization_result, timing_assessment)
            key_points = self._build_key_points(optimization_result)
            weather_impacts = self._build_weather_impacts(optimization_result)
            crop_stage_reasoning = self._build_crop_stage_reasoning(optimization_result)
            soil_condition_notes = self._build_soil_condition_notes(optimization_result)
            operational_factors = self._build_operational_factors(context, optimization_result)
            trade_offs = self._build_trade_offs(optimization_result)
            educational_guidance = self._collect_educational_guidance(context)
            knowledge_references = list(self._knowledge_references)

            return TimingExplanation(
                summary=summary_text,
                key_points=key_points,
                weather_impacts=weather_impacts,
                crop_stage_reasoning=crop_stage_reasoning,
                soil_condition_notes=soil_condition_notes,
                operational_considerations=operational_factors,
                trade_offs=trade_offs,
                educational_guidance=educational_guidance,
                knowledge_references=knowledge_references,
            )

        except Exception as exc:  # pylint: disable=broad-except
            logger.error("Failed to build timing explanation: {0}".format(exc))
            return TimingExplanation(
                summary="Detailed timing explanation is currently unavailable.",
                key_points=[],
                weather_impacts=[],
                crop_stage_reasoning=[],
                soil_condition_notes=[],
                operational_considerations=[],
                trade_offs=[],
                educational_guidance=[
                    "Confirm fertilizer timing with local agronomic advisors.",
                    "Monitor weather and soil conditions before application.",
                ],
                knowledge_references=list(self._knowledge_references),
            )

    def _build_summary(
        self,
        optimization_result: TimingOptimizationResult,
        timing_assessment: Optional[TimingAssessment],
    ) -> str:
        """Create overview statement describing timing alignment and impact."""
        overall_score = optimization_result.overall_timing_score
        confidence_score = optimization_result.confidence_score
        text_parts: List[str] = []

        text_parts.append(
            "Timing optimization achieved an overall alignment score of {0:.0%} with {1:.0%} confidence.".format(
                overall_score,
                confidence_score,
            )
        )

        if timing_assessment is not None:
            on_time_percent = timing_assessment.on_time_percentage
            average_deviation = timing_assessment.average_deviation_days
            text_parts.append(
                "Current program is {0:.0%} on time with an average deviation of {1:.1f} days.".format(
                    on_time_percent,
                    average_deviation,
                )
            )

        expected_yield = optimization_result.expected_yield_impact
        if expected_yield is not None:
            text_parts.append(
                "Staying within the recommended windows is projected to influence yield by {0:.1f}%.".format(
                    expected_yield
                )
            )

        summary_buffer = ""
        index = 0
        while index < len(text_parts):
            part = text_parts[index]
            if summary_buffer:
                summary_buffer = "{0} {1}".format(summary_buffer, part)
            else:
                summary_buffer = part
            index += 1
        return summary_buffer

    def _build_key_points(
        self,
        optimization_result: TimingOptimizationResult,
    ) -> List[str]:
        """Highlight critical takeaways for each fertilizer recommendation."""
        points: List[str] = []
        timings = optimization_result.optimal_timings
        index = 0
        while index < len(timings):
            timing = timings[index]
            segment = self._describe_application_timing(timing)
            points.append(segment)
            index += 1
        return points

    def _build_weather_impacts(
        self,
        optimization_result: TimingOptimizationResult,
    ) -> List[str]:
        """Explain how forecasted weather windows affected timing decisions."""
        impacts: List[str] = []

        windows = optimization_result.weather_windows
        index = 0
        while index < len(windows):
            window = windows[index]
            description = self._describe_weather_window(window, index + 1)
            impacts.append(description)
            index += 1

        if len(impacts) == 0:
            impacts.append(
                "Weather windows were not available, so default seasonal timing guidance was applied."
            )

        return impacts

    def _build_crop_stage_reasoning(
        self,
        optimization_result: TimingOptimizationResult,
    ) -> List[str]:
        """Detail how crop physiology and growth stages informed recommendations."""
        reasoning: List[str] = []

        timings = optimization_result.optimal_timings
        index = 0
        while index < len(timings):
            timing = timings[index]
            crop_stage_text = (
                "Apply {0} at the {1} stage to align nutrient availability with demand (timing score {2:.0%})."
            ).format(
                timing.fertilizer_type.capitalize(),
                timing.crop_stage.value.upper(),
                timing.crop_score,
            )
            reasoning.append(crop_stage_text)
            index += 1

        return reasoning

    def _build_soil_condition_notes(
        self,
        optimization_result: TimingOptimizationResult,
    ) -> List[str]:
        """Summarize soil-driven adjustments and considerations."""
        notes: List[str] = []

        timings = optimization_result.optimal_timings
        index = 0
        while index < len(timings):
            timing = timings[index]
            soil_score = timing.soil_score
            detail = (
                "Soil suitability score for this window is {0:.0%}, indicating {1} soil conditions."
            ).format(
                soil_score,
                self._classify_soil_score(soil_score),
            )
            notes.append(detail)

            if timing.application_window.soil_moisture is not None:
                moisture = timing.application_window.soil_moisture
                moisture_note = (
                    "Expected soil moisture near application is {0:.0%}, which affects nutrient movement."
                ).format(moisture)
                notes.append(moisture_note)
            index += 1

        return notes

    def _build_operational_factors(
        self,
        context: Optional[ProgramAnalysisContext],
        optimization_result: TimingOptimizationResult,
    ) -> List[str]:
        """Highlight equipment, labor, and operational constraints."""
        considerations: List[str] = []

        if context is not None:
            slope_percent = context.slope_percent
            soil_type = context.soil_type
            drainage = context.drainage_class

            considerations.append(
                "Field conditions: {0} soil with {1} drainage and {2:.1f}% slope.".format(
                    soil_type,
                    drainage,
                    slope_percent,
                )
            )

        timings = optimization_result.optimal_timings
        index = 0
        while index < len(timings):
            timing = timings[index]
            risk_text = (
                "Operational risk for {0} application is weather {1:.0%}, timing {2:.0%}, equipment {3:.0%}."
            ).format(
                timing.fertilizer_type,
                timing.weather_risk,
                timing.timing_risk,
                timing.equipment_risk,
            )
            considerations.append(risk_text)
            index += 1

        return considerations

    def _build_trade_offs(
        self,
        optimization_result: TimingOptimizationResult,
    ) -> List[str]:
        """Document key trade-offs considered during optimization."""
        trade_offs: List[str] = []

        recommendations = optimization_result.recommendations
        index = 0
        while index < len(recommendations):
            item = recommendations[index]
            trade_offs.append(item)
            index += 1

        if optimization_result.split_plans:
            trade_offs.append(
                "Split applications were evaluated to balance efficiency and risk."
            )

        if optimization_result.risk_score is not None:
            trade_offs.append(
                "Overall risk score registered at {0:.0%}, indicating balance between efficiency and resilience.".format(
                    optimization_result.risk_score
                )
            )

        return trade_offs

    def _collect_educational_guidance(
        self,
        context: Optional[ProgramAnalysisContext],
    ) -> List[str]:
        """Aggregate educational best practices relevant to the crop and region."""
        guidance: List[str] = []

        crop_key = "general"
        if context is not None:
            crop_name = context.crop_name.lower()
            if crop_name in self._educational_library:
                crop_key = crop_name

        library_entry = self._educational_library.get(crop_key, [])
        index = 0
        while index < len(library_entry):
            guidance.append(library_entry[index])
            index += 1

        if context is not None:
            regional_note = self._build_regional_note(context)
            guidance.append(regional_note)

        return guidance

    def _build_educational_library(self) -> Dict[str, List[str]]:
        """Create default educational content library."""
        library: Dict[str, List[str]] = {}

        library["general"] = [
            "Follow 4R Nutrient Stewardship: right source, rate, time, and place.",
            "Confirm soil temperature and trafficability before field entry.",
            "Document applications to evaluate year-over-year timing performance.",
        ]

        corn_guidance: List[str] = []
        corn_guidance.append(
            "Corn benefits from sidedress nitrogen near V6 when rapid uptake begins."
        )
        corn_guidance.append(
            "Avoid applications before heavy rainfall to limit nitrogen losses."
        )
        library["corn"] = corn_guidance

        soybean_guidance: List[str] = []
        soybean_guidance.append(
            "Starter phosphorus is most effective when applied close to planting."
        )
        soybean_guidance.append(
            "Monitor canopy development to time in-season micronutrient foliar sprays."
        )
        library["soybean"] = soybean_guidance

        wheat_guidance: List[str] = []
        wheat_guidance.append(
            "Schedule nitrogen topdress before jointing to support tiller survival."
        )
        wheat_guidance.append(
            "Late spring nitrogen should consider lodging risk under high rainfall."
        )
        library["wheat"] = wheat_guidance

        return library

    def _build_knowledge_references(self) -> List[str]:
        """List knowledge references for transparency."""
        references: List[str] = []
        references.append("4R Nutrient Stewardship Alliance")
        references.append("University Extension Fertility Guides")
        references.append("Regional Weather Service Advisories")
        return references

    def _describe_application_timing(self, timing: ApplicationTiming) -> str:
        """Format narrative for a single application recommendation."""
        return (
            "{0} application via {1} is targeted for {2} to achieve {3:.0%} timing efficiency with expected yield impact near {4:.1f}%."
        ).format(
            timing.fertilizer_type.capitalize(),
            timing.application_method.value.replace("_", " "),
            self._format_date(timing.recommended_date),
            timing.timing_score,
            timing.yield_impact_percent,
        )

    def _describe_weather_window(self, window, index: int) -> str:
        """Describe suitability of a weather window."""
        return (
            "Window {0}: {1} conditions with {2:.0f}°F average temperature, {3:.0%} precipitation probability, wind {4:.0f} mph."
        ).format(
            index,
            self._translate_weather_condition(window.condition),
            window.temperature_f,
            window.precipitation_probability,
            window.wind_speed_mph,
        )

    def _classify_soil_score(self, score: float) -> str:
        """Translate soil suitability score into descriptive text."""
        if score >= 0.85:
            return "excellent"
        if score >= 0.7:
            return "favorable"
        if score >= 0.5:
            return "moderate"
        return "cautionary"

    def _translate_weather_condition(self, condition: WeatherCondition) -> str:
        """Provide readable description for weather condition."""
        mapping = {
            WeatherCondition.OPTIMAL: "optimal",
            WeatherCondition.ACCEPTABLE: "acceptable",
            WeatherCondition.MARGINAL: "marginal",
            WeatherCondition.POOR: "poor",
            WeatherCondition.UNACCEPTABLE: "unacceptable",
        }
        return mapping.get(condition, condition.value)

    def _build_regional_note(self, context: ProgramAnalysisContext) -> str:
        """Create regional advisory note based on location."""
        latitude = context.location.get("lat")
        hemisphere = "northern"
        if latitude is not None and latitude < 0:
            hemisphere = "southern"

        return (
            "Consider regional extension advisories for the {0} hemisphere to adjust dates around local weather anomalies."
        ).format(hemisphere)

    def _format_date(self, value: date) -> str:
        """Format date consistently for explanations."""
        return value.strftime("%b %d, %Y")


__all__ = ["TimingExplanationService"]
