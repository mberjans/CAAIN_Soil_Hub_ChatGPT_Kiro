"""Tests for CropAttributeTaggingService."""
import os
import sys
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID, uuid4

import pytest

_TEST_DIR = os.path.dirname(__file__)
_SRC_PARENT = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_SRC_PARENT, 'src')

if _SRC_PARENT not in sys.path:
    sys.path.insert(0, _SRC_PARENT)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from src.services.crop_attribute_service import CropAttributeTaggingService  # type: ignore
from models.service_models import (  # type: ignore
    AutoTagGenerationRequest,
    TagManagementRequest,
    TagManagementInstruction,
    TagManagementAction,
    TagCategory,
    TagType,
    TagValidationStatus,
    CropAttributeTagPayload
)


class DummyTagDatabase:
    """Lightweight stand-in for CropTaxonomyDatabase."""

    def __init__(self, crop_record: Dict[str, Any]):
        self.crop_record = crop_record
        self.stored_payloads: List[Dict[str, Any]] = []
        self.removed_ids: List[UUID] = []

    def test_connection(self) -> bool:
        return True

    def get_crop_by_id(self, crop_id: UUID) -> Dict[str, Any]:
        return self.crop_record

    def get_attribute_tags(self, crop_id: UUID) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        for record in self.stored_payloads:
            result_record = {}
            for key, value in record.items():
                result_record[key] = value
            results.append(result_record)
        return results

    def bulk_upsert_attribute_tags(self, crop_id: UUID, payloads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        saved: List[Dict[str, Any]] = []
        for payload in payloads:
            stored = {}
            for key, value in payload.items():
                stored[key] = value
            if stored.get('tag_id') is None:
                stored['tag_id'] = str(uuid4())
            stored['crop_id'] = str(crop_id)
            if stored.get('last_generated_at') is None:
                stored['last_generated_at'] = datetime.utcnow().isoformat()
            if stored.get('last_used_at') is None:
                stored['last_used_at'] = None

            updated = False
            for existing in self.stored_payloads:
                if existing.get('tag_id') == stored.get('tag_id'):
                    for key, value in stored.items():
                        existing[key] = value
                    updated = True
                    break
            if not updated:
                new_record = {}
                for key, value in stored.items():
                    new_record[key] = value
                self.stored_payloads.append(new_record)

            saved_record = {}
            for key, value in stored.items():
                saved_record[key] = value
            saved.append(saved_record)

        return saved

    def remove_attribute_tags(self, crop_id: UUID, tag_ids: List[UUID]) -> int:
        removed_count = 0
        for tag_id in tag_ids:
            self.removed_ids.append(tag_id)
            filtered_payloads: List[Dict[str, Any]] = []
            for record in self.stored_payloads:
                if record.get('tag_id') == str(tag_id):
                    removed_count += 1
                    continue
                filtered_copy = {}
                for key, value in record.items():
                    filtered_copy[key] = value
                filtered_payloads.append(filtered_copy)
            self.stored_payloads = filtered_payloads
        return removed_count

    def update_attribute_tag_validation(
        self,
        tag_id: UUID,
        validation_status: str,
        notes: str,
        usage_increment: int
    ) -> Dict[str, Any]:
        for record in self.stored_payloads:
            if record.get('tag_id') == str(tag_id):
                record['validation_status'] = validation_status
                record['validation_notes'] = notes
                record['usage_count'] = (record.get('usage_count') or 0) + usage_increment
                record['last_used_at'] = datetime.utcnow().isoformat()
                update_copy = {}
                for key, value in record.items():
                    update_copy[key] = value
                return update_copy
        return {}


@pytest.mark.asyncio
async def test_auto_generate_tags_creates_taxonomy_tags():
    crop_id = uuid4()
    crop_record = {
        'crop_id': str(crop_id),
        'crop_name': 'Test Crop',
        'scientific_name': 'Testus cropus',
        'crop_category': 'grain',
        'crop_family': 'Poaceae',
        'crop_code': 'TEST',
        'crop_status': 'active',
        'is_cover_crop': False,
        'is_companion_crop': False,
        'search_keywords': ['test'],
        'tags': [],
        'attribute_tags': [],
        'nitrogen_fixing': False,
        'typical_yield_range': None,
        'maturity_days_range': None,
        'growing_degree_days': None,
        'taxonomic_hierarchy': {
            'family': 'Poaceae',
            'genus': 'Triticum',
            'species': 'aestivum'
        },
        'agricultural_classification': {
            'primary_use': 'food_human',
            'secondary_uses': ['feed_livestock'],
            'growth_habit': 'annual',
            'plant_type': 'grass',
            'photosynthesis_type': 'C3',
            'nitrogen_fixing': True
        },
        'climate_adaptations': {
            'tolerance': {
                'drought': 'moderate',
                'heat': 'moderate',
                'frost': 'moderate',
                'flooding': 'low'
            },
            'hardiness_zones': ['4', '5']
        },
        'soil_requirements': {
            'preferred_textures': ['loam'],
            'drainage_requirement': 'well_drained'
        }
    }

    service = CropAttributeTaggingService()
    dummy_db = DummyTagDatabase(crop_record)
    service.db = dummy_db
    service.database_available = True

    request = AutoTagGenerationRequest(
        crop_id=crop_id,
        include_existing_tags=False,
        include_related_crops=False,
        include_manual_tags=True,
        maximum_tags=10,
        forced_categories=None
    )

    response = await service.auto_generate_tags(request)

    assert response.crop_id == crop_id
    assert len(response.generated_tags) > 0
    found_taxonomy = False
    for tag in response.generated_tags:
        if tag.tag_category == TagCategory.TAXONOMY:
            found_taxonomy = True
            break
    assert found_taxonomy is True


@pytest.mark.asyncio
async def test_manage_tags_add_update_remove_flow():
    crop_id = uuid4()
    crop_record = {
        'crop_id': str(crop_id),
        'crop_name': 'Manage Crop',
        'scientific_name': 'Manageus cropus',
        'crop_category': 'grain',
        'crop_family': 'Poaceae',
        'crop_code': 'MG',
        'crop_status': 'active',
        'is_cover_crop': False,
        'is_companion_crop': False,
        'search_keywords': [],
        'tags': [],
        'attribute_tags': [],
        'nitrogen_fixing': False,
        'typical_yield_range': None,
        'maturity_days_range': None,
        'growing_degree_days': None,
        'taxonomic_hierarchy': {},
        'agricultural_classification': {},
        'climate_adaptations': {},
        'soil_requirements': {}
    }

    service = CropAttributeTaggingService()
    dummy_db = DummyTagDatabase(crop_record)
    service.db = dummy_db
    service.database_available = True

    add_payload = CropAttributeTagPayload(
        tag_id=None,
        crop_id=crop_id,
        tag_name='manual-tag',
        normalized_tag=None,
        tag_category=TagCategory.SPECIALTY,
        tag_type=TagType.MANUAL,
        validation_status=TagValidationStatus.PENDING,
        confidence_score=0.5,
        source='unit-test',
        usage_count=0,
        last_used_at=None,
        last_generated_at=None,
        parent_tag_id=None,
        validation_notes=None
    )

    add_instruction = TagManagementInstruction(
        action=TagManagementAction.ADD,
        tag=add_payload,
        tag_id=None,
        validation_status=None,
        notes=None
    )

    instructions: List[TagManagementInstruction] = []
    instructions.append(add_instruction)

    request = TagManagementRequest(
        crop_id=crop_id,
        instructions=instructions,
        apply_auto_validation=True
    )

    response = await service.manage_tags(request)

    assert response.processed_instruction_count == 1
    assert len(response.applied_tags) == 1
    stored_tag_id = response.applied_tags[0].tag_id
    assert stored_tag_id is not None

    update_payload = CropAttributeTagPayload(
        tag_id=stored_tag_id,
        crop_id=crop_id,
        tag_name='updated-manual-tag',
        normalized_tag=None,
        tag_category=TagCategory.SPECIALTY,
        tag_type=TagType.MANUAL,
        validation_status=TagValidationStatus.PENDING,
        confidence_score=0.6,
        source='unit-test',
        usage_count=2,
        last_used_at=None,
        last_generated_at=None,
        parent_tag_id=None,
        validation_notes='update'
    )

    update_instruction = TagManagementInstruction(
        action=TagManagementAction.UPDATE,
        tag=update_payload,
        tag_id=stored_tag_id,
        validation_status=None,
        notes=None
    )

    remove_instruction = TagManagementInstruction(
        action=TagManagementAction.REMOVE,
        tag=None,
        tag_id=stored_tag_id,
        validation_status=None,
        notes=None
    )

    validate_instruction = TagManagementInstruction(
        action=TagManagementAction.VALIDATE,
        tag=None,
        tag_id=stored_tag_id,
        validation_status=TagValidationStatus.VALIDATED,
        notes='approved'
    )

    instruction_list: List[TagManagementInstruction] = []
    instruction_list.append(update_instruction)
    instruction_list.append(validate_instruction)
    instruction_list.append(remove_instruction)

    manage_request = TagManagementRequest(
        crop_id=crop_id,
        instructions=instruction_list,
        apply_auto_validation=True
    )

    manage_response = await service.manage_tags(manage_request)

    assert manage_response.processed_instruction_count == 3
    assert str(stored_tag_id) in manage_response.validation_updates
    assert len(manage_response.removed_tag_ids) == 1
    assert manage_response.removed_tag_ids[0] == stored_tag_id
