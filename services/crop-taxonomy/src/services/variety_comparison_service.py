"""Variety Comparison Service.

Provides comprehensive variety comparison, trade-off analysis, and
decision-support guidance leveraging existing crop taxonomy data and
recommendation scoring logic.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from pydantic import ValidationError

try:  # pragma: no cover - handled during unit tests
    from ..models.crop_variety_models import (
        EnhancedCropVariety,
        VarietyComparisonRequest,
        VarietyComparisonResponse,
        VarietyComparisonMatrix,
        VarietyComparisonDetail,
        VarietyTradeOff,
        VarietyComparisonSummary,
        DiseaseResistanceEntry
    )
    from ..database.crop_taxonomy_db import CropTaxonomyDatabase
    from .variety_recommendation_service import VarietyRecommendationService
except ImportError:  # pragma: no cover - fallback for direct module execution
    try:
        from models.crop_variety_models import (
            EnhancedCropVariety,
            VarietyComparisonRequest,
            VarietyComparisonResponse,
            VarietyComparisonMatrix,
            VarietyComparisonDetail,
            VarietyTradeOff,
            VarietyComparisonSummary,
            DiseaseResistanceEntry
        )
        from database.crop_taxonomy_db import CropTaxonomyDatabase  # type: ignore
        from services.variety_recommendation_service import VarietyRecommendationService  # type: ignore
    except ImportError:
        # Create minimal fallback models for testing
        from pydantic import BaseModel
        from typing import List, Dict, Any, Optional
        from uuid import UUID
        
        class EnhancedCropVariety(BaseModel):
            variety_id: UUID
            variety_name: str
            crop_id: UUID
            
        class VarietyComparisonRequest(BaseModel):
            variety_ids: List[UUID]
            provided_varieties: List[Dict[str, Any]]
            
        class VarietyComparisonResponse(BaseModel):
            success: bool
            message: str
            
        class VarietyComparisonMatrix(BaseModel):
            pass
            
        class VarietyComparisonDetail(BaseModel):
            pass
            
        class VarietyTradeOff(BaseModel):
            pass
            
        class VarietyComparisonSummary(BaseModel):
            pass
            
        class DiseaseResistanceEntry(BaseModel):
            pass
            
        class CropTaxonomyDatabase:
            def __init__(self, *args, **kwargs):
                pass
                
        class VarietyRecommendationService:
            def __init__(self, *args, **kwargs):
                pass


logger = logging.getLogger(__name__)


class VarietyComparisonService:
    """Service providing advanced variety comparison analysis."""

    def __init__(
        self,
        database_url: Optional[str] = None,
        recommendation_service: Optional[VarietyRecommendationService] = None
    ) -> None:
        self.database: Optional[CropTaxonomyDatabase] = None
        self.database_available = False
        self.recommendation_service = recommendation_service

        try:
            if recommendation_service is None:
                self.recommendation_service = VarietyRecommendationService(database_url)
        except Exception as exc:  # pragma: no cover - initialization safety
            logger.warning("Failed to initialize VarietyRecommendationService: %s", exc)
            self.recommendation_service = None

        try:
            self.database = CropTaxonomyDatabase(database_url)
            self.database_available = self.database.test_connection()
            if not self.database_available:
                logger.info("Variety comparison service running without database connection")
        except Exception as exc:  # pragma: no cover - optional database usage
            logger.info("Variety comparison service could not connect to database: %s", exc)
            self.database = None
            self.database_available = False

        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Initialize default comparison criteria and weights."""
        self.criteria_order: List[str] = []
        self.criteria_order.append("yield_potential")
        self.criteria_order.append("disease_resilience")
        self.criteria_order.append("maturity_suitability")
        self.criteria_order.append("management_requirements")
        self.criteria_order.append("economic_outlook")

        self.criteria_weights: Dict[str, float] = {}
        self.criteria_weights["yield_potential"] = 0.28
        self.criteria_weights["disease_resilience"] = 0.24
        self.criteria_weights["maturity_suitability"] = 0.18
        self.criteria_weights["management_requirements"] = 0.16
        self.criteria_weights["economic_outlook"] = 0.14

        self.resistance_levels: Dict[str, float] = {}
        self.resistance_levels["immune"] = 0.95
        self.resistance_levels["resistant"] = 0.85
        self.resistance_levels["moderately_resistant"] = 0.75
        self.resistance_levels["tolerant"] = 0.65
        self.resistance_levels["moderately_susceptible"] = 0.45
        self.resistance_levels["susceptible"] = 0.35

    async def compare_varieties(self, request: VarietyComparisonRequest) -> VarietyComparisonResponse:
        """Generate comprehensive comparison for requested varieties."""
        response = VarietyComparisonResponse(
            request_id=request.request_id, 
            success=False,
            message="Comparison processing initiated",
            context_used=request.comparison_context or {}
        )

        try:
            varieties = await self._load_varieties(request)
            if len(varieties) < 2:
                response.message = "At least two varieties are required for comparison"
                return response

            weights = self._determine_weights(request)
            detailed_results = await self._build_detailed_results(varieties, request, weights)
            matrix = self._build_matrix_response(varieties, detailed_results, request)
            trade_offs = self._build_trade_offs(detailed_results, request)
            summary = self._build_summary(detailed_results, trade_offs)
            legacy_payloads = self._create_legacy_payloads(detailed_results, summary)

            response.success = True
            response.message = "Comparison generated successfully"
            response.detailed_results = detailed_results
            response.comparison_matrix = matrix
            response.trade_offs = trade_offs
            response.summary = summary
            response.comparisons = legacy_payloads["comparisons"]
            response.comparison_summary = legacy_payloads["summary"]
            response.data_sources = self._collect_data_sources()
            return response

        except Exception as exc:  # pragma: no cover - error path logged for operators
            logger.error("Variety comparison failed: %s", exc)
            response.message = f"Comparison error: {str(exc)}"
            response.success = False
            return response

    async def _build_detailed_results(
        self,
        varieties: List[EnhancedCropVariety],
        request: VarietyComparisonRequest,
        weights: Dict[str, float]
    ) -> List[VarietyComparisonDetail]:
        """Create detailed comparison entries for each variety."""
        details: List[VarietyComparisonDetail] = []
        for variety in varieties:
            metrics, insights = await self._collect_variety_metrics(variety, request)
            detail = self._build_detail_entry(variety, metrics, insights, weights, request)
            details.append(detail)
        return details

    async def _collect_variety_metrics(
        self,
        variety: EnhancedCropVariety,
        request: VarietyComparisonRequest
    ) -> Tuple[Dict[str, float], Dict[str, str]]:
        """Gather normalized metrics and qualitative insights for one variety."""
        metrics: Dict[str, float] = {}
        insights: Dict[str, str] = {}

        score_data = None
        preferences = None
        if request.comparison_context:
            preferences = request.comparison_context.get("farmer_preferences")

        if self.recommendation_service is not None:
            try:
                context = request.comparison_context or {}
                score_data = await self.recommendation_service._score_variety_for_context(  # type: ignore[attr-defined]
                    variety,
                    context,
                    preferences
                )
            except Exception as exc:  # pragma: no cover - safe fallback for scoring
                logger.debug("Variety scoring unavailable: %s", exc)
                score_data = None

        metrics["yield_potential"] = self._derive_yield_score(variety, score_data)
        insights["yield_potential"] = self._insight_for_yield(variety, metrics["yield_potential"])

        metrics["disease_resilience"] = self._derive_disease_score(variety, score_data)
        insights["disease_resilience"] = self._insight_for_disease(variety, metrics["disease_resilience"])

        metrics["maturity_suitability"] = self._derive_maturity_score(variety, request)
        insights["maturity_suitability"] = self._insight_for_maturity(variety, metrics["maturity_suitability"])

        metrics["management_requirements"] = self._derive_management_score(variety)
        insights["management_requirements"] = self._insight_for_management(variety, metrics["management_requirements"])

        metrics["economic_outlook"] = self._derive_economic_score(variety)
        insights["economic_outlook"] = self._insight_for_economics(variety, metrics["economic_outlook"])

        return metrics, insights

    def _build_detail_entry(
        self,
        variety: EnhancedCropVariety,
        metrics: Dict[str, float],
        insights: Dict[str, str],
        weights: Dict[str, float],
        request: VarietyComparisonRequest
    ) -> VarietyComparisonDetail:
        """Build detail response item for a variety."""
        overall_score = self._calculate_overall_score(metrics, weights)
        strengths, considerations = self._gather_strengths_considerations(metrics, insights)
        suitability_notes = self._build_suitability_notes(variety, metrics, request)
        risk_rating = self._estimate_risk_rating(metrics, variety)

        return VarietyComparisonDetail(
            variety_id=variety.variety_id,
            variety_name=variety.variety_name,
            overall_score=overall_score,
            criteria_scores=metrics,
            qualitative_insights=insights,
            strengths=strengths,
            considerations=considerations,
            best_fit_scenarios=suitability_notes,
            risk_rating=risk_rating
        )

    def _calculate_overall_score(self, metrics: Dict[str, float], weights: Dict[str, float]) -> float:
        """Calculate weighted score for a variety."""
        overall_score = 0.0
        for criterion in self.criteria_order:
            weight_value = weights.get(criterion, 0.0)
            metric_value = metrics.get(criterion, 0.0)
            overall_score = overall_score + (metric_value * weight_value)
        if overall_score > 1.0:
            return 1.0
        return overall_score

    def _gather_strengths_considerations(
        self,
        metrics: Dict[str, float],
        insights: Dict[str, str]
    ) -> Tuple[List[str], List[str]]:
        """Create human-readable strengths and considerations lists."""
        strengths: List[str] = []
        considerations: List[str] = []

        for criterion in self.criteria_order:
            score = metrics.get(criterion, 0.0)
            insight_text = insights.get(criterion)
            if score >= 0.75 and insight_text:
                strengths.append(insight_text)
            elif score <= 0.45 and insight_text:
                considerations.append(insight_text)

        return strengths, considerations

    def _build_suitability_notes(
        self,
        variety: EnhancedCropVariety,
        metrics: Dict[str, float],
        request: VarietyComparisonRequest
    ) -> List[str]:
        """Generate suitability notes based on metrics and context."""
        notes: List[str] = []

        context = request.comparison_context or {}
        climate_focus = context.get("climate_focus")
        soil_focus = context.get("soil_requirements")

        yield_value = metrics.get("yield_potential", 0.0)
        if yield_value >= 0.75:
            notes.append("Well-suited for maximizing yield potential")

        disease_value = metrics.get("disease_resilience", 0.0)
        if disease_value >= 0.75:
            notes.append("Performs reliably in disease-prone environments")

        if climate_focus == "short_season" and metrics.get("maturity_suitability", 0.0) >= 0.65:
            notes.append("Fits short-season production windows")

        if soil_focus == "high_clay" and metrics.get("management_requirements", 0.0) >= 0.6:
            notes.append("Supports careful management on heavy soils")

        if not notes:
            notes.append("Suitable for balanced production goals")

        return notes

    def _estimate_risk_rating(self, metrics: Dict[str, float], variety: EnhancedCropVariety) -> str:
        """Estimate qualitative risk rating based on metrics."""
        disease_score = metrics.get("disease_resilience", 0.0)
        management_score = metrics.get("management_requirements", 0.0)

        if disease_score >= 0.8 and management_score >= 0.7:
            return "low"
        if disease_score < 0.5 and management_score < 0.5:
            return "high"
        return "moderate"

    def _determine_weights(self, request: VarietyComparisonRequest) -> Dict[str, float]:
        """Determine effective weights for this comparison request."""
        weights: Dict[str, float] = {}
        for criterion in self.criteria_order:
            weights[criterion] = self.criteria_weights.get(criterion, 0.0)

        if request.prioritized_factors:
            for factor in request.prioritized_factors:
                normalized = factor.lower()
                if normalized in weights:
                    weights[normalized] = min(1.0, weights[normalized] + 0.12)

        total_weight = 0.0
        for value in weights.values():
            total_weight = total_weight + value

        if total_weight > 0:
            for key in list(weights.keys()):
                weights[key] = weights[key] / total_weight

        return weights

    def _build_matrix_response(
        self,
        varieties: List[EnhancedCropVariety],
        details: List[VarietyComparisonDetail],
        request: VarietyComparisonRequest
    ) -> VarietyComparisonMatrix:
        """Create structured matrix data for the comparison."""
        performance_matrix: Dict[str, Dict[str, Any]] = {}
        for detail in details:
            metrics: Dict[str, Any] = {}
            for criterion in self.criteria_order:
                metrics[criterion] = detail.criteria_scores.get(criterion, 0.0)
            name_key = detail.variety_name
            performance_matrix[name_key] = metrics

        ranking_by_criteria: Dict[str, List[str]] = {}
        for criterion in self.criteria_order:
            sortable: List[Tuple[str, float]] = []
            for detail in details:
                pair = (detail.variety_name, detail.criteria_scores.get(criterion, 0.0))
                sortable.append(pair)
            sortable.sort(key=lambda value: value[1], reverse=True)
            ordered_names: List[str] = []
            for item in sortable:
                ordered_names.append(item[0])
            ranking_by_criteria[criterion] = ordered_names

        sorted_details = sorted(details, key=lambda entry: entry.overall_score, reverse=True)
        top_overall: List[str] = []
        index = 0
        while index < len(sorted_details) and index < 3:
            top_overall.append(sorted_details[index].variety_name)
            index = index + 1

        best_for_criteria: Dict[str, str] = {}
        for criterion in ranking_by_criteria:
            names = ranking_by_criteria[criterion]
            if names:
                best_for_criteria[criterion] = names[0]

        trade_off_analysis: Dict[str, str] = {}
        for criterion in self.criteria_order:
            top_name = best_for_criteria.get(criterion)
            if top_name:
                trade_off_analysis[criterion] = f"{top_name} leads for {criterion.replace('_', ' ')}"

        selection_guidance: List[str] = []
        selection_guidance.append("Match variety selection to prioritized production goals")
        selection_guidance.append("Balance yield, resilience, and economics for diversified fields")

        return VarietyComparisonMatrix(
            comparison_id=request.request_id,
            comparison_criteria=self.criteria_order,
            varieties=varieties,
            performance_matrix=performance_matrix,
            ranking_by_criteria=ranking_by_criteria,
            top_overall_varieties=top_overall,
            best_for_criteria=best_for_criteria,
            trade_off_analysis=trade_off_analysis,
            selection_guidance=selection_guidance
        )

    def _build_trade_offs(
        self,
        details: List[VarietyComparisonDetail],
        request: VarietyComparisonRequest
    ) -> List[VarietyTradeOff]:
        """Generate trade-off recommendations."""
        trade_offs: List[VarietyTradeOff] = []
        for criterion in self.criteria_order:
            best_candidate = None
            best_score = -1.0
            for detail in details:
                score = detail.criteria_scores.get(criterion, 0.0)
                if score > best_score:
                    best_score = score
                    best_candidate = detail

            if best_candidate is None:
                continue

            rationale = best_candidate.qualitative_insights.get(criterion, "")
            if not rationale:
                rationale = f"{best_candidate.variety_name} provides strength in {criterion.replace('_', ' ')}"

            trade_offs.append(
                VarietyTradeOff(
                    focus_area=criterion,
                    preferred_variety_name=best_candidate.variety_name,
                    rationale=rationale
                )
            )

        return trade_offs

    def _build_summary(
        self,
        details: List[VarietyComparisonDetail],
        trade_offs: List[VarietyTradeOff]
    ) -> VarietyComparisonSummary:
        """Build high-level summary from comparison results."""
        if not details:
            return VarietyComparisonSummary(best_overall_variety=None)

        best_detail = max(details, key=lambda entry: entry.overall_score)

        key_takeaways: List[str] = []
        key_takeaways.append(f"{best_detail.variety_name} delivers the highest balanced performance")
        if trade_offs:
            trade_text = f"{trade_offs[0].preferred_variety_name} excels when prioritizing {trade_offs[0].focus_area.replace('_', ' ')}"
            key_takeaways.append(trade_text)

        recommended_actions: List[str] = []
        recommended_actions.append("Validate field-level constraints before final selection")
        recommended_actions.append("Pair selected variety with tailored management plan")

        confidence = self._estimate_summary_confidence(details)

        return VarietyComparisonSummary(
            best_overall_variety=best_detail.variety_name,
            confidence_score=confidence,
            key_takeaways=key_takeaways,
            recommended_actions=recommended_actions
        )

    def _estimate_summary_confidence(self, details: List[VarietyComparisonDetail]) -> float:
        """Estimate confidence level based on score spread."""
        if not details:
            return 0.5

        highest = max(detail.overall_score for detail in details)
        lowest = min(detail.overall_score for detail in details)
        spread = highest - lowest

        if spread < 0.15:
            return 0.55
        if spread < 0.3:
            return 0.68
        return 0.8

    def _create_legacy_payloads(
        self,
        details: List[VarietyComparisonDetail],
        summary: VarietyComparisonSummary
    ) -> Dict[str, Any]:
        """Create legacy comparison structures for backward compatibility."""
        comparisons: List[Dict[str, Any]] = []
        for detail in details:
            entry: Dict[str, Any] = {}
            entry["variety"] = detail.variety_name
            entry["overall_score"] = detail.overall_score
            entry["strengths"] = detail.strengths
            entry["considerations"] = detail.considerations
            comparisons.append(entry)

        summary_payload: Dict[str, Any] = {}
        summary_payload["best_overall_variety"] = summary.best_overall_variety
        summary_payload["confidence_score"] = summary.confidence_score
        summary_payload["key_takeaways"] = summary.key_takeaways

        payload = {
            "comparisons": comparisons,
            "summary": summary_payload
        }
        return payload

    def _collect_data_sources(self) -> List[str]:
        """Return list of data sources used for comparison."""
        sources: List[str] = []
        if self.database_available:
            sources.append("crop_taxonomy_database")
        if self.recommendation_service is not None:
            sources.append("variety_recommendation_engine")
        return sources

    async def _load_varieties(self, request: VarietyComparisonRequest) -> List[EnhancedCropVariety]:
        """Load all varieties from provided data or database."""
        collected: Dict[str, EnhancedCropVariety] = {}

        for provided in request.provided_varieties:
            identifier = None
            if provided.variety_id is not None:
                identifier = str(provided.variety_id)
            else:
                identifier = provided.variety_name
                provided.variety_id = uuid4()
            collected[identifier] = provided

        missing_ids: List[UUID] = []
        for variety_id in request.variety_ids:
            key = str(variety_id)
            if key not in collected:
                missing_ids.append(variety_id)

        if missing_ids and self.database_available:
            loaded = self._fetch_varieties_from_database(missing_ids)
            for key, variety in loaded.items():
                collected[key] = variety

        varieties: List[EnhancedCropVariety] = []
        for variety in collected.values():
            varieties.append(variety)

        return varieties

    def _fetch_varieties_from_database(self, variety_ids: List[UUID]) -> Dict[str, EnhancedCropVariety]:
        """Fetch varieties from database and convert to Pydantic models."""
        fetched: Dict[str, EnhancedCropVariety] = {}
        if not self.database_available or self.database is None:
            return fetched

        try:
            records = self.database.get_varieties_by_ids(variety_ids)
            for key, data in records.items():
                variety = self._convert_dictionary_to_variety(data)
                if variety is not None:
                    fetched[key] = variety
        except Exception as exc:
            logger.error("Failed to fetch varieties for comparison: %s", exc)

        return fetched

    def _convert_dictionary_to_variety(self, data: Dict[str, Any]) -> Optional[EnhancedCropVariety]:
        """Convert database dictionary to EnhancedCropVariety model."""
        prepared: Dict[str, Any] = {}

        if not data:
            return None

        variety_id = data.get('variety_id')
        if isinstance(variety_id, str):
            try:
                prepared['variety_id'] = UUID(variety_id)
            except ValueError:
                prepared['variety_id'] = uuid4()
        elif isinstance(variety_id, UUID):
            prepared['variety_id'] = variety_id

        crop_id_value = data.get('crop_id')
        if isinstance(crop_id_value, str):
            try:
                prepared['crop_id'] = UUID(crop_id_value)
            except ValueError:
                prepared['crop_id'] = uuid4()
        elif isinstance(crop_id_value, UUID):
            prepared['crop_id'] = crop_id_value
        else:
            prepared['crop_id'] = uuid4()

        prepared['variety_name'] = data.get('variety_name', 'Unknown Variety')
        prepared['variety_code'] = data.get('variety_code')
        prepared['breeder_company'] = data.get('breeder_company')

        parent_varieties = data.get('parent_varieties')
        if isinstance(parent_varieties, list):
            prepared['parent_varieties'] = parent_varieties

        seed_companies = data.get('seed_companies')
        if isinstance(seed_companies, list):
            prepared['seed_companies'] = seed_companies

        maturity = data.get('maturity') or {}
        prepared['relative_maturity'] = maturity.get('relative_maturity')
        prepared['maturity_group'] = maturity.get('maturity_group')
        prepared['days_to_emergence'] = maturity.get('days_to_emergence')
        prepared['days_to_flowering'] = maturity.get('days_to_flowering')
        prepared['days_to_physiological_maturity'] = maturity.get('days_to_physiological_maturity')

        performance = data.get('performance') or {}
        prepared['yield_potential_percentile'] = performance.get('yield_potential_percentile')
        prepared['yield_stability_rating'] = performance.get('yield_stability_rating')
        prepared['market_acceptance_score'] = performance.get('market_acceptance_score')
        prepared['standability_rating'] = performance.get('standability_rating')

        traits = data.get('traits') or {}
        disease_resistances = traits.get('disease_resistances')
        if isinstance(disease_resistances, list):
            prepared['disease_resistances'] = disease_resistances
        elif isinstance(disease_resistances, dict):
            converted: List[Dict[str, Any]] = []
            for name, value in disease_resistances.items():
                entry: Dict[str, Any] = {}
                entry['disease_name'] = name
                entry['resistance_level'] = str(value)
                converted.append(entry)
            prepared['disease_resistances'] = converted

        pest_resistances = traits.get('pest_resistances')
        if isinstance(pest_resistances, list):
            prepared['pest_resistances'] = pest_resistances

        herbicide_tolerances = traits.get('herbicide_tolerances')
        if isinstance(herbicide_tolerances, list):
            prepared['herbicide_tolerances'] = herbicide_tolerances

        stress_tolerances = traits.get('stress_tolerances')
        if isinstance(stress_tolerances, list):
            prepared['stress_tolerances'] = stress_tolerances

        quality = data.get('quality') or {}
        prepared['quality_characteristics'] = quality.get('quality_characteristics', [])
        prepared['protein_content_range'] = quality.get('protein_content_range')
        prepared['oil_content_range'] = quality.get('oil_content_range')

        adaptation = data.get('adaptation') or {}
        prepared['adapted_regions'] = adaptation.get('adapted_regions', [])
        populations = adaptation.get('recommended_planting_populations')
        if isinstance(populations, list):
            prepared['recommended_planting_populations'] = populations
        else:
            prepared['recommended_planting_populations'] = []
        prepared['special_management_notes'] = adaptation.get('special_management_notes')

        commercial = data.get('commercial') or {}
        prepared['seed_availability'] = commercial.get('seed_availability')
        prepared['seed_availability_status'] = commercial.get('seed_availability_status')
        prepared['relative_seed_cost'] = commercial.get('relative_seed_cost')
        prepared['technology_package'] = commercial.get('technology_package')
        prepared['organic_approved'] = commercial.get('organic_approved')
        prepared['non_gmo_certified'] = commercial.get('non_gmo_certified')
        prepared['registration_year'] = commercial.get('registration_year')
        prepared['release_year'] = commercial.get('release_year')
        prepared['patent_protected'] = commercial.get('patent_protected', False)
        prepared['patent_status'] = commercial.get('patent_status')

        prepared['is_active'] = data.get('is_active', True)

        try:
            return EnhancedCropVariety(**prepared)
        except ValidationError as exc:
            logger.error("Failed to convert variety data to model: %s", exc)
            return None

    def _derive_yield_score(self, variety: EnhancedCropVariety, score_data: Optional[Dict[str, Any]]) -> float:
        """Determine yield-focused score."""
        if score_data and isinstance(score_data.get('individual_scores'), dict):
            value = score_data['individual_scores'].get('yield_potential')
            if isinstance(value, (int, float)):
                return float(max(0.0, min(1.0, value)))

        percentile = variety.yield_potential_percentile
        if percentile is not None:
            return max(0.0, min(1.0, percentile / 100.0))

        stability = variety.yield_stability_rating
        if stability is not None:
            return max(0.0, min(1.0, stability / 10.0))

        return 0.5

    def _derive_disease_score(self, variety: EnhancedCropVariety, score_data: Optional[Dict[str, Any]]) -> float:
        """Determine disease resilience score."""
        if score_data and isinstance(score_data.get('individual_scores'), dict):
            value = score_data['individual_scores'].get('disease_resistance')
            if isinstance(value, (int, float)):
                return float(max(0.0, min(1.0, value)))

        resistances = variety.disease_resistances or []
        if resistances:
            total = 0.0
            count = 0
            for entry in resistances:
                rating = self._map_resistance_value(entry)
                total = total + rating
                count = count + 1
            if count > 0:
                return max(0.0, min(1.0, total / count))

        return 0.55

    def _map_resistance_value(self, entry: Any) -> float:
        """Convert disease resistance entry to numeric value."""
        if isinstance(entry, DiseaseResistanceEntry):
            level = entry.resistance_level
        elif isinstance(entry, dict):
            level = entry.get('resistance_level')
        else:
            level = None

        if isinstance(level, (int, float)):
            numeric = float(level)
            if numeric > 5:
                numeric = 5.0
            return numeric / 5.0

        if isinstance(level, str):
            key = level.lower()
            if key in self.resistance_levels:
                return self.resistance_levels[key]

        return 0.5

    def _derive_maturity_score(self, variety: EnhancedCropVariety, request: VarietyComparisonRequest) -> float:
        """Determine maturity suitability score."""
        relative = variety.relative_maturity
        context = request.comparison_context or {}
        target = context.get('target_relative_maturity')

        if relative is not None and isinstance(target, (int, float)):
            difference = abs(relative - target)
            if difference <= 2:
                return 0.9
            if difference <= 5:
                return 0.75
            if difference <= 8:
                return 0.6
            return 0.45

        if relative is not None:
            if 95 <= relative <= 110:
                return 0.72
            if 88 <= relative < 95:
                return 0.68

        return 0.6

    def _derive_management_score(self, variety: EnhancedCropVariety) -> float:
        """Estimate management requirement score (higher is easier)."""
        if variety.special_management_notes:
            return 0.5

        if variety.herbicide_tolerances and variety.stress_tolerances:
            return 0.7

        return 0.65

    def _derive_economic_score(self, variety: EnhancedCropVariety) -> float:
        """Estimate economic outlook score."""
        score = 0.62
        if variety.market_acceptance_score is not None:
            score = max(0.0, min(1.0, float(variety.market_acceptance_score) / 5.0))

        if variety.relative_seed_cost:
            cost = str(variety.relative_seed_cost).lower()
            if cost in ("premium", "high"):
                score = max(0.0, score - 0.1)
            elif cost == "low":
                score = min(1.0, score + 0.1)

        if variety.seed_availability_status:
            availability = str(variety.seed_availability_status).lower()
            if "limited" in availability:
                score = max(0.0, score - 0.08)

        return score

    def _insight_for_yield(self, variety: EnhancedCropVariety, score: float) -> str:
        """Create qualitative yield insight."""
        if score >= 0.8:
            return "Delivers top-tier yield potential in comparable trials"
        if score <= 0.45:
            return "Yield potential trails leading options"
        return "Balanced yield performance under typical conditions"

    def _insight_for_disease(self, variety: EnhancedCropVariety, score: float) -> str:
        """Create qualitative disease insight."""
        if score >= 0.8:
            return "Strong resistance to key regional diseases"
        if score <= 0.45:
            return "Requires vigilant disease management"
        return "Moderate disease resilience with standard protection"

    def _insight_for_maturity(self, variety: EnhancedCropVariety, score: float) -> str:
        """Create qualitative maturity insight."""
        if score >= 0.75:
            return "Matches targeted maturity window"
        if score <= 0.45:
            return "Maturity timing may challenge current rotation"
        return "Flexible maturity timing for diversified operations"

    def _insight_for_management(self, variety: EnhancedCropVariety, score: float) -> str:
        """Create qualitative management insight."""
        if score >= 0.75:
            return "Simplified management requirements"
        if score <= 0.45:
            return "Demands higher management attention"
        return "Standard management effort required"

    def _insight_for_economics(self, variety: EnhancedCropVariety, score: float) -> str:
        """Create qualitative economic insight."""
        if score >= 0.75:
            return "Strong market acceptance and premium potential"
        if score <= 0.45:
            return "May face pricing or availability constraints"
        return "Competitive economic outlook"


# Instantiate default service for application use
variety_comparison_service = VarietyComparisonService()
