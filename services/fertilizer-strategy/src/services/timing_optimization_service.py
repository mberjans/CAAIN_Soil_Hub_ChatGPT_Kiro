"""
Fertilizer Timing Optimization Service

This service provides comprehensive fertilizer timing optimization with weather integration,
crop growth stage analysis, and multi-objective optimization for optimal application timing.
"""

import asyncio
import logging
import time
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Any, Tuple
import statistics
import math

from ..models.timing_optimization_models import (
    TimingOptimizationRequest,
    TimingOptimizationResult,
    ApplicationTiming,
    SplitApplicationPlan,
    WeatherWindow,
    WeatherCondition,
    CropGrowthStage,
    ApplicationMethod,
    FertilizerType,
    TimingConstraint,
    EquipmentAvailability,
    LaborAvailability,
    TimingOptimizationSummary
)

# Import advanced optimization algorithms
from ..algorithms.dynamic_programming_optimizer import DynamicProgrammingOptimizer
from ..algorithms.genetic_algorithm_optimizer import GeneticAlgorithmOptimizer
from ..algorithms.ml_optimizer import MLOptimizer
from ..algorithms.multi_objective_optimizer import MultiObjectiveOptimizer
from ..algorithms.uncertainty_handler import UncertaintyHandler

logger = logging.getLogger(__name__)


