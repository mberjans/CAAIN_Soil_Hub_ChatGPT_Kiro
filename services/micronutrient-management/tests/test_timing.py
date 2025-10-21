import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from src.models.timing_models import MicronutrientApplicationTiming
from src.schemas.timing_schemas import MicronutrientApplicationTimingCreate, MicronutrientApplicationTimingUpdate
from src.services.timing_service import TimingService

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def timing_service():
    return TimingService()

@pytest.fixture
def sample_timing_data():
    return MicronutrientApplicationTimingCreate(
        micronutrient_id=uuid4(),
        crop_id=uuid4(),
        growth_stage="vegetative",
        timing_window_start=30,
        timing_window_end=45,
        environmental_conditions={"min_temp": 15, "max_temp": 30, "soil_moisture": "adequate"},
        efficiency_impact=0.9,
        notes="Apply before flowering"
    )

def test_create_timing(mock_db_session, timing_service, sample_timing_data):
    created_timing = timing_service.create_timing(mock_db_session, sample_timing_data)

    assert created_timing.micronutrient_id == sample_timing_data.micronutrient_id
    assert created_timing.growth_stage == sample_timing_data.growth_stage
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(created_timing)

def test_get_timing(mock_db_session, timing_service):
    timing_id = uuid4()
    mock_timing = MicronutrientApplicationTiming(id=timing_id, micronutrient_id=uuid4(), crop_id=uuid4(), growth_stage="vegetative", timing_window_start=30, timing_window_end=45, environmental_conditions={}, efficiency_impact=0.9)
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_timing

    fetched_timing = timing_service.get_timing(mock_db_session, timing_id)

    assert fetched_timing.id == timing_id
    assert fetched_timing.growth_stage == "vegetative"

def test_get_timings_by_micronutrient_crop(mock_db_session, timing_service):
    micronutrient_id = uuid4()
    crop_id = uuid4()
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = [
        MicronutrientApplicationTiming(id=uuid4(), micronutrient_id=micronutrient_id, crop_id=crop_id, growth_stage="vegetative", timing_window_start=30, timing_window_end=45, environmental_conditions={}, efficiency_impact=0.9),
        MicronutrientApplicationTiming(id=uuid4(), micronutrient_id=micronutrient_id, crop_id=crop_id, growth_stage="flowering", timing_window_start=60, timing_window_end=75, environmental_conditions={}, efficiency_impact=0.8)
    ]

    timings = timing_service.get_timings_by_micronutrient_crop(mock_db_session, micronutrient_id, crop_id)

    assert len(timings) == 2
    assert all(t.micronutrient_id == micronutrient_id for t in timings)
    assert all(t.crop_id == crop_id for t in timings)

def test_get_timings(mock_db_session, timing_service):
    mock_db_session.query.return_value.offset.return_value.limit.return_value.all.return_value = [
        MicronutrientApplicationTiming(id=uuid4(), micronutrient_id=uuid4(), crop_id=uuid4(), growth_stage="vegetative", timing_window_start=30, timing_window_end=45, environmental_conditions={}, efficiency_impact=0.9),
        MicronutrientApplicationTiming(id=uuid4(), micronutrient_id=uuid4(), crop_id=uuid4(), growth_stage="flowering", timing_window_start=60, timing_window_end=75, environmental_conditions={}, efficiency_impact=0.8)
    ]

    timings = timing_service.get_timings(mock_db_session)

    assert len(timings) == 2

def test_update_timing(mock_db_session, timing_service):
    timing_id = uuid4()
    existing_timing = MicronutrientApplicationTiming(id=timing_id, micronutrient_id=uuid4(), crop_id=uuid4(), growth_stage="vegetative", timing_window_start=30, timing_window_end=45, environmental_conditions={}, efficiency_impact=0.9)
    mock_db_session.query.return_value.filter.return_value.first.return_value = existing_timing

    update_data = MicronutrientApplicationTimingUpdate(growth_stage="flowering", efficiency_impact=0.95)
    updated_timing = timing_service.update_timing(mock_db_session, timing_id, update_data)

    assert updated_timing.growth_stage == "flowering"
    assert updated_timing.efficiency_impact == 0.95
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once_with(existing_timing)

def test_delete_timing(mock_db_session, timing_service):
    timing_id = uuid4()
    existing_timing = MicronutrientApplicationTiming(id=timing_id, micronutrient_id=uuid4(), crop_id=uuid4(), growth_stage="vegetative", timing_window_start=30, timing_window_end=45, environmental_conditions={}, efficiency_impact=0.9)
    mock_db_session.query.return_value.filter.return_value.first.return_value = existing_timing

    deleted_timing = timing_service.delete_timing(mock_db_session, timing_id)

    assert deleted_timing.id == timing_id
    mock_db_session.delete.assert_called_once_with(existing_timing)
    mock_db_session.commit.assert_called_once()