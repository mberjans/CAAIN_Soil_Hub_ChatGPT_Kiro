"""Evidence management service for crop variety explanations.

Provides citation management, credibility scoring, and evidence strength
assessment for variety recommendations.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..models.evidence_models import (
    EvidencePackage,
    EvidenceRecord,
    EvidenceSourceType,
    EvidenceStrengthLevel,
    EvidenceSummary,
)

logger = logging.getLogger(__name__)


class EvidenceManagementService:
    """Manage supporting evidence and references for variety recommendations."""

    def __init__(
        self,
        recency_window_years: int = 5,
        minimum_records: int = 3,
    ) -> None:
        self.recency_window_years = recency_window_years
        self.minimum_records = minimum_records
        self.source_base_scores: Dict[EvidenceSourceType, float] = {}
        self._initialize_source_base_scores()
        self.category_priority: Dict[str, float] = {}
        self._initialize_category_priority()
        self.strength_thresholds: Dict[EvidenceStrengthLevel, float] = {}
        self._initialize_strength_thresholds()

    def build_evidence_package(
        self,
        recommendation: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> EvidencePackage:
        """Build evidence package for a recommendation payload."""
        if recommendation is None:
            raise ValueError("Recommendation payload is required")

        context_data = context or {}
        variety_entries = self._collect_variety_entries(recommendation)
        records: List[EvidenceRecord] = []
        variety_names: List[str] = []

        index = 0
        while index < len(variety_entries):
            entry = variety_entries[index]
            variety_name = entry.get("name")
            if variety_name and variety_name not in variety_names:
                variety_names.append(variety_name)

            entry_records = self._collect_evidence_for_variety(entry, context_data)
            record_index = 0
            while record_index < len(entry_records):
                records.append(entry_records[record_index])
                record_index += 1
            index += 1

        if len(records) < self.minimum_records:
            fallback_records = self._build_fallback_records(variety_entries, context_data)
            fallback_index = 0
            while fallback_index < len(fallback_records):
                records.append(fallback_records[fallback_index])
                fallback_index += 1

        summary = self._aggregate_summary(records)
        coverage_notes = self._compose_coverage_notes(records, summary, context_data)

        package = EvidencePackage()
        package.records = records
        package.summary = summary
        package.variety_names = variety_names
        package.coverage_notes = coverage_notes

        logger.debug(
            "Evidence package created",
            extra={
                "varieties": variety_names,
                "record_count": len(records),
                "average_credibility": summary.average_credibility,
            },
        )
        return package

    def _initialize_source_base_scores(self) -> None:
        """Initialize base credibility scores for each source type."""
        self.source_base_scores[EvidenceSourceType.UNIVERSITY_RESEARCH] = 0.95
        self.source_base_scores[EvidenceSourceType.PEER_REVIEWED_RESEARCH] = 0.97
        self.source_base_scores[EvidenceSourceType.EXTENSION_PUBLICATION] = 0.92
        self.source_base_scores[EvidenceSourceType.GOVERNMENT_AGENCY] = 0.9
        self.source_base_scores[EvidenceSourceType.SEED_COMPANY_DATA] = 0.75
        self.source_base_scores[EvidenceSourceType.FARMER_TESTIMONIAL] = 0.6
        self.source_base_scores[EvidenceSourceType.INTERNAL_ANALYSIS] = 0.7
        self.source_base_scores[EvidenceSourceType.UNKNOWN] = 0.5

    def _initialize_category_priority(self) -> None:
        """Initialize category priority weights for fallback handling."""
        self.category_priority["yield_performance"] = 1.0
        self.category_priority["disease_resistance"] = 0.9
        self.category_priority["climate_adaptation"] = 0.8
        self.category_priority["management_guidance"] = 0.7
        self.category_priority["market_analysis"] = 0.6
        self.category_priority["soil_fit"] = 0.6

    def _initialize_strength_thresholds(self) -> None:
        """Initialize strength level thresholds for scoring."""
        self.strength_thresholds[EvidenceStrengthLevel.HIGH] = 0.8
        self.strength_thresholds[EvidenceStrengthLevel.MEDIUM] = 0.6
        self.strength_thresholds[EvidenceStrengthLevel.LOW] = 0.4
        self.strength_thresholds[EvidenceStrengthLevel.LIMITED] = 0.0

    def _collect_variety_entries(self, recommendation: Dict[str, Any]) -> List[Dict[str, Any]]:
        varieties: List[Dict[str, Any]] = []
        source_keys = [
            "recommended_varieties",
            "variety_recommendations",
            "variety_suggestions",
        ]
        key_index = 0
        while key_index < len(source_keys):
            key = source_keys[key_index]
            entries = recommendation.get(key)
            if isinstance(entries, list):
                entry_index = 0
                while entry_index < len(entries):
                    normalized = self._normalize_variety_entry(entries[entry_index], key)
                    if normalized:
                        varieties.append(normalized)
                    entry_index += 1
            key_index += 1
        return varieties

    def _normalize_variety_entry(self, entry: Any, source_key: str) -> Optional[Dict[str, Any]]:
        if entry is None:
            return None

        raw_data: Dict[str, Any] = {}
        if isinstance(entry, dict):
            for key, value in entry.items():
                raw_data[key] = value
        else:
            attributes = [
                "variety_name",
                "name",
                "variety",
                "overall_score",
                "confidence_level",
                "yield_potential_percentile",
                "disease_resistances",
                "management_recommendations",
                "data_sources",
                "evidence",
            ]
            attr_index = 0
            while attr_index < len(attributes):
                attr = attributes[attr_index]
                if hasattr(entry, attr):
                    raw_data[attr] = getattr(entry, attr)
                attr_index += 1

        normalized: Dict[str, Any] = {}
        normalized["source_key"] = source_key
        normalized["raw"] = raw_data
        normalized["name"] = self._extract_variety_name(raw_data)
        normalized["confidence_level"] = self._extract_float(raw_data.get("confidence_level"))
        normalized["overall_score"] = self._extract_float(raw_data.get("overall_score"))
        normalized["yield_percentile"] = self._extract_float(raw_data.get("yield_potential_percentile"))
        return normalized

    def _extract_variety_name(self, data: Dict[str, Any]) -> Optional[str]:
        preferred_keys = ["variety_name", "name", "variety_code"]
        key_index = 0
        while key_index < len(preferred_keys):
            key = preferred_keys[key_index]
            value = data.get(key)
            if isinstance(value, str) and len(value.strip()) > 0:
                return value.strip()
            key_index += 1

        nested = data.get("variety")
        if isinstance(nested, dict):
            nested_keys = ["variety_name", "name", "display_name"]
            nested_index = 0
            while nested_index < len(nested_keys):
                nested_key = nested_keys[nested_index]
                nested_value = nested.get(nested_key)
                if isinstance(nested_value, str) and len(nested_value.strip()) > 0:
                    return nested_value.strip()
                nested_index += 1
        return None

    def _extract_float(self, value: Any) -> Optional[float]:
        if isinstance(value, (int, float)):
            return float(value)
        return None

    def _collect_evidence_for_variety(
        self,
        variety_entry: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[EvidenceRecord]:
        records: List[EvidenceRecord] = []
        raw_data = variety_entry.get("raw", {})
        variety_name = variety_entry.get("name")

        explicit_sources = self._extract_explicit_sources(raw_data)
        source_index = 0
        while source_index < len(explicit_sources):
            source_payload = explicit_sources[source_index]
            record = self._build_record_from_source(
                source_payload,
                variety_name,
                raw_data,
                context,
            )
            if record:
                records.append(record)
            source_index += 1

        inferred_records = self._generate_inferred_records(
            variety_entry,
            raw_data,
            context,
        )
        inferred_index = 0
        while inferred_index < len(inferred_records):
            records.append(inferred_records[inferred_index])
            inferred_index += 1

        return records

    def _extract_explicit_sources(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        sources: List[Dict[str, Any]] = []
        candidate_keys = [
            "evidence_sources",
            "supporting_evidence",
            "sources",
            "references",
            "research_references",
            "trial_sources",
            "extension_documents",
            "seed_company_documents",
        ]
        key_index = 0
        while key_index < len(candidate_keys):
            key = candidate_keys[key_index]
            value = raw_data.get(key)
            if isinstance(value, list):
                value_index = 0
                while value_index < len(value):
                    normalized = self._normalize_source_entry(value[value_index])
                    if normalized:
                        sources.append(normalized)
                    value_index += 1
            elif isinstance(value, dict):
                normalized_dict = self._normalize_source_entry(value)
                if normalized_dict:
                    sources.append(normalized_dict)
            key_index += 1
        return sources

    def _normalize_source_entry(self, entry: Any) -> Optional[Dict[str, Any]]:
        if entry is None:
            return None

        normalized: Dict[str, Any] = {}
        if isinstance(entry, dict):
            for key, value in entry.items():
                normalized[key] = value
        elif isinstance(entry, str):
            normalized["title"] = entry
        else:
            return None

        if "category" not in normalized:
            normalized["category"] = self._infer_category_from_entry(normalized)
        if "source_type" not in normalized:
            normalized["source_type"] = self._infer_source_type(normalized)
        return normalized

    def _infer_category_from_entry(self, entry: Dict[str, Any]) -> str:
        possible_fields = ["category", "type", "focus", "topic"]
        index = 0
        while index < len(possible_fields):
            field = possible_fields[index]
            value = entry.get(field)
            if isinstance(value, str) and len(value.strip()) > 0:
                return value.strip()
            index += 1

        title = entry.get("title")
        if isinstance(title, str):
            lowered = title.lower()
            if "yield" in lowered or "performance" in lowered:
                return "yield_performance"
            if "disease" in lowered or "pest" in lowered:
                return "disease_resistance"
            if "management" in lowered or "practice" in lowered:
                return "management_guidance"
            if "climate" in lowered or "zone" in lowered:
                return "climate_adaptation"
        return "general_support"

    def _infer_source_type(self, entry: Dict[str, Any]) -> EvidenceSourceType:
        explicit = entry.get("source_type")
        if isinstance(explicit, EvidenceSourceType):
            return explicit
        if isinstance(explicit, str):
            mapped = self._map_source_type(explicit)
            if mapped:
                return mapped

        title = entry.get("title")
        organization = entry.get("organization")
        name_candidates: List[str] = []
        if isinstance(title, str):
            name_candidates.append(title)
        if isinstance(organization, str):
            name_candidates.append(organization)

        index = 0
        while index < len(name_candidates):
            candidate = name_candidates[index]
            lowered = candidate.lower()
            if "university" in lowered or "college" in lowered:
                return EvidenceSourceType.UNIVERSITY_RESEARCH
            if "extension" in lowered or "cooperative" in lowered:
                return EvidenceSourceType.EXTENSION_PUBLICATION
            if "department" in lowered or "agency" in lowered:
                return EvidenceSourceType.GOVERNMENT_AGENCY
            if "seed" in lowered or "company" in lowered or "ag" in lowered:
                return EvidenceSourceType.SEED_COMPANY_DATA
            if "farmer" in lowered or "producer" in lowered:
                return EvidenceSourceType.FARMER_TESTIMONIAL
            if "journal" in lowered or "review" in lowered:
                return EvidenceSourceType.PEER_REVIEWED_RESEARCH
            index += 1
        return EvidenceSourceType.UNKNOWN

    def _map_source_type(self, value: str) -> Optional[EvidenceSourceType]:
        normalized = value.strip().lower()
        if normalized in ("university", "university_research", "research_station"):
            return EvidenceSourceType.UNIVERSITY_RESEARCH
        if normalized in ("extension", "extension_publication", "cooperative_extension"):
            return EvidenceSourceType.EXTENSION_PUBLICATION
        if normalized in ("government", "government_agency", "usda"):
            return EvidenceSourceType.GOVERNMENT_AGENCY
        if normalized in ("seed_company", "seed_company_data", "seed"):
            return EvidenceSourceType.SEED_COMPANY_DATA
        if normalized in ("farmer", "farmer_testimonial", "farmer_feedback"):
            return EvidenceSourceType.FARMER_TESTIMONIAL
        if normalized in ("peer_reviewed", "peer_reviewed_research", "journal"):
            return EvidenceSourceType.PEER_REVIEWED_RESEARCH
        if normalized in ("internal", "internal_analysis", "ai_inference"):
            return EvidenceSourceType.INTERNAL_ANALYSIS
        if normalized in ("unknown", "other"):
            return EvidenceSourceType.UNKNOWN
        return None

    def _build_record_from_source(
        self,
        source_payload: Dict[str, Any],
        variety_name: Optional[str],
        raw_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[EvidenceRecord]:
        title = source_payload.get("title")
        organization = source_payload.get("organization")
        if not isinstance(title, str) and not isinstance(organization, str):
            return None

        category = source_payload.get("category")
        if not isinstance(category, str):
            category = "general_support"

        record_id = f"evidence-{uuid.uuid4()}"
        summary = source_payload.get("summary")
        if not isinstance(summary, str) or len(summary.strip()) == 0:
            summary = self._build_summary_from_category(category, raw_data)
        if summary is None:
            return None

        record = EvidenceRecord(
            id=record_id,
            variety_name=variety_name,
            category=category,
            summary=summary,
            source_name=self._determine_source_name(title, organization),
            source_type=self._infer_source_type(source_payload),
            source_link=self._extract_source_link(source_payload),
            published_at=self._parse_datetime(source_payload.get("published_at")),
            credibility_score=0.0,
            strength_score=0.0,
            strength_level=EvidenceStrengthLevel.LIMITED,
            reliability_notes=source_payload.get("reliability_notes"),
            last_verified=self._parse_datetime(source_payload.get("last_verified")),
        )

        record.credibility_score = self._calculate_credibility(record, source_payload)
        record.strength_score = self._calculate_evidence_strength(record, raw_data, context)
        record.strength_level = self._determine_strength_level(record.strength_score)
        return record

    def _determine_source_name(self, title: Optional[str], organization: Optional[str]) -> str:
        if isinstance(title, str) and len(title.strip()) > 0:
            return title.strip()
        if isinstance(organization, str) and len(organization.strip()) > 0:
            return organization.strip()
        return "Supporting evidence"

    def _extract_source_link(self, source_payload: Dict[str, Any]) -> Optional[str]:
        link_fields = ["url", "link", "source_url", "reference"]
        index = 0
        while index < len(link_fields):
            field = link_fields[index]
            value = source_payload.get(field)
            if isinstance(value, str) and len(value.strip()) > 0:
                return value.strip()
            index += 1
        return None

    def _parse_datetime(self, value: Any) -> Optional[datetime]:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str) and len(value.strip()) > 0:
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                return None
        return None

    def _build_summary_from_category(self, category: str, raw_data: Dict[str, Any]) -> Optional[str]:
        if category == "yield_performance":
            percentile = self._extract_float(raw_data.get("yield_potential_percentile"))
            if percentile is not None:
                rounded = round(percentile, 1)
                return f"Yield percentile of {rounded} based on multi-year trial analysis"
        if category == "disease_resistance":
            diseases = raw_data.get("disease_resistances")
            if isinstance(diseases, dict):
                items = []
                for disease, rating in diseases.items():
                    if isinstance(disease, str) and isinstance(rating, str):
                        items.append(f"{disease.replace('_', ' ')}: {rating}")
                if len(items) > 0:
                    joined = "; ".join(items)
                    return f"Disease resistance ratings: {joined}"
        if category == "management_guidance":
            guidance = raw_data.get("management_recommendations")
            if isinstance(guidance, list) and len(guidance) > 0:
                first = guidance[0]
                if isinstance(first, str) and len(first.strip()) > 0:
                    return first.strip()
        if category == "climate_adaptation":
            regions = raw_data.get("adapted_regions")
            if isinstance(regions, list) and len(regions) > 0:
                first_region = regions[0]
                if isinstance(first_region, str) and len(first_region.strip()) > 0:
                    return f"Adapted to region: {first_region.strip()}"
        return None

    def _calculate_credibility(self, record: EvidenceRecord, payload: Dict[str, Any]) -> float:
        base_score = self.source_base_scores.get(record.source_type, 0.5)
        score = base_score

        confidence_value = payload.get("confidence")
        if isinstance(confidence_value, (int, float)):
            adjusted = float(confidence_value)
            if adjusted > 1.0:
                adjusted = adjusted / 100.0
            score += adjusted * 0.1

        peer_reviewed = payload.get("peer_reviewed")
        if isinstance(peer_reviewed, bool) and peer_reviewed:
            score += 0.05

        published_at = record.published_at
        if published_at:
            now = datetime.utcnow()
            recency_threshold = now - timedelta(days=365 * self.recency_window_years)
            if published_at >= recency_threshold:
                score += 0.05

        reliability_flag = payload.get("reliability")
        if isinstance(reliability_flag, str):
            lowered = reliability_flag.lower()
            if "limited" in lowered:
                score -= 0.1
            if "strong" in lowered or "validated" in lowered:
                score += 0.05

        if score > 1.0:
            score = 1.0
        if score < 0.0:
            score = 0.0
        return round(score, 3)

    def _calculate_evidence_strength(
        self,
        record: EvidenceRecord,
        raw_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> float:
        score = 0.5
        sample_size = raw_data.get("trial_sample_size")
        if isinstance(sample_size, (int, float)) and sample_size > 0:
            normalized = float(sample_size) / 100.0
            if normalized > 1.0:
                normalized = 1.0
            score += normalized * 0.2

        confidence_level = raw_data.get("confidence_level")
        numeric_confidence = self._extract_float(confidence_level)
        if numeric_confidence is not None:
            if numeric_confidence > 1.0:
                numeric_confidence = numeric_confidence / 100.0
            score += numeric_confidence * 0.2

        overall_score = raw_data.get("overall_score")
        numeric_overall = self._extract_float(overall_score)
        if numeric_overall is not None:
            score += numeric_overall * 0.1

        location_data = context.get("location") if isinstance(context, dict) else None
        if isinstance(location_data, dict):
            climate_zone = location_data.get("climate_zone")
            regions = raw_data.get("adapted_regions")
            if isinstance(climate_zone, str) and isinstance(regions, list):
                if self._contains_case_insensitive(regions, climate_zone):
                    score += 0.05

        if score > 1.0:
            score = 1.0
        if score < 0.0:
            score = 0.0
        return round(score, 3)

    def _contains_case_insensitive(self, items: List[Any], target: str) -> bool:
        if target is None:
            return False
        target_lower = target.lower()
        index = 0
        while index < len(items):
            item = items[index]
            if isinstance(item, str) and item.lower() == target_lower:
                return True
            index += 1
        return False

    def _determine_strength_level(self, strength_score: float) -> EvidenceStrengthLevel:
        threshold_items = list(self.strength_thresholds.items())
        index = 0
        determined = EvidenceStrengthLevel.LIMITED
        while index < len(threshold_items):
            level, threshold = threshold_items[index]
            if strength_score >= threshold:
                determined = level
            index += 1
        return determined

    def _generate_inferred_records(
        self,
        variety_entry: Dict[str, Any],
        raw_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[EvidenceRecord]:
        records: List[EvidenceRecord] = []
        generated_categories = self._determine_missing_categories(raw_data)
        cat_index = 0
        while cat_index < len(generated_categories):
            category = generated_categories[cat_index]
            summary = self._build_summary_from_category(category, raw_data)
            if summary is None:
                cat_index += 1
                continue

            record = EvidenceRecord(
                id=f"inferred-{uuid.uuid4()}",
                variety_name=variety_entry.get("name"),
                category=category,
                summary=summary,
                source_name="AFAS Knowledge Base",
                source_type=EvidenceSourceType.INTERNAL_ANALYSIS,
                source_link=None,
                published_at=None,
                credibility_score=0.0,
                strength_score=0.0,
                strength_level=EvidenceStrengthLevel.LIMITED,
                reliability_notes="Derived from integrated variety dataset",
                last_verified=None,
            )
            record.credibility_score = self._calculate_credibility(record, {"confidence": raw_data.get("confidence_level")})
            record.strength_score = self._calculate_evidence_strength(record, raw_data, context)
            record.strength_level = self._determine_strength_level(record.strength_score)
            records.append(record)
            cat_index += 1
        return records

    def _determine_missing_categories(self, raw_data: Dict[str, Any]) -> List[str]:
        categories: List[str] = []
        for category_name in self.category_priority.keys():
            has_data = False
            if category_name == "yield_performance":
                if self._extract_float(raw_data.get("yield_potential_percentile")) is not None:
                    has_data = True
            elif category_name == "disease_resistance":
                if isinstance(raw_data.get("disease_resistances"), dict):
                    has_data = True
            elif category_name == "climate_adaptation":
                if isinstance(raw_data.get("adapted_regions"), list):
                    has_data = True
            elif category_name == "management_guidance":
                if isinstance(raw_data.get("management_recommendations"), list):
                    has_data = True
            elif category_name == "market_analysis":
                if isinstance(raw_data.get("market_acceptance_score"), (int, float)):
                    has_data = True
            elif category_name == "soil_fit":
                if isinstance(raw_data.get("soil_fit"), list):
                    has_data = True

            if has_data:
                categories.append(category_name)
        return categories

    def _build_fallback_records(
        self,
        variety_entries: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[EvidenceRecord]:
        records: List[EvidenceRecord] = []
        required_categories: List[str] = []
        for category_name, _ in self.category_priority.items():
            if category_name not in required_categories:
                required_categories.append(category_name)

        category_coverage: Dict[str, int] = {}
        record_index = 0
        while record_index < len(required_categories):
            category = required_categories[record_index]
            category_coverage[category] = 0
            record_index += 1

        entry_index = 0
        while entry_index < len(variety_entries):
            variety_entry = variety_entries[entry_index]
            raw_data = variety_entry.get("raw", {})
            category_list = self._determine_missing_categories(raw_data)
            category_index = 0
            while category_index < len(category_list):
                category_name = category_list[category_index]
                coverage = category_coverage.get(category_name, 0)
                if coverage >= 1:
                    category_index += 1
                    continue

                summary = self._build_summary_from_category(category_name, raw_data)
                if summary is None:
                    category_index += 1
                    continue

                record = EvidenceRecord(
                    id=f"fallback-{uuid.uuid4()}",
                    variety_name=variety_entry.get("name"),
                    category=category_name,
                    summary=summary,
                    source_name="AFAS Evidence Framework",
                    source_type=EvidenceSourceType.INTERNAL_ANALYSIS,
                    source_link=None,
                    published_at=None,
                    credibility_score=0.65,
                    strength_score=0.5,
                    strength_level=EvidenceStrengthLevel.MEDIUM,
                    reliability_notes="Fallback evidence generated from structured data",
                    last_verified=None,
                )
                records.append(record)
                category_coverage[category_name] = coverage + 1
                category_index += 1
            entry_index += 1
        return records

    def _aggregate_summary(self, records: List[EvidenceRecord]) -> EvidenceSummary:
        summary = EvidenceSummary()
        total_records = len(records)
        summary.total_records = total_records
        if total_records == 0:
            return summary

        credibility_sum = 0.0
        strength_sum = 0.0
        latest_publication: Optional[datetime] = None

        index = 0
        while index < total_records:
            record = records[index]
            credibility_sum += record.credibility_score
            strength_sum += record.strength_score

            current = summary.source_distribution.get(record.source_type)
            if current is None:
                summary.source_distribution[record.source_type] = 1
            else:
                summary.source_distribution[record.source_type] = current + 1

            level_count = summary.strength_distribution.get(record.strength_level)
            if level_count is None:
                summary.strength_distribution[record.strength_level] = 1
            else:
                summary.strength_distribution[record.strength_level] = level_count + 1

            if record.published_at:
                if latest_publication is None or record.published_at > latest_publication:
                    latest_publication = record.published_at
            index += 1

        summary.average_credibility = round(credibility_sum / total_records, 3)
        summary.average_strength = round(strength_sum / total_records, 3)
        summary.latest_publication = latest_publication
        return summary

    def _compose_coverage_notes(
        self,
        records: List[EvidenceRecord],
        summary: EvidenceSummary,
        context: Dict[str, Any],
    ) -> List[str]:
        notes: List[str] = []
        if summary.total_records < self.minimum_records:
            notes.append(
                "Limited supporting evidence detected; consider adding regional trial data."
            )

        location = context.get("location") if isinstance(context, dict) else None
        if isinstance(location, dict):
            climate_zone = location.get("climate_zone")
            if isinstance(climate_zone, str) and len(climate_zone.strip()) > 0:
                has_climate_evidence = False
                index = 0
                while index < len(records):
                    record = records[index]
                    if record.category == "climate_adaptation":
                        has_climate_evidence = True
                        break
                    index += 1
                if not has_climate_evidence:
                    notes.append(
                        f"No climate adaptation references matched climate zone {climate_zone.strip()}."
                    )

        unique_categories: List[str] = []
        index = 0
        while index < len(records):
            record = records[index]
            if record.category not in unique_categories:
                unique_categories.append(record.category)
            index += 1

        for category_name, weight in self.category_priority.items():
            if category_name not in unique_categories and weight >= 0.8:
                notes.append(
                    f"Add evidence for {category_name.replace('_', ' ')} to enhance recommendation transparency."
                )
        return notes
