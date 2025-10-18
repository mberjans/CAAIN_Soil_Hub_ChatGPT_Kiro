"""Tests for mobile fertilizer strategy tracking API."""

import importlib
import importlib.machinery
import importlib.util
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


SRC_DIR = Path(__file__).resolve().parent.parent
src_path_str = str(SRC_DIR)
if src_path_str not in sys.path:
    sys.path.append(src_path_str)

PACKAGE_NAME = "fertilizer_strategy_pkg"
if PACKAGE_NAME not in sys.modules:
    module_spec = importlib.machinery.ModuleSpec(name=PACKAGE_NAME, loader=None)
    package_module = importlib.util.module_from_spec(module_spec)
    package_module.__path__ = [src_path_str]
    sys.modules[PACKAGE_NAME] = package_module

routes_module = importlib.import_module(f"{PACKAGE_NAME}.api.mobile_strategy_tracking_routes")
models_module = importlib.import_module(f"{PACKAGE_NAME}.models.mobile_strategy_tracking_models")
services_module = importlib.import_module(f"{PACKAGE_NAME}.services.mobile_strategy_tracking_service")
management_module = importlib.import_module(f"{PACKAGE_NAME}.services.strategy_management_service")
database_module = importlib.import_module(f"{PACKAGE_NAME}.database.strategy_management_db")


def build_sample_entry() -> Dict[str, object]:
    """Build sample mobile progress entry payload."""
    now_iso = datetime.utcnow().isoformat()
    entry: Dict[str, object] = {}
    entry["client_event_id"] = str(uuid4())
    entry["strategy_id"] = "strategy-mobile-1"
    entry["version_number"] = 1
    entry["user_id"] = "operator-1"
    entry["field_id"] = "field-100"
    entry["activity_type"] = "application"
    entry["status"] = "completed"
    entry["activity_timestamp"] = now_iso
    entry["captured_offline"] = False

    application: Dict[str, object] = {}
    application["product_name"] = "UAN 32"
    application["application_rate"] = 150.0
    application["rate_unit"] = "lbs_ac"
    application["equipment"] = "Y-drop"
    entry["application"] = application

    cost_summary: Dict[str, object] = {}
    cost_summary["input_cost"] = 480.0
    cost_summary["labor_cost"] = 120.0
    cost_summary["equipment_cost"] = 60.0
    cost_summary["total_cost"] = 660.0
    cost_summary["currency"] = "USD"
    entry["cost_summary"] = cost_summary

    yield_summary: Dict[str, object] = {}
    yield_summary["observed_yield"] = 185.0
    yield_summary["expected_yield"] = 190.0
    yield_summary["yield_unit"] = "bu_ac"
    entry["yield_summary"] = yield_summary

    gps: Dict[str, object] = {}
    gps["latitude"] = 43.15
    gps["longitude"] = -79.03
    gps["accuracy"] = 5.0
    entry["gps"] = gps

    photos = []
    photo_payload = {}
    photo_payload["photo_id"] = str(uuid4())
    photo_payload["uri"] = "file://photo"
    photo_payload["file_size_bytes"] = 2048
    photos.append(photo_payload)
    entry["photos"] = photos

    return entry


@pytest.fixture
def tracking_service():
    repository = database_module.StrategyRepository(database_url="sqlite:///:memory:")
    management_service = management_module.StrategyManagementService(repository=repository)
    service = services_module.MobileStrategyTrackingService(
        repository=repository,
        management_service=management_service,
    )
    return service


@pytest.fixture
def client(tracking_service):
    app = FastAPI()
    app.include_router(routes_module.router, prefix="/api/v1")

    async def override_service():
        return tracking_service

    app.dependency_overrides[routes_module.get_mobile_tracking_service] = override_service
    return TestClient(app)


def test_record_mobile_progress_creates_activity(client):
    entry = build_sample_entry()
    response = client.post("/api/v1/mobile-strategy/progress", json=entry)
    assert response.status_code == 200

    payload = response.json()
    assert payload.get("activity_id") is not None
    assert payload.get("created") is True
    assert payload.get("conflict_resolved") is False


def test_record_mobile_progress_detects_conflict(client):
    entry = build_sample_entry()
    response_one = client.post("/api/v1/mobile-strategy/progress", json=entry)
    assert response_one.status_code == 200
    first_payload = response_one.json()
    first_activity_id = first_payload.get("activity_id")

    entry["status"] = "completed"
    response_two = client.post("/api/v1/mobile-strategy/progress", json=entry)
    assert response_two.status_code == 200
    second_payload = response_two.json()

    assert second_payload.get("activity_id") == first_activity_id
    assert second_payload.get("conflict_resolved") is True
    assert second_payload.get("created") is False


def test_tracking_summary_returns_recent_activity(client):
    entry = build_sample_entry()
    response = client.post("/api/v1/mobile-strategy/progress", json=entry)
    assert response.status_code == 200

    summary_response = client.get(
        "/api/v1/mobile-strategy/summary",
        params={"strategy_id": entry["strategy_id"], "version_number": 1, "limit": 5},
    )
    assert summary_response.status_code == 200

    summary_payload = summary_response.json()
    activities = summary_payload.get("recent_activities", [])
    assert len(activities) >= 1
    first_activity = activities[0]
    assert first_activity.get("activity_type") == "application"
