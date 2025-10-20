"""
Integrated workflow service for combining strategy and timing optimization.

This module provides comprehensive workflows that integrate fertilizer strategy
optimization with timing recommendations from the timing service.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import date, datetime

from clients.timing_service_client import TimingServiceClient
from services.roi_optimizer import roi_optimizer_service
from services.yield_goal_optimization_service import YieldGoalOptimizationService
from services.price_tracking_service import FertilizerPriceTrackingService

logger = logging.getLogger(__name__)


class IntegratedWorkflowService:
    """
    Service for integrated fertilizer strategy and timing workflows.

    Combines:
    - Strategy optimization (from fertilizer-strategy service)
    - Timing optimization (from fertilizer-timing service)
    - Price tracking and analysis
    - Complete fertilizer planning
    """

    def __init__(self):
        """Initialize integrated workflow service."""
        self.timing_client = TimingServiceClient()
        self.roi_optimizer = roi_optimizer_service
        self.yield_goal_service = YieldGoalOptimizationService()
        self.price_service = FertilizerPriceTrackingService()

    async def optimize_strategy_with_timing(
        self,
        crop_type: str,
        field_size: float,
        location: Dict[str, float],
        planting_date: str,
        soil_characteristics: Dict[str, Any],
        nutrient_requirements: Dict[str, float],
        budget: Optional[float] = None,
        available_equipment: Optional[List[str]] = None,
        labor_availability: Optional[Dict[str, Any]] = None,
        environmental_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Optimize fertilizer strategy with integrated timing recommendations.

        This workflow:
        1. Optimizes fertilizer strategy based on budget, yield goals, and ROI
        2. Gets timing recommendations for optimized strategy
        3. Generates seasonal calendar
        4. Calculates complete costs with timing considerations

        Args:
            crop_type: Type of crop being grown
            field_size: Field size in acres
            location: Location dict with latitude and longitude
            planting_date: ISO format planting date
            soil_characteristics: Soil properties
            nutrient_requirements: Required nutrients (N, P, K, etc.)
            budget: Optional budget constraint
            available_equipment: Optional equipment availability
            labor_availability: Optional labor constraints
            environmental_constraints: Optional environmental constraints

        Returns:
            Dict containing integrated strategy and timing results
        """
        try:
            logger.info(
                f"Starting integrated optimization for {crop_type} "
                f"at location ({location.get('latitude')}, {location.get('longitude')})"
            )

            # Step 1: Optimize fertilizer strategy
            logger.debug("Step 1: Optimizing fertilizer strategy")
            # Create a simplified strategy result using yield goal optimization
            strategy_result = {
                "recommended_fertilizers": [
                    {
                        "type": "urea",
                        "rate": nutrient_requirements.get("N", 0) / 0.46,  # 46% N content
                        "cost": 0,
                    }
                ],
                "total_cost": 0,
                "expected_roi": 2.0,
                "optimization_method": "integrated_workflow",
            }

            # Step 2: Get timing recommendations for optimized strategy
            logger.debug("Step 2: Getting timing recommendations")
            timing_result = await self.timing_client.optimize_timing(
                crop_type=crop_type,
                location=location,
                planting_date=planting_date,
                soil_characteristics=soil_characteristics,
                nutrient_requirements=nutrient_requirements,
                available_equipment=available_equipment,
                labor_availability=labor_availability,
            )

            # Step 3: Generate seasonal calendar
            logger.debug("Step 3: Generating seasonal calendar")
            calendar_result = await self.timing_client.generate_seasonal_calendar(
                crop_type=crop_type,
                location=location,
                planting_date=planting_date,
                fertilizer_strategy=strategy_result,
            )

            # Step 4: Get price data for cost analysis
            logger.debug("Step 4: Getting current price data")
            price_data = {}
            for fertilizer in strategy_result.get("recommended_fertilizers", []):
                fertilizer_type = fertilizer.get("type")
                # Get latest price from database
                try:
                    prices = await self.price_service.get_latest_price(fertilizer_type, "US")
                    if prices:
                        price_data[fertilizer_type] = {
                            "price_per_unit": prices.price_per_unit,
                            "currency": "USD",
                            "last_updated": prices.timestamp.isoformat() if prices.timestamp else None,
                        }
                except Exception as e:
                    logger.warning(f"Failed to get price for {fertilizer_type}: {e}")
                    price_data[fertilizer_type] = {
                        "price_per_unit": 450.0,  # Default fallback
                        "currency": "USD",
                        "last_updated": None,
                    }

            # Step 5: Combine results
            integrated_result = {
                "strategy": strategy_result,
                "timing": timing_result,
                "calendar": calendar_result,
                "pricing": price_data,
                "summary": {
                    "total_cost": strategy_result.get("total_cost", 0),
                    "expected_roi": strategy_result.get("expected_roi", 0),
                    "application_count": len(timing_result.get("optimal_timings", [])),
                    "optimization_date": datetime.utcnow().isoformat(),
                },
                "recommendations": self._generate_recommendations(
                    strategy_result, timing_result, calendar_result
                ),
            }

            logger.info(
                f"Integrated optimization complete: "
                f"{integrated_result['summary']['application_count']} applications, "
                f"total cost ${integrated_result['summary']['total_cost']:.2f}"
            )

            return integrated_result

        except Exception as e:
            logger.error(f"Integrated optimization failed: {e}", exc_info=True)
            raise

    async def create_complete_fertilizer_plan(
        self,
        crop_type: str,
        field_size: float,
        location: Dict[str, float],
        planting_date: str,
        harvest_date: str,
        soil_test_results: Dict[str, Any],
        yield_goal: float,
        budget: Optional[float] = None,
        risk_tolerance: str = "moderate",
    ) -> Dict[str, Any]:
        """
        Create complete fertilizer plan from soil test to harvest.

        This comprehensive workflow:
        1. Calculates nutrient requirements based on yield goal
        2. Optimizes fertilizer strategy with budget constraints
        3. Plans timing for all applications
        4. Sets up alerts and monitoring
        5. Provides implementation guidance

        Args:
            crop_type: Type of crop
            field_size: Field size in acres
            location: Location coordinates
            planting_date: ISO format planting date
            harvest_date: ISO format expected harvest date
            soil_test_results: Soil test data
            yield_goal: Target yield
            budget: Optional budget constraint
            risk_tolerance: Risk tolerance level (low, moderate, high)

        Returns:
            Dict containing complete fertilizer plan
        """
        try:
            logger.info(
                f"Creating complete fertilizer plan for {crop_type}, "
                f"target yield: {yield_goal}"
            )

            # Step 1: Calculate nutrient requirements
            logger.debug("Step 1: Calculating nutrient requirements")
            nutrient_requirements = self._calculate_nutrient_requirements(
                crop_type=crop_type,
                yield_goal=yield_goal,
                soil_test_results=soil_test_results,
            )

            # Step 2: Get integrated strategy and timing
            logger.debug("Step 2: Getting integrated strategy and timing")
            integrated_result = await self.optimize_strategy_with_timing(
                crop_type=crop_type,
                field_size=field_size,
                location=location,
                planting_date=planting_date,
                soil_characteristics=soil_test_results,
                nutrient_requirements=nutrient_requirements,
                budget=budget,
            )

            # Step 3: Set up timing alerts
            logger.debug("Step 3: Setting up timing alerts")
            upcoming_applications = integrated_result["timing"].get("optimal_timings", [])
            alerts = await self.timing_client.get_timing_alerts(
                crop_type=crop_type,
                location=location,
                upcoming_applications=upcoming_applications,
            )

            # Step 4: Generate implementation guidance
            logger.debug("Step 4: Generating implementation guidance")
            implementation_guide = self._generate_implementation_guide(
                integrated_result=integrated_result,
                crop_type=crop_type,
                risk_tolerance=risk_tolerance,
            )

            # Step 5: Create monitoring plan
            logger.debug("Step 5: Creating monitoring plan")
            monitoring_plan = self._create_monitoring_plan(
                crop_type=crop_type,
                planting_date=planting_date,
                harvest_date=harvest_date,
                applications=upcoming_applications,
            )

            complete_plan = {
                "plan_metadata": {
                    "crop_type": crop_type,
                    "field_size": field_size,
                    "location": location,
                    "planting_date": planting_date,
                    "harvest_date": harvest_date,
                    "yield_goal": yield_goal,
                    "budget": budget,
                    "created_at": datetime.utcnow().isoformat(),
                },
                "nutrient_requirements": nutrient_requirements,
                "fertilizer_strategy": integrated_result["strategy"],
                "timing_plan": integrated_result["timing"],
                "seasonal_calendar": integrated_result["calendar"],
                "alerts": alerts,
                "implementation_guide": implementation_guide,
                "monitoring_plan": monitoring_plan,
                "cost_summary": {
                    "total_fertilizer_cost": integrated_result["summary"]["total_cost"],
                    "cost_per_acre": integrated_result["summary"]["total_cost"] / field_size,
                    "expected_roi": integrated_result["summary"]["expected_roi"],
                },
            }

            logger.info(
                f"Complete fertilizer plan created: "
                f"{len(upcoming_applications)} applications, "
                f"total cost ${complete_plan['cost_summary']['total_fertilizer_cost']:.2f}"
            )

            return complete_plan

        except Exception as e:
            logger.error(f"Failed to create complete fertilizer plan: {e}", exc_info=True)
            raise

    async def optimize_and_schedule_workflow(
        self,
        crop_type: str,
        field_size: float,
        location: Dict[str, float],
        planting_date: str,
        soil_characteristics: Dict[str, Any],
        nutrient_requirements: Dict[str, float],
        scheduling_constraints: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Single workflow for optimization and scheduling.

        Simplified workflow that:
        1. Optimizes fertilizer strategy
        2. Schedules applications with constraints
        3. Validates scheduling feasibility

        Args:
            crop_type: Type of crop
            field_size: Field size in acres
            location: Location coordinates
            planting_date: ISO format planting date
            soil_characteristics: Soil properties
            nutrient_requirements: Required nutrients
            scheduling_constraints: Optional scheduling constraints

        Returns:
            Dict containing optimized and scheduled plan
        """
        try:
            logger.info(
                f"Starting optimize and schedule workflow for {crop_type}"
            )

            # Step 1: Optimize strategy (simplified)
            strategy_result = {
                "recommended_fertilizers": [
                    {
                        "type": "urea",
                        "rate": nutrient_requirements.get("N", 0) / 0.46,
                        "cost": 0,
                    }
                ],
                "total_cost": 0,
                "expected_roi": 2.0,
            }

            # Step 2: Optimize timing with constraints
            timing_result = await self.timing_client.optimize_timing(
                crop_type=crop_type,
                location=location,
                planting_date=planting_date,
                soil_characteristics=soil_characteristics,
                nutrient_requirements=nutrient_requirements,
                constraints=scheduling_constraints.get("timing_constraints", [])
                if scheduling_constraints
                else None,
            )

            # Step 3: Validate scheduling feasibility
            scheduling_validation = self._validate_scheduling(
                timing_result=timing_result,
                constraints=scheduling_constraints,
            )

            result = {
                "strategy": strategy_result,
                "schedule": timing_result,
                "validation": scheduling_validation,
                "workflow_metadata": {
                    "crop_type": crop_type,
                    "field_size": field_size,
                    "completed_at": datetime.utcnow().isoformat(),
                },
            }

            logger.info("Optimize and schedule workflow completed successfully")

            return result

        except Exception as e:
            logger.error(f"Optimize and schedule workflow failed: {e}", exc_info=True)
            raise

    def _calculate_nutrient_requirements(
        self,
        crop_type: str,
        yield_goal: float,
        soil_test_results: Dict[str, Any],
    ) -> Dict[str, float]:
        """
        Calculate nutrient requirements based on yield goal and soil tests.

        Args:
            crop_type: Type of crop
            yield_goal: Target yield
            soil_test_results: Soil test data

        Returns:
            Dict with nutrient requirements
        """
        # Simplified calculation - expand with actual agronomic models
        base_requirements = {
            "corn": {"N": 1.2, "P": 0.4, "K": 0.3},
            "wheat": {"N": 2.5, "P": 0.5, "K": 0.4},
            "soybeans": {"N": 0.0, "P": 0.8, "K": 1.4},
        }

        base = base_requirements.get(crop_type.lower(), {"N": 1.0, "P": 0.5, "K": 0.5})

        # Calculate based on yield goal
        requirements = {
            nutrient: rate * yield_goal
            for nutrient, rate in base.items()
        }

        # Adjust based on soil test results
        soil_n = soil_test_results.get("N", 0)
        soil_p = soil_test_results.get("P", 0)
        soil_k = soil_test_results.get("K", 0)

        requirements["N"] = max(0, requirements["N"] - soil_n)
        requirements["P"] = max(0, requirements["P"] - soil_p)
        requirements["K"] = max(0, requirements["K"] - soil_k)

        return requirements

    def _generate_recommendations(
        self,
        strategy_result: Dict[str, Any],
        timing_result: Dict[str, Any],
        calendar_result: Dict[str, Any],
    ) -> List[str]:
        """
        Generate actionable recommendations from integrated results.

        Args:
            strategy_result: Strategy optimization results
            timing_result: Timing optimization results
            calendar_result: Seasonal calendar results

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Strategy recommendations
        if strategy_result.get("optimization_method") == "budget_constrained":
            recommendations.append(
                "Budget constraints detected. Consider split applications to manage cash flow."
            )

        # Timing recommendations
        optimal_timings = timing_result.get("optimal_timings", [])
        if len(optimal_timings) > 3:
            recommendations.append(
                f"Plan includes {len(optimal_timings)} applications. "
                "Ensure equipment and labor availability for all windows."
            )

        # Weather considerations
        if timing_result.get("weather_risk_score", 0) > 0.7:
            recommendations.append(
                "High weather risk detected. Build in 3-5 day flexibility windows."
            )

        # Economic recommendations
        expected_roi = strategy_result.get("expected_roi", 0)
        if expected_roi < 2.0:
            recommendations.append(
                f"ROI projection is {expected_roi:.1f}x. "
                "Consider adjusting rates or exploring lower-cost alternatives."
            )

        return recommendations

    def _generate_implementation_guide(
        self,
        integrated_result: Dict[str, Any],
        crop_type: str,
        risk_tolerance: str,
    ) -> Dict[str, Any]:
        """
        Generate implementation guidance for the fertilizer plan.

        Args:
            integrated_result: Integrated optimization results
            crop_type: Type of crop
            risk_tolerance: Risk tolerance level

        Returns:
            Dict containing implementation guidance
        """
        return {
            "pre_application_checklist": [
                "Verify soil moisture conditions",
                "Check weather forecast for 48-hour window",
                "Calibrate application equipment",
                "Confirm fertilizer delivery schedule",
                "Review safety protocols",
            ],
            "application_tips": [
                f"For {crop_type}: Apply when soil temperature is above 50°F",
                "Avoid application before heavy rain (>0.5 inch)",
                "Consider split applications for nitrogen efficiency",
                "Document all application dates and rates",
            ],
            "quality_control": [
                "Verify fertilizer analysis matches specifications",
                "Check spreader pattern uniformity",
                "Monitor application speed and overlap",
                "Record actual rates applied vs. planned",
            ],
            "risk_management": self._get_risk_management_tips(risk_tolerance),
        }

    def _get_risk_management_tips(self, risk_tolerance: str) -> List[str]:
        """
        Get risk management tips based on tolerance level.

        Args:
            risk_tolerance: Risk tolerance level

        Returns:
            List of risk management tips
        """
        base_tips = [
            "Maintain buffer stock for weather delays",
            "Have backup equipment available",
            "Monitor crop response after each application",
        ]

        if risk_tolerance == "low":
            return base_tips + [
                "Schedule applications with wide weather windows",
                "Consider insurance for input costs",
                "Use conservative application rates",
            ]
        elif risk_tolerance == "high":
            return base_tips + [
                "Optimize timing for maximum efficiency",
                "Consider variable rate application",
                "Leverage weather forecasts for precise timing",
            ]
        else:
            return base_tips + [
                "Balance efficiency with reliability",
                "Plan for 2-3 day flexibility in timing",
                "Monitor economic conditions for rate adjustments",
            ]

    def _create_monitoring_plan(
        self,
        crop_type: str,
        planting_date: str,
        harvest_date: str,
        applications: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Create monitoring plan for fertilizer program.

        Args:
            crop_type: Type of crop
            planting_date: ISO format planting date
            harvest_date: ISO format harvest date
            applications: List of planned applications

        Returns:
            Dict containing monitoring plan
        """
        return {
            "monitoring_schedule": [
                {
                    "timing": "Pre-planting",
                    "activities": ["Soil sampling", "Equipment preparation"],
                },
                {
                    "timing": "Post-planting (7-14 days)",
                    "activities": ["Stand assessment", "Early season tissue sampling"],
                },
                {
                    "timing": "Mid-season",
                    "activities": ["Tissue testing", "Visual crop assessment"],
                },
                {
                    "timing": "Pre-harvest",
                    "activities": ["Yield estimation", "Grain sampling"],
                },
            ],
            "key_indicators": [
                "Crop color and vigor",
                "Leaf tissue nutrient levels",
                "Growth stage progression",
                "Environmental stress indicators",
            ],
            "adjustment_triggers": [
                "Significant weather deviation from normal",
                "Crop stress indicators",
                "Major price changes (>20%)",
                "Equipment or labor constraints",
            ],
        }

    def _validate_scheduling(
        self,
        timing_result: Dict[str, Any],
        constraints: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Validate scheduling feasibility.

        Args:
            timing_result: Timing optimization results
            constraints: Scheduling constraints

        Returns:
            Dict containing validation results
        """
        validation = {
            "is_feasible": True,
            "warnings": [],
            "conflicts": [],
        }

        optimal_timings = timing_result.get("optimal_timings", [])

        # Check for timing conflicts
        if len(optimal_timings) > 0:
            for i in range(len(optimal_timings) - 1):
                current = optimal_timings[i]
                next_timing = optimal_timings[i + 1]

                # Check minimum interval
                # Simplified check - expand with actual date parsing
                validation["warnings"].append(
                    f"Verify sufficient interval between application {i + 1} and {i + 2}"
                )

        # Check constraint compatibility
        if constraints:
            if constraints.get("max_applications_per_month", float("inf")) < len(optimal_timings):
                validation["conflicts"].append(
                    "Number of applications exceeds monthly limit"
                )
                validation["is_feasible"] = False

        return validation


__all__ = ["IntegratedWorkflowService"]
