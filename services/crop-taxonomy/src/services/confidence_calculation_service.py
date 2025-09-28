"""Advanced confidence scoring and uncertainty quantification for variety recommendations."""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


@dataclass
class ConfidenceAssessment:
    """Container for detailed confidence scoring outputs."""

    overall_confidence: float
    confidence_interval: Tuple[float, float]
    uncertainty_score: float
    data_quality_score: float
    factor_breakdown: Dict[str, float] = field(default_factory=dict)
    reliability_indicators: Dict[str, str] = field(default_factory=dict)
    explanations: List[str] = field(default_factory=list)


class ConfidenceCalculationService:
    """Service responsible for advanced confidence scoring and uncertainty analysis."""

    def __init__(self) -> None:
        self._factor_weights: Dict[str, float] = {}
        self._initialize_weights()
        self._minimum_confidence: float = 0.05
        self._maximum_confidence: float = 0.99

    def _initialize_weights(self) -> None:
        """Initialize weighting for each confidence factor."""
        self._factor_weights["data_quality"] = 0.30
        self._factor_weights["source_reliability"] = 0.20
        self._factor_weights["regional_validation"] = 0.20
        self._factor_weights["temporal_relevance"] = 0.15
        self._factor_weights["performance_consistency"] = 0.15

    def calculate(
        self,
        variety: Any,
        score_data: Dict[str, Any],
        regional_context: Optional[Dict[str, Any]] = None,
        performance_prediction: Optional[Any] = None,
        risk_assessment: Optional[Any] = None
    ) -> ConfidenceAssessment:
        """Calculate detailed confidence scores and uncertainty metrics."""

        try:
            factor_scores: Dict[str, float] = {}
            factor_scores["data_quality"] = self._evaluate_data_quality(variety)
            factor_scores["source_reliability"] = self._evaluate_source_reliability(variety)
            factor_scores["regional_validation"] = self._evaluate_regional_validation(variety, regional_context)
            factor_scores["temporal_relevance"] = self._evaluate_temporal_relevance(variety)
            factor_scores["performance_consistency"] = self._evaluate_performance_consistency(
                score_data,
                performance_prediction,
                risk_assessment
            )

            overall_confidence = self._combine_scores(factor_scores)
            sample_size = self._estimate_sample_size(variety, score_data)
            confidence_interval = self._build_confidence_interval(overall_confidence, sample_size)
            uncertainty_score = self._calculate_uncertainty(overall_confidence, confidence_interval)
            reliability_indicators = self._build_reliability_indicators(factor_scores, sample_size)
            explanations = self._build_explanations(factor_scores, reliability_indicators)

            data_quality_score = factor_scores.get("data_quality", 0.0)

            return ConfidenceAssessment(
                overall_confidence=overall_confidence,
                confidence_interval=confidence_interval,
                uncertainty_score=uncertainty_score,
                data_quality_score=data_quality_score,
                factor_breakdown=factor_scores,
                reliability_indicators=reliability_indicators,
                explanations=explanations
            )
        except Exception as exc:
            logger.exception("Failed to calculate confidence score: %s", exc)
            fallback_interval: Tuple[float, float] = (0.2, 0.8)
            fallback_breakdown: Dict[str, float] = {}
            fallback_indicators: Dict[str, str] = {}
            fallback_explanations: List[str] = []
            fallback_explanations.append(
                "Confidence defaulted due to calculation error. Manual review recommended."
            )
            return ConfidenceAssessment(
                overall_confidence=0.5,
                confidence_interval=fallback_interval,
                uncertainty_score=0.5,
                data_quality_score=0.5,
                factor_breakdown=fallback_breakdown,
                reliability_indicators=fallback_indicators,
                explanations=fallback_explanations
            )

    def _evaluate_data_quality(self, variety: Any) -> float:
        """Evaluate data completeness and coverage for the variety."""
        total_checks = 0
        achieved_checks = 0

        checks = [
            "yield_potential",
            "disease_resistance",
            "disease_resistances",
            "abiotic_stress_tolerances",
            "stress_tolerances",
            "market_attributes",
            "regional_performance_data",
            "seed_companies",
            "quality_attributes"
        ]

        index = 0
        while index < len(checks):
            attribute_name = checks[index]
            total_checks += 1
            value = getattr(variety, attribute_name, None)
            if self._has_meaningful_data(value):
                achieved_checks += 1
            index += 1

        if total_checks == 0:
            return 0.0

        score = achieved_checks / float(total_checks)
        return max(0.0, min(1.0, score))

    def _evaluate_source_reliability(self, variety: Any) -> float:
        """Evaluate reliability based on data sources and validation."""
        score = 0.5

        seed_companies = getattr(variety, "seed_companies", None)
        count = self._safe_length(seed_companies)
        if count > 0:
            score += 0.1
            if count >= 2:
                score += 0.05
            if count >= 3:
                score += 0.05

        breeder = getattr(variety, "breeder_company", None)
        if breeder:
            score += 0.05

        data_quality_flag = getattr(variety, "data_quality", None)
        if isinstance(data_quality_flag, str):
            lower_value = data_quality_flag.lower()
            if lower_value == "high":
                score += 0.15
            elif lower_value == "medium":
                score += 0.05
            elif lower_value == "low":
                score -= 0.05

        validation_notes = getattr(variety, "validation_notes", None)
        if validation_notes:
            score += 0.05

        regional_data = getattr(variety, "regional_performance_data", None)
        if regional_data:
            trials_total = 0
            index = 0
            for _ in regional_data:
                index += 1
            if index > 0:
                trials_total = self._count_trials(regional_data)
            if trials_total >= 10:
                score += 0.1
            elif trials_total >= 5:
                score += 0.05

        return max(0.0, min(1.0, score))

    def _evaluate_regional_validation(
        self,
        variety: Any,
        regional_context: Optional[Dict[str, Any]]
    ) -> float:
        """Evaluate how well the variety is validated for the target region."""
        if regional_context is None:
            return 0.5

        region_targets = []
        keys = ["region", "region_name", "state", "province", "county", "climate_zone"]
        index = 0
        while index < len(keys):
            context_value = regional_context.get(keys[index]) if isinstance(regional_context, dict) else None
            if context_value:
                region_targets.append(str(context_value).lower())
            index += 1

        if len(region_targets) == 0:
            return 0.5

        regional_data = getattr(variety, "regional_performance_data", None)
        if not regional_data:
            return 0.4

        matches = 0
        total_entries = 0
        for entry in regional_data:
            total_entries += 1
            entry_region = self._read_attribute(entry, "region_name")
            entry_zone = self._read_attribute(entry, "climate_zone")
            if entry_region:
                entry_region_lower = entry_region.lower()
                for target in region_targets:
                    if entry_region_lower == target:
                        matches += 1
                        break
            if entry_zone:
                entry_zone_lower = entry_zone.lower()
                for target in region_targets:
                    if entry_zone_lower == target:
                        matches += 1
                        break

        if total_entries == 0:
            return 0.4

        match_ratio = matches / float(total_entries)
        base_score = 0.4 + match_ratio * 0.6
        return max(0.0, min(1.0, base_score))

    def _evaluate_temporal_relevance(self, variety: Any) -> float:
        """Evaluate freshness of the underlying data."""
        latest_update = None

        updated_at = getattr(variety, "updated_at", None)
        if isinstance(updated_at, datetime):
            latest_update = self._ensure_utc_datetime(updated_at)

        seed_companies = getattr(variety, "seed_companies", None)
        if seed_companies:
            for entry in seed_companies:
                entry_update = getattr(entry, "last_updated", None)
                if isinstance(entry_update, datetime):
                    normalized_entry = self._ensure_utc_datetime(entry_update)
                    if latest_update is None or normalized_entry > latest_update:
                        latest_update = normalized_entry

        release_year = getattr(variety, "release_year", None)
        if latest_update is None and isinstance(release_year, int):
            try:
                constructed = datetime(release_year, 6, 15, tzinfo=UTC)
                latest_update = constructed
            except ValueError:
                latest_update = None

        if latest_update is None:
            return 0.5

        now = datetime.now(UTC)
        delta = now - latest_update
        days = delta.days

        if days <= 365:
            return 0.95
        if days <= 365 * 3:
            return 0.8
        if days <= 365 * 5:
            return 0.65
        return 0.45

    def _evaluate_performance_consistency(
        self,
        score_data: Dict[str, Any],
        performance_prediction: Optional[Any],
        risk_assessment: Optional[Any]
    ) -> float:
        """Evaluate consistency of performance predictions and risk profiles."""
        individual_scores = score_data.get("individual_scores", {}) if isinstance(score_data, dict) else {}

        numerical_scores: List[float] = []
        if isinstance(individual_scores, dict):
            for value in individual_scores.values():
                if isinstance(value, (int, float)):
                    numerical_scores.append(float(value))

        if len(numerical_scores) == 0:
            return 0.5

        mean_value = sum(numerical_scores) / float(len(numerical_scores))
        variance_total = 0.0
        index = 0
        while index < len(numerical_scores):
            difference = numerical_scores[index] - mean_value
            variance_total += difference * difference
            index += 1

        variance = variance_total / float(len(numerical_scores))
        standard_deviation = math.sqrt(variance)

        consistency = 1.0 - min(standard_deviation, 1.0)

        if performance_prediction:
            predicted_range = self._extract_prediction_range(performance_prediction)
            if predicted_range:
                spread = predicted_range[1] - predicted_range[0]
                if spread > 0:
                    spread_adjustment = spread / max(predicted_range[1], 1.0)
                    consistency -= spread_adjustment * 0.2

        if risk_assessment:
            risk_level = self._extract_risk_level(risk_assessment)
            if risk_level:
                normalized = self._normalize_risk_level(risk_level)
                consistency -= normalized * 0.1

        return max(0.0, min(1.0, consistency))

    def _combine_scores(self, factor_scores: Dict[str, float]) -> float:
        """Combine factor scores using configured weights."""
        weighted_total = 0.0
        weight_sum = 0.0

        for factor_name, weight in self._factor_weights.items():
            value = factor_scores.get(factor_name, 0.0)
            weighted_total += value * weight
            weight_sum += weight

        if weight_sum == 0:
            return 0.5

        combined = weighted_total / weight_sum
        combined = max(self._minimum_confidence, min(self._maximum_confidence, combined))
        return combined

    def _estimate_sample_size(self, variety: Any, score_data: Dict[str, Any]) -> int:
        """Estimate effective sample size for uncertainty calculations."""
        sample_size = 1

        regional_data = getattr(variety, "regional_performance_data", None)
        if regional_data:
            sample_size += self._count_trials(regional_data)

        seed_companies = getattr(variety, "seed_companies", None)
        sample_size += self._safe_length(seed_companies)

        individual_scores = score_data.get("individual_scores", {}) if isinstance(score_data, dict) else {}
        if isinstance(individual_scores, dict):
            score_count = 0
            for _ in individual_scores:
                score_count += 1
            sample_size += score_count

        return max(sample_size, 1)

    def _build_confidence_interval(self, mean: float, sample_size: int) -> Tuple[float, float]:
        """Construct a simple confidence interval around the confidence estimate."""
        adjusted_size = max(sample_size, 1)
        variance = mean * (1.0 - mean) / float(adjusted_size + 1)
        margin = 0.0
        if variance > 0.0:
            margin = 1.96 * math.sqrt(variance)

        lower = max(0.0, mean - margin)
        upper = min(1.0, mean + margin)
        return (lower, upper)

    def _calculate_uncertainty(self, confidence: float, interval: Tuple[float, float]) -> float:
        """Translate interval width into an uncertainty score."""
        span = interval[1] - interval[0]
        uncertainty = min(1.0, max(0.0, span * 2.0))
        return uncertainty

    def _build_reliability_indicators(
        self,
        factor_scores: Dict[str, float],
        sample_size: int
    ) -> Dict[str, str]:
        """Build textual reliability indicators for UI consumption."""
        indicators: Dict[str, str] = {}

        for factor, score in factor_scores.items():
            if score >= 0.85:
                indicators[factor] = "strong"
            elif score >= 0.65:
                indicators[factor] = "moderate"
            else:
                indicators[factor] = "limited"

        if sample_size >= 20:
            indicators["sample_depth"] = "extensive"
        elif sample_size >= 10:
            indicators["sample_depth"] = "adequate"
        else:
            indicators["sample_depth"] = "limited"

        return indicators

    def _build_explanations(
        self,
        factor_scores: Dict[str, float],
        indicators: Dict[str, str]
    ) -> List[str]:
        """Generate narrative explanations for confidence results."""
        explanations: List[str] = []

        for factor, score in factor_scores.items():
            descriptor = indicators.get(factor, "moderate")
            if score >= 0.85:
                explanations.append(f"{factor.replace('_', ' ').title()} provides strong support for this recommendation.")
            elif score >= 0.65:
                explanations.append(
                    f"{factor.replace('_', ' ').title()} offers moderate confidence. Additional validation could improve certainty."
                )
            else:
                explanations.append(
                    f"Confidence limited by {factor.replace('_', ' ')}. Consider gathering more region-specific data."
                )

        depth_indicator = indicators.get("sample_depth")
        if depth_indicator == "extensive":
            explanations.append("Extensive trial history reduces uncertainty.")
        elif depth_indicator == "adequate":
            explanations.append("Adequate sample depth supports the recommendation with moderate certainty.")
        else:
            explanations.append("Limited sample depth increases uncertainty; monitor outcomes closely.")

        return explanations

    @staticmethod
    def _has_meaningful_data(value: Any) -> bool:
        """Determine whether the provided value represents meaningful data."""
        if value is None:
            return False

        if isinstance(value, (int, float)):
            return True

        if isinstance(value, str):
            return len(value.strip()) > 0

        if isinstance(value, (list, tuple, set, dict)):
            return len(value) > 0

        return True

    @staticmethod
    def _safe_length(value: Any) -> int:
        """Safely compute the length of a collection."""
        if value is None:
            return 0
        try:
            return len(value)  # type: ignore[arg-type]
        except Exception:
            return 0

    @staticmethod
    def _count_trials(regional_data: Any) -> int:
        """Count total trials from regional performance entries."""
        total_trials = 0
        for entry in regional_data:
            trials_count = getattr(entry, "trials_count", None)
            if isinstance(trials_count, int):
                total_trials += trials_count
            else:
                total_trials += 1
        return total_trials

    @staticmethod
    def _read_attribute(entry: Any, attribute_name: str) -> Optional[str]:
        """Read attribute value from entry handling dicts and objects."""
        value = None
        if hasattr(entry, attribute_name):
            value = getattr(entry, attribute_name)
        elif isinstance(entry, dict):
            value = entry.get(attribute_name)
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def _extract_prediction_range(prediction: Any) -> Optional[Tuple[float, float]]:
        """Extract yield range from prediction structures."""
        range_value = None
        if hasattr(prediction, "predicted_yield_range"):
            range_value = getattr(prediction, "predicted_yield_range")
        elif isinstance(prediction, dict):
            range_value = prediction.get("predicted_yield_range")

        if isinstance(range_value, tuple) and len(range_value) == 2:
            lower = range_value[0]
            upper = range_value[1]
            if isinstance(lower, (int, float)) and isinstance(upper, (int, float)):
                return (float(lower), float(upper))

        return None

    @staticmethod
    def _extract_risk_level(risk_assessment: Any) -> Optional[Any]:
        """Extract risk level from risk assessment structures."""
        if hasattr(risk_assessment, "overall_risk_level"):
            return getattr(risk_assessment, "overall_risk_level")
        if isinstance(risk_assessment, dict):
            return risk_assessment.get("overall_risk_level")
        return None

    @staticmethod
    def _normalize_risk_level(level: Any) -> float:
        """Normalize risk level values into numeric scale."""
        if isinstance(level, (int, float)):
            return max(0.0, min(1.0, float(level)))

        if isinstance(level, str):
            lower_value = level.lower().strip()
            mapping = {
                "very_low": 0.1,
                "low": 0.2,
                "moderate": 0.5,
                "moderately_high": 0.65,
                "high": 0.8,
                "very_high": 0.9
            }
            if lower_value in mapping:
                return mapping[lower_value]

        return 0.5

    @staticmethod
    def _ensure_utc_datetime(value: datetime) -> datetime:
        """Ensure datetime objects are timezone aware in UTC."""
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
