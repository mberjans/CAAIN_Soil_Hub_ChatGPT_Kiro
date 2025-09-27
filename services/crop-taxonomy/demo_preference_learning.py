#!/usr/bin/env python3
"""
Demo script for Preference Learning and Adaptation System

This script demonstrates the core functionality of the preference learning system
without requiring database connections or complex dependencies.
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from uuid import uuid4
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from collections import defaultdict

# Add src to path for imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("🌾 CAAIN Soil Hub - Preference Learning System Demo")
print("=" * 60)

# Define simplified classes for demo
@dataclass
class UserInteraction:
    """Data class for tracking user interactions"""
    user_id: str
    interaction_type: str  # 'view', 'select', 'reject', 'save', 'share'
    crop_id: Optional[str] = None
    recommendation_id: Optional[str] = None
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
    user_id: str
    recommendation_id: str
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


class DemoPreferenceLearningService:
    """Demo version of preference learning service for testing"""
    
    def __init__(self):
        self.interactions = []
        self.feedback_events = []
        self.user_preferences = defaultdict(dict)
        self.learning_rate = 0.1
        self.min_interactions_for_learning = 5
    
    def track_user_interaction(self, interaction: UserInteraction) -> bool:
        """Track user interaction for learning purposes"""
        try:
            self.interactions.append(interaction)
            print(f"✓ Tracked {interaction.interaction_type} interaction for crop {interaction.crop_id}")
            
            # Check if learning should be triggered
            user_interactions = [i for i in self.interactions if i.user_id == interaction.user_id]
            if len(user_interactions) >= self.min_interactions_for_learning:
                self._learn_from_interactions(interaction.user_id)
            
            return True
        except Exception as e:
            print(f"❌ Error tracking interaction: {e}")
            return False
    
    def record_feedback(self, feedback: FeedbackEvent) -> bool:
        """Record user feedback for learning"""
        try:
            self.feedback_events.append(feedback)
            print(f"✓ Recorded {feedback.feedback_type} feedback: {feedback.feedback_value}")
            
            # Immediate learning from feedback
            self._learn_from_feedback(feedback)
            return True
        except Exception as e:
            print(f"❌ Error recording feedback: {e}")
            return False
    
    def _learn_from_interactions(self, user_id: str) -> None:
        """Learn implicit preferences from user interactions"""
        try:
            user_interactions = [i for i in self.interactions if i.user_id == user_id]
            
            if not user_interactions:
                return
            
            # Analyze interaction patterns
            patterns = self._analyze_interaction_patterns(user_interactions)
            
            # Update preferences based on patterns
            self._update_preferences_from_patterns(user_id, patterns)
            
            print(f"📊 Updated preferences for user {user_id[:8]}... based on {len(user_interactions)} interactions")
            
        except Exception as e:
            print(f"❌ Error learning from interactions: {e}")
    
    def _learn_from_feedback(self, feedback: FeedbackEvent) -> None:
        """Learn from explicit user feedback"""
        try:
            adjustments = self._calculate_preference_adjustments(feedback)
            
            if adjustments:
                self._apply_preference_adjustments(feedback.user_id, adjustments)
                print(f"🎯 Applied preference adjustments based on {feedback.feedback_type} feedback")
                
        except Exception as e:
            print(f"❌ Error learning from feedback: {e}")
    
    def _analyze_interaction_patterns(self, interactions: List[UserInteraction]) -> Dict[str, Any]:
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
            interaction_type = interaction.interaction_type
            weight = interaction_weights.get(interaction_type, 0.1)
            
            # Track crop preferences
            if interaction.crop_id:
                patterns['crop_preferences'][interaction.crop_id] += weight
                
            # Track interaction type preferences
            patterns['interaction_preferences'][interaction_type] += 1
            
            # Track temporal patterns
            hour = interaction.timestamp.hour
            patterns['temporal_patterns'][hour].append(interaction_type)
        
        # Normalize scores
        self._normalize_pattern_scores(patterns)
        
        return patterns
    
    def _normalize_pattern_scores(self, patterns: Dict[str, Any]) -> None:
        """Normalize pattern scores to [0, 1] range"""
        for category, scores in patterns.items():
            if category in ['crop_preferences', 'category_preferences'] and scores:
                max_score = max(scores.values()) if scores.values() else 1
                min_score = min(scores.values()) if scores.values() else 0
                if max_score != min_score:
                    for key in scores:
                        scores[key] = (scores[key] - min_score) / (max_score - min_score)
    
    def _update_preferences_from_patterns(self, user_id: str, patterns: Dict[str, Any]) -> None:
        """Update user preferences based on analyzed patterns"""
        
        # Update crop type preferences
        crop_prefs = patterns['crop_preferences']
        if crop_prefs:
            top_crops = sorted(crop_prefs.items(), key=lambda x: x[1], reverse=True)[:5]
            preferred_crops = [crop_id for crop_id, score in top_crops if score > 0.3]
            
            if preferred_crops:
                self.user_preferences[user_id]['preferred_crops'] = preferred_crops
                print(f"  📝 Updated preferred crops: {preferred_crops}")
        
        # Update interaction behavior insights
        interaction_prefs = patterns['interaction_preferences']
        if interaction_prefs:
            total_actions = sum(interaction_prefs.values())
            risky_actions = interaction_prefs.get('select', 0) + interaction_prefs.get('save', 0)
            
            if total_actions > 0:
                risk_score = risky_actions / total_actions
                risk_level = 'high' if risk_score > 0.6 else 'moderate' if risk_score > 0.3 else 'low'
                
                self.user_preferences[user_id]['risk_tolerance'] = {
                    'level': risk_level,
                    'score': risk_score
                }
                print(f"  🎲 Inferred risk tolerance: {risk_level} (score: {risk_score:.2f})")
    
    def _calculate_preference_adjustments(self, feedback: FeedbackEvent) -> Dict[str, Any]:
        """Calculate how to adjust preferences based on feedback"""
        adjustments = {}
        
        if feedback.feedback_type == 'rating':
            rating = feedback.feedback_value
            if isinstance(rating, (int, float)) and 1 <= rating <= 5:
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
        
        return adjustments
    
    def _apply_preference_adjustments(self, user_id: str, adjustments: Dict[str, Any]) -> None:
        """Apply calculated preference adjustments"""
        weight_multiplier = adjustments.get('weight_multiplier', 1.0)
        
        if user_id in self.user_preferences:
            # Apply adjustments to existing preferences
            current_prefs = self.user_preferences[user_id]
            for key, value in current_prefs.items():
                if isinstance(value, dict) and 'score' in value:
                    value['score'] *= weight_multiplier
                    value['score'] = max(0.1, min(1.0, value['score']))
    
    def get_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user learning and preference evolution"""
        user_interactions = [i for i in self.interactions if i.user_id == user_id]
        user_feedback = [f for f in self.feedback_events if f.user_id == user_id]
        
        interaction_summary = defaultdict(int)
        for interaction in user_interactions:
            interaction_summary[interaction.interaction_type] += 1
        
        feedback_summary = defaultdict(list)
        for feedback in user_feedback:
            if feedback.feedback_type == 'rating' and isinstance(feedback.feedback_value, (int, float)):
                feedback_summary['ratings'].append(feedback.feedback_value)
        
        insights = {
            'user_id': user_id,
            'total_interactions': len(user_interactions),
            'interaction_summary': dict(interaction_summary),
            'total_feedback': len(user_feedback),
            'avg_rating': sum(feedback_summary['ratings']) / len(feedback_summary['ratings']) if feedback_summary['ratings'] else None,
            'learned_preferences': self.user_preferences.get(user_id, {}),
            'learning_confidence': self._calculate_learning_confidence(user_interactions, user_feedback)
        }
        
        return insights
    
    def _calculate_learning_confidence(self, interactions: List[Any], feedback: List[Any]) -> float:
        """Calculate confidence in learned preferences"""
        interaction_count = len(interactions)
        feedback_count = len(feedback)
        
        base_confidence = min(interaction_count / 20.0, 1.0)
        feedback_boost = min(feedback_count / 5.0, 0.2)
        
        return min(base_confidence + feedback_boost, 1.0)


