"""
Database operations for educational content and training system.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from src.models.educational_models import (
    EducationalContent, TrainingModule, LearningPath, LearningProgress,
    ExpertInsight, CaseStudy, InteractiveSimulation, VirtualRealityTraining,
    Certification, UserProfile, ContentType, ContentCategory, DifficultyLevel
)
from src.models.application_models import ApplicationMethodType, EquipmentType

logger = logging.getLogger(__name__)


class EducationDatabase:
    """Database operations for educational content management."""
    
    def __init__(self):
        self.content_collection = {}
        self.user_progress_collection = {}
        self.certifications_collection = {}
        self.expert_insights_collection = {}
        self.case_studies_collection = {}
        self.simulations_collection = {}
        self.vr_trainings_collection = {}
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database with sample data."""
        # Initialize content collection
        self.content_collection = {
            "broadcast_basics_guide": {
                "content_id": "broadcast_basics_guide",
                "title": "Broadcast Application Fundamentals",
                "content_type": ContentType.TEXT_GUIDE.value,
                "category": ContentCategory.APPLICATION_METHODS.value,
                "difficulty_level": DifficultyLevel.BEGINNER.value,
                "description": "Complete guide to broadcast fertilizer application",
                "duration_minutes": 45,
                "learning_objectives": [
                    {
                        "objective_id": "broadcast_1",
                        "description": "Understand broadcast application principles",
                        "category": "knowledge"
                    },
                    {
                        "objective_id": "broadcast_2",
                        "description": "Learn equipment calibration techniques",
                        "category": "skill"
                    },
                    {
                        "objective_id": "broadcast_3",
                        "description": "Master safety protocols for broadcast application",
                        "category": "safety"
                    }
                ],
                "content_data": {
                    "sections": [
                        "Introduction to Broadcast Application",
                        "Equipment Types and Selection",
                        "Calibration and Setup",
                        "Application Techniques",
                        "Safety Considerations",
                        "Troubleshooting Common Issues"
                    ],
                    "key_points": [
                        "Uniform distribution is critical for broadcast application",
                        "Wind conditions significantly affect application accuracy",
                        "Proper calibration ensures accurate nutrient delivery",
                        "Safety equipment is essential for all operators"
                    ]
                },
                "tags": ["broadcast", "fertilizer", "application", "beginner"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "expert_reviewed": True,
                "validation_score": 0.95
            },
            "broadcast_calibration_video": {
                "content_id": "broadcast_calibration_video",
                "title": "Broadcast Spreader Calibration",
                "content_type": ContentType.VIDEO_TUTORIAL.value,
                "category": ContentCategory.APPLICATION_METHODS.value,
                "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
                "description": "Step-by-step calibration tutorial",
                "duration_minutes": 25,
                "content_url": "/videos/broadcast_calibration.mp4",
                "learning_objectives": [
                    {
                        "objective_id": "calibration_1",
                        "description": "Learn calibration procedures",
                        "category": "skill"
                    }
                ],
                "tags": ["broadcast", "calibration", "video", "intermediate"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "expert_reviewed": True,
                "validation_score": 0.92
            },
            "fertilizer_safety_guide": {
                "content_id": "fertilizer_safety_guide",
                "title": "Fertilizer Application Safety Manual",
                "content_type": ContentType.SAFETY_TRAINING.value,
                "category": ContentCategory.SAFETY.value,
                "difficulty_level": DifficultyLevel.BEGINNER.value,
                "description": "Comprehensive safety guide for fertilizer application",
                "duration_minutes": 60,
                "learning_objectives": [
                    {
                        "objective_id": "safety_1",
                        "description": "Understand safety protocols",
                        "category": "safety"
                    },
                    {
                        "objective_id": "safety_2",
                        "description": "Learn emergency procedures",
                        "category": "safety"
                    }
                ],
                "content_data": {
                    "sections": [
                        "Personal Protective Equipment",
                        "Chemical Handling Safety",
                        "Equipment Safety Checks",
                        "Emergency Response Procedures",
                        "Environmental Protection",
                        "Regulatory Compliance"
                    ]
                },
                "tags": ["safety", "fertilizer", "training", "beginner"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "expert_reviewed": True,
                "validation_score": 0.98
            }
        }
        
        # Initialize expert insights collection
        self.expert_insights_collection = {
            "broadcast_expert_1": {
                "insight_id": "broadcast_expert_1",
                "title": "Wind Management in Broadcast Application",
                "expert_name": "Dr. Sarah Johnson",
                "expert_credentials": "Extension Specialist, University of Nebraska",
                "content": "Wind is the most critical factor in broadcast application. Always check wind speed and direction before application. Ideal conditions are wind speeds below 10 mph with consistent direction. Consider using GPS guidance systems to maintain accuracy even in challenging conditions.",
                "application_methods": [ApplicationMethodType.BROADCAST.value],
                "tags": ["wind", "accuracy", "guidance"],
                "credibility_score": 0.95,
                "created_at": datetime.utcnow().isoformat()
            },
            "foliar_expert_1": {
                "insight_id": "foliar_expert_1",
                "title": "Foliar Application Timing for Maximum Uptake",
                "expert_name": "Dr. Michael Chen",
                "expert_credentials": "Plant Physiologist, Iowa State University",
                "content": "The optimal time for foliar application is early morning (6-8 AM) when stomata are open and humidity is high. Avoid applications during hot, dry conditions as this can cause phytotoxicity. Always include a surfactant to improve coverage and uptake.",
                "application_methods": [ApplicationMethodType.FOLIAR.value],
                "tags": ["timing", "uptake", "phytotoxicity"],
                "credibility_score": 0.92,
                "created_at": datetime.utcnow().isoformat()
            }
        }
        
        # Initialize case studies collection
        self.case_studies_collection = {
            "case_study_1": {
                "case_id": "case_study_1",
                "title": "Precision Broadcast Application Success Story",
                "farm_name": "Green Valley Farms",
                "location": "Central Iowa",
                "farm_size_acres": 1200,
                "crop_type": "Corn",
                "application_method": ApplicationMethodType.BROADCAST.value,
                "scenario_description": "Large-scale corn operation implementing precision broadcast application with GPS guidance",
                "challenge": "Achieving uniform application across 1200 acres with varying field conditions",
                "solution_implemented": "GPS-guided broadcast application with variable rate technology",
                "results_achieved": {
                    "yield_increase": "8%",
                    "fertilizer_efficiency": "15% improvement",
                    "cost_savings": "$12,000 annually",
                    "environmental_impact": "Reduced runoff by 20%"
                },
                "lessons_learned": [
                    "GPS guidance significantly improves application accuracy",
                    "Variable rate technology optimizes fertilizer use",
                    "Proper calibration is essential for success",
                    "Regular equipment maintenance prevents issues"
                ],
                "key_factors": ["GPS guidance", "variable rate", "calibration", "maintenance"],
                "success_metrics": {
                    "accuracy_improvement": "25%",
                    "time_savings": "3 hours per application",
                    "fuel_efficiency": "12% improvement"
                },
                "created_at": datetime.utcnow().isoformat()
            }
        }
        
        # Initialize simulations collection
        self.simulations_collection = {
            "broadcast_simulator": {
                "simulation_id": "broadcast_simulator",
                "title": "Broadcast Application Simulator",
                "description": "Interactive simulation for broadcast application practice",
                "simulation_type": "equipment_operation",
                "difficulty_level": DifficultyLevel.INTERMEDIATE.value,
                "estimated_duration_minutes": 30,
                "learning_objectives": [
                    {
                        "objective_id": "sim_1",
                        "description": "Practice broadcast application techniques",
                        "category": "skill"
                    }
                ],
                "simulation_scenarios": [
                    "Calibration practice",
                    "Wind condition adjustment",
                    "Field boundary management",
                    "Overlap optimization",
                    "Equipment troubleshooting"
                ],
                "interactive_elements": [
                    "Equipment controls",
                    "Environmental conditions",
                    "Field parameters",
                    "Real-time feedback"
                ],
                "assessment_criteria": {
                    "accuracy_score": "Application uniformity",
                    "efficiency_score": "Time and fuel usage",
                    "safety_score": "Safety protocol adherence"
                },
                "created_at": datetime.utcnow().isoformat()
            }
        }
        
        # Initialize certifications collection
        self.certifications_collection = {
            "safety_certification": {
                "certification_id": "safety_certification",
                "name": "Fertilizer Application Safety Certification",
                "description": "Certification in fertilizer application safety protocols",
                "requirements": [
                    "Complete safety training module",
                    "Pass safety assessment with 90% score",
                    "Demonstrate proper PPE usage",
                    "Complete emergency response training"
                ],
                "validity_period_months": 24,
                "renewal_requirements": ["Annual safety refresher", "Updated regulations training"],
                "created_at": datetime.utcnow().isoformat()
            },
            "broadcast_certification": {
                "certification_id": "broadcast_certification",
                "name": "Broadcast Application Certification",
                "description": "Certification in broadcast fertilizer application",
                "requirements": [
                    "Complete broadcast application training",
                    "Pass equipment operation assessment",
                    "Demonstrate calibration proficiency",
                    "Complete practical application test"
                ],
                "validity_period_months": 36,
                "renewal_requirements": ["Equipment updates training", "Technique refresher"],
                "created_at": datetime.utcnow().isoformat()
            }
        }
    
    async def get_content_by_id(self, content_id: str) -> Optional[EducationalContent]:
        """Get educational content by ID."""
        try:
            content_data = self.content_collection.get(content_id)
            if not content_data:
                return None
            
            return EducationalContent(**content_data)
            
        except Exception as e:
            logger.error(f"Error retrieving content {content_id}: {e}")
            return None
    
    async def get_content_by_category(
        self,
        category: ContentCategory,
        difficulty_level: Optional[DifficultyLevel] = None,
        content_type: Optional[ContentType] = None,
        max_duration_minutes: Optional[int] = None
    ) -> List[EducationalContent]:
        """Get educational content filtered by category and criteria."""
        try:
            results = []
            
            for content_data in self.content_collection.values():
                # Filter by category
                if content_data["category"] != category.value:
                    continue
                
                # Filter by difficulty level
                if difficulty_level and content_data["difficulty_level"] != difficulty_level.value:
                    continue
                
                # Filter by content type
                if content_type and content_data["content_type"] != content_type.value:
                    continue
                
                # Filter by duration
                if max_duration_minutes and content_data.get("duration_minutes", 0) > max_duration_minutes:
                    continue
                
                results.append(EducationalContent(**content_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving content by category: {e}")
            return []
    
    async def search_content(
        self,
        query: str,
        category: Optional[ContentCategory] = None,
        difficulty_level: Optional[DifficultyLevel] = None,
        content_type: Optional[ContentType] = None,
        tags: Optional[List[str]] = None
    ) -> List[EducationalContent]:
        """Search educational content using text queries and filters."""
        try:
            results = []
            query_lower = query.lower()
            
            for content_data in self.content_collection.values():
                # Text search in title and description
                title_match = query_lower in content_data.get("title", "").lower()
                desc_match = query_lower in content_data.get("description", "").lower()
                
                if not (title_match or desc_match):
                    continue
                
                # Apply filters
                if category and content_data["category"] != category.value:
                    continue
                
                if difficulty_level and content_data["difficulty_level"] != difficulty_level.value:
                    continue
                
                if content_type and content_data["content_type"] != content_type.value:
                    continue
                
                if tags:
                    content_tags = content_data.get("tags", [])
                    if not any(tag in content_tags for tag in tags):
                        continue
                
                results.append(EducationalContent(**content_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching content: {e}")
            return []
    
    async def get_expert_insights(
        self,
        application_methods: Optional[List[ApplicationMethodType]] = None
    ) -> List[ExpertInsight]:
        """Get expert insights filtered by application methods."""
        try:
            results = []
            
            for insight_data in self.expert_insights_collection.values():
                # Filter by application methods
                if application_methods:
                    insight_methods = [ApplicationMethodType(method) for method in insight_data["application_methods"]]
                    if not any(method in insight_methods for method in application_methods):
                        continue
                
                results.append(ExpertInsight(**insight_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving expert insights: {e}")
            return []
    
    async def get_case_studies(
        self,
        application_methods: Optional[List[ApplicationMethodType]] = None,
        farm_size_range: Optional[tuple] = None
    ) -> List[CaseStudy]:
        """Get case studies filtered by criteria."""
        try:
            results = []
            
            for case_data in self.case_studies_collection.values():
                # Filter by application methods
                if application_methods:
                    case_method = ApplicationMethodType(case_data["application_method"])
                    if case_method not in application_methods:
                        continue
                
                # Filter by farm size range
                if farm_size_range:
                    farm_size = case_data["farm_size_acres"]
                    if not (farm_size_range[0] <= farm_size <= farm_size_range[1]):
                        continue
                
                results.append(CaseStudy(**case_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving case studies: {e}")
            return []
    
    async def get_interactive_simulations(
        self,
        difficulty_level: Optional[DifficultyLevel] = None,
        simulation_type: Optional[str] = None
    ) -> List[InteractiveSimulation]:
        """Get interactive simulations filtered by criteria."""
        try:
            results = []
            
            for sim_data in self.simulations_collection.values():
                # Filter by difficulty level
                if difficulty_level and sim_data["difficulty_level"] != difficulty_level.value:
                    continue
                
                # Filter by simulation type
                if simulation_type and sim_data["simulation_type"] != simulation_type:
                    continue
                
                results.append(InteractiveSimulation(**sim_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving simulations: {e}")
            return []
    
    async def get_certifications(
        self,
        application_method: Optional[ApplicationMethodType] = None
    ) -> List[Certification]:
        """Get certifications filtered by application method."""
        try:
            results = []
            
            for cert_data in self.certifications_collection.values():
                # Always include safety certification
                if cert_data["certification_id"] == "safety_certification":
                    results.append(Certification(**cert_data))
                    continue
                
                # Filter by application method for method-specific certifications
                if application_method:
                    if cert_data["certification_id"] == f"{application_method.value}_certification":
                        results.append(Certification(**cert_data))
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving certifications: {e}")
            return []
    
    async def save_user_progress(self, user_id: str, progress: LearningProgress) -> bool:
        """Save user learning progress."""
        try:
            progress_data = {
                "user_id": progress.user_id,
                "completed_content": progress.completed_content,
                "in_progress_content": progress.in_progress_content,
                "learning_paths_started": progress.learning_paths_started,
                "learning_paths_completed": progress.learning_paths_completed,
                "certifications_earned": [cert.dict() for cert in progress.certifications_earned],
                "skill_assessments": progress.skill_assessments,
                "learning_goals": progress.learning_goals,
                "last_activity": progress.last_activity.isoformat(),
                "total_learning_time_minutes": progress.total_learning_time_minutes,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.user_progress_collection[user_id] = progress_data
            return True
            
        except Exception as e:
            logger.error(f"Error saving user progress: {e}")
            return False
    
    async def get_user_progress(self, user_id: str) -> Optional[LearningProgress]:
        """Get user learning progress."""
        try:
            progress_data = self.user_progress_collection.get(user_id)
            if not progress_data:
                return None
            
            # Convert back to LearningProgress object
            progress_data["last_activity"] = datetime.fromisoformat(progress_data["last_activity"])
            progress_data["certifications_earned"] = [
                Certification(**cert) for cert in progress_data["certifications_earned"]
            ]
            
            return LearningProgress(**progress_data)
            
        except Exception as e:
            logger.error(f"Error retrieving user progress: {e}")
            return None
    
    async def create_content(self, content: EducationalContent) -> bool:
        """Create new educational content."""
        try:
            content_data = content.dict()
            content_data["created_at"] = datetime.utcnow().isoformat()
            content_data["updated_at"] = datetime.utcnow().isoformat()
            
            self.content_collection[content.content_id] = content_data
            return True
            
        except Exception as e:
            logger.error(f"Error creating content: {e}")
            return False
    
    async def update_content(self, content_id: str, content: EducationalContent) -> bool:
        """Update existing educational content."""
        try:
            if content_id not in self.content_collection:
                return False
            
            content_data = content.dict()
            content_data["updated_at"] = datetime.utcnow().isoformat()
            
            self.content_collection[content_id] = content_data
            return True
            
        except Exception as e:
            logger.error(f"Error updating content: {e}")
            return False
    
    async def delete_content(self, content_id: str) -> bool:
        """Delete educational content."""
        try:
            if content_id not in self.content_collection:
                return False
            
            del self.content_collection[content_id]
            return True
            
        except Exception as e:
            logger.error(f"Error deleting content: {e}")
            return False
    
    async def get_content_statistics(self) -> Dict[str, Any]:
        """Get content statistics for analytics."""
        try:
            stats = {
                "total_content_items": len(self.content_collection),
                "content_by_type": {},
                "content_by_category": {},
                "content_by_difficulty": {},
                "expert_reviewed_count": 0,
                "average_validation_score": 0.0
            }
            
            total_score = 0
            score_count = 0
            
            for content_data in self.content_collection.values():
                # Count by type
                content_type = content_data["content_type"]
                stats["content_by_type"][content_type] = stats["content_by_type"].get(content_type, 0) + 1
                
                # Count by category
                category = content_data["category"]
                stats["content_by_category"][category] = stats["content_by_category"].get(category, 0) + 1
                
                # Count by difficulty
                difficulty = content_data["difficulty_level"]
                stats["content_by_difficulty"][difficulty] = stats["content_by_difficulty"].get(difficulty, 0) + 1
                
                # Count expert reviewed
                if content_data.get("expert_reviewed", False):
                    stats["expert_reviewed_count"] += 1
                
                # Calculate average validation score
                validation_score = content_data.get("validation_score", 0)
                if validation_score > 0:
                    total_score += validation_score
                    score_count += 1
            
            if score_count > 0:
                stats["average_validation_score"] = total_score / score_count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error calculating content statistics: {e}")
            return {}


# Global database instance
education_db = EducationDatabase()