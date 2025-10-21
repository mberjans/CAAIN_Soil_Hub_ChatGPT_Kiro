import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.price_models import FertilizerType, FertilizerPrice, Base

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

def test_fertilizer_type_creation(session):
    fertilizer_type = FertilizerType(
        name="Urea",
        description="A common nitrogen fertilizer",
        category="nitrogen"
    )
    session.add(fertilizer_type)
    session.commit()

    assert fertilizer_type.id is not None
    assert fertilizer_type.name == "Urea"
    assert fertilizer_type.description == "A common nitrogen fertilizer"
    assert fertilizer_type.category == "nitrogen"
    assert fertilizer_type.created_at is not None
    assert fertilizer_type.updated_at is not None
    # Check relationship (assuming prices is a list)
    assert fertilizer_type.prices == []

def test_fertilizer_price_creation(session):
    """Test creating a FertilizerPrice instance and verifying its attributes."""
    # First create a fertilizer type to reference
    fertilizer_type = FertilizerType(
        name="Urea",
        description="A common nitrogen fertilizer",
        category="nitrogen"
    )
    session.add(fertilizer_type)
    session.commit()
    
    # Create a fertilizer price
    from datetime import datetime
    price_date = datetime(2024, 1, 15).date()
    
    fertilizer_price = FertilizerPrice(
        fertilizer_type_id=fertilizer_type.id,
        price=680.50,
        price_date=price_date,
        region="Midwest",
        source="USDA_NASS"
    )
    session.add(fertilizer_price)
    session.commit()
    
    # Verify the fertilizer price was created correctly
    assert fertilizer_price.id is not None
    assert fertilizer_price.fertilizer_type_id == fertilizer_type.id
    assert fertilizer_price.price == 680.50
    assert fertilizer_price.price_date == price_date
    assert fertilizer_price.region == "Midwest"
    assert fertilizer_price.source == "USDA_NASS"
    assert fertilizer_price.created_at is not None
    assert fertilizer_price.updated_at is not None
    
    # Verify the relationship to fertilizer_type
    assert fertilizer_price.fertilizer_type == fertilizer_type
    assert fertilizer_price.fertilizer_type.name == "Urea"
    
    # Verify the reverse relationship from fertilizer_type
    assert len(fertilizer_type.prices) == 1
    assert fertilizer_type.prices[0] == fertilizer_price