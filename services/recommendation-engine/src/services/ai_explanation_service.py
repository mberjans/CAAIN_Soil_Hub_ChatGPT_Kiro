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
        Generate seasonal timing advice for recommendations with climate zone context.
        
        Args:
            recommendation_type: Type of recommendation
            recommendation_data: Recommendation details
            location_data: Location information for regional timing
            
        Returns:
            Seasonal timing advice with climate zone considerations
        """
        try:
            current_month = datetime.now().month
            climate_zone = self._extract_climate_zone(recommendation_data, location_data)
            
            if recommendation_type == "crop_selection":
                return self._generate_crop_timing_advice(recommendation_data, current_month, climate_zone)
            elif recommendation_type == "soil_fertility":
                return self._generate_soil_timing_advice(recommendation_data, current_month, climate_zone)
            elif recommendation_type == "fertilizer_selection":
                return self._generate_fertilizer_timing_advice(recommendation_data, current_month, climate_zone)
            else:
                return self._generate_generic_timing_advice(current_month, climate_zone)
                
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
                "{climate_zone_context} "
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
                'climate_zone_context': self._generate_climate_zone_context(recommendation_data, context),
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
    
    def _build_variety_insights(
        self,
        recommendation_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Build variety-specific insight messages."""
        insights: List[str] = []
        try:
            candidates = self._extract_variety_candidates(recommendation_data)
            if len(candidates) == 0:
                return insights

            summary = self._generate_variety_summary(candidates, context)
            if summary:
                insights.append(summary)

            comparison = self._generate_variety_comparison(candidates)
            if comparison:
                insights.append(comparison)

            trade_offs = self._generate_variety_trade_offs(candidates)
            if trade_offs:
                insights.append(trade_offs)

        except Exception as exc:
            logger.warning(f"Variety insight generation failed: {exc}")

        return insights

    def _extract_variety_candidates(self, recommendation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract variety candidate data from recommendation payload."""
        candidates: List[Dict[str, Any]] = []

        raw_collections: List[Any] = []
        raw_lists = [
            recommendation_data.get('variety_suggestions'),
            recommendation_data.get('recommended_varieties'),
            recommendation_data.get('variety_recommendations')
        ]

        index = 0
        while index < len(raw_lists):
            raw_collection = raw_lists[index]
            raw_collections.append(raw_collection)
            index += 1

        collection_index = 0
        while collection_index < len(raw_collections):
            entries = raw_collections[collection_index]
            if isinstance(entries, list):
                entry_index = 0
                while entry_index < len(entries):
                    entry = entries[entry_index]
                    processed = self._convert_variety_entry(entry)
                    if processed:
                        candidates.append(processed)
                    entry_index += 1
            collection_index += 1

        return candidates

    def _convert_variety_entry(self, entry: Any) -> Optional[Dict[str, Any]]:
        """Convert variety entry into dictionary representation."""
        if entry is None:
            return None

        if isinstance(entry, dict):
            return entry

        if hasattr(entry, 'dict'):
            try:
                return entry.dict()
            except Exception:
                try:
                    return entry.model_dump()  # type: ignore[attr-defined]
                except Exception:
                    pass

        if hasattr(entry, '__dict__') and isinstance(entry.__dict__, dict):
            return dict(entry.__dict__)

        return None

    def _generate_variety_summary(
        self,
        candidates: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> str:
        """Generate summary statement for top variety."""
        if len(candidates) == 0:
            return ""

        top_variety = candidates[0]

        try:
            variety_name = top_variety.get('variety_name')
        except Exception:
            variety_name = None

        if not variety_name:
            variety_name = top_variety.get('name')

        summary_parts: List[str] = []

        if variety_name:
            summary_parts.append(f"Top variety focus: {variety_name}.")
        else:
            summary_parts.append("Top variety focus identified from recommendation data.")

        attribute_description = self._describe_variety_attributes(top_variety)
        if attribute_description:
            summary_parts.append(attribute_description)

        fit_description = self._describe_variety_fit(top_variety, context)
        if fit_description:
            summary_parts.append(fit_description)

        key_advantages = top_variety.get('key_advantages')
        if isinstance(key_advantages, list) and len(key_advantages) > 0:
            highlighted: List[str] = []
            advantage_index = 0
            while advantage_index < len(key_advantages) and advantage_index < 3:
                advantage = key_advantages[advantage_index]
                if advantage:
                    highlighted.append(str(advantage))
                advantage_index += 1
            combined_advantages = self._combine_phrases(highlighted, '; ')
            if combined_advantages:
                summary_parts.append(f"Key strengths include {combined_advantages}.")

        combined_summary = self._combine_phrases(summary_parts, ' ')
        return combined_summary

    def _describe_variety_attributes(self, variety_data: Dict[str, Any]) -> str:
        """Create descriptive sentence for variety attributes."""
        detail_parts: List[str] = []

        maturity_value = variety_data.get('maturity_days')
        if not maturity_value:
            maturity_value = variety_data.get('relative_maturity')
        if maturity_value:
            detail_parts.append(f"{maturity_value}-day maturity")

        yield_value = variety_data.get('yield_potential_bu_per_acre')
        if not yield_value:
            yield_value = variety_data.get('yield_expectation')
        if yield_value:
            try:
                if isinstance(yield_value, (int, float)):
                    detail_parts.append(f"approximately {yield_value} bu/ac potential")
                else:
                    detail_parts.append(str(yield_value))
            except Exception:
                detail_parts.append(str(yield_value))

        drought_tolerance = variety_data.get('drought_tolerance')
        if drought_tolerance:
            detail_parts.append(f"{drought_tolerance} drought tolerance")

        stress_traits = variety_data.get('abiotic_stress_tolerances')
        if stress_traits and hasattr(stress_traits, '__dict__'):
            stress_info = []
            for attribute_name, attribute_value in stress_traits.__dict__.items():
                if attribute_value:
                    stress_info.append(f"{attribute_name.replace('_', ' ')} rating {attribute_value}")
            stress_summary = self._combine_phrases(stress_info, ', ')
            if stress_summary:
                detail_parts.append(stress_summary)

        detail_sentence = self._combine_phrases(detail_parts, ', ')
        description = ""
        if detail_sentence:
            description = f"It offers {detail_sentence}."

        trait_phrases = self._extract_variety_traits(variety_data)
        traits_sentence = self._combine_phrases(trait_phrases, '; ')
        if traits_sentence:
            if description:
                description = f"{description} Strengths include {traits_sentence}."
            else:
                description = f"Strengths include {traits_sentence}."

        return description

    def _describe_variety_fit(
        self,
        variety_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Summarize how the variety fits farm conditions."""
        fit_parts: List[str] = []

        climate_targets = variety_data.get('suitable_climate_zones')
        if not climate_targets:
            climate_targets = variety_data.get('compatible_climate_zones')
        if not climate_targets:
            climate_targets = variety_data.get('climate_zones')

        if climate_targets:
            try:
                combined_zones = self._combine_phrases(list(climate_targets), ', ')
            except Exception:
                combined_zones = None
            if combined_zones:
                fit_parts.append(f"Adapted to climate zones {combined_zones}.")

        soil_preferences = variety_data.get('soil_adaptation')
        if not soil_preferences:
            soil_preferences = variety_data.get('soil_preferences')
        if not soil_preferences:
            soil_preferences = variety_data.get('soil_types')

        if soil_preferences:
            try:
                combined_soils = self._combine_phrases(list(soil_preferences), ', ')
            except Exception:
                combined_soils = None
            if combined_soils:
                fit_parts.append(f"Performs well on {combined_soils} soils.")

        ph_range = variety_data.get('soil_ph_range')
        if ph_range and isinstance(ph_range, dict):
            minimum_ph = ph_range.get('min')
            maximum_ph = ph_range.get('max')
            if minimum_ph is not None and maximum_ph is not None:
                fit_parts.append(f"Best within soil pH {minimum_ph}-{maximum_ph} range.")

        location_profile = context.get('farm_profile', {}) if isinstance(context, dict) else {}
        irrigation_available = location_profile.get('irrigation_available')
        irrigation_notes = variety_data.get('water_requirements')
        if irrigation_notes and not irrigation_available:
            fit_parts.append("Plan for supplemental irrigation to reach full potential.")

        return self._combine_phrases(fit_parts, ' ')

    def _extract_variety_traits(self, variety_data: Dict[str, Any]) -> List[str]:
        """Extract notable trait descriptions from variety data."""
        traits: List[str] = []

        key_advantages = variety_data.get('key_advantages')
        if isinstance(key_advantages, list):
            index = 0
            while index < len(key_advantages) and index < 3:
                item = key_advantages[index]
                if item:
                    traits.append(str(item))
                index += 1

        special_traits = variety_data.get('special_traits')
        if isinstance(special_traits, list):
            trait_index = 0
            while trait_index < len(special_traits) and trait_index < 2:
                trait_value = special_traits[trait_index]
                if trait_value:
                    traits.append(str(trait_value))
                trait_index += 1

        disease_resistance = variety_data.get('disease_resistance')
        if isinstance(disease_resistance, dict):
            noted = []
            for disease_name, resistance in disease_resistance.items():
                if resistance:
                    noted.append(f"{disease_name} resistance")
            disease_summary = self._combine_phrases(noted, ', ')
            if disease_summary:
                traits.append(disease_summary)

        return traits

    def _generate_variety_comparison(self, candidates: List[Dict[str, Any]]) -> str:
        """Generate comparison overview across top varieties."""
        if len(candidates) < 2:
            return ""

        comparison_sentences: List[str] = []
        primary_variety = candidates[0]

        candidate_index = 1
        while candidate_index < len(candidates) and candidate_index <= 2:
            other_variety = candidates[candidate_index]
            comparison_sentence = self._compare_variety_profiles(primary_variety, other_variety)
            if comparison_sentence:
                comparison_sentences.append(comparison_sentence)
            candidate_index += 1

        combined_comparison = self._combine_phrases(comparison_sentences, ' ')
        if combined_comparison:
            return f"Variety comparison: {combined_comparison}"

        return ""

    def _compare_variety_profiles(
        self,
        primary_variety: Dict[str, Any],
        other_variety: Dict[str, Any]
    ) -> str:
        """Compare primary variety with an alternative option."""
        try:
            primary_name = primary_variety.get('variety_name', 'primary variety')
        except Exception:
            primary_name = 'primary variety'

        try:
            other_name = other_variety.get('variety_name', 'alternative variety')
        except Exception:
            other_name = 'alternative variety'

        primary_strength = self._summarize_primary_strength(primary_variety)
        alternative_strength = self._summarize_primary_strength(other_variety)

        if alternative_strength and primary_strength and alternative_strength != primary_strength:
            return (
                f"{primary_name} emphasizes {primary_strength}, while {other_name} provides {alternative_strength}."
            )

        if alternative_strength:
            return (
                f"{other_name} offers {alternative_strength} as an alternative to {primary_name}."
            )

        return ""

    def _summarize_primary_strength(self, variety_data: Dict[str, Any]) -> str:
        """Summarize primary strength for a variety."""
        traits = self._extract_variety_traits(variety_data)
        if len(traits) > 0:
            return traits[0]

        yield_value = variety_data.get('yield_potential_bu_per_acre')
        if yield_value:
            try:
                if isinstance(yield_value, (int, float)):
                    return f"high yield potential around {yield_value} bu/ac"
            except Exception:
                pass

        maturity = variety_data.get('maturity_days')
        if maturity:
            return f"{maturity}-day maturity fit"

        management_notes = variety_data.get('management_recommendations')
        if isinstance(management_notes, list) and len(management_notes) > 0:
            return management_notes[0]

        return "balanced agronomic performance"

    def _generate_variety_trade_offs(self, candidates: List[Dict[str, Any]]) -> str:
        """Highlight trade-offs between top varieties."""
        if len(candidates) < 2:
            return ""

        trade_off_statements: List[str] = []
        primary = candidates[0]

        index = 1
        while index < len(candidates) and index <= 2:
            alternative = candidates[index]
            trade_off_text = self._identify_trade_off(primary, alternative)
            if trade_off_text:
                trade_off_statements.append(trade_off_text)
            index += 1

        combined_trade_offs = self._combine_phrases(trade_off_statements, ' ')
        if combined_trade_offs:
            return f"Variety trade-offs: {combined_trade_offs}"

        return ""

    def _identify_trade_off(
        self,
        primary: Dict[str, Any],
        alternative: Dict[str, Any]
    ) -> str:
        """Identify trade-off message between two varieties."""
        primary_name = primary.get('variety_name', 'primary variety')
        alternative_name = alternative.get('variety_name', 'alternative variety')

        primary_strength = self._summarize_primary_strength(primary)
        alternative_strength = self._summarize_primary_strength(alternative)

        if alternative_strength and primary_strength and alternative_strength != primary_strength:
            return (
                f"Choose {primary_name} when prioritizing {primary_strength}, "
                f"or {alternative_name} for {alternative_strength}."
            )

        alternative_risk = alternative.get('risk_assessment')
        if isinstance(alternative_risk, dict):
            risk_level = alternative_risk.get('overall_risk_level')
            if risk_level:
                return (
                    f"{alternative_name} carries {risk_level} risk; balance it against the higher production "+
                    f"focus of {primary_name}."
                )

        return ""

    def _combine_phrases(self, phrases: List[Any], separator: str = ', ') -> str:
        """Combine phrases into a single string using separator."""
        normalized: List[str] = []

        index = 0
        while index < len(phrases):
            phrase = phrases[index]
            if phrase:
                normalized.append(str(phrase))
            index += 1

        if len(normalized) == 0:
            return ""

        combined = normalized[0]
        combine_index = 1
        while combine_index < len(normalized):
            combined += separator + normalized[combine_index]
            combine_index += 1

        return combined

    def _generate_climate_zone_context(self, recommendation_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Generate climate zone context for recommendations.
        
        Args:
            recommendation_data: Recommendation details including climate compatibility
            context: Farm and location context data
            
        Returns:
            Climate zone context description
        """
        try:
            # Prioritize climate zone from recommendation data (more specific)
            climate_zone = recommendation_data.get('climate_zone')
            
            # Fallback to location data if not in recommendation
            if not climate_zone:
                location_data = context.get('location_data') or context.get('farm_profile', {}).get('location')
                if location_data:
                    climate_zone = getattr(location_data, 'climate_zone', None) or location_data.get('climate_zone')
            
            if not climate_zone:
                return "Climate zone information not available."
            
            # Get climate compatibility information from recommendation
            climate_compatibility_score = recommendation_data.get('climate_compatibility_score', 0.7)
            crop_name = recommendation_data.get('crop_name', 'this crop')
            
            # Generate context based on compatibility score
            if climate_compatibility_score >= 1.0:
                return f"Climate Zone {climate_zone} is optimal for {crop_name} production."
            elif climate_compatibility_score >= 0.8:
                compatible_zones = recommendation_data.get('compatible_climate_zones', [])
                if compatible_zones:
                    return f"Climate Zone {climate_zone} is well-suited for {crop_name}, being adjacent to optimal zones {', '.join(compatible_zones[:3])}."
                else:
                    return f"Climate Zone {climate_zone} is well-suited for {crop_name} production."
            elif climate_compatibility_score >= 0.5:
                return f"Climate Zone {climate_zone} is marginal for {crop_name}. Consider heat/cold tolerant varieties and monitor seasonal conditions."
            else:
                compatible_zones = recommendation_data.get('compatible_climate_zones', [])
                if compatible_zones:
                    return f"Climate Zone {climate_zone} may present challenges for {crop_name}. Optimal zones are {', '.join(compatible_zones[:3])}."
                else:
                    return f"Climate Zone {climate_zone} may present challenges for {crop_name}. Consult local extension services for variety recommendations."
                    
        except Exception as e:
            logger.warning(f"Error generating climate zone context: {e}")
            return "Climate zone analysis not available."
    
    def _extract_climate_zone(self, recommendation_data: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Extract climate zone from recommendation or context data.
        
        Args:
            recommendation_data: Recommendation details
            context: Full context including location information
            
        Returns:
            Climate zone string or None if not available
        """
        # Check recommendation_data first (more specific)
        climate_zone = recommendation_data.get('climate_zone')
        if climate_zone:
            return climate_zone
        
        # Check context for location_data as fallback
        if context:
            location_data = context.get('location_data')
            if location_data:
                if hasattr(location_data, 'climate_zone'):
                    return location_data.climate_zone
                elif isinstance(location_data, dict):
                    return location_data.get('climate_zone')
        
        return None
    
    def _get_climate_timing_context(self, climate_zone: str) -> str:
        """
        Generate climate zone specific timing context.
        
        Args:
            climate_zone: USDA climate zone (e.g., "6a")
            
        Returns:
            Climate-specific timing context
        """
        if not climate_zone:
            return ""
            
        try:
            # Extract the numeric part of climate zone (e.g., "10a" -> 10, "6b" -> 6)
            import re
            zone_match = re.search(r'(\d+)', climate_zone)
            zone_num = int(zone_match.group(1)) if zone_match else 0
            
            if zone_num <= 4:
                return f" Zone {climate_zone} has a shorter growing season with late spring start and early fall finish."
            elif zone_num <= 6:
                return f" Zone {climate_zone} provides a moderate growing season with standard spring/fall timing."
            elif zone_num <= 8:
                return f" Zone {climate_zone} offers an extended growing season with early spring start and late fall finish."
            else:
                return f" Zone {climate_zone} allows for year-round growing with minimal frost risk."
        except (ValueError, IndexError):
            return f" Consider climate zone {climate_zone} characteristics for optimal timing."
    
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
        
        # Add variety-specific insights
        variety_insights = self._build_variety_insights(recommendation_data, context)
        if variety_insights:
            for insight in variety_insights:
                enhancements.append(insight)

        # Add climate zone specific notes
        climate_zone = self._extract_climate_zone(recommendation_data, context)
        if climate_zone:
            climate_compatibility_score = recommendation_data.get('climate_compatibility_score', 0.7)
            if climate_compatibility_score < 0.7:
                enhancements.append(f"Consider cold-hardy or heat-tolerant varieties for Zone {climate_zone}.")
        
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

        variety_candidates = self._extract_variety_candidates(recommendation_data)
        if len(variety_candidates) > 0:
            steps.insert(
                2,
                "Review recommended varieties to align yield goals with risk tolerance and field conditions"
            )

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
    
    def _generate_crop_timing_advice(self, recommendation_data: Dict[str, Any], current_month: int, climate_zone: Optional[str] = None) -> str:
        """Generate crop selection timing advice with climate zone considerations."""
        crop_name = recommendation_data.get('crop_name', '').lower()
        climate_context = self._get_climate_timing_context(climate_zone) if climate_zone else ""
        
        if current_month in [1, 2, 3]:  # Winter/Early Spring
            base_advice = "Plan seed purchases and equipment preparation. Review crop insurance options."
            if climate_zone:
                if climate_zone in ['3a', '3b', '4a']:
                    base_advice += f" In Zone {climate_zone}, plan for later spring planting due to extended frost risk."
                elif climate_zone in ['7a', '7b', '8a', '8b']:
                    base_advice += f" In Zone {climate_zone}, consider early spring varieties and soil preparation."
            return base_advice
            
        elif current_month in [4, 5]:  # Spring planting season
            if 'corn' in crop_name:
                base_advice = "Optimal corn planting window. Monitor soil temperature (50°F+) and moisture conditions."
                if climate_zone:
                    if climate_zone in ['3a', '3b', '4a']:
                        base_advice += f" Zone {climate_zone} may require waiting until late May for optimal conditions."
                    elif climate_zone in ['6a', '6b', '7a']:
                        base_advice += f" Zone {climate_zone} allows for mid-April to early May planting."
                return base_advice
            elif 'soybean' in crop_name:
                base_advice = "Prepare for soybean planting after corn. Soil temperature should reach 55°F+."
                if climate_zone:
                    if climate_zone in ['3a', '3b', '4a']:
                        base_advice += f" Zone {climate_zone} typically allows planting from late May through June."
                return base_advice
            else:
                return f"Spring planting season. Monitor soil conditions and weather forecasts.{climate_context}"
                
        elif current_month in [6, 7, 8]:  # Growing season
            base_advice = "Focus on crop monitoring and in-season management. Plan for next year's crop selection."
            if climate_zone and climate_zone in ['8a', '8b', '9a', '9b']:
                base_advice += f" Zone {climate_zone} may allow for second season plantings of cool-season crops."
            return base_advice
            
        elif current_month in [9, 10]:  # Harvest season
            base_advice = "Harvest season. Evaluate crop performance for next year's planning."
            if climate_zone:
                if climate_zone in ['3a', '3b', '4a']:
                    base_advice += f" Zone {climate_zone} harvest typically occurs early to mid-September."
                elif climate_zone in ['7a', '7b', '8a']:
                    base_advice += f" Zone {climate_zone} allows for extended harvest window through October."
            return base_advice
        else:  # Late fall/winter
            return f"Post-harvest evaluation period. Plan crop selection for next growing season.{climate_context}"
    
    def _generate_soil_timing_advice(self, recommendation_data: Dict[str, Any], current_month: int, climate_zone: Optional[str] = None) -> str:
        """Generate soil fertility timing advice with climate zone considerations."""
        if current_month in [9, 10, 11]:  # Fall
            base_advice = "Optimal time for lime application and fall fertilizer programs. Soil sampling recommended."
            if climate_zone:
                if climate_zone in ['3a', '3b', '4a']:
                    base_advice += f" Zone {climate_zone} benefits from early fall applications before ground freeze."
                elif climate_zone in ['8a', '8b', '9a']:
                    base_advice += f" Zone {climate_zone} allows for extended fall application window through December."
            return base_advice
            
        elif current_month in [12, 1, 2]:  # Winter
            base_advice = "Plan soil fertility program for next season. Review soil test results and plan amendments."
            if climate_zone and climate_zone in ['7a', '7b', '8a', '8b', '9a']:
                base_advice += f" Zone {climate_zone} may allow for winter lime applications during mild periods."
            return base_advice
            
        elif current_month in [3, 4]:  # Early spring
            base_advice = "Spring soil testing and fertilizer application window. Monitor soil conditions."
            if climate_zone:
                if climate_zone in ['3a', '3b', '4a']:
                    base_advice += f" Zone {climate_zone} requires waiting for soil thaw and drainage."
                elif climate_zone in ['6a', '6b', '7a']:
                    base_advice += f" Zone {climate_zone} typically allows early April applications."
            return base_advice
        else:  # Growing season
            return "Monitor crop response to fertility program. Plan tissue testing if needed."
    
    def _generate_fertilizer_timing_advice(self, recommendation_data: Dict[str, Any], current_month: int, climate_zone: Optional[str] = None) -> str:
        """Generate fertilizer application timing advice with climate zone considerations."""
        fertilizer_type = recommendation_data.get('fertilizer_type', '').lower()
        
        if 'nitrogen' in fertilizer_type or 'n' in fertilizer_type:
            if current_month in [4, 5]:
                base_advice = "Spring nitrogen application window. Split applications may improve efficiency."
                if climate_zone:
                    if climate_zone in ['3a', '3b', '4a']:
                        base_advice += f" Zone {climate_zone} may require delayed applications until soil temperature reaches 40°F."
                    elif climate_zone in ['7a', '7b', '8a']:
                        base_advice += f" Zone {climate_zone} allows for earlier March applications."
                return base_advice
            elif current_month in [6, 7]:
                return "Side-dress nitrogen application period for corn. Monitor crop needs."
            else:
                return "Plan nitrogen application timing to match crop uptake patterns."
        else:
            if current_month in [9, 10, 11]:
                base_advice = "Fall application recommended for phosphorus and potassium."
                if climate_zone:
                    if climate_zone in ['3a', '3b', '4a']:
                        base_advice += f" Zone {climate_zone} benefits from early fall application before freeze-up."
                return base_advice
            else:
                return "Spring application acceptable if fall application was missed."
    
    def _generate_generic_timing_advice(self, current_month: int, climate_zone: Optional[str] = None) -> str:
        """Generate generic timing advice with climate zone considerations."""
        climate_context = self._get_climate_timing_context(climate_zone) if climate_zone else ""
        
        if current_month in [3, 4, 5]:
            return f"Spring planning and implementation season. Monitor weather and soil conditions.{climate_context}"
        elif current_month in [6, 7, 8]:
            return f"Growing season monitoring period. Focus on crop management and assessment.{climate_context}"
        elif current_month in [9, 10, 11]:
            return f"Harvest and fall preparation season. Plan for next year's management.{climate_context}"
        else:
            return f"Winter planning period. Review performance and plan improvements.{climate_context}"

# Factory function for easy initialization
def create_ai_explanation_service() -> AIExplanationService:
    """Create and return an AI explanation service instance."""
    return AIExplanationService()
