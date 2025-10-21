"""
API routes for educational content and training system.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional, Dict, Any
import logging

from src.models.educational_models import (
    EducationalRequest, EducationalResponse, EducationalContent,
    TrainingModule, LearningPath, UserProfile, ContentRecommendation,
    LearningProgress, Certification, ApplicationMethodType, EquipmentType,
    DifficultyLevel, ContentType, ContentCategory
)
from src.services.education_service import EducationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/education", tags=["education"])


# Dependency injection
async def get_education_service() -> EducationService:
    return EducationService()


@router.post("/content", response_model=EducationalResponse)
async def get_educational_content(
    request: EducationalRequest,
    service: EducationService = Depends(get_education_service)
):
    """
    Get comprehensive educational content based on user needs and preferences.
    
    This endpoint provides personalized educational content including:
    - Interactive tutorials and guides
    - Best practices and case studies
    - Expert insights and recommendations
    - Learning paths and progress tracking
    - Safety training and equipment training
    
    **Agricultural Context:**
    - Content tailored to user's experience level and farm characteristics
    - Method-specific training for different application techniques
    - Safety protocols and environmental stewardship
    - Regional considerations and best practices
    
    **Response includes:**
    - Personalized content recommendations
    - Structured learning paths
    - Expert insights from agricultural professionals
    - Real-world case studies
    - Interactive simulations and VR training
    - Learning progress tracking
    """
    try:
        logger.info("Processing educational content request")
        
        response = await service.get_educational_content(request)
        
        logger.info("Educational content request completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in educational content request: {e}")
        raise HTTPException(status_code=500, detail=f"Educational content request failed: {str(e)}")


@router.get("/content/{content_id}", response_model=EducationalContent)
async def get_content_by_id(
    content_id: str = Path(..., description="Content identifier"),
    service: EducationService = Depends(get_education_service)
):
    """
    Get specific educational content by ID.
    
    Retrieves detailed information about a specific educational content item
    including learning objectives, duration, and content data.
    """
    try:
        content = await service.db.get_content_by_id(content_id)
        if not content:
            raise HTTPException(status_code=404, detail="Content not found")
        
        return content
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving content {content_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Content retrieval failed: {str(e)}")


@router.get("/content", response_model=List[EducationalContent])
async def get_content_by_category(
    category: ContentCategory = Query(..., description="Content category"),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="Difficulty level filter"),
    content_type: Optional[ContentType] = Query(None, description="Content type filter"),
    max_duration_minutes: Optional[int] = Query(None, ge=1, description="Maximum duration filter"),
    service: EducationService = Depends(get_education_service)
):
    """
    Get educational content filtered by category and other criteria.
    
    Allows filtering educational content by:
    - Content category (application methods, safety, equipment, etc.)
    - Difficulty level (beginner, intermediate, advanced)
    - Content type (text guide, video, simulation, etc.)
    - Maximum duration
    """
    try:
        logger.info(f"Getting content for category: {category}")
        
        content = await service.db.get_content_by_category(
            category, difficulty_level, content_type, max_duration_minutes
        )
        
        return content
        
    except Exception as e:
        logger.error(f"Error retrieving content by category: {e}")
        raise HTTPException(status_code=500, detail=f"Content retrieval failed: {str(e)}")


@router.get("/learning-paths", response_model=List[LearningPath])
async def get_learning_paths(
    experience_level: DifficultyLevel = Query(..., description="User experience level"),
    application_methods: Optional[List[ApplicationMethodType]] = Query(None, description="Application methods of interest"),
    service: EducationService = Depends(get_education_service)
):
    """
    Get structured learning paths based on user experience and interests.
    
    Returns recommended learning paths that provide structured progression
    through educational content for specific application methods and
    experience levels.
    """
    try:
        logger.info(f"Getting learning paths for experience level: {experience_level}")
        
        # This would typically generate learning paths based on criteria
        # For now, return empty list
        return []
        
    except Exception as e:
        logger.error(f"Error retrieving learning paths: {e}")
        raise HTTPException(status_code=500, detail=f"Learning paths retrieval failed: {str(e)}")


@router.post("/progress/track")
async def track_learning_progress(
    user_id: str = Query(..., description="User identifier"),
    content_id: str = Query(..., description="Content identifier"),
    progress_data: Dict[str, Any],
    service: EducationService = Depends(get_education_service)
):
    """
    Track user's learning progress for specific content.
    
    Updates the user's learning progress including:
    - Content completion status
    - Time spent on content
    - Assessment scores
    - Learning milestones
    """
    try:
        logger.info(f"Tracking progress for user {user_id}, content {content_id}")
        
        progress = await service.track_learning_progress(user_id, content_id, progress_data)
        
        logger.info("Learning progress tracked successfully")
        return {"success": True, "progress": progress}
        
    except Exception as e:
        logger.error(f"Error tracking learning progress: {e}")
        raise HTTPException(status_code=500, detail=f"Progress tracking failed: {str(e)}")


@router.get("/progress/{user_id}", response_model=LearningProgress)
async def get_learning_progress(
    user_id: str = Path(..., description="User identifier"),
    service: EducationService = Depends(get_education_service)
):
    """
    Get user's learning progress and achievements.
    
    Returns comprehensive learning progress including:
    - Completed content and learning paths
    - Current progress on ongoing content
    - Certifications earned
    - Skill assessments and achievements
    - Learning goals and milestones
    """
    try:
        logger.info(f"Getting learning progress for user: {user_id}")
        
        progress = await service._get_learning_progress(user_id)
        
        if not progress:
            raise HTTPException(status_code=404, detail="User progress not found")
        
        return progress
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving learning progress: {e}")
        raise HTTPException(status_code=500, detail=f"Progress retrieval failed: {str(e)}")


@router.get("/certifications", response_model=List[Certification])
async def get_certification_requirements(
    application_method: ApplicationMethodType = Query(..., description="Application method"),
    experience_level: DifficultyLevel = Query(..., description="User experience level"),
    service: EducationService = Depends(get_education_service)
):
    """
    Get certification requirements for specific application methods.
    
    Returns certification requirements including:
    - Required training modules
    - Assessment criteria
    - Validity periods
    - Renewal requirements
    - Compliance standards
    """
    try:
        logger.info(f"Getting certifications for {application_method}, level {experience_level}")
        
        certifications = await service.get_certification_requirements(application_method, experience_level)
        
        return certifications
        
    except Exception as e:
        logger.error(f"Error retrieving certifications: {e}")
        raise HTTPException(status_code=500, detail=f"Certification retrieval failed: {str(e)}")


@router.get("/content/recommendations", response_model=List[ContentRecommendation])
async def get_personalized_recommendations(
    user_id: str = Query(..., description="User identifier"),
    farm_size_acres: float = Query(..., ge=0, description="Farm size in acres"),
    primary_crops: List[str] = Query(..., description="Primary crops grown"),
    experience_level: DifficultyLevel = Query(..., description="User experience level"),
    equipment_available: List[EquipmentType] = Query(..., description="Available equipment"),
    service: EducationService = Depends(get_education_service)
):
    """
    Get personalized content recommendations based on user profile.
    
    Provides tailored recommendations based on:
    - Farm characteristics and size
    - Crops grown and equipment available
    - User experience level and learning preferences
    - Regional considerations and best practices
    """
    try:
        logger.info(f"Getting personalized recommendations for user: {user_id}")
        
        # Create user profile for recommendations
        user_profile = UserProfile(
            user_id=user_id,
            experience_level=experience_level,
            primary_crops=primary_crops,
            farm_size_acres=farm_size_acres,
            equipment_available=equipment_available,
            learning_preferences={},
            time_availability="medium",
            learning_style="visual"
        )
        
        # Create educational request
        request = EducationalRequest(
            user_profile=user_profile,
            application_methods=[ApplicationMethodType.BROADCAST],  # Default
            equipment_types=equipment_available,
            experience_level=experience_level,
            content_preferences={},
            learning_goals=[],
            farm_characteristics={"farm_size_acres": farm_size_acres}
        )
        
        response = await service.get_educational_content(request)
        
        # Convert to recommendations format
        recommendations = []
        for content in response.recommended_content:
            recommendation = ContentRecommendation(
                content_id=content.content_id,
                title=content.title,
                content_type=content.content_type,
                category=content.category,
                difficulty_level=content.difficulty_level,
                duration_minutes=content.duration_minutes,
                description=content.description,
                relevance_score=0.8,  # Would be calculated based on user profile
                learning_objectives=content.learning_objectives,
                tags=content.tags
            )
            recommendations.append(recommendation)
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting personalized recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Recommendations retrieval failed: {str(e)}")


@router.get("/content/search")
async def search_educational_content(
    query: str = Query(..., description="Search query"),
    category: Optional[ContentCategory] = Query(None, description="Content category filter"),
    difficulty_level: Optional[DifficultyLevel] = Query(None, description="Difficulty level filter"),
    content_type: Optional[ContentType] = Query(None, description="Content type filter"),
    tags: Optional[List[str]] = Query(None, description="Content tags filter"),
    service: EducationService = Depends(get_education_service)
):
    """
    Search educational content using text queries and filters.
    
    Allows searching through educational content using:
    - Text search in titles and descriptions
    - Category and difficulty level filters
    - Content type and tag filters
    - Relevance scoring and ranking
    """
    try:
        logger.info(f"Searching educational content with query: {query}")
        
        results = await service.db.search_content(
            query, category, difficulty_level, content_type, tags
        )
        
        return {
            "results": [content.dict() for content in results],
            "total_count": len(results),
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching educational content: {e}")
        raise HTTPException(status_code=500, detail=f"Content search failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for education service."""
    return {
        "status": "healthy",
        "service": "education",
        "version": "1.0.0",
        "features": [
            "educational_content",
            "learning_paths",
            "progress_tracking",
            "certifications",
            "personalized_recommendations"
        ]
    }