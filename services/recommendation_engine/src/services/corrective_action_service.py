"""
Corrective Action Recommendation Service
Provides targeted treatment recommendations for nutrient deficiencies
including fertilizer applications, timing, and monitoring protocols.
"""
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from enum import Enum
from .nutrient_deficiency_detection_service import (
    NutrientDeficiency, DeficiencySeverity, NutrientType
)

class ApplicationMethod(Enum):
    """Fertilizer application methods."""
    SOIL_BROADCAST = "soil_broadcast"
    SOIL_BANDED = "soil_banded"
    FOLIAR_SPRAY = "foliar_spray"
    FERTIGATION = "fertigation"
    SEED_PLACEMENT = "seed_placement"
    SIDEDRESS = "sidedress"

class TreatmentUrgency(Enum):
    """Treatment urgency levels."""
    IMMEDIATE = "immediate"  # Within 24-48 hours
    URGENT = "urgent"  # Within 1 week
    MODERATE = "moderate"  # Within 2-4 weeks
    ROUTINE = "routine"  # Next season or maintenance

@dataclass
class FertilizerRecommendation:
    """Fertilizer application recommendation."""
    nutrient: str
    fertilizer_type: str
    application_rate_lbs_per_acre: float
    application_method: ApplicationMethod
    timing: str
    frequency: int
    cost_per_acre: float
    expected_response_days: int
    application_notes: List[str]
    safety_precautions: List[str]

@dataclass
class TreatmentPlan:
    """Complete treatment plan for nutrient deficiencies."""
    plan_id: str
    farm_id: str
    field_id: str
    crop_type: str
    deficiencies_addressed: List[str]
    fertilizer_recommendations: List[FertilizerRecommendation]
    application_schedule: Dict[str, List[str]]  # date -> actions
    monitoring_schedule: List[Dict[str, Any]]
    total_cost: float
    expected_yield_recovery: float
    treatment_urgency: TreatmentUrgency
    prevention_strategies: List[str]
    created_at: datetime

@dataclass
class EmergencyTreatment:
    """Emergency treatment protocol for severe deficiencies."""
    nutrient: str
    emergency_fertilizer: str
    application_rate: float
    application_method: ApplicationMethod
    timing: str  # "immediate", "within_24_hours", etc.
    expected_response_hours: int
    follow_up_treatment: Optional[FertilizerRecommendation]
    monitoring_frequency: str
    warning_signs: List[str]

