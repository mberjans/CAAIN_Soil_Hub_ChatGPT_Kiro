"""
Filter Explanation Service

Service to provide comprehensive explanations for crop filtering results,
including why crops were included/excluded, filter impact analysis, and
tuning suggestions.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
import logging
import sys
import os

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from models.crop_filtering_models import (
    FilterExplanation,
    FilterExplanationResponse,
    FilterImpactAnalysis,
    FilterConflictExplanation,
    FilterTuningSuggestion,
    CropSearchResult,
    TaxonomyFilterCriteria,
    ComprehensiveCropData
)

logger = logging.getLogger(__name__)


class FilterExplanationService:
    """Service to provide explanations for crop filtering results."""
    
    def __init__(self):
        self.filter_descriptions = {
            "text": "Text matching filters",
            "geographic": "Geographic and climate zone filters",
            "climate": "Climate requirement filters",
            "soil": "Soil characteristic filters",
            "agricultural": "Agricultural classification filters",
            "management": "Management complexity filters",
            "sustainability": "Sustainability and environmental filters",
            "economic": "Economic and market filters"
        }
        
    def explain_filter_result(
        self,
        crop: ComprehensiveCropData,
        search_result: CropSearchResult,
        criteria: TaxonomyFilterCriteria
    ) -> FilterExplanationResponse:
        """
        Generate comprehensive explanations for why a crop was included/excluded 
        from search results based on filter criteria.
        """
        explanations = []
        
        # Extract filter breakdown from ranking details if available
        if search_result.ranking_details and search_result.ranking_details.filter_scores:
            for score_breakdown in search_result.ranking_details.filter_scores:
                explanation = self._create_filter_explanation(
                    crop,
                    score_breakdown.name,
                    score_breakdown.score,
                    score_breakdown.matched,
                    criteria
                )
                explanations.append(explanation)
        else:
            # If no breakdown is available, create default explanations based on score
            explanations = self._fallback_explanations(crop, search_result, criteria)
        
        # Determine overall recommendation
        overall_score = search_result.suitability_score
        if overall_score >= 0.8:
            recommendation = "Highly recommended based on your criteria"
        elif overall_score >= 0.5:
            recommendation = "Moderately suitable, consider trade-offs"
        else:
            recommendation = "Not recommended based on your criteria"
        
        # Generate improvement suggestions if score is low
        improvement_suggestions = []
        if overall_score < 0.5:
            improvement_suggestions = self._generate_improvement_suggestions(
                crop, explanations, criteria
            )
        
        # Generate alternative suggestions
        alternative_suggestions = []
        if overall_score < 0.5:
            alternative_suggestions = self._generate_alternative_suggestions(
                crop, explanations
            )
        
        return FilterExplanationResponse(
            crop_id=crop.crop_id,
            crop_name=crop.crop_name,
            overall_compatibility_score=overall_score,
            filter_explanations=explanations,
            recommendation=recommendation,
            alternative_suggestions=alternative_suggestions,
            improvement_suggestions=improvement_suggestions
        )
    
    def _create_filter_explanation(
        self,
        crop: ComprehensiveCropData,
        filter_name: str,
        score: float,
        matched: bool,
        criteria: TaxonomyFilterCriteria
    ) -> FilterExplanation:
        """Create an explanation for a specific filter."""
        # Determine crop value based on filter type
        crop_value = self._get_crop_value_for_filter(crop, filter_name)
        
        # Determine filter requirement based on criteria
        filter_requirement = self._get_filter_requirement_for_criteria(criteria, filter_name)
        
        # Create explanation text
        explanation = self._generate_explanation_text(
            filter_name,
            crop_value,
            filter_requirement,
            matched,
            score
        )
        
        # Determine confidence based on match status and score
        confidence = score if matched else (1.0 - score)
        
        return FilterExplanation(
            filter_name=filter_name,
            filter_category=self.filter_descriptions.get(filter_name, filter_name),
            crop_value=crop_value,
            filter_requirement=filter_requirement,
            matched=matched,
            score=score,
            explanation=explanation,
            confidence=confidence
        )
    
    def _get_crop_value_for_filter(self, crop: ComprehensiveCropData, filter_name: str):
        """Get the crop's value for a specific filter."""
        if filter_name == "climate":
            return crop.climate_adaptations
        elif filter_name == "soil":
            return crop.soil_requirements
        elif filter_name == "agricultural":
            return crop.agricultural_classification
        elif filter_name == "management":
            return crop.filtering_attributes
        elif filter_name == "sustainability":
            return crop.filtering_attributes
        elif filter_name == "economic":
            return crop.filtering_attributes if crop.filtering_attributes else {}
        else:
            # Default: return entire crop object
            return crop
    
    def _get_filter_requirement_for_criteria(
        self, 
        criteria: TaxonomyFilterCriteria, 
        filter_name: str
    ):
        """Get the filter requirement from criteria for a specific filter."""
        if filter_name == "geographic":
            return criteria.geographic_filter
        elif filter_name == "climate":
            return criteria.climate_filter
        elif filter_name == "soil":
            return criteria.soil_filter
        elif filter_name == "agricultural":
            return criteria.agricultural_filter
        elif filter_name == "management":
            return criteria.management_filter
        elif filter_name == "sustainability":
            return criteria.sustainability_filter
        elif filter_name == "economic":
            return criteria.economic_filter
        else:
            return getattr(criteria, filter_name + "_filter", None)
    
    def _generate_explanation_text(
        self,
        filter_name: str,
        crop_value,
        filter_requirement,
        matched: bool,
        score: float
    ) -> str:
        """Generate explanation text for the filter result."""
        if filter_requirement is None:
            return f"No {filter_name} filter was applied"
        
        if matched:
            if score >= 0.9:
                return f"Excellent match for {filter_name} criteria - fully compatible"
            elif score >= 0.7:
                return f"Good match for {filter_name} criteria - meets requirements"
            else:
                return f"Partial match for {filter_name} criteria - acceptable but not ideal"
        else:
            if score <= 0.1:
                return f"Poor match for {filter_name} criteria - significantly fails requirements"
            elif score <= 0.3:
                return f"Low compatibility for {filter_name} criteria - major limitations"
            else:
                return f"Moderate compatibility for {filter_name} criteria - some limitations"
    
    def _fallback_explanations(
        self,
        crop: ComprehensiveCropData,
        search_result: CropSearchResult,
        criteria: TaxonomyFilterCriteria
    ) -> List[FilterExplanation]:
        """Generate fallback explanations when detailed breakdown is not available."""
        explanations = []
        
        # Check if each filter type was applied
        applied_filters = []
        
        if criteria.geographic_filter:
            applied_filters.append("geographic")
        if criteria.climate_filter:
            applied_filters.append("climate")
        if criteria.soil_filter:
            applied_filters.append("soil")
        if criteria.agricultural_filter:
            applied_filters.append("agricultural")
        if criteria.management_filter:
            applied_filters.append("management")
        if criteria.sustainability_filter:
            applied_filters.append("sustainability")
        if criteria.economic_filter:
            applied_filters.append("economic")
        
        # Create a general explanation for each applied filter
        for filter_name in applied_filters:
            # For fallback, we'll use overall result score as an approximation
            explanation = FilterExplanation(
                filter_name=filter_name,
                filter_category=self.filter_descriptions.get(filter_name, filter_name),
                crop_value=self._get_crop_value_for_filter(crop, filter_name),
                filter_requirement=self._get_filter_requirement_for_criteria(criteria, filter_name),
                matched=search_result.suitability_score > 0.5,
                score=search_result.suitability_score,
                explanation=f"Based on overall compatibility of {search_result.suitability_score:.2f}",
                confidence=search_result.suitability_score if search_result.suitability_score > 0.5 
                else (1.0 - search_result.suitability_score)
            )
            explanations.append(explanation)
        
        return explanations
    
    def _generate_improvement_suggestions(
        self,
        crop: ComprehensiveCropData,
        explanations: List[FilterExplanation],
        criteria: TaxonomyFilterCriteria
    ) -> List[str]:
        """Generate improvement suggestions based on failed filters."""
        suggestions = []
        
        # Identify the filters with the lowest scores
        low_scoring_filters = [exp for exp in explanations if exp.score < 0.5]
        
        for exp in low_scoring_filters:
            if exp.filter_name == "climate":
                if exp.crop_value and hasattr(exp.crop_value, 'optimal_temp_min_f') and exp.crop_value.optimal_temp_max_f:
                    suggestions.append(
                        "Consider adjusting temperature requirements to match the crop's optimal range: "
                        f"{exp.crop_value.optimal_temp_min_f}°F to {exp.crop_value.optimal_temp_max_f}°F"
                    )
            elif exp.filter_name == "soil":
                if exp.crop_value and hasattr(exp.crop_value, 'optimal_ph_min') and exp.crop_value.optimal_ph_max:
                    suggestions.append(
                        f"Adjust soil pH requirements to {exp.crop_value.optimal_ph_min} - {exp.crop_value.optimal_ph_max} "
                        "for better compatibility with this crop"
                    )
            elif exp.filter_name == "management" and exp.crop_value:
                if hasattr(exp.crop_value, 'management_complexity'):
                    suggestions.append(
                        f"This crop requires management complexity level '{exp.crop_value.management_complexity}', "
                        "which may be higher than your requirement"
                    )
        
        return suggestions
    
    def _generate_alternative_suggestions(
        self,
        crop: ComprehensiveCropData,
        explanations: List[FilterExplanation]
    ) -> List[str]:
        """Generate alternative crop suggestions based on filtering results."""
        suggestions = []
        
        # Identify the main reason for low compatibility
        weak_filters = [exp for exp in explanations if exp.score < 0.4]
        
        for exp in weak_filters:
            if exp.filter_name == "climate":
                suggestions.append("Consider crops with more flexible climate requirements")
            elif exp.filter_name == "soil":
                suggestions.append("Consider crops with broader soil adaptability")
            elif exp.filter_name == "drought":
                suggestions.append("Consider drought-tolerant alternatives")
        
        # Add general suggestions if no specific ones were generated
        if not suggestions:
            suggestions.append("Consider crops with different characteristics")
            suggestions.append("Adjust your filtering criteria for more options")
        
        return suggestions
    
    def analyze_filter_impact(
        self,
        all_results: List[CropSearchResult],
        criteria: TaxonomyFilterCriteria
    ) -> List[FilterImpactAnalysis]:
        """
        Analyze how each filter impacts the overall search results.
        """
        analyses = []
        
        # Count how many crops were affected by each filter category
        total_crops = len(all_results)
        if total_crops == 0:
            return analyses
        
        # For this implementation, we'll analyze based on the breakdown in results
        # if available
        if all_results and all_results[0].ranking_details:
            filter_names = set()
            for result in all_results:
                if result.ranking_details:
                    for score_breakdown in result.ranking_details.filter_scores:
                        filter_names.add(score_breakdown.name)
            
            for filter_name in filter_names:
                # Calculate average impact for this filter
                total_scores = 0.0
                count = 0
                exclusions = 0
                
                for result in all_results:
                    if result.ranking_details:
                        for score_breakdown in result.ranking_details.filter_scores:
                            if score_breakdown.name == filter_name:
                                total_scores += score_breakdown.score
                                count += 1
                                if score_breakdown.score < 0.3:  # Considered low compatibility
                                    exclusions += 1
                
                if count > 0:
                    avg_impact = total_scores / count
                    exclusion_rate = exclusions / total_crops
                    
                    analysis = FilterImpactAnalysis(
                        filter_name=filter_name,
                        total_crops_affected=count,
                        average_impact_score=avg_impact,
                        exclusion_rate=exclusion_rate,
                        sensitivity_analysis=self._calculate_sensitivity(filter_name, criteria),
                        recommendation=self._generate_impact_recommendation(filter_name, avg_impact, exclusion_rate)
                    )
                    analyses.append(analysis)
        
        return analyses
    
    def _calculate_sensitivity(self, filter_name: str, criteria: TaxonomyFilterCriteria) -> Dict[str, float]:
        """Calculate sensitivity of results to changes in filter parameters."""
        # This is a simplified implementation - in a real system, you'd run multiple queries
        # with slightly modified parameters
        return {
            "parameter_sensitivity": 0.5,
            "relaxation_potential": 0.7,
            "tightening_effect": 0.3
        }
    
    def _generate_impact_recommendation(
        self,
        filter_name: str,
        avg_impact: float,
        exclusion_rate: float
    ) -> str:
        """Generate a recommendation based on filter impact analysis."""
        if exclusion_rate > 0.8:
            return f"The '{filter_name}' filter is very restrictive, excluding most crops. Consider relaxing this filter."
        elif exclusion_rate > 0.5:
            return f"The '{filter_name}' filter is moderately restrictive. Review if requirements are too strict."
        elif avg_impact < 0.3:
            return f"The '{filter_name}' filter has low compatibility across results. Consider alternatives."
        else:
            return f"The '{filter_name}' filter is appropriately set for your needs."
    
    def identify_filter_conflicts(
        self,
        criteria: TaxonomyFilterCriteria
    ) -> List[FilterConflictExplanation]:
        """
        Identify potential conflicts between different filter criteria.
        """
        conflicts = []
        
        # Check for geographic vs climate conflicts
        if (criteria.geographic_filter and criteria.geographic_filter.hardiness_zones and
            criteria.climate_filter and criteria.climate_filter.drought_tolerance_required):
            # Check if specified zones are known to have drought conditions
            drought_zones = ["7b", "8a", "8b", "9a", "9b", "10a", "10b"]  # Simplified for example
            conflict_zones = [z for z in criteria.geographic_filter.hardiness_zones 
                             if z in drought_zones]
            
            if conflict_zones and str(criteria.climate_filter.drought_tolerance_required).lower() == "none":
                conflicts.append(FilterConflictExplanation(
                    conflicting_filters=["geographic", "climate"],
                    conflict_type="climate-geographic",
                    explanation=f"Hardiness zones {conflict_zones} are typically dry areas but drought tolerance is required to be none",
                    severity="high",
                    resolution_suggestions=[
                        "Adjust drought tolerance requirement to 'moderate' or higher",
                        "Select different hardiness zones with more moisture",
                        "Consider irrigation options"
                    ]
                ))
        
        # Check for soil pH vs plant type conflicts
        if (criteria.soil_filter and 
            criteria.soil_filter.ph_range and 
            criteria.agricultural_filter and
            criteria.agricultural_filter.plant_types):
            
            acid_loving_plants = ["blueberry", "rhododendron", "azalea"]  # Simplified for example
            if (criteria.soil_filter.ph_range.get("min", 7.0) > 6.0 and 
                any(str(pt).lower() in acid_loving_plants for pt in criteria.agricultural_filter.plant_types)):
                
                conflicts.append(FilterConflictExplanation(
                    conflicting_filters=["soil", "agricultural"],
                    conflict_type="soil-plant_type",
                    explanation="Selected plant types prefer acidic soil, but soil pH requirements are neutral to alkaline",
                    severity="medium",
                    resolution_suggestions=[
                        "Lower soil pH requirements to acidic range (5.0-6.0)",
                        "Select different plant types that prefer neutral pH",
                        "Consider soil amendments for acid-loving plants"
                    ]
                ))
        
        return conflicts
    
    def generate_tuning_suggestions(
        self,
        criteria: TaxonomyFilterCriteria,
        results_count: int,
        total_crops: int
    ) -> List[FilterTuningSuggestion]:
        """
        Generate suggestions for tuning filter parameters based on search results.
        """
        suggestions = []
        
        # If no results, suggest relaxing filters
        if results_count == 0:
            if criteria.climate_filter and criteria.climate_filter.drought_tolerance_required:
                suggestions.append(FilterTuningSuggestion(
                    filter_name="drought_tolerance",
                    current_value=criteria.climate_filter.drought_tolerance_required,
                    suggested_value="moderate",  # Suggest less restrictive
                    expected_impact="May increase results by 20-40%",
                    confidence=0.7,
                    reasoning="No results found; drought tolerance may be too restrictive"
                ))
            
            if criteria.soil_filter and criteria.soil_filter.ph_range:
                suggestions.append(FilterTuningSuggestion(
                    filter_name="soil_ph_range",
                    current_value=criteria.soil_filter.ph_range,
                    suggested_value={"min": max(5.5, criteria.soil_filter.ph_range.get("min", 6.0) - 0.5),
                                   "max": min(7.5, criteria.soil_filter.ph_range.get("max", 7.0) + 0.5)},
                    expected_impact="May increase results by 10-25%",
                    confidence=0.6,
                    reasoning="Expanding pH range may include more compatible crops"
                ))
        
        # If too many results, suggest tightening filters
        elif results_count > 50 and results_count > total_crops * 0.5:
            if criteria.management_filter and not criteria.management_filter.max_management_complexity:
                suggestions.append(FilterTuningSuggestion(
                    filter_name="management_complexity",
                    current_value="unspecified",
                    suggested_value="moderate",
                    expected_impact="May reduce results by 30-50%",
                    confidence=0.8,
                    reasoning="Many results available; filtering by management complexity can focus options"
                ))
        
        return suggestions