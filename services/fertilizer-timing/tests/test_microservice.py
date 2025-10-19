"""Integration tests for the fertilizer timing microservice."""

import sys
from pathlib import Path
from typing import Dict

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(name="test_client")
def fixture_test_client(tmp_path, monkeypatch):
    """Provide a TestClient with isolated database configuration."""
    db_path = tmp_path / "timing.db"
    monkeypatch.setenv(
        "FERTILIZER_TIMING_DATABASE_URL",
        f"sqlite+aiosqlite:///{db_path}",
    )

    service_src = Path(__file__).resolve().parents[1] / "src"
    src_path = str(service_src)
    if src_path in sys.path:
        sys.path.remove(src_path)
    sys.path.insert(0, src_path)

    import main  # pylint: disable=import-error,import-outside-toplevel

    with TestClient(main.app) as client:
        yield client


def _sample_request_payload() -> Dict[str, object]:
    payload: Dict[str, object] = {}
    payload["field_id"] = "field-001"
    payload["crop_type"] = "corn"
    payload["planting_date"] = "2025-04-20"
    payload["expected_harvest_date"] = "2025-10-05"
    payload["fertilizer_requirements"] = {"nitrogen": 120.0, "phosphorus": 45.0}
    payload["application_methods"] = ["broadcast", "side_dress"]
    payload["soil_type"] = "loam"
    payload["soil_moisture_capacity"] = 0.65
    payload["drainage_class"] = "moderate"
    payload["slope_percent"] = 2.0
    payload["weather_data_source"] = "noaa"
    payload["location"] = {"lat": 41.0, "lng": -93.0}
    payload["equipment_availability"] = {"spreader": ["2025-05-01"]}
    payload["labor_availability"] = {"2025-05-01": 4}
    payload["budget_constraints"] = {"max_total_cost": 6000}
    payload["optimization_horizon_days"] = 150
    payload["risk_tolerance"] = 0.5
    payload["prioritize_yield"] = True
    payload["prioritize_cost"] = False
    payload["split_application_allowed"] = True
    payload["weather_dependent_timing"] = True
    payload["soil_temperature_threshold"] = 45.0
    return payload


def test_optimize_endpoint_returns_result(test_client: TestClient) -> None:
    payload = _sample_request_payload()
    response = test_client.post("/api/v1/fertilizer-timing/optimize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "optimal_timings" in data
    assert len(data["optimal_timings"]) > 0


def test_calendar_endpoint_generates_entries(test_client: TestClient) -> None:
    payload = _sample_request_payload()
    response = test_client.post("/api/v1/fertilizer-calendar/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "entries" in data
    assert len(data["entries"]) > 0


def test_alert_endpoint_generates_alerts(test_client: TestClient) -> None:
    payload = _sample_request_payload()
    response = test_client.post("/api/v1/fertilizer-alerts/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
