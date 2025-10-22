from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Replace with your actual database URL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost/caain_soil_hub"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
