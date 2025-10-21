import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models.priority_constraint_models import Priority, Constraint, PriorityType, ConstraintType, PriorityDB, ConstraintDB
from src.services.priority_constraint_service import PriorityConstraintService
from src.database.fertilizer_db import get_db_session

@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy AsyncSession for service testing."""
    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value.scalars.return_value.first.return_value = None
    session.execute.return_value.scalars.return_value.all.return_value = []
    return session

@pytest.fixture
def priority_service(mock_db_session):
    """Fixture for PriorityConstraintService with a mocked database session."""
    return PriorityConstraintService(mock_db_session)

@pytest.fixture
def client_with_mock_db(mock_db_session):
    """Test client with mocked database session dependency."""
    app.dependency_overrides[get_db_session] = lambda: mock_db_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_priority(priority_service, mock_db_session):
    """Test creating a new priority."""
    priority_data = Priority(priority_type=PriorityType.YIELD_MAXIMIZATION, weight=0.8, description="Maximize crop yield")
    
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    created_priority = await priority_service.create_priority(priority_data)

    assert created_priority.priority_type == PriorityType.YIELD_MAXIMIZATION.value
    assert created_priority.weight == 0.8
    assert created_priority.description == "Maximize crop yield"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(created_priority)

@pytest.mark.asyncio
async def test_get_priority(priority_service, mock_db_session):
    """Test retrieving a priority by ID."""
    priority_id = uuid4()
    mock_priority_db = PriorityDB(id=priority_id, priority_type=PriorityType.COST_MINIMIZATION.value, weight=0.7)
    
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_priority_db

    retrieved_priority = await priority_service.get_priority(priority_id)

    assert retrieved_priority.id == priority_id
    assert retrieved_priority.priority_type == PriorityType.COST_MINIMIZATION.value
    mock_db_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_priorities(priority_service, mock_db_session):
    """Test retrieving all priorities."""
    mock_priorities_db = [
        PriorityDB(id=uuid4(), priority_type=PriorityType.YIELD_MAXIMIZATION.value, weight=0.9),
        PriorityDB(id=uuid4(), priority_type=PriorityType.ENVIRONMENTAL_PROTECTION.value, weight=0.6)
    ]
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_priorities_db

    all_priorities = await priority_service.get_all_priorities()

    assert len(all_priorities) == 2
    assert all_priorities[0].priority_type == PriorityType.YIELD_MAXIMIZATION.value
    mock_db_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_priority(priority_service, mock_db_session):
    """Test updating an existing priority."""
    priority_id = uuid4()
    mock_priority_db = PriorityDB(id=priority_id, priority_type=PriorityType.YIELD_MAXIMIZATION.value, weight=0.8)
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_priority_db

    updated_data = Priority(priority_id=priority_id, priority_type=PriorityType.COST_MINIMIZATION, weight=0.7, description="Minimize costs")
    updated_priority = await priority_service.update_priority(priority_id, updated_data)

    assert updated_priority.id == priority_id
    assert updated_priority.priority_type == PriorityType.COST_MINIMIZATION.value
    assert updated_priority.weight == 0.7
    assert updated_priority.description == "Minimize costs"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(updated_priority)

@pytest.mark.asyncio
async def test_delete_priority(priority_service, mock_db_session):
    """Test deleting a priority."""
    priority_id = uuid4()
    mock_priority_db = PriorityDB(id=priority_id, priority_type=PriorityType.YIELD_MAXIMIZATION.value, weight=0.8)
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_priority_db
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    result = await priority_service.delete_priority(priority_id)

    assert result is True
    mock_db_session.delete.assert_called_once_with(mock_priority_db)
    mock_db_session.commit.assert_called_once()

@pytest.mark.asyncio
async def test_create_constraint(priority_service, mock_db_session):
    """Test creating a new constraint."""
    constraint_data = Constraint(constraint_type=ConstraintType.BUDGET, value=1000.0, unit="USD")
    
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.return_value = None

    created_constraint = await priority_service.create_constraint(constraint_data)

    assert created_constraint.constraint_type == ConstraintType.BUDGET.value
    assert created_constraint.value == "1000.0"
    assert created_constraint.unit == "USD"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(created_constraint)

@pytest.mark.asyncio
async def test_get_constraint(priority_service, mock_db_session):
    """Test retrieving a constraint by ID."""
    constraint_id = uuid4()
    mock_constraint_db = ConstraintDB(id=constraint_id, constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY.value, value="Sprayer")
    
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_constraint_db

    retrieved_constraint = await priority_service.get_constraint(constraint_id)

    assert retrieved_constraint.id == constraint_id
    assert retrieved_constraint.constraint_type == ConstraintType.EQUIPMENT_AVAILABILITY.value
    mock_db_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_get_all_constraints(priority_service, mock_db_session):
    """Test retrieving all constraints."""
    mock_constraints_db = [
        ConstraintDB(id=uuid4(), constraint_type=ConstraintType.BUDGET.value, value="5000.0"),
        ConstraintDB(id=uuid4(), constraint_type=ConstraintType.ENVIRONMENTAL_REGULATION.value, value="Local_Water_Quality")
    ]
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_constraints_db

    all_constraints = await priority_service.get_all_constraints()

    assert len(all_constraints) == 2
    assert all_constraints[0].constraint_type == ConstraintType.BUDGET.value
    mock_db_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_constraint(priority_service, mock_db_session):
    """Test updating an existing constraint."""
    constraint_id = uuid4()
    mock_constraint_db = ConstraintDB(id=constraint_id, constraint_type=ConstraintType.BUDGET.value, value="1000.0")
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_constraint_db

    updated_data = Constraint(constraint_id=constraint_id, constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY, value="Tractor", description="New tractor")
    updated_constraint = await priority_service.update_constraint(constraint_id, updated_data)

    assert updated_constraint.id == constraint_id
    assert updated_constraint.constraint_type == ConstraintType.EQUIPMENT_AVAILABILITY.value
    assert updated_constraint.value == "Tractor"
    assert updated_constraint.description == "New tractor"
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(updated_constraint)

@pytest.mark.asyncio
async def test_delete_constraint(priority_service, mock_db_session):
    """Test deleting a constraint."""
    constraint_id = uuid4()
    mock_constraint_db = ConstraintDB(id=constraint_id, constraint_type=ConstraintType.BUDGET.value, value="1000.0")
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_constraint_db
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    result = await priority_service.delete_constraint(constraint_id)

    assert result is True
    mock_db_session.delete.assert_called_once_with(mock_constraint_db)
    mock_db_session.commit.assert_called_once()

# --- API Integration Tests ---

@pytest.mark.integration
def test_api_create_priority(client_with_mock_db, mock_db_session):
    """Test POST /priorities/ endpoint."""
    priority_data = {
        "priority_type": "yield_maximization",
        "weight": 0.9,
        "description": "Maximize yield for corn"
    }
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda obj: setattr(obj, "id", uuid4())

    response = client_with_mock_db.post("/api/v1/priority-constraints/priorities/", json=priority_data)

    assert response.status_code == 201
    assert response.json()["priority_type"] == "yield_maximization"
    assert response.json()["weight"] == 0.9
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.integration
def test_api_get_priority(client_with_mock_db, mock_db_session):
    """Test GET /priorities/{priority_id} endpoint."""
    priority_id = uuid4()
    mock_priority_db = PriorityDB(id=priority_id, priority_type=PriorityType.COST_MINIMIZATION.value, weight=0.7)
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_priority_db

    response = client_with_mock_db.get(f"/api/v1/priority-constraints/priorities/{priority_id}")

    assert response.status_code == 200
    assert response.json()["priority_id"] == str(priority_id)
    assert response.json()["priority_type"] == "cost_minimizatio"

@pytest.mark.integration
def test_api_get_all_priorities(client_with_mock_db, mock_db_session):
    """Test GET /priorities/ endpoint for all priorities."""
    mock_priorities_db = [
        PriorityDB(id=uuid4(), priority_type=PriorityType.YIELD_MAXIMIZATION.value, weight=0.9),
        PriorityDB(id=uuid4(), priority_type=PriorityType.ENVIRONMENTAL_PROTECTION.value, weight=0.6)
    ]
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_priorities_db

    response = client_with_mock_db.get("/api/v1/priority-constraints/priorities/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["priority_type"] == "yield_maximization"

@pytest.mark.integration
def test_api_update_priority(client_with_mock_db, mock_db_session):
    """Test PUT /priorities/{priority_id} endpoint."""
    priority_id = uuid4()
    mock_priority_db = PriorityDB(id=priority_id, priority_type=PriorityType.YIELD_MAXIMIZATION.value, weight=0.8)
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_priority_db
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda obj: None

    updated_data = {
        "priority_id": str(priority_id),
        "priority_type": "cost_minimization",
        "weight": 0.7,
        "description": "Minimize costs"
    }
    response = client_with_mock_db.put(f"/api/v1/priority-constraints/priorities/{priority_id}", json=updated_data)

    assert response.status_code == 200
    assert response.json()["priority_type"] == "cost_minimization"
    assert response.json()["weight"] == 0.7
    mock_db_session.commit.assert_called_once()

@pytest.mark.integration
def test_api_delete_priority(client_with_mock_db, mock_db_session):
    """Test DELETE /priorities/{priority_id} endpoint."""
    priority_id = uuid4()
    mock_priority_db = PriorityDB(id=priority_id, priority_type=PriorityType.YIELD_MAXIMIZATION.value, weight=0.8)
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_priority_db
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    response = client_with_mock_db.delete(f"/api/v1/priority-constraints/priorities/{priority_id}")

    assert response.status_code == 204
    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.integration
def test_api_create_constraint(client_with_mock_db, mock_db_session):
    """Test POST /constraints/ endpoint."""
    constraint_data = {
        "constraint_type": "budget",
        "value": 1500.0,
        "unit": "USD",
        "description": "Max budget for fertilizer"
    }
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda obj: setattr(obj, "id", uuid4())

    response = client_with_mock_db.post("/api/v1/priority-constraints/constraints/", json=constraint_data)

    assert response.status_code == 201
    assert response.json()["constraint_type"] == "budget"
    assert response.json()["value"] == "1500.0"
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.integration
def test_api_get_constraint(client_with_mock_db, mock_db_session):
    """Test GET /constraints/{constraint_id} endpoint."""
    constraint_id = uuid4()
    mock_constraint_db = ConstraintDB(id=constraint_id, constraint_type=ConstraintType.EQUIPMENT_AVAILABILITY.value, value="Spreader")
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_constraint_db

    response = client_with_mock_db.get(f"/api/v1/priority-constraints/constraints/{constraint_id}")

    assert response.status_code == 200
    assert response.json()["constraint_id"] == str(constraint_id)
    assert response.json()["constraint_type"] == "equipment_availability"

@pytest.mark.integration
def test_api_get_all_constraints(client_with_mock_db, mock_db_session):
    """Test GET /constraints/ endpoint for all constraints."""
    mock_constraints_db = [
        ConstraintDB(id=uuid4(), constraint_type=ConstraintType.BUDGET.value, value="2000.0"),
        ConstraintDB(id=uuid4(), constraint_type=ConstraintType.TIME_WINDOW.value, value="Spring")
    ]
    mock_db_session.execute.return_value.scalars.return_value.all.return_value = mock_constraints_db

    response = client_with_mock_db.get("/api/v1/priority-constraints/constraints/")

    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["constraint_type"] == "budget"

@pytest.mark.integration
def test_api_update_constraint(client_with_mock_db, mock_db_session):
    """Test PUT /constraints/{constraint_id} endpoint."""
    constraint_id = uuid4()
    mock_constraint_db = ConstraintDB(id=constraint_id, constraint_type=ConstraintType.BUDGET.value, value="1000.0")
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_constraint_db
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda obj: None

    updated_data = {
        "constraint_id": str(constraint_id),
        "constraint_type": "equipment_availability",
        "value": "New Sprayer",
        "description": "Updated equipment"
    }
    response = client_with_mock_db.put(f"/api/v1/priority-constraints/constraints/{constraint_id}", json=updated_data)

    assert response.status_code == 200
    assert response.json()["constraint_type"] == "equipment_availability"
    assert response.json()["value"] == "New Sprayer"
    mock_db_session.commit.assert_called_once()

@pytest.mark.integration
def test_api_delete_constraint(client_with_mock_db, mock_db_session):
    """Test DELETE /constraints/{constraint_id} endpoint."""
    constraint_id = uuid4()
    mock_constraint_db = ConstraintDB(id=constraint_id, constraint_type=ConstraintType.BUDGET.value, value="1000.0")
    mock_db_session.execute.return_value.scalars.return_value.first.return_value = mock_constraint_db
    mock_db_session.delete.return_value = None
    mock_db_session.commit.return_value = None

    response = client_with_mock_db.delete(f"/api/v1/priority-constraints/constraints/{constraint_id}")

    assert response.status_code == 204
    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()

@pytest.mark.integration
def test_api_submit_priority_constraints(client_with_mock_db, mock_db_session):
    """Test POST / endpoint for combined submission."""
    combined_data = {
        "priorities": [
            {"priority_type": "yield_maximization", "weight": 0.9},
            {"priority_type": "cost_minimization", "weight": 0.7}
        ],
        "constraints": [
            {"constraint_type": "budget", "value": 2000.0, "unit": "USD"},
            {"constraint_type": "equipment_availability", "value": "Tractor"}
        ]
    }
    mock_db_session.add.return_value = None
    mock_db_session.commit.return_value = None
    mock_db_session.refresh.side_effect = lambda obj: setattr(obj, "id", uuid4())

    response = client_with_mock_db.post("/api/v1/priority-constraints/", json=combined_data)

    assert response.status_code == 200
    assert response.json()["message"] == "Priorities and constraints submitted successfully"
    assert response.json()["created_priorities_count"] == 2
    assert response.json()["created_constraints_count"] == 2
    assert mock_db_session.add.call_count == 4  # 2 priorities + 2 constraints
    assert mock_db_session.commit.call_count == 4
