"""
Crop Attribute Tagging Service

Provides automated crop attribute tagging, manual tag management,
and validation workflows for the crop taxonomy system.
"""

import logging
import sys
from datetime import datetime
from importlib import import_module
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from uuid import UUID

_existing_models_module = sys.modules.get('models')
if _existing_models_module is not None and not hasattr(_existing_models_module, 'Base'):
    sys.modules.pop('models')

_repo_root = Path(__file__).resolve().parents[4]
_sqlalchemy_models_path = _repo_root / 'databases' / 'python'
_sqlalchemy_path_str = str(_sqlalchemy_models_path)
if _sqlalchemy_path_str not in sys.path:
    sys.path.insert(0, _sqlalchemy_path_str)

_src_package_path = Path(__file__).resolve().parents[1]
_src_path_str = str(_src_package_path)
_src_path_removed = False
if _src_path_str in sys.path:
    sys.path.remove(_src_path_str)
    _src_path_removed = True

CropTaxonomyDatabase = None
_database_import_candidates = [
    'src.database.crop_taxonomy_db',
    '..database.crop_taxonomy_db',
    'database.crop_taxonomy_db'
]

for _module_path in _database_import_candidates:
    try:  # pragma: no cover - dynamic import for flexible environments
        if _module_path.startswith('..'):
            _module = import_module(_module_path, package=__package__)
        else:
            _module = import_module(_module_path)
        CropTaxonomyDatabase = getattr(_module, 'CropTaxonomyDatabase', None)
        if CropTaxonomyDatabase is not None:
            break
    except ModuleNotFoundError as _exc:
        if getattr(_exc, 'name', '') == 'geoalchemy2':
            CropTaxonomyDatabase = None
            break
        continue
    except ImportError:
        continue

if _src_path_removed:
    sys.path.insert(0, _src_path_str)

_service_models_module = None
for _service_path in (
    'src.models.service_models',
    '..models.service_models',
    'models.service_models'
):
    try:
        if _service_path.startswith('..'):
            _service_models_module = import_module(_service_path, package=__package__)
        else:
            _service_models_module = import_module(_service_path)
        break
    except ImportError:
        continue

_filtering_models_module = None
for _filter_path in (
    'src.models.crop_filtering_models',
    '..models.crop_filtering_models',
    'models.crop_filtering_models'
):
    try:
        if _filter_path.startswith('..'):
            _filtering_models_module = import_module(_filter_path, package=__package__)
        else:
            _filtering_models_module = import_module(_filter_path)
        break
    except ImportError:
        continue

if _service_models_module is None or _filtering_models_module is None:
    raise ImportError("Unable to load crop taxonomy service models for attribute tagging")

AutoTagGenerationRequest = _service_models_module.AutoTagGenerationRequest
AutoTagGenerationResponse = _service_models_module.AutoTagGenerationResponse
TagManagementRequest = _service_models_module.TagManagementRequest
TagManagementResponse = _service_models_module.TagManagementResponse
CropAttributeTagPayload = _service_models_module.CropAttributeTagPayload
TagCategory = _service_models_module.TagCategory
TagType = _service_models_module.TagType
TagValidationStatus = _service_models_module.TagValidationStatus
TagManagementInstruction = _service_models_module.TagManagementInstruction
TagManagementAction = _service_models_module.TagManagementAction
CropFilteringAttributes = _filtering_models_module.CropFilteringAttributes


logger = logging.getLogger(__name__)


