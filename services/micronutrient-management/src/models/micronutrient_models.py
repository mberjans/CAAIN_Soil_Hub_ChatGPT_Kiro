from pydantic import BaseModel
from typing import List, Optional

class MicronutrientRecommendation(BaseModel):
    nutrient: str
    recommendation: str
    priority: int
    confidence: float
    details: Optional[str] = None
