"""
Market Intelligence Models
Comprehensive data models for variety-specific market analysis and pricing intelligence.
"""

from typing import Dict, List, Optional, Any, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID


class MarketType(str, Enum):
    """Types of agricultural markets."""
    COMMODITY_EXCHANGE = "commodity_exchange"
    LOCAL_ELEVATOR = "local_elevator"
    CONTRACT_PRICING = "contract_pricing"
    SPECIALTY_MARKET = "specialty_market"
    ORGANIC_MARKET = "organic_market"
    EXPORT_MARKET = "export_market"
    DIRECT_MARKET = "direct_market"


class QualityGrade(str, Enum):
    """Quality grades for agricultural commodities."""
    # Corn grades
    CORN_NO1 = "corn_no1"
    CORN_NO2 = "corn_no2"
    CORN_NO3 = "corn_no3"
    
    # Soybean grades
    SOYBEAN_NO1 = "soybean_no1"
    SOYBEAN_NO2 = "soybean_no2"
    SOYBEAN_NO3 = "soybean_no3"
    
    # Wheat grades
    WHEAT_NO1_HARD_RED_WINTER = "wheat_no1_hrw"
    WHEAT_NO2_HARD_RED_WINTER = "wheat_no2_hrw"
    WHEAT_NO1_SOFT_RED_WINTER = "wheat_no1_srw"
    
    # Specialty grades
    FOOD_GRADE = "food_grade"
    FEED_GRADE = "feed_grade"
    PREMIUM_GRADE = "premium_grade"


class ContractType(str, Enum):
    """Types of pricing contracts."""
    CASH_PRICE = "cash_price"
    FUTURES_CONTRACT = "futures_contract"
    BASIS_CONTRACT = "basis_contract"
    FORWARD_CONTRACT = "forward_contract"
    HEDGE_CONTRACT = "hedge_contract"
    PREMIUM_CONTRACT = "premium_contract"


class VarietyMarketPrice(BaseModel):
    """Market price data specific to a crop variety."""
    
    variety_id: Optional[UUID] = Field(None, description="Unique variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Base crop name")
    
    # Price information
    price_per_unit: Decimal = Field(..., description="Price per unit")
    unit: str = Field(..., description="Price unit (bushel, ton, cwt, etc.)")
    currency: str = Field(default="USD", description="Currency code")
    
    # Market context
    market_type: MarketType = Field(..., description="Type of market")
    quality_grade: Optional[QualityGrade] = Field(None, description="Quality grade")
    contract_type: ContractType = Field(..., description="Type of pricing contract")
    
    # Location and timing
    region: str = Field(..., description="Geographic region")
    state: Optional[str] = Field(None, description="State or province")
    county: Optional[str] = Field(None, description="County or district")
    delivery_location: Optional[str] = Field(None, description="Specific delivery location")
    
    # Timing
    price_date: date = Field(..., description="Date of price")
    delivery_date: Optional[date] = Field(None, description="Expected delivery date")
    contract_expiry: Optional[date] = Field(None, description="Contract expiry date")
    
    # Premium/Discount information
    premium_discount_amount: Optional[Decimal] = Field(None, description="Premium or discount amount")
    premium_discount_reason: Optional[str] = Field(None, description="Reason for premium/discount")
    basis_level: Optional[Decimal] = Field(None, description="Basis level vs futures")
    
    # Data quality and source
    source: str = Field(..., description="Data source")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Data confidence score")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Additional context
    volume_available: Optional[Decimal] = Field(None, description="Available volume")
    minimum_order_size: Optional[Decimal] = Field(None, description="Minimum order size")
    payment_terms: Optional[str] = Field(None, description="Payment terms")
    delivery_terms: Optional[str] = Field(None, description="Delivery terms")


class MarketTrend(BaseModel):
    """Market trend analysis for a variety."""
    
    variety_id: Optional[UUID] = Field(None, description="Unique variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Base crop name")
    
    # Trend periods
    trend_7d: Optional[Decimal] = Field(None, description="7-day price trend")
    trend_30d: Optional[Decimal] = Field(None, description="30-day price trend")
    trend_90d: Optional[Decimal] = Field(None, description="90-day price trend")
    trend_1y: Optional[Decimal] = Field(None, description="1-year price trend")
    
    # Volatility metrics
    volatility_7d: Optional[float] = Field(None, description="7-day volatility")
    volatility_30d: Optional[float] = Field(None, description="30-day volatility")
    volatility_90d: Optional[float] = Field(None, description="90-day volatility")
    
    # Trend direction
    trend_direction: str = Field(..., description="Overall trend direction (up/down/stable)")
    trend_strength: str = Field(..., description="Trend strength (weak/moderate/strong)")
    
    # Seasonal patterns
    seasonal_factor: Optional[float] = Field(None, description="Seasonal adjustment factor")
    seasonal_pattern: Optional[str] = Field(None, description="Seasonal pattern description")
    
    # Market analysis
    market_sentiment: Optional[str] = Field(None, description="Market sentiment (bullish/bearish/neutral)")
    demand_outlook: Optional[str] = Field(None, description="Demand outlook (increasing/decreasing/stable)")
    supply_outlook: Optional[str] = Field(None, description="Supply outlook (tight/adequate/abundant)")
    
    # Analysis metadata
    analysis_date: date = Field(default_factory=date.today, description="Analysis date")
    data_points_used: int = Field(default=0, description="Number of data points used")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Analysis confidence")


