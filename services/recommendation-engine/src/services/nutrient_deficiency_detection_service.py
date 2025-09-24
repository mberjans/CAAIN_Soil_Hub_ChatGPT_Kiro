"""
Comprehensive Nutrient Deficiency Detection Service
Provides advanced nutrient deficiency analysis using soil tests, tissue tests,
visual symptoms, and AI-powered image analysis.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import base64
from io import BytesIO

from ..models.agricultural_models import SoilTestData


class DeficiencyType(Enum):
    """Types of nutrient deficiencies."""
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    CALCIUM = "calcium"
    MAGNESIUM = "magnesium"
    SULFUR = "sulfur"
    IRON = "iron"
    MANGANESE = "manganese"
    ZINC = "zinc"
    COPPER = "copper"
    BORON = "boron"
    MOLYBDENUM = "molybdenum"


class DeficiencySeverity(Enum):
    """Severity levels for nutrient deficiencies."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"
    CRITICAL = "critical"


@dataclass
class DeficiencyAnalysis:
    """Comprehensive deficiency analysis result."""
    deficiency_type: DeficiencyType
    severity: DeficiencySeverity
    confidence_score: float  # 0-1
    probability: float  # 0-1
    evidence_sources: List[str]  # soil_test, tissue_test, visual_symptoms, image_analysis
    impact_assessment: Dict[str, float]
    urgency_score: float  # 0-100
    yield_impact_percent: float
    economic_impact_dollars_per_acre: float


@dataclass
class VisualSymptomAnalysis:
    """Visual symptom analysis from images or descriptions."""
    detected_symptoms: List[str]
    symptom_severity: Dict[str, float]
    affected_plant_parts: List[str]
    symptom_distribution: str  # uniform, patchy, localized
    confidence_score: float
    alternative_diagnoses: List[str]


@dataclass
class TreatmentRecommendation:
    """Treatment recommendation for nutrient deficiency."""
    deficiency_type: DeficiencyType
    treatment_type: str  # fertilizer, foliar, soil_amendment
    product_recommendations: List[Dict[str, Any]]
    application_rate: float
    application_timing: str
    application_method: str
    expected_response_time: str
    cost_estimate_per_acre: float
    effectiveness_probability: float


