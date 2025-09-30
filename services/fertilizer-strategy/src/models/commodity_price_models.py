"""
Pydantic models for commodity price tracking and analysis.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class CommodityType(str, Enum):
    """Types of commodities tracked."""
    CORN = "corn"
    SOYBEAN = "soybean"
    WHEAT = "wheat"
    BARLEY = "barley"
    OATS = "oats"
    CANOLA = "canola"
    COTTON = "cotton"
    SUGAR = "sugar"


class CommodityContract(str, Enum):
    """Commodity contract types."""
    CASH = "cash"
    FUTURES = "futures"
    BASIS = "basis"
    SPREAD = "spread"


class CommoditySource(str, Enum):
    """Sources of commodity price data."""
    CBOT = "cbot"  # Chicago Board of Trade
    CME_GROUP = "cme_group"
    LOCAL_ELEVATOR = "local_elevator"
    CASH_MARKET = "cash_market"
    FUTURES_EXCHANGE = "futures_exchange"
    USDA_NASS = "usda_nass"
    FALLBACK = "fallback"


class CommodityPriceData(BaseModel):
    """Model for commodity price data."""
    
    # Commodity identification
    commodity_id: str = Field(..., description="Unique commodity identifier")
    commodity_name: str = Field(..., description="Commodity name")
    commodity_type: CommodityType = Field(..., description="Type of commodity")
    contract_type: CommodityContract = Field(..., description="Contract type")
    
    # Price information
    price_per_unit: float = Field(..., gt=0, description="Price per unit")
    unit: str = Field(..., description="Unit of measurement (bushel, ton, cwt)")
    currency: str = Field(default="USD", description="Currency code")
    
    # Contract details (for futures)
    contract_month: Optional[str] = Field(None, description="Contract month (e.g., 'H24' for March 2024)")
    contract_year: Optional[int] = Field(None, description="Contract year")
    delivery_location: Optional[str] = Field(None, description="Delivery location")
    
    # Location and source
    region: str = Field(..., description="Geographic region")
    state: Optional[str] = Field(None, description="State if applicable")
    source: CommoditySource = Field(..., description="Data source")
    
    # Price metadata
    price_date: date = Field(..., description="Date of price")
    is_spot_price: bool = Field(default=True, description="Whether this is a spot price")
    is_futures_price: bool = Field(default=False, description="Whether this is a futures price")
    
    # Market conditions
    market_conditions: Optional[Dict[str, Any]] = Field(None, description="Market condition factors")
    seasonal_factors: Optional[Dict[str, Any]] = Field(None, description="Seasonal price factors")
    
    # Quality metrics
    confidence: float = Field(..., ge=0.0, le=1.0, description="Data confidence score")
    volatility: float = Field(..., ge=0.0, description="Price volatility measure")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('price_per_unit')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v
    
    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v):
        valid_units = ['bushel', 'ton', 'cwt', 'lb', 'kg', 'metric_ton']
        if v.lower() not in valid_units:
            raise ValueError(f'Unit must be one of: {valid_units}')
        return v.lower()


class CommodityTrendAnalysis(BaseModel):
    """Model for commodity price trend analysis."""
    
    commodity_id: str = Field(..., description="Commodity identifier")
    commodity_name: str = Field(..., description="Commodity name")
    region: str = Field(..., description="Geographic region")
    
    # Current price
    current_price: float = Field(..., description="Current price per unit")
    current_date: date = Field(..., description="Current price date")
    
    # Historical prices
    price_7d_ago: Optional[float] = Field(None, description="Price 7 days ago")
    price_30d_ago: Optional[float] = Field(None, description="Price 30 days ago")
    price_90d_ago: Optional[float] = Field(None, description="Price 90 days ago")
    price_1y_ago: Optional[float] = Field(None, description="Price 1 year ago")
    
    # Trend calculations
    trend_7d_percent: Optional[float] = Field(None, description="7-day price change percentage")
    trend_30d_percent: Optional[float] = Field(None, description="30-day price change percentage")
    trend_90d_percent: Optional[float] = Field(None, description="90-day price change percentage")
    trend_1y_percent: Optional[float] = Field(None, description="1-year price change percentage")
    
    # Volatility metrics
    volatility_7d: Optional[float] = Field(None, description="7-day volatility")
    volatility_30d: Optional[float] = Field(None, description="30-day volatility")
    volatility_90d: Optional[float] = Field(None, description="90-day volatility")
    volatility_1y: Optional[float] = Field(None, description="1-year volatility")
    
    # Trend direction
    trend_direction: str = Field(..., description="Overall trend direction (up/down/stable)")
    trend_strength: str = Field(..., description="Trend strength (weak/moderate/strong)")
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    data_points_used: int = Field(..., description="Number of data points used in analysis")


class FertilizerCropPriceRatio(BaseModel):
    """Model for fertilizer-to-crop price ratio analysis."""
    
    ratio_id: str = Field(..., description="Unique ratio identifier")
    fertilizer_product: str = Field(..., description="Fertilizer product name")
    commodity_type: CommodityType = Field(..., description="Crop commodity type")
    region: str = Field(..., description="Geographic region")
    
    # Price data
    fertilizer_price: float = Field(..., description="Fertilizer price per unit")
    fertilizer_unit: str = Field(..., description="Fertilizer unit")
    crop_price: float = Field(..., description="Crop price per unit")
    crop_unit: str = Field(..., description="Crop unit")
    
    # Ratio calculations
    price_ratio: float = Field(..., description="Fertilizer price / crop price ratio")
    inverse_ratio: float = Field(..., description="Crop price / fertilizer price ratio")
    
    # Analysis
    ratio_trend: str = Field(..., description="Ratio trend direction")
    profitability_indicator: str = Field(..., description="Profitability indicator (favorable/unfavorable)")
    
    # Metadata
    analysis_date: date = Field(..., description="Analysis date")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Analysis confidence")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CommodityPriceQueryRequest(BaseModel):
    """Request model for commodity price queries."""
    
    commodity_types: Optional[List[CommodityType]] = Field(None, description="Types of commodities")
    contract_types: Optional[List[CommodityContract]] = Field(None, description="Contract types")
    regions: Optional[List[str]] = Field(None, description="Geographic regions")
    sources: Optional[List[CommoditySource]] = Field(None, description="Data sources to include")
    
    # Date range
    start_date: Optional[date] = Field(None, description="Start date for historical data")
    end_date: Optional[date] = Field(None, description="End date for historical data")
    
    # Analysis options
    include_trend_analysis: bool = Field(default=True, description="Include trend analysis")
    include_volatility: bool = Field(default=True, description="Include volatility metrics")
    include_price_ratios: bool = Field(default=False, description="Include fertilizer-crop price ratios")
    max_age_hours: int = Field(default=24, description="Maximum age of cached data in hours")


class CommodityPriceQueryResponse(BaseModel):
    """Response model for commodity price queries."""
    
    query_id: str = Field(..., description="Unique query identifier")
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Results
    prices: List[CommodityPriceData] = Field(..., description="Price data results")
    trend_analyses: Optional[List[CommodityTrendAnalysis]] = Field(None, description="Trend analysis results")
    price_ratios: Optional[List[FertilizerCropPriceRatio]] = Field(None, description="Price ratio results")
    
    # Metadata
    total_results: int = Field(..., description="Total number of results")
    data_sources_used: List[CommoditySource] = Field(..., description="Sources used for data")
    cache_hit_rate: float = Field(..., description="Percentage of data from cache")
    processing_time_ms: float = Field(..., description="Query processing time in milliseconds")


class CommodityMarketIntelligence(BaseModel):
    """Model for commodity market intelligence reports."""
    
    report_id: str = Field(..., description="Unique report identifier")
    report_date: date = Field(..., description="Report date")
    region: str = Field(..., description="Geographic region covered")
    
    # Market summary
    market_summary: str = Field(..., description="Overall market summary")
    key_trends: List[str] = Field(..., description="Key market trends")
    price_outlook: str = Field(..., description="Price outlook forecast")
    
    # Commodity analysis
    commodity_analyses: Dict[str, Dict[str, Any]] = Field(..., description="Analysis by commodity")
    
    # Fertilizer-crop correlations
    price_correlations: Dict[str, float] = Field(..., description="Price correlations between commodities and fertilizers")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Market recommendations")
    
    # Metadata
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Report confidence")
    data_sources: List[CommoditySource] = Field(..., description="Sources used")
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class BasisAnalysis(BaseModel):
    """Model for basis analysis (cash price - futures price)."""
    
    basis_id: str = Field(..., description="Unique basis identifier")
    commodity_type: CommodityType = Field(..., description="Commodity type")
    region: str = Field(..., description="Geographic region")
    
    # Price data
    cash_price: float = Field(..., description="Local cash price")
    futures_price: float = Field(..., description="Futures price")
    basis_value: float = Field(..., description="Basis value (cash - futures)")
    
    # Analysis
    basis_trend: str = Field(..., description="Basis trend direction")
    basis_strength: str = Field(..., description="Basis strength (weak/moderate/strong)")
    
    # Metadata
    analysis_date: date = Field(..., description="Analysis date")
    delivery_location: str = Field(..., description="Delivery location")
    created_at: datetime = Field(default_factory=datetime.utcnow)