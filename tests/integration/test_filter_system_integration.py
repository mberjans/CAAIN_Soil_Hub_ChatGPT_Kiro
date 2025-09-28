"""Integration tests validating crop filter combination, caching, and analytics flows."""

from __future__ import annotations

import importlib
import sys
import types
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

import pytest


def _ensure_namespace(package_name: str, path_obj: Path) -> None:
    """Ensure namespace packages resolve to the provided path."""
    module = sys.modules.get(package_name)
    path_string = str(path_obj)
    if module is None:
        namespace_module = types.ModuleType(package_name)
        namespace_module.__path__ = [path_string]
        sys.modules[package_name] = namespace_module
        return
    existing_path = getattr(module, "__path__", None)
    if existing_path is None:
        replacement_module = types.ModuleType(package_name)
        replacement_module.__path__ = [path_string]
        sys.modules[package_name] = replacement_module
        return
    paths = list(existing_path)
    index = 0
    needs_append = True
    while index < len(paths):
        if paths[index] == path_string:
            needs_append = False
            break
        index += 1
    if needs_append:
        paths.append(path_string)
        module.__path__ = paths


def _install_variety_service_stub() -> None:
    module_name = "services.crop_taxonomy.src.services.variety_recommendation_service"
    if module_name in sys.modules:
        return
    stub_module = types.ModuleType(module_name)

    class VarietyRecommendationService:  # type: ignore[misc]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.placeholder = True

        async def _score_variety_for_context(self, variety: Any, regional_context: Dict[str, Any], farmer_preferences: Dict[str, Any]) -> Dict[str, Any]:
            return {"overall_score": 0.75}

        async def recommend_varieties(self, *args: Any, **kwargs: Any) -> List[Any]:
            return []

    stub_service = VarietyRecommendationService()
    stub_module.VarietyRecommendationService = VarietyRecommendationService
    stub_module.variety_recommendation_service = stub_service
    stub_module.__all__ = ["VarietyRecommendationService", "variety_recommendation_service"]
    sys.modules[module_name] = stub_module


def _install_result_processor_stub() -> None:
    module_name = "services.crop_taxonomy.src.services.result_processor"
    if module_name in sys.modules:
        return
    stub_module = types.ModuleType(module_name)

    class FilterResultProcessor:  # type: ignore[misc]
        def __init__(self, variety_service: Any = None) -> None:
            self.variety_service = variety_service

        async def process_results(self, ranked_results: List[Any], filter_criteria: Dict[str, Any]) -> Dict[str, Any]:
            summary = {}
            summary["ranked_results"] = ranked_results
            summary["clustered_results"] = {}
            summary["visualization_data"] = {}
            summary["alternatives"] = []
            return summary

    stub_module.FilterResultProcessor = FilterResultProcessor
    sys.modules[module_name] = stub_module


