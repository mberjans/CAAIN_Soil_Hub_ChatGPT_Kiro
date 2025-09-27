"""Tests for crop preference Pydantic models."""
import os
import sys
from uuid import uuid4
import pytest

_TEST_DIR = os.path.dirname(__file__)
_PARENT_DIR = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_PARENT_DIR, 'src')

if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from src.models.preference_models import (  # type: ignore
    PreferenceProfile,
    PreferenceWeight,
    PreferenceConstraint,
    PreferenceDimension,
    PreferenceConfidence,
    ConstraintType,
)


def test_preference_profile_normalizes_lists():
    profile = PreferenceProfile(
        user_id=uuid4(),
        crop_categories=["  grains  ", "", "oilseeds"],
        market_focus=[" direct ", None],
        sustainability_focus=[" soil "],
        weights=[],
        constraints=[],
        confidence=PreferenceConfidence.HIGH,
    )

    assert profile.crop_categories == ["grains", "oilseeds"]
    assert profile.market_focus == ["direct"]
    assert profile.sustainability_focus == ["soil"]


def test_preference_profile_rejects_duplicate_weights():
    weight_one = PreferenceWeight(
        dimension=PreferenceDimension.MARKET,
        key="premium",
        weight=0.6,
    )
    weight_two = PreferenceWeight(
        dimension=PreferenceDimension.MARKET,
        key="premium",
        weight=0.6,
    )

    with pytest.raises(ValueError):
        PreferenceProfile(
            user_id=uuid4(),
            weights=[weight_one, weight_two],
            constraints=[]
        )


def test_preference_constraint_requires_key():
    with pytest.raises(ValueError):
        PreferenceConstraint(
            constraint_type=ConstraintType.REQUIRE,
            dimension=PreferenceDimension.CROP_CATEGORY,
            key="  ",
        )
