from pydantic import BaseModel
from typing import List, Optional

class MicronutrientRecommendationSchema(BaseModel):
    nutrient: str
    recommendation: str
    priority: int
    confidence: float
    details: Optional[str] = None