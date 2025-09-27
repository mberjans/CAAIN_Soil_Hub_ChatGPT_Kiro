"""
Crop Taxonomy Service

Core service for botanical classification, agricultural categorization,
and comprehensive crop data management following scientific standards.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

try:
    from data.reference_crops import build_reference_crops_dataset
    from models.crop_taxonomy_models import (
        CropTaxonomicHierarchy,
        CropAgriculturalClassification,
        CropClimateAdaptations,
        CropSoilRequirements,
        CropNutritionalProfile,
        ComprehensiveCropData,
        CropCategory,
        PrimaryUse
    )
    from models.service_models import (
        CropClassificationRequest,
        ClassificationResult,
        CropClassificationResponse,
        ValidationRequest,
        ValidationResponse,
        OperationType,
        DataSource,
        BulkOperationResponse
    )
except ImportError:
    from ..data.reference_crops import build_reference_crops_dataset
    from ..models.crop_taxonomy_models import (
        CropTaxonomicHierarchy,
        CropAgriculturalClassification,
        CropClimateAdaptations,
        CropSoilRequirements,
        CropNutritionalProfile,
        ComprehensiveCropData,
        CropCategory,
        PrimaryUse
    )
    from ..models.service_models import (
        CropClassificationRequest,
        ClassificationResult,
        CropClassificationResponse,
        ValidationRequest,
        ValidationResponse,
        OperationType,
        DataSource,
        BulkOperationResponse
    )

# Define enum for confidence levels used in the service
from enum import Enum

class ConfidenceLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Lightweight validation result for internal checks."""

    field_name: str
    is_valid: bool
    message: Optional[str] = None
    error_message: Optional[str] = None
    warnings: List[str] = Field(default_factory=list)


