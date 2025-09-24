"""
Visual Symptom Analyzer
Processes crop images and symptom descriptions for nutrient deficiency detection.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
import numpy as np
import re
from enum import Enum

from .nutrient_deficiency_detection_service import DeficiencyType, VisualSymptomAnalysis


class SymptomLocation(Enum):
    """Locations where symptoms can appear."""
    OLDER_LEAVES = "older_leaves"
    YOUNGER_LEAVES = "younger_leaves"
    NEW_GROWTH = "new_growth"
    LEAF_MARGINS = "leaf_margins"
    LEAF_VEINS = "leaf_veins"
    STEMS = "stems"
    ROOTS = "roots"
    WHOLE_PLANT = "whole_plant"


class SymptomPattern(Enum):
    """Patterns of symptom distribution."""
    UNIFORM = "uniform"
    PATCHY = "patchy"
    LOCALIZED = "localized"
    PROGRESSIVE = "progressive"
    RANDOM = "random"


@dataclass
class SymptomMatch:
    """Match between observed and known symptoms."""
    deficiency_type: DeficiencyType
    symptom_description: str
    match_confidence: float
    severity_indicator: float
    location_match: bool
    timing_match: bool


class VisualSymptomAnalyzer:
    """Analyzes visual symptoms from descriptions and images."""
    
    def __init__(self):
        self.symptom_keywords = self._initialize_symptom_keywords()
        self.severity_indicators = self._initialize_severity_indicators()
        self.location_patterns = self._initialize_location_patterns()
    
    def _initialize_symptom_keywords(self) -> Dict[DeficiencyType, Dict[str, List[str]]]:
        """Initialize keyword patterns for symptom recognition."""
        return {
            DeficiencyType.NITROGEN: {
                'primary_keywords': [
                    'yellow', 'yellowing', 'pale', 'light green', 'chlorotic',
                    'stunted', 'small', 'reduced growth', 'poor vigor'
                ],
                'location_keywords': ['older leaves', 'bottom leaves', 'lower leaves'],
                'pattern_keywords': ['uniform', 'even', 'gradual', 'v-shaped'],
                'progression_keywords': ['starts bottom', 'moves up', 'older first']
            },
            DeficiencyType.PHOSPHORUS: {
                'primary_keywords': [
                    'purple', 'purpling', 'reddish', 'dark green', 'delayed',
                    'slow growth', 'poor root', 'late maturity'
                ],
                'location_keywords': ['older leaves', 'stems', 'leaf undersides'],
                'pattern_keywords': ['purple tinge', 'reddish coloration'],
                'progression_keywords': ['early season', 'cool weather']
            },
            DeficiencyType.POTASSIUM: {
                'primary_keywords': [
                    'burn', 'scorched', 'brown edges', 'marginal burn',
                    'yellowing between veins', 'weak stems', 'lodging'
                ],
                'location_keywords': ['leaf margins', 'leaf edges', 'older leaves'],
                'pattern_keywords': ['marginal', 'edge burn', 'interveinal'],
                'progression_keywords': ['mid season', 'grain fill', 'stress periods']
            },
            DeficiencyType.IRON: {
                'primary_keywords': [
                    'interveinal chlorosis', 'yellow between veins', 'green veins',
                    'white leaves', 'bleached', 'striping'
                ],
                'location_keywords': ['young leaves', 'new growth', 'upper leaves'],
                'pattern_keywords': ['green veins', 'yellow tissue', 'striped'],
                'progression_keywords': ['young leaves first', 'new growth affected']
            },
            DeficiencyType.ZINC: {
                'primary_keywords': [
                    'white bud', 'striping', 'banding', 'shortened internodes',
                    'small leaves', 'rosetting', 'delayed maturity'
                ],
                'location_keywords': ['young leaves', 'growing points', 'new growth'],
                'pattern_keywords': ['white stripes', 'banding', 'shortened'],
                'progression_keywords': ['early season', 'cool soils', 'high pH']
            },
            DeficiencyType.MANGANESE: {
                'primary_keywords': [
                    'interveinal chlorosis', 'yellow spots', 'necrotic spots',
                    'brown spots', 'gray speck', 'marsh spot'
                ],
                'location_keywords': ['young leaves', 'middle leaves'],
                'pattern_keywords': ['spotted', 'interveinal', 'necrotic'],
                'progression_keywords': ['alkaline soils', 'wet conditions']
            },
            DeficiencyType.COPPER: {
                'primary_keywords': [
                    'wilting', 'blue-green', 'twisted leaves', 'necrosis',
                    'white tips', 'dieback'
                ],
                'location_keywords': ['leaf tips', 'young leaves'],
                'pattern_keywords': ['twisted', 'curled', 'necrotic tips'],
                'progression_keywords': ['organic soils', 'sandy soils']
            },
            DeficiencyType.BORON: {
                'primary_keywords': [
                    'brittle', 'cracked stems', 'hollow stems', 'poor pollination',
                    'corky', 'rough', 'deformed'
                ],
                'location_keywords': ['growing points', 'stems', 'reproductive parts'],
                'pattern_keywords': ['brittle', 'hollow', 'deformed'],
                'progression_keywords': ['reproductive stage', 'drought stress']
            }
        }
    
    def _initialize_severity_indicators(self) -> Dict[str, float]:
        """Initialize severity indicators based on symptom descriptions."""
        return {
            # Mild indicators (20-40% severity)
            'slight': 25, 'minor': 25, 'beginning': 30, 'early': 30,
            'light': 35, 'faint': 30, 'subtle': 25,
            
            # Moderate indicators (40-70% severity)
            'moderate': 55, 'noticeable': 50, 'visible': 45, 'clear': 50,
            'obvious': 55, 'distinct': 60, 'pronounced': 65,
            
            # Severe indicators (70-90% severity)
            'severe': 80, 'heavy': 85, 'intense': 85, 'strong': 75,
            'marked': 75, 'significant': 70, 'extensive': 80,
            
            # Critical indicators (90-100% severity)
            'extreme': 95, 'complete': 100, 'total': 100, 'widespread': 90,
            'devastating': 95, 'critical': 90, 'massive': 95
        }
    
    def _initialize_location_patterns(self) -> Dict[DeficiencyType, Dict[str, float]]:
        """Initialize location pattern weights for deficiency types."""
        return {
            DeficiencyType.NITROGEN: {
                'older_leaves': 1.0, 'bottom_leaves': 1.0, 'lower_leaves': 1.0,
                'younger_leaves': 0.2, 'new_growth': 0.1
            },
            DeficiencyType.PHOSPHORUS: {
                'older_leaves': 1.0, 'stems': 0.8, 'whole_plant': 0.9,
                'younger_leaves': 0.3
            },
            DeficiencyType.POTASSIUM: {
                'older_leaves': 1.0, 'leaf_margins': 1.0, 'leaf_edges': 1.0,
                'younger_leaves': 0.3
            },
            DeficiencyType.IRON: {
                'younger_leaves': 1.0, 'new_growth': 1.0, 'upper_leaves': 1.0,
                'older_leaves': 0.2
            },
            DeficiencyType.ZINC: {
                'younger_leaves': 1.0, 'new_growth': 1.0, 'growing_points': 1.0,
                'older_leaves': 0.1
            }
        }
    
    async def analyze_symptom_description(
        self,
        symptom_description: str,
        crop_type: str,
        growth_stage: Optional[str] = None,
        environmental_conditions: Optional[Dict[str, Any]] = None
    ) -> VisualSymptomAnalysis:
        """Analyze natural language symptom description."""
        
        # Clean and normalize description
        description = symptom_description.lower().strip()
        
        # Extract symptom matches for each deficiency type
        symptom_matches = []
        for deficiency_type in DeficiencyType:
            match = self._match_symptoms_to_deficiency(
                description, deficiency_type, growth_stage, environmental_conditions
            )
            if match.match_confidence > 0.2:
                symptom_matches.append(match)
        
        # Sort by confidence
        symptom_matches.sort(key=lambda x: x.match_confidence, reverse=True)
        
        # Extract detected symptoms
        detected_symptoms = self._extract_symptom_list(description)
        
        # Analyze symptom severity
        symptom_severity = self._analyze_symptom_severity(description, symptom_matches)
        
        # Identify affected plant parts
        affected_parts = self._identify_affected_parts(description)
        
        # Determine symptom distribution pattern
        distribution = self._determine_distribution_pattern(description)
        
        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(symptom_matches)
        
        # Generate alternative diagnoses
        alternative_diagnoses = self._generate_alternative_diagnoses(
            symptom_matches, crop_type, environmental_conditions
        )
        
        return VisualSymptomAnalysis(
            detected_symptoms=detected_symptoms,
            symptom_severity=symptom_severity,
            affected_plant_parts=affected_parts,
            symptom_distribution=distribution,
            confidence_score=overall_confidence,
            alternative_diagnoses=alternative_diagnoses
        )
    
    def _match_symptoms_to_deficiency(
        self,
        description: str,
        deficiency_type: DeficiencyType,
        growth_stage: Optional[str],
        environmental_conditions: Optional[Dict[str, Any]]
    ) -> SymptomMatch:
        """Match symptom description to specific deficiency type."""
        
        keywords = self.symptom_keywords.get(deficiency_type, {})
        
        # Check primary symptom keywords
        primary_matches = 0
        primary_keywords = keywords.get('primary_keywords', [])
        for keyword in primary_keywords:
            if keyword in description:
                primary_matches += 1
        
        primary_score = min(1.0, primary_matches / max(1, len(primary_keywords) * 0.3))
        
        # Check location keywords
        location_matches = 0
        location_keywords = keywords.get('location_keywords', [])
        for keyword in location_keywords:
            if keyword in description:
                location_matches += 1
        
        location_score = min(1.0, location_matches / max(1, len(location_keywords)))
        
        # Check pattern keywords
        pattern_matches = 0
        pattern_keywords = keywords.get('pattern_keywords', [])
        for keyword in pattern_keywords:
            if keyword in description:
                pattern_matches += 1
        
        pattern_score = min(1.0, pattern_matches / max(1, len(pattern_keywords)))
        
        # Check timing/progression keywords
        timing_matches = 0
        timing_keywords = keywords.get('progression_keywords', [])
        for keyword in timing_keywords:
            if keyword in description:
                timing_matches += 1
        
        timing_score = min(1.0, timing_matches / max(1, len(timing_keywords)))
        
        # Calculate overall match confidence
        match_confidence = (
            primary_score * 0.4 +
            location_score * 0.25 +
            pattern_score * 0.2 +
            timing_score * 0.15
        )
        
        # Adjust for growth stage compatibility
        if growth_stage:
            stage_compatibility = self._check_growth_stage_compatibility(
                deficiency_type, growth_stage
            )
            match_confidence *= stage_compatibility
        
        # Adjust for environmental conditions
        if environmental_conditions:
            env_compatibility = self._check_environmental_compatibility(
                deficiency_type, environmental_conditions
            )
            match_confidence *= env_compatibility
        
        # Extract severity indicators
        severity_indicator = self._extract_severity_from_description(description)
        
        return SymptomMatch(
            deficiency_type=deficiency_type,
            symptom_description=description,
            match_confidence=match_confidence,
            severity_indicator=severity_indicator,
            location_match=location_score > 0.5,
            timing_match=timing_score > 0.3
        )
    
    def _extract_symptom_list(self, description: str) -> List[str]:
        """Extract individual symptoms from description."""
        
        # Common symptom patterns
        symptom_patterns = [
            r'yellow\w*', r'brown\w*', r'purple\w*', r'white\w*',
            r'chlorot\w*', r'necrot\w*', r'burn\w*', r'scorch\w*',
            r'stunt\w*', r'wilt\w*', r'curl\w*', r'twist\w*',
            r'strip\w*', r'spot\w*', r'margin\w*', r'interveinal'
        ]
        
        detected_symptoms = []
        for pattern in symptom_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            detected_symptoms.extend(matches)
        
        # Remove duplicates and normalize
        unique_symptoms = list(set([symptom.lower() for symptom in detected_symptoms]))
        
        return unique_symptoms
    
    def _analyze_symptom_severity(
        self,
        description: str,
        symptom_matches: List[SymptomMatch]
    ) -> Dict[str, float]:
        """Analyze severity of symptoms from description."""
        
        severity_dict = {}
        
        # Extract severity indicators from text
        base_severity = self._extract_severity_from_description(description)
        
        # Assign severity to each matched deficiency
        for match in symptom_matches:
            if match.match_confidence > 0.3:
                # Adjust base severity by match confidence
                adjusted_severity = base_severity * match.match_confidence
                severity_dict[match.deficiency_type.value] = adjusted_severity
        
        return severity_dict
    
    def _extract_severity_from_description(self, description: str) -> float:
        """Extract severity level from text description."""
        
        severity_score = 50.0  # Default moderate severity
        
        # Check for severity indicators
        for indicator, score in self.severity_indicators.items():
            if indicator in description:
                severity_score = max(severity_score, score)
        
        # Check for percentage indicators
        percentage_pattern = r'(\d+)%'
        percentages = re.findall(percentage_pattern, description)
        if percentages:
            # Use the highest percentage found
            max_percentage = max([int(p) for p in percentages])
            severity_score = max(severity_score, max_percentage)
        
        # Check for area coverage indicators
        area_indicators = {
            'few': 20, 'some': 35, 'many': 60, 'most': 80, 'all': 95,
            'scattered': 30, 'widespread': 85, 'throughout': 90
        }
        
        for indicator, score in area_indicators.items():
            if indicator in description:
                severity_score = max(severity_score, score)
        
        return min(100, severity_score)
    
    def _identify_affected_parts(self, description: str) -> List[str]:
        """Identify which plant parts are affected."""
        
        plant_parts = {
            'leaves': ['leaf', 'leaves', 'foliage'],
            'older_leaves': ['older leaves', 'bottom leaves', 'lower leaves'],
            'younger_leaves': ['younger leaves', 'new leaves', 'upper leaves'],
            'stems': ['stem', 'stems', 'stalk', 'stalks'],
            'roots': ['root', 'roots'],
            'growing_points': ['growing point', 'growing tip', 'bud', 'buds'],
            'leaf_margins': ['margin', 'margins', 'edge', 'edges', 'border'],
            'veins': ['vein', 'veins', 'vascular']
        }
        
        affected_parts = []
        for part_name, keywords in plant_parts.items():
            for keyword in keywords:
                if keyword in description:
                    affected_parts.append(part_name)
                    break
        
        return list(set(affected_parts))
    
    def _determine_distribution_pattern(self, description: str) -> str:
        """Determine the distribution pattern of symptoms."""
        
        pattern_indicators = {
            'uniform': ['uniform', 'even', 'consistent', 'throughout'],
            'patchy': ['patchy', 'patches', 'spots', 'scattered', 'random'],
            'localized': ['localized', 'specific area', 'one area', 'confined'],
            'progressive': ['progressive', 'spreading', 'advancing', 'moving'],
            'marginal': ['margin', 'edge', 'border', 'perimeter']
        }
        
        for pattern, indicators in pattern_indicators.items():
            for indicator in indicators:
                if indicator in description:
                    return pattern
        
        return 'unknown'
    
    def _calculate_overall_confidence(self, symptom_matches: List[SymptomMatch]) -> float:
        """Calculate overall confidence in symptom analysis."""
        
        if not symptom_matches:
            return 0.0
        
        # Weight by match confidence
        weighted_confidence = sum(
            match.match_confidence for match in symptom_matches[:3]  # Top 3 matches
        ) / min(3, len(symptom_matches))
        
        # Adjust for number of matches
        match_bonus = min(0.2, len(symptom_matches) * 0.05)
        
        return min(1.0, weighted_confidence + match_bonus)
    
    def _generate_alternative_diagnoses(
        self,
        symptom_matches: List[SymptomMatch],
        crop_type: str,
        environmental_conditions: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Generate alternative diagnoses beyond nutrient deficiencies."""
        
        alternatives = []
        
        # Check for disease symptoms that might be confused with deficiencies
        if any('spot' in match.symptom_description for match in symptom_matches):
            alternatives.append('fungal_leaf_spot_disease')
        
        if any('wilt' in match.symptom_description for match in symptom_matches):
            alternatives.append('root_rot_or_vascular_disease')
        
        # Check for environmental stress
        if environmental_conditions:
            if environmental_conditions.get('drought_stress'):
                alternatives.append('drought_stress')
            
            if environmental_conditions.get('temperature_stress'):
                alternatives.append('temperature_stress')
            
            if environmental_conditions.get('herbicide_application'):
                alternatives.append('herbicide_injury')
        
        # Check for pest damage
        if any('damage' in match.symptom_description for match in symptom_matches):
            alternatives.append('insect_or_pest_damage')
        
        return alternatives
    
    def _check_growth_stage_compatibility(
        self,
        deficiency_type: DeficiencyType,
        growth_stage: str
    ) -> float:
        """Check if deficiency timing matches growth stage."""
        
        # Growth stage compatibility for different deficiencies
        stage_compatibility = {
            DeficiencyType.NITROGEN: {
                'early_vegetative': 1.0,
                'mid_vegetative': 1.0,
                'reproductive': 0.8,
                'maturity': 0.3
            },
            DeficiencyType.PHOSPHORUS: {
                'early_vegetative': 1.0,
                'mid_vegetative': 0.8,
                'reproductive': 0.6,
                'maturity': 0.2
            },
            DeficiencyType.POTASSIUM: {
                'early_vegetative': 0.6,
                'mid_vegetative': 0.8,
                'reproductive': 1.0,
                'maturity': 0.9
            },
            DeficiencyType.IRON: {
                'early_vegetative': 1.0,
                'mid_vegetative': 0.9,
                'reproductive': 0.7,
                'maturity': 0.3
            }
        }
        
        return stage_compatibility.get(deficiency_type, {}).get(growth_stage, 0.8)
    
    def _check_environmental_compatibility(
        self,
        deficiency_type: DeficiencyType,
        environmental_conditions: Dict[str, Any]
    ) -> float:
        """Check environmental condition compatibility with deficiency."""
        
        compatibility = 1.0
        
        # Iron deficiency more likely in high pH, wet conditions
        if deficiency_type == DeficiencyType.IRON:
            if environmental_conditions.get('soil_ph', 7.0) > 7.5:
                compatibility *= 1.2
            if environmental_conditions.get('wet_conditions'):
                compatibility *= 1.1
        
        # Zinc deficiency more likely in high pH, cool conditions
        if deficiency_type == DeficiencyType.ZINC:
            if environmental_conditions.get('soil_ph', 7.0) > 7.0:
                compatibility *= 1.2
            if environmental_conditions.get('cool_temperatures'):
                compatibility *= 1.1
        
        # Phosphorus deficiency more likely in cool, wet conditions
        if deficiency_type == DeficiencyType.PHOSPHORUS:
            if environmental_conditions.get('cool_temperatures'):
                compatibility *= 1.2
            if environmental_conditions.get('wet_conditions'):
                compatibility *= 1.1
        
        return min(1.5, compatibility)


