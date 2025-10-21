"""
Image Analysis Models - JOB3-003.3.impl

SQLAlchemy models for storing image analysis results and deficiency detection data.
Follows established AFAS database patterns and conventions.

Autonomous Farm Advisory System
Version: 1.0
Date: December 2024
"""

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, CheckConstraint, Index, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

# Use the same Base as the rest of the AFAS system
Base = declarative_base()

# For testing compatibility with SQLite, always use String for UUID and JSON for JSONB
# This works with both SQLite and PostgreSQL
def UUIDColumn(*args, **kwargs):
    """Create a UUID column that works with both PostgreSQL and SQLite."""
    # Convert default UUID to string if present
    if 'default' in kwargs and callable(kwargs['default']):
        original_default = kwargs['default']
        kwargs['default'] = lambda: str(original_default())
    return Column(String(36), *args, **kwargs)

def JSONBColumn(*args, **kwargs):
    """Create a JSON column that works with both PostgreSQL and SQLite."""
    return Column(JSON, *args, **kwargs)


class ImageAnalysis(Base):
    """
    Image analysis model for storing crop image metadata and analysis results.

    This model stores information about uploaded crop images and their
    processing status, following AFAS database conventions.
    """

    __tablename__ = 'image_analyses'

    # Primary identification - following AFAS UUID pattern
    id = UUIDColumn(primary_key=True, default=uuid.uuid4)

    # Image metadata - matching test expectations
    image_path = Column(String(512), nullable=False, index=True)
    crop_type = Column(String(100), nullable=False)
    growth_stage = Column(String(50))
    image_size_mb = Column(Float)
    upload_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    processing_status = Column(String(50), default='pending', nullable=False)
    quality_score = Column(Float)

    # Additional metadata following AFAS patterns
    original_filename = Column(String(255))
    image_format = Column(String(10))  # jpg, png, etc.
    image_width_pixels = Column(Integer)
    image_height_pixels = Column(Integer)
    model_version = Column(String(20))

    # Analysis results (JSON fields for flexibility)
    image_quality_metrics = JSONBColumn()
    analysis_metadata = JSONBColumn()

    # AFAS standard timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    deficiency_detections = relationship(
        "DeficiencyDetection",
        back_populates="image_analysis",
        cascade="all, delete-orphan"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "processing_status IN ('pending', 'processing', 'completed', 'failed')",
            name='check_processing_status'
        ),
        CheckConstraint(
            "quality_score >= 0 AND quality_score <= 1",
            name='check_quality_score_range'
        ),
        CheckConstraint(
            "image_size_mb > 0",
            name='check_positive_image_size'
        ),
        Index('idx_image_analyses_crop_type', 'crop_type'),
        Index('idx_image_analyses_status', 'processing_status'),
        Index('idx_image_analyses_upload_time', 'upload_timestamp'),
    )

    def __repr__(self):
        return f"<ImageAnalysis(id='{self.id}', crop_type='{self.crop_type}', status='{self.processing_status}')>"

    @property
    def is_completed(self) -> bool:
        """Check if analysis is completed."""
        return self.processing_status == 'completed'

    @property
    def has_deficiencies(self) -> bool:
        """Check if any deficiencies were detected."""
        return len(self.deficiency_detections) > 0


