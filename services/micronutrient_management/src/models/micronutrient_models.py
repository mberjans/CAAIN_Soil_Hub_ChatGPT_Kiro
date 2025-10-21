from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Micronutrient(BaseModel):
    name: str
    symbol: str

class MicronutrientRecommendation(BaseModel):
    micronutrient: Micronutrient
    recommendation: str

class MicronutrientLevel(BaseModel):
    micronutrient: Micronutrient
    level: float
    unit: str

class SoilTest(BaseModel):
    lab_name: str
    report_date: str
    micronutrient_levels: List[MicronutrientLevel]