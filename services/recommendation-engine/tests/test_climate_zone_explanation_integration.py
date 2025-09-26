"""
Test suite for climate zone integration in AI explanation service.

This tests the enhanced AI explanation service with climate zone context
to ensure recommendations include appropriate climate-aware explanations.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

# Import the AI explanation service
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from services.ai_explanation_service import AIExplanationService


class TestClimateZoneExplanationIntegration:
    """Test climate zone integration in AI explanation service."""
    
    @pytest.fixture
    def explanation_service(self):
        """Create AI explanation service instance."""
        return AIExplanationService()
    
    @pytest.fixture
    def sample_crop_recommendation(self):
        """Sample crop recommendation with climate zone data."""
        return {
            'crop_name': 'corn',
            'confidence_score': 0.85,
            'climate_zone': '6a',
            'climate_compatibility_score': 1.0,
            'compatible_climate_zones': ['5a', '5b', '6a', '6b', '7a'],
            'timing': 'Plant mid-April to early May',
            'cost_per_acre': 125.50,
            'agricultural_sources': ['USDA Extension', 'State University Research']
        }
    
    @pytest.fixture
    def sample_location_data(self):
        """Sample location data with climate zone."""
        mock_location = Mock()
        mock_location.climate_zone = '6a'
        mock_location.latitude = 42.5
        mock_location.longitude = -83.5
        return mock_location
    
    @pytest.fixture
    def sample_context(self, sample_location_data):
        """Sample context with soil and location data."""
        return {
            'location_data': sample_location_data,
            'soil_data': {
                'ph': 6.2,
                'organic_matter_percent': 3.5,
                'phosphorus_ppm': 25,
                'potassium_ppm': 150
            },
            'farm_profile': {
                'farm_size_acres': 200,
                'irrigation_available': True
            }
        }
    
    def test_generate_explanation_includes_climate_zone_context(self, explanation_service, sample_crop_recommendation, sample_context):
        """Test that crop selection explanations include climate zone context."""
        explanation = explanation_service.generate_explanation(
            recommendation_type="crop_selection",
            recommendation_data=sample_crop_recommendation,
            context=sample_context
        )
        
        # Should include climate zone information
        assert "Climate Zone 6a" in explanation
        assert "optimal for corn production" in explanation
        assert "corn is highly suitable" in explanation
        assert "optimal" in explanation  # pH assessment
    
    def test_climate_zone_context_generation_optimal_zone(self, explanation_service, sample_crop_recommendation, sample_context):
        """Test climate zone context for optimal compatibility."""
        context_text = explanation_service._generate_climate_zone_context(
            sample_crop_recommendation, sample_context
        )
        
        assert "Climate Zone 6a is optimal for corn production" in context_text
    
    def test_climate_zone_context_generation_adjacent_zone(self, explanation_service, sample_context):
        """Test climate zone context for adjacent zone compatibility."""
        recommendation_data = {
            'crop_name': 'soybean',
            'climate_zone': '7b',
            'climate_compatibility_score': 0.8,
            'compatible_climate_zones': ['6a', '6b', '7a']
        }
        
        context_text = explanation_service._generate_climate_zone_context(
            recommendation_data, sample_context
        )
        
        assert "Climate Zone 7b is well-suited for soybean" in context_text
        assert "adjacent to optimal zones" in context_text
    
    def test_climate_zone_context_generation_marginal_zone(self, explanation_service, sample_context):
        """Test climate zone context for marginal compatibility."""
        recommendation_data = {
            'crop_name': 'wheat',
            'climate_zone': '8b',
            'climate_compatibility_score': 0.6
        }
        
        context_text = explanation_service._generate_climate_zone_context(
            recommendation_data, sample_context
        )
        
        assert "Climate Zone 8b is marginal for wheat" in context_text
        assert "heat/cold tolerant varieties" in context_text
    
    def test_climate_zone_context_generation_incompatible_zone(self, explanation_service, sample_context):
        """Test climate zone context for incompatible zones."""
        recommendation_data = {
            'crop_name': 'corn',
            'climate_zone': '9b',
            'climate_compatibility_score': 0.3,
            'compatible_climate_zones': ['5a', '6a', '7a']
        }
        
        context_text = explanation_service._generate_climate_zone_context(
            recommendation_data, sample_context
        )
        
        assert "Climate Zone 9b may present challenges for corn" in context_text
        assert "Optimal zones are 5a, 6a, 7a" in context_text
    
    def test_seasonal_timing_advice_with_climate_zone(self, explanation_service, sample_crop_recommendation, sample_location_data):
        """Test seasonal timing advice includes climate zone considerations."""
        with patch('services.ai_explanation_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = Mock(month=4)  # April
            
            timing_advice = explanation_service.generate_seasonal_timing_advice(
                recommendation_type="crop_selection",
                recommendation_data=sample_crop_recommendation,
                location_data=sample_location_data
            )
            
            assert "Zone 6a" in timing_advice
            assert "April" in timing_advice or "planting" in timing_advice
    
    def test_crop_timing_advice_northern_zone(self, explanation_service):
        """Test crop timing advice for northern climate zones."""
        recommendation_data = {'crop_name': 'corn', 'climate_zone': '3a'}
        
        timing_advice = explanation_service._generate_crop_timing_advice(
            recommendation_data, current_month=4, climate_zone='3a'
        )
        
        assert "Zone 3a" in timing_advice
        assert "late May" in timing_advice or "extended frost risk" in timing_advice
    
    def test_crop_timing_advice_southern_zone(self, explanation_service):
        """Test crop timing advice for southern climate zones."""
        recommendation_data = {'crop_name': 'corn', 'climate_zone': '7a'}
        
        timing_advice = explanation_service._generate_crop_timing_advice(
            recommendation_data, current_month=4, climate_zone='7a'
        )
        
        assert "Zone 7a" in timing_advice
        assert "April" in timing_advice or "early" in timing_advice
    
    def test_soil_timing_advice_with_climate_zone(self, explanation_service):
        """Test soil fertility timing advice includes climate zone considerations."""
        timing_advice = explanation_service._generate_soil_timing_advice(
            recommendation_data={}, current_month=10, climate_zone='4a'
        )
        
        assert "Zone 4a" in timing_advice
        assert "early fall" in timing_advice or "ground freeze" in timing_advice
    
    def test_fertilizer_timing_advice_with_climate_zone(self, explanation_service):
        """Test fertilizer timing advice includes climate zone considerations."""
        recommendation_data = {'fertilizer_type': 'nitrogen'}
        
        timing_advice = explanation_service._generate_fertilizer_timing_advice(
            recommendation_data, current_month=4, climate_zone='3b'
        )
        
        assert "Zone 3b" in timing_advice
        assert "soil temperature" in timing_advice or "delayed" in timing_advice
    
    def test_climate_timing_context_generation(self, explanation_service):
        """Test climate timing context generation for different zones."""
        # Northern zone
        context_3a = explanation_service._get_climate_timing_context('3a')
        assert "shorter growing season" in context_3a
        
        # Moderate zone
        context_6a = explanation_service._get_climate_timing_context('6a')
        assert "moderate growing season" in context_6a
        
        # Southern zone
        context_8a = explanation_service._get_climate_timing_context('8a')
        assert "extended growing season" in context_8a
        
        # Tropical zone
        context_10a = explanation_service._get_climate_timing_context('10a')
        assert "year-round growing" in context_10a
    
    def test_enhanced_explanation_includes_climate_recommendations(self, explanation_service, sample_context):
        """Test that enhanced explanations include climate-specific recommendations."""
        # Test with marginal climate compatibility
        recommendation_data = {
            'crop_name': 'wheat',
            'climate_zone': '8b',
            'climate_compatibility_score': 0.6,
            'timing': 'Fall planting recommended',
            'agricultural_sources': ['Extension Service']
        }
        
        base_explanation = "Wheat is suitable for your farm conditions."
        enhanced = explanation_service._enhance_explanation(
            base_explanation, recommendation_data, sample_context
        )
        
        assert "cold-hardy or heat-tolerant varieties" in enhanced
        assert "Zone 8b" in enhanced
    
    def test_extract_climate_zone_from_various_sources(self, explanation_service):
        """Test climate zone extraction from different data sources."""
        # From location_data object
        location_mock = Mock()
        location_mock.climate_zone = '6a'
        context1 = {'location_data': location_mock}
        
        zone = explanation_service._extract_climate_zone({}, context1)
        assert zone == '6a'
        
        # From location_data dictionary
        context2 = {'location_data': {'climate_zone': '7b'}}
        zone = explanation_service._extract_climate_zone({}, context2)
        assert zone == '7b'
        
        # From recommendation_data
        recommendation = {'climate_zone': '5a'}
        zone = explanation_service._extract_climate_zone(recommendation, {})
        assert zone == '5a'
        
        # None when not available
        zone = explanation_service._extract_climate_zone({}, {})
        assert zone is None
    
    def test_explanation_generation_without_climate_zone(self, explanation_service):
        """Test that explanations work gracefully without climate zone data."""
        recommendation_data = {
            'crop_name': 'corn',
            'confidence_score': 0.75
        }
        context = {
            'soil_data': {'ph': 6.5}
        }
        
        explanation = explanation_service.generate_explanation(
            recommendation_type="crop_selection",
            recommendation_data=recommendation_data,
            context=context
        )
        
        # Should still generate explanation without climate info
        assert "corn is" in explanation
        assert "Climate zone information not available" in explanation
    
    def test_confidence_explanation_includes_climate_factors(self, explanation_service):
        """Test that confidence explanations can include climate-related factors."""
        confidence_factors = {
            'soil_data_quality': 0.8,
            'climate_data_availability': 0.6,  # Lower climate data quality
            'expert_validation': 0.9
        }
        
        explanation = explanation_service.generate_confidence_explanation(
            confidence_factors, overall_confidence=0.75
        )
        
        assert "moderate confidence" in explanation
        # Would include climate-related confidence factors if implemented
    
    @pytest.mark.parametrize("climate_zone,expected_timing", [
        ('3a', 'shorter growing season'),
        ('6a', 'moderate growing season'),
        ('8a', 'extended growing season'),
        ('10a', 'year-round growing'),
    ])
    def test_climate_timing_context_for_zones(self, explanation_service, climate_zone, expected_timing):
        """Test climate timing context for various zones."""
        context = explanation_service._get_climate_timing_context(climate_zone)
        assert expected_timing in context
        assert climate_zone in context


if __name__ == "__main__":
    pytest.main([__file__])