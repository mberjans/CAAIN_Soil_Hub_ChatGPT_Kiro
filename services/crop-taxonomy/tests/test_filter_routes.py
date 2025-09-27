"""Tests for filter combination API routes."""

import os
import sys
import importlib.util

from fastapi import FastAPI
from fastapi.testclient import TestClient

_TEST_DIR = os.path.dirname(__file__)
_PARENT_DIR = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_PARENT_DIR, 'src')

if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

_FILTER_ROUTE_PATH = os.path.join(_SRC_DIR, 'api', 'filter_routes.py')
_spec = importlib.util.spec_from_file_location('filter_routes_test_module', _FILTER_ROUTE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError('Unable to load filter_routes module for testing')
_filter_routes_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_filter_routes_module)
filter_router = getattr(_filter_routes_module, 'router')


def _build_app() -> FastAPI:
    app_instance = FastAPI()
    app_instance.include_router(filter_router, prefix="/api/v1")
    return app_instance


def test_combine_filters_endpoint_returns_combined_filters():
    app_instance = _build_app()
    client = TestClient(app_instance)

    payload = {
        "request_id": "api-unit-001",
        "preset_keys": ["organic_farming"],
        "directives": [
            {
                "category": "economic",
                "attribute": "high_roi_potential",
                "value": True,
                "priority": 0.6,
                "rationale": "Increase profitability"
            }
        ],
        "context": {"climate_zone": "5a"}
    }

    response = client.post("/api/v1/crop-taxonomy/filters/combine", json=payload)
    assert response.status_code == 200
    body = response.json()

    preset_found = False
    for preset_key in body.get("applied_presets", []):
        if preset_key == "organic_farming":
            preset_found = True
            break
    assert preset_found is True

    economic_filter = body.get("combined_criteria", {}).get("economic_filter", {})
    assert economic_filter.get("high_roi_potential") is True


def test_filter_suggestions_endpoint_returns_suggestions():
    app_instance = _build_app()
    client = TestClient(app_instance)

    params = {
        "request_id": "api-unit-002",
        "climate_zone": "4b",
        "soil_ph": 6.4,
        "soil_drainage": "poor",
        "market_goal": "premium",
        "sustainability_focus": "carbon",
        "focus_areas": ["organic", "profit"],
        "max_suggestions": 4
    }

    response = client.get("/api/v1/crop-taxonomy/filters/suggestions", params=params)
    assert response.status_code == 200
    body = response.json()

    suggestions = body.get("suggestions", [])
    assert len(suggestions) > 0
    first_has_directives = False
    for suggestion in suggestions:
        directives = suggestion.get("directives", [])
        if len(directives) > 0:
            first_has_directives = True
            break
    assert first_has_directives is True
