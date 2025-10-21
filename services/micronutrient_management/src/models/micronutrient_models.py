from pydantic import BaseModel
from typing import List, Optional

class Micronutrient(BaseModel):
    name: str
    symbol: str

class MicronutrientRecommendation(BaseModel):
    micronutrient: Micronutrient
    recommendation: str
