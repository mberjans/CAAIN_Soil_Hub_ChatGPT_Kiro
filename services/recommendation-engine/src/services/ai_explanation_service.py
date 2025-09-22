"""
AI Explanation Service for AFAS Recommendation Engine
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This service generates natural language explanations for agricultural recommendations
using a simple template-based approach that can be enhanced with LLM integration later.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AIExplanationService:
    """
    Service for generating natural language explanations of agricultural recommendations.
    
    This implementation uses template-based explanation generation that can be
    enhanced with LLM integration in Phase 2 of the project.
    """
    
    def __init__(self):
        """Initialize the AI explanation service."""
        self.explanation_templates = self._load_explanation_templates()
        logger.info("AI Explanation Service initialized")
    
    def generate_explanation(
        self, 
        recommendation_type: str, 
        recommendation_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate a natural language explanation for a recommendation.
        
        Args:
            recommendation_type: Type of recommendation (crop_selection, soil_fertility, etc.)
            recommendation_data: The recommendation details
            context: Farm and soil context data
            
        Returns:
            Natural language explanation string
        """
        try:
            template = self.explanation_templates.get(recommendation_type)
            if not template:
                return self._generate_generic_explanation(recommendation_data, context)
            
            explanation = self._apply_template(template, recommendation_data, context)
            return self._enhance_explanation(explanation, recommendation_data, context)
            
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return self._generate_fallback_explanation(recommendation_data)
    
    def generate_confidence_explanation(
        self, 
        confidence_factors: Dict[str, float],
        overall_confidence: float
    ) -> str:
        """
        Generate explanation for confidence scoring.
        
        Args:
            confidence_factors: Breakdown of confidence factors
            overall_confidence: Overall confidence score
            
        Returns:
            Explanation of confidence scoring
        """
        try:
            confidence_level = self._get_confidence_level(overall_confidence)
            
            explanation_parts = [
                f"This recommendation has {confidence_level} confidence ({overall_confidence:.0%})."
            ]
            
            # Explain key confidence factors
            if confidence_factors.get('soil_data_quality', 0) < 0.7:
                explanation_parts.append(
                    "Confidence is reduced due to limited soil test data. "
                    "Recent soil testing would improve recommendation accuracy."
                )
            
            if confidence_factors.get('regional_data_availability', 0) < 0.7:
                explanation_parts.append(
                    "Limited regional data available for your area. "
                    "Consult local extension services for additional guidance."
                )
            
            if confidence_factors.get('expert_validation', 0) >= 0.8:
                explanation_parts.append(
                    "This recommendation is based on expert-validated agricultural practices."
                )
            
            return " ".join(explanation_parts)
            
        except Exception as e:
            logger.error(f"Error generating confidence explanation: {e}")
            return f"Confidence level: {overall_confidence:.0%}"
    
    def generate_implementation_steps(
        self, 
        recommendation_type: str,
        recommendation_data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate step-by-step implementation guidance.
        
        Args:
            recommendation_type: Type of recommendation
            recommendation_data: Recommendation details
            
        Returns:
            List of implementation steps
        """
        try:
            if recommendation_type == "crop_selection":
                return self._generate_crop_selection_steps(recommendation_data)
            elif recommendation_type == "soil_fertility":
                return self._generate_soil_fertility_steps(recommendation_data)
            elif recommendation_type == "fertilizer_selection":
                return self._generate_fertilizer_steps(recommendation_data)
            elif recommendation_type == "crop_rotation":
                return self._generate_rotation_steps(recommendation_data)
            elif recommendation_type == "nutrient_deficiency":
                return self._generate_deficiency_steps(recommendation_data)
            else:
                return self._generate_generic_steps(recommendation_data)
                
        except Exception as e:
            logger.error(f"Error generating implementation steps: {e}")
            return ["Consult with local agricultural extension service for implementation guidance."]
    
    def generate_seasonal_timing_advice(
        self, 
        recommendation_type: str,
        recommendation_data: Dict[str, Any],
        location_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate seasonal timing advice for recommendations.
        
        Args:
            recommendation_type: Type of recommendation
            recommendation_data: Recommendation details
            location_data: Location information for regional timing
            
        Returns:
            Seasonal timing advice
        """
        try:
            current_month = datetime.now().month
            
            if recommendation_type == "crop_selection":
                return self._generate_crop_timing_advice(recommendation_data, current_month)
            elif recommendation_type == "soil_fertility":
                return self._generate_soil_timing_advice(recommendation_data, current_month)
            elif recommendation_type == "fertilizer_selection":
                return self._generate_fertilizer_timing_advice(recommendation_data, current_month)
            else:
                return self._generate_generic_timing_advice(current_month)
                
        except Exception as e:
            logger.error(f"Error generating timing advice: {e}")
            return "Consult local extension service for optimal timing in your region."
    
    def generate_risk_assessment(
        self, 
        recommendation_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate risk assessment for recommendations.
        
        Args:
            recommendation_data: Recommendation details
            context: Farm and environmental context
            
        Returns:
            Dictionary with risk factors and mitigation strategies
        """
        try:
            risks = {}
            
            # Weather risks
            if context.get('weather_data', {}).get('drought_risk', 'low') == 'high':
                risks['weather'] = "High drought risk may affect crop performance. Consider drought-tolerant varieties and water conservation practices."
            
            # Market risks
            confidence = recommendation_data.get('confidence_score', 0)
            if confidence < 0.7:
                risks['recommendation'] = "Lower confidence in recommendation due to limited data. Consider additional soil testing or expert consultation."
            
            # Implementation risks
            cost = recommendation_data.get('cost_per_acre', 0)
            if cost > 100:
                risks['economic'] = "Higher cost recommendation. Evaluate return on investment and consider phased implementation."
            
            # Timing risks
            current_month = datetime.now().month
            if current_month in [11, 12, 1, 2]:  # Winter months
                risks['timing'] = "Winter timing may limit implementation options. Plan for spring application when conditions allow."
            
            return risks
            
        except Exception as e:
            logger.error(f"Error generating risk assessment: {e}")
            return {"general": "Consult with agricultural professionals to assess implementation risks."}
    
    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load explanation templates for different recommendation types."""
        return {
            "crop_selection": (
                "{crop_name} is {suitability_level} for your farm conditions. "
                "Your soil pH of {soil_ph} is {ph_assessment} for {crop_name}. "
                "{additional_factors}"
            ),
            "soil_fertility": (
                "Your soil health assessment shows {soil_score}/10. "
                "Priority improvements include: {priority_areas}. "
                "{improvement_strategy}"
            ),
            "fertilizer_selection": (
                "Based on your {criteria}, {fertilizer_type} fertilizers are recommended. "
                "{cost_analysis} {environmental_impact}"
            ),
            "crop_rotation": (
                "Your current rotation has a diversity score of {diversity_score}/10. "
                "{rotation_benefits} {improvement_recommendations}"
            ),
            "nutrient_deficiency": (
                "Soil analysis indicates {deficiency_level} {nutrient} deficiency. "
                "{correction_strategy} {monitoring_advice}"
            )
        }
    
    def _apply_template(
        self, 
        template: str, 
        recommendation_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """Apply template with data substitution."""
        try:
            # Extract common variables
            variables = {
                'crop_name': recommendation_data.get('crop_name', 'the recommended crop'),
                'soil_ph': context.get('soil_data', {}).get('ph', 'unknown'),
                'soil_score': recommendation_data.get('soil_health_score', 'unknown'),
                'fertilizer_type': recommendation_data.get('fertilizer_type', 'recommended'),
                'diversity_score': recommendation_data.get('diversity_score', 'unknown'),
                'nutrient': recommendation_data.get('nutrient', 'nutrient'),
                'deficiency_level': recommendation_data.get('severity', 'moderate'),
            }
            
            # Add assessment variables
            variables.update(self._generate_assessment_variables(recommendation_data, context))
            
            # Apply template
            return template.format(**variables)
            
        except KeyError as e:
            logger.warning(f"Missing template variable: {e}")
            return self._generate_generic_explanation(recommendation_data, context)
    
    def _generate_assessment_variables(
        self, 
        recommendation_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate assessment variables for templates."""
        variables = {}
        
        # pH assessment
        soil_ph = context.get('soil_data', {}).get('ph')
        if soil_ph:
            if 6.0 <= soil_ph <= 7.0:
                variables['ph_assessment'] = 'optimal'
            elif 5.5 <= soil_ph < 6.0 or 7.0 < soil_ph <= 7.5:
                variables['ph_assessment'] = 'acceptable'
            else:
                variables['ph_assessment'] = 'suboptimal'
        else:
            variables['ph_assessment'] = 'unknown'
        
        # Suitability level
        confidence = recommendation_data.get('confidence_score', 0)
        if confidence >= 0.8:
            variables['suitability_level'] = 'highly suitable'
        elif confidence >= 0.6:
            variables['suitability_level'] = 'suitable'
        else:
            variables['suitability_level'] = 'marginally suitable'
        
        # Additional factors
        factors = []
        if context.get('soil_data', {}).get('organic_matter_percent', 0) < 2.5:
            factors.append("organic matter improvement recommended")
        if context.get('farm_profile', {}).get('irrigation_available'):
            factors.append("irrigation available for optimal management")
        
        variables['additional_factors'] = ". ".join(factors) if factors else "No additional concerns identified"
        
        # Soil fertility specific variables
        variables['priority_areas'] = self._generate_priority_areas(recommendation_data, context)
        variables['improvement_strategy'] = self._generate_improvement_strategy(recommendation_data, context)
        
        # Fertilizer selection variables
        variables['criteria'] = self._generate_selection_criteria(recommendation_data, context)
        variables['cost_analysis'] = self._generate_cost_analysis(recommendation_data)
        variables['environmental_impact'] = self._generate_environmental_impact(recommendation_data)
        
        # Crop rotation variables
        variables['rotation_benefits'] = self._generate_rotation_benefits(recommendation_data, context)
        variables['improvement_recommendations'] = self._generate_rotation_improvements(recommendation_data, context)
        
        # Nutrient deficiency variables
        variables['correction_strategy'] = self._generate_correction_strategy(recommendation_data, context)
        variables['monitoring_advice'] = self._generate_monitoring_advice(recommendation_data, context)
        
        return variables
    
    def _enhance_explanation(
        self, 
        base_explanation: str, 
        recommendation_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """Enhance explanation with additional context."""
        enhancements = []
        
        # Add source attribution
        sources = recommendation_data.get('agricultural_sources', [])
        if sources:
            enhancements.append(f"Based on guidelines from {', '.join(sources[:2])}.")
        
        # Add timing information
        timing = recommendation_data.get('timing')
        if timing:
            enhancements.append(f"Recommended timing: {timing}.")
        
        # Add cost information
        cost = recommendation_data.get('cost_per_acre')
        if cost:
            enhancements.append(f"Estimated cost: ${cost:.2f}/acre.")
        
        if enhancements:
            return f"{base_explanation} {' '.join(enhancements)}"
        
        return base_explanation
    
    def _generate_crop_selection_steps(self, recommendation_data: Dict[str, Any]) -> List[str]:
        """Generate crop selection implementation steps."""
        steps = [
            "Verify soil conditions meet crop requirements through recent soil testing",
            "Select appropriate variety for your region and climate zone",
            "Plan planting schedule based on local frost dates and soil conditions",
            "Ensure equipment is suitable for chosen crop and field conditions",
            "Consider crop insurance options and market contracts"
        ]
        
        # Add specific steps based on recommendation
        crop_name = recommendation_data.get('crop_name', '').lower()
        if 'corn' in crop_name:
            steps.append("Plan nitrogen application strategy for corn production")
        elif 'soybean' in crop_name:
            steps.append("Consider inoculant application for nitrogen fixation")
        
        return steps
    
    def _generate_soil_fertility_steps(self, recommendation_data: Dict[str, Any]) -> List[str]:
        """Generate soil fertility improvement steps."""
        steps = [
            "Conduct comprehensive soil testing if not done recently",
            "Apply lime if pH adjustment is needed (fall application preferred)",
            "Implement organic matter improvement program",
            "Plan nutrient applications based on soil test results",
            "Monitor soil health improvements over time"
        ]
        
        # Add specific steps based on recommendations
        if recommendation_data.get('lime_needed'):
            steps.insert(1, f"Apply {recommendation_data.get('lime_rate', 'recommended')} tons/acre of agricultural limestone")
        
        return steps
    
    def _generate_fertilizer_steps(self, recommendation_data: Dict[str, Any]) -> List[str]:
        """Generate fertilizer selection implementation steps."""
        return [
            "Evaluate current soil fertility status through testing",
            "Compare fertilizer options based on cost and crop needs",
            "Consider application equipment compatibility",
            "Plan application timing for optimal crop uptake",
            "Monitor crop response and adjust future applications"
        ]
    
    def _generate_rotation_steps(self, recommendation_data: Dict[str, Any]) -> List[str]:
        """Generate crop rotation implementation steps."""
        return [
            "Assess current rotation diversity and pest pressure",
            "Plan rotation sequence to maximize benefits",
            "Consider nitrogen-fixing crops to reduce fertilizer needs",
            "Evaluate equipment needs for different crops",
            "Monitor rotation benefits over multiple years"
        ]
    
    def _generate_deficiency_steps(self, recommendation_data: Dict[str, Any]) -> List[str]:
        """Generate nutrient deficiency correction steps."""
        return [
            "Confirm deficiency through soil and/or tissue testing",
            "Select appropriate correction method (soil vs foliar application)",
            "Apply corrective measures at optimal timing",
            "Monitor crop response to treatment",
            "Adjust long-term fertility program to prevent recurrence"
        ]
    
    def _generate_generic_steps(self, recommendation_data: Dict[str, Any]) -> List[str]:
        """Generate generic implementation steps."""
        return [
            "Review recommendation details and requirements",
            "Consult with local agricultural extension service if needed",
            "Plan implementation timing and resource requirements",
            "Implement recommendations according to best practices",
            "Monitor results and adjust future management accordingly"
        ]
    
    def _generate_generic_explanation(
        self, 
        recommendation_data: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> str:
        """Generate generic explanation when templates are not available."""
        confidence = recommendation_data.get('confidence_score', 0)
        confidence_text = self._get_confidence_level(confidence)
        
        return (
            f"This recommendation has {confidence_text} confidence based on available data. "
            f"The recommendation considers your specific farm conditions and follows "
            f"established agricultural best practices."
        )
    
    def _generate_fallback_explanation(self, recommendation_data: Dict[str, Any]) -> str:
        """Generate fallback explanation for error cases."""
        return (
            "This recommendation is based on agricultural best practices and available data. "
            "Consult with local agricultural extension services for additional guidance."
        )
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to descriptive level."""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "moderate"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very low"
    
    def _generate_priority_areas(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate priority improvement areas for soil fertility."""
        areas = []
        
        soil_data = context.get('soil_data', {})
        
        # Check pH
        ph = soil_data.get('ph', 0)
        if ph < 6.0:
            areas.append("soil pH adjustment (lime application)")
        elif ph > 7.5:
            areas.append("soil pH management (sulfur application)")
        
        # Check organic matter
        om = soil_data.get('organic_matter_percent', 0)
        if om < 3.0:
            areas.append("organic matter enhancement")
        
        # Check nutrients
        p = soil_data.get('phosphorus_ppm', 0)
        if p < 15:
            areas.append("phosphorus buildup")
        
        k = soil_data.get('potassium_ppm', 0)
        if k < 120:
            areas.append("potassium improvement")
        
        return ", ".join(areas) if areas else "maintaining current soil health levels"
    
    def _generate_improvement_strategy(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate improvement strategy for soil fertility."""
        strategies = []
        
        if recommendation_data.get('lime_needed'):
            strategies.append("Apply agricultural limestone in fall")
        
        soil_data = context.get('soil_data', {})
        if soil_data.get('organic_matter_percent', 0) < 3.0:
            strategies.append("Implement cover crops and organic matter additions")
        
        if not strategies:
            strategies.append("Continue current management practices with regular monitoring")
        
        return ". ".join(strategies) + "."
    
    def _generate_selection_criteria(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate selection criteria for fertilizer recommendations."""
        criteria = []
        
        if context.get('farm_profile', {}).get('organic_certified'):
            criteria.append("organic certification requirements")
        
        if recommendation_data.get('cost_per_acre'):
            criteria.append("cost-effectiveness analysis")
        
        criteria.append("soil test results and crop nutrient needs")
        
        return ", ".join(criteria) if criteria else "agricultural best practices"
    
    def _generate_cost_analysis(self, recommendation_data: Dict[str, Any]) -> str:
        """Generate cost analysis for fertilizer recommendations."""
        cost = recommendation_data.get('cost_per_acre')
        if cost:
            return f"This approach provides good value at ${cost:.2f}/acre."
        return "Cost-effectiveness varies based on current market prices."
    
    def _generate_environmental_impact(self, recommendation_data: Dict[str, Any]) -> str:
        """Generate environmental impact assessment."""
        fertilizer_type = recommendation_data.get('fertilizer_type', '').lower()
        
        if 'organic' in fertilizer_type:
            return "Organic fertilizers improve soil biology and reduce environmental impact."
        elif 'slow-release' in fertilizer_type:
            return "Slow-release formulations reduce nutrient loss and environmental impact."
        else:
            return "Follow 4R principles (Right rate, Right time, Right place, Right source) for environmental protection."
    
    def _generate_rotation_benefits(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate rotation benefits explanation."""
        diversity_score = recommendation_data.get('diversity_score', 0)
        
        if diversity_score >= 8:
            return "Your rotation provides excellent diversity benefits including pest management and soil health improvement."
        elif diversity_score >= 6:
            return "Your rotation provides good diversity with opportunities for enhancement."
        else:
            return "Your rotation would benefit from increased diversity to improve pest management and soil health."
    
    def _generate_rotation_improvements(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate rotation improvement recommendations."""
        current_rotation = context.get('crop_data', {}).get('current_rotation', [])
        
        improvements = []
        
        if len(current_rotation) < 3:
            improvements.append("Consider adding a third crop to the rotation")
        
        if 'legume' not in str(current_rotation).lower() and 'soybean' not in str(current_rotation).lower():
            improvements.append("Include nitrogen-fixing legumes")
        
        if not improvements:
            improvements.append("Continue monitoring rotation performance")
        
        return ". ".join(improvements) + "."
    
    def _generate_correction_strategy(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate nutrient deficiency correction strategy."""
        nutrient = recommendation_data.get('nutrient', 'nutrient')
        severity = recommendation_data.get('severity', 'moderate')
        
        if severity == 'severe':
            return f"Immediate {nutrient} application is recommended through both soil and foliar methods."
        elif severity == 'moderate':
            return f"Apply {nutrient} fertilizer according to soil test recommendations."
        else:
            return f"Monitor {nutrient} levels and apply maintenance rates as needed."
    
    def _generate_monitoring_advice(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate monitoring advice for nutrient management."""
        nutrient = recommendation_data.get('nutrient', 'nutrient')
        
        return f"Monitor crop response and retest soil {nutrient} levels next season to evaluate correction effectiveness."
    
    def _generate_crop_timing_advice(self, recommendation_data: Dict[str, Any], current_month: int) -> str:
        """Generate crop selection timing advice."""
        crop_name = recommendation_data.get('crop_name', '').lower()
        
        if current_month in [1, 2, 3]:  # Winter/Early Spring
            return "Plan seed purchases and equipment preparation. Review crop insurance options."
        elif current_month in [4, 5]:  # Spring planting season
            if 'corn' in crop_name:
                return "Optimal corn planting window. Monitor soil temperature (50°F+) and moisture conditions."
            elif 'soybean' in crop_name:
                return "Prepare for soybean planting after corn. Soil temperature should reach 55°F+."
            else:
                return "Spring planting season. Monitor soil conditions and weather forecasts."
        elif current_month in [6, 7, 8]:  # Growing season
            return "Focus on crop monitoring and in-season management. Plan for next year's crop selection."
        elif current_month in [9, 10]:  # Harvest season
            return "Harvest season. Evaluate crop performance for next year's planning."
        else:  # Late fall/winter
            return "Post-harvest evaluation period. Plan crop selection for next growing season."
    
    def _generate_soil_timing_advice(self, recommendation_data: Dict[str, Any], current_month: int) -> str:
        """Generate soil fertility timing advice."""
        if current_month in [9, 10, 11]:  # Fall
            return "Optimal time for lime application and fall fertilizer programs. Soil sampling recommended."
        elif current_month in [12, 1, 2]:  # Winter
            return "Plan soil fertility program for next season. Review soil test results and plan amendments."
        elif current_month in [3, 4]:  # Early spring
            return "Spring soil testing and fertilizer application window. Monitor soil conditions."
        else:  # Growing season
            return "Monitor crop response to fertility program. Plan tissue testing if needed."
    
    def _generate_fertilizer_timing_advice(self, recommendation_data: Dict[str, Any], current_month: int) -> str:
        """Generate fertilizer application timing advice."""
        fertilizer_type = recommendation_data.get('fertilizer_type', '').lower()
        
        if 'nitrogen' in fertilizer_type or 'n' in fertilizer_type:
            if current_month in [4, 5]:
                return "Spring nitrogen application window. Split applications may improve efficiency."
            elif current_month in [6, 7]:
                return "Side-dress nitrogen application period for corn. Monitor crop needs."
            else:
                return "Plan nitrogen application timing to match crop uptake patterns."
        else:
            if current_month in [9, 10, 11]:
                return "Fall application recommended for phosphorus and potassium."
            else:
                return "Spring application acceptable if fall application was missed."
    
    def _generate_generic_timing_advice(self, current_month: int) -> str:
        """Generate generic timing advice."""
        if current_month in [3, 4, 5]:
            return "Spring planning and implementation season. Monitor weather and soil conditions."
        elif current_month in [6, 7, 8]:
            return "Growing season monitoring period. Focus on crop management and assessment."
        elif current_month in [9, 10, 11]:
            return "Harvest and fall preparation season. Plan for next year's management."
        else:
            return "Winter planning period. Review performance and plan improvements."

# Factory function for easy initialization
def create_ai_explanation_service() -> AIExplanationService:
    """Create and return an AI explanation service instance."""
    return AIExplanationService()