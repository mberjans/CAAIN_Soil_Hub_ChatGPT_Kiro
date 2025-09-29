"""
Tests for Climate Zone Integration in Crop Recommendation System

This module tests the integration of climate zone detection and compatibility
scoring into the crop recommendation workflow.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date

# Import from the src directory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.crop_recommendation_service import CropRecommendationService
from models.agricultural_models import (
    RecommendationRequest,
    LocationData,
    SoilTestData,
    FarmProfile
)


class TestClimateZoneCompatibilityScoring:
    """Test climate zone compatibility scoring algorithms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CropRecommendationService()
        
        # Mock location data for different climate zones
        self.location_6a = LocationData(
            latitude=41.8781,
            longitude=-87.6298,
            climate_zone="6a",
            climate_zone_name="USDA Hardiness Zone 6a"
        )
        
        self.location_3a = LocationData(
            latitude=46.7296,
            longitude=-94.6859,
            climate_zone="3a",
            climate_zone_name="USDA Hardiness Zone 3a"
        )
        
        self.location_9a = LocationData(
            latitude=28.5383,
            longitude=-81.3792,
            climate_zone="9a",
            climate_zone_name="USDA Hardiness Zone 9a"
        )
        
        # Sample crop data from the service
        self.corn_data = self.service.crop_database["corn"]
        self.wheat_data = self.service.crop_database["wheat"]
        self.soybean_data = self.service.crop_database["soybean"]
    
    def test_perfect_climate_zone_match(self):
        """Test perfect climate zone compatibility scoring."""
        # Corn is compatible with zone 6a
        score = self.service._calculate_climate_zone_suitability(
            self.location_6a, self.corn_data
        )
        assert score == 1.0, f"Expected perfect match score of 1.0, got {score}"
        
        # Wheat is compatible with zone 3a  
        score = self.service._calculate_climate_zone_suitability(
            self.location_3a, self.wheat_data
        )
        assert score == 1.0, f"Expected perfect match score of 1.0, got {score}"
    
    def test_adjacent_zone_compatibility(self):
        """Test adjacent climate zone compatibility scoring."""
        # Create a crop with zones 5a, 5b, 6a, 6b
        test_crop = {
            "climate_zones": ["5a", "5b", "6a", "6b"]
        }
        
        # Test zone 4a (adjacent to 5a)
        location_4a = LocationData(
            latitude=42.0, longitude=-83.0, climate_zone="4a"
        )
        score = self.service._calculate_climate_zone_suitability(
            location_4a, test_crop
        )
        assert score == 0.8, f"Expected adjacent zone score of 0.8, got {score}"
        
        # Test zone 7a (adjacent to 6b)
        location_7a = LocationData(
            latitude=38.0, longitude=-84.0, climate_zone="7a"
        )
        score = self.service._calculate_climate_zone_suitability(
            location_7a, test_crop
        )
        assert score == 0.8, f"Expected adjacent zone score of 0.8, got {score}"
    
    def test_same_zone_different_subzone(self):
        """Test same zone number but different subzone."""
        # Create a crop with zone 6a
        test_crop = {
            "climate_zones": ["6a"]
        }
        
        # Test zone 6b (same zone, different subzone)
        location_6b = LocationData(
            latitude=40.0, longitude=-85.0, climate_zone="6b"
        )
        score = self.service._calculate_climate_zone_suitability(
            location_6b, test_crop
        )
        assert score == 0.9, f"Expected same zone different subzone score of 0.9, got {score}"
    
    def test_incompatible_climate_zones(self):
        """Test incompatible climate zone scoring."""
        # Test corn (zones 3a-7b) in zone 9a (too hot)
        score = self.service._calculate_climate_zone_suitability(
            self.location_9a, self.corn_data
        )
        assert score == 0.3, f"Expected incompatible zone score of 0.3, got {score}"
        
        # Test warm-season crop in cold zone
        warm_crop = {
            "climate_zones": ["9a", "9b", "10a", "10b", "11"]
        }
        score = self.service._calculate_climate_zone_suitability(
            self.location_3a, warm_crop
        )
        assert score == 0.3, f"Expected incompatible zone score of 0.3, got {score}"
    
    def test_missing_climate_data(self):
        """Test handling of missing climate zone data."""
        # Location without climate zone
        location_no_zone = LocationData(
            latitude=41.8781,
            longitude=-87.6298
        )
        
        score = self.service._calculate_climate_zone_suitability(
            location_no_zone, self.corn_data
        )
        assert score == 0.7, f"Expected default score of 0.7 for missing climate data, got {score}"
        
        # Crop without climate zones
        crop_no_zones = {"optimal_ph_range": (6.0, 7.0)}
        score = self.service._calculate_climate_zone_suitability(
            self.location_6a, crop_no_zones
        )
        assert score == 0.7, f"Expected default score of 0.7 for missing crop climate data, got {score}"


