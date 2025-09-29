"""
Practice Comparison Service

Service for comparing conservation practices side-by-side, providing
trade-off analysis and decision support for drought management.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import asyncio
import statistics
from enum import Enum

from ..models.drought_models import (
    PracticeComparisonRequest,
    PracticeComparisonResponse,
    PracticeComparisonResult,
    DroughtRiskLevel,
    ConservationPracticeType
)

logger = logging.getLogger(__name__)

class ComparisonCriteria(str, Enum):
    """Comparison criteria options."""
    WATER_SAVINGS = "water_savings"
    COST_EFFECTIVENESS = "cost_effectiveness"
    SOIL_HEALTH = "soil_health"
    IMPLEMENTATION_EASE = "implementation_ease"
    MAINTENANCE_REQUIREMENTS = "maintenance_requirements"
    RISK_MITIGATION = "risk_mitigation"
    ENVIRONMENTAL_IMPACT = "environmental_impact"

class PracticeComparisonService:
    """Service for comparing conservation practices."""
    
    def __init__(self):
        self.database = None
        self.water_savings_calculator = None
        self.cost_analyzer = None
        self.soil_health_assessor = None
        self.risk_assessor = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the practice comparison service."""
        try:
            logger.info("Initializing Practice Comparison Service...")
            
            # Initialize database connection
            self.database = await self._initialize_database()
            
            # Initialize supporting services
            self.water_savings_calculator = await self._initialize_water_savings_calculator()
            self.cost_analyzer = await self._initialize_cost_analyzer()
            self.soil_health_assessor = await self._initialize_soil_health_assessor()
            self.risk_assessor = await self._initialize_risk_assessor()
            
            self.initialized = True
            logger.info("Practice Comparison Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Practice Comparison Service: {str(e)}")
            raise
    
    async def _initialize_database(self):
        """Initialize database connection."""
        # Database initialization logic
        return None
    
    async def _initialize_water_savings_calculator(self):
        """Initialize water savings calculator."""
        # Water savings calculator initialization
        return None
    
    async def _initialize_cost_analyzer(self):
        """Initialize cost analyzer."""
        # Cost analyzer initialization
        return None
    
    async def _initialize_soil_health_assessor(self):
        """Initialize soil health assessor."""
        # Soil health assessor initialization
        return None
    
    async def _initialize_risk_assessor(self):
        """Initialize risk assessor."""
        # Risk assessor initialization
        return None
    
    async def compare_practices(self, request: PracticeComparisonRequest) -> PracticeComparisonResponse:
        """
        Compare multiple conservation practices for a specific field.
        
        Args:
            request: Practice comparison request with field and practice details
            
        Returns:
            PracticeComparisonResponse with detailed comparison results
        """
        try:
            logger.info(f"Comparing practices for field {request.field_id}")
            
            if not self.initialized:
                await self.initialize()
            
            # Validate field exists and get field data
            field_data = await self._get_field_data(request.field_id)
            if not field_data:
                raise ValueError(f"Field {request.field_id} not found")
            
            # Get practice details for comparison
            practices_data = await self._get_practices_data(request.practices_to_compare)
            if len(practices_data) < 2:
                raise ValueError("At least 2 practices required for comparison")
            
            # Perform comparison for each practice
            comparison_results = []
            for practice_data in practices_data:
                result = await self._analyze_practice(
                    practice_data, 
                    field_data, 
                    request.comparison_criteria,
                    request.time_horizon_years
                )
                comparison_results.append(result)
            
            # Generate decision matrix
            decision_matrix = await self._generate_decision_matrix(
                comparison_results, 
                request.comparison_criteria
            )
            
            # Perform trade-off analysis
            trade_off_analysis = await self._perform_trade_off_analysis(comparison_results)
            
            # Determine recommended practice
            recommended_practice, recommendation_reason = await self._determine_recommendation(
                comparison_results, 
                request.comparison_criteria
            )
            
            # Create response
            response = PracticeComparisonResponse(
                field_id=request.field_id,
                practices_compared=comparison_results,
                recommended_practice=recommended_practice,
                recommendation_reason=recommendation_reason,
                decision_matrix=decision_matrix,
                trade_off_analysis=trade_off_analysis
            )
            
            logger.info(f"Practice comparison completed for field {request.field_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error comparing practices: {str(e)}")
            raise
    
    async def _get_field_data(self, field_id: UUID) -> Optional[Dict[str, Any]]:
        """Get field data for analysis."""
        try:
            # Query database for field information
            # This would include soil type, size, current practices, etc.
            field_data = {
                "field_id": field_id,
                "soil_type": "clay_loam",
                "field_size_acres": 40.0,
                "current_ph": 6.2,
                "organic_matter_percent": 3.5,
                "drainage_class": "moderate",
                "slope_percent": 2.0,
                "irrigation_available": True,
                "current_practices": []
            }
            return field_data
        except Exception as e:
            logger.error(f"Error getting field data: {str(e)}")
            return None
    
    async def _get_practices_data(self, practice_ids: List[UUID]) -> List[Dict[str, Any]]:
        """Get practice data for comparison."""
        try:
            practices_data = []
            for practice_id in practice_ids:
                # Query database for practice details
                practice_data = {
                    "practice_id": practice_id,
                    "practice_name": f"Practice {practice_id}",
                    "practice_type": ConservationPracticeType.COVER_CROPS,
                    "description": "Cover crop implementation",
                    "implementation_cost_per_acre": Decimal("25.00"),
                    "annual_maintenance_cost": Decimal("5.00"),
                    "water_savings_potential": 15.0,
                    "soil_health_benefits": 8.5,
                    "implementation_complexity": 6.0,
                    "maintenance_requirements": 4.0,
                    "risk_mitigation_score": 7.5,
                    "environmental_impact_score": 9.0
                }
                practices_data.append(practice_data)
            return practices_data
        except Exception as e:
            logger.error(f"Error getting practices data: {str(e)}")
            return []
    
    async def _analyze_practice(
        self, 
        practice_data: Dict[str, Any], 
        field_data: Dict[str, Any],
        criteria: List[str],
        time_horizon: int
    ) -> PracticeComparisonResult:
        """Analyze individual practice for comparison."""
        try:
            # Calculate water savings
            water_savings_percent = await self._calculate_water_savings(
                practice_data, field_data, time_horizon
            )
            
            # Calculate cost effectiveness
            implementation_cost = practice_data["implementation_cost_per_acre"]
            annual_maintenance = practice_data["annual_maintenance_cost"]
            
            # Calculate soil health impact
            soil_health_impact_score = await self._calculate_soil_health_impact(
                practice_data, field_data
            )
            
            # Calculate effectiveness rating
            effectiveness_rating = await self._calculate_effectiveness_rating(
                practice_data, field_data, criteria
            )
            
            # Assess risk level
            risk_level = await self._assess_risk_level(practice_data, field_data)
            
            # Calculate payback period
            payback_period = await self._calculate_payback_period(
                practice_data, field_data, water_savings_percent
            )
            
            # Calculate total benefit score
            total_benefit_score = await self._calculate_total_benefit_score(
                practice_data, water_savings_percent, soil_health_impact_score, 
                effectiveness_rating, risk_level
            )
            
            return PracticeComparisonResult(
                practice_id=practice_data["practice_id"],
                practice_name=practice_data["practice_name"],
                water_savings_percent=water_savings_percent,
                implementation_cost_per_acre=implementation_cost,
                annual_maintenance_cost=annual_maintenance,
                soil_health_impact_score=soil_health_impact_score,
                effectiveness_rating=effectiveness_rating,
                risk_level=risk_level,
                payback_period_years=payback_period,
                total_benefit_score=total_benefit_score
            )
            
        except Exception as e:
            logger.error(f"Error analyzing practice: {str(e)}")
            raise
    
    async def _calculate_water_savings(
        self, 
        practice_data: Dict[str, Any], 
        field_data: Dict[str, Any],
        time_horizon: int
    ) -> float:
        """Calculate expected water savings percentage."""
        try:
            base_savings = practice_data["water_savings_potential"]
            
            # Adjust based on field characteristics
            soil_factor = 1.0
            if field_data["soil_type"] == "sandy":
                soil_factor = 1.2  # Sandy soils benefit more from water conservation
            elif field_data["soil_type"] == "clay":
                soil_factor = 0.8  # Clay soils retain water better
            
            # Adjust based on irrigation availability
            irrigation_factor = 1.0
            if field_data["irrigation_available"]:
                irrigation_factor = 1.1  # More savings potential with irrigation
            
            # Adjust based on time horizon
            time_factor = min(1.0 + (time_horizon * 0.05), 1.5)  # Benefits increase over time
            
            adjusted_savings = base_savings * soil_factor * irrigation_factor * time_factor
            return round(min(adjusted_savings, 50.0), 1)  # Cap at 50%
            
        except Exception as e:
            logger.error(f"Error calculating water savings: {str(e)}")
            return 0.0
    
    async def _calculate_soil_health_impact(
        self, 
        practice_data: Dict[str, Any], 
        field_data: Dict[str, Any]
    ) -> float:
        """Calculate soil health impact score."""
        try:
            base_score = practice_data["soil_health_benefits"]
            
            # Adjust based on current soil health
            current_om = field_data["organic_matter_percent"]
            if current_om < 2.0:
                om_factor = 1.3  # Low OM fields benefit more
            elif current_om > 5.0:
                om_factor = 0.7  # High OM fields benefit less
            else:
                om_factor = 1.0
            
            # Adjust based on soil type
            soil_type = field_data["soil_type"]
            if soil_type == "clay":
                soil_factor = 1.1  # Clay soils benefit more from organic matter
            elif soil_type == "sandy":
                soil_factor = 1.2  # Sandy soils benefit more from structure
            else:
                soil_factor = 1.0
            
            adjusted_score = base_score * om_factor * soil_factor
            return round(min(adjusted_score, 10.0), 1)  # Cap at 10
            
        except Exception as e:
            logger.error(f"Error calculating soil health impact: {str(e)}")
            return 0.0
    
    async def _calculate_effectiveness_rating(
        self, 
        practice_data: Dict[str, Any], 
        field_data: Dict[str, Any],
        criteria: List[str]
    ) -> float:
        """Calculate overall effectiveness rating."""
        try:
            scores = []
            
            # Water savings score
            if "water_savings" in criteria:
                water_score = practice_data["water_savings_potential"] / 10.0
                scores.append(water_score)
            
            # Cost effectiveness score
            if "cost_effectiveness" in criteria:
                cost_score = 10.0 - (practice_data["implementation_cost_per_acre"] / 10.0)
                scores.append(max(cost_score, 0))
            
            # Soil health score
            if "soil_health" in criteria:
                soil_score = practice_data["soil_health_benefits"]
                scores.append(soil_score)
            
            # Implementation ease score
            if "implementation_ease" in criteria:
                ease_score = 10.0 - practice_data["implementation_complexity"]
                scores.append(max(ease_score, 0))
            
            # Maintenance requirements score
            if "maintenance_requirements" in criteria:
                maint_score = 10.0 - practice_data["maintenance_requirements"]
                scores.append(max(maint_score, 0))
            
            # Risk mitigation score
            if "risk_mitigation" in criteria:
                risk_score = practice_data["risk_mitigation_score"]
                scores.append(risk_score)
            
            # Environmental impact score
            if "environmental_impact" in criteria:
                env_score = practice_data["environmental_impact_score"]
                scores.append(env_score)
            
            if scores:
                return round(sum(scores) / len(scores), 1)
            else:
                return 5.0  # Default score
                
        except Exception as e:
            logger.error(f"Error calculating effectiveness rating: {str(e)}")
            return 5.0
    
    async def _assess_risk_level(
        self, 
        practice_data: Dict[str, Any], 
        field_data: Dict[str, Any]
    ) -> DroughtRiskLevel:
        """Assess risk level for the practice."""
        try:
            risk_score = practice_data["risk_mitigation_score"]
            
            if risk_score >= 8.0:
                return DroughtRiskLevel.LOW
            elif risk_score >= 6.0:
                return DroughtRiskLevel.MODERATE
            elif risk_score >= 4.0:
                return DroughtRiskLevel.HIGH
            else:
                return DroughtRiskLevel.SEVERE
                
        except Exception as e:
            logger.error(f"Error assessing risk level: {str(e)}")
            return DroughtRiskLevel.MODERATE
    
    async def _calculate_payback_period(
        self, 
        practice_data: Dict[str, Any], 
        field_data: Dict[str, Any],
        water_savings_percent: float
    ) -> Optional[float]:
        """Calculate payback period in years."""
        try:
            implementation_cost = float(practice_data["implementation_cost_per_acre"])
            annual_maintenance = float(practice_data["annual_maintenance_cost"])
            
            if implementation_cost <= 0:
                return None
            
            # Estimate annual savings from water conservation
            # This would be more sophisticated in a real implementation
            annual_savings = water_savings_percent * 2.0  # $2 per percent savings per acre
            
            net_annual_benefit = annual_savings - annual_maintenance
            
            if net_annual_benefit <= 0:
                return None
            
            payback_period = implementation_cost / net_annual_benefit
            return round(payback_period, 1)
            
        except Exception as e:
            logger.error(f"Error calculating payback period: {str(e)}")
            return None
    
    async def _calculate_total_benefit_score(
        self, 
        practice_data: Dict[str, Any], 
        water_savings: float,
        soil_health: float,
        effectiveness: float,
        risk_level: DroughtRiskLevel
    ) -> float:
        """Calculate total benefit score."""
        try:
            # Weighted scoring system
            weights = {
                "water_savings": 0.3,
                "soil_health": 0.25,
                "effectiveness": 0.25,
                "risk_mitigation": 0.2
            }
            
            # Convert risk level to numeric score
            risk_scores = {
                DroughtRiskLevel.LOW: 10.0,
                DroughtRiskLevel.MODERATE: 7.5,
                DroughtRiskLevel.HIGH: 5.0,
                DroughtRiskLevel.SEVERE: 2.5,
                DroughtRiskLevel.EXTREME: 1.0
            }
            
            risk_score = risk_scores.get(risk_level, 5.0)
            
            # Calculate weighted score
            total_score = (
                (water_savings / 10.0) * weights["water_savings"] +
                (soil_health / 10.0) * weights["soil_health"] +
                (effectiveness / 10.0) * weights["effectiveness"] +
                (risk_score / 10.0) * weights["risk_mitigation"]
            ) * 10.0
            
            return round(total_score, 1)
            
        except Exception as e:
            logger.error(f"Error calculating total benefit score: {str(e)}")
            return 5.0
    
    async def _generate_decision_matrix(
        self, 
        comparison_results: List[PracticeComparisonResult],
        criteria: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Generate decision matrix for comparison."""
        try:
            matrix = {}
            
            for criterion in criteria:
                matrix[criterion] = {}
                for result in comparison_results:
                    if criterion == "water_savings":
                        matrix[criterion][str(result.practice_id)] = result.water_savings_percent
                    elif criterion == "cost_effectiveness":
                        # Higher cost = lower score
                        cost_score = 10.0 - (float(result.implementation_cost_per_acre) / 10.0)
                        matrix[criterion][str(result.practice_id)] = max(cost_score, 0)
                    elif criterion == "soil_health":
                        matrix[criterion][str(result.practice_id)] = result.soil_health_impact_score
                    else:
                        # Default to effectiveness rating
                        matrix[criterion][str(result.practice_id)] = result.effectiveness_rating
            
            return matrix
            
        except Exception as e:
            logger.error(f"Error generating decision matrix: {str(e)}")
            return {}
    
    async def _perform_trade_off_analysis(
        self, 
        comparison_results: List[PracticeComparisonResult]
    ) -> Dict[str, Any]:
        """Perform trade-off analysis between practices."""
        try:
            analysis = {
                "cost_vs_benefit": {},
                "implementation_vs_maintenance": {},
                "short_term_vs_long_term": {},
                "risk_vs_reward": {}
            }
            
            # Cost vs Benefit analysis
            for result in comparison_results:
                cost_benefit_ratio = float(result.implementation_cost_per_acre) / result.total_benefit_score
                analysis["cost_vs_benefit"][str(result.practice_id)] = {
                    "ratio": round(cost_benefit_ratio, 2),
                    "cost": float(result.implementation_cost_per_acre),
                    "benefit": result.total_benefit_score
                }
            
            # Implementation vs Maintenance analysis
            for result in comparison_results:
                analysis["implementation_vs_maintenance"][str(result.practice_id)] = {
                    "implementation_cost": float(result.implementation_cost_per_acre),
                    "annual_maintenance": float(result.annual_maintenance_cost),
                    "total_cost_ratio": round(
                        float(result.implementation_cost_per_acre) / 
                        max(float(result.annual_maintenance_cost), 1.0), 2
                    )
                }
            
            # Short term vs Long term analysis
            for result in comparison_results:
                analysis["short_term_vs_long_term"][str(result.practice_id)] = {
                    "immediate_cost": float(result.implementation_cost_per_acre),
                    "payback_period": result.payback_period_years,
                    "long_term_benefit": result.total_benefit_score
                }
            
            # Risk vs Reward analysis
            for result in comparison_results:
                risk_scores = {
                    DroughtRiskLevel.LOW: 1.0,
                    DroughtRiskLevel.MODERATE: 2.0,
                    DroughtRiskLevel.HIGH: 3.0,
                    DroughtRiskLevel.SEVERE: 4.0,
                    DroughtRiskLevel.EXTREME: 5.0
                }
                risk_score = risk_scores.get(result.risk_level, 2.0)
                
                analysis["risk_vs_reward"][str(result.practice_id)] = {
                    "risk_level": result.risk_level.value,
                    "risk_score": risk_score,
                    "reward_score": result.total_benefit_score,
                    "risk_reward_ratio": round(risk_score / result.total_benefit_score, 2)
                }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error performing trade-off analysis: {str(e)}")
            return {}
    
    async def _determine_recommendation(
        self, 
        comparison_results: List[PracticeComparisonResult],
        criteria: List[str]
    ) -> Tuple[Optional[UUID], str]:
        """Determine recommended practice and reasoning."""
        try:
            if not comparison_results:
                return None, "No practices to compare"
            
            # Sort by total benefit score
            sorted_results = sorted(comparison_results, key=lambda x: x.total_benefit_score, reverse=True)
            recommended_practice = sorted_results[0]
            
            # Generate recommendation reason
            reasons = []
            
            if recommended_practice.total_benefit_score >= 8.0:
                reasons.append("highest overall benefit score")
            
            if recommended_practice.water_savings_percent >= 20.0:
                reasons.append("excellent water savings potential")
            
            if recommended_practice.soil_health_impact_score >= 8.0:
                reasons.append("strong soil health benefits")
            
            if recommended_practice.payback_period_years and recommended_practice.payback_period_years <= 3.0:
                reasons.append("quick payback period")
            
            if recommended_practice.risk_level in [DroughtRiskLevel.LOW, DroughtRiskLevel.MODERATE]:
                reasons.append("low to moderate risk level")
            
            if not reasons:
                reasons.append("best overall performance across all criteria")
            
            reason_text = f"Recommended due to {', '.join(reasons)}"
            
            return recommended_practice.practice_id, reason_text
            
        except Exception as e:
            logger.error(f"Error determining recommendation: {str(e)}")
            return None, "Unable to determine recommendation"