def run_demo():
    """Run the preference learning system demo"""
    
    # Initialize service
    learning_service = DemoPreferenceLearningService()
    
    # Create sample user
    user_id = str(uuid4())
    print(f"\n👤 Demo User: {user_id[:8]}...")
    
    print("\n📊 Simulating User Interactions:")
    print("-" * 40)
    
    # Simulate user interactions
    interactions = [
        UserInteraction(user_id, 'view', 'corn_001', interaction_data={'duration_seconds': 45}),
        UserInteraction(user_id, 'view', 'corn_002', interaction_data={'duration_seconds': 20}),
        UserInteraction(user_id, 'select', 'corn_001', interaction_data={'selection_time_ms': 2000}),
        UserInteraction(user_id, 'save', 'corn_001', interaction_data={'saved_to': 'favorites'}),
        UserInteraction(user_id, 'view', 'soybean_001', interaction_data={'duration_seconds': 30}),
        UserInteraction(user_id, 'select', 'soybean_001', interaction_data={'selection_time_ms': 1500}),
        UserInteraction(user_id, 'reject', 'wheat_001', interaction_data={'reason': 'not_suitable'}),
    ]
    
    for interaction in interactions:
        learning_service.track_user_interaction(interaction)
    
    print("\n💬 Simulating User Feedback:")
    print("-" * 40)
    
    # Simulate user feedback
    feedback_events = [
        FeedbackEvent(user_id, str(uuid4()), 'rating', 5, 'Excellent corn recommendation!', ['corn_001']),
        FeedbackEvent(user_id, str(uuid4()), 'implemented', True, 'Planted this variety', ['corn_001']),
        FeedbackEvent(user_id, str(uuid4()), 'rating', 4, 'Good soybean option', ['soybean_001']),
        FeedbackEvent(user_id, str(uuid4()), 'rating', 2, 'Wheat not suitable for my area', ['wheat_001'])
    ]
    
    for feedback in feedback_events:
        learning_service.record_feedback(feedback)
    
    print("\n🧠 Learning Insights:")
    print("-" * 40)
    
    # Get learning insights
    insights = learning_service.get_learning_insights(user_id)
    
    print(f"Total Interactions: {insights['total_interactions']}")
    print(f"Interaction Types: {insights['interaction_summary']}")
    print(f"Total Feedback: {insights['total_feedback']}")
    print(f"Average Rating: {insights['avg_rating']:.1f}" if insights['avg_rating'] else "No ratings")
    print(f"Learning Confidence: {insights['learning_confidence']:.2f}")
    
    print(f"\n🎯 Learned Preferences:")
    learned_prefs = insights['learned_preferences']
    if learned_prefs:
        for pref_type, pref_data in learned_prefs.items():
            print(f"  {pref_type}: {pref_data}")
    else:
        print("  No preferences learned yet")
    
    print("\n📈 Preference Learning Features Demonstrated:")
    print("-" * 50)
    print("✓ User interaction tracking (view, select, save, reject)")
    print("✓ Feedback collection and processing (ratings, implementation)")
    print("✓ Pattern analysis from user behavior")
    print("✓ Implicit preference learning (crop preferences, risk tolerance)")
    print("✓ Preference weight adjustment based on feedback")
    print("✓ Learning confidence calculation")
    print("✓ Comprehensive learning insights")
    
    print("\n🚀 Integration Ready:")
    print("-" * 30)
    print("• Database schema created (004_preference_learning_tables.sql)")
    print("• API endpoints implemented (/api/v1/crop-taxonomy/learning/*)")
    print("• Service integrated into crop taxonomy system")
    print("• Comprehensive test suite available")
    
    print(f"\n✅ Preference Learning System Demo Complete!")
    print(f"🌾 Ready for TICKET-005_crop-type-filtering-3.2 completion")


if __name__ == "__main__":
    run_demo()