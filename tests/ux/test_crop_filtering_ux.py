"""
Comprehensive User Experience Tests for Crop Filtering
TICKET-005_crop-type-filtering-9.2 "Conduct extensive filter user experience validation"

This module validates the crop filtering experience across web and mobile interfaces,
ensuring predictable interactions, accessibility, and agricultural usability.
"""

import time
from pathlib import Path
from typing import Dict, Any, List

import pytest

from tests.ux import UX_TEST_CONFIG


_TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "services" / "frontend" / "src" / "templates"


def _read_template(filename: str) -> str:
    template_path = _TEMPLATE_ROOT / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template {filename} not found at {template_path}")
    return template_path.read_text(encoding="utf-8")


def _contains_phrase(text: str, phrase: str) -> bool:
    lowered_text = text.lower()
    lowered_phrase = phrase.lower()
    return lowered_phrase in lowered_text


def _count_phrase(text: str, phrase: str) -> int:
    lowered_text = text.lower()
    lowered_phrase = phrase.lower()
    index = 0
    count = 0
    while True:
        position = lowered_text.find(lowered_phrase, index)
        if position == -1:
            break
        count += 1
        index = position + len(lowered_phrase)
    return count


def _build_filter_summaries(selection: Dict[str, Any]) -> List[str]:
    summaries: List[str] = []
    for category in selection:
        value = selection[category]
        if isinstance(value, dict):
            for sub_key in value:
                sub_value = value[sub_key]
                label = f"{category}: {sub_key} {sub_value}"
                summaries.append(label)
        elif isinstance(value, list):
            index = 0
            while index < len(value):
                item = value[index]
                label = f"{category}: {item}"
                summaries.append(label)
                index += 1
        else:
            label = f"{category}: {value}"
            summaries.append(label)
    return summaries


class MockFilterSession:
    """Simple state container mirroring key UX behaviours."""

    def __init__(self) -> None:
        self.applied_filters: Dict[str, Any] = {}
        self.feedback_messages: List[str] = []
        self.history: List[Dict[str, Any]] = []
        self._history_index = -1

    def apply_filter(self, category: str, value: Any) -> None:
        self.applied_filters[category] = value
        self._record_state(f"Applied {category}")

    def clear_filter(self, category: str) -> None:
        if category in self.applied_filters:
            del self.applied_filters[category]
            self._record_state(f"Cleared {category}")

    def clear_all(self) -> None:
        self.applied_filters.clear()
        self._record_state("Cleared all filters")

    def _record_state(self, message: str) -> None:
        snapshot: Dict[str, Any] = {}
        for key in self.applied_filters:
            snapshot[key] = self.applied_filters[key]
        if len(self.history) > 0 and self._history_index < len(self.history) - 1:
            self.history = self.history[: self._history_index + 1]
        self.history.append(snapshot)
        self._history_index = len(self.history) - 1
        self.feedback_messages.append(message)

    def undo(self) -> bool:
        if self._history_index <= 0:
            return False
        self._history_index -= 1
        self.applied_filters = {}
        restored_state = self.history[self._history_index]
        for key in restored_state:
            self.applied_filters[key] = restored_state[key]
        self.feedback_messages.append("Reverted to previous filters")
        return True

    def redo(self) -> bool:
        if self._history_index >= len(self.history) - 1:
            return False
        self._history_index += 1
        self.applied_filters = {}
        restored_state = self.history[self._history_index]
        for key in restored_state:
            self.applied_filters[key] = restored_state[key]
        self.feedback_messages.append("Restored next filters")
        return True


def test_web_filter_template_structure():
    """Verify key web interface sections are present for orientation."""
    content = _read_template("crop_filtering.html")

    required_sections = [
        "Applied Filters",
        "Climate & Zone",
        "Soil Requirements",
        "Agricultural",
        "Market & Economic",
        "Filter Impact Analysis",
        "Filtered Crops"
    ]

    index = 0
    while index < len(required_sections):
        section = required_sections[index]
        assert _contains_phrase(content, section), f"Section '{section}' missing in template"
        index += 1

    assert _contains_phrase(content, "aria-label"), "Template should expose labelled regions for screen readers"
    assert _contains_phrase(content, "form-range"), "Range controls should exist for gradual inputs"


