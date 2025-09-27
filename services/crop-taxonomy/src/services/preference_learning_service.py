"""
Preference Learning and Adaptation Service

This service implements machine learning algorithms to automatically adapt farmer preferences
based on user interactions, feedback, and recommendation performance.

Features:
- User interaction tracking
- Feedback-based preference adjustment
- Recommendation performance analysis
- Preference weight optimization
- Pattern detection in user behavior
"""

import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from collections import defaultdict
from dataclasses import dataclass

try:
    from ..database.crop_taxonomy_db import get_db_connection
    from .preference_manager import FarmerPreferenceManager, PreferenceCategory
except ImportError:
    from database.crop_taxonomy_db import get_db_connection
    from preference_manager import FarmerPreferenceManager, PreferenceCategory

logger = logging.getLogger(__name__)


@dataclass
class UserInteraction:
    """Data class for tracking user interactions"""
    user_id: UUID
    interaction_type: str  # 'view', 'select', 'reject', 'save', 'share'
    crop_id: Optional[str] = None
    recommendation_id: Optional[UUID] = None
    interaction_data: Dict[str, Any] = None
    timestamp: datetime = None
    session_id: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.interaction_data is None:
            self.interaction_data = {}


@dataclass
class FeedbackEvent:
    """Data class for user feedback events"""
    user_id: UUID
    recommendation_id: UUID
    feedback_type: str  # 'rating', 'implemented', 'rejected', 'modified'
    feedback_value: Any  # Rating 1-5, boolean, or modification details
    feedback_text: Optional[str] = None
    crop_ids: List[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.crop_ids is None:
            self.crop_ids = []


class PreferenceLearningService:
    """
    Service for learning and adapting farmer preferences based on user behavior.
    
    This service uses multiple learning algorithms:
    1. Collaborative filtering for similar farmer recommendations
    2. Content-based filtering for crop characteristics
    3. Reinforcement learning for preference weight optimization
    4. Pattern recognition for implicit preference detection
    """

    def __init__(self):
        self.preference_manager = FarmerPreferenceManager()
        self.learning_rate = 0.1
        self.decay_factor = 0.95
        self.min_interactions_for_learning = 5

    async def _get_connection(self):
        """Get database connection"""
        return await get_db_connection()

    async def track_user_interaction(self, interaction: UserInteraction) -> bool:
        """Track user interaction for learning purposes"""
        conn = await self._get_connection()
        
        query = """
        INSERT INTO user_interactions 
        (user_id, interaction_type, crop_id, recommendation_id, interaction_data, 
         timestamp, session_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        try:
            await conn.execute(
                query,
                interaction.user_id,
                interaction.interaction_type,
                interaction.crop_id,
                interaction.recommendation_id,
                json.dumps(interaction.interaction_data),
                interaction.timestamp,
                interaction.session_id
            )
            logger.info(f"Tracked interaction for user {interaction.user_id}: {interaction.interaction_type}")
            
            # Trigger learning if enough interactions accumulated
            await self._trigger_learning_if_ready(interaction.user_id)
            return True
            
        except Exception as e:
            logger.error(f"Error tracking user interaction: {e}")
            return False

    async def record_feedback(self, feedback: FeedbackEvent) -> bool:
        """Record user feedback for learning"""
        conn = await self._get_connection()
        
        query = """
        INSERT INTO user_feedback 
        (user_id, recommendation_id, feedback_type, feedback_value, feedback_text, 
         crop_ids, timestamp)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """
        
        try:
            await conn.execute(
                query,
                feedback.user_id,
                feedback.recommendation_id,
                feedback.feedback_type,
                json.dumps(feedback.feedback_value),
                feedback.feedback_text,
                feedback.crop_ids,
                feedback.timestamp
            )
            logger.info(f"Recorded feedback for user {feedback.user_id}: {feedback.feedback_type}")
            
            # Immediate learning from explicit feedback
            await self._learn_from_feedback(feedback)
            return True
            
        except Exception as e:
            logger.error(f"Error recording feedback: {e}")
            return False

    async def _trigger_learning_if_ready(self, user_id: UUID) -> None:
        """Check if user has enough interactions to trigger learning"""
        conn = await self._get_connection()
        
        # Count recent interactions
        query = """
        SELECT COUNT(*) as interaction_count
        FROM user_interactions 
        WHERE user_id = $1 AND timestamp >= $2
        """
        
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            result = await conn.fetchrow(query, user_id, cutoff_date)
            
            if result['interaction_count'] >= self.min_interactions_for_learning:
                await self._learn_from_interactions(user_id)
                
        except Exception as e:
            logger.error(f"Error checking learning readiness for user {user_id}: {e}")

    async def _learn_from_interactions(self, user_id: UUID) -> None:
        """Learn implicit preferences from user interactions"""
        conn = await self._get_connection()
        
        # Get recent interactions
        query = """
        SELECT ui.*, c.common_name, c.crop_category, c.scientific_name
        FROM user_interactions ui
        LEFT JOIN crops c ON ui.crop_id = c.crop_id
        WHERE ui.user_id = $1 AND ui.timestamp >= $2
        ORDER BY ui.timestamp DESC
        """
        
        try:
            cutoff_date = datetime.now() - timedelta(days=30)
            interactions = await conn.fetch(query, user_id, cutoff_date)
            
            if not interactions:
                return
                
            # Analyze interaction patterns
            patterns = self._analyze_interaction_patterns(interactions)
            
            # Update preferences based on patterns
            await self._update_preferences_from_patterns(user_id, patterns)
            
            logger.info(f"Updated preferences for user {user_id} based on {len(interactions)} interactions")
            
        except Exception as e:
            logger.error(f"Error learning from interactions for user {user_id}: {e}")

    async def _learn_from_feedback(self, feedback: FeedbackEvent) -> None:
        """Learn from explicit user feedback"""
        try:
            # Adjust preferences based on feedback type and value
            adjustments = self._calculate_preference_adjustments(feedback)
            
            if adjustments:
                await self._apply_preference_adjustments(feedback.user_id, adjustments)
                logger.info(f"Applied preference adjustments for user {feedback.user_id} based on feedback")
                
        except Exception as e:
            logger.error(f"Error learning from feedback: {e}")

    def _analyze_interaction_patterns(self, interactions: List[Any]) -> Dict[str, Any]:
        """Analyze user interaction patterns to infer preferences"""
        patterns = {
            'crop_preferences': defaultdict(float),
            'category_preferences': defaultdict(float),
            'interaction_preferences': defaultdict(float),
            'temporal_patterns': defaultdict(list),
            'rejection_patterns': defaultdict(int)
        }
        
        # Weight different interaction types
        interaction_weights = {
            'view': 0.1,
            'select': 0.5,
            'save': 0.8,
            'share': 0.9,
            'reject': -0.3,
            'skip': -0.1
        }
        
        for interaction in interactions:
            interaction_type = interaction['interaction_type']
            weight = interaction_weights.get(interaction_type, 0.1)
            
            # Track crop preferences
            if interaction['crop_id']:
                patterns['crop_preferences'][interaction['crop_id']] += weight
                
            # Track category preferences
            if interaction['crop_category']:
                patterns['category_preferences'][interaction['crop_category']] += weight
                
            # Track interaction type preferences
            patterns['interaction_preferences'][interaction_type] += 1
            
            # Track temporal patterns
            hour = interaction['timestamp'].hour
            patterns['temporal_patterns'][hour].append(interaction_type)
            
            # Track rejection patterns
            if interaction_type in ['reject', 'skip']:
                crop_category = interaction['crop_category']
                if crop_category:
                    patterns['rejection_patterns'][crop_category] += 1
        
        # Normalize scores
        self._normalize_pattern_scores(patterns)
        
        return patterns

    def _normalize_pattern_scores(self, patterns: Dict[str, Any]) -> None:
        """Normalize pattern scores to [0, 1] range"""
        for category, scores in patterns.items():
            if category in ['crop_preferences', 'category_preferences'] and scores:
                max_score = max(scores.values())
                min_score = min(scores.values())
                if max_score != min_score:
                    for key in scores:
                        scores[key] = (scores[key] - min_score) / (max_score - min_score)

    async def _update_preferences_from_patterns(self, user_id: UUID, patterns: Dict[str, Any]) -> None:
        """Update user preferences based on analyzed patterns"""
        
        # Update crop type preferences
        crop_prefs = patterns['crop_preferences']
        if crop_prefs:
            top_crops = sorted(crop_prefs.items(), key=lambda x: x[1], reverse=True)[:10]
            preferred_crops = [crop_id for crop_id, score in top_crops if score > 0.3]
            
            if preferred_crops:
                await self._update_crop_type_preferences(user_id, preferred_crops)
        
        # Update category preferences (management style, etc.)
        category_prefs = patterns['category_preferences']
        if category_prefs:
            await self._update_category_preferences(user_id, category_prefs)
        
        # Update risk tolerance based on interaction patterns
        interaction_prefs = patterns['interaction_preferences']
        if interaction_prefs:
            await self._update_risk_tolerance_from_behavior(user_id, interaction_prefs)

    async def _update_crop_type_preferences(self, user_id: UUID, preferred_crops: List[str]) -> None:
        """Update crop type preferences based on interaction patterns"""
        try:
            current_prefs = await self.preference_manager.get_user_preferences(
                user_id, PreferenceCategory.CROP_TYPES
            )
            
            if current_prefs:
                # Update existing preference
                pref = current_prefs[0]
                new_data = pref.preference_data.copy()
                
                # Merge with learned preferences
                existing_crops = set(new_data.get('preferred_crops', []))
                learned_crops = set(preferred_crops)
                merged_crops = list(existing_crops.union(learned_crops))
                
                new_data['preferred_crops'] = merged_crops
                new_data['learned_from_interactions'] = True
                new_data['last_learned'] = datetime.now().isoformat()
                
                await self.preference_manager.update_preference(
                    pref.id, preference_data=new_data
                )
            else:
                # Create new preference
                preference_data = {
                    'preferred_crops': preferred_crops,
                    'learned_from_interactions': True,
                    'last_learned': datetime.now().isoformat(),
                    'confidence_score': min(len(preferred_crops) / 10.0, 1.0)
                }
                
                await self.preference_manager.create_preference(
                    user_id, PreferenceCategory.CROP_TYPES, preference_data, weight=0.7
                )
                
        except Exception as e:
            logger.error(f"Error updating crop type preferences: {e}")

    async def _update_category_preferences(self, user_id: UUID, category_prefs: Dict[str, float]) -> None:
        """Update category-based preferences"""
        # This would involve more complex logic to map interaction patterns
        # to management style, sustainability preferences, etc.
        # For now, we'll implement a basic mapping
        
        try:
            # Infer sustainability preferences from organic crop interactions
            organic_score = category_prefs.get('organic', 0.0)
            if organic_score > 0.5:
                await self._update_sustainability_preferences(user_id, high_sustainability=True)
                
        except Exception as e:
            logger.error(f"Error updating category preferences: {e}")

    async def _update_sustainability_preferences(self, user_id: UUID, high_sustainability: bool) -> None:
        """Update sustainability preferences based on behavior"""
        try:
            current_prefs = await self.preference_manager.get_user_preferences(
                user_id, PreferenceCategory.SUSTAINABILITY
            )
            
            sustainability_data = {
                'carbon_sequestration': high_sustainability,
                'water_conservation': high_sustainability,
                'biodiversity': high_sustainability,
                'soil_health': high_sustainability,
                'learned_from_behavior': True,
                'last_learned': datetime.now().isoformat()
            }
            
            if current_prefs:
                await self.preference_manager.update_preference(
                    current_prefs[0].id, preference_data=sustainability_data
                )
            else:
                await self.preference_manager.create_preference(
                    user_id, PreferenceCategory.SUSTAINABILITY, sustainability_data, weight=0.6
                )
                
        except Exception as e:
            logger.error(f"Error updating sustainability preferences: {e}")

    async def _update_risk_tolerance_from_behavior(self, user_id: UUID, interaction_prefs: Dict[str, int]) -> None:
        """Infer risk tolerance from user behavior patterns"""
        try:
            # Calculate risk tolerance based on behavior
            safe_actions = interaction_prefs.get('view', 0) + interaction_prefs.get('save', 0)
            risky_actions = interaction_prefs.get('select', 0) + interaction_prefs.get('share', 0)
            
            total_actions = safe_actions + risky_actions
            if total_actions == 0:
                return
                
            risk_score = risky_actions / total_actions
            
            if risk_score > 0.7:
                risk_level = 'high'
                experimental_willingness = 0.8
            elif risk_score > 0.4:
                risk_level = 'moderate'
                experimental_willingness = 0.5
            else:
                risk_level = 'low'
                experimental_willingness = 0.2
                
            risk_data = {
                'level': risk_level,
                'experimental_willingness': experimental_willingness,
                'diversification_preference': risk_score < 0.5,
                'learned_from_behavior': True,
                'behavior_risk_score': risk_score,
                'last_learned': datetime.now().isoformat()
            }
            
            current_prefs = await self.preference_manager.get_user_preferences(
                user_id, PreferenceCategory.RISK_TOLERANCE
            )
            
            if current_prefs:
                await self.preference_manager.update_preference(
                    current_prefs[0].id, preference_data=risk_data
                )
            else:
                await self.preference_manager.create_preference(
                    user_id, PreferenceCategory.RISK_TOLERANCE, risk_data, weight=0.8
                )
                
        except Exception as e:
            logger.error(f"Error updating risk tolerance: {e}")

    def _calculate_preference_adjustments(self, feedback: FeedbackEvent) -> Dict[str, Any]:
        """Calculate how to adjust preferences based on feedback"""
        adjustments = {}
        
        if feedback.feedback_type == 'rating':
            rating = feedback.feedback_value
            if isinstance(rating, (int, float)) and 1 <= rating <= 5:
                # Positive feedback (4-5) increases preference weights
                # Negative feedback (1-2) decreases them
                if rating >= 4:
                    adjustments['weight_multiplier'] = 1.1
                    adjustments['preference_boost'] = True
                elif rating <= 2:
                    adjustments['weight_multiplier'] = 0.9
                    adjustments['preference_penalty'] = True
                    
        elif feedback.feedback_type == 'implemented':
            if feedback.feedback_value:
                adjustments['weight_multiplier'] = 1.2
                adjustments['implementation_boost'] = True
            else:
                adjustments['weight_multiplier'] = 0.8
                adjustments['rejection_penalty'] = True
                
        elif feedback.feedback_type == 'rejected':
            adjustments['weight_multiplier'] = 0.7
            adjustments['rejection_penalty'] = True
            
        return adjustments

    async def _apply_preference_adjustments(self, user_id: UUID, adjustments: Dict[str, Any]) -> None:
        """Apply calculated preference adjustments"""
        try:
            # Get all user preferences
            all_prefs = await self.preference_manager.get_user_preferences(user_id)
            
            weight_multiplier = adjustments.get('weight_multiplier', 1.0)
            
            for pref in all_prefs:
                new_weight = pref.weight * weight_multiplier
                new_weight = max(0.1, min(1.0, new_weight))  # Keep within bounds
                
                await self.preference_manager.update_preference(
                    pref.id, weight=new_weight
                )
                
            logger.info(f"Applied preference adjustments for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error applying preference adjustments: {e}")

    async def get_learning_insights(self, user_id: UUID) -> Dict[str, Any]:
        """Get insights about user learning and preference evolution"""
        conn = await self._get_connection()
        
        try:
            # Get interaction statistics
            interaction_query = """
            SELECT 
                interaction_type,
                COUNT(*) as count,
                MAX(timestamp) as last_interaction
            FROM user_interactions 
            WHERE user_id = $1 AND timestamp >= $2
            GROUP BY interaction_type
            """
            
            # Get feedback statistics
            feedback_query = """
            SELECT 
                feedback_type,
                AVG(CAST(feedback_value as FLOAT)) as avg_rating,
                COUNT(*) as count
            FROM user_feedback 
            WHERE user_id = $1 AND timestamp >= $2
            GROUP BY feedback_type
            """
            
            cutoff_date = datetime.now() - timedelta(days=30)
            
            interactions = await conn.fetch(interaction_query, user_id, cutoff_date)
            feedback_stats = await conn.fetch(feedback_query, user_id, cutoff_date)
            
            # Get preference evolution
            prefs = await self.preference_manager.get_user_preferences(user_id)
            learned_prefs = [p for p in prefs if p.preference_data.get('learned_from_interactions')]
            
            insights = {
                'user_id': str(user_id),
                'learning_period_days': 30,
                'interaction_summary': {
                    row['interaction_type']: {
                        'count': row['count'],
                        'last_interaction': row['last_interaction'].isoformat()
                    } for row in interactions
                },
                'feedback_summary': {
                    row['feedback_type']: {
                        'count': row['count'],
                        'avg_rating': float(row['avg_rating']) if row['avg_rating'] else None
                    } for row in feedback_stats
                },
                'learned_preferences_count': len(learned_prefs),
                'total_preferences': len(prefs),
                'learning_confidence': self._calculate_learning_confidence(interactions, feedback_stats),
                'generated_at': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting learning insights for user {user_id}: {e}")
            return {}

    def _calculate_learning_confidence(self, interactions: List[Any], feedback_stats: List[Any]) -> float:
        """Calculate confidence in learned preferences"""
        interaction_count = sum(row['count'] for row in interactions)
        feedback_count = sum(row['count'] for row in feedback_stats)
        
        # Base confidence on amount of data
        base_confidence = min(interaction_count / 50.0, 1.0)  # 50 interactions = full confidence
        feedback_boost = min(feedback_count / 10.0, 0.2)  # Up to 20% boost from feedback
        
        return min(base_confidence + feedback_boost, 1.0)


# Global instance for dependency injection
preference_learning_service = PreferenceLearningService()