class CropTaxonomyService:
    """
    Core service for crop taxonomic operations including botanical classification,
    agricultural categorization, and comprehensive crop data management.
    """

    def __init__(self, database_url: Optional[str] = None):
        """Initialize the crop taxonomy service with database integration."""
        try:
            from ..database.crop_taxonomy_db import CropTaxonomyDatabase
            self.db = CropTaxonomyDatabase(database_url)
            self.database_available = self.db.test_connection()
            logger.info(f"Database connection: {'successful' if self.database_available else 'failed'}")
        except ImportError:
            logger.warning("Database integration not available, using fallback mode")
            self.db = None
            self.database_available = False
        
        self.taxonomy_cache = {}
        self._initialize_taxonomic_knowledge()

    def _initialize_taxonomic_knowledge(self):
        """Initialize taxonomic knowledge base and validation rules."""
        # Initialize crop family mappings
        self.crop_families = {
            "Poaceae": ["wheat", "corn", "rice", "barley", "oats", "rye", "sorghum", "millet"],
            "Fabaceae": ["soybean", "pea", "bean", "lentil", "chickpea", "alfalfa", "clover"],
            "Brassicaceae": ["canola", "mustard", "turnip", "radish", "cabbage", "broccoli"],
            "Solanaceae": ["tomato", "potato", "pepper", "eggplant", "tobacco"],
            "Cucurbitaceae": ["cucumber", "melon", "watermelon", "squash", "pumpkin"],
            "Asteraceae": ["sunflower", "lettuce", "artichoke", "safflower"],
            "Apiaceae": ["carrot", "celery", "parsnip", "dill", "fennel"],
            "Chenopodiaceae": ["beet", "spinach", "quinoa", "chard"]
        }

        # Initialize genus-species mappings for common crops
        self.genus_species_map = {
            "wheat": {"genus": "Triticum", "species": "aestivum"},
            "corn": {"genus": "Zea", "species": "mays"},
            "soybean": {"genus": "Glycine", "species": "max"},
            "rice": {"genus": "Oryza", "species": "sativa"},
            "barley": {"genus": "Hordeum", "species": "vulgare"},
            "canola": {"genus": "Brassica", "species": "napus"},
            "sunflower": {"genus": "Helianthus", "species": "annuus"}
        }

        # Agricultural classification rules
        self.classification_rules = {
            "grain_crops": ["wheat", "corn", "rice", "barley", "oats", "rye", "sorghum"],
            "oilseed_crops": ["soybean", "canola", "sunflower", "flax", "safflower"],
            "legume_crops": ["soybean", "pea", "bean", "lentil", "chickpea", "alfalfa"],
            "forage_crops": ["alfalfa", "clover", "timothy", "fescue", "ryegrass"],
            "vegetable_crops": ["tomato", "cucumber", "lettuce", "carrot", "onion"]
        }

        # Load reference dataset for fallback operations
        self.reference_crops = build_reference_crops_dataset()
        self.reference_crop_index = {}

        for crop in self.reference_crops:
            crop_key = crop.crop_name.lower()
            self.reference_crop_index[crop_key] = crop
            self.taxonomy_cache[crop_key] = crop

            if crop.search_keywords:
                for keyword in crop.search_keywords:
                    keyword_key = keyword.lower()
                    if keyword_key not in self.reference_crop_index:
                        self.reference_crop_index[keyword_key] = crop

            taxonomy = crop.taxonomic_hierarchy
            if taxonomy:
                if crop_key not in self.genus_species_map:
                    self.genus_species_map[crop_key] = {
                        "genus": taxonomy.genus,
                        "species": taxonomy.species
                    }

                synonyms = taxonomy.common_synonyms or []
                for synonym in synonyms:
                    synonym_key = synonym.lower()
                    if synonym_key not in self.reference_crop_index:
                        self.reference_crop_index[synonym_key] = crop
                    if synonym_key not in self.genus_species_map:
                        self.genus_species_map[synonym_key] = {
                            "genus": taxonomy.genus,
                            "species": taxonomy.species
                        }

                family_name = taxonomy.family
                if family_name:
                    if family_name not in self.crop_families:
                        self.crop_families[family_name] = []
                    family_list = self.crop_families[family_name]
                    if crop_key not in family_list:
                        family_list.append(crop_key)


    async def classify_crop_taxonomically(
        self,
        request: CropClassificationRequest
    ) -> CropClassificationResponse:
        """
        Classify a crop taxonomically based on common name or botanical characteristics.

        Args:
            request: Classification request with crop name or characteristics

        Returns:
            Complete taxonomic classification with confidence scores
        """
        start_time = datetime.utcnow()
        try:
            crop_name_value = request.crop_name.lower() if request.crop_name else None
            confidence = ConfidenceLevel.LOW
            taxonomy = None

            if crop_name_value:
                taxonomy = await self._classify_from_common_name(crop_name_value)
                if taxonomy:
                    confidence = ConfidenceLevel.HIGH
                else:
                    taxonomy, confidence = await self._fuzzy_taxonomic_match(crop_name_value)
            else:
                taxonomy, confidence = await self._classify_from_characteristics(request)

            if not taxonomy:
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                failure_details = ["No matching taxonomy found"]
                if not request.crop_name and not request.description:
                    failure_details.append("Insufficient crop descriptors provided")
                return CropClassificationResponse(
                    request_id=request.request_id,
                    operation_type=OperationType.CLASSIFY,
                    processing_time_seconds=processing_time,
                    success=False,
                    status_message="Unable to classify crop",
                    error_details=failure_details,
                    overall_confidence=0.0,
                    classification_results=[],
                    best_match=None,
                    similar_crops=[],
                    taxonomic_family_crops=[],
                    input_quality_score=0.0,
                    classification_method="reference-dataset",
                    suggested_refinements=["Provide crop name or additional descriptors"]
                )

            agricultural_classification = await self._generate_agricultural_classification(taxonomy, crop_name_value)

            matched_fields = []
            if crop_name_value:
                matched_fields.append("crop_name")
            classification_result = ClassificationResult(
                matched_crop=ComprehensiveCropData(
                    crop_name=crop_name_value or "Unknown Crop",
                    taxonomic_hierarchy=taxonomy,
                    agricultural_classification=agricultural_classification
                ),
                confidence_score=0.9 if confidence == ConfidenceLevel.HIGH else 0.6,
                similarity_score=0.9 if confidence == ConfidenceLevel.HIGH else 0.6,
                matched_fields=matched_fields
            )

            processing_time = (datetime.utcnow() - start_time).total_seconds()
            data_sources = []
            if self.database_available:
                data_sources.append(DataSource.INTERNAL_DATABASE)
            else:
                data_sources.append(DataSource.INTERNAL_DATABASE)

            return CropClassificationResponse(
                request_id=request.request_id,
                operation_type=OperationType.CLASSIFY,
                processing_time_seconds=processing_time,
                success=True,
                status_message="Classification completed",
                overall_confidence=classification_result.confidence_score,
                data_sources=data_sources,
                classification_results=[classification_result],
                best_match=classification_result,
                similar_crops=[],
                taxonomic_family_crops=[],
                input_quality_score=1.0 if crop_name_value else 0.8,
                classification_method="reference-dataset" if not self.database_available else "database-reference",
                suggested_refinements=None
            )

        except Exception as e:
            logger.error(f"Error in taxonomic classification: {str(e)}")
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            return CropClassificationResponse(
                request_id=request.request_id if request else "classification-error",
                operation_type=OperationType.CLASSIFY,
                processing_time_seconds=processing_time,
                success=False,
                status_message="Classification error",
                error_details=[str(e)],
                overall_confidence=0.0,
                classification_results=[],
                best_match=None,
                similar_crops=[],
                taxonomic_family_crops=[],
                input_quality_score=0.0,
                classification_method="reference-dataset",
                suggested_refinements=None
            )

    async def _classify_from_common_name(self, crop_name: str) -> Optional[CropTaxonomicHierarchy]:
        """Classify crop from common name using database and knowledge base."""
        # First try database lookup if available
        if self.database_available:
            try:
                crops = self.db.search_crops(search_text=crop_name, limit=5)
                if crops:
                    # Use the first match and convert to CropTaxonomicHierarchy
                    best_match = crops[0]
                    if 'taxonomic_hierarchy' in best_match:
                        taxonomy_data = best_match['taxonomic_hierarchy']
                        return CropTaxonomicHierarchy(
                            id=taxonomy_data.get('id', uuid4()),
                            kingdom=taxonomy_data.get('kingdom', 'Plantae'),
                            phylum=taxonomy_data.get('phylum', 'Tracheophyta'),
                            class_name=taxonomy_data.get('class_name', 'Magnoliopsida'),
                            order=taxonomy_data.get('order', 'Unknown'),
                            family=taxonomy_data.get('family', 'Unknown'),
                            genus=taxonomy_data.get('genus', 'Unknown'),
                            species=taxonomy_data.get('species', 'Unknown'),
                            common_names=taxonomy_data.get('common_names', [crop_name]),
                            botanical_authority=taxonomy_data.get('botanical_authority', 'L.'),
                            is_hybrid=taxonomy_data.get('is_hybrid', False),
                            ploidy_level=taxonomy_data.get('ploidy_level', 2),
                            chromosome_count=taxonomy_data.get('chromosome_count', 0)
                        )
            except Exception as e:
                logger.warning(f"Database lookup failed for {crop_name}: {e}")

        # Reference dataset fallback
        reference_crop = self.reference_crop_index.get(crop_name)
        if reference_crop and reference_crop.taxonomic_hierarchy:
            taxonomy_model = reference_crop.taxonomic_hierarchy
            taxonomy_payload = taxonomy_model.model_dump(by_alias=True)
            return CropTaxonomicHierarchy(**taxonomy_payload)

        # Fallback to knowledge base
        if crop_name in self.genus_species_map:
            genus_species = self.genus_species_map[crop_name]
            family = self._get_family_from_genus_species(genus_species["genus"], genus_species["species"])
            
            return CropTaxonomicHierarchy(
                id=uuid4(),
                kingdom="Plantae",
                phylum="Tracheophyta",
                class_name="Magnoliopsida" if family != "Poaceae" else "Liliopsida",
                order=self._get_order_from_family(family),
                family=family,
                genus=genus_species["genus"],
                species=genus_species["species"],
                common_names=[crop_name],
                botanical_authority=self._get_botanical_authority(genus_species["genus"], genus_species["species"]),
                is_hybrid=False,
                ploidy_level=self._get_typical_ploidy(crop_name),
                chromosome_count=self._get_chromosome_count(crop_name)
            )
        return None

    async def _fuzzy_taxonomic_match(self, crop_name: str) -> Tuple[Optional[CropTaxonomicHierarchy], ConfidenceLevel]:
        """Perform fuzzy matching for crop classification."""
        # Simple fuzzy matching implementation
        possible_matches = []
        
        for known_crop in self.genus_species_map.keys():
            # Check for partial matches, synonyms, etc.
            if crop_name in known_crop or known_crop in crop_name:
                possible_matches.append((known_crop, 0.8))
            elif self._calculate_similarity(crop_name, known_crop) > 0.6:
                possible_matches.append((known_crop, 0.6))

        if possible_matches:
            # Take the best match
            best_match = max(possible_matches, key=lambda x: x[1])
            taxonomy = await self._classify_from_common_name(best_match[0])
            confidence = ConfidenceLevel.MEDIUM if best_match[1] > 0.7 else ConfidenceLevel.LOW
            return taxonomy, confidence

        return None, ConfidenceLevel.LOW

    async def _classify_from_characteristics(
        self,
        request: CropClassificationRequest
    ) -> Tuple[Optional[CropTaxonomicHierarchy], ConfidenceLevel]:
        """Classify from botanical characteristics."""
        # This would implement classification based on morphological characteristics
        # For now, return a placeholder implementation
        return None, ConfidenceLevel.LOW

    async def _generate_agricultural_classification(
        self, 
        taxonomy: CropTaxonomicHierarchy, 
        crop_name: Optional[str]
    ) -> Optional[CropAgriculturalClassification]:
        """Generate agricultural classification from taxonomic data and database lookup."""
        if not crop_name:
            return None

        # Try to get agricultural classification from database
        if self.database_available and crop_name:
            try:
                crops = self.db.search_crops(search_text=crop_name, limit=1)
                if crops and 'agricultural_classification' in crops[0]:
                    ag_data = crops[0]['agricultural_classification']
                    return CropAgriculturalClassification(
                        id=ag_data.get('id', uuid4()),
                        primary_category=CropCategory(ag_data.get('crop_category', 'specialty')),
                        secondary_categories=[],
                        primary_use=PrimaryUse(ag_data.get('primary_use', 'food_human')),
                        secondary_uses=[],
                        life_cycle=LifeCycle(ag_data.get('plant_type', 'annual')),
                        growth_habit=ag_data.get('growth_habit', 'upright'),
                        plant_height_range=ag_data.get('plant_height_range', (30, 200)),
                        maturity_days_range=ag_data.get('maturity_days_range', (60, 120)),
                        harvest_index_range=ag_data.get('harvest_index_range', (0.3, 0.6)),
                        is_cover_crop=ag_data.get('is_cover_crop', False),
                        is_cash_crop=ag_data.get('is_cash_crop', True),
                        rotation_benefits=ag_data.get('rotation_benefits', []),
                        companion_plants=ag_data.get('companion_plants', []),
                        incompatible_plants=ag_data.get('incompatible_plants', [])
                    )
            except Exception as e:
                logger.warning(f"Database agricultural classification lookup failed: {e}")

        reference_crop = self.reference_crop_index.get(crop_name) if crop_name else None
        if reference_crop and reference_crop.agricultural_classification:
            return reference_crop.agricultural_classification.copy(deep=True)

        # Fallback to knowledge base rules
        primary_category = None
        primary_use = None
        life_cycle = LifeCycle.ANNUAL  # Default

        for category, crops in self.classification_rules.items():
            if crop_name in crops:
                if category == "grain_crops":
                    primary_category = CropCategory.GRAIN
                    primary_use = PrimaryUse.FOOD_HUMAN
                elif category == "oilseed_crops":
                    primary_category = CropCategory.OILSEED
                    primary_use = PrimaryUse.INDUSTRIAL
                elif category == "legume_crops":
                    primary_category = CropCategory.LEGUME
                    primary_use = PrimaryUse.FOOD_HUMAN
                elif category == "forage_crops":
                    primary_category = CropCategory.FORAGE
                    primary_use = PrimaryUse.FEED_LIVESTOCK
                    life_cycle = LifeCycle.PERENNIAL
                elif category == "vegetable_crops":
                    primary_category = CropCategory.VEGETABLE
                    primary_use = PrimaryUse.FOOD_HUMAN
                break

        if not primary_category:
            primary_category = CropCategory.SPECIALTY
            primary_use = PrimaryUse.FOOD_HUMAN

        return CropAgriculturalClassification(
            id=uuid4(),
            primary_category=primary_category,
            secondary_categories=[],
            primary_use=primary_use,
            secondary_uses=[],
            life_cycle=life_cycle,
            growth_habit="upright",  # Default
            plant_height_range=(30, 200),  # Default range in cm
            maturity_days_range=(60, 120),  # Default range
            harvest_index_range=(0.3, 0.6),  # Default range
            is_cover_crop=crop_name in ["clover", "ryegrass", "crimson clover"],
            is_cash_crop=primary_use in [PrimaryUse.FOOD_HUMAN, PrimaryUse.INDUSTRIAL],
            rotation_benefits=["soil_improvement"] if taxonomy.family == "Fabaceae" else [],
            companion_plants=[],
            incompatible_plants=[]
        )

    def _get_family_from_genus_species(self, genus: str, species: str) -> str:
        """Get botanical family from genus and species."""
        genus_family_map = {
            "Triticum": "Poaceae",
            "Zea": "Poaceae",
            "Glycine": "Fabaceae", 
            "Oryza": "Poaceae",
            "Hordeum": "Poaceae",
            "Brassica": "Brassicaceae",
            "Helianthus": "Asteraceae"
        }
        return genus_family_map.get(genus, "Unknown")

    def _get_order_from_family(self, family: str) -> str:
        """Get botanical order from family."""
        family_order_map = {
            "Poaceae": "Poales",
            "Fabaceae": "Fabales",
            "Brassicaceae": "Brassicales",
            "Asteraceae": "Asterales",
            "Solanaceae": "Solanales"
        }
        return family_order_map.get(family, "Unknown")

    def _get_botanical_authority(self, genus: str, species: str) -> str:
        """Get botanical naming authority."""
        # Common authorities for major crops
        authorities = {
            ("Triticum", "aestivum"): "L.",
            ("Zea", "mays"): "L.",
            ("Glycine", "max"): "(L.) Merr.",
            ("Oryza", "sativa"): "L.",
            ("Hordeum", "vulgare"): "L."
        }
        return authorities.get((genus, species), "L.")

    def _get_typical_ploidy(self, crop_name: str) -> int:
        """Get typical ploidy level for crop."""
        ploidy_map = {
            "wheat": 6,  # Hexaploid
            "corn": 2,   # Diploid
            "soybean": 2, # Diploid
            "rice": 2,   # Diploid
            "barley": 2  # Diploid
        }
        return ploidy_map.get(crop_name, 2)

    def _get_chromosome_count(self, crop_name: str) -> int:
        """Get chromosome count for crop."""
        chromosome_map = {
            "wheat": 42,   # 2n = 6x = 42
            "corn": 20,    # 2n = 20
            "soybean": 40, # 2n = 40
            "rice": 24,    # 2n = 24
            "barley": 14   # 2n = 14
        }
        return chromosome_map.get(crop_name, 0)

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity using simple algorithm."""
        # Simple Levenshtein-based similarity
        if len(str1) == 0 or len(str2) == 0:
            return 0.0
        
        # Calculate common characters
        common = sum(1 for a, b in zip(str1, str2) if a == b)
        max_len = max(len(str1), len(str2))
        
        return common / max_len if max_len > 0 else 0.0

    async def validate_crop_data(
        self, 
        request: ValidationRequest
    ) -> ValidationResponse:
        """
        Validate comprehensive crop data for accuracy and completeness.
        
        Args:
            request: Crop data validation request
            
        Returns:
            Validation results with detailed feedback
        """
        try:
            validation_results = []
            overall_valid = True

            # Validate taxonomic hierarchy
            if request.crop_data.taxonomic_hierarchy:
                taxonomic_result = await self._validate_taxonomic_hierarchy(
                    request.crop_data.taxonomic_hierarchy
                )
                validation_results.append(taxonomic_result)
                if not taxonomic_result.is_valid:
                    overall_valid = False

            # Validate agricultural classification
            if request.crop_data.agricultural_classification:
                agricultural_result = await self._validate_agricultural_classification(
                    request.crop_data.agricultural_classification
                )
                validation_results.append(agricultural_result)
                if not agricultural_result.is_valid:
                    overall_valid = False

            # Validate climate adaptations
            if request.crop_data.climate_adaptations:
                climate_result = await self._validate_climate_adaptations(
                    request.crop_data.climate_adaptations
                )
                validation_results.append(climate_result)
                if not climate_result.is_valid:
                    overall_valid = False

            # Validate soil requirements
            if request.crop_data.soil_requirements:
                soil_result = await self._validate_soil_requirements(
                    request.crop_data.soil_requirements
                )
                validation_results.append(soil_result)
                if not soil_result.is_valid:
                    overall_valid = False

            return ValidationResponse(
                success=overall_valid,
                validation_results=validation_results,
                overall_validation_status=overall_valid,
                message="Validation completed successfully" if overall_valid else "Validation failed"
            )

        except Exception as e:
            logger.error(f"Error in crop data validation: {str(e)}")
            error_result = ValidationResult(
                field_name="general",
                is_valid=False,
                error_message=f"Validation error: {str(e)}"
            )
            return ValidationResponse(
                success=False,
                validation_results=[error_result],
                overall_validation_status=False,
                message=f"Validation error: {str(e)}"
            )

    async def _validate_taxonomic_hierarchy(self, taxonomy: CropTaxonomicHierarchy) -> ValidationResult:
        """Validate taxonomic hierarchy for botanical accuracy."""
        # Check required fields
        if not all([taxonomy.kingdom, taxonomy.phylum, taxonomy.family, taxonomy.genus, taxonomy.species]):
            return ValidationResult(
                field_name="taxonomic_hierarchy",
                is_valid=False,
                error_message="Missing required taxonomic fields"
            )

        # Validate kingdom
        if taxonomy.kingdom != "Plantae":
            return ValidationResult(
                field_name="taxonomic_hierarchy.kingdom",
                is_valid=False,
                error_message="Kingdom must be 'Plantae' for crops"
            )

        # Validate family consistency
        known_families = set(self.crop_families.keys())
        if taxonomy.family not in known_families:
            return ValidationResult(
                field_name="taxonomic_hierarchy.family",
                is_valid=False,
                error_message=f"Unknown or uncommon plant family: {taxonomy.family}",
                warnings=["Please verify this is a legitimate botanical family"]
            )

        return ValidationResult(
            field_name="taxonomic_hierarchy",
            is_valid=True,
            message="Taxonomic hierarchy is valid"
        )

    async def _validate_agricultural_classification(
        self, 
        classification: CropAgriculturalClassification
    ) -> ValidationResult:
        """Validate agricultural classification for consistency."""
        # Check maturity days range
        if classification.maturity_days_range:
            min_days, max_days = classification.maturity_days_range
            if min_days >= max_days or min_days < 10 or max_days > 400:
                return ValidationResult(
                    field_name="agricultural_classification.maturity_days_range",
                    is_valid=False,
                    error_message="Invalid maturity days range"
                )

        # Check harvest index range
        if classification.harvest_index_range:
            min_hi, max_hi = classification.harvest_index_range
            if min_hi >= max_hi or min_hi < 0 or max_hi > 1:
                return ValidationResult(
                    field_name="agricultural_classification.harvest_index_range",
                    is_valid=False,
                    error_message="Harvest index must be between 0 and 1"
                )

        return ValidationResult(
            field_name="agricultural_classification",
            is_valid=True,
            message="Agricultural classification is valid"
        )

    async def _validate_climate_adaptations(self, climate: CropClimateAdaptations) -> ValidationResult:
        """Validate climate adaptation requirements."""
        # Check temperature ranges
        if climate.temperature_range:
            min_temp, max_temp = climate.temperature_range
            if min_temp >= max_temp or min_temp < -50 or max_temp > 60:
                return ValidationResult(
                    field_name="climate_adaptations.temperature_range",
                    is_valid=False,
                    error_message="Invalid temperature range (must be -50°C to 60°C)"
                )

        # Check precipitation range
        if climate.precipitation_range:
            min_precip, max_precip = climate.precipitation_range
            if min_precip >= max_precip or min_precip < 0 or max_precip > 5000:
                return ValidationResult(
                    field_name="climate_adaptations.precipitation_range",
                    is_valid=False,
                    error_message="Invalid precipitation range (must be 0-5000mm)"
                )

        return ValidationResult(
            field_name="climate_adaptations",
            is_valid=True,
            message="Climate adaptations are valid"
        )

    async def _validate_soil_requirements(self, soil: CropSoilRequirements) -> ValidationResult:
        """Validate soil requirements."""
        # Check pH range
        if soil.ph_range:
            min_ph, max_ph = soil.ph_range
            if min_ph >= max_ph or min_ph < 3.0 or max_ph > 10.0:
                return ValidationResult(
                    field_name="soil_requirements.ph_range",
                    is_valid=False,
                    error_message="pH range must be between 3.0 and 10.0"
                )

        return ValidationResult(
            field_name="soil_requirements",
            is_valid=True,
            message="Soil requirements are valid"
        )

    def _calculate_overall_confidence(self, results: List[ValidationResult]) -> float:
        """Calculate overall confidence score from validation results."""
        if not results:
            return 0.0

        valid_count = sum(1 for result in results if result.is_valid)
        return valid_count / len(results)

    async def list_reference_crops(
        self,
        category: Optional[str] = None,
        family: Optional[str] = None,
        region: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[ComprehensiveCropData]:
        """Return reference crops with optional filtering and pagination."""
        filtered_crops: List[ComprehensiveCropData] = []

        for crop in self.reference_crops:
            include_crop = True

            if category and crop.agricultural_classification:
                crop_category_value = crop.agricultural_classification.crop_category.value
                if crop_category_value != category:
                    include_crop = False

            if include_crop and family and crop.taxonomic_hierarchy:
                family_value = crop.taxonomic_hierarchy.family
                if family_value.lower() != family.lower():
                    include_crop = False

            if include_crop and region and crop.climate_adaptations:
                zones = crop.climate_adaptations.hardiness_zones
                zone_match = False
                for zone in zones:
                    if zone == region:
                        zone_match = True
                        break
                if not zone_match:
                    include_crop = False

            if include_crop:
                filtered_crops.append(crop)

        paginated_crops: List[ComprehensiveCropData] = []
        index = 0
        for crop in filtered_crops:
            if index >= offset and len(paginated_crops) < limit:
                paginated_crops.append(crop)
            index += 1
            if len(paginated_crops) >= limit:
                break

        return paginated_crops

    async def get_reference_families(self) -> List[str]:
        """Return sorted list of families represented in reference dataset."""
        family_counts: Dict[str, int] = {}

        for crop in self.reference_crops:
            taxonomy = crop.taxonomic_hierarchy
            if taxonomy and taxonomy.family:
                family_name = taxonomy.family
                if family_name not in family_counts:
                    family_counts[family_name] = 0
                family_counts[family_name] += 1

        sorted_families: List[str] = []
        for family_name in sorted(family_counts.keys()):
            sorted_families.append(family_name)
        return sorted_families

    async def get_comprehensive_crop_data(
        self,
        crop_id: UUID
    ) -> Optional[ComprehensiveCropData]:
        """
        Get comprehensive crop data by ID from database.
        
        Args:
            crop_id: UUID of the crop
            
        Returns:
            Complete crop data or None if not found
        """
        if not self.database_available:
            logger.warning("Database not available for comprehensive crop data lookup")
            return None
            
        try:
            crop_data = self.db.get_crop_by_id(crop_id)
            if not crop_data:
                return None
                
            # Convert database format to ComprehensiveCropData
            return self._convert_db_to_comprehensive_crop_data(crop_data)
            
        except Exception as e:
            logger.error(f"Error getting comprehensive crop data for {crop_id}: {e}")
            return None

    def _convert_db_to_comprehensive_crop_data(self, db_data: Dict[str, Any]) -> ComprehensiveCropData:
        """Convert database format to ComprehensiveCropData Pydantic model."""
        
        # Extract taxonomic hierarchy
        taxonomic_hierarchy = None
        if 'taxonomic_hierarchy' in db_data:
            tax_data = db_data['taxonomic_hierarchy']
            taxonomic_hierarchy = CropTaxonomicHierarchy(
                id=tax_data.get('id', uuid4()),
                kingdom=tax_data.get('kingdom', 'Plantae'),
                phylum=tax_data.get('phylum', 'Tracheophyta'),
                class_name=tax_data.get('class_name', 'Unknown'),
                order=tax_data.get('order', 'Unknown'),
                family=tax_data.get('family', 'Unknown'),
                genus=tax_data.get('genus', 'Unknown'),
                species=tax_data.get('species', 'Unknown'),
                common_names=tax_data.get('common_names', []),
                botanical_authority=tax_data.get('botanical_authority', ''),
                is_hybrid=tax_data.get('is_hybrid', False),
                ploidy_level=tax_data.get('ploidy_level', 2),
                chromosome_count=tax_data.get('chromosome_count', 0)
            )
        
        # Extract agricultural classification
        agricultural_classification = None
        if 'agricultural_classification' in db_data:
            ag_data = db_data['agricultural_classification']
            agricultural_classification = CropAgriculturalClassification(
                id=ag_data.get('id', uuid4()),
                primary_category=CropCategory(ag_data.get('crop_category', 'specialty')),
                secondary_categories=[],
                primary_use=PrimaryUse(ag_data.get('primary_use', 'food_human')),
                secondary_uses=[],
                life_cycle=LifeCycle(ag_data.get('plant_type', 'annual')),
                growth_habit=ag_data.get('growth_habit', 'upright'),
                plant_height_range=ag_data.get('plant_height_range', (0, 0)),
                maturity_days_range=ag_data.get('maturity_days_range', (0, 0)),
                harvest_index_range=ag_data.get('harvest_index_range', (0.0, 0.0)),
                is_cover_crop=ag_data.get('is_cover_crop', False),
                is_cash_crop=ag_data.get('is_cash_crop', True),
                rotation_benefits=ag_data.get('rotation_benefits', []),
                companion_plants=ag_data.get('companion_plants', []),
                incompatible_plants=ag_data.get('incompatible_plants', [])
            )
        
        # Extract climate adaptations
        climate_adaptations = None
        if 'climate_adaptations' in db_data:
            climate_data = db_data['climate_adaptations']
            climate_adaptations = CropClimateAdaptations(
                id=climate_data.get('id', uuid4()),
                hardiness_zones=climate_data.get('hardiness_zones', []),
                temperature_range=climate_data.get('temperature_range', (0, 0)),
                precipitation_range=climate_data.get('precipitation_range', (0, 0)),
                climate_zones=[ClimateZone(zone) for zone in climate_data.get('climate_zones', [])],
                drought_tolerance=climate_data.get('drought_tolerance', 'moderate'),
                heat_tolerance=climate_data.get('heat_tolerance', 'moderate'),
                cold_tolerance=climate_data.get('cold_tolerance', 'moderate'),
                photoperiod_sensitivity=PhotoperiodSensitivity(climate_data.get('photoperiod_sensitivity', 'neutral')),
                seasonal_requirements=climate_data.get('seasonal_requirements', {}),
                elevation_range=climate_data.get('elevation_range', (0, 3000))
            )
            
        # Extract soil requirements
        soil_requirements = None
        if 'soil_requirements' in db_data:
            soil_data = db_data['soil_requirements']
            soil_requirements = CropSoilRequirements(
                id=soil_data.get('id', uuid4()),
                ph_range=soil_data.get('ph_range', (6.0, 7.5)),
                preferred_textures=[SoilType(texture) for texture in soil_data.get('preferred_textures', ['loam'])],
                drainage_class=DrainageClass(soil_data.get('drainage_requirement', 'well_drained')),
                organic_matter_range=soil_data.get('organic_matter_range', (2.0, 5.0)),
                salinity_tolerance=SalinityTolerance(soil_data.get('salinity_tolerance', 'low')),
                nutrient_requirements=soil_data.get('nutrient_requirements', {}),
                soil_depth_requirements=soil_data.get('soil_depth_requirements', (30, 100)),
                compaction_sensitivity=soil_data.get('compaction_sensitivity', 'moderate')
            )
        
        # Extract nutritional profile
        nutritional_profile = None
        if 'nutritional_profile' in db_data:
            nutr_data = db_data['nutritional_profile']
            nutritional_profile = CropNutritionalProfile(
                id=nutr_data.get('id', uuid4()),
                macronutrients=nutr_data.get('macronutrients', {}),
                micronutrients=nutr_data.get('micronutrients', {}),
                vitamins=nutr_data.get('vitamins', {}),
                minerals=nutr_data.get('minerals', {}),
                calories_per_100g=nutr_data.get('calories_per_100g', 0),
                protein_content=nutr_data.get('protein_content', 0.0),
                carbohydrate_content=nutr_data.get('carbohydrate_content', 0.0),
                fat_content=nutr_data.get('fat_content', 0.0),
                fiber_content=nutr_data.get('fiber_content', 0.0),
                water_content=nutr_data.get('water_content', 0.0)
            )
        
        return ComprehensiveCropData(
            crop_id=db_data.get('crop_id', uuid4()),
            crop_name=db_data.get('crop_name', ''),
            taxonomic_hierarchy=taxonomic_hierarchy,
            agricultural_classification=agricultural_classification,
            climate_adaptations=climate_adaptations,
            soil_requirements=soil_requirements,
            nutritional_profile=nutritional_profile,
            search_keywords=db_data.get('search_keywords', []),
            tags=db_data.get('tags', []),
            data_source="database",
            confidence_score=0.95,
            updated_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )

    async def process_bulk_operation(
        self, 
        request
    ) -> BulkOperationResponse:
        """
        Process multiple crop data entries with batch validation and processing.
        
        Args:
            request: Bulk crop data processing request
            
        Returns:
            Batch processing results with individual validation outcomes
        """
        try:
            processed_crops = []
            failed_crops = []
            
            # Get the crop data list from the request
            crop_data_list = request.operation_data if hasattr(request, 'operation_data') else []
            
            for i, crop_data in enumerate(crop_data_list):
                try:
                    # Validate each crop
                    # Convert data to proper format for validation if needed
                    validation_request = ValidationRequest(
                        request_id=f"bulk-{i}", 
                        operation_type="validate_taxonomy",
                        crop_data=crop_data if isinstance(crop_data, (list, tuple)) else [crop_data]
                    )
                    validation_result = await self.validate_crop_data(validation_request)
                    
                    # Check if validation passed
                    validation_passed = validation_result.success if hasattr(validation_result, 'success') else True
                    
                    if validation_passed or (hasattr(request, 'allow_partial_validation') and request.allow_partial_validation):
                        # Process valid crops
                        processed_crop = {
                            "index": i,
                            "crop_data": crop_data,
                            "validation_result": validation_result,
                            "processed_at": datetime.utcnow()
                        }
                        processed_crops.append(processed_crop)
                    else:
                        failed_crops.append({
                            "index": i,
                            "crop_data": crop_data,
                            "validation_result": validation_result,
                            "reason": "Validation failed"
                        })
                        
                except Exception as e:
                    failed_crops.append({
                        "index": i,
                        "crop_data": crop_data,
                        "reason": f"Processing error: {str(e)}"
                    })

            return BulkOperationResponse(
                success=True,
                total_processed=len(processed_crops),
                successful_operations=len(processed_crops),
                failed_operations=len(failed_crops),
                skipped_operations=0,
                operation_results=[],
                message="Bulk operation completed",
                processing_rate_per_second=0.0  # Calculate as needed
            )

        except Exception as e:
            logger.error(f"Error in bulk crop data processing: {str(e)}")
            return BulkOperationResponse(
                success=False,
                total_processed=0,
                successful_operations=0,
                failed_operations=len(request.operation_data) if hasattr(request, 'operation_data') else 0,
                skipped_operations=0,
                operation_results=[],
                message=f"Error in bulk processing: {str(e)}",
                processing_rate_per_second=0.0
            )


# Create service instance with database connection
import os
crop_taxonomy_service = CropTaxonomyService(
    database_url=os.getenv('DATABASE_URL')
)
