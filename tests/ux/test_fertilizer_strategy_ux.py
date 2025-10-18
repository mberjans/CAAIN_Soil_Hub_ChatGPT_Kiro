"""
Comprehensive User Experience Tests for Fertilizer Strategy Optimization
TICKET-006_fertilizer-strategy-optimization-10.3 "Test user experience and agricultural usability"

This module validates the fertilizer strategy experience across web and mobile
surfaces, ensuring agricultural usability metrics are met and that field
workflows integrate with backend tracking services.
"""

import importlib
import importlib.machinery
import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pytest

from tests.ux import UX_TEST_CONFIG


_TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "services" / "frontend" / "src" / "templates"
_STATIC_ROOT = Path(__file__).resolve().parents[2] / "services" / "frontend" / "src" / "static"
_JS_PATH = _STATIC_ROOT / "js" / "mobile-fertilizer-strategy.js"

_SERVICE_SRC_DIR = Path(__file__).resolve().parents[2] / "services" / "fertilizer-strategy" / "src"
_SERVICE_SRC_STR = str(_SERVICE_SRC_DIR)
if _SERVICE_SRC_STR not in sys.path:
    sys.path.append(_SERVICE_SRC_STR)

_PACKAGE_NAME = "fertilizer_strategy_pkg"
if _PACKAGE_NAME not in sys.modules:
    _module_spec = importlib.machinery.ModuleSpec(name=_PACKAGE_NAME, loader=None)
    _package_module = importlib.util.module_from_spec(_module_spec)
    _package_module.__path__ = [_SERVICE_SRC_STR]
    sys.modules[_PACKAGE_NAME] = _package_module

database_module = importlib.import_module(f"{_PACKAGE_NAME}.database.strategy_management_db")
services_module = importlib.import_module(f"{_PACKAGE_NAME}.services.mobile_strategy_tracking_service")
strategy_service_module = importlib.import_module(f"{_PACKAGE_NAME}.services.strategy_management_service")
strategy_models_module = importlib.import_module(f"{_PACKAGE_NAME}.models.strategy_management_models")
mobile_models_module = importlib.import_module(f"{_PACKAGE_NAME}.models.mobile_strategy_tracking_models")


def _read_template(filename: str) -> str:
    template_path = _TEMPLATE_ROOT / filename
    if not template_path.exists():
        raise FileNotFoundError(f"Template {filename} not found at {template_path}")
    return template_path.read_text(encoding="utf-8")


def _read_static_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Static asset not found at {path}")
    return path.read_text(encoding="utf-8")


def _contains_segment(text: str, segment: str) -> bool:
    lower_text = text.lower()
    lower_segment = segment.lower()
    if lower_segment in lower_text:
        return True
    return False


def _assert_segments_present(text: str, segments: List[str]) -> None:
    index = 0
    while index < len(segments):
        segment = segments[index]
        assert _contains_segment(text, segment), f"Expected segment '{segment}' missing"
        index += 1


def _count_occurrences(text: str, fragment: str) -> int:
    lower_text = text.lower()
    lower_fragment = fragment.lower()
    start = 0
    count = 0
    while True:
        position = lower_text.find(lower_fragment, start)
        if position == -1:
            break
        count += 1
        start = position + len(lower_fragment)
    return count


def test_web_strategy_template_highlights_agronomic_sections():
    """Verify desktop strategy template surfaces critical agronomic content."""
    content = _read_template("fertilizer_strategy.html")

    sections = [
        "Crop & Field Information",
        "Soil Test Results",
        "Economic Parameters",
        "ROI Analysis",
        "Recommended Fertilizer Program",
        "Nitrogen Program",
        "Phosphorus Program",
        "Potassium Program"
    ]
    _assert_segments_present(content, sections)

    # Confirm agricultural units and guided inputs are available.
    assert _contains_segment(content, "lbs/ac"), "Units per acre should be displayed for nutrient guidance"
    assert _count_occurrences(content, "form-label") >= 6, "Form labels should guide data entry"
    assert _count_occurrences(content, "form-control") >= 10, "Interactive controls should guide farmer data capture"


def test_mobile_strategy_template_supports_field_operations():
    """Ensure mobile template guides field operators through critical workflows."""
    content = _read_template("mobile_fertilizer_strategy.html")

    required_elements = [
        "Quick actions",
        "Strategy Summary",
        "Market Signals",
        "Price Alerts",
        "Field Actions",
        "Strategy Tracking",
        "Field Intelligence",
        "Analysis",
        "Offline mode"
    ]
    _assert_segments_present(content, required_elements)

    # Confirm GPS and camera capture cues exist for in-field data capture.
    assert _contains_segment(content, "Capture GPS"), "GPS capture affordance should be visible"
    assert _contains_segment(content, "Field Photo"), "Photo capture control should be accessible"
    assert _contains_segment(content, "Offline Queue"), "Offline queue indicator should guide connectivity handling"

    # Performance expectations
    mobile_threshold = UX_TEST_CONFIG.get("performance_thresholds", {}).get("page_load", 2.0)
    assert mobile_threshold <= 2.5, "Mobile UX threshold should remain farmer-friendly"


