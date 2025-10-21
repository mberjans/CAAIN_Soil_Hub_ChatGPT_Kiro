"""
Expert Insights Service for Fertilizer Application Methods.

This service provides integration with agricultural experts, extension services,
and research institutions to deliver authoritative insights and recommendations
for fertilizer application methods.
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timedelta
from enum import Enum

from src.models.educational_models import (
    ExpertInsight, EducationalContent, ContentType, ContentCategory,
    DifficultyLevel, LearningObjective
)
from src.models.application_models import ApplicationMethodType, EquipmentType, FertilizerForm

logger = logging.getLogger(__name__)


class ExpertType(str, Enum):
    """Types of agricultural experts."""
    EXTENSION_SPECIALIST = "extension_specialist"
    RESEARCH_SCIENTIST = "research_scientist"
    CONSULTANT = "consultant"
    INDUSTRY_EXPERT = "industry_expert"
    FARMER_EXPERT = "farmer_expert"
    REGULATORY_EXPERT = "regulatory_expert"


class InsightCategory(str, Enum):
    """Categories of expert insights."""
    TECHNICAL_GUIDANCE = "technical_guidance"
    RESEARCH_FINDINGS = "research_findings"
    BEST_PRACTICES = "best_practices"
    REGULATORY_UPDATES = "regulatory_updates"
    MARKET_TRENDS = "market_trends"
    TECHNOLOGY_ADVANCES = "technology_advances"
    ENVIRONMENTAL_STEWARDSHIP = "environmental_stewardship"


class ExpertInsightsService:
    """Service for expert insights and agricultural expertise integration."""
    
    def __init__(self):
        self.expert_database = {}
        self.insights_database = {}
        self.research_findings = {}
        self.regulatory_updates = {}
        self.market_trends = {}
        self.technology_updates = {}
        self._initialize_expert_database()
        self._initialize_insights_database()
        self._initialize_research_findings()
        self._initialize_regulatory_updates()
        self._initialize_market_trends()
        self._initialize_technology_updates()
    
    def _initialize_expert_database(self):
        """Initialize expert database with agricultural professionals."""
        self.expert_database = {
            "extension_specialists": [
                {
                    "expert_id": "ext_001",
                    "name": "Dr. Sarah Johnson",
                    "title": "Extension Specialist",
                    "institution": "University of Nebraska-Lincoln",
                    "expertise": ["Soil fertility", "Nutrient management", "Precision agriculture"],
                    "credentials": "Ph.D. Soil Science, 15 years experience",
                    "specialization": ["Corn", "Soybeans", "Wheat"],
                    "region": "Great Plains",
                    "contact_info": {
                        "email": "sjohnson@unl.edu",
                        "phone": "(402) 555-0123",
                        "office": "Nebraska Extension"
                    },
                    "availability": "Available for consultations",
                    "languages": ["English"],
                    "publications": 45,
                    "years_experience": 15
                },
                {
                    "expert_id": "ext_002",
                    "name": "Dr. Michael Chen",
                    "title": "Extension Specialist",
                    "institution": "Iowa State University",
                    "expertise": ["Plant physiology", "Foliar nutrition", "Crop stress management"],
                    "credentials": "Ph.D. Plant Physiology, 12 years experience",
                    "specialization": ["Corn", "Soybeans"],
                    "region": "Midwest",
                    "contact_info": {
                        "email": "mchen@iastate.edu",
                        "phone": "(515) 555-0456",
                        "office": "Iowa State Extension"
                    },
                    "availability": "Available for consultations",
                    "languages": ["English", "Mandarin"],
                    "publications": 38,
                    "years_experience": 12
                },
                {
                    "expert_id": "ext_003",
                    "name": "Dr. Robert Martinez",
                    "title": "Extension Specialist",
                    "institution": "University of Illinois",
                    "expertise": ["Soil fertility", "Band application", "Nutrient placement"],
                    "credentials": "Ph.D. Agronomy, 18 years experience",
                    "specialization": ["Corn", "Soybeans", "Wheat"],
                    "region": "Midwest",
                    "contact_info": {
                        "email": "rmartinez@illinois.edu",
                        "phone": "(217) 555-0789",
                        "office": "Illinois Extension"
                    },
                    "availability": "Available for consultations",
                    "languages": ["English", "Spanish"],
                    "publications": 52,
                    "years_experience": 18
                }
            ],
            
            "research_scientists": [
                {
                    "expert_id": "res_001",
                    "name": "Dr. Jennifer Williams",
                    "title": "Research Scientist",
                    "institution": "USDA-ARS",
                    "expertise": ["Nutrient cycling", "Environmental impact", "Sustainable agriculture"],
                    "credentials": "Ph.D. Environmental Science, 20 years experience",
                    "specialization": ["All crops"],
                    "region": "National",
                    "contact_info": {
                        "email": "jennifer.williams@usda.gov",
                        "phone": "(301) 555-0321",
                        "office": "USDA-ARS Beltsville"
                    },
                    "availability": "Available for research collaborations",
                    "languages": ["English"],
                    "publications": 67,
                    "years_experience": 20
                },
                {
                    "expert_id": "res_002",
                    "name": "Dr. David Thompson",
                    "title": "Research Scientist",
                    "institution": "University of Wisconsin-Madison",
                    "expertise": ["Precision agriculture", "Variable rate application", "Technology integration"],
                    "credentials": "Ph.D. Agricultural Engineering, 14 years experience",
                    "specialization": ["Corn", "Soybeans", "Forages"],
                    "region": "Upper Midwest",
                    "contact_info": {
                        "email": "dthompson@wisc.edu",
                        "phone": "(608) 555-0654",
                        "office": "UW-Madison"
                    },
                    "availability": "Available for research collaborations",
                    "languages": ["English"],
                    "publications": 41,
                    "years_experience": 14
                }
            ],
            
            "industry_experts": [
                {
                    "expert_id": "ind_001",
                    "name": "Mark Anderson",
                    "title": "Technical Manager",
                    "institution": "AgriTech Solutions",
                    "expertise": ["Equipment technology", "Application systems", "Product development"],
                    "credentials": "M.S. Agricultural Engineering, 16 years experience",
                    "specialization": ["All crops"],
                    "region": "National",
                    "contact_info": {
                        "email": "manderson@agritech.com",
                        "phone": "(800) 555-0987",
                        "office": "AgriTech Solutions"
                    },
                    "availability": "Available for technical support",
                    "languages": ["English"],
                    "publications": 23,
                    "years_experience": 16
                }
            ],
            
            "farmer_experts": [
                {
                    "expert_id": "farm_001",
                    "name": "John Peterson",
                    "title": "Farm Manager",
                    "institution": "Peterson Farms",
                    "expertise": ["Practical application", "Equipment operation", "Farm management"],
                    "credentials": "B.S. Agronomy, 25 years farming experience",
                    "specialization": ["Corn", "Soybeans", "Wheat"],
                    "region": "Central Iowa",
                    "contact_info": {
                        "email": "john@petersonfarms.com",
                        "phone": "(515) 555-0123",
                        "office": "Peterson Farms"
                    },
                    "availability": "Available for peer consultation",
                    "languages": ["English"],
                    "publications": 8,
                    "years_experience": 25
                }
            ]
        }
    
    def _initialize_insights_database(self):
        """Initialize expert insights database."""
        self.insights_database = {
            ApplicationMethodType.BROADCAST: [
                ExpertInsight(
                    insight_id="broadcast_insight_1",
                    title="Wind Management in Broadcast Application",
                    expert_name="Dr. Sarah Johnson",
                    expert_credentials="Extension Specialist, University of Nebraska",
                    content="Wind is the most critical factor in broadcast application. Always check wind speed and direction before application. Ideal conditions are wind speeds below 10 mph with consistent direction. Consider using GPS guidance systems to maintain accuracy even in challenging conditions.",
                    application_methods=[ApplicationMethodType.BROADCAST],
                    tags=["wind", "accuracy", "guidance"],
                    credibility_score=0.95,
                    insight_category=InsightCategory.TECHNICAL_GUIDANCE,
                    expert_type=ExpertType.EXTENSION_SPECIALIST,
                    region="Great Plains",
                    publication_date=datetime(2024, 1, 15),
                    validation_status="peer_reviewed",
                    references=["Johnson et al. 2023. Wind Effects on Broadcast Application. Agronomy Journal."]
                ),
                ExpertInsight(
                    insight_id="broadcast_insight_2",
                    title="Calibration Best Practices for Broadcast Spreaders",
                    expert_name="Mark Anderson",
                    expert_credentials="Technical Manager, AgriTech Solutions",
                    content="Proper calibration is essential for accurate broadcast application. Use multiple test areas and account for fertilizer density variations. Document all calibration data and re-calibrate after any equipment maintenance or fertilizer type changes.",
                    application_methods=[ApplicationMethodType.BROADCAST],
                    tags=["calibration", "accuracy", "maintenance"],
                    credibility_score=0.92,
                    insight_category=InsightCategory.BEST_PRACTICES,
                    expert_type=ExpertType.INDUSTRY_EXPERT,
                    region="National",
                    publication_date=datetime(2024, 2, 1),
                    validation_status="industry_validated",
                    references=["Anderson, M. 2024. Equipment Calibration Guide. AgriTech Solutions."]
                )
            ],
            
            ApplicationMethodType.FOLIAR: [
                ExpertInsight(
                    insight_id="foliar_insight_1",
                    title="Foliar Application Timing for Maximum Uptake",
                    expert_name="Dr. Michael Chen",
                    expert_credentials="Extension Specialist, Iowa State University",
                    content="The optimal time for foliar application is early morning (6-8 AM) when stomata are open and humidity is high. Avoid applications during hot, dry conditions as this can cause phytotoxicity. Always include a surfactant to improve coverage and uptake.",
                    application_methods=[ApplicationMethodType.FOLIAR],
                    tags=["timing", "uptake", "phytotoxicity"],
                    credibility_score=0.94,
                    insight_category=InsightCategory.TECHNICAL_GUIDANCE,
                    expert_type=ExpertType.EXTENSION_SPECIALIST,
                    region="Midwest",
                    publication_date=datetime(2024, 1, 20),
                    validation_status="peer_reviewed",
                    references=["Chen et al. 2023. Foliar Application Timing. Crop Science."]
                ),
                ExpertInsight(
                    insight_id="foliar_insight_2",
                    title="Foliar Formulation Selection for Different Crops",
                    expert_name="Dr. Jennifer Williams",
                    expert_credentials="Research Scientist, USDA-ARS",
                    content="Crop-specific formulations are essential for effective foliar application. Corn responds well to chelated micronutrients, while soybeans benefit from amino acid complexes. Always consider plant stress levels when selecting formulations.",
                    application_methods=[ApplicationMethodType.FOLIAR],
                    tags=["formulation", "crop_specific", "stress"],
                    credibility_score=0.96,
                    insight_category=InsightCategory.RESEARCH_FINDINGS,
                    expert_type=ExpertType.RESEARCH_SCIENTIST,
                    region="National",
                    publication_date=datetime(2024, 2, 10),
                    validation_status="peer_reviewed",
                    references=["Williams et al. 2024. Foliar Formulation Research. Journal of Plant Nutrition."]
                )
            ],
            
            ApplicationMethodType.BAND: [
                ExpertInsight(
                    insight_id="band_insight_1",
                    title="Band Placement Optimization for Different Crops",
                    expert_name="Dr. Robert Martinez",
                    expert_credentials="Extension Specialist, University of Illinois",
                    content="For corn, place bands 2 inches to the side and 2 inches below the seed. For soybeans, bands should be 2-3 inches to the side of the row. This placement maximizes root contact while minimizing salt injury to emerging seedlings.",
                    application_methods=[ApplicationMethodType.BAND],
                    tags=["placement", "crops", "root_contact"],
                    credibility_score=0.93,
                    insight_category=InsightCategory.TECHNICAL_GUIDANCE,
                    expert_type=ExpertType.EXTENSION_SPECIALIST,
                    region="Midwest",
                    publication_date=datetime(2024, 1, 25),
                    validation_status="peer_reviewed",
                    references=["Martinez et al. 2023. Band Placement Research. Agronomy Journal."]
                )
            ],
            
            ApplicationMethodType.INJECTION: [
                ExpertInsight(
                    insight_id="injection_insight_1",
                    title="Injection Depth Optimization for Maximum Efficiency",
                    expert_name="Dr. David Thompson",
                    expert_credentials="Research Scientist, University of Wisconsin-Madison",
                    content="Injection depth should match the primary root zone for maximum nutrient efficiency. For most crops, 4-6 inches is optimal. Deeper injection (6-8 inches) may be needed in sandy soils, while shallower injection (3-4 inches) works in clay soils.",
                    application_methods=[ApplicationMethodType.INJECTION],
                    tags=["depth", "efficiency", "soil_type"],
                    credibility_score=0.91,
                    insight_category=InsightCategory.RESEARCH_FINDINGS,
                    expert_type=ExpertType.RESEARCH_SCIENTIST,
                    region="Upper Midwest",
                    publication_date=datetime(2024, 2, 5),
                    validation_status="peer_reviewed",
                    references=["Thompson et al. 2024. Injection Depth Research. Soil Science Society Journal."]
                )
            ]
        }
    
    def _initialize_research_findings(self):
        """Initialize research findings database."""
        self.research_findings = {
            "precision_agriculture": [
                {
                    "finding_id": "prec_ag_001",
                    "title": "GPS Guidance Improves Application Accuracy",
                    "researcher": "Dr. David Thompson",
                    "institution": "University of Wisconsin-Madison",
                    "study_type": "Field trial",
                    "duration": "3 years",
                    "location": "Wisconsin",
                    "findings": {
                        "accuracy_improvement": "25%",
                        "overlap_reduction": "15%",
                        "fuel_savings": "8%",
                        "time_savings": "12%"
                    },
                    "implications": [
                        "GPS guidance provides significant accuracy benefits",
                        "Overlap reduction improves efficiency",
                        "Fuel and time savings justify investment",
                        "Technology adoption is economically viable"
                    ],
                    "publication_date": datetime(2024, 1, 10),
                    "peer_reviewed": True,
                    "citations": 23
                }
            ],
            "environmental_impact": [
                {
                    "finding_id": "env_001",
                    "title": "Precision Application Reduces Nutrient Losses",
                    "researcher": "Dr. Jennifer Williams",
                    "institution": "USDA-ARS",
                    "study_type": "Long-term study",
                    "duration": "5 years",
                    "location": "Multiple states",
                    "findings": {
                        "nutrient_loss_reduction": "30%",
                        "water_quality_improvement": "Significant",
                        "soil_health_improvement": "Measurable",
                        "yield_maintenance": "100%"
                    },
                    "implications": [
                        "Precision application benefits environment",
                        "Nutrient losses can be significantly reduced",
                        "Environmental benefits don't compromise yields",
                        "Long-term studies validate benefits"
                    ],
                    "publication_date": datetime(2024, 1, 5),
                    "peer_reviewed": True,
                    "citations": 45
                }
            ]
        }
    
    def _initialize_regulatory_updates(self):
        """Initialize regulatory updates database."""
        self.regulatory_updates = {
            "environmental_regulations": [
                {
                    "update_id": "reg_001",
                    "title": "Updated Nutrient Management Regulations",
                    "agency": "EPA",
                    "effective_date": datetime(2024, 3, 1),
                    "description": "New regulations for nutrient management in agricultural operations",
                    "key_changes": [
                        "Enhanced reporting requirements",
                        "Stricter application timing restrictions",
                        "Improved buffer zone requirements",
                        "Enhanced record keeping"
                    ],
                    "impact": "Moderate",
                    "compliance_deadline": datetime(2024, 6, 1),
                    "resources": [
                        "EPA Nutrient Management Guide",
                        "State Extension Compliance Resources",
                        "Industry Best Practices"
                    ]
                }
            ],
            "safety_regulations": [
                {
                    "update_id": "safety_001",
                    "title": "Updated PPE Requirements for Fertilizer Application",
                    "agency": "OSHA",
                    "effective_date": datetime(2024, 4, 1),
                    "description": "New personal protective equipment requirements for fertilizer application",
                    "key_changes": [
                        "Enhanced respiratory protection",
                        "Improved eye protection standards",
                        "Updated chemical handling procedures",
                        "Enhanced training requirements"
                    ],
                    "impact": "High",
                    "compliance_deadline": datetime(2024, 7, 1),
                    "resources": [
                        "OSHA Safety Guidelines",
                        "Industry Safety Training",
                        "Equipment Manufacturer Guidelines"
                    ]
                }
            ]
        }
    
    def _initialize_market_trends(self):
        """Initialize market trends database."""
        self.market_trends = {
            "fertilizer_prices": [
                {
                    "trend_id": "price_001",
                    "title": "Fertilizer Price Trends 2024",
                    "analyst": "Agricultural Market Research",
                    "period": "Q1 2024",
                    "trend": "Stable to slightly increasing",
                    "key_factors": [
                        "Global supply chain stability",
                        "Energy cost fluctuations",
                        "Demand from emerging markets",
                        "Weather impact on production"
                    ],
                    "forecast": "Prices expected to remain stable through 2024",
                    "implications": [
                        "Plan fertilizer purchases strategically",
                        "Consider bulk purchasing opportunities",
                        "Monitor market conditions regularly",
                        "Evaluate alternative nutrient sources"
                    ],
                    "update_date": datetime(2024, 3, 1)
                }
            ],
            "technology_adoption": [
                {
                    "trend_id": "tech_001",
                    "title": "Precision Agriculture Technology Adoption",
                    "analyst": "Technology Research Group",
                    "period": "2024",
                    "trend": "Rapidly increasing",
                    "adoption_rate": "35% of farms",
                    "key_technologies": [
                        "GPS guidance systems",
                        "Variable rate application",
                        "Yield mapping",
                        "Soil testing technology"
                    ],
                    "forecast": "Adoption expected to reach 50% by 2026",
                    "implications": [
                        "Technology adoption accelerating",
                        "Competitive advantage for early adopters",
                        "Cost-benefit analysis becoming clearer",
                        "Training and support needs increasing"
                    ],
                    "update_date": datetime(2024, 2, 15)
                }
            ]
        }
    
    def _initialize_technology_updates(self):
        """Initialize technology updates database."""
        self.technology_updates = {
            "equipment_technology": [
                {
                    "update_id": "tech_001",
                    "title": "Next-Generation Broadcast Spreaders",
                    "technology_type": "Equipment",
                    "company": "AgriTech Solutions",
                    "release_date": datetime(2024, 2, 1),
                    "description": "New broadcast spreader technology with enhanced accuracy and efficiency",
                    "key_features": [
                        "Real-time rate adjustment",
                        "Improved spread pattern control",
                        "Enhanced GPS integration",
                        "Reduced maintenance requirements"
                    ],
                    "benefits": [
                        "Improved application accuracy",
                        "Reduced fertilizer waste",
                        "Lower operating costs",
                        "Enhanced environmental compliance"
                    ],
                    "availability": "Available now",
                    "cost_range": "$50,000 - $100,000",
                    "roi_estimate": "2-3 years"
                }
            ],
            "software_technology": [
                {
                    "update_id": "soft_001",
                    "title": "Advanced Application Planning Software",
                    "technology_type": "Software",
                    "company": "PrecisionAg Solutions",
                    "release_date": datetime(2024, 1, 15),
                    "description": "New software for comprehensive application planning and optimization",
                    "key_features": [
                        "Field mapping integration",
                        "Weather integration",
                        "Cost optimization",
                        "Environmental impact assessment"
                    ],
                    "benefits": [
                        "Improved planning efficiency",
                        "Better cost management",
                        "Enhanced environmental compliance",
                        "Simplified record keeping"
                    ],
                    "availability": "Available now",
                    "cost_range": "$500 - $2,000 annually",
                    "roi_estimate": "1-2 years"
                }
            ]
        }
    
    async def get_expert_insights(
        self,
        application_method: ApplicationMethodType,
        category: Optional[InsightCategory] = None,
        expert_type: Optional[ExpertType] = None,
        region: Optional[str] = None
    ) -> List[ExpertInsight]:
        """Get expert insights filtered by criteria."""
        try:
            insights = self.insights_database.get(application_method, [])
            
            # Filter by category
            if category:
                insights = [insight for insight in insights if insight.insight_category == category]
            
            # Filter by expert type
            if expert_type:
                insights = [insight for insight in insights if insight.expert_type == expert_type]
            
            # Filter by region
            if region:
                insights = [insight for insight in insights if region.lower() in insight.region.lower()]
            
            # Sort by credibility score
            insights.sort(key=lambda x: x.credibility_score, reverse=True)
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting expert insights: {e}")
            return []
    
    async def get_experts_by_specialization(
        self,
        specialization: str,
        expert_type: Optional[ExpertType] = None,
        region: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get experts by specialization."""
        try:
            experts = []
            
            for expert_type_key, expert_list in self.expert_database.items():
                for expert in expert_list:
                    # Check specialization
                    if specialization.lower() in expert["expertise"] or specialization.lower() in expert["specialization"]:
                        # Filter by expert type
                        if expert_type and expert_type.value not in expert_type_key:
                            continue
                        
                        # Filter by region
                        if region and region.lower() not in expert["region"].lower():
                            continue
                        
                        experts.append(expert)
            
            return experts
            
        except Exception as e:
            logger.error(f"Error getting experts: {e}")
            return []
    
    async def get_research_findings(
        self,
        topic: Optional[str] = None,
        researcher: Optional[str] = None,
        institution: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get research findings filtered by criteria."""
        try:
            findings = []
            
            for category, finding_list in self.research_findings.items():
                for finding in finding_list:
                    # Filter by topic
                    if topic and topic.lower() not in finding["title"].lower():
                        continue
                    
                    # Filter by researcher
                    if researcher and researcher.lower() not in finding["researcher"].lower():
                        continue
                    
                    # Filter by institution
                    if institution and institution.lower() not in finding["institution"].lower():
                        continue
                    
                    findings.append(finding)
            
            return findings
            
        except Exception as e:
            logger.error(f"Error getting research findings: {e}")
            return []
    
    async def get_regulatory_updates(
        self,
        agency: Optional[str] = None,
        impact_level: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get regulatory updates filtered by criteria."""
        try:
            updates = []
            
            for category, update_list in self.regulatory_updates.items():
                for update in update_list:
                    # Filter by agency
                    if agency and agency.lower() not in update["agency"].lower():
                        continue
                    
                    # Filter by impact level
                    if impact_level and impact_level.lower() != update["impact"].lower():
                        continue
                    
                    updates.append(update)
            
            return updates
            
        except Exception as e:
            logger.error(f"Error getting regulatory updates: {e}")
            return []
    
    async def get_market_trends(
        self,
        trend_type: Optional[str] = None,
        period: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get market trends filtered by criteria."""
        try:
            trends = []
            
            for category, trend_list in self.market_trends.items():
                for trend in trend_list:
                    # Filter by trend type
                    if trend_type and trend_type.lower() not in trend["title"].lower():
                        continue
                    
                    # Filter by period
                    if period and period.lower() not in trend["period"].lower():
                        continue
                    
                    trends.append(trend)
            
            return trends
            
        except Exception as e:
            logger.error(f"Error getting market trends: {e}")
            return []
    
    async def get_technology_updates(
        self,
        technology_type: Optional[str] = None,
        company: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get technology updates filtered by criteria."""
        try:
            updates = []
            
            for category, update_list in self.technology_updates.items():
                for update in update_list:
                    # Filter by technology type
                    if technology_type and technology_type.lower() != update["technology_type"].lower():
                        continue
                    
                    # Filter by company
                    if company and company.lower() not in update["company"].lower():
                        continue
                    
                    updates.append(update)
            
            return updates
            
        except Exception as e:
            logger.error(f"Error getting technology updates: {e}")
            return []
    
    async def get_expert_consultation_recommendations(
        self,
        user_profile: Dict[str, Any],
        farm_characteristics: Dict[str, Any],
        application_method: ApplicationMethodType
    ) -> List[Dict[str, Any]]:
        """Get expert consultation recommendations based on user needs."""
        try:
            recommendations = []
            
            # Get farm characteristics
            farm_size = farm_characteristics.get("farm_size_acres", 0)
            region = farm_characteristics.get("region", "")
            primary_crops = user_profile.get("primary_crops", [])
            experience_level = user_profile.get("experience_level", DifficultyLevel.BEGINNER)
            
            # Find relevant experts
            experts = await self.get_experts_by_specialization(
                application_method.value, region=region
            )
            
            for expert in experts:
                relevance_score = 0
                
                # Score based on region match
                if region.lower() in expert["region"].lower():
                    relevance_score += 0.3
                
                # Score based on crop specialization
                for crop in primary_crops:
                    if crop.lower() in [spec.lower() for spec in expert["specialization"]]:
                        relevance_score += 0.2
                        break
                
                # Score based on expertise match
                if application_method.value.lower() in [exp.lower() for exp in expert["expertise"]]:
                    relevance_score += 0.3
                
                # Score based on experience level
                if experience_level == DifficultyLevel.BEGINNER and expert["years_experience"] >= 10:
                    relevance_score += 0.1
                elif experience_level == DifficultyLevel.ADVANCED and expert["years_experience"] >= 15:
                    relevance_score += 0.1
                
                # Add expert if relevance score is high enough
                if relevance_score >= 0.4:
                    recommendation = {
                        "expert": expert,
                        "relevance_score": relevance_score,
                        "consultation_type": self._recommend_consultation_type(expert, experience_level),
                        "estimated_cost": self._estimate_consultation_cost(expert, farm_size),
                        "availability": expert["availability"],
                        "contact_info": expert["contact_info"]
                    }
                    recommendations.append(recommendation)
            
            # Sort by relevance score
            recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return recommendations[:3]  # Return top 3 recommendations
            
        except Exception as e:
            logger.error(f"Error getting expert consultation recommendations: {e}")
            return []
    
    def _recommend_consultation_type(
        self,
        expert: Dict[str, Any],
        experience_level: DifficultyLevel
    ) -> str:
        """Recommend consultation type based on expert and user experience."""
        if experience_level == DifficultyLevel.BEGINNER:
            return "Comprehensive training and guidance"
        elif experience_level == DifficultyLevel.INTERMEDIATE:
            return "Technical consultation and optimization"
        else:
            return "Advanced strategy and innovation consultation"
    
    def _estimate_consultation_cost(
        self,
        expert: Dict[str, Any],
        farm_size: float
    ) -> Dict[str, Any]:
        """Estimate consultation cost based on expert and farm size."""
        base_rate = 150  # Base hourly rate
        
        # Adjust based on expert type
        if expert["title"] == "Research Scientist":
            base_rate += 50
        elif expert["title"] == "Extension Specialist":
            base_rate += 25
        
        # Adjust based on farm size
        if farm_size > 1000:
            base_rate += 25
        elif farm_size < 100:
            base_rate -= 25
        
        return {
            "hourly_rate": base_rate,
            "estimated_hours": "2-4 hours",
            "total_range": f"${base_rate * 2} - ${base_rate * 4}",
            "notes": "Cost may vary based on consultation complexity"
        }
    
    async def validate_expert_insight(
        self,
        insight_id: str,
        validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate expert insight with additional data or feedback."""
        try:
            # Find the insight
            insight = None
            for method_insights in self.insights_database.values():
                for i in method_insights:
                    if i.insight_id == insight_id:
                        insight = i
                        break
            
            if not insight:
                raise ValueError(f"Expert insight {insight_id} not found")
            
            validation_results = {
                "insight_id": insight_id,
                "validation_score": 0.0,
                "validation_status": "pending",
                "feedback": [],
                "recommendations": []
            }
            
            # Validate based on provided data
            if "field_trial_results" in validation_data:
                results = validation_data["field_trial_results"]
                if results.get("success_rate", 0) >= 0.8:
                    validation_results["validation_score"] += 0.3
                    validation_results["feedback"].append("Field trial results support insight")
                else:
                    validation_results["feedback"].append("Field trial results inconclusive")
            
            if "expert_consensus" in validation_data:
                consensus = validation_data["expert_consensus"]
                if consensus.get("agreement_rate", 0) >= 0.8:
                    validation_results["validation_score"] += 0.4
                    validation_results["feedback"].append("Strong expert consensus")
                else:
                    validation_results["feedback"].append("Mixed expert opinion")
            
            if "research_support" in validation_data:
                research = validation_data["research_support"]
                if research.get("supporting_studies", 0) >= 3:
                    validation_results["validation_score"] += 0.3
                    validation_results["feedback"].append("Strong research support")
                else:
                    validation_results["feedback"].append("Limited research support")
            
            # Determine validation status
            if validation_results["validation_score"] >= 0.8:
                validation_results["validation_status"] = "validated"
                validation_results["recommendations"].append("Insight is well-supported and reliable")
            elif validation_results["validation_score"] >= 0.5:
                validation_results["validation_status"] = "partially_validated"
                validation_results["recommendations"].append("Insight has moderate support, use with caution")
            else:
                validation_results["validation_status"] = "needs_validation"
                validation_results["recommendations"].append("Insight needs additional validation")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating expert insight: {e}")
            raise