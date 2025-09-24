"""
Visual Symptom Analyzer Service
Analyzes crop photos and symptom descriptions to detect nutrient deficiencies.
Provides computer vision capabilities and symptom pattern matching.
"""
import asyncio
import base64
import io
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import numpy as np
from PIL import Image
import cv2

class SymptomType(Enum):
    """Types of visual symptoms."""
    CHLOROSIS = "chlorosis"  # Yellowing
    NECROSIS = "necrosis"  # Browning/death
    STUNTING = "stunting"  # Reduced growth
    DISCOLORATION = "discoloration"  # Color changes
    DEFORMATION = "deformation"  # Shape changes
    WILTING = "wilting"  # Water stress appearance

class PlantPart(Enum):
    """Plant parts affected by symptoms."""
    OLDER_LEAVES = "older_leaves"
    YOUNGER_LEAVES = "younger_leaves"
    LEAF_MARGINS = "leaf_margins"
    LEAF_VEINS = "leaf_veins"
    INTERVEINAL = "interveinal"
    STEMS = "stems"
    ROOTS = "roots"
    WHOLE_PLANT = "whole_plant"

@dataclass
class VisualSymptom:
    """Visual symptom detected from image or description."""
    symptom_id: str
    symptom_type: SymptomType
    plant_part: PlantPart
    severity: str  # mild, moderate, severe
    distribution: str  # uniform, patchy, marginal, etc.
    color_description: str
    confidence_score: float
    associated_nutrients: List[str]
    description: str
    image_coordinates: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height

@dataclass
class ImageAnalysisResult:
    """Result of image analysis for nutrient deficiencies."""
    analysis_id: str
    image_quality_score: float
    detected_symptoms: List[VisualSymptom]
    crop_identification: str
    growth_stage: str
    environmental_factors: List[str]
    deficiency_predictions: List[Dict[str, Any]]
    confidence_level: float
    recommendations: List[str]

@dataclass
class SymptomPattern:
    """Pattern definition for symptom matching."""
    nutrient: str
    crop_type: str
    primary_symptoms: List[str]
    secondary_symptoms: List[str]
    distinguishing_features: List[str]
    affected_plant_parts: List[PlantPart]
    symptom_progression: str
    confidence_weight: float