class BasisAnalysis(BaseModel):
    """Basis analysis for variety-specific pricing."""
    
    variety_id: Optional[UUID] = Field(None, description="Unique variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Base crop name")
    
    # Basis levels
    current_basis: Decimal = Field(..., description="Current basis level")
    historical_basis_avg: Optional[Decimal] = Field(None, description="Historical average basis")
    basis_range_min: Optional[Decimal] = Field(None, description="Minimum basis in range")
    basis_range_max: Optional[Decimal] = Field(None, description="Maximum basis in range")
    
    # Basis trends
    basis_trend_30d: Optional[Decimal] = Field(None, description="30-day basis trend")
    basis_trend_90d: Optional[Decimal] = Field(None, description="90-day basis trend")
    basis_volatility: Optional[float] = Field(None, description="Basis volatility")
    
    # Location-specific basis
    location: str = Field(..., description="Location for basis analysis")
    delivery_point: Optional[str] = Field(None, description="Specific delivery point")
    transportation_cost: Optional[Decimal] = Field(None, description="Transportation cost component")
    
    # Market factors affecting basis
    local_demand_factor: Optional[float] = Field(None, description="Local demand impact on basis")
    local_supply_factor: Optional[float] = Field(None, description="Local supply impact on basis")
    quality_premium_factor: Optional[float] = Field(None, description="Quality premium impact")
    
    # Analysis metadata
    analysis_date: date = Field(default_factory=date.today, description="Analysis date")
    futures_contract: Optional[str] = Field(None, description="Reference futures contract")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Analysis confidence")


class DemandForecast(BaseModel):
    """Demand forecast for variety-specific markets."""
    
    variety_id: Optional[UUID] = Field(None, description="Unique variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Base crop name")
    
    # Forecast periods
    forecast_30d: Optional[Dict[str, Any]] = Field(None, description="30-day demand forecast")
    forecast_90d: Optional[Dict[str, Any]] = Field(None, description="90-day demand forecast")
    forecast_1y: Optional[Dict[str, Any]] = Field(None, description="1-year demand forecast")
    
    # Demand drivers
    domestic_demand: Optional[float] = Field(None, description="Domestic demand factor")
    export_demand: Optional[float] = Field(None, description="Export demand factor")
    feed_demand: Optional[float] = Field(None, description="Feed demand factor")
    industrial_demand: Optional[float] = Field(None, description="Industrial demand factor")
    
    # Market segments
    food_grade_demand: Optional[float] = Field(None, description="Food grade demand")
    feed_grade_demand: Optional[float] = Field(None, description="Feed grade demand")
    specialty_demand: Optional[float] = Field(None, description="Specialty market demand")
    organic_demand: Optional[float] = Field(None, description="Organic market demand")
    
    # Quality preferences
    quality_preferences: List[str] = Field(default_factory=list, description="Quality preferences")
    premium_potential: Optional[float] = Field(None, description="Premium potential score")
    
    # Forecast metadata
    forecast_date: date = Field(default_factory=date.today, description="Forecast date")
    forecast_horizon: int = Field(default=90, description="Forecast horizon in days")
    confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Forecast confidence")
    data_sources: List[str] = Field(default_factory=list, description="Data sources used")


class PremiumDiscountAnalysis(BaseModel):
    """Analysis of premiums and discounts for variety-specific characteristics."""
    
    variety_id: Optional[UUID] = Field(None, description="Unique variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Base crop name")
    
    # Premium/Discount amounts
    current_premium_discount: Decimal = Field(default=Decimal('0'), description="Current premium/discount")
    premium_discount_percent: Optional[float] = Field(None, description="Premium/discount as percentage")
    
    # Quality-based premiums/discounts
    protein_premium: Optional[Decimal] = Field(None, description="Protein content premium")
    oil_premium: Optional[Decimal] = Field(None, description="Oil content premium")
    moisture_discount: Optional[Decimal] = Field(None, description="Moisture content discount")
    damage_discount: Optional[Decimal] = Field(None, description="Damage discount")
    
    # Market-specific premiums/discounts
    organic_premium: Optional[Decimal] = Field(None, description="Organic certification premium")
    non_gmo_premium: Optional[Decimal] = Field(None, description="Non-GMO premium")
    identity_preserved_premium: Optional[Decimal] = Field(None, description="Identity preserved premium")
    
    # Contract-based premiums/discounts
    delivery_timing_premium: Optional[Decimal] = Field(None, description="Delivery timing premium")
    volume_premium: Optional[Decimal] = Field(None, description="Volume premium")
    payment_terms_premium: Optional[Decimal] = Field(None, description="Payment terms premium")
    
    # Analysis context
    market_location: str = Field(..., description="Market location")
    analysis_date: date = Field(default_factory=date.today, description="Analysis date")
    reference_price: Decimal = Field(..., description="Reference base price")
    
    # Analysis metadata
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Analysis confidence")
    data_sources: List[str] = Field(default_factory=list, description="Data sources")


