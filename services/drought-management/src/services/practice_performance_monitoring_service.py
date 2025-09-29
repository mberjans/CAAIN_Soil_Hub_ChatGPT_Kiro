"""
Practice Performance Monitoring Service

Service for continuous monitoring of conservation practice performance,
automated data collection, and real-time effectiveness tracking.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
import asyncio
import statistics
from enum import Enum

from ..models.practice_effectiveness_models import (
    PracticeImplementation,
    PerformanceMeasurement,
    EffectivenessValidation,
    PerformanceMetric,
    EffectivenessStatus
)

logger = logging.getLogger(__name__)

class MonitoringFrequency(str, Enum):
    """Monitoring frequency options."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class AlertLevel(str, Enum):
    """Alert levels for monitoring."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class PerformanceAlert(BaseModel):
    """Model for performance alerts."""
    alert_id: UUID = Field(default_factory=uuid4, description="Unique alert identifier")
    implementation_id: UUID = Field(..., description="Reference to practice implementation")
    alert_type: str = Field(..., description="Type of alert")
    alert_level: AlertLevel = Field(..., description="Alert severity level")
    message: str = Field(..., description="Alert message")
    metric_type: Optional[PerformanceMetric] = Field(None, description="Related metric type")
    threshold_value: Optional[Decimal] = Field(None, description="Threshold value that triggered alert")
    actual_value: Optional[Decimal] = Field(None, description="Actual value that triggered alert")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = Field(default=False, description="Whether alert has been acknowledged")
    acknowledged_at: Optional[datetime] = Field(None, description="When alert was acknowledged")

class MonitoringConfiguration(BaseModel):
    """Configuration for practice monitoring."""
    config_id: UUID = Field(default_factory=uuid4, description="Unique configuration identifier")
    implementation_id: UUID = Field(..., description="Reference to practice implementation")
    monitoring_frequency: MonitoringFrequency = Field(..., description="How often to monitor")
    metrics_to_monitor: List[PerformanceMetric] = Field(..., description="Metrics to monitor")
    alert_thresholds: Dict[str, Dict[str, Decimal]] = Field(default_factory=dict, description="Alert thresholds")
    data_sources: List[str] = Field(default_factory=list, description="Data sources for monitoring")
    enabled: bool = Field(default=True, description="Whether monitoring is enabled")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PerformanceTrend(BaseModel):
    """Model for performance trends."""
    trend_id: UUID = Field(default_factory=uuid4, description="Unique trend identifier")
    implementation_id: UUID = Field(..., description="Reference to practice implementation")
    metric_type: PerformanceMetric = Field(..., description="Metric type")
    trend_period_start: date = Field(..., description="Trend period start")
    trend_period_end: date = Field(..., description="Trend period end")
    trend_direction: str = Field(..., description="Trend direction (increasing, decreasing, stable)")
    trend_strength: float = Field(..., ge=0, le=1, description="Trend strength (0-1)")
    data_points: int = Field(..., description="Number of data points used")
    confidence_level: float = Field(..., ge=0, le=1, description="Confidence in trend analysis")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PracticePerformanceMonitoringService:
    """Service for continuous monitoring of conservation practice performance."""
    
    def __init__(self):
        self.database = None
        self.sensor_manager = None
        self.alert_system = None
        self.data_collectors = {}
        self.monitoring_tasks = {}
        self.initialized = False
    
    async def initialize(self):
        """Initialize the performance monitoring service."""
        try:
            logger.info("Initializing Practice Performance Monitoring Service...")
            
            # Initialize database connection
            self.database = await self._initialize_database()
            
            # Initialize sensor manager
            self.sensor_manager = await self._initialize_sensor_manager()
            
            # Initialize alert system
            self.alert_system = await self._initialize_alert_system()
            
            # Initialize data collectors
            self.data_collectors = await self._initialize_data_collectors()
            
            self.initialized = True
            logger.info("Practice Performance Monitoring Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Practice Performance Monitoring Service: {str(e)}")
            raise
    
    async def cleanup(self):
        """Clean up service resources."""
        try:
            logger.info("Cleaning up Practice Performance Monitoring Service...")
            
            # Stop all monitoring tasks
            for task in self.monitoring_tasks.values():
                if not task.done():
                    task.cancel()
            
            self.initialized = False
            logger.info("Practice Performance Monitoring Service cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
    
    async def setup_monitoring(
        self,
        implementation_id: UUID,
        monitoring_frequency: MonitoringFrequency = MonitoringFrequency.WEEKLY,
        metrics_to_monitor: Optional[List[PerformanceMetric]] = None,
        alert_thresholds: Optional[Dict[str, Dict[str, Decimal]]] = None
    ) -> MonitoringConfiguration:
        """
        Set up monitoring for a practice implementation.
        
        Args:
            implementation_id: ID of the practice implementation
            monitoring_frequency: How often to collect data
            metrics_to_monitor: Which metrics to monitor
            alert_thresholds: Thresholds for generating alerts
            
        Returns:
            MonitoringConfiguration object
        """
        try:
            logger.info(f"Setting up monitoring for implementation: {implementation_id}")
            
            # Default metrics if not specified
            if metrics_to_monitor is None:
                metrics_to_monitor = [
                    PerformanceMetric.WATER_SAVINGS,
                    PerformanceMetric.SOIL_HEALTH,
                    PerformanceMetric.COST_EFFECTIVENESS
                ]
            
            # Default alert thresholds if not specified
            if alert_thresholds is None:
                alert_thresholds = {
                    "water_savings": {"warning": Decimal("10"), "critical": Decimal("5")},
                    "soil_health": {"warning": Decimal("5"), "critical": Decimal("0")},
                    "cost_effectiveness": {"warning": Decimal("3"), "critical": Decimal("1")}
                }
            
            # Create monitoring configuration
            config = MonitoringConfiguration(
                implementation_id=implementation_id,
                monitoring_frequency=monitoring_frequency,
                metrics_to_monitor=metrics_to_monitor,
                alert_thresholds=alert_thresholds,
                data_sources=["sensors", "manual_measurements", "weather_data"]
            )
            
            # Save configuration
            await self._save_monitoring_configuration(config)
            
            # Start monitoring task
            await self._start_monitoring_task(config)
            
            logger.info(f"Monitoring setup completed for implementation: {implementation_id}")
            return config
            
        except Exception as e:
            logger.error(f"Error setting up monitoring: {str(e)}")
            raise
    
    async def collect_performance_data(
        self,
        implementation_id: UUID,
        data_sources: Optional[List[str]] = None
    ) -> List[PerformanceMeasurement]:
        """
        Collect performance data from various sources.
        
        Args:
            implementation_id: ID of the practice implementation
            data_sources: Sources to collect data from
            
        Returns:
            List of PerformanceMeasurement objects
        """
        try:
            logger.info(f"Collecting performance data for implementation: {implementation_id}")
            
            # Get monitoring configuration
            config = await self._get_monitoring_configuration(implementation_id)
            if not config or not config.enabled:
                logger.warning(f"Monitoring not configured or disabled for implementation: {implementation_id}")
                return []
            
            # Use configured data sources if not specified
            if data_sources is None:
                data_sources = config.data_sources
            
            measurements = []
            
            # Collect data from each source
            for source in data_sources:
                source_measurements = await self._collect_from_source(
                    implementation_id, source, config.metrics_to_monitor
                )
                measurements.extend(source_measurements)
            
            # Save measurements
            for measurement in measurements:
                await self._save_performance_measurement(measurement)
            
            # Check for alerts
            await self._check_alerts(implementation_id, measurements, config)
            
            logger.info(f"Collected {len(measurements)} performance measurements")
            return measurements
            
        except Exception as e:
            logger.error(f"Error collecting performance data: {str(e)}")
            raise
    
    async def analyze_performance_trends(
        self,
        implementation_id: UUID,
        metric_type: Optional[PerformanceMetric] = None,
        analysis_period_days: int = 90
    ) -> List[PerformanceTrend]:
        """
        Analyze performance trends for a practice implementation.
        
        Args:
            implementation_id: ID of the practice implementation
            metric_type: Specific metric to analyze (optional)
            analysis_period_days: Period for trend analysis
            
        Returns:
            List of PerformanceTrend objects
        """
        try:
            logger.info(f"Analyzing performance trends for implementation: {implementation_id}")
            
            # Get measurements for analysis period
            end_date = date.today()
            start_date = end_date - timedelta(days=analysis_period_days)
            
            measurements = await self._get_performance_measurements(
                implementation_id, start_date, end_date
            )
            
            # Filter by metric type if specified
            if metric_type:
                measurements = [m for m in measurements if m.metric_type == metric_type]
            
            # Group measurements by metric type
            by_metric = {}
            for measurement in measurements:
                if measurement.metric_type not in by_metric:
                    by_metric[measurement.metric_type] = []
                by_metric[measurement.metric_type].append(measurement)
            
            trends = []
            
            # Analyze trends for each metric type
            for metric_type, metric_measurements in by_metric.items():
                if len(metric_measurements) >= 3:  # Minimum data points for trend analysis
                    trend = await self._calculate_trend(
                        implementation_id, metric_type, metric_measurements,
                        start_date, end_date
                    )
                    trends.append(trend)
            
            # Save trends
            for trend in trends:
                await self._save_performance_trend(trend)
            
            logger.info(f"Analyzed {len(trends)} performance trends")
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {str(e)}")
            raise
    
    async def generate_performance_alerts(
        self,
        implementation_id: UUID,
        alert_levels: Optional[List[AlertLevel]] = None
    ) -> List[PerformanceAlert]:
        """
        Generate performance alerts based on current data.
        
        Args:
            implementation_id: ID of the practice implementation
            alert_levels: Specific alert levels to generate (optional)
            
        Returns:
            List of PerformanceAlert objects
        """
        try:
            logger.info(f"Generating performance alerts for implementation: {implementation_id}")
            
            # Get monitoring configuration
            config = await self._get_monitoring_configuration(implementation_id)
            if not config:
                logger.warning(f"No monitoring configuration found for implementation: {implementation_id}")
                return []
            
            # Get recent measurements
            end_date = date.today()
            start_date = end_date - timedelta(days=7)  # Last week
            
            measurements = await self._get_performance_measurements(
                implementation_id, start_date, end_date
            )
            
            alerts = []
            
            # Check each metric for alerts
            for metric_type in config.metrics_to_monitor:
                metric_measurements = [
                    m for m in measurements if m.metric_type == metric_type
                ]
                
                if metric_measurements:
                    metric_alerts = await self._check_metric_alerts(
                        implementation_id, metric_type, metric_measurements, config
                    )
                    alerts.extend(metric_alerts)
            
            # Filter by alert levels if specified
            if alert_levels:
                alerts = [a for a in alerts if a.alert_level in alert_levels]
            
            # Save alerts
            for alert in alerts:
                await self._save_performance_alert(alert)
            
            logger.info(f"Generated {len(alerts)} performance alerts")
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating performance alerts: {str(e)}")
            raise
    
    async def get_monitoring_dashboard_data(
        self,
        implementation_id: UUID,
        dashboard_period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get data for monitoring dashboard.
        
        Args:
            implementation_id: ID of the practice implementation
            dashboard_period_days: Period for dashboard data
            
        Returns:
            Dashboard data dictionary
        """
        try:
            logger.info(f"Getting dashboard data for implementation: {implementation_id}")
            
            # Get monitoring configuration
            config = await self._get_monitoring_configuration(implementation_id)
            if not config:
                return {"error": "No monitoring configuration found"}
            
            # Get measurements for dashboard period
            end_date = date.today()
            start_date = end_date - timedelta(days=dashboard_period_days)
            
            measurements = await self._get_performance_measurements(
                implementation_id, start_date, end_date
            )
            
            # Get recent alerts
            alerts = await self._get_recent_alerts(implementation_id, days=7)
            
            # Get performance trends
            trends = await self._get_performance_trends(implementation_id, days=dashboard_period_days)
            
            # Generate dashboard data
            dashboard_data = {
                "implementation_id": implementation_id,
                "monitoring_config": {
                    "frequency": config.monitoring_frequency,
                    "metrics": config.metrics_to_monitor,
                    "enabled": config.enabled
                },
                "performance_summary": await self._generate_performance_summary(measurements),
                "recent_alerts": [alert.dict() for alert in alerts],
                "performance_trends": [trend.dict() for trend in trends],
                "data_collection_status": await self._get_data_collection_status(implementation_id),
                "last_updated": datetime.utcnow()
            }
            
            logger.info("Dashboard data generated successfully")
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            raise
    
    async def update_monitoring_configuration(
        self,
        config_id: UUID,
        updates: Dict[str, Any]
    ) -> MonitoringConfiguration:
        """
        Update monitoring configuration.
        
        Args:
            config_id: ID of the monitoring configuration
            updates: Updates to apply
            
        Returns:
            Updated MonitoringConfiguration object
        """
        try:
            logger.info(f"Updating monitoring configuration: {config_id}")
            
            # Get current configuration
            config = await self._get_monitoring_configuration_by_id(config_id)
            if not config:
                raise ValueError(f"Monitoring configuration not found: {config_id}")
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.utcnow()
            
            # Save updated configuration
            await self._save_monitoring_configuration(config)
            
            # Restart monitoring task if needed
            if config.enabled:
                await self._restart_monitoring_task(config)
            
            logger.info(f"Monitoring configuration updated: {config_id}")
            return config
            
        except Exception as e:
            logger.error(f"Error updating monitoring configuration: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _initialize_database(self):
        """Initialize database connection."""
        # In a real implementation, this would connect to the actual database
        return {"connection": "database_connection"}
    
    async def _initialize_sensor_manager(self):
        """Initialize sensor manager for data collection."""
        # In a real implementation, this would initialize sensor connections
        return {"sensors": "sensor_manager"}
    
    async def _initialize_alert_system(self):
        """Initialize alert system."""
        # In a real implementation, this would initialize alert mechanisms
        return {"alerts": "alert_system"}
    
    async def _initialize_data_collectors(self):
        """Initialize data collectors for different sources."""
        collectors = {
            "sensors": await self._create_sensor_collector(),
            "manual_measurements": await self._create_manual_collector(),
            "weather_data": await self._create_weather_collector(),
            "satellite_data": await self._create_satellite_collector()
        }
        return collectors
    
    async def _create_sensor_collector(self):
        """Create sensor data collector."""
        # In a real implementation, this would create sensor collectors
        return {"type": "sensor_collector"}
    
    async def _create_manual_collector(self):
        """Create manual measurement collector."""
        # In a real implementation, this would create manual collectors
        return {"type": "manual_collector"}
    
    async def _create_weather_collector(self):
        """Create weather data collector."""
        # In a real implementation, this would create weather collectors
        return {"type": "weather_collector"}
    
    async def _create_satellite_collector(self):
        """Create satellite data collector."""
        # In a real implementation, this would create satellite collectors
        return {"type": "satellite_collector"}
    
    async def _save_monitoring_configuration(self, config: MonitoringConfiguration):
        """Save monitoring configuration to database."""
        # In a real implementation, this would save to database
        logger.info(f"Saving monitoring configuration: {config.config_id}")
    
    async def _get_monitoring_configuration(self, implementation_id: UUID) -> Optional[MonitoringConfiguration]:
        """Get monitoring configuration for an implementation."""
        # In a real implementation, this would query the database
        return None
    
    async def _get_monitoring_configuration_by_id(self, config_id: UUID) -> Optional[MonitoringConfiguration]:
        """Get monitoring configuration by ID."""
        # In a real implementation, this would query the database
        return None
    
    async def _start_monitoring_task(self, config: MonitoringConfiguration):
        """Start monitoring task for a configuration."""
        task = asyncio.create_task(
            self._monitoring_loop(config)
        )
        self.monitoring_tasks[config.config_id] = task
        logger.info(f"Started monitoring task for config: {config.config_id}")
    
    async def _restart_monitoring_task(self, config: MonitoringConfiguration):
        """Restart monitoring task for a configuration."""
        # Stop existing task
        if config.config_id in self.monitoring_tasks:
            task = self.monitoring_tasks[config.config_id]
            if not task.done():
                task.cancel()
        
        # Start new task
        await self._start_monitoring_task(config)
    
    async def _monitoring_loop(self, config: MonitoringConfiguration):
        """Main monitoring loop for a configuration."""
        try:
            while config.enabled:
                # Collect data
                await self.collect_performance_data(config.implementation_id)
                
                # Wait for next collection based on frequency
                wait_seconds = self._get_frequency_seconds(config.monitoring_frequency)
                await asyncio.sleep(wait_seconds)
                
                # Refresh configuration
                config = await self._get_monitoring_configuration(config.implementation_id)
                if not config:
                    break
                    
        except asyncio.CancelledError:
            logger.info(f"Monitoring task cancelled for config: {config.config_id}")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {str(e)}")
    
    def _get_frequency_seconds(self, frequency: MonitoringFrequency) -> int:
        """Get seconds to wait based on monitoring frequency."""
        frequency_map = {
            MonitoringFrequency.DAILY: 86400,      # 24 hours
            MonitoringFrequency.WEEKLY: 604800,     # 7 days
            MonitoringFrequency.MONTHLY: 2592000,   # 30 days
            MonitoringFrequency.QUARTERLY: 7776000  # 90 days
        }
        return frequency_map.get(frequency, 86400)
    
    async def _collect_from_source(
        self,
        implementation_id: UUID,
        source: str,
        metrics_to_monitor: List[PerformanceMetric]
    ) -> List[PerformanceMeasurement]:
        """Collect data from a specific source."""
        collector = self.data_collectors.get(source)
        if not collector:
            logger.warning(f"No collector found for source: {source}")
            return []
        
        # In a real implementation, this would collect actual data
        measurements = []
        
        # Simulate data collection
        for metric_type in metrics_to_monitor:
            measurement = PerformanceMeasurement(
                implementation_id=implementation_id,
                measurement_date=date.today(),
                metric_type=metric_type,
                metric_value=Decimal("10.5"),  # Simulated value
                metric_unit="percent",
                measurement_method=f"{source}_collection",
                measurement_source=source,
                confidence_level=0.8
            )
            measurements.append(measurement)
        
        return measurements
    
    async def _save_performance_measurement(self, measurement: PerformanceMeasurement):
        """Save performance measurement to database."""
        # In a real implementation, this would save to database
        logger.info(f"Saving performance measurement: {measurement.measurement_id}")
    
    async def _get_performance_measurements(
        self,
        implementation_id: UUID,
        start_date: date,
        end_date: date
    ) -> List[PerformanceMeasurement]:
        """Get performance measurements for a date range."""
        # In a real implementation, this would query the database
        return []
    
    async def _check_alerts(
        self,
        implementation_id: UUID,
        measurements: List[PerformanceMeasurement],
        config: MonitoringConfiguration
    ):
        """Check for alerts based on new measurements."""
        for measurement in measurements:
            if measurement.metric_type in config.alert_thresholds:
                thresholds = config.alert_thresholds[measurement.metric_type]
                
                # Check warning threshold
                if "warning" in thresholds and measurement.metric_value < thresholds["warning"]:
                    alert = PerformanceAlert(
                        implementation_id=implementation_id,
                        alert_type=f"{measurement.metric_type}_warning",
                        alert_level=AlertLevel.WARNING,
                        message=f"{measurement.metric_type} below warning threshold",
                        metric_type=measurement.metric_type,
                        threshold_value=thresholds["warning"],
                        actual_value=measurement.metric_value
                    )
                    await self._save_performance_alert(alert)
                
                # Check critical threshold
                if "critical" in thresholds and measurement.metric_value < thresholds["critical"]:
                    alert = PerformanceAlert(
                        implementation_id=implementation_id,
                        alert_type=f"{measurement.metric_type}_critical",
                        alert_level=AlertLevel.CRITICAL,
                        message=f"{measurement.metric_type} below critical threshold",
                        metric_type=measurement.metric_type,
                        threshold_value=thresholds["critical"],
                        actual_value=measurement.metric_value
                    )
                    await self._save_performance_alert(alert)
    
    async def _save_performance_alert(self, alert: PerformanceAlert):
        """Save performance alert to database."""
        # In a real implementation, this would save to database
        logger.info(f"Saving performance alert: {alert.alert_id}")
    
    async def _calculate_trend(
        self,
        implementation_id: UUID,
        metric_type: PerformanceMetric,
        measurements: List[PerformanceMeasurement],
        start_date: date,
        end_date: date
    ) -> PerformanceTrend:
        """Calculate trend for a metric type."""
        # Sort measurements by date
        measurements.sort(key=lambda m: m.measurement_date)
        
        # Calculate trend direction
        if len(measurements) >= 2:
            first_value = measurements[0].metric_value
            last_value = measurements[-1].metric_value
            
            if last_value > first_value:
                trend_direction = "increasing"
            elif last_value < first_value:
                trend_direction = "decreasing"
            else:
                trend_direction = "stable"
        else:
            trend_direction = "stable"
        
        # Calculate trend strength (simplified)
        trend_strength = 0.5  # In real implementation, would calculate based on data variance
        
        # Calculate confidence level
        confidence_level = min(1.0, len(measurements) / 10.0)  # More data points = higher confidence
        
        return PerformanceTrend(
            implementation_id=implementation_id,
            metric_type=metric_type,
            trend_period_start=start_date,
            trend_period_end=end_date,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            data_points=len(measurements),
            confidence_level=confidence_level
        )
    
    async def _save_performance_trend(self, trend: PerformanceTrend):
        """Save performance trend to database."""
        # In a real implementation, this would save to database
        logger.info(f"Saving performance trend: {trend.trend_id}")
    
    async def _check_metric_alerts(
        self,
        implementation_id: UUID,
        metric_type: PerformanceMetric,
        measurements: List[PerformanceMeasurement],
        config: MonitoringConfiguration
    ) -> List[PerformanceAlert]:
        """Check alerts for a specific metric."""
        alerts = []
        
        if metric_type not in config.alert_thresholds:
            return alerts
        
        thresholds = config.alert_thresholds[metric_type]
        
        # Get latest measurement
        latest_measurement = max(measurements, key=lambda m: m.measurement_date)
        
        # Check thresholds
        for threshold_name, threshold_value in thresholds.items():
            if latest_measurement.metric_value < threshold_value:
                alert_level = AlertLevel.WARNING if threshold_name == "warning" else AlertLevel.CRITICAL
                
                alert = PerformanceAlert(
                    implementation_id=implementation_id,
                    alert_type=f"{metric_type}_{threshold_name}",
                    alert_level=alert_level,
                    message=f"{metric_type} below {threshold_name} threshold",
                    metric_type=metric_type,
                    threshold_value=threshold_value,
                    actual_value=latest_measurement.metric_value
                )
                alerts.append(alert)
        
        return alerts
    
    async def _get_recent_alerts(
        self,
        implementation_id: UUID,
        days: int = 7
    ) -> List[PerformanceAlert]:
        """Get recent alerts for an implementation."""
        # In a real implementation, this would query the database
        return []
    
    async def _get_performance_trends(
        self,
        implementation_id: UUID,
        days: int = 30
    ) -> List[PerformanceTrend]:
        """Get performance trends for an implementation."""
        # In a real implementation, this would query the database
        return []
    
    async def _generate_performance_summary(
        self,
        measurements: List[PerformanceMeasurement]
    ) -> Dict[str, Any]:
        """Generate performance summary from measurements."""
        if not measurements:
            return {"status": "no_data"}
        
        # Group by metric type
        by_metric = {}
        for measurement in measurements:
            if measurement.metric_type not in by_metric:
                by_metric[measurement.metric_type] = []
            by_metric[measurement.metric_type].append(measurement)
        
        summary = {}
        for metric_type, metric_measurements in by_metric.items():
            values = [m.metric_value for m in metric_measurements]
            summary[metric_type] = {
                "latest_value": float(values[-1]),
                "average_value": float(sum(values) / len(values)),
                "measurement_count": len(values),
                "last_measurement_date": metric_measurements[-1].measurement_date
            }
        
        return summary
    
    async def _get_data_collection_status(
        self,
        implementation_id: UUID
    ) -> Dict[str, Any]:
        """Get data collection status for an implementation."""
        # In a real implementation, this would check actual data collection status
        return {
            "sensors_online": True,
            "manual_measurements_pending": 0,
            "weather_data_current": True,
            "last_collection": datetime.utcnow()
        }