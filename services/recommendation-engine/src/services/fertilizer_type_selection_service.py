"""
Soil pH Management Service
Provides comprehensive soil pH analysis, amendment recommendations, and management guidance.
Helps farmers optimize soil pH for better nutrient availability and crop performance.
"""
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import math

class SoilTexture(Enum):
    """Soil texture classifications."""
    SAND = "sand"
    LOAMY_SAND = "loamy_sand"
    SANDY_LOAM = "sandy_loam"
    LOAM = "loam"
    SILT_LOAM = "silt_loam"
    SILT = "silt"
    CLAY_LOAM = "clay_loam"
    SILTY_CLAY_LOAM = "silty_clay_loam"
    SANDY_CLAY_LOAM = "sandy_clay_loam"
    CLAY = "clay"
    SILTY_CLAY = "silty_clay"
    SANDY_CLAY = "sandy_clay"

class AmendmentType(Enum):
    """Types of pH amendments."""
    AGRICULTURAL_LIME = "agricultural_lime"
    DOLOMITIC_LIME = "dolomitic_lime"
    HYDRATED_LIME = "hydrated_lime"
    ELEMENTAL_SULFUR = "elemental_sulfur"
    ALUMINUM_SULFATE = "aluminum_sulfate"
    IRON_SULFATE = "iron_sulfate"

class ApplicationTiming(Enum):
    """Optimal timing for pH amendments."""
    FALL_PREFERRED = "fall_preferred"
    SPRING_ACCEPTABLE = "spring_acceptable"
    SUMMER_AVOID = "summer_avoid"
    WINTER_AVOID = "winter_avoid"
    ANYTIME = "anytime"

@dataclass
class PHReading:
    """Individual pH reading with metadata."""
    ph_value: float
    test_date: date
    field_location: str
    lab_name: Optional[str] = None
    test_method: Optional[str] = None
    depth_inches: float = 6.0
    confidence_level: float = 0.9

@dataclass
class CropPHPreference:
    """pH preferences for specific crops."""
    crop_name: str
    optimal_ph_min: float
    optimal_ph_max: float
    acceptable_ph_min: float
    acceptable_ph_max: float
    critical_ph_min: float
    critical_ph_max: float
    tolerance_level: str  # high, medium, low
    yield_impact_curve: Dict[float, float]  # pH -> yield impact %

@dataclass
class PHAmendmentRecommendation:
    """pH amendment recommendation with details."""
    amendment_type: AmendmentType
    application_rate_tons_per_acre: float
    application_rate_lbs_per_acre: float
    cost_per_acre: float
    expected_ph_change: float
    time_to_effect_months: int
    application_timing: ApplicationTiming
    application_notes: List[str]
    safety_precautions: List[str]

@dataclass
class PHManagementPlan:
    """Comprehensive pH management plan."""
    plan_id: str
    farm_id: str
    field_id: str
    current_ph: float
    target_ph: float
    crop_type: str
    soil_texture: SoilTexture
    organic_matter_percent: float
    recommendations: List[PHAmendmentRecommendation]
    timeline_months: List[Dict[str, Any]]
    nutrient_availability_impact: Dict[str, float]
    economic_analysis: Dict[str, float]
    monitoring_schedule: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class PHTimeline:
    """Timeline for pH changes and monitoring."""
    timeline_id: str
    initial_ph: float
    target_ph: float
    amendment_applied: PHAmendmentRecommendation
    predicted_changes: List[Dict[str, Any]]  # month -> predicted pH
    monitoring_points: List[Dict[str, Any]]
    factors_affecting_change: List[str]
    confidence_intervals: Dict[str, Tuple[float, float]]

