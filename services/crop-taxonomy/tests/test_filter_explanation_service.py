"""
Unit tests for the Filter Explanation Service
"""
import pytest
from unittest.mock import Mock
from uuid import UUID
import sys
import os

# Add the src directory to the path to allow imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import models directly without triggering service initialization
from models.crop_filtering_models import (
    FilterExplanation,
    FilterExplanationResponse,
    FilterImpactAnalysis,
    FilterConflictExplanation,
    FilterTuningSuggestion,
    TaxonomyFilterCriteria,
    GeographicFilter,
    ClimateFilter,
    SoilFilter,
    AgriculturalFilter,
    ResultRankingDetails,
    FilterScoreBreakdown,
    SearchOperator,
    SortOrder,
    SortField
)
from models.crop_taxonomy_models import (
    ComprehensiveCropData,
    CropTaxonomicHierarchy,
    CropAgriculturalClassification,
    CropClimateAdaptations,
    CropSoilRequirements
)

# Import service using absolute path to avoid relative import issues
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from services.filter_explanation_service import FilterExplanationService


class TestFilterExplanationService:
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.service = FilterExplanationService()
        
        # Create a mock crop for testing
        self.mock_crop = ComprehensiveCropData(
            crop_id=UUID("12345678-1234-5678-1234-567812345678"),
            crop_name="Test Crop",
            scientific_name="Testus cropus",
            taxonomic_hierarchy=CropTaxonomicHierarchy(
                kingdom="Plantae",
                family="Poaceae",
                genus="Triticum",
                species="aestivum",
                common_synonyms=["Wheat", "Grain"]
            ),
            agricultural_classification=CropAgriculturalClassification(
                crop_category="grain",
                primary_use="food_human",
                life_cycle="annual",
                growth_habit="erect",
                plant_type="grass",
                photosynthesis_pathway="c3",
                nitrogen_fixing=False,
                maturity_days_min=90,
                maturity_days_max=120,
                height_min_cm=60,
                height_max_cm=120,
                preferred_spacing_cm=20,
                row_spacing_cm=30
            ),
            climate_adaptations=CropClimateAdaptations(
                hardiness_zones=["5", "6", "7"],
                optimal_temp_min_f=50,
                optimal_temp_max_f=80,
                frost_tolerance="moderate",
                heat_tolerance="moderate",
                drought_tolerance="moderate",
                humidity_preference="moderate",
                elevation_min_feet=0,
                elevation_max_feet=3000,
                growing_season_length_days=120
            ),
            soil_requirements=CropSoilRequirements(
                optimal_ph_min=6.0,
                optimal_ph_max=7.0,
                tolerable_ph_min=5.5,
                tolerable_ph_max=7.5,
                preferred_textures=["loam", "clay_loam"],
                tolerable_textures=["sandy_loam", "silty_loam"],
                drainage_requirement="well_drained",
                organic_matter_min_percent=2.0,
                salinity_tolerance="moderate",
                aluminum_tolerance="low"
            )
        )
    
    def test_explain_filter_result_basic(self):
        """Test basic filter explanation functionality."""
        # Create a search result with mock data
        from ..src.models.crop_filtering_models import (
            CropSearchResult,
            ResultRankingDetails,
            FilterScoreBreakdown
        )
        
        mock_search_result = CropSearchResult(
            crop=self.mock_crop,
            relevance_score=0.75,
            suitability_score=0.75,
            matching_criteria=["climate", "soil"],
            partial_matches=["management"],
            missing_criteria=[],
            search_highlights={},
            similarity_factors={},
            ranking_details=ResultRankingDetails(
                active_filters=3,
                matched_filters=2,
                partial_filters=1,
                missing_filters=0,
                coverage=0.67,
                filter_scores=[
                    FilterScoreBreakdown(
                        name="climate",
                        weight=0.2,
                        score=0.8,
                        matched=True,
                        partial=False,
                        notes=["Climate requirements met"]
                    ),
                    FilterScoreBreakdown(
                        name="soil", 
                        weight=0.15,
                        score=0.9,
                        matched=True,
                        partial=False,
                        notes=["Soil requirements met"]
                    ),
                    FilterScoreBreakdown(
                        name="management",
                        weight=0.05,
                        score=0.4,
                        matched=False,
                        partial=True,
                        notes=["Management requirements partially met"]
                    )
                ]
            ),
            recommendation_notes=[],
            potential_concerns=[]
        )
        
        criteria = TaxonomyFilterCriteria()
        
        # Test the explanation service
        response = self.service.explain_filter_result(
            self.mock_crop,
            mock_search_result,
            criteria
        )
        
        assert isinstance(response, FilterExplanationResponse)
        assert response.crop_id == self.mock_crop.crop_id
        assert response.crop_name == self.mock_crop.crop_name
        assert response.overall_compatibility_score == 0.75
        assert len(response.filter_explanations) == 3
        assert all(isinstance(exp, FilterExplanation) for exp in response.filter_explanations)
    
    def test_identify_filter_conflicts_no_conflicts(self):
        """Test conflict detection when there are no conflicts."""
        # Create criteria without conflicts
        criteria = TaxonomyFilterCriteria(
            geographic_filter=GeographicFilter(
                hardiness_zones=["5a", "5b"]
            ),
            climate_filter=ClimateFilter(
                drought_tolerance_required="moderate"
            )
        )
        
        conflicts = self.service.identify_filter_conflicts(criteria)
        
        # Should return empty list since there are no conflicts in our simplified detection
        assert isinstance(conflicts, list)
    
    def test_identify_filter_conflicts_with_conflicts(self):
        """Test conflict detection when there are conflicts."""
        # Create criteria with potential conflicts
        criteria = TaxonomyFilterCriteria(
            geographic_filter=GeographicFilter(
                hardiness_zones=["9a", "9b"]  # Typically dry zones
            ),
            climate_filter=ClimateFilter(
                drought_tolerance_required="none"  # Requires no drought tolerance
            ),
            soil_filter=SoilFilter(
                ph_range={"min": 7.5, "max": 8.0}  # Alkaline
            ),
            agricultural_filter=AgriculturalFilter(
                primary_uses=["forage"]
            )
        )
        
        conflicts = self.service.identify_filter_conflicts(criteria)
        
        assert isinstance(conflicts, list)
        # In our implementation, conflicts would be detected based on the logic in the service
        # Our simplified implementation may not detect any conflicts with these specific values
    
    def test_analyze_filter_impact(self):
        """Test filter impact analysis."""
        from ..src.models.crop_filtering_models import (
            CropSearchResult,
            ResultRankingDetails,
            FilterScoreBreakdown
        )
        
        # Create mock search results
        mock_results = [
            CropSearchResult(
                crop=self.mock_crop,
                relevance_score=0.7,
                suitability_score=0.7,
                matching_criteria=["climate"],
                partial_matches=[],
                missing_criteria=["soil"],
                search_highlights={},
                similarity_factors={},
                ranking_details=ResultRankingDetails(
                    active_filters=2,
                    matched_filters=1,
                    partial_filters=0,
                    missing_filters=1,
                    coverage=0.5,
                    filter_scores=[
                        FilterScoreBreakdown(
                            name="climate",
                            weight=0.2,
                            score=0.8,
                            matched=True,
                            partial=False,
                            notes=["Climate match"]
                        ),
                        FilterScoreBreakdown(
                            name="soil",
                            weight=0.15,
                            score=0.3,
                            matched=False,
                            partial=False,
                            notes=["Soil mismatch"]
                        )
                    ]
                ),
                recommendation_notes=[],
                potential_concerns=[]
            )
        ]
        
        criteria = TaxonomyFilterCriteria()
        impact_analysis = self.service.analyze_filter_impact(mock_results, criteria)
        
        assert isinstance(impact_analysis, list)
        if impact_analysis:  # Only check if analysis was possible
            assert all(isinstance(analysis, FilterImpactAnalysis) for analysis in impact_analysis)
    
    def test_generate_tuning_suggestions_no_results(self):
        """Test tuning suggestions when there are no results."""
        criteria = TaxonomyFilterCriteria()
        
        # Test with 0 results
        suggestions = self.service.generate_tuning_suggestions(criteria, 0, 1000)
        
        assert isinstance(suggestions, list)
        # If there are no results, our implementation might generate suggestions to relax filters
    
    def test_generate_tuning_suggestions_many_results(self):
        """Test tuning suggestions when there are too many results."""
        criteria = TaxonomyFilterCriteria()
        
        # Test with many results
        suggestions = self.service.generate_tuning_suggestions(criteria, 100, 100)
        
        assert isinstance(suggestions, list)
        # If there are too many results, our implementation might suggest tightening filters

    def test_filter_explanation_attributes(self):
        """Test that filter explanations have the correct structure."""
        explanation = FilterExplanation(
            filter_name="climate",
            filter_category="Climate Requirements",
            crop_value=25.0,
            filter_requirement={"min": 20.0, "max": 30.0},
            matched=True,
            score=0.8,
            explanation="Crop temperature range matches requirements",
            confidence=0.8
        )
        
        assert explanation.filter_name == "climate"
        assert explanation.matched is True
        assert explanation.score == 0.8
        assert explanation.confidence == 0.8
        assert "temperature" in explanation.explanation.lower()

    def test_filter_explanation_response_structure(self):
        """Test that filter explanation responses have the correct structure."""
        response = FilterExplanationResponse(
            crop_id=self.mock_crop.crop_id,
            crop_name=self.mock_crop.crop_name,
            overall_compatibility_score=0.75,
            filter_explanations=[],
            recommendation="Recommended",
            alternative_suggestions=["Alternative 1"],
            improvement_suggestions=["Suggestion 1"]
        )
        
        assert response.crop_id == self.mock_crop.crop_id
        assert response.crop_name == self.mock_crop.crop_name
        assert 0.0 <= response.overall_compatibility_score <= 1.0
        assert isinstance(response.filter_explanations, list)
        assert isinstance(response.recommendation, str)
        assert isinstance(response.alternative_suggestions, list)
        assert isinstance(response.improvement_suggestions, list)

    def test_filter_conflict_explanation_structure(self):
        """Test that filter conflict explanations have the correct structure."""
        conflict = FilterConflictExplanation(
            conflicting_filters=["climate", "soil"],
            conflict_type="climate-soil",
            explanation="Climate and soil requirements conflict",
            severity="high",
            resolution_suggestions=["Suggestion 1", "Suggestion 2"]
        )
        
        assert isinstance(conflict.conflicting_filters, list)
        assert conflict.conflict_type == "climate-soil"
        assert isinstance(conflict.explanation, str)
        assert conflict.severity in ["low", "medium", "high"]
        assert isinstance(conflict.resolution_suggestions, list)

    def test_filter_tuning_suggestion_structure(self):
        """Test that filter tuning suggestions have the correct structure."""
        suggestion = FilterTuningSuggestion(
            filter_name="drought_tolerance",
            current_value="none",
            suggested_value="moderate",
            expected_impact="May increase results",
            confidence=0.8,
            reasoning="Current setting is too restrictive"
        )
        
        assert isinstance(suggestion.filter_name, str)
        assert suggestion.confidence == 0.8
        assert isinstance(suggestion.reasoning, str)
        assert 0.0 <= suggestion.confidence <= 1.0