class MarketIntelligenceReport(BaseModel):
    """Comprehensive market intelligence report for a variety."""
    
    variety_id: Optional[UUID] = Field(None, description="Unique variety identifier")
    variety_name: str = Field(..., description="Variety name")
    crop_name: str = Field(..., description="Base crop name")
    
    # Current market data
    current_prices: List[VarietyMarketPrice] = Field(default_factory=list, description="Current market prices")
    market_trends: Optional[MarketTrend] = Field(None, description="Market trend analysis")
    basis_analysis: Optional[BasisAnalysis] = Field(None, description="Basis analysis")
    demand_forecast: Optional[DemandForecast] = Field(None, description="Demand forecast")
    premium_discount_analysis: Optional[PremiumDiscountAnalysis] = Field(None, description="Premium/discount analysis")
    
    # Market opportunities
    market_opportunities: List[str] = Field(default_factory=list, description="Identified market opportunities")
    risk_factors: List[str] = Field(default_factory=list, description="Market risk factors")
    competitive_advantages: List[str] = Field(default_factory=list, description="Competitive advantages")
    
    # Recommendations
    pricing_recommendations: List[str] = Field(default_factory=list, description="Pricing recommendations")
    market_timing_recommendations: List[str] = Field(default_factory=list, description="Market timing recommendations")
    contract_recommendations: List[str] = Field(default_factory=list, description="Contract recommendations")
    
    # Report metadata
    report_date: date = Field(default_factory=date.today, description="Report date")
    report_period: str = Field(default="30d", description="Analysis period")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall report confidence")
    data_quality_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data quality score")
    
    # Analysis summary
    executive_summary: Optional[str] = Field(None, description="Executive summary")
    key_insights: List[str] = Field(default_factory=list, description="Key insights")
    market_outlook: Optional[str] = Field(None, description="Market outlook")


class MarketIntelligenceRequest(BaseModel):
    """Request model for market intelligence analysis."""
    
    variety_ids: Optional[List[UUID]] = Field(None, description="Specific variety IDs to analyze")
    variety_names: Optional[List[str]] = Field(None, description="Variety names to analyze")
    crop_names: Optional[List[str]] = Field(None, description="Crop names to analyze")
    
    # Geographic scope
    regions: Optional[List[str]] = Field(None, description="Geographic regions")
    states: Optional[List[str]] = Field(None, description="States")
    counties: Optional[List[str]] = Field(None, description="Counties")
    
    # Market scope
    market_types: Optional[List[MarketType]] = Field(None, description="Market types to include")
    quality_grades: Optional[List[QualityGrade]] = Field(None, description="Quality grades to include")
    contract_types: Optional[List[ContractType]] = Field(None, description="Contract types to include")
    
    # Analysis parameters
    analysis_period: str = Field(default="30d", description="Analysis period")
    include_trends: bool = Field(default=True, description="Include trend analysis")
    include_basis: bool = Field(default=True, description="Include basis analysis")
    include_demand_forecast: bool = Field(default=True, description="Include demand forecast")
    include_premium_discount: bool = Field(default=True, description="Include premium/discount analysis")
    
    # Data quality requirements
    min_confidence: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum data confidence")
    min_data_points: int = Field(default=5, ge=1, description="Minimum data points required")
    
    # Output preferences
    include_recommendations: bool = Field(default=True, description="Include recommendations")
    include_executive_summary: bool = Field(default=True, description="Include executive summary")
    detail_level: str = Field(default="standard", description="Detail level (basic/standard/comprehensive)")


class MarketIntelligenceResponse(BaseModel):
    """Response model for market intelligence analysis."""
    
    request_id: str = Field(..., description="Unique request identifier")
    reports: List[MarketIntelligenceReport] = Field(default_factory=list, description="Market intelligence reports")
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")
    processing_time_ms: float = Field(default=0.0, description="Processing time in milliseconds")
    data_sources_used: List[str] = Field(default_factory=list, description="Data sources used")
    
    # Quality metrics
    overall_confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Overall analysis confidence")
    data_coverage_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Data coverage score")
    
    # Summary statistics
    total_varieties_analyzed: int = Field(default=0, description="Total varieties analyzed")
    total_markets_analyzed: int = Field(default=0, description="Total markets analyzed")
    price_points_collected: int = Field(default=0, description="Price points collected")
    
    # Warnings and limitations
    warnings: List[str] = Field(default_factory=list, description="Analysis warnings")
    limitations: List[str] = Field(default_factory=list, description="Analysis limitations")
    data_gaps: List[str] = Field(default_factory=list, description="Identified data gaps")