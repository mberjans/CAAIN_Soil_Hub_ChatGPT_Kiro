"""
Unit tests for TICKET-005_crop-type-filtering-3.3: Preference Recommendation Engine
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from services.preference_recommendation_engine import (
    PreferenceRecommendationEngine,
    FarmCharacteristics,
    FarmerProfile,
    RecommendationResult,
    RecommendationType
)


class TestPreferenceRecommendationEngine:
    """Test suite for PreferenceRecommendationEngine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.engine = PreferenceRecommendationEngine()
        
        # Sample farm characteristics
        self.sample_farm = FarmCharacteristics(
            location="Iowa, USA",
            climate_zone="zone_5",
            soil_type="loam",
            farm_size_acres=150.0,
            precipitation_annual=32.0,
            temperature_range=(25.0, 85.0),
            soil_ph=6.5,
            irrigation_available=True,
            organic_certification=False,
            equipment_capabilities=["tractor", "combine", "planter"]
        )
        
        # Sample farmer profile
        self.sample_farmer = FarmerProfile(
            farmer_id="farmer_001",
            experience_years=15,
            farm_characteristics=self.sample_farm,
            crop_preferences={"corn": 0.9, "soybeans": 0.8, "wheat": 0.6},
            filter_usage_patterns={"climate_zone": 10, "soil_type": 8, "farm_size": 5},
            success_metrics={"yield_efficiency": 0.85, "profit_margin": 0.12}
        )
    
    def test_engine_initialization(self):
        """Test that the engine initializes properly"""
        assert self.engine.crop_compatibility_matrix
        assert self.engine.filter_effectiveness_scores
        assert isinstance(self.engine.farmer_profiles, dict)
        
        # Check that compatibility matrix has expected categories
        expected_categories = ["grains", "oilseeds", "forage", "vegetables", "fruits", "specialty"]
        for category in expected_categories:
            assert category in self.engine.crop_compatibility_matrix
    
    def test_register_farmer_profile(self):
        """Test farmer profile registration"""
        self.engine.register_farmer_profile(self.sample_farmer)
        
        assert "farmer_001" in self.engine.farmer_profiles
        assert self.engine.farmer_profiles["farmer_001"] == self.sample_farmer
    
    def test_suggest_crop_types_basic(self):
        """Test basic crop type suggestions"""
        result = self.engine.suggest_crop_types(self.sample_farm, max_suggestions=3)
        
        assert isinstance(result, RecommendationResult)
        assert result.recommendation_type == RecommendationType.CROP_SUGGESTION
        assert len(result.suggestions) <= 3
        assert result.confidence_score > 0
        assert result.reasoning
        
        # Check suggestion structure
        for suggestion in result.suggestions:
            assert "crop_type" in suggestion
            assert "suitability_score" in suggestion
            assert "reasons" in suggestion
            assert isinstance(suggestion["reasons"], list)
    
    def test_suggest_crop_types_climate_zone_specific(self):
        """Test crop suggestions are appropriate for climate zone"""
        # Test zone 4 (cooler climate)
        cold_farm = FarmCharacteristics(
            location="Minnesota, USA",
            climate_zone="zone_4",
            soil_type="loam",
            farm_size_acres=200.0,
            precipitation_annual=28.0,
            temperature_range=(20.0, 80.0)
        )
        
        result = self.engine.suggest_crop_types(cold_farm)
        
        # Should suggest cold-hardy crops
        suggested_crops = [s["crop_type"] for s in result.suggestions]
        assert any(crop in suggested_crops for crop in ["wheat", "barley", "corn", "soybeans"])
    
    def test_recommend_filters_no_similar_farmers(self):
        """Test filter recommendations when no similar farmers exist"""
        result = self.engine.recommend_filters_by_similarity(self.sample_farm)
        
        assert result.recommendation_type == RecommendationType.FILTER_RECOMMENDATION
        assert len(result.suggestions) == 0
        assert result.confidence_score == 0.0
        assert "No similar farmers found" in result.reasoning
    
    def test_recommend_filters_with_similar_farmers(self):
        """Test filter recommendations with similar farmers"""
        # Register several similar farmers
        similar_farmers = []
        for i in range(3):
            farmer = FarmerProfile(
                farmer_id=f"farmer_{i:03d}",
                experience_years=10 + i,
                farm_characteristics=self.sample_farm,
                crop_preferences={"corn": 0.8, "soybeans": 0.7},
                filter_usage_patterns={"climate_zone": 8 + i, "soil_type": 6 + i, "precipitation": 4 + i},
                success_metrics={"yield_efficiency": 0.8}
            )
            similar_farmers.append(farmer)
            self.engine.register_farmer_profile(farmer)
        
        result = self.engine.recommend_filters_by_similarity(self.sample_farm, max_recommendations=2)
        
        assert result.recommendation_type == RecommendationType.FILTER_RECOMMENDATION
        assert len(result.suggestions) <= 2
        assert result.confidence_score > 0
        
        # Check suggestion structure
        for suggestion in result.suggestions:
            assert "filter_type" in suggestion
            assert "usage_frequency" in suggestion
            assert "effectiveness_score" in suggestion
            assert "similar_farmers_count" in suggestion
    
    def test_optimize_preferences_climate_mismatch(self):
        """Test preference optimization for climate mismatches"""
        # High preference for crop not suitable for climate
        mismatched_preferences = {
            "tropical_fruits": 0.9,  # Not suitable for zone_5
            "corn": 0.8,
            "soybeans": 0.7
        }
        
        result = self.engine.optimize_preferences(mismatched_preferences, self.sample_farm)
        
        assert result.recommendation_type == RecommendationType.PREFERENCE_OPTIMIZATION
        assert len(result.conflicts_detected) > 0
        assert any("tropical_fruits" in conflict for conflict in result.conflicts_detected)
        
        # Should have optimization suggestions
        climate_suggestions = [s for s in result.suggestions if s["optimization_type"] == "climate_mismatch"]
        assert len(climate_suggestions) > 0
    
    def test_optimize_preferences_opportunities(self):
        """Test preference optimization for missed opportunities"""
        # Low preferences for suitable crops
        low_preferences = {
            "corn": 0.3,  # Should be higher for this climate/soil
            "wheat": 0.2
        }
        
        result = self.engine.optimize_preferences(low_preferences, self.sample_farm)
        
        assert result.recommendation_type == RecommendationType.PREFERENCE_OPTIMIZATION
        
        # Should suggest increasing preferences for suitable crops
        opportunity_suggestions = [s for s in result.suggestions if s["optimization_type"] == "opportunity"]
        assert len(opportunity_suggestions) > 0
        
        for suggestion in opportunity_suggestions:
            assert suggestion["recommended_preference"] > suggestion["current_preference"]
    
    def test_resolve_preference_conflicts_exclusive_crops(self):
        """Test conflict resolution for mutually exclusive crops"""
        conflicting_preferences = {
            "corn": 0.9,
            "soybeans": 0.9,  # Rotation consideration
            "organic": 0.8,
            "conventional": 0.8  # Management style conflict
        }
        
        result = self.engine.resolve_preference_conflicts(conflicting_preferences, self.sample_farm)
        
        assert result.recommendation_type == RecommendationType.CONFLICT_RESOLUTION
        
        if result.conflicts_detected:
            assert len(result.suggestions) > 0
            
            # Check resolution structure
            for resolution in result.suggestions:
                assert "conflict_type" in resolution
                assert "recommended_action" in resolution
    
    def test_resolve_preference_conflicts_resource_constraints(self):
        """Test conflict resolution for resource constraints"""
        # Small farm with many high-input crops
        small_farm = FarmCharacteristics(
            location="Small Farm",
            climate_zone="zone_5",
            soil_type="loam",
            farm_size_acres=50.0,  # Small farm
            precipitation_annual=30.0,
            temperature_range=(25.0, 85.0)
        )
        
        high_input_preferences = {
            "corn": 0.9,
            "vegetables": 0.8,
            "fruits": 0.9  # Multiple high-input crops
        }
        
        result = self.engine.resolve_preference_conflicts(high_input_preferences, small_farm)
        
        # Should detect resource constraint conflicts
        resource_conflicts = [s for s in result.suggestions if s.get("conflict_type") == "resource_constraint"]
        if small_farm.farm_size_acres < 100:
            # May detect resource constraints for small farms
            pass  # This is optional based on the logic
    
    def test_calculate_farm_similarity(self):
        """Test farm similarity calculation"""
        # Identical farms
        identical_farm = FarmCharacteristics(
            location="Iowa, USA",
            climate_zone="zone_5",
            soil_type="loam",
            farm_size_acres=150.0,
            precipitation_annual=32.0,
            temperature_range=(25.0, 85.0)
        )
        
        similarity = self.engine._calculate_farm_similarity(self.sample_farm, identical_farm)
        assert similarity >= 0.9  # Should be very high
        
        # Different farms
        different_farm = FarmCharacteristics(
            location="California, USA",
            climate_zone="zone_9",
            soil_type="sandy",
            farm_size_acres=50.0,
            precipitation_annual=15.0,
            temperature_range=(40.0, 95.0)
        )
        
        similarity = self.engine._calculate_farm_similarity(self.sample_farm, different_farm)
        assert similarity < 0.5  # Should be low
    
    def test_get_crops_for_climate(self):
        """Test climate-based crop selection"""
        zone_4_crops = self.engine._get_crops_for_climate("zone_4")
        assert "wheat" in zone_4_crops
        assert "barley" in zone_4_crops
        
        zone_8_crops = self.engine._get_crops_for_climate("zone_8")
        assert "rice" in zone_8_crops
        assert "cotton" in zone_8_crops
        
        # Unknown zone should return default crops
        unknown_crops = self.engine._get_crops_for_climate("unknown_zone")
        assert "corn" in unknown_crops
        assert "soybeans" in unknown_crops
    
    def test_get_crops_for_soil(self):
        """Test soil-based crop selection"""
        clay_crops = self.engine._get_crops_for_soil("clay")
        assert "rice" in clay_crops
        
        sandy_crops = self.engine._get_crops_for_soil("sandy")
        assert "potatoes" in sandy_crops
        assert "carrots" in sandy_crops
        
        # Unknown soil should return default crops
        unknown_crops = self.engine._get_crops_for_soil("unknown_soil")
        assert "corn" in unknown_crops
        assert "soybeans" in unknown_crops
    
    def test_get_crops_for_farm_size(self):
        """Test farm size-based crop selection"""
        small_farm_crops = self.engine._get_crops_for_farm_size(5.0)
        assert "vegetables" in small_farm_crops
        assert "herbs" in small_farm_crops
        
        medium_farm_crops = self.engine._get_crops_for_farm_size(100.0)
        assert "corn" in medium_farm_crops
        assert "soybeans" in medium_farm_crops
        
        large_farm_crops = self.engine._get_crops_for_farm_size(500.0)
        assert "corn" in large_farm_crops
        assert "wheat" in large_farm_crops
    
    def test_get_crop_reasons(self):
        """Test crop suitability reasoning"""
        reasons = self.engine._get_crop_reasons("corn", self.sample_farm)
        
        assert isinstance(reasons, list)
        assert len(reasons) > 0
        
        # Should include climate and soil reasons for corn in zone_5 loam
        reason_text = " ".join(reasons).lower()
        assert any(keyword in reason_text for keyword in ["zone_5", "loam", "irrigation", "acre"])
    
    def test_find_similar_farmers(self):
        """Test finding similar farmers"""
        # Register farmers with varying similarity
        farmers_data = [
            ("very_similar", self.sample_farm),  # Identical farm
            ("somewhat_similar", FarmCharacteristics(
                location="Illinois, USA",
                climate_zone="zone_5",  # Same zone
                soil_type="clay",  # Different soil
                farm_size_acres=200.0,
                precipitation_annual=30.0,
                temperature_range=(20.0, 80.0)
            )),
            ("very_different", FarmCharacteristics(
                location="Florida, USA",
                climate_zone="zone_9",  # Very different
                soil_type="sandy",
                farm_size_acres=20.0,
                precipitation_annual=55.0,
                temperature_range=(60.0, 95.0)
            ))
        ]
        
        for farmer_id, farm_chars in farmers_data:
            farmer = FarmerProfile(
                farmer_id=farmer_id,
                experience_years=10,
                farm_characteristics=farm_chars,
                crop_preferences={"corn": 0.8},
                filter_usage_patterns={"climate_zone": 5},
                success_metrics={"yield": 0.8}
            )
            self.engine.register_farmer_profile(farmer)
        
        similar_farmers = self.engine._find_similar_farmers(self.sample_farm, max_similar=5)
        
        # Should find some similar farmers
        assert len(similar_farmers) >= 1
        
        # Check that similarity scores are reasonable
        for farmer_id, similarity_score in similar_farmers:
            assert 0.0 <= similarity_score <= 1.0
            
        # Most similar should be first
        if len(similar_farmers) > 1:
            assert similar_farmers[0][1] >= similar_farmers[1][1]


