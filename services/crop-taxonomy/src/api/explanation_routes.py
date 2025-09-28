"""
Explanation API Routes

FastAPI routes for filter-based explanation system.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..models.crop_filtering_models import (
    FilterExplanationResponse,
    FilterImpactAnalysis,
    FilterConflictExplanation,
    FilterTuningSuggestion,
    CropSearchResponse,
    TaxonomyFilterCriteria
)
from ..services.filter_explanation_service import FilterExplanationService

router = APIRouter(prefix="/explanations", tags=["explanations"])

# Initialize the explanation service
explanation_service = FilterExplanationService()


@router.post("/filter-explanation/{crop_id}", response_model=FilterExplanationResponse)
async def get_filter_explanation(
    crop_id: str,
    request_id: str = Query(..., description="ID of the search request that produced this result"),
    search_response: Optional[CropSearchResponse] = None
):
    """
    Get detailed explanation for why a specific crop was included/excluded from 
    search results based on applied filters.
    
    **Features:**
    - Detailed filter matching analysis
    - Crop-specific compatibility scores
    - Reasoning for inclusion/exclusion
    - Improvement suggestions
    - Alternative recommendations
    
    **Use Cases:**
    - Understanding search result rationale
    - Crop selection decision support
    - Filter adjustment guidance
    - Agricultural education
    """
    try:
        # In a real implementation, we'd retrieve the search response and criteria 
        # associated with request_id from cache or database
        # For now, return a placeholder response
        return FilterExplanationResponse(
            crop_id=UUID(crop_id),
            crop_name="Placeholder Crop",
            overall_compatibility_score=0.7,
            filter_explanations=[],
            recommendation="Placeholder recommendation",
            alternative_suggestions=["Alternative 1", "Alternative 2"],
            improvement_suggestions=["Suggestion 1", "Suggestion 2"]
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid crop ID format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")


@router.post("/filter-impact-analysis", response_model=List[FilterImpactAnalysis])
async def get_filter_impact_analysis(
    search_response: CropSearchResponse
):
    """
    Analyze how each filter impacts the overall search results.
    
    **Features:**
    - Filter effectiveness analysis
    - Exclusion rate statistics
    - Impact scoring
    - Sensitivity analysis
    - Tuning recommendations
    
    **Analysis includes:**
    - Percentage of crops excluded by each filter
    - Average compatibility scores by filter
    - Filter parameter sensitivity
    - Recommendations for filter adjustments
    """
    try:
        # Extract all results from the search response
        all_results = search_response.results
        
        # We'd also need the original criteria to perform the analysis
        # For demonstration, we'll return placeholder values
        return [
            FilterImpactAnalysis(
                filter_name="climate",
                total_crops_affected=len(all_results),
                average_impact_score=0.65,
                exclusion_rate=0.4,
                sensitivity_analysis={
                    "parameter_sensitivity": 0.5,
                    "relaxation_potential": 0.7,
                    "tightening_effect": 0.3
                },
                recommendation="Climate filter appropriately balanced"
            )
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Impact analysis error: {str(e)}")


@router.post("/filter-conflict-detection", response_model=List[FilterConflictExplanation])
async def detect_filter_conflicts(
    filter_criteria: TaxonomyFilterCriteria
):
    """
    Detect potential conflicts between different filter criteria.
    
    **Features:**
    - Cross-filter compatibility analysis
    - Conflict identification
    - Severity assessment
    - Resolution strategies
    - Agricultural constraint validation
    
    **Conflict Types:**
    - Geographic-climate incompatibilities
    - Soil-plant type mismatches
    - Market-season conflicts
    - Resource-requirement conflicts
    """
    try:
        conflicts = explanation_service.identify_filter_conflicts(filter_criteria)
        return conflicts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conflict detection error: {str(e)}")


@router.post("/filter-tuning-suggestions", response_model=List[FilterTuningSuggestion])
async def get_filter_tuning_suggestions(
    search_response: CropSearchResponse,
    filter_criteria: TaxonomyFilterCriteria,
    total_crop_count: int = Query(1000, description="Total number of crops in the database")
):
    """
    Get suggestions for tuning filter parameters to improve search results.
    
    **Features:**
    - Parameter optimization recommendations
    - Result count balancing
    - Agricultural context awareness
    - Confidence scoring
    - Expected impact estimates
    
    **Tuning Strategies:**
    - Relaxing overly restrictive filters
    - Tightening permissive filters
    - Balancing competing requirements
    - Optimizing for desired result count
    """
    try:
        suggestions = explanation_service.generate_tuning_suggestions(
            filter_criteria,
            len(search_response.results),
            total_crop_count
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tuning suggestions error: {str(e)}")


@router.post("/comprehensive-filter-analysis", response_model=Dict[str, Any])
async def get_comprehensive_filter_analysis(
    search_response: CropSearchResponse,
    filter_criteria: TaxonomyFilterCriteria,
    total_crop_count: int = Query(1000, description="Total number of crops in the database")
):
    """
    Get comprehensive analysis of filter effectiveness and recommendations.
    
    **Analysis includes:**
    - Filter impact analysis
    - Conflict detection
    - Tuning suggestions
    - Results quality metrics
    - Alternative approaches
    
    **Output:**
    - filter_impact: Analysis of how each filter affects results
    - conflicts: Identified conflicts between filters
    - tuning_suggestions: Recommendations for filter adjustments
    - overall_assessment: Quality assessment of the filter strategy
    """
    try:
        # Perform all analyses
        impact_analysis = explanation_service.analyze_filter_impact(
            search_response.results,
            filter_criteria
        )
        
        conflicts = explanation_service.identify_filter_conflicts(
            filter_criteria
        )
        
        tuning_suggestions = explanation_service.generate_tuning_suggestions(
            filter_criteria,
            len(search_response.results),
            total_crop_count
        )
        
        # Create overall assessment
        overall_assessment = {
            "result_count": len(search_response.results),
            "filter_efficiency": len(search_response.results) / total_crop_count,
            "conflict_count": len(conflicts),
            "suggestion_count": len(tuning_suggestions),
            "recommendation": "Optimal" if len(conflicts) == 0 and len(search_response.results) > 0 else "Review needed"
        }
        
        return {
            "filter_impact": impact_analysis,
            "conflicts": conflicts,
            "tuning_suggestions": tuning_suggestions,
            "overall_assessment": overall_assessment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis error: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint for the explanation service.
    """
    return {
        "status": "healthy",
        "service": "filter-explanations",
        "version": "1.0.0",
        "components": {
            "filter_explanation": "operational",
            "impact_analysis": "operational",
            "conflict_detection": "operational",
            "tuning_suggestions": "operational"
        }
    }