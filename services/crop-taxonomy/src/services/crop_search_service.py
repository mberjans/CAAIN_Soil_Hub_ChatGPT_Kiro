"""Crop search service with advanced multi-criteria filtering."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

try:  # pragma: no cover - runtime import resolution
    from ..data.reference_crops import build_reference_crops_dataset
    from ..models.crop_filtering_models import (
        CropSearchRequest,
        CropSearchResponse,
        CropSearchResult,
        FilterContributionAggregate,
        FilterScoreBreakdown,
        ResultRankingDetails,
        SearchFacets,
        SearchRankingOverview,
        SearchOperator,
        SearchStatistics,
        SearchVisualizationSummary,
        ScoreBucket,
        SortField,
        SortOrder,
        TaxonomyFilterCriteria,
    )
    from ..models.crop_taxonomy_models import (
        ComprehensiveCropData,
        CropAgriculturalClassification,
        CropClimateAdaptations,
        CropSoilRequirements,
    )
except ImportError:  # pragma: no cover - fallback for direct execution
    from data.reference_crops import build_reference_crops_dataset
    from models.crop_filtering_models import (  # type: ignore
        CropSearchRequest,
        CropSearchResponse,
        CropSearchResult,
        FilterContributionAggregate,
        FilterScoreBreakdown,
        ResultRankingDetails,
        SearchFacets,
        SearchRankingOverview,
        SearchOperator,
        SearchStatistics,
        SearchVisualizationSummary,
        ScoreBucket,
        SortField,
        SortOrder,
        TaxonomyFilterCriteria,
    )
    from models.crop_taxonomy_models import (  # type: ignore
        ComprehensiveCropData,
        CropAgriculturalClassification,
        CropClimateAdaptations,
        CropSoilRequirements,
    )

logger = logging.getLogger(__name__)


class FilterEvaluation:
    """Container for filter evaluation details."""

    def __init__(self, name: str, weight: float) -> None:
        self.name = name
        self.weight = weight
        self.active = False
        self.score = 0.0
        self.matched = False
        self.partial = False
        self.notes: List[str] = []
        self.partial_notes: List[str] = []
        self.missing_notes: List[str] = []
        self.highlights: Dict[str, List[str]] = {}


from .result_processor import FilterResultProcessor
from .variety_recommendation_service import VarietyRecommendationService

class CropSearchService:
    """Advanced search service for crop taxonomy data."""

    def __init__(self, database_url: Optional[str] = None) -> None:
        from .filter_cache_service import filter_cache_service
        from .performance_monitor import performance_monitor
        self.scoring_weights = self._initialize_scoring_weights()
        self.variety_recommendation_service = VarietyRecommendationService(database_url)
        self.result_processor = FilterResultProcessor(self.variety_recommendation_service)
        self.search_cache: Dict[str, CropSearchResponse] = {}
        self.reference_crops: List[ComprehensiveCropData] = []
        self.db = None
        self.database_available = False
        self.cache_service = filter_cache_service
        self.performance_monitor = performance_monitor
        self._optimizations_initialized = False
        self._initialise_database(database_url)
        self._load_reference_dataset()

    def _initialise_database(self, database_url: Optional[str]) -> None:
        """Initialise database connection if available."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
        except ImportError:  # pragma: no cover - optional dependency
            logger.info("Crop taxonomy database module not available; using reference dataset")
            return

        try:
            if database_url is None:
                database_url = os.getenv("DATABASE_URL")
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            if self.database_available:
                self._run_database_optimizations()
        except Exception as exc:  # pragma: no cover - connection failure path
            logger.warning("Crop taxonomy database unavailable: %s", str(exc))
            self.db = None
            self.database_available = False
            self._optimizations_initialized = False

    def _run_database_optimizations(self) -> None:
        """Run database optimization routines if available."""
        if self.db is None or not self.database_available:
            return
        if self._optimizations_initialized:
            return
        try:
            from .database_optimizer import DatabaseOptimizer
            optimizer = DatabaseOptimizer(self.db)
            optimizer.run_all_optimizations()
            self._optimizations_initialized = True
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("Database optimizations skipped: %s", str(exc))

    def _load_reference_dataset(self) -> None:
        """Load fallback dataset for searches."""
        try:
            dataset = build_reference_crops_dataset()
            self.reference_crops = dataset
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Failed to load reference crops dataset: %s", str(exc))
            self.reference_crops = []

    def _initialize_scoring_weights(self) -> Dict[str, float]:
        """Weighting for filter categories."""
        weights: Dict[str, float] = {}
        weights["text_match"] = 0.18
        weights["taxonomy_match"] = 0.07
        weights["geographic_match"] = 0.15
        weights["climate_match"] = 0.20
        weights["soil_match"] = 0.15
        weights["agricultural_match"] = 0.12
        weights["management_match"] = 0.05
        weights["sustainability_match"] = 0.04
        weights["economic_match"] = 0.04
        return weights

    async def search_crops(self, request: CropSearchRequest) -> CropSearchResponse:
        """Execute comprehensive crop search with filtering and scoring."""
        # Monitor the entire search operation
        operation_start = self.performance_monitor.start_timer()
        
        # Check cache first
        cached_result = await self.cache_service.get_search_result(request.request_id)
        if cached_result:
            # Update statistics to reflect cache hit
            cached_result.statistics.cache_hit = True
            execution_time = self.performance_monitor.stop_timer(operation_start)
            logger.info(f"Cache hit for search request {request.request_id}, took {execution_time:.2f}ms")
            
            # Record performance metrics for cache hit
            self.performance_monitor.record_operation(
                operation="crop_search_cached",
                execution_time_ms=execution_time,
                cache_hit=True
            )
            
            return cached_result

        start_time = datetime.utcnow()
        candidates = await self._get_candidate_crops(request)
        matched_results = self._evaluate_candidates(candidates, request.filter_criteria)
        sorted_results = self._sort_results(matched_results, request.sort_by, request.sort_order)
        paginated_results = self._paginate_results(sorted_results, request.offset, request.max_results)

        processed_results = self.result_processor.process_results(paginated_results, request.filter_criteria)
        ranked_results = processed_results["ranked_results"]
        visualization_summary = self._build_visualization_summary(ranked_results)

        facets = self._build_facets(sorted_results)
        statistics = self._build_statistics(start_time, matched_results, ranked_results)
        filters_summary = self._summarize_filters(request.filter_criteria)
        ranking_overview = self._build_ranking_overview(sorted_results)
        total_count = len(matched_results)
        returned_count = len(ranked_results)
        offset_value = request.offset
        has_more_results = False
        next_offset = None
        if offset_value + returned_count < total_count:
            has_more_results = True
            next_offset = offset_value + returned_count

        response = CropSearchResponse(
            request_id=request.request_id,
            results=ranked_results,
            total_count=total_count,
            returned_count=returned_count,
            facets=facets,
            suggested_refinements=self._suggest_refinements(matched_results, request.filter_criteria),
            alternative_searches=[],
            statistics=statistics,
            applied_filters=filters_summary,
            ranking_overview=ranking_overview,
            visualization_summary=visualization_summary,
            has_more_results=has_more_results,
            next_offset=next_offset,
        )
        
        # Cache the result with a TTL based on complexity (1-24 hours)
        ttl_seconds = self._calculate_cache_ttl(request)
        await self.cache_service.cache_search_result(request.request_id, response, ttl_seconds)
        
        # Record performance metrics for the search operation
        execution_time = self.performance_monitor.stop_timer(operation_start)
        self.performance_monitor.record_operation(
            operation="crop_search_full",
            execution_time_ms=execution_time,
            cache_hit=False,
            database_query_count=1,  # Simplified count
            memory_usage_mb=0.0  # Placeholder for now
        )
        
        logger.info(f"Full search for request {request.request_id} took {execution_time:.2f}ms")
        
        return response

    async def _get_candidate_crops(self, request: CropSearchRequest) -> List[ComprehensiveCropData]:
        """Retrieve initial candidate crops from database or reference dataset."""
        candidates: List[ComprehensiveCropData] = []
        existing_ids = set()

        if self.database_available and self.db is not None:
            try:
                optimized_candidates = self._load_optimized_candidates(request.filter_criteria)
                index = 0
                while index < len(optimized_candidates):
                    optimized_crop = optimized_candidates[index]
                    candidates.append(optimized_crop)
                    crop_identifier = optimized_crop.crop_id
                    if crop_identifier is not None:
                        existing_ids.add(str(crop_identifier))
                    index += 1

                search_text = self._primary_search_text(request.filter_criteria)
                filters = self._prepare_optimized_filters(request.filter_criteria)
                db_results = self.db.search_crops(
                    search_text=search_text,
                    filters=filters,
                    limit=request.max_results * 6,
                    offset=request.offset,
                )
                index = 0
                while index < len(db_results):
                    crop_dict = db_results[index]
                    crop = self._convert_db_to_comprehensive_crop_data(crop_dict)
                    if crop is not None:
                        crop_identifier = crop.crop_id
                        identifier_string = None
                        if crop_identifier is not None:
                            identifier_string = str(crop_identifier)
                        if identifier_string is None or identifier_string not in existing_ids:
                            candidates.append(crop)
                            if identifier_string is not None:
                                existing_ids.add(identifier_string)
                    index += 1
            except Exception as exc:  # pragma: no cover - database fallback path
                logger.warning("Database search failed, using reference dataset: %s", str(exc))

        if len(candidates) == 0:
            index = 0
            while index < len(self.reference_crops):
                candidates.append(self.reference_crops[index])
                index += 1

        return candidates

    def _prepare_optimized_filters(self, criteria):
        """Prepare optimized filter parameters for database query."""
        from ..models.crop_taxonomy_models import CropSearchFilters, CropClimateFilters, CropSoilFilters
        from ..models.crop_taxonomy_models import CropAgriculturalFilters, CropSearchFilters
        
        # Create optimized filters based on the criteria
        climate_filters = None
        if criteria.climate_filter:
            climate_filters = CropClimateFilters(
                drought_tolerance=[criteria.climate_filter.drought_tolerance_required.value] if criteria.climate_filter.drought_tolerance_required else None,
                temperature_range=criteria.climate_filter.temperature_range_f,
                hardiness_zones=criteria.climate_filter.hardiness_zones
            )
        
        soil_filters = None
        if criteria.soil_filter and criteria.soil_filter.ph_range:
            soil_filters = CropSoilFilters(
                ph_range=criteria.soil_filter.ph_range
            )
        
        agricultural_filters = None
        if criteria.agricultural_filter and criteria.agricultural_filter.categories:
            agricultural_filters = CropAgriculturalFilters(
                crop_categories=criteria.agricultural_filter.categories
            )
        
        optimized_filters = CropSearchFilters(
            climate_filters=climate_filters,
            soil_filters=soil_filters,
            agricultural_filters=agricultural_filters
        )
        
        return optimized_filters

    def _load_optimized_candidates(self, criteria: TaxonomyFilterCriteria) -> List[ComprehensiveCropData]:
        """Load candidate crops using optimized database paths."""
        optimized_candidates: List[ComprehensiveCropData] = []
        if self.db is None:
            return optimized_candidates
        if not hasattr(self.db, 'run_complex_filter'):
            return optimized_candidates

        arguments = self._build_optimized_filter_arguments(criteria)
        if arguments is None:
            return optimized_candidates

        ph_range = arguments['ph_range']
        results = self.db.run_complex_filter(
            climate_zones=arguments['climate_zones'],
            ph_range=ph_range,
            drought_tolerance=arguments['drought_tolerance'],
            management_complexity=arguments['management_complexity'],
            crop_categories=arguments['crop_categories'],
            limit=200,
            offset=0
        )

        if len(results) == 0:
            return optimized_candidates

        crop_ids: List[UUID] = []
        index = 0
        while index < len(results):
            row = results[index]
            crop_identifier = row.get('crop_id')
            if crop_identifier is not None:
                crop_ids.append(crop_identifier)
            index += 1

        if len(crop_ids) == 0:
            return optimized_candidates

        if hasattr(self.db, 'get_crops_by_ids'):
            detailed_records = self.db.get_crops_by_ids(crop_ids)
        else:
            detailed_records = []

        record_index = 0
        while record_index < len(detailed_records):
            record = detailed_records[record_index]
            converted = self._convert_db_to_comprehensive_crop_data(record)
            if converted is not None:
                score_value = None
                if record_index < len(results):
                    row = results[record_index]
                    score_value = row.get('overall_score')
                if score_value is not None:
                    try:
                        converted.confidence_score = float(score_value)
                    except Exception:
                        pass
                optimized_candidates.append(converted)
            record_index += 1

        return optimized_candidates

    def _build_optimized_filter_arguments(self, criteria: TaxonomyFilterCriteria) -> Optional[Dict[str, Any]]:
        """Build arguments for optimized database filter execution."""
        has_parameter = False
        arguments: Dict[str, Any] = {}
        arguments['climate_zones'] = None
        arguments['ph_range'] = None
        arguments['drought_tolerance'] = None
        arguments['management_complexity'] = None
        arguments['crop_categories'] = None

        climate_filter = criteria.climate_filter
        if climate_filter is not None:
            if climate_filter.hardiness_zones:
                zones: List[str] = []
                zone_index = 0
                while zone_index < len(climate_filter.hardiness_zones):
                    zone_value = climate_filter.hardiness_zones[zone_index]
                    if zone_value is not None:
                        zones.append(str(zone_value))
                    zone_index += 1
                if len(zones) > 0:
                    arguments['climate_zones'] = zones
                    has_parameter = True
            if climate_filter.drought_tolerance_required is not None:
                tolerance_value = climate_filter.drought_tolerance_required
                if hasattr(tolerance_value, 'value'):
                    arguments['drought_tolerance'] = tolerance_value.value
                else:
                    arguments['drought_tolerance'] = str(tolerance_value)
                has_parameter = True

        soil_filter = criteria.soil_filter
        if soil_filter is not None and soil_filter.ph_range:
            min_ph = None
            max_ph = None
            ph_range_value = soil_filter.ph_range
            if isinstance(ph_range_value, dict):
                min_ph = ph_range_value.get('min') or ph_range_value.get('min_ph')
                max_ph = ph_range_value.get('max') or ph_range_value.get('max_ph')
            elif isinstance(ph_range_value, (list, tuple)):
                if len(ph_range_value) > 0:
                    min_ph = ph_range_value[0]
                if len(ph_range_value) > 1:
                    max_ph = ph_range_value[1]
            if min_ph is not None or max_ph is not None:
                arguments['ph_range'] = (min_ph, max_ph)
                has_parameter = True

        management_filter = criteria.management_filter
        if management_filter is not None and management_filter.max_management_complexity is not None:
            complexity_value = management_filter.max_management_complexity
            if hasattr(complexity_value, 'value'):
                arguments['management_complexity'] = complexity_value.value
            else:
                arguments['management_complexity'] = str(complexity_value)
            has_parameter = True

        agricultural_filter = criteria.agricultural_filter
        if agricultural_filter is not None and agricultural_filter.categories is not None:
            categories: List[str] = []
            category_index = 0
            while category_index < len(agricultural_filter.categories):
                category_value = agricultural_filter.categories[category_index]
                if category_value is not None:
                    if hasattr(category_value, 'value'):
                        categories.append(str(category_value.value))
                    else:
                        categories.append(str(category_value))
                category_index += 1
            if len(categories) > 0:
                arguments['crop_categories'] = categories
                has_parameter = True

        if not has_parameter:
            return None

        return arguments

    def _primary_search_text(self, criteria: TaxonomyFilterCriteria) -> Optional[str]:
        """Select primary search text from criteria."""
        if criteria.text_search:
            return criteria.text_search
        if criteria.common_name_search:
            return criteria.common_name_search
        if criteria.scientific_name_search:
            return criteria.scientific_name_search
        return None

    def _convert_db_to_comprehensive_crop_data(self, record: Dict[str, object]) -> ComprehensiveCropData:
        """Convert database row to comprehensive crop data."""
        try:
            return ComprehensiveCropData(**record)
        except Exception:  # pragma: no cover - ensure fallback conversion
            crop_data = ComprehensiveCropData(
                crop_name=str(record.get("crop_name", "")),
                crop_id=record.get("crop_id"),
            )
            return crop_data

    def _evaluate_candidates(
        self,
        candidates: List[ComprehensiveCropData],
        criteria: TaxonomyFilterCriteria,
    ) -> List[CropSearchResult]:
        """Evaluate candidate crops against filter criteria."""
        results: List[CropSearchResult] = []
        index = 0
        while index < len(candidates):
            crop = candidates[index]
            evaluation = self._evaluate_crop(crop, criteria)
            if evaluation is not None:
                results.append(evaluation)
            index += 1
        return results

    def _evaluate_crop(
        self,
        crop: ComprehensiveCropData,
        criteria: TaxonomyFilterCriteria,
    ) -> Optional[CropSearchResult]:
        """Evaluate a single crop against all search criteria."""
        if not self._passes_taxonomy_filters(crop, criteria):
            return None

        filter_results: List[FilterEvaluation] = []
        filter_results.append(self._evaluate_text_filter(crop, criteria))
        filter_results.append(self._evaluate_geographic_filter(crop, criteria.geographic_filter))
        filter_results.append(self._evaluate_climate_filter(crop, criteria.climate_filter))
        filter_results.append(self._evaluate_soil_filter(crop, criteria.soil_filter))
        filter_results.append(self._evaluate_agricultural_filter(crop, criteria.agricultural_filter))
        filter_results.append(self._evaluate_management_filter(crop, criteria.management_filter))
        filter_results.append(self._evaluate_sustainability_filter(crop, criteria.sustainability_filter))
        filter_results.append(self._evaluate_economic_filter(crop, criteria.economic_filter))

        applicable_filters = 0
        matched_filters = 0
        partial_filters = 0
        filter_index = 0
        while filter_index < len(filter_results):
            current = filter_results[filter_index]
            if current.active:
                applicable_filters += 1
                if current.matched:
                    matched_filters += 1
                elif current.partial:
                    partial_filters += 1
            filter_index += 1

        passes_filters = self._determine_pass_status(criteria.search_operator, applicable_filters, matched_filters, partial_filters)
        if not passes_filters:
            return None

        relevance_score, matching_details, partial_details, missing_details, highlights, similarity = self._compile_scores(filter_results, matched_filters, applicable_filters)
        ranking_details, score_breakdown = self._build_result_ranking_details(
            filter_results,
            applicable_filters,
            matched_filters,
            partial_filters,
        )
        suitability_score = relevance_score

        result = CropSearchResult(
            crop=crop,
            relevance_score=relevance_score,
            suitability_score=suitability_score,
            matching_criteria=matching_details,
            partial_matches=partial_details,
            missing_criteria=missing_details,
            search_highlights=highlights,
            similarity_factors=similarity,
            score_breakdown=score_breakdown,
            ranking_details=ranking_details,
            recommendation_notes=[],
            potential_concerns=[],
        )
        return result

    def _passes_taxonomy_filters(self, crop: ComprehensiveCropData, criteria: TaxonomyFilterCriteria) -> bool:
        """Ensure crop satisfies taxonomy specific filters before scoring."""
        taxonomy = crop.taxonomic_hierarchy
        if criteria.families:
            if taxonomy is None or taxonomy.family is None:
                return False
            if not self._value_in_iterable(taxonomy.family, criteria.families):
                return False

        if criteria.genera:
            if taxonomy is None or taxonomy.genus is None:
                return False
            if not self._value_in_iterable(taxonomy.genus, criteria.genera):
                return False

        return True

    def _value_in_iterable(self, value: str, container: List[str]) -> bool:
        """Case-insensitive containment helper."""
        if value is None:
            return False
        lower_value = value.lower()
        index = 0
        while index < len(container):
            candidate = container[index]
            if candidate is not None and lower_value == candidate.lower():
                return True
            index += 1
        return False

    def _enum_value(self, enum_member) -> Optional[str]:
        if enum_member is None:
            return None
        if hasattr(enum_member, "value"):
            return str(enum_member.value)
        return str(enum_member)

    def _rank_in_order(self, value: Optional[str], order: List[str]) -> int:
        if value is None:
            return -1
        normalized = value.lower()
        index = 0
        while index < len(order):
            if normalized == order[index]:
                return index
            index += 1
        return -1

    def _meets_rank_requirement(self, candidate, required, order: List[str]) -> bool:
        candidate_value = self._enum_value(candidate)
        required_value = self._enum_value(required)
        if required_value is None:
            return True
        candidate_rank = self._rank_in_order(candidate_value, order)
        required_rank = self._rank_in_order(required_value, order)
        if candidate_rank == -1:
            return False
        return candidate_rank >= required_rank

    def _evaluate_text_filter(self, crop: ComprehensiveCropData, criteria: TaxonomyFilterCriteria) -> FilterEvaluation:
        evaluation = FilterEvaluation("text", self.scoring_weights.get("text_match", 0.18))
        terms = self._collect_search_terms(criteria)
        if len(terms) == 0:
            evaluation.score = 1.0
            evaluation.matched = True
            return evaluation

        evaluation.active = True
        fields = self._gather_text_fields(crop)
        matched_terms: List[str] = []
        term_count = len(terms)
        matched_count = 0
        term_index = 0
        while term_index < term_count:
            term = terms[term_index]
            if self._term_in_fields(term, fields):
                matched_count += 1
                matched_terms.append(term)
                evaluation.notes.append("Matched term '" + term + "'")
            else:
                evaluation.missing_notes.append("No match for term '" + term + "'")
            term_index += 1

        if len(matched_terms) > 0:
            evaluation.highlights["text"] = []
            index = 0
            while index < len(matched_terms):
                evaluation.highlights["text"].append(matched_terms[index])
                index += 1

        if term_count > 0:
            evaluation.score = matched_count / float(term_count)
        else:
            evaluation.score = 1.0

        if matched_count == term_count and term_count > 0:
            evaluation.matched = True
        elif matched_count > 0:
            evaluation.partial = True
        return evaluation

    def _gather_text_fields(self, crop: ComprehensiveCropData) -> List[str]:
        fields: List[str] = []
        if crop.crop_name:
            fields.append(crop.crop_name.lower())
        scientific = crop.scientific_name
        if scientific:
            fields.append(scientific.lower())
        if crop.search_keywords:
            index = 0
            while index < len(crop.search_keywords):
                keyword = crop.search_keywords[index]
                if keyword:
                    fields.append(keyword.lower())
                index += 1
        if crop.tags:
            index = 0
            while index < len(crop.tags):
                tag = crop.tags[index]
                if tag:
                    fields.append(tag.lower())
                index += 1
        taxonomy = crop.taxonomic_hierarchy
        if taxonomy and taxonomy.common_synonyms:
            index = 0
            while index < len(taxonomy.common_synonyms):
                synonym = taxonomy.common_synonyms[index]
                if synonym:
                    fields.append(synonym.lower())
                index += 1
        return fields

    def _term_in_fields(self, term: str, fields: List[str]) -> bool:
        if term is None or len(term) == 0:
            return False
        normalized = term.lower()
        index = 0
        while index < len(fields):
            field_value = fields[index]
            if normalized in field_value:
                return True
            index += 1
        return False

    def _collect_search_terms(self, criteria: TaxonomyFilterCriteria) -> List[str]:
        terms: List[str] = []
        for value in [criteria.text_search, criteria.common_name_search, criteria.scientific_name_search]:
            if value:
                for raw_term in value.split():
                    cleaned = raw_term.strip()
                    if len(cleaned) > 0:
                        terms.append(cleaned)
        return terms

    def _evaluate_geographic_filter(self, crop: ComprehensiveCropData, geo_filter) -> FilterEvaluation:
        evaluation = FilterEvaluation("geographic", self.scoring_weights.get("geographic_match", 0.15))
        if geo_filter is None:
            evaluation.score = 1.0
        else:
            evaluation.active = self._geographic_filter_has_values(geo_filter)
            if not evaluation.active:
                evaluation.score = 1.0
                return evaluation

            adaptation = crop.climate_adaptations
            if adaptation is None:
                evaluation.partial_notes.append("No climate adaptation data for geographic filter")
                return evaluation

            checks = 0
            matches = 0

            if geo_filter.hardiness_zones:
                checks += 1
                if adaptation.hardiness_zones:
                    overlap = self._intersect_lists(adaptation.hardiness_zones, geo_filter.hardiness_zones)
                    if len(overlap) > 0:
                        matches += 1
                        evaluation.notes.append("Hardiness zones overlap")
                    else:
                        evaluation.missing_notes.append("Hardiness zones do not overlap")
                else:
                    evaluation.partial_notes.append("Crop lacks hardiness zone data")

            if geo_filter.elevation_min_feet is not None or geo_filter.elevation_max_feet is not None:
                checks += 1
                min_ok = True
                max_ok = True
                if geo_filter.elevation_min_feet is not None and adaptation.elevation_min_feet is not None:
                    if adaptation.elevation_max_feet is not None and adaptation.elevation_max_feet < geo_filter.elevation_min_feet:
                        min_ok = False
                if geo_filter.elevation_max_feet is not None and adaptation.elevation_max_feet is not None:
                    if adaptation.elevation_min_feet is not None and adaptation.elevation_min_feet > geo_filter.elevation_max_feet:
                        max_ok = False
                if min_ok and max_ok:
                    matches += 1
                    evaluation.notes.append("Elevation range compatible")
                else:
                    evaluation.missing_notes.append("Elevation outside requested range")

            if checks > 0:
                evaluation.score = matches / float(checks)
            else:
                evaluation.score = 1.0

            if evaluation.score >= 0.99:
                evaluation.matched = True
            elif evaluation.score > 0.0:
                evaluation.partial = True
        return evaluation

    def _geographic_filter_has_values(self, geo_filter) -> bool:
        if geo_filter.hardiness_zones:
            if len(geo_filter.hardiness_zones) > 0:
                return True
        if geo_filter.latitude_range:
            return True
        if geo_filter.longitude_range:
            return True
        if geo_filter.elevation_min_feet is not None:
            return True
        if geo_filter.elevation_max_feet is not None:
            return True
        if geo_filter.states:
            if len(geo_filter.states) > 0:
                return True
        if geo_filter.countries:
            if len(geo_filter.countries) > 0:
                return True
        if geo_filter.koppen_zones:
            if len(geo_filter.koppen_zones) > 0:
                return True
        return False

    def _intersect_lists(self, first: List[str], second: List[str]) -> List[str]:
        overlap: List[str] = []
        index = 0
        while index < len(first):
            value = first[index]
            if value is not None and self._value_in_iterable(value, second):
                overlap.append(value)
            index += 1
        return overlap

    def _evaluate_climate_filter(self, crop: ComprehensiveCropData, climate_filter) -> FilterEvaluation:
        evaluation = FilterEvaluation("climate", self.scoring_weights.get("climate_match", 0.20))
        if climate_filter is None:
            evaluation.score = 1.0
        else:
            evaluation.active = self._climate_filter_has_values(climate_filter)
            if not evaluation.active:
                evaluation.score = 1.0
                return evaluation

            adaptation: Optional[CropClimateAdaptations] = crop.climate_adaptations
            if adaptation is None:
                evaluation.partial_notes.append("No climate adaptation data available")
                return evaluation

            checks = 0
            matches = 0

            if climate_filter.temperature_range_f:
                checks += 1
                temp_match = self._temperature_overlap(adaptation, climate_filter.temperature_range_f)
                if temp_match:
                    matches += 1
                    evaluation.notes.append("Temperature range compatible")
                else:
                    evaluation.missing_notes.append("Temperature range outside tolerance")

            if climate_filter.drought_tolerance_required:
                checks += 1
                drought_order = ["none", "low", "moderate", "high", "extreme"]
                if self._meets_rank_requirement(adaptation.drought_tolerance, climate_filter.drought_tolerance_required, drought_order):
                    matches += 1
                    evaluation.notes.append("Drought tolerance requirement met")
                else:
                    evaluation.missing_notes.append("Insufficient drought tolerance")

            if climate_filter.frost_tolerance_required:
                checks += 1
                frost_order = ["none", "light", "moderate", "heavy"]
                if self._meets_rank_requirement(adaptation.frost_tolerance, climate_filter.frost_tolerance_required, frost_order):
                    matches += 1
                    evaluation.notes.append("Frost tolerance requirement met")
                else:
                    evaluation.missing_notes.append("Frost tolerance requirement not met")

            if climate_filter.heat_tolerance_required:
                checks += 1
                heat_order = ["low", "moderate", "high", "extreme"]
                if self._meets_rank_requirement(adaptation.heat_tolerance, climate_filter.heat_tolerance_required, heat_order):
                    matches += 1
                    evaluation.notes.append("Heat tolerance requirement met")
                else:
                    evaluation.missing_notes.append("Heat tolerance requirement not met")

            if checks > 0:
                evaluation.score = matches / float(checks)
            else:
                evaluation.score = 1.0

            if evaluation.score >= 0.99:
                evaluation.matched = True
            elif evaluation.score > 0.0:
                evaluation.partial = True
        return evaluation

    def _climate_filter_has_values(self, climate_filter) -> bool:
        if climate_filter.temperature_range_f:
            return True
        if climate_filter.drought_tolerance_required:
            return True
        if climate_filter.frost_tolerance_required:
            return True
        if climate_filter.heat_tolerance_required:
            return True
        if climate_filter.annual_precipitation_range:
            return True
        if climate_filter.growing_season_length_days:
            return True
        if climate_filter.photoperiod_requirements:
            if len(climate_filter.photoperiod_requirements) > 0:
                return True
        return False

    def _temperature_overlap(self, adaptation: CropClimateAdaptations, requested: Dict[str, float]) -> bool:
        if adaptation.optimal_temp_min_f is None or adaptation.optimal_temp_max_f is None:
            return False
        min_key = "min"
        max_key = "max"
        request_min = requested.get(min_key)
        request_max = requested.get(max_key)
        if request_min is None or request_max is None:
            return False
        crop_min = adaptation.optimal_temp_min_f
        crop_max = adaptation.optimal_temp_max_f
        overlap_min = max(crop_min, request_min)
        overlap_max = min(crop_max, request_max)
        return overlap_max >= overlap_min

    def _evaluate_soil_filter(self, crop: ComprehensiveCropData, soil_filter) -> FilterEvaluation:
        evaluation = FilterEvaluation("soil", self.scoring_weights.get("soil_match", 0.15))
        if soil_filter is None:
            evaluation.score = 1.0
        else:
            evaluation.active = self._soil_filter_has_values(soil_filter)
            if not evaluation.active:
                evaluation.score = 1.0
                return evaluation

            soil: Optional[CropSoilRequirements] = crop.soil_requirements
            if soil is None:
                evaluation.partial_notes.append("No soil requirement data available")
                return evaluation

            checks = 0
            matches = 0

            if soil_filter.ph_range:
                checks += 1
                if self._ph_overlap(soil, soil_filter.ph_range, soil_filter.ph_tolerance_strict):
                    matches += 1
                    evaluation.notes.append("Soil pH range compatible")
                else:
                    evaluation.missing_notes.append("Soil pH outside acceptable range")

            if soil_filter.texture_classes:
                checks += 1
                if self._texture_match(soil, soil_filter.texture_classes):
                    matches += 1
                    evaluation.notes.append("Soil texture requirement met")
                else:
                    evaluation.missing_notes.append("Soil texture requirement not met")

            if soil_filter.drainage_classes:
                checks += 1
                if soil.drainage_requirement is not None and self._value_in_iterable(soil.drainage_requirement.value, soil_filter.drainage_classes):
                    matches += 1
                    evaluation.notes.append("Drainage requirement met")
                else:
                    evaluation.missing_notes.append("Drainage requirement not met")

            if checks > 0:
                evaluation.score = matches / float(checks)
            else:
                evaluation.score = 1.0

            if evaluation.score >= 0.99:
                evaluation.matched = True
            elif evaluation.score > 0.0:
                evaluation.partial = True
        return evaluation

    def _soil_filter_has_values(self, soil_filter) -> bool:
        if soil_filter.ph_range:
            return True
        if soil_filter.texture_classes:
            if len(soil_filter.texture_classes) > 0:
                return True
        if soil_filter.drainage_classes:
            if len(soil_filter.drainage_classes) > 0:
                return True
        if soil_filter.salinity_tolerance_required:
            return True
        if soil_filter.acidity_tolerance_required:
            return True
        if soil_filter.low_fertility_tolerance is not None:
            return True
        if soil_filter.high_fertility_requirement is not None:
            return True
        return False

    def _ph_overlap(self, soil: CropSoilRequirements, requested: Dict[str, float], strict: bool) -> bool:
        if soil.optimal_ph_min is None or soil.optimal_ph_max is None:
            return False
        min_key = "min"
        max_key = "max"
        req_min = requested.get(min_key)
        req_max = requested.get(max_key)
        if req_min is None or req_max is None:
            return False
        lower_bound = soil.optimal_ph_min
        upper_bound = soil.optimal_ph_max
        if not strict and soil.tolerable_ph_min is not None and soil.tolerable_ph_max is not None:
            lower_bound = soil.tolerable_ph_min
            upper_bound = soil.tolerable_ph_max
        overlap_min = max(lower_bound, req_min)
        overlap_max = min(upper_bound, req_max)
        return overlap_max >= overlap_min

    def _texture_match(self, soil: CropSoilRequirements, requested: List[str]) -> bool:
        if soil.preferred_textures:
            index = 0
            while index < len(soil.preferred_textures):
                texture = soil.preferred_textures[index]
                if texture and self._value_in_iterable(texture, requested):
                    return True
                index += 1
        if soil.tolerable_textures:
            index = 0
            while index < len(soil.tolerable_textures):
                texture = soil.tolerable_textures[index]
                if texture and self._value_in_iterable(texture, requested):
                    return True
                index += 1
        return False

    def _evaluate_agricultural_filter(self, crop: ComprehensiveCropData, ag_filter) -> FilterEvaluation:
        evaluation = FilterEvaluation("agricultural", self.scoring_weights.get("agricultural_match", 0.12))
        if ag_filter is None:
            evaluation.score = 1.0
            return evaluation

        evaluation.active = self._agricultural_filter_has_values(ag_filter)
        if not evaluation.active:
            evaluation.score = 1.0
            return evaluation

        classification: Optional[CropAgriculturalClassification] = crop.agricultural_classification
        if classification is None:
            evaluation.partial_notes.append("No agricultural classification data available")
            return evaluation

        checks = 0
        matches = 0

        if ag_filter.categories:
            checks += 1
            if classification.crop_category and self._enum_in_iterable(classification.crop_category.value, ag_filter.categories):
                matches += 1
                evaluation.notes.append("Crop category requirement met")
            else:
                evaluation.missing_notes.append("Crop category requirement not met")

        if ag_filter.primary_uses:
            checks += 1
            if classification.primary_use and self._enum_in_iterable(classification.primary_use.value, ag_filter.primary_uses):
                matches += 1
                evaluation.notes.append("Primary use requirement met")
            else:
                evaluation.missing_notes.append("Primary use requirement not met")

        if ag_filter.growth_habits:
            checks += 1
            if classification.growth_habit and self._enum_in_iterable(classification.growth_habit.value, ag_filter.growth_habits):
                matches += 1
                evaluation.notes.append("Growth habit requirement met")
            else:
                evaluation.missing_notes.append("Growth habit requirement not met")

        if ag_filter.plant_types:
            checks += 1
            if classification.plant_type and self._enum_in_iterable(classification.plant_type.value, ag_filter.plant_types):
                matches += 1
                evaluation.notes.append("Plant type requirement met")
            else:
                evaluation.missing_notes.append("Plant type requirement not met")

        if ag_filter.nitrogen_fixing_required is not None:
            checks += 1
            if classification.nitrogen_fixing == ag_filter.nitrogen_fixing_required:
                matches += 1
                evaluation.notes.append("Nitrogen fixing requirement met")
            else:
                evaluation.missing_notes.append("Nitrogen fixing requirement not met")

        if checks > 0:
            evaluation.score = matches / float(checks)
        else:
            evaluation.score = 1.0

        if evaluation.score >= 0.99:
            evaluation.matched = True
        elif evaluation.score > 0.0:
            evaluation.partial = True
        return evaluation

    def _agricultural_filter_has_values(self, ag_filter) -> bool:
        if ag_filter.categories and len(ag_filter.categories) > 0:
            return True
        if ag_filter.primary_uses and len(ag_filter.primary_uses) > 0:
            return True
        if ag_filter.exclude_categories and len(ag_filter.exclude_categories) > 0:
            return True
        if ag_filter.growth_habits and len(ag_filter.growth_habits) > 0:
            return True
        if ag_filter.plant_types and len(ag_filter.plant_types) > 0:
            return True
        if ag_filter.photosynthesis_types and len(ag_filter.photosynthesis_types) > 0:
            return True
        if ag_filter.nitrogen_fixing_required is not None:
            return True
        if ag_filter.cover_crop_only is not None:
            return True
        if ag_filter.companion_crop_suitable is not None:
            return True
        if ag_filter.max_height_inches is not None:
            return True
        if ag_filter.min_height_inches is not None:
            return True
        return False

    def _enum_in_iterable(self, value: str, container: List) -> bool:
        if value is None:
            return False
        index = 0
        while index < len(container):
            item = container[index]
            if item is None:
                index += 1
                continue
            candidate = item
            if hasattr(candidate, "value"):
                candidate_value = candidate.value
            else:
                candidate_value = str(candidate)
            if candidate_value.lower() == value.lower():
                return True
            index += 1
        return False

    def _evaluate_management_filter(self, crop: ComprehensiveCropData, management_filter) -> FilterEvaluation:
        evaluation = FilterEvaluation("management", self.scoring_weights.get("management_match", 0.05))
        if management_filter is None:
            evaluation.score = 1.0
            return evaluation

        evaluation.active = self._management_filter_has_values(management_filter)
        if not evaluation.active:
            evaluation.score = 1.0
            return evaluation

        attributes = crop.filtering_attributes
        if attributes is None:
            evaluation.partial_notes.append("No management attribute data available")
            return evaluation

        checks = 0
        matches = 0

        if management_filter.max_management_complexity is not None and attributes.management_complexity is not None:
            checks += 1
            if attributes.management_complexity.value <= management_filter.max_management_complexity.value:
                matches += 1
                evaluation.notes.append("Management complexity within range")
            else:
                evaluation.missing_notes.append("Management complexity exceeds preference")

        if management_filter.max_input_requirements is not None and attributes.input_requirements is not None:
            checks += 1
            if attributes.input_requirements.value <= management_filter.max_input_requirements.value:
                matches += 1
                evaluation.notes.append("Input requirements within range")
            else:
                evaluation.missing_notes.append("Input requirements exceed preference")

        if management_filter.max_labor_requirements is not None and attributes.labor_requirements is not None:
            checks += 1
            if attributes.labor_requirements.value <= management_filter.max_labor_requirements.value:
                matches += 1
                evaluation.notes.append("Labor requirements within range")
            else:
                evaluation.missing_notes.append("Labor requirements exceed preference")

        if checks > 0:
            evaluation.score = matches / float(checks)
        else:
            evaluation.score = 1.0

        if evaluation.score >= 0.99:
            evaluation.matched = True
        elif evaluation.score > 0.0:
            evaluation.partial = True
        return evaluation

    def _management_filter_has_values(self, management_filter) -> bool:
        if management_filter.max_management_complexity is not None:
            return True
        if management_filter.max_input_requirements is not None:
            return True
        if management_filter.max_labor_requirements is not None:
            return True
        if management_filter.precision_ag_compatible_required is not None:
            return True
        if management_filter.low_tech_suitable is not None:
            return True
        if management_filter.farming_systems and len(management_filter.farming_systems) > 0:
            return True
        if management_filter.organic_suitable is not None:
            return True
        return False

    def _evaluate_sustainability_filter(self, crop: ComprehensiveCropData, sustainability_filter) -> FilterEvaluation:
        evaluation = FilterEvaluation("sustainability", self.scoring_weights.get("sustainability_match", 0.04))
        if sustainability_filter is None:
            evaluation.score = 1.0
            return evaluation

        evaluation.active = self._sustainability_filter_has_values(sustainability_filter)
        if not evaluation.active:
            evaluation.score = 1.0
            return evaluation

        attributes = crop.filtering_attributes
        if attributes is None:
            evaluation.partial_notes.append("No sustainability attribute data available")
            return evaluation

        checks = 0
        matches = 0

        if sustainability_filter.min_carbon_sequestration is not None and attributes.carbon_sequestration_potential is not None:
            checks += 1
            if attributes.carbon_sequestration_potential.value >= sustainability_filter.min_carbon_sequestration.value:
                matches += 1
                evaluation.notes.append("Carbon sequestration meets requirement")
            else:
                evaluation.missing_notes.append("Carbon sequestration below requirement")

        if sustainability_filter.drought_resilient_only and crop.climate_adaptations is not None:
            checks += 1
            drought_order = ["none", "low", "moderate", "high", "extreme"]
            if self._meets_rank_requirement(crop.climate_adaptations.drought_tolerance, "high", drought_order):
                matches += 1
                evaluation.notes.append("Drought resilience requirement met")
            else:
                evaluation.missing_notes.append("Crop not drought resilient")

        if checks > 0:
            evaluation.score = matches / float(checks)
        else:
            evaluation.score = 1.0

        if evaluation.score >= 0.99:
            evaluation.matched = True
        elif evaluation.score > 0.0:
            evaluation.partial = True
        return evaluation

    def _sustainability_filter_has_values(self, sustainability_filter) -> bool:
        if sustainability_filter.min_carbon_sequestration is not None:
            return True
        if sustainability_filter.min_biodiversity_support is not None:
            return True
        if sustainability_filter.min_pollinator_value is not None:
            return True
        if sustainability_filter.min_water_efficiency is not None:
            return True
        if sustainability_filter.drought_resilient_only:
            return True
        if sustainability_filter.erosion_control_capable is not None:
            return True
        if sustainability_filter.soil_building_capable is not None:
            return True
        return False

    def _evaluate_economic_filter(self, crop: ComprehensiveCropData, economic_filter) -> FilterEvaluation:
        evaluation = FilterEvaluation("economic", self.scoring_weights.get("economic_match", 0.04))
        if economic_filter is None:
            evaluation.score = 1.0
            return evaluation

        evaluation.active = self._economic_filter_has_values(economic_filter)
        if not evaluation.active:
            evaluation.score = 1.0
            return evaluation

        attributes = crop.filtering_attributes
        if attributes is None:
            evaluation.partial_notes.append("No economic attribute data available")
            return evaluation

        checks = 0
        matches = 0

        if economic_filter.market_stability_required is not None and attributes.market_stability is not None:
            checks += 1
            if attributes.market_stability.value >= economic_filter.market_stability_required.value:
                matches += 1
                evaluation.notes.append("Market stability meets requirement")
            else:
                evaluation.missing_notes.append("Market stability below requirement")

        if economic_filter.premium_market_potential is not None:
            checks += 1
            if attributes.price_premium_potential == economic_filter.premium_market_potential:
                matches += 1
                evaluation.notes.append("Premium market potential requirement met")
            else:
                evaluation.missing_notes.append("Premium market potential requirement not met")

        if checks > 0:
            evaluation.score = matches / float(checks)
        else:
            evaluation.score = 1.0

        if evaluation.score >= 0.99:
            evaluation.matched = True
        elif evaluation.score > 0.0:
            evaluation.partial = True
        return evaluation

    def _economic_filter_has_values(self, economic_filter) -> bool:
        if economic_filter.market_stability_required is not None:
            return True
        if economic_filter.premium_market_potential is not None:
            return True
        if economic_filter.processing_opportunities and len(economic_filter.processing_opportunities) > 0:
            return True
        if economic_filter.low_establishment_cost is not None:
            return True
        if economic_filter.high_roi_potential is not None:
            return True
        return False

    def _determine_pass_status(
        self,
        operator: SearchOperator,
        applicable_filters: int,
        matched_filters: int,
        partial_filters: int,
    ) -> bool:
        if applicable_filters == 0:
            return True
        if operator == SearchOperator.AND:
            return matched_filters == applicable_filters
        if operator == SearchOperator.OR:
            return matched_filters > 0 or partial_filters > 0
        if operator == SearchOperator.NOT:
            return matched_filters == 0 and partial_filters == 0
        return matched_count > 0

    def _calculate_cache_ttl(self, request: CropSearchRequest) -> int:
        """Calculate cache TTL based on query complexity and filters."""
        # Base TTL: 1 hour
        ttl = 3600
        
        # Extend TTL if query is more general (fewer specific filters)
        filter_count = 0
        criteria = request.filter_criteria
        if criteria.text_search: filter_count += 1
        if criteria.families: filter_count += 1
        if criteria.genera: filter_count += 1
        if criteria.geographic_filter: filter_count += 1
        if criteria.climate_filter: filter_count += 1
        if criteria.soil_filter: filter_count += 1
        if criteria.agricultural_filter: filter_count += 1
        if criteria.management_filter: filter_count += 1
        if criteria.sustainability_filter: filter_count += 1
        if criteria.economic_filter: filter_count += 1
        
        if filter_count <= 2:
            # General queries get longer cache time (24 hours)
            ttl = 86400
        elif filter_count <= 4:
            # Moderate queries get medium cache time (4 hours)
            ttl = 14400
        else:
            # Specific queries get shorter cache time (1 hour)
            ttl = 3600
            
        # Adjust for time-sensitive data
        if criteria.geographic_filter and criteria.geographic_filter.latitude_range:
            # Geographic queries may need more frequent updates
            ttl = min(ttl, 7200)  # Max 2 hours for geographic queries
            
        return ttl

    def _compile_scores(
        self,
        filter_results: List[FilterEvaluation],
        matched_filters: int,
        applicable_filters: int,
    ) -> Tuple[float, List[str], List[str], List[str], Dict[str, List[str]], Dict[str, float]]:
        matching_details: List[str] = []
        partial_details: List[str] = []
        missing_details: List[str] = []
        highlights: Dict[str, List[str]] = {}
        weighted_sum = 0.0
        total_weight = 0.0

        index = 0
        while index < len(filter_results):
            evaluation = filter_results[index]
            if evaluation.highlights:
                for key, values in evaluation.highlights.items():
                    if key not in highlights:
                        highlights[key] = []
                    value_index = 0
                    while value_index < len(values):
                        highlights[key].append(values[value_index])
                        value_index += 1
            summary_text = evaluation.name + " filter applied"
            if evaluation.matched:
                matching_details.append(summary_text)
            elif evaluation.partial:
                partial_details.append(summary_text)
            elif evaluation.active:
                missing_details.append(summary_text)

            if evaluation.active:
                weighted_sum += evaluation.score * evaluation.weight
                total_weight += evaluation.weight
            index += 1

        relevance_score = 0.0
        if total_weight > 0.0:
            relevance_score = weighted_sum / total_weight

        similarity_factors: Dict[str, float] = {}
        if applicable_filters > 0:
            similarity_factors["filters_matched_ratio"] = matched_filters / float(applicable_filters)

        return relevance_score, matching_details, partial_details, missing_details, highlights, similarity_factors

    def _build_result_ranking_details(
        self,
        filter_results: List[FilterEvaluation],
        applicable_filters: int,
        matched_filters: int,
        partial_filters: int,
    ) -> Tuple[ResultRankingDetails, Dict[str, float]]:
        breakdown: Dict[str, float] = {}
        filter_scores: List[FilterScoreBreakdown] = []

        index = 0
        while index < len(filter_results):
            evaluation = filter_results[index]
            if evaluation.active:
                breakdown[evaluation.name] = evaluation.score
                collected_notes: List[str] = []

                note_index = 0
                while note_index < len(evaluation.notes):
                    collected_notes.append(evaluation.notes[note_index])
                    note_index += 1

                note_index = 0
                while note_index < len(evaluation.partial_notes):
                    note_text = "Partial: " + evaluation.partial_notes[note_index]
                    collected_notes.append(note_text)
                    note_index += 1

                note_index = 0
                while note_index < len(evaluation.missing_notes):
                    note_text = "Missing: " + evaluation.missing_notes[note_index]
                    collected_notes.append(note_text)
                    note_index += 1

                filter_scores.append(
                    FilterScoreBreakdown(
                        name=evaluation.name,
                        weight=evaluation.weight,
                        score=evaluation.score,
                        matched=evaluation.matched,
                        partial=evaluation.partial,
                        notes=collected_notes,
                    )
                )
            index += 1

        missing_filters = 0
        if applicable_filters > matched_filters + partial_filters:
            missing_filters = applicable_filters - matched_filters - partial_filters

        coverage = 1.0
        if applicable_filters > 0:
            coverage = matched_filters / float(applicable_filters)

        ranking_details = ResultRankingDetails(
            active_filters=applicable_filters,
            matched_filters=matched_filters,
            partial_filters=partial_filters,
            missing_filters=missing_filters,
            coverage=coverage,
            filter_scores=filter_scores,
        )

        return ranking_details, breakdown

    def _build_ranking_overview(self, results: List[CropSearchResult]) -> Optional[SearchRankingOverview]:
        if len(results) == 0:
            return None

        scores: List[float] = []
        index = 0
        best_score = 0.0
        worst_score = 0.0
        coverage_sum = 0.0
        coverage_count = 0

        while index < len(results):
            current_result = results[index]
            score = current_result.relevance_score
            scores.append(score)

            if index == 0:
                best_score = score
                worst_score = score
            else:
                if score > best_score:
                    best_score = score
                if score < worst_score:
                    worst_score = score

            details = current_result.ranking_details
            if details is not None:
                coverage_sum += details.coverage
                coverage_count += 1

            index += 1

        scores.sort()

        median_score = 0.0
        score_count = len(scores)
        if score_count > 0:
            middle_index = score_count // 2
            if score_count % 2 == 1:
                median_score = scores[middle_index]
            else:
                first_value = scores[middle_index - 1]
                second_value = scores[middle_index]
                median_score = (first_value + second_value) / 2.0

        average_coverage = 0.0
        if coverage_count > 0:
            average_coverage = coverage_sum / float(coverage_count)

        return SearchRankingOverview(
            best_score=best_score,
            worst_score=worst_score,
            median_score=median_score,
            average_coverage=average_coverage,
        )

    def _build_visualization_summary(self, results: List[CropSearchResult]) -> SearchVisualizationSummary:
        summary = SearchVisualizationSummary()
        if len(results) == 0:
            return summary

        bucket_ranges: List[Tuple[str, float, float]] = []
        bucket_ranges.append(("0.00-0.25", 0.0, 0.25))
        bucket_ranges.append(("0.25-0.50", 0.25, 0.5))
        bucket_ranges.append(("0.50-0.75", 0.5, 0.75))
        bucket_ranges.append(("0.75-1.00", 0.75, 1.0))

        bucket_counts: Dict[str, int] = {}
        range_index = 0
        while range_index < len(bucket_ranges):
            label_only = bucket_ranges[range_index][0]
            bucket_counts[label_only] = 0
            range_index += 1

        result_index = 0
        while result_index < len(results):
            score = results[result_index].relevance_score
            range_index = 0
            placed = False
            while range_index < len(bucket_ranges) and placed is False:
                bucket_info = bucket_ranges[range_index]
                label_value = bucket_info[0]
                lower_bound = bucket_info[1]
                upper_bound = bucket_info[2]

                if range_index == len(bucket_ranges) - 1:
                    if score >= lower_bound and score <= upper_bound:
                        bucket_counts[label_value] = bucket_counts[label_value] + 1
                        placed = True
                else:
                    if score >= lower_bound and score < upper_bound:
                        bucket_counts[label_value] = bucket_counts[label_value] + 1
                        placed = True
                range_index += 1
            result_index += 1

        score_buckets: List[ScoreBucket] = []
        range_index = 0
        while range_index < len(bucket_ranges):
            bucket_info = bucket_ranges[range_index]
            label_value = bucket_info[0]
            lower_bound = bucket_info[1]
            upper_bound = bucket_info[2]
            count_value = bucket_counts.get(label_value, 0)
            score_buckets.append(
                ScoreBucket(
                    label=label_value,
                    count=count_value,
                    minimum=lower_bound,
                    maximum=upper_bound,
                )
            )
            range_index += 1

        total_scores: Dict[str, float] = {}
        appearance_counts: Dict[str, int] = {}
        matched_counts: Dict[str, int] = {}
        partial_counts: Dict[str, int] = {}
        missing_counts: Dict[str, int] = {}
        weights: Dict[str, float] = {}

        result_index = 0
        while result_index < len(results):
            details = results[result_index].ranking_details
            if details is not None:
                filter_index = 0
                while filter_index < len(details.filter_scores):
                    score_detail = details.filter_scores[filter_index]
                    name_value = score_detail.name
                    if name_value not in total_scores:
                        total_scores[name_value] = 0.0
                        appearance_counts[name_value] = 0
                        matched_counts[name_value] = 0
                        partial_counts[name_value] = 0
                        missing_counts[name_value] = 0
                        weights[name_value] = score_detail.weight

                    total_scores[name_value] = total_scores[name_value] + score_detail.score
                    appearance_counts[name_value] = appearance_counts[name_value] + 1

                    if score_detail.matched:
                        matched_counts[name_value] = matched_counts[name_value] + 1
                    elif score_detail.partial:
                        partial_counts[name_value] = partial_counts[name_value] + 1
                    else:
                        missing_counts[name_value] = missing_counts[name_value] + 1

                    filter_index += 1
            result_index += 1

        filter_aggregates: List[FilterContributionAggregate] = []
        for name_value in total_scores:
            appearances = appearance_counts.get(name_value, 0)
            average_score = 0.0
            if appearances > 0:
                average_score = total_scores[name_value] / float(appearances)

            aggregate = FilterContributionAggregate(
                name=name_value,
                average_score=average_score,
                matched_results=matched_counts.get(name_value, 0),
                partial_results=partial_counts.get(name_value, 0),
                weight=weights.get(name_value, 0.0),
            )
            filter_aggregates.append(aggregate)

        filter_aggregates.sort(key=lambda item: item.average_score, reverse=True)

        missing_total = 0
        for name_value in missing_counts:
            missing_total = missing_total + missing_counts[name_value]

        match_summary: Dict[str, int] = {}
        match_summary['matched_filters'] = 0
        match_summary['partial_filters'] = 0
        match_summary['missing_filters'] = 0

        result_index = 0
        while result_index < len(results):
            details = results[result_index].ranking_details
            if details is not None:
                match_summary['matched_filters'] = match_summary['matched_filters'] + details.matched_filters
                match_summary['partial_filters'] = match_summary['partial_filters'] + details.partial_filters
                match_summary['missing_filters'] = match_summary['missing_filters'] + details.missing_filters
            result_index += 1

        highlights: List[str] = []

        if len(filter_aggregates) > 0:
            top_aggregate = filter_aggregates[0]
            scored_value = round(top_aggregate.average_score, 2)
            highlights.append(
                "Top filter dimension: " + top_aggregate.name + " (avg score " + str(scored_value) + ")"
            )

        dominant_bucket_label = ""
        dominant_bucket_count = 0
        bucket_index = 0
        while bucket_index < len(score_buckets):
            bucket = score_buckets[bucket_index]
            if bucket.count > dominant_bucket_count:
                dominant_bucket_count = bucket.count
                dominant_bucket_label = bucket.label
            bucket_index += 1

        if dominant_bucket_count > 0:
            highlights.append(
                "Most results fall in score range " + dominant_bucket_label + " (" + str(dominant_bucket_count) + " results)"
            )

        total_filters = match_summary['matched_filters'] + match_summary['partial_filters'] + match_summary['missing_filters']
        if total_filters > 0:
            coverage_ratio = match_summary['matched_filters'] / float(total_filters)
            coverage_percent = int(round(coverage_ratio * 100))
            highlights.append("Filter coverage: " + str(coverage_percent) + "% fully satisfied")

        if missing_total > 0:
            highlights.append(str(missing_total) + " filter evaluations lacked full matches")

        summary.score_distribution = score_buckets
        summary.filter_contributions = filter_aggregates
        summary.match_summary = match_summary
        summary.highlights = highlights

        return summary

    def _sort_results(
        self,
        results: List[CropSearchResult],
        sort_by: SortField,
        sort_order: SortOrder,
    ) -> List[CropSearchResult]:
        reverse = sort_order == SortOrder.DESC
        if sort_by == SortField.NAME:
            return sorted(results, key=lambda result: result.crop.crop_name.lower(), reverse=reverse)
        if sort_by == SortField.CATEGORY:
            return sorted(
                results,
                key=lambda result: result.crop.primary_category or "",
                reverse=reverse,
            )
        if sort_by == SortField.SCIENTIFIC_NAME:
            return sorted(
                results,
                key=lambda result: (result.crop.scientific_name or "").lower(),
                reverse=reverse,
            )
        if sort_by == SortField.UPDATED_DATE:
            return sorted(
                results,
                key=lambda result: result.crop.updated_at or datetime.min,
                reverse=reverse,
            )
        return sorted(results, key=lambda result: result.relevance_score, reverse=reverse)

    def _paginate_results(
        self,
        results: List[CropSearchResult],
        offset: int,
        limit: int,
    ) -> List[CropSearchResult]:
        paginated: List[CropSearchResult] = []
        index = 0
        appended = 0
        total = len(results)
        while index < total and appended < limit:
            if index >= offset:
                paginated.append(results[index])
                appended += 1
            index += 1
        return paginated

    def _build_facets(self, results: List[CropSearchResult]) -> SearchFacets:
        facets = SearchFacets()
        index = 0
        while index < len(results):
            crop = results[index].crop
            classification = crop.agricultural_classification
            taxonomy = crop.taxonomic_hierarchy

            if classification and classification.crop_category:
                category_value = classification.crop_category.value
                count = facets.categories.get(category_value, 0)
                facets.categories[category_value] = count + 1

            if taxonomy and taxonomy.family:
                family_value = taxonomy.family
                count = facets.families.get(family_value, 0)
                facets.families[family_value] = count + 1

            if classification and classification.growth_habit:
                habit_value = classification.growth_habit.value
                count = facets.growth_habits.get(habit_value, 0)
                facets.growth_habits[habit_value] = count + 1

            adaptation = crop.climate_adaptations
            if adaptation and adaptation.hardiness_zones:
                zone_index = 0
                while zone_index < len(adaptation.hardiness_zones):
                    zone = adaptation.hardiness_zones[zone_index]
                    count = facets.hardiness_zones.get(zone, 0)
                    facets.hardiness_zones[zone] = count + 1
                    zone_index += 1

            if classification and classification.primary_use:
                use_value = classification.primary_use.value
                count = facets.primary_uses.get(use_value, 0)
                facets.primary_uses[use_value] = count + 1

            index += 1
        return facets

    def _build_statistics(
        self,
        start_time: datetime,
        matched_results: List[CropSearchResult],
        paginated_results: List[CropSearchResult],
    ) -> SearchStatistics:
        search_duration = (datetime.utcnow() - start_time).total_seconds() * 1000.0
        total_results = len(matched_results)
        returned_results = len(paginated_results)
        average_score = 0.0
        if total_results > 0:
            score_sum = 0.0
            index = 0
            while index < total_results:
                score_sum += matched_results[index].relevance_score
                index += 1
            average_score = score_sum / float(total_results)

        result_quality = average_score

        statistics = SearchStatistics(
            total_results=total_results,
            search_time_ms=search_duration,
            filtered_results=total_results,
            index_hits=0,
            full_scan_required=False,
            cache_hit=False,
            average_relevance_score=average_score,
            result_quality_score=result_quality,
        )
        return statistics

    def _summarize_filters(self, criteria: TaxonomyFilterCriteria) -> Dict[str, object]:
        summary: Dict[str, object] = {}
        if criteria.text_search:
            summary["text_search"] = criteria.text_search
        if criteria.families:
            families_copy: List[str] = []
            index = 0
            while index < len(criteria.families):
                families_copy.append(criteria.families[index])
                index += 1
            summary["families"] = families_copy
        if criteria.genera:
            genera_copy: List[str] = []
            index = 0
            while index < len(criteria.genera):
                genera_copy.append(criteria.genera[index])
                index += 1
            summary["genera"] = genera_copy
        if criteria.geographic_filter and self._geographic_filter_has_values(criteria.geographic_filter):
            summary["geographic"] = "applied"
        if criteria.climate_filter and self._climate_filter_has_values(criteria.climate_filter):
            summary["climate"] = "applied"
        if criteria.soil_filter and self._soil_filter_has_values(criteria.soil_filter):
            summary["soil"] = "applied"
        if criteria.agricultural_filter and self._agricultural_filter_has_values(criteria.agricultural_filter):
            summary["agricultural"] = "applied"
        if criteria.management_filter and self._management_filter_has_values(criteria.management_filter):
            summary["management"] = "applied"
        if criteria.sustainability_filter and self._sustainability_filter_has_values(criteria.sustainability_filter):
            summary["sustainability"] = "applied"
        if criteria.economic_filter and self._economic_filter_has_values(criteria.economic_filter):
            summary["economic"] = "applied"
        return summary

    def _suggest_refinements(
        self,
        results: List[CropSearchResult],
        criteria: TaxonomyFilterCriteria,
    ) -> List[str]:
        refinements: List[str] = []
        if len(results) == 0 and criteria.text_search:
            refinements.append("Try a broader text search or remove restrictive filters")
        if len(results) > 10:
            refinements.append("Use additional filters to narrow results")
        return refinements


crop_search_service = CropSearchService()
