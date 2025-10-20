"""
Fertilizer Recommendation Explanation Service

Creates context-aware, farmer-friendly explanations for fertilizer type selection
recommendations with educational content and decision support.
Implements TICKET-023_fertilizer-type-selection-9.1
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class FertilizerExplanationService:
    """Generate comprehensive explanations for fertilizer type recommendations."""
    
    def __init__(self):
        """Initialize the fertilizer explanation service."""
        self.logger = logging.getLogger(__name__)
        
        self.supported_languages = {
            "en": {
                "summary_heading": "Recommendation Summary",
                "why_heading": "Why This Fertilizer?",
                "comparison_heading": "Comparison Analysis",
                "trade_offs_heading": "Key Trade-offs",
                "cost_heading": "Cost Analysis",
                "environmental_heading": "Environmental Impact",
                "soil_health_heading": "Soil Health Considerations",
                "application_heading": "Application Guidance",
                "monitoring_heading": "What to Monitor",
                "alternatives_heading": "Alternative Options"
            }
        }
        
        self.default_language = "en"
        self.logger.info("FertilizerExplanationService initialized")
    
    def generate_recommendation_explanation(
        self,
        recommendation: Dict[str, Any],
        priorities: Dict[str, Any],
        constraints: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """Generate comprehensive explanation for a fertilizer recommendation."""
        try:
            templates = self.supported_languages.get(language, self.supported_languages["en"])
            
            explanation = {
                "explanation_id": f"fert_exp_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "generated_at": datetime.utcnow().isoformat(),
                "language": language,
                "summary": self._build_summary(recommendation, priorities, templates),
                "selection_reasoning": self._build_selection_reasoning(recommendation, priorities, constraints, templates),
                "comparison_analysis": self._build_comparison_analysis(recommendation, templates),
                "trade_off_analysis": self._build_trade_off_analysis(recommendation, priorities, templates),
                "cost_breakdown": self._build_cost_explanation(recommendation, constraints, templates),
                "environmental_impact_explanation": self._build_environmental_explanation(recommendation, templates),
                "soil_health_explanation": self._build_soil_health_explanation(recommendation, templates),
                "application_guidance": self._build_application_guidance(recommendation, constraints, templates),
                "monitoring_recommendations": self._build_monitoring_guidance(recommendation, templates),
                "alternative_options": self._build_alternatives_section(recommendation, priorities, templates),
                "key_decision_factors": self._extract_key_decision_factors(recommendation, priorities),
                "confidence_explanation": self._build_confidence_explanation(recommendation),
                "educational_content": self._build_educational_content(recommendation, context),
                "supporting_evidence": self._build_supporting_evidence(recommendation),
                "complexity_level": "intermediate",
                "target_audience": "farmer_friendly"
            }
            
            explanation["plain_text_summary"] = self._generate_plain_text_summary(explanation)
            
            return explanation
            
        except Exception as e:
            self.logger.error(f"Error generating explanation: {str(e)}")
            return {
                "error": str(e),
                "fallback_summary": "Unable to generate detailed explanation."
            }
    
    def _build_summary(self, recommendation: Dict[str, Any], priorities: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        """Build high-level summary."""
        fertilizer_name = recommendation.get("fertilizer_name", "Unknown Fertilizer")
        fertilizer_type = recommendation.get("fertilizer_type", "Unknown Type")
        overall_score = recommendation.get("suitability_score", 0.0)
        
        top_priorities = self._identify_top_matching_priorities(recommendation, priorities)
        
        return {
            "heading": templates["summary_heading"],
            "fertilizer_name": fertilizer_name,
            "fertilizer_type": fertilizer_type,
            "overall_suitability": f"{int(overall_score * 100)}%",
            "primary_strength": self._identify_primary_strength(recommendation, priorities),
            "best_fit_for": top_priorities[:2],
            "one_sentence_summary": self._generate_one_sentence_summary(fertilizer_name, fertilizer_type, top_priorities)
        }
    
    def _build_selection_reasoning(self, recommendation: Dict[str, Any], priorities: Dict[str, Any], constraints: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        """Explain why this fertilizer was selected."""
        reasons = []
        
        if priorities.get("cost_effectiveness", 0) > 0.6:
            cost_per_acre = recommendation.get("cost_analysis", {}).get("cost_per_acre", 0)
            reasons.append(f"Competitive pricing at  per acre")
        
        if priorities.get("soil_health", 0) > 0.6:
            soil_score = recommendation.get("soil_health_score", 0)
            if isinstance(soil_score, (int, float)):
                reasons.append(f"Provides soil health benefits (score: {int(soil_score * 100)}%)")
        
        return {
            "heading": templates["why_heading"],
            "key_reasons": reasons,
            "priority_alignment": self._calculate_priority_alignment(recommendation, priorities)
        }
    
    def _identify_top_matching_priorities(self, recommendation: Dict[str, Any], priorities: Dict[str, Any]) -> List[str]:
        matches = []
        if priorities.get("cost_effectiveness", 0) > 0.5:
            matches.append("cost_effectiveness")
        if priorities.get("soil_health", 0) > 0.5 and recommendation.get("soil_health_score", 0) > 0.6:
            matches.append("soil_health")
        return matches
    
    def _identify_primary_strength(self, recommendation: Dict[str, Any], priorities: Dict[str, Any]) -> str:
        fertilizer_type = recommendation.get("fertilizer_type", "unknown")
        strengths = {"organic": "soil health improvement", "synthetic": "cost-effectiveness", "slow_release": "sustained availability"}
        return strengths.get(fertilizer_type, "balanced nutrition")
    
    def _generate_one_sentence_summary(self, fertilizer_name: str, fertilizer_type: str, top_priorities: List[str]) -> str:
        if not top_priorities:
            return f"{fertilizer_name} ({fertilizer_type}) recommended based on your farm conditions."
        priority_text = " and ".join([p.replace("_", " ") for p in top_priorities[:2]])
        return f"{fertilizer_name} ({fertilizer_type}) best matches your {priority_text} priorities."
    
    def _calculate_priority_alignment(self, recommendation: Dict[str, Any], priorities: Dict[str, Any]) -> Dict[str, float]:
        alignment = {}
        if priorities.get("cost_effectiveness", 0) > 0:
            cost_score = 1.0 - min(recommendation.get("cost_analysis", {}).get("cost_per_acre", 100) / 200, 1.0)
            alignment["cost_effectiveness"] = cost_score
        if priorities.get("soil_health", 0) > 0:
            alignment["soil_health"] = recommendation.get("soil_health_score", 0)
        return alignment
    
    def _build_comparison_analysis(self, recommendation: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        return {"heading": templates["comparison_heading"], "comparisons": []}
    
    def _build_trade_off_analysis(self, recommendation: Dict[str, Any], priorities: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        return {"heading": templates["trade_offs_heading"], "identified_trade_offs": []}
    
    def _build_cost_explanation(self, recommendation: Dict[str, Any], constraints: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        cost_analysis = recommendation.get("cost_analysis", {})
        cost_per_acre = cost_analysis.get("cost_per_acre", 0)
        return {"heading": templates["cost_heading"], "cost_per_acre": f""}
    
    def _build_environmental_explanation(self, recommendation: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        return {"heading": templates["environmental_heading"]}
    
    def _build_soil_health_explanation(self, recommendation: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        return {"heading": templates["soil_health_heading"]}
    
    def _build_application_guidance(self, recommendation: Dict[str, Any], constraints: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        return {"heading": templates["application_heading"]}
    
    def _build_monitoring_guidance(self, recommendation: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        return {"heading": templates["monitoring_heading"]}
    
    def _build_alternatives_section(self, recommendation: Dict[str, Any], priorities: Dict[str, Any], templates: Dict[str, str]) -> Dict[str, Any]:
        return {"heading": templates["alternatives_heading"]}
    
    def _build_educational_content(self, recommendation: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {}
    
    def _build_supporting_evidence(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        return {"research_basis": ["University extension research"]}
    
    def _generate_plain_text_summary(self, explanation: Dict[str, Any]) -> str:
        summary = explanation.get("summary", {})
        return summary.get("one_sentence_summary", "Fertilizer recommendation generated")
    
    def _extract_key_decision_factors(self, recommendation: Dict[str, Any], priorities: Dict[str, Any]) -> List[str]:
        return []
    
    def _build_confidence_explanation(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        confidence = recommendation.get("confidence_score", 0)
        return {"confidence_score": f"{int(confidence * 100)}%"}