class DeficiencyDetection(Base):
    """
    Deficiency detection model for storing nutrient deficiency analysis results.

    This model stores detailed results about detected nutrient deficiencies
    from crop image analysis, following AFAS database conventions.
    """

    __tablename__ = 'deficiency_detections'

    # Primary identification - following AFAS UUID pattern
    id = UUIDColumn(primary_key=True, default=uuid.uuid4)

    # Foreign key relationship - using the test expected name
    image_analysis_id = UUIDColumn(ForeignKey('image_analyses.id', ondelete='CASCADE'), nullable=False)

    # Detection results - matching test expectations and AFAS patterns
    nutrient = Column(String(50), nullable=False)
    confidence_score = Column(Float, nullable=False)
    severity = Column(String(20), nullable=False)
    affected_area_percent = Column(Float)

    # Additional detection data
    symptoms_detected = JSONBColumn()  # List of detected symptoms
    symptom_indicators = JSONBColumn()  # Detailed symptom analysis
    affected_regions = JSONBColumn()  # Regions of the image affected
    color_analysis = JSONBColumn()  # Color-based analysis data
    pattern_analysis = JSONBColumn()  # Pattern recognition results

    # Contextual information
    deficiency_type = Column(String(30))  # primary, secondary, micronutrient
    severity_score = Column(Float)  # Numerical severity (0-1)
    deficiency_probability = Column(Float)  # Overall probability

    # Model information
    model_version = Column(String(20))
    model_confidence_metrics = JSONBColumn()

    # Validation and expert review
    expert_validated = Column(Boolean, default=False)
    validation_notes = Column(Text)
    validation_date = Column(DateTime(timezone=True))

    # AFAS standard timestamp fields
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    image_analysis = relationship("ImageAnalysis", back_populates="deficiency_detections")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "confidence_score >= 0 AND confidence_score <= 1",
            name='check_confidence_score_range'
        ),
        CheckConstraint(
            "affected_area_percent >= 0 AND affected_area_percent <= 100",
            name='check_affected_area_range'
        ),
        CheckConstraint(
            "severity IN ('mild', 'moderate', 'severe')",
            name='check_severity_values'
        ),
        CheckConstraint(
            "severity_score >= 0 AND severity_score <= 1",
            name='check_severity_score_range'
        ),
        CheckConstraint(
            "deficiency_probability >= 0 AND deficiency_probability <= 1",
            name='check_deficiency_probability_range'
        ),
        Index('idx_deficiency_detections_analysis', 'image_analysis_id'),
        Index('idx_deficiency_detections_nutrient', 'nutrient'),
        Index('idx_deficiency_detections_severity', 'severity'),
        Index('idx_deficiency_detections_confidence', 'confidence_score'),
    )

    def __repr__(self):
        return f"<DeficiencyDetection(id='{self.id}', nutrient='{self.nutrient}', severity='{self.severity}')>"

    @property
    def is_high_confidence(self) -> bool:
        """Check if detection has high confidence (>0.7)."""
        return self.confidence_score > 0.7

    @property
    def is_severe(self) -> bool:
        """Check if deficiency is severe."""
        return self.severity == 'severe'

    @property
    def requires_immediate_action(self) -> bool:
        """Check if deficiency requires immediate attention."""
        return self.severity == 'severe' and self.confidence_score > 0.6


# Utility functions for model operations

def create_image_analysis(
    image_path: str,
    crop_type: str,
    growth_stage: Optional[str] = None,
    image_size_mb: Optional[float] = None,
    quality_score: Optional[float] = None
) -> ImageAnalysis:
    """
    Create a new ImageAnalysis record with common defaults.

    Args:
        image_path: Path to the image file
        crop_type: Type of crop (corn, soybean, wheat, etc.)
        growth_stage: Growth stage of the crop
        image_size_mb: Size of the image in megabytes
        quality_score: Quality assessment score (0-1)

    Returns:
        ImageAnalysis instance
    """
    return ImageAnalysis(
        image_path=image_path,
        crop_type=crop_type,
        growth_stage=growth_stage,
        image_size_mb=image_size_mb,
        quality_score=quality_score,
        processing_status='pending'
    )


def create_deficiency_detection(
    image_analysis_id: uuid.UUID,
    nutrient: str,
    confidence_score: float,
    severity: str,
    affected_area_percent: Optional[float] = None,
    symptoms_detected: Optional[List[str]] = None,
    model_version: str = "v1.0"
) -> DeficiencyDetection:
    """
    Create a new DeficiencyDetection record.

    Args:
        image_analysis_id: UUID of the associated image analysis
        nutrient: Nutrient name (nitrogen, phosphorus, etc.)
        confidence_score: Detection confidence (0-1)
        severity: Severity level (mild, moderate, severe)
        affected_area_percent: Percentage of plant affected
        symptoms_detected: List of detected symptoms
        model_version: Model version used for detection

    Returns:
        DeficiencyDetection instance
    """
    return DeficiencyDetection(
        image_analysis_id=image_analysis_id,
        nutrient=nutrient,
        confidence_score=confidence_score,
        severity=severity,
        affected_area_percent=affected_area_percent,
        symptoms_detected=symptoms_detected or [],
        model_version=model_version
    )