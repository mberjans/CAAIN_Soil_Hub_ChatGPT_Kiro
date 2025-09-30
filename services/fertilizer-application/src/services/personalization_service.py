"""
Personalization Service for Fertilizer Application Education.

This service provides personalized content recommendations, learning paths,
and educational experiences tailored to individual user profiles, farm
characteristics, and learning preferences.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timedelta
from enum import Enum

from src.models.educational_models import (
    EducationalContent, TrainingModule, LearningPath, ContentType, ContentCategory,
    DifficultyLevel, LearningObjective, UserProfile, ContentRecommendation
)
from src.models.application_models import ApplicationMethodType, EquipmentType, FertilizerForm

logger = logging.getLogger(__name__)


class LearningStyle(str, Enum):
    """Learning style preferences."""
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"


class ContentPreference(str, Enum):
    """Content format preferences."""
    TEXT_GUIDES = "text_guides"
    VIDEO_TUTORIALS = "video_tutorials"
    INTERACTIVE_SIMULATIONS = "interactive_simulations"
    VIRTUAL_REALITY = "virtual_reality"
    CASE_STUDIES = "case_studies"
    EXPERT_INSIGHTS = "expert_insights"


class PersonalizationService:
    """Service for personalized educational content and experiences."""
    
    def __init__(self):
        self.user_profiles = {}
        self.learning_preferences = {}
        self.content_recommendations = {}
        self.learning_paths = {}
        self.adaptation_algorithms = {}
        self._initialize_personalization_algorithms()
    
    def _initialize_personalization_algorithms(self):
        """Initialize personalization algorithms and models."""
        self.adaptation_algorithms = {
            "content_filtering": {
                "collaborative": "Recommend based on similar users",
                "content_based": "Recommend based on content similarity",
                "hybrid": "Combine collaborative and content-based"
            },
            "learning_path_optimization": {
                "difficulty_progression": "Gradual difficulty increase",
                "skill_based": "Based on skill gaps",
                "goal_oriented": "Based on learning goals"
            },
            "content_adaptation": {
                "format_preference": "Adapt to preferred formats",
                "pace_adjustment": "Adjust to learning pace",
                "context_aware": "Adapt to farm context"
            }
        }
    
    async def create_user_profile(
        self,
        user_id: str,
        profile_data: Dict[str, Any]
    ) -> UserProfile:
        """Create personalized user profile."""
        try:
            user_profile = UserProfile(
                user_id=user_id,
                experience_level=profile_data.get("experience_level", DifficultyLevel.BEGINNER),
                primary_crops=profile_data.get("primary_crops", []),
                farm_size_acres=profile_data.get("farm_size_acres", 0),
                equipment_available=profile_data.get("equipment_available", []),
                learning_preferences=profile_data.get("learning_preferences", {}),
                time_availability=profile_data.get("time_availability", "medium"),
                learning_style=profile_data.get("learning_style", LearningStyle.VISUAL),
                region=profile_data.get("region", ""),
                goals=profile_data.get("goals", []),
                interests=profile_data.get("interests", []),
                constraints=profile_data.get("constraints", [])
            )
            
            # Store profile
            self.user_profiles[user_id] = user_profile
            
            # Initialize learning preferences
            await self._initialize_learning_preferences(user_id, user_profile)
            
            return user_profile
            
        except Exception as e:
            logger.error(f"Error creating user profile: {e}")
            raise
    
    async def _initialize_learning_preferences(
        self,
        user_id: str,
        user_profile: UserProfile
    ):
        """Initialize learning preferences based on user profile."""
        preferences = {
            "content_formats": [],
            "difficulty_preference": user_profile.experience_level,
            "duration_preference": "medium",
            "interactive_preference": True,
            "practical_focus": True,
            "regional_relevance": True
        }
        
        # Set preferences based on experience level
        if user_profile.experience_level == DifficultyLevel.BEGINNER:
            preferences["content_formats"] = [ContentPreference.TEXT_GUIDES, ContentPreference.VIDEO_TUTORIALS]
            preferences["duration_preference"] = "short"
            preferences["practical_focus"] = True
        elif user_profile.experience_level == DifficultyLevel.INTERMEDIATE:
            preferences["content_formats"] = [ContentPreference.VIDEO_TUTORIALS, ContentPreference.INTERACTIVE_SIMULATIONS]
            preferences["duration_preference"] = "medium"
            preferences["practical_focus"] = True
        else:
            preferences["content_formats"] = [ContentPreference.INTERACTIVE_SIMULATIONS, ContentPreference.EXPERT_INSIGHTS]
            preferences["duration_preference"] = "long"
            preferences["practical_focus"] = False
        
        # Set preferences based on learning style
        if user_profile.learning_style == LearningStyle.VISUAL:
            preferences["content_formats"].extend([ContentPreference.VIDEO_TUTORIALS, ContentPreference.INTERACTIVE_SIMULATIONS])
        elif user_profile.learning_style == LearningStyle.AUDITORY:
            preferences["content_formats"].extend([ContentPreference.VIDEO_TUTORIALS, ContentPreference.EXPERT_INSIGHTS])
        elif user_profile.learning_style == LearningStyle.KINESTHETIC:
            preferences["content_formats"].extend([ContentPreference.INTERACTIVE_SIMULATIONS, ContentPreference.VIRTUAL_REALITY])
        else:  # Reading/Writing
            preferences["content_formats"].extend([ContentPreference.TEXT_GUIDES, ContentPreference.CASE_STUDIES])
        
        # Set preferences based on time availability
        if user_profile.time_availability == "low":
            preferences["duration_preference"] = "short"
        elif user_profile.time_availability == "high":
            preferences["duration_preference"] = "long"
        
        self.learning_preferences[user_id] = preferences
    
    async def get_personalized_content(
        self,
        user_id: str,
        application_methods: List[ApplicationMethodType],
        content_categories: Optional[List[ContentCategory]] = None
    ) -> List[ContentRecommendation]:
        """Get personalized content recommendations."""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                raise ValueError(f"User profile {user_id} not found")
            
            preferences = self.learning_preferences.get(user_id, {})
            
            # Generate content recommendations
            recommendations = []
            
            # Get content for each application method
            for method in application_methods:
                method_content = await self._get_method_content(method, user_profile, preferences)
                recommendations.extend(method_content)
            
            # Filter by content categories if specified
            if content_categories:
                recommendations = [
                    rec for rec in recommendations
                    if rec.category in content_categories
                ]
            
            # Score and rank recommendations
            scored_recommendations = await self._score_content_recommendations(
                recommendations, user_profile, preferences
            )
            
            # Sort by relevance score
            scored_recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return scored_recommendations[:20]  # Return top 20 recommendations
            
        except Exception as e:
            logger.error(f"Error getting personalized content: {e}")
            return []
    
    async def _get_method_content(
        self,
        application_method: ApplicationMethodType,
        user_profile: UserProfile,
        preferences: Dict[str, Any]
    ) -> List[ContentRecommendation]:
        """Get content for specific application method."""
        recommendations = []
        
        # Generate content recommendations based on method
        if application_method == ApplicationMethodType.BROADCAST:
            recommendations.extend([
                ContentRecommendation(
                    content_id="broadcast_basics_guide",
                    title="Broadcast Application Fundamentals",
                    content_type=ContentType.TEXT_GUIDE,
                    category=ContentCategory.APPLICATION_METHODS,
                    difficulty_level=DifficultyLevel.BEGINNER,
                    duration_minutes=45,
                    description="Complete guide to broadcast fertilizer application",
                    relevance_score=0.8,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="broadcast_1",
                            description="Understand broadcast application principles",
                            category="knowledge"
                        )
                    ],
                    tags=["broadcast", "fertilizer", "application", "beginner"]
                ),
                ContentRecommendation(
                    content_id="broadcast_calibration_video",
                    title="Broadcast Spreader Calibration",
                    content_type=ContentType.VIDEO_TUTORIAL,
                    category=ContentCategory.APPLICATION_METHODS,
                    difficulty_level=DifficultyLevel.INTERMEDIATE,
                    duration_minutes=25,
                    description="Step-by-step calibration tutorial",
                    relevance_score=0.9,
                    learning_objectives=[
                        LearningObjective(
                            objective_id="calibration_1",
                            description="Learn calibration procedures",
                            category="skill"
                        )
                    ],
                    tags=["broadcast", "calibration", "video", "intermediate"]
                )
            ])
        
        return recommendations
    
    async def _score_content_recommendations(
        self,
        recommendations: List[ContentRecommendation],
        user_profile: UserProfile,
        preferences: Dict[str, Any]
    ) -> List[ContentRecommendation]:
        """Score content recommendations based on user preferences."""
        for recommendation in recommendations:
            score = 0.0
            
            # Base score
            score += 0.2
            
            # Difficulty level match
            if recommendation.difficulty_level == user_profile.experience_level:
                score += 0.3
            elif abs(recommendation.difficulty_level.value - user_profile.experience_level.value) == 1:
                score += 0.1
            
            # Content format preference
            preferred_formats = preferences.get("content_formats", [])
            if recommendation.content_type.value in [fmt.value for fmt in preferred_formats]:
                score += 0.2
            
            # Duration preference
            duration_pref = preferences.get("duration_preference", "medium")
            duration = recommendation.duration_minutes or 30
            
            if duration_pref == "short" and duration <= 30:
                score += 0.1
            elif duration_pref == "medium" and 30 < duration <= 60:
                score += 0.1
            elif duration_pref == "long" and duration > 60:
                score += 0.1
            
            # Farm size relevance
            farm_size = user_profile.farm_size_acres
            if farm_size > 1000 and "large" in recommendation.tags:
                score += 0.1
            elif farm_size < 100 and "small" in recommendation.tags:
                score += 0.1
            
            # Equipment relevance
            equipment_available = user_profile.equipment_available
            for equipment in equipment_available:
                if equipment.value in recommendation.tags:
                    score += 0.1
            
            # Crop relevance
            primary_crops = user_profile.primary_crops
            for crop in primary_crops:
                if crop.lower() in recommendation.tags:
                    score += 0.1
            
            # Regional relevance
            if preferences.get("regional_relevance", True):
                region = user_profile.region
                if region.lower() in recommendation.description.lower():
                    score += 0.1
            
            recommendation.relevance_score = min(1.0, score)
        
        return recommendations
    
    async def generate_learning_path(
        self,
        user_id: str,
        learning_goals: List[str],
        application_methods: List[ApplicationMethodType]
    ) -> LearningPath:
        """Generate personalized learning path."""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                raise ValueError(f"User profile {user_id} not found")
            
            preferences = self.learning_preferences.get(user_id, {})
            
            # Generate learning path based on goals and methods
            learning_path = LearningPath(
                path_id=str(uuid4()),
                title=f"Personalized Learning Path for {user_profile.experience_level.value.title()}",
                description=f"Customized learning path for {', '.join([method.value for method in application_methods])}",
                category=ContentCategory.APPLICATION_METHODS,
                difficulty_level=user_profile.experience_level,
                learning_objectives=[
                    LearningObjective(
                        objective_id=f"goal_{i}",
                        description=goal,
                        category="knowledge"
                    )
                    for i, goal in enumerate(learning_goals)
                ],
                content_items=[],
                estimated_duration_minutes=0,
                prerequisites=[],
                assessment_questions=[],
                completion_criteria={
                    "min_score": 0.8,
                    "required_modules": len(application_methods),
                    "practical_assessment": True
                }
            )
            
            # Add content items based on application methods
            for method in application_methods:
                method_content = await self._get_method_content(method, user_profile, preferences)
                learning_path.content_items.extend(method_content[:3])  # Top 3 per method
            
            # Calculate estimated duration
            learning_path.estimated_duration_minutes = sum(
                content.duration_minutes or 30 for content in learning_path.content_items
            )
            
            # Set prerequisites based on experience level
            if user_profile.experience_level == DifficultyLevel.BEGINNER:
                learning_path.prerequisites = ["Basic agricultural knowledge", "Equipment safety awareness"]
            elif user_profile.experience_level == DifficultyLevel.INTERMEDIATE:
                learning_path.prerequisites = ["Equipment operation experience", "Basic fertilizer knowledge"]
            else:
                learning_path.prerequisites = ["Advanced equipment experience", "Comprehensive fertilizer knowledge"]
            
            return learning_path
            
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            raise
    
    async def adapt_content_difficulty(
        self,
        user_id: str,
        content_id: str,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt content difficulty based on user performance."""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                raise ValueError(f"User profile {user_id} not found")
            
            adaptation_result = {
                "content_id": content_id,
                "original_difficulty": user_profile.experience_level,
                "adapted_difficulty": user_profile.experience_level,
                "adaptation_reason": "",
                "recommendations": []
            }
            
            # Analyze performance data
            completion_time = performance_data.get("completion_time_minutes", 0)
            score = performance_data.get("score", 0.0)
            attempts = performance_data.get("attempts", 1)
            
            # Adapt difficulty based on performance
            if score >= 0.9 and completion_time < 30:
                # High performance - suggest more challenging content
                adaptation_result["adapted_difficulty"] = DifficultyLevel.ADVANCED
                adaptation_result["adaptation_reason"] = "High performance indicates readiness for advanced content"
                adaptation_result["recommendations"].append("Try advanced content and simulations")
            elif score < 0.6 or attempts > 3:
                # Low performance - suggest easier content
                adaptation_result["adapted_difficulty"] = DifficultyLevel.BEGINNER
                adaptation_result["adaptation_reason"] = "Performance indicates need for foundational content"
                adaptation_result["recommendations"].append("Review basic concepts and try beginner content")
            else:
                # Moderate performance - maintain current level
                adaptation_result["adapted_difficulty"] = user_profile.experience_level
                adaptation_result["adaptation_reason"] = "Performance appropriate for current level"
                adaptation_result["recommendations"].append("Continue with current difficulty level")
            
            return adaptation_result
            
        except Exception as e:
            logger.error(f"Error adapting content difficulty: {e}")
            raise
    
    async def track_learning_progress(
        self,
        user_id: str,
        content_id: str,
        progress_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track user learning progress and update personalization."""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                raise ValueError(f"User profile {user_id} not found")
            
            # Update learning preferences based on progress
            preferences = self.learning_preferences.get(user_id, {})
            
            # Track content format preferences
            content_type = progress_data.get("content_type")
            if content_type:
                if progress_data.get("completed", False):
                    # User completed this format - increase preference
                    if content_type not in preferences.get("content_formats", []):
                        preferences.setdefault("content_formats", []).append(content_type)
            
            # Track difficulty preferences
            difficulty = progress_data.get("difficulty_level")
            if difficulty and progress_data.get("score", 0) >= 0.8:
                # High score - user may be ready for higher difficulty
                if difficulty == user_profile.experience_level:
                    # Consider promoting to next level
                    pass
            
            # Track duration preferences
            duration = progress_data.get("duration_minutes", 0)
            if duration > 0:
                if progress_data.get("completed", False):
                    # User completed this duration - may prefer similar
                    if duration <= 30:
                        preferences["duration_preference"] = "short"
                    elif duration <= 60:
                        preferences["duration_preference"] = "medium"
                    else:
                        preferences["duration_preference"] = "long"
            
            # Update preferences
            self.learning_preferences[user_id] = preferences
            
            return {
                "user_id": user_id,
                "content_id": content_id,
                "progress_tracked": True,
                "preferences_updated": True,
                "next_recommendations": await self._generate_next_recommendations(user_id, content_id)
            }
            
        except Exception as e:
            logger.error(f"Error tracking learning progress: {e}")
            raise
    
    async def _generate_next_recommendations(
        self,
        user_id: str,
        completed_content_id: str
    ) -> List[str]:
        """Generate next content recommendations based on completed content."""
        try:
            recommendations = []
            
            # Simple recommendation logic based on completed content
            if "broadcast" in completed_content_id:
                recommendations.extend([
                    "broadcast_advanced_guide",
                    "broadcast_calibration_video",
                    "broadcast_simulation"
                ])
            elif "foliar" in completed_content_id:
                recommendations.extend([
                    "foliar_timing_guide",
                    "foliar_formulation_video",
                    "foliar_simulation"
                ])
            elif "safety" in completed_content_id:
                recommendations.extend([
                    "equipment_safety_guide",
                    "emergency_response_video",
                    "safety_certification"
                ])
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating next recommendations: {e}")
            return []
    
    async def get_personalized_dashboard(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Generate personalized dashboard for user."""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                raise ValueError(f"User profile {user_id} not found")
            
            preferences = self.learning_preferences.get(user_id, {})
            
            dashboard = {
                "user_id": user_id,
                "welcome_message": f"Welcome back, {user_profile.experience_level.value.title()} learner!",
                "quick_actions": [],
                "recommended_content": [],
                "learning_progress": {},
                "upcoming_tasks": [],
                "achievements": [],
                "personalized_insights": []
            }
            
            # Generate quick actions based on profile
            if user_profile.experience_level == DifficultyLevel.BEGINNER:
                dashboard["quick_actions"] = [
                    "Start Basic Safety Training",
                    "Learn Equipment Basics",
                    "Take Knowledge Assessment"
                ]
            elif user_profile.experience_level == DifficultyLevel.INTERMEDIATE:
                dashboard["quick_actions"] = [
                    "Advanced Techniques",
                    "Equipment Optimization",
                    "Safety Certification"
                ]
            else:
                dashboard["quick_actions"] = [
                    "Expert Insights",
                    "Advanced Simulations",
                    "Mentor Others"
                ]
            
            # Generate personalized insights
            farm_size = user_profile.farm_size_acres
            if farm_size > 1000:
                dashboard["personalized_insights"].append(
                    "Large farm operations benefit from precision agriculture technologies"
                )
            elif farm_size < 100:
                dashboard["personalized_insights"].append(
                    "Small farms can achieve significant efficiency gains with proper techniques"
                )
            
            # Add equipment-specific insights
            equipment_available = user_profile.equipment_available
            if EquipmentType.SPREADER in equipment_available:
                dashboard["personalized_insights"].append(
                    "Broadcast application requires careful calibration for optimal results"
                )
            if EquipmentType.SPRAYER in equipment_available:
                dashboard["personalized_insights"].append(
                    "Foliar application timing is critical for maximum nutrient uptake"
                )
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Error generating personalized dashboard: {e}")
            raise
    
    async def update_user_preferences(
        self,
        user_id: str,
        preference_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user learning preferences."""
        try:
            user_profile = self.user_profiles.get(user_id)
            if not user_profile:
                raise ValueError(f"User profile {user_id} not found")
            
            preferences = self.learning_preferences.get(user_id, {})
            
            # Update preferences
            for key, value in preference_updates.items():
                preferences[key] = value
            
            # Update user profile if needed
            if "learning_style" in preference_updates:
                user_profile.learning_style = preference_updates["learning_style"]
            if "time_availability" in preference_updates:
                user_profile.time_availability = preference_updates["time_availability"]
            
            # Store updated preferences
            self.learning_preferences[user_id] = preferences
            self.user_profiles[user_id] = user_profile
            
            return {
                "user_id": user_id,
                "preferences_updated": True,
                "updated_preferences": preferences,
                "recommendations": "Preferences updated successfully. Content recommendations will be refreshed."
            }
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            raise