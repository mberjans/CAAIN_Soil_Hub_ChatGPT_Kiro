"""Yield potential calculation engine for crop variety recommendations."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


def _clamp_value(value: float, minimum: float, maximum: float) -> float:
    """Clamp numeric value into inclusive range."""
    if value < minimum:
        return minimum
    if value > maximum:
        return maximum
    return value


def _safe_lower(value: Optional[str]) -> Optional[str]:
    """Safely convert string values to lowercase."""
    if value is None:
        return None
    return value.lower()


@dataclass
class YieldPotentialResult:
    """Container for calculated yield potential metrics."""

    baseline_yield: float
    expected_yield: float
    yield_range: Tuple[float, float]
    stability_score: float
    risk_index: float
    confidence: float
    component_breakdown: Dict[str, float] = field(default_factory=dict)
    component_confidences: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)
    data_sources: List[str] = field(default_factory=list)


class YieldPotentialCalculator:
    """Advanced yield potential calculation with multi-factor adjustments."""

    def __init__(self) -> None:
        self.component_weights: Dict[str, float] = {}
        self._initialize_component_weights()
        self._minimum_yield: float = 0.5
        self._maximum_modifier: float = 0.35
        self._minimum_modifier: float = -0.35

    def _initialize_component_weights(self) -> None:
        """Define weighting for yield adjustment components."""
        self.component_weights["baseline"] = 0.30
        self.component_weights["historical_trials"] = 0.22
        self.component_weights["weather_outlook"] = 0.18
        self.component_weights["soil_conditions"] = 0.12
        self.component_weights["management_practices"] = 0.10
        self.component_weights["genetic_traits"] = 0.08

    def calculate(self, variety: Any, context: Optional[Dict[str, Any]]) -> YieldPotentialResult:
        """Calculate yield potential metrics for a variety within the given context."""
        try:
            return self._execute_calculation(variety, context or {})
        except Exception as exc:  # pragma: no cover - defensive fallback
            logger.exception("Yield potential calculation failed: %s", exc)
            breakdown: Dict[str, float] = {}
            confidences: Dict[str, float] = {}
            notes: List[str] = []
            data_sources: List[str] = []
            notes.append("Fallback yield estimate applied due to calculation error.")
            return YieldPotentialResult(
                baseline_yield=4.0,
                expected_yield=4.0,
                yield_range=(3.2, 4.8),
                stability_score=0.5,
                risk_index=0.5,
                confidence=0.4,
                component_breakdown=breakdown,
                component_confidences=confidences,
                notes=notes,
                data_sources=data_sources
            )

    def _execute_calculation(self, variety: Any, context: Dict[str, Any]) -> YieldPotentialResult:
        """Perform detailed calculation with component adjustments."""
        baseline_value, baseline_confidence, baseline_notes, baseline_sources = self._calculate_baseline(variety)

        component_breakdown: Dict[str, float] = {}
        component_confidences: Dict[str, float] = {}
        notes: List[str] = []
        data_sources: List[str] = []

        expected_yield = baseline_value
        combined_confidence = self.component_weights["baseline"] * baseline_confidence

        modifier, confidence, explanation, sources = self._calculate_historical_adjustment(variety, context)
        component_breakdown["historical_trials"] = modifier
        component_confidences["historical_trials"] = confidence
        expected_yield *= 1.0 + modifier
        combined_confidence += confidence * self.component_weights["historical_trials"]
        if explanation:
            notes.append(explanation)
        self._extend_sources(data_sources, sources)

        modifier, confidence, explanation, sources = self._calculate_weather_adjustment(context)
        component_breakdown["weather_outlook"] = modifier
        component_confidences["weather_outlook"] = confidence
        expected_yield *= 1.0 + modifier
        combined_confidence += confidence * self.component_weights["weather_outlook"]
        if explanation:
            notes.append(explanation)
        self._extend_sources(data_sources, sources)

        modifier, confidence, explanation, sources = self._calculate_soil_adjustment(context)
        component_breakdown["soil_conditions"] = modifier
        component_confidences["soil_conditions"] = confidence
        expected_yield *= 1.0 + modifier
        combined_confidence += confidence * self.component_weights["soil_conditions"]
        if explanation:
            notes.append(explanation)
        self._extend_sources(data_sources, sources)

        modifier, confidence, explanation, sources = self._calculate_management_adjustment(context)
        component_breakdown["management_practices"] = modifier
        component_confidences["management_practices"] = confidence
        expected_yield *= 1.0 + modifier
        combined_confidence += confidence * self.component_weights["management_practices"]
        if explanation:
            notes.append(explanation)
        self._extend_sources(data_sources, sources)

        modifier, confidence, explanation, sources = self._calculate_genetic_adjustment(variety)
        component_breakdown["genetic_traits"] = modifier
        component_confidences["genetic_traits"] = confidence
        expected_yield *= 1.0 + modifier
        combined_confidence += confidence * self.component_weights["genetic_traits"]
        if explanation:
            notes.append(explanation)
        self._extend_sources(data_sources, sources)

        expected_yield = self._ensure_minimum_yield(expected_yield)

        stability_score = self._calculate_stability(variety, component_confidences)
        risk_index = self._calculate_risk_index(component_breakdown, stability_score, context)
        combined_confidence = _clamp_value(combined_confidence, 0.05, 0.98)

        risk_buffer = max(0.12, risk_index * 0.25)
        lowest_possible = expected_yield * (1.0 - risk_buffer)
        highest_possible = expected_yield * (1.0 + risk_buffer)
        yield_range = (self._ensure_minimum_yield(lowest_possible), max(expected_yield, highest_possible))

        for entry in baseline_notes:
            notes.append(entry)
        self._extend_sources(data_sources, baseline_sources)

        return YieldPotentialResult(
            baseline_yield=baseline_value,
            expected_yield=expected_yield,
            yield_range=yield_range,
            stability_score=stability_score,
            risk_index=risk_index,
            confidence=combined_confidence,
            component_breakdown=component_breakdown,
            component_confidences=component_confidences,
            notes=notes,
            data_sources=data_sources
        )

    def score_from_result(self, result: YieldPotentialResult) -> float:
        """Normalize yield potential result into recommendation score."""
        if result.expected_yield <= 0.0:
            return 0.4

        normalized_gain = 0.0
        denominator = result.baseline_yield if result.baseline_yield > 0.0 else 1.0
        delta = result.expected_yield - denominator
        normalized_gain = delta / denominator
        normalized_gain = _clamp_value(normalized_gain, -0.4, 0.6)

        score = 0.55 + normalized_gain * 0.25
        score += (result.stability_score - 0.5) * 0.3
        score += (result.confidence - 0.5) * 0.2
        score -= result.risk_index * 0.2
        score = _clamp_value(score, 0.0, 1.0)
        return score

    def build_prediction_payload(self, result: YieldPotentialResult) -> Dict[str, Any]:
        """Create performance prediction payload for API consumers."""
        payload: Dict[str, Any] = {}
        payload["expected_yield"] = result.expected_yield
        payload["baseline_yield"] = result.baseline_yield
        payload["predicted_yield_range"] = result.yield_range
        payload["yield_confidence"] = result.confidence
        payload["stability_score"] = result.stability_score
        payload["risk_index"] = result.risk_index
        payload["contributing_factors"] = {}
        for key, value in result.component_breakdown.items():
            payload["contributing_factors"][key] = value
        payload["factor_confidence"] = {}
        for key, value in result.component_confidences.items():
            payload["factor_confidence"][key] = value
        payload["notes"] = []
        for note in result.notes:
            payload["notes"].append(note)
        payload["data_sources"] = []
        for source in result.data_sources:
            payload["data_sources"].append(source)
        return payload

    def _calculate_baseline(self, variety: Any) -> Tuple[float, float, List[str], List[str]]:
        """Determine baseline yield from variety information."""
        baseline_value = 4.0
        confidence = 0.5
        notes: List[str] = []
        sources: List[str] = []

        yield_potential = getattr(variety, "yield_potential", None)
        if yield_potential and getattr(yield_potential, "average_yield_range", None):
            try:
                avg_range = yield_potential.average_yield_range
                if len(avg_range) == 2:
                    avg_min = avg_range[0]
                    avg_max = avg_range[1]
                    if isinstance(avg_min, (int, float)) and isinstance(avg_max, (int, float)):
                        baseline_value = (float(avg_min) + float(avg_max)) / 2.0
                        confidence = 0.7
                        sources.append("variety_record")
                        notes.append("Baseline yield derived from variety yield potential range.")
                potential_range = getattr(yield_potential, "potential_yield_range", None)
                if potential_range and len(potential_range) == 2:
                    high_value = potential_range[1]
                    if isinstance(high_value, (int, float)):
                        difference = float(high_value) - baseline_value
                        if difference > 0:
                            bonus = difference / max(baseline_value, 1.0)
                            confidence = _clamp_value(confidence + bonus * 0.05, 0.0, 0.9)
                            notes.append("Potential yield range indicates upside opportunity.")
            except Exception as exc:
                logger.debug("Baseline calculation warning: %s", exc)

        stability_rating = None
        if yield_potential:
            stability_rating = getattr(yield_potential, "yield_stability_rating", None)
        if stability_rating is not None:
            normalized = float(stability_rating) / 5.0
            confidence += normalized * 0.05
            notes.append("Yield stability rating incorporated into baseline confidence.")

        baseline_value = self._ensure_minimum_yield(baseline_value)
        confidence = _clamp_value(confidence, 0.2, 0.9)
        return baseline_value, confidence, notes, sources

    def _calculate_historical_adjustment(
        self,
        variety: Any,
        context: Dict[str, Any]
    ) -> Tuple[float, float, Optional[str], List[str]]:
        """Adjust yield based on historical regional performance."""
        regional_data = getattr(variety, "regional_performance_data", None)
        if not regional_data:
            return 0.0, 0.25, None, []

        targets = self._extract_target_regions(context)
        total_weight = 0.0
        weighted_delta = 0.0
        trials_count = 0
        sources: List[str] = []
        sources.append("regional_trials")
        explanation: Optional[str] = None

        for entry in regional_data:
            region_name = _safe_lower(getattr(entry, "region_name", None))
            climate_zone = _safe_lower(getattr(entry, "climate_zone", None))
            performance_index = getattr(entry, "performance_index", None)
            average_yield = getattr(entry, "average_yield", None)
            entry_trials = getattr(entry, "trials_count", None)
            if entry_trials is None:
                entry_trials = 1
            if entry_trials < 1:
                entry_trials = 1
            weight = float(entry_trials)
            match_score = self._calculate_region_match(region_name, climate_zone, targets)
            if match_score <= 0.0:
                continue
            total_weight += weight * match_score
            trials_count += entry_trials
            if isinstance(performance_index, (int, float)):
                weighted_delta += (float(performance_index) - 0.5) * weight * match_score
            elif isinstance(average_yield, (int, float)):
                baseline = getattr(variety, "yield_potential", None)
                baseline_avg = 0.0
                if baseline and getattr(baseline, "average_yield_range", None):
                    avg_range = baseline.average_yield_range
                    if len(avg_range) == 2:
                        baseline_avg = (float(avg_range[0]) + float(avg_range[1])) / 2.0
                if baseline_avg > 0.0:
                    weighted_delta += ((float(average_yield) - baseline_avg) / baseline_avg) * weight * match_score
            if entry_trials >= 5:
                if explanation is None:
                    explanation = "Multiple trials validate historical yield results."
                else:
                    explanation = explanation + " Multiple trials validate historical yield results."

        if total_weight == 0.0:
            return 0.0, 0.3, explanation, sources

        modifier = weighted_delta / total_weight
        modifier = _clamp_value(modifier, self._minimum_modifier, self._maximum_modifier)
        confidence = _clamp_value(0.35 + trials_count * 0.02, 0.3, 0.85)
        if modifier > 0.02:
            if explanation:
                explanation = explanation + " Historical trials indicate above-average performance in region."
            else:
                explanation = "Historical trials indicate above-average performance in region."
        elif modifier < -0.02:
            if explanation:
                explanation = explanation + " Historical trials indicate below-average performance in region."
            else:
                explanation = "Historical trials indicate below-average performance in region."
        elif trials_count > 0 and explanation is None:
            explanation = "Historical trials show consistent performance in region."
        return modifier, confidence, explanation, sources

    def _calculate_weather_adjustment(
        self,
        context: Dict[str, Any]
    ) -> Tuple[float, float, Optional[str], List[str]]:
        """Adjust yield based on seasonal weather outlook."""
        forecast = context.get("seasonal_forecast") if isinstance(context, dict) else None
        if not isinstance(forecast, dict):
            return 0.0, 0.3, None, []

        modifier = 0.0
        confidence = 0.35
        notes: List[str] = []
        sources: List[str] = []
        sources.append("weather_outlook")

        precipitation_outlook = forecast.get("precipitation_outlook")
        temperature_outlook = forecast.get("temperature_outlook")
        gdd_outlook = forecast.get("gdd_outlook")

        if isinstance(precipitation_outlook, (int, float)):
            modifier += float(precipitation_outlook) * 0.4
            if precipitation_outlook < -0.1:
                notes.append("Dry seasonal outlook may limit yield potential.")
            elif precipitation_outlook > 0.1:
                notes.append("Above-average precipitation outlook supports yield potential.")
        if isinstance(temperature_outlook, (int, float)):
            modifier += float(temperature_outlook) * 0.25
            if temperature_outlook > 0.15:
                notes.append("Warmer temperatures could accelerate development and increase stress.")
            elif temperature_outlook < -0.1:
                notes.append("Cool temperatures may delay maturity but reduce heat stress.")
        if isinstance(gdd_outlook, (int, float)):
            modifier += float(gdd_outlook) * 0.15

        weather_risk = forecast.get("weather_risk_index")
        if isinstance(weather_risk, (int, float)):
            confidence -= float(weather_risk) * 0.2
            notes.append("Weather risk index incorporated into yield confidence.")

        modifier = _clamp_value(modifier, self._minimum_modifier, self._maximum_modifier)
        confidence = _clamp_value(confidence, 0.2, 0.75)
        explanation = None
        if len(notes) > 0:
            explanation = "Weather outlook adjustments applied." if modifier != 0.0 else "Weather outlook considered with neutral impact."
        return modifier, confidence, explanation, sources

    def _calculate_soil_adjustment(
        self,
        context: Dict[str, Any]
    ) -> Tuple[float, float, Optional[str], List[str]]:
        """Adjust yield based on soil characteristics."""
        soil_profile = context.get("soil_profile") if isinstance(context, dict) else None
        if not isinstance(soil_profile, dict):
            return 0.0, 0.3, None, []

        modifier = 0.0
        confidence = 0.4
        notes: List[str] = []
        sources: List[str] = []
        sources.append("soil_profile")

        organic_matter = soil_profile.get("organic_matter")
        if isinstance(organic_matter, (int, float)):
            if organic_matter >= 4.0:
                modifier += 0.05
                notes.append("High organic matter supports moisture retention and nutrient availability.")
            elif organic_matter <= 2.0:
                modifier -= 0.05
                notes.append("Low organic matter may limit nutrient availability.")

        drainage = soil_profile.get("drainage")
        if isinstance(drainage, str):
            lowered = drainage.lower()
            if lowered in ("poor", "very_poor"):
                modifier -= 0.08
                notes.append("Poor drainage increases yield risk.")
            elif lowered in ("well", "moderately_well"):
                modifier += 0.03

        ph = soil_profile.get("ph")
        if isinstance(ph, (int, float)):
            if ph < 5.8 or ph > 7.6:
                modifier -= 0.06
                notes.append("Soil pH outside optimal range may limit nutrient uptake.")

        compaction = soil_profile.get("compaction")
        if isinstance(compaction, str) and compaction.lower() in ("high", "severe"):
            modifier -= 0.05
            notes.append("Soil compaction may restrict root development.")

        fertility_rating = soil_profile.get("fertility_rating")
        if isinstance(fertility_rating, str):
            lowered = fertility_rating.lower()
            if lowered == "high":
                modifier += 0.04
            elif lowered == "low":
                modifier -= 0.04

        modifier = _clamp_value(modifier, self._minimum_modifier, self._maximum_modifier)
        confidence = _clamp_value(confidence, 0.25, 0.65)
        explanation = None
        if len(notes) > 0:
            explanation = "Soil profile adjustments applied."
        return modifier, confidence, explanation, sources

    def _calculate_management_adjustment(
        self,
        context: Dict[str, Any]
    ) -> Tuple[float, float, Optional[str], List[str]]:
        """Adjust yield based on management practices."""
        management = context.get("management_practices") if isinstance(context, dict) else None
        if not isinstance(management, dict):
            return 0.0, 0.3, None, []

        modifier = 0.0
        confidence = 0.35
        notes: List[str] = []
        sources: List[str] = []
        sources.append("management_profile")

        irrigation = management.get("irrigation")
        if isinstance(irrigation, str):
            lowered = irrigation.lower()
            if lowered == "full":
                modifier += 0.05
                notes.append("Reliable irrigation increases yield stability.")
            elif lowered == "limited":
                modifier -= 0.03
            elif lowered == "rainfed":
                modifier -= 0.05

        fertility_program = management.get("fertility_program")
        if isinstance(fertility_program, str):
            lowered = fertility_program.lower()
            if lowered == "advanced":
                modifier += 0.04
            elif lowered == "minimal":
                modifier -= 0.04

        crop_rotation = management.get("crop_rotation")
        if isinstance(crop_rotation, str) and crop_rotation.lower() == "continuous_monocrop":
            modifier -= 0.03
            notes.append("Continuous monocropping may reduce yield due to pest pressure.")

        precision_ag = management.get("precision_agriculture")
        if isinstance(precision_ag, bool) and precision_ag:
            modifier += 0.02

        modifier = _clamp_value(modifier, self._minimum_modifier, self._maximum_modifier)
        confidence = _clamp_value(confidence, 0.25, 0.6)
        explanation = None
        if len(notes) > 0:
            explanation = "Management practices influence yield adjustments."
        return modifier, confidence, explanation, sources

    def _calculate_genetic_adjustment(self, variety: Any) -> Tuple[float, float, Optional[str], List[str]]:
        """Adjust yield based on genetic and trait data."""
        modifier = 0.0
        confidence = 0.3
        notes: List[str] = []
        sources: List[str] = []
        sources.append("genetic_profile")

        yield_potential = getattr(variety, "yield_potential", None)
        if yield_potential and getattr(yield_potential, "yield_stability_rating", None) is not None:
            stability_rating = float(yield_potential.yield_stability_rating)
            modifier += (stability_rating - 3.0) * 0.02
            confidence += 0.05
            notes.append("Yield stability rating incorporated into genetic adjustment.")

        disease_resistance = getattr(variety, "disease_resistance", None)
        if disease_resistance and getattr(disease_resistance, "rust_resistance", None):
            rust_values = disease_resistance.rust_resistance.values()
            total = 0.0
            count = 0
            for value in rust_values:
                if isinstance(value, (int, float)):
                    total += float(value)
                    count += 1
            if count > 0:
                average = total / count
                modifier += (average - 3.0) * 0.015
                confidence += 0.05
                notes.append("Strong disease resistance supports yield consistency.")

        abiotic = getattr(variety, "abiotic_stress_tolerances", None)
        if abiotic and getattr(abiotic, "drought_tolerance", None):
            drought = abiotic.drought_tolerance
            if isinstance(drought, (int, float)) and drought >= 4:
                modifier += 0.025
                notes.append("Drought tolerance reduces yield risk in dry seasons.")

        trait_stack = getattr(variety, "trait_stack", None)
        if trait_stack:
            count = 0
            for _ in trait_stack:
                count += 1
            if count >= 2:
                modifier += 0.02
                notes.append("Stacked traits enhance resilience and yield potential.")

        modifier = _clamp_value(modifier, self._minimum_modifier, self._maximum_modifier)
        confidence = _clamp_value(confidence, 0.25, 0.65)
        explanation = None
        if len(notes) > 0:
            explanation = "Genetic attributes adjusted yield expectation."
        return modifier, confidence, explanation, sources

    def _calculate_stability(
        self,
        variety: Any,
        component_confidences: Dict[str, float]
    ) -> float:
        """Evaluate yield stability based on available information."""
        stability = 0.5
        yield_potential = getattr(variety, "yield_potential", None)
        if yield_potential and getattr(yield_potential, "yield_stability_rating", None) is not None:
            rating = float(yield_potential.yield_stability_rating)
            stability = rating / 5.0
        historical_conf = component_confidences.get("historical_trials")
        if historical_conf is not None:
            stability += (historical_conf - 0.5) * 0.2
        weather_conf = component_confidences.get("weather_outlook")
        if weather_conf is not None:
            stability -= (0.5 - weather_conf) * 0.1
        stability = _clamp_value(stability, 0.0, 1.0)
        return stability

    def _calculate_risk_index(
        self,
        component_breakdown: Dict[str, float],
        stability_score: float,
        context: Dict[str, Any]
    ) -> float:
        """Calculate yield risk index combining components and contextual risk."""
        risk_index = 1.0 - stability_score
        weather_modifier = component_breakdown.get("weather_outlook")
        if weather_modifier is not None and weather_modifier < 0:
            risk_index += abs(weather_modifier) * 0.6
        management_modifier = component_breakdown.get("management_practices")
        if management_modifier is not None and management_modifier < 0:
            risk_index += abs(management_modifier) * 0.4
        climate_risks = context.get("climate_risks") if isinstance(context, dict) else None
        if isinstance(climate_risks, dict):
            drought_risk = climate_risks.get("drought_risk")
            if isinstance(drought_risk, (int, float)):
                risk_index += float(drought_risk) * 0.2
            extreme_events = climate_risks.get("extreme_event_risk")
            if isinstance(extreme_events, (int, float)):
                risk_index += float(extreme_events) * 0.15
        risk_index = _clamp_value(risk_index, 0.0, 1.0)
        return risk_index

    def _extend_sources(self, target: List[str], sources: List[str]) -> None:
        """Add new sources to accumulator without duplicates."""
        for source in sources:
            if source not in target:
                target.append(source)

    def _ensure_minimum_yield(self, value: float) -> float:
        """Ensure yield output does not drop below practical minimum."""
        if value < self._minimum_yield:
            return self._minimum_yield
        return value

    def _extract_target_regions(self, context: Dict[str, Any]) -> List[str]:
        """Collect possible region identifiers from context."""
        targets: List[str] = []
        keys = ["region", "region_name", "state", "province", "county", "climate_zone", "preferred_regions"]
        for key in keys:
            value = context.get(key) if isinstance(context, dict) else None
            if value is None:
                continue
            if isinstance(value, str):
                lowered = value.lower()
                targets.append(lowered)
            elif isinstance(value, (list, tuple)):
                index = 0
                while index < len(value):
                    item = value[index]
                    if isinstance(item, str):
                        targets.append(item.lower())
                    index += 1
        return targets

    def _calculate_region_match(
        self,
        region_name: Optional[str],
        climate_zone: Optional[str],
        targets: List[str]
    ) -> float:
        """Score how well trial region aligns with target context."""
        if len(targets) == 0:
            return 0.5
        match_score = 0.0
        if region_name:
            lowered = region_name.lower()
            index = 0
            while index < len(targets):
                if lowered == targets[index]:
                    match_score += 0.7
                    break
                index += 1
        if climate_zone:
            lowered_zone = climate_zone.lower()
            index = 0
            while index < len(targets):
                if lowered_zone == targets[index]:
                    match_score += 0.3
                    break
                index += 1
        return match_score


__all__ = ["YieldPotentialCalculator", "YieldPotentialResult"]
