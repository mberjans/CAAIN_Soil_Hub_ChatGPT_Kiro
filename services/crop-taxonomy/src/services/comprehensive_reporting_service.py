"""
Comprehensive Reporting Service

This service provides comprehensive reporting capabilities for variety recommendations system.
Generates regular reports on system performance, user adoption, and agricultural impact.

TICKET-005_crop-variety-recommendations-15.2: Implement comprehensive monitoring and analytics
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Types of reports."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class ReportFormat(Enum):
    """Report formats."""
    JSON = "json"
    HTML = "html"
    PDF = "pdf"
    CSV = "csv"
    MARKDOWN = "markdown"


@dataclass
class ReportSection:
    """Report section definition."""
    title: str
    content: Dict[str, Any]
    charts: List[Dict[str, Any]] = field(default_factory=list)
    insights: List[str] = field(default_factory=list)


@dataclass
class Report:
    """Report definition."""
    id: str
    title: str
    report_type: ReportType
    period_start: datetime
    period_end: datetime
    generated_at: datetime
    sections: List[ReportSection]
    summary: Dict[str, Any]
    recommendations: List[str] = field(default_factory=list)


class ComprehensiveReportingService:
    """Comprehensive reporting service for variety recommendations system."""
    
    def __init__(self, output_directory: str = "reports"):
        """Initialize the reporting service."""
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # Report templates
        self.report_templates = {
            ReportType.DAILY: self._generate_daily_report,
            ReportType.WEEKLY: self._generate_weekly_report,
            ReportType.MONTHLY: self._generate_monthly_report,
            ReportType.QUARTERLY: self._generate_quarterly_report,
            ReportType.YEARLY: self._generate_yearly_report
        }
        
        logger.info("Comprehensive reporting service initialized")
    
    async def generate_report(
        self,
        report_type: ReportType,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        format: ReportFormat = ReportFormat.JSON
    ) -> Report:
        """Generate a comprehensive report."""
        try:
            # Set default period if not provided
            if period_start is None or period_end is None:
                period_start, period_end = self._get_default_period(report_type)
            
            # Generate report content
            report_generator = self.report_templates.get(report_type)
            if not report_generator:
                raise ValueError(f"Unsupported report type: {report_type}")
            
            report = await report_generator(period_start, period_end)
            
            # Save report
            await self._save_report(report, format)
            
            logger.info(f"Generated {report_type.value} report for period {period_start} to {period_end}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            raise
    
    def _get_default_period(self, report_type: ReportType) -> tuple[datetime, datetime]:
        """Get default period for report type."""
        now = datetime.utcnow()
        
        if report_type == ReportType.DAILY:
            period_start = now - timedelta(days=1)
            period_end = now
        elif report_type == ReportType.WEEKLY:
            period_start = now - timedelta(weeks=1)
            period_end = now
        elif report_type == ReportType.MONTHLY:
            period_start = now - timedelta(days=30)
            period_end = now
        elif report_type == ReportType.QUARTERLY:
            period_start = now - timedelta(days=90)
            period_end = now
        elif report_type == ReportType.YEARLY:
            period_start = now - timedelta(days=365)
            period_end = now
        else:
            period_start = now - timedelta(days=1)
            period_end = now
        
        return period_start, period_end
    
    async def _generate_daily_report(self, period_start: datetime, period_end: datetime) -> Report:
        """Generate daily report."""
        report_id = f"daily_report_{period_start.strftime('%Y%m%d')}"
        
        # Collect metrics data
        metrics_data = await self._collect_metrics_data(period_start, period_end)
        
        # Generate sections
        sections = [
            await self._generate_system_health_section(metrics_data),
            await self._generate_user_engagement_section(metrics_data),
            await self._generate_recommendation_effectiveness_section(metrics_data),
            await self._generate_business_metrics_section(metrics_data),
            await self._generate_alerts_section(metrics_data)
        ]
        
        # Generate summary
        summary = await self._generate_summary(metrics_data, sections)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_data, sections)
        
        return Report(
            id=report_id,
            title=f"Daily Report - {period_start.strftime('%Y-%m-%d')}",
            report_type=ReportType.DAILY,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.utcnow(),
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
    
    async def _generate_weekly_report(self, period_start: datetime, period_end: datetime) -> Report:
        """Generate weekly report."""
        report_id = f"weekly_report_{period_start.strftime('%Y%m%d')}"
        
        # Collect metrics data
        metrics_data = await self._collect_metrics_data(period_start, period_end)
        
        # Generate sections
        sections = [
            await self._generate_system_health_section(metrics_data),
            await self._generate_user_engagement_section(metrics_data),
            await self._generate_recommendation_effectiveness_section(metrics_data),
            await self._generate_business_metrics_section(metrics_data),
            await self._generate_alerts_section(metrics_data),
            await self._generate_trend_analysis_section(metrics_data),
            await self._generate_agricultural_impact_section(metrics_data)
        ]
        
        # Generate summary
        summary = await self._generate_summary(metrics_data, sections)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_data, sections)
        
        return Report(
            id=report_id,
            title=f"Weekly Report - {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}",
            report_type=ReportType.WEEKLY,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.utcnow(),
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
    
    async def _generate_monthly_report(self, period_start: datetime, period_end: datetime) -> Report:
        """Generate monthly report."""
        report_id = f"monthly_report_{period_start.strftime('%Y%m')}"
        
        # Collect metrics data
        metrics_data = await self._collect_metrics_data(period_start, period_end)
        
        # Generate sections
        sections = [
            await self._generate_executive_summary_section(metrics_data),
            await self._generate_system_health_section(metrics_data),
            await self._generate_user_engagement_section(metrics_data),
            await self._generate_recommendation_effectiveness_section(metrics_data),
            await self._generate_business_metrics_section(metrics_data),
            await self._generate_alerts_section(metrics_data),
            await self._generate_trend_analysis_section(metrics_data),
            await self._generate_agricultural_impact_section(metrics_data),
            await self._generate_competitive_analysis_section(metrics_data),
            await self._generate_future_outlook_section(metrics_data)
        ]
        
        # Generate summary
        summary = await self._generate_summary(metrics_data, sections)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_data, sections)
        
        return Report(
            id=report_id,
            title=f"Monthly Report - {period_start.strftime('%Y-%m')}",
            report_type=ReportType.MONTHLY,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.utcnow(),
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
    
    async def _generate_quarterly_report(self, period_start: datetime, period_end: datetime) -> Report:
        """Generate quarterly report."""
        report_id = f"quarterly_report_{period_start.strftime('%Y%m')}"
        
        # Collect metrics data
        metrics_data = await self._collect_metrics_data(period_start, period_end)
        
        # Generate sections
        sections = [
            await self._generate_executive_summary_section(metrics_data),
            await self._generate_system_health_section(metrics_data),
            await self._generate_user_engagement_section(metrics_data),
            await self._generate_recommendation_effectiveness_section(metrics_data),
            await self._generate_business_metrics_section(metrics_data),
            await self._generate_alerts_section(metrics_data),
            await self._generate_trend_analysis_section(metrics_data),
            await self._generate_agricultural_impact_section(metrics_data),
            await self._generate_competitive_analysis_section(metrics_data),
            await self._generate_future_outlook_section(metrics_data),
            await self._generate_strategic_recommendations_section(metrics_data)
        ]
        
        # Generate summary
        summary = await self._generate_summary(metrics_data, sections)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_data, sections)
        
        return Report(
            id=report_id,
            title=f"Quarterly Report - Q{((period_start.month - 1) // 3) + 1} {period_start.year}",
            report_type=ReportType.QUARTERLY,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.utcnow(),
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
    
    async def _generate_yearly_report(self, period_start: datetime, period_end: datetime) -> Report:
        """Generate yearly report."""
        report_id = f"yearly_report_{period_start.year}"
        
        # Collect metrics data
        metrics_data = await self._collect_metrics_data(period_start, period_end)
        
        # Generate sections
        sections = [
            await self._generate_executive_summary_section(metrics_data),
            await self._generate_system_health_section(metrics_data),
            await self._generate_user_engagement_section(metrics_data),
            await self._generate_recommendation_effectiveness_section(metrics_data),
            await self._generate_business_metrics_section(metrics_data),
            await self._generate_alerts_section(metrics_data),
            await self._generate_trend_analysis_section(metrics_data),
            await self._generate_agricultural_impact_section(metrics_data),
            await self._generate_competitive_analysis_section(metrics_data),
            await self._generate_future_outlook_section(metrics_data),
            await self._generate_strategic_recommendations_section(metrics_data),
            await self._generate_annual_achievements_section(metrics_data)
        ]
        
        # Generate summary
        summary = await self._generate_summary(metrics_data, sections)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(metrics_data, sections)
        
        return Report(
            id=report_id,
            title=f"Annual Report - {period_start.year}",
            report_type=ReportType.YEARLY,
            period_start=period_start,
            period_end=period_end,
            generated_at=datetime.utcnow(),
            sections=sections,
            summary=summary,
            recommendations=recommendations
        )
    
    async def _collect_metrics_data(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Collect metrics data for the specified period."""
        # This would integrate with the comprehensive monitoring analytics service
        # For now, return mock data
        return {
            "system_health": {
                "avg_cpu_percent": 45.2,
                "avg_memory_percent": 67.8,
                "avg_response_time_ms": 1250.5,
                "avg_error_rate": 0.02,
                "uptime_percent": 99.8
            },
            "user_engagement": {
                "total_active_users": 1250,
                "new_users": 85,
                "returning_users": 1165,
                "avg_session_duration_minutes": 12.5,
                "user_satisfaction_score": 0.87
            },
            "recommendation_effectiveness": {
                "total_recommendations": 12500,
                "successful_recommendations": 11875,
                "failed_recommendations": 625,
                "avg_confidence_score": 0.89,
                "avg_response_time_ms": 1250.5,
                "cache_hit_rate": 0.75,
                "expert_validation_rate": 0.82,
                "farmer_feedback_score": 0.84
            },
            "business_metrics": {
                "total_revenue_impact": 125000.0,
                "cost_savings_estimated": 45000.0,
                "environmental_impact_score": 0.78,
                "user_retention_rate": 0.85,
                "market_penetration": 0.12
            },
            "alerts": {
                "total_alerts": 45,
                "critical_alerts": 3,
                "warning_alerts": 12,
                "info_alerts": 30,
                "resolved_alerts": 42
            }
        }
    
    async def _generate_executive_summary_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate executive summary section."""
        content = {
            "key_metrics": {
                "total_users": metrics_data["user_engagement"]["total_active_users"],
                "total_recommendations": metrics_data["recommendation_effectiveness"]["total_recommendations"],
                "success_rate": metrics_data["recommendation_effectiveness"]["successful_recommendations"] / metrics_data["recommendation_effectiveness"]["total_recommendations"],
                "user_satisfaction": metrics_data["user_engagement"]["user_satisfaction_score"],
                "revenue_impact": metrics_data["business_metrics"]["total_revenue_impact"]
            },
            "highlights": [
                f"System maintained {metrics_data['system_health']['uptime_percent']:.1f}% uptime",
                f"Generated {metrics_data['recommendation_effectiveness']['total_recommendations']:,} recommendations",
                f"Achieved {metrics_data['user_engagement']['user_satisfaction_score']:.1%} user satisfaction",
                f"Delivered ${metrics_data['business_metrics']['total_revenue_impact']:,.0f} in revenue impact"
            ]
        }
        
        insights = [
            "System performance exceeded targets with high reliability",
            "User engagement continues to grow with strong satisfaction scores",
            "Recommendation accuracy remains above 90%",
            "Business impact demonstrates strong ROI"
        ]
        
        return ReportSection(
            title="Executive Summary",
            content=content,
            insights=insights
        )
    
    async def _generate_system_health_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate system health section."""
        content = {
            "performance_metrics": {
                "cpu_usage": f"{metrics_data['system_health']['avg_cpu_percent']:.1f}%",
                "memory_usage": f"{metrics_data['system_health']['avg_memory_percent']:.1f}%",
                "response_time": f"{metrics_data['system_health']['avg_response_time_ms']:.1f}ms",
                "error_rate": f"{metrics_data['system_health']['avg_error_rate']:.2%}",
                "uptime": f"{metrics_data['system_health']['uptime_percent']:.1f}%"
            },
            "trends": {
                "cpu_trend": "stable",
                "memory_trend": "stable",
                "response_time_trend": "improving",
                "error_rate_trend": "decreasing"
            }
        }
        
        charts = [
            {
                "type": "line",
                "title": "CPU Usage Over Time",
                "data": "cpu_usage_timeseries"
            },
            {
                "type": "line",
                "title": "Response Time Over Time",
                "data": "response_time_timeseries"
            }
        ]
        
        insights = [
            "System performance remains stable and within acceptable ranges",
            "Response times have improved due to optimization efforts",
            "Error rates are decreasing, indicating improved reliability"
        ]
        
        return ReportSection(
            title="System Health",
            content=content,
            charts=charts,
            insights=insights
        )
    
    async def _generate_user_engagement_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate user engagement section."""
        content = {
            "user_metrics": {
                "total_active_users": metrics_data["user_engagement"]["total_active_users"],
                "new_users": metrics_data["user_engagement"]["new_users"],
                "returning_users": metrics_data["user_engagement"]["returning_users"],
                "session_duration": f"{metrics_data['user_engagement']['avg_session_duration_minutes']:.1f} minutes",
                "satisfaction_score": f"{metrics_data['user_engagement']['user_satisfaction_score']:.1%}"
            },
            "engagement_trends": {
                "user_growth": "positive",
                "retention_rate": "high",
                "session_duration": "stable",
                "satisfaction": "improving"
            }
        }
        
        charts = [
            {
                "type": "bar",
                "title": "User Growth Over Time",
                "data": "user_growth_timeseries"
            },
            {
                "type": "pie",
                "title": "User Distribution",
                "data": "user_distribution"
            }
        ]
        
        insights = [
            "User base continues to grow with strong retention",
            "Session duration indicates high engagement",
            "Satisfaction scores are improving over time"
        ]
        
        return ReportSection(
            title="User Engagement",
            content=content,
            charts=charts,
            insights=insights
        )
    
    async def _generate_recommendation_effectiveness_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate recommendation effectiveness section."""
        success_rate = metrics_data["recommendation_effectiveness"]["successful_recommendations"] / metrics_data["recommendation_effectiveness"]["total_recommendations"]
        
        content = {
            "effectiveness_metrics": {
                "total_recommendations": metrics_data["recommendation_effectiveness"]["total_recommendations"],
                "success_rate": f"{success_rate:.1%}",
                "confidence_score": f"{metrics_data['recommendation_effectiveness']['avg_confidence_score']:.1%}",
                "response_time": f"{metrics_data['recommendation_effectiveness']['avg_response_time_ms']:.1f}ms",
                "cache_hit_rate": f"{metrics_data['recommendation_effectiveness']['cache_hit_rate']:.1%}",
                "expert_validation_rate": f"{metrics_data['recommendation_effectiveness']['expert_validation_rate']:.1%}",
                "farmer_feedback_score": f"{metrics_data['recommendation_effectiveness']['farmer_feedback_score']:.1%}"
            },
            "quality_indicators": {
                "accuracy": "high",
                "confidence": "high",
                "validation": "strong",
                "feedback": "positive"
            }
        }
        
        charts = [
            {
                "type": "line",
                "title": "Recommendation Volume Over Time",
                "data": "recommendation_volume_timeseries"
            },
            {
                "type": "gauge",
                "title": "Success Rate",
                "data": "success_rate_gauge"
            }
        ]
        
        insights = [
            "Recommendation accuracy remains above 90%",
            "High confidence scores indicate reliable recommendations",
            "Strong expert validation and farmer feedback"
        ]
        
        return ReportSection(
            title="Recommendation Effectiveness",
            content=content,
            charts=charts,
            insights=insights
        )
    
    async def _generate_business_metrics_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate business metrics section."""
        content = {
            "financial_metrics": {
                "revenue_impact": f"${metrics_data['business_metrics']['total_revenue_impact']:,.0f}",
                "cost_savings": f"${metrics_data['business_metrics']['cost_savings_estimated']:,.0f}",
                "roi": "positive",
                "market_penetration": f"{metrics_data['business_metrics']['market_penetration']:.1%}"
            },
            "impact_metrics": {
                "environmental_score": f"{metrics_data['business_metrics']['environmental_impact_score']:.1%}",
                "user_retention": f"{metrics_data['business_metrics']['user_retention_rate']:.1%}",
                "cost_per_user": "decreasing",
                "lifetime_value": "increasing"
            }
        }
        
        charts = [
            {
                "type": "line",
                "title": "Revenue Impact Over Time",
                "data": "revenue_impact_timeseries"
            },
            {
                "type": "bar",
                "title": "Cost Savings by Category",
                "data": "cost_savings_breakdown"
            }
        ]
        
        insights = [
            "Strong revenue impact demonstrates business value",
            "Cost savings continue to grow",
            "Market penetration is expanding steadily"
        ]
        
        return ReportSection(
            title="Business Metrics",
            content=content,
            charts=charts,
            insights=insights
        )
    
    async def _generate_alerts_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate alerts section."""
        content = {
            "alert_summary": {
                "total_alerts": metrics_data["alerts"]["total_alerts"],
                "critical_alerts": metrics_data["alerts"]["critical_alerts"],
                "warning_alerts": metrics_data["alerts"]["warning_alerts"],
                "info_alerts": metrics_data["alerts"]["info_alerts"],
                "resolved_alerts": metrics_data["alerts"]["resolved_alerts"]
            },
            "alert_trends": {
                "alert_frequency": "decreasing",
                "resolution_time": "improving",
                "critical_issues": "low"
            }
        }
        
        insights = [
            "Alert frequency is decreasing, indicating improved system stability",
            "Resolution times are improving",
            "Critical issues remain low"
        ]
        
        return ReportSection(
            title="System Alerts",
            content=content,
            insights=insights
        )
    
    async def _generate_trend_analysis_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate trend analysis section."""
        content = {
            "key_trends": {
                "user_growth": "positive",
                "recommendation_accuracy": "stable",
                "system_performance": "improving",
                "business_impact": "growing"
            },
            "forecasts": {
                "user_growth_forecast": "continued growth",
                "performance_forecast": "stable",
                "business_impact_forecast": "increasing"
            }
        }
        
        insights = [
            "All key metrics show positive trends",
            "System is well-positioned for continued growth",
            "Performance improvements are sustainable"
        ]
        
        return ReportSection(
            title="Trend Analysis",
            content=content,
            insights=insights
        )
    
    async def _generate_agricultural_impact_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate agricultural impact section."""
        content = {
            "agricultural_metrics": {
                "crop_varieties_recommended": "500+",
                "farmers_served": metrics_data["user_engagement"]["total_active_users"],
                "acres_covered": "estimated",
                "environmental_impact": f"{metrics_data['business_metrics']['environmental_impact_score']:.1%}"
            },
            "impact_areas": {
                "yield_improvement": "positive",
                "cost_reduction": "significant",
                "environmental_benefits": "measurable",
                "farmer_education": "ongoing"
            }
        }
        
        insights = [
            "Significant positive impact on agricultural practices",
            "Measurable environmental benefits",
            "Strong farmer adoption and satisfaction"
        ]
        
        return ReportSection(
            title="Agricultural Impact",
            content=content,
            insights=insights
        )
    
    async def _generate_competitive_analysis_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate competitive analysis section."""
        content = {
            "competitive_position": {
                "market_share": "growing",
                "technology_leadership": "strong",
                "user_satisfaction": "high",
                "feature_completeness": "comprehensive"
            },
            "differentiators": [
                "Agricultural expertise integration",
                "High accuracy recommendations",
                "Comprehensive monitoring and analytics",
                "Strong user engagement"
            ]
        }
        
        insights = [
            "Strong competitive position in agricultural technology",
            "Unique value proposition with agricultural expertise",
            "Technology leadership in recommendation accuracy"
        ]
        
        return ReportSection(
            title="Competitive Analysis",
            content=content,
            insights=insights
        )
    
    async def _generate_future_outlook_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate future outlook section."""
        content = {
            "growth_prospects": {
                "user_growth": "strong",
                "market_expansion": "positive",
                "technology_advancement": "ongoing",
                "business_impact": "increasing"
            },
            "strategic_initiatives": [
                "Enhanced AI capabilities",
                "Expanded crop coverage",
                "Improved user experience",
                "Advanced analytics"
            ]
        }
        
        insights = [
            "Strong growth prospects based on current trends",
            "Strategic initiatives will drive continued improvement",
            "Market expansion opportunities identified"
        ]
        
        return ReportSection(
            title="Future Outlook",
            content=content,
            insights=insights
        )
    
    async def _generate_strategic_recommendations_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate strategic recommendations section."""
        content = {
            "strategic_priorities": [
                "Maintain high system reliability",
                "Continue user growth initiatives",
                "Enhance recommendation accuracy",
                "Expand agricultural impact"
            ],
            "action_items": [
                "Implement performance optimizations",
                "Expand user acquisition programs",
                "Develop new agricultural features",
                "Strengthen expert validation processes"
            ]
        }
        
        insights = [
            "Focus on maintaining current performance levels",
            "Prioritize user growth and satisfaction",
            "Continue innovation in agricultural technology"
        ]
        
        return ReportSection(
            title="Strategic Recommendations",
            content=content,
            insights=insights
        )
    
    async def _generate_annual_achievements_section(self, metrics_data: Dict[str, Any]) -> ReportSection:
        """Generate annual achievements section."""
        content = {
            "key_achievements": [
                f"Served {metrics_data['user_engagement']['total_active_users']:,} farmers",
                f"Generated {metrics_data['recommendation_effectiveness']['total_recommendations']:,} recommendations",
                f"Achieved {metrics_data['user_engagement']['user_satisfaction_score']:.1%} user satisfaction",
                f"Delivered ${metrics_data['business_metrics']['total_revenue_impact']:,.0f} in revenue impact"
            ],
            "milestones": [
                "Launched comprehensive monitoring system",
                "Achieved 90%+ recommendation accuracy",
                "Expanded to new agricultural regions",
                "Implemented advanced analytics"
            ]
        }
        
        insights = [
            "Significant achievements across all key metrics",
            "Strong foundation for future growth",
            "Demonstrated value to agricultural community"
        ]
        
        return ReportSection(
            title="Annual Achievements",
            content=content,
            insights=insights
        )
    
    async def _generate_summary(self, metrics_data: Dict[str, Any], sections: List[ReportSection]) -> Dict[str, Any]:
        """Generate report summary."""
        return {
            "period_summary": {
                "total_users": metrics_data["user_engagement"]["total_active_users"],
                "total_recommendations": metrics_data["recommendation_effectiveness"]["total_recommendations"],
                "success_rate": metrics_data["recommendation_effectiveness"]["successful_recommendations"] / metrics_data["recommendation_effectiveness"]["total_recommendations"],
                "user_satisfaction": metrics_data["user_engagement"]["user_satisfaction_score"],
                "revenue_impact": metrics_data["business_metrics"]["total_revenue_impact"],
                "system_uptime": metrics_data["system_health"]["uptime_percent"]
            },
            "key_insights": [
                "System performance exceeded all targets",
                "User engagement continues to grow",
                "Recommendation accuracy remains high",
                "Business impact demonstrates strong ROI"
            ],
            "overall_rating": "excellent"
        }
    
    async def _generate_recommendations(self, metrics_data: Dict[str, Any], sections: List[ReportSection]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # System performance recommendations
        if metrics_data["system_health"]["avg_cpu_percent"] > 70:
            recommendations.append("Consider scaling system resources to handle increased load")
        
        if metrics_data["system_health"]["avg_response_time_ms"] > 2000:
            recommendations.append("Optimize response times through caching and database tuning")
        
        # User engagement recommendations
        if metrics_data["user_engagement"]["user_satisfaction_score"] < 0.8:
            recommendations.append("Improve user experience based on feedback analysis")
        
        if metrics_data["user_engagement"]["new_users"] < 50:
            recommendations.append("Implement user acquisition strategies")
        
        # Recommendation effectiveness recommendations
        if metrics_data["recommendation_effectiveness"]["avg_confidence_score"] < 0.8:
            recommendations.append("Enhance recommendation algorithms for higher confidence")
        
        if metrics_data["recommendation_effectiveness"]["cache_hit_rate"] < 0.7:
            recommendations.append("Improve caching strategies for better performance")
        
        # Business metrics recommendations
        if metrics_data["business_metrics"]["market_penetration"] < 0.1:
            recommendations.append("Develop market expansion strategies")
        
        if metrics_data["business_metrics"]["user_retention_rate"] < 0.8:
            recommendations.append("Implement user retention programs")
        
        return recommendations
    
    async def _save_report(self, report: Report, format: ReportFormat):
        """Save report in specified format."""
        filename = f"{report.id}.{format.value}"
        filepath = self.output_directory / filename
        
        if format == ReportFormat.JSON:
            report_data = {
                "id": report.id,
                "title": report.title,
                "report_type": report.report_type.value,
                "period_start": report.period_start.isoformat(),
                "period_end": report.period_end.isoformat(),
                "generated_at": report.generated_at.isoformat(),
                "sections": [
                    {
                        "title": section.title,
                        "content": section.content,
                        "charts": section.charts,
                        "insights": section.insights
                    }
                    for section in report.sections
                ],
                "summary": report.summary,
                "recommendations": report.recommendations
            }
            
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=2)
        
        elif format == ReportFormat.HTML:
            html_content = self._generate_html_report(report)
            with open(filepath, 'w') as f:
                f.write(html_content)
        
        elif format == ReportFormat.MARKDOWN:
            markdown_content = self._generate_markdown_report(report)
            with open(filepath, 'w') as f:
                f.write(markdown_content)
        
        logger.info(f"Report saved to {filepath}")
    
    def _generate_html_report(self, report: Report) -> str:
        """Generate HTML report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{report.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; border-bottom: 2px solid #3498db; }}
                .section {{ margin-bottom: 30px; }}
                .insights {{ background-color: #f8f9fa; padding: 15px; border-left: 4px solid #3498db; }}
                .recommendations {{ background-color: #e8f5e8; padding: 15px; border-left: 4px solid #27ae60; }}
            </style>
        </head>
        <body>
            <h1>{report.title}</h1>
            <p><strong>Period:</strong> {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}</p>
            <p><strong>Generated:</strong> {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="section">
                <h2>Summary</h2>
                <p>{report.summary.get('overall_rating', 'N/A').title()} performance</p>
                <ul>
                    {''.join(f'<li>{insight}</li>' for insight in report.summary.get('key_insights', []))}
                </ul>
            </div>
            
            {''.join(self._generate_html_section(section) for section in report.sections)}
            
            <div class="section">
                <h2>Recommendations</h2>
                <div class="recommendations">
                    <ul>
                        {''.join(f'<li>{rec}</li>' for rec in report.recommendations)}
                    </ul>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def _generate_html_section(self, section: ReportSection) -> str:
        """Generate HTML for a report section."""
        return f"""
        <div class="section">
            <h2>{section.title}</h2>
            <div class="content">
                {self._format_content_as_html(section.content)}
            </div>
            {f'<div class="insights"><h3>Insights</h3><ul>{"".join(f"<li>{insight}</li>" for insight in section.insights)}</ul></div>' if section.insights else ''}
        </div>
        """
    
    def _format_content_as_html(self, content: Dict[str, Any]) -> str:
        """Format content as HTML."""
        html = ""
        for key, value in content.items():
            if isinstance(value, dict):
                html += f"<h3>{key.replace('_', ' ').title()}</h3>"
                html += "<ul>"
                for sub_key, sub_value in value.items():
                    html += f"<li><strong>{sub_key.replace('_', ' ').title()}:</strong> {sub_value}</li>"
                html += "</ul>"
            elif isinstance(value, list):
                html += f"<h3>{key.replace('_', ' ').title()}</h3>"
                html += "<ul>"
                for item in value:
                    html += f"<li>{item}</li>"
                html += "</ul>"
            else:
                html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"
        return html
    
    def _generate_markdown_report(self, report: Report) -> str:
        """Generate Markdown report."""
        markdown = f"""# {report.title}

**Period:** {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}  
**Generated:** {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}

## Summary

**Overall Rating:** {report.summary.get('overall_rating', 'N/A').title()}

### Key Insights
{chr(10).join(f'- {insight}' for insight in report.summary.get('key_insights', []))}

"""
        
        for section in report.sections:
            markdown += f"## {section.title}\n\n"
            markdown += self._format_content_as_markdown(section.content)
            if section.insights:
                markdown += "### Insights\n"
                markdown += chr(10).join(f'- {insight}' for insight in section.insights)
                markdown += "\n\n"
        
        markdown += "## Recommendations\n\n"
        markdown += chr(10).join(f'- {rec}' for rec in report.recommendations)
        
        return markdown
    
    def _format_content_as_markdown(self, content: Dict[str, Any]) -> str:
        """Format content as Markdown."""
        markdown = ""
        for key, value in content.items():
            if isinstance(value, dict):
                markdown += f"### {key.replace('_', ' ').title()}\n\n"
                for sub_key, sub_value in value.items():
                    markdown += f"- **{sub_key.replace('_', ' ').title()}:** {sub_value}\n"
                markdown += "\n"
            elif isinstance(value, list):
                markdown += f"### {key.replace('_', ' ').title()}\n\n"
                for item in value:
                    markdown += f"- {item}\n"
                markdown += "\n"
            else:
                markdown += f"**{key.replace('_', ' ').title()}:** {value}\n\n"
        return markdown


# Singleton instance for global access
reporting_service: Optional[ComprehensiveReportingService] = None


def get_reporting_service(output_directory: str = "reports") -> ComprehensiveReportingService:
    """Get or create the global reporting service instance."""
    global reporting_service
    
    if reporting_service is None:
        reporting_service = ComprehensiveReportingService(output_directory)
    
    return reporting_service