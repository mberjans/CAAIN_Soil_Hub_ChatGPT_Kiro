"""
Production Analytics Service

Comprehensive analytics system for drought management service.
Provides usage pattern analysis, success metrics calculation,
agricultural impact assessment, and advanced reporting capabilities.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import statistics
from collections import defaultdict, Counter
import json
import numpy as np
from dataclasses import dataclass

from ..models.production_analytics_models import (
    UsagePatternAnalysis,
    SuccessMetricsAnalysis,
    AgriculturalImpactAnalysis,
    UserBehaviorAnalysis,
    RecommendationAnalytics,
    SystemPerformanceAnalytics,
    TrendAnalysis,
    ComparativeAnalysis,
    PredictiveAnalytics,
    AnalyticsReport,
    AnalyticsRequest,
    AnalyticsResponse,
    MetricCorrelation,
    PerformanceBenchmark,
    UserSegmentAnalysis,
    FeatureAdoptionAnalysis,
    ROI_Analysis,
    CostBenefitAnalysis,
    EnvironmentalImpactAnalysis,
    DataQualityMetrics,
    AnalyticsInsight,
    RecommendationInsight,
    PerformanceInsight,
    UserInsight,
    AgriculturalInsight
)

logger = logging.getLogger(__name__)

class AnalyticsTimeframe(str, Enum):
    """Analytics timeframe options."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"

class AnalyticsGranularity(str, Enum):
    """Analytics granularity options."""
    FARM_LEVEL = "farm_level"
    FIELD_LEVEL = "field_level"
    USER_LEVEL = "user_level"
    REGIONAL_LEVEL = "regional_level"
    SYSTEM_LEVEL = "system_level"

@dataclass
class AnalyticsDataPoint:
    """Data point for analytics calculations."""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any]
    dimensions: Dict[str, str]  # For grouping/filtering

