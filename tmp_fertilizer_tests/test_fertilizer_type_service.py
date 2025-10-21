import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from services.fertilizer_application.src.database.fertilizer_db import Base, get_db
from services.fertilizer_application.src.models.fertilizer_type_models import FertilizerType, FertilizerTypeEnum, EnvironmentalImpactEnum
from services.fertilizer_application.src.schemas.fertilizer_type_schemas import FertilizerTypeCreate, FertilizerTypeUpdate, NPKRatio
from services.fertilizer_application.src.services.fertilizer_type_service import FertilizerTypeService

# Setup for in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = SessionTesting()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="fertilizer_service")
def fertilizer_service_fixture(session):
    return FertilizerTypeService(session)

def test_create_fertilizer_type(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    fertilizer_data = FertilizerTypeCreate(
        name="Test Fertilizer",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk,
        cost_per_unit=1.5,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    fertilizer = fertilizer_service.create_fertilizer_type(fertilizer_data)

    assert fertilizer.id is not None
    assert fertilizer.name == "Test Fertilizer"
    assert fertilizer.type == FertilizerTypeEnum.SYNTHETIC
    assert fertilizer.npk_ratio == {"N": 10.0, "P": 10.0, "K": 10.0}
    assert fertilizer.cost_per_unit == 1.5

def test_create_fertilizer_type_duplicate_name(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    fertilizer_data = FertilizerTypeCreate(
        name="Duplicate Fertilizer",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk,
        cost_per_unit=1.5,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    fertilizer_service.create_fertilizer_type(fertilizer_data)

    with pytest.raises(ValueError, match="Fertilizer type with this name already exists."):
        fertilizer_service.create_fertilizer_type(fertilizer_data)

def test_get_fertilizer_type(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    fertilizer_data = FertilizerTypeCreate(
        name="Get Me Fertilizer",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk,
        cost_per_unit=1.5,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    created_fertilizer = fertilizer_service.create_fertilizer_type(fertilizer_data)

    fetched_fertilizer = fertilizer_service.get_fertilizer_type(created_fertilizer.id)
    assert fetched_fertilizer.name == "Get Me Fertilizer"

def test_get_fertilizer_type_by_name(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    fertilizer_data = FertilizerTypeCreate(
        name="Get By Name Fertilizer",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk,
        cost_per_unit=1.5,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    fertilizer_service.create_fertilizer_type(fertilizer_data)

    fetched_fertilizer = fertilizer_service.get_fertilizer_type_by_name("Get By Name Fertilizer")
    assert fetched_fertilizer.name == "Get By Name Fertilizer"

def test_get_all_fertilizer_types(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    fertilizer_data1 = FertilizerTypeCreate(
        name="Fertilizer 1",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk,
        cost_per_unit=1.0,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.LOW,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    fertilizer_data2 = FertilizerTypeCreate(
        name="Fertilizer 2",
        type=FertilizerTypeEnum.ORGANIC,
        npk_ratio=npk,
        cost_per_unit=2.0,
        unit="lb",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="slow",
        organic_certified=True,
        application_methods=["foliar"]
    )
    fertilizer_service.create_fertilizer_type(fertilizer_data1)
    fertilizer_service.create_fertilizer_type(fertilizer_data2)

    all_fertilizers = fertilizer_service.get_all_fertilizer_types()
    assert len(all_fertilizers) == 2
    assert any(f.name == "Fertilizer 1" for f in all_fertilizers)
    assert any(f.name == "Fertilizer 2" for f in all_fertilizers)

def test_update_fertilizer_type(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    fertilizer_data = FertilizerTypeCreate(
        name="Update Me Fertilizer",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk,
        cost_per_unit=1.5,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    created_fertilizer = fertilizer_service.create_fertilizer_type(fertilizer_data)

    update_data = FertilizerTypeUpdate(
        name="Updated Fertilizer Name",
        cost_per_unit=2.0,
        organic_certified=True
    )
    updated_fertilizer = fertilizer_service.update_fertilizer_type(created_fertilizer.id, update_data)

    assert updated_fertilizer.name == "Updated Fertilizer Name"
    assert updated_fertilizer.cost_per_unit == 2.0
    assert updated_fertilizer.organic_certified is True
    assert updated_fertilizer.type == FertilizerTypeEnum.SYNTHETIC  # Should remain unchanged

def test_update_fertilizer_type_not_found(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    update_data = FertilizerTypeUpdate(
        name="Non Existent",
        cost_per_unit=2.0
    )
    updated_fertilizer = fertilizer_service.update_fertilizer_type(999, update_data)
    assert updated_fertilizer is None

def test_delete_fertilizer_type(fertilizer_service: FertilizerTypeService):
    npk = NPKRatio(N=10, P=10, K=10)
    fertilizer_data = FertilizerTypeCreate(
        name="Delete Me Fertilizer",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk,
        cost_per_unit=1.5,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    created_fertilizer = fertilizer_service.create_fertilizer_type(fertilizer_data)

    deleted_fertilizer = fertilizer_service.delete_fertilizer_type(created_fertilizer.id)
    assert deleted_fertilizer.name == "Delete Me Fertilizer"
    assert fertilizer_service.get_fertilizer_type(created_fertilizer.id) is None

def test_delete_fertilizer_type_not_found(fertilizer_service: FertilizerTypeService):
    deleted_fertilizer = fertilizer_service.delete_fertilizer_type(999)
    assert deleted_fertilizer is None

def test_compare_fertilizer_types(fertilizer_service: FertilizerTypeService):
    npk1 = NPKRatio(N=10, P=10, K=10)
    fertilizer_data1 = FertilizerTypeCreate(
        name="Compare Fert 1",
        type=FertilizerTypeEnum.SYNTHETIC,
        npk_ratio=npk1,
        cost_per_unit=1.0,
        unit="kg",
        environmental_impact_score=EnvironmentalImpactEnum.LOW,
        release_rate="fast",
        organic_certified=False,
        application_methods=["broadcast"]
    )
    npk2 = NPKRatio(N=5, P=15, K=5)
    fertilizer_data2 = FertilizerTypeCreate(
        name="Compare Fert 2",
        type=FertilizerTypeEnum.ORGANIC,
        npk_ratio=npk2,
        cost_per_unit=2.0,
        unit="lb",
        environmental_impact_score=EnvironmentalImpactEnum.MEDIUM,
        release_rate="slow",
        organic_certified=True,
        application_methods=["foliar"]
    )
    created_fert1 = fertilizer_service.create_fertilizer_type(fertilizer_data1)
    created_fert2 = fertilizer_service.create_fertilizer_type(fertilizer_data2)

    compared_fertilizers = fertilizer_service.compare_fertilizer_types([created_fert1.id, created_fert2.id])
    assert len(compared_fertilizers) == 2
    assert any(f.name == "Compare Fert 1" for f in compared_fertilizers)
    assert any(f.name == "Compare Fert 2" for f in compared_fertilizers)

def test_compare_fertilizer_types_not_found(fertilizer_service: FertilizerTypeService):
    compared_fertilizers = fertilizer_service.compare_fertilizer_types([999])
    assert len(compared_fertilizers) == 0