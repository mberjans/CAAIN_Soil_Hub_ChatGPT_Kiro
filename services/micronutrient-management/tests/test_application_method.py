import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from src.models.application_models import MicronutrientApplicationMethod
from src.schemas.application_schemas import MicronutrientApplicationMethodCreate, MicronutrientApplicationMethodUpdate
from src.services.application_method_service import ApplicationMethodService

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def application_method_service():
    return ApplicationMethodService()

@pytest.fixture
def sample_method_data():
    return MicronutrientApplicationMethodCreate(
        name="Foliar Spray",
        description="Application directly to leaves",
        method_type="foliar",
        efficiency_rate=0.85,
        equipment_requirements=["sprayer"],
        cost_per_unit_area=15.0,
        environmental_impact={"runoff_risk": "low", "leaching_risk": "low"}
    )

def test_create_method(mock_db_session, application_method_service, sample_method_data):
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
    created_method = application_method_service.create_method(mock_db_session, sample_method_data)

    assert created_method.name == sample_method_data.name
    assert created_method.method_type == sample_method_data.method_type
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(created_method)

def test_get_method(mock_db_session, application_method_service):
    method_id = uuid4()
    mock_method = MicronutrientApplicationMethod(id=method_id, name="Test Method", method_type="soil", efficiency_rate=0.7, equipment_requirements=[], cost_per_unit_area=10.0, environmental_impact={})
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_method

    fetched_method = application_method_service.get_method(mock_db_session, method_id)

    assert fetched_method.id == method_id
    assert fetched_method.name == "Test Method"

def test_get_method_by_name(mock_db_session, application_method_service):
    method_name = "Test Method"
    mock_method = MicronutrientApplicationMethod(id=uuid4(), name=method_name, method_type="soil", efficiency_rate=0.7, equipment_requirements=[], cost_per_unit_area=10.0, environmental_impact={})
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_method

    fetched_method = application_method_service.get_method_by_name(mock_db_session, method_name)

    assert fetched_method.name == method_name

def test_get_methods(mock_db_session, application_method_service):
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [
        MicronutrientApplicationMethod(id=uuid4(), name="Method 1", method_type="soil", efficiency_rate=0.7, equipment_requirements=[], cost_per_unit_area=10.0, environmental_impact={}),
        MicronutrientApplicationMethod(id=uuid4(), name="Method 2", method_type="foliar", efficiency_rate=0.8, equipment_requirements=[], cost_per_unit_area=12.0, environmental_impact={})
    ]

    methods = application_method_service.get_methods(mock_db_session)

    assert len(methods) == 2
    assert methods[0].name == "Method 1"

def test_update_method(mock_db_session, application_method_service):
    method_id = uuid4()
    existing_method = MicronutrientApplicationMethod(id=method_id, name="Old Name", method_type="soil", efficiency_rate=0.7, equipment_requirements=[], cost_per_unit_area=10.0, environmental_impact={})
    mock_db_session.query.return_value.filter.return_value.first.return_value = existing_method

    update_data = MicronutrientApplicationMethodUpdate(name="New Name", efficiency_rate=0.9)
    updated_method = application_method_service.update_method(mock_db_session, method_id, update_data)

    assert updated_method.name == "New Name"
    assert updated_method.efficiency_rate == 0.9
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(existing_method)

def test_delete_method(mock_db_session, application_method_service):
    method_id = uuid4()
    existing_method = MicronutrientApplicationMethod(id=method_id, name="To Delete", method_type="soil", efficiency_rate=0.7, equipment_requirements=[], cost_per_unit_area=10.0, environmental_impact={})
    mock_db_session.query.return_value.filter.return_value.first.return_value = existing_method

    deleted_method = application_method_service.delete_method(mock_db_session, method_id)

    assert deleted_method.id == method_id
    mock_db_session.delete.assert_called_once_with(existing_method)
    mock_db_session.commit.assert_called_once()