class CropAttributeTaggingService:
    """Service implementing crop attribute tagging workflows."""

    def __init__(self, database_url: Optional[str] = None):
        db_class = CropTaxonomyDatabase
        if db_class is not None:
            try:
                self.db = db_class(database_url)
                self.database_available = self.db.test_connection()
            except Exception as exc:
                logger.warning("Crop attribute tagging database unavailable: %s", exc)
                self.db = None
                self.database_available = False
        else:
            self.db = None
            self.database_available = False

        if not self.database_available:
            logger.warning("CropAttributeTaggingService running without database integration")

    # ------------------------------------------------------------------
    # Normalization and validation helpers
    # ------------------------------------------------------------------

    def _normalize_text(self, text: Optional[str]) -> Optional[str]:
        """Normalize text for comparison without using regular expressions."""
        if text is None:
            return None
        normalized = CropFilteringAttributes._normalize_term(str(text))  # type: ignore[attr-defined]
        if not normalized:
            return None
        return normalized

    def _parse_datetime_value(self, value: Any) -> Optional[datetime]:
        """Parse datetime values from strings or datetime objects."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            logger.debug("Unable to parse datetime from value: %s", value)
            return None

    def _validate_tag_payload(
        self,
        payload: Dict[str, Any],
        notes: List[str]
    ) -> bool:
        """Validate tag payload against basic agricultural tagging rules."""
        required_fields = ['tag_name', 'tag_category', 'tag_type', 'validation_status']
        for field_name in required_fields:
            if payload.get(field_name) is None:
                notes.append(f"Missing required field '{field_name}'")
                return False

        normalized_value = payload.get('normalized_tag')
        if normalized_value is None:
            notes.append("Normalized tag value missing")
            return False

        try:
            TagCategory(payload.get('tag_category'))
        except Exception:
            notes.append("Invalid tag category")
            return False

        try:
            TagType(payload.get('tag_type'))
        except Exception:
            notes.append("Invalid tag type")
            return False

        try:
            TagValidationStatus(payload.get('validation_status'))
        except Exception:
            notes.append("Invalid validation status")
            return False

        return True

    def _build_tag_payload(
        self,
        crop_id: UUID,
        tag_name: str,
        category: TagCategory,
        tag_type: TagType,
        validation_status: TagValidationStatus,
        confidence: float,
        source: str,
        parent_tag_id: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Construct a tag payload dictionary if valid."""
        normalized_value = self._normalize_text(tag_name)
        if normalized_value is None:
            return None

        payload: Dict[str, Any] = {
            'crop_id': crop_id,
            'tag_name': tag_name,
            'normalized_tag': normalized_value,
            'tag_category': category.value,
            'tag_type': tag_type.value,
            'validation_status': validation_status.value,
            'confidence_score': confidence,
            'source': source,
            'usage_count': 0,
            'last_generated_at': datetime.utcnow(),
            'parent_tag_id': parent_tag_id,
            'validation_notes': None
        }

        validation_notes: List[str] = []
        if not self._validate_tag_payload(payload, validation_notes):
            for note in validation_notes:
                logger.debug("Tag payload validation note: %s", note)
            return None

        return payload

    def _convert_record_to_payload(self, record: Dict[str, Any]) -> Optional[CropAttributeTagPayload]:
        """Convert database dictionary to Pydantic payload."""
        try:
            tag_id_value = record.get('tag_id')
            tag_uuid = UUID(tag_id_value) if tag_id_value else None
            parent_value = record.get('parent_tag_id')
            parent_uuid = UUID(parent_value) if parent_value else None
            payload = CropAttributeTagPayload(
                tag_id=tag_uuid,
                crop_id=UUID(str(record.get('crop_id'))),
                tag_name=record.get('tag_name', ''),
                normalized_tag=record.get('normalized_tag'),
                tag_category=TagCategory(record.get('tag_category')),
                tag_type=TagType(record.get('tag_type', 'auto')),
                validation_status=TagValidationStatus(record.get('validation_status', 'pending')),
                confidence_score=record.get('confidence_score'),
                source=record.get('source'),
                usage_count=record.get('usage_count') or 0,
                last_used_at=self._parse_datetime_value(record.get('last_used_at')),
                last_generated_at=self._parse_datetime_value(record.get('last_generated_at')),
                parent_tag_id=parent_uuid,
                validation_notes=record.get('validation_notes')
            )
            return payload
        except Exception as exc:
            logger.error("Failed to convert tag record to payload: %s", exc)
            return None

    # ------------------------------------------------------------------
    # Data retrieval helpers
    # ------------------------------------------------------------------

    def _load_crop(self, crop_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve crop data using database if available."""
        if not self.database_available or self.db is None:
            return None
        try:
            return self.db.get_crop_by_id(crop_id)
        except Exception as exc:
            logger.error("Error loading crop %s: %s", crop_id, exc)
            return None

    def _load_existing_tags(
        self,
        crop_id: UUID,
        include_manual: bool
    ) -> Tuple[List[CropAttributeTagPayload], Set[str]]:
        """Load existing tags and build a set of normalized keys."""
        payloads: List[CropAttributeTagPayload] = []
        normalized_keys: Set[str] = set()

        if not self.database_available or self.db is None:
            return payloads, normalized_keys

        try:
            records = self.db.get_attribute_tags(crop_id)
        except Exception as exc:
            logger.error("Unable to load existing tags for %s: %s", crop_id, exc)
            return payloads, normalized_keys

        for record in records:
            payload = self._convert_record_to_payload(record)
            if payload is None:
                continue
            if not include_manual and payload.tag_type == TagType.MANUAL:
                continue
            payloads.append(payload)
            if payload.normalized_tag:
                key_value = f"{payload.tag_category.value}:{payload.normalized_tag}"
                normalized_keys.add(key_value)

        return payloads, normalized_keys

    # ------------------------------------------------------------------
    # Auto-tag generation
    # ------------------------------------------------------------------

    async def auto_generate_tags(
        self,
        request: AutoTagGenerationRequest
    ) -> AutoTagGenerationResponse:
        """Generate crop attribute tags using existing taxonomy data."""
        crop_id = request.crop_id
        crop_data = self._load_crop(crop_id)

        existing_tags, existing_keys = self._load_existing_tags(
            crop_id,
            include_manual=request.include_manual_tags
        )

        generation_notes: List[str] = []
        generated_payloads: List[Dict[str, Any]] = []
        generated_keys: Set[str] = set()
        confidence_totals: Dict[str, float] = {}
        confidence_counts: Dict[str, int] = {}

        if crop_data is None:
            generation_notes.append("Crop data unavailable for auto-tagging")
            response = AutoTagGenerationResponse(
                crop_id=crop_id,
                generated_tags=[],
                existing_tags=existing_tags,
                confidence_summary={},
                generation_notes=generation_notes
            )
            return response

        # Helper to add payload respecting limits and duplicates
        def add_payload(candidate: Optional[Dict[str, Any]]) -> None:
            if candidate is None:
                return
            if len(generated_payloads) >= request.maximum_tags:
                return
            normalized_value = candidate.get('normalized_tag')
            category_value = candidate.get('tag_category')
            if normalized_value is None or category_value is None:
                return
            key_value = f"{category_value}:{normalized_value}"
            if key_value in existing_keys or key_value in generated_keys:
                return
            if request.forced_categories and TagCategory(category_value) not in request.forced_categories:
                return
            generated_payloads.append(candidate)
            generated_keys.add(key_value)
            if category_value not in confidence_totals:
                confidence_totals[category_value] = 0.0
            if category_value not in confidence_counts:
                confidence_counts[category_value] = 0
            confidence_value = candidate.get('confidence_score') or 0.0
            confidence_totals[category_value] = confidence_totals[category_value] + confidence_value
            confidence_counts[category_value] = confidence_counts[category_value] + 1

        taxonomic_hierarchy = crop_data.get('taxonomic_hierarchy') or {}
        agricultural = crop_data.get('agricultural_classification') or {}
        climate = crop_data.get('climate_adaptations') or {}
        soil = crop_data.get('soil_requirements') or {}

        # Taxonomy-driven tags
        taxonomy_pairs: List[Tuple[str, Optional[str]]] = [
            ("family", taxonomic_hierarchy.get('family')),
            ("genus", taxonomic_hierarchy.get('genus')),
            ("species", taxonomic_hierarchy.get('species')),
            ("category", crop_data.get('crop_category'))
        ]
        for descriptor, value in taxonomy_pairs:
            if value:
                tag_label = f"{value} {descriptor}" if descriptor != "category" else value
                payload = self._build_tag_payload(
                    crop_id=crop_id,
                    tag_name=tag_label,
                    category=TagCategory.TAXONOMY,
                    tag_type=TagType.AUTO,
                    validation_status=TagValidationStatus.PENDING,
                    confidence=0.9,
                    source='taxonomy-auto'
                )
                add_payload(payload)

        # Agricultural characteristics
        agronomic_pairs: List[Tuple[TagCategory, Optional[str], float, str]] = [
            (TagCategory.AGRONOMIC, agricultural.get('primary_use'), 0.85, 'primary-use'),
            (TagCategory.MANAGEMENT, agricultural.get('growth_habit'), 0.75, 'growth-habit'),
            (TagCategory.MANAGEMENT, agricultural.get('plant_type'), 0.75, 'plant-type'),
            (TagCategory.AGRONOMIC, agricultural.get('photosynthesis_type'), 0.7, 'photosynthesis-type')
        ]
        for category_enum, value, confidence_value, source_suffix in agronomic_pairs:
            if value:
                payload = self._build_tag_payload(
                    crop_id=crop_id,
                    tag_name=value,
                    category=category_enum,
                    tag_type=TagType.AUTO,
                    validation_status=TagValidationStatus.PENDING,
                    confidence=confidence_value,
                    source=f"agronomic-{source_suffix}"
                )
                add_payload(payload)

        if agricultural.get('secondary_uses'):
            for use_value in agricultural.get('secondary_uses'):
                if not use_value:
                    continue
                payload = self._build_tag_payload(
                    crop_id=crop_id,
                    tag_name=str(use_value),
                    category=TagCategory.AGRONOMIC,
                    tag_type=TagType.AUTO,
                    validation_status=TagValidationStatus.PENDING,
                    confidence=0.7,
                    source='secondary-use'
                )
                add_payload(payload)

        if agricultural.get('nitrogen_fixing') is True:
            payload = self._build_tag_payload(
                crop_id=crop_id,
                tag_name='nitrogen-fixing',
                category=TagCategory.SUSTAINABILITY,
                tag_type=TagType.AUTO,
                validation_status=TagValidationStatus.PENDING,
                confidence=0.8,
                source='nitrogen-trait'
            )
            add_payload(payload)

        # Climate adaptations
        tolerance = climate.get('tolerance') or {}
        if tolerance.get('drought'):
            tag_value = f"drought-{tolerance.get('drought')}"
            payload = self._build_tag_payload(
                crop_id=crop_id,
                tag_name=tag_value,
                category=TagCategory.CLIMATE,
                tag_type=TagType.AUTO,
                validation_status=TagValidationStatus.PENDING,
                confidence=0.75,
                source='climate-tolerance'
            )
            add_payload(payload)

        if climate.get('hardiness_zones'):
            for zone in climate.get('hardiness_zones'):
                if not zone:
                    continue
                payload = self._build_tag_payload(
                    crop_id=crop_id,
                    tag_name=f"hardiness-zone-{zone}",
                    category=TagCategory.CLIMATE,
                    tag_type=TagType.AUTO,
                    validation_status=TagValidationStatus.PENDING,
                    confidence=0.7,
                    source='hardiness-zone'
                )
                add_payload(payload)

        # Soil characteristics
        if soil.get('preferred_textures'):
            for texture in soil.get('preferred_textures'):
                if not texture:
                    continue
                payload = self._build_tag_payload(
                    crop_id=crop_id,
                    tag_name=f"prefers-{texture}",
                    category=TagCategory.SOIL,
                    tag_type=TagType.AUTO,
                    validation_status=TagValidationStatus.PENDING,
                    confidence=0.7,
                    source='soil-texture'
                )
                add_payload(payload)

        drainage_requirement = soil.get('drainage_requirement')
        if drainage_requirement:
            payload = self._build_tag_payload(
                crop_id=crop_id,
                tag_name=f"drainage-{drainage_requirement}",
                category=TagCategory.SOIL,
                tag_type=TagType.AUTO,
                validation_status=TagValidationStatus.PENDING,
                confidence=0.65,
                source='soil-drainage'
            )
            add_payload(payload)

        # Persist generated tags
        saved_records: List[Dict[str, Any]] = []
        if generated_payloads and self.database_available and self.db is not None:
            try:
                saved_records = self.db.bulk_upsert_attribute_tags(crop_id, generated_payloads)
            except Exception as exc:
                logger.error("Failed to persist generated tags for %s: %s", crop_id, exc)
                generation_notes.append("Failed to persist generated tags; returning suggestions only")
                saved_records = generated_payloads
        else:
            saved_records = generated_payloads

        generated_payload_models: List[CropAttributeTagPayload] = []
        for record in saved_records:
            payload_model = self._convert_record_to_payload(record)
            if payload_model:
                generated_payload_models.append(payload_model)

        confidence_summary: Dict[str, float] = {}
        for category_name, total_value in confidence_totals.items():
            count_value = confidence_counts.get(category_name, 0)
            if count_value > 0:
                average_confidence = total_value / count_value
                confidence_summary[category_name] = round(average_confidence, 3)

        response = AutoTagGenerationResponse(
            crop_id=crop_id,
            generated_tags=generated_payload_models,
            existing_tags=existing_tags if request.include_existing_tags else [],
            confidence_summary=confidence_summary,
            generation_notes=generation_notes
        )

        return response

    # ------------------------------------------------------------------
    # Manual tag management
    # ------------------------------------------------------------------

    async def manage_tags(
        self,
        request: TagManagementRequest
    ) -> TagManagementResponse:
        """Process manual tag management actions."""
        crop_id = request.crop_id

        if not self.database_available or self.db is None:
            warning_message = "Database unavailable; cannot manage tags"
            return TagManagementResponse(
                crop_id=crop_id,
                applied_tags=[],
                removed_tag_ids=[],
                validation_updates={},
                warnings=[warning_message],
                processed_instruction_count=0
            )

        applied_records: List[Dict[str, Any]] = []
        removed_ids: List[UUID] = []
        validation_updates: Dict[str, TagValidationStatus] = {}
        warnings: List[str] = []
        processed_count = 0

        for instruction in request.instructions:
            processed_count += 1
            try:
                if instruction.action == TagManagementAction.ADD:
                    tag_payload = instruction.tag
                    if tag_payload is None:
                        warnings.append("Add instruction missing tag payload")
                        continue
                    normalized_value = tag_payload.normalized_tag
                    if not normalized_value:
                        normalized_value = self._normalize_text(tag_payload.tag_name)
                    payload_dict = {
                        'tag_id': tag_payload.tag_id,
                        'crop_id': crop_id,
                        'tag_name': tag_payload.tag_name,
                        'normalized_tag': normalized_value,
                        'tag_category': tag_payload.tag_category.value,
                        'tag_type': TagType.MANUAL.value,
                        'validation_status': tag_payload.validation_status.value,
                        'confidence_score': tag_payload.confidence_score,
                        'source': tag_payload.source or 'manual-entry',
                        'usage_count': tag_payload.usage_count,
                        'last_used_at': tag_payload.last_used_at,
                        'last_generated_at': tag_payload.last_generated_at or datetime.utcnow(),
                        'parent_tag_id': tag_payload.parent_tag_id,
                        'validation_notes': tag_payload.validation_notes
                    }
                    validation_notes: List[str] = []
                    if not self._validate_tag_payload(payload_dict, validation_notes):
                        warnings.extend(validation_notes)
                        continue
                    saved = self.db.bulk_upsert_attribute_tags(crop_id, [payload_dict])
                    for record in saved:
                        applied_records.append(record)

                elif instruction.action == TagManagementAction.UPDATE:
                    tag_payload = instruction.tag
                    if tag_payload is None or instruction.tag_id is None:
                        warnings.append("Update instruction missing tag data or tag_id")
                        continue
                    normalized_value = tag_payload.normalized_tag
                    if not normalized_value:
                        normalized_value = self._normalize_text(tag_payload.tag_name)
                    payload_dict = {
                        'tag_id': instruction.tag_id,
                        'crop_id': crop_id,
                        'tag_name': tag_payload.tag_name,
                        'normalized_tag': normalized_value,
                        'tag_category': tag_payload.tag_category.value,
                        'tag_type': tag_payload.tag_type.value,
                        'validation_status': tag_payload.validation_status.value,
                        'confidence_score': tag_payload.confidence_score,
                        'source': tag_payload.source,
                        'usage_count': tag_payload.usage_count,
                        'last_used_at': tag_payload.last_used_at,
                        'last_generated_at': tag_payload.last_generated_at or datetime.utcnow(),
                        'parent_tag_id': tag_payload.parent_tag_id,
                        'validation_notes': tag_payload.validation_notes
                    }
                    validation_notes = []
                    if not self._validate_tag_payload(payload_dict, validation_notes):
                        warnings.extend(validation_notes)
                        continue
                    saved = self.db.bulk_upsert_attribute_tags(crop_id, [payload_dict])
                    for record in saved:
                        applied_records.append(record)

                elif instruction.action == TagManagementAction.REMOVE:
                    if instruction.tag_id is None:
                        warnings.append("Remove instruction missing tag_id")
                        continue
                    removed_ids.append(instruction.tag_id)

                elif instruction.action == TagManagementAction.VALIDATE:
                    if instruction.tag_id is None:
                        warnings.append("Validate instruction missing tag_id")
                        continue
                    status_value = instruction.validation_status or TagValidationStatus.VALIDATED
                    updated = self.db.update_attribute_tag_validation(
                        tag_id=instruction.tag_id,
                        validation_status=status_value.value,
                        notes=instruction.notes,
                        usage_increment=0
                    )
                    if updated:
                        validation_updates[str(instruction.tag_id)] = status_value
                        applied_records.append(updated)

            except Exception as exc:
                warnings.append(f"Failed to process instruction {instruction.action}: {exc}")
                logger.error("Error processing tag management instruction: %s", exc)

        if removed_ids:
            try:
                self.db.remove_attribute_tags(crop_id, removed_ids)
            except Exception as exc:
                warnings.append(f"Failed to remove tags: {exc}")
                logger.error("Error removing tags for crop %s: %s", crop_id, exc)

        applied_payloads: List[CropAttributeTagPayload] = []
        for record in applied_records:
            payload_model = self._convert_record_to_payload(record)
            if payload_model:
                applied_payloads.append(payload_model)

        response = TagManagementResponse(
            crop_id=crop_id,
            applied_tags=applied_payloads,
            removed_tag_ids=removed_ids,
            validation_updates=validation_updates,
            warnings=warnings,
            processed_instruction_count=processed_count
        )

        return response


import os  # pragma: no cover - runtime configuration

crop_attribute_tagging_service = CropAttributeTaggingService(
    database_url=os.getenv('DATABASE_URL')
)