def test_mobile_sample_content_reinforces_agronomic_guidance():
    """Validate sample data builders communicate agricultural decision support."""
    script = _read_static_file(_JS_PATH)

    agronomic_phrases = [
        "Apply 32% UAN",
        "lbs n/acre",
        "Forward purchase 40%",
        "cover crop nutrient credit",
        "Rain probability",
        "Document pre-application crop condition"
    ]
    _assert_segments_present(script, agronomic_phrases)

    # Ensure recommendation scaffolding is comprehensive.
    recommendation_count = _count_occurrences(script, "recommendations")
    assert recommendation_count >= 3, "Sample content should outline multiple actionable recommendations"


@pytest.mark.asyncio
async def test_mobile_tracking_service_supports_farmer_progress_workflow():
    """Exercise mobile tracking service to confirm user experience metrics stay coherent."""
    repository = database_module.StrategyRepository(database_url="sqlite:///:memory:")
    management_instance = strategy_service_module.StrategyManagementService(repository=repository)
    tracking_service = services_module.MobileStrategyTrackingService(
        repository=repository,
        management_service=management_instance,
    )

    field_strategy = strategy_models_module.FieldStrategyData(
        field_id="field-ux-01",
        acres=120.0,
        crop_type="corn",
        recommended_rates={"nitrogen": 165.0, "phosphorus": 45.0, "potassium": 60.0},
        application_schedule=["pre-plant", "side-dress"],
        application_method="Y-drop",
        expected_yield=190.0,
        total_cost=42000.0,
        roi_projection=0.22,
    )
    field_strategies: List[strategy_models_module.FieldStrategyData] = []
    field_strategies.append(field_strategy)

    tags: List[str] = []
    tags.append("corn")
    tags.append("roi_focus")

    sharing_settings = strategy_models_module.StrategySharingSettings(is_public=False, shared_with=[])

    save_request = strategy_models_module.SaveStrategyRequest(
        strategy_name="UX Fertility Plan",
        description="Test strategy for UX validation",
        user_id="operator-ux",
        farm_id="farm-ux-01",
        is_template=False,
        tags=tags,
        sharing=sharing_settings,
        field_strategies=field_strategies,
        economic_summary={"total_cost": 42000.0, "currency": "USD"},
        environmental_metrics={"runoff_risk": "low"},
        roi_estimate=0.18,
        metadata={"season": "2025"},
        strategy_id="strategy-ux-01",
    )

    save_response = await management_instance.save_strategy(save_request)
    assert save_response.latest_version.version_number == 1, "Initial strategy version should equal one"

    photos: List[mobile_models_module.MobileStrategyPhotoMetadata] = []
    photos.append(
        mobile_models_module.MobileStrategyPhotoMetadata(
            photo_id="photo-ux-01",
            uri="file://photo-ux-01.jpg",
            file_size_bytes=3072,
            notes="Canopy photo before application",
        )
    )

    progress_entry = mobile_models_module.MobileStrategyProgressEntry(
        client_event_id="event-ux-001",
        strategy_id=save_response.strategy_id,
        version_number=save_response.latest_version.version_number,
        user_id="operator-ux",
        field_id="field-ux-01",
        activity_type="application",
        status="completed",
        activity_timestamp=datetime.utcnow(),
        device_identifier="mobile-ux-device",
        notes="Applied N before rainfall window closes",
        captured_offline=True,
        gps=mobile_models_module.MobileGpsCoordinate(latitude=44.11, longitude=-93.25, accuracy=4.2),
        application=mobile_models_module.StrategyApplicationDetail(
            product_name="32% UAN",
            application_rate=150.0,
            rate_unit="lbs_ac",
            equipment="Y-drop",
            status="completed",
            notes="Applied along contour strips",
        ),
        cost_summary=mobile_models_module.StrategyCostSummary(
            input_cost=480.0,
            labor_cost=130.0,
            equipment_cost=70.0,
            total_cost=680.0,
            currency="USD",
        ),
        yield_summary=mobile_models_module.StrategyYieldSummary(
            observed_yield=185.0,
            expected_yield=192.0,
            yield_unit="bu_ac",
            notes="Green snap minimal",
        ),
        photos=photos,
        attachments={"weather_window": "48hr dry period"},
    )

    progress_response = await tracking_service.record_progress(progress_entry)
    assert progress_response.created is True, "Progress entry should be recorded"
    assert progress_response.conflict_resolved is False, "First entry should not trigger conflict resolution"

    summary = await tracking_service.get_tracking_summary(
        strategy_id=save_response.strategy_id,
        version_number=save_response.latest_version.version_number,
        limit=5,
    )

    assert summary.strategy_id == save_response.strategy_id, "Summary should return matching strategy identifier"
    assert summary.progress_percent >= 99.0, "Completed activity should reflect near-full progress"
    assert summary.pending_actions == 0, "Completed activity should not leave pending actions"

    activities_count = len(summary.recent_activities)
    assert activities_count >= 1, "Recent activity list should include the recorded entry"

    first_activity = summary.recent_activities[0]
    assert first_activity.activity_type == "application", "Activity type should retain agricultural context"
    assert first_activity.cost_summary is not None, "Cost details should surface for economic usability"

    snapshot = summary.performance_snapshot
    assert snapshot.total_events_recorded >= 1, "Performance snapshot should track recorded events"
