"""
Tests for fertilizer strategy management API and service.
"""

import importlib
import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from typing import List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

# Dynamically configure import path to load strategy modules
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

routes_module = importlib.import_module(f"{PACKAGE_NAME}.api.strategy_management_routes")
models_module = importlib.import_module(f"{PACKAGE_NAME}.models.strategy_management_models")
service_module = importlib.import_module(f"{PACKAGE_NAME}.services.strategy_management_service")
database_module = importlib.import_module(f"{PACKAGE_NAME}.database.strategy_management_db")

app = FastAPI()
app.include_router(routes_module.router, prefix="/api/v1")
get_strategy_management_service = routes_module.get_strategy_management_service
FieldStrategyData = models_module.FieldStrategyData
SaveStrategyRequest = models_module.SaveStrategyRequest
StrategySaveResponse = models_module.StrategySaveResponse
StrategyManagementService = service_module.StrategyManagementService
StrategyRepository = database_module.StrategyRepository
StrategyComparisonRequest = models_module.StrategyComparisonRequest
StrategyComparisonResponse = models_module.StrategyComparisonResponse
StrategyUpdateRequest = models_module.StrategyUpdateRequest
StrategyUpdateResponse = models_module.StrategyUpdateResponse


@pytest.fixture
def in_memory_service():
    """Provide service backed by in-memory database for isolation."""
    repository = StrategyRepository("sqlite:///:memory:")
    service = StrategyManagementService(repository=repository)
    return service


