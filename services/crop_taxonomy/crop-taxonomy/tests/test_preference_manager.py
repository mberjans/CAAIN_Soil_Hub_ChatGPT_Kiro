import pytest
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from src.services.preference_manager import FarmerPreferenceManager

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

def test_farmer_preference_manager_instantiation(mock_db_session):
    manager = FarmerPreferenceManager(mock_db_session)
    assert manager is not None
    assert manager.db == mock_db_session
