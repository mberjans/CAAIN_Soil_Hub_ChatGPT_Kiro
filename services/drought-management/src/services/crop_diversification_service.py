"""
Crop Diversification and Risk Management Service

Service for implementing crop diversification strategies to reduce drought risk,
optimize portfolio allocation, and enhance farm resilience through intelligent
crop mix planning and risk assessment.
"""

import logging
import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import statistics

from ..models.crop_diversification_models import (
    DiversificationRequest,
    DiversificationResponse,
    DiversificationRecommendation,
    DiversificationPortfolio,
    CropRiskProfile,
    MarketRiskAssessment,
    CropCompatibilityMatrix,
    RiskMitigationStrategy,
    RiskLevel,
    DiversificationStrategy,
    CropCategory,
    DroughtToleranceLevel,
    MarketRiskType
)

logger = logging.getLogger(__name__)

class CropDiversificationService:
    """Service for crop diversification and risk management."""
    
    def __init__(self):
        """Initialize the crop diversification service."""
        self.crop_database = self._build_crop_database()
        self.compatibility_matrix = self._build_compatibility_matrix()
        self.market_risk_data = self._build_market_risk_data()
        self.drought_tolerance_data = self._build_drought_tolerance_data()
        self.initialized = False
    
    async def initialize(self):
        """Initialize the crop diversification service."""
        try:
            logger.info("Initializing Crop Diversification Service...")
            
            # Initialize external service connections
            self.weather_service = None  # Would connect to weather service
            self.market_service = None    # Would connect to market service
            self.crop_service = None      # Would connect to crop recommendation service
            
            self.initialized = True
            logger.info("Crop Diversification Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Crop Diversification Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Crop Diversification Service...")
            self.initialized = False
            logger.info("Crop Diversification Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def analyze_diversification_options(self, request: DiversificationRequest) -> DiversificationResponse:
        """
        Analyze diversification options for drought risk reduction.
        
        Args:
            request: Diversification analysis request
            
        Returns:
            Comprehensive diversification analysis with recommendations
        """
        try:
            logger.info(f"Analyzing diversification options for farm: {request.farm_id}")
            
            # Assess current risk profile
            current_risk = await self._assess_current_risk(request)
            
            # Generate diversification strategies
            diversification_strategies = await self._generate_diversification_strategies(request)
            
            # Create optimized portfolios
            portfolios = await self._create_optimized_portfolios(request, diversification_strategies)
            
            # Assess market risks
            market_risks = await self._assess_market_risks(portfolios)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(
                request, portfolios, market_risks, current_risk
            )
            
            # Calculate economic analysis
            economic_analysis = await self._calculate_economic_analysis(recommendations)
            
            # Create monitoring plan
            monitoring_plan = await self._create_monitoring_plan(recommendations)
            
            # Determine implementation priority
            implementation_priority = await self._determine_implementation_priority(recommendations)
            
            # Calculate overall confidence
            confidence_score = await self._calculate_confidence_score(recommendations, request)
            
            response = DiversificationResponse(
                request_id=uuid4(),
                farm_id=request.farm_id,
                current_risk_assessment=current_risk,
                diversification_recommendations=recommendations,
                risk_comparison=await self._compare_risk_levels(current_risk, recommendations),
                economic_analysis=economic_analysis,
                implementation_priority=implementation_priority,
                monitoring_plan=monitoring_plan,
                next_review_date=date.today() + timedelta(days=90),
                confidence_score=confidence_score
            )
            
            logger.info(f"Diversification analysis completed for farm: {request.farm_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error analyzing diversification options: {str(e)}")
            raise
    
    async def optimize_crop_portfolio(self, request: DiversificationRequest) -> DiversificationPortfolio:
        """
        Optimize crop portfolio for maximum diversification benefits.
        
        Args:
            request: Diversification request with constraints
            
        Returns:
            Optimized crop portfolio
        """
        try:
            logger.info(f"Optimizing crop portfolio for farm: {request.farm_id}")
            
            # Get available crops for the region
            available_crops = await self._get_available_crops(request)
            
            # Filter crops by constraints
            filtered_crops = await self._filter_crops_by_constraints(available_crops, request)
            
            # Calculate diversification scores
            diversification_scores = await self._calculate_diversification_scores(filtered_crops)
            
            # Optimize allocation using portfolio theory
            optimal_allocation = await self._optimize_allocation(
                filtered_crops, diversification_scores, request
            )
            
            # Create optimized portfolio
            portfolio = await self._create_portfolio(
                request.farm_id, filtered_crops, optimal_allocation, request.total_acres
            )
            
            logger.info(f"Portfolio optimization completed for farm: {request.farm_id}")
            return portfolio
            
        except Exception as e:
            logger.error(f"Error optimizing crop portfolio: {str(e)}")
            raise
    
    async def assess_drought_risk_reduction(self, portfolio: DiversificationPortfolio) -> Dict[str, Any]:
        """
        Assess drought risk reduction potential of a portfolio.
        
        Args:
            portfolio: Crop diversification portfolio
            
        Returns:
            Drought risk reduction assessment
        """
        try:
            logger.info(f"Assessing drought risk reduction for portfolio: {portfolio.portfolio_id}")
            
            # Calculate water efficiency
            water_efficiency = await self._calculate_water_efficiency(portfolio)
            
            # Assess yield stability
            yield_stability = await self._calculate_yield_stability(portfolio)
            
            # Calculate soil health benefits
            soil_health_benefits = await self._calculate_soil_health_benefits(portfolio)
            
            # Assess temporal risk distribution
            temporal_risk = await self._assess_temporal_risk_distribution(portfolio)
            
            # Calculate overall drought resilience
            drought_resilience = await self._calculate_drought_resilience(
                water_efficiency, yield_stability, soil_health_benefits, temporal_risk
            )
            
            assessment = {
                "water_efficiency_score": water_efficiency,
                "yield_stability_score": yield_stability,
                "soil_health_score": soil_health_benefits,
                "temporal_risk_score": temporal_risk,
                "overall_drought_resilience": drought_resilience,
                "risk_reduction_percent": await self._calculate_risk_reduction_percent(drought_resilience),
                "recommendations": await self._generate_drought_mitigation_recommendations(portfolio)
            }
            
            logger.info(f"Drought risk assessment completed for portfolio: {portfolio.portfolio_id}")
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing drought risk reduction: {str(e)}")
            raise
    
    def _build_crop_database(self) -> Dict[str, Dict[str, Any]]:
        """Build comprehensive crop database with risk profiles."""
        return {
            "corn": {
                "category": CropCategory.GRAINS,
                "drought_tolerance": DroughtToleranceLevel.MODERATE,
                "water_requirement_mm": 500,
                "yield_stability_score": 0.7,
                "market_price_volatility": 0.6,
                "disease_susceptibility": 0.5,
                "pest_susceptibility": 0.6,
                "soil_health_contribution": 0.3,
                "nitrogen_fixation": False,
                "root_depth_cm": 120,
                "maturity_days": 120
            },
            "soybeans": {
                "category": CropCategory.LEGUMES,
                "drought_tolerance": DroughtToleranceLevel.MODERATE,
                "water_requirement_mm": 450,
                "yield_stability_score": 0.8,
                "market_price_volatility": 0.7,
                "disease_susceptibility": 0.4,
                "pest_susceptibility": 0.5,
                "soil_health_contribution": 0.8,
                "nitrogen_fixation": True,
                "root_depth_cm": 100,
                "maturity_days": 110
            },
            "wheat": {
                "category": CropCategory.GRAINS,
                "drought_tolerance": DroughtToleranceLevel.HIGH,
                "water_requirement_mm": 400,
                "yield_stability_score": 0.9,
                "market_price_volatility": 0.5,
                "disease_susceptibility": 0.6,
                "pest_susceptibility": 0.4,
                "soil_health_contribution": 0.4,
                "nitrogen_fixation": False,
                "root_depth_cm": 150,
                "maturity_days": 100
            },
            "sorghum": {
                "category": CropCategory.GRAINS,
                "drought_tolerance": DroughtToleranceLevel.VERY_HIGH,
                "water_requirement_mm": 350,
                "yield_stability_score": 0.8,
                "market_price_volatility": 0.6,
                "disease_susceptibility": 0.3,
                "pest_susceptibility": 0.3,
                "soil_health_contribution": 0.5,
                "nitrogen_fixation": False,
                "root_depth_cm": 180,
                "maturity_days": 90
            },
            "sunflower": {
                "category": CropCategory.OILSEEDS,
                "drought_tolerance": DroughtToleranceLevel.HIGH,
                "water_requirement_mm": 380,
                "yield_stability_score": 0.7,
                "market_price_volatility": 0.8,
                "disease_susceptibility": 0.4,
                "pest_susceptibility": 0.5,
                "soil_health_contribution": 0.6,
                "nitrogen_fixation": False,
                "root_depth_cm": 200,
                "maturity_days": 85
            },
            "alfalfa": {
                "category": CropCategory.FORAGE,
                "drought_tolerance": DroughtToleranceLevel.HIGH,
                "water_requirement_mm": 600,
                "yield_stability_score": 0.9,
                "market_price_volatility": 0.4,
                "disease_susceptibility": 0.3,
                "pest_susceptibility": 0.4,
                "soil_health_contribution": 0.9,
                "nitrogen_fixation": True,
                "root_depth_cm": 300,
                "maturity_days": 30
            },
            "clover": {
                "category": CropCategory.COVER_CROPS,
                "drought_tolerance": DroughtToleranceLevel.MODERATE,
                "water_requirement_mm": 300,
                "yield_stability_score": 0.8,
                "market_price_volatility": 0.3,
                "disease_susceptibility": 0.2,
                "pest_susceptibility": 0.2,
                "soil_health_contribution": 0.9,
                "nitrogen_fixation": True,
                "root_depth_cm": 60,
                "maturity_days": 60
            },
            "millet": {
                "category": CropCategory.GRAINS,
                "drought_tolerance": DroughtToleranceLevel.VERY_HIGH,
                "water_requirement_mm": 250,
                "yield_stability_score": 0.9,
                "market_price_volatility": 0.7,
                "disease_susceptibility": 0.2,
                "pest_susceptibility": 0.2,
                "soil_health_contribution": 0.6,
                "nitrogen_fixation": False,
                "root_depth_cm": 120,
                "maturity_days": 70
            }
        }
    
    def _build_compatibility_matrix(self) -> CropCompatibilityMatrix:
        """Build crop compatibility matrix for diversification."""
        return CropCompatibilityMatrix(
            crop_pairs={
                ("corn", "soybeans"): 0.9,
                ("wheat", "soybeans"): 0.8,
                ("sorghum", "soybeans"): 0.7,
                ("sunflower", "wheat"): 0.6,
                ("alfalfa", "corn"): 0.8,
                ("clover", "corn"): 0.9,
                ("millet", "soybeans"): 0.8
            },
            rotation_benefits={
                "corn": {"soybeans": 0.8, "wheat": 0.6, "alfalfa": 0.7},
                "soybeans": {"corn": 0.9, "wheat": 0.8, "sorghum": 0.7},
                "wheat": {"soybeans": 0.8, "sunflower": 0.6, "alfalfa": 0.7},
                "sorghum": {"soybeans": 0.7, "millet": 0.6},
                "alfalfa": {"corn": 0.8, "wheat": 0.7, "soybeans": 0.8}
            },
            intercropping_potential={
                ("corn", "soybeans"): 0.7,
                ("wheat", "clover"): 0.8,
                ("sorghum", "millet"): 0.6
            },
            soil_health_benefits={
                "soybeans": 0.8,
                "alfalfa": 0.9,
                "clover": 0.9,
                "wheat": 0.4,
                "corn": 0.3,
                "sorghum": 0.5,
                "sunflower": 0.6,
                "millet": 0.6
            },
            pest_disease_interactions={
                ("corn", "soybeans"): "beneficial",
                ("wheat", "corn"): "neutral",
                ("sorghum", "corn"): "competitive"
            }
        )
    
    def _build_market_risk_data(self) -> Dict[str, MarketRiskAssessment]:
        """Build market risk assessment data."""
        return {
            "corn": MarketRiskAssessment(
                crop_id=uuid4(),
                risk_types=[MarketRiskType.PRICE_VOLATILITY, MarketRiskType.WEATHER_IMPACT],
                price_volatility_score=0.6,
                demand_stability_score=0.8,
                supply_chain_risk_score=0.4,
                weather_sensitivity_score=0.7,
                policy_risk_score=0.5,
                overall_market_risk=0.6,
                risk_mitigation_strategies=["Futures contracts", "Crop insurance", "Diversification"]
            ),
            "soybeans": MarketRiskAssessment(
                crop_id=uuid4(),
                risk_types=[MarketRiskType.PRICE_VOLATILITY, MarketRiskType.DEMAND_FLUCTUATION],
                price_volatility_score=0.7,
                demand_stability_score=0.7,
                supply_chain_risk_score=0.5,
                weather_sensitivity_score=0.6,
                policy_risk_score=0.6,
                overall_market_risk=0.6,
                risk_mitigation_strategies=["Export contracts", "Processing agreements", "Diversification"]
            ),
            "wheat": MarketRiskAssessment(
                crop_id=uuid4(),
                risk_types=[MarketRiskType.PRICE_VOLATILITY],
                price_volatility_score=0.5,
                demand_stability_score=0.9,
                supply_chain_risk_score=0.3,
                weather_sensitivity_score=0.5,
                policy_risk_score=0.4,
                overall_market_risk=0.4,
                risk_mitigation_strategies=["Storage", "Quality contracts", "Diversification"]
            )
        }
    
    def _build_drought_tolerance_data(self) -> Dict[str, Dict[str, Any]]:
        """Build drought tolerance and water efficiency data."""
        return {
            "very_high": {
                "water_efficiency": 0.9,
                "drought_recovery": 0.8,
                "deep_rooting": 0.9,
                "water_storage": 0.8
            },
            "high": {
                "water_efficiency": 0.8,
                "drought_recovery": 0.7,
                "deep_rooting": 0.8,
                "water_storage": 0.7
            },
            "moderate": {
                "water_efficiency": 0.6,
                "drought_recovery": 0.6,
                "deep_rooting": 0.6,
                "water_storage": 0.6
            },
            "low": {
                "water_efficiency": 0.4,
                "drought_recovery": 0.4,
                "deep_rooting": 0.4,
                "water_storage": 0.4
            }
        }
    
    async def _assess_current_risk(self, request: DiversificationRequest) -> Dict[str, Any]:
        """Assess current risk profile of the farm."""
        current_crops = request.current_crops
        if not current_crops:
            return {
                "diversification_index": 0.0,
                "drought_risk": 0.8,
                "market_risk": 0.7,
                "yield_stability": 0.5,
                "soil_health_risk": 0.6
            }
        
        # Calculate current diversification
        diversification_index = 1.0 - (1.0 / len(current_crops)) if len(current_crops) > 1 else 0.0
        
        # Assess risks based on current crops
        drought_risk = 0.0
        market_risk = 0.0
        yield_stability = 0.0
        soil_health_risk = 0.0
        
        for crop in current_crops:
            if crop in self.crop_database:
                crop_data = self.crop_database[crop]
                drought_risk += (1.0 - self._get_drought_tolerance_score(crop_data["drought_tolerance"]))
                market_risk += crop_data["market_price_volatility"]
                yield_stability += crop_data["yield_stability_score"]
                soil_health_risk += (1.0 - crop_data["soil_health_contribution"])
        
        # Average the risks
        num_crops = len(current_crops)
        drought_risk /= num_crops
        market_risk /= num_crops
        yield_stability /= num_crops
        soil_health_risk /= num_crops
        
        return {
            "diversification_index": diversification_index,
            "drought_risk": drought_risk,
            "market_risk": market_risk,
            "yield_stability": yield_stability,
            "soil_health_risk": soil_health_risk,
            "current_crops": current_crops
        }
    
    def _get_drought_tolerance_score(self, tolerance_level: DroughtToleranceLevel) -> float:
        """Convert drought tolerance level to numeric score."""
        tolerance_scores = {
            DroughtToleranceLevel.VERY_HIGH: 0.9,
            DroughtToleranceLevel.HIGH: 0.8,
            DroughtToleranceLevel.MODERATE: 0.6,
            DroughtToleranceLevel.LOW: 0.4
        }
        return tolerance_scores.get(tolerance_level, 0.5)
    
    async def _generate_diversification_strategies(self, request: DiversificationRequest) -> List[DiversificationStrategy]:
        """Generate appropriate diversification strategies based on farm characteristics."""
        strategies = []
        
        # Always include crop rotation for drought resilience
        strategies.append(DiversificationStrategy.CROP_ROTATION)
        
        # Add temporal diversification for drought risk reduction
        strategies.append(DiversificationStrategy.TEMPORAL_DIVERSIFICATION)
        
        # Add spatial diversification if multiple fields
        if len(request.field_ids) > 1:
            strategies.append(DiversificationStrategy.SPATIAL_DIVERSIFICATION)
        
        # Add market diversification if market preferences are diverse
        if len(request.market_preferences) > 1:
            strategies.append(DiversificationStrategy.MARKET_DIVERSIFICATION)
        
        # Add intercropping for small farms or specific goals
        if request.total_acres < 100 or "soil_health" in request.sustainability_goals:
            strategies.append(DiversificationStrategy.INTERCROPPING)
        
        return strategies
    
    async def _create_optimized_portfolios(self, request: DiversificationRequest, strategies: List[DiversificationStrategy]) -> List[DiversificationPortfolio]:
        """Create optimized portfolios for each strategy."""
        portfolios = []
        
        for strategy in strategies:
            portfolio = await self.optimize_crop_portfolio(request)
            portfolio.portfolio_name = f"{strategy.value.replace('_', ' ').title()} Portfolio"
            portfolios.append(portfolio)
        
        return portfolios
    
    async def _assess_market_risks(self, portfolios: List[DiversificationPortfolio]) -> Dict[str, MarketRiskAssessment]:
        """Assess market risks for portfolios."""
        market_risks = {}
        
        for portfolio in portfolios:
            portfolio_risk = await self._calculate_portfolio_market_risk(portfolio)
            market_risks[str(portfolio.portfolio_id)] = portfolio_risk
        
        return market_risks
    
    async def _calculate_portfolio_market_risk(self, portfolio: DiversificationPortfolio) -> MarketRiskAssessment:
        """Calculate market risk for a portfolio."""
        total_risk = 0.0
        total_weight = 0.0
        
        for crop in portfolio.crops:
            weight = portfolio.crop_allocation.get(crop.crop_name, 0.0) / 100.0
            crop_risk = crop.market_price_volatility
            total_risk += crop_risk * weight
            total_weight += weight
        
        overall_risk = total_risk / total_weight if total_weight > 0 else 0.0
        
        return MarketRiskAssessment(
            crop_id=portfolio.portfolio_id,
            risk_types=[MarketRiskType.PRICE_VOLATILITY],
            price_volatility_score=overall_risk,
            demand_stability_score=0.7,  # Would be calculated from market data
            supply_chain_risk_score=0.5,
            weather_sensitivity_score=0.6,
            policy_risk_score=0.5,
            overall_market_risk=overall_risk,
            risk_mitigation_strategies=["Diversification", "Crop insurance", "Market contracts"]
        )
    
    async def _generate_recommendations(self, request: DiversificationRequest, portfolios: List[DiversificationPortfolio], 
                                      market_risks: Dict[str, MarketRiskAssessment], current_risk: Dict[str, Any]) -> List[DiversificationRecommendation]:
        """Generate diversification recommendations."""
        recommendations = []
        
        for portfolio in portfolios:
            # Calculate benefits
            risk_reduction = await self._calculate_risk_reduction(current_risk, portfolio)
            yield_stability_improvement = await self._calculate_yield_stability_improvement(current_risk, portfolio)
            water_savings = await self._calculate_water_savings(portfolio)
            soil_health_improvement = await self._calculate_soil_health_improvement(current_risk, portfolio)
            
            # Calculate costs and ROI
            implementation_cost = await self._calculate_implementation_cost(portfolio, request)
            expected_roi = await self._calculate_expected_roi(portfolio, implementation_cost)
            payback_period = await self._calculate_payback_period(implementation_cost, expected_roi)
            
            # Determine strategy type
            strategy_type = DiversificationStrategy.CROP_ROTATION  # Default
            
            recommendation = DiversificationRecommendation(
                recommendation_id=uuid4(),
                farm_id=request.farm_id,
                strategy_type=strategy_type,
                recommended_portfolio=portfolio,
                risk_reduction_percent=risk_reduction,
                yield_stability_improvement=yield_stability_improvement,
                water_savings_percent=water_savings,
                soil_health_improvement=soil_health_improvement,
                implementation_cost=implementation_cost,
                expected_roi_percent=expected_roi,
                payback_period_years=payback_period,
                confidence_score=0.8,  # Would be calculated based on data quality
                implementation_timeline="3-6 months",
                monitoring_recommendations=[
                    "Monitor soil moisture levels weekly",
                    "Track yield performance by crop",
                    "Assess market price trends monthly",
                    "Evaluate soil health indicators quarterly"
                ]
            )
            
            recommendations.append(recommendation)
        
        return recommendations
    
    async def _calculate_risk_reduction(self, current_risk: Dict[str, Any], portfolio: DiversificationPortfolio) -> float:
        """Calculate risk reduction percentage."""
        current_drought_risk = current_risk.get("drought_risk", 0.8)
        portfolio_drought_risk = 1.0 - portfolio.water_efficiency_score
        
        risk_reduction = max(0, (current_drought_risk - portfolio_drought_risk) / current_drought_risk * 100)
        return min(risk_reduction, 100.0)
    
    async def _calculate_yield_stability_improvement(self, current_risk: Dict[str, Any], portfolio: DiversificationPortfolio) -> float:
        """Calculate yield stability improvement percentage."""
        current_stability = current_risk.get("yield_stability", 0.5)
        portfolio_stability = portfolio.risk_score  # Lower risk score = higher stability
        
        improvement = max(0, (portfolio_stability - current_stability) / current_stability * 100)
        return min(improvement, 100.0)
    
    async def _calculate_water_savings(self, portfolio: DiversificationPortfolio) -> float:
        """Calculate water savings percentage."""
        return portfolio.water_efficiency_score * 100
    
    async def _calculate_soil_health_improvement(self, current_risk: Dict[str, Any], portfolio: DiversificationPortfolio) -> float:
        """Calculate soil health improvement percentage."""
        current_soil_health = current_risk.get("soil_health_risk", 0.6)
        portfolio_soil_health = 1.0 - portfolio.soil_health_score
        
        improvement = max(0, (portfolio_soil_health - current_soil_health) / current_soil_health * 100)
        return min(improvement, 100.0)
    
    async def _calculate_implementation_cost(self, portfolio: DiversificationPortfolio, request: DiversificationRequest) -> Decimal:
        """Calculate implementation cost per acre."""
        # Base cost per acre for diversification
        base_cost = Decimal("50.00")
        
        # Add costs for new crops
        new_crop_cost = Decimal("25.00") * len(portfolio.crops)
        
        # Add equipment costs if needed
        equipment_cost = Decimal("0.00")
        if request.equipment_available:
            equipment_cost = Decimal("10.00")
        
        total_cost = base_cost + new_crop_cost + equipment_cost
        return total_cost
    
    async def _calculate_expected_roi(self, portfolio: DiversificationPortfolio, implementation_cost: Decimal) -> float:
        """Calculate expected ROI percentage."""
        if implementation_cost == 0:
            return 0.0
        
        # Simplified ROI calculation
        expected_revenue = portfolio.expected_revenue
        roi_percent = float((expected_revenue - implementation_cost) / implementation_cost * 100)
        return max(roi_percent, 0.0)
    
    async def _calculate_payback_period(self, implementation_cost: Decimal, expected_roi_percent: float) -> float:
        """Calculate payback period in years."""
        if expected_roi_percent <= 0:
            return float('inf')
        
        payback_period = 100.0 / expected_roi_percent
        return min(payback_period, 10.0)  # Cap at 10 years
    
    async def _calculate_economic_analysis(self, recommendations: List[DiversificationRecommendation]) -> Dict[str, Any]:
        """Calculate comprehensive economic analysis."""
        if not recommendations:
            return {}
        
        total_cost = sum(rec.implementation_cost for rec in recommendations)
        avg_roi = statistics.mean([rec.expected_roi_percent for rec in recommendations])
        avg_payback = statistics.mean([rec.payback_period_years for rec in recommendations])
        
        return {
            "total_implementation_cost": float(total_cost),
            "average_roi_percent": avg_roi,
            "average_payback_period_years": avg_payback,
            "cost_benefit_ratio": avg_roi / 100.0 if avg_roi > 0 else 0.0,
            "risk_adjusted_return": avg_roi * 0.8,  # Adjust for risk
            "recommendations": len(recommendations)
        }
    
    async def _create_monitoring_plan(self, recommendations: List[DiversificationRecommendation]) -> Dict[str, Any]:
        """Create monitoring plan for diversification implementation."""
        return {
            "soil_monitoring": {
                "frequency": "weekly",
                "parameters": ["moisture", "organic_matter", "pH", "nutrients"],
                "tools": ["soil probes", "lab tests", "visual assessment"]
            },
            "crop_monitoring": {
                "frequency": "bi-weekly",
                "parameters": ["growth_stage", "yield_potential", "disease_pressure", "pest_pressure"],
                "tools": ["field_scouting", "drones", "satellite_imagery"]
            },
            "market_monitoring": {
                "frequency": "monthly",
                "parameters": ["price_trends", "demand_patterns", "supply_conditions"],
                "tools": ["market_reports", "price_feeds", "industry_analysis"]
            },
            "performance_tracking": {
                "frequency": "quarterly",
                "parameters": ["yield_comparison", "cost_analysis", "profitability"],
                "tools": ["farm_records", "financial_software", "benchmarking"]
            }
        }
    
    async def _determine_implementation_priority(self, recommendations: List[DiversificationRecommendation]) -> List[str]:
        """Determine implementation priority order."""
        # Sort by risk reduction and ROI
        sorted_recs = sorted(recommendations, key=lambda x: (x.risk_reduction_percent, x.expected_roi_percent), reverse=True)
        return [rec.recommended_portfolio.portfolio_name for rec in sorted_recs]
    
    async def _calculate_confidence_score(self, recommendations: List[DiversificationRecommendation], request: DiversificationRequest) -> float:
        """Calculate overall confidence score."""
        if not recommendations:
            return 0.0
        
        # Base confidence on data availability and recommendation quality
        base_confidence = 0.7
        
        # Increase confidence based on data completeness
        if request.climate_zone:
            base_confidence += 0.1
        if request.soil_types:
            base_confidence += 0.1
        if request.irrigation_capacity:
            base_confidence += 0.1
        
        # Increase confidence based on recommendation quality
        avg_confidence = statistics.mean([rec.confidence_score for rec in recommendations])
        base_confidence = (base_confidence + avg_confidence) / 2
        
        return min(base_confidence, 1.0)
    
    async def _compare_risk_levels(self, current_risk: Dict[str, Any], recommendations: List[DiversificationRecommendation]) -> Dict[str, float]:
        """Compare risk levels between current and recommended portfolios."""
        comparison = {
            "current_drought_risk": current_risk.get("drought_risk", 0.8),
            "current_market_risk": current_risk.get("market_risk", 0.7),
            "current_yield_stability": current_risk.get("yield_stability", 0.5)
        }
        
        if recommendations:
            best_rec = max(recommendations, key=lambda x: x.risk_reduction_percent)
            comparison.update({
                "recommended_drought_risk": 1.0 - best_rec.recommended_portfolio.water_efficiency_score,
                "recommended_market_risk": best_rec.recommended_portfolio.risk_score,
                "recommended_yield_stability": 1.0 - best_rec.recommended_portfolio.risk_score
            })
        
        return comparison
    
    async def _get_available_crops(self, request: DiversificationRequest) -> List[CropRiskProfile]:
        """Get available crops for the region and constraints."""
        available_crops = []
        
        for crop_name, crop_data in self.crop_database.items():
            # Filter by climate zone if specified
            if request.climate_zone:
                # Simplified climate zone filtering
                if crop_name in ["corn", "soybeans", "wheat"]:  # Common crops for most zones
                    pass
                elif crop_name in ["sorghum", "millet"] and "arid" in request.climate_zone.lower():
                    pass
                else:
                    continue
            
            # Create crop risk profile
            crop_profile = CropRiskProfile(
                crop_id=uuid4(),
                crop_name=crop_name,
                crop_category=crop_data["category"],
                drought_tolerance=crop_data["drought_tolerance"],
                water_requirement_mm=crop_data["water_requirement_mm"],
                yield_stability_score=crop_data["yield_stability_score"],
                market_price_volatility=crop_data["market_price_volatility"],
                disease_susceptibility=crop_data["disease_susceptibility"],
                pest_susceptibility=crop_data["pest_susceptibility"],
                soil_health_contribution=crop_data["soil_health_contribution"],
                nitrogen_fixation=crop_data["nitrogen_fixation"],
                root_depth_cm=crop_data["root_depth_cm"],
                maturity_days=crop_data["maturity_days"]
            )
            
            available_crops.append(crop_profile)
        
        return available_crops
    
    async def _filter_crops_by_constraints(self, crops: List[CropRiskProfile], request: DiversificationRequest) -> List[CropRiskProfile]:
        """Filter crops based on farm constraints."""
        filtered_crops = []
        
        for crop in crops:
            # Filter by irrigation capacity
            if request.irrigation_capacity and crop.water_requirement_mm > request.irrigation_capacity:
                continue
            
            # Filter by risk tolerance
            if request.risk_tolerance == RiskLevel.LOW and crop.market_price_volatility > 0.7:
                continue
            
            # Filter by sustainability goals
            if "soil_health" in request.sustainability_goals and crop.soil_health_contribution < 0.5:
                continue
            
            filtered_crops.append(crop)
        
        return filtered_crops
    
    async def _calculate_diversification_scores(self, crops: List[CropRiskProfile]) -> Dict[str, float]:
        """Calculate diversification scores for crops."""
        scores = {}
        
        for crop in crops:
            # Calculate diversification score based on multiple factors
            score = (
                crop.yield_stability_score * 0.3 +
                (1.0 - crop.market_price_volatility) * 0.2 +
                crop.soil_health_contribution * 0.2 +
                self._get_drought_tolerance_score(crop.drought_tolerance) * 0.3
            )
            scores[crop.crop_name] = score
        
        return scores
    
    async def _optimize_allocation(self, crops: List[CropRiskProfile], scores: Dict[str, float], request: DiversificationRequest) -> Dict[str, float]:
        """Optimize crop allocation using portfolio theory."""
        # Sort crops by diversification score
        sorted_crops = sorted(crops, key=lambda x: scores[x.crop_name], reverse=True)
        
        # Allocate based on diversification goals and risk tolerance
        allocation = {}
        
        if request.risk_tolerance == RiskLevel.LOW:
            # Conservative allocation - focus on stable crops
            stable_crops = [c for c in sorted_crops if c.yield_stability_score > 0.8]
            if stable_crops:
                allocation[stable_crops[0].crop_name] = 60.0
                if len(stable_crops) > 1:
                    allocation[stable_crops[1].crop_name] = 40.0
        elif request.risk_tolerance == RiskLevel.MODERATE:
            # Balanced allocation
            for i, crop in enumerate(sorted_crops[:3]):
                allocation[crop.crop_name] = 40.0 - (i * 10.0)
        else:
            # Diversified allocation
            num_crops = min(len(sorted_crops), 4)
            base_allocation = 100.0 / num_crops
            
            for i, crop in enumerate(sorted_crops[:num_crops]):
                allocation[crop.crop_name] = base_allocation
        
        # Ensure allocation sums to 100%
        total = sum(allocation.values())
        if total > 0:
            for crop_name in allocation:
                allocation[crop_name] = (allocation[crop_name] / total) * 100.0
        
        return allocation
    
    async def _create_portfolio(self, farm_id: UUID, crops: List[CropRiskProfile], allocation: Dict[str, float], total_acres: float) -> DiversificationPortfolio:
        """Create diversification portfolio."""
        # Filter crops that have allocation
        allocated_crops = [c for c in crops if c.crop_name in allocation]
        
        # Calculate portfolio metrics
        diversification_index = len(allocated_crops) / 10.0  # Normalize to 0-1
        risk_score = statistics.mean([c.market_price_volatility for c in allocated_crops])
        water_efficiency = statistics.mean([self._get_drought_tolerance_score(c.drought_tolerance) for c in allocated_crops])
        soil_health = statistics.mean([c.soil_health_contribution for c in allocated_crops])
        
        # Calculate expected yield and revenue (simplified)
        expected_yield = statistics.mean([100.0 for _ in allocated_crops])  # Would use actual yield data
        expected_revenue = Decimal(str(expected_yield * 4.0))  # Simplified revenue calculation
        
        return DiversificationPortfolio(
            portfolio_id=uuid4(),
            farm_id=farm_id,
            portfolio_name="Optimized Diversification Portfolio",
            crops=allocated_crops,
            total_acres=total_acres,
            crop_allocation=allocation,
            diversification_index=diversification_index,
            risk_score=risk_score,
            expected_yield=expected_yield,
            expected_revenue=expected_revenue,
            water_efficiency_score=water_efficiency,
            soil_health_score=soil_health
        )
    
    async def _calculate_water_efficiency(self, portfolio: DiversificationPortfolio) -> float:
        """Calculate water efficiency score for portfolio."""
        if not portfolio.crops:
            return 0.0
        
        total_water_requirement = sum(crop.water_requirement_mm for crop in portfolio.crops)
        avg_water_requirement = total_water_requirement / len(portfolio.crops)
        
        # Lower water requirement = higher efficiency
        efficiency = max(0, 1.0 - (avg_water_requirement / 600.0))  # Normalize to 600mm max
        return min(efficiency, 1.0)
    
    async def _calculate_yield_stability(self, portfolio: DiversificationPortfolio) -> float:
        """Calculate yield stability score for portfolio."""
        if not portfolio.crops:
            return 0.0
        
        return statistics.mean([crop.yield_stability_score for crop in portfolio.crops])
    
    async def _calculate_soil_health_benefits(self, portfolio: DiversificationPortfolio) -> float:
        """Calculate soil health benefits for portfolio."""
        if not portfolio.crops:
            return 0.0
        
        return statistics.mean([crop.soil_health_contribution for crop in portfolio.crops])
    
    async def _assess_temporal_risk_distribution(self, portfolio: DiversificationPortfolio) -> float:
        """Assess temporal risk distribution."""
        if not portfolio.crops:
            return 0.0
        
        # Calculate maturity spread
        maturities = [crop.maturity_days for crop in portfolio.crops]
        maturity_spread = max(maturities) - min(maturities)
        
        # Higher spread = better temporal distribution
        temporal_score = min(maturity_spread / 120.0, 1.0)  # Normalize to 120 days max spread
        return temporal_score
    
    async def _calculate_drought_resilience(self, water_efficiency: float, yield_stability: float, 
                                          soil_health: float, temporal_risk: float) -> float:
        """Calculate overall drought resilience score."""
        # Weighted average of resilience factors
        resilience = (
            water_efficiency * 0.4 +
            yield_stability * 0.3 +
            soil_health * 0.2 +
            temporal_risk * 0.1
        )
        return min(resilience, 1.0)
    
    async def _calculate_risk_reduction_percent(self, drought_resilience: float) -> float:
        """Calculate risk reduction percentage."""
        return drought_resilience * 100.0
    
    async def _generate_drought_mitigation_recommendations(self, portfolio: DiversificationPortfolio) -> List[str]:
        """Generate drought mitigation recommendations."""
        recommendations = []
        
        # Check water efficiency
        if portfolio.water_efficiency_score < 0.7:
            recommendations.append("Consider adding more drought-tolerant crops")
        
        # Check soil health
        if portfolio.soil_health_score < 0.6:
            recommendations.append("Include more nitrogen-fixing crops")
        
        # Check diversification
        if portfolio.diversification_index < 0.5:
            recommendations.append("Increase crop diversity for better risk distribution")
        
        return recommendations