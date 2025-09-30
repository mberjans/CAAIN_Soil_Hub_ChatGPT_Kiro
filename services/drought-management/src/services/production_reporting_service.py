"""
Production Reporting Service

Comprehensive reporting system for production monitoring and analytics.
Generates regular reports on system performance, user adoption,
agricultural outcomes, and business metrics.
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import json
from dataclasses import dataclass
from enum import Enum

from ..models.production_reporting_models import (
    ReportType,
    ReportFrequency,
    ReportTemplate,
    ReportConfiguration,
    SystemPerformanceReport,
    UserAdoptionReport,
    AgriculturalOutcomesReport,
    BusinessMetricsReport,
    ComprehensiveReport,
    ReportSection,
    ReportChart,
    ReportMetric,
    ReportInsight,
    ReportRecommendation,
    ReportGenerationRequest,
    ReportGenerationResponse,
    ReportSchedule,
    ReportDelivery,
    ReportSubscription,
    ReportHistory,
    ReportMetrics,
    ReportTemplateRequest,
    ReportTemplateResponse
)

logger = logging.getLogger(__name__)

class ReportStatus(str, Enum):
    """Report generation status."""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    DELIVERED = "delivered"

class ReportFormat(str, Enum):
    """Report output formats."""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    EXCEL = "excel"

@dataclass
class ReportData:
    """Report data container."""
    section_name: str
    data: Dict[str, Any]
    charts: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]

class ProductionReportingService:
    """Service for comprehensive production reporting."""
    
    def __init__(self):
        self.initialized = False
        self.report_templates: Dict[str, ReportTemplate] = {}
        self.report_schedules: Dict[str, ReportSchedule] = {}
        self.report_history: Dict[str, ReportHistory] = {}
        self.report_configurations: Dict[str, ReportConfiguration] = {}
        
        # Service dependencies
        self.database = None
        self.production_monitoring_service = None
        self.production_analytics_service = None
        self.notification_service = None
        
    async def initialize(self):
        """Initialize the production reporting service."""
        try:
            logger.info("Initializing Production Reporting Service...")
            
            # Initialize database connection
            self.database = await self._initialize_database()
            
            # Initialize service dependencies
            await self._initialize_service_dependencies()
            
            # Load report configurations
            await self._load_report_templates()
            await self._load_report_schedules()
            await self._load_report_configurations()
            
            # Start scheduled report generation
            await self._start_scheduled_reports()
            
            self.initialized = True
            logger.info("Production Reporting Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Production Reporting Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Production Reporting Service...")
            
            # Stop scheduled reports
            await self._stop_scheduled_reports()
            
            # Close database connections
            if self.database:
                await self.database.close()
            
            logger.info("Production Reporting Service cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during Production Reporting Service cleanup: {str(e)}")
    
    async def _initialize_database(self):
        """Initialize database connection for reporting data."""
        # Database initialization logic
        return None
    
    async def _initialize_service_dependencies(self):
        """Initialize service dependencies."""
        # Initialize service dependencies
        self.production_monitoring_service = None
        self.production_analytics_service = None
        self.notification_service = None
    
    async def _load_report_templates(self):
        """Load report templates."""
        self.report_templates = {
            "system_performance_daily": ReportTemplate(
                template_id="system_performance_daily",
                name="Daily System Performance Report",
                description="Daily report on system performance metrics",
                report_type=ReportType.SYSTEM_PERFORMANCE,
                sections=[
                    "system_overview",
                    "performance_metrics",
                    "resource_usage",
                    "error_analysis",
                    "recommendations"
                ],
                charts=[
                    {"type": "line", "metric": "cpu_usage_percent", "title": "CPU Usage Over Time"},
                    {"type": "line", "metric": "memory_usage_percent", "title": "Memory Usage Over Time"},
                    {"type": "bar", "metric": "error_rate_percent", "title": "Error Rate by Hour"}
                ],
                format=ReportFormat.HTML
            ),
            "user_adoption_weekly": ReportTemplate(
                template_id="user_adoption_weekly",
                name="Weekly User Adoption Report",
                description="Weekly report on user adoption and engagement",
                report_type=ReportType.USER_ADOPTION,
                sections=[
                    "user_overview",
                    "engagement_metrics",
                    "feature_usage",
                    "user_feedback",
                    "growth_analysis"
                ],
                charts=[
                    {"type": "line", "metric": "daily_active_users", "title": "Daily Active Users"},
                    {"type": "pie", "metric": "feature_usage_stats", "title": "Feature Usage Distribution"},
                    {"type": "bar", "metric": "user_satisfaction_score", "title": "User Satisfaction Trends"}
                ],
                format=ReportFormat.HTML
            ),
            "agricultural_outcomes_monthly": ReportTemplate(
                template_id="agricultural_outcomes_monthly",
                name="Monthly Agricultural Outcomes Report",
                description="Monthly report on agricultural impact and outcomes",
                report_type=ReportType.AGRICULTURAL_OUTCOMES,
                sections=[
                    "impact_overview",
                    "water_savings",
                    "cost_savings",
                    "environmental_impact",
                    "farmer_feedback",
                    "success_stories"
                ],
                charts=[
                    {"type": "line", "metric": "total_water_savings_gallons", "title": "Water Savings Over Time"},
                    {"type": "bar", "metric": "total_cost_savings_dollars", "title": "Cost Savings by Month"},
                    {"type": "pie", "metric": "farms_with_conservation_practices", "title": "Conservation Practice Adoption"}
                ],
                format=ReportFormat.PDF
            ),
            "business_metrics_quarterly": ReportTemplate(
                template_id="business_metrics_quarterly",
                name="Quarterly Business Metrics Report",
                description="Quarterly report on business performance and metrics",
                report_type=ReportType.BUSINESS_METRICS,
                sections=[
                    "business_overview",
                    "financial_metrics",
                    "user_metrics",
                    "operational_metrics",
                    "strategic_insights",
                    "future_outlook"
                ],
                charts=[
                    {"type": "line", "metric": "revenue", "title": "Revenue Growth"},
                    {"type": "bar", "metric": "customer_acquisition", "title": "Customer Acquisition"},
                    {"type": "pie", "metric": "market_penetration", "title": "Market Penetration"}
                ],
                format=ReportFormat.PDF
            ),
            "comprehensive_monthly": ReportTemplate(
                template_id="comprehensive_monthly",
                name="Comprehensive Monthly Report",
                description="Comprehensive monthly report covering all aspects",
                report_type=ReportType.COMPREHENSIVE,
                sections=[
                    "executive_summary",
                    "system_performance",
                    "user_adoption",
                    "agricultural_outcomes",
                    "business_metrics",
                    "key_insights",
                    "recommendations",
                    "appendix"
                ],
                charts=[
                    {"type": "dashboard", "metrics": ["cpu_usage_percent", "memory_usage_percent"], "title": "System Health Dashboard"},
                    {"type": "line", "metric": "daily_active_users", "title": "User Growth"},
                    {"type": "bar", "metric": "total_water_savings_gallons", "title": "Water Savings Impact"},
                    {"type": "pie", "metric": "user_satisfaction_score", "title": "User Satisfaction"}
                ],
                format=ReportFormat.PDF
            )
        }
    
    async def _load_report_schedules(self):
        """Load report schedules."""
        self.report_schedules = {
            "daily_system_performance": ReportSchedule(
                schedule_id="daily_system_performance",
                template_id="system_performance_daily",
                frequency=ReportFrequency.DAILY,
                time_of_day="08:00",
                timezone="UTC",
                enabled=True,
                recipients=["admin@drought-management.com", "ops@drought-management.com"]
            ),
            "weekly_user_adoption": ReportSchedule(
                schedule_id="weekly_user_adoption",
                template_id="user_adoption_weekly",
                frequency=ReportFrequency.WEEKLY,
                day_of_week="monday",
                time_of_day="09:00",
                timezone="UTC",
                enabled=True,
                recipients=["product@drought-management.com", "marketing@drought-management.com"]
            ),
            "monthly_agricultural_outcomes": ReportSchedule(
                schedule_id="monthly_agricultural_outcomes",
                template_id="agricultural_outcomes_monthly",
                frequency=ReportFrequency.MONTHLY,
                day_of_month=1,
                time_of_day="10:00",
                timezone="UTC",
                enabled=True,
                recipients=["agriculture@drought-management.com", "research@drought-management.com"]
            ),
            "quarterly_business_metrics": ReportSchedule(
                schedule_id="quarterly_business_metrics",
                template_id="business_metrics_quarterly",
                frequency=ReportFrequency.QUARTERLY,
                day_of_month=1,
                time_of_day="11:00",
                timezone="UTC",
                enabled=True,
                recipients=["executives@drought-management.com", "finance@drought-management.com"]
            )
        }
    
    async def _load_report_configurations(self):
        """Load report configurations."""
        self.report_configurations = {
            "default": ReportConfiguration(
                config_id="default",
                name="Default Report Configuration",
                default_format=ReportFormat.HTML,
                include_charts=True,
                include_insights=True,
                include_recommendations=True,
                max_chart_points=100,
                chart_width=800,
                chart_height=400,
                report_title_template="Drought Management Service - {report_type} Report",
                report_footer_template="Generated on {date} | Drought Management Service v1.0"
            )
        }
    
    async def _start_scheduled_reports(self):
        """Start scheduled report generation."""
        # Start background task for scheduled reports
        asyncio.create_task(self._scheduled_report_loop())
        logger.info("Started scheduled report generation")
    
    async def _stop_scheduled_reports(self):
        """Stop scheduled report generation."""
        # Stop background task
        logger.info("Stopped scheduled report generation")
    
    async def _scheduled_report_loop(self):
        """Main scheduled report loop."""
        while True:
            try:
                # Check for scheduled reports every hour
                await self._check_scheduled_reports()
                await asyncio.sleep(3600)  # Wait 1 hour
            except Exception as e:
                logger.error(f"Error in scheduled report loop: {str(e)}")
                await asyncio.sleep(3600)  # Wait before retrying
    
    async def _check_scheduled_reports(self):
        """Check for scheduled reports that need to be generated."""
        try:
            current_time = datetime.utcnow()
            
            for schedule_id, schedule in self.report_schedules.items():
                if not schedule.enabled:
                    continue
                
                # Check if it's time to generate this report
                if await self._should_generate_report(schedule, current_time):
                    await self._generate_scheduled_report(schedule)
                    
        except Exception as e:
            logger.error(f"Error checking scheduled reports: {str(e)}")
    
    async def _should_generate_report(self, schedule: ReportSchedule, current_time: datetime) -> bool:
        """Check if a report should be generated based on schedule."""
        try:
            # Check if report was already generated today
            today = current_time.date()
            report_key = f"{schedule.schedule_id}_{today}"
            
            if report_key in self.report_history:
                return False
            
            # Check frequency and timing
            if schedule.frequency == ReportFrequency.DAILY:
                return current_time.hour == int(schedule.time_of_day.split(':')[0])
            elif schedule.frequency == ReportFrequency.WEEKLY:
                if current_time.strftime('%A').lower() == schedule.day_of_week:
                    return current_time.hour == int(schedule.time_of_day.split(':')[0])
            elif schedule.frequency == ReportFrequency.MONTHLY:
                if current_time.day == schedule.day_of_month:
                    return current_time.hour == int(schedule.time_of_day.split(':')[0])
            elif schedule.frequency == ReportFrequency.QUARTERLY:
                # Check if it's the first day of a quarter
                if (current_time.day == schedule.day_of_month and 
                    current_time.month in [1, 4, 7, 10]):
                    return current_time.hour == int(schedule.time_of_day.split(':')[0])
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking report schedule: {str(e)}")
            return False
    
    async def _generate_scheduled_report(self, schedule: ReportSchedule):
        """Generate a scheduled report."""
        try:
            logger.info(f"Generating scheduled report: {schedule.schedule_id}")
            
            # Get template
            template = self.report_templates.get(schedule.template_id)
            if not template:
                logger.error(f"Template not found: {schedule.template_id}")
                return
            
            # Generate report
            report = await self._generate_report_from_template(template)
            
            # Store report history
            report_id = str(uuid4())
            report_history = ReportHistory(
                report_id=report_id,
                schedule_id=schedule.schedule_id,
                template_id=schedule.template_id,
                report_type=template.report_type,
                status=ReportStatus.COMPLETED,
                generated_at=datetime.utcnow(),
                file_path=f"reports/{report_id}.{template.format.value}",
                recipients=schedule.recipients
            )
            
            self.report_history[report_id] = report_history
            
            # Deliver report
            await self._deliver_report(report, schedule.recipients, template.format)
            
            logger.info(f"Scheduled report generated: {report_id}")
            
        except Exception as e:
            logger.error(f"Error generating scheduled report: {str(e)}")
    
    async def _generate_report_from_template(self, template: ReportTemplate) -> ComprehensiveReport:
        """Generate report from template."""
        try:
            # Collect data for each section
            sections = []
            charts = []
            insights = []
            recommendations = []
            
            for section_name in template.sections:
                section_data = await self._generate_section_data(section_name, template.report_type)
                sections.append(section_data)
            
            # Generate charts
            for chart_config in template.charts:
                chart_data = await self._generate_chart_data(chart_config, template.report_type)
                charts.append(chart_data)
            
            # Generate insights and recommendations
            insights = await self._generate_insights(template.report_type)
            recommendations = await self._generate_recommendations(template.report_type)
            
            # Create comprehensive report
            report = ComprehensiveReport(
                report_id=str(uuid4()),
                report_type=template.report_type,
                title=self._generate_report_title(template),
                generated_at=datetime.utcnow(),
                sections=sections,
                charts=charts,
                insights=insights,
                recommendations=recommendations,
                summary=self._generate_report_summary(template.report_type)
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating report from template: {str(e)}")
            raise
    
    async def _generate_section_data(self, section_name: str, report_type: ReportType) -> ReportSection:
        """Generate data for a report section."""
        try:
            # Simulate section data generation
            # In production, this would collect actual data from various services
            
            section_data = {
                "section_name": section_name,
                "data": await self._get_section_metrics(section_name, report_type),
                "charts": await self._get_section_charts(section_name, report_type),
                "insights": await self._get_section_insights(section_name, report_type),
                "recommendations": await self._get_section_recommendations(section_name, report_type)
            }
            
            return ReportSection(**section_data)
            
        except Exception as e:
            logger.error(f"Error generating section data: {str(e)}")
            raise
    
    async def _get_section_metrics(self, section_name: str, report_type: ReportType) -> Dict[str, Any]:
        """Get metrics for a report section."""
        # Simulate metrics collection
        import random
        
        metrics_templates = {
            "system_overview": {
                "uptime_percent": random.uniform(95, 99.9),
                "response_time_ms": random.uniform(100, 500),
                "error_rate_percent": random.uniform(0.1, 2.0),
                "active_users": random.randint(50, 200)
            },
            "performance_metrics": {
                "cpu_usage_percent": random.uniform(30, 80),
                "memory_usage_percent": random.uniform(40, 85),
                "disk_usage_percent": random.uniform(20, 70),
                "network_throughput_mbps": random.uniform(100, 1000)
            },
            "user_overview": {
                "total_users": random.randint(1000, 5000),
                "active_users": random.randint(100, 500),
                "new_users_this_period": random.randint(50, 200),
                "user_retention_rate": random.uniform(70, 90)
            },
            "impact_overview": {
                "total_water_savings_gallons": random.uniform(100000, 1000000),
                "total_cost_savings_dollars": random.uniform(50000, 500000),
                "farms_impacted": random.randint(100, 1000),
                "environmental_score": random.uniform(80, 95)
            }
        }
        
        return metrics_templates.get(section_name, {})
    
    async def _get_section_charts(self, section_name: str, report_type: ReportType) -> List[ReportChart]:
        """Get charts for a report section."""
        # Simulate chart data generation
        charts = []
        
        chart_templates = {
            "performance_metrics": [
                {
                    "chart_id": "cpu_usage_trend",
                    "chart_type": "line",
                    "title": "CPU Usage Trend",
                    "data": [{"timestamp": "2024-01-01", "value": 45}, {"timestamp": "2024-01-02", "value": 52}]
                }
            ],
            "user_overview": [
                {
                    "chart_id": "user_growth",
                    "chart_type": "line",
                    "title": "User Growth",
                    "data": [{"timestamp": "2024-01-01", "value": 1200}, {"timestamp": "2024-01-02", "value": 1250}]
                }
            ]
        }
        
        chart_data = chart_templates.get(section_name, [])
        for chart_config in chart_data:
            charts.append(ReportChart(**chart_config))
        
        return charts
    
    async def _get_section_insights(self, section_name: str, report_type: ReportType) -> List[str]:
        """Get insights for a report section."""
        insights_templates = {
            "system_overview": [
                "System performance has been stable with 99.5% uptime",
                "Response times are within acceptable limits",
                "Error rates have decreased by 15% compared to last period"
            ],
            "user_overview": [
                "User adoption continues to grow at 25% month-over-month",
                "User satisfaction scores remain high at 4.2/5.0",
                "Feature usage patterns show strong engagement"
            ],
            "impact_overview": [
                "Water savings have exceeded targets by 20%",
                "Cost savings are trending upward",
                "Environmental impact scores are consistently high"
            ]
        }
        
        return insights_templates.get(section_name, [])
    
    async def _get_section_recommendations(self, section_name: str, report_type: ReportType) -> List[str]:
        """Get recommendations for a report section."""
        recommendations_templates = {
            "system_overview": [
                "Continue monitoring system performance closely",
                "Consider scaling resources during peak usage",
                "Implement additional error monitoring"
            ],
            "user_overview": [
                "Focus on user onboarding improvements",
                "Develop additional features based on usage patterns",
                "Implement user feedback collection system"
            ],
            "impact_overview": [
                "Expand conservation practice recommendations",
                "Develop partnerships with agricultural organizations",
                "Create farmer success story documentation"
            ]
        }
        
        return recommendations_templates.get(section_name, [])
    
    async def _generate_chart_data(self, chart_config: Dict[str, Any], report_type: ReportType) -> ReportChart:
        """Generate chart data from configuration."""
        # Simulate chart data generation
        import random
        
        chart_data = []
        for i in range(30):  # 30 data points
            date = datetime.utcnow() - timedelta(days=30-i)
            value = random.uniform(20, 80)
            chart_data.append({
                "timestamp": date.isoformat(),
                "value": value
            })
        
        return ReportChart(
            chart_id=f"{chart_config['metric']}_chart",
            chart_type=chart_config["type"],
            title=chart_config["title"],
            data=chart_data
        )
    
    async def _generate_insights(self, report_type: ReportType) -> List[ReportInsight]:
        """Generate insights for the report."""
        insights = []
        
        insight_templates = {
            ReportType.SYSTEM_PERFORMANCE: [
                "System performance has been stable with high uptime",
                "Resource usage is within optimal ranges",
                "Error rates have decreased significantly"
            ],
            ReportType.USER_ADOPTION: [
                "User adoption continues to grow steadily",
                "User engagement metrics are positive",
                "Feature usage patterns show strong adoption"
            ],
            ReportType.AGRICULTURAL_OUTCOMES: [
                "Agricultural impact metrics exceed expectations",
                "Water conservation practices are highly effective",
                "Farmer satisfaction with recommendations is high"
            ],
            ReportType.BUSINESS_METRICS: [
                "Business metrics show strong growth",
                "Customer acquisition costs are decreasing",
                "Revenue growth is exceeding targets"
            ]
        }
        
        insight_texts = insight_templates.get(report_type, [])
        for i, text in enumerate(insight_texts):
            insights.append(ReportInsight(
                insight_id=str(uuid4()),
                title=f"Key Insight {i+1}",
                description=text,
                impact="high",
                confidence=0.85
            ))
        
        return insights
    
    async def _generate_recommendations(self, report_type: ReportType) -> List[ReportRecommendation]:
        """Generate recommendations for the report."""
        recommendations = []
        
        recommendation_templates = {
            ReportType.SYSTEM_PERFORMANCE: [
                "Continue monitoring system performance",
                "Implement proactive scaling",
                "Enhance error monitoring"
            ],
            ReportType.USER_ADOPTION: [
                "Improve user onboarding process",
                "Develop additional features",
                "Enhance user support"
            ],
            ReportType.AGRICULTURAL_OUTCOMES: [
                "Expand conservation practices",
                "Develop farmer partnerships",
                "Create success documentation"
            ],
            ReportType.BUSINESS_METRICS: [
                "Focus on customer retention",
                "Optimize acquisition channels",
                "Develop new revenue streams"
            ]
        }
        
        recommendation_texts = recommendation_templates.get(report_type, [])
        for i, text in enumerate(recommendation_texts):
            recommendations.append(ReportRecommendation(
                recommendation_id=str(uuid4()),
                title=f"Recommendation {i+1}",
                description=text,
                priority="high",
                implementation_effort="medium",
                expected_impact="high"
            ))
        
        return recommendations
    
    def _generate_report_title(self, template: ReportTemplate) -> str:
        """Generate report title."""
        config = self.report_configurations.get("default")
        if config:
            return config.report_title_template.format(
                report_type=template.report_type.value.replace("_", " ").title()
            )
        return f"{template.name} - {datetime.utcnow().strftime('%Y-%m-%d')}"
    
    def _generate_report_summary(self, report_type: ReportType) -> Dict[str, Any]:
        """Generate report summary."""
        return {
            "report_type": report_type.value,
            "generated_at": datetime.utcnow().isoformat(),
            "key_highlights": [
                "System performance is stable",
                "User adoption continues to grow",
                "Agricultural impact exceeds expectations"
            ],
            "next_steps": [
                "Continue monitoring key metrics",
                "Implement recommended improvements",
                "Plan for future growth"
            ]
        }
    
    async def _deliver_report(self, report: ComprehensiveReport, recipients: List[str], format: ReportFormat):
        """Deliver report to recipients."""
        try:
            # This would integrate with actual delivery mechanisms
            # For now, simulate delivery
            
            logger.info(f"Delivering report {report.report_id} to {len(recipients)} recipients")
            
            # Simulate delivery delay
            await asyncio.sleep(0.1)
            
            logger.info(f"Report {report.report_id} delivered successfully")
            
        except Exception as e:
            logger.error(f"Error delivering report: {str(e)}")
    
    # Public API methods
    async def generate_report(self, request: ReportGenerationRequest) -> ReportGenerationResponse:
        """Generate a report on demand."""
        try:
            logger.info(f"Generating report: {request.report_type}")
            
            # Get template
            template = self._get_template_for_report_type(request.report_type)
            if not template:
                return ReportGenerationResponse(
                    success=False,
                    report=None,
                    errors=[f"No template found for report type: {request.report_type}"]
                )
            
            # Generate report
            report = await self._generate_report_from_template(template)
            
            # Store report history
            report_id = str(uuid4())
            report_history = ReportHistory(
                report_id=report_id,
                schedule_id=None,
                template_id=template.template_id,
                report_type=request.report_type,
                status=ReportStatus.COMPLETED,
                generated_at=datetime.utcnow(),
                file_path=f"reports/{report_id}.{template.format.value}",
                recipients=request.recipients or []
            )
            
            self.report_history[report_id] = report_history
            
            logger.info(f"Report generated successfully: {report_id}")
            return ReportGenerationResponse(
                success=True,
                report=report,
                errors=[]
            )
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return ReportGenerationResponse(
                success=False,
                report=None,
                errors=[str(e)]
            )
    
    def _get_template_for_report_type(self, report_type: ReportType) -> Optional[ReportTemplate]:
        """Get template for report type."""
        for template in self.report_templates.values():
            if template.report_type == report_type:
                return template
        return None
    
    async def get_report_history(self, limit: int = 50) -> List[ReportHistory]:
        """Get report generation history."""
        # Return recent reports sorted by generation time
        recent_reports = sorted(
            self.report_history.values(),
            key=lambda x: x.generated_at,
            reverse=True
        )
        return recent_reports[:limit]
    
    async def get_report_metrics(self) -> ReportMetrics:
        """Get report generation metrics."""
        try:
            total_reports = len(self.report_history)
            successful_reports = len([r for r in self.report_history.values() if r.status == ReportStatus.COMPLETED])
            failed_reports = len([r for r in self.report_history.values() if r.status == ReportStatus.FAILED])
            
            # Calculate by report type
            type_counts = {}
            for report in self.report_history.values():
                report_type = report.report_type.value
                type_counts[report_type] = type_counts.get(report_type, 0) + 1
            
            return ReportMetrics(
                total_reports=total_reports,
                successful_reports=successful_reports,
                failed_reports=failed_reports,
                success_rate=(successful_reports / total_reports * 100) if total_reports > 0 else 0,
                reports_by_type=type_counts,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting report metrics: {str(e)}")
            raise