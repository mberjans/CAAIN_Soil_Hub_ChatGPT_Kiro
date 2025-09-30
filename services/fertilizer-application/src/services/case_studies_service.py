"""
Case Studies Service for Fertilizer Application Methods.

This service provides comprehensive case studies with real-world examples,
scenarios, and success stories for fertilizer application methods.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timedelta
from enum import Enum

from src.models.educational_models import (
    CaseStudy, EducationalContent, ContentType, ContentCategory,
    DifficultyLevel, LearningObjective, ExpertInsight
)
from src.models.application_models import ApplicationMethodType, EquipmentType, FertilizerForm

logger = logging.getLogger(__name__)


class CaseStudyCategory(str, Enum):
    """Categories of case studies."""
    SUCCESS_STORY = "success_story"
    PROBLEM_SOLVING = "problem_solving"
    INNOVATION = "innovation"
    COST_OPTIMIZATION = "cost_optimization"
    ENVIRONMENTAL_STEWARDSHIP = "environmental_stewardship"
    TECHNOLOGY_ADOPTION = "technology_adoption"
    REGIONAL_ADAPTATION = "regional_adaptation"


class CaseStudiesService:
    """Service for comprehensive case studies and real-world examples."""
    
    def __init__(self):
        self.case_studies_database = {}
        self.success_stories = {}
        self.problem_solving_cases = {}
        self.innovation_cases = {}
        self.cost_optimization_cases = {}
        self.environmental_cases = {}
        self.technology_adoption_cases = {}
        self._initialize_case_studies()
        self._initialize_success_stories()
        self._initialize_problem_solving_cases()
        self._initialize_innovation_cases()
        self._initialize_cost_optimization_cases()
        self._initialize_environmental_cases()
        self._initialize_technology_adoption_cases()
    
    def _initialize_case_studies(self):
        """Initialize comprehensive case studies database."""
        self.case_studies_database = {
            ApplicationMethodType.BROADCAST: {
                CaseStudyCategory.SUCCESS_STORY: [
                    CaseStudy(
                        case_id="broadcast_success_1",
                        title="Precision Broadcast Application Success Story",
                        farm_name="Green Valley Farms",
                        location="Central Iowa",
                        farm_size_acres=1200,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.BROADCAST,
                        scenario_description="Large-scale corn operation implementing precision broadcast application with GPS guidance",
                        challenge="Achieving uniform application across 1200 acres with varying field conditions",
                        solution_implemented="GPS-guided broadcast application with variable rate technology",
                        results_achieved={
                            "yield_increase": "8%",
                            "fertilizer_efficiency": "15% improvement",
                            "cost_savings": "$12,000 annually",
                            "environmental_impact": "Reduced runoff by 20%"
                        },
                        lessons_learned=[
                            "GPS guidance significantly improves application accuracy",
                            "Variable rate technology optimizes fertilizer use",
                            "Proper calibration is essential for success",
                            "Regular equipment maintenance prevents issues"
                        ],
                        key_factors=["GPS guidance", "variable rate", "calibration", "maintenance"],
                        success_metrics={
                            "accuracy_improvement": "25%",
                            "time_savings": "3 hours per application",
                            "fuel_efficiency": "12% improvement"
                        },
                        implementation_timeline={
                            "planning": "2 weeks",
                            "equipment_setup": "1 week",
                            "training": "1 week",
                            "full_implementation": "1 season"
                        },
                        cost_benefit_analysis={
                            "initial_investment": "$45,000",
                            "annual_savings": "$12,000",
                            "payback_period": "3.75 years",
                            "roi": "267% over 5 years"
                        }
                    ),
                    CaseStudy(
                        case_id="broadcast_success_2",
                        title="Small Farm Broadcast Optimization",
                        farm_name="Prairie View Farm",
                        location="Eastern Nebraska",
                        farm_size_acres=180,
                        crop_type="Soybeans",
                        application_method=ApplicationMethodType.BROADCAST,
                        scenario_description="Small farm optimizing broadcast application for soybeans",
                        challenge="Maximizing efficiency on small acreage with limited equipment",
                        solution_implemented="Optimized calibration and timing for small farm operations",
                        results_achieved={
                            "yield_increase": "5%",
                            "fertilizer_efficiency": "12% improvement",
                            "cost_savings": "$2,400 annually",
                            "time_savings": "2 hours per application"
                        },
                        lessons_learned=[
                            "Small farms can achieve significant efficiency gains",
                            "Proper calibration is critical regardless of farm size",
                            "Timing optimization provides substantial benefits",
                            "Equipment maintenance is essential for small operations"
                        ],
                        key_factors=["calibration", "timing", "maintenance", "optimization"],
                        success_metrics={
                            "application_accuracy": "95%",
                            "coverage_uniformity": "92%",
                            "cost_per_acre": "Reduced by 15%"
                        }
                    )
                ],
                
                CaseStudyCategory.PROBLEM_SOLVING: [
                    CaseStudy(
                        case_id="broadcast_problem_1",
                        title="Broadcast Application Drift Problem Resolution",
                        farm_name="River Valley Farm",
                        location="Western Iowa",
                        farm_size_acres=800,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.BROADCAST,
                        scenario_description="Farm experiencing fertilizer drift issues affecting neighboring properties",
                        challenge="Controlling fertilizer drift while maintaining application efficiency",
                        solution_implemented="Wind monitoring system and application timing optimization",
                        results_achieved={
                            "drift_reduction": "85%",
                            "neighbor_complaints": "Eliminated",
                            "application_efficiency": "Maintained at 90%",
                            "environmental_compliance": "100%"
                        },
                        lessons_learned=[
                            "Wind monitoring is essential for drift control",
                            "Application timing significantly affects drift",
                            "Equipment adjustments can reduce drift",
                            "Communication with neighbors is important"
                        ],
                        key_factors=["wind_monitoring", "timing", "equipment_adjustment", "communication"],
                        problem_resolution_steps=[
                            "Installed wind monitoring equipment",
                            "Developed application timing protocols",
                            "Adjusted equipment settings",
                            "Implemented buffer zones",
                            "Established communication with neighbors"
                        ]
                    )
                ],
                
                CaseStudyCategory.COST_OPTIMIZATION: [
                    CaseStudy(
                        case_id="broadcast_cost_1",
                        title="Broadcast Application Cost Optimization",
                        farm_name="Efficiency Farms",
                        location="Central Illinois",
                        farm_size_acres=2000,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.BROADCAST,
                        scenario_description="Large farm optimizing broadcast application costs",
                        challenge="Reducing fertilizer application costs while maintaining yields",
                        solution_implemented="Comprehensive cost optimization program",
                        results_achieved={
                            "cost_reduction": "18%",
                            "yield_maintenance": "100%",
                            "efficiency_improvement": "22%",
                            "annual_savings": "$28,000"
                        },
                        lessons_learned=[
                            "Bulk purchasing reduces fertilizer costs",
                            "Equipment efficiency improvements pay dividends",
                            "Timing optimization reduces waste",
                            "Regular maintenance prevents costly breakdowns"
                        ],
                        key_factors=["bulk_purchasing", "equipment_efficiency", "timing", "maintenance"],
                        cost_optimization_strategies=[
                            "Bulk fertilizer purchasing contracts",
                            "Equipment efficiency upgrades",
                            "Application timing optimization",
                            "Preventive maintenance program",
                            "Labor efficiency improvements"
                        ]
                    )
                ]
            },
            
            ApplicationMethodType.FOLIAR: {
                CaseStudyCategory.SUCCESS_STORY: [
                    CaseStudy(
                        case_id="foliar_success_1",
                        title="Foliar Application for Micronutrient Correction",
                        farm_name="Prairie View Farm",
                        location="Eastern Nebraska",
                        farm_size_acres=800,
                        crop_type="Soybeans",
                        application_method=ApplicationMethodType.FOLIAR,
                        scenario_description="Soybean field showing micronutrient deficiency symptoms",
                        challenge="Correcting zinc deficiency in soybeans without soil application",
                        solution_implemented="Foliar zinc application at R1 growth stage",
                        results_achieved={
                            "deficiency_correction": "Complete visual recovery",
                            "yield_response": "12% increase",
                            "application_cost": "$8 per acre",
                            "roi": "300% return on investment"
                        },
                        lessons_learned=[
                            "Early detection is critical for foliar correction",
                            "Proper timing maximizes nutrient uptake",
                            "Surfactant inclusion improves coverage",
                            "Multiple applications may be needed"
                        ],
                        key_factors=["early_detection", "timing", "formulation", "coverage"],
                        success_metrics={
                            "nutrient_uptake": "85% improvement",
                            "plant_recovery": "Complete within 7 days",
                            "yield_response": "12% increase"
                        }
                    ),
                    CaseStudy(
                        case_id="foliar_success_2",
                        title="Foliar Application for Stress Management",
                        farm_name="Drought Valley Farm",
                        location="Western Kansas",
                        farm_size_acres=1200,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.FOLIAR,
                        scenario_description="Corn field under drought stress requiring nutrient support",
                        challenge="Supporting corn nutrition during drought stress",
                        solution_implemented="Foliar nutrient application with stress management",
                        results_achieved={
                            "stress_reduction": "Significant improvement",
                            "yield_protection": "Maintained 85% of potential yield",
                            "nutrient_efficiency": "Improved uptake by 40%",
                            "cost_effectiveness": "Excellent ROI"
                        },
                        lessons_learned=[
                            "Foliar application can support stressed plants",
                            "Timing is critical during stress periods",
                            "Formulation selection affects success",
                            "Multiple applications may be beneficial"
                        ],
                        key_factors=["stress_timing", "formulation", "application_timing", "plant_support"]
                    )
                ],
                
                CaseStudyCategory.PROBLEM_SOLVING: [
                    CaseStudy(
                        case_id="foliar_problem_1",
                        title="Foliar Application Phytotoxicity Resolution",
                        farm_name="Sunrise Farm",
                        location="Central Iowa",
                        farm_size_acres=600,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.FOLIAR,
                        scenario_description="Corn field showing phytotoxicity symptoms after foliar application",
                        challenge="Resolving phytotoxicity while maintaining nutrient benefits",
                        solution_implemented="Formulation adjustment and application timing optimization",
                        results_achieved={
                            "phytotoxicity_resolution": "Complete recovery",
                            "nutrient_benefits": "Maintained",
                            "future_prevention": "Protocol established",
                            "yield_protection": "Minimal impact"
                        },
                        lessons_learned=[
                            "Concentration is critical for foliar applications",
                            "Environmental conditions affect phytotoxicity risk",
                            "Plant stress increases sensitivity",
                            "Proper formulation prevents problems"
                        ],
                        key_factors=["concentration", "environmental_conditions", "plant_stress", "formulation"],
                        problem_resolution_steps=[
                            "Identified phytotoxicity cause",
                            "Adjusted formulation concentration",
                            "Optimized application timing",
                            "Established prevention protocols",
                            "Monitored plant recovery"
                        ]
                    )
                ]
            },
            
            ApplicationMethodType.BAND: {
                CaseStudyCategory.SUCCESS_STORY: [
                    CaseStudy(
                        case_id="band_success_1",
                        title="Band Application for Precision Nutrition",
                        farm_name="Precision Farms",
                        location="Central Illinois",
                        farm_size_acres=1500,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.BAND,
                        scenario_description="Large farm implementing precision band application",
                        challenge="Optimizing nutrient placement for maximum efficiency",
                        solution_implemented="Precision band application with GPS guidance",
                        results_achieved={
                            "nutrient_efficiency": "25% improvement",
                            "yield_increase": "6%",
                            "cost_savings": "$18,000 annually",
                            "environmental_impact": "Reduced nutrient losses by 30%"
                        },
                        lessons_learned=[
                            "Precise placement improves nutrient efficiency",
                            "GPS guidance enhances accuracy",
                            "Proper depth is critical for success",
                            "Timing affects nutrient availability"
                        ],
                        key_factors=["placement_precision", "gps_guidance", "depth", "timing"],
                        success_metrics={
                            "placement_accuracy": "98%",
                            "nutrient_efficiency": "25% improvement",
                            "yield_response": "6% increase"
                        }
                    )
                ],
                
                CaseStudyCategory.INNOVATION: [
                    CaseStudy(
                        case_id="band_innovation_1",
                        title="Innovative Band Application Technology",
                        farm_name="Innovation Farm",
                        location="Eastern Iowa",
                        farm_size_acres=900,
                        crop_type="Soybeans",
                        application_method=ApplicationMethodType.BAND,
                        scenario_description="Farm testing innovative band application technology",
                        challenge="Improving band application efficiency and accuracy",
                        solution_implemented="New banding technology with real-time adjustment",
                        results_achieved={
                            "accuracy_improvement": "35%",
                            "efficiency_gain": "20%",
                            "cost_reduction": "15%",
                            "technology_adoption": "Successful"
                        },
                        lessons_learned=[
                            "New technology can provide significant benefits",
                            "Proper training is essential for adoption",
                            "Gradual implementation reduces risk",
                            "Performance monitoring validates benefits"
                        ],
                        key_factors=["new_technology", "training", "gradual_implementation", "monitoring"],
                        innovation_details={
                            "technology_type": "Real-time adjustment system",
                            "implementation_approach": "Gradual rollout",
                            "training_required": "2 weeks",
                            "performance_monitoring": "Continuous"
                        }
                    )
                ]
            },
            
            ApplicationMethodType.INJECTION: {
                CaseStudyCategory.SUCCESS_STORY: [
                    CaseStudy(
                        case_id="injection_success_1",
                        title="Injection Application for Maximum Efficiency",
                        farm_name="Efficiency Valley Farm",
                        location="Central Nebraska",
                        farm_size_acres=1800,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.INJECTION,
                        scenario_description="Large farm implementing injection application for maximum efficiency",
                        challenge="Maximizing fertilizer efficiency while minimizing environmental impact",
                        solution_implemented="Precision injection application system",
                        results_achieved={
                            "nutrient_efficiency": "30% improvement",
                            "yield_increase": "8%",
                            "environmental_impact": "Reduced losses by 40%",
                            "cost_savings": "$24,000 annually"
                        },
                        lessons_learned=[
                            "Injection provides maximum nutrient efficiency",
                            "Proper depth is critical for success",
                            "Soil conditions affect injection quality",
                            "Equipment maintenance is essential"
                        ],
                        key_factors=["nutrient_efficiency", "depth", "soil_conditions", "maintenance"],
                        success_metrics={
                            "injection_accuracy": "96%",
                            "nutrient_efficiency": "30% improvement",
                            "environmental_compliance": "100%"
                        }
                    )
                ],
                
                CaseStudyCategory.TECHNOLOGY_ADOPTION: [
                    CaseStudy(
                        case_id="injection_tech_1",
                        title="Advanced Injection Technology Adoption",
                        farm_name="Tech Forward Farm",
                        location="Western Illinois",
                        farm_size_acres=2200,
                        crop_type="Corn",
                        application_method=ApplicationMethodType.INJECTION,
                        scenario_description="Farm adopting advanced injection technology",
                        challenge="Implementing new injection technology while maintaining operations",
                        solution_implemented="Gradual adoption of advanced injection system",
                        results_achieved={
                            "technology_adoption": "Successful",
                            "performance_improvement": "25%",
                            "efficiency_gain": "18%",
                            "roi": "Positive within 2 years"
                        },
                        lessons_learned=[
                            "Gradual adoption reduces implementation risk",
                            "Proper training is essential for success",
                            "Performance monitoring validates benefits",
                            "Technology integration requires planning"
                        ],
                        key_factors=["gradual_adoption", "training", "monitoring", "planning"],
                        technology_adoption_steps=[
                            "Technology evaluation and selection",
                            "Pilot program implementation",
                            "Staff training and development",
                            "Gradual rollout across farm",
                            "Performance monitoring and optimization"
                        ]
                    )
                ]
            }
        }
    
    def _initialize_success_stories(self):
        """Initialize success stories database."""
        self.success_stories = {
            "precision_agriculture_adoption": {
                "story_id": "precision_ag_1",
                "title": "Precision Agriculture Transformation",
                "farm_name": "Future Farms",
                "location": "Central Iowa",
                "farm_size_acres": 3000,
                "transformation_timeline": "3 years",
                "key_technologies": ["GPS guidance", "Variable rate", "Yield mapping", "Soil testing"],
                "results": {
                    "yield_increase": "12%",
                    "cost_reduction": "15%",
                    "environmental_improvement": "25%",
                    "profitability_increase": "18%"
                },
                "lessons_learned": [
                    "Start with one technology and expand gradually",
                    "Invest in training and education",
                    "Monitor and measure results",
                    "Share experiences with other farmers"
                ]
            },
            "environmental_stewardship": {
                "story_id": "env_stewardship_1",
                "title": "Environmental Stewardship Success",
                "farm_name": "Green Acres Farm",
                "location": "Eastern Nebraska",
                "farm_size_acres": 1200,
                "environmental_practices": ["Buffer strips", "Cover crops", "Precision application", "Nutrient management"],
                "results": {
                    "nutrient_loss_reduction": "40%",
                    "soil_health_improvement": "Significant",
                    "wildlife_habitat": "Enhanced",
                    "community_recognition": "Award received"
                },
                "lessons_learned": [
                    "Environmental practices can be profitable",
                    "Community support is important",
                    "Long-term thinking pays off",
                    "Document and share results"
                ]
            }
        }
    
    def _initialize_problem_solving_cases(self):
        """Initialize problem-solving case studies."""
        self.problem_solving_cases = {
            "equipment_failure": {
                "case_id": "equipment_failure_1",
                "title": "Equipment Failure During Critical Application",
                "problem": "Spreader breakdown during peak application period",
                "impact": "Delayed application affecting crop yield potential",
                "solution": "Emergency equipment rental and backup planning",
                "outcome": "Minimal yield impact due to quick response",
                "prevention": "Improved maintenance schedule and backup equipment"
            },
            "weather_challenges": {
                "case_id": "weather_challenges_1",
                "title": "Weather Challenges During Application",
                "problem": "Unexpected weather changes during application",
                "impact": "Application quality and timing affected",
                "solution": "Flexible application scheduling and weather monitoring",
                "outcome": "Successful completion with minimal impact",
                "prevention": "Enhanced weather monitoring and flexible scheduling"
            }
        }
    
    def _initialize_innovation_cases(self):
        """Initialize innovation case studies."""
        self.innovation_cases = {
            "drone_application": {
                "case_id": "drone_innovation_1",
                "title": "Drone-Based Fertilizer Application",
                "innovation": "Using drones for precision fertilizer application",
                "benefits": ["Precision application", "Reduced labor", "Access to difficult areas"],
                "challenges": ["Regulatory approval", "Technology limitations", "Cost"],
                "outcome": "Successful pilot program with expansion plans",
                "lessons_learned": [
                    "Innovation requires patience and persistence",
                    "Regulatory compliance is essential",
                    "Technology limitations must be understood",
                    "Cost-benefit analysis is critical"
                ]
            }
        }
    
    def _initialize_cost_optimization_cases(self):
        """Initialize cost optimization case studies."""
        self.cost_optimization_cases = {
            "bulk_purchasing": {
                "case_id": "bulk_purchasing_1",
                "title": "Bulk Fertilizer Purchasing Optimization",
                "strategy": "Coordinated bulk purchasing with neighboring farms",
                "savings": "15% reduction in fertilizer costs",
                "implementation": "Formed purchasing cooperative",
                "outcome": "Significant cost savings for all participants",
                "lessons_learned": [
                    "Cooperation can provide significant benefits",
                    "Planning and coordination are essential",
                    "Volume discounts are substantial",
                    "Long-term relationships are valuable"
                ]
            }
        }
    
    def _initialize_environmental_cases(self):
        """Initialize environmental stewardship case studies."""
        self.environmental_cases = {
            "nutrient_management": {
                "case_id": "nutrient_mgmt_1",
                "title": "Comprehensive Nutrient Management Program",
                "practice": "Integrated nutrient management system",
                "environmental_benefits": ["Reduced nutrient losses", "Improved water quality", "Enhanced soil health"],
                "economic_benefits": ["Cost savings", "Improved yields", "Premium prices"],
                "implementation": "Multi-year program with monitoring",
                "outcome": "Successful environmental and economic results"
            }
        }
    
    def _initialize_technology_adoption_cases(self):
        """Initialize technology adoption case studies."""
        self.technology_adoption_cases = {
            "gps_adoption": {
                "case_id": "gps_adoption_1",
                "title": "GPS Guidance System Adoption",
                "technology": "GPS guidance system for fertilizer application",
                "adoption_process": "Gradual implementation over 2 years",
                "benefits": ["Improved accuracy", "Reduced overlap", "Time savings"],
                "challenges": ["Initial cost", "Learning curve", "Technology maintenance"],
                "outcome": "Successful adoption with significant benefits",
                "lessons_learned": [
                    "Gradual adoption reduces risk",
                    "Training is essential for success",
                    "Benefits justify investment",
                    "Maintenance is important"
                ]
            }
        }
    
    async def get_case_studies_by_method(
        self,
        application_method: ApplicationMethodType,
        category: Optional[CaseStudyCategory] = None,
        difficulty_level: Optional[DifficultyLevel] = None
    ) -> List[CaseStudy]:
        """Get case studies for specific application method."""
        try:
            method_cases = self.case_studies_database.get(application_method, {})
            
            if category:
                cases = method_cases.get(category, [])
            else:
                # Return all cases for the method
                cases = []
                for category_cases in method_cases.values():
                    cases.extend(category_cases)
            
            # Filter by difficulty level if specified
            if difficulty_level:
                cases = [case for case in cases if hasattr(case, 'difficulty_level') and case.difficulty_level == difficulty_level]
            
            return cases
            
        except Exception as e:
            logger.error(f"Error getting case studies: {e}")
            return []
    
    async def get_case_study_by_id(self, case_id: str) -> Optional[CaseStudy]:
        """Get specific case study by ID."""
        try:
            # Search through all case studies
            for method_cases in self.case_studies_database.values():
                for category_cases in method_cases.values():
                    for case in category_cases:
                        if case.case_id == case_id:
                            return case
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting case study {case_id}: {e}")
            return None
    
    async def get_success_stories(
        self,
        farm_size_range: Optional[Tuple[int, int]] = None,
        region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get success stories filtered by criteria."""
        try:
            stories = list(self.success_stories.values())
            
            # Filter by farm size range
            if farm_size_range:
                stories = [
                    story for story in stories
                    if farm_size_range[0] <= story["farm_size_acres"] <= farm_size_range[1]
                ]
            
            # Filter by region
            if region:
                stories = [
                    story for story in stories
                    if region.lower() in story["location"].lower()
                ]
            
            return stories
            
        except Exception as e:
            logger.error(f"Error getting success stories: {e}")
            return []
    
    async def get_problem_solving_cases(
        self,
        problem_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get problem-solving case studies."""
        try:
            cases = list(self.problem_solving_cases.values())
            
            if problem_type:
                cases = [
                    case for case in cases
                    if problem_type.lower() in case["title"].lower()
                ]
            
            return cases
            
        except Exception as e:
            logger.error(f"Error getting problem-solving cases: {e}")
            return []
    
    async def get_innovation_cases(
        self,
        innovation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get innovation case studies."""
        try:
            cases = list(self.innovation_cases.values())
            
            if innovation_type:
                cases = [
                    case for case in cases
                    if innovation_type.lower() in case["title"].lower()
                ]
            
            return cases
            
        except Exception as e:
            logger.error(f"Error getting innovation cases: {e}")
            return []
    
    async def get_cost_optimization_cases(
        self,
        optimization_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get cost optimization case studies."""
        try:
            cases = list(self.cost_optimization_cases.values())
            
            if optimization_type:
                cases = [
                    case for case in cases
                    if optimization_type.lower() in case["title"].lower()
                ]
            
            return cases
            
        except Exception as e:
            logger.error(f"Error getting cost optimization cases: {e}")
            return []
    
    async def get_environmental_cases(
        self,
        environmental_practice: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get environmental stewardship case studies."""
        try:
            cases = list(self.environmental_cases.values())
            
            if environmental_practice:
                cases = [
                    case for case in cases
                    if environmental_practice.lower() in case["title"].lower()
                ]
            
            return cases
            
        except Exception as e:
            logger.error(f"Error getting environmental cases: {e}")
            return []
    
    async def get_technology_adoption_cases(
        self,
        technology_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get technology adoption case studies."""
        try:
            cases = list(self.technology_adoption_cases.values())
            
            if technology_type:
                cases = [
                    case for case in cases
                    if technology_type.lower() in case["title"].lower()
                ]
            
            return cases
            
        except Exception as e:
            logger.error(f"Error getting technology adoption cases: {e}")
            return []
    
    async def generate_personalized_case_studies(
        self,
        user_profile: Dict[str, Any],
        farm_characteristics: Dict[str, Any],
        application_method: ApplicationMethodType
    ) -> List[CaseStudy]:
        """Generate personalized case studies based on user profile."""
        try:
            personalized_cases = []
            
            # Get farm size and region
            farm_size = farm_characteristics.get("farm_size_acres", 0)
            region = farm_characteristics.get("region", "")
            primary_crops = user_profile.get("primary_crops", [])
            experience_level = user_profile.get("experience_level", DifficultyLevel.BEGINNER)
            
            # Get relevant case studies
            all_cases = await self.get_case_studies_by_method(application_method)
            
            for case in all_cases:
                relevance_score = 0
                
                # Score based on farm size similarity
                size_diff = abs(case.farm_size_acres - farm_size)
                if size_diff < 200:
                    relevance_score += 0.3
                elif size_diff < 500:
                    relevance_score += 0.2
                elif size_diff < 1000:
                    relevance_score += 0.1
                
                # Score based on region similarity
                if region.lower() in case.location.lower():
                    relevance_score += 0.2
                
                # Score based on crop similarity
                if case.crop_type.lower() in [crop.lower() for crop in primary_crops]:
                    relevance_score += 0.2
                
                # Score based on experience level
                if hasattr(case, 'difficulty_level'):
                    if case.difficulty_level == experience_level:
                        relevance_score += 0.2
                    elif abs(case.difficulty_level.value - experience_level.value) == 1:
                        relevance_score += 0.1
                
                # Add case if relevance score is high enough
                if relevance_score >= 0.3:
                    personalized_cases.append(case)
            
            # Sort by relevance score
            personalized_cases.sort(key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)
            
            return personalized_cases[:5]  # Return top 5 most relevant cases
            
        except Exception as e:
            logger.error(f"Error generating personalized case studies: {e}")
            return []
    
    async def analyze_case_study_outcomes(
        self,
        case_id: str,
        implementation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze outcomes of implementing a case study solution."""
        try:
            case = await self.get_case_study_by_id(case_id)
            if not case:
                raise ValueError(f"Case study {case_id} not found")
            
            analysis = {
                "case_id": case_id,
                "implementation_status": "in_progress",
                "outcome_analysis": {},
                "success_factors": [],
                "challenges_encountered": [],
                "recommendations": [],
                "lessons_learned": []
            }
            
            # Analyze implementation data
            implementation_steps = implementation_data.get("completed_steps", [])
            total_steps = len(case.lessons_learned)
            completion_rate = len(implementation_steps) / total_steps if total_steps > 0 else 0
            
            analysis["implementation_status"] = "completed" if completion_rate >= 0.8 else "in_progress"
            
            # Analyze outcomes
            if "results_achieved" in implementation_data:
                results = implementation_data["results_achieved"]
                analysis["outcome_analysis"] = {
                    "yield_impact": results.get("yield_increase", "Not measured"),
                    "cost_impact": results.get("cost_savings", "Not measured"),
                    "efficiency_impact": results.get("fertilizer_efficiency", "Not measured"),
                    "environmental_impact": results.get("environmental_impact", "Not measured")
                }
            
            # Identify success factors
            if completion_rate >= 0.8:
                analysis["success_factors"] = [
                    "Proper planning and preparation",
                    "Adequate training and support",
                    "Regular monitoring and adjustment",
                    "Stakeholder engagement"
                ]
            
            # Identify challenges
            challenges = implementation_data.get("challenges", [])
            analysis["challenges_encountered"] = challenges
            
            # Generate recommendations
            if completion_rate < 0.5:
                analysis["recommendations"] = [
                    "Focus on completing basic implementation steps",
                    "Seek additional training and support",
                    "Address identified challenges",
                    "Consider phased implementation approach"
                ]
            elif completion_rate < 0.8:
                analysis["recommendations"] = [
                    "Complete remaining implementation steps",
                    "Address any outstanding challenges",
                    "Monitor and measure results",
                    "Plan for optimization and improvement"
                ]
            else:
                analysis["recommendations"] = [
                    "Continue monitoring and optimization",
                    "Share experiences with other farmers",
                    "Consider expanding successful practices",
                    "Document lessons learned for future reference"
                ]
            
            # Extract lessons learned
            analysis["lessons_learned"] = case.lessons_learned
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing case study outcomes: {e}")
            raise