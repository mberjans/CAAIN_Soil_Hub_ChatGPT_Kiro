"""
Advanced Recommendation Personalization and Learning Service

This service implements sophisticated machine learning algorithms for personalizing
crop variety recommendations based on user behavior, farm characteristics, and
continuous learning from feedback.

Features:
- Collaborative filtering for similar farmer recommendations
- Content-based filtering for crop characteristics matching
- Hybrid recommendation systems combining multiple approaches
- User preference learning and adaptation
- Farm characteristics integration
- Management style and risk tolerance adaptation
- Economic goals optimization
- Continuous learning from feedback
"""

import logging
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from uuid import UUID
from collections import defaultdict
from dataclasses import dataclass
import statistics

try:
    from ..models.crop_variety_models import (
        VarietyRecommendation,
        EnhancedCropVariety,
        VarietyCharacteristics
    )
    from ..models.preference_models import (
        PreferenceProfile,
        PreferenceSignal,
        PreferenceLearningRequest,
        RiskTolerance,
        ManagementStyle
    )
    from ..models.service_models import (
        VarietyRecommendationRequest,
        ConfidenceLevel
    )
    from .preference_learning_service import PreferenceLearningService
    from .variety_recommendation_service import VarietyRecommendationService
except ImportError:
    from models.crop_variety_models import (
        VarietyRecommendation,
        EnhancedCropVariety,
        VarietyCharacteristics
    )
    from models.preference_models import (
        PreferenceProfile,
        PreferenceSignal,
        PreferenceLearningRequest,
        RiskTolerance,
        ManagementStyle
    )
    from models.service_models import (
        VarietyRecommendationRequest,
        ConfidenceLevel
    )
    from preference_learning_service import PreferenceLearningService
    from variety_recommendation_service import VarietyRecommendationService

logger = logging.getLogger(__name__)


@dataclass
class FarmCharacteristics:
    """Farm characteristics for personalization."""
    farm_size_acres: float
    soil_type: str
    climate_zone: str
    irrigation_available: bool
    equipment_level: str  # 'basic', 'intermediate', 'advanced'
    labor_availability: str  # 'limited', 'moderate', 'abundant'
    market_access: str  # 'local', 'regional', 'national'
    organic_certification: bool
    sustainability_focus: float  # 0.0 to 1.0
    technology_adoption: float  # 0.0 to 1.0


@dataclass
class UserProfile:
    """Comprehensive user profile for personalization."""
    user_id: UUID
    farm_characteristics: FarmCharacteristics
    management_style: ManagementStyle
    risk_tolerance: RiskTolerance
    economic_goals: Dict[str, float]  # goal -> weight
    experience_level: str  # 'beginner', 'intermediate', 'expert'
    crop_preferences: List[str]
    sustainability_priorities: List[str]
    market_preferences: List[str]


@dataclass
class SimilarityScore:
    """Similarity score between users or items."""
    entity_id: Union[UUID, str]
    similarity: float
    confidence: float
    factors: Dict[str, float]