class VisualSymptomAnalyzer:
    """Service for analyzing visual symptoms of nutrient deficiencies."""
    
    def __init__(self):
        self.symptom_patterns = self._initialize_symptom_patterns()
        self.color_analysis_thresholds = self._initialize_color_thresholds()
        self.crop_characteristics = self._initialize_crop_characteristics()
        
    def _initialize_symptom_patterns(self) -> Dict[str, List[SymptomPattern]]:
        """Initialize symptom pattern database."""
        return {
            'nitrogen': [
                SymptomPattern(
                    nutrient='nitrogen',
                    crop_type='corn',
                    primary_symptoms=[
                        'yellowing of older leaves first',
                        'pale green coloration overall',
                        'stunted growth',
                        'V-shaped yellowing pattern'
                    ],
                    secondary_symptoms=[
                        'reduced tillering',
                        'delayed maturity',
                        'smaller plant size'
                    ],
                    distinguishing_features=[
                        'starts with older leaves',
                        'uniform yellowing',
                        'affects whole plant eventually'
                    ],
                    affected_plant_parts=[PlantPart.OLDER_LEAVES, PlantPart.WHOLE_PLANT],
                    symptom_progression='bottom_to_top',
                    confidence_weight=0.9
                ),
                SymptomPattern(
                    nutrient='nitrogen',
                    crop_type='soybean',
                    primary_symptoms=[
                        'yellowing of lower leaves',
                        'pale green upper leaves',
                        'reduced plant vigor'
                    ],
                    secondary_symptoms=[
                        'fewer pods',
                        'smaller seeds',
                        'early senescence'
                    ],
                    distinguishing_features=[
                        'lower leaf yellowing first',
                        'overall pale appearance'
                    ],
                    affected_plant_parts=[PlantPart.OLDER_LEAVES, PlantPart.WHOLE_PLANT],
                    symptom_progression='bottom_to_top',
                    confidence_weight=0.85
                )
            ],
            'phosphorus': [
                SymptomPattern(
                    nutrient='phosphorus',
                    crop_type='corn',
                    primary_symptoms=[
                        'purplish discoloration of leaves',
                        'reddish coloration on leaf undersides',
                        'delayed growth and maturity'
                    ],
                    secondary_symptoms=[
                        'poor root development',
                        'delayed tasseling',
                        'reduced kernel set'
                    ],
                    distinguishing_features=[
                        'purple/red coloration',
                        'especially on cool days',
                        'affects young plants more'
                    ],
                    affected_plant_parts=[PlantPart.YOUNGER_LEAVES, PlantPart.STEMS],
                    symptom_progression='whole_plant',
                    confidence_weight=0.8
                )
            ],
            'potassium': [
                SymptomPattern(
                    nutrient='potassium',
                    crop_type='corn',
                    primary_symptoms=[
                        'yellowing and browning of leaf margins',
                        'scorched appearance of leaf edges',
                        'weak, lodging-prone stems'
                    ],
                    secondary_symptoms=[
                        'poor grain fill',
                        'increased disease susceptibility',
                        'premature leaf death'
                    ],
                    distinguishing_features=[
                        'marginal leaf burn',
                        'fire-like appearance',
                        'older leaves affected first'
                    ],
                    affected_plant_parts=[PlantPart.LEAF_MARGINS, PlantPart.OLDER_LEAVES],
                    symptom_progression='margin_to_center',
                    confidence_weight=0.85
                )
            ],
            'iron': [
                SymptomPattern(
                    nutrient='iron',
                    crop_type='corn',
                    primary_symptoms=[
                        'interveinal chlorosis of young leaves',
                        'yellowing between leaf veins',
                        'white or pale yellow new growth'
                    ],
                    secondary_symptoms=[
                        'stunted growth',
                        'poor tillering',
                        'delayed maturity'
                    ],
                    distinguishing_features=[
                        'veins remain green',
                        'affects young leaves first',
                        'striped appearance'
                    ],
                    affected_plant_parts=[PlantPart.YOUNGER_LEAVES, PlantPart.INTERVEINAL],
                    symptom_progression='top_to_bottom',
                    confidence_weight=0.9
                )
            ],
            'zinc': [
                SymptomPattern(
                    nutrient='zinc',
                    crop_type='corn',
                    primary_symptoms=[
                        'white or yellow stripes between veins',
                        'shortened internodes',
                        'small, narrow leaves'
                    ],
                    secondary_symptoms=[
                        'rosetting growth pattern',
                        'delayed maturity',
                        'poor ear development'
                    ],
                    distinguishing_features=[
                        'white striping pattern',
                        'banding appearance',
                        'affects young tissue'
                    ],
                    affected_plant_parts=[PlantPart.YOUNGER_LEAVES, PlantPart.INTERVEINAL],
                    symptom_progression='whole_plant',
                    confidence_weight=0.85
                )
            ],
            'manganese': [
                SymptomPattern(
                    nutrient='manganese',
                    crop_type='soybean',
                    primary_symptoms=[
                        'interveinal chlorosis of young leaves',
                        'gray or brown necrotic spots',
                        'poor seed development'
                    ],
                    secondary_symptoms=[
                        'reduced nodulation',
                        'delayed maturity',
                        'lower yields'
                    ],
                    distinguishing_features=[
                        'similar to iron but with necrotic spots',
                        'affects young leaves',
                        'more common in high pH soils'
                    ],
                    affected_plant_parts=[PlantPart.YOUNGER_LEAVES, PlantPart.INTERVEINAL],
                    symptom_progression='young_to_old',
                    confidence_weight=0.75
                )
            ]
        }
    
    def _initialize_color_thresholds(self) -> Dict[str, Dict[str, Any]]:
        """Initialize color analysis thresholds for symptom detection."""
        return {
            'chlorosis': {
                'hue_range': (20, 60),  # Yellow range in HSV
                'saturation_min': 0.3,
                'value_min': 0.4
            },
            'necrosis': {
                'hue_range': (10, 25),  # Brown range in HSV
                'saturation_min': 0.2,
                'value_max': 0.6
            },
            'healthy_green': {
                'hue_range': (60, 120),  # Green range in HSV
                'saturation_min': 0.4,
                'value_min': 0.3
            },
            'purple_discoloration': {
                'hue_range': (270, 330),  # Purple range in HSV
                'saturation_min': 0.3,
                'value_min': 0.2
            }
        }
    
    def _initialize_crop_characteristics(self) -> Dict[str, Dict[str, Any]]:
        """Initialize crop-specific characteristics for analysis."""
        return {
            'corn': {
                'leaf_shape': 'linear',
                'venation': 'parallel',
                'growth_habit': 'upright',
                'typical_green_hue': (80, 120),
                'deficiency_susceptibility': {
                    'nitrogen': 'high',
                    'potassium': 'high',
                    'iron': 'moderate',
                    'zinc': 'high'
                }
            },
            'soybean': {
                'leaf_shape': 'trifoliate',
                'venation': 'pinnate',
                'growth_habit': 'bushy',
                'typical_green_hue': (70, 110),
                'deficiency_susceptibility': {
                    'nitrogen': 'moderate',  # Can fix nitrogen
                    'potassium': 'high',
                    'iron': 'high',
                    'manganese': 'high'
                }
            },
            'wheat': {
                'leaf_shape': 'linear',
                'venation': 'parallel',
                'growth_habit': 'tillering',
                'typical_green_hue': (75, 115),
                'deficiency_susceptibility': {
                    'nitrogen': 'high',
                    'phosphorus': 'moderate',
                    'potassium': 'moderate'
                }
            }
        }
    
    async def analyze_crop_image(
        self,
        image_data: bytes,
        crop_type: str,
        growth_stage: Optional[str] = None,
        field_conditions: Optional[Dict[str, Any]] = None
    ) -> ImageAnalysisResult:
        """Analyze crop image for nutrient deficiency symptoms."""
        
        analysis_id = f"img_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Load and preprocess image
        image = self._load_image_from_bytes(image_data)
        if image is None:
            return self._create_error_result(analysis_id, "Invalid image data")
        
        # Assess image quality
        quality_score = self._assess_image_quality(image)
        if quality_score < 0.3:
            return self._create_error_result(analysis_id, "Poor image quality")
        
        # Detect crop and growth stage if not provided
        if not crop_type:
            crop_type = await self._identify_crop(image)
        if not growth_stage:
            growth_stage = await self._identify_growth_stage(image, crop_type)
        
        # Detect visual symptoms
        detected_symptoms = await self._detect_visual_symptoms(image, crop_type)
        
        # Analyze environmental factors
        environmental_factors = self._analyze_environmental_factors(image, field_conditions)
        
        # Predict nutrient deficiencies
        deficiency_predictions = await self._predict_deficiencies_from_symptoms(
            detected_symptoms, crop_type, growth_stage
        )
        
        # Calculate overall confidence
        confidence_level = self._calculate_analysis_confidence(
            detected_symptoms, quality_score, deficiency_predictions
        )
        
        # Generate recommendations
        recommendations = self._generate_image_analysis_recommendations(
            deficiency_predictions, detected_symptoms
        )
        
        return ImageAnalysisResult(
            analysis_id=analysis_id,
            image_quality_score=quality_score,
            detected_symptoms=detected_symptoms,
            crop_identification=crop_type,
            growth_stage=growth_stage,
            environmental_factors=environmental_factors,
            deficiency_predictions=deficiency_predictions,
            confidence_level=confidence_level,
            recommendations=recommendations
        )
    
    def _load_image_from_bytes(self, image_data: bytes) -> Optional[np.ndarray]:
        """Load image from bytes data."""
        try:
            # Convert bytes to PIL Image
            image_pil = Image.open(io.BytesIO(image_data))
            # Convert to RGB if necessary
            if image_pil.mode != 'RGB':
                image_pil = image_pil.convert('RGB')
            # Convert to numpy array for OpenCV
            image_np = np.array(image_pil)
            # Convert RGB to BGR for OpenCV
            image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
            return image_bgr
        except Exception as e:
            print(f"Error loading image: {e}")
            return None
    
    def _assess_image_quality(self, image: np.ndarray) -> float:
        """Assess image quality for analysis suitability."""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate sharpness using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, laplacian_var / 1000.0)  # Normalize
            
            # Calculate brightness
            mean_brightness = np.mean(gray) / 255.0
            brightness_score = 1.0 - abs(mean_brightness - 0.5) * 2  # Optimal around 0.5
            
            # Calculate contrast
            contrast = np.std(gray) / 255.0
            contrast_score = min(1.0, contrast * 4)  # Normalize
            
            # Check for motion blur (simplified)
            motion_blur_score = min(1.0, laplacian_var / 500.0)
            
            # Overall quality score
            quality_score = (sharpness_score * 0.4 + 
                           brightness_score * 0.2 + 
                           contrast_score * 0.2 + 
                           motion_blur_score * 0.2)
            
            return max(0.0, min(1.0, quality_score))
        
        except Exception as e:
            print(f"Error assessing image quality: {e}")
            return 0.0
    
    async def _identify_crop(self, image: np.ndarray) -> str:
        """Identify crop type from image (simplified implementation)."""
        # This would typically use a trained ML model
        # For now, return a default based on leaf characteristics
        
        # Analyze leaf shape and structure (simplified)
        # In production, this would use computer vision models
        return 'corn'  # Default assumption
    
    async def _identify_growth_stage(self, image: np.ndarray, crop_type: str) -> str:
        """Identify crop growth stage from image."""
        # This would typically analyze plant size, leaf count, reproductive structures
        # For now, return a general stage
        return 'vegetative'  # Default assumption
    
    async def _detect_visual_symptoms(
        self, 
        image: np.ndarray, 
        crop_type: str
    ) -> List[VisualSymptom]:
        """Detect visual symptoms in the crop image."""
        symptoms = []
        
        # Convert to HSV for better color analysis
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Detect chlorosis (yellowing)
        chlorosis_symptoms = self._detect_chlorosis(hsv_image, crop_type)
        symptoms.extend(chlorosis_symptoms)
        
        # Detect necrosis (browning)
        necrosis_symptoms = self._detect_necrosis(hsv_image, crop_type)
        symptoms.extend(necrosis_symptoms)
        
        # Detect interveinal patterns
        interveinal_symptoms = self._detect_interveinal_patterns(hsv_image, crop_type)
        symptoms.extend(interveinal_symptoms)
        
        # Detect marginal symptoms
        marginal_symptoms = self._detect_marginal_symptoms(hsv_image, crop_type)
        symptoms.extend(marginal_symptoms)
        
        return symptoms
    
    def _detect_chlorosis(self, hsv_image: np.ndarray, crop_type: str) -> List[VisualSymptom]:
        """Detect chlorosis (yellowing) symptoms."""
        symptoms = []
        
        try:
            # Define yellow color range in HSV
            yellow_thresholds = self.color_analysis_thresholds['chlorosis']
            lower_yellow = np.array([yellow_thresholds['hue_range'][0], 
                                   int(yellow_thresholds['saturation_min'] * 255), 
                                   int(yellow_thresholds['value_min'] * 255)])
            upper_yellow = np.array([yellow_thresholds['hue_range'][1], 255, 255])
            
            # Create mask for yellow areas
            yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
            
            # Calculate percentage of yellow pixels
            total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
            yellow_pixels = np.sum(yellow_mask > 0)
            yellow_percentage = yellow_pixels / total_pixels
            
            if yellow_percentage > 0.05:  # More than 5% yellow pixels
                # Determine severity based on percentage
                if yellow_percentage > 0.3:
                    severity = "severe"
                elif yellow_percentage > 0.15:
                    severity = "moderate"
                else:
                    severity = "mild"
                
                # Find contours to determine distribution
                contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                # Analyze distribution pattern
                if len(contours) > 10:
                    distribution = "patchy"
                elif len(contours) > 3:
                    distribution = "scattered"
                else:
                    distribution = "uniform"
                
                # Create symptom
                symptom = VisualSymptom(
                    symptom_id=f"chlorosis_{datetime.now().strftime('%H%M%S')}",
                    symptom_type=SymptomType.CHLOROSIS,
                    plant_part=PlantPart.OLDER_LEAVES,  # Default assumption
                    severity=severity,
                    distribution=distribution,
                    color_description="yellowing of leaf tissue",
                    confidence_score=min(0.9, yellow_percentage * 3),  # Higher percentage = higher confidence
                    associated_nutrients=['nitrogen', 'iron', 'sulfur'],
                    description=f"Chlorosis detected covering {yellow_percentage:.1%} of visible plant tissue"
                )
                symptoms.append(symptom)
        
        except Exception as e:
            print(f"Error detecting chlorosis: {e}")
        
        return symptoms
    
    def _detect_necrosis(self, hsv_image: np.ndarray, crop_type: str) -> List[VisualSymptom]:
        """Detect necrosis (browning/death) symptoms."""
        symptoms = []
        
        try:
            # Define brown color range in HSV
            brown_thresholds = self.color_analysis_thresholds['necrosis']
            lower_brown = np.array([brown_thresholds['hue_range'][0], 
                                  int(brown_thresholds['saturation_min'] * 255), 0])
            upper_brown = np.array([brown_thresholds['hue_range'][1], 255, 
                                  int(brown_thresholds['value_max'] * 255)])
            
            # Create mask for brown areas
            brown_mask = cv2.inRange(hsv_image, lower_brown, upper_brown)
            
            # Calculate percentage of brown pixels
            total_pixels = hsv_image.shape[0] * hsv_image.shape[1]
            brown_pixels = np.sum(brown_mask > 0)
            brown_percentage = brown_pixels / total_pixels
            
            if brown_percentage > 0.02:  # More than 2% brown pixels
                # Determine severity
                if brown_percentage > 0.2:
                    severity = "severe"
                elif brown_percentage > 0.08:
                    severity = "moderate"
                else:
                    severity = "mild"
                
                # Create symptom
                symptom = VisualSymptom(
                    symptom_id=f"necrosis_{datetime.now().strftime('%H%M%S')}",
                    symptom_type=SymptomType.NECROSIS,
                    plant_part=PlantPart.LEAF_MARGINS,  # Common location for necrosis
                    severity=severity,
                    distribution="marginal",
                    color_description="brown/dead tissue",
                    confidence_score=min(0.85, brown_percentage * 5),
                    associated_nutrients=['potassium', 'magnesium', 'boron'],
                    description=f"Necrosis detected covering {brown_percentage:.1%} of visible plant tissue"
                )
                symptoms.append(symptom)
        
        except Exception as e:
            print(f"Error detecting necrosis: {e}")
        
        return symptoms
    
    def _detect_interveinal_patterns(self, hsv_image: np.ndarray, crop_type: str) -> List[VisualSymptom]:
        """Detect interveinal chlorosis patterns."""
        symptoms = []
        
        try:
            # This would require more sophisticated image processing
            # to detect the pattern between leaf veins
            # For now, we'll use a simplified approach
            
            # Convert to grayscale for edge detection
            gray = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)
            gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
            
            # Detect edges (veins)
            edges = cv2.Canny(gray, 50, 150)
            
            # If we can detect a pattern of edges (veins) with yellowing between them,
            # it might indicate interveinal chlorosis
            # This is a simplified implementation
            
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            if edge_density > 0.05:  # Sufficient vein structure detected
                # Check for yellowing in non-edge areas
                yellow_thresholds = self.color_analysis_thresholds['chlorosis']
                lower_yellow = np.array([yellow_thresholds['hue_range'][0], 
                                       int(yellow_thresholds['saturation_min'] * 255), 
                                       int(yellow_thresholds['value_min'] * 255)])
                upper_yellow = np.array([yellow_thresholds['hue_range'][1], 255, 255])
                
                yellow_mask = cv2.inRange(hsv_image, lower_yellow, upper_yellow)
                
                # Remove edge areas from yellow mask
                kernel = np.ones((3,3), np.uint8)
                edges_dilated = cv2.dilate(edges, kernel, iterations=1)
                interveinal_yellow = cv2.bitwise_and(yellow_mask, cv2.bitwise_not(edges_dilated))
                
                interveinal_percentage = np.sum(interveinal_yellow > 0) / (hsv_image.shape[0] * hsv_image.shape[1])
                
                if interveinal_percentage > 0.03:  # Significant interveinal yellowing
                    symptom = VisualSymptom(
                        symptom_id=f"interveinal_{datetime.now().strftime('%H%M%S')}",
                        symptom_type=SymptomType.CHLOROSIS,
                        plant_part=PlantPart.INTERVEINAL,
                        severity="moderate" if interveinal_percentage > 0.1 else "mild",
                        distribution="interveinal",
                        color_description="yellowing between leaf veins",
                        confidence_score=min(0.8, interveinal_percentage * 10),
                        associated_nutrients=['iron', 'zinc', 'manganese'],
                        description=f"Interveinal chlorosis pattern detected"
                    )
                    symptoms.append(symptom)
        
        except Exception as e:
            print(f"Error detecting interveinal patterns: {e}")
        
        return symptoms
    
    def _detect_marginal_symptoms(self, hsv_image: np.ndarray, crop_type: str) -> List[VisualSymptom]:
        """Detect marginal leaf symptoms (edge burning, etc.)."""
        symptoms = []
        
        try:
            # Create a mask for the outer edges of the image
            # This is a simplified approach - in production, you'd detect actual leaf edges
            height, width = hsv_image.shape[:2]
            
            # Create edge mask (outer 10% of image)
            edge_mask = np.zeros((height, width), dtype=np.uint8)
            edge_width = int(min(height, width) * 0.1)
            edge_mask[:edge_width, :] = 255  # Top edge
            edge_mask[-edge_width:, :] = 255  # Bottom edge
            edge_mask[:, :edge_width] = 255  # Left edge
            edge_mask[:, -edge_width:] = 255  # Right edge
            
            # Check for browning in edge areas
            brown_thresholds = self.color_analysis_thresholds['necrosis']
            lower_brown = np.array([brown_thresholds['hue_range'][0], 
                                  int(brown_thresholds['saturation_min'] * 255), 0])
            upper_brown = np.array([brown_thresholds['hue_range'][1], 255, 
                                  int(brown_thresholds['value_max'] * 255)])
            
            brown_mask = cv2.inRange(hsv_image, lower_brown, upper_brown)
            marginal_brown = cv2.bitwise_and(brown_mask, edge_mask)
            
            marginal_percentage = np.sum(marginal_brown > 0) / np.sum(edge_mask > 0)
            
            if marginal_percentage > 0.1:  # More than 10% of edges are brown
                symptom = VisualSymptom(
                    symptom_id=f"marginal_{datetime.now().strftime('%H%M%S')}",
                    symptom_type=SymptomType.NECROSIS,
                    plant_part=PlantPart.LEAF_MARGINS,
                    severity="severe" if marginal_percentage > 0.4 else "moderate",
                    distribution="marginal",
                    color_description="browning of leaf margins",
                    confidence_score=min(0.9, marginal_percentage * 2),
                    associated_nutrients=['potassium', 'magnesium'],
                    description=f"Marginal leaf burn detected"
                )
                symptoms.append(symptom)
        
        except Exception as e:
            print(f"Error detecting marginal symptoms: {e}")
        
        return symptoms
    
    def _analyze_environmental_factors(
        self, 
        image: np.ndarray, 
        field_conditions: Optional[Dict[str, Any]]
    ) -> List[str]:
        """Analyze environmental factors that might affect symptom interpretation."""
        factors = []
        
        # Analyze lighting conditions
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        if mean_brightness < 80:
            factors.append("low_light_conditions")
        elif mean_brightness > 200:
            factors.append("overexposed_lighting")
        
        # Check for shadows
        std_brightness = np.std(gray)
        if std_brightness > 60:
            factors.append("uneven_lighting_shadows")
        
        # Add field conditions if provided
        if field_conditions:
            if field_conditions.get('recent_rain'):
                factors.append("recent_moisture")
            if field_conditions.get('drought_stress'):
                factors.append("drought_conditions")
            if field_conditions.get('temperature_stress'):
                factors.append("temperature_stress")
        
        return factors
    
    async def _predict_deficiencies_from_symptoms(
        self,
        symptoms: List[VisualSymptom],
        crop_type: str,
        growth_stage: str
    ) -> List[Dict[str, Any]]:
        """Predict nutrient deficiencies based on detected symptoms."""
        deficiency_scores = {}
        
        # Get symptom patterns for this crop
        crop_patterns = {}
        for nutrient, patterns in self.symptom_patterns.items():
            crop_patterns[nutrient] = [p for p in patterns if p.crop_type == crop_type]
        
        # Score each potential deficiency
        for symptom in symptoms:
            for nutrient in symptom.associated_nutrients:
                if nutrient not in deficiency_scores:
                    deficiency_scores[nutrient] = {
                        'score': 0.0,
                        'confidence': 0.0,
                        'supporting_symptoms': [],
                        'pattern_matches': []
                    }
                
                # Add symptom contribution to score
                symptom_weight = symptom.confidence_score
                deficiency_scores[nutrient]['score'] += symptom_weight
                deficiency_scores[nutrient]['supporting_symptoms'].append(symptom.description)
                
                # Check pattern matches
                patterns = crop_patterns.get(nutrient, [])
                for pattern in patterns:
                    match_score = self._calculate_pattern_match(symptom, pattern)
                    if match_score > 0.5:
                        deficiency_scores[nutrient]['pattern_matches'].append({
                            'pattern': pattern.nutrient,
                            'match_score': match_score
                        })
                        deficiency_scores[nutrient]['confidence'] += match_score * pattern.confidence_weight
        
        # Convert to sorted list of predictions
        predictions = []
        for nutrient, data in deficiency_scores.items():
            if data['score'] > 0.3:  # Minimum threshold
                predictions.append({
                    'nutrient': nutrient,
                    'probability': min(1.0, data['score']),
                    'confidence': min(1.0, data['confidence']),
                    'supporting_symptoms': data['supporting_symptoms'],
                    'pattern_matches': len(data['pattern_matches']),
                    'severity_estimate': self._estimate_severity_from_symptoms(
                        [s for s in symptoms if nutrient in s.associated_nutrients]
                    )
                })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        return predictions[:5]  # Return top 5 predictions
    
    def _calculate_pattern_match(self, symptom: VisualSymptom, pattern: SymptomPattern) -> float:
        """Calculate how well a symptom matches a known pattern."""
        match_score = 0.0
        
        # Check plant part match
        if symptom.plant_part in pattern.affected_plant_parts:
            match_score += 0.3
        
        # Check symptom type relevance
        symptom_keywords = symptom.description.lower().split()
        pattern_keywords = ' '.join(pattern.primary_symptoms + pattern.secondary_symptoms).lower().split()
        
        keyword_matches = len(set(symptom_keywords) & set(pattern_keywords))
        if keyword_matches > 0:
            match_score += min(0.4, keyword_matches * 0.1)
        
        # Check distinguishing features
        for feature in pattern.distinguishing_features:
            if any(word in symptom.description.lower() for word in feature.lower().split()):
                match_score += 0.1
        
        return min(1.0, match_score)
    
    def _estimate_severity_from_symptoms(self, symptoms: List[VisualSymptom]) -> str:
        """Estimate deficiency severity from visual symptoms."""
        if not symptoms:
            return "mild"
        
        severity_scores = {'mild': 1, 'moderate': 2, 'severe': 3}
        avg_severity = np.mean([severity_scores.get(s.severity, 1) for s in symptoms])
        
        if avg_severity >= 2.5:
            return "severe"
        elif avg_severity >= 1.5:
            return "moderate"
        else:
            return "mild"
    
    def _calculate_analysis_confidence(
        self,
        symptoms: List[VisualSymptom],
        quality_score: float,
        predictions: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall confidence in the analysis."""
        if not symptoms or not predictions:
            return 0.0
        
        # Base confidence from image quality
        confidence = quality_score * 0.3
        
        # Add confidence from symptom detection
        avg_symptom_confidence = np.mean([s.confidence_score for s in symptoms])
        confidence += avg_symptom_confidence * 0.4
        
        # Add confidence from deficiency predictions
        if predictions:
            top_prediction_confidence = predictions[0]['confidence']
            confidence += top_prediction_confidence * 0.3
        
        return min(1.0, confidence)
    
    def _generate_image_analysis_recommendations(
        self,
        predictions: List[Dict[str, Any]],
        symptoms: List[VisualSymptom]
    ) -> List[str]:
        """Generate recommendations based on image analysis."""
        recommendations = []
        
        if not predictions:
            recommendations.append("No clear nutrient deficiency patterns detected")
            recommendations.append("Consider soil testing for comprehensive nutrient analysis")
            return recommendations
        
        # Recommendations for top predictions
        for i, prediction in enumerate(predictions[:3]):
            nutrient = prediction['nutrient']
            probability = prediction['probability']
            
            if probability > 0.7:
                recommendations.append(f"Strong indication of {nutrient} deficiency - recommend immediate soil/tissue testing")
            elif probability > 0.5:
                recommendations.append(f"Possible {nutrient} deficiency - monitor closely and consider testing")
            else:
                recommendations.append(f"Mild symptoms suggesting {nutrient} stress - continue monitoring")
        
        # General recommendations
        recommendations.append("Take additional photos from different angles for better analysis")
        recommendations.append("Document symptom progression over time")
        
        if any(s.severity == "severe" for s in symptoms):
            recommendations.append("Severe symptoms detected - consult with agricultural advisor")
        
        return recommendations
    
    def _create_error_result(self, analysis_id: str, error_message: str) -> ImageAnalysisResult:
        """Create error result for failed analysis."""
        return ImageAnalysisResult(
            analysis_id=analysis_id,
            image_quality_score=0.0,
            detected_symptoms=[],
            crop_identification="unknown",
            growth_stage="unknown",
            environmental_factors=[],
            deficiency_predictions=[],
            confidence_level=0.0,
            recommendations=[f"Analysis failed: {error_message}"]
        )
    
    async def analyze_symptom_description(
        self,
        description: str,
        crop_type: str,
        growth_stage: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Analyze text description of symptoms for deficiency detection."""
        
        # Extract keywords from description
        description_lower = description.lower()
        
        # Initialize scoring for each nutrient
        nutrient_scores = {}
        
        # Check against symptom patterns
        for nutrient, patterns in self.symptom_patterns.items():
            crop_patterns = [p for p in patterns if p.crop_type == crop_type]
            
            for pattern in crop_patterns:
                score = 0.0
                matched_symptoms = []
                
                # Check primary symptoms
                for symptom in pattern.primary_symptoms:
                    if any(word in description_lower for word in symptom.lower().split()):
                        score += 0.4
                        matched_symptoms.append(symptom)
                
                # Check secondary symptoms
                for symptom in pattern.secondary_symptoms:
                    if any(word in description_lower for word in symptom.lower().split()):
                        score += 0.2
                        matched_symptoms.append(symptom)
                
                # Check distinguishing features
                for feature in pattern.distinguishing_features:
                    if any(word in description_lower for word in feature.lower().split()):
                        score += 0.3
                        matched_symptoms.append(feature)
                
                if score > 0:
                    if nutrient not in nutrient_scores:
                        nutrient_scores[nutrient] = {
                            'total_score': 0,
                            'matched_symptoms': [],
                            'confidence': 0
                        }
                    
                    nutrient_scores[nutrient]['total_score'] += score * pattern.confidence_weight
                    nutrient_scores[nutrient]['matched_symptoms'].extend(matched_symptoms)
                    nutrient_scores[nutrient]['confidence'] = max(
                        nutrient_scores[nutrient]['confidence'], 
                        score * pattern.confidence_weight
                    )
        
        # Convert to predictions
        predictions = []
        for nutrient, data in nutrient_scores.items():
            if data['total_score'] > 0.3:
                predictions.append({
                    'nutrient': nutrient,
                    'probability': min(1.0, data['total_score']),
                    'confidence': min(1.0, data['confidence']),
                    'matched_symptoms': list(set(data['matched_symptoms'])),
                    'description_analysis': True
                })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        return predictions[:5]