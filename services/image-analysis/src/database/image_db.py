from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class ImageAnalysisResult(Base):
    __tablename__ = "image_analysis_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True) # Optional, if user context is available
    farm_id = Column(UUID(as_uuid=True), nullable=True)
    field_id = Column(UUID(as_uuid=True), nullable=True)
    crop_type = Column(String, nullable=False)
    image_url = Column(String, nullable=True) # URL to stored image (e.g., S3 bucket)
    image_quality_score = Column(Float, nullable=False)
    image_quality_issues = Column(JSON, nullable=True)
    deficiencies = Column(JSON, nullable=True) # Store list of DeficiencySymptom as JSON
    recommendations = Column(JSON, nullable=True) # Store list of Recommendation as JSON
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ImageAnalysisResult(id='{self.id}', crop_type='{self.crop_type}')>"

class ImageDatabase:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def save_analysis_result(self, result: ImageAnalysisResult):
        db = self.SessionLocal()
        try:
            db.add(result)
            db.commit()
            db.refresh(result)
            return result
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
