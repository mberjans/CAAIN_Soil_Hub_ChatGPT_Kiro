"""
AFAS Knowledge Manager
Autonomous Farm Advisory System
Version: 1.0
Date: December 2024

This module provides a high-level interface for managing agricultural knowledge
and integrating it with the recommendation engine.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, date
from dataclasses import dataclass
import json

from .knowledge_base import (
    KnowledgeBase, KnowledgeCategory, KnowledgeItem, 
    KnowledgeSource, SourceType, initialize_knowledge_base
)

logger = logging.getLogger(__name__)

@dataclass
class RecommendationContext:
    """Context information for generating recommendations."""
    user_id: str
    farm_id: Optional[str] = None
    field_id: Optional[str] = None
    location: Optional[Dict[str, float]] = None
    soil_data: Optional[Dict[str, Any]] = None
    crop_data: Optional[Dict[str, Any]] = None
    weather_data: Optional[Dict[str, Any]] = None
    farm_constraints: Optional[Dict[str, Any]] = None
    question_type: Optional[str] = None

class KnowledgeManager:
    """
    High-level knowledge manager that provides agricultural expertise
    for the recommendation engine.
    """
    
    def __init__(self):
        """Initialize the knowledge manager."""
        self.knowledge_base = initialize_knowledge_base()
        self._question_type_mapping = self._initialize_question_mapping()
        logger.info("Knowledge manager initialized")
    
    def _initialize_question_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Initialize mapping of question types to knowledge categories."""
        return {
            "crop_selection": {
                "categories": [KnowledgeCategory.CROP_MANAGEMENT],
                "subcategories": ["variety_selection", "adaptation", "requirements"],
                "required_data": ["location", "soil_data"],
                "optional_data": ["climate_preferences", "farm_constraints"]
            },
            "soil_fertility": {
                "categories": [KnowledgeCategory.SOIL_HEALTH, KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["fertility_improvement", "organic_matter", "ph_management"],
                "required_data": ["soil_data"],
                "optional_data": ["management_goals", "current_practices"]
            },
            "crop_rotation": {
                "categories": [KnowledgeCategory.CROP_MANAGEMENT],
                "subcategories": ["rotation", "succession", "benefits"],
                "required_data": ["crop_history"],
                "optional_data": ["soil_data", "pest_pressure"]
            },
            "nutrient_deficiency": {
                "categories": [KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["deficiency_diagnosis", "soil_testing", "tissue_testing"],
                "required_data": ["soil_data"],
                "optional_data": ["crop_symptoms", "tissue_test"]
            },
            "fertilizer_type": {
                "categories": [KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["fertilizer_selection", "organic_vs_synthetic"],
                "required_data": ["soil_data", "crop_type"],
                "optional_data": ["budget_constraints", "environmental_goals"]
            },
            "application_method": {
                "categories": [KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["application_methods", "timing", "placement"],
                "required_data": ["fertilizer_type", "crop_stage"],
                "optional_data": ["equipment_available", "weather_conditions"]
            },
            "fertilizer_timing": {
                "categories": [KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["timing", "split_applications"],
                "required_data": ["crop_type", "growth_stage"],
                "optional_data": ["weather_forecast", "soil_conditions"]
            },
            "environmental_impact": {
                "categories": [KnowledgeCategory.ENVIRONMENTAL_STEWARDSHIP],
                "subcategories": ["runoff_prevention", "water_quality", "sustainability"],
                "required_data": ["location", "soil_data"],
                "optional_data": ["slope", "drainage", "buffer_strips"]
            },
            "cover_crops": {
                "categories": [KnowledgeCategory.CROP_MANAGEMENT, KnowledgeCategory.SOIL_HEALTH],
                "subcategories": ["cover_crops", "species_selection", "termination"],
                "required_data": ["location", "main_crop"],
                "optional_data": ["soil_data", "management_goals"]
            },
            "soil_ph": {
                "categories": [KnowledgeCategory.SOIL_HEALTH],
                "subcategories": ["ph_management", "lime_application"],
                "required_data": ["soil_ph", "soil_type"],
                "optional_data": ["target_crops", "buffer_ph"]
            },
            "micronutrients": {
                "categories": [KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["micronutrients", "deficiency_correction"],
                "required_data": ["soil_data", "crop_type"],
                "optional_data": ["tissue_test", "deficiency_symptoms"]
            },
            "precision_agriculture": {
                "categories": [KnowledgeCategory.EQUIPMENT_OPERATION, KnowledgeCategory.ECONOMIC_ANALYSIS],
                "subcategories": ["technology_adoption", "roi_analysis"],
                "required_data": ["farm_size", "current_equipment"],
                "optional_data": ["budget", "tech_comfort_level"]
            },
            "drought_management": {
                "categories": [KnowledgeCategory.CROP_MANAGEMENT, KnowledgeCategory.ENVIRONMENTAL_STEWARDSHIP],
                "subcategories": ["water_conservation", "drought_tolerance"],
                "required_data": ["location", "crop_type"],
                "optional_data": ["irrigation_available", "soil_water_capacity"]
            },
            "deficiency_detection": {
                "categories": [KnowledgeCategory.NUTRIENT_MANAGEMENT, KnowledgeCategory.CROP_MANAGEMENT],
                "subcategories": ["symptom_recognition", "early_detection"],
                "required_data": ["crop_type", "growth_stage"],
                "optional_data": ["visual_symptoms", "tissue_test"]
            },
            "tillage_practices": {
                "categories": [KnowledgeCategory.SOIL_HEALTH, KnowledgeCategory.CROP_MANAGEMENT],
                "subcategories": ["tillage_systems", "soil_conservation"],
                "required_data": ["soil_type", "current_tillage"],
                "optional_data": ["erosion_risk", "equipment_available"]
            },
            "cost_optimization": {
                "categories": [KnowledgeCategory.ECONOMIC_ANALYSIS, KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["cost_analysis", "roi_optimization"],
                "required_data": ["input_prices", "yield_goals"],
                "optional_data": ["budget_constraints", "market_prices"]
            },
            "weather_integration": {
                "categories": [KnowledgeCategory.CROP_MANAGEMENT, KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["weather_impacts", "timing_adjustments"],
                "required_data": ["weather_data", "crop_stage"],
                "optional_data": ["forecast_data", "historical_patterns"]
            },
            "testing_integration": {
                "categories": [KnowledgeCategory.NUTRIENT_MANAGEMENT],
                "subcategories": ["soil_testing", "tissue_testing", "interpretation"],
                "required_data": ["test_results"],
                "optional_data": ["sampling_methods", "lab_procedures"]
            },
            "sustainable_intensification": {
                "categories": [KnowledgeCategory.ENVIRONMENTAL_STEWARDSHIP, KnowledgeCategory.CROP_MANAGEMENT],
                "subcategories": ["sustainability", "yield_optimization"],
                "required_data": ["current_practices", "yield_history"],
                "optional_data": ["environmental_goals", "certification_requirements"]
            },
            "policy_compliance": {
                "categories": [KnowledgeCategory.REGULATORY_COMPLIANCE],
                "subcategories": ["government_programs", "regulations", "subsidies"],
                "required_data": ["location", "farm_size"],
                "optional_data": ["current_programs", "compliance_history"]
            }
        }
    
    # ========================================================================
    # RECOMMENDATION GENERATION
    # ========================================================================
    
    def generate_recommendations(self, context: RecommendationContext) -> Dict[str, Any]:
        """
        Generate agricultural recommendations based on context.
        
        Args:
            context: Recommendation context with user data
            
        Returns:
            Dictionary containing recommendations and metadata
        """
        try:
            logger.info(f"Generating recommendations for question type: {context.question_type}")
            
            # Get relevant knowledge for the question type
            knowledge_items = self._get_relevant_knowledge(context)
            
            # Analyze the context data
            analysis = self._analyze_context(context)
            
            # Generate specific recommendations
            recommendations = self._generate_specific_recommendations(context, knowledge_items, analysis)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(context, knowledge_items, analysis)
            
            # Compile response
            response = {
                "recommendations": recommendations,
                "confidence_score": confidence_score,
                "confidence_factors": analysis.get("confidence_factors", {}),
                "knowledge_sources": [item.get("source", {}) for item in knowledge_items],
                "analysis_summary": analysis.get("summary", ""),
                "warnings": analysis.get("warnings", []),
                "next_steps": self._generate_next_steps(context, recommendations),
                "generated_at": datetime.utcnow().isoformat(),
                "context_completeness": self._assess_context_completeness(context)
            }
            
            # Store the recommendation
            recommendation_id = self.knowledge_base.store_recommendation(
                user_id=context.user_id,
                question_type=context.question_type,
                request_data=self._context_to_dict(context),
                response_data=response
            )
            
            response["recommendation_id"] = recommendation_id
            
            logger.info(f"Recommendations generated successfully with confidence: {confidence_score:.2f}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return {
                "recommendations": [],
                "confidence_score": 0.0,
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
    
    def _get_relevant_knowledge(self, context: RecommendationContext) -> List[Dict[str, Any]]:
        """Get relevant knowledge items for the context."""
        knowledge_items = []
        
        if not context.question_type:
            return knowledge_items
        
        question_config = self._question_type_mapping.get(context.question_type, {})
        categories = question_config.get("categories", [])
        
        # Get knowledge by categories
        for category in categories:
            items = self.knowledge_base.get_knowledge_by_category(
                category=category,
                expert_validated_only=True
            )
            knowledge_items.extend(items)
        
        # Get crop-specific knowledge if crop data is available
        if context.crop_data and context.crop_data.get("crop_name"):
            crop_knowledge = self.knowledge_base.get_knowledge_for_crop(
                crop_name=context.crop_data["crop_name"],
                categories=categories
            )
            knowledge_items.extend(crop_knowledge)
        
        # Search for specific knowledge based on question type
        search_terms = self._get_search_terms_for_question(context.question_type)
        if search_terms:
            search_results = self.knowledge_base.search_knowledge(
                search_text=search_terms,
                categories=categories,
                limit=10
            )
            knowledge_items.extend(search_results)
        
        # Remove duplicates based on knowledge_id
        seen_ids = set()
        unique_items = []
        for item in knowledge_items:
            knowledge_id = item.get("knowledge_id")
            if knowledge_id and knowledge_id not in seen_ids:
                seen_ids.add(knowledge_id)
                unique_items.append(item)
        
        logger.info(f"Retrieved {len(unique_items)} relevant knowledge items")
        return unique_items
    
    def _get_search_terms_for_question(self, question_type: str) -> str:
        """Get search terms for a specific question type."""
        search_mapping = {
            "crop_selection": "crop variety selection adaptation suitability",
            "soil_fertility": "soil fertility improvement organic matter pH",
            "crop_rotation": "crop rotation benefits succession planning",
            "nutrient_deficiency": "nutrient deficiency diagnosis symptoms",
            "fertilizer_type": "fertilizer selection organic synthetic",
            "application_method": "fertilizer application method timing placement",
            "fertilizer_timing": "fertilizer timing split application",
            "environmental_impact": "environmental impact runoff water quality",
            "cover_crops": "cover crops species selection benefits",
            "soil_ph": "soil pH lime application management",
            "micronutrients": "micronutrients zinc boron iron deficiency",
            "precision_agriculture": "precision agriculture technology ROI",
            "drought_management": "drought management water conservation",
            "deficiency_detection": "nutrient deficiency detection symptoms",
            "tillage_practices": "tillage no-till conservation practices",
            "cost_optimization": "cost optimization fertilizer economics",
            "weather_integration": "weather impact timing decisions",
            "testing_integration": "soil testing tissue testing interpretation",
            "sustainable_intensification": "sustainable practices yield optimization",
            "policy_compliance": "government programs regulations compliance"
        }
        
        return search_mapping.get(question_type, "")
    
    def _analyze_context(self, context: RecommendationContext) -> Dict[str, Any]:
        """Analyze the context data to inform recommendations."""
        analysis = {
            "summary": "",
            "confidence_factors": {},
            "warnings": [],
            "data_quality": {}
        }
        
        # Analyze soil data if available
        if context.soil_data:
            soil_analysis = self._analyze_soil_data(context.soil_data)
            analysis["soil_analysis"] = soil_analysis
            analysis["confidence_factors"]["soil_data_quality"] = soil_analysis.get("quality_score", 0.5)
        
        # Analyze location data
        if context.location:
            location_analysis = self._analyze_location_data(context.location)
            analysis["location_analysis"] = location_analysis
            analysis["confidence_factors"]["location_specificity"] = location_analysis.get("specificity_score", 0.5)
        
        # Analyze crop data
        if context.crop_data:
            crop_analysis = self._analyze_crop_data(context.crop_data)
            analysis["crop_analysis"] = crop_analysis
            analysis["confidence_factors"]["crop_data_completeness"] = crop_analysis.get("completeness_score", 0.5)
        
        # Check data completeness for question type
        completeness = self._assess_context_completeness(context)
        analysis["confidence_factors"]["data_completeness"] = completeness
        
        # Generate summary
        analysis["summary"] = self._generate_analysis_summary(analysis)
        
        return analysis
    
    def _analyze_soil_data(self, soil_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze soil data quality and characteristics."""
        analysis = {
            "quality_score": 0.0,
            "issues": [],
            "strengths": []
        }
        
        required_fields = ["ph", "organic_matter_percent", "phosphorus_ppm", "potassium_ppm"]
        available_fields = [field for field in required_fields if field in soil_data and soil_data[field] is not None]
        
        # Calculate quality score based on available data
        analysis["quality_score"] = len(available_fields) / len(required_fields)
        
        # Check for data issues
        if "ph" in soil_data:
            ph = soil_data["ph"]
            if ph < 4.5:
                analysis["issues"].append("Very acidic soil (pH < 4.5) may limit crop options")
            elif ph > 8.5:
                analysis["issues"].append("Very alkaline soil (pH > 8.5) may cause nutrient deficiencies")
            else:
                analysis["strengths"].append("Soil pH is within reasonable range")
        
        if "organic_matter_percent" in soil_data:
            om = soil_data["organic_matter_percent"]
            if om < 2.0:
                analysis["issues"].append("Low organic matter may reduce soil health")
            elif om > 4.0:
                analysis["strengths"].append("Good organic matter levels support soil health")
        
        # Check test date if available
        if "test_date" in soil_data:
            try:
                test_date = datetime.fromisoformat(soil_data["test_date"]).date()
                days_old = (date.today() - test_date).days
                if days_old > 1095:  # 3 years
                    analysis["issues"].append("Soil test data is over 3 years old")
                elif days_old < 365:  # 1 year
                    analysis["strengths"].append("Recent soil test data available")
            except:
                pass
        
        return analysis
    
    def _analyze_location_data(self, location_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze location data for regional specificity."""
        analysis = {
            "specificity_score": 0.0,
            "region": "unknown",
            "climate_zone": "unknown"
        }
        
        if "latitude" in location_data and "longitude" in location_data:
            analysis["specificity_score"] = 1.0
            
            # Determine general region based on coordinates (simplified)
            lat = location_data["latitude"]
            lon = location_data["longitude"]
            
            if 25 <= lat <= 49 and -125 <= lon <= -66:  # Continental US
                if 40 <= lat <= 49 and -104 <= lon <= -80:
                    analysis["region"] = "midwest"
                elif 32 <= lat <= 40 and -104 <= lon <= -75:
                    analysis["region"] = "southeast"
                elif 25 <= lat <= 40 and -125 <= lon <= -104:
                    analysis["region"] = "southwest"
                elif 40 <= lat <= 49 and -125 <= lon <= -104:
                    analysis["region"] = "northwest"
                else:
                    analysis["region"] = "northeast"
            
        elif "address" in location_data or "state" in location_data:
            analysis["specificity_score"] = 0.7
        
        return analysis
    
    def _analyze_crop_data(self, crop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze crop data completeness."""
        analysis = {
            "completeness_score": 0.0,
            "crop_info": None
        }
        
        if "crop_name" in crop_data:
            # Get crop information from knowledge base
            crop_info = self.knowledge_base.get_crop_information(crop_data["crop_name"])
            if crop_info:
                analysis["crop_info"] = crop_info
                analysis["completeness_score"] = 0.8
                
                # Check for additional crop data
                additional_fields = ["variety", "planting_date", "growth_stage", "yield_goal"]
                available_additional = sum(1 for field in additional_fields if field in crop_data)
                analysis["completeness_score"] += (available_additional / len(additional_fields)) * 0.2
        
        return analysis
    
    def _generate_specific_recommendations(self, context: RecommendationContext, 
                                        knowledge_items: List[Dict[str, Any]], 
                                        analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate specific recommendations based on context and knowledge."""
        recommendations = []
        
        # Route to specific recommendation generators based on question type
        if context.question_type == "crop_selection":
            recommendations = self._generate_crop_selection_recommendations(context, knowledge_items, analysis)
        elif context.question_type == "soil_fertility":
            recommendations = self._generate_soil_fertility_recommendations(context, knowledge_items, analysis)
        elif context.question_type == "nutrient_deficiency":
            recommendations = self._generate_nutrient_deficiency_recommendations(context, knowledge_items, analysis)
        elif context.question_type == "fertilizer_type":
            recommendations = self._generate_fertilizer_type_recommendations(context, knowledge_items, analysis)
        else:
            # Generic recommendations based on knowledge items
            recommendations = self._generate_generic_recommendations(context, knowledge_items, analysis)
        
        return recommendations
    
    def _generate_crop_selection_recommendations(self, context: RecommendationContext,
                                              knowledge_items: List[Dict[str, Any]],
                                              analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate crop selection recommendations."""
        recommendations = []
        
        # Get suitable crops based on soil and location
        if context.soil_data and context.location:
            soil_ph = context.soil_data.get("ph", 6.5)
            region = analysis.get("location_analysis", {}).get("region", "unknown")
            
            # Define crop suitability based on pH and region
            crop_suitability = {
                "corn": {
                    "ph_range": (6.0, 6.8),
                    "regions": ["midwest", "southeast"],
                    "description": "Well-suited for fertile soils with good drainage"
                },
                "soybean": {
                    "ph_range": (6.0, 7.0),
                    "regions": ["midwest", "southeast"],
                    "description": "Nitrogen-fixing legume, good rotation crop"
                },
                "wheat": {
                    "ph_range": (6.0, 7.0),
                    "regions": ["midwest", "northwest", "northeast"],
                    "description": "Cool-season grain crop, good for rotation"
                }
            }
            
            for crop_name, suitability in crop_suitability.items():
                ph_min, ph_max = suitability["ph_range"]
                suitable_regions = suitability["regions"]
                
                # Calculate suitability score
                ph_score = 1.0 if ph_min <= soil_ph <= ph_max else max(0.0, 1.0 - abs(soil_ph - (ph_min + ph_max) / 2) * 0.2)
                region_score = 1.0 if region in suitable_regions else 0.6
                overall_score = (ph_score + region_score) / 2
                
                if overall_score > 0.5:
                    # Get crop varieties
                    varieties = self.knowledge_base.get_crop_varieties(crop_name, region)
                    
                    recommendation = {
                        "crop_name": crop_name,
                        "suitability_score": overall_score,
                        "description": suitability["description"],
                        "varieties": varieties[:3],  # Top 3 varieties
                        "reasoning": f"Suitable for your soil pH ({soil_ph}) and region ({region})",
                        "confidence_factors": {
                            "soil_suitability": ph_score,
                            "regional_adaptation": region_score
                        }
                    }
                    recommendations.append(recommendation)
            
            # Sort by suitability score
            recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_soil_fertility_recommendations(self, context: RecommendationContext,
                                               knowledge_items: List[Dict[str, Any]],
                                               analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate soil fertility improvement recommendations."""
        recommendations = []
        
        if context.soil_data:
            # Get soil test interpretation
            interpretation = self.knowledge_base.get_soil_test_interpretation(
                ph=context.soil_data.get("ph", 6.5),
                organic_matter=context.soil_data.get("organic_matter_percent", 3.0),
                phosphorus=context.soil_data.get("phosphorus_ppm", 20),
                potassium=context.soil_data.get("potassium_ppm", 150),
                crop_type=context.crop_data.get("crop_name") if context.crop_data else None
            )
            
            # Convert interpretation to recommendations
            for category in ["ph_interpretation", "organic_matter_interpretation", 
                           "phosphorus_interpretation", "potassium_interpretation"]:
                interp = interpretation.get(category, {})
                if interp.get("recommendations"):
                    for rec_text in interp["recommendations"]:
                        recommendation = {
                            "category": category.replace("_interpretation", ""),
                            "action": rec_text,
                            "priority": "high" if interp.get("status") in ["low", "very_acidic", "very_alkaline"] else "medium",
                            "current_status": interp.get("status", "unknown"),
                            "current_value": interp.get("value"),
                            "reasoning": interp.get("description", "")
                        }
                        recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_nutrient_deficiency_recommendations(self, context: RecommendationContext,
                                                    knowledge_items: List[Dict[str, Any]],
                                                    analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate nutrient deficiency diagnosis recommendations."""
        recommendations = []
        
        if context.soil_data:
            soil_data = context.soil_data
            
            # Check for potential deficiencies
            deficiency_thresholds = {
                "nitrogen": {"threshold": 10, "unit": "ppm", "symptoms": "yellowing of older leaves"},
                "phosphorus": {"threshold": 15, "unit": "ppm", "symptoms": "purple leaf coloration"},
                "potassium": {"threshold": 120, "unit": "ppm", "symptoms": "leaf edge burn"},
                "sulfur": {"threshold": 10, "unit": "ppm", "symptoms": "yellowing of younger leaves"}
            }
            
            for nutrient, info in deficiency_thresholds.items():
                soil_level = soil_data.get(f"{nutrient}_ppm", info["threshold"] + 1)
                
                if soil_level < info["threshold"]:
                    recommendation = {
                        "nutrient": nutrient,
                        "status": "deficient",
                        "current_level": soil_level,
                        "threshold": info["threshold"],
                        "unit": info["unit"],
                        "symptoms": info["symptoms"],
                        "action": f"Apply {nutrient} fertilizer",
                        "priority": "high",
                        "testing_recommendation": f"Consider tissue testing to confirm {nutrient} deficiency"
                    }
                    recommendations.append(recommendation)
        
        return recommendations
    
    def _generate_fertilizer_type_recommendations(self, context: RecommendationContext,
                                                knowledge_items: List[Dict[str, Any]],
                                                analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fertilizer type selection recommendations."""
        recommendations = []
        
        # Get fertilizer products from knowledge base
        fertilizer_products = self.knowledge_base.get_fertilizer_products()
        
        if context.soil_data and fertilizer_products:
            soil_data = context.soil_data
            
            # Determine nutrient needs
            nutrient_needs = {}
            if soil_data.get("phosphorus_ppm", 20) < 15:
                nutrient_needs["phosphorus"] = "high"
            if soil_data.get("potassium_ppm", 150) < 120:
                nutrient_needs["potassium"] = "high"
            if soil_data.get("nitrogen_ppm", 15) < 10:
                nutrient_needs["nitrogen"] = "high"
            
            # Recommend fertilizer types based on needs
            for product in fertilizer_products[:10]:  # Limit to top 10 products
                suitability_score = 0.0
                reasons = []
                
                # Check nutrient content match
                if "phosphorus" in nutrient_needs and product["nutrient_analysis"]["phosphorus_percent"] > 5:
                    suitability_score += 0.3
                    reasons.append("High phosphorus content addresses soil deficiency")
                
                if "potassium" in nutrient_needs and product["nutrient_analysis"]["potassium_percent"] > 5:
                    suitability_score += 0.3
                    reasons.append("High potassium content addresses soil deficiency")
                
                if "nitrogen" in nutrient_needs and product["nutrient_analysis"]["nitrogen_percent"] > 10:
                    suitability_score += 0.4
                    reasons.append("Nitrogen content supports crop growth")
                
                if suitability_score > 0.3:
                    recommendation = {
                        "product_name": product["product_name"],
                        "manufacturer": product["manufacturer"],
                        "product_type": product["product_type"],
                        "suitability_score": suitability_score,
                        "nutrient_analysis": product["nutrient_analysis"],
                        "reasons": reasons,
                        "estimated_cost": product["economic_data"].get("typical_price_per_ton"),
                        "application_methods": product["physical_properties"].get("application_method", [])
                    }
                    recommendations.append(recommendation)
            
            # Sort by suitability score
            recommendations.sort(key=lambda x: x["suitability_score"], reverse=True)
        
        return recommendations[:5]  # Return top 5 recommendations
    
    def _generate_generic_recommendations(self, context: RecommendationContext,
                                        knowledge_items: List[Dict[str, Any]],
                                        analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate generic recommendations from knowledge items."""
        recommendations = []
        
        for item in knowledge_items[:5]:  # Limit to top 5 items
            content = item.get("content", {})
            guidelines = content.get("guidelines", [])
            
            if guidelines:
                recommendation = {
                    "title": content.get("title", "Agricultural Recommendation"),
                    "category": item.get("category", "general"),
                    "guidelines": guidelines,
                    "description": content.get("description", ""),
                    "source": item.get("source", {}).get("name", "Agricultural Knowledge Base"),
                    "expert_validated": item.get("expert_validated", False)
                }
                recommendations.append(recommendation)
        
        return recommendations
    
    def _calculate_confidence_score(self, context: RecommendationContext,
                                  knowledge_items: List[Dict[str, Any]],
                                  analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence score for recommendations."""
        confidence_factors = analysis.get("confidence_factors", {})
        
        # Base confidence from data quality
        data_quality_score = sum(confidence_factors.values()) / max(len(confidence_factors), 1)
        
        # Knowledge base quality score
        expert_validated_count = sum(1 for item in knowledge_items if item.get("expert_validated", False))
        knowledge_quality_score = expert_validated_count / max(len(knowledge_items), 1)
        
        # Context completeness score
        completeness_score = self._assess_context_completeness(context)
        
        # Weighted average
        overall_confidence = (
            data_quality_score * 0.4 +
            knowledge_quality_score * 0.3 +
            completeness_score * 0.3
        )
        
        return min(1.0, max(0.0, overall_confidence))
    
    def _assess_context_completeness(self, context: RecommendationContext) -> float:
        """Assess how complete the context data is for the question type."""
        if not context.question_type:
            return 0.5
        
        question_config = self._question_type_mapping.get(context.question_type, {})
        required_data = question_config.get("required_data", [])
        optional_data = question_config.get("optional_data", [])
        
        # Check required data
        required_score = 0.0
        for data_type in required_data:
            if hasattr(context, data_type) and getattr(context, data_type) is not None:
                required_score += 1.0
        
        required_score = required_score / max(len(required_data), 1)
        
        # Check optional data
        optional_score = 0.0
        for data_type in optional_data:
            if hasattr(context, data_type) and getattr(context, data_type) is not None:
                optional_score += 1.0
        
        optional_score = optional_score / max(len(optional_data), 1)
        
        # Weighted score (required data is more important)
        return required_score * 0.7 + optional_score * 0.3
    
    def _generate_analysis_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a summary of the context analysis."""
        summaries = []
        
        if "soil_analysis" in analysis:
            soil_analysis = analysis["soil_analysis"]
            quality_score = soil_analysis.get("quality_score", 0)
            if quality_score > 0.8:
                summaries.append("Comprehensive soil data available")
            elif quality_score > 0.5:
                summaries.append("Partial soil data available")
            else:
                summaries.append("Limited soil data available")
        
        if "location_analysis" in analysis:
            location_analysis = analysis["location_analysis"]
            region = location_analysis.get("region", "unknown")
            if region != "unknown":
                summaries.append(f"Location identified as {region} region")
        
        if "crop_analysis" in analysis:
            crop_analysis = analysis["crop_analysis"]
            if crop_analysis.get("crop_info"):
                summaries.append("Crop information available in knowledge base")
        
        return ". ".join(summaries) if summaries else "Basic analysis completed"
    
    def _generate_next_steps(self, context: RecommendationContext, 
                           recommendations: List[Dict[str, Any]]) -> List[str]:
        """Generate next steps based on recommendations."""
        next_steps = []
        
        # Generic next steps based on question type
        if context.question_type == "crop_selection":
            next_steps.extend([
                "Review local variety trial results",
                "Consider crop insurance options",
                "Plan planting schedule and equipment needs"
            ])
        elif context.question_type == "soil_fertility":
            next_steps.extend([
                "Schedule soil sampling if tests are outdated",
                "Consult with local extension agent",
                "Develop implementation timeline"
            ])
        elif context.question_type == "nutrient_deficiency":
            next_steps.extend([
                "Consider tissue testing for confirmation",
                "Monitor crop symptoms closely",
                "Plan corrective fertilizer applications"
            ])
        
        # Add recommendation-specific next steps
        for rec in recommendations[:3]:  # Top 3 recommendations
            if rec.get("priority") == "high":
                next_steps.append(f"Prioritize: {rec.get('action', rec.get('title', 'Implement recommendation'))}")
        
        return next_steps[:5]  # Limit to 5 next steps
    
    def _context_to_dict(self, context: RecommendationContext) -> Dict[str, Any]:
        """Convert context object to dictionary for storage."""
        return {
            "user_id": context.user_id,
            "farm_id": context.farm_id,
            "field_id": context.field_id,
            "location": context.location,
            "soil_data": context.soil_data,
            "crop_data": context.crop_data,
            "weather_data": context.weather_data,
            "farm_constraints": context.farm_constraints,
            "question_type": context.question_type
        }
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_user_recommendation_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recommendation history for a user."""
        return self.knowledge_base.get_user_recommendations(user_id, limit=limit)
    
    def search_knowledge(self, search_text: str, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search the knowledge base."""
        knowledge_categories = []
        if categories:
            for cat_str in categories:
                try:
                    knowledge_categories.append(KnowledgeCategory(cat_str))
                except ValueError:
                    continue
        
        return self.knowledge_base.search_knowledge(
            search_text=search_text,
            categories=knowledge_categories if knowledge_categories else None
        )
    
    def close(self):
        """Close knowledge manager connections."""
        if self.knowledge_base:
            self.knowledge_base.close()
        logger.info("Knowledge manager closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def create_recommendation_context(user_id: str, question_type: str, **kwargs) -> RecommendationContext:
    """Create a recommendation context from parameters."""
    return RecommendationContext(
        user_id=user_id,
        question_type=question_type,
        farm_id=kwargs.get("farm_id"),
        field_id=kwargs.get("field_id"),
        location=kwargs.get("location"),
        soil_data=kwargs.get("soil_data"),
        crop_data=kwargs.get("crop_data"),
        weather_data=kwargs.get("weather_data"),
        farm_constraints=kwargs.get("farm_constraints")
    )

def initialize_knowledge_manager() -> KnowledgeManager:
    """Initialize and return a knowledge manager instance."""
    return KnowledgeManager()


if __name__ == "__main__":
    # Test the knowledge manager
    try:
        print("Testing AFAS Knowledge Manager...")
        
        with initialize_knowledge_manager() as km:
            # Test crop selection recommendations
            print("\n1. Testing crop selection recommendations:")
            context = create_recommendation_context(
                user_id="test_user_123",
                question_type="crop_selection",
                location={"latitude": 42.0308, "longitude": -93.6319},
                soil_data={
                    "ph": 6.2,
                    "organic_matter_percent": 3.8,
                    "phosphorus_ppm": 25,
                    "potassium_ppm": 180
                }
            )
            
            recommendations = km.generate_recommendations(context)
            print(f"   Generated {len(recommendations.get('recommendations', []))} recommendations")
            print(f"   Confidence score: {recommendations.get('confidence_score', 0):.2f}")
            
            # Test soil fertility recommendations
            print("\n2. Testing soil fertility recommendations:")
            context = create_recommendation_context(
                user_id="test_user_123",
                question_type="soil_fertility",
                soil_data={
                    "ph": 5.8,
                    "organic_matter_percent": 2.1,
                    "phosphorus_ppm": 12,
                    "potassium_ppm": 95
                }
            )
            
            recommendations = km.generate_recommendations(context)
            print(f"   Generated {len(recommendations.get('recommendations', []))} recommendations")
            print(f"   Confidence score: {recommendations.get('confidence_score', 0):.2f}")
            
            print("\n✅ Knowledge manager test completed successfully!")
            
    except Exception as e:
        print(f"\n❌ Knowledge manager test failed: {e}")