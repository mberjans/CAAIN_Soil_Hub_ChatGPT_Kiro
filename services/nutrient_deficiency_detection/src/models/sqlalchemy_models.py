from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import TypeDecorator, TEXT
import uuid
import json
from datetime import datetime

from .deficiency_models import Nutrient, Severity, PlantPart

# Custom TypeDecorator to handle ARRAY for PostgreSQL and JSON for SQLite
class ChoiceArray(TypeDecorator):
    """Enables to store a list of choices in a TEXT column in SQLite and ARRAY in PostgreSQL.
    """
    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return [v.value for v in value] if value and isinstance(value[0], PlantPart) else value
            else:
                return json.dumps([v.value for v in value] if value and isinstance(value[0], PlantPart) else value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if dialect.name == 'postgresql':
                return [PlantPart(v) for v in value] if self.as_enum else value
            else: # SQLite
                loaded = json.loads(value)
                return [PlantPart(v) for v in loaded] if self.as_enum else loaded
        return value

    def __init__(self, type, **kw):
        self.as_enum = kw.pop('as_enum', False)
        super(ChoiceArray, self).__init__(**kw)
        self.type = type

    def copy(self, **kw):
        return ChoiceArray(self.type, **kw)

Base = declarative_base()

class NutrientDeficiencySymptomORM(Base):
    __tablename__ = "nutrient_deficiency_symptoms"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nutrient = Column(SQLEnum(Nutrient, name="nutrient_enum", create_type=False), nullable=False, index=True)
    crop_type = Column(String, nullable=False, index=True)
    symptom_name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    affected_parts = Column(ChoiceArray(String, as_enum=True), nullable=False) # Use custom type
    visual_characteristics = Column(ChoiceArray(String), nullable=False) # Use custom type
    typical_severity = Column(SQLEnum(Severity, name="severity_enum", create_type=False), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    __table_args__ = (
        # Ensure unique combination of nutrient, crop_type, and symptom_name
        # This prevents duplicate symptom definitions
        # UniqueConstraint('nutrient', 'crop_type', 'symptom_name', name='_nutrient_crop_symptom_uc'),
    )

    def __repr__(self):
        return f"<NutrientDeficiencySymptom(nutrient='{self.nutrient}', crop_type='{self.crop_type}', symptom_name='{self.symptom_name}')>"

# Example of how to set up engine and session (adjust as per actual project setup)
# DATABASE_URL = "postgresql://user:password@host:port/dbname"
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# To create tables (run once or via migration tool like Alembic)
# Base.metadata.create_all(bind=engine)
