"""
Soil Health Tracking Service
Provides long-term soil health monitoring, trend analysis,
and progress tracking capabilities.
"""

import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
import numpy as np
import pandas as pd

from .soil_fertility_assessment_service import SoilHealthScore
from ..models.agricultural_models import SoilTestData


@dataclass
class SoilHealthTrend:
    """Soil health trend analysis."""
    parameter: str
    trend_direction: str  # 'improving', 'declining', 'stable'
    rate_of_change: float  # units per year
    confidence_level: float
    time_period_years: int
    current_value: float
    projected_value_1yr: float
    projected_value_5yr: float


@dataclass
class SoilHealthAlert:
    """Soil health alert."""
    alert_id: str
    alert_type: str  # 'declining_trend', 'threshold_breach', 'goal_deviation'
    severity: str  # 'low', 'medium', 'high', 'critical'
    parameter: str
    current_value: float
    threshold_value: float
    description: str
    recommended_actions: List[str]
    created_at: datetime


@dataclass
class SoilHealthReport:
    """Comprehensive soil health report."""
    report_id: str
    farm_id: str
    field_id: str
    report_period: Dict[str, date]
    current_soil_health: SoilHealthScore
    trends: List[SoilHealthTrend]
    alerts: List[SoilHealthAlert]
    improvement_summary: Dict[str, Any]
    practice_effectiveness: Dict[str, float]
    recommendations: List[str]
    generated_at: datetime


class SoilHealthTrackingService:
    """Service for tracking and monitoring soil health over time."""
    
    def __init__(self):
        self.trend_analyzer = TrendAnalyzer()
        self.alert_manager = AlertManager()
        self.report_generator = ReportGenerator()
    
    async def track_soil_health_progress(
        self,
        farm_id: str,
        field_id: str,
        historical_data: List[SoilTestData],
        current_data: SoilTestData,
        improvement_goals: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Track soil health progress over time."""
        
        # Analyze trends
        trends = await self._analyze_soil_health_trends(historical_data, current_data)
        
        # Check for alerts
        alerts = await self._check_soil_health_alerts(
            trends, current_data, improvement_goals
        )
        
        # Calculate progress toward goals
        goal_progress = await self._calculate_goal_progress(
            historical_data, current_data, improvement_goals
        )
        
        # Assess practice effectiveness
        practice_effectiveness = await self._assess_practice_effectiveness(
            historical_data, current_data
        )
        
        return {
            'tracking_id': f"tracking_{farm_id}_{field_id}_{datetime.now().strftime('%Y%m%d')}",
            'trends': trends,
            'alerts': alerts,
            'goal_progress': goal_progress,
            'practice_effectiveness': practice_effectiveness,
            'overall_trajectory': self._calculate_overall_trajectory(trends),
            'next_monitoring_date': self._calculate_next_monitoring_date(trends, alerts),
            'updated_at': datetime.now()
        }
    
    async def _analyze_soil_health_trends(
        self,
        historical_data: List[SoilTestData],
        current_data: SoilTestData
    ) -> List[SoilHealthTrend]:
        """Analyze trends in soil health parameters."""
        
        trends = []
        
        # Create time series data
        time_series = self._create_time_series(historical_data, current_data)
        
        # Analyze key parameters
        parameters = [
            'ph', 'organic_matter_percent', 'phosphorus_ppm', 'potassium_ppm',
            'nitrogen_ppm', 'cec_meq_per_100g'
        ]
        
        for param in parameters:
            if param in time_series and len(time_series[param]) >= 3:
                trend = await self._calculate_parameter_trend(param, time_series[param])
                if trend:
                    trends.append(trend)
        
        return trends
    
    def _create_time_series(
        self,
        historical_data: List[SoilTestData],
        current_data: SoilTestData
    ) -> Dict[str, List[Tuple[datetime, float]]]:
        """Create time series data from soil test history."""
        
        time_series = {}
        
        # Combine historical and current data
        all_data = historical_data + [current_data]
        
        for soil_test in all_data:
            test_date = soil_test.test_date if hasattr(soil_test, 'test_date') else datetime.now()
            
            # Extract parameter values
            if hasattr(soil_test, 'ph'):
                if 'ph' not in time_series:
                    time_series['ph'] = []
                time_series['ph'].append((test_date, soil_test.ph))
            
            if hasattr(soil_test, 'organic_matter_percent'):
                if 'organic_matter_percent' not in time_series:
                    time_series['organic_matter_percent'] = []
                time_series['organic_matter_percent'].append(
                    (test_date, soil_test.organic_matter_percent)
                )
            
            if hasattr(soil_test, 'phosphorus_ppm'):
                if 'phosphorus_ppm' not in time_series:
                    time_series['phosphorus_ppm'] = []
                time_series['phosphorus_ppm'].append(
                    (test_date, soil_test.phosphorus_ppm)
                )
            
            if hasattr(soil_test, 'potassium_ppm'):
                if 'potassium_ppm' not in time_series:
                    time_series['potassium_ppm'] = []
                time_series['potassium_ppm'].append(
                    (test_date, soil_test.potassium_ppm)
                )
        
        # Sort by date
        for param in time_series:
            time_series[param].sort(key=lambda x: x[0])
        
        return time_series
    
    async def _calculate_parameter_trend(
        self,
        parameter: str,
        data_points: List[Tuple[datetime, float]]
    ) -> Optional[SoilHealthTrend]:
        """Calculate trend for a specific parameter."""
        
        if len(data_points) < 3:
            return None
        
        # Extract dates and values
        dates = [point[0] for point in data_points]
        values = [point[1] for point in data_points]
        
        # Convert dates to years for regression
        base_date = dates[0]
        years = [(date - base_date).days / 365.25 for date in dates]
        
        # Calculate linear regression
        coefficients = np.polyfit(years, values, 1)
        slope = coefficients[0]  # Rate of change per year
        
        # Calculate R-squared for confidence
        y_pred = np.polyval(coefficients, years)
        ss_res = np.sum((values - y_pred) ** 2)
        ss_tot = np.sum((values - np.mean(values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.01:  # Threshold for stability
            trend_direction = 'stable'
        elif slope > 0:
            trend_direction = 'improving'
        else:
            trend_direction = 'declining'
        
        # Calculate projections
        current_value = values[-1]
        projected_1yr = current_value + slope
        projected_5yr = current_value + (slope * 5)
        
        return SoilHealthTrend(
            parameter=parameter,
            trend_direction=trend_direction,
            rate_of_change=slope,
            confidence_level=r_squared,
            time_period_years=len(data_points),
            current_value=current_value,
            projected_value_1yr=projected_1yr,
            projected_value_5yr=projected_5yr
        )