class CropImageAnalyzer:
    """Analyzes crop images for nutrient deficiency symptoms."""
    
    def __init__(self):
        self.image_quality_thresholds = {
            'min_resolution': (640, 480),
            'max_blur_score': 0.3,
            'min_brightness': 50,
            'max_brightness': 200
        }
    
    async def analyze_crop_image(
        self,
        image_data: str,  # base64 encoded
        crop_type: str,
        suspected_deficiencies: Optional[List[DeficiencyType]] = None
    ) -> Dict[str, Any]:
        """Analyze crop image for deficiency symptoms."""
        
        # In production, this would use computer vision models
        # For now, we'll simulate the analysis
        
        analysis_result = {
            'image_quality_score': 0.85,
            'detected_symptoms': [],
            'deficiency_probabilities': {},
            'confidence_scores': {},
            'affected_areas': [],
            'severity_assessment': {},
            'recommendations': []
        }
        
        # Simulate deficiency detection
        if suspected_deficiencies:
            for deficiency in suspected_deficiencies:
                # Mock detection results
                probability = np.random.uniform(0.3, 0.9)
                confidence = np.random.uniform(0.6, 0.95)
                
                analysis_result['deficiency_probabilities'][deficiency.value] = probability
                analysis_result['confidence_scores'][deficiency.value] = confidence
                
                if probability > 0.6:
                    analysis_result['detected_symptoms'].append(f"{deficiency.value}_symptoms")
        
        return analysis_result
    
    def assess_image_quality(self, image_data: str) -> Dict[str, Any]:
        """Assess image quality for analysis suitability."""
        
        # Mock image quality assessment
        quality_assessment = {
            'overall_quality': 'good',
            'resolution_adequate': True,
            'lighting_adequate': True,
            'focus_adequate': True,
            'angle_appropriate': True,
            'quality_score': 0.85,
            'improvement_suggestions': []
        }
        
        # Add suggestions if quality is poor
        if quality_assessment['quality_score'] < 0.7:
            quality_assessment['improvement_suggestions'] = [
                'Ensure adequate lighting',
                'Hold camera steady for sharp focus',
                'Capture from multiple angles',
                'Include affected and healthy areas for comparison'
            ]
        
        return quality_assessment