class CollaborativeFilteringEngine:
    """Collaborative filtering for finding similar farmers."""
    
    def __init__(self):
        self.user_item_matrix = {}
        self.item_similarity_cache = {}
        self.user_similarity_cache = {}
    
    def build_user_item_matrix(self, interactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
        """Build user-item interaction matrix."""
        matrix = defaultdict(lambda: defaultdict(float))
        
        for interaction in interactions:
            user_id = str(interaction['user_id'])
            item_id = str(interaction.get('crop_id', interaction.get('variety_id', '')))
            rating = self._extract_rating(interaction)
            
            if item_id:
                matrix[user_id][item_id] = rating
        
        return dict(matrix)
    
    def _extract_rating(self, interaction: Dict[str, Any]) -> float:
        """Extract rating from interaction data."""
        interaction_type = interaction.get('interaction_type', '')
        feedback_value = interaction.get('feedback_value', 0)
        
        # Map interaction types to ratings
        rating_map = {
            'view': 0.1,
            'select': 0.5,
            'save': 0.7,
            'share': 0.9,
            'reject': -0.5,
            'skip': -0.1
        }
        
        base_rating = rating_map.get(interaction_type, 0.1)
        
        # Adjust based on explicit feedback
        if isinstance(feedback_value, (int, float)) and 1 <= feedback_value <= 5:
            return feedback_value / 5.0
        
        return base_rating
    
    def calculate_user_similarity(self, user1_id: str, user2_id: str, 
                                user_item_matrix: Dict[str, Dict[str, float]]) -> float:
        """Calculate cosine similarity between two users."""
        user1_items = user_item_matrix.get(user1_id, {})
        user2_items = user_item_matrix.get(user2_id, {})
        
        if not user1_items or not user2_items:
            return 0.0
        
        # Find common items
        common_items = set(user1_items.keys()) & set(user2_items.keys())
        if not common_items:
            return 0.0
        
        # Calculate cosine similarity
        dot_product = sum(user1_items[item] * user2_items[item] for item in common_items)
        norm1 = sum(rating ** 2 for rating in user1_items.values()) ** 0.5
        norm2 = sum(rating ** 2 for rating in user2_items.values()) ** 0.5
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def find_similar_users(self, target_user_id: str, user_item_matrix: Dict[str, Dict[str, float]], 
                          min_similarity: float = 0.3) -> List[SimilarityScore]:
        """Find users similar to the target user."""
        similarities = []
        
        for user_id in user_item_matrix.keys():
            if user_id == target_user_id:
                continue
            
            similarity = self.calculate_user_similarity(target_user_id, user_id, user_item_matrix)
            if similarity >= min_similarity:
                similarities.append(SimilarityScore(
                    entity_id=user_id,
                    similarity=similarity,
                    confidence=min(similarity * 2, 1.0),
                    factors={'interaction_pattern': similarity}
                ))
        
        return sorted(similarities, key=lambda x: x.similarity, reverse=True)


class ContentBasedFilteringEngine:
    """Content-based filtering for crop characteristics matching."""
    
    def __init__(self):
        self.crop_feature_weights = {
            'yield_potential': 0.25,
            'disease_resistance': 0.20,
            'maturity_days': 0.15,
            'drought_tolerance': 0.15,
            'quality_attributes': 0.10,
            'market_demand': 0.10,
            'input_requirements': 0.05
        }
    
    def extract_crop_features(self, variety: EnhancedCropVariety) -> Dict[str, float]:
        """Extract numerical features from crop variety."""
        features = {}
        
        # Yield potential
        if variety.characteristics and variety.characteristics.yield_potential:
            features['yield_potential'] = variety.characteristics.yield_potential.expected_yield or 0.5
        
        # Disease resistance
        if variety.characteristics and variety.characteristics.disease_resistance:
            resistance_count = len(variety.characteristics.disease_resistance.resistant_diseases or [])
            features['disease_resistance'] = min(resistance_count / 10.0, 1.0)
        
        # Maturity days
        if variety.characteristics and variety.characteristics.seasonal_timing:
            maturity = variety.characteristics.seasonal_timing.maturity_days
            if maturity:
                # Normalize to 0-1 scale (60-180 days)
                features['maturity_days'] = max(0, min(1, (maturity - 60) / 120))
        
        # Drought tolerance
        if variety.characteristics and variety.characteristics.abiotic_stress_tolerances:
            drought = variety.characteristics.abiotic_stress_tolerances.drought_tolerance
            features['drought_tolerance'] = drought.value if drought else 0.5
        
        # Quality attributes
        if variety.characteristics and variety.characteristics.quality_attributes:
            quality_score = 0.0
            quality_attrs = variety.characteristics.quality_attributes
            if quality_attrs.protein_content:
                quality_score += 0.3
            if quality_attrs.oil_content:
                quality_score += 0.3
            if quality_attrs.starch_content:
                quality_score += 0.4
            features['quality_attributes'] = min(quality_score, 1.0)
        
        # Market demand (simplified)
        features['market_demand'] = 0.7  # Default moderate demand
        
        # Input requirements (inverse - lower inputs = higher score)
        if variety.characteristics:
            input_score = 0.5  # Default moderate
            if variety.characteristics.input_requirements:
                # Lower fertilizer needs = higher score
                fertilizer_needs = variety.characteristics.input_requirements.get('fertilizer_level', 'moderate')
                if fertilizer_needs == 'low':
                    input_score = 0.8
                elif fertilizer_needs == 'high':
                    input_score = 0.2
            features['input_requirements'] = input_score
        
        return features
    
    def calculate_content_similarity(self, variety1: EnhancedCropVariety, 
                                   variety2: EnhancedCropVariety) -> float:
        """Calculate content-based similarity between two varieties."""
        features1 = self.extract_crop_features(variety1)
        features2 = self.extract_crop_features(variety2)
        
        # Calculate weighted cosine similarity
        dot_product = 0.0
        norm1 = 0.0
        norm2 = 0.0
        
        for feature, weight in self.crop_feature_weights.items():
            val1 = features1.get(feature, 0.0)
            val2 = features2.get(feature, 0.0)
            
            dot_product += weight * val1 * val2
            norm1 += weight * (val1 ** 2)
            norm2 += weight * (val2 ** 2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / ((norm1 ** 0.5) * (norm2 ** 0.5))
    
    def find_similar_varieties(self, target_variety: EnhancedCropVariety, 
                             candidate_varieties: List[EnhancedCropVariety],
                             min_similarity: float = 0.3) -> List[SimilarityScore]:
        """Find varieties similar to the target variety."""
        similarities = []
        
        for variety in candidate_varieties:
            if variety.id == target_variety.id:
                continue
            
            similarity = self.calculate_content_similarity(target_variety, variety)
            if similarity >= min_similarity:
                similarities.append(SimilarityScore(
                    entity_id=variety.id,
                    similarity=similarity,
                    confidence=similarity,
                    factors={'content_similarity': similarity}
                ))
        
        return sorted(similarities, key=lambda x: x.similarity, reverse=True)


class HybridRecommendationEngine:
    """Hybrid recommendation engine combining collaborative and content-based filtering."""
    
    def __init__(self):
        self.collaborative_engine = CollaborativeFilteringEngine()
        self.content_engine = ContentBasedFilteringEngine()
        self.collaborative_weight = 0.4
        self.content_weight = 0.6
    
    def generate_hybrid_recommendations(self, user_profile: UserProfile, 
                                      candidate_varieties: List[EnhancedCropVariety],
                                      user_interactions: List[Dict[str, Any]]) -> List[VarietyRecommendation]:
        """Generate hybrid recommendations combining multiple approaches."""
        
        # Build user-item matrix for collaborative filtering
        user_item_matrix = self.collaborative_engine.build_user_item_matrix(user_interactions)
        
        # Get collaborative recommendations
        collaborative_recs = self._get_collaborative_recommendations(
            user_profile, candidate_varieties, user_item_matrix
        )
        
        # Get content-based recommendations
        content_recs = self._get_content_based_recommendations(
            user_profile, candidate_varieties
        )
        
        # Combine recommendations
        hybrid_recs = self._combine_recommendations(collaborative_recs, content_recs)
        
        return hybrid_recs
    
    def _get_collaborative_recommendations(self, user_profile: UserProfile,
                                         candidate_varieties: List[EnhancedCropVariety],
                                         user_item_matrix: Dict[str, Dict[str, float]]) -> List[VarietyRecommendation]:
        """Get recommendations based on similar users."""
        user_id = str(user_profile.user_id)
        
        # Find similar users
        similar_users = self.collaborative_engine.find_similar_users(user_id, user_item_matrix)
        
        if not similar_users:
            return []
        
        # Get varieties liked by similar users
        recommended_varieties = []
        variety_scores = defaultdict(float)
        
        for similar_user in similar_users[:5]:  # Top 5 similar users
            similar_user_id = str(similar_user.entity_id)
            user_items = user_item_matrix.get(similar_user_id, {})
            
            for variety_id, rating in user_items.items():
                if rating > 0.3:  # Only positive ratings
                    variety_scores[variety_id] += rating * similar_user.similarity
        
        # Convert to recommendations
        for variety_id, score in variety_scores.items():
            variety = next((v for v in candidate_varieties if str(v.id) == variety_id), None)
            if variety:
                recommendation = VarietyRecommendation(
                    variety=variety,
                    variety_id=variety.id,
                    variety_name=variety.variety_name,
                    overall_score=min(score / 5.0, 1.0),  # Normalize
                    suitability_factors={'collaborative_score': score},
                    individual_scores={'collaborative': score},
                    weighted_contributions={'collaborative': score * self.collaborative_weight}
                )
                recommended_varieties.append(recommendation)
        
        return recommended_varieties
    
    def _get_content_based_recommendations(self, user_profile: UserProfile,
                                         candidate_varieties: List[EnhancedCropVariety]) -> List[VarietyRecommendation]:
        """Get recommendations based on content similarity to user preferences."""
        recommendations = []
        
        # Score varieties based on user profile
        for variety in candidate_varieties:
            score = self._score_variety_for_user(variety, user_profile)
            
            if score > 0.3:  # Minimum threshold
                recommendation = VarietyRecommendation(
                    variety=variety,
                    variety_id=variety.id,
                    variety_name=variety.variety_name,
                    overall_score=score,
                    suitability_factors={'content_score': score},
                    individual_scores={'content': score},
                    weighted_contributions={'content': score * self.content_weight}
                )
                recommendations.append(recommendation)
        
        return recommendations
    
    def _score_variety_for_user(self, variety: EnhancedCropVariety, 
                              user_profile: UserProfile) -> float:
        """Score a variety based on user profile characteristics."""
        score = 0.0
        
        # Farm characteristics matching
        farm_chars = user_profile.farm_characteristics
        
        # Size appropriateness
        if farm_chars.farm_size_acres < 50:  # Small farm
            if variety.characteristics and variety.characteristics.input_requirements:
                input_level = variety.characteristics.input_requirements.get('fertilizer_level', 'moderate')
                if input_level == 'low':
                    score += 0.2
        
        # Soil type compatibility
        if variety.characteristics and variety.characteristics.soil_preferences:
            soil_prefs = variety.characteristics.soil_preferences
            if farm_chars.soil_type in (soil_prefs.preferred_soil_types or []):
                score += 0.15
        
        # Irrigation requirements
        if variety.characteristics and variety.characteristics.water_requirements:
            water_req = variety.characteristics.water_requirements
            if farm_chars.irrigation_available:
                if water_req.irrigation_required:
                    score += 0.1
            else:
                if not water_req.irrigation_required:
                    score += 0.1
        
        # Management style compatibility
        if user_profile.management_style == ManagementStyle.LOW_INPUT:
            if variety.characteristics and variety.characteristics.input_requirements:
                input_level = variety.characteristics.input_requirements.get('fertilizer_level', 'moderate')
                if input_level == 'low':
                    score += 0.2
        elif user_profile.management_style == ManagementStyle.HIGH_INTENSITY:
            if variety.characteristics and variety.characteristics.input_requirements:
                input_level = variety.characteristics.input_requirements.get('fertilizer_level', 'moderate')
                if input_level == 'high':
                    score += 0.2
        
        # Risk tolerance matching
        if user_profile.risk_tolerance == RiskTolerance.LOW:
            # Prefer stable, proven varieties
            if variety.characteristics and variety.characteristics.market_attributes:
                market_attrs = variety.characteristics.market_attributes
                if market_attrs.market_stability and market_attrs.market_stability > 0.7:
                    score += 0.15
        elif user_profile.risk_tolerance == RiskTolerance.HIGH:
            # Prefer high-potential, newer varieties
            if variety.characteristics and variety.characteristics.yield_potential:
                yield_pot = variety.characteristics.yield_potential
                if yield_pot.expected_yield and yield_pot.expected_yield > 0.8:
                    score += 0.15
        
        # Sustainability focus
        if farm_chars.sustainability_focus > 0.7:
            if variety.characteristics and variety.characteristics.sustainability_attributes:
                sustainability = variety.characteristics.sustainability_attributes
                if sustainability.organic_suitable:
                    score += 0.1
                if sustainability.environmental_benefits:
                    score += 0.1
        
        # Crop preferences
        if variety.crop_id and str(variety.crop_id) in user_profile.crop_preferences:
            score += 0.2
        
        return min(score, 1.0)
    
    def _combine_recommendations(self, collaborative_recs: List[VarietyRecommendation],
                               content_recs: List[VarietyRecommendation]) -> List[VarietyRecommendation]:
        """Combine collaborative and content-based recommendations."""
        combined_scores = defaultdict(lambda: {'collaborative': 0.0, 'content': 0.0, 'count': 0})
        
        # Collect scores from both approaches
        for rec in collaborative_recs:
            variety_id = str(rec.variety_id)
            combined_scores[variety_id]['collaborative'] = rec.overall_score
            combined_scores[variety_id]['count'] += 1
        
        for rec in content_recs:
            variety_id = str(rec.variety_id)
            combined_scores[variety_id]['content'] = rec.overall_score
            combined_scores[variety_id]['count'] += 1
        
        # Create hybrid recommendations
        hybrid_recs = []
        for variety_id, scores in combined_scores.items():
            # Weighted combination
            hybrid_score = (scores['collaborative'] * self.collaborative_weight + 
                          scores['content'] * self.content_weight)
            
            # Boost score if variety appears in both approaches
            if scores['count'] > 1:
                hybrid_score *= 1.2
            
            # Find the variety object
            variety_obj = None
            for rec in collaborative_recs + content_recs:
                if str(rec.variety_id) == variety_id:
                    variety_obj = rec.variety
                    break
            
            if variety_obj:
                recommendation = VarietyRecommendation(
                    variety=variety_obj,
                    variety_id=variety_obj.id,
                    variety_name=variety_obj.variety_name,
                    overall_score=min(hybrid_score, 1.0),
                    suitability_factors={
                        'hybrid_score': hybrid_score,
                        'collaborative_score': scores['collaborative'],
                        'content_score': scores['content']
                    },
                    individual_scores={
                        'collaborative': scores['collaborative'],
                        'content': scores['content']
                    },
                    weighted_contributions={
                        'collaborative': scores['collaborative'] * self.collaborative_weight,
                        'content': scores['content'] * self.content_weight
                    }
                )
                hybrid_recs.append(recommendation)
        
        return sorted(hybrid_recs, key=lambda x: x.overall_score, reverse=True)


class PersonalizationService:
    """
    Advanced recommendation personalization service with machine learning capabilities.
    
    This service implements sophisticated personalization algorithms including:
    - Collaborative filtering for similar farmer recommendations
    - Content-based filtering for crop characteristics matching
    - Hybrid recommendation systems
    - User preference learning and adaptation
    - Farm characteristics integration
    - Management style and risk tolerance adaptation
    - Economic goals optimization
    - Continuous learning from feedback
    """
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize the personalization service."""
        self.preference_learning_service = PreferenceLearningService()
        self.hybrid_engine = HybridRecommendationEngine()
        self.variety_service = VarietyRecommendationService(database_url)
        
        # Learning parameters
        self.learning_rate = 0.1
        self.decay_factor = 0.95
        self.min_interactions_for_personalization = 10
        
        # Personalization weights
        self.personalization_weights = {
            'collaborative': 0.3,
            'content_based': 0.4,
            'preference_learning': 0.2,
            'farm_characteristics': 0.1
        }
    
    async def personalize_recommendations(self, 
                                         user_profile: UserProfile,
                                         base_recommendations: List[VarietyRecommendation],
                                         user_interactions: List[Dict[str, Any]] = None) -> List[VarietyRecommendation]:
        """
        Personalize variety recommendations based on user profile and learning.
        
        Args:
            user_profile: Comprehensive user profile
            base_recommendations: Base recommendations from variety service
            user_interactions: Historical user interactions for learning
            
        Returns:
            Personalized variety recommendations
        """
        try:
            # Get user interactions if not provided
            if user_interactions is None:
                user_interactions = await self._get_user_interactions(user_profile.user_id)
            
            # Apply personalization algorithms
            personalized_recs = []
            
            for rec in base_recommendations:
                # Calculate personalization score
                personalization_score = await self._calculate_personalization_score(
                    rec, user_profile, user_interactions
                )
                
                # Apply personalization adjustments
                adjusted_rec = self._apply_personalization_adjustments(
                    rec, personalization_score, user_profile
                )
                
                personalized_recs.append(adjusted_rec)
            
            # Sort by personalized score
            personalized_recs.sort(key=lambda x: x.overall_score, reverse=True)
            
            # Add personalization metadata
            for rec in personalized_recs:
                rec.metadata = rec.metadata or {}
                rec.metadata['personalized'] = True
                rec.metadata['personalization_timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Personalized {len(personalized_recs)} recommendations for user {user_profile.user_id}")
            return personalized_recs
            
        except Exception as e:
            logger.error(f"Error personalizing recommendations: {e}")
            return base_recommendations  # Fallback to base recommendations
    
    async def _calculate_personalization_score(self, 
                                            recommendation: VarietyRecommendation,
                                            user_profile: UserProfile,
                                            user_interactions: List[Dict[str, Any]]) -> float:
        """Calculate personalization score for a recommendation."""
        score = 0.0
        
        # Collaborative filtering component
        if len(user_interactions) >= self.min_interactions_for_personalization:
            collaborative_score = await self._get_collaborative_score(
                recommendation, user_profile, user_interactions
            )
            score += collaborative_score * self.personalization_weights['collaborative']
        
        # Content-based filtering component
        content_score = self._get_content_based_score(recommendation, user_profile)
        score += content_score * self.personalization_weights['content_based']
        
        # Preference learning component
        preference_score = await self._get_preference_learning_score(
            recommendation, user_profile
        )
        score += preference_score * self.personalization_weights['preference_learning']
        
        # Farm characteristics component
        farm_score = self._get_farm_characteristics_score(recommendation, user_profile)
        score += farm_score * self.personalization_weights['farm_characteristics']
        
        return min(score, 1.0)
    
    async def _get_collaborative_score(self, 
                                     recommendation: VarietyRecommendation,
                                     user_profile: UserProfile,
                                     user_interactions: List[Dict[str, Any]]) -> float:
        """Get collaborative filtering score."""
        try:
            # Build user-item matrix
            user_item_matrix = self.hybrid_engine.collaborative_engine.build_user_item_matrix(user_interactions)
            
            # Find similar users
            similar_users = self.hybrid_engine.collaborative_engine.find_similar_users(
                str(user_profile.user_id), user_item_matrix
            )
            
            if not similar_users:
                return 0.0
            
            # Check if similar users liked this variety
            variety_id = str(recommendation.variety_id)
            collaborative_score = 0.0
            
            for similar_user in similar_users[:3]:  # Top 3 similar users
                similar_user_id = str(similar_user.entity_id)
                user_items = user_item_matrix.get(similar_user_id, {})
                
                if variety_id in user_items:
                    rating = user_items[variety_id]
                    collaborative_score += rating * similar_user.similarity
            
            return min(collaborative_score / 3.0, 1.0)  # Normalize
            
        except Exception as e:
            logger.error(f"Error calculating collaborative score: {e}")
            return 0.0
    
    def _get_content_based_score(self, 
                               recommendation: VarietyRecommendation,
                               user_profile: UserProfile) -> float:
        """Get content-based filtering score."""
        try:
            variety = recommendation.variety
            if not variety:
                return 0.0
            
            return self.hybrid_engine._score_variety_for_user(variety, user_profile)
            
        except Exception as e:
            logger.error(f"Error calculating content-based score: {e}")
            return 0.0
    
    async def _get_preference_learning_score(self, 
                                           recommendation: VarietyRecommendation,
                                           user_profile: UserProfile) -> float:
        """Get preference learning score."""
        try:
            # Get user preferences
            preferences = await self.preference_learning_service.preference_manager.get_user_preferences(
                user_profile.user_id
            )
            
            if not preferences:
                return 0.0
            
            # Score based on learned preferences
            preference_score = 0.0
            
            for pref in preferences:
                if pref.preference_data.get('learned_from_interactions'):
                    # This is a learned preference
                    weight = pref.weight
                    confidence = pref.preference_data.get('confidence_score', 0.5)
                    
                    # Apply preference to recommendation
                    if pref.category.value == 'crop_types':
                        preferred_crops = pref.preference_data.get('preferred_crops', [])
                        if str(recommendation.variety.crop_id) in preferred_crops:
                            preference_score += weight * confidence
            
            return min(preference_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating preference learning score: {e}")
            return 0.0
    
    def _get_farm_characteristics_score(self, 
                                      recommendation: VarietyRecommendation,
                                      user_profile: UserProfile) -> float:
        """Get farm characteristics matching score."""
        try:
            variety = recommendation.variety
            farm_chars = user_profile.farm_characteristics
            
            if not variety or not variety.characteristics:
                return 0.0
            
            score = 0.0
            
            # Farm size appropriateness
            if farm_chars.farm_size_acres < 50:  # Small farm
                if variety.characteristics.input_requirements:
                    input_level = variety.characteristics.input_requirements.get('fertilizer_level', 'moderate')
                    if input_level == 'low':
                        score += 0.3
            
            # Soil type compatibility
            if variety.characteristics.soil_preferences:
                soil_prefs = variety.characteristics.soil_preferences
                if farm_chars.soil_type in (soil_prefs.preferred_soil_types or []):
                    score += 0.2
            
            # Irrigation compatibility
            if variety.characteristics.water_requirements:
                water_req = variety.characteristics.water_requirements
                if farm_chars.irrigation_available:
                    if water_req.irrigation_required:
                        score += 0.2
                else:
                    if not water_req.irrigation_required:
                        score += 0.2
            
            # Equipment level compatibility
            if variety.characteristics.equipment_requirements:
                equip_req = variety.characteristics.equipment_requirements
                if farm_chars.equipment_level == 'basic' and equip_req.complexity_level == 'basic':
                    score += 0.1
                elif farm_chars.equipment_level == 'advanced' and equip_req.complexity_level == 'advanced':
                    score += 0.1
            
            return min(score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating farm characteristics score: {e}")
            return 0.0
    
    def _apply_personalization_adjustments(self, 
                                         recommendation: VarietyRecommendation,
                                         personalization_score: float,
                                         user_profile: UserProfile) -> VarietyRecommendation:
        """Apply personalization adjustments to recommendation."""
        try:
            # Create adjusted recommendation
            adjusted_rec = recommendation.copy(deep=True)
            
            # Adjust overall score
            base_score = recommendation.overall_score
            adjusted_score = base_score * (0.7 + 0.3 * personalization_score)  # 70% base + 30% personalization
            
            adjusted_rec.overall_score = min(adjusted_score, 1.0)
            
            # Add personalization factors
            adjusted_rec.suitability_factors['personalization_score'] = personalization_score
            adjusted_rec.individual_scores['personalization'] = personalization_score
            adjusted_rec.weighted_contributions['personalization'] = personalization_score * 0.3
            
            # Add personalized explanations
            adjusted_rec.score_details['personalization'] = self._generate_personalization_explanation(
                personalization_score, user_profile
            )
            
            # Adjust recommendations based on user profile
            adjusted_rec.recommended_practices = self._personalize_practices(
                recommendation.recommended_practices, user_profile
            )
            
            return adjusted_rec
            
        except Exception as e:
            logger.error(f"Error applying personalization adjustments: {e}")
            return recommendation
    
    def _generate_personalization_explanation(self, 
                                             personalization_score: float,
                                             user_profile: UserProfile) -> str:
        """Generate explanation for personalization score."""
        if personalization_score > 0.7:
            return f"This variety is highly recommended for your {user_profile.management_style.value} management style and {user_profile.risk_tolerance.value} risk tolerance."
        elif personalization_score > 0.4:
            return f"This variety is moderately suitable for your farm characteristics and management preferences."
        else:
            return f"This variety may not be the best fit for your current farm setup and preferences."
    
    def _personalize_practices(self, 
                              practices: List[str],
                              user_profile: UserProfile) -> List[str]:
        """Personalize recommended practices based on user profile."""
        personalized_practices = practices.copy()
        
        # Add management style specific practices
        if user_profile.management_style == ManagementStyle.LOW_INPUT:
            personalized_practices.append("Consider minimal fertilizer applications")
            personalized_practices.append("Focus on soil health improvements")
        elif user_profile.management_style == ManagementStyle.HIGH_INTENSITY:
            personalized_practices.append("Consider precision application techniques")
            personalized_practices.append("Monitor closely for optimal timing")
        
        # Add risk tolerance specific practices
        if user_profile.risk_tolerance == RiskTolerance.LOW:
            personalized_practices.append("Consider conservative planting dates")
            personalized_practices.append("Maintain crop insurance coverage")
        elif user_profile.risk_tolerance == RiskTolerance.HIGH:
            personalized_practices.append("Consider early planting opportunities")
            personalized_practices.append("Explore new market opportunities")
        
        return personalized_practices
    
    async def _get_user_interactions(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get user interactions for learning."""
        try:
            conn = await self.preference_learning_service._get_connection()
            
            query = """
            SELECT ui.*, c.crop_id, c.common_name, c.crop_category
            FROM user_interactions ui
            LEFT JOIN crops c ON ui.crop_id = c.crop_id
            WHERE ui.user_id = $1 AND ui.timestamp >= $2
            ORDER BY ui.timestamp DESC
            """
            
            cutoff_date = datetime.now() - timedelta(days=90)  # Last 90 days
            interactions = await conn.fetch(query, user_id, cutoff_date)
            
            return [dict(row) for row in interactions]
            
        except Exception as e:
            logger.error(f"Error getting user interactions: {e}")
            return []
    
    async def learn_from_feedback(self, 
                                user_id: UUID,
                                recommendation_id: UUID,
                                feedback_type: str,
                                feedback_value: Any,
                                feedback_text: Optional[str] = None) -> bool:
        """Learn from user feedback to improve future recommendations."""
        try:
            from .preference_learning_service import FeedbackEvent
            
            feedback = FeedbackEvent(
                user_id=user_id,
                recommendation_id=recommendation_id,
                feedback_type=feedback_type,
                feedback_value=feedback_value,
                feedback_text=feedback_text
            )
            
            success = await self.preference_learning_service.record_feedback(feedback)
            
            if success:
                logger.info(f"Learned from feedback for user {user_id}: {feedback_type}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error learning from feedback: {e}")
            return False
    
    async def get_personalization_insights(self, user_id: UUID) -> Dict[str, Any]:
        """Get insights about personalization and learning for a user."""
        try:
            # Get learning insights
            learning_insights = await self.preference_learning_service.get_learning_insights(user_id)
            
            # Get personalization statistics
            user_interactions = await self._get_user_interactions(user_id)
            
            insights = {
                'user_id': str(user_id),
                'learning_insights': learning_insights,
                'personalization_stats': {
                    'total_interactions': len(user_interactions),
                    'interaction_types': self._count_interaction_types(user_interactions),
                    'personalization_ready': len(user_interactions) >= self.min_interactions_for_personalization,
                    'learning_confidence': learning_insights.get('learning_confidence', 0.0)
                },
                'recommendation_adaptation': {
                    'collaborative_filtering_active': len(user_interactions) >= self.min_interactions_for_personalization,
                    'content_based_filtering_active': True,
                    'preference_learning_active': learning_insights.get('learned_preferences_count', 0) > 0,
                    'farm_characteristics_active': True
                },
                'generated_at': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting personalization insights: {e}")
            return {}
    
    def _count_interaction_types(self, interactions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count interaction types."""
        counts = defaultdict(int)
        for interaction in interactions:
            counts[interaction.get('interaction_type', 'unknown')] += 1
        return dict(counts)


# Global instance for dependency injection
personalization_service = PersonalizationService()