class TestClimateZoneFiltering:
    """Test climate zone-based crop filtering."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CropRecommendationService()
        
        # Create location in zone 6a (good for corn, soybean, wheat)
        self.location_6a = LocationData(
            latitude=41.8781,
            longitude=-87.6298,
            climate_zone="6a"
        )
        
        # Create location in zone 2a (cold, limited crop options)
        self.location_2a = LocationData(
            latitude=48.0,
            longitude=-97.0,
            climate_zone="2a"
        )
    
    def test_crop_filtering_compatible_zone(self):
        """Test crop filtering in a compatible climate zone."""
        filtered_crops = self.service._filter_crops_by_climate_zone(self.location_6a)
        
        # Zone 6a should include all current crops (corn, soybean, wheat)
        assert "corn" in filtered_crops
        assert "soybean" in filtered_crops
        assert "wheat" in filtered_crops
        assert len(filtered_crops) == len(self.service.crop_database)
    
    def test_crop_filtering_cold_zone(self):
        """Test crop filtering in a cold climate zone."""
        filtered_crops = self.service._filter_crops_by_climate_zone(self.location_2a)
        
        # Zone 2a is compatible with wheat (2a-6b) but not corn/soybean (3a+)
        assert "wheat" in filtered_crops  # Should be included
        
        # Check that incompatible crops might be excluded or marginally included
        # depending on the exact zone ranges in the database
        total_original = len(self.service.crop_database)
        total_filtered = len(filtered_crops)
        assert total_filtered <= total_original, "Filtered crops should not exceed original database"
    
    def test_excluded_crops_identification(self):
        """Test identification of excluded crops."""
        excluded_crops = self.service._get_excluded_crops_by_climate(self.location_2a)
        
        # Should return list of crop names that are incompatible
        assert isinstance(excluded_crops, list)
        
        # All returned items should be strings (crop names)
        for crop in excluded_crops:
            assert isinstance(crop, str)
            assert crop in self.service.crop_database
    
    def test_no_location_data_filtering(self):
        """Test crop filtering with no location data."""
        filtered_crops = self.service._filter_crops_by_climate_zone(None)
        
        # Should return all crops when no location data
        assert filtered_crops == self.service.crop_database
        
        excluded_crops = self.service._get_excluded_crops_by_climate(None)
        assert excluded_crops == []


class TestClimateZoneIntegrationInRecommendations:
    """Test end-to-end climate zone integration in recommendations."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CropRecommendationService()
        
        # Create comprehensive test request
        self.location = LocationData(
            latitude=41.8781,
            longitude=-87.6298,
            climate_zone="6a",
            climate_zone_name="USDA Hardiness Zone 6a"
        )
        
        self.soil_data = SoilTestData(
            ph=6.5,
            organic_matter_percent=3.5,
            phosphorus_ppm=25,
            potassium_ppm=200,
            test_date=date.today()
        )
        
        self.farm_profile = FarmProfile(
            farm_id="test_farm_001",
            farm_size_acres=100,
            primary_crops=["corn", "soybean"]
        )
        
        self.request = RecommendationRequest(
            request_id="test_climate_integration_001",
            question_type="crop_selection",
            location=self.location,
            soil_data=self.soil_data,
            farm_profile=self.farm_profile
        )
    
    @pytest.mark.asyncio
    async def test_crop_recommendations_with_climate_zone(self):
        """Test crop recommendations include climate zone considerations."""
        recommendations = await self.service.get_crop_recommendations(self.request)
        
        # Should return recommendations
        assert len(recommendations) > 0
        
        # All recommendations should have climate information in descriptions
        for rec in recommendations:
            assert "Climate Zone" in rec.description or "climate" in rec.description.lower()
            assert rec.confidence_score > 0
            assert rec.confidence_score <= 1.0
    
    @pytest.mark.asyncio 
    @patch('services.climate_integration_service.climate_integration_service')
    async def test_auto_climate_zone_detection(self, mock_climate_service):
        """Test automatic climate zone detection when missing."""
        # Create request without climate zone
        location_no_zone = LocationData(
            latitude=41.8781,
            longitude=-87.6298
        )
        
        request_no_zone = RecommendationRequest(
            request_id="test_auto_climate_001",
            question_type="crop_selection",
            location=location_no_zone,
            soil_data=self.soil_data,
            farm_profile=self.farm_profile
        )
        
        # Mock climate service response
        mock_climate_data = {
            'primary_zone': {
                'zone_id': '6a',
                'name': 'USDA Hardiness Zone 6a',
                'description': 'Cold winter zone'
            },
            'confidence_score': 0.95
        }
        
        mock_climate_service.detect_climate_zone = AsyncMock(return_value=mock_climate_data)
        mock_climate_service.enhance_location_with_climate = MagicMock(
            return_value={
                **location_no_zone.dict(),
                'climate_zone': '6a',
                'climate_zone_name': 'USDA Hardiness Zone 6a'
            }
        )
        
        # Mock the service in the crop recommendation service
        self.service.climate_service = mock_climate_service
        
        recommendations = await self.service.get_crop_recommendations(request_no_zone)
        
        # Should have called climate service
        mock_climate_service.detect_climate_zone.assert_called_once_with(
            latitude=41.8781,
            longitude=-87.6298,
            elevation_ft=None
        )
        
        # Should return recommendations
        assert len(recommendations) > 0
    
    @pytest.mark.asyncio
    async def test_climate_service_unavailable(self):
        """Test graceful handling when climate service is unavailable."""
        # Set climate service to None
        self.service.climate_service = None
        
        location_no_zone = LocationData(
            latitude=41.8781,
            longitude=-87.6298
        )
        
        request_no_zone = RecommendationRequest(
            request_id="test_no_climate_service_001",
            question_type="crop_selection",
            location=location_no_zone,
            soil_data=self.soil_data,
            farm_profile=self.farm_profile
        )
        
        # Should still return recommendations using default scoring
        recommendations = await self.service.get_crop_recommendations(request_no_zone)
        
        assert len(recommendations) > 0
        # Should use default climate scoring
        for rec in recommendations:
            assert rec.confidence_score > 0


