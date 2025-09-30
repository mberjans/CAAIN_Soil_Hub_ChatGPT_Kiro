"""
Analytics Service for comprehensive fertilizer application system analysis.

This service provides advanced analytics capabilities including:
- User engagement analytics
- Recommendation effectiveness tracking
- Agricultural impact assessment
- System performance analytics
- Usage pattern analysis
- Success metrics calculation
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from uuid import uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import statistics
from collections import defaultdict, Counter

from src.models.application_models import (
    ApplicationMethod, ApplicationResponse, ApplicationPlan,
    EquipmentAssessment, FieldConditions, CropRequirements
)
from src.services.performance_monitoring_service import (
    PerformanceMonitoringService, PerformanceMetric, PerformanceSnapshot
)

logger = logging.getLogger(__name__)


class AnalyticsMetric(str, Enum):
    """Analytics metrics for comprehensive analysis."""
    USER_ENGAGEMENT = "user_engagement"
    RECOMMENDATION_ACCURACY = "recommendation_accuracy"
    AGRICULTURAL_IMPACT = "agricultural_impact"
    SYSTEM_PERFORMANCE = "system_performance"
    USAGE_PATTERNS = "usage_patterns"
    SUCCESS_RATE = "success_rate"
    COST_EFFECTIVENESS = "cost_effectiveness"
    ENVIRONMENTAL_IMPACT = "environmental_impact"


class AnalyticsPeriod(str, Enum):
    """Analytics time periods."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class UserEngagementMetrics:
    """User engagement analytics data."""
    user_id: str
    session_count: int
    total_time_minutes: float
    recommendations_requested: int
    recommendations_implemented: int
    feedback_provided: int
    features_used: List[str]
    last_activity: str
    engagement_score: float


@dataclass
class RecommendationEffectiveness:
    """Recommendation effectiveness analysis."""
    recommendation_id: str
    method_recommended: str
    method_implemented: Optional[str]
    farmer_satisfaction: Optional[float]
    yield_impact: Optional[float]
    cost_savings: Optional[float]
    implementation_rate: float
    success_score: float


@dataclass
class AgriculturalImpactMetrics:
    """Agricultural impact assessment."""
    period: str
    total_recommendations: int
    implemented_recommendations: int
    estimated_yield_increase: float
    estimated_cost_savings: float
    environmental_benefits: Dict[str, float]
    farmer_satisfaction_avg: float
    adoption_rate: float


@dataclass
class SystemPerformanceMetrics:
    """System performance analytics."""
    period: str
    total_requests: int
    average_response_time_ms: float
    error_rate: float
    uptime_percentage: float
    throughput_per_hour: float
    resource_utilization: Dict[str, float]


@dataclass
class UsagePatternAnalysis:
    """Usage pattern analysis."""
    period: str
    peak_usage_hours: List[int]
    most_used_features: List[str]
    seasonal_patterns: Dict[str, int]
    geographic_distribution: Dict[str, int]
    user_segments: Dict[str, int]


@dataclass
class AnalyticsReport:
    """Comprehensive analytics report."""
    report_id: str
    report_type: str
    period: str
    generated_at: str
    user_engagement: UserEngagementMetrics
    recommendation_effectiveness: List[RecommendationEffectiveness]
    agricultural_impact: AgriculturalImpactMetrics
    system_performance: SystemPerformanceMetrics
    usage_patterns: UsagePatternAnalysis
    key_insights: List[str]
    recommendations: List[str]


