"""
Comprehensive Soil Fertility Assessment Service
Provides advanced soil fertility analysis, sustainable improvement recommendations,
and long-term soil health tracking capabilities.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from ..models.agricultural_models import SoilTestData


@dataclass
class SoilHealthScore:
    """Comprehensive soil health scoring."""
    overall_score: float  # 0-100
    nutrient_score: float
    biological_score: float
    physical_score: float
    chemical_score: float
    improvement_potential: float
    limiting_factors: List[str]
    strengths: List[str]


@dataclass
class FertilizationGoal:
    """Fertilization and soil improvement goals."""
    goal_id: str
    goal_type: str  # 'chemical_reduction', 'organic_matter', 'sustainability', 'economic'
    target_value: float
    current_value: float
    timeline_years: int
    priority: int  # 1-10
    description: str
    measurement_criteria: List[str]


@dataclass
class SoilImprovementPlan:
    """Comprehensive soil improvement plan."""
    plan_id: str
    farm_id: str
    field_id: str
    goals: List[FertilizationGoal]
    organic_amendments: List[Dict[str, Any]]
    cover_crop_recommendations: List[Dict[str, Any]]
    fertilizer_optimization: Dict[str, Any]
    implementation_timeline: Dict[int, List[str]]  # year -> actions
    expected_benefits: Dict[str, float]
    cost_analysis: Dict[str, float]
    created_at: datetime


class SoilFertilityAssessmentService:
    """Advanced soil fertility assessment and improvement planning."""
    
    def __init__(self):
        self.nutrient_sufficiency_ranges = self._initialize_sufficiency_ranges()
        self.organic_amendments_database = self._initialize_organic_amendments()
        self.cover_crop_database = self._initialize_cover_crops()
        self.soil_biology_indicators = self._initialize_biology_indicators()    

    def _initialize_sufficiency_ranges(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Initialize nutrient sufficiency ranges by crop and soil type."""
        return {
            'corn': {
                'phosphorus_ppm': (20, 40),
                'potassium_ppm': (160, 300),
                'organic_matter_percent': (3.0, 5.0),
                'ph': (6.0, 6.8),
                'zinc_ppm': (1.0, 3.0),
                'iron_ppm': (4.5, 25.0),
                'manganese_ppm': (1.0, 5.0),
                'copper_ppm': (0.2, 1.0),
                'boron_ppm': (0.5, 2.0)
            },
            'soybean': {
                'phosphorus_ppm': (15, 35),
                'potassium_ppm': (140, 280),
                'organic_matter_percent': (2.5, 4.5),
                'ph': (6.0, 7.0),
                'zinc_ppm': (0.8, 2.5),
                'iron_ppm': (4.0, 20.0),
                'manganese_ppm': (1.0, 4.0),
                'copper_ppm': (0.2, 0.8),
                'boron_ppm': (0.5, 1.5)
            },
            'wheat': {
                'phosphorus_ppm': (18, 38),
                'potassium_ppm': (150, 290),
                'organic_matter_percent': (2.8, 4.8),
                'ph': (6.2, 7.2),
                'zinc_ppm': (0.9, 2.8),
                'iron_ppm': (4.2, 22.0),
                'manganese_ppm': (1.2, 4.5),
                'copper_ppm': (0.2, 0.9),
                'boron_ppm': (0.4, 1.8)
            }
        }
    
    def _initialize_organic_amendments(self) -> Dict[str, Dict[str, Any]]:
        """Initialize organic amendment database."""
        return {
            'compost': {
                'nitrogen_percent': 1.5,
                'phosphorus_percent': 0.8,
                'potassium_percent': 1.2,
                'organic_matter_percent': 45.0,
                'application_rate_tons_per_acre': (2, 8),
                'cost_per_ton': 35.0,
                'benefits': ['organic_matter', 'soil_structure', 'water_retention', 'biology'],
                'application_timing': ['fall', 'early_spring'],
                'incorporation_required': True
            },
            'aged_manure': {
                'nitrogen_percent': 2.0,
                'phosphorus_percent': 1.2,
                'potassium_percent': 2.5,
                'organic_matter_percent': 35.0,
                'application_rate_tons_per_acre': (5, 15),
                'cost_per_ton': 25.0,
                'benefits': ['nutrients', 'organic_matter', 'biology', 'soil_structure'],
                'application_timing': ['fall', 'spring'],
                'incorporation_required': True
            },
            'biochar': {
                'nitrogen_percent': 0.5,
                'phosphorus_percent': 0.3,
                'potassium_percent': 0.8,
                'organic_matter_percent': 80.0,
                'application_rate_tons_per_acre': (0.5, 2.0),
                'cost_per_ton': 150.0,
                'benefits': ['carbon_sequestration', 'water_retention', 'nutrient_retention'],
                'application_timing': ['any'],
                'incorporation_required': False
            }
        }
    
    def _initialize_cover_crops(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cover crop database."""
        return {
            'crimson_clover': {
                'nitrogen_fixation_lbs_per_acre': 60,
                'biomass_production_tons_per_acre': 2.5,
                'root_depth_inches': 24,
                'seeding_rate_lbs_per_acre': 15,
                'seeding_cost_per_acre': 25.0,
                'planting_window': {'start': 'august_15', 'end': 'september_30'},
                'termination_timing': 'april_15',
                'benefits': ['nitrogen_fixation', 'erosion_control', 'soil_biology'],
                'soil_types': ['well_drained', 'moderately_drained']
            },
            'winter_rye': {
                'nitrogen_fixation_lbs_per_acre': 0,
                'biomass_production_tons_per_acre': 3.0,
                'root_depth_inches': 36,
                'seeding_rate_lbs_per_acre': 90,
                'seeding_cost_per_acre': 18.0,
                'planting_window': {'start': 'september_1', 'end': 'october_15'},
                'termination_timing': 'april_30',
                'benefits': ['erosion_control', 'weed_suppression', 'organic_matter'],
                'soil_types': ['all']
            }
        }    

    def _initialize_biology_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize soil biology health indicators."""
        return {
            'organic_matter': {
                'excellent': (4.0, float('inf')),
                'good': (3.0, 4.0),
                'fair': (2.0, 3.0),
                'poor': (0, 2.0),
                'weight': 0.3
            },
            'soil_respiration': {
                'excellent': (200, float('inf')),  # mg CO2/kg soil/day
                'good': (150, 200),
                'fair': (100, 150),
                'poor': (0, 100),
                'weight': 0.25
            },
            'aggregate_stability': {
                'excellent': (80, 100),  # percentage
                'good': (60, 80),
                'fair': (40, 60),
                'poor': (0, 40),
                'weight': 0.2
            },
            'earthworm_count': {
                'excellent': (10, float('inf')),  # per cubic foot
                'good': (6, 10),
                'fair': (3, 6),
                'poor': (0, 3),
                'weight': 0.15
            },
            'water_infiltration': {
                'excellent': (2.0, float('inf')),  # inches per hour
                'good': (1.0, 2.0),
                'fair': (0.5, 1.0),
                'poor': (0, 0.5),
                'weight': 0.1
            }
        }
    
    async def assess_comprehensive_soil_fertility(
        self,
        soil_test_data: SoilTestData,
        crop_type: str,
        field_characteristics: Dict[str, Any],
        historical_data: Optional[List[SoilTestData]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive soil fertility assessment."""
        
        # Calculate soil health score
        soil_health_score = await self._calculate_soil_health_score(
            soil_test_data, field_characteristics
        )
        
        # Analyze nutrient status
        nutrient_analysis = await self._analyze_nutrient_status(
            soil_test_data, crop_type
        )
        
        # Assess soil biology
        biology_assessment = await self._assess_soil_biology(
            soil_test_data, field_characteristics
        )
        
        # Analyze trends if historical data available
        trend_analysis = None
        if historical_data:
            trend_analysis = await self._analyze_soil_fertility_trends(
                historical_data, soil_test_data
            )
        
        # Generate improvement recommendations
        improvement_recommendations = await self._generate_improvement_recommendations(
            soil_health_score, nutrient_analysis, biology_assessment, crop_type
        )
        
        return {
            'assessment_id': f"soil_assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'soil_health_score': soil_health_score,
            'nutrient_analysis': nutrient_analysis,
            'biology_assessment': biology_assessment,
            'trend_analysis': trend_analysis,
            'improvement_recommendations': improvement_recommendations,
            'assessment_date': datetime.now(),
            'confidence_level': self._calculate_assessment_confidence(soil_test_data)
        }
    
    async def _calculate_soil_health_score(
        self,
        soil_test_data: SoilTestData,
        field_characteristics: Dict[str, Any]
    ) -> SoilHealthScore:
        """Calculate comprehensive soil health score."""
        
        # Nutrient score (0-100)
        nutrient_score = self._calculate_nutrient_score(soil_test_data)
        
        # Chemical score (pH, CEC, base saturation)
        chemical_score = self._calculate_chemical_score(soil_test_data)
        
        # Physical score (structure, compaction, drainage)
        physical_score = self._calculate_physical_score(
            soil_test_data, field_characteristics
        )
        
        # Biological score (organic matter, activity indicators)
        biological_score = self._calculate_biological_score(soil_test_data)
        
        # Overall score (weighted average)
        overall_score = (
            nutrient_score * 0.25 +
            chemical_score * 0.25 +
            physical_score * 0.25 +
            biological_score * 0.25
        )
        
        # Identify limiting factors and strengths
        limiting_factors = self._identify_limiting_factors(
            nutrient_score, chemical_score, physical_score, biological_score
        )
        
        strengths = self._identify_strengths(
            nutrient_score, chemical_score, physical_score, biological_score
        )
        
        # Calculate improvement potential
        improvement_potential = min(100 - overall_score, 30)  # Cap at 30 points
        
        return SoilHealthScore(
            overall_score=overall_score,
            nutrient_score=nutrient_score,
            biological_score=biological_score,
            physical_score=physical_score,
            chemical_score=chemical_score,
            improvement_potential=improvement_potential,
            limiting_factors=limiting_factors,
            strengths=strengths
        )    

    def _calculate_nutrient_score(self, soil_test_data: SoilTestData) -> float:
        """Calculate nutrient adequacy score."""
        
        nutrient_scores = []
        
        # Primary nutrients
        if hasattr(soil_test_data, 'phosphorus_ppm'):
            p_score = self._score_nutrient_level(
                soil_test_data.phosphorus_ppm, (15, 40), 'phosphorus'
            )
            nutrient_scores.append(p_score)
        
        if hasattr(soil_test_data, 'potassium_ppm'):
            k_score = self._score_nutrient_level(
                soil_test_data.potassium_ppm, (140, 300), 'potassium'
            )
            nutrient_scores.append(k_score)
        
        # Micronutrients (if available)
        micronutrients = ['zinc_ppm', 'iron_ppm', 'manganese_ppm', 'copper_ppm', 'boron_ppm']
        for nutrient in micronutrients:
            if hasattr(soil_test_data, nutrient):
                value = getattr(soil_test_data, nutrient)
                if nutrient == 'zinc_ppm':
                    score = self._score_nutrient_level(value, (1.0, 3.0), 'zinc')
                elif nutrient == 'iron_ppm':
                    score = self._score_nutrient_level(value, (4.5, 25.0), 'iron')
                elif nutrient == 'manganese_ppm':
                    score = self._score_nutrient_level(value, (1.0, 5.0), 'manganese')
                elif nutrient == 'copper_ppm':
                    score = self._score_nutrient_level(value, (0.2, 1.0), 'copper')
                elif nutrient == 'boron_ppm':
                    score = self._score_nutrient_level(value, (0.5, 2.0), 'boron')
                
                nutrient_scores.append(score)
        
        return np.mean(nutrient_scores) if nutrient_scores else 50.0
    
    def _score_nutrient_level(self, value: float, optimal_range: Tuple[float, float], nutrient_name: str) -> float:
        """Score individual nutrient level."""
        
        low_optimal, high_optimal = optimal_range
        
        if low_optimal <= value <= high_optimal:
            return 100.0  # Optimal range
        elif value < low_optimal:
            # Below optimal - score based on how far below
            if value < low_optimal * 0.5:
                return 20.0  # Very deficient
            elif value < low_optimal * 0.75:
                return 50.0  # Deficient
            else:
                return 75.0  # Slightly low
        else:
            # Above optimal - generally less problematic than deficiency
            if value > high_optimal * 2.0:
                return 60.0  # Very high (potential toxicity)
            elif value > high_optimal * 1.5:
                return 80.0  # High
            else:
                return 90.0  # Slightly high
    
    def _calculate_chemical_score(self, soil_test_data: SoilTestData) -> float:
        """Calculate chemical properties score."""
        
        scores = []
        
        # pH score
        if hasattr(soil_test_data, 'ph'):
            ph_score = self._score_ph_level(soil_test_data.ph)
            scores.append(ph_score)
        
        # CEC score (if available)
        if hasattr(soil_test_data, 'cec_meq_per_100g'):
            cec_score = self._score_cec_level(soil_test_data.cec_meq_per_100g)
            scores.append(cec_score)
        
        # Base saturation (if available)
        if hasattr(soil_test_data, 'base_saturation_percent'):
            base_sat_score = self._score_base_saturation(soil_test_data.base_saturation_percent)
            scores.append(base_sat_score)
        
        return np.mean(scores) if scores else 70.0
    
    def _score_ph_level(self, ph: float) -> float:
        """Score soil pH level."""
        
        if 6.0 <= ph <= 7.0:
            return 100.0  # Optimal for most crops
        elif 5.5 <= ph < 6.0 or 7.0 < ph <= 7.5:
            return 85.0  # Good
        elif 5.0 <= ph < 5.5 or 7.5 < ph <= 8.0:
            return 65.0  # Fair
        elif 4.5 <= ph < 5.0 or 8.0 < ph <= 8.5:
            return 40.0  # Poor
        else:
            return 20.0  # Very poor
    
    def _calculate_physical_score(
        self,
        soil_test_data: SoilTestData,
        field_characteristics: Dict[str, Any]
    ) -> float:
        """Calculate physical properties score."""
        
        scores = []
        
        # Organic matter (affects structure)
        if hasattr(soil_test_data, 'organic_matter_percent'):
            om_score = self._score_organic_matter(soil_test_data.organic_matter_percent)
            scores.append(om_score)
        
        # Bulk density (if available)
        if 'bulk_density' in field_characteristics:
            bd_score = self._score_bulk_density(field_characteristics['bulk_density'])
            scores.append(bd_score)
        
        # Drainage class
        if 'drainage_class' in field_characteristics:
            drainage_score = self._score_drainage_class(field_characteristics['drainage_class'])
            scores.append(drainage_score)
        
        # Compaction indicators
        if 'compaction_issues' in field_characteristics:
            compaction_score = 30.0 if field_characteristics['compaction_issues'] else 90.0
            scores.append(compaction_score)
        
        return np.mean(scores) if scores else 70.0
    
    def _calculate_biological_score(self, soil_test_data: SoilTestData) -> float:
        """Calculate biological activity score."""
        
        scores = []
        
        # Organic matter (primary indicator)
        if hasattr(soil_test_data, 'organic_matter_percent'):
            om_score = self._score_organic_matter_biology(soil_test_data.organic_matter_percent)
            scores.append(om_score)
        
        # Soil respiration (if available)
        if hasattr(soil_test_data, 'soil_respiration'):
            respiration_score = self._score_soil_respiration(soil_test_data.soil_respiration)
            scores.append(respiration_score)
        
        # Microbial biomass (if available)
        if hasattr(soil_test_data, 'microbial_biomass'):
            biomass_score = self._score_microbial_biomass(soil_test_data.microbial_biomass)
            scores.append(biomass_score)
        
        return np.mean(scores) if scores else 60.0