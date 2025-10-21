import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.price_models import FertilizerType, Base

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