"""
Comprehensive fertilizer database service with CRUD operations,
classification methods, and advanced search capabilities.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date
from uuid import UUID, uuid4

from ..models.fertilizer_database_models import (
    FertilizerProduct, FertilizerProductCreate, FertilizerProductUpdate,
    FertilizerClassification, FertilizerCompatibility, NutrientAnalysis,
    ApplicationRecommendation, FertilizerSearchFilters, FertilizerSearchResponse,
    FertilizerTypeEnum, NutrientReleasePattern, CompatibilityLevel,
    ClassificationType, EnvironmentalImpact, CostData
)
from ..database.fertilizer_database_db import (
    FertilizerDatabaseRepository, get_db_session,
    FertilizerProductDB, FertilizerClassificationDB, FertilizerCompatibilityDB
)

logger = logging.getLogger(__name__)


class FertilizerDatabaseService:
    """
    Main service for fertilizer database operations including CRUD,
    classification, search, and analysis.
    """

    def __init__(self):
        """Initialize the fertilizer database service."""
        self._in_memory_products: Dict[str, FertilizerProduct] = {}
        self._in_memory_classifications: List[FertilizerClassification] = []
        self._in_memory_compatibility: List[FertilizerCompatibility] = []

    # ==================== CRUD Operations ====================

    async def create_fertilizer(
        self,
        fertilizer_data: FertilizerProductCreate
    ) -> FertilizerProduct:
        """
        Create a new fertilizer product.

        Args:
            fertilizer_data: Fertilizer product creation data

        Returns:
            Created fertilizer product
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)

                # Convert Pydantic model to dict
                product_dict = fertilizer_data.model_dump()
                product_dict['created_at'] = datetime.utcnow()
                product_dict['updated_at'] = datetime.utcnow()
                product_dict['last_verified'] = datetime.utcnow()

                # Create in database
                db_product = await repo.create_product(product_dict)

                # Convert to Pydantic model
                return self._db_to_pydantic(db_product)

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, using in-memory storage")
                return self._create_in_memory(fertilizer_data)
            raise
        except Exception as e:
            logger.error(f"Error creating fertilizer product: {e}")
            raise

    async def get_fertilizer(self, product_id: UUID) -> Optional[FertilizerProduct]:
        """
        Get a fertilizer product by ID.

        Args:
            product_id: Product UUID

        Returns:
            Fertilizer product or None if not found
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)
                db_product = await repo.get_product_by_id(product_id)

                if db_product:
                    return self._db_to_pydantic(db_product)
                return None

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, using in-memory storage")
                return self._in_memory_products.get(str(product_id))
            raise
        except Exception as e:
            logger.error(f"Error getting fertilizer product: {e}")
            raise

    async def get_fertilizer_by_name(self, product_name: str) -> Optional[FertilizerProduct]:
        """
        Get a fertilizer product by name.

        Args:
            product_name: Product name

        Returns:
            Fertilizer product or None if not found
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)
                db_product = await repo.get_product_by_name(product_name)

                if db_product:
                    return self._db_to_pydantic(db_product)
                return None

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, using in-memory storage")
                for product in self._in_memory_products.values():
                    if product.product_name == product_name:
                        return product
                return None
            raise
        except Exception as e:
            logger.error(f"Error getting fertilizer by name: {e}")
            raise

    async def update_fertilizer(
        self,
        product_id: UUID,
        update_data: FertilizerProductUpdate
    ) -> Optional[FertilizerProduct]:
        """
        Update a fertilizer product.

        Args:
            product_id: Product UUID
            update_data: Fields to update

        Returns:
            Updated fertilizer product or None if not found
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)

                # Convert to dict, excluding None values
                update_dict = update_data.model_dump(exclude_none=True)

                # Update in database
                db_product = await repo.update_product(product_id, update_dict)

                if db_product:
                    return self._db_to_pydantic(db_product)
                return None

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, using in-memory storage")
                return self._update_in_memory(product_id, update_data)
            raise
        except Exception as e:
            logger.error(f"Error updating fertilizer product: {e}")
            raise

    async def delete_fertilizer(self, product_id: UUID) -> bool:
        """
        Delete (soft delete) a fertilizer product.

        Args:
            product_id: Product UUID

        Returns:
            True if deleted, False if not found
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)
                return await repo.delete_product(product_id)

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, using in-memory storage")
                if str(product_id) in self._in_memory_products:
                    self._in_memory_products[str(product_id)].is_active = False
                    return True
                return False
            raise
        except Exception as e:
            logger.error(f"Error deleting fertilizer product: {e}")
            raise

    async def search_fertilizers(
        self,
        filters: FertilizerSearchFilters
    ) -> FertilizerSearchResponse:
        """
        Search fertilizer products with advanced filters.

        Args:
            filters: Search filters

        Returns:
            Search results with pagination
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)

                # Execute search
                products_db, total_count = await repo.search_products(filters)

                # Convert to Pydantic models
                products = []
                for db_product in products_db:
                    products.append(self._db_to_pydantic(db_product))

                return FertilizerSearchResponse(
                    products=products,
                    total_count=total_count,
                    limit=filters.limit,
                    offset=filters.offset,
                    filters_applied=filters.model_dump(exclude_none=True)
                )

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, using in-memory search")
                return self._search_in_memory(filters)
            raise
        except Exception as e:
            logger.error(f"Error searching fertilizer products: {e}")
            raise

    async def get_all_fertilizers(
        self,
        is_active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[FertilizerProduct]:
        """
        Get all fertilizer products.

        Args:
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of fertilizer products
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)
                products_db = await repo.get_all_products(is_active, limit, offset)

                products = []
                for db_product in products_db:
                    products.append(self._db_to_pydantic(db_product))

                return products

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, using in-memory storage")
                filtered = []
                for product in self._in_memory_products.values():
                    if product.is_active == is_active:
                        filtered.append(product)
                return filtered[offset:offset + limit]
            raise
        except Exception as e:
            logger.error(f"Error getting all fertilizer products: {e}")
            raise

    # ==================== Classification Methods ====================

    async def classify_by_nutrient_content(
        self,
        product: FertilizerProduct
    ) -> str:
        """
        Classify fertilizer by primary nutrient content.

        Args:
            product: Fertilizer product

        Returns:
            Classification name (e.g., 'high_nitrogen', 'balanced', 'complete')
        """
        analysis = product.get_nutrient_analysis()

        # Check if balanced
        if analysis.is_balanced(tolerance=3.0):
            return "balanced"

        # Check for complete fertilizer (has N, P, and K)
        if analysis.nitrogen_percent > 0 and analysis.phosphorus_percent > 0 and analysis.potassium_percent > 0:
            # Determine primary nutrient
            max_nutrient = max(analysis.nitrogen_percent, analysis.phosphorus_percent, analysis.potassium_percent)

            if max_nutrient == analysis.nitrogen_percent:
                return "high_nitrogen"
            elif max_nutrient == analysis.phosphorus_percent:
                return "high_phosphorus"
            else:
                return "high_potassium"

        # Single nutrient fertilizers
        if analysis.nitrogen_percent > 0 and analysis.phosphorus_percent == 0 and analysis.potassium_percent == 0:
            return "nitrogen_only"
        elif analysis.phosphorus_percent > 0 and analysis.nitrogen_percent == 0 and analysis.potassium_percent == 0:
            return "phosphorus_only"
        elif analysis.potassium_percent > 0 and analysis.nitrogen_percent == 0 and analysis.phosphorus_percent == 0:
            return "potassium_only"

        # Micronutrient focused
        if len(analysis.micronutrients) > 0 and analysis.get_total_nutrients() < 10:
            return "micronutrient_focused"

        # Secondary nutrients
        if product.sulfur_percent > 10 or product.calcium_percent > 10 or product.magnesium_percent > 5:
            return "secondary_nutrient_focused"

        return "specialty"

    async def classify_by_source(self, product: FertilizerProduct) -> str:
        """
        Classify fertilizer by source (organic vs synthetic).

        Args:
            product: Fertilizer product

        Returns:
            Classification name (e.g., 'organic_plant', 'synthetic_chemical', 'mineral')
        """
        if product.organic_certified:
            # Further classify organic sources
            if product.fertilizer_type == FertilizerTypeEnum.ORGANIC_SOLID:
                # Check product name for common organic sources
                name_lower = product.product_name.lower()
                if any(term in name_lower for term in ['manure', 'compost', 'blood', 'bone', 'feather', 'fish']):
                    return "organic_animal"
                elif any(term in name_lower for term in ['kelp', 'seaweed', 'alfalfa', 'soy']):
                    return "organic_plant"
                else:
                    return "organic_mixed"
            elif product.fertilizer_type == FertilizerTypeEnum.ORGANIC_LIQUID:
                return "organic_liquid"
            else:
                return "organic_other"
        else:
            # Synthetic classification
            if product.fertilizer_type == FertilizerTypeEnum.SYNTHETIC_GRANULAR:
                return "synthetic_granular"
            elif product.fertilizer_type == FertilizerTypeEnum.SYNTHETIC_LIQUID:
                return "synthetic_liquid"
            elif product.fertilizer_type in [
                FertilizerTypeEnum.SLOW_RELEASE_COATED,
                FertilizerTypeEnum.SLOW_RELEASE_MATRIX
            ]:
                return "synthetic_controlled_release"
            else:
                # Check for mineral sources
                name_lower = product.product_name.lower()
                if any(term in name_lower for term in ['sulfate', 'phosphate', 'muriate', 'nitrate']):
                    return "mineral_based"
                else:
                    return "synthetic_chemical"

    async def classify_by_release_pattern(self, product: FertilizerProduct) -> str:
        """
        Classify fertilizer by nutrient release pattern.

        Args:
            product: Fertilizer product

        Returns:
            Classification name
        """
        if product.release_pattern == NutrientReleasePattern.IMMEDIATE:
            return "immediate_release"
        elif product.release_pattern in [
            NutrientReleasePattern.SLOW_RELEASE_30_DAYS,
            NutrientReleasePattern.SLOW_RELEASE_60_DAYS,
            NutrientReleasePattern.SLOW_RELEASE_90_DAYS
        ]:
            return "slow_release"
        elif product.release_pattern in [
            NutrientReleasePattern.CONTROLLED_RELEASE_TEMPERATURE,
            NutrientReleasePattern.CONTROLLED_RELEASE_MOISTURE
        ]:
            return "controlled_release"
        elif product.release_pattern == NutrientReleasePattern.STABILIZED:
            return "stabilized"
        else:
            return "other_release"

    async def classify_by_application_method(self, product: FertilizerProduct) -> List[str]:
        """
        Classify fertilizer by compatible application methods.

        Args:
            product: Fertilizer product

        Returns:
            List of application method classifications
        """
        classifications = []

        for method in product.application_methods:
            method_lower = method.lower()

            if method_lower == "broadcast":
                classifications.append("broadcast_application")
            elif method_lower == "banded":
                classifications.append("banded_application")
            elif method_lower == "foliar":
                classifications.append("foliar_application")
            elif method_lower in ["fertigation", "irrigation"]:
                classifications.append("fertigation_application")
            elif method_lower in ["injection", "subsurface"]:
                classifications.append("injection_application")
            elif method_lower in ["seed_placed", "starter"]:
                classifications.append("starter_application")
            elif method_lower in ["topdress", "sidedress"]:
                classifications.append("topdress_application")
            else:
                classifications.append("other_application")

        return classifications if classifications else ["unspecified_application"]

    async def get_product_classifications(
        self,
        product: FertilizerProduct
    ) -> Dict[str, Any]:
        """
        Get all classifications for a product.

        Args:
            product: Fertilizer product

        Returns:
            Dictionary of all classifications
        """
        return {
            "nutrient_based": await self.classify_by_nutrient_content(product),
            "source_based": await self.classify_by_source(product),
            "release_based": await self.classify_by_release_pattern(product),
            "application_based": await self.classify_by_application_method(product),
            "npk_ratio": product.get_npk_ratio(),
            "is_organic": product.organic_certified,
            "is_balanced": product.get_nutrient_analysis().is_balanced()
        }

    # ==================== Compatibility Operations ====================

    async def check_compatibility(
        self,
        product_id_1: UUID,
        product_id_2: UUID
    ) -> Optional[FertilizerCompatibility]:
        """
        Check compatibility between two fertilizer products.

        Args:
            product_id_1: First product UUID
            product_id_2: Second product UUID

        Returns:
            Compatibility information or None
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)
                db_compat = await repo.get_compatibility(product_id_1, product_id_2)

                if db_compat:
                    return FertilizerCompatibility(
                        compatibility_id=db_compat.compatibility_id,
                        product_id_1=db_compat.product_id_1,
                        product_id_2=db_compat.product_id_2,
                        compatibility_level=db_compat.compatibility_level,
                        mixing_ratio_limits=db_compat.mixing_ratio_limits,
                        notes=db_compat.notes,
                        test_date=db_compat.test_date,
                        verified_by=db_compat.verified_by,
                        created_at=db_compat.created_at,
                        updated_at=db_compat.updated_at
                    )
                return None

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, checking in-memory compatibility")
                for compat in self._in_memory_compatibility:
                    if ((compat.product_id_1 == product_id_1 and compat.product_id_2 == product_id_2) or
                        (compat.product_id_1 == product_id_2 and compat.product_id_2 == product_id_1)):
                        return compat
                return None
            raise
        except Exception as e:
            logger.error(f"Error checking compatibility: {e}")
            raise

    async def add_compatibility(
        self,
        product_id_1: UUID,
        product_id_2: UUID,
        compatibility_level: CompatibilityLevel,
        mixing_ratio_limits: Optional[Dict[str, float]] = None,
        notes: Optional[str] = None
    ) -> FertilizerCompatibility:
        """
        Add compatibility information for two products.

        Args:
            product_id_1: First product UUID
            product_id_2: Second product UUID
            compatibility_level: Compatibility level
            mixing_ratio_limits: Mixing ratio limits
            notes: Additional notes

        Returns:
            Created compatibility record
        """
        try:
            async for session in get_db_session():
                repo = FertilizerDatabaseRepository(session)

                compat_data = {
                    'product_id_1': product_id_1,
                    'product_id_2': product_id_2,
                    'compatibility_level': compatibility_level,
                    'mixing_ratio_limits': mixing_ratio_limits or {},
                    'notes': notes,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }

                db_compat = await repo.create_compatibility(compat_data)

                return FertilizerCompatibility(
                    compatibility_id=db_compat.compatibility_id,
                    product_id_1=db_compat.product_id_1,
                    product_id_2=db_compat.product_id_2,
                    compatibility_level=db_compat.compatibility_level,
                    mixing_ratio_limits=db_compat.mixing_ratio_limits,
                    notes=db_compat.notes,
                    test_date=db_compat.test_date,
                    verified_by=db_compat.verified_by,
                    created_at=db_compat.created_at,
                    updated_at=db_compat.updated_at
                )

        except RuntimeError as e:
            if "Database not initialized" in str(e):
                logger.warning("Database not initialized, storing in memory")
                compat = FertilizerCompatibility(
                    compatibility_id=uuid4(),
                    product_id_1=product_id_1,
                    product_id_2=product_id_2,
                    compatibility_level=compatibility_level,
                    mixing_ratio_limits=mixing_ratio_limits or {},
                    notes=notes
                )
                self._in_memory_compatibility.append(compat)
                return compat
            raise
        except Exception as e:
            logger.error(f"Error adding compatibility: {e}")
            raise

    # ==================== Nutrient Analysis ====================

    async def analyze_nutrient_content(
        self,
        product: FertilizerProduct
    ) -> Dict[str, Any]:
        """
        Perform comprehensive nutrient content analysis.

        Args:
            product: Fertilizer product

        Returns:
            Analysis results
        """
        analysis = product.get_nutrient_analysis()

        return {
            "npk_ratio": analysis.get_npk_ratio(),
            "total_primary_nutrients": analysis.get_total_nutrients(),
            "is_balanced": analysis.is_balanced(),
            "nitrogen_percent": analysis.nitrogen_percent,
            "phosphorus_percent": analysis.phosphorus_percent,
            "potassium_percent": analysis.potassium_percent,
            "sulfur_percent": analysis.sulfur_percent,
            "calcium_percent": analysis.calcium_percent,
            "magnesium_percent": analysis.magnesium_percent,
            "micronutrients": analysis.micronutrients,
            "has_micronutrients": len(analysis.micronutrients) > 0,
            "nutrient_classification": await self.classify_by_nutrient_content(product)
        }

    # ==================== Bulk Import ====================

    async def bulk_import_fertilizers(
        self,
        fertilizers: List[FertilizerProductCreate]
    ) -> Dict[str, Any]:
        """
        Import multiple fertilizer products at once.

        Args:
            fertilizers: List of fertilizer products to import

        Returns:
            Import results summary
        """
        results = {
            "total": len(fertilizers),
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        for fertilizer in fertilizers:
            try:
                await self.create_fertilizer(fertilizer)
                results["successful"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "product_name": fertilizer.product_name,
                    "error": str(e)
                })

        return results

    # ==================== Helper Methods ====================

    def _db_to_pydantic(self, db_product: FertilizerProductDB) -> FertilizerProduct:
        """Convert database model to Pydantic model."""
        return FertilizerProduct(
            product_id=db_product.product_id,
            product_name=db_product.product_name,
            manufacturer=db_product.manufacturer,
            fertilizer_type=db_product.fertilizer_type,
            nitrogen_percent=db_product.nitrogen_percent,
            phosphorus_percent=db_product.phosphorus_percent,
            potassium_percent=db_product.potassium_percent,
            sulfur_percent=db_product.sulfur_percent,
            calcium_percent=db_product.calcium_percent,
            magnesium_percent=db_product.magnesium_percent,
            micronutrients=db_product.micronutrients or {},
            physical_form=db_product.physical_form,
            particle_size=db_product.particle_size,
            bulk_density=db_product.bulk_density,
            solubility=db_product.solubility,
            release_pattern=db_product.release_pattern,
            application_methods=db_product.application_methods or [],
            compatible_equipment=db_product.compatible_equipment or [],
            mixing_compatibility=db_product.mixing_compatibility or {},
            environmental_impact=db_product.environmental_impact or {},
            organic_certified=db_product.organic_certified,
            sustainability_rating=db_product.sustainability_rating,
            average_cost_per_unit=db_product.average_cost_per_unit,
            cost_unit=db_product.cost_unit,
            price_volatility=db_product.price_volatility,
            availability_score=db_product.availability_score,
            regulatory_status=db_product.regulatory_status,
            safety_data=db_product.safety_data or {},
            handling_requirements=db_product.handling_requirements or [],
            storage_requirements=db_product.storage_requirements or [],
            recommended_crops=db_product.recommended_crops or [],
            not_recommended_crops=db_product.not_recommended_crops or [],
            growth_stage_suitability=db_product.growth_stage_suitability or {},
            created_at=db_product.created_at,
            updated_at=db_product.updated_at,
            data_source=db_product.data_source,
            last_verified=db_product.last_verified,
            is_active=db_product.is_active
        )

    def _create_in_memory(self, fertilizer_data: FertilizerProductCreate) -> FertilizerProduct:
        """Create fertilizer in in-memory storage."""
        product = FertilizerProduct(
            product_id=uuid4(),
            **fertilizer_data.model_dump()
        )
        self._in_memory_products[str(product.product_id)] = product
        return product

    def _update_in_memory(
        self,
        product_id: UUID,
        update_data: FertilizerProductUpdate
    ) -> Optional[FertilizerProduct]:
        """Update fertilizer in in-memory storage."""
        product_key = str(product_id)
        if product_key not in self._in_memory_products:
            return None

        product = self._in_memory_products[product_key]
        update_dict = update_data.model_dump(exclude_none=True)

        for key, value in update_dict.items():
            if hasattr(product, key):
                setattr(product, key, value)

        product.updated_at = datetime.utcnow()
        return product

    def _search_in_memory(self, filters: FertilizerSearchFilters) -> FertilizerSearchResponse:
        """Search fertilizers in in-memory storage."""
        filtered = []

        for product in self._in_memory_products.values():
            if not self._matches_filters(product, filters):
                continue
            filtered.append(product)

        total_count = len(filtered)
        paginated = filtered[filters.offset:filters.offset + filters.limit]

        return FertilizerSearchResponse(
            products=paginated,
            total_count=total_count,
            limit=filters.limit,
            offset=filters.offset,
            filters_applied=filters.model_dump(exclude_none=True)
        )

    def _matches_filters(self, product: FertilizerProduct, filters: FertilizerSearchFilters) -> bool:
        """Check if product matches search filters."""
        if filters.fertilizer_types and product.fertilizer_type not in filters.fertilizer_types:
            return False

        if filters.min_nitrogen is not None and product.nitrogen_percent < filters.min_nitrogen:
            return False

        if filters.max_nitrogen is not None and product.nitrogen_percent > filters.max_nitrogen:
            return False

        if filters.min_phosphorus is not None and product.phosphorus_percent < filters.min_phosphorus:
            return False

        if filters.max_phosphorus is not None and product.phosphorus_percent > filters.max_phosphorus:
            return False

        if filters.min_potassium is not None and product.potassium_percent < filters.min_potassium:
            return False

        if filters.max_potassium is not None and product.potassium_percent > filters.max_potassium:
            return False

        if filters.organic_only is not None and product.organic_certified != filters.organic_only:
            return False

        if filters.crop_type:
            if not product.is_suitable_for_crop(filters.crop_type):
                return False

        if filters.application_method:
            method_found = False
            for method in product.application_methods:
                if filters.application_method.lower() in method.lower():
                    method_found = True
                    break
            if not method_found:
                return False

        if filters.release_pattern and product.release_pattern != filters.release_pattern:
            return False

        if filters.min_sustainability_rating is not None:
            if product.sustainability_rating < filters.min_sustainability_rating:
                return False

        if filters.manufacturer:
            if not product.manufacturer or filters.manufacturer.lower() not in product.manufacturer.lower():
                return False

        if product.is_active != filters.is_active:
            return False

        return True