class TestStrategyManagementService:
    """Service-level tests for strategy management."""

    @pytest.mark.asyncio
    async def test_save_strategy_creates_new_entry(self, in_memory_service):
        """Ensure saving a strategy creates a new record with version 1."""
        field_strategy = FieldStrategyData(
            field_id="field-001",
            acres=120.0,
            crop_type="corn",
            recommended_rates={"N": 180.0},
            application_schedule=["pre-plant"],
            application_method="broadcast",
            expected_yield=190.0,
            total_cost=150.0,
            roi_projection=0.25,
        )

        request = SaveStrategyRequest(
            strategy_name="High Yield Corn Plan",
            description="Initial corn fertility plan",
            user_id="user-123",
            farm_id="farm-456",
            is_template=False,
            tags=["corn", "high-yield"],
            field_strategies=[field_strategy],
            economic_summary={"total_cost": 18000.0, "expected_profit": 9000.0},
            environmental_metrics={"runoff_risk": 0.2},
            roi_estimate=0.5,
            metadata={"season": "2025"},
            version_notes="Initial version",
        )

        response = await in_memory_service.save_strategy(request)

        assert isinstance(response, StrategySaveResponse)
        assert response.created is True
        assert response.strategy_id is not None
        assert response.latest_version.version_number == 1
        assert response.latest_version.version_notes == "Initial version"

    @pytest.mark.asyncio
    async def test_save_strategy_creates_new_version(self, in_memory_service):
        """Ensure saving with existing strategy ID creates additional version."""
        field_strategy = FieldStrategyData(
            field_id="field-002",
            acres=80.0,
            crop_type="soybean",
            recommended_rates={"N": 40.0},
            application_schedule=["at-planting"],
            application_method="banded",
            expected_yield=60.0,
            total_cost=90.0,
            roi_projection=0.15,
        )

        initial_request = SaveStrategyRequest(
            strategy_name="Soybean Balanced Plan",
            description="Baseline soybean fertility approach",
            user_id="user-123",
            farm_id="farm-456",
            is_template=False,
            tags=["soybean"],
            field_strategies=[field_strategy],
            economic_summary={"total_cost": 7200.0},
            environmental_metrics={"runoff_risk": 0.1},
            roi_estimate=0.3,
            metadata={"season": "2025"},
            version_notes="Initial soybean plan",
        )

        initial_response = await in_memory_service.save_strategy(initial_request)
        strategy_id = initial_response.strategy_id

        updated_field_strategy = FieldStrategyData(
            field_id="field-002",
            acres=80.0,
            crop_type="soybean",
            recommended_rates={"N": 45.0},
            application_schedule=["at-planting", "mid-season"],
            application_method="banded",
            expected_yield=62.0,
            total_cost=95.0,
            roi_projection=0.18,
        )

        update_request = SaveStrategyRequest(
            strategy_name="Soybean Balanced Plan",
            description="Adjusted soybean fertility approach",
            user_id="user-123",
            farm_id="farm-456",
            is_template=False,
            tags=["soybean", "updated"],
            field_strategies=[updated_field_strategy],
            economic_summary={"total_cost": 7600.0},
            environmental_metrics={"runoff_risk": 0.12},
            roi_estimate=0.32,
            metadata={"season": "2025"},
            strategy_id=strategy_id,
            version_notes="Adjustments after soil test",
        )

        updated_response = await in_memory_service.save_strategy(update_request)

        assert updated_response.created is False
        assert updated_response.strategy_id == strategy_id
        assert updated_response.latest_version.version_number == 2
        assert updated_response.latest_version.version_notes == "Adjustments after soil test"

    @pytest.mark.asyncio
    async def test_compare_strategies_success(self, in_memory_service):
        """Verify strategy comparison produces metrics."""
        base_field = FieldStrategyData(
            field_id="field-100",
            acres=60.0,
            crop_type="corn",
            recommended_rates={"N": 160.0},
            application_schedule=["pre-plant"],
            application_method="broadcast",
            expected_yield=185.0,
            total_cost=140.0,
            roi_projection=0.28,
        )

        first_request = SaveStrategyRequest(
            strategy_name="Corn Growth Plan A",
            description="Baseline corn program",
            user_id="user-abc",
            farm_id="farm-orange",
            field_strategies=[base_field],
            economic_summary={"total_cost": 12000.0},
            environmental_metrics={"runoff_risk": 0.22},
            roi_estimate=0.42,
            metadata={"season": "2025"},
        )

        first_response = await in_memory_service.save_strategy(first_request)

        modified_field = FieldStrategyData(
            field_id="field-101",
            acres=60.0,
            crop_type="corn",
            recommended_rates={"N": 150.0},
            application_schedule=["pre-plant", "side-dress"],
            application_method="banded",
            expected_yield=190.0,
            total_cost=145.0,
            roi_projection=0.30,
        )

        second_request = SaveStrategyRequest(
            strategy_name="Corn Growth Plan B",
            description="Alternative corn program",
            user_id="user-abc",
            farm_id="farm-orange",
            field_strategies=[modified_field],
            economic_summary={"total_cost": 11800.0},
            environmental_metrics={"runoff_risk": 0.18},
            roi_estimate=0.45,
            metadata={"season": "2025"},
        )

        second_response = await in_memory_service.save_strategy(second_request)

        metric_list: List[str] = []
        metric_list.append("total_cost")
        metric_list.append("roi_estimate")
        metric_list.append("expected_yield")

        comparison_request = StrategyComparisonRequest(
            strategy_ids=[first_response.strategy_id, second_response.strategy_id],
            include_metrics=metric_list,
            comparison_window_days=None,
        )

        comparison_response = await in_memory_service.compare_strategies(comparison_request)

        assert isinstance(comparison_response, StrategyComparisonResponse)
        assert len(comparison_response.strategies) == 2
        assert comparison_response.metrics

    @pytest.mark.asyncio
    async def test_compare_strategies_missing_strategy(self, in_memory_service):
        """Ensure missing strategies produce lookup error."""
        metric_list: List[str] = []
        metric_list.append("total_cost")

        request = StrategyComparisonRequest(
            strategy_ids=["missing-1", "missing-2"],
            include_metrics=metric_list,
            comparison_window_days=None,
        )

        with pytest.raises(LookupError):
            await in_memory_service.compare_strategies(request)

    @pytest.mark.asyncio
    async def test_update_strategy_creates_new_version(self, in_memory_service):
        """Ensure update creates an additional strategy version."""
        base_field = FieldStrategyData(
            field_id="field-update-1",
            acres=70.0,
            crop_type="corn",
            recommended_rates={"N": 155.0},
            application_schedule=["pre-plant"],
            application_method="broadcast",
            expected_yield=188.0,
            total_cost=135.0,
            roi_projection=0.31,
        )

        create_request = SaveStrategyRequest(
            strategy_name="Update Plan",
            description="Plan prior to updates",
            user_id="user-update",
            farm_id="farm-update",
            field_strategies=[base_field],
            economic_summary={"total_cost": 11000.0},
            environmental_metrics={"runoff_risk": 0.23},
            roi_estimate=0.41,
            metadata={"season": "2025"},
        )

        initial_response = await in_memory_service.save_strategy(create_request)

        update_request = StrategyUpdateRequest(
            description="Plan after updates",
            economic_summary={"total_cost": 10850.0},
            environmental_metrics={"runoff_risk": 0.19},
            roi_estimate=0.44,
            version_notes="Adjusted cost and risk",
        )

        update_response = await in_memory_service.update_strategy(
            initial_response.strategy_id,
            update_request,
            user_id="user-update",
        )

        assert isinstance(update_response, StrategyUpdateResponse)
        assert update_response.latest_version.version_number == 2
        assert update_response.latest_version.version_notes == "Adjusted cost and risk"

    @pytest.mark.asyncio
    async def test_update_strategy_missing_record(self, in_memory_service):
        """Ensure missing strategy update raises error."""
        update_request = StrategyUpdateRequest(description="No strategy")
        with pytest.raises(LookupError):
            await in_memory_service.update_strategy("missing-strategy", update_request, user_id="user-1")


