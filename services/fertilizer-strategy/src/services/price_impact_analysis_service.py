"""
Advanced Price Impact Analysis Service for fertilizer strategy optimization.

This service provides comprehensive price impact analysis including:
- Sensitivity analysis for price changes
- Scenario modeling and planning
- Risk assessment and mitigation
- Profitability impact calculations
- Timing optimization recommendations
"""

import asyncio
import logging
import time
import statistics
# import numpy as np  # Not currently used
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from uuid import uuid4
import math

from ..models.price_impact_models import (
    PriceImpactAnalysisRequest, PriceImpactAnalysisResult, PriceImpactAnalysisResponse,
    PriceImpactMetrics, PriceImpactScenario, SensitivityAnalysisResult,
    RiskAssessmentResult, AnalysisType, ScenarioType, RiskLevel
)
from ..models.price_models import FertilizerPriceData, FertilizerProduct
from ..services.price_tracking_service import FertilizerPriceTrackingService
from ..services.commodity_price_service import CommodityPriceService
from ..database.fertilizer_price_db import FertilizerPriceRepository

logger = logging.getLogger(__name__)


class PriceImpactAnalysisService:
    """Advanced price impact analysis service for fertilizer strategy optimization."""
    
    def __init__(self):
        self.price_tracking_service = FertilizerPriceTrackingService()
        self.commodity_price_service = CommodityPriceService()
        # Note: price_repository will be initialized when needed with proper session
        
        # Analysis configuration
        self.default_scenarios = [
            ScenarioType.BASELINE,
            ScenarioType.OPTIMISTIC,
            ScenarioType.PESSIMISTIC,
            ScenarioType.VOLATILE
        ]
        
        self.default_sensitivity_ranges = [-50, -25, -10, -5, 0, 5, 10, 25, 50]  # Percentage changes
    
    async def analyze_price_impact(
        self,
        request: PriceImpactAnalysisRequest
    ) -> PriceImpactAnalysisResponse:
        """
        Perform comprehensive price impact analysis.
        
        Args:
            request: Price impact analysis request
            
        Returns:
            PriceImpactAnalysisResponse with analysis results
        """
        start_time = time.time()
        request_id = str(uuid4())
        
        try:
            logger.info(f"Starting price impact analysis: {request.analysis_id}")
            
            # Validate request
            await self._validate_request(request)
            
            # Get current market data
            market_data = await self._get_market_data(request)
            
            # Perform analysis based on type
            if request.analysis_type == AnalysisType.SENSITIVITY:
                result = await self._perform_sensitivity_analysis(request, market_data)
            elif request.analysis_type == AnalysisType.SCENARIO:
                result = await self._perform_scenario_analysis(request, market_data)
            elif request.analysis_type == AnalysisType.RISK_ASSESSMENT:
                result = await self._perform_risk_assessment(request, market_data)
            elif request.analysis_type == AnalysisType.PROFITABILITY_IMPACT:
                result = await self._perform_profitability_analysis(request, market_data)
            elif request.analysis_type == AnalysisType.TIMING_OPTIMIZATION:
                result = await self._perform_timing_optimization(request, market_data)
            else:
                # Comprehensive analysis
                result = await self._perform_comprehensive_analysis(request, market_data)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            
            # Create response
            response = PriceImpactAnalysisResponse(
                request_id=request_id,
                success=True,
                analysis_result=result,
                processing_time_ms=processing_time,
                data_sources_used=["fertilizer_prices", "commodity_prices", "market_data"]
            )
            
            logger.info(f"Price impact analysis completed: {request.analysis_id}")
            return response
            
        except Exception as e:
            logger.error(f"Price impact analysis failed: {e}")
            processing_time = (time.time() - start_time) * 1000
            
            return PriceImpactAnalysisResponse(
                request_id=request_id,
                success=False,
                error_message=str(e),
                error_code="ANALYSIS_FAILED",
                processing_time_ms=processing_time
            )
    
    async def _validate_request(self, request: PriceImpactAnalysisRequest) -> None:
        """Validate the analysis request."""
        if request.field_size_acres <= 0:
            raise ValueError("Field size must be positive")
        
        if request.expected_yield_bu_per_acre <= 0:
            raise ValueError("Expected yield must be positive")
        
        if request.crop_price_per_bu <= 0:
            raise ValueError("Crop price must be positive")
        
        if not request.fertilizer_requirements:
            raise ValueError("Fertilizer requirements cannot be empty")
        
        # Validate fertilizer requirements
        for req in request.fertilizer_requirements:
            if req.get('rate_lbs_per_acre', 0) <= 0:
                raise ValueError("Fertilizer rate must be positive")
    
    async def _get_market_data(self, request: PriceImpactAnalysisRequest) -> Dict[str, Any]:
        """Get current market data for analysis."""
        market_data = {
            'fertilizer_prices': {},
            'commodity_prices': {},
            'price_trends': {},
            'volatility_metrics': {}
        }
        
        # Get fertilizer prices
        for req in request.fertilizer_requirements:
            product_name = req.get('product')
            if product_name:
                try:
                    # Create fertilizer product object
                    product = FertilizerProduct(
                        name=product_name,
                        fertilizer_type=req.get('fertilizer_type', 'unknown'),
                        n_content=req.get('n_content', 0),
                        p_content=req.get('p_content', 0),
                        k_content=req.get('k_content', 0)
                    )
                    
                    price_data = await self.price_tracking_service.get_current_price(product)
                    if price_data:
                        market_data['fertilizer_prices'][product_name] = price_data
                        
                        # Get price trends
                        trends = await self.price_tracking_service.get_price_trends(
                            product, days=30
                        )
                        if trends:
                            market_data['price_trends'][product_name] = trends
                            
                except Exception as e:
                    logger.warning(f"Failed to get price for {product_name}: {e}")
        
        # Get commodity prices
        try:
            commodity_price = await self.commodity_price_service.get_current_price(
                commodity_type=request.crop_type.lower(),
                region="US"
            )
            if commodity_price:
                market_data['commodity_prices'][request.crop_type] = commodity_price
        except Exception as e:
            logger.warning(f"Failed to get commodity price for {request.crop_type}: {e}")
        
        return market_data
    
    async def _perform_sensitivity_analysis(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> PriceImpactAnalysisResult:
        """Perform sensitivity analysis for price changes."""
        logger.info("Performing sensitivity analysis")
        
        # Use default sensitivity ranges if not specified
        price_changes = request.price_change_percentages or self.default_sensitivity_ranges
        
        # Calculate baseline metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        # Perform sensitivity analysis for each parameter
        sensitivity_results = []
        
        # Fertilizer price sensitivity
        fertilizer_sensitivity = await self._analyze_fertilizer_price_sensitivity(
            request, market_data, price_changes
        )
        sensitivity_results.append(fertilizer_sensitivity)
        
        # Crop price sensitivity
        crop_sensitivity = await self._analyze_crop_price_sensitivity(
            request, market_data, price_changes
        )
        sensitivity_results.append(crop_sensitivity)
        
        # Yield sensitivity
        yield_sensitivity = await self._analyze_yield_sensitivity(
            request, market_data, price_changes
        )
        sensitivity_results.append(yield_sensitivity)
        
        # Generate recommendations
        recommendations = self._generate_sensitivity_recommendations(sensitivity_results)
        
        return PriceImpactAnalysisResult(
            analysis_id=request.analysis_id,
            analysis_type=AnalysisType.SENSITIVITY,
            baseline_metrics=baseline_metrics,
            sensitivity_results=sensitivity_results,
            recommendations=recommendations,
            confidence_score=0.85,
            data_quality_score=0.90,
            processing_time_ms=0  # Will be set by caller
        )
    
    async def _perform_scenario_analysis(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> PriceImpactAnalysisResult:
        """Perform scenario analysis with different price assumptions."""
        logger.info("Performing scenario analysis")
        
        # Use default scenarios if not specified
        scenarios = request.scenarios or self.default_scenarios
        
        # Calculate baseline metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        # Generate scenarios
        scenario_results = []
        for scenario_type in scenarios:
            scenario_data = await self._generate_scenario_data(
                scenario_type, request, market_data
            )
            scenario_results.append(scenario_data)
        
        # Process custom scenarios if provided
        if request.custom_scenarios:
            for custom_scenario in request.custom_scenarios:
                scenario_data = await self._process_custom_scenario(
                    custom_scenario, request, market_data
                )
                scenario_results.append(scenario_data)
        
        # Generate recommendations
        recommendations = self._generate_scenario_recommendations(scenario_results)
        
        return PriceImpactAnalysisResult(
            analysis_id=request.analysis_id,
            analysis_type=AnalysisType.SCENARIO,
            baseline_metrics=baseline_metrics,
            scenarios=scenario_results,
            recommendations=recommendations,
            confidence_score=0.80,
            data_quality_score=0.85,
            processing_time_ms=0
        )
    
    async def _perform_risk_assessment(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> PriceImpactAnalysisResult:
        """Perform comprehensive risk assessment."""
        logger.info("Performing risk assessment")
        
        # Calculate baseline metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        # Assess different risk factors
        risk_factors = await self._assess_risk_factors(request, market_data)
        
        # Calculate overall risk level
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        # Generate risk mitigation recommendations
        mitigation_actions = self._generate_risk_mitigation_recommendations(risk_factors)
        
        # Create risk assessment result
        risk_assessment = RiskAssessmentResult(
            overall_risk_level=overall_risk['level'],
            risk_score=overall_risk['score'],
            price_volatility_risk=risk_factors.get('price_volatility', 0.5),
            market_timing_risk=risk_factors.get('market_timing', 0.5),
            supply_chain_risk=risk_factors.get('supply_chain', 0.5),
            weather_risk=risk_factors.get('weather', 0.5),
            recommended_actions=mitigation_actions['actions'],
            hedging_recommendations=mitigation_actions['hedging']
        )
        
        # Generate recommendations
        recommendations = self._generate_risk_recommendations(risk_assessment)
        
        return PriceImpactAnalysisResult(
            analysis_id=request.analysis_id,
            analysis_type=AnalysisType.RISK_ASSESSMENT,
            baseline_metrics=baseline_metrics,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            confidence_score=0.75,
            data_quality_score=0.80,
            processing_time_ms=0
        )
    
    async def _perform_profitability_analysis(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> PriceImpactAnalysisResult:
        """Perform profitability impact analysis."""
        logger.info("Performing profitability analysis")
        
        # Calculate baseline metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        # Analyze profitability under different conditions
        profitability_scenarios = await self._analyze_profitability_scenarios(
            request, market_data
        )
        
        # Generate profitability recommendations
        recommendations = self._generate_profitability_recommendations(
            baseline_metrics, profitability_scenarios
        )
        
        return PriceImpactAnalysisResult(
            analysis_id=request.analysis_id,
            analysis_type=AnalysisType.PROFITABILITY_IMPACT,
            baseline_metrics=baseline_metrics,
            scenarios=profitability_scenarios,
            recommendations=recommendations,
            confidence_score=0.85,
            data_quality_score=0.90,
            processing_time_ms=0
        )
    
    async def _perform_timing_optimization(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> PriceImpactAnalysisResult:
        """Perform timing optimization analysis."""
        logger.info("Performing timing optimization")
        
        # Calculate baseline metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        # Analyze optimal timing windows
        timing_analysis = await self._analyze_timing_windows(request, market_data)
        
        # Generate timing recommendations
        recommendations = self._generate_timing_recommendations(timing_analysis)
        optimal_timing = timing_analysis.get('optimal_timing')
        
        return PriceImpactAnalysisResult(
            analysis_id=request.analysis_id,
            analysis_type=AnalysisType.TIMING_OPTIMIZATION,
            baseline_metrics=baseline_metrics,
            recommendations=recommendations,
            optimal_timing=optimal_timing,
            confidence_score=0.80,
            data_quality_score=0.85,
            processing_time_ms=0
        )
    
    async def _perform_comprehensive_analysis(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> PriceImpactAnalysisResult:
        """Perform comprehensive analysis including all analysis types."""
        logger.info("Performing comprehensive analysis")
        
        # Calculate baseline metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        # Perform sensitivity analysis
        sensitivity_results = []
        fertilizer_sensitivity = await self._analyze_fertilizer_price_sensitivity(
            request, market_data, self.default_sensitivity_ranges
        )
        sensitivity_results.append(fertilizer_sensitivity)
        
        # Add crop price sensitivity
        crop_sensitivity = await self._analyze_crop_price_sensitivity(
            request, market_data, self.default_sensitivity_ranges
        )
        sensitivity_results.append(crop_sensitivity)
        
        # Add yield sensitivity
        yield_sensitivity = await self._analyze_yield_sensitivity(
            request, market_data, self.default_sensitivity_ranges
        )
        sensitivity_results.append(yield_sensitivity)
        
        # Perform scenario analysis
        scenario_results = []
        for scenario_type in self.default_scenarios:
            scenario_data = await self._generate_scenario_data(
                scenario_type, request, market_data
            )
            scenario_results.append(scenario_data)
        
        # Perform risk assessment
        risk_factors = await self._assess_risk_factors(request, market_data)
        overall_risk = self._calculate_overall_risk(risk_factors)
        
        risk_assessment = RiskAssessmentResult(
            overall_risk_level=overall_risk['level'],
            risk_score=overall_risk['score'],
            price_volatility_risk=risk_factors.get('price_volatility', 0.5),
            market_timing_risk=risk_factors.get('market_timing', 0.5),
            supply_chain_risk=risk_factors.get('supply_chain', 0.5),
            weather_risk=risk_factors.get('weather', 0.5),
            recommended_actions=self._generate_risk_mitigation_recommendations(risk_factors)['actions'],
            hedging_recommendations=self._generate_risk_mitigation_recommendations(risk_factors)['hedging']
        )
        
        # Generate comprehensive recommendations
        recommendations = self._generate_comprehensive_recommendations(
            baseline_metrics, sensitivity_results, scenario_results, risk_assessment
        )
        
        return PriceImpactAnalysisResult(
            analysis_id=request.analysis_id,
            analysis_type=AnalysisType.SENSITIVITY,  # Default to sensitivity for comprehensive
            baseline_metrics=baseline_metrics,
            scenarios=scenario_results,
            sensitivity_results=sensitivity_results,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            confidence_score=0.80,
            data_quality_score=0.85,
            processing_time_ms=0
        )
    
    async def _calculate_baseline_metrics(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> PriceImpactMetrics:
        """Calculate baseline profitability metrics."""
        # Calculate total fertilizer cost
        total_fertilizer_cost = 0
        fertilizer_cost_per_acre = 0
        
        for req in request.fertilizer_requirements:
            product_name = req.get('product')
            rate_lbs_per_acre = req.get('rate_lbs_per_acre', 0)
            
            if product_name in market_data['fertilizer_prices']:
                price_data = market_data['fertilizer_prices'][product_name]
                cost_per_lb = price_data.price_per_unit / price_data.unit_conversion_factor
                product_cost_per_acre = rate_lbs_per_acre * cost_per_lb
                fertilizer_cost_per_acre += product_cost_per_acre
        
        total_fertilizer_cost = fertilizer_cost_per_acre * request.field_size_acres
        
        # Calculate crop revenue
        total_crop_revenue = (
            request.expected_yield_bu_per_acre * 
            request.crop_price_per_bu * 
            request.field_size_acres
        )
        
        # Calculate net profit
        net_profit = total_crop_revenue - total_fertilizer_cost
        
        # Calculate profit margin
        profit_margin_percent = (net_profit / total_crop_revenue * 100) if total_crop_revenue > 0 else 0
        
        # Calculate per-unit metrics
        fertilizer_cost_per_bu = (
            fertilizer_cost_per_acre / request.expected_yield_bu_per_acre
            if request.expected_yield_bu_per_acre > 0 else 0
        )
        crop_revenue_per_acre = total_crop_revenue / request.field_size_acres
        
        return PriceImpactMetrics(
            total_fertilizer_cost=total_fertilizer_cost,
            total_crop_revenue=total_crop_revenue,
            net_profit=net_profit,
            profit_margin_percent=profit_margin_percent,
            fertilizer_cost_per_acre=fertilizer_cost_per_acre,
            fertilizer_cost_per_bu=fertilizer_cost_per_bu,
            crop_revenue_per_acre=crop_revenue_per_acre,
            price_impact_percent=0,  # Baseline has no impact
            profitability_change_percent=0  # Baseline has no change
        )
    
    async def _analyze_fertilizer_price_sensitivity(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any],
        price_changes: List[float]
    ) -> SensitivityAnalysisResult:
        """Analyze sensitivity to fertilizer price changes."""
        parameter_values = []
        impact_values = []
        
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        for change_pct in price_changes:
            # Calculate modified fertilizer cost
            modified_cost_per_acre = baseline_metrics.fertilizer_cost_per_acre * (1 + change_pct / 100)
            modified_total_cost = modified_cost_per_acre * request.field_size_acres
            
            # Calculate new profitability
            total_revenue = baseline_metrics.total_crop_revenue
            new_profit = total_revenue - modified_total_cost
            
            # Calculate impact
            profit_change = new_profit - baseline_metrics.net_profit
            impact_pct = (profit_change / baseline_metrics.net_profit * 100) if baseline_metrics.net_profit != 0 else 0
            
            parameter_values.append(change_pct)
            impact_values.append(impact_pct)
        
        # Calculate elasticity
        elasticity = self._calculate_elasticity(parameter_values, impact_values)
        
        # Calculate sensitivity score
        sensitivity_score = abs(elasticity)
        
        # Find critical threshold (where profit becomes negative)
        critical_threshold = None
        for i, impact in enumerate(impact_values):
            if impact <= -100:  # Profit becomes zero or negative
                critical_threshold = parameter_values[i]
                break
        
        return SensitivityAnalysisResult(
            parameter_name="fertilizer_price",
            parameter_values=parameter_values,
            impact_values=impact_values,
            elasticity=elasticity,
            sensitivity_score=sensitivity_score,
            critical_threshold=critical_threshold
        )
    
    async def _analyze_crop_price_sensitivity(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any],
        price_changes: List[float]
    ) -> SensitivityAnalysisResult:
        """Analyze sensitivity to crop price changes."""
        parameter_values = []
        impact_values = []
        
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        for change_pct in price_changes:
            # Calculate modified crop revenue
            modified_price_per_bu = request.crop_price_per_bu * (1 + change_pct / 100)
            modified_total_revenue = (
                request.expected_yield_bu_per_acre * 
                modified_price_per_bu * 
                request.field_size_acres
            )
            
            # Calculate new profitability
            new_profit = modified_total_revenue - baseline_metrics.total_fertilizer_cost
            
            # Calculate impact
            profit_change = new_profit - baseline_metrics.net_profit
            impact_pct = (profit_change / baseline_metrics.net_profit * 100) if baseline_metrics.net_profit != 0 else 0
            
            parameter_values.append(change_pct)
            impact_values.append(impact_pct)
        
        # Calculate elasticity
        elasticity = self._calculate_elasticity(parameter_values, impact_values)
        
        # Calculate sensitivity score
        sensitivity_score = abs(elasticity)
        
        # Find critical threshold (where profit becomes negative)
        critical_threshold = None
        for i, impact in enumerate(impact_values):
            if impact <= -100:  # Profit becomes zero or negative
                critical_threshold = parameter_values[i]
                break
        
        return SensitivityAnalysisResult(
            parameter_name="crop_price",
            parameter_values=parameter_values,
            impact_values=impact_values,
            elasticity=elasticity,
            sensitivity_score=sensitivity_score,
            critical_threshold=critical_threshold
        )
    
    async def _analyze_yield_sensitivity(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any],
        yield_changes: List[float]
    ) -> SensitivityAnalysisResult:
        """Analyze sensitivity to yield changes."""
        parameter_values = []
        impact_values = []
        
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        for change_pct in yield_changes:
            # Calculate modified yield
            modified_yield = request.expected_yield_bu_per_acre * (1 + change_pct / 100)
            modified_total_revenue = (
                modified_yield * 
                request.crop_price_per_bu * 
                request.field_size_acres
            )
            
            # Calculate new profitability
            new_profit = modified_total_revenue - baseline_metrics.total_fertilizer_cost
            
            # Calculate impact
            profit_change = new_profit - baseline_metrics.net_profit
            impact_pct = (profit_change / baseline_metrics.net_profit * 100) if baseline_metrics.net_profit != 0 else 0
            
            parameter_values.append(change_pct)
            impact_values.append(impact_pct)
        
        # Calculate elasticity
        elasticity = self._calculate_elasticity(parameter_values, impact_values)
        
        # Calculate sensitivity score
        sensitivity_score = abs(elasticity)
        
        # Find critical threshold (where profit becomes negative)
        critical_threshold = None
        for i, impact in enumerate(impact_values):
            if impact <= -100:  # Profit becomes zero or negative
                critical_threshold = parameter_values[i]
                break
        
        return SensitivityAnalysisResult(
            parameter_name="yield",
            parameter_values=parameter_values,
            impact_values=impact_values,
            elasticity=elasticity,
            sensitivity_score=sensitivity_score,
            critical_threshold=critical_threshold
        )
    
    def _calculate_elasticity(self, parameter_values: List[float], impact_values: List[float]) -> float:
        """Calculate price elasticity of profitability."""
        if len(parameter_values) < 2:
            return 0.0
        
        # Find the baseline point (closest to 0% change)
        baseline_idx = min(range(len(parameter_values)), key=lambda i: abs(parameter_values[i]))
        
        if baseline_idx == 0 or baseline_idx == len(parameter_values) - 1:
            # Use adjacent points for elasticity calculation
            if baseline_idx == 0:
                x1, x2 = parameter_values[0], parameter_values[1]
                y1, y2 = impact_values[0], impact_values[1]
            else:
                x1, x2 = parameter_values[-2], parameter_values[-1]
                y1, y2 = impact_values[-2], impact_values[-1]
        else:
            # Use points around baseline
            x1, x2 = parameter_values[baseline_idx-1], parameter_values[baseline_idx+1]
            y1, y2 = impact_values[baseline_idx-1], impact_values[baseline_idx+1]
        
        # Calculate elasticity: (ΔY/Y) / (ΔX/X)
        # Handle the case where baseline values might be zero
        if abs(x1) < 0.001:  # Very close to zero
            # Use the change from baseline to next point
            if baseline_idx < len(parameter_values) - 1:
                x1, x2 = parameter_values[baseline_idx], parameter_values[baseline_idx + 1]
                y1, y2 = impact_values[baseline_idx], impact_values[baseline_idx + 1]
            else:
                x1, x2 = parameter_values[baseline_idx - 1], parameter_values[baseline_idx]
                y1, y2 = impact_values[baseline_idx - 1], impact_values[baseline_idx]
        
        if abs(x1) > 0.001 and abs(y1) > 0.001:
            elasticity = ((y2 - y1) / y1) / ((x2 - x1) / x1)
        else:
            # Fallback to simple slope calculation
            elasticity = (y2 - y1) / (x2 - x1) if (x2 - x1) != 0 else 0.0
        
        return elasticity
    
    async def _generate_scenario_data(
        self,
        scenario_type: ScenarioType,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate scenario data for analysis."""
        scenario_multipliers = {
            ScenarioType.BASELINE: {'fertilizer': 1.0, 'crop': 1.0},
            ScenarioType.OPTIMISTIC: {'fertilizer': 0.8, 'crop': 1.2},
            ScenarioType.PESSIMISTIC: {'fertilizer': 1.3, 'crop': 0.8},
            ScenarioType.VOLATILE: {'fertilizer': 1.1, 'crop': 0.9}
        }
        
        multipliers = scenario_multipliers.get(scenario_type, {'fertilizer': 1.0, 'crop': 1.0})
        
        # Calculate scenario metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        # Apply multipliers
        scenario_fertilizer_cost = baseline_metrics.total_fertilizer_cost * multipliers['fertilizer']
        scenario_crop_revenue = baseline_metrics.total_crop_revenue * multipliers['crop']
        scenario_net_profit = scenario_crop_revenue - scenario_fertilizer_cost
        
        # Calculate impact
        profit_change = scenario_net_profit - baseline_metrics.net_profit
        impact_pct = (profit_change / baseline_metrics.net_profit * 100) if baseline_metrics.net_profit != 0 else 0
        
        return {
            'scenario_type': scenario_type.value,
            'scenario_name': scenario_type.value.title(),
            'fertilizer_multiplier': multipliers['fertilizer'],
            'crop_multiplier': multipliers['crop'],
            'total_fertilizer_cost': scenario_fertilizer_cost,
            'total_crop_revenue': scenario_crop_revenue,
            'net_profit': scenario_net_profit,
            'profit_change_percent': impact_pct,
            'probability': self._get_scenario_probability(scenario_type),
            'risk_level': self._get_scenario_risk_level(scenario_type)
        }
    
    def _get_scenario_probability(self, scenario_type: ScenarioType) -> float:
        """Get probability for scenario type."""
        probabilities = {
            ScenarioType.BASELINE: 0.4,
            ScenarioType.OPTIMISTIC: 0.2,
            ScenarioType.PESSIMISTIC: 0.2,
            ScenarioType.VOLATILE: 0.2
        }
        return probabilities.get(scenario_type, 0.25)
    
    def _get_scenario_risk_level(self, scenario_type: ScenarioType) -> str:
        """Get risk level for scenario type."""
        risk_levels = {
            ScenarioType.BASELINE: 'low',
            ScenarioType.OPTIMISTIC: 'low',
            ScenarioType.PESSIMISTIC: 'high',
            ScenarioType.VOLATILE: 'medium'
        }
        return risk_levels.get(scenario_type, 'medium')
    
    async def _process_custom_scenario(
        self,
        custom_scenario: Dict[str, Any],
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process custom scenario data."""
        # Extract scenario parameters
        fertilizer_multiplier = custom_scenario.get('fertilizer_multiplier', 1.0)
        crop_multiplier = custom_scenario.get('crop_multiplier', 1.0)
        scenario_name = custom_scenario.get('name', 'Custom Scenario')
        
        # Calculate scenario metrics
        baseline_metrics = await self._calculate_baseline_metrics(request, market_data)
        
        scenario_fertilizer_cost = baseline_metrics.total_fertilizer_cost * fertilizer_multiplier
        scenario_crop_revenue = baseline_metrics.total_crop_revenue * crop_multiplier
        scenario_net_profit = scenario_crop_revenue - scenario_fertilizer_cost
        
        # Calculate impact
        profit_change = scenario_net_profit - baseline_metrics.net_profit
        impact_pct = (profit_change / baseline_metrics.net_profit * 100) if baseline_metrics.net_profit != 0 else 0
        
        return {
            'scenario_type': 'custom',
            'scenario_name': scenario_name,
            'fertilizer_multiplier': fertilizer_multiplier,
            'crop_multiplier': crop_multiplier,
            'total_fertilizer_cost': scenario_fertilizer_cost,
            'total_crop_revenue': scenario_crop_revenue,
            'net_profit': scenario_net_profit,
            'profit_change_percent': impact_pct,
            'probability': custom_scenario.get('probability', 0.1),
            'risk_level': custom_scenario.get('risk_level', 'medium')
        }
    
    async def _assess_risk_factors(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> Dict[str, float]:
        """Assess various risk factors."""
        risk_factors = {}
        
        # Price volatility risk
        volatility_risk = await self._calculate_price_volatility_risk(market_data)
        risk_factors['price_volatility'] = volatility_risk
        
        # Market timing risk
        timing_risk = await self._calculate_market_timing_risk(request, market_data)
        risk_factors['market_timing'] = timing_risk
        
        # Supply chain risk
        supply_chain_risk = await self._calculate_supply_chain_risk(request, market_data)
        risk_factors['supply_chain'] = supply_chain_risk
        
        # Weather risk
        weather_risk = await self._calculate_weather_risk(request)
        risk_factors['weather'] = weather_risk
        
        return risk_factors
    
    async def _calculate_price_volatility_risk(self, market_data: Dict[str, Any]) -> float:
        """Calculate price volatility risk."""
        volatility_scores = []
        
        for product_name, price_data in market_data['fertilizer_prices'].items():
            if product_name in market_data['price_trends']:
                trend_data = market_data['price_trends'][product_name]
                # Calculate volatility based on price changes
                if hasattr(trend_data, 'price_history') and len(trend_data.price_history) > 1:
                    prices = [p['price'] for p in trend_data.price_history]
                    if len(prices) > 1:
                        volatility = statistics.stdev(prices) / statistics.mean(prices)
                        volatility_scores.append(min(volatility, 1.0))  # Cap at 1.0
        
        return statistics.mean(volatility_scores) if volatility_scores else 0.5
    
    async def _calculate_market_timing_risk(self, request: PriceImpactAnalysisRequest, market_data: Dict[str, Any]) -> float:
        """Calculate market timing risk."""
        # Simple timing risk based on analysis horizon
        if request.analysis_horizon_days > 365:
            return 0.8  # High risk for long-term analysis
        elif request.analysis_horizon_days > 180:
            return 0.6  # Medium risk
        else:
            return 0.4  # Lower risk for short-term analysis
    
    async def _calculate_supply_chain_risk(self, request: PriceImpactAnalysisRequest, market_data: Dict[str, Any]) -> float:
        """Calculate supply chain risk."""
        # Simple supply chain risk assessment
        risk_score = 0.5  # Base risk
        
        # Increase risk for multiple fertilizer products
        if len(request.fertilizer_requirements) > 3:
            risk_score += 0.2
        
        # Increase risk for high application rates
        total_rate = sum(req.get('rate_lbs_per_acre', 0) for req in request.fertilizer_requirements)
        if total_rate > 200:  # High application rate
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    async def _calculate_weather_risk(self, request: PriceImpactAnalysisRequest) -> float:
        """Calculate weather-related risk."""
        # Simple weather risk assessment
        # In a real implementation, this would integrate with weather data
        return 0.6  # Moderate weather risk
    
    def _calculate_overall_risk(self, risk_factors: Dict[str, float]) -> Dict[str, Any]:
        """Calculate overall risk level and score."""
        # Calculate weighted average of risk factors
        weights = {
            'price_volatility': 0.3,
            'market_timing': 0.25,
            'supply_chain': 0.25,
            'weather': 0.2
        }
        
        overall_score = sum(
            risk_factors.get(factor, 0.5) * weight 
            for factor, weight in weights.items()
        )
        
        # Determine risk level
        if overall_score >= 0.8:
            risk_level = RiskLevel.CRITICAL
        elif overall_score >= 0.6:
            risk_level = RiskLevel.HIGH
        elif overall_score >= 0.4:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.LOW
        
        return {
            'level': risk_level,
            'score': overall_score
        }
    
    def _generate_risk_mitigation_recommendations(self, risk_factors: Dict[str, float]) -> Dict[str, List[str]]:
        """Generate risk mitigation recommendations."""
        actions = []
        hedging = []
        
        # Price volatility mitigation
        if risk_factors.get('price_volatility', 0) > 0.6:
            actions.append("Consider forward contracting for fertilizer purchases")
            actions.append("Implement price monitoring and alert system")
            hedging.append("Fertilizer price hedging contracts")
        
        # Market timing mitigation
        if risk_factors.get('market_timing', 0) > 0.6:
            actions.append("Implement flexible purchasing strategy")
            actions.append("Monitor market trends and seasonal patterns")
        
        # Supply chain mitigation
        if risk_factors.get('supply_chain', 0) > 0.6:
            actions.append("Diversify fertilizer suppliers")
            actions.append("Maintain adequate inventory levels")
            actions.append("Develop alternative fertilizer sources")
        
        # Weather mitigation
        if risk_factors.get('weather', 0) > 0.6:
            actions.append("Monitor weather forecasts for application timing")
            actions.append("Implement flexible application schedules")
            hedging.append("Weather-based insurance products")
        
        return {
            'actions': actions,
            'hedging': hedging
        }
    
    def _generate_sensitivity_recommendations(self, sensitivity_results: List[SensitivityAnalysisResult]) -> List[str]:
        """Generate recommendations based on sensitivity analysis."""
        recommendations = []
        
        for result in sensitivity_results:
            if result.sensitivity_score > 2.0:  # High sensitivity
                recommendations.append(
                    f"High sensitivity to {result.parameter_name} changes - monitor closely"
                )
            
            if result.critical_threshold is not None:
                recommendations.append(
                    f"Critical threshold for {result.parameter_name}: {result.critical_threshold:.1f}% change"
                )
        
        return recommendations
    
    def _generate_scenario_recommendations(self, scenario_results: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on scenario analysis."""
        recommendations = []
        
        # Find best and worst case scenarios
        best_scenario = max(scenario_results, key=lambda s: s['net_profit'])
        worst_scenario = min(scenario_results, key=lambda s: s['net_profit'])
        
        recommendations.append(f"Best case scenario: {best_scenario['scenario_name']} with ${best_scenario['net_profit']:,.2f} profit")
        recommendations.append(f"Worst case scenario: {worst_scenario['scenario_name']} with ${worst_scenario['net_profit']:,.2f} profit")
        
        # Risk mitigation recommendations
        if worst_scenario['net_profit'] < 0:
            recommendations.append("Consider risk mitigation strategies for negative profit scenarios")
        
        return recommendations
    
    def _generate_risk_recommendations(self, risk_assessment: RiskAssessmentResult) -> List[str]:
        """Generate recommendations based on risk assessment."""
        recommendations = []
        
        if risk_assessment.overall_risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("High risk detected - implement comprehensive risk management")
        
        recommendations.extend(risk_assessment.recommended_actions)
        
        if risk_assessment.hedging_recommendations:
            recommendations.append("Consider hedging strategies:")
            recommendations.extend([f"- {hedge}" for hedge in risk_assessment.hedging_recommendations])
        
        return recommendations
    
    def _generate_profitability_recommendations(
        self,
        baseline_metrics: PriceImpactMetrics,
        profitability_scenarios: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate profitability recommendations."""
        recommendations = []
        
        if baseline_metrics.profit_margin_percent < 10:
            recommendations.append("Low profit margin - consider cost optimization")
        
        if baseline_metrics.fertilizer_cost_per_bu > baseline_metrics.crop_revenue_per_acre * 0.3:
            recommendations.append("High fertilizer cost relative to revenue - optimize rates")
        
        return recommendations
    
    def _generate_timing_recommendations(self, timing_analysis: Dict[str, Any]) -> List[str]:
        """Generate timing recommendations."""
        recommendations = []
        
        optimal_timing = timing_analysis.get('optimal_timing')
        if optimal_timing:
            recommendations.append(f"Optimal timing: {optimal_timing}")
        
        recommendations.append("Monitor market conditions for optimal purchasing timing")
        recommendations.append("Consider seasonal price patterns")
        
        return recommendations
    
    def _generate_comprehensive_recommendations(
        self,
        baseline_metrics: PriceImpactMetrics,
        sensitivity_results: List[SensitivityAnalysisResult],
        scenario_results: List[Dict[str, Any]],
        risk_assessment: RiskAssessmentResult
    ) -> List[str]:
        """Generate comprehensive recommendations."""
        recommendations = []
        
        # Add sensitivity recommendations
        recommendations.extend(self._generate_sensitivity_recommendations(sensitivity_results))
        
        # Add scenario recommendations
        recommendations.extend(self._generate_scenario_recommendations(scenario_results))
        
        # Add risk recommendations
        recommendations.extend(self._generate_risk_recommendations(risk_assessment))
        
        # Add profitability recommendations
        profitability_scenarios = scenario_results
        recommendations.extend(self._generate_profitability_recommendations(baseline_metrics, profitability_scenarios))
        
        return recommendations
    
    async def _analyze_profitability_scenarios(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Analyze profitability under different scenarios."""
        # This would include more sophisticated profitability analysis
        # For now, return basic scenario data
        scenarios = []
        
        for scenario_type in [ScenarioType.OPTIMISTIC, ScenarioType.PESSIMISTIC]:
            scenario_data = await self._generate_scenario_data(scenario_type, request, market_data)
            scenarios.append(scenario_data)
        
        return scenarios
    
    async def _analyze_timing_windows(
        self,
        request: PriceImpactAnalysisRequest,
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze optimal timing windows."""
        # This would include sophisticated timing analysis
        # For now, return basic timing recommendations
        return {
            'optimal_timing': 'Spring application (March-April)',
            'avoid_periods': ['Late fall', 'Winter months'],
            'monitoring_periods': ['Pre-season pricing', 'Post-harvest pricing']
        }