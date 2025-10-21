import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from src.main import app
from src.database.database import Base, get_db, FertilizerPriorityDB, FertilizerConstraintDB
from src.models.priority_constraint_models import (
    PriorityCategory, ConstraintType, AppliesTo,
    FertilizerPriorityCreate, FertilizerConstraintCreate
)

# Setup in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# --- Test Fertilizer Priorities ---

def test_create_priority(client, db_session):
    user_id = uuid4()
    priority_data = FertilizerPriorityCreate(
        user_id=user_id,
        name="Environmental Impact",
        description="Minimize environmental footprint",
        weight=0.9,
        category=PriorityCategory.ENVIRONMENTAL
    )
    response = client.post("/api/v1/fertilizer-type-selection/priorities", json=priority_data.model_dump_json().replace('"', '\"'))
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Environmental Impact"
    assert data["user_id"] == str(user_id)
    assert "priority_id" in data

def test_get_priority(client, db_session):
    user_id = uuid4()
    priority_data = FertilizerPriorityDB(
        user_id=user_id,
        name="Yield Maximization",
        description="Maximize crop yield",
        weight=0.8,
        category=PriorityCategory.AGRONOMIC
    )
    db_session.add(priority_data)
    db_session.commit()
    db_session.refresh(priority_data)

    response = client.get(f"/api/v1/fertilizer-type-selection/priorities/{priority_data.priority_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Yield Maximization"
    assert data["priority_id"] == str(priority_data.priority_id)

def test_get_priority_not_found(client):
    response = client.get(f"/api/v1/fertilizer-type-selection/priorities/{uuid4()}")
    assert response.status_code == 404

def test_get_priorities_by_user(client, db_session):
    user_id = uuid4()
    priority1 = FertilizerPriorityDB(user_id=user_id, name="P1", weight=0.7, category=PriorityCategory.ECONOMIC)
    priority2 = FertilizerPriorityDB(user_id=user_id, name="P2", weight=0.6, category=PriorityCategory.OPERATIONAL)
    db_session.add_all([priority1, priority2])
    db_session.commit()

    response = client.get(f"/api/v1/fertilizer-type-selection/priorities/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "P1" or data[0]["name"] == "P2"

def test_update_priority(client, db_session):
    user_id = uuid4()
    priority_data = FertilizerPriorityDB(user_id=user_id, name="Old Name", weight=0.5, category=PriorityCategory.ECONOMIC)
    db_session.add(priority_data)
    db_session.commit()
    db_session.refresh(priority_data)

    update_data = {"name": "New Name", "weight": 0.9}
    response = client.put(f"/api/v1/fertilizer-type-selection/priorities/{priority_data.priority_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["weight"] == 0.9

def test_delete_priority(client, db_session):
    user_id = uuid4()
    priority_data = FertilizerPriorityDB(user_id=user_id, name="To Delete", weight=0.1, category=PriorityCategory.OPERATIONAL)
    db_session.add(priority_data)
    db_session.commit()
    db_session.refresh(priority_data)

    response = client.delete(f"/api/v1/fertilizer-type-selection/priorities/{priority_data.priority_id}")
    assert response.status_code == 204

    response = client.get(f"/api/v1/fertilizer-type-selection/priorities/{priority_data.priority_id}")
    assert response.status_code == 404

# --- Test Fertilizer Constraints ---

def test_create_constraint(client, db_session):
    user_id = uuid4()
    constraint_data = FertilizerConstraintCreate(
        user_id=user_id,
        name="Max Nitrogen",
        description="Maximum nitrogen application rate",
        type=ConstraintType.REGULATORY,
        value=150.0,
        unit="kg/ha",
        applies_to=AppliesTo.NUTRIENT
    )
    response = client.post("/api/v1/fertilizer-type-selection/constraints", json=constraint_data.model_dump_json().replace('"', '\"'))
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Max Nitrogen"
    assert data["user_id"] == str(user_id)
    assert "constraint_id" in data

def test_get_constraint(client, db_session):
    user_id = uuid4()
    constraint_data = FertilizerConstraintDB(
        user_id=user_id,
        name="Organic Certified",
        type=ConstraintType.REGULATORY,
        value=True,
        applies_to=AppliesTo.FERTILIZER_TYPE
    )
    db_session.add(constraint_data)
    db_session.commit()
    db_session.refresh(constraint_data)

    response = client.get(f"/api/v1/fertilizer-type-selection/constraints/{constraint_data.constraint_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Organic Certified"
    assert data["constraint_id"] == str(constraint_data.constraint_id)

def test_get_constraint_not_found(client):
    response = client.get(f"/api/v1/fertilizer-type-selection/constraints/{uuid4()}")
    assert response.status_code == 404

def test_get_constraints_by_user(client, db_session):
    user_id = uuid4()
    constraint1 = FertilizerConstraintDB(user_id=user_id, name="C1", type=ConstraintType.ECONOMIC, value=100, applies_to=AppliesTo.COST)
    constraint2 = FertilizerConstraintDB(user_id=user_id, name="C2", type=ConstraintType.SAFETY, value="gloves", applies_to=AppliesTo.APPLICATION_METHOD)
    db_session.add_all([constraint1, constraint2])
    db_session.commit()

    response = client.get(f"/api/v1/fertilizer-type-selection/constraints/user/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "C1" or data[0]["name"] == "C2"

def test_update_constraint(client, db_session):
    user_id = uuid4()
    constraint_data = FertilizerConstraintDB(user_id=user_id, name="Old Constraint", type=ConstraintType.AGRONOMIC, value="some_value", applies_to=AppliesTo.NUTRIENT)
    db_session.add(constraint_data)
    db_session.commit()
    db_session.refresh(constraint_data)

    update_data = {"name": "New Constraint", "value": "another_value"}
    response = client.put(f"/api/v1/fertilizer-type-selection/constraints/{constraint_data.constraint_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Constraint"
    assert data["value"] == "another_value"

def test_delete_constraint(client, db_session):
    user_id = uuid4()
    constraint_data = FertilizerConstraintDB(user_id=user_id, name="To Delete", type=ConstraintType.ENVIRONMENTAL, value=False, applies_to=AppliesTo.ENVIRONMENTAL_IMPACT)
    db_session.add(constraint_data)
    db_session.commit()
    db_session.refresh(constraint_data)

    response = client.delete(f"/api/v1/fertilizer-type-selection/constraints/{constraint_data.constraint_id}")
    assert response.status_code == 204

    response = client.get(f"/api/v1/fertilizer-type-selection/constraints/{constraint_data.constraint_id}")
    assert response.status_code == 404