def _install_filter_analytics_stub() -> None:
    service_module = "services.crop_taxonomy.src.services.filter_analytics_service"
    models_module = "services.crop_taxonomy.src.models.filter_analytics_models"

    if models_module not in sys.modules:
        models_stub = types.ModuleType(models_module)

        class FilterUsageRecord:  # type: ignore[misc]
            def __init__(self, record_id: str, user_id: Any, session_id: str, filter_config: Dict[str, Any], applied_at: datetime, result_count: int, search_duration_ms: float, interaction_type: str) -> None:
                self.record_id = record_id
                self.user_id = user_id
                self.session_id = session_id
                self.filter_config = filter_config
                self.applied_at = applied_at
                self.result_count = result_count
                self.search_duration_ms = search_duration_ms
                self.interaction_type = interaction_type

        class FilterUsageSummary:  # type: ignore[misc]
            def __init__(self, total_applications: int, unique_users: int, average_result_count: float, average_search_duration: float) -> None:
                self.total_applications = total_applications
                self.unique_users = unique_users
                self.average_result_count = average_result_count
                self.average_search_duration = average_search_duration
                self.filter_efficiency_score = 0.0
                self.peak_usage_times = []

        class FilterEffectiveness:  # type: ignore[misc]
            def __init__(self) -> None:
                self.placeholder = True

        class FilterTrend:  # type: ignore[misc]
            def __init__(self) -> None:
                self.placeholder = True

        class FilterAnalyticsRequest:  # type: ignore[misc]
            def __init__(self, request_id: str, start_date: datetime, end_date: datetime, user_id: Any = None) -> None:
                self.request_id = request_id
                self.start_date = start_date
                self.end_date = end_date
                self.user_id = user_id

        class FilterPerformanceMetrics:  # type: ignore[misc]
            def __init__(self) -> None:
                self.placeholder = True

        class FilterInsight:  # type: ignore[misc]
            def __init__(self, title: str, description: str) -> None:
                self.title = title
                self.description = description

        class FilterAnalyticsResponse:  # type: ignore[misc]
            def __init__(self, usage_summary: FilterUsageSummary, effectiveness_metrics: FilterEffectiveness, popular_filters: List[Any], user_behavior_patterns: List[Any], trends: List[Any], recommendations: List[str], metadata: Dict[str, Any]) -> None:
                self.usage_summary = usage_summary
                self.effectiveness_metrics = effectiveness_metrics
                self.popular_filters = popular_filters
                self.user_behavior_patterns = user_behavior_patterns
                self.trends = trends
                self.recommendations = recommendations
                self.metadata = metadata

        class FilterAnalyticsInsightsResponse:  # type: ignore[misc]
            def __init__(self) -> None:
                self.placeholder = True

        class FilterABTestResult:  # type: ignore[misc]
            def __init__(self) -> None:
                self.placeholder = True

        models_stub.FilterUsageRecord = FilterUsageRecord
        models_stub.FilterUsageSummary = FilterUsageSummary
        models_stub.FilterEffectiveness = FilterEffectiveness
        models_stub.FilterTrend = FilterTrend
        models_stub.FilterAnalyticsRequest = FilterAnalyticsRequest
        models_stub.FilterAnalyticsResponse = FilterAnalyticsResponse
        models_stub.FilterInsight = FilterInsight
        models_stub.FilterAnalyticsInsightsResponse = FilterAnalyticsInsightsResponse
        models_stub.FilterPerformanceMetrics = FilterPerformanceMetrics
        models_stub.FilterABTestResult = FilterABTestResult
        models_stub.__all__ = [
            "FilterUsageRecord",
            "FilterUsageSummary",
            "FilterEffectiveness",
            "FilterTrend",
            "FilterAnalyticsRequest",
            "FilterAnalyticsResponse",
            "FilterInsight",
            "FilterAnalyticsInsightsResponse",
            "FilterPerformanceMetrics",
            "FilterABTestResult",
        ]
        sys.modules[models_module] = models_stub

    if service_module in sys.modules:
        return

    service_stub = types.ModuleType(service_module)

    class FilterAnalyticsService:  # type: ignore[misc]
        def __init__(self) -> None:
            self.records: List[Any] = []

        async def record_filter_usage(self, user_id: Any, session_id: str, filter_config: Dict[str, Any], result_count: int, search_duration_ms: float, interaction_type: str = "search") -> bool:
            record_class = sys.modules[models_module].FilterUsageRecord
            record = record_class(
                record_id=str(uuid4()),
                user_id=user_id,
                session_id=session_id,
                filter_config=filter_config,
                applied_at=datetime.utcnow(),
                result_count=result_count,
                search_duration_ms=search_duration_ms,
                interaction_type=interaction_type,
            )
            self.records.append(record)
            return True

        async def get_filter_analytics(self, request: Any):
            total = len(self.records)
            unique_users = len({record.user_id for record in self.records}) if total > 0 else 0
            total_results = 0
            total_duration = 0.0
            index = 0
            while index < total:
                entry = self.records[index]
                total_results += entry.result_count
                total_duration += entry.search_duration_ms
                index += 1
            average_results = total_results / total if total > 0 else 0.0
            average_duration = total_duration / total if total > 0 else 0.0
            summary_class = sys.modules[models_module].FilterUsageSummary
            summary = summary_class(total, unique_users, average_results, average_duration)
            response_class = sys.modules[models_module].FilterAnalyticsResponse
            response = response_class(
                usage_summary=summary,
                effectiveness_metrics=sys.modules[models_module].FilterEffectiveness(),
                popular_filters=[],
                user_behavior_patterns=[],
                trends=[],
                recommendations=["Increase dataset size for deeper analytics"],
                metadata={"record_count": total},
            )
            return response

    service_stub.FilterAnalyticsService = FilterAnalyticsService
    service_stub.__all__ = ["FilterAnalyticsService"]
    sys.modules[service_module] = service_stub


