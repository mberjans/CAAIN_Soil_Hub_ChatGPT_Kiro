"""Tests for mobile price alert orchestration."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from ..services.mobile_price_alert_service import MobilePriceAlertManager
from ..models.price_optimization_alert_models import (
    MobilePriceAlertRequest,
    AlertChannel,
    AlertType
)
from ..models.price_models import FertilizerType
from ..api.price_optimization_alert_routes import router as alert_router


test_app = FastAPI()
test_app.include_router(alert_router)


@pytest.mark.asyncio
async def test_mobile_price_alert_manager_response_structure():
    """Ensure the mobile alert manager returns a well-formed response."""
    manager = MobilePriceAlertManager()
    request = MobilePriceAlertRequest(
        user_id="mobile-test-user",
        latitude=41.5,
        longitude=-93.5,
        history_days=14,
        max_alerts=3,
        delivery_channel=AlertChannel.APP_NOTIFICATION
    )
    
    response = await manager.generate_mobile_alerts(request)
    
    assert response.user_id == "mobile-test-user"
    assert isinstance(response.region, str)
    assert response.region != ""
    assert isinstance(response.alerts, list)
    assert len(response.alerts) <= 3
    assert isinstance(response.insights, dict)


def test_mobile_price_alert_route_returns_data():
    """Verify API route returns mobile alerts without error."""
    client = TestClient(test_app)
    payload = {
        "user_id": "route-user",
        "latitude": 40.0,
        "longitude": -90.0,
        "history_days": 10,
        "max_alerts": 2,
        "fertilizer_types": [FertilizerType.NITROGEN.value, FertilizerType.PHOSPHORUS.value],
        "alert_types": [AlertType.PRICE_THRESHOLD.value, AlertType.OPPORTUNITY.value]
    }
    
    response = client.post("/api/v1/alerts/mobile-price", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["user_id"] == "route-user"
    assert "alerts" in data
    assert isinstance(data["alerts"], list)
