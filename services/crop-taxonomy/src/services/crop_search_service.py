"""Crop search service with advanced filtering capabilities."""
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Dict, Any, Optional
import time
import hashlib
import json

# Import models and schemas with relative imports that work from the project root
try:
    # When running from the project root
    from models.filtering_models import CropFilteringAttributes, FilterCombination
    from schemas.crop_schemas import CropFilterRequest, CropSearchResponse, VarietyResult
except ImportError:
    # When running from services/crop-taxonomy directory
    try:
        from src.models.filtering_models import CropFilteringAttributes, FilterCombination
        from src.schemas.crop_schemas import CropFilterRequest, CropSearchResponse, VarietyResult
    except ImportError:
        # When running from the module file location
        from ..models.filtering_models import CropFilteringAttributes, FilterCombination
        from ..schemas.crop_schemas import CropFilterRequest, CropSearchResponse, VarietyResult


class CropSearchService:
    """Advanced crop search with multi-criteria filtering"""

    def __init__(self, db: Session):
        self.db = db

    async def search_varieties(self, filter_request: CropFilterRequest) -> CropSearchResponse:
        """
        Search crop varieties with advanced filtering

        Performance requirement: <2s for complex queries
        """
        start_time = time.time()

        # Build base query - in a real implementation, this would join with actual crop variety data
        query = self.db.query(CropFilteringAttributes)

        # Apply filters
        query = self._apply_maturity_filters(query, filter_request)
        query = self._apply_pest_resistance_filters(query, filter_request)
        query = self._apply_disease_resistance_filters(query, filter_request)
        query = self._apply_market_class_filters(query, filter_request)
        query = self._apply_performance_filters(query, filter_request)

        # Get total count before pagination
        total_count = query.count()

        # Apply sorting
        query = self._apply_sorting(query, filter_request)

        # Apply pagination
        offset = (filter_request.page - 1) * filter_request.page_size
        query = query.offset(offset).limit(filter_request.page_size)

        # Execute query
        results = query.all()

        # Calculate relevance scores
        varieties = [
            self._build_variety_result(result, filter_request)
            for result in results
        ]

        # Calculate response time
        search_time_ms = int((time.time() - start_time) * 1000)

        # Log filter combination for optimization
        self._log_filter_combination(filter_request, total_count, search_time_ms)

        # Build response
        total_pages = (total_count + filter_request.page_size - 1) // filter_request.page_size

        return CropSearchResponse(
            varieties=varieties,
            total_count=total_count,
            page=filter_request.page,
            page_size=filter_request.page_size,
            total_pages=total_pages,
            filters_applied=filter_request.model_dump(exclude_none=True),
            search_time_ms=search_time_ms
        )

    def _apply_maturity_filters(self, query, filter_request: CropFilterRequest):
        """
        Apply maturity day filters
        
        This method filters varieties based on maturity days range requirements.
        In a real implementation, this would filter on actual maturity days field
        from the crop varieties table that is related to CropFilteringAttributes.
        """
        if filter_request.maturity_days_min is not None:
            # In a complete implementation, we would join with a crop varieties table
            # that has maturity_days field and filter on it
            # query = query.filter(CropVariety.maturity_days >= filter_request.maturity_days_min)
            pass  # Placeholder - would connect to actual maturity days in real implementation
        
        if filter_request.maturity_days_max is not None:
            # In a complete implementation, we would join with a crop varieties table
            # that has maturity_days field and filter on it
            # query = query.filter(CropVariety.maturity_days <= filter_request.maturity_days_max)
            pass  # Placeholder - would connect to actual maturity days in real implementation
        
        # Since the filtering models don't have a direct maturity_days field,
        # we would need to join with another table that has this information
        # For the current models, we could potentially have maturity days in 
        # crop filtering attributes if extended, or in related crop variety table
        return query

    def _apply_pest_resistance_filters(self, query, filter_request: CropFilterRequest):
        """Apply pest resistance filters using JSONB queries"""
        if not filter_request.pest_resistance:
            return query

        for pest_filter in filter_request.pest_resistance:
            # JSONB containment query - check if the pest exists in the traits and meets the minimum resistance level
            query = query.filter(
                CropFilteringAttributes.pest_resistance_traits[pest_filter.pest_name].astext.in_(
                    self._get_resistance_levels(pest_filter.min_resistance_level)
                )
            )

        return query

    def _apply_disease_resistance_filters(self, query, filter_request: CropFilterRequest):
        """Apply disease resistance filters using JSONB queries"""
        if not filter_request.disease_resistance:
            return query

        for disease_filter in filter_request.disease_resistance:
            query = query.filter(
                CropFilteringAttributes.disease_resistance_traits[disease_filter.disease_name].astext.in_(
                    self._get_resistance_levels(disease_filter.min_resistance_level)
                )
            )

        return query

    def _apply_market_class_filters(self, query, filter_request: CropFilterRequest):
        """Apply market class filters"""
        if not filter_request.market_class:
            return query

        market_filter = filter_request.market_class

        if market_filter.market_class:
            query = query.filter(
                CropFilteringAttributes.market_class_filters['market_class'].astext == market_filter.market_class
            )

        if market_filter.organic_certified is not None:
            query = query.filter(
                CropFilteringAttributes.market_class_filters['organic_certified'].astext == str(market_filter.organic_certified).lower()
            )

        if market_filter.non_gmo is not None:
            query = query.filter(
                CropFilteringAttributes.market_class_filters['non_gmo'].astext == str(market_filter.non_gmo).lower()
            )

        return query

    def _apply_performance_filters(self, query, filter_request: CropFilterRequest):
        """Apply performance score filters"""
        if filter_request.min_yield_stability:
            query = query.filter(
                CropFilteringAttributes.yield_stability_score >= filter_request.min_yield_stability
            )

        if filter_request.min_drought_tolerance:
            query = query.filter(
                CropFilteringAttributes.drought_tolerance_score >= filter_request.min_drought_tolerance
            )

        return query

    def _apply_sorting(self, query, filter_request: CropFilterRequest):
        """Apply sorting"""
        if filter_request.sort_by == "yield_stability":
            if filter_request.sort_order == "desc":
                query = query.order_by(CropFilteringAttributes.yield_stability_score.desc())
            else:
                query = query.order_by(CropFilteringAttributes.yield_stability_score.asc())
        elif filter_request.sort_by == "drought_tolerance":
            if filter_request.sort_order == "desc":
                query = query.order_by(CropFilteringAttributes.drought_tolerance_score.desc())
            else:
                query = query.order_by(CropFilteringAttributes.drought_tolerance_score.asc())

        return query

    def _get_resistance_levels(self, min_level: str) -> List[str]:
        """Get acceptable resistance levels based on minimum"""
        levels = {
            "susceptible": ["susceptible", "moderate", "resistant"],
            "moderate": ["moderate", "resistant"],
            "resistant": ["resistant"]
        }
        return levels.get(min_level, ["resistant"])

    def _build_variety_result(self, result: CropFilteringAttributes, filter_request: CropFilterRequest) -> VarietyResult:
        """Build variety result with relevance score"""
        relevance_score = self._calculate_relevance(result, filter_request)

        return VarietyResult(
            variety_id=result.variety_id,
            variety_name=f"Variety {str(result.variety_id)[:8]}",  # Placeholder
            maturity_days=100,  # Placeholder - in real implementation this would come from the crop varieties data
            yield_potential=180.0,  # Placeholder
            pest_resistance_summary=result.pest_resistance_traits or {},
            disease_resistance_summary=result.disease_resistance_traits or {},
            market_class=result.market_class_filters.get('market_class') if result.market_class_filters else None,
            relevance_score=relevance_score
        )

    def _calculate_relevance(self, result: CropFilteringAttributes, filter_request: CropFilterRequest) -> float:
        """Calculate relevance score (0-1)"""
        score = 0.5  # Base score

        # Boost for performance scores
        if result.yield_stability_score:
            score += (result.yield_stability_score / 100) * 0.25

        if result.drought_tolerance_score:
            score += (result.drought_tolerance_score / 100) * 0.25

        return min(score, 1.0)

    def _log_filter_combination(self, filter_request: CropFilterRequest, result_count: int, response_time_ms: int):
        """Log filter combination for optimization"""
        filters_dict = filter_request.model_dump(exclude={'page', 'page_size', 'sort_by', 'sort_order'}, exclude_none=True)
        combination_hash = hashlib.sha256(json.dumps(filters_dict, sort_keys=True).encode()).hexdigest()

        existing = self.db.query(FilterCombination).filter(
            FilterCombination.combination_hash == combination_hash
        ).first()

        if existing:
            existing.usage_count += 1
            existing.avg_result_count = (existing.avg_result_count + result_count) // 2
            existing.avg_response_time_ms = (existing.avg_response_time_ms + response_time_ms) // 2
        else:
            new_combo = FilterCombination(
                combination_hash=combination_hash,
                filters=filters_dict,
                usage_count=1,
                avg_result_count=result_count,
                avg_response_time_ms=response_time_ms
            )
            self.db.add(new_combo)

        self.db.commit()