"""
Core Recommendation Engine

Central orchestrator for all agricultural recommendations with expert-validated algorithms.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import asyncio

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from ..models.recommendation_filtering_models import (
        RecommendationRequestWithFiltering,
        FilteredRecommendationResponse,
        FilterImpactAnalysis
    )
    from ..services.enhanced_crop_recommendation_service import EnhancedCropRecommendationService
    from ..services.fertilizer_recommendation_service import FertilizerRecommendationService
    from ..services.soil_management_service import SoilManagementService
    from ..services.nutrient_deficiency_service import NutrientDeficiencyService
    from ..services.crop_rotation_service import CropRotationService
    from ..services.personalization_service import PersonalizationService
    from ..services.rule_engine import AgriculturalRuleEngine, RuleType
    from ..services.ai_explanation_service import AIExplanationService
    from ..services.climate_integration_service import climate_integration_service
    from ..services.location_integration_service import location_integration_service
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationResponse,
        RecommendationItem,
        ConfidenceFactors
    )
    from models.recommendation_filtering_models import (
        RecommendationRequestWithFiltering,
        FilteredRecommendationResponse,
        FilterImpactAnalysis
    )
    from services.enhanced_crop_recommendation_service import EnhancedCropRecommendationService
    from services.fertilizer_recommendation_service import FertilizerRecommendationService
    from services.soil_management_service import SoilManagementService
    from services.nutrient_deficiency_service import NutrientDeficiencyService
    from services.crop_rotation_service import CropRotationService
    from services.personalization_service import PersonalizationService
    from services.rule_engine import AgriculturalRuleEngine, RuleType
    from services.ai_explanation_service import AIExplanationService
    from services.climate_integration_service import climate_integration_service
    from services.location_integration_service import location_integration_service

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Core recommendation engine that orchestrates all agricultural recommendations.
    
    This class implements the central logic for processing farmer questions and
    generating expert-validated agricultural recommendations.
    """
    
    def __init__(self):
        """Initialize recommendation engine with all service components."""
        self.crop_service = CropRecommendationService()
        self.enhanced_crop_service = EnhancedCropRecommendationService()
        self.fertilizer_service = FertilizerRecommendationService()
        self.soil_service = SoilManagementService()
        self.nutrient_service = NutrientDeficiencyService()
        self.rotation_service = CropRotationService()

        # Initialize the centralized rule engine
        self.rule_engine = AgriculturalRuleEngine()

        # Initialize AI explanation service
        self.ai_explanation_service = AIExplanationService()

        try:
            self.personalization_service = PersonalizationService()
        except Exception as exc:
            logger.warning("Personalization service disabled: %s", exc)
            self.personalization_service = None
        
        # Question type mapping to service methods
        self.question_handlers = {
            "crop_selection": self._handle_crop_selection,
            "crop_selection_with_filtering": self._handle_crop_selection_with_filtering,
            "soil_fertility": self._handle_soil_fertility,
            "crop_rotation": self._handle_crop_rotation,
            "nutrient_deficiency": self._handle_nutrient_deficiency,
            "fertilizer_selection": self._handle_fertilizer_selection,
            "fertilizer_strategy": self._handle_fertilizer_strategy,
            "soil_management": self._handle_soil_management,
            "ph_management": self._handle_ph_management,
            "organic_matter": self._handle_organic_matter,
            "nutrient_timing": self._handle_nutrient_timing
        }
    
    async def generate_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """
        Generate comprehensive agricultural recommendations based on request.
        
        Args:
            request: Recommendation request with farm data and question type
            
        Returns:
            Complete recommendation response with confidence scores and sources
        """
        try:
            logger.info(f"Processing recommendation request: {request.question_type}")
            
            # Validate request data
            self._validate_request(request)
            
            # LOCATION INTEGRATION: Deep integration with location services
            location_integration_result = None
            if request.location or True:  # Always attempt location integration
                try:
                    location_integration_result = await location_integration_service.integrate_location_with_recommendation(
                        request=request,
                        auto_detect_location=True,  # Auto-detect if no location provided
                        validate_location=True
                    )
                    
                    if location_integration_result.success:
                        logger.info(f"Location integration successful: {location_integration_result.enhanced_location.climate_zone if location_integration_result.enhanced_location else 'unknown'}")
                        
                        # Log regional adaptations
                        if location_integration_result.regional_adaptations:
                            logger.info(f"Regional adaptations applied: {len(location_integration_result.regional_adaptations)}")
                        
                        # Log agricultural suitability
                        if location_integration_result.agricultural_suitability:
                            logger.info(f"Agricultural suitability: {location_integration_result.agricultural_suitability}")
                    
                except Exception as e:
                    logger.warning(f"Location integration failed, proceeding with basic climate detection: {str(e)}")
                    
                    # Fallback to basic climate zone integration
                    if request.location:
                        try:
                            climate_data = await climate_integration_service.detect_climate_zone(
                                latitude=request.location.latitude,
                                longitude=request.location.longitude,
                                elevation_ft=getattr(request.location, 'elevation_ft', None)
                            )
                            
                            if climate_data:
                                # Enhance location data with climate zone information
                                enhanced_location_dict = climate_integration_service.enhance_location_with_climate(
                                    request.location.dict(), climate_data
                                )
                                
                                # Update request with enhanced location data (preserve original structure)
                                for key, value in enhanced_location_dict.items():
                                    if hasattr(request.location, key):
                                        setattr(request.location, key, value)
                                
                                logger.info(f"Fallback climate zone enhancement: {enhanced_location_dict.get('climate_zone', 'unknown')}")
                            
                        except Exception as e2:
                            logger.warning(f"Fallback climate zone detection also failed: {str(e2)}")
            
            # Check if this involves filtering and generate impact analysis if requested
            filter_impact_analysis = None
            filter_warnings = []
            filter_optimization_suggestions = []
            personalization_summary = None

            # Get handler for question type
            handler = self.question_handlers.get(request.question_type)
            if not handler:
                raise ValueError(f"Unsupported question type: {request.question_type}")
            
            # Generate recommendations using appropriate handler
            recommendations = await handler(request)
            
            # SPECIAL: If request includes filtering and wants impact analysis
            if (hasattr(request, 'filter_criteria') and 
                request.filter_criteria and 
                hasattr(request, 'request_filter_impact_analysis') and 
                request.request_filter_impact_analysis):
                
                try:
                    filter_impact_analysis = await self.enhanced_crop_service.get_filter_impact_analysis(
                        request, request.filter_criteria
                    )
                    
                    # Extract warnings and suggestions from impact analysis
                    filter_warnings = filter_impact_analysis.get("filter_warnings", [])
                    filter_optimization_suggestions = filter_impact_analysis.get("filter_optimization_recommendations", [])
                    
                except Exception as e:
                    logger.warning(f"Filter impact analysis failed: {str(e)}")
            
            # LOCATION-BASED INTEGRATION: Apply location-specific adjustments
            if location_integration_result and location_integration_result.success and recommendations:
                # Apply regional adaptations to recommendations
                if location_integration_result.regional_adaptations:
                    recommendations = self._apply_regional_adaptations(
                        recommendations, location_integration_result.regional_adaptations
                    )
                
                # Apply agricultural suitability adjustments
                if location_integration_result.agricultural_suitability:
                    recommendations = self._apply_agricultural_suitability_adjustments(
                        recommendations, location_integration_result.agricultural_suitability
                    )
            
            # CLIMATE ZONE INTEGRATION: Adjust recommendations based on climate data
            elif climate_data and recommendations:
                if request.question_type in ["crop_selection", "crop_selection_with_filtering", "crop_rotation"]:
                    recommendations = climate_integration_service.get_climate_adjusted_crop_recommendations(
                        [rec.dict() for rec in recommendations], climate_data
                    )
                    # Convert back to RecommendationItem objects
                    recommendations = [RecommendationItem(**rec) for rec in recommendations]
                
                elif request.question_type in ["fertilizer_strategy", "fertilizer_selection", "nutrient_timing"]:
                    recommendations = climate_integration_service.get_climate_adjusted_fertilizer_recommendations(
                        [rec.dict() for rec in recommendations], climate_data
                    )
                    # Convert back to RecommendationItem objects
                    recommendations = [RecommendationItem(**rec) for rec in recommendations]

            if self.personalization_service:
                try:
                    personalization_result = await self.personalization_service.personalize_recommendations(
                        request,
                        recommendations,
                    )
                    updated_list = personalization_result.get("recommendations")
                    if updated_list:
                        recommendations = updated_list
                    personalization_summary = personalization_result.get("summary")
                except Exception as personalization_error:
                    logger.warning(
                        "Personalization adjustments failed: %s",
                        personalization_error,
                    )

            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(recommendations, request)

            # Build confidence factors (enhanced with climate data)
            confidence_factors = self._build_confidence_factors(request, climate_data)

            # Enhance recommendations with AI explanations
            recommendations = self._enhance_with_ai_explanations(recommendations, request)

            if self.personalization_service:
                try:
                    await self.personalization_service.log_recommendation_delivery(
                        request,
                        recommendations,
                        personalization_summary,
                    )
                except Exception as learning_error:
                    logger.debug(
                        "Failed to log personalization learning event: %s",
                        learning_error,
                    )

            # Generate warnings and next steps (enhanced with climate warnings)
            warnings = self._generate_warnings(request, recommendations, climate_data)
            # Add filter-specific warnings if any
            if hasattr(request, 'filter_criteria') and request.filter_criteria:
                warnings.extend(filter_warnings)

            next_steps = self._generate_next_steps(request, recommendations)
            # Add filter optimization suggestions to next steps if any
            if filter_optimization_suggestions:
                suggestion_index = 0
                while suggestion_index < len(filter_optimization_suggestions):
                    suggestion_text = filter_optimization_suggestions[suggestion_index]
                    next_steps.append(f"Filter optimization: {suggestion_text}")
                    suggestion_index += 1

            if personalization_summary and personalization_summary.get("insights"):
                insight_entries = personalization_summary["insights"]
                insight_index = 0
                while insight_index < len(insight_entries):
                    insight_text = insight_entries[insight_index]
                    next_steps.append(f"Personalization insight: {insight_text}")
                    insight_index += 1

            follow_up_questions = self._generate_follow_up_questions(request.question_type)

            # Create appropriate response based on whether filtering was used
            response_params = {
                "request_id": request.request_id,
                "question_type": request.question_type,
                "overall_confidence": overall_confidence,
                "confidence_factors": confidence_factors,
                "recommendations": recommendations,
                "warnings": warnings,
                "next_steps": next_steps,
                "follow_up_questions": follow_up_questions,
                "personalization_summary": personalization_summary,
            }
            
            # Use enhanced response if filtering was applied
            if filter_impact_analysis:
                from ..models.recommendation_filtering_models import FilteredRecommendationResponse
                response = FilteredRecommendationResponse(
                    **response_params,
                    filter_impact_analysis=self._convert_impact_analysis(filter_impact_analysis),
                    filter_warnings=filter_warnings,
                    filter_optimization_suggestions=filter_optimization_suggestions
                )
            else:
                response = RecommendationResponse(**response_params)
            
            logger.info(f"Generated {len(recommendations)} recommendations with confidence {overall_confidence:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            raise
    
    def _convert_impact_analysis(self, analysis_dict: Dict[str, Any]) -> FilterImpactAnalysis:
        """
        Convert impact analysis dictionary to FilterImpactAnalysis model.
        
        Args:
            analysis_dict: Dictionary containing impact analysis data
            
        Returns:
            FilterImpactAnalysis model instance
        """
        return FilterImpactAnalysis(
            original_count=analysis_dict.get('original_count', 0),
            filtered_count=analysis_dict.get('filtered_count', 0),
            filter_reduction_percentage=analysis_dict.get('filter_reduction_percentage', 0.0),
            most_affected_criteria=analysis_dict.get('most_affected_criteria', []),
            alternative_suggestions=analysis_dict.get('alternative_suggestions', []),
            filter_optimization_recommendations=analysis_dict.get('filter_optimization_recommendations', []),
            baseline_recommendations=analysis_dict.get('baseline_recommendations', []),
            filtered_recommendations=analysis_dict.get('filtered_recommendations', [])
        )
    
    async def _handle_crop_selection(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle crop selection recommendations (Question 1)."""
        # Get rule-based recommendations first
        rule_recommendations = self._get_rule_based_recommendations(request, RuleType.CROP_SUITABILITY)
        
        # Get service-based recommendations
        service_recommendations = await self.crop_service.get_crop_recommendations(request)
        
        # Enhance service recommendations with rule engine insights
        enhanced_recommendations = self._enhance_with_rule_insights(
            service_recommendations, rule_recommendations, request
        )
        
        return enhanced_recommendations

    async def _handle_crop_selection_with_filtering(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle crop selection with advanced filtering integration."""
        try:
            # Check if request has filter criteria (this would come from the enhanced request model)
            filter_criteria = getattr(request, 'filter_criteria', None)
            
            if filter_criteria:
                # Use the enhanced service with filtering
                recommendations = await self.enhanced_crop_service.get_crop_recommendations_with_filters(
                    request, filter_criteria
                )
                
                # Apply rule-based enhancements
                rule_recommendations = self._get_rule_based_recommendations(request, RuleType.CROP_SUITABILITY)
                enhanced_recommendations = self._enhance_with_rule_insights(
                    recommendations, rule_recommendations, request
                )
                
                return enhanced_recommendations
            else:
                # Fallback to standard crop selection
                return await self._handle_crop_selection(request)
        except Exception as e:
            logger.error(f"Error in crop selection with filtering: {e}")
            # Fallback to standard crop selection if filtering fails
            return await self._handle_crop_selection(request)
    
    async def _handle_soil_fertility(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle soil fertility improvement recommendations (Question 2)."""
        return await self.soil_service.get_fertility_recommendations(request)
    
    async def _handle_crop_rotation(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle crop rotation recommendations (Question 3)."""
        return await self.rotation_service.get_rotation_recommendations(request)
    
    async def _handle_nutrient_deficiency(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle nutrient deficiency detection recommendations (Question 4)."""
        return await self.nutrient_service.get_deficiency_recommendations(request)
    
    async def _handle_fertilizer_selection(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle fertilizer type selection recommendations (Question 5)."""
        return await self.fertilizer_service.get_fertilizer_type_recommendations(request)
    
    async def _handle_fertilizer_strategy(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle comprehensive fertilizer strategy recommendations."""
        # Get rule-based fertilizer recommendations
        rule_recommendations = self._get_rule_based_recommendations(request, RuleType.FERTILIZER_RATE)
        
        # Get service-based recommendations
        service_recommendations = await self.fertilizer_service.get_fertilizer_strategy_recommendations(request)
        
        # Use decision tree for nitrogen rate calculation if applicable
        if request.crop_data and request.soil_data:
            dt_nitrogen_rate = self._get_decision_tree_nitrogen_rate(request)
            service_recommendations = self._adjust_nitrogen_recommendations(
                service_recommendations, dt_nitrogen_rate
            )
        
        # Enhance with rule insights
        enhanced_recommendations = self._enhance_with_rule_insights(
            service_recommendations, rule_recommendations, request
        )
        
        return enhanced_recommendations
    
    async def _handle_soil_management(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle general soil management recommendations."""
        return await self.soil_service.get_management_recommendations(request)
    
    async def _handle_ph_management(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle soil pH management recommendations."""
        return await self.soil_service.get_ph_management_recommendations(request)
    
    async def _handle_organic_matter(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle organic matter improvement recommendations."""
        return await self.soil_service.get_organic_matter_recommendations(request)
    
    async def _handle_nutrient_timing(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Handle nutrient application timing recommendations."""
        return await self.fertilizer_service.get_timing_recommendations(request)
    
    def _validate_request(self, request: RecommendationRequest) -> None:
        """Validate recommendation request data."""
        if not request.request_id:
            raise ValueError("Request ID is required")
        
        if not request.question_type:
            raise ValueError("Question type is required")
        
        if not request.location:
            raise ValueError("Location data is required for agricultural recommendations")
        
        # Validate location coordinates
        if not (-90 <= request.location.latitude <= 90):
            raise ValueError("Invalid latitude value")
        
        if not (-180 <= request.location.longitude <= 180):
            raise ValueError("Invalid longitude value")
    
    def _calculate_overall_confidence(
        self, 
        recommendations: List[RecommendationItem], 
        request: RecommendationRequest
    ) -> float:
        """Calculate overall confidence score for recommendations."""
        if not recommendations:
            return 0.0
        
        # Weight recommendations by priority (higher priority = more weight)
        total_weighted_confidence = 0.0
        total_weight = 0.0
        
        for rec in recommendations:
            # Convert priority to weight (priority 1 = weight 3, priority 2 = weight 2, etc.)
            weight = max(1.0, 4.0 - rec.priority)
            total_weighted_confidence += rec.confidence_score * weight
            total_weight += weight
        
        base_confidence = total_weighted_confidence / total_weight if total_weight > 0 else 0.0
        
        # Apply data quality adjustments
        data_quality_factor = 1.0
        
        if not request.soil_data:
            data_quality_factor *= 0.7  # Reduce confidence without soil data
        elif request.soil_data.test_date:
            # Reduce confidence for old soil tests
            from datetime import date, timedelta
            age_days = (date.today() - request.soil_data.test_date).days
            if age_days > 365 * 2:  # Older than 2 years
                data_quality_factor *= 0.9
            elif age_days > 365 * 3:  # Older than 3 years
                data_quality_factor *= 0.8
        
        return min(1.0, base_confidence * data_quality_factor)
    
    def _build_confidence_factors(self, request: RecommendationRequest, climate_data: Optional[Dict[str, Any]] = None) -> ConfidenceFactors:
        """Build detailed confidence factors breakdown."""
        
        # Soil data quality assessment
        soil_quality = 0.3  # Default low quality without data
        if request.soil_data:
            soil_quality = 0.7  # Base quality with data
            
            # Bonus for complete data
            if all([
                request.soil_data.ph,
                request.soil_data.organic_matter_percent,
                request.soil_data.phosphorus_ppm,
                request.soil_data.potassium_ppm
            ]):
                soil_quality = 0.9
            
            # Bonus for recent data
            if request.soil_data.test_date:
                from datetime import date, timedelta
                age_days = (date.today() - request.soil_data.test_date).days
                if age_days <= 365:  # Within 1 year
                    soil_quality = min(1.0, soil_quality + 0.1)
        
        # Regional data availability (would be enhanced with actual regional database)
        regional_availability = 0.8
        if request.location:
            # US locations generally have better data
            if -125 <= request.location.longitude <= -66 and 20 <= request.location.latitude <= 49:
                regional_availability = 0.9
        
        # Seasonal appropriateness (would be enhanced with actual seasonal logic)
        seasonal_appropriateness = 0.8
        current_month = datetime.now().month
        if request.question_type in ["crop_selection", "fertilizer_strategy"]:
            # Higher confidence during planning season (fall/winter/early spring)
            if current_month in [10, 11, 12, 1, 2, 3, 4]:
                seasonal_appropriateness = 0.9
        
        # Expert validation level (based on algorithm validation status)
        expert_validation = 0.85  # Current validation level
        
        # Climate data enhancement
        if climate_data:
            climate_confidence = climate_data.get('confidence_score', 0.7)
            # Enhance regional availability with climate data
            regional_availability = min(1.0, regional_availability + (climate_confidence * 0.1))
            
            # Enhance expert validation with climate zone information
            if climate_confidence > 0.8:
                expert_validation = min(1.0, expert_validation + 0.05)
        
        return ConfidenceFactors(
            soil_data_quality=soil_quality,
            regional_data_availability=regional_availability,
            seasonal_appropriateness=seasonal_appropriateness,
            expert_validation=expert_validation
        )
    
    def _generate_warnings(
        self, 
        request: RecommendationRequest, 
        recommendations: List[RecommendationItem],
        climate_data: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Generate appropriate warnings based on request and recommendations."""
        warnings = []
        
        # Data quality warnings
        if not request.soil_data:
            warnings.append(
                "Recommendations are based on general conditions. "
                "Soil testing is strongly recommended for accurate, site-specific advice."
            )
        
        # Soil condition warnings
        if request.soil_data:
            if request.soil_data.ph and request.soil_data.ph < 5.0:
                warnings.append(
                    "Extremely acidic soil (pH < 5.0) may severely limit crop options "
                    "and require significant lime application before planting."
                )
            elif request.soil_data.ph and request.soil_data.ph > 8.5:
                warnings.append(
                    "Very alkaline soil (pH > 8.5) may cause micronutrient deficiencies "
                    "and limit nutrient availability."
                )
            
            if (request.soil_data.organic_matter_percent and 
                request.soil_data.organic_matter_percent < 2.0):
                warnings.append(
                    "Low organic matter (<2%) indicates poor soil health. "
                    "Consider long-term soil building practices."
                )
        
        # Regional warnings
        if request.location and request.location.latitude > 45:
            warnings.append(
                "Northern locations have shorter growing seasons. "
                "Verify variety maturity and frost tolerance."
            )
        
        # Climate-specific warnings
        if climate_data and 'primary_zone' in climate_data:
            primary_zone = climate_data['primary_zone']
            usda_zone = primary_zone.get('zone_id', '')
            
            if usda_zone:
                zone_num = int(usda_zone[0]) if usda_zone[0].isdigit() else 6
                
                # Extreme climate warnings
                if zone_num <= 3:
                    warnings.append(
                        f"USDA Zone {usda_zone} has very short growing seasons and extreme cold. "
                        "Verify all recommendations are suitable for arctic/subarctic conditions."
                    )
                elif zone_num >= 10:
                    warnings.append(
                        f"USDA Zone {usda_zone} has intense heat and possible drought stress. "
                        "Ensure adequate irrigation and heat protection measures."
                    )
                
                # Climate transition warnings
                if climate_data.get('confidence_score', 1.0) < 0.7:
                    warnings.append(
                        "Location appears to be in a climate transition zone. "
                        "Monitor local weather patterns closely and consider multiple climate scenarios."
                    )
        
        # Confidence warnings
        overall_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations) if recommendations else 0
        if overall_confidence < 0.7:
            warnings.append(
                "Lower confidence recommendations due to limited data. "
                "Consider consulting local agricultural experts."
            )
        
        return warnings
    
    def _generate_next_steps(
        self, 
        request: RecommendationRequest, 
        recommendations: List[RecommendationItem]
    ) -> List[str]:
        """Generate suggested next steps based on recommendations."""
        next_steps = []
        
        # Always recommend soil testing if not recent
        if not request.soil_data:
            next_steps.append("Obtain comprehensive soil test from certified laboratory")
        elif request.soil_data.test_date:
            from datetime import date, timedelta
            age_days = (date.today() - request.soil_data.test_date).days
            if age_days > 365 * 2:
                next_steps.append("Update soil test - current data is over 2 years old")
        
        # Question-specific next steps
        if request.question_type == "crop_selection":
            next_steps.extend([
                "Research local variety trials and performance data",
                "Contact seed dealers for variety availability and pricing",
                "Review crop insurance options and coverage",
                "Plan field preparation and planting schedule"
            ])
        elif request.question_type in ["fertilizer_strategy", "fertilizer_selection"]:
            next_steps.extend([
                "Obtain current fertilizer prices from local suppliers",
                "Schedule fertilizer application equipment",
                "Plan application timing with weather forecasts",
                "Consider precision application technology"
            ])
        elif request.question_type in ["soil_fertility", "soil_management"]:
            next_steps.extend([
                "Develop multi-year soil improvement plan",
                "Consider cover crop integration",
                "Evaluate current tillage practices",
                "Plan organic matter improvement strategies"
            ])
        
        # Always recommend expert consultation
        next_steps.append("Consult local extension service or certified crop advisor")
        
        return next_steps
    
    def _generate_follow_up_questions(self, question_type: str) -> List[str]:
        """Generate relevant follow-up questions based on current question type."""
        
        follow_up_map = {
            "crop_selection": [
                "What fertilizer strategy should I use for this crop?",
                "When is the optimal planting time for my location?",
                "What are the expected input costs and profit margins?",
                "Should I consider crop insurance for this selection?"
            ],
            "soil_fertility": [
                "What crop rotation would best improve my soil health?",
                "Should I invest in organic or synthetic fertilizers?",
                "How can I detect nutrient deficiencies early?",
                "What cover crops would benefit my soil?"
            ],
            "fertilizer_strategy": [
                "How do I time fertilizer applications for maximum efficiency?",
                "What equipment do I need for precise application?",
                "How can I reduce fertilizer costs while maintaining yields?",
                "Should I consider slow-release fertilizer options?"
            ],
            "crop_rotation": [
                "What crops are best suited to my soil type?",
                "How can I improve soil fertility through rotation?",
                "What are the economic benefits of this rotation?",
                "How do I manage pests and diseases in rotation?"
            ],
            "nutrient_deficiency": [
                "What fertilizer strategy addresses these deficiencies?",
                "How can I prevent these deficiencies in the future?",
                "Should I consider foliar feeding for quick correction?",
                "What soil amendments would help long-term?"
            ]
        }
        
        return follow_up_map.get(question_type, [
            "What other aspects of my farming operation should I consider?",
            "How can I improve my overall farm profitability?",
            "What sustainable practices should I adopt?",
            "How can I prepare for climate variability?"
        ])
    
    def _get_rule_based_recommendations(self, request: RecommendationRequest, rule_type: RuleType) -> List:
        """Get recommendations from the rule engine."""
        try:
            rule_results = self.rule_engine.evaluate_rules(request, rule_type)
            return [result for result in rule_results if result.matched]
        except Exception as e:
            logger.error(f"Error getting rule-based recommendations: {str(e)}")
            return []
    
    def _enhance_with_rule_insights(
        self, 
        service_recommendations: List[RecommendationItem], 
        rule_recommendations: List, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Enhance service recommendations with rule engine insights."""
        
        enhanced_recommendations = []
        
        for rec in service_recommendations:
            enhanced_rec = rec.copy()
            
            # Find matching rule recommendations
            matching_rules = [
                rule_rec for rule_rec in rule_recommendations 
                if self._recommendations_match(rec, rule_rec)
            ]
            
            if matching_rules:
                # Adjust confidence based on rule validation
                rule_confidence = max(rule.confidence for rule in matching_rules)
                enhanced_rec.confidence_score = (rec.confidence_score + rule_confidence) / 2
                
                # Add rule-based explanations
                rule_explanations = [rule.explanation for rule in matching_rules]
                if rule_explanations:
                    enhanced_rec.description += f" Rule validation: {'; '.join(rule_explanations[:2])}"
                
                # Add agricultural sources from rules
                rule_sources = [
                    self.rule_engine.rules[rule.rule_id].agricultural_source 
                    for rule in matching_rules
                ]
                enhanced_rec.agricultural_sources.extend(rule_sources)
            
            enhanced_recommendations.append(enhanced_rec)
        
        # Add pure rule-based recommendations that don't match service recommendations
        for rule_rec in rule_recommendations:
            if not any(self._recommendations_match(rec, rule_rec) for rec in service_recommendations):
                rule_based_rec = self._convert_rule_to_recommendation(rule_rec, request)
                if rule_based_rec:
                    enhanced_recommendations.append(rule_based_rec)
        
        return enhanced_recommendations
    
    def _recommendations_match(self, service_rec: RecommendationItem, rule_rec) -> bool:
        """Check if service and rule recommendations are related."""
        # Simple matching based on recommendation type and content
        service_type = service_rec.recommendation_type.lower()
        rule_action = str(rule_rec.action).lower()
        
        # Check for common keywords
        common_keywords = ["crop", "fertilizer", "nitrogen", "phosphorus", "potassium", "soil", "lime"]
        
        for keyword in common_keywords:
            if keyword in service_type and keyword in rule_action:
                return True
        
        return False
    
    def _convert_rule_to_recommendation(self, rule_result, request: RecommendationRequest) -> Optional[RecommendationItem]:
        """Convert a rule evaluation result to a recommendation item."""
        try:
            rule = self.rule_engine.rules[rule_result.rule_id]
            action = rule_result.action
            
            # Create recommendation based on rule action
            if "crop" in action:
                return self._create_crop_recommendation_from_rule(rule, action, rule_result.confidence)
            elif "amendment" in action or "strategy" in action:
                return self._create_soil_recommendation_from_rule(rule, action, rule_result.confidence)
            elif "deficiency" in action:
                return self._create_nutrient_recommendation_from_rule(rule, action, rule_result.confidence)
            
            return None
        except Exception as e:
            logger.error(f"Error converting rule to recommendation: {str(e)}")
            return None
    
    def _create_crop_recommendation_from_rule(self, rule, action: Dict, confidence: float) -> RecommendationItem:
        """Create crop recommendation from rule action."""
        crop_name = action.get("crop", "Unknown")
        suitability = action.get("recommendation", "suitable")
        yield_range = action.get("expected_yield_range", (0, 0))
        
        return RecommendationItem(
            recommendation_type="crop_selection_rule",
            title=f"{crop_name.title()} - {suitability.replace('_', ' ').title()}",
            description=f"Rule-based analysis indicates {crop_name} is {suitability.replace('_', ' ')} "
                       f"for your farm conditions. {rule.description}",
            priority=rule.priority,
            confidence_score=confidence,
            implementation_steps=[
                f"Verify {crop_name} variety availability in your area",
                "Confirm soil preparation requirements",
                "Plan planting schedule based on local conditions"
            ],
            expected_outcomes=[
                f"Expected yield range: {yield_range[0]}-{yield_range[1]} bu/acre" if yield_range[0] > 0 else "Suitable crop performance",
                "Alignment with soil and climate conditions",
                "Reduced production risks"
            ],
            timing="Plan for next growing season",
            agricultural_sources=[rule.agricultural_source]
        )
    
    def _create_soil_recommendation_from_rule(self, rule, action: Dict, confidence: float) -> RecommendationItem:
        """Create soil management recommendation from rule action."""
        amendment = action.get("amendment", action.get("strategy", "soil improvement"))
        
        return RecommendationItem(
            recommendation_type="soil_management_rule",
            title=f"Soil Management: {amendment.replace('_', ' ').title()}",
            description=f"Rule-based analysis recommends {amendment.replace('_', ' ')} "
                       f"based on your soil conditions. {rule.description}",
            priority=rule.priority,
            confidence_score=confidence,
            implementation_steps=[
                f"Implement {amendment.replace('_', ' ')} strategy",
                "Monitor soil response over time",
                "Retest soil to verify improvements"
            ],
            expected_outcomes=[
                "Improved soil health and fertility",
                "Better nutrient availability",
                "Enhanced crop performance"
            ],
            timing=action.get("application_timing", "As recommended"),
            agricultural_sources=[rule.agricultural_source]
        )
    
    def _create_nutrient_recommendation_from_rule(self, rule, action: Dict, confidence: float) -> RecommendationItem:
        """Create nutrient management recommendation from rule action."""
        deficiency = action.get("deficiency", "nutrient")
        severity = action.get("severity", "moderate")
        
        return RecommendationItem(
            recommendation_type="nutrient_management_rule",
            title=f"{deficiency.title()} Deficiency Management",
            description=f"Rule-based analysis detected {severity} {deficiency} deficiency. "
                       f"{rule.description}",
            priority=rule.priority,
            confidence_score=confidence,
            implementation_steps=[
                f"Address {deficiency} deficiency immediately",
                "Apply recommended correction rate",
                "Monitor crop response",
                "Adjust long-term fertility program"
            ],
            expected_outcomes=[
                f"Corrected {deficiency} deficiency",
                "Improved crop health and yield",
                "Prevented further nutrient-related issues"
            ],
            timing=action.get("immediate_action", "Immediate attention required"),
            agricultural_sources=[rule.agricultural_source]
        )
    
    def _get_decision_tree_nitrogen_rate(self, request: RecommendationRequest) -> Dict:
        """Get nitrogen rate recommendation from decision tree."""
        try:
            features = {
                'yield_goal': request.crop_data.yield_goal or 150,
                'soil_n': request.soil_data.nitrogen_ppm or 10,
                'organic_matter': request.soil_data.organic_matter_percent or 3.0,
                'previous_legume': 1 if request.crop_data.previous_crop == "soybean" else 0,
                'ph': request.soil_data.ph or 6.2
            }
            
            return self.rule_engine.predict_with_decision_tree('nitrogen_rate', features)
        except Exception as e:
            logger.error(f"Error getting decision tree nitrogen rate: {str(e)}")
            return {}
    
    def _adjust_nitrogen_recommendations(
        self, 
        recommendations: List[RecommendationItem], 
        dt_nitrogen_rate: Dict
    ) -> List[RecommendationItem]:
        """Adjust nitrogen recommendations based on decision tree results."""
        if not dt_nitrogen_rate or 'nitrogen_rate' not in dt_nitrogen_rate:
            return recommendations
        
        dt_rate = dt_nitrogen_rate['nitrogen_rate']
        dt_confidence = dt_nitrogen_rate.get('confidence', 0.8)
        
        adjusted_recommendations = []
        
        for rec in recommendations:
            if "nitrogen" in rec.recommendation_type.lower():
                # Adjust the recommendation based on decision tree
                adjusted_rec = rec.copy()
                
                # Update description with decision tree insight
                adjusted_rec.description += f" Decision tree analysis suggests {dt_rate:.0f} lbs N/acre " \
                                          f"(confidence: {dt_confidence:.2f})."
                
                # Adjust confidence score
                adjusted_rec.confidence_score = (rec.confidence_score + dt_confidence) / 2
                
                adjusted_recommendations.append(adjusted_rec)
            else:
                adjusted_recommendations.append(rec)
        
        return adjusted_recommendations
    
    def _enhance_with_ai_explanations(
        self, 
        recommendations: List[RecommendationItem], 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """
        Enhance recommendations with AI-generated explanations.
        
        Args:
            recommendations: List of recommendation items to enhance
            request: Original recommendation request for context
            
        Returns:
            Enhanced recommendations with AI explanations
        """
        try:
            enhanced_recommendations = []
            
            # Prepare context for AI explanation generation
            context = {
                'soil_data': request.soil_data.dict() if request.soil_data else {},
                'farm_profile': request.farm_profile.dict() if request.farm_profile else {},
                'location': request.location.dict() if request.location else {}
            }
            
            for rec in recommendations:
                enhanced_rec = rec.copy()
                
                # Generate AI explanation for the recommendation
                ai_explanation = self.ai_explanation_service.generate_explanation(
                    recommendation_type=request.question_type,
                    recommendation_data=rec.dict(),
                    context=context
                )
                
                # Enhance the description with AI explanation
                if ai_explanation and ai_explanation != enhanced_rec.description:
                    enhanced_rec.description = f"{enhanced_rec.description} {ai_explanation}"
                
                # Generate implementation steps using AI service
                ai_steps = self.ai_explanation_service.generate_implementation_steps(
                    recommendation_type=request.question_type,
                    recommendation_data=rec.dict()
                )
                
                # Merge AI-generated steps with existing steps
                if ai_steps:
                    existing_steps = enhanced_rec.implementation_steps or []
                    # Combine and deduplicate steps
                    all_steps = existing_steps + ai_steps
                    unique_steps = []
                    seen_steps = set()
                    
                    for step in all_steps:
                        step_lower = step.lower()
                        if step_lower not in seen_steps:
                            unique_steps.append(step)
                            seen_steps.add(step_lower)
                    
                    enhanced_rec.implementation_steps = unique_steps[:10]  # Limit to 10 steps
                
                enhanced_recommendations.append(enhanced_rec)
            
            logger.info(f"Enhanced {len(recommendations)} recommendations with AI explanations")
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error enhancing recommendations with AI explanations: {e}")
            # Return original recommendations if AI enhancement fails
            return recommendations
    
    def _apply_regional_adaptations(
        self,
        recommendations: List[RecommendationItem],
        regional_adaptations: List[str]
    ) -> List[RecommendationItem]:
        """
        Apply regional adaptations to recommendations.
        
        Args:
            recommendations: List of recommendation items
            regional_adaptations: List of regional adaptation strings
            
        Returns:
            Recommendations with regional adaptations applied
        """
        try:
            enhanced_recommendations = []
            
            for rec in recommendations:
                enhanced_rec = rec.copy()
                
                # Add regional adaptations to description
                if regional_adaptations:
                    adaptation_text = "Regional considerations: " + "; ".join(regional_adaptations[:3])
                    enhanced_rec.description = f"{enhanced_rec.description} {adaptation_text}"
                
                # Add regional adaptations to implementation steps
                if regional_adaptations:
                    existing_steps = enhanced_rec.implementation_steps or []
                    regional_steps = [f"Consider regional practice: {adaptation}" for adaptation in regional_adaptations[:2]]
                    enhanced_rec.implementation_steps = existing_steps + regional_steps
                
                enhanced_recommendations.append(enhanced_rec)
            
            logger.info(f"Applied {len(regional_adaptations)} regional adaptations to {len(recommendations)} recommendations")
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error applying regional adaptations: {e}")
            return recommendations
    
    def _apply_agricultural_suitability_adjustments(
        self,
        recommendations: List[RecommendationItem],
        agricultural_suitability: str
    ) -> List[RecommendationItem]:
        """
        Apply agricultural suitability adjustments to recommendations.
        
        Args:
            recommendations: List of recommendation items
            agricultural_suitability: Agricultural suitability rating
            
        Returns:
            Recommendations with agricultural suitability adjustments applied
        """
        try:
            enhanced_recommendations = []
            
            # Define suitability-based adjustments
            suitability_adjustments = {
                "excellent": {
                    "confidence_boost": 0.1,
                    "message": "Location has excellent agricultural potential"
                },
                "very_good": {
                    "confidence_boost": 0.05,
                    "message": "Location has very good agricultural potential"
                },
                "good": {
                    "confidence_boost": 0.0,
                    "message": "Location has good agricultural potential"
                },
                "moderate": {
                    "confidence_boost": -0.05,
                    "message": "Location has moderate agricultural potential - consider site-specific adjustments"
                },
                "challenging": {
                    "confidence_boost": -0.1,
                    "message": "Location has challenging agricultural conditions - expert consultation recommended"
                },
                "limited": {
                    "confidence_boost": -0.15,
                    "message": "Location has limited agricultural potential - consider alternative approaches"
                }
            }
            
            adjustment = suitability_adjustments.get(agricultural_suitability, suitability_adjustments["moderate"])
            
            for rec in recommendations:
                enhanced_rec = rec.copy()
                
                # Adjust confidence based on agricultural suitability
                enhanced_rec.confidence = max(0.0, min(1.0, enhanced_rec.confidence + adjustment["confidence_boost"]))
                
                # Add suitability message to description
                enhanced_rec.description = f"{enhanced_rec.description} {adjustment['message']}"
                
                enhanced_recommendations.append(enhanced_rec)
            
            logger.info(f"Applied agricultural suitability adjustments ({agricultural_suitability}) to {len(recommendations)} recommendations")
            return enhanced_recommendations
            
        except Exception as e:
            logger.error(f"Error applying agricultural suitability adjustments: {e}")
            return recommendations
