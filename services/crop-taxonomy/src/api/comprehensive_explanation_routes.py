"""
API routes for comprehensive explanation and reasoning display system.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from ..services.comprehensive_explanation_service import (
    ComprehensiveExplanationService,
    ComprehensiveExplanation,
    ExplanationType,
    ConfidenceLevel
)
from ..models.service_models import (
    VarietyRecommendationRequest,
    VarietyRecommendationResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/explanations", tags=["explanations"])

# Dependency injection
async def get_explanation_service() -> ComprehensiveExplanationService:
    """Get comprehensive explanation service instance."""
    return ComprehensiveExplanationService()

@router.post("/comprehensive", response_model=Dict[str, Any])
async def generate_comprehensive_explanation(
    request: Dict[str, Any],
    explanation_service: ComprehensiveExplanationService = Depends(get_explanation_service)
):
    """
    Generate comprehensive explanation with detailed reasoning, evidence, and educational content.
    
    **Comprehensive Explanation Features:**
    - **Detailed Reasoning**: In-depth analysis of variety selection factors
    - **Evidence Display**: Supporting data from multiple sources with confidence scores
    - **Trade-off Analysis**: Balanced view of strengths and considerations
    - **Risk Assessment**: Comprehensive risk evaluation with mitigation strategies
    - **Economic Analysis**: ROI calculations and cost-benefit analysis
    - **Management Guidance**: Actionable recommendations and best practices
    - **Educational Content**: Learning resources and explanatory content
    - **Accessibility Features**: Screen reader support and keyboard navigation
    
    **Request Schema:**
    ```json
    {
      "variety_data": {
        "variety_id": "uuid",
        "variety_name": "Variety Name",
        "request_id": "unique_request_id",
        "overall_score": 0.85,
        "scores": {
          "yield_potential": 0.88,
          "disease_resistance": 0.92,
          "soil_compatibility": 0.85,
          "market_acceptance": 0.80
        },
        "data_completeness": 0.9,
        "testing_years": 4,
        "trial_yield": 185,
        "trial_years": 3,
        "farmer_satisfaction": 87,
        "resistant_diseases": ["Northern Corn Leaf Blight", "Gray Leaf Spot"],
        "disease_cost_savings": 35,
        "strengths": ["High yield potential", "Strong disease resistance"],
        "considerations": ["Higher seed cost", "Requires careful management"],
        "risk_level": "low",
        "risk_factors": [
          {"factor": "Weather Sensitivity", "level": "Low", "description": "Good stability"},
          {"factor": "Management Risk", "level": "Medium", "description": "Requires attention"}
        ],
        "mitigation_strategies": ["Precision nitrogen management", "Regular monitoring"],
        "estimated_roi": 1.35,
        "break_even_yield": 165.5,
        "premium_potential": 0.15,
        "cost_analysis": {
          "seed_cost_per_acre": 145.00,
          "additional_inputs": 25.00,
          "total_investment": 170.00
        },
        "planting_recommendations": [
          "Plant when soil temperature reaches 50°F",
          "Optimal planting depth: 1.5-2 inches"
        ],
        "fertilizer_recommendations": [
          "Apply nitrogen in split applications",
          "Monitor soil phosphorus levels"
        ],
        "pest_recommendations": [
          "Monitor for early season insects",
          "Scout regularly for disease symptoms"
        ]
      },
      "context": {
        "location": {"latitude": 41.8781, "longitude": -87.6298},
        "soil_data": {"ph": 6.5, "organic_matter": 3.2, "texture": "loam"},
        "climate_zone": "5b",
        "region": "Midwest",
        "soil_type": "clay_loam",
        "regional_data_quality": 0.8
      },
      "explanation_options": {
        "include_detailed_reasoning": true,
        "include_evidence": true,
        "include_trade_offs": true,
        "include_risk_analysis": true,
        "include_economic_analysis": true,
        "include_management_guidance": true,
        "explanation_style": "comprehensive",
        "max_sections": 7
      }
    }
    ```
    
    **Response Features:**
    - Structured explanation sections with confidence levels
    - Evidence-based reasoning with data sources
    - Interactive elements for detailed exploration
    - Educational content integration
    - Accessibility features for inclusive access
    - Expandable sections for progressive disclosure
    
    Returns comprehensive explanation with AI-powered insights for informed variety selection decisions.
    """
    try:
        # Validate request structure
        if not request.get("variety_data"):
            raise HTTPException(
                status_code=400,
                detail="variety_data is required for comprehensive explanation generation"
            )
        
        variety_data = request.get("variety_data", {})
        context = request.get("context", {})
        explanation_options = request.get("explanation_options", {})
        
        # Generate comprehensive explanation
        explanation = await explanation_service.generate_comprehensive_explanation(
            variety_data=variety_data,
            context=context,
            explanation_options=explanation_options
        )
        
        # Convert to response format
        response = {
            "request_id": explanation.request_id,
            "variety_id": explanation.variety_id,
            "variety_name": explanation.variety_name,
            "generated_at": explanation.generated_at.isoformat(),
            "overall_confidence": explanation.overall_confidence,
            "summary": explanation.summary,
            "key_insights": explanation.key_insights,
            "recommendations": explanation.recommendations,
            "educational_resources": explanation.educational_resources,
            "accessibility_features": explanation.accessibility_features,
            "sections": []
        }
        
        # Convert sections to response format
        for section in explanation.sections:
            section_data = {
                "section_id": section.section_id,
                "title": section.title,
                "content": section.content,
                "explanation_type": section.explanation_type.value,
                "confidence_level": section.confidence_level.value,
                "expandable": section.expandable,
                "educational_content": section.educational_content,
                "interactive_elements": section.interactive_elements or [],
                "evidence_items": []
            }
            
            # Convert evidence items
            for evidence in section.evidence_items:
                evidence_data = {
                    "title": evidence.title,
                    "description": evidence.description,
                    "source": evidence.source,
                    "confidence": evidence.confidence,
                    "data_type": evidence.data_type,
                    "relevance_score": evidence.relevance_score,
                    "supporting_data": evidence.supporting_data
                }
                section_data["evidence_items"].append(evidence_data)
            
            response["sections"].append(section_data)
        
        return response
        
    except Exception as e:
        logger.error(f"Error generating comprehensive explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate comprehensive explanation: {str(e)}"
        )

@router.get("/types", response_model=List[Dict[str, str]])
async def get_explanation_types():
    """
    Get available explanation types and their descriptions.
    
    Returns list of explanation types with descriptions for UI configuration.
    """
    return [
        {
            "type": ExplanationType.SUMMARY.value,
            "name": "Summary",
            "description": "High-level overview of the recommendation"
        },
        {
            "type": ExplanationType.DETAILED_REASONING.value,
            "name": "Detailed Reasoning",
            "description": "In-depth analysis of recommendation factors"
        },
        {
            "type": ExplanationType.EVIDENCE_BASED.value,
            "name": "Evidence-Based",
            "description": "Supporting data and research evidence"
        },
        {
            "type": ExplanationType.EDUCATIONAL.value,
            "name": "Educational",
            "description": "Learning content and explanatory information"
        },
        {
            "type": ExplanationType.TRADE_OFF_ANALYSIS.value,
            "name": "Trade-off Analysis",
            "description": "Balanced view of strengths and considerations"
        },
        {
            "type": ExplanationType.RISK_ASSESSMENT.value,
            "name": "Risk Assessment",
            "description": "Risk evaluation and mitigation strategies"
        },
        {
            "type": ExplanationType.ECONOMIC_ANALYSIS.value,
            "name": "Economic Analysis",
            "description": "ROI calculations and cost-benefit analysis"
        },
        {
            "type": ExplanationType.MANAGEMENT_GUIDANCE.value,
            "name": "Management Guidance",
            "description": "Actionable recommendations and best practices"
        }
    ]

@router.get("/confidence-levels", response_model=List[Dict[str, str]])
async def get_confidence_levels():
    """
    Get available confidence levels and their descriptions.
    
    Returns list of confidence levels with descriptions for UI display.
    """
    return [
        {
            "level": ConfidenceLevel.HIGH.value,
            "name": "High Confidence",
            "description": "Strong evidence and data support",
            "color": "success"
        },
        {
            "level": ConfidenceLevel.MEDIUM.value,
            "name": "Medium Confidence",
            "description": "Moderate evidence and data support",
            "color": "warning"
        },
        {
            "level": ConfidenceLevel.LOW.value,
            "name": "Low Confidence",
            "description": "Limited evidence and data support",
            "color": "danger"
        },
        {
            "level": ConfidenceLevel.VERY_LOW.value,
            "name": "Very Low Confidence",
            "description": "Minimal evidence and data support",
            "color": "secondary"
        }
    ]

@router.post("/section", response_model=Dict[str, Any])
async def generate_specific_section(
    section_type: ExplanationType,
    variety_data: Dict[str, Any],
    context: Dict[str, Any],
    explanation_service: ComprehensiveExplanationService = Depends(get_explanation_service)
):
    """
    Generate a specific explanation section.
    
    Useful for progressive loading or on-demand section generation.
    """
    try:
        # Create explanation options for specific section
        explanation_options = {
            "include_detailed_reasoning": section_type == ExplanationType.DETAILED_REASONING,
            "include_evidence": section_type == ExplanationType.EVIDENCE_BASED,
            "include_trade_offs": section_type == ExplanationType.TRADE_OFF_ANALYSIS,
            "include_risk_analysis": section_type == ExplanationType.RISK_ASSESSMENT,
            "include_economic_analysis": section_type == ExplanationType.ECONOMIC_ANALYSIS,
            "include_management_guidance": section_type == ExplanationType.MANAGEMENT_GUIDANCE
        }
        
        # Generate comprehensive explanation
        explanation = await explanation_service.generate_comprehensive_explanation(
            variety_data=variety_data,
            context=context,
            explanation_options=explanation_options
        )
        
        # Find the specific section
        target_section = None
        for section in explanation.sections:
            if section.explanation_type == section_type:
                target_section = section
                break
        
        if not target_section:
            raise HTTPException(
                status_code=404,
                detail=f"Section type {section_type.value} not found in explanation"
            )
        
        # Convert to response format
        section_data = {
            "section_id": target_section.section_id,
            "title": target_section.title,
            "content": target_section.content,
            "explanation_type": target_section.explanation_type.value,
            "confidence_level": target_section.confidence_level.value,
            "expandable": target_section.expandable,
            "educational_content": target_section.educational_content,
            "interactive_elements": target_section.interactive_elements or [],
            "evidence_items": []
        }
        
        # Convert evidence items
        for evidence in target_section.evidence_items:
            evidence_data = {
                "title": evidence.title,
                "description": evidence.description,
                "source": evidence.source,
                "confidence": evidence.confidence,
                "data_type": evidence.data_type,
                "relevance_score": evidence.relevance_score,
                "supporting_data": evidence.supporting_data
            }
            section_data["evidence_items"].append(evidence_data)
        
        return section_data
        
    except Exception as e:
        logger.error(f"Error generating specific section: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate section {section_type.value}: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check endpoint for comprehensive explanation service."""
    return {
        "status": "healthy",
        "service": "comprehensive-explanation",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "detailed_reasoning",
            "evidence_display",
            "trade_off_analysis",
            "risk_assessment",
            "economic_analysis",
            "management_guidance",
            "educational_content",
            "accessibility_features"
        ]
    }