class AnalyticsService:
    """Service for comprehensive analytics and reporting."""
    
    def __init__(self):
        self.performance_service = PerformanceMonitoringService()
        self.analytics_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.user_sessions: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.recommendation_outcomes: Dict[str, Dict[str, Any]] = {}
        self.system_metrics: List[Dict[str, Any]] = []
        self.agricultural_data: List[Dict[str, Any]] = []
        
    async def track_user_engagement(
        self,
        user_id: str,
        session_data: Dict[str, Any]
    ) -> UserEngagementMetrics:
        """
        Track and analyze user engagement metrics.
        
        Args:
            user_id: User identifier
            session_data: Session activity data
            
        Returns:
            UserEngagementMetrics with comprehensive engagement analysis
        """
        try:
            logger.info(f"Tracking user engagement for user {user_id}")
            
            # Store session data
            self.user_sessions[user_id].append({
                **session_data,
                "timestamp": datetime.now().isoformat()
            })
            
            # Calculate engagement metrics
            sessions = self.user_sessions[user_id]
            total_sessions = len(sessions)
            
            # Calculate total time
            total_time = sum(session.get("duration_minutes", 0) for session in sessions)
            
            # Count recommendations
            recommendations_requested = sum(
                1 for session in sessions 
                if "recommendation_requested" in session.get("actions", [])
            )
            
            recommendations_implemented = sum(
                1 for session in sessions 
                if "recommendation_implemented" in session.get("actions", [])
            )
            
            # Count feedback
            feedback_provided = sum(
                1 for session in sessions 
                if "feedback_provided" in session.get("actions", [])
            )
            
            # Extract features used
            features_used = list(set(
                feature for session in sessions 
                for feature in session.get("features_used", [])
            ))
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(
                total_sessions, total_time, recommendations_requested,
                recommendations_implemented, feedback_provided
            )
            
            # Get last activity
            last_activity = sessions[-1]["timestamp"] if sessions else datetime.now().isoformat()
            
            metrics = UserEngagementMetrics(
                user_id=user_id,
                session_count=total_sessions,
                total_time_minutes=total_time,
                recommendations_requested=recommendations_requested,
                recommendations_implemented=recommendations_implemented,
                feedback_provided=feedback_provided,
                features_used=features_used,
                last_activity=last_activity,
                engagement_score=engagement_score
            )
            
            # Store analytics data
            self.analytics_data["user_engagement"].append(metrics.__dict__)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error tracking user engagement for user {user_id}: {e}")
            raise
    
    def _calculate_engagement_score(
        self,
        session_count: int,
        total_time: float,
        recommendations_requested: int,
        recommendations_implemented: int,
        feedback_provided: int
    ) -> float:
        """Calculate user engagement score."""
        # Weighted scoring system
        session_score = min(session_count / 10, 1.0) * 0.2
        time_score = min(total_time / 300, 1.0) * 0.2  # 5 hours max
        request_score = min(recommendations_requested / 20, 1.0) * 0.3
        implementation_score = min(recommendations_implemented / 10, 1.0) * 0.2
        feedback_score = min(feedback_provided / 5, 1.0) * 0.1
        
        return session_score + time_score + request_score + implementation_score + feedback_score
    
    async def track_recommendation_outcome(
        self,
        recommendation_id: str,
        outcome_data: Dict[str, Any]
    ) -> RecommendationEffectiveness:
        """
        Track recommendation outcomes and effectiveness.
        
        Args:
            recommendation_id: Recommendation identifier
            outcome_data: Outcome and feedback data
            
        Returns:
            RecommendationEffectiveness analysis
        """
        try:
            logger.info(f"Tracking recommendation outcome for {recommendation_id}")
            
            # Store outcome data
            self.recommendation_outcomes[recommendation_id] = {
                **outcome_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Extract metrics
            method_recommended = outcome_data.get("method_recommended", "")
            method_implemented = outcome_data.get("method_implemented")
            farmer_satisfaction = outcome_data.get("farmer_satisfaction")
            yield_impact = outcome_data.get("yield_impact")
            cost_savings = outcome_data.get("cost_savings")
            
            # Calculate implementation rate
            implementation_rate = 1.0 if method_implemented else 0.0
            
            # Calculate success score
            success_score = self._calculate_success_score(
                farmer_satisfaction, yield_impact, cost_savings, implementation_rate
            )
            
            effectiveness = RecommendationEffectiveness(
                recommendation_id=recommendation_id,
                method_recommended=method_recommended,
                method_implemented=method_implemented,
                farmer_satisfaction=farmer_satisfaction,
                yield_impact=yield_impact,
                cost_savings=cost_savings,
                implementation_rate=implementation_rate,
                success_score=success_score
            )
            
            # Store analytics data
            self.analytics_data["recommendation_effectiveness"].append(effectiveness.__dict__)
            
            return effectiveness
            
        except Exception as e:
            logger.error(f"Error tracking recommendation outcome for {recommendation_id}: {e}")
            raise
    
    def _calculate_success_score(
        self,
        farmer_satisfaction: Optional[float],
        yield_impact: Optional[float],
        cost_savings: Optional[float],
        implementation_rate: float
    ) -> float:
        """Calculate recommendation success score."""
        score = 0.0
        
        # Implementation rate (40% weight)
        score += implementation_rate * 0.4
        
        # Farmer satisfaction (30% weight)
        if farmer_satisfaction is not None:
            score += (farmer_satisfaction / 5.0) * 0.3
        
        # Yield impact (20% weight)
        if yield_impact is not None:
            score += min(yield_impact / 20.0, 1.0) * 0.2  # 20% yield increase max
        
        # Cost savings (10% weight)
        if cost_savings is not None:
            score += min(cost_savings / 1000.0, 1.0) * 0.1  # $1000 savings max
        
        return min(score, 1.0)
    
    async def calculate_agricultural_impact(
        self,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> AgriculturalImpactMetrics:
        """
        Calculate agricultural impact metrics for a period.
        
        Args:
            period: Analysis period
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            AgriculturalImpactMetrics with comprehensive impact analysis
        """
        try:
            logger.info(f"Calculating agricultural impact for period {period}")
            
            # Filter data by date range
            period_data = [
                outcome for outcome in self.recommendation_outcomes.values()
                if start_date <= datetime.fromisoformat(outcome["timestamp"]) <= end_date
            ]
            
            total_recommendations = len(period_data)
            implemented_recommendations = sum(
                1 for outcome in period_data 
                if outcome.get("method_implemented") is not None
            )
            
            # Calculate aggregate metrics
            farmer_satisfaction_scores = [
                outcome.get("farmer_satisfaction") 
                for outcome in period_data 
                if outcome.get("farmer_satisfaction") is not None
            ]
            farmer_satisfaction_avg = (
                statistics.mean(farmer_satisfaction_scores) 
                if farmer_satisfaction_scores else 0.0
            )
            
            yield_impacts = [
                outcome.get("yield_impact") 
                for outcome in period_data 
                if outcome.get("yield_impact") is not None
            ]
            estimated_yield_increase = sum(yield_impacts) if yield_impacts else 0.0
            
            cost_savings_list = [
                outcome.get("cost_savings") 
                for outcome in period_data 
                if outcome.get("cost_savings") is not None
            ]
            estimated_cost_savings = sum(cost_savings_list) if cost_savings_list else 0.0
            
            # Calculate adoption rate
            adoption_rate = (
                implemented_recommendations / total_recommendations 
                if total_recommendations > 0 else 0.0
            )
            
            # Calculate environmental benefits
            environmental_benefits = self._calculate_environmental_benefits(period_data)
            
            metrics = AgriculturalImpactMetrics(
                period=period,
                total_recommendations=total_recommendations,
                implemented_recommendations=implemented_recommendations,
                estimated_yield_increase=estimated_yield_increase,
                estimated_cost_savings=estimated_cost_savings,
                environmental_benefits=environmental_benefits,
                farmer_satisfaction_avg=farmer_satisfaction_avg,
                adoption_rate=adoption_rate
            )
            
            # Store analytics data
            self.analytics_data["agricultural_impact"].append(metrics.__dict__)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating agricultural impact for period {period}: {e}")
            raise
    
    def _calculate_environmental_benefits(self, period_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate environmental benefits from recommendations."""
        benefits = {
            "fertilizer_reduction": 0.0,
            "water_conservation": 0.0,
            "soil_health_improvement": 0.0,
            "carbon_sequestration": 0.0
        }
        
        for outcome in period_data:
            if outcome.get("environmental_benefits"):
                env_data = outcome["environmental_benefits"]
                benefits["fertilizer_reduction"] += env_data.get("fertilizer_reduction", 0.0)
                benefits["water_conservation"] += env_data.get("water_conservation", 0.0)
                benefits["soil_health_improvement"] += env_data.get("soil_health_improvement", 0.0)
                benefits["carbon_sequestration"] += env_data.get("carbon_sequestration", 0.0)
        
        return benefits
    
    async def calculate_system_performance(
        self,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> SystemPerformanceMetrics:
        """
        Calculate system performance metrics.
        
        Args:
            period: Analysis period
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            SystemPerformanceMetrics with performance analysis
        """
        try:
            logger.info(f"Calculating system performance for period {period}")
            
            # Filter system metrics by date range
            period_metrics = [
                metric for metric in self.system_metrics
                if start_date <= datetime.fromisoformat(metric["timestamp"]) <= end_date
            ]
            
            if not period_metrics:
                # Return default metrics if no data available
                return SystemPerformanceMetrics(
                    period=period,
                    total_requests=0,
                    average_response_time_ms=0.0,
                    error_rate=0.0,
                    uptime_percentage=100.0,
                    throughput_per_hour=0.0,
                    resource_utilization={
                        "cpu_usage": 0.0,
                        "memory_usage": 0.0,
                        "disk_usage": 0.0,
                        "network_usage": 0.0
                    }
                )
            
            # Calculate aggregate metrics
            total_requests = sum(metric.get("requests", 0) for metric in period_metrics)
            
            response_times = [
                metric.get("response_time_ms", 0) 
                for metric in period_metrics 
                if metric.get("response_time_ms") is not None
            ]
            average_response_time_ms = (
                statistics.mean(response_times) 
                if response_times else 0.0
            )
            
            errors = sum(metric.get("errors", 0) for metric in period_metrics)
            error_rate = errors / total_requests if total_requests > 0 else 0.0
            
            # Calculate uptime
            uptime_percentage = (
                sum(metric.get("uptime_percentage", 100) for metric in period_metrics) / len(period_metrics)
            )
            
            # Calculate throughput
            period_hours = (end_date - start_date).total_seconds() / 3600
            throughput_per_hour = total_requests / period_hours if period_hours > 0 else 0.0
            
            # Calculate resource utilization
            resource_utilization = self._calculate_resource_utilization(period_metrics)
            
            metrics = SystemPerformanceMetrics(
                period=period,
                total_requests=total_requests,
                average_response_time_ms=average_response_time_ms,
                error_rate=error_rate,
                uptime_percentage=uptime_percentage,
                throughput_per_hour=throughput_per_hour,
                resource_utilization=resource_utilization
            )
            
            # Store analytics data
            self.analytics_data["system_performance"].append(metrics.__dict__)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating system performance for period {period}: {e}")
            raise
    
    def _calculate_resource_utilization(self, period_metrics: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate average resource utilization."""
        utilization = defaultdict(list)
        
        for metric in period_metrics:
            if "resource_utilization" in metric:
                for resource, value in metric["resource_utilization"].items():
                    utilization[resource].append(value)
        
        # Ensure all required fields are present with default values
        result = {
            "cpu_usage": 0.0,
            "memory_usage": 0.0,
            "disk_usage": 0.0,
            "network_usage": 0.0
        }
        
        # Update with calculated values if available
        for resource, values in utilization.items():
            if values:
                result[resource] = statistics.mean(values)
        
        return result
    
    async def analyze_usage_patterns(
        self,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> UsagePatternAnalysis:
        """
        Analyze usage patterns and trends.
        
        Args:
            period: Analysis period
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            UsagePatternAnalysis with pattern insights
        """
        try:
            logger.info(f"Analyzing usage patterns for period {period}")
            
            # Filter session data by date range
            period_sessions = []
            for user_sessions in self.user_sessions.values():
                for session in user_sessions:
                    session_date = datetime.fromisoformat(session["timestamp"])
                    if start_date <= session_date <= end_date:
                        period_sessions.append(session)
            
            # Analyze peak usage hours
            hour_counts = Counter()
            for session in period_sessions:
                hour = datetime.fromisoformat(session["timestamp"]).hour
                hour_counts[hour] += 1
            
            peak_usage_hours = [hour for hour, count in hour_counts.most_common(3)]
            
            # Analyze most used features
            feature_counts = Counter()
            for session in period_sessions:
                for feature in session.get("features_used", []):
                    feature_counts[feature] += 1
            
            most_used_features = [feature for feature, count in feature_counts.most_common(5)]
            
            # Analyze seasonal patterns
            seasonal_patterns = self._analyze_seasonal_patterns(period_sessions)
            
            # Analyze geographic distribution
            geographic_distribution = self._analyze_geographic_distribution(period_sessions)
            
            # Analyze user segments
            user_segments = self._analyze_user_segments(period_sessions)
            
            analysis = UsagePatternAnalysis(
                period=period,
                peak_usage_hours=peak_usage_hours,
                most_used_features=most_used_features,
                seasonal_patterns=seasonal_patterns,
                geographic_distribution=geographic_distribution,
                user_segments=user_segments
            )
            
            # Store analytics data
            self.analytics_data["usage_patterns"].append(analysis.__dict__)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing usage patterns for period {period}: {e}")
            raise
    
    def _analyze_seasonal_patterns(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze seasonal usage patterns."""
        seasonal_counts = defaultdict(int)
        
        for session in sessions:
            month = datetime.fromisoformat(session["timestamp"]).month
            season = self._get_season(month)
            seasonal_counts[season] += 1
        
        return dict(seasonal_counts)
    
    def _get_season(self, month: int) -> str:
        """Get season from month."""
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "fall"
    
    def _analyze_geographic_distribution(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze geographic distribution of usage."""
        region_counts = defaultdict(int)
        
        for session in sessions:
            region = session.get("region", "unknown")
            region_counts[region] += 1
        
        return dict(region_counts)
    
    def _analyze_user_segments(self, sessions: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze user segments."""
        segment_counts = defaultdict(int)
        
        for session in sessions:
            user_type = session.get("user_type", "unknown")
            segment_counts[user_type] += 1
        
        return dict(segment_counts)
    
    async def generate_comprehensive_report(
        self,
        report_type: str,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> AnalyticsReport:
        """
        Generate comprehensive analytics report.
        
        Args:
            report_type: Type of report to generate
            period: Analysis period
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            AnalyticsReport with comprehensive analysis
        """
        try:
            logger.info(f"Generating comprehensive report for period {period}")
            
            report_id = str(uuid4())
            generated_at = datetime.now().isoformat()
            
            # Calculate all metrics
            user_engagement = await self._calculate_aggregate_user_engagement(period, start_date, end_date)
            recommendation_effectiveness = await self._get_recommendation_effectiveness(period, start_date, end_date)
            agricultural_impact = await self.calculate_agricultural_impact(period, start_date, end_date)
            system_performance = await self.calculate_system_performance(period, start_date, end_date)
            usage_patterns = await self.analyze_usage_patterns(period, start_date, end_date)
            
            # Generate key insights
            key_insights = self._generate_key_insights(
                user_engagement, recommendation_effectiveness, 
                agricultural_impact, system_performance, usage_patterns
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                user_engagement, recommendation_effectiveness,
                agricultural_impact, system_performance, usage_patterns
            )
            
            report = AnalyticsReport(
                report_id=report_id,
                report_type=report_type,
                period=period,
                generated_at=generated_at,
                user_engagement=user_engagement,
                recommendation_effectiveness=recommendation_effectiveness,
                agricultural_impact=agricultural_impact,
                system_performance=system_performance,
                usage_patterns=usage_patterns,
                key_insights=key_insights,
                recommendations=recommendations
            )
            
            # Store report
            self.analytics_data["reports"].append(report.__dict__)
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report for period {period}: {e}")
            raise
    
    async def _calculate_aggregate_user_engagement(
        self,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> UserEngagementMetrics:
        """Calculate aggregate user engagement metrics."""
        # This would aggregate engagement metrics across all users
        # For now, return a representative sample
        return UserEngagementMetrics(
            user_id="aggregate",
            session_count=0,
            total_time_minutes=0.0,
            recommendations_requested=0,
            recommendations_implemented=0,
            feedback_provided=0,
            features_used=[],
            last_activity=datetime.now().isoformat(),
            engagement_score=0.0
        )
    
    async def _get_recommendation_effectiveness(
        self,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[RecommendationEffectiveness]:
        """Get recommendation effectiveness data for period."""
        period_data = [
            outcome for outcome in self.recommendation_outcomes.values()
            if start_date <= datetime.fromisoformat(outcome["timestamp"]) <= end_date
        ]
        
        effectiveness_list = []
        for outcome in period_data:
            effectiveness = RecommendationEffectiveness(
                recommendation_id=outcome.get("recommendation_id", ""),
                method_recommended=outcome.get("method_recommended", ""),
                method_implemented=outcome.get("method_implemented"),
                farmer_satisfaction=outcome.get("farmer_satisfaction"),
                yield_impact=outcome.get("yield_impact"),
                cost_savings=outcome.get("cost_savings"),
                implementation_rate=1.0 if outcome.get("method_implemented") else 0.0,
                success_score=self._calculate_success_score(
                    outcome.get("farmer_satisfaction"),
                    outcome.get("yield_impact"),
                    outcome.get("cost_savings"),
                    1.0 if outcome.get("method_implemented") else 0.0
                )
            )
            effectiveness_list.append(effectiveness)
        
        return effectiveness_list
    
    def _generate_key_insights(
        self,
        user_engagement: UserEngagementMetrics,
        recommendation_effectiveness: List[RecommendationEffectiveness],
        agricultural_impact: AgriculturalImpactMetrics,
        system_performance: SystemPerformanceMetrics,
        usage_patterns: UsagePatternAnalysis
    ) -> List[str]:
        """Generate key insights from analytics data."""
        insights = []
        
        # User engagement insights
        if user_engagement.engagement_score > 0.7:
            insights.append("High user engagement indicates strong platform adoption")
        elif user_engagement.engagement_score < 0.3:
            insights.append("Low user engagement suggests need for improved user experience")
        
        # Recommendation effectiveness insights
        if recommendation_effectiveness:
            avg_success = statistics.mean([r.success_score for r in recommendation_effectiveness])
            if avg_success > 0.8:
                insights.append("Recommendations show high success rates and farmer satisfaction")
            elif avg_success < 0.5:
                insights.append("Recommendation effectiveness needs improvement")
        
        # Agricultural impact insights
        if agricultural_impact.adoption_rate > 0.7:
            insights.append("High adoption rate indicates strong farmer trust in recommendations")
        if agricultural_impact.estimated_yield_increase > 0:
            insights.append(f"System has contributed to {agricultural_impact.estimated_yield_increase:.1f}% yield increase")
        
        # System performance insights
        if system_performance.average_response_time_ms < 2000:
            insights.append("System performance is excellent with fast response times")
        elif system_performance.average_response_time_ms > 5000:
            insights.append("System performance needs optimization for better user experience")
        
        # Usage pattern insights
        if usage_patterns.peak_usage_hours:
            insights.append(f"Peak usage occurs during hours: {', '.join(map(str, usage_patterns.peak_usage_hours))}")
        
        return insights
    
    def _generate_recommendations(
        self,
        user_engagement: UserEngagementMetrics,
        recommendation_effectiveness: List[RecommendationEffectiveness],
        agricultural_impact: AgriculturalImpactMetrics,
        system_performance: SystemPerformanceMetrics,
        usage_patterns: UsagePatternAnalysis
    ) -> List[str]:
        """Generate actionable recommendations from analytics."""
        recommendations = []
        
        # User engagement recommendations
        if user_engagement.engagement_score < 0.5:
            recommendations.append("Implement user onboarding improvements and feature tutorials")
        
        # Recommendation effectiveness recommendations
        if recommendation_effectiveness:
            avg_implementation = statistics.mean([r.implementation_rate for r in recommendation_effectiveness])
            if avg_implementation < 0.6:
                recommendations.append("Improve recommendation presentation and farmer education")
        
        # Agricultural impact recommendations
        if agricultural_impact.adoption_rate < 0.5:
            recommendations.append("Focus on building farmer trust through demonstration programs")
        
        # System performance recommendations
        if system_performance.error_rate > 0.05:
            recommendations.append("Investigate and resolve system errors to improve reliability")
        
        if system_performance.average_response_time_ms > 3000:
            recommendations.append("Optimize system performance and consider infrastructure scaling")
        
        # Usage pattern recommendations
        if usage_patterns.most_used_features:
            recommendations.append(f"Enhance popular features: {', '.join(usage_patterns.most_used_features[:3])}")
        
        return recommendations
    
    async def track_system_metric(self, metric_data: Dict[str, Any]):
        """Track system performance metric."""
        self.system_metrics.append({
            **metric_data,
            "timestamp": datetime.now().isoformat()
        })
    
    async def get_analytics_summary(self, period: str = "monthly") -> Dict[str, Any]:
        """Get analytics summary for a period."""
        try:
            # Calculate date range
            end_date = datetime.now()
            if period == "daily":
                start_date = end_date - timedelta(days=1)
            elif period == "weekly":
                start_date = end_date - timedelta(weeks=1)
            elif period == "monthly":
                start_date = end_date - timedelta(days=30)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get summary data
            agricultural_impact = await self.calculate_agricultural_impact(period, start_date, end_date)
            system_performance = await self.calculate_system_performance(period, start_date, end_date)
            usage_patterns = await self.analyze_usage_patterns(period, start_date, end_date)
            
            return {
                "period": period,
                "agricultural_impact": agricultural_impact.__dict__,
                "system_performance": system_performance.__dict__,
                "usage_patterns": usage_patterns.__dict__,
                "summary_generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics summary for period {period}: {e}")
            raise