class CorrectiveActionService:
    """Service for generating corrective action recommendations."""
    
    def __init__(self):
        self.fertilizer_database = self._initialize_fertilizer_database()
        self.application_rates = self._initialize_application_rates()
        self.timing_guidelines = self._initialize_timing_guidelines()
        self.emergency_protocols = self._initialize_emergency_protocols()

    def _initialize_fertilizer_database(self) -> Dict[str, Dict[str, Any]]:
        """Initialize fertilizer product database."""
        return {
            'nitrogen': {
                'urea': {
                    'nutrient_content': 46.0,  # % N
                    'cost_per_lb': 0.45,
                    'application_methods': [ApplicationMethod.SOIL_BROADCAST, ApplicationMethod.SIDEDRESS],
                    'response_time_days': 7,
                    'notes': ['Quick release', 'Can volatilize if not incorporated']
                },
                'ammonium_sulfate': {
                    'nutrient_content': 21.0,  # % N
                    'cost_per_lb': 0.38,
                    'application_methods': [ApplicationMethod.SOIL_BROADCAST, ApplicationMethod.FOLIAR_SPRAY],
                    'response_time_days': 5,
                    'notes': ['Also provides sulfur', 'Acidifying effect']
                },
                'liquid_nitrogen': {
                    'nutrient_content': 28.0,  # % N
                    'cost_per_lb': 0.42,
                    'application_methods': [ApplicationMethod.FOLIAR_SPRAY, ApplicationMethod.FERTIGATION],
                    'response_time_days': 3,
                    'notes': ['Fast uptake', 'Good for emergency treatment']
                }
            },
            'phosphorus': {
                'map': {  # Monoammonium phosphate
                    'nutrient_content': 52.0,  # % P2O5
                    'cost_per_lb': 0.65,
                    'application_methods': [ApplicationMethod.SOIL_BANDED, ApplicationMethod.SEED_PLACEMENT],
                    'response_time_days': 14,
                    'notes': ['High analysis', 'Good starter fertilizer']
                },
                'liquid_phosphorus': {
                    'nutrient_content': 10.0,  # % P2O5
                    'cost_per_lb': 0.55,
                    'application_methods': [ApplicationMethod.FOLIAR_SPRAY, ApplicationMethod.FERTIGATION],
                    'response_time_days': 7,
                    'notes': ['Fast foliar uptake', 'Good for emergency correction']
                }
            },
            'potassium': {
                'muriate_of_potash': {
                    'nutrient_content': 60.0,  # % K2O
                    'cost_per_lb': 0.35,
                    'application_methods': [ApplicationMethod.SOIL_BROADCAST, ApplicationMethod.SOIL_BANDED],
                    'response_time_days': 21,
                    'notes': ['High salt index', 'Chloride source']
                },
                'sulfate_of_potash': {
                    'nutrient_content': 50.0,  # % K2O
                    'cost_per_lb': 0.55,
                    'application_methods': [ApplicationMethod.SOIL_BROADCAST, ApplicationMethod.FOLIAR_SPRAY],
                    'response_time_days': 18,
                    'notes': ['Low salt index', 'Also provides sulfur']
                }
            }
        }

    def _initialize_application_rates(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Initialize application rates by nutrient, severity, and crop."""
        return {
            'nitrogen': {
                'mild': {'corn': 20, 'soybean': 15, 'wheat': 18},
                'moderate': {'corn': 40, 'soybean': 25, 'wheat': 30},
                'severe': {'corn': 60, 'soybean': 35, 'wheat': 45},
                'critical': {'corn': 80, 'soybean': 45, 'wheat': 60}
            },
            'phosphorus': {
                'mild': {'corn': 15, 'soybean': 12, 'wheat': 14},
                'moderate': {'corn': 30, 'soybean': 20, 'wheat': 25},
                'severe': {'corn': 50, 'soybean': 35, 'wheat': 40},
                'critical': {'corn': 70, 'soybean': 45, 'wheat': 55}
            }
        }

    def _initialize_timing_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Initialize application timing guidelines."""
        return {
            'nitrogen': {
                'emergency': 'immediate_foliar',
                'severe': 'within_48_hours',
                'moderate': 'within_1_week',
                'mild': 'next_application_window'
            }
        }

    def _initialize_emergency_protocols(self) -> Dict[str, EmergencyTreatment]:
        """Initialize emergency treatment protocols."""
        return {
            'nitrogen': EmergencyTreatment(
                nutrient='nitrogen',
                emergency_fertilizer='liquid_nitrogen_28%',
                application_rate=10.0,  # lbs N/acre
                application_method=ApplicationMethod.FOLIAR_SPRAY,
                timing='immediate',
                expected_response_hours=48,
                follow_up_treatment=None,
                monitoring_frequency='daily_for_1_week',
                warning_signs=['continued yellowing', 'stunted growth', 'leaf drop']
            )
        }

    async def generate_treatment_plan(
        self,
        deficiencies: List[NutrientDeficiency],
        farm_id: str,
        field_id: str,
        crop_type: str,
        field_conditions: Optional[Dict[str, Any]] = None
    ) -> TreatmentPlan:
        """Generate comprehensive treatment plan for nutrient deficiencies."""
        
        plan_id = f"treatment_{farm_id}_{field_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Generate basic treatment plan
        fertilizer_recommendations = []
        for deficiency in deficiencies:
            recommendation = FertilizerRecommendation(
                nutrient=deficiency.nutrient,
                fertilizer_type=f"{deficiency.nutrient}_fertilizer",
                application_rate_lbs_per_acre=50.0,
                application_method=ApplicationMethod.SOIL_BROADCAST,
                timing="within_1_week",
                frequency=1,
                cost_per_acre=25.0,
                expected_response_days=14,
                application_notes=["Apply according to label instructions"],
                safety_precautions=["Wear appropriate PPE"]
            )
            fertilizer_recommendations.append(recommendation)
        
        return TreatmentPlan(
            plan_id=plan_id,
            farm_id=farm_id,
            field_id=field_id,
            crop_type=crop_type,
            deficiencies_addressed=[d.nutrient for d in deficiencies],
            fertilizer_recommendations=fertilizer_recommendations,
            application_schedule={"within_1_week": ["Apply fertilizers"]},
            monitoring_schedule=[{"timing": "weekly", "activities": ["Monitor progress"]}],
            total_cost=sum(r.cost_per_acre for r in fertilizer_recommendations),
            expected_yield_recovery=50.0,
            treatment_urgency=TreatmentUrgency.MODERATE,
            prevention_strategies=["Regular soil testing", "Balanced fertilization"],
            created_at=datetime.now()
        )