class ProductionAnalyticsService:
    """Service for comprehensive production analytics."""
    
    def __init__(self):
        self.initialized = False
        self.analytics_cache: Dict[str, Any] = {}
        self.cache_ttl_minutes = 15
        
        # Service dependencies
        self.database = None
        self.production_monitoring_service = None
        self.drought_assessment_service = None
        
    async def initialize(self):
        """Initialize the production analytics service."""
        try:
            logger.info("Initializing Production Analytics Service...")
            
            # Initialize database connection
            self.database = await self._initialize_database()
            
            # Initialize service dependencies
            await self._initialize_service_dependencies()
            
            # Initialize analytics cache
            await self._initialize_analytics_cache()
            
            self.initialized = True
            logger.info("Production Analytics Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Production Analytics Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Production Analytics Service...")
            
            # Clear analytics cache
            self.analytics_cache.clear()
            
            # Close database connections
            if self.database:
                await self.database.close()
            
            logger.info("Production Analytics Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during Production Analytics Service cleanup: {str(e)}")
    
    async def _initialize_database(self):
        """Initialize database connection for analytics data."""
        # Database initialization logic
        return None
    
    async def _initialize_service_dependencies(self):
        """Initialize service dependencies."""
        # Initialize service dependencies
        self.production_monitoring_service = None
        self.drought_assessment_service = None
    
    async def _initialize_analytics_cache(self):
        """Initialize analytics cache."""
        self.analytics_cache = {}
    
    def _get_cache_key(self, analysis_type: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for analytics data."""
        param_str = json.dumps(parameters, sort_keys=True, default=str)
        return f"{analysis_type}:{hash(param_str)}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid."""
        if cache_key not in self.analytics_cache:
            return False
        
        cached_data = self.analytics_cache[cache_key]
        cache_time = cached_data.get('timestamp', datetime.min)
        return datetime.utcnow() - cache_time < timedelta(minutes=self.cache_ttl_minutes)
    
    def _cache_data(self, cache_key: str, data: Any):
        """Cache analytics data."""
        self.analytics_cache[cache_key] = {
            'data': data,
            'timestamp': datetime.utcnow()
        }
    
    def _get_cached_data(self, cache_key: str) -> Optional[Any]:
        """Get cached analytics data."""
        if self._is_cache_valid(cache_key):
            return self.analytics_cache[cache_key]['data']
        return None
    
    # Usage Pattern Analysis
    async def analyze_usage_patterns(self, 
                                   start_date: datetime, 
                                   end_date: datetime,
                                   granularity: AnalyticsGranularity = AnalyticsGranularity.DAILY) -> UsagePatternAnalysis:
        """Analyze usage patterns for the specified time period."""
        try:
            cache_key = self._get_cache_key("usage_patterns", {
                "start_date": start_date,
                "end_date": end_date,
                "granularity": granularity
            })
            
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            logger.info(f"Analyzing usage patterns from {start_date} to {end_date}")
            
            # Get usage data
            usage_data = await self._get_usage_data(start_date, end_date, granularity)
            
            # Analyze patterns
            peak_usage_times = await self._analyze_peak_usage_times(usage_data)
            usage_trends = await self._analyze_usage_trends(usage_data)
            seasonal_patterns = await self._analyze_seasonal_patterns(usage_data)
            user_behavior_patterns = await self._analyze_user_behavior_patterns(usage_data)
            
            # Calculate metrics
            total_users = len(set(point.metadata.get('user_id') for point in usage_data if point.metadata.get('user_id')))
            total_requests = len(usage_data)
            avg_requests_per_user = total_requests / total_users if total_users > 0 else 0
            
            analysis = UsagePatternAnalysis(
                analysis_id=uuid4(),
                start_date=start_date,
                end_date=end_date,
                granularity=granularity,
                total_users=total_users,
                total_requests=total_requests,
                avg_requests_per_user=avg_requests_per_user,
                peak_usage_times=peak_usage_times,
                usage_trends=usage_trends,
                seasonal_patterns=seasonal_patterns,
                user_behavior_patterns=user_behavior_patterns,
                generated_at=datetime.utcnow()
            )
            
            self._cache_data(cache_key, analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {str(e)}")
            raise
    
    async def _get_usage_data(self, start_date: datetime, end_date: datetime, granularity: AnalyticsGranularity) -> List[AnalyticsDataPoint]:
        """Get usage data for analysis."""
        # Simulate usage data collection
        # In production, this would query actual usage data from the database
        
        usage_data = []
        current_date = start_date
        
        while current_date <= end_date:
            # Simulate daily usage patterns
            import random
            
            # Peak hours (9 AM - 5 PM)
            for hour in range(9, 18):
                timestamp = current_date.replace(hour=hour, minute=random.randint(0, 59))
                value = random.uniform(50, 200)  # Requests per hour
                
                usage_data.append(AnalyticsDataPoint(
                    timestamp=timestamp,
                    value=value,
                    metadata={
                        'user_id': f"user_{random.randint(1, 100)}",
                        'feature': random.choice(['drought_assessment', 'water_savings', 'irrigation_optimization']),
                        'device_type': random.choice(['mobile', 'desktop', 'tablet'])
                    },
                    dimensions={
                        'hour': str(hour),
                        'day_of_week': timestamp.strftime('%A'),
                        'month': timestamp.strftime('%B')
                    }
                ))
            
            current_date += timedelta(days=1)
        
        return usage_data
    
    async def _analyze_peak_usage_times(self, usage_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze peak usage times."""
        # Group by hour
        hourly_usage = defaultdict(list)
        for point in usage_data:
            hour = point.timestamp.hour
            hourly_usage[hour].append(point.value)
        
        # Calculate average usage per hour
        avg_hourly_usage = {}
        for hour, values in hourly_usage.items():
            avg_hourly_usage[hour] = statistics.mean(values)
        
        # Find peak hours
        peak_hours = sorted(avg_hourly_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "peak_hours": [hour for hour, _ in peak_hours],
            "hourly_averages": avg_hourly_usage,
            "peak_usage_value": peak_hours[0][1] if peak_hours else 0
        }
    
    async def _analyze_usage_trends(self, usage_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze usage trends."""
        if len(usage_data) < 2:
            return {"trend": "insufficient_data", "change_percent": 0}
        
        # Sort by timestamp
        sorted_data = sorted(usage_data, key=lambda x: x.timestamp)
        
        # Calculate trend
        first_value = sorted_data[0].value
        last_value = sorted_data[-1].value
        
        if first_value == 0:
            change_percent = 0
        else:
            change_percent = ((last_value - first_value) / first_value) * 100
        
        # Determine trend direction
        if change_percent > 10:
            trend = "increasing"
        elif change_percent < -10:
            trend = "decreasing"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "change_percent": change_percent,
            "first_value": first_value,
            "last_value": last_value
        }
    
    async def _analyze_seasonal_patterns(self, usage_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze seasonal patterns."""
        # Group by month
        monthly_usage = defaultdict(list)
        for point in usage_data:
            month = point.timestamp.month
            monthly_usage[month].append(point.value)
        
        # Calculate monthly averages
        monthly_averages = {}
        for month, values in monthly_usage.items():
            monthly_averages[month] = statistics.mean(values)
        
        # Find seasonal patterns
        peak_month = max(monthly_averages.items(), key=lambda x: x[1])[0]
        low_month = min(monthly_averages.items(), key=lambda x: x[1])[0]
        
        return {
            "monthly_averages": monthly_averages,
            "peak_month": peak_month,
            "low_month": low_month,
            "seasonal_variation": max(monthly_averages.values()) - min(monthly_averages.values())
        }
    
    async def _analyze_user_behavior_patterns(self, usage_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze user behavior patterns."""
        # Group by user
        user_usage = defaultdict(list)
        feature_usage = defaultdict(int)
        device_usage = defaultdict(int)
        
        for point in usage_data:
            user_id = point.metadata.get('user_id')
            feature = point.metadata.get('feature')
            device_type = point.metadata.get('device_type')
            
            if user_id:
                user_usage[user_id].append(point.value)
            if feature:
                feature_usage[feature] += 1
            if device_type:
                device_usage[device_type] += 1
        
        # Calculate user behavior metrics
        user_activity_levels = {}
        for user_id, values in user_usage.items():
            user_activity_levels[user_id] = {
                'total_requests': len(values),
                'avg_requests_per_session': statistics.mean(values) if values else 0,
                'max_requests': max(values) if values else 0
            }
        
        return {
            "user_activity_levels": user_activity_levels,
            "feature_popularity": dict(feature_usage),
            "device_preferences": dict(device_usage),
            "most_active_users": sorted(user_activity_levels.items(), 
                                      key=lambda x: x[1]['total_requests'], 
                                      reverse=True)[:10]
        }
    
    # Success Metrics Analysis
    async def analyze_success_metrics(self, 
                                    start_date: datetime, 
                                    end_date: datetime) -> SuccessMetricsAnalysis:
        """Analyze success metrics for the specified time period."""
        try:
            cache_key = self._get_cache_key("success_metrics", {
                "start_date": start_date,
                "end_date": end_date
            })
            
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            logger.info(f"Analyzing success metrics from {start_date} to {end_date}")
            
            # Get success data
            success_data = await self._get_success_data(start_date, end_date)
            
            # Analyze metrics
            user_satisfaction = await self._analyze_user_satisfaction(success_data)
            recommendation_effectiveness = await self._analyze_recommendation_effectiveness(success_data)
            system_reliability = await self._analyze_system_reliability(success_data)
            business_metrics = await self._analyze_business_metrics(success_data)
            
            analysis = SuccessMetricsAnalysis(
                analysis_id=uuid4(),
                start_date=start_date,
                end_date=end_date,
                user_satisfaction=user_satisfaction,
                recommendation_effectiveness=recommendation_effectiveness,
                system_reliability=system_reliability,
                business_metrics=business_metrics,
                generated_at=datetime.utcnow()
            )
            
            self._cache_data(cache_key, analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing success metrics: {str(e)}")
            raise
    
    async def _get_success_data(self, start_date: datetime, end_date: datetime) -> List[AnalyticsDataPoint]:
        """Get success data for analysis."""
        # Simulate success data collection
        success_data = []
        current_date = start_date
        
        while current_date <= end_date:
            import random
            
            # Simulate daily success metrics
            timestamp = current_date.replace(hour=12, minute=0)
            
            # User satisfaction score
            satisfaction_value = random.uniform(3.5, 4.8)
            success_data.append(AnalyticsDataPoint(
                timestamp=timestamp,
                value=satisfaction_value,
                metadata={'metric_type': 'user_satisfaction'},
                dimensions={'date': current_date.strftime('%Y-%m-%d')}
            ))
            
            # Recommendation accuracy
            accuracy_value = random.uniform(75, 95)
            success_data.append(AnalyticsDataPoint(
                timestamp=timestamp,
                value=accuracy_value,
                metadata={'metric_type': 'recommendation_accuracy'},
                dimensions={'date': current_date.strftime('%Y-%m-%d')}
            ))
            
            # System uptime
            uptime_value = random.uniform(95, 99.9)
            success_data.append(AnalyticsDataPoint(
                timestamp=timestamp,
                value=uptime_value,
                metadata={'metric_type': 'system_uptime'},
                dimensions={'date': current_date.strftime('%Y-%m-%d')}
            ))
            
            current_date += timedelta(days=1)
        
        return success_data
    
    async def _analyze_user_satisfaction(self, success_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze user satisfaction metrics."""
        satisfaction_data = [point for point in success_data if point.metadata.get('metric_type') == 'user_satisfaction']
        
        if not satisfaction_data:
            return {"avg_satisfaction": 0, "trend": "no_data"}
        
        values = [point.value for point in satisfaction_data]
        avg_satisfaction = statistics.mean(values)
        
        # Calculate trend
        if len(values) >= 2:
            first_value = values[0]
            last_value = values[-1]
            trend_percent = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
            
            if trend_percent > 5:
                trend = "improving"
            elif trend_percent < -5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "avg_satisfaction": avg_satisfaction,
            "trend": trend,
            "min_satisfaction": min(values),
            "max_satisfaction": max(values),
            "satisfaction_distribution": self._calculate_distribution(values)
        }
    
    async def _analyze_recommendation_effectiveness(self, success_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze recommendation effectiveness."""
        accuracy_data = [point for point in success_data if point.metadata.get('metric_type') == 'recommendation_accuracy']
        
        if not accuracy_data:
            return {"avg_accuracy": 0, "trend": "no_data"}
        
        values = [point.value for point in accuracy_data]
        avg_accuracy = statistics.mean(values)
        
        # Calculate trend
        if len(values) >= 2:
            first_value = values[0]
            last_value = values[-1]
            trend_percent = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
            
            if trend_percent > 5:
                trend = "improving"
            elif trend_percent < -5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "avg_accuracy": avg_accuracy,
            "trend": trend,
            "min_accuracy": min(values),
            "max_accuracy": max(values),
            "accuracy_distribution": self._calculate_distribution(values)
        }
    
    async def _analyze_system_reliability(self, success_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze system reliability."""
        uptime_data = [point for point in success_data if point.metadata.get('metric_type') == 'system_uptime']
        
        if not uptime_data:
            return {"avg_uptime": 0, "trend": "no_data"}
        
        values = [point.value for point in uptime_data]
        avg_uptime = statistics.mean(values)
        
        # Calculate trend
        if len(values) >= 2:
            first_value = values[0]
            last_value = values[-1]
            trend_percent = ((last_value - first_value) / first_value) * 100 if first_value > 0 else 0
            
            if trend_percent > 1:
                trend = "improving"
            elif trend_percent < -1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "avg_uptime": avg_uptime,
            "trend": trend,
            "min_uptime": min(values),
            "max_uptime": max(values),
            "downtime_percent": 100 - avg_uptime
        }
    
    async def _analyze_business_metrics(self, success_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze business metrics."""
        # Simulate business metrics
        import random
        
        return {
            "user_retention_rate": random.uniform(70, 90),
            "feature_adoption_rate": random.uniform(60, 85),
            "conversion_rate": random.uniform(15, 35),
            "customer_lifetime_value": random.uniform(500, 2000),
            "churn_rate": random.uniform(5, 15)
        }
    
    def _calculate_distribution(self, values: List[float]) -> Dict[str, float]:
        """Calculate distribution statistics."""
        if not values:
            return {}
        
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "q1": np.percentile(values, 25) if len(values) > 1 else values[0],
            "q3": np.percentile(values, 75) if len(values) > 1 else values[0]
        }
    
    # Agricultural Impact Analysis
    async def analyze_agricultural_impact(self, 
                                        start_date: datetime, 
                                        end_date: datetime) -> AgriculturalImpactAnalysis:
        """Analyze agricultural impact for the specified time period."""
        try:
            cache_key = self._get_cache_key("agricultural_impact", {
                "start_date": start_date,
                "end_date": end_date
            })
            
            cached_data = self._get_cached_data(cache_key)
            if cached_data:
                return cached_data
            
            logger.info(f"Analyzing agricultural impact from {start_date} to {end_date}")
            
            # Get agricultural impact data
            impact_data = await self._get_agricultural_impact_data(start_date, end_date)
            
            # Analyze impact metrics
            water_savings_analysis = await self._analyze_water_savings(impact_data)
            cost_savings_analysis = await self._analyze_cost_savings(impact_data)
            environmental_impact = await self._analyze_environmental_impact(impact_data)
            farm_productivity = await self._analyze_farm_productivity(impact_data)
            
            analysis = AgriculturalImpactAnalysis(
                analysis_id=uuid4(),
                start_date=start_date,
                end_date=end_date,
                water_savings_analysis=water_savings_analysis,
                cost_savings_analysis=cost_savings_analysis,
                environmental_impact=environmental_impact,
                farm_productivity=farm_productivity,
                generated_at=datetime.utcnow()
            )
            
            self._cache_data(cache_key, analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing agricultural impact: {str(e)}")
            raise
    
    async def _get_agricultural_impact_data(self, start_date: datetime, end_date: datetime) -> List[AnalyticsDataPoint]:
        """Get agricultural impact data for analysis."""
        # Simulate agricultural impact data collection
        impact_data = []
        current_date = start_date
        
        while current_date <= end_date:
            import random
            
            timestamp = current_date.replace(hour=12, minute=0)
            
            # Water savings
            water_savings = random.uniform(1000, 5000)
            impact_data.append(AnalyticsDataPoint(
                timestamp=timestamp,
                value=water_savings,
                metadata={'metric_type': 'water_savings'},
                dimensions={'date': current_date.strftime('%Y-%m-%d')}
            ))
            
            # Cost savings
            cost_savings = random.uniform(500, 2000)
            impact_data.append(AnalyticsDataPoint(
                timestamp=timestamp,
                value=cost_savings,
                metadata={'metric_type': 'cost_savings'},
                dimensions={'date': current_date.strftime('%Y-%m-%d')}
            ))
            
            # Environmental impact score
            env_score = random.uniform(70, 95)
            impact_data.append(AnalyticsDataPoint(
                timestamp=timestamp,
                value=env_score,
                metadata={'metric_type': 'environmental_impact'},
                dimensions={'date': current_date.strftime('%Y-%m-%d')}
            ))
            
            current_date += timedelta(days=1)
        
        return impact_data
    
    async def _analyze_water_savings(self, impact_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze water savings impact."""
        water_data = [point for point in impact_data if point.metadata.get('metric_type') == 'water_savings']
        
        if not water_data:
            return {"total_savings": 0, "avg_daily_savings": 0}
        
        values = [point.value for point in water_data]
        total_savings = sum(values)
        avg_daily_savings = statistics.mean(values)
        
        return {
            "total_savings": total_savings,
            "avg_daily_savings": avg_daily_savings,
            "max_daily_savings": max(values),
            "min_daily_savings": min(values),
            "savings_trend": self._calculate_trend(values)
        }
    
    async def _analyze_cost_savings(self, impact_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze cost savings impact."""
        cost_data = [point for point in impact_data if point.metadata.get('metric_type') == 'cost_savings']
        
        if not cost_data:
            return {"total_savings": 0, "avg_daily_savings": 0}
        
        values = [point.value for point in cost_data]
        total_savings = sum(values)
        avg_daily_savings = statistics.mean(values)
        
        return {
            "total_savings": total_savings,
            "avg_daily_savings": avg_daily_savings,
            "max_daily_savings": max(values),
            "min_daily_savings": min(values),
            "savings_trend": self._calculate_trend(values),
            "roi_percentage": (total_savings / 10000) * 100  # Simulated ROI calculation
        }
    
    async def _analyze_environmental_impact(self, impact_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze environmental impact."""
        env_data = [point for point in impact_data if point.metadata.get('metric_type') == 'environmental_impact']
        
        if not env_data:
            return {"avg_score": 0, "trend": "no_data"}
        
        values = [point.value for point in env_data]
        avg_score = statistics.mean(values)
        
        return {
            "avg_score": avg_score,
            "trend": self._calculate_trend(values),
            "min_score": min(values),
            "max_score": max(values),
            "environmental_benefits": {
                "water_conservation": avg_score * 0.4,
                "soil_health_improvement": avg_score * 0.3,
                "carbon_footprint_reduction": avg_score * 0.3
            }
        }
    
    async def _analyze_farm_productivity(self, impact_data: List[AnalyticsDataPoint]) -> Dict[str, Any]:
        """Analyze farm productivity impact."""
        # Simulate farm productivity analysis
        import random
        
        return {
            "yield_improvement_percent": random.uniform(5, 20),
            "efficiency_gains": random.uniform(10, 30),
            "resource_optimization": random.uniform(15, 35),
            "sustainability_score": random.uniform(75, 95)
        }
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 2:
            return "insufficient_data"
        
        first_value = values[0]
        last_value = values[-1]
        
        if first_value == 0:
            change_percent = 0
        else:
            change_percent = ((last_value - first_value) / first_value) * 100
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    # Comprehensive Analytics Report
    async def generate_comprehensive_analytics_report(self, 
                                                    start_date: datetime, 
                                                    end_date: datetime) -> AnalyticsReport:
        """Generate comprehensive analytics report."""
        try:
            logger.info(f"Generating comprehensive analytics report from {start_date} to {end_date}")
            
            # Run all analyses
            usage_patterns = await self.analyze_usage_patterns(start_date, end_date)
            success_metrics = await self.analyze_success_metrics(start_date, end_date)
            agricultural_impact = await self.analyze_agricultural_impact(start_date, end_date)
            
            # Generate insights
            insights = await self._generate_analytics_insights(usage_patterns, success_metrics, agricultural_impact)
            
            # Create comprehensive report
            report = AnalyticsReport(
                report_id=uuid4(),
                start_date=start_date,
                end_date=end_date,
                generated_at=datetime.utcnow(),
                usage_patterns=usage_patterns,
                success_metrics=success_metrics,
                agricultural_impact=agricultural_impact,
                insights=insights,
                summary=self._generate_report_summary(usage_patterns, success_metrics, agricultural_impact)
            )
            
            logger.info("Comprehensive analytics report generated successfully")
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive analytics report: {str(e)}")
            raise
    
    async def _generate_analytics_insights(self, 
                                         usage_patterns: UsagePatternAnalysis,
                                         success_metrics: SuccessMetricsAnalysis,
                                         agricultural_impact: AgriculturalImpactAnalysis) -> List[AnalyticsInsight]:
        """Generate analytics insights."""
        insights = []
        
        # Usage pattern insights
        if usage_patterns.peak_usage_times.get('peak_hours'):
            insights.append(AnalyticsInsight(
                insight_type="usage_pattern",
                title="Peak Usage Times Identified",
                description=f"Peak usage occurs during hours {usage_patterns.peak_usage_times['peak_hours']}",
                impact="high",
                recommendation="Consider scaling resources during peak hours",
                confidence=0.85
            ))
        
        # Success metrics insights
        if success_metrics.user_satisfaction.get('avg_satisfaction', 0) > 4.0:
            insights.append(AnalyticsInsight(
                insight_type="user_satisfaction",
                title="High User Satisfaction",
                description=f"User satisfaction is {success_metrics.user_satisfaction['avg_satisfaction']:.2f}/5.0",
                impact="positive",
                recommendation="Continue current practices to maintain satisfaction",
                confidence=0.90
            ))
        
        # Agricultural impact insights
        if agricultural_impact.water_savings_analysis.get('total_savings', 0) > 10000:
            insights.append(AnalyticsInsight(
                insight_type="agricultural_impact",
                title="Significant Water Savings Achieved",
                description=f"Total water savings: {agricultural_impact.water_savings_analysis['total_savings']:.0f} gallons",
                impact="high",
                recommendation="Promote water conservation practices to more farms",
                confidence=0.95
            ))
        
        return insights
    
    def _generate_report_summary(self, 
                               usage_patterns: UsagePatternAnalysis,
                               success_metrics: SuccessMetricsAnalysis,
                               agricultural_impact: AgriculturalImpactAnalysis) -> Dict[str, Any]:
        """Generate report summary."""
        return {
            "key_metrics": {
                "total_users": usage_patterns.total_users,
                "total_requests": usage_patterns.total_requests,
                "user_satisfaction": success_metrics.user_satisfaction.get('avg_satisfaction', 0),
                "water_savings": agricultural_impact.water_savings_analysis.get('total_savings', 0)
            },
            "trends": {
                "usage_trend": usage_patterns.usage_trends.get('trend', 'unknown'),
                "satisfaction_trend": success_metrics.user_satisfaction.get('trend', 'unknown'),
                "water_savings_trend": agricultural_impact.water_savings_analysis.get('savings_trend', 'unknown')
            },
            "recommendations": [
                "Monitor peak usage times for resource planning",
                "Maintain high user satisfaction levels",
                "Continue promoting water conservation practices",
                "Track agricultural impact metrics regularly"
            ]
        }