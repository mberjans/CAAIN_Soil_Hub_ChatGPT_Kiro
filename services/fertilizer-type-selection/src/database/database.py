from sqlalchemy import create_engine, Column, String, Float, DateTime, JSONB, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from uuid import uuid4

from ..models.priority_constraint_models import PriorityCategory, ConstraintType, AppliesTo

import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/fertilizer_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FertilizerPriorityDB(Base):
    __tablename__ = "fertilizer_priorities"

    priority_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    weight = Column(Float, nullable=False)
    category = Column(SQLEnum(PriorityCategory, name="priority_category_enum"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class FertilizerConstraintDB(Base):
    __tablename__ = "fertilizer_constraints"

    constraint_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    type = Column(SQLEnum(ConstraintType, name="constraint_type_enum"), nullable=False)
    value = Column(JSONB, nullable=False)
    unit = Column(String(20), nullable=True)
    applies_to = Column(SQLEnum(AppliesTo, name="applies_to_enum"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
