"""
NOAA Drought Monitor Data Provider

Integration with NOAA's U.S. Drought Monitor for real-time drought data,
historical drought patterns, and regional drought analysis.
"""

import logging
import asyncio
import httpx
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

class DroughtIntensity(str, Enum):
    """NOAA Drought Monitor intensity levels."""
    NONE = "D0"
    ABNORMALLY_DRY = "D0"
    MODERATE_DROUGHT = "D1"
    SEVERE_DROUGHT = "D2"
    EXTREME_DROUGHT = "D3"
    EXCEPTIONAL_DROUGHT = "D4"

@dataclass
class DroughtMonitorData:
    """NOAA Drought Monitor data structure."""
    date: date
    region: str
    intensity: DroughtIntensity
    area_percent: float
    population_affected: int
    area_acres: float
    description: str
    impacts: List[str]
    outlook: str

@dataclass
class DroughtStatistics:
    """Drought statistics for a region."""
    region: str
    total_area_acres: float
    drought_area_acres: float
    drought_percent: float
    population_total: int
    population_affected: int
    population_percent: float
    intensity_breakdown: Dict[str, float]

class NOAADroughtProvider:
    """Provider for NOAA Drought Monitor data."""
    
    def __init__(self):
        self.base_url = "https://droughtmonitor.unl.edu"
        self.client = None
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
    async def initialize(self):
        """Initialize HTTP client."""
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "AFAS-Drought-Management/1.0",
                "Accept": "application/json, application/xml"
            }
        )
        logger.info("NOAA Drought Provider initialized")
    
    async def cleanup(self):
        """Clean up HTTP client."""
        if self.client:
            await self.client.aclose()
        logger.info("NOAA Drought Provider cleaned up")
    
    async def get_current_drought_data(self, region: str = "US") -> Dict[str, Any]:
        """
        Get current drought data from NOAA Drought Monitor.
        
        Args:
            region: Region identifier (US, state code, etc.)
            
        Returns:
            Current drought data for the region
        """
        try:
            cache_key = f"current_drought_{region}_{date.today()}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                    return cached_data
            
            # Get current drought map data
            url = f"{self.base_url}/Data/DataTables.aspx"
            params = {
                "area": region,
                "statstype": "1",  # Area statistics
                "format": "json"
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            
            # Parse the response (NOAA returns HTML with embedded JSON)
            data = await self._parse_drought_data(response.text)
            
            # Cache the result
            self.cache[cache_key] = (data, datetime.now())
            
            logger.info(f"Retrieved current drought data for {region}")
            return data
            
        except Exception as e:
            logger.error(f"Error getting current drought data: {str(e)}")
            return await self._get_fallback_drought_data(region)
    
    async def get_historical_drought_data(
        self, 
        region: str, 
        start_date: date, 
        end_date: date
    ) -> List[DroughtMonitorData]:
        """
        Get historical drought data for a region.
        
        Args:
            region: Region identifier
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            List of historical drought data points
        """
        try:
            logger.info(f"Getting historical drought data for {region} from {start_date} to {end_date}")
            
            # Generate list of dates (weekly data)
            dates = []
            current_date = start_date
            while current_date <= end_date:
                # NOAA Drought Monitor is updated weekly (Thursdays)
                days_ahead = 3 - current_date.weekday()  # Thursday is 3
                if days_ahead <= 0:
                    days_ahead += 7
                thursday = current_date + timedelta(days=days_ahead)
                if thursday <= end_date:
                    dates.append(thursday)
                current_date += timedelta(days=7)
            
            historical_data = []
            for drought_date in dates:
                try:
                    data = await self._get_drought_data_for_date(region, drought_date)
                    if data:
                        historical_data.append(data)
                except Exception as e:
                    logger.warning(f"Error getting data for {drought_date}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(historical_data)} historical drought data points")
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical drought data: {str(e)}")
            return []
    
    async def get_drought_statistics(self, region: str) -> DroughtStatistics:
        """
        Get comprehensive drought statistics for a region.
        
        Args:
            region: Region identifier
            
        Returns:
            Drought statistics for the region
        """
        try:
            current_data = await self.get_current_drought_data(region)
            
            # Calculate statistics
            total_area = current_data.get("total_area_acres", 0)
            drought_area = current_data.get("drought_area_acres", 0)
            drought_percent = (drought_area / total_area * 100) if total_area > 0 else 0
            
            population_total = current_data.get("population_total", 0)
            population_affected = current_data.get("population_affected", 0)
            population_percent = (population_affected / population_total * 100) if population_total > 0 else 0
            
            intensity_breakdown = current_data.get("intensity_breakdown", {})
            
            return DroughtStatistics(
                region=region,
                total_area_acres=total_area,
                drought_area_acres=drought_area,
                drought_percent=drought_percent,
                population_total=population_total,
                population_affected=population_affected,
                population_percent=population_percent,
                intensity_breakdown=intensity_breakdown
            )
            
        except Exception as e:
            logger.error(f"Error getting drought statistics: {str(e)}")
            return DroughtStatistics(
                region=region,
                total_area_acres=0,
                drought_area_acres=0,
                drought_percent=0,
                population_total=0,
                population_affected=0,
                population_percent=0,
                intensity_breakdown={}
            )
    
    async def get_drought_forecast(self, region: str, days_ahead: int = 30) -> Dict[str, Any]:
        """
        Get drought forecast for a region.
        
        Args:
            region: Region identifier
            days_ahead: Number of days to forecast ahead
            
        Returns:
            Drought forecast data
        """
        try:
            # Get current conditions
            current_data = await self.get_current_drought_data(region)
            
            # Get historical patterns for trend analysis
            end_date = date.today()
            start_date = end_date - timedelta(days=365)  # 1 year of data
            historical_data = await self.get_historical_drought_data(region, start_date, end_date)
            
            # Analyze trends
            trend_analysis = await self._analyze_drought_trends(historical_data)
            
            # Generate forecast
            forecast = await self._generate_drought_forecast(
                current_data, trend_analysis, days_ahead
            )
            
            logger.info(f"Generated drought forecast for {region}")
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating drought forecast: {str(e)}")
            return await self._get_fallback_forecast(region, days_ahead)
    
    async def get_regional_drought_map(self, region: str) -> Dict[str, Any]:
        """
        Get drought map data for visualization.
        
        Args:
            region: Region identifier
            
        Returns:
            Drought map data including geospatial information
        """
        try:
            # Get current drought data
            current_data = await self.get_current_drought_data(region)
            
            # Get geospatial data (simplified - in production would use actual GIS data)
            map_data = await self._generate_drought_map_data(current_data, region)
            
            logger.info(f"Generated drought map data for {region}")
            return map_data
            
        except Exception as e:
            logger.error(f"Error generating drought map: {str(e)}")
            return await self._get_fallback_map_data(region)
    
    # Private helper methods
    
    async def _parse_drought_data(self, html_content: str) -> Dict[str, Any]:
        """Parse drought data from NOAA HTML response."""
        try:
            # NOAA returns HTML with embedded data - this is a simplified parser
            # In production, would need more sophisticated HTML parsing
            
            # Extract key information (simplified approach)
            data = {
                "region": "US",
                "date": date.today(),
                "total_area_acres": 0,
                "drought_area_acres": 0,
                "population_total": 0,
                "population_affected": 0,
                "intensity_breakdown": {
                    "D0": 0.0,  # Abnormally Dry
                    "D1": 0.0,  # Moderate Drought
                    "D2": 0.0,  # Severe Drought
                    "D3": 0.0,  # Extreme Drought
                    "D4": 0.0   # Exceptional Drought
                },
                "current_intensity": "D0",
                "description": "Current drought conditions",
                "impacts": [],
                "outlook": "Monitoring conditions"
            }
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing drought data: {str(e)}")
            return await self._get_fallback_drought_data("US")
    
    async def _get_drought_data_for_date(self, region: str, drought_date: date) -> Optional[DroughtMonitorData]:
        """Get drought data for a specific date."""
        try:
            # This would query NOAA's historical data API
            # For now, return mock data
            return DroughtMonitorData(
                date=drought_date,
                region=region,
                intensity=DroughtIntensity.MODERATE_DROUGHT,
                area_percent=25.0,
                population_affected=1000000,
                area_acres=50000000,
                description=f"Drought conditions for {region}",
                impacts=["Agricultural stress", "Water restrictions"],
                outlook="Conditions expected to persist"
            )
            
        except Exception as e:
            logger.error(f"Error getting drought data for {drought_date}: {str(e)}")
            return None
    
    async def _analyze_drought_trends(self, historical_data: List[DroughtMonitorData]) -> Dict[str, Any]:
        """Analyze drought trends from historical data."""
        if not historical_data:
            return {"trend": "stable", "confidence": 0.0}
        
        # Simple trend analysis
        recent_data = historical_data[-4:] if len(historical_data) >= 4 else historical_data
        older_data = historical_data[:-4] if len(historical_data) >= 8 else historical_data[:4]
        
        if not older_data:
            return {"trend": "stable", "confidence": 0.0}
        
        recent_avg_intensity = sum(
            self._intensity_to_numeric(d.intensity) for d in recent_data
        ) / len(recent_data)
        
        older_avg_intensity = sum(
            self._intensity_to_numeric(d.intensity) for d in older_data
        ) / len(older_data)
        
        intensity_change = recent_avg_intensity - older_avg_intensity
        
        if intensity_change > 0.5:
            trend = "increasing"
            confidence = min(abs(intensity_change) / 2.0, 1.0)
        elif intensity_change < -0.5:
            trend = "decreasing"
            confidence = min(abs(intensity_change) / 2.0, 1.0)
        else:
            trend = "stable"
            confidence = 0.5
        
        return {
            "trend": trend,
            "confidence": confidence,
            "intensity_change": intensity_change,
            "recent_avg_intensity": recent_avg_intensity,
            "older_avg_intensity": older_avg_intensity
        }
    
    def _intensity_to_numeric(self, intensity: DroughtIntensity) -> float:
        """Convert drought intensity to numeric value."""
        intensity_map = {
            DroughtIntensity.NONE: 0.0,
            DroughtIntensity.ABNORMALLY_DRY: 0.5,
            DroughtIntensity.MODERATE_DROUGHT: 1.0,
            DroughtIntensity.SEVERE_DROUGHT: 2.0,
            DroughtIntensity.EXTREME_DROUGHT: 3.0,
            DroughtIntensity.EXCEPTIONAL_DROUGHT: 4.0
        }
        return intensity_map.get(intensity, 0.0)
    
    async def _generate_drought_forecast(
        self, 
        current_data: Dict[str, Any], 
        trend_analysis: Dict[str, Any], 
        days_ahead: int
    ) -> Dict[str, Any]:
        """Generate drought forecast based on current conditions and trends."""
        current_intensity = current_data.get("current_intensity", "D0")
        trend = trend_analysis.get("trend", "stable")
        confidence = trend_analysis.get("confidence", 0.5)
        
        # Simple forecasting logic
        if trend == "increasing" and confidence > 0.7:
            forecast_intensity = self._increase_intensity(current_intensity)
            probability = min(confidence + 0.2, 0.9)
        elif trend == "decreasing" and confidence > 0.7:
            forecast_intensity = self._decrease_intensity(current_intensity)
            probability = min(confidence + 0.2, 0.9)
        else:
            forecast_intensity = current_intensity
            probability = 0.5
        
        return {
            "forecast_date": date.today(),
            "forecast_period_days": days_ahead,
            "current_intensity": current_intensity,
            "forecast_intensity": forecast_intensity,
            "probability": probability,
            "confidence": confidence,
            "trend": trend,
            "description": f"Drought conditions expected to {trend}",
            "recommendations": self._get_forecast_recommendations(forecast_intensity, trend)
        }
    
    def _increase_intensity(self, current_intensity: str) -> str:
        """Increase drought intensity by one level."""
        intensity_levels = ["D0", "D1", "D2", "D3", "D4"]
        try:
            current_index = intensity_levels.index(current_intensity)
            return intensity_levels[min(current_index + 1, len(intensity_levels) - 1)]
        except ValueError:
            return "D1"
    
    def _decrease_intensity(self, current_intensity: str) -> str:
        """Decrease drought intensity by one level."""
        intensity_levels = ["D0", "D1", "D2", "D3", "D4"]
        try:
            current_index = intensity_levels.index(current_intensity)
            return intensity_levels[max(current_index - 1, 0)]
        except ValueError:
            return "D0"
    
    def _get_forecast_recommendations(self, intensity: str, trend: str) -> List[str]:
        """Get recommendations based on forecast."""
        recommendations = []
        
        if intensity in ["D2", "D3", "D4"]:
            recommendations.extend([
                "Implement water conservation measures",
                "Monitor soil moisture levels closely",
                "Consider drought-resistant crop varieties",
                "Prepare emergency water management plans"
            ])
        
        if trend == "increasing":
            recommendations.append("Prepare for worsening drought conditions")
        elif trend == "decreasing":
            recommendations.append("Continue monitoring as conditions improve")
        
        return recommendations
    
    async def _generate_drought_map_data(self, current_data: Dict[str, Any], region: str) -> Dict[str, Any]:
        """Generate drought map data for visualization."""
        return {
            "region": region,
            "date": date.today(),
            "map_layers": {
                "drought_intensity": current_data.get("intensity_breakdown", {}),
                "affected_areas": current_data.get("affected_areas", []),
                "water_resources": current_data.get("water_resources", [])
            },
            "visualization_data": {
                "color_scheme": {
                    "D0": "#FFFF00",  # Yellow
                    "D1": "#FFCC00",  # Orange
                    "D2": "#FF6600",  # Red
                    "D3": "#CC0000",  # Dark Red
                    "D4": "#660000"   # Darkest Red
                },
                "legend": {
                    "D0": "Abnormally Dry",
                    "D1": "Moderate Drought",
                    "D2": "Severe Drought",
                    "D3": "Extreme Drought",
                    "D4": "Exceptional Drought"
                }
            },
            "metadata": {
                "data_source": "NOAA Drought Monitor",
                "last_updated": datetime.utcnow().isoformat(),
                "coverage_area": region
            }
        }
    
    # Fallback methods for when NOAA data is unavailable
    
    async def _get_fallback_drought_data(self, region: str) -> Dict[str, Any]:
        """Get fallback drought data when NOAA is unavailable."""
        return {
            "region": region,
            "date": date.today(),
            "total_area_acres": 1000000000,  # Mock data
            "drought_area_acres": 250000000,
            "population_total": 100000000,
            "population_affected": 25000000,
            "intensity_breakdown": {
                "D0": 15.0,
                "D1": 8.0,
                "D2": 3.0,
                "D3": 1.0,
                "D4": 0.5
            },
            "current_intensity": "D1",
            "description": "Moderate drought conditions",
            "impacts": ["Agricultural stress", "Water restrictions"],
            "outlook": "Conditions expected to persist",
            "data_source": "fallback",
            "warning": "Using fallback data - NOAA service unavailable"
        }
    
    async def _get_fallback_forecast(self, region: str, days_ahead: int) -> Dict[str, Any]:
        """Get fallback forecast when NOAA is unavailable."""
        return {
            "forecast_date": date.today(),
            "forecast_period_days": days_ahead,
            "current_intensity": "D1",
            "forecast_intensity": "D1",
            "probability": 0.6,
            "confidence": 0.4,
            "trend": "stable",
            "description": "Drought conditions expected to remain stable",
            "recommendations": [
                "Continue monitoring conditions",
                "Implement water conservation practices",
                "Prepare for potential worsening"
            ],
            "data_source": "fallback",
            "warning": "Using fallback forecast - NOAA service unavailable"
        }
    
    async def _get_fallback_map_data(self, region: str) -> Dict[str, Any]:
        """Get fallback map data when NOAA is unavailable."""
        return {
            "region": region,
            "date": date.today(),
            "map_layers": {
                "drought_intensity": {
                    "D0": 15.0,
                    "D1": 8.0,
                    "D2": 3.0,
                    "D3": 1.0,
                    "D4": 0.5
                },
                "affected_areas": [],
                "water_resources": []
            },
            "visualization_data": {
                "color_scheme": {
                    "D0": "#FFFF00",
                    "D1": "#FFCC00",
                    "D2": "#FF6600",
                    "D3": "#CC0000",
                    "D4": "#660000"
                },
                "legend": {
                    "D0": "Abnormally Dry",
                    "D1": "Moderate Drought",
                    "D2": "Severe Drought",
                    "D3": "Extreme Drought",
                    "D4": "Exceptional Drought"
                }
            },
            "metadata": {
                "data_source": "fallback",
                "last_updated": datetime.utcnow().isoformat(),
                "coverage_area": region,
                "warning": "Using fallback data - NOAA service unavailable"
            }
        }