"""Tests for CropPreferenceService."""
import os
import sys
from uuid import uuid4
import asyncio

_TEST_DIR = os.path.dirname(__file__)
_PARENT_DIR = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_PARENT_DIR, 'src')

if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from src.services.crop_preference_service import CropPreferenceService  # type: ignore
from src.models.preference_models import (  # type: ignore
    PreferenceProfile,
    PreferenceUpdateRequest,
    PreferenceWeight,
    PreferenceConstraint,
    PreferenceType,
    PreferenceDimension,
    PreferenceLearningRequest,
    PreferenceSignal,
    ConstraintType,
)


def test_upsert_and_fetch_preference_profile_conflict_detection():
    service = CropPreferenceService()
    service.database_available = False
    service.db = None

    user_id = uuid4()
    profile = PreferenceProfile(
        preference_id=None,
        user_id=user_id,
        preference_type=PreferenceType.USER_DEFINED,
        crop_categories=['Grain'],
        market_focus=['premium'],
        sustainability_focus=[],
        weights=[
            PreferenceWeight(
                dimension=PreferenceDimension.MARKET,
                key='premium',
                weight=0.8
            )
        ],
        constraints=[
            PreferenceConstraint(
                constraint_type=ConstraintType.EXCLUDE,
                dimension=PreferenceDimension.CROP_CATEGORY,
                key='grain'
            )
        ]
    )
    request = PreferenceUpdateRequest(
        profile=profile,
        replace_existing=True
    )

    asyncio.run(service.upsert_preference_profile(request))
    response = asyncio.run(service.get_preference_profile(user_id, PreferenceType.USER_DEFINED))

    assert response.profile.user_id == user_id
    assert response.profile.crop_categories == ['Grain']
    assert len(response.conflict_notes) == 1
    assert 'conflicts' in response.conflict_notes[0]


def test_learn_preferences_adds_weight():
    service = CropPreferenceService()
    service.database_available = False
    service.db = None

    user_id = uuid4()
    signal = PreferenceSignal(
        crop_id=uuid4(),
        signal_type='view',
        weight=0.7,
        context={
            'dimension': PreferenceDimension.CROP_CATEGORY.value,
            'key': 'oilseed'
        }
    )
    learning_request = PreferenceLearningRequest(
        user_id=user_id,
        signals=[signal],
        learning_rate=0.5,
        decay_factor=0.9
    )

    response = asyncio.run(service.learn_preferences(learning_request))

    has_weight = False
    for weight_record in response.profile.weights:
        if weight_record.dimension == PreferenceDimension.CROP_CATEGORY and weight_record.key == 'oilseed':
            has_weight = True
            assert weight_record.weight > 0
    assert has_weight is True
