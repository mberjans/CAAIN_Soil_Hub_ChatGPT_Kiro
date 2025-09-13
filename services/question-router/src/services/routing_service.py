"""
Question Routing Service

Routes classified questions to appropriate microservices for processing.
"""

from typing import List
try:
    from ..models.question_models import QuestionType, RoutingDecision
except ImportError:
    from models.question_models import QuestionType, RoutingDecision


class QuestionRoutingService:
    """Service for routing questions to appropriate microservices."""
    
    def __init__(self):
        """Initialize routing service with service mappings."""
        self.service_mappings = self._build_service_mappings()
    
    def _build_service_mappings(self) -> dict:
        """Build mappings from question types to services."""
        return {
            QuestionType.CROP_SELECTION: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 5
            },
            QuestionType.SOIL_FERTILITY: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 1,
                "estimated_time": 4
            },
            QuestionType.CROP_ROTATION: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 6
            },
            QuestionType.NUTRIENT_DEFICIENCY: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "image-analysis", "ai-agent"],
                "priority": 1,
                "estimated_time": 3
            },
            QuestionType.FERTILIZER_TYPE: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 4
            },
            QuestionType.FERTILIZER_APPLICATION: {
                "primary": "recommendation-engine",
                "secondary": ["ai-agent"],
                "priority": 2,
                "estimated_time": 3
            },
            QuestionType.FERTILIZER_TIMING: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 1,
                "estimated_time": 4
            },
            QuestionType.ENVIRONMENTAL_IMPACT: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 5
            },
            QuestionType.COVER_CROPS: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 4
            },
            QuestionType.SOIL_PH: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 1,
                "estimated_time": 3
            },
            QuestionType.MICRONUTRIENTS: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 4
            },
            QuestionType.PRECISION_AGRICULTURE: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 3,
                "estimated_time": 7
            },
            QuestionType.DROUGHT_MANAGEMENT: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 1,
                "estimated_time": 5
            },
            QuestionType.DEFICIENCY_DETECTION: {
                "primary": "image-analysis",
                "secondary": ["recommendation-engine", "ai-agent"],
                "priority": 1,
                "estimated_time": 8
            },
            QuestionType.TILLAGE_PRACTICES: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 4
            },
            QuestionType.COST_EFFECTIVE_STRATEGY: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 1,
                "estimated_time": 6
            },
            QuestionType.WEATHER_IMPACT: {
                "primary": "data-integration",
                "secondary": ["recommendation-engine", "ai-agent"],
                "priority": 2,
                "estimated_time": 4
            },
            QuestionType.TESTING_INTEGRATION: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 3
            },
            QuestionType.SUSTAINABLE_YIELD: {
                "primary": "recommendation-engine",
                "secondary": ["data-integration", "ai-agent"],
                "priority": 2,
                "estimated_time": 6
            },
            QuestionType.GOVERNMENT_PROGRAMS: {
                "primary": "data-integration",
                "secondary": ["recommendation-engine", "ai-agent"],
                "priority": 3,
                "estimated_time": 5
            }
        }
    
    async def route_question(self, question_type: QuestionType) -> RoutingDecision:
        """
        Route a classified question to appropriate services.
        
        Args:
            question_type: The classified question type
            
        Returns:
            RoutingDecision with service routing information
        """
        mapping = self.service_mappings.get(question_type)
        
        if not mapping:
            # Default routing for unknown question types
            return RoutingDecision(
                primary_service="recommendation-engine",
                secondary_services=["ai-agent"],
                processing_priority=3,
                estimated_processing_time=5
            )
        
        return RoutingDecision(
            primary_service=mapping["primary"],
            secondary_services=mapping["secondary"],
            processing_priority=mapping["priority"],
            estimated_processing_time=mapping["estimated_time"]
        )