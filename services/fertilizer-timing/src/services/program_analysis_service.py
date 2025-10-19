"""
Comprehensive fertilizer program analysis service.

Evaluates current fertilizer programs for timing alignment, nutrient
synchronization, efficiency, and risk to recommend improvements.
"""

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Sequence, Tuple

from models import (
    ApplicationMethod,
    ApplicationTiming,
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
    TimingOptimizationRequest,
    TimingOptimizationResult,
    YieldRecord,
)
from timing_services.timing_service import TimingOptimizationAdapter

logger = logging.getLogger(__name__)


class FertilizerProgramAnalysisService:
    """Analyze existing fertilizer programs and highlight improvements."""

    def __init__(self) -> None:
        self._timing_adapter = TimingOptimizationAdapter()
        logger.info("FertilizerProgramAnalysisService initialized")

    async def analyze_program(self, request: ProgramAnalysisRequest) -> ProgramAssessmentReport:
        """
        Perform full analysis of the provided fertilizer program.

        Returns:
            ProgramAssessmentReport containing assessments and recommendations.
        """
        optimization_result: Optional[TimingOptimizationResult] = None
        if request.current_program:
            try:
                optimization_request = self._build_optimization_request(request.context, request.current_program)
                optimization_result = await self._timing_adapter.optimize(optimization_request)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning("Optimization fallback due to error: %s", exc)

        timing_assessment = self._evaluate_timing(request.current_program, optimization_result)
        nutrient_assessment = self._evaluate_nutrient_synchronization(request, optimization_result)
        loss_assessment = self._evaluate_loss_risk(request, timing_assessment)
        efficiency_assessment = self._evaluate_efficiency(request, timing_assessment, nutrient_assessment)
        recommendations = self._build_recommendations(timing_assessment, nutrient_assessment, loss_assessment, efficiency_assessment)
        key_takeaways = self._summarize_takeaways(timing_assessment, efficiency_assessment, loss_assessment, recommendations)

        report = ProgramAssessmentReport(
            request_id=request.request_id,
            generated_at=datetime.utcnow(),
            timing_assessment=timing_assessment,
            nutrient_assessment=nutrient_assessment,
            loss_assessment=loss_assessment,
            efficiency_assessment=efficiency_assessment,
            recommendations=recommendations,
            key_takeaways=key_takeaways,
        )
        return report

    def _build_optimization_request(
        self,
        context: ProgramAnalysisContext,
        program: Sequence[FertilizerApplicationRecord],
    ) -> TimingOptimizationRequest:
        application_methods: List[ApplicationMethod] = []
        for record in program:
            method_value = self._map_application_method(record.application_method)
            if method_value not in application_methods:
                application_methods.append(method_value)

        if not application_methods:
            application_methods.append(ApplicationMethod.BROADCAST)

        equipment_availability: Dict[str, List[str]] = {}
        labor_availability: Dict[str, int] = {}

        optimization_request = TimingOptimizationRequest(
            field_id=context.field_id,
            crop_type=context.crop_name,
            planting_date=context.planting_date,
            expected_harvest_date=context.expected_harvest_date,
            fertilizer_requirements=context.fertilizer_requirements,
            application_methods=application_methods,
            soil_type=context.soil_type,
            soil_moisture_capacity=context.soil_moisture_capacity,
            drainage_class=context.drainage_class,
            slope_percent=context.slope_percent,
            weather_data_source="noaa",
            location=context.location,
            equipment_availability=equipment_availability,
            labor_availability=labor_availability,
            optimization_horizon_days=365,
            risk_tolerance=0.5,
            prioritize_yield=True,
            prioritize_cost=False,
            split_application_allowed=True,
            weather_dependent_timing=True,
            soil_temperature_threshold=50.0,
        )
        return optimization_request

    def _evaluate_timing(
        self,
        program: Sequence[FertilizerApplicationRecord],
        optimization_result: Optional[TimingOptimizationResult],
    ) -> TimingAssessment:
        if not program:
            return TimingAssessment(
                average_deviation_days=0.0,
                on_time_percentage=1.0,
                early_applications=0,
                late_applications=0,
                critical_risk_events=0,
                deviations=[],
            )

        recommended_map = self._group_recommended_timings(optimization_result)
        deviations: List[ApplicationTimingDeviation] = []
        total_abs_deviation = 0.0
        on_time_count = 0
        early_count = 0
        late_count = 0
        critical_count = 0
        tolerance_days = 3
        for record in program:
            deviation = self._assess_record_timing(record, recommended_map, tolerance_days)
            deviations.append(deviation)
            if deviation.days_difference is not None:
                difference_value = abs(deviation.days_difference)
                total_abs_deviation += difference_value
                if difference_value <= tolerance_days:
                    on_time_count += 1
                elif deviation.days_difference < 0:
                    early_count += 1
                else:
                    late_count += 1
                if deviation.risk_flag == "critical":
                    critical_count += 1

        total_records = len(program)
        if total_records > 0:
            average_deviation = total_abs_deviation / total_records
            on_time_ratio = on_time_count / total_records
        else:
            average_deviation = 0.0
            on_time_ratio = 1.0

        assessment = TimingAssessment(
            average_deviation_days=average_deviation,
            on_time_percentage=on_time_ratio,
            early_applications=early_count,
            late_applications=late_count,
            critical_risk_events=critical_count,
            deviations=deviations,
        )
        return assessment

    def _evaluate_nutrient_synchronization(
        self,
        request: ProgramAnalysisRequest,
        optimization_result: Optional[TimingOptimizationResult],
    ) -> NutrientSynchronizationAssessment:
        requirements = request.context.fertilizer_requirements
        applied_totals: Dict[str, float] = {}
        for record in request.current_program:
            nutrient_key = self._determine_nutrient_key(record)
            if nutrient_key not in applied_totals:
                applied_totals[nutrient_key] = 0.0
            applied_totals[nutrient_key] += record.amount_lbs_per_acre

        nutrient_balance: Dict[str, float] = {}
        for nutrient, requirement in requirements.items():
            applied_amount = applied_totals.get(nutrient, 0.0)
            if requirement > 0:
                balance_value = applied_amount / requirement
            else:
                balance_value = 1.0
            nutrient_balance[nutrient] = balance_value

        soil_flags = self._evaluate_soil_sufficiency(request.soil_tests, requirements)
        observations: List[str] = self._build_nutrient_observations(nutrient_balance, soil_flags)

        synchronization_score = self._calculate_synchronization_score(nutrient_balance, soil_flags, optimization_result)

        assessment = NutrientSynchronizationAssessment(
            nutrient_balance=nutrient_balance,
            soil_sufficiency_flags=soil_flags,
            synchronization_score=synchronization_score,
            observations=observations,
        )
        return assessment

    def _evaluate_loss_risk(
        self,
        request: ProgramAnalysisRequest,
        timing_assessment: TimingAssessment,
    ) -> LossRiskAssessment:
        slope_factor = request.context.slope_percent / 20.0
        if slope_factor > 1.0:
            slope_factor = 1.0

        runoff_risk = slope_factor + timing_assessment.average_deviation_days / 30.0
        if runoff_risk > 1.0:
            runoff_risk = 1.0

        volatilization_risk = 0.3
        if self._contains_keyword(request.operational_notes, "hot"):
            volatilization_risk += 0.3
        if self._contains_keyword(request.operational_notes, "dry"):
            volatilization_risk += 0.2
        if volatilization_risk > 1.0:
            volatilization_risk = 1.0

        leaching_risk = 0.2
        soil_type = request.context.soil_type.lower()
        if "sand" in soil_type:
            leaching_risk += 0.3
        if self._contains_keyword(request.operational_notes, "rain"):
            leaching_risk += 0.3
        if timing_assessment.late_applications > timing_assessment.early_applications:
            leaching_risk += 0.1
        if leaching_risk > 1.0:
            leaching_risk = 1.0

        incident_notes: List[str] = []
        for item in request.environmental_incidents:
            incident_notes.append(item)

        assessment = LossRiskAssessment(
            runoff_risk_score=runoff_risk,
            volatilization_risk_score=volatilization_risk,
            leaching_risk_score=leaching_risk,
            incident_notes=incident_notes,
        )
        return assessment

    def _evaluate_efficiency(
        self,
        request: ProgramAnalysisRequest,
        timing_assessment: TimingAssessment,
        nutrient_assessment: NutrientSynchronizationAssessment,
    ) -> EfficiencyAssessment:
        yield_trend = self._calculate_yield_trend(request.yield_history)

        timing_weight = 0.4
        nutrient_weight = 0.4
        yield_weight = 0.2
        efficiency_score = (
            timing_assessment.on_time_percentage * timing_weight
            + nutrient_assessment.synchronization_score * nutrient_weight
            + self._clamp_ratio((yield_trend + 100.0) / 200.0) * yield_weight
        )

        cost_effectiveness = self._estimate_cost_effectiveness(request.yield_history, request.current_program)

        focus_areas = self._identify_focus_areas(timing_assessment, nutrient_assessment, yield_trend)

        assessment = EfficiencyAssessment(
            yield_trend_percent=yield_trend,
            efficiency_score=efficiency_score,
            cost_effectiveness_index=cost_effectiveness,
            recommended_focus_areas=focus_areas,
        )
        return assessment

    def _build_recommendations(
        self,
        timing: TimingAssessment,
        nutrient: NutrientSynchronizationAssessment,
        loss: LossRiskAssessment,
        efficiency: EfficiencyAssessment,
    ) -> List[ImprovementRecommendation]:
        recommendations: List[ImprovementRecommendation] = []

        if timing.on_time_percentage < 0.75 or timing.critical_risk_events > 0:
            recommendations.append(
                ImprovementRecommendation(
                    title="Improve timing precision",
                    description="Align fertilizer applications with optimized windows using scheduling tools and contingency plans.",
                    expected_benefit="Protect yield response and reduce weather-related losses.",
                    priority="high",
                )
            )

        for nutrient_key, balance in nutrient.nutrient_balance.items():
            if balance < 0.85:
                recommendations.append(
                    ImprovementRecommendation(
                        title=f"Increase {nutrient_key} application",
                        description=f"Current program delivers {balance:.2f} of the required {nutrient_key}. Adjust rates or add supplemental sources.",
                        expected_benefit="Avoid nutrient deficiencies and safeguard yield.",
                        priority="high",
                    )
                )
            elif balance > 1.2:
                recommendations.append(
                    ImprovementRecommendation(
                        title=f"Reduce {nutrient_key} rates",
                        description=f"Applications exceed {nutrient_key} requirements by {balance:.2f}x. Optimize rates to cut waste and losses.",
                        expected_benefit="Lower input costs and limit environmental impact.",
                        priority="medium",
                    )
                )

        if loss.runoff_risk_score > 0.6 or loss.leaching_risk_score > 0.6:
            recommendations.append(
                ImprovementRecommendation(
                    title="Mitigate nutrient loss risks",
                    description="Adopt buffer strips, stabilizers, or split applications to reduce runoff and leaching risk.",
                    expected_benefit="Protect water quality and retain applied nutrients.",
                    priority="high",
                )
            )

        if efficiency.yield_trend_percent < 0:
            recommendations.append(
                ImprovementRecommendation(
                    title="Investigate declining yields",
                    description="Combine tissue tests, scouting, and agronomic review to diagnose declining yield trend.",
                    expected_benefit="Identify limiting factors and restore productivity.",
                    priority="medium",
                )
            )

        if not recommendations:
            recommendations.append(
                ImprovementRecommendation(
                    title="Maintain current program",
                    description="Program performance is stable. Continue monitoring and update with new soil tests.",
                    expected_benefit="Sustain current productivity and efficiency.",
                    priority="low",
                )
            )
        return recommendations

    def _summarize_takeaways(
        self,
        timing: TimingAssessment,
        efficiency: EfficiencyAssessment,
        loss: LossRiskAssessment,
        recommendations: Sequence[ImprovementRecommendation],
    ) -> List[str]:
        takeaways: List[str] = []

        takeaways.append(f"On-time application rate: {timing.on_time_percentage:.0%}")
        takeaways.append(f"Average timing deviation: {timing.average_deviation_days:.1f} days")

        takeaways.append(f"Efficiency score: {efficiency.efficiency_score:.2f}")
        takeaways.append(f"Yield trend: {efficiency.yield_trend_percent:.1f}%")

        takeaways.append(f"Runoff risk score: {loss.runoff_risk_score:.2f}")
        takeaways.append(f"Leaching risk score: {loss.leaching_risk_score:.2f}")

        if recommendations:
            first_recommendation = recommendations[0]
            takeaways.append(f"Top priority recommendation: {first_recommendation.title}")

        return takeaways

    def _group_recommended_timings(
        self,
        optimization_result: Optional[TimingOptimizationResult],
    ) -> Dict[str, List[ApplicationTiming]]:
        grouped: Dict[str, List[ApplicationTiming]] = {}
        if optimization_result is None or not optimization_result.optimal_timings:
            return grouped

        for timing in optimization_result.optimal_timings:
            key = timing.fertilizer_type
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(timing)
        return grouped

    def _assess_record_timing(
        self,
        record: FertilizerApplicationRecord,
        recommended_map: Dict[str, List[ApplicationTiming]],
        tolerance_days: int,
    ) -> ApplicationTimingDeviation:
        recommended_list = recommended_map.get(record.fertilizer_type)
        recommended_date: Optional[date] = None
        crop_stage_alignment = "unknown"
        risk_flag = None
        days_difference: Optional[int] = None

        if recommended_list:
            closest = self._select_closest_timing(record, recommended_list)
            if closest is not None:
                recommended_date = closest.recommended_date
                days_difference = (record.applied_date - closest.recommended_date).days
                crop_stage_alignment = self._compare_crop_stage(record.crop_stage, closest.crop_stage.value)
                if days_difference < -tolerance_days or days_difference > tolerance_days:
                    if abs(days_difference) > 7:
                        risk_flag = "critical"
                    else:
                        risk_flag = "warning"
                if closest.timing_risk > 0.7 or closest.weather_risk > 0.7:
                    risk_flag = "critical"

        deviation = ApplicationTimingDeviation(
            application_id=record.application_id,
            fertilizer_type=record.fertilizer_type,
            application_method=record.application_method,
            actual_date=record.applied_date,
            recommended_date=recommended_date,
            days_difference=days_difference,
            crop_stage_alignment=crop_stage_alignment,
            risk_flag=risk_flag,
        )
        return deviation

    def _select_closest_timing(
        self,
        record: FertilizerApplicationRecord,
        timings: Sequence[ApplicationTiming],
    ) -> Optional[ApplicationTiming]:
        if not timings:
            return None
        closest = None
        smallest_delta = None
        for timing in timings:
            delta_days = abs((record.applied_date - timing.recommended_date).days)
            if smallest_delta is None or delta_days < smallest_delta:
                smallest_delta = delta_days
                closest = timing
        return closest

    def _determine_nutrient_key(self, record: FertilizerApplicationRecord) -> str:
        if record.target_nutrient:
            return record.target_nutrient.lower()
        return record.fertilizer_type.lower()

    def _evaluate_soil_sufficiency(
        self,
        soil_tests: Sequence[SoilTestResult],
        requirements: Dict[str, float],
    ) -> Dict[str, str]:
        latest_values = self._extract_latest_soil_levels(soil_tests)
        sufficiency: Dict[str, str] = {}
        for nutrient in requirements.keys():
            nutrient_lower = nutrient.lower()
            level = latest_values.get(nutrient_lower)
            if level is None:
                sufficiency[nutrient] = "unknown"
            else:
                threshold = self._lookup_sufficiency_threshold(nutrient_lower)
                if level >= threshold:
                    sufficiency[nutrient] = "adequate"
                elif level >= threshold * 0.8:
                    sufficiency[nutrient] = "marginal"
                else:
                    sufficiency[nutrient] = "deficient"
        return sufficiency

    def _extract_latest_soil_levels(
        self,
        soil_tests: Sequence[SoilTestResult],
    ) -> Dict[str, float]:
        latest_levels: Dict[str, Tuple[date, float]] = {}
        for test in soil_tests:
            for nutrient, value in test.nutrient_levels.items():
                nutrient_lower = nutrient.lower()
                existing = latest_levels.get(nutrient_lower)
                if existing is None or test.sample_date > existing[0]:
                    latest_levels[nutrient_lower] = (test.sample_date, value)

        flattened: Dict[str, float] = {}
        for nutrient, pair in latest_levels.items():
            flattened[nutrient] = pair[1]
        return flattened

    def _lookup_sufficiency_threshold(self, nutrient: str) -> float:
        thresholds = {
            "nitrogen": 25.0,
            "phosphorus": 20.0,
            "potassium": 120.0,
            "micronutrients": 1.0,
            "sulfur": 15.0,
            "zinc": 1.0,
            "boron": 0.8,
        }
        return thresholds.get(nutrient, 20.0)

    def _build_nutrient_observations(
        self,
        nutrient_balance: Dict[str, float],
        soil_flags: Dict[str, str],
    ) -> List[str]:
        observations: List[str] = []
        for nutrient, balance in nutrient_balance.items():
            soil_status = soil_flags.get(nutrient, "unknown")
            message = f"{nutrient.title()} balance {balance:.2f} with soil status {soil_status}"
            observations.append(message)
        return observations

    def _calculate_synchronization_score(
        self,
        nutrient_balance: Dict[str, float],
        soil_flags: Dict[str, str],
        optimization_result: Optional[TimingOptimizationResult],
    ) -> float:
        if not nutrient_balance:
            return 1.0

        total_score = 0.0
        count = 0
        for nutrient, balance in nutrient_balance.items():
            score = 1.0
            if balance > 1.2:
                score -= 0.2
            elif balance < 0.85:
                score -= 0.3

            soil_status = soil_flags.get(nutrient)
            if soil_status == "deficient":
                score -= 0.3
            elif soil_status == "marginal":
                score -= 0.15
            elif soil_status == "adequate":
                score += 0.05

            if optimization_result is not None and optimization_result.optimal_timings:
                score += 0.05

            if score < 0.0:
                score = 0.0
            if score > 1.0:
                score = 1.0

            total_score += score
            count += 1

        if count == 0:
            return 1.0
        return total_score / count

    def _calculate_yield_trend(self, yield_history: Sequence[YieldRecord]) -> float:
        if len(yield_history) < 2:
            return 0.0

        sorted_history = self._sort_yield_history(yield_history)
        first = sorted_history[0].yield_per_acre
        last = sorted_history[-1].yield_per_acre
        if first == 0:
            return 0.0
        return ((last - first) / first) * 100.0

    def _estimate_cost_effectiveness(
        self,
        yield_history: Sequence[YieldRecord],
        program: Sequence[FertilizerApplicationRecord],
    ) -> float:
        if not yield_history or not program:
            return 0.5

        latest_yield = self._get_latest_yield_record(yield_history)
        target = latest_yield.target_yield_per_acre
        if target is None or target == 0:
            target = latest_yield.yield_per_acre
        yield_ratio = latest_yield.yield_per_acre / target
        if yield_ratio > 1.2:
            yield_ratio = 1.2
        if yield_ratio < 0.5:
            yield_ratio = 0.5

        total_amount = 0.0
        for record in program:
            total_amount += record.amount_lbs_per_acre
        average_rate = total_amount / len(program)
        if average_rate > 250:
            cost_penalty = 0.3
        elif average_rate > 150:
            cost_penalty = 0.2
        else:
            cost_penalty = 0.0

        cost_effectiveness = yield_ratio - cost_penalty
        if cost_effectiveness < 0.0:
            cost_effectiveness = 0.0
        if cost_effectiveness > 1.0:
            cost_effectiveness = 1.0
        return cost_effectiveness

    def _identify_focus_areas(
        self,
        timing: TimingAssessment,
        nutrient: NutrientSynchronizationAssessment,
        yield_trend: float,
    ) -> List[str]:
        focus_areas: List[str] = []
        if timing.on_time_percentage < 0.85:
            focus_areas.append("Improve scheduling reliability")
        if nutrient.synchronization_score < 0.8:
            focus_areas.append("Rebalance nutrient ratios")
        if yield_trend < 0:
            focus_areas.append("Investigate yield limitations")
        if not focus_areas:
            focus_areas.append("Maintain current efficiency practices")
        return focus_areas

    def _sort_yield_history(self, yield_history: Sequence[YieldRecord]) -> List[YieldRecord]:
        return sorted(yield_history, key=self._season_sort_key)

    def _season_sort_key(self, record: YieldRecord):
        season_text = record.season.strip()
        digits: List[str] = []
        for character in season_text:
            if character.isdigit():
                digits.append(character)
        if digits:
            number_string = "".join(digits)
            try:
                return int(number_string)
            except ValueError:
                return season_text
        return season_text

    def _get_latest_yield_record(self, yield_history: Sequence[YieldRecord]) -> YieldRecord:
        sorted_history = self._sort_yield_history(yield_history)
        return sorted_history[-1]

    def _map_application_method(self, method_name: str) -> ApplicationMethod:
        normalized = self._normalize_token(method_name)
        mapping = {
            "broadcast": ApplicationMethod.BROADCAST,
            "broadcast_incorporated": ApplicationMethod.BROADCAST_INCORPORATED,
            "banded": ApplicationMethod.BANDED,
            "side_dress": ApplicationMethod.SIDE_DRESS,
            "sidedress": ApplicationMethod.SIDE_DRESS,
            "foliar": ApplicationMethod.FOLIAR,
            "fertigation": ApplicationMethod.FERTIGATION,
            "injection": ApplicationMethod.INJECTION,
        }
        result = mapping.get(normalized)
        if result is not None:
            return result
        logger.debug("Unknown application method '%s', defaulting to broadcast", method_name)
        return ApplicationMethod.BROADCAST

    def _normalize_token(self, value: str) -> str:
        stripped = value.strip().lower()
        builder: List[str] = []
        for character in stripped:
            if character == " " or character == "-":
                builder.append("_")
            else:
                builder.append(character)
        return "".join(builder)

    def _compare_crop_stage(self, actual_stage: Optional[str], recommended_stage: str) -> str:
        if actual_stage is None:
            return "unknown"
        actual_normalized = self._normalize_token(actual_stage)
        recommended_normalized = self._normalize_token(recommended_stage)
        if actual_normalized == recommended_normalized:
            return "aligned"
        return "misaligned"

    def _contains_keyword(self, notes: Sequence[str], keyword: str) -> bool:
        token = keyword.lower()
        for note in notes:
            lowered = note.lower()
            if token in lowered:
                return True
        return False

    def _clamp_ratio(self, value: float) -> float:
        if value < 0.0:
            return 0.0
        if value > 1.0:
            return 1.0
        return value


__all__ = ["FertilizerProgramAnalysisService"]