class TestStrategyManagementAPI:
    """API tests for strategy management endpoints."""

    @pytest.fixture(autouse=True)
    def override_dependency(self, in_memory_service):
        """Override dependency injection for consistent testing."""
        app.dependency_overrides[get_strategy_management_service] = lambda: in_memory_service
        yield
        app.dependency_overrides.pop(get_strategy_management_service, None)

    def test_save_strategy_endpoint_success(self):
        """Verify API endpoint stores strategy successfully."""
        client = TestClient(app)

        payload = {
            "strategy_name": "Corn Intensive Plan",
            "description": "Comprehensive corn fertility plan",
            "user_id": "user-321",
            "farm_id": "farm-789",
            "is_template": False,
            "tags": ["corn", "intensive"],
            "sharing": {"is_public": False, "shared_with": []},
            "field_strategies": [
                {
                    "field_id": "field-010",
                    "acres": 150.0,
                    "crop_type": "corn",
                    "recommended_rates": {"N": 200.0, "P": 60.0},
                    "application_schedule": ["pre-plant", "side-dress"],
                    "application_method": "broadcast",
                    "expected_yield": 210.0,
                    "total_cost": 240.0,
                    "roi_projection": 0.35,
                }
            ],
            "economic_summary": {"total_cost": 32000.0, "expected_profit": 15000.0},
            "environmental_metrics": {"runoff_risk": 0.18},
            "roi_estimate": 0.47,
            "metadata": {"season": "2025"},
            "version_notes": "Initial intensive corn plan",
        }

        response = client.post("/api/v1/strategies/save", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["created"] is True
        assert data["strategy_id"] is not None
        assert data["latest_version"]["version_number"] == 1

    def test_save_strategy_endpoint_validation_error(self, monkeypatch, in_memory_service):
        """Ensure validation errors return proper status."""
        async def mock_save_strategy(_):
            raise ValueError("Invalid request data")

        monkeypatch.setattr(in_memory_service, "save_strategy", mock_save_strategy)

        client = TestClient(app)

        payload = {
            "strategy_name": "Test Strategy",
            "description": "Invalid payload",
            "user_id": "user-555",
            "field_strategies": [
                {
                    "field_id": "field-xyz",
                    "acres": 10.0,
                    "crop_type": "corn",
                    "recommended_rates": {"N": 50.0},
                    "application_schedule": ["pre-plant"],
                    "application_method": "broadcast",
                }
            ],
        }

        response = client.post("/api/v1/strategies/save", json=payload)

        assert response.status_code == 400
        data = response.json()
        assert "Invalid request data" in data["detail"]

    def test_compare_strategies_endpoint_success(self, in_memory_service):
        """Ensure comparison endpoint returns metrics."""
        client = TestClient(app)

        first_payload = {
            "strategy_name": "Compare Plan A",
            "description": "First comparison strategy",
            "user_id": "user-900",
            "field_strategies": [
                {
                    "field_id": "field-900",
                    "acres": 50.0,
                    "crop_type": "corn",
                    "recommended_rates": {"N": 150.0},
                    "application_schedule": ["pre-plant"],
                    "application_method": "broadcast",
                    "expected_yield": 180.0,
                    "total_cost": 130.0,
                }
            ],
            "economic_summary": {"total_cost": 10000.0},
            "environmental_metrics": {"runoff_risk": 0.25},
            "roi_estimate": 0.4,
        }

        second_payload = {
            "strategy_name": "Compare Plan B",
            "description": "Second comparison strategy",
            "user_id": "user-900",
            "field_strategies": [
                {
                    "field_id": "field-901",
                    "acres": 55.0,
                    "crop_type": "corn",
                    "recommended_rates": {"N": 140.0},
                    "application_schedule": ["pre-plant", "mid-season"],
                    "application_method": "banded",
                    "expected_yield": 185.0,
                    "total_cost": 128.0,
                }
            ],
            "economic_summary": {"total_cost": 9800.0},
            "environmental_metrics": {"runoff_risk": 0.20},
            "roi_estimate": 0.45,
        }

        first_response = client.post("/api/v1/strategies/save", json=first_payload)
        second_response = client.post("/api/v1/strategies/save", json=second_payload)

        first_id = first_response.json()["strategy_id"]
        second_id = second_response.json()["strategy_id"]

        params = [
            ("strategy_ids", first_id),
            ("strategy_ids", second_id),
            ("include_metrics", "total_cost"),
            ("include_metrics", "roi_estimate"),
        ]

        compare_response = client.get("/api/v1/strategies/compare", params=params)

        assert compare_response.status_code == 200
        data = compare_response.json()
        assert len(data["strategies"]) == 2
        assert data["metrics"]

    def test_compare_strategies_endpoint_not_found(self):
        """Ensure comparison endpoint returns not found for unknown strategies."""
        client = TestClient(app)
        params = [
            ("strategy_ids", "missing-a"),
            ("strategy_ids", "missing-b"),
        ]

        response = client.get("/api/v1/strategies/compare", params=params)

        assert response.status_code == 404
        data = response.json()
        assert "Strategies not found" in data["detail"]

    def test_update_strategy_endpoint_success(self):
        """Ensure update endpoint creates a new version."""
        client = TestClient(app)

        create_payload = {
            "strategy_name": "Update Endpoint Plan",
            "description": "Original strategy",
            "user_id": "user-endpoint",
            "field_strategies": [
                {
                    "field_id": "field-endpoint",
                    "acres": 42.0,
                    "crop_type": "corn",
                    "recommended_rates": {"N": 140.0},
                    "application_schedule": ["pre-plant"],
                    "application_method": "broadcast",
                    "expected_yield": 175.0,
                    "total_cost": 120.0,
                }
            ],
            "economic_summary": {"total_cost": 9000.0},
            "environmental_metrics": {"runoff_risk": 0.26},
            "roi_estimate": 0.38,
        }

        create_response = client.post("/api/v1/strategies/save", json=create_payload)
        strategy_id = create_response.json()["strategy_id"]

        update_payload = {
            "description": "Updated strategy",
            "economic_summary": {"total_cost": 8800.0},
            "roi_estimate": 0.40,
            "version_notes": "Cost optimization",
        }

        params = [("user_id", "user-endpoint")]

        update_response = client.put(
            f"/api/v1/strategies/{strategy_id}/update",
            params=params,
            json=update_payload,
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["latest_version"]["version_number"] == 2

    def test_update_strategy_endpoint_not_found(self):
        """Ensure update endpoint returns not found for missing strategy."""
        client = TestClient(app)
        params = [("user_id", "user-zzz")]
        payload = {"description": "No strategy"}

        response = client.put("/api/v1/strategies/missing/update", params=params, json=payload)

        assert response.status_code == 404
