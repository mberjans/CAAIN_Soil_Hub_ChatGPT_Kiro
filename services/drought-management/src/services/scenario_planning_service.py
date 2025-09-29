"""
Scenario Planning Service

Service for drought management scenario planning, providing what-if analysis,
scenario comparison, and risk assessment for long-term planning.
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
    ScenarioPlanningRequest,
    ScenarioPlanningResponse,
    ScenarioOutcome,
    DroughtRiskLevel,
    ConservationPracticeType
)

logger = logging.getLogger(__name__)

class WeatherScenario(str, Enum):
    """Weather scenario types."""
    NORMAL = "normal"
    DROUGHT = "drought"
    WET = "wet"
    EXTREME_DROUGHT = "extreme_drought"
    VARIABLE = "variable"

class ScenarioComplexity(str, Enum):
    """Scenario complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class ScenarioPlanningService:
    """Service for drought management scenario planning."""
    
    def __init__(self):
        self.database = None
        self.weather_model = None
        self.economic_model = None
        self.risk_assessor = None
        self.practice_analyzer = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize the scenario planning service."""
        try:
            logger.info("Initializing Scenario Planning Service...")
            
            # Initialize database connection
            self.database = await self._initialize_database()
            
            # Initialize supporting services
            self.weather_model = await self._initialize_weather_model()
            self.economic_model = await self._initialize_economic_model()
            self.risk_assessor = await self._initialize_risk_assessor()
            self.practice_analyzer = await self._initialize_practice_analyzer()
            
            self.initialized = True
            logger.info("Scenario Planning Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Scenario Planning Service: {str(e)}")
            raise
    
    async def _initialize_database(self):
        """Initialize database connection."""
        # Database initialization logic
        return None
    
    async def _initialize_weather_model(self):
        """Initialize weather modeling service."""
        # Weather model initialization
        return None
    
    async def _initialize_economic_model(self):
        """Initialize economic modeling service."""
        # Economic model initialization
        return None
    
    async def _initialize_risk_assessor(self):
        """Initialize risk assessment service."""
        # Risk assessor initialization
        return None
    
    async def _initialize_practice_analyzer(self):
        """Initialize practice analysis service."""
        # Practice analyzer initialization
        return None
    
    async def plan_scenarios(self, request: ScenarioPlanningRequest) -> ScenarioPlanningResponse:
        """
        Plan and analyze drought management scenarios.
        
        Args:
            request: Scenario planning request with parameters and constraints
            
        Returns:
            ScenarioPlanningResponse with scenario analysis results
        """
        try:
            logger.info(f"Planning scenarios for farm {request.farm_location_id}")
            
            if not self.initialized:
                await self.initialize()
            
            # Get farm data
            farm_data = await self._get_farm_data(request.farm_location_id)
            if not farm_data:
                raise ValueError(f"Farm location {request.farm_location_id} not found")
            
            # Get practice data
            practices_data = await self._get_practices_data(request.practices_to_evaluate)
            if not practices_data:
                raise ValueError("No practices found for evaluation")
            
            # Generate scenarios
            scenarios_evaluated = []
            for weather_scenario in request.weather_scenarios:
                for practice_combination in self._generate_practice_combinations(practices_data):
                    scenario_outcome = await self._evaluate_scenario(
                        weather_scenario,
                        practice_combination,
                        farm_data,
                        request.time_horizon_months,
                        request.include_economic_analysis,
                        request.include_risk_assessment
                    )
                    scenarios_evaluated.append(scenario_outcome)
            
            # Perform risk assessment
            risk_assessment = {}
            if request.include_risk_assessment:
                risk_assessment = await self._perform_risk_assessment(scenarios_evaluated)
            
            # Perform economic analysis
            economic_summary = {}
            if request.include_economic_analysis:
                economic_summary = await self._perform_economic_analysis(scenarios_evaluated)
            
            # Determine recommended scenario
            recommended_scenario, recommendation_reason = await self._determine_recommended_scenario(
                scenarios_evaluated, request.include_economic_analysis, request.include_risk_assessment
            )
            
            # Generate implementation timeline
            implementation_timeline = await self._generate_implementation_timeline(
                recommended_scenario, scenarios_evaluated, request.time_horizon_months
            )
            
            # Create response
            response = ScenarioPlanningResponse(
                farm_location_id=request.farm_location_id,
                scenario_name=request.scenario_name,
                time_horizon_months=request.time_horizon_months,
                scenarios_evaluated=scenarios_evaluated,
                recommended_scenario=recommended_scenario,
                recommendation_reason=recommendation_reason,
                risk_assessment=risk_assessment,
                economic_summary=economic_summary,
                implementation_timeline=implementation_timeline
            )
            
            logger.info(f"Scenario planning completed for farm {request.farm_location_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error planning scenarios: {str(e)}")
            raise
    
    async def _get_farm_data(self, farm_location_id: UUID) -> Optional[Dict[str, Any]]:
        """Get farm location data."""
        try:
            # Query database for farm information
            farm_data = {
                "farm_location_id": farm_location_id,
                "farm_name": "Sample Farm",
                "location": {"lat": 40.0, "lng": -95.0},
                "total_acres": 200.0,
                "number_of_fields": 5,
                "primary_crops": ["corn", "soybean"],
                "soil_types": ["clay_loam", "sandy_loam"],
                "irrigation_system": "center_pivot",
                "current_practices": [],
                "historical_yields": {"corn": 180.0, "soybean": 55.0},
                "water_rights": "surface_water",
                "energy_costs": {"electricity": 0.12, "diesel": 3.50}
            }
            return farm_data
        except Exception as e:
            logger.error(f"Error getting farm data: {str(e)}")
            return None
    
    async def _get_practices_data(self, practice_ids: List[UUID]) -> List[Dict[str, Any]]:
        """Get practice data for scenario evaluation."""
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
                    "yield_impact_percent": -2.0,  # Slight yield reduction initially
                    "soil_health_benefits": 8.5,
                    "implementation_time_months": 3,
                    "effectiveness_rating": 7.5,
                    "risk_level": DroughtRiskLevel.MODERATE,
                    "compatibility_with_other_practices": ["no_till", "mulching"]
                }
                practices_data.append(practice_data)
            return practices_data
        except Exception as e:
            logger.error(f"Error getting practices data: {str(e)}")
            return []
    
    def _generate_practice_combinations(self, practices_data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Generate combinations of practices for scenario evaluation."""
        try:
            combinations = []
            
            # Single practices
            for practice in practices_data:
                combinations.append([practice])
            
            # Two-practice combinations
            for i in range(len(practices_data)):
                for j in range(i + 1, len(practices_data)):
                    practice1 = practices_data[i]
                    practice2 = practices_data[j]
                    
                    # Check compatibility
                    if self._are_practices_compatible(practice1, practice2):
                        combinations.append([practice1, practice2])
            
            # Three-practice combinations (if applicable)
            if len(practices_data) >= 3:
                for i in range(len(practices_data)):
                    for j in range(i + 1, len(practices_data)):
                        for k in range(j + 1, len(practices_data)):
                            practice1 = practices_data[i]
                            practice2 = practices_data[j]
                            practice3 = practices_data[k]
                            
                            if (self._are_practices_compatible(practice1, practice2) and
                                self._are_practices_compatible(practice1, practice3) and
                                self._are_practices_compatible(practice2, practice3)):
                                combinations.append([practice1, practice2, practice3])
            
            return combinations
            
        except Exception as e:
            logger.error(f"Error generating practice combinations: {str(e)}")
            return []
    
    def _are_practices_compatible(self, practice1: Dict[str, Any], practice2: Dict[str, Any]) -> bool:
        """Check if two practices are compatible."""
        try:
            # Check compatibility based on practice types and characteristics
            compatible_types = {
                ConservationPracticeType.COVER_CROPS: [ConservationPracticeType.NO_TILL, ConservationPracticeType.MULCHING],
                ConservationPracticeType.NO_TILL: [ConservationPracticeType.COVER_CROPS, ConservationPracticeType.CROP_ROTATION],
                ConservationPracticeType.MULCHING: [ConservationPracticeType.COVER_CROPS, ConservationPracticeType.IRRIGATION_EFFICIENCY],
                ConservationPracticeType.IRRIGATION_EFFICIENCY: [ConservationPracticeType.MULCHING, ConservationPracticeType.SOIL_AMENDMENTS]
            }
            
            type1 = practice1["practice_type"]
            type2 = practice2["practice_type"]
            
            return (type2 in compatible_types.get(type1, []) or 
                    type1 in compatible_types.get(type2, []))
            
        except Exception as e:
            logger.error(f"Error checking practice compatibility: {str(e)}")
            return False
    
    async def _evaluate_scenario(
        self,
        weather_scenario: str,
        practice_combination: List[Dict[str, Any]],
        farm_data: Dict[str, Any],
        time_horizon_months: int,
        include_economic: bool,
        include_risk: bool
    ) -> ScenarioOutcome:
        """Evaluate a specific scenario."""
        try:
            # Calculate expected water savings
            expected_water_savings = await self._calculate_scenario_water_savings(
                practice_combination, weather_scenario, farm_data, time_horizon_months
            )
            
            # Calculate expected yield impact
            expected_yield_impact = await self._calculate_scenario_yield_impact(
                practice_combination, weather_scenario, farm_data, time_horizon_months
            )
            
            # Calculate implementation cost
            implementation_cost = await self._calculate_scenario_cost(
                practice_combination, farm_data, time_horizon_months
            )
            
            # Calculate net benefit
            net_benefit = await self._calculate_scenario_net_benefit(
                practice_combination, expected_water_savings, expected_yield_impact,
                implementation_cost, farm_data, time_horizon_months
            )
            
            # Calculate risk score
            risk_score = 5.0  # Default moderate risk
            if include_risk:
                risk_score = await self._calculate_scenario_risk_score(
                    practice_combination, weather_scenario, farm_data
                )
            
            # Calculate success probability
            success_probability = await self._calculate_success_probability(
                practice_combination, weather_scenario, risk_score
            )
            
            # Create scenario outcome
            scenario_outcome = ScenarioOutcome(
                scenario_name=f"{weather_scenario}_{len(practice_combination)}_practices",
                weather_condition=weather_scenario,
                practice_combination=[p["practice_name"] for p in practice_combination],
                expected_water_savings=expected_water_savings,
                expected_yield_impact=expected_yield_impact,
                implementation_cost=implementation_cost,
                net_benefit=net_benefit,
                risk_score=risk_score,
                success_probability=success_probability
            )
            
            return scenario_outcome
            
        except Exception as e:
            logger.error(f"Error evaluating scenario: {str(e)}")
            raise
    
    async def _calculate_scenario_water_savings(
        self,
        practice_combination: List[Dict[str, Any]],
        weather_scenario: str,
        farm_data: Dict[str, Any],
        time_horizon_months: int
    ) -> Decimal:
        """Calculate expected water savings for scenario."""
        try:
            base_savings = sum(p["water_savings_potential"] for p in practice_combination)
            
            # Adjust for weather scenario
            weather_multipliers = {
                WeatherScenario.NORMAL: 1.0,
                WeatherScenario.DROUGHT: 1.3,  # More savings in drought
                WeatherScenario.WET: 0.7,      # Less savings in wet conditions
                WeatherScenario.EXTREME_DROUGHT: 1.5,
                WeatherScenario.VARIABLE: 1.1
            }
            
            weather_multiplier = weather_multipliers.get(weather_scenario, 1.0)
            
            # Adjust for practice interactions
            interaction_factor = 1.0
            if len(practice_combination) > 1:
                # Practices may have synergistic or antagonistic effects
                interaction_factor = 0.9 + (len(practice_combination) * 0.05)  # Slight synergy
            
            # Adjust for time horizon
            time_factor = min(1.0 + (time_horizon_months * 0.01), 1.3)  # Benefits increase over time
            
            # Calculate total savings
            total_savings = base_savings * weather_multiplier * interaction_factor * time_factor
            
            # Convert to monetary value (simplified)
            water_cost_per_gallon = Decimal("0.002")  # $0.002 per gallon
            gallons_saved_per_acre = total_savings * 1000  # Simplified conversion
            total_acres = farm_data["total_acres"]
            
            monetary_savings = Decimal(str(total_savings)) * water_cost_per_gallon * Decimal(str(gallons_saved_per_acre)) * Decimal(str(total_acres))
            
            return monetary_savings
            
        except Exception as e:
            logger.error(f"Error calculating water savings: {str(e)}")
            return Decimal("0.00")
    
    async def _calculate_scenario_yield_impact(
        self,
        practice_combination: List[Dict[str, Any]],
        weather_scenario: str,
        farm_data: Dict[str, Any],
        time_horizon_months: int
    ) -> float:
        """Calculate expected yield impact for scenario."""
        try:
            base_impact = sum(p["yield_impact_percent"] for p in practice_combination)
            
            # Adjust for weather scenario
            weather_adjustments = {
                WeatherScenario.NORMAL: 0.0,
                WeatherScenario.DROUGHT: -5.0,  # Additional yield loss in drought
                WeatherScenario.WET: 2.0,        # Slight yield increase in wet conditions
                WeatherScenario.EXTREME_DROUGHT: -10.0,
                WeatherScenario.VARIABLE: -2.0
            }
            
            weather_adjustment = weather_adjustments.get(weather_scenario, 0.0)
            
            # Adjust for practice interactions
            if len(practice_combination) > 1:
                # Multiple practices may have cumulative effects
                interaction_adjustment = len(practice_combination) * 0.5
                base_impact += interaction_adjustment
            
            # Adjust for time horizon (practices may improve over time)
            time_adjustment = min(time_horizon_months * 0.1, 5.0)  # Up to 5% improvement over time
            
            total_impact = base_impact + weather_adjustment + time_adjustment
            
            return round(total_impact, 1)
            
        except Exception as e:
            logger.error(f"Error calculating yield impact: {str(e)}")
            return 0.0
    
    async def _calculate_scenario_cost(
        self,
        practice_combination: List[Dict[str, Any]],
        farm_data: Dict[str, Any],
        time_horizon_months: int
    ) -> Decimal:
        """Calculate implementation cost for scenario."""
        try:
            total_acres = farm_data["total_acres"]
            
            # Calculate implementation costs
            implementation_costs = []
            annual_costs = []
            
            for practice in practice_combination:
                impl_cost = practice["implementation_cost_per_acre"] * Decimal(str(total_acres))
                annual_cost = practice["annual_maintenance_cost"] * Decimal(str(total_acres))
                
                implementation_costs.append(impl_cost)
                annual_costs.append(annual_cost)
            
            total_implementation_cost = sum(implementation_costs)
            
            # Calculate total annual costs over time horizon
            years = time_horizon_months / 12.0
            total_annual_costs = sum(annual_costs) * Decimal(str(years))
            
            total_cost = total_implementation_cost + total_annual_costs
            
            return total_cost
            
        except Exception as e:
            logger.error(f"Error calculating scenario cost: {str(e)}")
            return Decimal("0.00")
    
    async def _calculate_scenario_net_benefit(
        self,
        practice_combination: List[Dict[str, Any]],
        water_savings: Decimal,
        yield_impact: float,
        implementation_cost: Decimal,
        farm_data: Dict[str, Any],
        time_horizon_months: int
    ) -> Decimal:
        """Calculate net benefit for scenario."""
        try:
            # Calculate yield impact value
            historical_yields = farm_data["historical_yields"]
            avg_yield = sum(historical_yields.values()) / len(historical_yields)
            yield_value_per_bushel = Decimal("5.00")  # Simplified crop price
            
            yield_impact_value = Decimal(str(yield_impact)) * Decimal(str(avg_yield)) * yield_value_per_bushel * Decimal(str(farm_data["total_acres"]))
            
            # Calculate total benefits
            total_benefits = water_savings + yield_impact_value
            
            # Calculate net benefit
            net_benefit = total_benefits - implementation_cost
            
            return net_benefit
            
        except Exception as e:
            logger.error(f"Error calculating net benefit: {str(e)}")
            return Decimal("0.00")
    
    async def _calculate_scenario_risk_score(
        self,
        practice_combination: List[Dict[str, Any]],
        weather_scenario: str,
        farm_data: Dict[str, Any]
    ) -> float:
        """Calculate risk score for scenario."""
        try:
            base_risk = 5.0  # Default moderate risk
            
            # Adjust for weather scenario
            weather_risks = {
                WeatherScenario.NORMAL: 3.0,
                WeatherScenario.DROUGHT: 7.0,
                WeatherScenario.WET: 4.0,
                WeatherScenario.EXTREME_DROUGHT: 9.0,
                WeatherScenario.VARIABLE: 6.0
            }
            
            weather_risk = weather_risks.get(weather_scenario, 5.0)
            
            # Adjust for practice complexity
            complexity_risk = len(practice_combination) * 0.5
            
            # Adjust for practice risk levels
            practice_risks = []
            for practice in practice_combination:
                risk_level = practice["risk_level"]
                risk_scores = {
                    DroughtRiskLevel.LOW: 2.0,
                    DroughtRiskLevel.MODERATE: 5.0,
                    DroughtRiskLevel.HIGH: 7.0,
                    DroughtRiskLevel.SEVERE: 8.5,
                    DroughtRiskLevel.EXTREME: 10.0
                }
                practice_risks.append(risk_scores.get(risk_level, 5.0))
            
            avg_practice_risk = sum(practice_risks) / len(practice_risks) if practice_risks else 5.0
            
            # Calculate weighted risk score
            total_risk = (weather_risk * 0.4 + avg_practice_risk * 0.4 + complexity_risk * 0.2)
            
            return round(min(total_risk, 10.0), 1)
            
        except Exception as e:
            logger.error(f"Error calculating risk score: {str(e)}")
            return 5.0
    
    async def _calculate_success_probability(
        self,
        practice_combination: List[Dict[str, Any]],
        weather_scenario: str,
        risk_score: float
    ) -> float:
        """Calculate success probability for scenario."""
        try:
            base_probability = 0.8  # 80% base success rate
            
            # Adjust for weather scenario
            weather_probabilities = {
                WeatherScenario.NORMAL: 0.9,
                WeatherScenario.DROUGHT: 0.7,
                WeatherScenario.WET: 0.85,
                WeatherScenario.EXTREME_DROUGHT: 0.6,
                WeatherScenario.VARIABLE: 0.75
            }
            
            weather_probability = weather_probabilities.get(weather_scenario, 0.8)
            
            # Adjust for risk score
            risk_adjustment = (10.0 - risk_score) / 10.0
            
            # Adjust for practice complexity
            complexity_adjustment = max(0.5, 1.0 - (len(practice_combination) * 0.05))
            
            # Calculate final probability
            final_probability = base_probability * weather_probability * risk_adjustment * complexity_adjustment
            
            return round(max(0.1, min(final_probability, 0.95)), 2)  # Clamp between 10% and 95%
            
        except Exception as e:
            logger.error(f"Error calculating success probability: {str(e)}")
            return 0.7
    
    async def _perform_risk_assessment(self, scenarios_evaluated: List[ScenarioOutcome]) -> Dict[str, Any]:
        """Perform comprehensive risk assessment."""
        try:
            risk_assessment = {
                "overall_risk_level": "moderate",
                "risk_factors": [],
                "mitigation_strategies": [],
                "risk_distribution": {},
                "sensitivity_analysis": {}
            }
            
            # Analyze risk distribution
            risk_scores = [scenario.risk_score for scenario in scenarios_evaluated]
            avg_risk = sum(risk_scores) / len(risk_scores)
            
            if avg_risk >= 8.0:
                risk_assessment["overall_risk_level"] = "high"
            elif avg_risk >= 6.0:
                risk_assessment["overall_risk_level"] = "moderate"
            else:
                risk_assessment["overall_risk_level"] = "low"
            
            # Identify risk factors
            high_risk_scenarios = [s for s in scenarios_evaluated if s.risk_score >= 7.0]
            if high_risk_scenarios:
                risk_assessment["risk_factors"].append("High-risk weather scenarios identified")
                risk_assessment["risk_factors"].append("Complex practice combinations increase risk")
            
            # Generate mitigation strategies
            risk_assessment["mitigation_strategies"] = [
                "Implement practices gradually to reduce risk",
                "Monitor weather conditions closely",
                "Have contingency plans for extreme weather",
                "Consider insurance options for high-risk scenarios"
            ]
            
            # Risk distribution analysis
            risk_assessment["risk_distribution"] = {
                "low_risk_scenarios": len([s for s in scenarios_evaluated if s.risk_score < 5.0]),
                "moderate_risk_scenarios": len([s for s in scenarios_evaluated if 5.0 <= s.risk_score < 7.0]),
                "high_risk_scenarios": len([s for s in scenarios_evaluated if s.risk_score >= 7.0])
            }
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error performing risk assessment: {str(e)}")
            return {}
    
    async def _perform_economic_analysis(self, scenarios_evaluated: List[ScenarioOutcome]) -> Dict[str, Any]:
        """Perform comprehensive economic analysis."""
        try:
            economic_summary = {
                "total_scenarios_analyzed": len(scenarios_evaluated),
                "profitable_scenarios": 0,
                "break_even_scenarios": 0,
                "loss_scenarios": 0,
                "best_case_scenario": None,
                "worst_case_scenario": None,
                "average_net_benefit": 0.0,
                "roi_analysis": {},
                "payback_periods": []
            }
            
            # Categorize scenarios by profitability
            profitable_scenarios = []
            break_even_scenarios = []
            loss_scenarios = []
            
            for scenario in scenarios_evaluated:
                if scenario.net_benefit > Decimal("1000.00"):
                    profitable_scenarios.append(scenario)
                    economic_summary["profitable_scenarios"] += 1
                elif scenario.net_benefit >= Decimal("0.00"):
                    break_even_scenarios.append(scenario)
                    economic_summary["break_even_scenarios"] += 1
                else:
                    loss_scenarios.append(scenario)
                    economic_summary["loss_scenarios"] += 1
            
            # Find best and worst case scenarios
            if scenarios_evaluated:
                best_scenario = max(scenarios_evaluated, key=lambda x: x.net_benefit)
                worst_scenario = min(scenarios_evaluated, key=lambda x: x.net_benefit)
                
                economic_summary["best_case_scenario"] = {
                    "scenario_name": best_scenario.scenario_name,
                    "net_benefit": float(best_scenario.net_benefit),
                    "success_probability": best_scenario.success_probability
                }
                
                economic_summary["worst_case_scenario"] = {
                    "scenario_name": worst_scenario.scenario_name,
                    "net_benefit": float(worst_scenario.net_benefit),
                    "success_probability": worst_scenario.success_probability
                }
            
            # Calculate average net benefit
            if scenarios_evaluated:
                avg_benefit = sum(float(s.net_benefit) for s in scenarios_evaluated) / len(scenarios_evaluated)
                economic_summary["average_net_benefit"] = round(avg_benefit, 2)
            
            # ROI analysis
            economic_summary["roi_analysis"] = {
                "high_roi_scenarios": len([s for s in scenarios_evaluated if float(s.net_benefit) / float(s.implementation_cost) > 2.0]),
                "moderate_roi_scenarios": len([s for s in scenarios_evaluated if 1.0 <= float(s.net_benefit) / float(s.implementation_cost) <= 2.0]),
                "low_roi_scenarios": len([s for s in scenarios_evaluated if float(s.net_benefit) / float(s.implementation_cost) < 1.0])
            }
            
            return economic_summary
            
        except Exception as e:
            logger.error(f"Error performing economic analysis: {str(e)}")
            return {}
    
    async def _determine_recommended_scenario(
        self,
        scenarios_evaluated: List[ScenarioOutcome],
        include_economic: bool,
        include_risk: bool
    ) -> Tuple[Optional[str], str]:
        """Determine recommended scenario based on analysis."""
        try:
            if not scenarios_evaluated:
                return None, "No scenarios to evaluate"
            
            # Score scenarios based on criteria
            scored_scenarios = []
            for scenario in scenarios_evaluated:
                score = 0.0
                
                # Economic score (40% weight)
                if include_economic:
                    economic_score = float(scenario.net_benefit) / 10000.0  # Normalize to 0-1
                    score += economic_score * 0.4
                
                # Risk score (30% weight)
                if include_risk:
                    risk_score = (10.0 - scenario.risk_score) / 10.0  # Lower risk = higher score
                    score += risk_score * 0.3
                
                # Success probability (30% weight)
                success_score = scenario.success_probability
                score += success_score * 0.3
                
                scored_scenarios.append((scenario, score))
            
            # Sort by score
            scored_scenarios.sort(key=lambda x: x[1], reverse=True)
            recommended_scenario = scored_scenarios[0][0]
            
            # Generate recommendation reason
            reasons = []
            
            if include_economic and float(recommended_scenario.net_benefit) > 0:
                reasons.append("positive economic returns")
            
            if include_risk and recommended_scenario.risk_score <= 6.0:
                reasons.append("acceptable risk level")
            
            if recommended_scenario.success_probability >= 0.7:
                reasons.append("high success probability")
            
            if not reasons:
                reasons.append("best overall performance")
            
            reason_text = f"Recommended due to {', '.join(reasons)}"
            
            return recommended_scenario.scenario_name, reason_text
            
        except Exception as e:
            logger.error(f"Error determining recommended scenario: {str(e)}")
            return None, "Unable to determine recommendation"
    
    async def _generate_implementation_timeline(
        self,
        recommended_scenario: Optional[str],
        scenarios_evaluated: List[ScenarioOutcome],
        time_horizon_months: int
    ) -> List[Dict[str, Any]]:
        """Generate implementation timeline for recommended scenario."""
        try:
            timeline = []
            
            if not recommended_scenario:
                return timeline
            
            # Find the recommended scenario
            recommended_scenario_data = None
            for scenario in scenarios_evaluated:
                if scenario.scenario_name == recommended_scenario:
                    recommended_scenario_data = scenario
                    break
            
            if not recommended_scenario_data:
                return timeline
            
            # Generate timeline phases
            current_month = 0
            
            # Phase 1: Planning and Preparation (Months 1-2)
            timeline.append({
                "phase": "Planning and Preparation",
                "start_month": current_month + 1,
                "end_month": current_month + 2,
                "activities": [
                    "Conduct detailed field assessment",
                    "Finalize practice selection",
                    "Secure necessary permits",
                    "Order materials and equipment",
                    "Develop implementation schedule"
                ],
                "milestones": ["Field assessment complete", "Materials ordered"]
            })
            current_month += 2
            
            # Phase 2: Initial Implementation (Months 3-6)
            timeline.append({
                "phase": "Initial Implementation",
                "start_month": current_month + 1,
                "end_month": current_month + 4,
                "activities": [
                    "Begin practice implementation",
                    "Install monitoring systems",
                    "Train staff on new practices",
                    "Establish baseline measurements"
                ],
                "milestones": ["Implementation started", "Monitoring systems active"]
            })
            current_month += 4
            
            # Phase 3: Optimization and Adjustment (Months 7-12)
            timeline.append({
                "phase": "Optimization and Adjustment",
                "start_month": current_month + 1,
                "end_month": min(current_month + 6, time_horizon_months),
                "activities": [
                    "Monitor practice effectiveness",
                    "Adjust implementation as needed",
                    "Optimize resource allocation",
                    "Document lessons learned"
                ],
                "milestones": ["Optimization complete", "Documentation finished"]
            })
            
            # Phase 4: Long-term Management (if applicable)
            if time_horizon_months > 12:
                timeline.append({
                    "phase": "Long-term Management",
                    "start_month": 13,
                    "end_month": time_horizon_months,
                    "activities": [
                        "Maintain implemented practices",
                        "Continue monitoring and assessment",
                        "Plan for practice expansion",
                        "Evaluate long-term benefits"
                    ],
                    "milestones": ["Long-term assessment complete"]
                })
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error generating implementation timeline: {str(e)}")
            return []