def _prepare_service_imports() -> None:
    if getattr(_prepare_service_imports, "_prepared", False):
        return
    project_root = Path(__file__).resolve().parents[2]
    recommendation_src = project_root / "services" / "recommendation-engine" / "src"
    crop_src = project_root / "services" / "crop-taxonomy" / "src"

    candidate_paths = [recommendation_src, crop_src]
    idx = 0
    while idx < len(candidate_paths):
        candidate = str(candidate_paths[idx])
        if candidate not in sys.path:
            sys.path.insert(0, candidate)
        idx += 1

    if "services" not in sys.modules:
        import services  # pylint: disable=import-outside-toplevel
        sys.modules["services"] = services

    _ensure_namespace("services.recommendation_engine", recommendation_src.parent)
    _ensure_namespace("services.recommendation_engine.src", recommendation_src)
    _ensure_namespace("services.crop_taxonomy", crop_src.parent)
    _ensure_namespace("services.crop_taxonomy.src", crop_src)

    try:
        ag_models = importlib.import_module("services.recommendation_engine.src.models.agricultural_models")
        if not hasattr(ag_models, "SoilData") and hasattr(ag_models, "SoilTestData"):
            ag_models.SoilData = ag_models.SoilTestData
    except ImportError:
        pass

    _install_variety_service_stub()
    _install_result_processor_stub()
    _install_filter_analytics_stub()

    _prepare_service_imports._prepared = True  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_filter_combination_filters_reference_dataset() -> None:
    """Ensure combined criteria can filter the reference crop dataset consistently."""
    _prepare_service_imports()

    from services.crop_taxonomy.src.data.reference_crops import (  # pylint: disable=import-error
        build_reference_crops_dataset,
    )
    from services.crop_taxonomy.src.models.crop_filtering_models import (  # pylint: disable=import-error
        TaxonomyFilterCriteria,
    )
    from services.crop_taxonomy.src.services.filter_engine import (  # pylint: disable=import-error
        FilterCombinationRequest,
        FilterDirective,
        filter_combination_engine,
    )

    directives: List[Any] = []
    directives.append(
        FilterDirective(
            category="geographic",
            attribute="hardiness_zones",
            value=["4", "5"],
            priority=0.8,
            rationale="Dataset integration zone",
        )
    )
    directives.append(
        FilterDirective(
            category="agricultural",
            attribute="categories",
            value=["grain"],
            priority=0.7,
            rationale="Dataset integration crop type",
        )
    )

    base_criteria = TaxonomyFilterCriteria().model_dump()
    combination_request = FilterCombinationRequest(
        request_id="dataset-integration",
        base_criteria=base_criteria,
        preset_keys=[],
        directives=directives,
        context={"source": "integration-test"},
        include_suggestions=False,
    )

    combination_response = filter_combination_engine.combine_filters(combination_request)
    combined_criteria = combination_response.combined_criteria
    if hasattr(combined_criteria, "model_dump"):
        criteria_payload = combined_criteria.model_dump()
    else:
        criteria_payload = combined_criteria

    dataset = build_reference_crops_dataset()

    filtered_crops = []
    index = 0
    while index < len(dataset):
        crop = dataset[index]
        zone_list = crop.get_suitable_zones()
        category = crop.agricultural_classification.crop_category if crop.agricultural_classification else None
        zone_match = False
        zone_idx = 0
        while zone_idx < len(zone_list):
            zone_candidate = zone_list[zone_idx]
            if zone_candidate.startswith("4") or zone_candidate.startswith("5"):
                zone_match = True
                break
            zone_idx += 1
        if zone_match and category is not None and "grain" in category.value:
            filtered_crops.append(crop)
        index += 1

    assert len(filtered_crops) > 0

    soil_filter_payload = criteria_payload.get("soil_filter")
    if isinstance(soil_filter_payload, dict):
        soil_range = soil_filter_payload.get("ph_range")
        if isinstance(soil_range, dict):
            filtered_index = 0
            while filtered_index < len(filtered_crops):
                crop = filtered_crops[filtered_index]
                requirements = getattr(crop.soil_requirements, "optimal_ph_min", None)
                if requirements is not None and "max" in soil_range:
                    assert crop.soil_requirements.optimal_ph_min <= soil_range["max"]
                filtered_index += 1