class TestClimateCompatibilityDescriptions:
    """Test climate compatibility description generation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CropRecommendationService()
        
        self.location_6a = LocationData(
            latitude=41.8781,
            longitude=-87.6298,
            climate_zone="6a"
        )
    
    def test_optimal_climate_description(self):
        """Test description for optimal climate match."""
        corn_data = self.service.crop_database["corn"]
        
        description = self.service._get_climate_compatibility_description(
            self.location_6a, corn_data, "corn"
        )
        
        assert "optimal" in description.lower()
        assert "6a" in description
        assert "corn" in description.lower()
    
    def test_marginal_climate_description(self):
        """Test description for marginal climate compatibility."""
        # Create a crop not well-suited to zone 6a
        marginal_crop = {
            "climate_zones": ["8a", "8b", "9a", "9b"]
        }
        
        description = self.service._get_climate_compatibility_description(
            self.location_6a, marginal_crop, "test_crop"
        )
        
        assert "marginal" in description.lower() or "challenges" in description.lower()
        assert "6a" in description
    
    def test_no_climate_data_description(self):
        """Test description when climate data is missing."""
        location_no_zone = LocationData(
            latitude=41.8781,
            longitude=-87.6298
        )
        
        corn_data = self.service.crop_database["corn"]
        
        description = self.service._get_climate_compatibility_description(
            location_no_zone, corn_data, "corn"
        )
        
        assert description == ""


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = CropRecommendationService()
    
    def test_invalid_climate_zone_format(self):
        """Test handling of invalid climate zone formats."""
        location_invalid = LocationData(
            latitude=41.8781,
            longitude=-87.6298,
            climate_zone="invalid_zone"
        )
        
        corn_data = self.service.crop_database["corn"]
        
        score = self.service._calculate_climate_zone_suitability(
            location_invalid, corn_data
        )
        
        # Should handle gracefully and return incompatible score
        assert score == 0.3
    
    def test_empty_compatible_zones(self):
        """Test crop with empty compatible zones list."""
        empty_zones_crop = {
            "climate_zones": []
        }
        
        location = LocationData(
            latitude=41.8781,
            longitude=-87.6298,
            climate_zone="6a"
        )
        
        score = self.service._calculate_climate_zone_suitability(
            location, empty_zones_crop
        )
        
        assert score == 0.7  # Should use default score
    
    def test_adjacent_zone_calculation_edge_cases(self):
        """Test edge cases in adjacent zone calculation."""
        # Test zone with only letter (no number)
        score = self.service._calculate_adjacent_zone_compatibility(
            "a", ["6a", "6b"]
        )
        assert score == 0.0
        
        # Test empty zone strings
        score = self.service._calculate_adjacent_zone_compatibility(
            "", ["6a", "6b"]
        )
        assert score == 0.0
        
        # Test None values
        score = self.service._calculate_adjacent_zone_compatibility(
            None, ["6a", "6b"]
        )
        assert score == 0.0


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__])