class SoilPHManagementService:
    """Service for comprehensive soil pH management."""
    
    def __init__(self):
        self.crop_ph_preferences = self._initialize_crop_ph_preferences()
        self.buffer_capacity_factors = self._initialize_buffer_capacity_factors()
        self.amendment_properties = self._initialize_amendment_properties()
        self.timing_guidelines = self._initialize_timing_guidelines()
        self.nutrient_availability_curves = self._initialize_nutrient_availability_curves()
    
    def _initialize_crop_ph_preferences(self) -> Dict[str, CropPHPreference]:
        """Initialize crop pH preference database."""
        return {
            'corn': CropPHPreference(
                crop_name='corn',
                optimal_ph_min=6.0,
                optimal_ph_max=6.8,
                acceptable_ph_min=5.8,
                acceptable_ph_max=7.2,
                critical_ph_min=5.5,
                critical_ph_max=7.5,
                tolerance_level='medium',
                yield_impact_curve={
                    5.0: -25.0, 5.5: -15.0, 6.0: -5.0, 6.2: 0.0, 6.5: 0.0,
                    6.8: 0.0, 7.0: -3.0, 7.5: -10.0, 8.0: -20.0, 8.5: -35.0
                }
            ),
            'soybean': CropPHPreference(
                crop_name='soybean',
                optimal_ph_min=6.0,
                optimal_ph_max=7.0,
                acceptable_ph_min=5.8,
                acceptable_ph_max=7.5,
                critical_ph_min=5.5,
                critical_ph_max=8.0,
                tolerance_level='medium',
                yield_impact_curve={
                    5.0: -30.0, 5.5: -18.0, 6.0: -8.0, 6.2: -2.0, 6.5: 0.0,
                    7.0: 0.0, 7.5: -5.0, 8.0: -15.0, 8.5: -30.0
                }
            ),
            'wheat': CropPHPreference(
                crop_name='wheat',
                optimal_ph_min=6.0,
                optimal_ph_max=7.0,
                acceptable_ph_min=5.5,
                acceptable_ph_max=7.5,
                critical_ph_min=5.0,
                critical_ph_max=8.0,
                tolerance_level='high',
                yield_impact_curve={
                    5.0: -15.0, 5.5: -8.0, 6.0: -3.0, 6.5: 0.0, 7.0: 0.0,
                    7.5: -2.0, 8.0: -8.0, 8.5: -20.0
                }
            ),
            'alfalfa': CropPHPreference(
                crop_name='alfalfa',
                optimal_ph_min=6.8,
                optimal_ph_max=7.5,
                acceptable_ph_min=6.5,
                acceptable_ph_max=8.0,
                critical_ph_min=6.0,
                critical_ph_max=8.5,
                tolerance_level='low',
                yield_impact_curve={
                    5.5: -40.0, 6.0: -25.0, 6.5: -10.0, 6.8: -2.0, 7.0: 0.0,
                    7.5: 0.0, 8.0: -5.0, 8.5: -15.0
                }
            ),
            'blueberry': CropPHPreference(
                crop_name='blueberry',
                optimal_ph_min=4.5,
                optimal_ph_max=5.5,
                acceptable_ph_min=4.0,
                acceptable_ph_max=6.0,
                critical_ph_min=3.8,
                critical_ph_max=6.5,
                tolerance_level='low',
                yield_impact_curve={
                    3.5: -30.0, 4.0: -10.0, 4.5: 0.0, 5.0: 0.0, 5.5: 0.0,
                    6.0: -15.0, 6.5: -35.0, 7.0: -60.0
                }
            ),
            'potato': CropPHPreference(
                crop_name='potato',
                optimal_ph_min=5.0,
                optimal_ph_max=6.0,
                acceptable_ph_min=4.8,
                acceptable_ph_max=6.5,
                critical_ph_min=4.5,
                critical_ph_max=7.0,
                tolerance_level='medium',
                yield_impact_curve={
                    4.0: -20.0, 4.5: -8.0, 5.0: 0.0, 5.5: 0.0, 6.0: 0.0,
                    6.5: -5.0, 7.0: -15.0, 7.5: -25.0
                }
            )
        }
    
    def _initialize_buffer_capacity_factors(self) -> Dict[SoilTexture, Dict[str, float]]:
        """Initialize soil buffer capacity factors for pH calculations."""
        return {
            SoilTexture.SAND: {
                'lime_efficiency': 1.2,  # Higher efficiency due to low buffering
                'sulfur_efficiency': 1.3,
                'base_buffer_capacity': 2.0,  # meq/100g per pH unit
                'organic_matter_factor': 0.8
            },
            SoilTexture.LOAMY_SAND: {
                'lime_efficiency': 1.1,
                'sulfur_efficiency': 1.2,
                'base_buffer_capacity': 3.0,
                'organic_matter_factor': 0.9
            },
            SoilTexture.SANDY_LOAM: {
                'lime_efficiency': 1.0,
                'sulfur_efficiency': 1.1,
                'base_buffer_capacity': 4.5,
                'organic_matter_factor': 1.0
            },
            SoilTexture.LOAM: {
                'lime_efficiency': 0.9,
                'sulfur_efficiency': 1.0,
                'base_buffer_capacity': 6.0,
                'organic_matter_factor': 1.1
            },
            SoilTexture.SILT_LOAM: {
                'lime_efficiency': 0.8,
                'sulfur_efficiency': 0.9,
                'base_buffer_capacity': 7.5,
                'organic_matter_factor': 1.2
            },
            SoilTexture.CLAY_LOAM: {
                'lime_efficiency': 0.7,
                'sulfur_efficiency': 0.8,
                'base_buffer_capacity': 9.0,
                'organic_matter_factor': 1.3
            },
            SoilTexture.CLAY: {
                'lime_efficiency': 0.6,
                'sulfur_efficiency': 0.7,
                'base_buffer_capacity': 12.0,
                'organic_matter_factor': 1.4
            }
        }
    
    def _initialize_amendment_properties(self) -> Dict[AmendmentType, Dict[str, Any]]:
        """Initialize properties of different pH amendments."""
        return {
            AmendmentType.AGRICULTURAL_LIME: {
                'calcium_carbonate_equivalent': 90.0,  # %
                'neutralizing_value': 90.0,
                'cost_per_ton': 45.0,
                'fineness_factor': 0.85,
                'time_to_effect_months': 6,
                'ph_change_per_ton': 0.3,  # Approximate for loam soil
                'application_notes': [
                    'Best applied in fall for spring crops',
                    'Incorporate into soil within 30 days',
                    'Works slowly but provides long-lasting effect'
                ],
                'safety_precautions': [
                    'Wear dust mask during application',
                    'Avoid application during windy conditions',
                    'Store in dry location'
                ]
            },
            AmendmentType.DOLOMITIC_LIME: {
                'calcium_carbonate_equivalent': 95.0,
                'neutralizing_value': 95.0,
                'cost_per_ton': 50.0,
                'fineness_factor': 0.85,
                'time_to_effect_months': 6,
                'ph_change_per_ton': 0.32,
                'magnesium_content': 12.0,  # %
                'application_notes': [
                    'Provides both calcium and magnesium',
                    'Preferred for soils low in magnesium',
                    'Apply 3-6 months before planting'
                ],
                'safety_precautions': [
                    'Use appropriate PPE during handling',
                    'Avoid inhalation of dust',
                    'Keep away from water sources during storage'
                ]
            },
            AmendmentType.HYDRATED_LIME: {
                'calcium_carbonate_equivalent': 135.0,
                'neutralizing_value': 135.0,
                'cost_per_ton': 85.0,
                'fineness_factor': 1.0,
                'time_to_effect_months': 1,
                'ph_change_per_ton': 0.45,
                'application_notes': [
                    'Fast-acting but more expensive',
                    'Use for quick pH adjustment',
                    'Apply in smaller quantities'
                ],
                'safety_precautions': [
                    'CAUSTIC - wear protective equipment',
                    'Avoid skin and eye contact',
                    'Do not inhale dust'
                ]
            },
            AmendmentType.ELEMENTAL_SULFUR: {
                'sulfur_content': 90.0,  # %
                'cost_per_ton': 320.0,
                'fineness_factor': 0.9,
                'time_to_effect_months': 4,
                'ph_change_per_ton': -0.8,  # Negative for pH reduction
                'application_notes': [
                    'Requires microbial oxidation to be effective',
                    'Works best in warm, moist conditions',
                    'Apply 3-4 months before planting'
                ],
                'safety_precautions': [
                    'Avoid dust inhalation',
                    'Store in cool, dry place',
                    'Keep away from heat sources'
                ]
            },
            AmendmentType.ALUMINUM_SULFATE: {
                'aluminum_content': 17.0,  # %
                'sulfur_content': 14.0,  # %
                'cost_per_ton': 280.0,
                'time_to_effect_months': 1,
                'ph_change_per_ton': -1.2,
                'application_notes': [
                    'Fast-acting acidifier',
                    'Can be toxic to plants in high concentrations',
                    'Use with caution around sensitive crops'
                ],
                'safety_precautions': [
                    'Wear gloves and eye protection',
                    'Avoid over-application',
                    'Test soil regularly after application'
                ]
            }
        }
    
    def _initialize_timing_guidelines(self) -> Dict[str, Dict[str, Any]]:
        """Initialize timing guidelines for pH amendments."""
        return {
            'lime_application': {
                'fall': {
                    'preference': 'optimal',
                    'reasons': ['Time for reaction before spring', 'Freeze-thaw helps incorporation'],
                    'months': [9, 10, 11]
                },
                'spring': {
                    'preference': 'acceptable',
                    'reasons': ['Can work if applied early', 'May not be fully effective first season'],
                    'months': [3, 4]
                },
                'summer': {
                    'preference': 'avoid',
                    'reasons': ['Dry conditions limit effectiveness', 'Dust issues'],
                    'months': [6, 7, 8]
                }
            },
            'sulfur_application': {
                'spring': {
                    'preference': 'optimal',
                    'reasons': ['Warm weather promotes microbial activity', 'Time for effect before crop needs'],
                    'months': [4, 5]
                },
                'fall': {
                    'preference': 'acceptable',
                    'reasons': ['Some reaction over winter', 'Ready for spring crops'],
                    'months': [9, 10]
                },
                'summer': {
                    'preference': 'good',
                    'reasons': ['High microbial activity', 'Fast reaction'],
                    'months': [6, 7]
                }
            }
        }
    
    def _initialize_nutrient_availability_curves(self) -> Dict[str, Dict[float, float]]:
        """Initialize nutrient availability curves by pH."""
        return {
            'nitrogen': {
                4.0: 0.6, 4.5: 0.7, 5.0: 0.8, 5.5: 0.85, 6.0: 0.9,
                6.5: 1.0, 7.0: 1.0, 7.5: 0.95, 8.0: 0.9, 8.5: 0.8
            },
            'phosphorus': {
                4.0: 0.3, 4.5: 0.4, 5.0: 0.5, 5.5: 0.7, 6.0: 0.85,
                6.5: 1.0, 7.0: 0.9, 7.5: 0.7, 8.0: 0.5, 8.5: 0.3
            },
            'potassium': {
                4.0: 0.7, 4.5: 0.8, 5.0: 0.85, 5.5: 0.9, 6.0: 0.95,
                6.5: 1.0, 7.0: 1.0, 7.5: 0.98, 8.0: 0.95, 8.5: 0.9
            },
            'calcium': {
                4.0: 0.4, 4.5: 0.5, 5.0: 0.6, 5.5: 0.75, 6.0: 0.9,
                6.5: 1.0, 7.0: 1.0, 7.5: 1.0, 8.0: 0.95, 8.5: 0.9
            },
            'magnesium': {
                4.0: 0.4, 4.5: 0.5, 5.0: 0.6, 5.5: 0.75, 6.0: 0.9,
                6.5: 1.0, 7.0: 1.0, 7.5: 1.0, 8.0: 0.95, 8.5: 0.9
            },
            'iron': {
                4.0: 1.0, 4.5: 1.0, 5.0: 0.95, 5.5: 0.9, 6.0: 0.8,
                6.5: 0.6, 7.0: 0.4, 7.5: 0.2, 8.0: 0.1, 8.5: 0.05
            },
            'manganese': {
                4.0: 1.0, 4.5: 1.0, 5.0: 0.9, 5.5: 0.8, 6.0: 0.7,
                6.5: 0.5, 7.0: 0.3, 7.5: 0.15, 8.0: 0.08, 8.5: 0.04
            },
            'zinc': {
                4.0: 0.9, 4.5: 0.95, 5.0: 1.0, 5.5: 0.95, 6.0: 0.9,
                6.5: 0.8, 7.0: 0.6, 7.5: 0.4, 8.0: 0.2, 8.5: 0.1
            },
            'copper': {
                4.0: 0.8, 4.5: 0.9, 5.0: 1.0, 5.5: 0.95, 6.0: 0.9,
                6.5: 0.85, 7.0: 0.7, 7.5: 0.5, 8.0: 0.3, 8.5: 0.15
            },
            'boron': {
                4.0: 0.6, 4.5: 0.7, 5.0: 0.8, 5.5: 0.9, 6.0: 1.0,
                6.5: 1.0, 7.0: 0.95, 7.5: 0.9, 8.0: 0.8, 8.5: 0.7
            }
        }
    
    async def analyze_ph_status(
        self,
        farm_id: str,
        field_id: str,
        ph_readings: List[PHReading],
        crop_type: str,
        soil_texture: SoilTexture,
        organic_matter_percent: float
    ) -> Dict[str, Any]:
        """Analyze current pH status and crop suitability."""
        
        # Calculate average pH from readings
        if not ph_readings:
            raise ValueError("At least one pH reading is required")
        
        current_ph = np.mean([reading.ph_value for reading in ph_readings])
        ph_std = np.std([reading.ph_value for reading in ph_readings]) if len(ph_readings) > 1 else 0.0
        
        # Get crop pH preferences
        crop_preferences = self.crop_ph_preferences.get(crop_type.lower())
        if not crop_preferences:
            crop_preferences = self.crop_ph_preferences['corn']  # Default to corn
        
        # Determine pH status
        ph_status = self._determine_ph_status(current_ph, crop_preferences)
        
        # Calculate yield impact
        yield_impact = self._calculate_yield_impact(current_ph, crop_preferences)
        
        # Assess nutrient availability
        nutrient_availability = self._assess_nutrient_availability(current_ph)
        
        # Determine if adjustment is needed
        adjustment_needed = not (crop_preferences.optimal_ph_min <= current_ph <= crop_preferences.optimal_ph_max)
        
        return {
            'farm_id': farm_id,
            'field_id': field_id,
            'current_ph': current_ph,
            'ph_variability': ph_std,
            'crop_type': crop_type,
            'ph_status': ph_status,
            'yield_impact_percent': yield_impact,
            'adjustment_needed': adjustment_needed,
            'target_ph_range': {
                'min': crop_preferences.optimal_ph_min,
                'max': crop_preferences.optimal_ph_max
            },
            'nutrient_availability': nutrient_availability,
            'readings_count': len(ph_readings),
            'confidence_level': min([r.confidence_level for r in ph_readings])
        }
    
    def _determine_ph_status(self, current_ph: float, crop_preferences: CropPHPreference) -> str:
        """Determine pH status relative to crop needs."""
        if current_ph < crop_preferences.critical_ph_min:
            return "critically_low"
        elif current_ph < crop_preferences.acceptable_ph_min:
            return "low"
        elif current_ph < crop_preferences.optimal_ph_min:
            return "slightly_low"
        elif current_ph <= crop_preferences.optimal_ph_max:
            return "optimal"
        elif current_ph <= crop_preferences.acceptable_ph_max:
            return "slightly_high"
        elif current_ph <= crop_preferences.critical_ph_max:
            return "high"
        else:
            return "critically_high"
    
    def _calculate_yield_impact(self, current_ph: float, crop_preferences: CropPHPreference) -> float:
        """Calculate yield impact based on pH deviation from optimal."""
        yield_curve = crop_preferences.yield_impact_curve
        
        # Find closest pH values in the curve
        ph_values = sorted(yield_curve.keys())
        
        if current_ph <= ph_values[0]:
            return yield_curve[ph_values[0]]
        elif current_ph >= ph_values[-1]:
            return yield_curve[ph_values[-1]]
        
        # Interpolate between closest values
        for i in range(len(ph_values) - 1):
            if ph_values[i] <= current_ph <= ph_values[i + 1]:
                # Linear interpolation
                x1, y1 = ph_values[i], yield_curve[ph_values[i]]
                x2, y2 = ph_values[i + 1], yield_curve[ph_values[i + 1]]
                
                return y1 + (y2 - y1) * (current_ph - x1) / (x2 - x1)
        
        return 0.0  # Fallback
    
    def _assess_nutrient_availability(self, current_ph: float) -> Dict[str, float]:
        """Assess nutrient availability at current pH."""
        availability = {}
        
        for nutrient, curve in self.nutrient_availability_curves.items():
            ph_values = sorted(curve.keys())
            
            if current_ph <= ph_values[0]:
                availability[nutrient] = curve[ph_values[0]]
            elif current_ph >= ph_values[-1]:
                availability[nutrient] = curve[ph_values[-1]]
            else:
                # Interpolate
                for i in range(len(ph_values) - 1):
                    if ph_values[i] <= current_ph <= ph_values[i + 1]:
                        x1, y1 = ph_values[i], curve[ph_values[i]]
                        x2, y2 = ph_values[i + 1], curve[ph_values[i + 1]]
                        
                        availability[nutrient] = y1 + (y2 - y1) * (current_ph - x1) / (x2 - x1)
                        break
        
        return availability  
  async def calculate_ph_amendments(
        self,
        current_ph: float,
        target_ph: float,
        soil_texture: SoilTexture,
        organic_matter_percent: float,
        field_size_acres: float = 1.0
    ) -> List[PHAmendmentRecommendation]:
        """Calculate pH amendment recommendations."""
        
        ph_change_needed = target_ph - current_ph
        
        if abs(ph_change_needed) < 0.1:
            return []  # No significant change needed
        
        recommendations = []
        
        if ph_change_needed > 0:
            # Need to raise pH - use lime
            recommendations.extend(self._calculate_lime_recommendations(
                ph_change_needed, soil_texture, organic_matter_percent, field_size_acres
            ))
        else:
            # Need to lower pH - use sulfur or acidifiers
            recommendations.extend(self._calculate_acidifier_recommendations(
                abs(ph_change_needed), soil_texture, organic_matter_percent, field_size_acres
            ))
        
        return recommendations
    
    def _calculate_lime_recommendations(
        self,
        ph_increase_needed: float,
        soil_texture: SoilTexture,
        organic_matter_percent: float,
        field_size_acres: float
    ) -> List[PHAmendmentRecommendation]:
        """Calculate lime application recommendations."""
        
        recommendations = []
        buffer_factors = self.buffer_capacity_factors[soil_texture]
        
        # Adjust buffer capacity for organic matter
        om_adjustment = 1.0 + (organic_matter_percent - 3.0) * buffer_factors['organic_matter_factor'] * 0.1
        effective_buffer_capacity = buffer_factors['base_buffer_capacity'] * om_adjustment
        
        # Calculate lime requirement using buffer capacity method
        # Base calculation: tons lime/acre = (target pH - current pH) * buffer capacity / lime efficiency
        
        # Agricultural lime recommendation
        ag_lime_props = self.amendment_properties[AmendmentType.AGRICULTURAL_LIME]
        lime_efficiency = buffer_factors['lime_efficiency'] * (ag_lime_props['neutralizing_value'] / 100.0)
        
        tons_per_acre = (ph_increase_needed * effective_buffer_capacity) / lime_efficiency
        tons_per_acre = max(0.5, min(tons_per_acre, 4.0))  # Safety limits
        
        lbs_per_acre = tons_per_acre * 2000
        cost_per_acre = tons_per_acre * ag_lime_props['cost_per_ton']
        
        # Determine application timing
        current_month = datetime.now().month
        if current_month in [9, 10, 11]:
            timing = ApplicationTiming.FALL_PREFERRED
        elif current_month in [3, 4, 5]:
            timing = ApplicationTiming.SPRING_ACCEPTABLE
        else:
            timing = ApplicationTiming.FALL_PREFERRED
        
        ag_lime_rec = PHAmendmentRecommendation(
            amendment_type=AmendmentType.AGRICULTURAL_LIME,
            application_rate_tons_per_acre=tons_per_acre,
            application_rate_lbs_per_acre=lbs_per_acre,
            cost_per_acre=cost_per_acre,
            expected_ph_change=ph_increase_needed,
            time_to_effect_months=ag_lime_props['time_to_effect_months'],
            application_timing=timing,
            application_notes=ag_lime_props['application_notes'].copy(),
            safety_precautions=ag_lime_props['safety_precautions'].copy()
        )
        
        recommendations.append(ag_lime_rec)
        
        # Dolomitic lime alternative (if magnesium might be beneficial)
        dol_lime_props = self.amendment_properties[AmendmentType.DOLOMITIC_LIME]
        dol_lime_efficiency = buffer_factors['lime_efficiency'] * (dol_lime_props['neutralizing_value'] / 100.0)
        dol_tons_per_acre = (ph_increase_needed * effective_buffer_capacity) / dol_lime_efficiency
        dol_tons_per_acre = max(0.5, min(dol_tons_per_acre, 4.0))
        
        dol_lime_rec = PHAmendmentRecommendation(
            amendment_type=AmendmentType.DOLOMITIC_LIME,
            application_rate_tons_per_acre=dol_tons_per_acre,
            application_rate_lbs_per_acre=dol_tons_per_acre * 2000,
            cost_per_acre=dol_tons_per_acre * dol_lime_props['cost_per_ton'],
            expected_ph_change=ph_increase_needed,
            time_to_effect_months=dol_lime_props['time_to_effect_months'],
            application_timing=timing,
            application_notes=dol_lime_props['application_notes'].copy(),
            safety_precautions=dol_lime_props['safety_precautions'].copy()
        )
        
        recommendations.append(dol_lime_rec)
        
        return recommendations
    
    def _calculate_acidifier_recommendations(
        self,
        ph_decrease_needed: float,
        soil_texture: SoilTexture,
        organic_matter_percent: float,
        field_size_acres: float
    ) -> List[PHAmendmentRecommendation]:
        """Calculate acidifier application recommendations."""
        
        recommendations = []
        buffer_factors = self.buffer_capacity_factors[soil_texture]
        
        # Adjust buffer capacity for organic matter
        om_adjustment = 1.0 + (organic_matter_percent - 3.0) * buffer_factors['organic_matter_factor'] * 0.1
        effective_buffer_capacity = buffer_factors['base_buffer_capacity'] * om_adjustment
        
        # Elemental sulfur recommendation
        sulfur_props = self.amendment_properties[AmendmentType.ELEMENTAL_SULFUR]
        sulfur_efficiency = buffer_factors['sulfur_efficiency']
        
        # Calculate sulfur requirement
        lbs_per_acre = (ph_decrease_needed * effective_buffer_capacity * 320) / sulfur_efficiency
        lbs_per_acre = max(50, min(lbs_per_acre, 500))  # Safety limits
        
        tons_per_acre = lbs_per_acre / 2000
        cost_per_acre = tons_per_acre * sulfur_props['cost_per_ton']
        
        # Determine timing for sulfur
        current_month = datetime.now().month
        if current_month in [4, 5, 6]:
            timing = ApplicationTiming.SPRING_ACCEPTABLE
        elif current_month in [7, 8]:
            timing = ApplicationTiming.SUMMER_AVOID  # Too hot
        else:
            timing = ApplicationTiming.FALL_PREFERRED
        
        sulfur_rec = PHAmendmentRecommendation(
            amendment_type=AmendmentType.ELEMENTAL_SULFUR,
            application_rate_tons_per_acre=tons_per_acre,
            application_rate_lbs_per_acre=lbs_per_acre,
            cost_per_acre=cost_per_acre,
            expected_ph_change=-ph_decrease_needed,
            time_to_effect_months=sulfur_props['time_to_effect_months'],
            application_timing=timing,
            application_notes=sulfur_props['application_notes'].copy(),
            safety_precautions=sulfur_props['safety_precautions'].copy()
        )
        
        recommendations.append(sulfur_rec)
        
        # Aluminum sulfate alternative for faster action
        if ph_decrease_needed <= 1.0:  # Only for moderate pH reductions
            al_sulfate_props = self.amendment_properties[AmendmentType.ALUMINUM_SULFATE]
            
            al_lbs_per_acre = (ph_decrease_needed * effective_buffer_capacity * 200)
            al_lbs_per_acre = max(25, min(al_lbs_per_acre, 200))
            
            al_sulfate_rec = PHAmendmentRecommendation(
                amendment_type=AmendmentType.ALUMINUM_SULFATE,
                application_rate_tons_per_acre=al_lbs_per_acre / 2000,
                application_rate_lbs_per_acre=al_lbs_per_acre,
                cost_per_acre=(al_lbs_per_acre / 2000) * al_sulfate_props['cost_per_ton'],
                expected_ph_change=-ph_decrease_needed,
                time_to_effect_months=al_sulfate_props['time_to_effect_months'],
                application_timing=ApplicationTiming.ANYTIME,
                application_notes=al_sulfate_props['application_notes'].copy(),
                safety_precautions=al_sulfate_props['safety_precautions'].copy()
            )
            
            recommendations.append(al_sulfate_rec)
        
        return recommendations
    
    async def create_ph_management_plan(
        self,
        farm_id: str,
        field_id: str,
        ph_readings: List[PHReading],
        crop_type: str,
        soil_texture: SoilTexture,
        organic_matter_percent: float,
        field_size_acres: float = 1.0
    ) -> PHManagementPlan:
        """Create comprehensive pH management plan."""
        
        # Analyze current status
        ph_analysis = await self.analyze_ph_status(
            farm_id, field_id, ph_readings, crop_type, soil_texture, organic_matter_percent
        )
        
        current_ph = ph_analysis['current_ph']
        crop_preferences = self.crop_ph_preferences.get(crop_type.lower(), self.crop_ph_preferences['corn'])
        
        # Determine target pH
        target_ph = (crop_preferences.optimal_ph_min + crop_preferences.optimal_ph_max) / 2
        
        # Calculate amendments if needed
        recommendations = []
        if ph_analysis['adjustment_needed']:
            recommendations = await self.calculate_ph_amendments(
                current_ph, target_ph, soil_texture, organic_matter_percent, field_size_acres
            )
        
        # Create timeline
        timeline_months = self._create_ph_timeline(current_ph, target_ph, recommendations)
        
        # Calculate economic analysis
        economic_analysis = self._calculate_economic_analysis(
            recommendations, ph_analysis['yield_impact_percent'], crop_type, field_size_acres
        )
        
        # Create monitoring schedule
        monitoring_schedule = self._create_monitoring_schedule(recommendations)
        
        plan_id = f"ph_plan_{farm_id}_{field_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return PHManagementPlan(
            plan_id=plan_id,
            farm_id=farm_id,
            field_id=field_id,
            current_ph=current_ph,
            target_ph=target_ph,
            crop_type=crop_type,
            soil_texture=soil_texture,
            organic_matter_percent=organic_matter_percent,
            recommendations=recommendations,
            timeline_months=timeline_months,
            nutrient_availability_impact=ph_analysis['nutrient_availability'],
            economic_analysis=economic_analysis,
            monitoring_schedule=monitoring_schedule,
            created_at=datetime.now()
        )
    
    def _create_ph_timeline(
        self,
        current_ph: float,
        target_ph: float,
        recommendations: List[PHAmendmentRecommendation]
    ) -> List[Dict[str, Any]]:
        """Create timeline for pH changes."""
        
        timeline = []
        
        if not recommendations:
            return timeline
        
        # Use the first (primary) recommendation for timeline
        primary_rec = recommendations[0]
        ph_change_needed = target_ph - current_ph
        
        # Create monthly progression
        months_to_effect = primary_rec.time_to_effect_months
        
        for month in range(0, months_to_effect + 6):  # Extend 6 months beyond full effect
            if month == 0:
                predicted_ph = current_ph
                activity = f"Apply {primary_rec.amendment_type.value}"
            elif month <= months_to_effect:
                # Gradual change following S-curve
                progress = self._ph_change_curve(month / months_to_effect)
                predicted_ph = current_ph + (ph_change_needed * progress)
                activity = "pH adjustment in progress"
            else:
                predicted_ph = target_ph
                activity = "Monitor and maintain pH"
            
            timeline.append({
                'month': month,
                'predicted_ph': round(predicted_ph, 2),
                'activity': activity,
                'monitoring_recommended': month % 3 == 0  # Every 3 months
            })
        
        return timeline
    
    def _ph_change_curve(self, progress: float) -> float:
        """Model pH change over time using S-curve."""
        # S-curve: slow start, rapid middle, slow finish
        return 1 / (1 + math.exp(-6 * (progress - 0.5)))
    
    def _calculate_economic_analysis(
        self,
        recommendations: List[PHAmendmentRecommendation],
        yield_impact_percent: float,
        crop_type: str,
        field_size_acres: float
    ) -> Dict[str, float]:
        """Calculate economic analysis for pH management."""
        
        if not recommendations:
            return {'total_cost': 0.0, 'expected_benefit': 0.0, 'roi_percent': 0.0}
        
        # Calculate total treatment cost
        total_cost = min([rec.cost_per_acre for rec in recommendations]) * field_size_acres
        
        # Estimate yield benefit
        crop_values = {
            'corn': {'yield_bu_per_acre': 180, 'price_per_bu': 4.25},
            'soybean': {'yield_bu_per_acre': 50, 'price_per_bu': 12.50},
            'wheat': {'yield_bu_per_acre': 60, 'price_per_bu': 6.80},
            'alfalfa': {'yield_tons_per_acre': 4.5, 'price_per_ton': 180}
        }
        
        crop_data = crop_values.get(crop_type.lower(), crop_values['corn'])
        
        if 'yield_bu_per_acre' in crop_data:
            base_value = crop_data['yield_bu_per_acre'] * crop_data['price_per_bu']
        else:
            base_value = crop_data['yield_tons_per_acre'] * crop_data['price_per_ton']
        
        # Calculate benefit from eliminating yield loss
        yield_benefit = abs(yield_impact_percent) / 100.0 * base_value * field_size_acres
        
        # Calculate ROI
        roi_percent = ((yield_benefit - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        return {
            'total_cost': total_cost,
            'expected_benefit': yield_benefit,
            'roi_percent': roi_percent,
            'payback_years': total_cost / yield_benefit if yield_benefit > 0 else float('inf')
        }
    
    def _create_monitoring_schedule(
        self,
        recommendations: List[PHAmendmentRecommendation]
    ) -> List[Dict[str, Any]]:
        """Create monitoring schedule for pH management."""
        
        schedule = []
        
        if not recommendations:
            return schedule
        
        primary_rec = recommendations[0]
        
        # Pre-application monitoring
        schedule.append({
            'timing': 'before_application',
            'activity': 'Baseline pH testing',
            'frequency': 'once',
            'notes': 'Confirm current pH before treatment'
        })
        
        # Post-application monitoring
        months_to_effect = primary_rec.time_to_effect_months
        
        schedule.append({
            'timing': f'{months_to_effect // 2}_months_post_application',
            'activity': 'Interim pH testing',
            'frequency': 'once',
            'notes': 'Check pH change progress'
        })
        
        schedule.append({
            'timing': f'{months_to_effect}_months_post_application',
            'activity': 'Full effect pH testing',
            'frequency': 'once',
            'notes': 'Verify target pH achieved'
        })
        
        schedule.append({
            'timing': 'annual',
            'activity': 'Routine pH monitoring',
            'frequency': 'yearly',
            'notes': 'Maintain optimal pH range'
        })
        
        return schedule
    
    def validate_ph_reading(self, ph_value: float) -> Dict[str, Any]:
        """Validate pH reading input."""
        
        validation_result = {
            'is_valid': True,
            'warnings': [],
            'errors': []
        }
        
        # Basic range validation
        if ph_value < 3.0 or ph_value > 10.0:
            validation_result['is_valid'] = False
            validation_result['errors'].append(
                f"pH value {ph_value} is outside valid range (3.0-10.0). Please verify measurement."
            )
        
        # Agricultural reasonableness checks
        if ph_value < 4.0:
            validation_result['warnings'].append(
                f"Extremely acidic pH ({ph_value}). Verify with laboratory test if field measurement."
            )
        elif ph_value > 8.5:
            validation_result['warnings'].append(
                f"Very alkaline pH ({ph_value}). May indicate measurement error or unusual soil conditions."
            )
        
        # Precision validation
        if len(str(ph_value).split('.')[-1]) > 2:
            validation_result['warnings'].append(
                "pH measurements are typically reported to 1-2 decimal places."
            )
        
        return validation_result
    
    async def get_nutrient_availability_explanation(self, ph_value: float) -> Dict[str, Any]:
        """Get detailed explanation of nutrient availability at given pH."""
        
        availability = self._assess_nutrient_availability(ph_value)
        
        explanations = {
            'nitrogen': self._explain_nitrogen_availability(ph_value, availability['nitrogen']),
            'phosphorus': self._explain_phosphorus_availability(ph_value, availability['phosphorus']),
            'potassium': self._explain_potassium_availability(ph_value, availability['potassium']),
            'iron': self._explain_iron_availability(ph_value, availability['iron']),
            'zinc': self._explain_zinc_availability(ph_value, availability['zinc']),
            'manganese': self._explain_manganese_availability(ph_value, availability['manganese'])
        }
        
        # Overall assessment
        avg_availability = np.mean(list(availability.values()))
        
        if avg_availability >= 0.9:
            overall_status = "excellent"
        elif avg_availability >= 0.8:
            overall_status = "good"
        elif avg_availability >= 0.7:
            overall_status = "fair"
        else:
            overall_status = "poor"
        
        return {
            'ph_value': ph_value,
            'overall_nutrient_availability': overall_status,
            'individual_nutrients': availability,
            'explanations': explanations,
            'most_limited_nutrients': [
                nutrient for nutrient, avail in availability.items() 
                if avail < 0.6
            ]
        }
    
    def _explain_nitrogen_availability(self, ph: float, availability: float) -> str:
        """Explain nitrogen availability at given pH."""
        if availability >= 0.9:
            return f"At pH {ph:.1f}, nitrogen availability is excellent. Soil microbes can efficiently convert organic nitrogen to plant-available forms."
        elif availability >= 0.7:
            return f"At pH {ph:.1f}, nitrogen availability is good. Some reduction in microbial activity may occur."
        else:
            return f"At pH {ph:.1f}, nitrogen availability is limited. Extreme pH reduces microbial activity and nitrogen cycling."
    
    def _explain_phosphorus_availability(self, ph: float, availability: float) -> str:
        """Explain phosphorus availability at given pH."""
        if ph < 6.0:
            return f"At pH {ph:.1f}, phosphorus is tied up by iron and aluminum, making it less available to plants."
        elif ph > 7.5:
            return f"At pH {ph:.1f}, phosphorus forms insoluble compounds with calcium, reducing plant availability."
        else:
            return f"At pH {ph:.1f}, phosphorus availability is near optimal. Most phosphorus remains in plant-available forms."
    
    def _explain_iron_availability(self, ph: float, availability: float) -> str:
        """Explain iron availability at given pH."""
        if ph > 7.0:
            return f"At pH {ph:.1f}, iron becomes increasingly unavailable as it forms insoluble hydroxides. Iron chlorosis may occur in sensitive crops."
        else:
            return f"At pH {ph:.1f}, iron availability is good. Iron remains in soluble, plant-available forms."
    
    def _explain_zinc_availability(self, ph: float, availability: float) -> str:
        """Explain zinc availability at given pH."""
        if ph > 7.0:
            return f"At pH {ph:.1f}, zinc availability decreases significantly. Zinc deficiency symptoms may appear, especially in young plants."
        else:
            return f"At pH {ph:.1f}, zinc availability is adequate for most crops."
    
    def _explain_manganese_availability(self, ph: float, availability: float) -> str:
        """Explain manganese availability at given pH."""
        if ph > 6.5:
            return f"At pH {ph:.1f}, manganese availability is reduced. Manganese deficiency may occur in sensitive crops like soybeans."
        elif ph < 5.5:
            return f"At pH {ph:.1f}, manganese may be too available, potentially reaching toxic levels in some crops."
        else:
            return f"At pH {ph:.1f}, manganese availability is in the optimal range."
    
    def _explain_potassium_availability(self, ph: float, availability: float) -> str:
        """Explain potassium availability at given pH."""
        return f"At pH {ph:.1f}, potassium availability is {availability*100:.0f}%. Potassium is generally available across a wide pH range, but extreme pH can affect uptake." 
       return economics

    def _interpolate_yield_impact(self, ph: float, yield_curve: Dict[float, float]) -> float:
        """Interpolate yield impact from pH-yield curve."""
        ph_values = sorted(yield_curve.keys())
        if ph <= ph_values[0]:
            return yield_curve[ph_values[0]]
        elif ph >= ph_values[-1]:
            return yield_curve[ph_values[-1]]
        
        # Linear interpolation
        for i in range(len(ph_values) - 1):
            if ph_values[i] <= ph <= ph_values[i + 1]:
                x1, y1 = ph_values[i], yield_curve[ph_values[i]]
                x2, y2 = ph_values[i + 1], yield_curve[ph_values[i + 1]]
                return y1 + (y2 - y1) * (ph - x1) / (x2 - x1)
        
        return 0.0

    def _develop_long_term_ph_strategy(
        self,
        ph_analysis: PHAnalysis,
        crop_type: str,
        field_conditions: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Develop long-term pH management strategy."""
        strategy = []
        
        # Maintenance strategy
        if ph_analysis.management_priority == "maintenance":
            strategy.append("Continue current pH management practices")
            strategy.append("Test pH every 3-4 years to monitor stability")
        
        # Improvement strategy
        else:
            strategy.append("Implement systematic pH correction program")
            strategy.append("Focus on building soil buffering capacity through organic matter")
            
        # Crop rotation considerations
        strategy.append("Consider pH requirements in crop rotation planning")
        
        # Fertilizer management
        strategy.append("Select fertilizers that support pH goals")
        
        # Organic matter strategy
        if ph_analysis.buffering_capacity in ["low", "very_low"]:
            strategy.append("Prioritize organic matter building to improve pH buffering")
        
        return strategy

    async def track_ph_monitoring_record(
        self,
        farm_id: str,
        field_id: str,
        ph_value: float,
        buffer_ph: Optional[float] = None,
        testing_method: str = "standard",
        lab_name: Optional[str] = None,
        notes: str = ""
    ) -> PHMonitoringRecord:
        """Track pH monitoring record over time."""
        record_id = f"ph_record_{farm_id}_{field_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        record = PHMonitoringRecord(
            record_id=record_id,
            farm_id=farm_id,
            field_id=field_id,
            test_date=datetime.now(),
            ph_value=ph_value,
            buffer_ph=buffer_ph,
            testing_method=testing_method,
            lab_name=lab_name,
            notes=notes
        )
        
        # Here you would typically save to database
        # await self.database.save_ph_record(record)
        
        return record

    async def analyze_ph_trends(
        self,
        farm_id: str,
        field_id: str,
        ph_records: List[PHMonitoringRecord]
    ) -> Dict[str, Any]:
        """Analyze pH trends over time."""
        if len(ph_records) < 2:
            return {
                "trend": "insufficient_data",
                "message": "Need at least 2 pH readings to analyze trends"
            }
        
        # Sort records by date
        sorted_records = sorted(ph_records, key=lambda x: x.test_date)
        
        # Calculate trend
        ph_values = [record.ph_value for record in sorted_records]
        dates = [record.test_date for record in sorted_records]
        
        # Simple linear trend calculation
        n = len(ph_values)
        sum_x = sum(range(n))
        sum_y = sum(ph_values)
        sum_xy = sum(i * ph for i, ph in enumerate(ph_values))
        sum_x2 = sum(i * i for i in range(n))
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction
        if abs(slope) < 0.05:  # Less than 0.05 pH units per reading
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        # Calculate rate of change per year
        time_span_years = (dates[-1] - dates[0]).days / 365.25
        annual_change = slope * (len(ph_values) - 1) / time_span_years if time_span_years > 0 else 0
        
        return {
            "trend": trend,
            "slope": slope,
            "annual_change_rate": annual_change,
            "current_ph": ph_values[-1],
            "initial_ph": ph_values[0],
            "total_change": ph_values[-1] - ph_values[0],
            "readings_count": len(ph_values),
            "time_span_years": time_span_years
        }

    async def generate_ph_alerts(
        self,
        ph_analysis: PHAnalysis,
        crop_type: str,
        ph_trends: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Generate pH-related alerts and warnings."""
        alerts = []
        
        # Critical pH alerts
        if ph_analysis.management_priority == "critical":
            alerts.append({
                "type": "critical",
                "title": "Critical pH Level Detected",
                "message": f"Soil pH of {ph_analysis.current_ph:.1f} requires immediate attention",
                "action_required": "Apply lime or sulfur treatment immediately",
                "urgency": "high"
            })
        
        # Crop suitability alerts
        if ph_analysis.crop_suitability_score < 0.5:
            alerts.append({
                "type": "warning",
                "title": "Poor Crop Suitability",
                "message": f"Current pH is poorly suited for {crop_type}",
                "action_required": "Consider pH adjustment or alternative crops",
                "urgency": "medium"
            })
        
        # Nutrient availability alerts
        critical_nutrients = [
            nutrient for nutrient, availability in ph_analysis.nutrient_availability_impact.items()
            if availability < 0.5
        ]
        
        if critical_nutrients:
            alerts.append({
                "type": "warning",
                "title": "Nutrient Availability Issues",
                "message": f"Low availability of: {', '.join(critical_nutrients)}",
                "action_required": "Adjust pH or supplement affected nutrients",
                "urgency": "medium"
            })
        
        # Trend-based alerts
        if ph_trends:
            if ph_trends["trend"] == "decreasing" and abs(ph_trends["annual_change_rate"]) > 0.2:
                alerts.append({
                    "type": "warning",
                    "title": "Rapid Soil Acidification",
                    "message": f"pH declining at {abs(ph_trends['annual_change_rate']):.2f} units per year",
                    "action_required": "Investigate acidification causes and implement prevention",
                    "urgency": "medium"
                })
        
        return alerts

    async def calculate_buffer_ph_requirements(
        self,
        current_buffer_ph: float,
        target_ph: float,
        soil_texture: str,
        organic_matter_percent: float
    ) -> Dict[str, Any]:
        """Calculate lime requirements using buffer pH method."""
        
        # Buffer pH to lime requirement lookup table (tons/acre)
        buffer_lime_table = {
            7.0: 0.0, 6.9: 0.5, 6.8: 1.0, 6.7: 1.5, 6.6: 2.0,
            6.5: 2.5, 6.4: 3.0, 6.3: 3.5, 6.2: 4.0, 6.1: 4.5,
            6.0: 5.0, 5.9: 5.5, 5.8: 6.0, 5.7: 6.5, 5.6: 7.0,
            5.5: 7.5, 5.4: 8.0, 5.3: 8.5, 5.2: 9.0, 5.1: 9.5,
            5.0: 10.0
        }
        
        # Find closest buffer pH value
        closest_buffer = min(buffer_lime_table.keys(), key=lambda x: abs(x - current_buffer_ph))
        base_lime_rate = buffer_lime_table[closest_buffer]
        
        # Adjust for soil texture
        texture_factors = {
            'sand': 0.8, 'loamy_sand': 0.9, 'sandy_loam': 0.95,
            'loam': 1.0, 'silt_loam': 1.05, 'clay_loam': 1.1, 'clay': 1.2
        }
        
        texture_factor = texture_factors.get(soil_texture.lower().replace(' ', '_'), 1.0)
        
        # Adjust for organic matter
        om_factor = 1.0 + (organic_matter_percent - 3.0) * 0.1
        om_factor = max(0.7, min(1.5, om_factor))
        
        adjusted_lime_rate = base_lime_rate * texture_factor * om_factor
        
        return {
            "base_lime_rate_tons_per_acre": base_lime_rate,
            "adjusted_lime_rate_tons_per_acre": adjusted_lime_rate,
            "texture_adjustment_factor": texture_factor,
            "organic_matter_adjustment_factor": om_factor,
            "buffer_ph_used": closest_buffer,
            "confidence": "high" if abs(closest_buffer - current_buffer_ph) < 0.1 else "medium"
        }

    async def assess_alkaline_soil_management(
        self,
        ph_analysis: PHAnalysis,
        soil_test_data: SoilTestData,
        crop_type: str
    ) -> Dict[str, Any]:
        """Assess alkaline soil management strategies."""
        
        if ph_analysis.current_ph <= 7.5:
            return {"management_needed": False, "message": "Soil is not alkaline"}
        
        management_strategies = []
        
        # Sulfur application for moderate alkalinity
        if 7.5 < ph_analysis.current_ph <= 8.5:
            sulfur_rate = self._calculate_sulfur_requirement(
                ph_analysis.current_ph, ph_analysis.target_ph
            )
            management_strategies.append({
                "strategy": "sulfur_application",
                "rate_lbs_per_acre": sulfur_rate,
                "expected_ph_reduction": min(1.0, (ph_analysis.current_ph - ph_analysis.target_ph) * 0.7),
                "timeline": "6-12 months"
            })
        
        # Organic matter for buffering
        management_strategies.append({
            "strategy": "organic_matter_addition",
            "materials": ["compost", "well_rotted_manure", "peat_moss"],
            "rate_tons_per_acre": 3.0,
            "benefits": ["improved_buffering", "better_nutrient_availability"]
        })
        
        # Micronutrient management
        deficient_micronutrients = [
            nutrient for nutrient, availability in ph_analysis.nutrient_availability_impact.items()
            if nutrient in ['iron', 'manganese', 'zinc'] and availability < 0.6
        ]
        
        if deficient_micronutrients:
            management_strategies.append({
                "strategy": "micronutrient_supplementation",
                "nutrients": deficient_micronutrients,
                "application_method": "foliar_spray_or_chelated_forms"
            })
        
        # Crop selection recommendations
        alkaline_tolerant_crops = {
            'alfalfa': 'excellent', 'wheat': 'good', 'barley': 'good',
            'sugar_beet': 'excellent', 'asparagus': 'good'
        }
        
        crop_tolerance = alkaline_tolerant_crops.get(crop_type, 'poor')
        
        return {
            "management_needed": True,
            "alkalinity_level": self._classify_alkalinity_level(ph_analysis.current_ph),
            "management_strategies": management_strategies,
            "crop_tolerance": crop_tolerance,
            "monitoring_frequency": "every_6_months" if ph_analysis.current_ph > 8.0 else "annually"
        }

    def _calculate_sulfur_requirement(self, current_ph: float, target_ph: float) -> float:
        """Calculate sulfur requirement to lower pH."""
        ph_reduction_needed = current_ph - target_ph
        
        # Sulfur requirement (lbs/acre) per pH unit reduction
        # Varies by soil type - using average values
        sulfur_per_ph_unit = 300  # lbs/acre
        
        return min(ph_reduction_needed * sulfur_per_ph_unit, 500)  # Cap at 500 lbs/acre

    def _classify_alkalinity_level(self, ph: float) -> str:
        """Classify alkalinity level."""
        if ph <= 7.3:
            return "neutral"
        elif ph <= 7.8:
            return "slightly_alkaline"
        elif ph <= 8.4:
            return "moderately_alkaline"
        elif ph <= 9.0:
            return "strongly_alkaline"
        else:
            return "very_strongly_alkaline"