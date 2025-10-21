
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from uuid import uuid4, UUID
from datetime import date

from services.nutrient_deficiency.main import app
from services.nutrient_deficiency.src.database import Base, get_db
from services.nutrient_deficiency.src.models.soil_nutrient_models import SoilNutrientAnalysis
from services.nutrient_deficiency.src.schemas.soil_nutrient_schemas import SoilNutrientAnalysisCreate, MacroNutrients, MicroNutrients, OtherSoilProperties

# Setup for in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="session")
def session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
async def client_fixture(session: SessionLocal):
    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_analysis_data() -> SoilNutrientAnalysisCreate:
    return SoilNutrientAnalysisCreate(
        farm_id=uuid4(),
        field_id=uuid4(),
        analysis_date=date(2023, 10, 26),
        lab_name="AgriLab",
        sample_id="SL12345",
        macro_nutrients=MacroNutrients(
            nitrogen_total_n=120.5,
            phosphorus_p=30.2,
            potassium_k=250.0,
            sulfur_s=15.0,
            calcium_ca=1500.0,
            magnesium_mg=300.0
        ),
        micro_nutrients=MicroNutrients(
            boron_b=0.8,
            copper_cu=0.5,
            iron_fe=50.0,
            manganese_mn=25.0,
            zinc_zn=3.0,
            molybdenum_mo=0.1,
            chlorine_cl=10.0
        ),
        other_properties=OtherSoilProperties(
            ph=6.5,
            organic_matter_percent=3.5,
            cation_exchange_capacity_cec=15.0,
            electrical_conductivity_ec=0.8,
            soil_texture="loam"
        ),
        notes="Sample taken after corn harvest"
    )

@pytest.mark.asyncio
async def test_create_soil_nutrient_analysis(client: AsyncClient, sample_analysis_data: SoilNutrientAnalysisCreate):
    response = await client.post("/api/v1/soil-nutrient-analysis/", json=sample_analysis_data.model_dump_json(by_alias=True, exclude_unset=True))
    assert response.status_code == 201
    data = response.json()
    assert UUID(data["id"])
    assert data["farm_id"] == str(sample_analysis_data.farm_id)
    assert data["field_id"] == str(sample_analysis_data.field_id)
    assert data["lab_name"] == sample_analysis_data.lab_name
    assert data["macro_nutrients"]["nitrogen_total_n"] == sample_analysis_data.macro_nutrients.nitrogen_total_n

@pytest.mark.asyncio
async def test_get_soil_nutrient_analysis(client: AsyncClient, sample_analysis_data: SoilNutrientAnalysisCreate):
    create_response = await client.post("/api/v1/soil-nutrient-analysis/", json=sample_analysis_data.model_dump_json(by_alias=True, exclude_unset=True))
    created_id = create_response.json()["id"]

    get_response = await client.get(f"/api/v1/soil-nutrient-analysis/{created_id}")
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == created_id
    assert data["farm_id"] == str(sample_analysis_data.farm_id)

@pytest.mark.asyncio
async def test_get_soil_nutrient_analysis_not_found(client: AsyncClient):
    response = await client.get(f"/api/v1/soil-nutrient-analysis/{uuid4()}")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_analyses_by_farm(client: AsyncClient, sample_analysis_data: SoilNutrientAnalysisCreate):
    farm_id = uuid4()
    sample_analysis_data.farm_id = farm_id
    await client.post("/api/v1/soil-nutrient-analysis/", json=sample_analysis_data.model_dump_json(by_alias=True, exclude_unset=True))

    response = await client.get(f"/api/v1/soil-nutrient-analysis/farm/{farm_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["farm_id"] == str(farm_id)

@pytest.mark.asyncio
async def test_get_analyses_by_field(client: AsyncClient, sample_analysis_data: SoilNutrientAnalysisCreate):
    field_id = uuid4()
    sample_analysis_data.field_id = field_id
    await client.post("/api/v1/soil-nutrient-analysis/", json=sample_analysis_data.model_dump_json(by_alias=True, exclude_unset=True))

    response = await client.get(f"/api/v1/soil-nutrient-analysis/field/{field_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["field_id"] == str(field_id)

@pytest.mark.asyncio
async def test_update_soil_nutrient_analysis(client: AsyncClient, sample_analysis_data: SoilNutrientAnalysisCreate):
    create_response = await client.post("/api/v1/soil-nutrient-analysis/", json=sample_analysis_data.model_dump_json(by_alias=True, exclude_unset=True))
    created_id = create_response.json()["id"]

    updated_data = sample_analysis_data.model_copy(deep=True)
    updated_data.lab_name = "New Lab Name"
    updated_data.macro_nutrients.nitrogen_total_n = 150.0

    response = await client.put(f"/api/v1/soil-nutrient-analysis/{created_id}", json=updated_data.model_dump_json(by_alias=True, exclude_unset=True))
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_id
    assert data["lab_name"] == "New Lab Name"
    assert data["macro_nutrients"]["nitrogen_total_n"] == 150.0

@pytest.mark.asyncio
async def test_delete_soil_nutrient_analysis(client: AsyncClient, sample_analysis_data: SoilNutrientAnalysisCreate):
    create_response = await client.post("/api/v1/soil-nutrient-analysis/", json=sample_analysis_data.model_dump_json(by_alias=True, exclude_unset=True))
    created_id = create_response.json()["id"]

    delete_response = await client.delete(f"/api/v1/soil-nutrient-analysis/{created_id}")
    assert delete_response.status_code == 204

    get_response = await client.get(f"/api/v1/soil-nutrient-analysis/{created_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_soil_nutrient_analysis_not_found(client: AsyncClient):
    response = await client.delete(f"/api/v1/soil-nutrient-analysis/{uuid4()}")
    assert response.status_code == 404