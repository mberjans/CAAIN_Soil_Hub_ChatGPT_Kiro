"""
Comprehensive tests for fertilizer database service.
Tests CRUD operations, classification methods, search, and agricultural validation.
"""

import pytest
from uuid import uuid4
from datetime import datetime

from ..models.fertilizer_database_models import (
    FertilizerProduct, FertilizerProductCreate, FertilizerProductUpdate,
    FertilizerTypeEnum, NutrientReleasePattern, CompatibilityLevel,
    FertilizerSearchFilters, ClassificationType
)
from ..services.fertilizer_database_service import FertilizerDatabaseService
from ..data.fertilizer_seed_data import get_fertilizer_seed_data


class TestFertilizerDatabaseService:
    """Test suite for FertilizerDatabaseService."""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test."""
        return FertilizerDatabaseService()

    @pytest.fixture
    def sample_urea(self, service):
        """Create a sample urea fertilizer product."""
        import asyncio
        urea_data = FertilizerProductCreate(
            product_name="Test Urea 46-0-0",
            manufacturer="Test Manufacturer",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
            nitrogen_percent=46.0,
            phosphorus_percent=0.0,
            potassium_percent=0.0,
            physical_form="granular",
            application_methods=["broadcast", "banded"],
            recommended_crops=["corn", "wheat"],
            release_pattern=NutrientReleasePattern.IMMEDIATE
        )
        return asyncio.run(service.create_fertilizer(urea_data))

    @pytest.fixture
    def sample_dap(self, service):
        """Create a sample DAP fertilizer product."""
        import asyncio
        dap_data = FertilizerProductCreate(
            product_name="Test DAP 18-46-0",
            manufacturer="Test Manufacturer",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
            nitrogen_percent=18.0,
            phosphorus_percent=46.0,
            potassium_percent=0.0,
            physical_form="granular",
            application_methods=["broadcast", "banded"],
            recommended_crops=["corn", "soybeans"],
            release_pattern=NutrientReleasePattern.IMMEDIATE
        )
        return asyncio.run(service.create_fertilizer(dap_data))

    @pytest.fixture
    def sample_organic(self, service):
        """Create a sample organic fertilizer product."""
        import asyncio
        organic_data = FertilizerProductCreate(
            product_name="Test Composted Manure 2-1-2",
            manufacturer="Organic Farms",
            fertilizer_type=FertilizerTypeEnum.ORGANIC_SOLID,
            nitrogen_percent=2.0,
            phosphorus_percent=1.0,
            potassium_percent=2.0,
            physical_form="pellet",
            organic_certified=True,
            application_methods=["broadcast"],
            recommended_crops=["vegetables", "fruits"],
            release_pattern=NutrientReleasePattern.SLOW_RELEASE_60_DAYS,
            sustainability_rating=9.0
        )
        return asyncio.run(service.create_fertilizer(organic_data))

    # ==================== CRUD Operation Tests ====================

    @pytest.mark.asyncio
    async def test_create_fertilizer(self, service):
        """Test creating a new fertilizer product."""
        fertilizer_data = FertilizerProductCreate(
            product_name="Create Test 10-10-10",
            manufacturer="Test Corp",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
            nitrogen_percent=10.0,
            phosphorus_percent=10.0,
            potassium_percent=10.0
        )

        product = await service.create_fertilizer(fertilizer_data)

        assert product is not None
        assert product.product_id is not None
        assert product.product_name == "Create Test 10-10-10"
        assert product.nitrogen_percent == 10.0
        assert product.phosphorus_percent == 10.0
        assert product.potassium_percent == 10.0
        assert product.fertilizer_type == FertilizerTypeEnum.SYNTHETIC_GRANULAR
        assert product.is_active is True

    @pytest.mark.asyncio
    async def test_get_fertilizer(self, service, sample_urea):
        """Test retrieving a fertilizer product by ID."""
        product = await service.get_fertilizer(sample_urea.product_id)

        assert product is not None
        assert product.product_id == sample_urea.product_id
        assert product.product_name == sample_urea.product_name
        assert product.nitrogen_percent == 46.0

    @pytest.mark.asyncio
    async def test_get_fertilizer_by_name(self, service, sample_urea):
        """Test retrieving a fertilizer product by name."""
        product = await service.get_fertilizer_by_name("Test Urea 46-0-0")

        assert product is not None
        assert product.product_name == "Test Urea 46-0-0"
        assert product.nitrogen_percent == 46.0

    @pytest.mark.asyncio
    async def test_get_nonexistent_fertilizer(self, service):
        """Test retrieving a non-existent fertilizer."""
        product = await service.get_fertilizer(uuid4())
        assert product is None

    @pytest.mark.asyncio
    async def test_update_fertilizer(self, service, sample_urea):
        """Test updating a fertilizer product."""
        update_data = FertilizerProductUpdate(
            manufacturer="Updated Manufacturer",
            average_cost_per_unit=500.0,
            sustainability_rating=7.5
        )

        updated = await service.update_fertilizer(sample_urea.product_id, update_data)

        assert updated is not None
        assert updated.manufacturer == "Updated Manufacturer"
        assert updated.average_cost_per_unit == 500.0
        assert updated.sustainability_rating == 7.5
        # Unchanged fields should remain the same
        assert updated.nitrogen_percent == 46.0

    @pytest.mark.asyncio
    async def test_delete_fertilizer(self, service, sample_urea):
        """Test deleting (soft delete) a fertilizer product."""
        result = await service.delete_fertilizer(sample_urea.product_id)
        assert result is True

        # Product should still exist but be inactive
        product = await service.get_fertilizer(sample_urea.product_id)
        assert product is not None
        assert product.is_active is False

    @pytest.mark.asyncio
    async def test_get_all_fertilizers(self, service, sample_urea, sample_dap):
        """Test retrieving all fertilizer products."""
        products = await service.get_all_fertilizers(is_active=True, limit=100)

        assert len(products) >= 2
        product_names = []
        for p in products:
            product_names.append(p.product_name)

        assert "Test Urea 46-0-0" in product_names
        assert "Test DAP 18-46-0" in product_names

    # ==================== Search and Filter Tests ====================

    @pytest.mark.asyncio
    async def test_search_by_fertilizer_type(self, service, sample_urea, sample_organic):
        """Test searching by fertilizer type."""
        filters = FertilizerSearchFilters(
            fertilizer_types=[FertilizerTypeEnum.SYNTHETIC_GRANULAR]
        )

        response = await service.search_fertilizers(filters)

        assert response.total_count >= 1
        for product in response.products:
            assert product.fertilizer_type == FertilizerTypeEnum.SYNTHETIC_GRANULAR

    @pytest.mark.asyncio
    async def test_search_by_nitrogen_range(self, service, sample_urea, sample_dap):
        """Test searching by nitrogen content range."""
        filters = FertilizerSearchFilters(
            min_nitrogen=40.0,
            max_nitrogen=50.0
        )

        response = await service.search_fertilizers(filters)

        assert response.total_count >= 1
        for product in response.products:
            assert 40.0 <= product.nitrogen_percent <= 50.0

    @pytest.mark.asyncio
    async def test_search_by_organic_certified(self, service, sample_organic):
        """Test searching for organic certified products."""
        filters = FertilizerSearchFilters(organic_only=True)

        response = await service.search_fertilizers(filters)

        assert response.total_count >= 1
        for product in response.products:
            assert product.organic_certified is True

    @pytest.mark.asyncio
    async def test_search_by_crop(self, service, sample_urea):
        """Test searching by recommended crop."""
        filters = FertilizerSearchFilters(crop_type="corn")

        response = await service.search_fertilizers(filters)

        assert response.total_count >= 1
        for product in response.products:
            assert "corn" in [crop.lower() for crop in product.recommended_crops]

    @pytest.mark.asyncio
    async def test_search_with_pagination(self, service):
        """Test search pagination."""
        # Create multiple products
        for i in range(5):
            fertilizer_data = FertilizerProductCreate(
                product_name=f"Pagination Test {i}",
                manufacturer="Test",
                fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
                nitrogen_percent=10.0 + i
            )
            await service.create_fertilizer(fertilizer_data)

        # Test pagination
        filters = FertilizerSearchFilters(limit=2, offset=0)
        page1 = await service.search_fertilizers(filters)

        filters.offset = 2
        page2 = await service.search_fertilizers(filters)

        assert len(page1.products) <= 2
        assert len(page2.products) <= 2
        # Products should be different
        if len(page1.products) > 0 and len(page2.products) > 0:
            assert page1.products[0].product_id != page2.products[0].product_id

    # ==================== Classification Tests ====================

    @pytest.mark.asyncio
    async def test_classify_by_nutrient_high_nitrogen(self, service, sample_urea):
        """Test classification of high nitrogen fertilizer."""
        classification = await service.classify_by_nutrient_content(sample_urea)
        assert classification == "nitrogen_only"

    @pytest.mark.asyncio
    async def test_classify_by_nutrient_balanced(self, service):
        """Test classification of balanced fertilizer."""
        balanced_data = FertilizerProductCreate(
            product_name="Balanced 10-10-10",
            manufacturer="Test",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
            nitrogen_percent=10.0,
            phosphorus_percent=10.0,
            potassium_percent=10.0
        )
        balanced = await service.create_fertilizer(balanced_data)

        classification = await service.classify_by_nutrient_content(balanced)
        assert classification == "balanced"

    @pytest.mark.asyncio
    async def test_classify_by_nutrient_high_phosphorus(self, service, sample_dap):
        """Test classification of high phosphorus fertilizer."""
        classification = await service.classify_by_nutrient_content(sample_dap)
        # DAP has both N and P, so it's a complete fertilizer with high P
        assert classification in ["high_phosphorus", "specialty"]

    @pytest.mark.asyncio
    async def test_classify_by_source_organic(self, service, sample_organic):
        """Test classification of organic fertilizer by source."""
        classification = await service.classify_by_source(sample_organic)
        assert "organic" in classification

    @pytest.mark.asyncio
    async def test_classify_by_source_synthetic(self, service, sample_urea):
        """Test classification of synthetic fertilizer by source."""
        classification = await service.classify_by_source(sample_urea)
        assert "synthetic" in classification

    @pytest.mark.asyncio
    async def test_classify_by_release_immediate(self, service, sample_urea):
        """Test classification by immediate release pattern."""
        classification = await service.classify_by_release_pattern(sample_urea)
        assert classification == "immediate_release"

    @pytest.mark.asyncio
    async def test_classify_by_release_slow(self, service, sample_organic):
        """Test classification by slow release pattern."""
        classification = await service.classify_by_release_pattern(sample_organic)
        assert classification == "slow_release"

    @pytest.mark.asyncio
    async def test_classify_by_application_method(self, service, sample_urea):
        """Test classification by application method."""
        classifications = await service.classify_by_application_method(sample_urea)
        assert "broadcast_application" in classifications
        assert "banded_application" in classifications

    @pytest.mark.asyncio
    async def test_get_all_classifications(self, service, sample_urea):
        """Test getting all classifications for a product."""
        classifications = await service.get_product_classifications(sample_urea)

        assert "nutrient_based" in classifications
        assert "source_based" in classifications
        assert "release_based" in classifications
        assert "application_based" in classifications
        assert "npk_ratio" in classifications
        assert classifications["npk_ratio"] == "46-0-0"

    # ==================== Compatibility Tests ====================

    @pytest.mark.asyncio
    async def test_add_compatibility(self, service, sample_urea, sample_dap):
        """Test adding compatibility information."""
        compat = await service.add_compatibility(
            product_id_1=sample_urea.product_id,
            product_id_2=sample_dap.product_id,
            compatibility_level=CompatibilityLevel.COMPATIBLE,
            mixing_ratio_limits={"max_ratio": 1.5, "recommended_ratio": 1.0},
            notes="Compatible for blending"
        )

        assert compat is not None
        assert compat.product_id_1 == sample_urea.product_id
        assert compat.product_id_2 == sample_dap.product_id
        assert compat.compatibility_level == CompatibilityLevel.COMPATIBLE

    @pytest.mark.asyncio
    async def test_check_compatibility(self, service, sample_urea, sample_dap):
        """Test checking compatibility between products."""
        # Add compatibility first
        await service.add_compatibility(
            product_id_1=sample_urea.product_id,
            product_id_2=sample_dap.product_id,
            compatibility_level=CompatibilityLevel.COMPATIBLE,
            notes="Test compatibility"
        )

        # Check compatibility
        compat = await service.check_compatibility(
            sample_urea.product_id,
            sample_dap.product_id
        )

        assert compat is not None
        assert compat.compatibility_level == CompatibilityLevel.COMPATIBLE

    # ==================== Nutrient Analysis Tests ====================

    @pytest.mark.asyncio
    async def test_analyze_nutrient_content(self, service, sample_urea):
        """Test comprehensive nutrient content analysis."""
        analysis = await service.analyze_nutrient_content(sample_urea)

        assert analysis is not None
        assert analysis["npk_ratio"] == "46-0-0"
        assert analysis["total_primary_nutrients"] == 46.0
        assert analysis["nitrogen_percent"] == 46.0
        assert analysis["nutrient_classification"] == "nitrogen_only"
        assert analysis["is_balanced"] is False

    @pytest.mark.asyncio
    async def test_npk_ratio_calculation(self, service):
        """Test NPK ratio calculation."""
        product_data = FertilizerProductCreate(
            product_name="NPK Test 15-15-15",
            manufacturer="Test",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
            nitrogen_percent=15.0,
            phosphorus_percent=15.0,
            potassium_percent=15.0
        )
        product = await service.create_fertilizer(product_data)

        npk_ratio = product.get_npk_ratio()
        assert npk_ratio == "15-15-15"

    # ==================== Bulk Import Tests ====================

    @pytest.mark.asyncio
    async def test_bulk_import_fertilizers(self, service):
        """Test bulk importing fertilizer products."""
        fertilizers = [
            FertilizerProductCreate(
                product_name=f"Bulk Import {i}",
                manufacturer="Bulk Test",
                fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
                nitrogen_percent=10.0 + i
            )
            for i in range(3)
        ]

        results = await service.bulk_import_fertilizers(fertilizers)

        assert results["total"] == 3
        assert results["successful"] == 3
        assert results["failed"] == 0

    # ==================== Agricultural Validation Tests ====================

    @pytest.mark.asyncio
    async def test_crop_suitability_check(self, service, sample_urea):
        """Test agricultural validation for crop suitability."""
        # Check suitable crop
        is_suitable = sample_urea.is_suitable_for_crop("corn")
        assert is_suitable is True

        # Check unsuitable crop
        is_suitable = sample_urea.is_suitable_for_crop("unknown_crop")
        assert is_suitable is False

    @pytest.mark.asyncio
    async def test_balanced_nutrient_validation(self, service):
        """Test validation of balanced nutrient ratios."""
        balanced_data = FertilizerProductCreate(
            product_name="Validation Balanced",
            manufacturer="Test",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
            nitrogen_percent=10.0,
            phosphorus_percent=10.0,
            potassium_percent=10.0
        )
        balanced = await service.create_fertilizer(balanced_data)
        analysis = balanced.get_nutrient_analysis()

        assert analysis.is_balanced(tolerance=1.0) is True

    @pytest.mark.asyncio
    async def test_micronutrient_presence(self, service):
        """Test detection of micronutrient content."""
        micro_data = FertilizerProductCreate(
            product_name="Micronutrient Test",
            manufacturer="Test",
            fertilizer_type=FertilizerTypeEnum.SPECIALTY_MICRONUTRIENT,
            nitrogen_percent=0.0,
            micronutrients={"zinc": 5.0, "iron": 3.0}
        )
        micro_product = await service.create_fertilizer(micro_data)

        analysis = await service.analyze_nutrient_content(micro_product)
        assert analysis["has_micronutrients"] is True
        assert "zinc" in analysis["micronutrients"]
        assert analysis["micronutrients"]["zinc"] == 5.0

    @pytest.mark.asyncio
    async def test_organic_certification_validation(self, service, sample_organic):
        """Test organic certification flag."""
        assert sample_organic.organic_certified is True

        classifications = await service.get_product_classifications(sample_organic)
        assert classifications["is_organic"] is True

    @pytest.mark.asyncio
    async def test_sustainability_rating_range(self, service):
        """Test sustainability rating is within valid range."""
        sustainable_data = FertilizerProductCreate(
            product_name="Sustainability Test",
            manufacturer="Test",
            fertilizer_type=FertilizerTypeEnum.ORGANIC_SOLID,
            sustainability_rating=9.5,
            nitrogen_percent=5.0
        )
        product = await service.create_fertilizer(sustainable_data)

        assert 0.0 <= product.sustainability_rating <= 10.0

    # ==================== Seed Data Integration Tests ====================

    @pytest.mark.asyncio
    async def test_seed_data_import(self, service):
        """Test importing all seed data."""
        seed_data = get_fertilizer_seed_data()

        # Import first 5 products from seed data
        results = await service.bulk_import_fertilizers(seed_data[:5])

        assert results["total"] == 5
        assert results["successful"] == 5

    @pytest.mark.asyncio
    async def test_seed_data_diversity(self, service):
        """Test that seed data covers diverse fertilizer types."""
        seed_data = get_fertilizer_seed_data()

        fertilizer_types = set()
        organic_count = 0
        synthetic_count = 0

        # Look at more products to ensure we get diversity
        for fertilizer_create in seed_data[:15]:
            fertilizer_types.add(fertilizer_create.fertilizer_type)
            if fertilizer_create.organic_certified:
                organic_count += 1
            else:
                synthetic_count += 1

        # Ensure diversity - should have at least 2 different types
        assert len(fertilizer_types) >= 2
        assert organic_count > 0
        assert synthetic_count > 0

    # ==================== Edge Cases and Error Handling ====================

    @pytest.mark.asyncio
    async def test_update_nonexistent_product(self, service):
        """Test updating a product that doesn't exist."""
        update_data = FertilizerProductUpdate(manufacturer="Test")
        result = await service.update_fertilizer(uuid4(), update_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_product(self, service):
        """Test deleting a product that doesn't exist."""
        result = await service.delete_fertilizer(uuid4())
        assert result is False

    @pytest.mark.asyncio
    async def test_empty_search_results(self, service):
        """Test search with filters that match no products."""
        filters = FertilizerSearchFilters(
            min_nitrogen=99.0,  # Impossible nitrogen content
            max_nitrogen=100.0
        )

        response = await service.search_fertilizers(filters)
        assert response.total_count == 0
        assert len(response.products) == 0

    @pytest.mark.asyncio
    async def test_nutrient_percentage_validation(self, service):
        """Test that nutrient percentages are within valid ranges."""
        product_data = FertilizerProductCreate(
            product_name="Validation Test",
            manufacturer="Test",
            fertilizer_type=FertilizerTypeEnum.SYNTHETIC_GRANULAR,
            nitrogen_percent=46.0,
            phosphorus_percent=52.0,
            potassium_percent=60.0
        )
        product = await service.create_fertilizer(product_data)

        # All percentages should be within 0-100 range
        assert 0 <= product.nitrogen_percent <= 100
        assert 0 <= product.phosphorus_percent <= 100
        assert 0 <= product.potassium_percent <= 100


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