class FertilizerTimingOptimizer:
    """
    Advanced fertilizer timing optimization service with weather integration.
    
    Features:
    - Optimal application timing based on crop growth stages
    - Weather-based timing adjustments and risk assessment
    - Split application optimization for risk reduction
    - Multi-objective optimization (yield, cost, risk)
    - Equipment and labor constraint integration
    - Soil condition and temperature considerations
    """
    
    def __init__(self):
        self.weather_service = None  # Will be integrated with weather service
        self.crop_growth_service = None  # Will be integrated with crop growth models
        self.equipment_service = None  # Will be integrated with equipment management

        # Initialize advanced optimization algorithms
        self.dp_optimizer = DynamicProgrammingOptimizer(
            discount_factor=0.98,
            max_horizon_days=365,
            state_discretization=10
        )

        self.ga_optimizer = GeneticAlgorithmOptimizer(
            population_size=100,
            max_generations=200,
            crossover_rate=0.8,
            mutation_rate=0.1,
            elitism_count=5
        )

        self.ml_optimizer = MLOptimizer(
            learning_rate=0.01,
            exploration_rate=0.1,
            discount_factor=0.95
        )

        self.mo_optimizer = MultiObjectiveOptimizer(
            population_size=100,
            max_generations=150,
            crossover_rate=0.9,
            mutation_rate=0.1
        )

        self.uncertainty_handler = UncertaintyHandler(
            num_scenarios=1000,
            confidence_level=0.95,
            risk_aversion=0.5
        )

        # Crop-specific timing parameters
        self.crop_timing_params = {
            "corn": {
                "critical_stages": [CropGrowthStage.V4, CropGrowthStage.V6, CropGrowthStage.VT],
                "nitrogen_timing": [CropGrowthStage.PLANTING, CropGrowthStage.V6],
                "phosphorus_timing": [CropGrowthStage.PLANTING],
                "potassium_timing": [CropGrowthStage.PLANTING, CropGrowthStage.V6],
                "temperature_threshold": 50.0,
                "soil_moisture_optimal": 0.6
            },
            "soybean": {
                "critical_stages": [CropGrowthStage.V2, CropGrowthStage.V4, CropGrowthStage.R1],
                "nitrogen_timing": [CropGrowthStage.PLANTING],
                "phosphorus_timing": [CropGrowthStage.PLANTING],
                "potassium_timing": [CropGrowthStage.PLANTING],
                "temperature_threshold": 45.0,
                "soil_moisture_optimal": 0.7
            },
            "wheat": {
                "critical_stages": [CropGrowthStage.EMERGENCE, CropGrowthStage.V4, CropGrowthStage.VT],
                "nitrogen_timing": [CropGrowthStage.PLANTING, CropGrowthStage.V4],
                "phosphorus_timing": [CropGrowthStage.PLANTING],
                "potassium_timing": [CropGrowthStage.PLANTING],
                "temperature_threshold": 40.0,
                "soil_moisture_optimal": 0.6
            }
        }
        
        # Weather condition scoring
        self.weather_scores = {
            WeatherCondition.OPTIMAL: 1.0,
            WeatherCondition.ACCEPTABLE: 0.8,
            WeatherCondition.MARGINAL: 0.6,
            WeatherCondition.POOR: 0.3,
            WeatherCondition.UNACCEPTABLE: 0.0
        }
    
    async def optimize_timing(self, request: TimingOptimizationRequest) -> TimingOptimizationResult:
        """
        Optimize fertilizer application timing with comprehensive analysis.
        
        Args:
            request: Timing optimization request with field and crop data
            
        Returns:
            TimingOptimizationResult with optimal timings and analysis
        """
        start_time = time.time()
        logger.info(f"Starting timing optimization for request {request.request_id}")
        
        try:
            # 1. Analyze weather windows
            weather_windows = await self._analyze_weather_windows(request)
            
            # 2. Determine crop growth stages
            crop_stages = await self._determine_crop_growth_stages(request)
            
            # 3. Generate optimal timings for each fertilizer
            optimal_timings = []
            for fertilizer_type, amount in request.fertilizer_requirements.items():
                timings = await self._optimize_fertilizer_timing(
                    fertilizer_type, amount, request, weather_windows, crop_stages
                )
                optimal_timings.extend(timings)
            
            # 4. Generate split application plans
            split_plans = await self._generate_split_plans(request, optimal_timings)
            
            # 5. Calculate optimization metrics
            metrics = await self._calculate_optimization_metrics(
                request, optimal_timings, weather_windows
            )
            
            # 6. Generate recommendations
            recommendations = await self._generate_recommendations(
                request, optimal_timings, split_plans, metrics
            )
            
            # 7. Calculate economic analysis
            economic_analysis = await self._calculate_economic_analysis(
                request, optimal_timings, split_plans
            )
            
            processing_time = (time.time() - start_time) * 1000
            
            result = TimingOptimizationResult(
                request_id=request.request_id,
                optimal_timings=optimal_timings,
                split_plans=split_plans,
                weather_windows=weather_windows,
                overall_timing_score=metrics["overall_score"],
                weather_suitability_score=metrics["weather_score"],
                crop_stage_alignment_score=metrics["crop_score"],
                risk_score=metrics["risk_score"],
                total_estimated_cost=economic_analysis["total_cost"],
                cost_per_acre=economic_analysis["cost_per_acre"],
                expected_yield_impact=economic_analysis["yield_impact"],
                roi_estimate=economic_analysis["roi"],
                recommendations=recommendations,
                confidence_score=metrics["confidence"],
                processing_time_ms=processing_time
            )
            
            logger.info(f"Timing optimization completed for request {request.request_id}")
            return result

        except Exception as e:
            logger.error(f"Error in timing optimization: {e}")
            raise

    async def optimize_with_advanced_algorithms(
        self,
        request: TimingOptimizationRequest,
        algorithm: str = "auto",
        historical_data: Optional[List[Dict[str, Any]]] = None
    ) -> TimingOptimizationResult:
        """
        Optimize fertilizer timing using advanced algorithms.

        Args:
            request: Timing optimization request
            algorithm: Algorithm to use ('dp', 'ga', 'ml', 'mo', 'auto')
            historical_data: Optional historical data for ML optimizer

        Returns:
            TimingOptimizationResult with optimal timings
        """
        start_time = time.time()
        logger.info(f"Starting advanced optimization with algorithm: {algorithm}")

        try:
            # Prepare common data
            weather_windows = await self._analyze_weather_windows(request)
            crop_stages = await self._determine_crop_growth_stages(request)

            # Select algorithm based on problem characteristics
            if algorithm == "auto":
                algorithm = self._select_optimal_algorithm(request, historical_data)
                logger.info(f"Auto-selected algorithm: {algorithm}")

            # Run optimization with selected algorithm
            if algorithm == "dp":
                result = await self._optimize_with_dp(request, weather_windows, crop_stages)
            elif algorithm == "ga":
                result = await self._optimize_with_ga(request, weather_windows, crop_stages)
            elif algorithm == "ml":
                result = await self._optimize_with_ml(request, weather_windows, crop_stages, historical_data)
            elif algorithm == "mo":
                result = await self._optimize_with_mo(request, weather_windows, crop_stages)
            else:
                # Fall back to default optimization
                logger.warning(f"Unknown algorithm '{algorithm}', using default")
                return await self.optimize_timing(request)

            # Add uncertainty analysis to result
            uncertainty_analysis = await self._add_uncertainty_analysis(
                result, request, weather_windows, crop_stages
            )

            # Update result with uncertainty metrics
            result.recommendations.extend(uncertainty_analysis.get("recommendations", []))

            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time

            logger.info(f"Advanced optimization completed in {processing_time:.2f}ms")
            return result

        except Exception as e:
            logger.error(f"Error in advanced optimization: {e}")
            raise

    def _select_optimal_algorithm(
        self,
        request: TimingOptimizationRequest,
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> str:
        """
        Select optimal algorithm based on problem characteristics.

        Decision criteria:
        - Use ML if sufficient historical data available
        - Use DP for smaller problems with clear state transitions
        - Use GA for medium-complexity problems
        - Use MO for explicit multi-objective requirements
        """
        # Check for historical data (ML preferred)
        if historical_data and len(historical_data) >= 50:
            return "ml"

        # Check problem size
        num_fertilizers = len(request.fertilizer_requirements)
        horizon_days = request.optimization_horizon_days

        # DP works well for smaller problems
        if num_fertilizers <= 2 and horizon_days <= 120:
            return "dp"

        # Use MO if explicit multi-objective preferences
        if request.prioritize_yield and request.prioritize_cost:
            return "mo"

        # Default to GA for general problems
        return "ga"

    async def _optimize_with_dp(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> TimingOptimizationResult:
        """Optimize using dynamic programming."""
        logger.info("Running DP optimization")

        # Run DP optimizer
        dp_result = self.dp_optimizer.optimize(request, weather_windows, crop_stages)

        # Convert DP result to standard format
        optimal_timings = []
        for app_date, action in dp_result.optimal_schedule:
            if action.apply:
                # Find best weather window for this date
                weather_window = await self._find_best_weather_window(
                    app_date, weather_windows, request
                )

                # Get crop stage for this date
                crop_stage = self._get_crop_stage_for_date(app_date, crop_stages)

                timing = ApplicationTiming(
                    fertilizer_type=action.fertilizer_type,
                    application_method=action.method,
                    recommended_date=app_date,
                    application_window=weather_window,
                    crop_stage=crop_stage,
                    amount_lbs_per_acre=action.amount,
                    timing_score=0.85,
                    weather_score=weather_window.suitability_score if weather_window else 0.5,
                    crop_score=0.90,
                    soil_score=0.85,
                    weather_risk=0.2,
                    timing_risk=0.15,
                    equipment_risk=0.1,
                    estimated_cost_per_acre=action.amount * 0.6,
                    yield_impact_percent=5.0
                )
                optimal_timings.append(timing)

        # Create result
        result = await self._create_result_from_timings(
            request, optimal_timings, weather_windows, "dynamic_programming",
            dp_result.confidence_score
        )

        return result

    async def _optimize_with_ga(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> TimingOptimizationResult:
        """Optimize using genetic algorithm."""
        logger.info("Running GA optimization")

        # Run GA optimizer
        ga_result = self.ga_optimizer.optimize(request, weather_windows, crop_stages)

        # Convert GA result to standard format
        optimal_timings = []
        for app_date, fertilizer_type, amount, method in ga_result.best_schedule.schedule:
            weather_window = await self._find_best_weather_window(
                app_date, weather_windows, request
            )
            crop_stage = self._get_crop_stage_for_date(app_date, crop_stages)

            timing = ApplicationTiming(
                fertilizer_type=fertilizer_type,
                application_method=method,
                recommended_date=app_date,
                application_window=weather_window,
                crop_stage=crop_stage,
                amount_lbs_per_acre=amount,
                timing_score=ga_result.best_schedule.fitness / 100.0,
                weather_score=weather_window.suitability_score if weather_window else 0.5,
                crop_score=0.88,
                soil_score=0.85,
                weather_risk=0.18,
                timing_risk=0.15,
                equipment_risk=0.12,
                estimated_cost_per_acre=amount * 0.6,
                yield_impact_percent=4.5
            )
            optimal_timings.append(timing)

        # Create result
        result = await self._create_result_from_timings(
            request, optimal_timings, weather_windows, "genetic_algorithm", 0.85
        )

        return result

    async def _optimize_with_ml(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage],
        historical_data: Optional[List[Dict[str, Any]]]
    ) -> TimingOptimizationResult:
        """Optimize using machine learning."""
        logger.info("Running ML optimization")

        # Run ML optimizer
        ml_result = self.ml_optimizer.optimize(
            request, weather_windows, crop_stages, historical_data
        )

        # Convert ML result to standard format
        optimal_timings = []
        for app_date, fertilizer_type, amount, method in ml_result.recommended_schedule:
            weather_window = await self._find_best_weather_window(
                app_date, weather_windows, request
            )
            crop_stage = self._get_crop_stage_for_date(app_date, crop_stages)

            timing = ApplicationTiming(
                fertilizer_type=fertilizer_type,
                application_method=method,
                recommended_date=app_date,
                application_window=weather_window,
                crop_stage=crop_stage,
                amount_lbs_per_acre=amount,
                timing_score=ml_result.model_confidence,
                weather_score=weather_window.suitability_score if weather_window else 0.5,
                crop_score=0.90,
                soil_score=0.87,
                weather_risk=0.15,
                timing_risk=0.12,
                equipment_risk=0.10,
                estimated_cost_per_acre=amount * 0.6,
                yield_impact_percent=ml_result.predicted_yield / 40.0
            )
            optimal_timings.append(timing)

        # Create result
        result = await self._create_result_from_timings(
            request, optimal_timings, weather_windows, "machine_learning",
            ml_result.model_confidence
        )

        return result

    async def _optimize_with_mo(
        self,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> TimingOptimizationResult:
        """Optimize using multi-objective optimization."""
        logger.info("Running MO optimization")

        # Set preference weights based on request
        preference_weights = {
            "yield": 0.40 if request.prioritize_yield else 0.30,
            "cost": 0.30 if request.prioritize_cost else 0.20,
            "environment": 0.20,
            "risk": 0.10
        }

        # Run MO optimizer
        mo_result = self.mo_optimizer.optimize(
            request, weather_windows, crop_stages, preference_weights
        )

        # Convert MO result to standard format
        optimal_timings = []
        for app_date, fertilizer_type, amount, method in mo_result.recommended_solution.schedule:
            weather_window = await self._find_best_weather_window(
                app_date, weather_windows, request
            )
            crop_stage = self._get_crop_stage_for_date(app_date, crop_stages)

            timing = ApplicationTiming(
                fertilizer_type=fertilizer_type,
                application_method=method,
                recommended_date=app_date,
                application_window=weather_window,
                crop_stage=crop_stage,
                amount_lbs_per_acre=amount,
                timing_score=mo_result.recommended_solution.objectives.yield_score / 100.0,
                weather_score=weather_window.suitability_score if weather_window else 0.5,
                crop_score=0.89,
                soil_score=0.86,
                weather_risk=0.16,
                timing_risk=0.14,
                equipment_risk=0.11,
                estimated_cost_per_acre=amount * 0.6,
                yield_impact_percent=4.8
            )
            optimal_timings.append(timing)

        # Create result
        result = await self._create_result_from_timings(
            request, optimal_timings, weather_windows, "multi_objective", 0.88
        )

        return result

    async def _add_uncertainty_analysis(
        self,
        result: TimingOptimizationResult,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> Dict[str, Any]:
        """Add uncertainty analysis to optimization result."""
        logger.info("Adding uncertainty analysis")

        # Extract schedule from result
        schedule = []
        for timing in result.optimal_timings:
            schedule.append((
                timing.recommended_date,
                timing.fertilizer_type,
                timing.amount_lbs_per_acre,
                timing.application_method
            ))

        # Run uncertainty analysis
        uncertainty_result = self.uncertainty_handler.analyze_uncertainty(
            request, schedule, weather_windows, crop_stages
        )

        # Generate uncertainty-based recommendations
        recommendations = []

        # Check risk metrics
        if uncertainty_result.risk_metrics["value_at_risk_5"] < 50:
            recommendations.append(
                "High downside risk detected. Consider more conservative timing strategy."
            )

        if uncertainty_result.risk_metrics["volatility"] > 20:
            recommendations.append(
                "High outcome volatility. Implement risk mitigation strategies."
            )

        # Check confidence intervals
        for metric, outcome in uncertainty_result.confidence_intervals.items():
            if outcome.probability_success < 0.7:
                recommendations.append(
                    f"Low success probability for {metric}. Consider alternative timing."
                )

        return {
            "recommendations": recommendations,
            "risk_metrics": uncertainty_result.risk_metrics,
            "confidence_intervals": uncertainty_result.confidence_intervals
        }

    async def _create_result_from_timings(
        self,
        request: TimingOptimizationRequest,
        timings: List[ApplicationTiming],
        weather_windows: List[WeatherWindow],
        method: str,
        confidence: float
    ) -> TimingOptimizationResult:
        """Create TimingOptimizationResult from timings."""
        # Generate split plans
        split_plans = await self._generate_split_plans(request, timings)

        # Calculate metrics
        metrics = await self._calculate_optimization_metrics(request, timings, weather_windows)

        # Generate recommendations
        recommendations = await self._generate_recommendations(
            request, timings, split_plans, metrics
        )

        # Calculate economic analysis
        economic_analysis = await self._calculate_economic_analysis(
            request, timings, split_plans
        )

        result = TimingOptimizationResult(
            request_id=request.request_id,
            optimal_timings=timings,
            split_plans=split_plans,
            weather_windows=weather_windows,
            overall_timing_score=metrics["overall_score"],
            weather_suitability_score=metrics["weather_score"],
            crop_stage_alignment_score=metrics["crop_score"],
            risk_score=metrics["risk_score"],
            total_estimated_cost=economic_analysis["total_cost"],
            cost_per_acre=economic_analysis["cost_per_acre"],
            expected_yield_impact=economic_analysis["yield_impact"],
            roi_estimate=economic_analysis["roi"],
            recommendations=recommendations,
            optimization_method=method,
            confidence_score=confidence,
            processing_time_ms=0.0
        )

        return result

    def _get_crop_stage_for_date(
        self,
        target_date: date,
        crop_stages: Dict[date, CropGrowthStage]
    ) -> CropGrowthStage:
        """Get crop growth stage for a specific date."""
        closest_stage = CropGrowthStage.PLANTING
        min_diff = float('inf')

        for stage_date, stage in crop_stages.items():
            diff = abs((target_date - stage_date).days)
            if diff < min_diff:
                min_diff = diff
                closest_stage = stage

        return closest_stage
    
    async def _analyze_weather_windows(
        self, request: TimingOptimizationRequest
    ) -> List[WeatherWindow]:
        """Analyze available weather windows for application."""
        logger.info("Analyzing weather windows")
        
        # For now, generate mock weather windows
        # In production, this would integrate with weather service
        weather_windows = []
        
        start_date = request.planting_date
        end_date = start_date + timedelta(days=request.optimization_horizon_days)
        
        current_date = start_date
        while current_date <= end_date:
            # Generate weather conditions for each day
            weather_condition = await self._assess_weather_condition(current_date, request)
            
            if weather_condition != WeatherCondition.UNACCEPTABLE:
                window = WeatherWindow(
                    start_date=current_date,
                    end_date=current_date,
                    condition=weather_condition,
                    temperature_f=await self._get_temperature(current_date, request),
                    precipitation_probability=await self._get_precipitation_probability(current_date, request),
                    wind_speed_mph=await self._get_wind_speed(current_date, request),
                    soil_moisture=await self._get_soil_moisture(current_date, request),
                    suitability_score=self.weather_scores[weather_condition]
                )
                weather_windows.append(window)
            
            current_date += timedelta(days=1)
        
        return weather_windows
    
    async def _determine_crop_growth_stages(
        self, request: TimingOptimizationRequest
    ) -> Dict[date, CropGrowthStage]:
        """Determine crop growth stages based on planting date."""
        logger.info("Determining crop growth stages")
        
        crop_params = self.crop_timing_params.get(request.crop_type.lower(), {})
        growth_stages = {}
        
        # Calculate growth stage dates based on crop type and planting date
        planting_date = request.planting_date
        
        if request.crop_type.lower() == "corn":
            growth_stages[planting_date] = CropGrowthStage.PLANTING
            growth_stages[planting_date + timedelta(days=7)] = CropGrowthStage.EMERGENCE
            growth_stages[planting_date + timedelta(days=14)] = CropGrowthStage.V2
            growth_stages[planting_date + timedelta(days=21)] = CropGrowthStage.V4
            growth_stages[planting_date + timedelta(days=28)] = CropGrowthStage.V6
            growth_stages[planting_date + timedelta(days=35)] = CropGrowthStage.V8
            growth_stages[planting_date + timedelta(days=42)] = CropGrowthStage.V10
            growth_stages[planting_date + timedelta(days=49)] = CropGrowthStage.V12
            growth_stages[planting_date + timedelta(days=56)] = CropGrowthStage.VT
            growth_stages[planting_date + timedelta(days=63)] = CropGrowthStage.R1
            growth_stages[planting_date + timedelta(days=70)] = CropGrowthStage.R2
            growth_stages[planting_date + timedelta(days=77)] = CropGrowthStage.R3
            growth_stages[planting_date + timedelta(days=84)] = CropGrowthStage.R4
            growth_stages[planting_date + timedelta(days=91)] = CropGrowthStage.R5
            growth_stages[planting_date + timedelta(days=98)] = CropGrowthStage.R6
            growth_stages[planting_date + timedelta(days=105)] = CropGrowthStage.HARVEST
        
        elif request.crop_type.lower() == "soybean":
            growth_stages[planting_date] = CropGrowthStage.PLANTING
            growth_stages[planting_date + timedelta(days=5)] = CropGrowthStage.EMERGENCE
            growth_stages[planting_date + timedelta(days=10)] = CropGrowthStage.V2
            growth_stages[planting_date + timedelta(days=15)] = CropGrowthStage.V4
            growth_stages[planting_date + timedelta(days=20)] = CropGrowthStage.V6
            growth_stages[planting_date + timedelta(days=25)] = CropGrowthStage.V8
            growth_stages[planting_date + timedelta(days=30)] = CropGrowthStage.V10
            growth_stages[planting_date + timedelta(days=35)] = CropGrowthStage.V12
            growth_stages[planting_date + timedelta(days=40)] = CropGrowthStage.VT
            growth_stages[planting_date + timedelta(days=45)] = CropGrowthStage.R1
            growth_stages[planting_date + timedelta(days=50)] = CropGrowthStage.R2
            growth_stages[planting_date + timedelta(days=55)] = CropGrowthStage.R3
            growth_stages[planting_date + timedelta(days=60)] = CropGrowthStage.R4
            growth_stages[planting_date + timedelta(days=65)] = CropGrowthStage.R5
            growth_stages[planting_date + timedelta(days=70)] = CropGrowthStage.R6
            growth_stages[planting_date + timedelta(days=75)] = CropGrowthStage.HARVEST
        
        return growth_stages
    
    async def _optimize_fertilizer_timing(
        self,
        fertilizer_type: str,
        amount: float,
        request: TimingOptimizationRequest,
        weather_windows: List[WeatherWindow],
        crop_stages: Dict[date, CropGrowthStage]
    ) -> List[ApplicationTiming]:
        """Optimize timing for a specific fertilizer type."""
        logger.info(f"Optimizing timing for {fertilizer_type}")
        
        crop_params = self.crop_timing_params.get(request.crop_type.lower(), {})
        optimal_stages = crop_params.get(f"{fertilizer_type.lower()}_timing", [])
        
        timings = []
        
        for stage in optimal_stages:
            # Find the date for this growth stage
            stage_date = None
            for date, stage_name in crop_stages.items():
                if stage_name == stage:
                    stage_date = date
                    break
            
            if stage_date:
                # Find best weather window around this date
                best_window = await self._find_best_weather_window(
                    stage_date, weather_windows, request
                )
                
                if best_window:
                    timing = ApplicationTiming(
                        fertilizer_type=fertilizer_type,
                        application_method=request.application_methods[0],  # Use first preferred method
                        recommended_date=best_window.start_date,
                        application_window=best_window,
                        crop_stage=stage,
                        amount_lbs_per_acre=amount,
                        timing_score=await self._calculate_timing_score(
                            stage_date, best_window, request
                        ),
                        weather_score=best_window.suitability_score,
                        crop_score=await self._calculate_crop_stage_score(stage, request),
                        soil_score=await self._calculate_soil_score(best_window, request),
                        weather_risk=await self._calculate_weather_risk(best_window),
                        timing_risk=await self._calculate_timing_risk(stage_date, request),
                        equipment_risk=await self._calculate_equipment_risk(best_window.start_date, request),
                        estimated_cost_per_acre=await self._calculate_application_cost(
                            fertilizer_type, amount, request
                        ),
                        yield_impact_percent=await self._calculate_yield_impact(
                            fertilizer_type, stage, request
                        )
                    )
                    timings.append(timing)
        
        return timings
    
    async def _generate_split_plans(
        self,
        request: TimingOptimizationRequest,
        timings: List[ApplicationTiming]
    ) -> List[SplitApplicationPlan]:
        """Generate split application plans for risk reduction."""
        logger.info("Generating split application plans")
        
        split_plans = []
        
        for fertilizer_type, total_amount in request.fertilizer_requirements.items():
            if request.split_application_allowed and total_amount > 50:  # Split if amount > 50 lbs/acre
                # Create 2-3 split applications
                num_splits = min(3, max(2, int(total_amount / 30)))  # Adaptive splitting
                
                fertilizer_timings = [t for t in timings if t.fertilizer_type == fertilizer_type]
                
                if len(fertilizer_timings) >= num_splits:
                    # Distribute amount across splits
                    split_amounts = [total_amount / num_splits] * num_splits
                    
                    # Adjust for optimal distribution (e.g., more N early for corn)
                    if fertilizer_type.lower() == "nitrogen" and request.crop_type.lower() == "corn":
                        split_amounts[0] = total_amount * 0.6  # 60% early
                        split_amounts[1] = total_amount * 0.4  # 40% later
                    
                    applications = []
                    for i, timing in enumerate(fertilizer_timings[:num_splits]):
                        timing.amount_lbs_per_acre = split_amounts[i]
                        applications.append(timing)
                    
                    split_plan = SplitApplicationPlan(
                        fertilizer_type=fertilizer_type,
                        total_amount_lbs_per_acre=total_amount,
                        applications=applications,
                        split_ratio=[amount / total_amount for amount in split_amounts],
                        total_timing_score=statistics.mean([t.timing_score for t in applications]),
                        risk_reduction_percent=20.0,  # Estimate 20% risk reduction
                        cost_impact_percent=5.0  # Estimate 5% cost increase
                    )
                    split_plans.append(split_plan)
        
        return split_plans
    
    async def _calculate_optimization_metrics(
        self,
        request: TimingOptimizationRequest,
        timings: List[ApplicationTiming],
        weather_windows: List[WeatherWindow]
    ) -> Dict[str, float]:
        """Calculate optimization metrics."""
        logger.info("Calculating optimization metrics")
        
        if not timings:
            return {
                "overall_score": 0.0,
                "weather_score": 0.0,
                "crop_score": 0.0,
                "risk_score": 0.0,
                "confidence": 0.0
            }
        
        # Calculate weighted scores
        weather_scores = [t.weather_score for t in timings]
        crop_scores = [t.crop_score for t in timings]
        timing_scores = [t.timing_score for t in timings]
        risk_scores = [min(1.0, t.weather_risk + t.timing_risk + t.equipment_risk) for t in timings]
        
        overall_score = statistics.mean(timing_scores)
        weather_score = statistics.mean(weather_scores)
        crop_score = statistics.mean(crop_scores)
        risk_score = statistics.mean(risk_scores)
        
        # Calculate confidence based on data quality and consistency
        confidence = min(0.95, max(0.5, overall_score * 0.8 + weather_score * 0.2))
        
        return {
            "overall_score": overall_score,
            "weather_score": weather_score,
            "crop_score": crop_score,
            "risk_score": risk_score,
            "confidence": confidence
        }
    
    async def _generate_recommendations(
        self,
        request: TimingOptimizationRequest,
        timings: List[ApplicationTiming],
        split_plans: List[SplitApplicationPlan],
        metrics: Dict[str, float]
    ) -> List[str]:
        """Generate timing recommendations."""
        logger.info("Generating recommendations")
        
        recommendations = []
        
        # Overall timing recommendations
        if metrics["overall_score"] > 0.8:
            recommendations.append("Excellent timing optimization achieved with high confidence")
        elif metrics["overall_score"] > 0.6:
            recommendations.append("Good timing optimization with acceptable risk levels")
        else:
            recommendations.append("Consider alternative timing strategies due to constraints")
        
        # Weather-based recommendations
        if metrics["weather_score"] < 0.6:
            recommendations.append("Monitor weather forecasts closely for optimal application windows")
            recommendations.append("Consider flexible application scheduling to accommodate weather changes")
        
        # Risk mitigation recommendations
        if metrics["risk_score"] > 0.6:
            recommendations.append("High risk detected - implement risk mitigation strategies")
            recommendations.append("Consider split applications to reduce timing risk")
        
        # Split application recommendations
        if split_plans:
            recommendations.append("Split applications recommended for risk reduction")
            recommendations.append("Consider equipment availability for multiple application passes")
        
        # Crop-specific recommendations
        crop_params = self.crop_timing_params.get(request.crop_type.lower(), {})
        if crop_params:
            recommendations.append(f"Follow {request.crop_type} growth stage timing for optimal results")
        
        return recommendations
    
    async def _calculate_economic_analysis(
        self,
        request: TimingOptimizationRequest,
        timings: List[ApplicationTiming],
        split_plans: List[SplitApplicationPlan]
    ) -> Dict[str, float]:
        """Calculate economic analysis for timing optimization."""
        logger.info("Calculating economic analysis")
        
        total_cost = sum(t.estimated_cost_per_acre for t in timings)
        cost_per_acre = total_cost
        
        # Calculate yield impact
        yield_impact = sum(t.yield_impact_percent for t in timings)
        
        # Estimate ROI (simplified calculation)
        # In production, this would integrate with yield and price models
        estimated_yield_value = 1000.0  # $/acre (placeholder)
        roi = (yield_impact / 100 * estimated_yield_value - total_cost) / total_cost if total_cost > 0 else 0
        
        return {
            "total_cost": total_cost,
            "cost_per_acre": cost_per_acre,
            "yield_impact": yield_impact,
            "roi": roi
        }
    
    # Helper methods for weather and condition assessment
    async def _assess_weather_condition(
        self, target_date: date, request: TimingOptimizationRequest
    ) -> WeatherCondition:
        """Assess weather condition for application on target date."""
        # Mock weather assessment - in production, integrate with weather service
        import random
        
        # Simulate weather conditions based on season and location
        month = target_date.month
        
        if month in [3, 4, 5]:  # Spring
            conditions = [WeatherCondition.OPTIMAL, WeatherCondition.ACCEPTABLE, WeatherCondition.MARGINAL]
            weights = [0.4, 0.4, 0.2]
        elif month in [6, 7, 8]:  # Summer
            conditions = [WeatherCondition.OPTIMAL, WeatherCondition.ACCEPTABLE, WeatherCondition.MARGINAL, WeatherCondition.POOR]
            weights = [0.3, 0.3, 0.2, 0.2]
        else:  # Fall/Winter
            conditions = [WeatherCondition.ACCEPTABLE, WeatherCondition.MARGINAL, WeatherCondition.POOR, WeatherCondition.UNACCEPTABLE]
            weights = [0.2, 0.3, 0.3, 0.2]
        
        return random.choices(conditions, weights=weights)[0]
    
    async def _get_temperature(self, target_date: date, request: TimingOptimizationRequest) -> float:
        """Get temperature for target date."""
        # Mock temperature - in production, integrate with weather service
        import random
        
        month = target_date.month
        base_temp = 50 if month in [3, 4, 5] else 70 if month in [6, 7, 8] else 40
        return base_temp + random.uniform(-10, 10)
    
    async def _get_precipitation_probability(
        self, target_date: date, request: TimingOptimizationRequest
    ) -> float:
        """Get precipitation probability for target date."""
        # Mock precipitation probability - in production, integrate with weather service
        import random
        
        month = target_date.month
        base_prob = 0.3 if month in [3, 4, 5] else 0.4 if month in [6, 7, 8] else 0.2
        return base_prob + random.uniform(-0.1, 0.1)
    
    async def _get_wind_speed(self, target_date: date, request: TimingOptimizationRequest) -> float:
        """Get wind speed for target date."""
        # Mock wind speed - in production, integrate with weather service
        import random
        return random.uniform(5, 15)
    
    async def _get_soil_moisture(self, target_date: date, request: TimingOptimizationRequest) -> float:
        """Get soil moisture for target date."""
        # Mock soil moisture - in production, integrate with soil moisture models
        import random
        return request.soil_moisture_capacity + random.uniform(-0.2, 0.2)
    
    async def _find_best_weather_window(
        self,
        target_date: date,
        weather_windows: List[WeatherWindow],
        request: TimingOptimizationRequest
    ) -> Optional[WeatherWindow]:
        """Find the best weather window around target date."""
        # Find windows within 7 days of target date
        acceptable_windows = []
        
        for window in weather_windows:
            days_diff = abs((window.start_date - target_date).days)
            if days_diff <= 7:  # Within 7 days
                acceptable_windows.append((window, days_diff))
        
        if not acceptable_windows:
            return None
        
        # Sort by suitability score and proximity
        acceptable_windows.sort(key=lambda x: (x[0].suitability_score, -x[1]), reverse=True)
        
        return acceptable_windows[0][0]
    
    async def _calculate_timing_score(
        self, target_date: date, weather_window: WeatherWindow, request: TimingOptimizationRequest
    ) -> float:
        """Calculate timing optimization score."""
        # Base score from weather suitability
        score = weather_window.suitability_score
        
        # Adjust for proximity to optimal date
        days_diff = abs((weather_window.start_date - target_date).days)
        proximity_factor = max(0.5, 1.0 - (days_diff / 14.0))  # Decrease score for distant dates
        
        return score * proximity_factor
    
    async def _calculate_crop_stage_score(
        self, crop_stage: CropGrowthStage, request: TimingOptimizationRequest
    ) -> float:
        """Calculate crop stage suitability score."""
        crop_params = self.crop_timing_params.get(request.crop_type.lower(), {})
        critical_stages = crop_params.get("critical_stages", [])
        
        if crop_stage in critical_stages:
            return 1.0
        else:
            return 0.8
    
    async def _calculate_soil_score(
        self, weather_window: WeatherWindow, request: TimingOptimizationRequest
    ) -> float:
        """Calculate soil condition score."""
        # Score based on soil moisture and temperature
        moisture_score = 1.0 - abs(weather_window.soil_moisture - 0.6)  # Optimal around 0.6
        temp_score = 1.0 if weather_window.temperature_f >= request.soil_temperature_threshold else 0.5
        
        return (moisture_score + temp_score) / 2
    
    async def _calculate_weather_risk(self, weather_window: WeatherWindow) -> float:
        """Calculate weather-related risk."""
        # Risk increases with precipitation probability and decreases with suitability
        precip_risk = weather_window.precipitation_probability
        suitability_risk = 1.0 - weather_window.suitability_score
        
        return (precip_risk + suitability_risk) / 2
    
    async def _calculate_timing_risk(self, target_date: date, request: TimingOptimizationRequest) -> float:
        """Calculate timing-related risk."""
        # Risk based on optimization horizon and risk tolerance
        horizon_risk = min(0.5, request.optimization_horizon_days / 365.0)
        tolerance_risk = 1.0 - request.risk_tolerance
        
        return (horizon_risk + tolerance_risk) / 2
    
    async def _calculate_equipment_risk(self, target_date: date, request: TimingOptimizationRequest) -> float:
        """Calculate equipment availability risk."""
        # Check if equipment is available on target date
        equipment_available = False
        for equipment_type, available_dates in request.equipment_availability.items():
            if target_date in available_dates:
                equipment_available = True
                break
        
        return 0.2 if equipment_available else 0.8
    
    async def _calculate_application_cost(
        self, fertilizer_type: str, amount: float, request: TimingOptimizationRequest
    ) -> float:
        """Calculate application cost per acre."""
        # Mock cost calculation - in production, integrate with price service
        base_costs = {
            "nitrogen": 0.5,  # $/lb
            "phosphorus": 0.8,
            "potassium": 0.6,
            "complete": 0.7
        }
        
        base_cost = base_costs.get(fertilizer_type.lower(), 0.6)
        return amount * base_cost
    
    async def _calculate_yield_impact(
        self, fertilizer_type: str, crop_stage: CropGrowthStage, request: TimingOptimizationRequest
    ) -> float:
        """Calculate expected yield impact percentage."""
        # Mock yield impact calculation - in production, integrate with yield models
        crop_params = self.crop_timing_params.get(request.crop_type.lower(), {})
        critical_stages = crop_params.get("critical_stages", [])
        
        if crop_stage in critical_stages:
            return 5.0  # 5% yield increase for optimal timing
        else:
            return 2.0  # 2% yield increase for suboptimal timing