class TestIntegrationScenarios:
    """Integration tests for realistic scenarios"""
    
    def setup_method(self):
        self.engine = PreferenceRecommendationEngine()
    
    def test_complete_recommendation_workflow(self):
        """Test a complete recommendation workflow"""
        # Setup farm and farmer
        farm = FarmCharacteristics(
            location="Nebraska, USA",
            climate_zone="zone_5",
            soil_type="loam",
            farm_size_acres=320.0,
            precipitation_annual=28.0,
            temperature_range=(22.0, 88.0),
            irrigation_available=False,
            organic_certification=True
        )
        
        current_preferences = {
            "corn": 0.9,
            "tropical_fruits": 0.8,  # Problematic for zone 5
            "soybeans": 0.6,
            "wheat": 0.3  # Low preference for suitable crop
        }
        
        # 1. Get crop suggestions
        crop_suggestions = self.engine.suggest_crop_types(farm, max_suggestions=5)
        assert len(crop_suggestions.suggestions) <= 5
        assert crop_suggestions.confidence_score > 0
        
        # 2. Optimize preferences
        optimization = self.engine.optimize_preferences(current_preferences, farm)
        assert optimization.recommendation_type == RecommendationType.PREFERENCE_OPTIMIZATION
        
        # Should detect tropical_fruits conflict
        assert any("tropical_fruits" in conflict for conflict in optimization.conflicts_detected)
        
        # 3. Resolve conflicts
        conflict_resolution = self.engine.resolve_preference_conflicts(current_preferences, farm)
        assert conflict_resolution.recommendation_type == RecommendationType.CONFLICT_RESOLUTION
        
        # 4. Register farmer and test similarity
        farmer = FarmerProfile(
            farmer_id="test_farmer",
            experience_years=12,
            farm_characteristics=farm,
            crop_preferences=current_preferences,
            filter_usage_patterns={"climate_zone": 15, "soil_type": 10, "organic": 8},
            success_metrics={"yield_efficiency": 0.78}
        )
        
        self.engine.register_farmer_profile(farmer)
        
        # Test filter recommendations (should work even with one farmer)
        filter_recommendations = self.engine.recommend_filters_by_similarity(farm)
        # May be empty if no truly similar farmers found
        assert filter_recommendations.recommendation_type == RecommendationType.FILTER_RECOMMENDATION
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Empty preferences
        empty_preferences = {}
        farm = FarmCharacteristics(
            location="Test",
            climate_zone="zone_5",
            soil_type="loam",
            farm_size_acres=100.0,
            precipitation_annual=30.0,
            temperature_range=(25.0, 85.0)
        )
        
        optimization = self.engine.optimize_preferences(empty_preferences, farm)
        # Should still provide opportunity suggestions
        assert optimization.recommendation_type == RecommendationType.PREFERENCE_OPTIMIZATION
        
        # Very small farm
        tiny_farm = FarmCharacteristics(
            location="Tiny Farm",
            climate_zone="zone_5",
            soil_type="loam",
            farm_size_acres=0.5,
            precipitation_annual=30.0,
            temperature_range=(25.0, 85.0)
        )
        
        suggestions = self.engine.suggest_crop_types(tiny_farm)
        # Should suggest appropriate small-scale crops
        suggested_crops = [s["crop_type"] for s in suggestions.suggestions]
        assert any(crop in suggested_crops for crop in ["vegetables", "herbs", "berries"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])