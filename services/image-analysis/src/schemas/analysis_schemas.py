"""
Analysis schemas for image analysis API requests and validation.

This module contains Pydantic schemas for validating image analysis requests,
including crop type validation, growth stage validation, and metadata handling.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional


class ImageAnalysisRequest(BaseModel):
    """Schema for image analysis requests."""

    crop_type: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Type of crop being analyzed (e.g., corn, soybean, wheat)"
    )
    growth_stage: Optional[str] = Field(
        None,
        description="Growth stage of the crop (e.g., V2, V4, V6, R1, R2)"
    )
    additional_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the image or analysis request"
    )

    @validator('crop_type')
    def validate_crop_type(cls, v):
        """Validate that crop type is supported."""
        if not v or not v.strip():
            raise ValueError('crop_type cannot be empty')

        supported_crops = {
            'corn', 'soybean', 'wheat', 'cotton', 'rice',
            'barley', 'sorghum', 'millet', 'peanuts', 'sunflower'
        }

        crop_type_lower = v.lower().strip()
        if crop_type_lower not in supported_crops:
            raise ValueError(
                f'Unsupported crop type: {v}. Supported types: {sorted(supported_crops)}'
            )

        return crop_type_lower

    @validator('growth_stage')
    def validate_growth_stage(cls, v):
        """Validate that growth stage is in correct format if provided."""
        if v is None:
            return v

        if not v or not v.strip():
            raise ValueError('growth_stage cannot be empty string if provided')

        # Common growth stage patterns
        valid_patterns = {
            # Vegetative stages
            'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9',
            'V10', 'V11', 'V12', 'V13', 'V14', 'V15', 'V16', 'V17', 'V18', 'V19', 'V20',
            # Reproductive stages
            'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9',
            # Germination and emergence
            'VE', 'VC', 'V1', 'V2', 'V3', 'V4', 'V5',
            # Tillering stages (for wheat, barley)
            'T1', 'T2', 'T3', 'T4', 'T5',
            # Other common stages
            'emergence', 'seedling', 'tillering', 'booting', 'heading',
            'flowering', 'milk', 'dough', 'maturity'
        }

        stage_upper = v.upper().strip()
        if stage_upper not in valid_patterns:
            raise ValueError(
                f'Invalid growth stage: {v}. Valid stages include: {sorted(valid_patterns)[:10]}...'
            )

        return stage_upper

    @validator('additional_metadata')
    def validate_additional_metadata(cls, v):
        """Validate additional metadata structure."""
        if not isinstance(v, dict):
            raise ValueError('additional_metadata must be a dictionary')

        # Check for reasonable metadata keys and values
        reserved_keys = {'analysis_id', 'timestamp', 'user_id', 'file_id'}
        for key in v.keys():
            if key in reserved_keys:
                raise ValueError(f'Reserved metadata key: {key}')

        return v