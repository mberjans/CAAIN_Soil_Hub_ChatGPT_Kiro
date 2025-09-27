"""API tests for preference routes."""
import os
import sys
import importlib.util
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

_TEST_DIR = os.path.dirname(__file__)
_PARENT_DIR = os.path.abspath(os.path.join(_TEST_DIR, '..'))
_SRC_DIR = os.path.join(_PARENT_DIR, 'src')

if _PARENT_DIR not in sys.path:
    sys.path.insert(0, _PARENT_DIR)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

_PREFERENCE_PATH = os.path.join(_SRC_DIR, 'api', 'preference_routes.py')
_spec = importlib.util.spec_from_file_location('preference_routes_test_module', _PREFERENCE_PATH)
if _spec is None or _spec.loader is None:
    raise RuntimeError('Unable to load preference_routes module for testing')
preference_routes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(preference_routes)
preference_router = getattr(preference_routes, 'router')
CropPreferenceService = getattr(preference_routes, 'CropPreferenceService')


def _build_app() -> FastAPI:
    app_instance = FastAPI()
    app_instance.include_router(preference_router, prefix="/api/v1")
    return app_instance


def _prepare_service() -> CropPreferenceService:
    service = CropPreferenceService()
    service.database_available = False
    service.db = None
    return service


def test_update_and_get_preference_profile_endpoint():
    service = _prepare_service()
    preference_routes.crop_preference_service = service
    app_instance = _build_app()
    client = TestClient(app_instance)

    user_id = uuid4()
    payload = {
        "profile": {
            "preference_id": None,
            "user_id": str(user_id),
            "preference_type": "user_defined",
            "title": "Primary",
            "crop_categories": ["grain"],
            "market_focus": ["premium"],
            "sustainability_focus": [],
            "weights": [],
            "constraints": [],
            "priority_notes": {},
            "metadata": {},
            "confidence": "medium"
        },
        "replace_existing": True
    }

    put_response = client.put(f"/api/v1/crop-taxonomy/preferences/{user_id}", json=payload)
    assert put_response.status_code == 200
    result = put_response.json()
    assert result["profile"]["user_id"] == str(user_id)

    get_response = client.get(f"/api/v1/crop-taxonomy/preferences/{user_id}")
    assert get_response.status_code == 200
    get_payload = get_response.json()
    assert get_payload["profile"]["crop_categories"] == ["grain"]


def test_learn_preferences_endpoint():
    service = _prepare_service()
    preference_routes.crop_preference_service = service
    app_instance = _build_app()
    client = TestClient(app_instance)

    user_id = uuid4()
    signal_payload = {
        "user_id": str(user_id),
        "signals": [
            {
                "crop_id": str(uuid4()),
                "signal_type": "select",
                "weight": 0.9,
                "context": {
                    "dimension": "crop_category",
                    "key": "legume"
                }
            }
        ],
        "learning_rate": 0.5,
        "decay_factor": 0.9
    }

    response = client.post("/api/v1/crop-taxonomy/preferences/learn", json=signal_payload)
    assert response.status_code == 200
    body = response.json()
    weights = body["profile"]["weights"]
    found = False
    for weight_record in weights:
        if weight_record["dimension"] == "crop_category" and weight_record["key"] == "legume":
            found = True
            assert weight_record["weight"] > 0
    assert found is True