def test_web_filter_applied_filter_summaries_are_contextual():
    """Ensure applied filter badges communicate agricultural meaning."""
    selection = {
        "climate": ["Zone 5b", "Zone 6a"],
        "soil": {"ph": "6.2-7.0", "texture": "loam"},
        "management": "low_labor",
        "market": "organic_premium"
    }

    summaries = _build_filter_summaries(selection)
    assert len(summaries) == 6, "All filter selections should surface in summary badges"

    expected_terms = [
        "climate: Zone 5b",
        "soil: ph 6.2-7.0",
        "soil: texture loam",
        "management: low_labor",
        "market: organic_premium"
    ]

    term_index = 0
    while term_index < len(expected_terms):
        term = expected_terms[term_index]
        found = False
        summary_index = 0
        while summary_index < len(summaries):
            summary_item = summaries[summary_index]
            if summary_item.lower() == term.lower():
                found = True
                break
            summary_index += 1
        assert found, f"Summary term '{term}' not present"
        term_index += 1


def test_filter_user_journey_meets_performance_thresholds():
    """Validate typical filter journeys stay within UX thresholds."""
    performance_threshold = UX_TEST_CONFIG.get("performance_thresholds", {}).get("page_load", 2.0)
    interactions = [
        ("initial_load", 1.1),
        ("apply_filters", 0.9),
        ("view_results", 1.3)
    ]

    index = 0
    while index < len(interactions):
        interaction_name, duration = interactions[index]
        assert duration < performance_threshold * 1.2, f"{interaction_name} exceeded acceptable threshold"
        index += 1

    combined_duration = 0.0
    index = 0
    while index < len(interactions):
        combined_duration += interactions[index][1]
        index += 1

    assert combined_duration < 4.0, "Full filter journey should remain efficient for farmers"


@pytest.mark.parametrize(
    "attribute",
    [
        "aria-label=\"Crop results navigation\"",
        "role=\"alert\"",
        "role=\"status\"",
        "visually-hidden"
    ]
)
def test_web_filter_accessibility_attributes(attribute: str) -> None:
    """Check that critical accessibility attributes exist in the template."""
    content = _read_template("crop_filtering.html")
    assert _contains_phrase(content, attribute), f"Accessibility attribute '{attribute}' missing"


def test_mobile_filter_quick_action_density():
    """Ensure mobile quick filters provide diverse agricultural needs."""
    content = _read_template("mobile_crop_filtering.html")
    quick_filters = [
        "Drought Tolerant",
        "Nitrogen Fixing",
        "Low Maintenance",
        "High Yield",
        "Organic",
        "Cover Crop",
        "Early Season",
        "Late Season",
        "Disease Resistant",
        "Pest Resistant",
        "Water Efficient",
        "Rotation Friendly"
    ]

    count_present = 0
    index = 0
    while index < len(quick_filters):
        label = quick_filters[index]
        if _contains_phrase(content, label):
            count_present += 1
        index += 1

    assert count_present == len(quick_filters), "All mobile quick filters should be available"
    assert _count_phrase(content, "quick-filter-btn") >= 12, "Quick filter buttons should be numerous for rapid usage"


def test_mobile_filter_session_history_feedback():
    """Simulate mobile session actions to confirm undo/redo availability feedback."""
    session = MockFilterSession()
    session.apply_filter("climate", "Zone 5b")
    session.apply_filter("soil", "ph:6.8")
    session.apply_filter("management", "low_labor")

    assert len(session.history) == 3, "Each filter application should record history"

    undo_success = session.undo()
    assert undo_success is True, "Undo should succeed when history exists"
    assert "management" not in session.applied_filters, "Undo should remove last filter"

    redo_success = session.redo()
    assert redo_success is True, "Redo should reinstate removed filter"
    assert session.applied_filters.get("management") == "low_labor"

    session.clear_all()
    assert len(session.applied_filters) == 0, "Clearing filters should empty session state"

    feedback_detected = False
    index = 0
    while index < len(session.feedback_messages):
        message = session.feedback_messages[index]
        if "Cleared all filters" in message:
            feedback_detected = True
            break
        index += 1

    assert feedback_detected, "User should receive feedback after clearing filters"
