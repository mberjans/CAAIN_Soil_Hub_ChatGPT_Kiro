from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4

# Re-export models from image_analysis_models for convenience
from ..models.image_analysis_models import (
    ImageQuality,
    DeficiencySymptom,
    Recommendation,
    DeficiencyAnalysisResponse
)

# If there were specific request schemas, they would go here.
# For now, the form data directly maps to the API endpoint parameters.
