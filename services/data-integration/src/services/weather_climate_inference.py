"""
Weather-based Climate Zone Inference Service
Infers climate zones from historical weather data patterns.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import asyncio
import statistics

logger = logging.getLogger(__name__)


@dataclass
class WeatherPattern:
    """Weather pattern analysis result."""
    temperature_stats: Dict
    precipitation_stats: Dict
    growing_degree_days: float
    frost_dates: Dict
    growing_season_length: int
    climate_indicators: Dict


@dataclass
class ClimateInference:
    """Climate inference from weather data."""
    inferred_usda_zone: str
    inferred_koppen_type: str
    confidence_score: float
    weather_pattern: WeatherPattern
    analysis_period: Dict
    data_quality: Dict


class WeatherClimateInference:
    """Service for inferring climate zones from weather data."""
    
    def __init__(self):
        self.min_data_years = 3  # Minimum years of data for reliable inference
        self.growing_season_threshold = 50  # °F threshold for growing season
        self.frost_threshold = 32  # °F frost threshold
    
    async def infer_climate_from_weather(
        self,
        weather_data: List[Dict],
        latitude: float,
        longitude: float
    ) -> ClimateInference:
        """
        Infer climate zone from historical weather data.
        
        Args:
            weather_data: List of daily weather observations
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            ClimateInference with inferred zones and analysis
        """
        try:
            # Analyze weather patterns
            weather_pattern = self._analyze_weather_patterns(weather_data)
            
            # Assess data quality
            data_quality = self._assess_data_quality(weather_data)
            
            # Infer USDA hardiness zone
            usda_zone = self._infer_usda_zone(weather_pattern, latitude)
            
            # Infer Köppen climate type
            koppen_type = self._infer_koppen_type(weather_pattern, latitude)
            
            # Calculate confidence
            confidence = self._calculate_inference_confidence(
                weather_pattern, data_quality, len(weather_data)
            )
            
            return ClimateInference(
                inferred_usda_zone=usda_zone,
                inferred_koppen_type=koppen_type,
                confidence_score=confidence,
                weather_pattern=weather_pattern,
                analysis_period=self._get_analysis_period(weather_data),
                data_quality=data_quality
            )
            
        except Exception as e:
            logger.error(f"Error inferring climate from weather data: {str(e)}")
            return self._get_fallback_inference(latitude, longitude)
    
    def _analyze_weather_patterns(self, weather_data: List[Dict]) -> WeatherPattern:
        """Analyze weather patterns from historical data."""
        
        # Extract temperature and precipitation data
        temperatures = []
        precipitations = []
        daily_data = []
        
        for record in weather_data:
            if 'temperature' in record and 'precipitation' in record:
                temp = record['temperature']
                precip = record['precipitation']
                date = record.get('date', datetime.now())
                
                temperatures.append(temp)
                precipitations.append(precip)
                daily_data.append({
                    'date': date,
                    'temp': temp,
                    'precip': precip
                })
        
        # Calculate temperature statistics
        temp_stats = {
            'mean_annual': statistics.mean(temperatures) if temperatures else 0,
            'min_annual': min(temperatures) if temperatures else 0,
            'max_annual': max(temperatures) if temperatures else 0,
            'coldest_month_avg': self._calculate_coldest_month_avg(daily_data),
            'warmest_month_avg': self._calculate_warmest_month_avg(daily_data)
        }
        
        # Calculate precipitation statistics
        precip_stats = {
            'annual_total': sum(precipitations) if precipitations else 0,
            'monthly_averages': self._calculate_monthly_precip_averages(daily_data),
            'driest_month': self._find_driest_month(daily_data),
            'wettest_month': self._find_wettest_month(daily_data)
        }
        
        # Calculate growing degree days
        gdd = self._calculate_growing_degree_days(daily_data)
        
        # Determine frost dates
        frost_dates = self._calculate_frost_dates(daily_data)
        
        # Calculate growing season length
        growing_season = self._calculate_growing_season_length(daily_data)
        
        # Generate climate indicators
        climate_indicators = self._generate_climate_indicators(
            temp_stats, precip_stats, gdd, growing_season
        )
        
        return WeatherPattern(
            temperature_stats=temp_stats,
            precipitation_stats=precip_stats,
            growing_degree_days=gdd,
            frost_dates=frost_dates,
            growing_season_length=growing_season,
            climate_indicators=climate_indicators
        )
    
    def _calculate_coldest_month_avg(self, daily_data: List[Dict]) -> float:
        """Calculate average temperature of coldest month."""
        
        monthly_temps = {}
        for record in daily_data:
            month = record['date'].month if hasattr(record['date'], 'month') else 1
            if month not in monthly_temps:
                monthly_temps[month] = []
            monthly_temps[month].append(record['temp'])
        
        monthly_averages = {
            month: statistics.mean(temps) 
            for month, temps in monthly_temps.items()
        }
        
        return min(monthly_averages.values()) if monthly_averages else 0
    
    def _calculate_warmest_month_avg(self, daily_data: List[Dict]) -> float:
        """Calculate average temperature of warmest month."""
        
        monthly_temps = {}
        for record in daily_data:
            month = record['date'].month if hasattr(record['date'], 'month') else 7
            if month not in monthly_temps:
                monthly_temps[month] = []
            monthly_temps[month].append(record['temp'])
        
        monthly_averages = {
            month: statistics.mean(temps) 
            for month, temps in monthly_temps.items()
        }
        
        return max(monthly_averages.values()) if monthly_averages else 70
    
    def _calculate_monthly_precip_averages(self, daily_data: List[Dict]) -> Dict:
        """Calculate monthly precipitation averages."""
        
        monthly_precip = {}
        for record in daily_data:
            month = record['date'].month if hasattr(record['date'], 'month') else 1
            if month not in monthly_precip:
                monthly_precip[month] = []
            monthly_precip[month].append(record['precip'])
        
        return {
            month: statistics.mean(precips) 
            for month, precips in monthly_precip.items()
        }
    
    def _find_driest_month(self, daily_data: List[Dict]) -> float:
        """Find driest month precipitation."""
        
        monthly_averages = self._calculate_monthly_precip_averages(daily_data)
        return min(monthly_averages.values()) if monthly_averages else 0
    
    def _find_wettest_month(self, daily_data: List[Dict]) -> float:
        """Find wettest month precipitation."""
        
        monthly_averages = self._calculate_monthly_precip_averages(daily_data)
        return max(monthly_averages.values()) if monthly_averages else 0
    
    def _calculate_growing_degree_days(self, daily_data: List[Dict]) -> float:
        """Calculate growing degree days (base 50°F)."""
        
        gdd_total = 0
        base_temp = 50  # Base temperature for GDD calculation
        
        for record in daily_data:
            daily_avg = record['temp']
            if daily_avg > base_temp:
                gdd_total += (daily_avg - base_temp)
        
        return gdd_total
    
    def _calculate_frost_dates(self, daily_data: List[Dict]) -> Dict:
        """Calculate last spring frost and first fall frost dates."""
        
        frost_dates = {
            'last_spring_frost': None,
            'first_fall_frost': None,
            'frost_free_days': 0
        }
        
        # Group data by year
        yearly_data = {}
        for record in daily_data:
            year = record['date'].year if hasattr(record['date'], 'year') else 2024
            if year not in yearly_data:
                yearly_data[year] = []
            yearly_data[year].append(record)
        
        # Calculate frost dates for each year
        spring_frosts = []
        fall_frosts = []
        
        for year, year_data in yearly_data.items():
            year_data.sort(key=lambda x: x['date'] if hasattr(x['date'], 'year') else datetime(2024, 1, 1))
            
            # Find last spring frost (before July)
            last_spring = None
            for record in year_data:
                if record['temp'] <= self.frost_threshold:
                    month = record['date'].month if hasattr(record['date'], 'month') else 1
                    if month <= 6:  # First half of year
                        last_spring = record['date']
            
            if last_spring:
                spring_frosts.append(last_spring)
            
            # Find first fall frost (after July)
            first_fall = None
            for record in reversed(year_data):
                if record['temp'] <= self.frost_threshold:
                    month = record['date'].month if hasattr(record['date'], 'month') else 12
                    if month >= 7:  # Second half of year
                        first_fall = record['date']
                        break
            
            if first_fall:
                fall_frosts.append(first_fall)
        
        # Calculate average frost dates
        if spring_frosts:
            avg_spring_day = statistics.mean([d.timetuple().tm_yday for d in spring_frosts])
            frost_dates['last_spring_frost'] = f"Day {int(avg_spring_day)} of year"
        
        if fall_frosts:
            avg_fall_day = statistics.mean([d.timetuple().tm_yday for d in fall_frosts])
            frost_dates['first_fall_frost'] = f"Day {int(avg_fall_day)} of year"
        
        # Calculate frost-free days
        if spring_frosts and fall_frosts:
            avg_spring = statistics.mean([d.timetuple().tm_yday for d in spring_frosts])
            avg_fall = statistics.mean([d.timetuple().tm_yday for d in fall_frosts])
            frost_dates['frost_free_days'] = int(avg_fall - avg_spring)
        
        return frost_dates
    
    def _calculate_growing_season_length(self, daily_data: List[Dict]) -> int:
        """Calculate growing season length in days."""
        
        growing_days = 0
        for record in daily_data:
            if record['temp'] >= self.growing_season_threshold:
                growing_days += 1
        
        # Convert to average days per year
        years_of_data = len(set(
            record['date'].year if hasattr(record['date'], 'year') else 2024 
            for record in daily_data
        ))
        
        return int(growing_days / max(1, years_of_data))
    
    def _generate_climate_indicators(
        self, 
        temp_stats: Dict, 
        precip_stats: Dict, 
        gdd: float, 
        growing_season: int
    ) -> Dict:
        """Generate climate indicators for zone inference."""
        
        return {
            'temperature_regime': self._classify_temperature_regime(temp_stats),
            'precipitation_regime': self._classify_precipitation_regime(precip_stats),
            'thermal_growing_season': 'long' if gdd > 3000 else 'moderate' if gdd > 1500 else 'short',
            'frost_risk': 'low' if temp_stats['min_annual'] > 20 else 'moderate' if temp_stats['min_annual'] > 0 else 'high',
            'agricultural_potential': self._assess_agricultural_potential(temp_stats, precip_stats, growing_season)
        }
    
    def _classify_temperature_regime(self, temp_stats: Dict) -> str:
        """Classify temperature regime."""
        
        mean_temp = temp_stats['mean_annual']
        
        if mean_temp > 75:
            return 'tropical'
        elif mean_temp > 65:
            return 'subtropical'
        elif mean_temp > 55:
            return 'temperate'
        elif mean_temp > 45:
            return 'cool_temperate'
        else:
            return 'cold'
    
    def _classify_precipitation_regime(self, precip_stats: Dict) -> str:
        """Classify precipitation regime."""
        
        annual_precip = precip_stats['annual_total']
        
        if annual_precip > 60:  # inches
            return 'wet'
        elif annual_precip > 30:
            return 'moderate'
        elif annual_precip > 15:
            return 'dry'
        else:
            return 'arid'
    
    def _assess_agricultural_potential(
        self, 
        temp_stats: Dict, 
        precip_stats: Dict, 
        growing_season: int
    ) -> str:
        """Assess agricultural potential."""
        
        if growing_season > 200 and precip_stats['annual_total'] > 30:
            return 'excellent'
        elif growing_season > 150 and precip_stats['annual_total'] > 20:
            return 'good'
        elif growing_season > 100:
            return 'moderate'
        else:
            return 'limited'
    
    def _infer_usda_zone(self, weather_pattern: WeatherPattern, latitude: float) -> str:
        """Infer USDA hardiness zone from weather pattern."""
        
        coldest_month = weather_pattern.temperature_stats['coldest_month_avg']
        
        # USDA zones based on average minimum winter temperature
        if coldest_month >= 65:
            return "13a"
        elif coldest_month >= 60:
            return "12a"
        elif coldest_month >= 55:
            return "11a"
        elif coldest_month >= 50:
            return "10b"
        elif coldest_month >= 45:
            return "10a"
        elif coldest_month >= 40:
            return "9b"
        elif coldest_month >= 35:
            return "9a"
        elif coldest_month >= 30:
            return "8b"
        elif coldest_month >= 25:
            return "8a"
        elif coldest_month >= 20:
            return "7b"
        elif coldest_month >= 15:
            return "7a"
        elif coldest_month >= 10:
            return "6b"
        elif coldest_month >= 5:
            return "6a"
        elif coldest_month >= 0:
            return "5b"
        elif coldest_month >= -5:
            return "5a"
        elif coldest_month >= -10:
            return "4b"
        elif coldest_month >= -15:
            return "4a"
        elif coldest_month >= -20:
            return "3b"
        elif coldest_month >= -25:
            return "3a"
        elif coldest_month >= -30:
            return "2b"
        elif coldest_month >= -35:
            return "2a"
        elif coldest_month >= -40:
            return "1b"
        else:
            return "1a"
    
    def _infer_koppen_type(self, weather_pattern: WeatherPattern, latitude: float) -> str:
        """Infer Köppen climate type from weather pattern."""
        
        temp_stats = weather_pattern.temperature_stats
        precip_stats = weather_pattern.precipitation_stats
        
        coldest_month = temp_stats['coldest_month_avg']
        warmest_month = temp_stats['warmest_month_avg']
        annual_precip = precip_stats['annual_total']
        driest_month = precip_stats['driest_month']
        
        # Convert to Celsius for Köppen classification
        coldest_c = (coldest_month - 32) * 5/9
        warmest_c = (warmest_month - 32) * 5/9
        annual_precip_mm = annual_precip * 25.4  # inches to mm
        driest_mm = driest_month * 25.4
        
        # Köppen classification logic
        if coldest_c >= 18:
            # Tropical (A)
            if driest_mm >= 60:
                return "Af"  # Tropical rainforest
            elif driest_mm >= (100 - annual_precip_mm/25):
                return "Am"  # Tropical monsoon
            else:
                return "Aw"  # Tropical savanna
        
        elif warmest_c < 10:
            # Polar (E)
            if warmest_c >= 0:
                return "ET"  # Tundra
            else:
                return "EF"  # Ice cap
        
        else:
            # Check if arid (B)
            arid_threshold = self._calculate_koppen_arid_threshold(temp_stats, precip_stats)
            if annual_precip_mm < arid_threshold:
                if annual_precip_mm < arid_threshold / 2:
                    # Desert (BW)
                    if temp_stats['mean_annual'] >= 64.4:  # 18°C
                        return "BWh"  # Hot desert
                    else:
                        return "BWk"  # Cold desert
                else:
                    # Semi-arid (BS)
                    if temp_stats['mean_annual'] >= 64.4:  # 18°C
                        return "BSh"  # Hot semi-arid
                    else:
                        return "BSk"  # Cold semi-arid
            
            # Temperate (C) or Continental (D)
            if coldest_c >= -3:
                # Temperate (C)
                return self._determine_temperate_koppen(temp_stats, precip_stats)
            else:
                # Continental (D)
                return self._determine_continental_koppen(temp_stats, precip_stats)
    
    def _calculate_koppen_arid_threshold(self, temp_stats: Dict, precip_stats: Dict) -> float:
        """Calculate Köppen arid threshold."""
        
        annual_temp_c = (temp_stats['mean_annual'] - 32) * 5/9
        return 20 * annual_temp_c  # Simplified threshold
    
    def _determine_temperate_koppen(self, temp_stats: Dict, precip_stats: Dict) -> str:
        """Determine temperate Köppen subtype."""
        
        warmest_c = (temp_stats['warmest_month_avg'] - 32) * 5/9
        driest_mm = precip_stats['driest_month'] * 25.4
        wettest_mm = precip_stats['wettest_month'] * 25.4
        
        # Precipitation pattern
        if driest_mm >= 60:
            precip_code = "f"  # Wet year-round
        elif driest_mm < wettest_mm / 3:
            precip_code = "w"  # Dry winter (simplified)
        else:
            precip_code = "s"  # Dry summer
        
        # Temperature pattern
        if warmest_c >= 22:
            temp_code = "a"  # Hot summer
        elif warmest_c >= 10:
            temp_code = "b"  # Warm summer
        else:
            temp_code = "c"  # Cool summer
        
        return f"C{precip_code}{temp_code}"
    
    def _determine_continental_koppen(self, temp_stats: Dict, precip_stats: Dict) -> str:
        """Determine continental Köppen subtype."""
        
        warmest_c = (temp_stats['warmest_month_avg'] - 32) * 5/9
        coldest_c = (temp_stats['coldest_month_avg'] - 32) * 5/9
        driest_mm = precip_stats['driest_month'] * 25.4
        wettest_mm = precip_stats['wettest_month'] * 25.4
        
        # Precipitation pattern
        if driest_mm >= 60:
            precip_code = "f"  # Wet year-round
        elif driest_mm < wettest_mm / 3:
            precip_code = "w"  # Dry winter
        else:
            precip_code = "s"  # Dry summer
        
        # Temperature pattern
        if warmest_c >= 22:
            temp_code = "a"  # Hot summer
        elif warmest_c >= 10:
            temp_code = "b"  # Warm summer
        elif coldest_c < -38:
            temp_code = "d"  # Very cold winter
        else:
            temp_code = "c"  # Cool summer
        
        return f"D{precip_code}{temp_code}"
    
    def _calculate_inference_confidence(
        self, 
        weather_pattern: WeatherPattern, 
        data_quality: Dict, 
        data_points: int
    ) -> float:
        """Calculate confidence in climate inference."""
        
        base_confidence = 0.6
        
        # Adjust for data quality
        if data_quality['completeness'] > 0.9:
            base_confidence += 0.2
        elif data_quality['completeness'] > 0.7:
            base_confidence += 0.1
        
        # Adjust for data quantity
        if data_points > 1000:  # ~3 years of daily data
            base_confidence += 0.1
        
        # Adjust for data consistency
        if data_quality['consistency'] > 0.8:
            base_confidence += 0.1
        
        return min(1.0, base_confidence)
    
    def _assess_data_quality(self, weather_data: List[Dict]) -> Dict:
        """Assess quality of weather data."""
        
        total_records = len(weather_data)
        complete_records = sum(
            1 for record in weather_data 
            if 'temperature' in record and 'precipitation' in record
        )
        
        completeness = complete_records / max(1, total_records)
        
        # Simple consistency check (no extreme outliers)
        temps = [r['temperature'] for r in weather_data if 'temperature' in r]
        consistency = 0.8  # Simplified consistency score
        
        return {
            'completeness': completeness,
            'consistency': consistency,
            'total_records': total_records,
            'complete_records': complete_records,
            'data_span_years': self._calculate_data_span_years(weather_data)
        }
    
    def _calculate_data_span_years(self, weather_data: List[Dict]) -> float:
        """Calculate span of weather data in years."""
        
        dates = [
            record['date'] for record in weather_data 
            if 'date' in record and hasattr(record['date'], 'year')
        ]
        
        if not dates:
            return 1.0
        
        min_date = min(dates)
        max_date = max(dates)
        span_days = (max_date - min_date).days
        
        return span_days / 365.25
    
    def _get_analysis_period(self, weather_data: List[Dict]) -> Dict:
        """Get analysis period information."""
        
        dates = [
            record['date'] for record in weather_data 
            if 'date' in record and hasattr(record['date'], 'year')
        ]
        
        if dates:
            return {
                'start_date': min(dates).isoformat(),
                'end_date': max(dates).isoformat(),
                'total_days': len(weather_data),
                'years_covered': self._calculate_data_span_years(weather_data)
            }
        else:
            return {
                'start_date': 'unknown',
                'end_date': 'unknown',
                'total_days': len(weather_data),
                'years_covered': 1.0
            }
    
    def _get_fallback_inference(self, latitude: float, longitude: float) -> ClimateInference:
        """Get fallback inference when weather analysis fails."""
        
        # Simple latitude-based fallback
        if abs(latitude) < 23.5:
            usda_zone = "10a"
            koppen_type = "Aw"
        elif abs(latitude) < 35:
            usda_zone = "8a"
            koppen_type = "Cfa"
        elif abs(latitude) < 50:
            usda_zone = "6a"
            koppen_type = "Cfb"
        else:
            usda_zone = "4a"
            koppen_type = "Dfb"
        
        fallback_pattern = WeatherPattern(
            temperature_stats={'mean_annual': 60, 'coldest_month_avg': 30},
            precipitation_stats={'annual_total': 30, 'driest_month': 2},
            growing_degree_days=2000,
            frost_dates={'frost_free_days': 180},
            growing_season_length=180,
            climate_indicators={'note': 'fallback_data'}
        )
        
        return ClimateInference(
            inferred_usda_zone=usda_zone,
            inferred_koppen_type=koppen_type,
            confidence_score=0.3,  # Low confidence for fallback
            weather_pattern=fallback_pattern,
            analysis_period={'note': 'fallback_analysis'},
            data_quality={'note': 'insufficient_data'}
        )


# Global service instance
weather_climate_inference = WeatherClimateInference()