"""
Pydantic models for fertilizer price tracking and analysis.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum


class FertilizerType(str, Enum):
    """Types of fertilizers tracked."""
    NITROGEN = "nitrogen"
    PHOSPHORUS = "phosphorus"
    POTASSIUM = "potassium"
    BLEND = "blend"
    ORGANIC = "organic"
    MICRONUTRIENT = "micronutrient"


class FertilizerProduct(str, Enum):
    """Specific fertilizer products."""
    # Nitrogen products
    UREA = "urea"
    ANHYDROUS_AMMONIA = "anhydrous_ammonia"
    AMMONIUM_NITRATE = "ammonium_nitrate"
    AMMONIUM_SULFATE = "ammonium_sulfate"
    UAN = "uan"  # Urea Ammonium Nitrate
    
    # Phosphorus products
    DAP = "dap"  # Diammonium Phosphate
    MAP = "map"  # Monoammonium Phosphate
    TRIPLE_SUPERPHOSPHATE = "triple_superphosphate"
    
    # Potassium products
    MURIATE_OF_POTASH = "muriate_of_potash"
    POTASSIUM_SULFATE = "potassium_sulfate"
    
    # Blends
    NPK_BLEND = "npk_blend"
    CUSTOM_BLEND = "custom_blend"


class PriceSource(str, Enum):
    """Sources of price data."""
    USDA_NASS = "usda_nass"
    CME_GROUP = "cme_group"
    MANUFACTURER = "manufacturer"
    REGIONAL_DEALER = "regional_dealer"
    COMMODITY_EXCHANGE = "commodity_exchange"
    FALLBACK = "fallback"


class FertilizerPriceData(BaseModel):
    """Model for fertilizer price data."""
    
    # Product identification
    product_id: str = Field(..., description="Unique product identifier")
    product_name: str = Field(..., description="Product name")
    fertilizer_type: FertilizerType = Field(..., description="Type of fertilizer")
    specific_product: FertilizerProduct = Field(..., description="Specific product type")
    
    # Price information
    price_per_unit: float = Field(..., gt=0, description="Price per unit")
    unit: str = Field(..., description="Unit of measurement (ton, cwt, lb)")
    currency: str = Field(default="USD", description="Currency code")
    
    # Location and source
    region: str = Field(..., description="Geographic region")
    state: Optional[str] = Field(None, description="State if applicable")
    source: PriceSource = Field(..., description="Data source")
    
    # Price metadata
    price_date: date = Field(..., description="Date of price")
    is_spot_price: bool = Field(default=True, description="Whether this is a spot price")
    is_contract_price: bool = Field(default=False, description="Whether this is a contract price")
    
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
        valid_units = ['ton', 'cwt', 'lb', 'kg', 'metric_ton']
        if v.lower() not in valid_units:
            raise ValueError(f'Unit must be one of: {valid_units}')
        return v.lower()


class PriceTrendAnalysis(BaseModel):
    """Model for price trend analysis."""
    
    product_id: str = Field(..., description="Product identifier")
    product_name: str = Field(..., description="Product name")
    region: str = Field(..., description="Geographic region")
    
    # Current price
    current_price: float = Field(..., description="Current price per unit")
    current_date: date = Field(..., description="Current price date")
    
    # Historical prices
    price_7d_ago: Optional[float] = Field(None, description="Price 7 days ago")
    price_30d_ago: Optional[float] = Field(None, description="Price 30 days ago")
    price_90d_ago: Optional[float] = Field(None, description="Price 90 days ago")
    
    # Trend calculations
    trend_7d_percent: Optional[float] = Field(None, description="7-day price change percentage")
    trend_30d_percent: Optional[float] = Field(None, description="30-day price change percentage")
    trend_90d_percent: Optional[float] = Field(None, description="90-day price change percentage")
    
    # Volatility metrics
    volatility_7d: Optional[float] = Field(None, description="7-day volatility")
    volatility_30d: Optional[float] = Field(None, description="30-day volatility")
    volatility_90d: Optional[float] = Field(None, description="90-day volatility")
    
    # Trend direction
    trend_direction: str = Field(..., description="Overall trend direction (up/down/stable)")
    trend_strength: str = Field(..., description="Trend strength (weak/moderate/strong)")
    
    # Analysis metadata
    analysis_date: datetime = Field(default_factory=datetime.utcnow)
    data_points_used: int = Field(..., description="Number of data points used in analysis")


class PriceQueryRequest(BaseModel):
    """Request model for price queries."""
    
    product_ids: Optional[List[str]] = Field(None, description="Specific product IDs to query")
    fertilizer_types: Optional[List[FertilizerType]] = Field(None, description="Types of fertilizers")
    regions: Optional[List[str]] = Field(None, description="Geographic regions")
    sources: Optional[List[PriceSource]] = Field(None, description="Data sources to include")
    
    # Date range
    start_date: Optional[date] = Field(None, description="Start date for historical data")
    end_date: Optional[date] = Field(None, description="End date for historical data")
    
    # Analysis options
    include_trend_analysis: bool = Field(default=True, description="Include trend analysis")
    include_volatility: bool = Field(default=True, description="Include volatility metrics")
    max_age_hours: int = Field(default=24, description="Maximum age of cached data in hours")


class PriceQueryResponse(BaseModel):
    """Response model for price queries."""
    
    query_id: str = Field(..., description="Unique query identifier")
    request_timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Results
    prices: List[FertilizerPriceData] = Field(..., description="Price data results")
    trend_analyses: Optional[List[PriceTrendAnalysis]] = Field(None, description="Trend analysis results")
    
    # Metadata
    total_results: int = Field(..., description="Total number of results")
    data_sources_used: List[PriceSource] = Field(..., description="Sources used for data")
    cache_hit_rate: float = Field(..., description="Percentage of data from cache")
    processing_time_ms: float = Field(..., description="Query processing time in milliseconds")


class PriceUpdateRequest(BaseModel):
    """Request model for updating prices."""
    
    product_id: str = Field(..., description="Product to update")
    region: str = Field(..., description="Region for price update")
    force_update: bool = Field(default=False, description="Force update even if recent data exists")


class PriceUpdateResponse(BaseModel):
    """Response model for price updates."""
    
    product_id: str = Field(..., description="Product updated")
    region: str = Field(..., description="Region updated")
    success: bool = Field(..., description="Whether update was successful")
    new_price: Optional[FertilizerPriceData] = Field(None, description="New price data")
    error_message: Optional[str] = Field(None, description="Error message if update failed")
    update_timestamp: datetime = Field(default_factory=datetime.utcnow)


class MarketIntelligenceReport(BaseModel):
    """Model for market intelligence reports."""
    
    report_id: str = Field(..., description="Unique report identifier")
    report_date: date = Field(..., description="Report date")
    region: str = Field(..., description="Geographic region covered")
    
    # Market summary
    market_summary: str = Field(..., description="Overall market summary")
    key_trends: List[str] = Field(..., description="Key market trends")
    price_outlook: str = Field(..., description="Price outlook forecast")
    
    # Product analysis
    product_analyses: Dict[str, Dict[str, Any]] = Field(..., description="Analysis by product")
    
    # Recommendations
    recommendations: List[str] = Field(..., description="Market recommendations")
    
    # Metadata
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Report confidence")
    data_sources: List[PriceSource] = Field(..., description="Sources used")
    generated_at: datetime = Field(default_factory=datetime.utcnow)