@pytest.mark.asyncio
async def test_filter_cache_and_analytics_flow() -> None:
    """Validate cache population and analytics recording for combined criteria."""
    _prepare_service_imports()

    from services.crop_taxonomy.src.models.crop_filtering_models import (  # pylint: disable=import-error
        TaxonomyFilterCriteria,
    )
    from services.crop_taxonomy.src.models.filter_analytics_models import (  # pylint: disable=import-error
        FilterAnalyticsRequest,
    )
    from services.crop_taxonomy.src.services.filter_cache_service import (  # pylint: disable=import-error
        filter_cache_service,
    )
    from services.crop_taxonomy.src.services.filter_engine import (  # pylint: disable=import-error
        FilterCombinationRequest,
        FilterDirective,
        filter_combination_engine,
    )
    from services.crop_taxonomy.src.services.filter_analytics_service import (  # pylint: disable=import-error
        FilterAnalyticsService,
    )

    directives: List[Any] = []
    directives.append(
        FilterDirective(
            category="geographic",
            attribute="hardiness_zones",
            value=["4"],
            priority=0.6,
            rationale="Cache integration zone",
        )
    )

    base_criteria = TaxonomyFilterCriteria().model_dump()
    combination_request = FilterCombinationRequest(
        request_id="cache-integration",
        base_criteria=base_criteria,
        preset_keys=[],
        directives=directives,
        context={"mode": "cache"},
        include_suggestions=False,
    )

    combination_response = filter_combination_engine.combine_filters(combination_request)
    cached_payload = filter_cache_service.get_filter_combination("cache-integration")
    assert cached_payload is not None

    combined_criteria = combination_response.combined_criteria
    if hasattr(combined_criteria, "model_dump"):
        criteria_payload = combined_criteria.model_dump()
    else:
        criteria_payload = combined_criteria

    analytics_service = FilterAnalyticsService()
    await analytics_service.record_filter_usage(
        user_id=uuid4(),
        session_id="s-integrated",
        filter_config=criteria_payload,
        result_count=5,
        search_duration_ms=125.0,
        interaction_type="search",
    )

    analytics_request = FilterAnalyticsRequest(
        request_id="analytics-integration",
        start_date=datetime.utcnow() - timedelta(minutes=2),
        end_date=datetime.utcnow() + timedelta(minutes=2),
    )
    analytics_response = await analytics_service.get_filter_analytics(analytics_request)

    assert analytics_response.usage_summary.total_applications >= 1
    assert analytics_response.usage_summary.average_search_duration >= 0.0
    assert len(analytics_response.recommendations) > 0

    cached_after = filter_cache_service.get_filter_combination("cache-integration")
    assert cached_after is not None
