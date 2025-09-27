"""
Unit tests for the extended crop filtering attributes model.

This test file verifies that the CropFilteringAttributes model has been correctly
extended with the required filtering attributes for TICKET-005_crop-type-filtering-1.2.
"""

import pytest
from uuid import UUID, uuid4
from datetime import datetime

from src.models.crop_filtering_models import (
    CropFilteringAttributes,
    ManagementComplexity,
    InputRequirements,
    LaborRequirements,
    CarbonSequestrationPotential,
    BiodiversitySupport,
    PollinatorValue,
    WaterUseEfficiency,
    MarketStability
)


class TestCropFilteringAttributesExtension:
    """Test the extended crop filtering attributes model."""

    def test_basic_model_creation_with_extended_attributes(self):
        """Test that the model can be created with all extended attributes."""
        crop_id = uuid4()
        
        # Create a model instance with all required extended attributes
        filtering_attrs = CropFilteringAttributes(
            crop_id=crop_id,
            pest_resistance_traits={
                "corn_borer": {"level": "high", "genes": ["Bt1", "Bt2"]},
                "aphids": {"level": "moderate"},
                "rootworm": {"level": "low", "notes": "Susceptible in some regions"}
            },
            market_class_filters={
                "organic": True,
                "non_gmo": True,
                "heirloom": False,
                "specialty": {"type": "quality", "premium": 1.2}
            },
            certification_filters={
                "usda_organic": {
                    "certified": True,
                    "expiration": "2025-12-31",
                    "certificate_number": "ORG-12345"
                },
                "non_gmo_project": {
                    "certified": True,
                    "expiration": "2024-06-30"
                }
            },
            seed_availability_filters={
                "status": "available",
                "regions": ["Midwest", "Great Plains"],
                "suppliers": ["SeedCo", "AgriSupply"],
                "seasonal_availability": {
                    "spring": "available",
                    "fall": "limited"
                }
            }
        )

        # Verify the instance was created correctly
        assert filtering_attrs.crop_id == crop_id
        assert "pest_resistance_traits" in filtering_attrs.__fields__
        assert "market_class_filters" in filtering_attrs.__fields__
        assert "certification_filters" in filtering_attrs.__fields__
        assert "seed_availability_filters" in filtering_attrs.__fields__

        # Verify the extended attributes have the expected data
        assert filtering_attrs.pest_resistance_traits["corn_borer"]["level"] == "high"
        assert filtering_attrs.market_class_filters["organic"] is True
        assert filtering_attrs.certification_filters["usda_organic"]["certified"] is True
        assert "Midwest" in filtering_attrs.seed_availability_filters["regions"]

    def test_backwards_compatibility_with_legacy_fields(self):
        """Test that the extended model maintains backwards compatibility."""
        crop_id = uuid4()
        
        # Create a model with traditional fields to ensure backwards compatibility
        filtering_attrs = CropFilteringAttributes(
            crop_id=crop_id,
            management_complexity=ManagementComplexity.MODERATE,
            input_requirements=InputRequirements.MODERATE,
            labor_requirements=LaborRequirements.LOW,
            carbon_sequestration_potential=CarbonSequestrationPotential.MODERATE,
            biodiversity_support=BiodiversitySupport.HIGH,
            pollinator_value=PollinatorValue.MODERATE,
            water_use_efficiency=WaterUseEfficiency.GOOD,
            market_stability=MarketStability.STABLE,
            planting_season=["spring", "fall"],
            growing_season=["summer"],
            harvest_season=["fall"],
            farming_systems=["conventional", "organic"],
            precision_ag_compatible=True,
            cover_crop_compatible=True,
            price_premium_potential=True,
            value_added_opportunities=["food_processing", "direct_marketing"]
        )

        # Verify backwards compatibility
        assert filtering_attrs.management_complexity == ManagementComplexity.MODERATE
        assert filtering_attrs.input_requirements == InputRequirements.MODERATE
        assert filtering_attrs.labor_requirements == LaborRequirements.LOW
        assert filtering_attrs.carbon_sequestration_potential == CarbonSequestrationPotential.MODERATE
        assert filtering_attrs.market_stability == MarketStability.STABLE
        assert "spring" in filtering_attrs.planting_season
        assert filtering_attrs.precision_ag_compatible is True
        assert len(filtering_attrs.value_added_opportunities) == 2

    def test_extended_attributes_are_optional(self):
        """Test that the newly added extended attributes are optional."""
        crop_id = uuid4()
        
        # Create a model without the extended attributes (should still work)
        filtering_attrs = CropFilteringAttributes(crop_id=crop_id)
        
        # Verify the extended attributes default to empty dicts
        assert filtering_attrs.pest_resistance_traits == {}
        assert filtering_attrs.market_class_filters == {}
        assert filtering_attrs.certification_filters == {}
        assert filtering_attrs.seed_availability_filters == {}

    def test_all_extended_attributes_can_be_populated(self):
        """Test that all extended attributes can be populated with complex data."""
        crop_id = uuid4()
        
        # Create complex data for all extended attributes
        filtering_attrs = CropFilteringAttributes(
            crop_id=crop_id,
            pest_resistance_traits={
                "insects": {
                    "corn_borer": {"level": "high", "genes": ["Bt1", "Bt2"]},
                    "aphids": {"level": "moderate", "effectiveness": 0.75},
                    "cutworms": {"level": "low", "management_required": True}
                },
                "diseases": {
                    "northern_leaf_blight": {"level": "resistant", "notes": "Moderate resistance"},
                    "gray_leaf_spot": {"level": "susceptible", "management_required": True}
                }
            },
            market_class_filters={
                "specialty_markets": {
                    "organic": {
                        "certified": True,
                        "market_premium": 1.3,
                        "target_audience": "health_conscious_consumers"
                    },
                    "non_gmo": {
                        "certified": True,
                        "market_premium": 1.15,
                        "target_audience": "traditional_markets"
                    },
                    "heirloom": {
                        "available": True,
                        "market_premium": 1.25,
                        "target_audience": "niche_markets"
                    }
                },
                "export_markets": ["Asia", "Europe"],
                "local_markets": ["farmers_markets", "csa"],
                "direct_sales": True
            },
            certification_filters={
                "organic": {
                    "usda_organic": {
                        "certified": True,
                        "certificate_number": "ORG-12345",
                        "expiration_date": "2025-12-31",
                        "issuing_body": "USDA"
                    }
                },
                "non_gmo": {
                    "non_gmo_project": {
                        "certified": True,
                        "certificate_number": "NONGMO-67890",
                        "expiration_date": "2024-06-30",
                        "issuing_body": "Non-GMO Project"
                    }
                },
                "fair_trade": {
                    "certified": False,
                    "notes": "Not pursued due to cost/benefit analysis"
                }
            },
            seed_availability_filters={
                "varieties": {
                    "hybrid_variety_1": {
                        "availability_status": "available",
                        "source_type": "commercial",
                        "treatment": "fungicidal",
                        "germination_rate": 0.95,
                        "purity_percentage": 99.5,
                        "regional_availability": {
                            "midwest": "available",
                            "great_plains": "limited",
                            "northeast": "seasonal"
                        },
                        "suppliers": ["SeedCo", "AgriSupply", "FarmersCooperative"]
                    },
                    "open_pollinated_variety": {
                        "availability_status": "available",
                        "source_type": "heirloom",
                        "treatment": "none",
                        "germination_rate": 0.85,
                        "purity_percentage": 95.0,
                        "regional_availability": {
                            "general": "available"
                        },
                        "suppliers": ["HeritageSeeds", "FarmSaved"]
                    }
                },
                "overall_availability_score": 0.9,
                "regional_supply_distributions": {
                    "midwest": 0.6,
                    "great_plains": 0.25,
                    "northeast": 0.15
                },
                "supplier_diversity_score": 0.75
            }
        )

        # Verify all complex data was correctly stored
        assert len(filtering_attrs.pest_resistance_traits["insects"]) == 3
        assert filtering_attrs.market_class_filters["specialty_markets"]["organic"]["market_premium"] == 1.3
        assert filtering_attrs.certification_filters["organic"]["usda_organic"]["certified"] is True
        assert filtering_attrs.seed_availability_filters["varieties"]["hybrid_variety_1"]["germination_rate"] == 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])