class NutrientDeficiencyDetectionService:
    """Advanced nutrient deficiency detection and analysis service."""
    
    def __init__(self):
        self.deficiency_thresholds = self._initialize_deficiency_thresholds()
        self.symptom_database = self._initialize_symptom_database()
        self.treatment_database = self._initialize_treatment_database()
        self.visual_analyzer = VisualSymptomAnalyzer()
        self.image_analyzer = CropImageAnalyzer()
    
    def _initialize_deficiency_thresholds(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Initialize nutrient deficiency thresholds by crop and test type."""
        return {
            'corn': {
                'soil_test': {
                    'nitrogen_ppm': {'severe': 5, 'moderate': 8, 'mild': 12},
                    'phosphorus_ppm': {'severe': 8, 'moderate': 12, 'mild': 16},
                    'potassium_ppm': {'severe': 80, 'moderate': 120, 'mild': 160},
                    'zinc_ppm': {'severe': 0.5, 'moderate': 0.8, 'mild': 1.0},
                    'iron_ppm': {'severe': 2.0, 'moderate': 3.0, 'mild': 4.0},
                    'manganese_ppm': {'severe': 0.5, 'moderate': 0.8, 'mild': 1.0},
                    'copper_ppm': {'severe': 0.1, 'moderate': 0.15, 'mild': 0.2},
                    'boron_ppm': {'severe': 0.2, 'moderate': 0.3, 'mild': 0.4}
                },
                'tissue_test': {
                    'nitrogen_percent': {'severe': 2.0, 'moderate': 2.5, 'mild': 2.8},
                    'phosphorus_percent': {'severe': 0.15, 'moderate': 0.20, 'mild': 0.25},
                    'potassium_percent': {'severe': 1.2, 'moderate': 1.5, 'mild': 1.8},
                    'zinc_ppm': {'severe': 15, 'moderate': 20, 'mild': 25},
                    'iron_ppm': {'severe': 30, 'moderate': 50, 'mild': 70},
                    'manganese_ppm': {'severe': 15, 'moderate': 20, 'mild': 25}
                }
            },
            'soybean': {
                'soil_test': {
                    'phosphorus_ppm': {'severe': 6, 'moderate': 10, 'mild': 15},
                    'potassium_ppm': {'severe': 70, 'moderate': 110, 'mild': 140},
                    'zinc_ppm': {'severe': 0.4, 'moderate': 0.7, 'mild': 0.9},
                    'iron_ppm': {'severe': 2.5, 'moderate': 4.0, 'mild': 5.0},
                    'manganese_ppm': {'severe': 0.8, 'moderate': 1.2, 'mild': 1.5}
                },
                'tissue_test': {
                    'nitrogen_percent': {'severe': 3.5, 'moderate': 4.0, 'mild': 4.5},
                    'phosphorus_percent': {'severe': 0.20, 'moderate': 0.25, 'mild': 0.30},
                    'potassium_percent': {'severe': 1.5, 'moderate': 1.8, 'mild': 2.0}
                }
            }
        }
    
    def _initialize_symptom_database(self) -> Dict[DeficiencyType, Dict[str, Any]]:
        """Initialize comprehensive symptom database."""
        return {
            DeficiencyType.NITROGEN: {
                'visual_symptoms': [
                    'yellowing of older leaves',
                    'stunted growth',
                    'pale green coloration',
                    'reduced tillering',
                    'early senescence'
                ],
                'symptom_progression': 'starts_with_older_leaves',
                'affected_parts': ['older_leaves', 'whole_plant'],
                'timing': 'early_to_mid_season',
                'distinguishing_features': ['uniform_yellowing', 'v_shaped_pattern']
            },
            DeficiencyType.PHOSPHORUS: {
                'visual_symptoms': [
                    'purpling of leaves',
                    'delayed maturity',
                    'poor root development',
                    'reduced flowering',
                    'dark green coloration with purple tinge'
                ],
                'symptom_progression': 'starts_with_older_leaves',
                'affected_parts': ['older_leaves', 'stems', 'roots'],
                'timing': 'early_season',
                'distinguishing_features': ['purple_coloration', 'delayed_development']
            },
            DeficiencyType.POTASSIUM: {
                'visual_symptoms': [
                    'leaf margin burn',
                    'yellowing between veins',
                    'weak stems',
                    'increased disease susceptibility',
                    'poor grain fill'
                ],
                'symptom_progression': 'starts_with_older_leaves',
                'affected_parts': ['leaf_margins', 'older_leaves'],
                'timing': 'mid_to_late_season',
                'distinguishing_features': ['marginal_burn', 'interveinal_yellowing']
            },
            DeficiencyType.IRON: {
                'visual_symptoms': [
                    'interveinal chlorosis',
                    'yellowing with green veins',
                    'white or yellow new growth',
                    'stunted growth'
                ],
                'symptom_progression': 'starts_with_younger_leaves',
                'affected_parts': ['younger_leaves', 'new_growth'],
                'timing': 'early_season',
                'distinguishing_features': ['green_veins_yellow_tissue', 'young_leaves_first']
            },
            DeficiencyType.ZINC: {
                'visual_symptoms': [
                    'white bud syndrome',
                    'interveinal striping',
                    'shortened internodes',
                    'small leaves',
                    'delayed maturity'
                ],
                'symptom_progression': 'starts_with_younger_leaves',
                'affected_parts': ['younger_leaves', 'growing_points'],
                'timing': 'early_season',
                'distinguishing_features': ['white_striping', 'shortened_internodes']
            }
        }
    
    def _initialize_treatment_database(self) -> Dict[DeficiencyType, List[Dict[str, Any]]]:
        """Initialize treatment recommendation database."""
        return {
            DeficiencyType.NITROGEN: [
                {
                    'treatment_type': 'soil_fertilizer',
                    'products': ['urea', 'ammonium_nitrate', 'anhydrous_ammonia'],
                    'application_rate_range': (30, 150),  # lbs N/acre
                    'timing': 'pre_plant_or_side_dress',
                    'method': 'broadcast_or_banded',
                    'response_time': '7-14_days',
                    'cost_per_lb_n': 0.45
                },
                {
                    'treatment_type': 'foliar_fertilizer',
                    'products': ['urea_solution', 'liquid_nitrogen'],
                    'application_rate_range': (10, 30),  # lbs N/acre
                    'timing': 'early_growth_stages',
                    'method': 'foliar_spray',
                    'response_time': '3-7_days',
                    'cost_per_lb_n': 0.65
                }
            ],
            DeficiencyType.PHOSPHORUS: [
                {
                    'treatment_type': 'soil_fertilizer',
                    'products': ['DAP', 'MAP', 'triple_superphosphate'],
                    'application_rate_range': (20, 80),  # lbs P2O5/acre
                    'timing': 'pre_plant_or_starter',
                    'method': 'banded_near_seed',
                    'response_time': '14-21_days',
                    'cost_per_lb_p2o5': 0.55
                },
                {
                    'treatment_type': 'foliar_fertilizer',
                    'products': ['liquid_phosphate', 'phosphoric_acid'],
                    'application_rate_range': (2, 8),  # lbs P2O5/acre
                    'timing': 'early_vegetative',
                    'method': 'foliar_spray',
                    'response_time': '7-14_days',
                    'cost_per_lb_p2o5': 0.85
                }
            ],
            DeficiencyType.POTASSIUM: [
                {
                    'treatment_type': 'soil_fertilizer',
                    'products': ['muriate_of_potash', 'sulfate_of_potash'],
                    'application_rate_range': (40, 120),  # lbs K2O/acre
                    'timing': 'pre_plant_or_side_dress',
                    'method': 'broadcast_incorporated',
                    'response_time': '14-28_days',
                    'cost_per_lb_k2o': 0.35
                }
            ],
            DeficiencyType.ZINC: [
                {
                    'treatment_type': 'soil_fertilizer',
                    'products': ['zinc_sulfate', 'zinc_oxide'],
                    'application_rate_range': (5, 15),  # lbs Zn/acre
                    'timing': 'pre_plant',
                    'method': 'broadcast_or_banded',
                    'response_time': '21-35_days',
                    'cost_per_lb_zn': 2.50
                },
                {
                    'treatment_type': 'foliar_fertilizer',
                    'products': ['zinc_sulfate_solution', 'chelated_zinc'],
                    'application_rate_range': (0.5, 2.0),  # lbs Zn/acre
                    'timing': 'early_vegetative',
                    'method': 'foliar_spray',
                    'response_time': '7-14_days',
                    'cost_per_lb_zn': 4.00
                }
            ],
            DeficiencyType.IRON: [
                {
                    'treatment_type': 'foliar_fertilizer',
                    'products': ['iron_chelate', 'ferrous_sulfate'],
                    'application_rate_range': (0.5, 2.0),  # lbs Fe/acre
                    'timing': 'early_vegetative',
                    'method': 'foliar_spray',
                    'response_time': '5-10_days',
                    'cost_per_lb_fe': 3.50
                },
                {
                    'treatment_type': 'soil_amendment',
                    'products': ['sulfur', 'acidifying_fertilizer'],
                    'application_rate_range': (100, 500),  # lbs/acre
                    'timing': 'fall_or_early_spring',
                    'method': 'broadcast_incorporated',
                    'response_time': '30-60_days',
                    'cost_per_lb': 0.25
                }
            ]
        } 
   
    async def analyze_comprehensive_deficiency(
        self,
        crop_type: str,
        soil_test_data: Optional[SoilTestData] = None,
        tissue_test_data: Optional[Dict[str, float]] = None,
        visual_symptoms: Optional[List[str]] = None,
        crop_images: Optional[List[str]] = None,  # base64 encoded images
        field_observations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform comprehensive nutrient deficiency analysis."""
        
        deficiency_analyses = []
        
        # Analyze each potential deficiency type
        for deficiency_type in DeficiencyType:
            analysis = await self._analyze_single_deficiency(
                deficiency_type,
                crop_type,
                soil_test_data,
                tissue_test_data,
                visual_symptoms,
                crop_images,
                field_observations
            )
            
            if analysis.probability > 0.1:  # Only include likely deficiencies
                deficiency_analyses.append(analysis)
        
        # Sort by urgency and probability
        deficiency_analyses.sort(key=lambda x: (x.urgency_score, x.probability), reverse=True)
        
        # Generate treatment recommendations
        treatment_recommendations = []
        for analysis in deficiency_analyses[:5]:  # Top 5 deficiencies
            treatments = await self._generate_treatment_recommendations(
                analysis, crop_type, field_observations
            )
            treatment_recommendations.extend(treatments)
        
        # Create monitoring recommendations
        monitoring_plan = await self._create_monitoring_plan(
            deficiency_analyses, crop_type
        )
        
        return {
            'analysis_id': f"deficiency_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'crop_type': crop_type,
            'deficiency_analyses': deficiency_analyses,
            'treatment_recommendations': treatment_recommendations,
            'monitoring_plan': monitoring_plan,
            'overall_risk_score': self._calculate_overall_risk_score(deficiency_analyses),
            'priority_actions': self._identify_priority_actions(deficiency_analyses),
            'analysis_date': datetime.now(),
            'confidence_level': self._calculate_overall_confidence(deficiency_analyses)
        }
    
    async def _analyze_single_deficiency(
        self,
        deficiency_type: DeficiencyType,
        crop_type: str,
        soil_test_data: Optional[SoilTestData],
        tissue_test_data: Optional[Dict[str, float]],
        visual_symptoms: Optional[List[str]],
        crop_images: Optional[List[str]],
        field_observations: Optional[Dict[str, Any]]
    ) -> DeficiencyAnalysis:
        """Analyze a single nutrient deficiency type."""
        
        evidence_sources = []
        confidence_scores = []
        severity_scores = []
        
        # Soil test analysis
        soil_severity, soil_confidence = 0.0, 0.0
        if soil_test_data:
            soil_severity, soil_confidence = self._analyze_soil_test_deficiency(
                deficiency_type, crop_type, soil_test_data
            )
            if soil_confidence > 0.3:
                evidence_sources.append('soil_test')
                confidence_scores.append(soil_confidence)
                severity_scores.append(soil_severity)
        
        # Tissue test analysis
        tissue_severity, tissue_confidence = 0.0, 0.0
        if tissue_test_data:
            tissue_severity, tissue_confidence = self._analyze_tissue_test_deficiency(
                deficiency_type, crop_type, tissue_test_data
            )
            if tissue_confidence > 0.3:
                evidence_sources.append('tissue_test')
                confidence_scores.append(tissue_confidence)
                severity_scores.append(tissue_severity)
        
        # Visual symptom analysis
        visual_severity, visual_confidence = 0.0, 0.0
        if visual_symptoms:
            visual_severity, visual_confidence = self._analyze_visual_symptoms(
                deficiency_type, visual_symptoms
            )
            if visual_confidence > 0.3:
                evidence_sources.append('visual_symptoms')
                confidence_scores.append(visual_confidence)
                severity_scores.append(visual_severity)
        
        # Image analysis
        image_severity, image_confidence = 0.0, 0.0
        if crop_images:
            image_severity, image_confidence = await self._analyze_crop_images(
                deficiency_type, crop_images
            )
            if image_confidence > 0.3:
                evidence_sources.append('image_analysis')
                confidence_scores.append(image_confidence)
                severity_scores.append(image_severity)
        
        # Calculate overall probability and confidence
        if confidence_scores:
            overall_confidence = np.mean(confidence_scores)
            weighted_severity = np.average(severity_scores, weights=confidence_scores)
            probability = min(1.0, overall_confidence * (weighted_severity / 100))
        else:
            overall_confidence = 0.0
            weighted_severity = 0.0
            probability = 0.0
        
        # Determine severity level
        severity = self._determine_severity_level(weighted_severity)
        
        # Calculate impact assessment
        impact_assessment = self._calculate_deficiency_impact(
            deficiency_type, severity, crop_type
        )
        
        # Calculate urgency score
        urgency_score = self._calculate_urgency_score(
            deficiency_type, severity, crop_type, field_observations
        )
        
        return DeficiencyAnalysis(
            deficiency_type=deficiency_type,
            severity=severity,
            confidence_score=overall_confidence,
            probability=probability,
            evidence_sources=evidence_sources,
            impact_assessment=impact_assessment,
            urgency_score=urgency_score,
            yield_impact_percent=impact_assessment.get('yield_impact_percent', 0),
            economic_impact_dollars_per_acre=impact_assessment.get('economic_impact', 0)
        )
    
    def _analyze_soil_test_deficiency(
        self,
        deficiency_type: DeficiencyType,
        crop_type: str,
        soil_test_data: SoilTestData
    ) -> Tuple[float, float]:
        """Analyze soil test data for specific deficiency."""
        
        thresholds = self.deficiency_thresholds.get(crop_type, {}).get('soil_test', {})
        nutrient_name = f"{deficiency_type.value}_ppm"
        
        if nutrient_name not in thresholds:
            return 0.0, 0.0
        
        # Get soil test value
        soil_value = getattr(soil_test_data, nutrient_name, None)
        if soil_value is None:
            return 0.0, 0.0
        
        nutrient_thresholds = thresholds[nutrient_name]
        
        # Calculate severity score (0-100)
        if soil_value <= nutrient_thresholds['severe']:
            severity = 90 + (nutrient_thresholds['severe'] - soil_value) / nutrient_thresholds['severe'] * 10
        elif soil_value <= nutrient_thresholds['moderate']:
            severity = 60 + (nutrient_thresholds['moderate'] - soil_value) / (nutrient_thresholds['moderate'] - nutrient_thresholds['severe']) * 30
        elif soil_value <= nutrient_thresholds['mild']:
            severity = 30 + (nutrient_thresholds['mild'] - soil_value) / (nutrient_thresholds['mild'] - nutrient_thresholds['moderate']) * 30
        else:
            severity = max(0, 30 - (soil_value - nutrient_thresholds['mild']) / nutrient_thresholds['mild'] * 30)
        
        # Confidence is high for soil tests
        confidence = 0.9 if severity > 30 else 0.7
        
        return min(100, severity), confidence
    
    def _analyze_tissue_test_deficiency(
        self,
        deficiency_type: DeficiencyType,
        crop_type: str,
        tissue_test_data: Dict[str, float]
    ) -> Tuple[float, float]:
        """Analyze tissue test data for specific deficiency."""
        
        thresholds = self.deficiency_thresholds.get(crop_type, {}).get('tissue_test', {})
        
        # Map deficiency type to tissue test parameter
        if deficiency_type == DeficiencyType.NITROGEN:
            param_name = 'nitrogen_percent'
        elif deficiency_type == DeficiencyType.PHOSPHORUS:
            param_name = 'phosphorus_percent'
        elif deficiency_type == DeficiencyType.POTASSIUM:
            param_name = 'potassium_percent'
        else:
            param_name = f"{deficiency_type.value}_ppm"
        
        if param_name not in thresholds or param_name not in tissue_test_data:
            return 0.0, 0.0
        
        tissue_value = tissue_test_data[param_name]
        nutrient_thresholds = thresholds[param_name]
        
        # Calculate severity similar to soil test
        if tissue_value <= nutrient_thresholds['severe']:
            severity = 95
        elif tissue_value <= nutrient_thresholds['moderate']:
            severity = 70
        elif tissue_value <= nutrient_thresholds['mild']:
            severity = 40
        else:
            severity = 10
        
        # Tissue tests are very reliable for current plant status
        confidence = 0.95 if severity > 40 else 0.8
        
        return severity, confidence
    
    def _analyze_visual_symptoms(
        self,
        deficiency_type: DeficiencyType,
        visual_symptoms: List[str]
    ) -> Tuple[float, float]:
        """Analyze visual symptoms for specific deficiency."""
        
        symptom_data = self.symptom_database.get(deficiency_type, {})
        known_symptoms = symptom_data.get('visual_symptoms', [])
        
        if not known_symptoms:
            return 0.0, 0.0
        
        # Calculate symptom match score
        matches = 0
        total_symptoms = len(visual_symptoms)
        
        for symptom in visual_symptoms:
            symptom_lower = symptom.lower()
            for known_symptom in known_symptoms:
                if any(word in symptom_lower for word in known_symptom.lower().split()):
                    matches += 1
                    break
        
        if total_symptoms == 0:
            return 0.0, 0.0
        
        match_ratio = matches / total_symptoms
        severity = match_ratio * 80  # Visual symptoms can indicate up to 80% severity
        
        # Confidence depends on symptom specificity
        confidence = 0.6 if match_ratio > 0.5 else 0.4
        
        return severity, confidence
    
    async def _analyze_crop_images(
        self,
        deficiency_type: DeficiencyType,
        crop_images: List[str]
    ) -> Tuple[float, float]:
        """Analyze crop images for deficiency symptoms using AI."""
        
        # Simplified image analysis (in production, this would use computer vision models)
        if not crop_images:
            return 0.0, 0.0
        
        # Mock AI analysis results
        # In production, this would process actual images
        severity_scores = []
        confidence_scores = []
        
        for image_data in crop_images:
            # Simulate image analysis
            image_severity, image_confidence = self._mock_image_analysis(
                deficiency_type, image_data
            )
            severity_scores.append(image_severity)
            confidence_scores.append(image_confidence)
        
        if severity_scores:
            avg_severity = np.mean(severity_scores)
            avg_confidence = np.mean(confidence_scores)
            return avg_severity, avg_confidence
        
        return 0.0, 0.0
    
    def _mock_image_analysis(
        self,
        deficiency_type: DeficiencyType,
        image_data: str
    ) -> Tuple[float, float]:
        """Mock image analysis for demonstration."""
        
        # Simulate different deficiency detection rates
        detection_rates = {
            DeficiencyType.NITROGEN: 0.85,
            DeficiencyType.IRON: 0.90,
            DeficiencyType.ZINC: 0.75,
            DeficiencyType.POTASSIUM: 0.70,
            DeficiencyType.PHOSPHORUS: 0.65
        }
        
        base_confidence = detection_rates.get(deficiency_type, 0.60)
        
        # Simulate severity detection (random for demo)
        import random
        severity = random.uniform(20, 80)
        confidence = base_confidence * random.uniform(0.8, 1.0)
        
        return severity, confidence
    
    def _determine_severity_level(self, severity_score: float) -> DeficiencySeverity:
        """Determine severity level from numeric score."""
        
        if severity_score >= 80:
            return DeficiencySeverity.CRITICAL
        elif severity_score >= 60:
            return DeficiencySeverity.SEVERE
        elif severity_score >= 40:
            return DeficiencySeverity.MODERATE
        elif severity_score >= 20:
            return DeficiencySeverity.MILD
        else:
            return DeficiencySeverity.NONE
    
    def _calculate_deficiency_impact(
        self,
        deficiency_type: DeficiencyType,
        severity: DeficiencySeverity,
        crop_type: str
    ) -> Dict[str, float]:
        """Calculate impact of deficiency on yield and economics."""
        
        # Base yield impact by deficiency type and severity
        yield_impacts = {
            DeficiencyType.NITROGEN: {
                DeficiencySeverity.CRITICAL: 25.0,
                DeficiencySeverity.SEVERE: 15.0,
                DeficiencySeverity.MODERATE: 8.0,
                DeficiencySeverity.MILD: 3.0
            },
            DeficiencyType.PHOSPHORUS: {
                DeficiencySeverity.CRITICAL: 20.0,
                DeficiencySeverity.SEVERE: 12.0,
                DeficiencySeverity.MODERATE: 6.0,
                DeficiencySeverity.MILD: 2.0
            },
            DeficiencyType.POTASSIUM: {
                DeficiencySeverity.CRITICAL: 18.0,
                DeficiencySeverity.SEVERE: 10.0,
                DeficiencySeverity.MODERATE: 5.0,
                DeficiencySeverity.MILD: 2.0
            },
            DeficiencyType.IRON: {
                DeficiencySeverity.CRITICAL: 15.0,
                DeficiencySeverity.SEVERE: 8.0,
                DeficiencySeverity.MODERATE: 4.0,
                DeficiencySeverity.MILD: 1.0
            },
            DeficiencyType.ZINC: {
                DeficiencySeverity.CRITICAL: 12.0,
                DeficiencySeverity.SEVERE: 6.0,
                DeficiencySeverity.MODERATE: 3.0,
                DeficiencySeverity.MILD: 1.0
            }
        }
        
        yield_impact = yield_impacts.get(deficiency_type, {}).get(severity, 0.0)
        
        # Calculate economic impact (simplified)
        crop_values = {
            'corn': 4.25,  # $/bushel
            'soybean': 12.50,  # $/bushel
            'wheat': 6.80   # $/bushel
        }
        
        crop_yields = {
            'corn': 170,  # bu/acre
            'soybean': 50,  # bu/acre
            'wheat': 60   # bu/acre
        }
        
        crop_value = crop_values.get(crop_type, 5.0)
        expected_yield = crop_yields.get(crop_type, 100)
        
        yield_loss_bushels = expected_yield * (yield_impact / 100)
        economic_impact = yield_loss_bushels * crop_value
        
        return {
            'yield_impact_percent': yield_impact,
            'yield_loss_bushels_per_acre': yield_loss_bushels,
            'economic_impact': economic_impact,
            'quality_impact_percent': yield_impact * 0.5  # Quality often affected less than yield
        }
    
    def _calculate_urgency_score(
        self,
        deficiency_type: DeficiencyType,
        severity: DeficiencySeverity,
        crop_type: str,
        field_observations: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate urgency score for addressing deficiency."""
        
        # Base urgency by severity
        severity_urgency = {
            DeficiencySeverity.CRITICAL: 95,
            DeficiencySeverity.SEVERE: 80,
            DeficiencySeverity.MODERATE: 60,
            DeficiencySeverity.MILD: 30,
            DeficiencySeverity.NONE: 0
        }
        
        base_urgency = severity_urgency[severity]
        
        # Adjust for deficiency type (some are more time-sensitive)
        type_multipliers = {
            DeficiencyType.NITROGEN: 1.2,  # Quick response needed
            DeficiencyType.IRON: 1.1,      # Can worsen quickly
            DeficiencyType.ZINC: 1.0,      # Moderate urgency
            DeficiencyType.PHOSPHORUS: 0.9, # Slower response
            DeficiencyType.POTASSIUM: 0.8   # Can wait longer
        }
        
        urgency = base_urgency * type_multipliers.get(deficiency_type, 1.0)
        
        # Adjust for growth stage if available
        if field_observations and 'growth_stage' in field_observations:
            growth_stage = field_observations['growth_stage']
            if growth_stage in ['early_vegetative', 'reproductive']:
                urgency *= 1.2  # More critical during active growth
            elif growth_stage in ['maturity', 'harvest']:
                urgency *= 0.5  # Less critical near harvest
        
        return min(100, urgency)