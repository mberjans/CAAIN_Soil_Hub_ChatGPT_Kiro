"""
Soil Management Service

Provides soil health, fertility improvement, and management recommendations.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime, date

try:
    from ..models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem
    )
except ImportError:
    from models.agricultural_models import (
        RecommendationRequest,
        RecommendationItem
    )


class SoilManagementService:
    """Service for soil health and management recommendations."""
    
    def __init__(self):
        """Initialize soil management service."""
        self.soil_health_indicators = self._build_soil_health_indicators()
        self.amendment_database = self._build_amendment_database()
        self.management_practices = self._build_management_practices()
    
    def _build_soil_health_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Build soil health indicator thresholds and targets."""
        return {
            "ph": {
                "optimal_range": (6.0, 7.0),
                "acceptable_range": (5.5, 7.5),
                "critical_low": 5.0,
                "critical_high": 8.5,
                "crop_specific": {
                    "corn": (6.0, 6.8),
                    "soybean": (6.0, 7.0),
                    "wheat": (6.0, 7.0),
                    "alfalfa": (6.8, 7.2)
                }
            },
            "organic_matter": {
                "excellent": 4.0,
                "good": 3.0,
                "fair": 2.0,
                "poor": 1.5,
                "target_increase_rate": 0.1  # % per year with good management
            },
            "phosphorus": {
                "very_low": 10,
                "low": 15,
                "medium": 30,
                "high": 50,
                "very_high": 75,
                "environmental_threshold": 100  # ppm
            },
            "potassium": {
                "very_low": 80,
                "low": 120,
                "medium": 200,
                "high": 300,
                "very_high": 400
            },
            "cec": {
                "sandy_soils": (5, 15),
                "loam_soils": (15, 25),
                "clay_soils": (25, 40)
            }
        }
    
    def _build_amendment_database(self) -> Dict[str, Dict[str, Any]]:
        """Build soil amendment database with characteristics."""
        return {
            "agricultural_lime": {
                "primary_purpose": "ph_adjustment",
                "ph_change_per_ton": 0.1,  # pH units per ton per acre
                "application_rate_range": (1.0, 4.0),  # tons per acre
                "cost_per_ton": 35.0,
                "incorporation_required": True,
                "response_time_months": 6,
                "duration_years": 3
            },
            "gypsum": {
                "primary_purpose": "calcium_sulfur_supply",
                "ph_effect": "neutral",
                "application_rate_range": (0.5, 2.0),
                "cost_per_ton": 45.0,
                "incorporation_required": False,
                "response_time_months": 3,
                "benefits": ["improved_structure", "reduced_compaction"]
            },
            "compost": {
                "primary_purpose": "organic_matter_improvement",
                "organic_matter_contribution": 0.1,  # % OM per ton per acre
                "application_rate_range": (5.0, 20.0),
                "cost_per_ton": 25.0,
                "nutrient_content": {"N": 1.5, "P": 1.0, "K": 1.0},
                "benefits": ["biology_enhancement", "structure_improvement", "water_retention"]
            },
            "manure": {
                "primary_purpose": "fertility_and_organic_matter",
                "organic_matter_contribution": 0.05,
                "application_rate_range": (10.0, 30.0),
                "cost_per_ton": 15.0,
                "nutrient_variability": "high",
                "testing_required": True,
                "incorporation_timing": "within_24_hours"
            }
        }
    
    def _build_management_practices(self) -> Dict[str, Dict[str, Any]]:
        """Build soil management practice database."""
        return {
            "cover_crops": {
                "benefits": ["erosion_control", "organic_matter", "nitrogen_fixation", "compaction_reduction"],
                "species": {
                    "crimson_clover": {"nitrogen_fixation": 60, "cost_per_acre": 35},
                    "winter_rye": {"erosion_control": "excellent", "cost_per_acre": 25},
                    "radishes": {"compaction_relief": "excellent", "cost_per_acre": 20}
                },
                "establishment_window": "august_september",
                "termination_timing": "spring_before_planting"
            },
            "no_till": {
                "benefits": ["soil_structure", "organic_matter", "erosion_control", "fuel_savings"],
                "challenges": ["residue_management", "pest_pressure", "equipment_requirements"],
                "transition_period_years": 3,
                "yield_impact_initial": -5,  # % yield reduction initially
                "yield_impact_mature": 5    # % yield increase after transition
            },
            "controlled_traffic": {
                "benefits": ["compaction_reduction", "improved_infiltration", "yield_increase"],
                "implementation_cost": 15000,  # Equipment modification cost
                "yield_benefit_percent": 8,
                "fuel_savings_percent": 12
            }
        }
    
    async def get_fertility_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate soil fertility improvement recommendations (Question 2)."""
        recommendations = []
        
        if not request.soil_data:
            return self._get_general_fertility_recommendations()
        
        # Analyze soil health status
        soil_health_score = self._calculate_soil_health_score(request.soil_data)
        
        # Generate specific recommendations based on soil test results
        ph_rec = self._get_ph_recommendation(request)
        if ph_rec:
            recommendations.append(ph_rec)
        
        om_rec = self._get_organic_matter_recommendation(request)
        if om_rec:
            recommendations.append(om_rec)
        
        nutrient_recs = self._get_nutrient_balance_recommendations(request)
        recommendations.extend(nutrient_recs)
        
        # Add management practice recommendations
        practice_recs = self._get_management_practice_recommendations(request, soil_health_score)
        recommendations.extend(practice_recs)
        
        return recommendations
    
    async def get_management_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate general soil management recommendations."""
        recommendations = []
        
        # Always recommend soil testing if not recent
        if not request.soil_data or self._is_soil_test_old(request.soil_data):
            testing_rec = self._create_soil_testing_recommendation()
            recommendations.append(testing_rec)
        
        # Cover crop recommendations
        cover_crop_rec = self._get_cover_crop_recommendation(request)
        if cover_crop_rec:
            recommendations.append(cover_crop_rec)
        
        # Tillage practice recommendations
        tillage_rec = self._get_tillage_recommendation(request)
        if tillage_rec:
            recommendations.append(tillage_rec)
        
        return recommendations
    
    async def get_ph_management_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate pH management recommendations."""
        recommendations = []
        
        if not request.soil_data or not request.soil_data.ph:
            return recommendations
        
        ph_rec = self._get_ph_recommendation(request)
        if ph_rec:
            recommendations.append(ph_rec)
        
        return recommendations
    
    async def get_organic_matter_recommendations(
        self, 
        request: RecommendationRequest
    ) -> List[RecommendationItem]:
        """Generate organic matter improvement recommendations."""
        recommendations = []
        
        om_rec = self._get_organic_matter_recommendation(request)
        if om_rec:
            recommendations.append(om_rec)
        
        return recommendations
    
    def _calculate_soil_health_score(self, soil_data) -> float:
        """Calculate overall soil health score (0-10 scale)."""
        scores = []
        
        # pH score
        if soil_data.ph:
            ph_score = self._score_ph(soil_data.ph)
            scores.append(ph_score)
        
        # Organic matter score
        if soil_data.organic_matter_percent:
            om_score = self._score_organic_matter(soil_data.organic_matter_percent)
            scores.append(om_score)
        
        # Nutrient scores
        if soil_data.phosphorus_ppm:
            p_score = self._score_phosphorus(soil_data.phosphorus_ppm)
            scores.append(p_score)
        
        if soil_data.potassium_ppm:
            k_score = self._score_potassium(soil_data.potassium_ppm)
            scores.append(k_score)
        
        return sum(scores) / len(scores) if scores else 5.0
    
    def _score_ph(self, ph: float) -> float:
        """Score pH on 0-10 scale."""
        optimal_range = self.soil_health_indicators["ph"]["optimal_range"]
        acceptable_range = self.soil_health_indicators["ph"]["acceptable_range"]
        
        if optimal_range[0] <= ph <= optimal_range[1]:
            return 10.0
        elif acceptable_range[0] <= ph <= acceptable_range[1]:
            return 7.0
        elif ph < self.soil_health_indicators["ph"]["critical_low"]:
            return 2.0
        elif ph > self.soil_health_indicators["ph"]["critical_high"]:
            return 3.0
        else:
            return 5.0
    
    def _score_organic_matter(self, om_percent: float) -> float:
        """Score organic matter on 0-10 scale."""
        indicators = self.soil_health_indicators["organic_matter"]
        
        if om_percent >= indicators["excellent"]:
            return 10.0
        elif om_percent >= indicators["good"]:
            return 8.0
        elif om_percent >= indicators["fair"]:
            return 6.0
        elif om_percent >= indicators["poor"]:
            return 4.0
        else:
            return 2.0
    
    def _score_phosphorus(self, p_ppm: float) -> float:
        """Score phosphorus on 0-10 scale."""
        indicators = self.soil_health_indicators["phosphorus"]
        
        if indicators["medium"] <= p_ppm <= indicators["high"]:
            return 10.0
        elif indicators["low"] <= p_ppm < indicators["medium"]:
            return 7.0
        elif p_ppm >= indicators["very_high"]:
            return 6.0  # Too high can be problematic
        elif p_ppm < indicators["very_low"]:
            return 3.0
        else:
            return 8.0
    
    def _score_potassium(self, k_ppm: float) -> float:
        """Score potassium on 0-10 scale."""
        indicators = self.soil_health_indicators["potassium"]
        
        if indicators["medium"] <= k_ppm <= indicators["high"]:
            return 10.0
        elif indicators["low"] <= k_ppm < indicators["medium"]:
            return 7.0
        elif k_ppm >= indicators["very_high"]:
            return 8.0
        elif k_ppm < indicators["very_low"]:
            return 3.0
        else:
            return 8.0
    
    def _get_ph_recommendation(self, request: RecommendationRequest) -> Optional[RecommendationItem]:
        """Generate pH management recommendation."""
        
        if not request.soil_data or not request.soil_data.ph:
            return None
        
        ph = request.soil_data.ph
        optimal_range = self.soil_health_indicators["ph"]["optimal_range"]
        
        # Determine if pH adjustment is needed
        if optimal_range[0] <= ph <= optimal_range[1]:
            return None  # pH is optimal
        
        if ph < optimal_range[0]:
            # Need lime application
            target_ph = 6.5
            ph_change_needed = target_ph - ph
            lime_rate = ph_change_needed / self.amendment_database["agricultural_lime"]["ph_change_per_ton"]
            lime_rate = max(1.0, min(4.0, lime_rate))  # Limit to reasonable range
            
            cost_estimate = lime_rate * self.amendment_database["agricultural_lime"]["cost_per_ton"]
            
            return RecommendationItem(
                recommendation_type="ph_management",
                title=f"Lime Application - {lime_rate:.1f} tons/acre",
                description=f"Your soil pH of {ph:.1f} is below optimal range. "
                           f"Apply {lime_rate:.1f} tons/acre of agricultural limestone "
                           f"to raise pH to {target_ph:.1f}.",
                priority=1,
                confidence_score=0.9,
                implementation_steps=[
                    f"Purchase {lime_rate:.1f} tons/acre of agricultural limestone",
                    "Apply lime in fall for spring crop benefit",
                    "Incorporate lime 6-8 inches deep if possible",
                    "Retest soil pH in 12-18 months",
                    "Plan annual maintenance lime applications"
                ],
                expected_outcomes=[
                    f"Soil pH increase to approximately {target_ph:.1f}",
                    "Improved phosphorus and micronutrient availability",
                    "Enhanced beneficial microbial activity",
                    "Better crop nutrient uptake and yield potential"
                ],
                cost_estimate=cost_estimate,
                roi_estimate=200.0,
                timing="Fall application preferred, 6 months before planting",
                agricultural_sources=[
                    "University Extension Lime Recommendations",
                    "Soil pH Management Guidelines",
                    "Agricultural Limestone Application Guide"
                ]
            )
        
        elif ph > optimal_range[1]:
            # pH too high - recommend sulfur or organic matter
            return RecommendationItem(
                recommendation_type="ph_management",
                title="High pH Management",
                description=f"Your soil pH of {ph:.1f} is above optimal range. "
                           f"Consider sulfur application or organic matter additions "
                           f"to gradually lower pH.",
                priority=2,
                confidence_score=0.8,
                implementation_steps=[
                    "Apply elemental sulfur at 200-400 lbs/acre",
                    "Increase organic matter through compost or manure",
                    "Monitor micronutrient availability",
                    "Consider acidifying fertilizers",
                    "Retest soil pH annually"
                ],
                expected_outcomes=[
                    "Gradual pH reduction toward optimal range",
                    "Improved micronutrient availability",
                    "Better iron and manganese uptake",
                    "Reduced risk of nutrient deficiencies"
                ],
                cost_estimate=45.0,
                timing="Fall or early spring application",
                agricultural_sources=[
                    "High pH Soil Management",
                    "Sulfur Application Guidelines"
                ]
            )
        
        return None
    
    def _get_organic_matter_recommendation(self, request: RecommendationRequest) -> Optional[RecommendationItem]:
        """Generate organic matter improvement recommendation."""
        
        if not request.soil_data or not request.soil_data.organic_matter_percent:
            return None
        
        om_percent = request.soil_data.organic_matter_percent
        indicators = self.soil_health_indicators["organic_matter"]
        
        if om_percent >= indicators["good"]:
            return None  # Organic matter is adequate
        
        # Determine improvement strategy
        target_om = indicators["good"]
        om_increase_needed = target_om - om_percent
        years_to_target = om_increase_needed / indicators["target_increase_rate"]
        
        # Recommend compost application
        compost_rate = 10.0  # tons per acre
        cost_estimate = compost_rate * self.amendment_database["compost"]["cost_per_ton"]
        
        return RecommendationItem(
            recommendation_type="organic_matter_improvement",
            title=f"Organic Matter Building Program",
            description=f"Your soil organic matter of {om_percent:.1f}% is below optimal levels. "
                       f"Implement a multi-year program to increase organic matter to {target_om:.1f}%.",
            priority=1 if om_percent < indicators["fair"] else 2,
            confidence_score=0.85,
            implementation_steps=[
                f"Apply {compost_rate:.0f} tons/acre of quality compost annually",
                "Establish cover crops in rotation",
                "Reduce tillage intensity when possible",
                "Return crop residues to soil",
                "Consider manure applications if available"
            ],
            expected_outcomes=[
                f"Organic matter increase to {target_om:.1f}% over {years_to_target:.0f} years",
                "Improved soil structure and water retention",
                "Enhanced nutrient cycling and availability",
                "Increased beneficial soil biology",
                "Better drought resilience"
            ],
            cost_estimate=cost_estimate,
            roi_estimate=150.0,
            timing="Fall application preferred",
            agricultural_sources=[
                "Soil Organic Matter Management",
                "Compost Application Guidelines",
                "Soil Health Improvement Strategies"
            ]
        )
    
    def _get_nutrient_balance_recommendations(self, request: RecommendationRequest) -> List[RecommendationItem]:
        """Generate nutrient balance recommendations."""
        recommendations = []
        
        if not request.soil_data:
            return recommendations
        
        # Phosphorus management
        if request.soil_data.phosphorus_ppm:
            p_ppm = request.soil_data.phosphorus_ppm
            p_indicators = self.soil_health_indicators["phosphorus"]
            
            if p_ppm < p_indicators["low"]:
                recommendations.append(self._create_phosphorus_buildup_recommendation(p_ppm))
            elif p_ppm > p_indicators["environmental_threshold"]:
                recommendations.append(self._create_phosphorus_reduction_recommendation(p_ppm))
        
        # Potassium management
        if request.soil_data.potassium_ppm:
            k_ppm = request.soil_data.potassium_ppm
            k_indicators = self.soil_health_indicators["potassium"]
            
            if k_ppm < k_indicators["low"]:
                recommendations.append(self._create_potassium_buildup_recommendation(k_ppm))
        
        return recommendations
    
    def _create_phosphorus_buildup_recommendation(self, p_ppm: float) -> RecommendationItem:
        """Create phosphorus buildup recommendation."""
        
        buildup_rate = 60  # lbs P2O5 per acre
        cost_estimate = 35.0
        
        return RecommendationItem(
            recommendation_type="phosphorus_buildup",
            title=f"Phosphorus Buildup Program",
            description=f"Soil test phosphorus of {p_ppm:.0f} ppm is below critical level. "
                       f"Implement buildup program to improve phosphorus availability.",
            priority=1,
            confidence_score=0.88,
            implementation_steps=[
                f"Apply {buildup_rate} lbs P2O5/acre for 2-3 years",
                "Use high-phosphorus fertilizer (DAP or MAP)",
                "Consider banding for improved efficiency",
                "Retest soil annually to monitor progress"
            ],
            expected_outcomes=[
                "Increased soil test phosphorus levels",
                "Improved root development and early growth",
                "Enhanced crop establishment and vigor",
                "Better yield potential"
            ],
            cost_estimate=cost_estimate,
            timing="Fall or at planting",
            agricultural_sources=[
                "Phosphorus Buildup Guidelines",
                "Soil Test P Interpretation"
            ]
        )
    
    def _create_phosphorus_reduction_recommendation(self, p_ppm: float) -> RecommendationItem:
        """Create phosphorus reduction recommendation."""
        
        return RecommendationItem(
            recommendation_type="phosphorus_reduction",
            title="Phosphorus Management - Reduce Applications",
            description=f"Soil test phosphorus of {p_ppm:.0f} ppm is very high. "
                       f"Reduce or eliminate phosphorus applications to prevent environmental issues.",
            priority=1,
            confidence_score=0.9,
            implementation_steps=[
                "Eliminate phosphorus fertilizer applications",
                "Use nitrogen-only fertilizers",
                "Implement erosion control practices",
                "Monitor soil test levels annually",
                "Consider phosphorus removal through high-yielding crops"
            ],
            expected_outcomes=[
                "Gradual reduction in soil phosphorus levels",
                "Reduced environmental risk",
                "Cost savings on fertilizer",
                "Maintained crop yields"
            ],
            cost_estimate=-25.0,  # Cost savings
            timing="Immediate implementation",
            agricultural_sources=[
                "Environmental Phosphorus Management",
                "High Soil Test P Guidelines"
            ]
        )
    
    def _create_potassium_buildup_recommendation(self, k_ppm: float) -> RecommendationItem:
        """Create potassium buildup recommendation."""
        
        buildup_rate = 80  # lbs K2O per acre
        cost_estimate = 28.0
        
        return RecommendationItem(
            recommendation_type="potassium_buildup",
            title="Potassium Buildup Program",
            description=f"Soil test potassium of {k_ppm:.0f} ppm is below optimal levels. "
                       f"Implement buildup program to improve potassium availability.",
            priority=2,
            confidence_score=0.85,
            implementation_steps=[
                f"Apply {buildup_rate} lbs K2O/acre annually",
                "Use muriate of potash (0-0-60)",
                "Apply in fall for best results",
                "Monitor soil test levels every 2-3 years"
            ],
            expected_outcomes=[
                "Increased soil potassium levels",
                "Improved drought tolerance",
                "Enhanced disease resistance",
                "Better grain quality"
            ],
            cost_estimate=cost_estimate,
            timing="Fall application preferred",
            agricultural_sources=[
                "Potassium Management Guidelines",
                "Soil Test K Interpretation"
            ]
        )
    
    def _get_management_practice_recommendations(
        self, 
        request: RecommendationRequest, 
        soil_health_score: float
    ) -> List[RecommendationItem]:
        """Generate management practice recommendations."""
        recommendations = []
        
        # Cover crop recommendation if soil health is poor
        if soil_health_score < 6.0:
            cover_crop_rec = self._get_cover_crop_recommendation(request)
            if cover_crop_rec:
                recommendations.append(cover_crop_rec)
        
        return recommendations
    
    def _get_cover_crop_recommendation(self, request: RecommendationRequest) -> Optional[RecommendationItem]:
        """Generate cover crop recommendation."""
        
        # Determine best cover crop species
        recommended_species = "winter_rye_crimson_clover_mix"
        cost_estimate = 30.0
        
        return RecommendationItem(
            recommendation_type="cover_crops",
            title="Cover Crop Implementation",
            description="Establish cover crops to improve soil health, reduce erosion, "
                       "and enhance nutrient cycling between cash crops.",
            priority=2,
            confidence_score=0.82,
            implementation_steps=[
                "Select appropriate cover crop species for your rotation",
                "Plant cover crops in late summer/early fall",
                "Ensure adequate seed-to-soil contact",
                "Terminate cover crops 2-3 weeks before planting",
                "Monitor establishment and growth"
            ],
            expected_outcomes=[
                "Improved soil structure and organic matter",
                "Reduced soil erosion and nutrient loss",
                "Enhanced water infiltration and retention",
                "Nitrogen fixation (with legume species)",
                "Weed suppression and pest management"
            ],
            cost_estimate=cost_estimate,
            roi_estimate=120.0,
            timing="Plant in August-September, terminate in spring",
            agricultural_sources=[
                "Cover Crop Selection Guide",
                "Soil Health Benefits of Cover Crops",
                "Cover Crop Management Recommendations"
            ]
        )
    
    def _get_tillage_recommendation(self, request: RecommendationRequest) -> Optional[RecommendationItem]:
        """Generate tillage practice recommendation."""
        
        return RecommendationItem(
            recommendation_type="tillage_management",
            title="Reduced Tillage Implementation",
            description="Consider transitioning to reduced tillage or no-till practices "
                       "to improve soil health and reduce operational costs.",
            priority=3,
            confidence_score=0.75,
            implementation_steps=[
                "Evaluate current tillage practices and equipment",
                "Plan gradual transition to reduced tillage",
                "Invest in appropriate planting equipment",
                "Develop residue management strategies",
                "Monitor soil compaction and structure"
            ],
            expected_outcomes=[
                "Improved soil structure and biology",
                "Reduced fuel and labor costs",
                "Enhanced water conservation",
                "Increased organic matter over time",
                "Better long-term soil health"
            ],
            cost_estimate=0.0,  # Equipment costs vary
            roi_estimate=110.0,
            timing="Implement during equipment replacement cycle",
            agricultural_sources=[
                "No-Till Management Guidelines",
                "Reduced Tillage Benefits and Challenges"
            ]
        )
    
    def _create_soil_testing_recommendation(self) -> RecommendationItem:
        """Create soil testing recommendation."""
        
        return RecommendationItem(
            recommendation_type="soil_testing",
            title="Comprehensive Soil Testing",
            description="Obtain current soil test results to guide fertilizer and lime applications "
                       "for optimal crop production and environmental stewardship.",
            priority=1,
            confidence_score=0.95,
            implementation_steps=[
                "Collect representative soil samples from each field",
                "Submit samples to certified laboratory",
                "Request complete analysis including pH, OM, NPK, and micronutrients",
                "Review results with agricultural professional",
                "Develop fertilizer and lime recommendations"
            ],
            expected_outcomes=[
                "Accurate assessment of soil fertility status",
                "Precise fertilizer and lime recommendations",
                "Optimized input costs and crop yields",
                "Environmental protection through proper rates"
            ],
            cost_estimate=25.0,  # Per sample
            roi_estimate=500.0,  # High ROI for proper soil management
            timing="Fall sampling preferred, spring acceptable",
            agricultural_sources=[
                "Soil Sampling Guidelines",
                "Soil Test Interpretation Guide"
            ]
        )
    
    def _is_soil_test_old(self, soil_data) -> bool:
        """Check if soil test is too old."""
        if not soil_data.test_date:
            return True
        
        from datetime import date, timedelta
        age_days = (date.today() - soil_data.test_date).days
        return age_days > 365 * 3  # Older than 3 years
    
    def _get_general_fertility_recommendations(self) -> List[RecommendationItem]:
        """Get general fertility recommendations when soil data unavailable."""
        
        return [
            RecommendationItem(
                recommendation_type="general_fertility",
                title="Establish Soil Testing Program",
                description="Without current soil test data, establish a comprehensive soil testing "
                           "program to guide fertility management decisions.",
                priority=1,
                confidence_score=0.9,
                implementation_steps=[
                    "Develop soil sampling plan for all fields",
                    "Collect samples every 2-3 years minimum",
                    "Test for pH, organic matter, NPK, and micronutrients",
                    "Work with certified crop advisor for interpretation",
                    "Implement recommendations based on results"
                ],
                expected_outcomes=[
                    "Data-driven fertility management",
                    "Optimized fertilizer applications",
                    "Improved crop yields and quality",
                    "Reduced environmental impact"
                ],
                cost_estimate=25.0,
                timing="Fall sampling preferred",
                agricultural_sources=[
                    "Soil Testing Best Practices",
                    "Fertility Management Guidelines"
                ]
            )
        ]