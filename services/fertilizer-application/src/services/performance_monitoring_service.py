"""
Performance Monitoring Service for real-time equipment performance tracking.

This service provides real-time monitoring, performance tracking, and alerting
capabilities for equipment efficiency and optimization.
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

from ..models.equipment_models import (
    Equipment, EquipmentCategory, EquipmentStatus, MaintenanceLevel,
    EquipmentPerformance, EquipmentMaintenance
)

logger = logging.getLogger(__name__)


class PerformanceMetric(str, Enum):
    """Performance metrics for monitoring."""
    APPLICATION_ACCURACY = "application_accuracy"
    COVERAGE_UNIFORMITY = "coverage_uniformity"
    SPEED_EFFICIENCY = "speed_efficiency"
    FUEL_EFFICIENCY = "fuel_efficiency"
    LABOR_EFFICIENCY = "labor_efficiency"
    MAINTENANCE_EFFICIENCY = "maintenance_efficiency"
    OVERALL_EFFICIENCY = "overall_efficiency"
    DOWNTIME_HOURS = "downtime_hours"
    MAINTENANCE_COST = "maintenance_cost"


class AlertLevel(str, Enum):
    """Alert levels for performance monitoring."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PerformanceStatus(str, Enum):
    """Performance status levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class PerformanceAlert:
    """Performance alert data structure."""
    alert_id: str
    equipment_id: str
    metric: PerformanceMetric
    alert_level: AlertLevel
    current_value: float
    threshold_value: float
    message: str
    timestamp: str
    recommendations: List[str]
    acknowledged: bool = False


@dataclass
class PerformanceSnapshot:
    """Performance snapshot data structure."""
    snapshot_id: str
    equipment_id: str
    timestamp: str
    metrics: Dict[str, float]
    status: PerformanceStatus
    alerts: List[PerformanceAlert]
    efficiency_trend: Dict[str, float]
    maintenance_status: str


@dataclass
class PerformanceTrend:
    """Performance trend analysis."""
    equipment_id: str
    metric: PerformanceMetric
    time_period: str
    data_points: List[Dict[str, Any]]
    trend_direction: str  # "improving", "declining", "stable"
    trend_strength: float  # 0-1
    confidence: float  # 0-1
    forecast: List[Dict[str, Any]]


@dataclass
class MonitoringConfiguration:
    """Configuration for performance monitoring."""
    equipment_id: str
    monitoring_enabled: bool
    alert_thresholds: Dict[str, Dict[str, float]]
    monitoring_frequency_minutes: int
    data_retention_days: int
    alert_notifications: List[str]


class PerformanceMonitoringService:
    """Service for real-time performance monitoring and tracking."""
    
    def __init__(self):
        self.monitoring_configs: Dict[str, MonitoringConfiguration] = {}
        self.performance_data: Dict[str, List[PerformanceSnapshot]] = {}
        self.active_alerts: Dict[str, List[PerformanceAlert]] = {}
        self.performance_thresholds = self._initialize_performance_thresholds()
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
    
    def _initialize_performance_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize performance thresholds for different alert levels."""
        return {
            PerformanceMetric.APPLICATION_ACCURACY: {
                AlertLevel.CRITICAL: 0.6,
                AlertLevel.WARNING: 0.75,
                AlertLevel.INFO: 0.85
            },
            PerformanceMetric.COVERAGE_UNIFORMITY: {
                AlertLevel.CRITICAL: 0.6,
                AlertLevel.WARNING: 0.75,
                AlertLevel.INFO: 0.85
            },
            PerformanceMetric.SPEED_EFFICIENCY: {
                AlertLevel.CRITICAL: 0.5,
                AlertLevel.WARNING: 0.65,
                AlertLevel.INFO: 0.8
            },
            PerformanceMetric.FUEL_EFFICIENCY: {
                AlertLevel.CRITICAL: 0.5,
                AlertLevel.WARNING: 0.65,
                AlertLevel.INFO: 0.8
            },
            PerformanceMetric.LABOR_EFFICIENCY: {
                AlertLevel.CRITICAL: 0.5,
                AlertLevel.WARNING: 0.65,
                AlertLevel.INFO: 0.8
            },
            PerformanceMetric.MAINTENANCE_EFFICIENCY: {
                AlertLevel.CRITICAL: 0.5,
                AlertLevel.WARNING: 0.65,
                AlertLevel.INFO: 0.8
            },
            PerformanceMetric.OVERALL_EFFICIENCY: {
                AlertLevel.CRITICAL: 0.6,
                AlertLevel.WARNING: 0.75,
                AlertLevel.INFO: 0.85
            },
            PerformanceMetric.DOWNTIME_HOURS: {
                AlertLevel.CRITICAL: 24,
                AlertLevel.WARNING: 12,
                AlertLevel.INFO: 4
            },
            PerformanceMetric.MAINTENANCE_COST: {
                AlertLevel.CRITICAL: 2000,
                AlertLevel.WARNING: 1000,
                AlertLevel.INFO: 500
            }
        }
    
    async def start_monitoring(
        self, 
        equipment_id: str, 
        config: MonitoringConfiguration
    ) -> bool:
        """
        Start performance monitoring for equipment.
        
        Args:
            equipment_id: Equipment identifier
            config: Monitoring configuration
            
        Returns:
            True if monitoring started successfully
        """
        try:
            logger.info(f"Starting performance monitoring for equipment {equipment_id}")
            
            # Store configuration
            self.monitoring_configs[equipment_id] = config
            
            # Initialize data storage
            self.performance_data[equipment_id] = []
            self.active_alerts[equipment_id] = []
            
            # Start monitoring task
            if config.monitoring_enabled:
                monitoring_task = asyncio.create_task(
                    self._monitoring_loop(equipment_id, config)
                )
                self.monitoring_tasks[equipment_id] = monitoring_task
                
                logger.info(f"Performance monitoring started for equipment {equipment_id}")
                return True
            else:
                logger.info(f"Monitoring disabled for equipment {equipment_id}")
                return True  # Still return True since configuration was stored successfully
                
        except Exception as e:
            logger.error(f"Error starting monitoring for equipment {equipment_id}: {e}")
            return False
    
    async def stop_monitoring(self, equipment_id: str) -> bool:
        """
        Stop performance monitoring for equipment.
        
        Args:
            equipment_id: Equipment identifier
            
        Returns:
            True if monitoring stopped successfully
        """
        try:
            logger.info(f"Stopping performance monitoring for equipment {equipment_id}")
            
            # Cancel monitoring task
            if equipment_id in self.monitoring_tasks:
                self.monitoring_tasks[equipment_id].cancel()
                del self.monitoring_tasks[equipment_id]
            
            # Clear configuration
            if equipment_id in self.monitoring_configs:
                del self.monitoring_configs[equipment_id]
            
            logger.info(f"Performance monitoring stopped for equipment {equipment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping monitoring for equipment {equipment_id}: {e}")
            return False
    
    async def _monitoring_loop(self, equipment_id: str, config: MonitoringConfiguration):
        """Main monitoring loop for equipment."""
        while True:
            try:
                # Collect performance data
                snapshot = await self._collect_performance_snapshot(equipment_id)
                
                # Store snapshot
                self.performance_data[equipment_id].append(snapshot)
                
                # Check for alerts
                alerts = await self._check_performance_alerts(equipment_id, snapshot)
                
                # Process alerts
                await self._process_alerts(equipment_id, alerts)
                
                # Clean up old data
                await self._cleanup_old_data(equipment_id, config.data_retention_days)
                
                # Wait for next monitoring cycle
                await asyncio.sleep(config.monitoring_frequency_minutes * 60)
                
            except asyncio.CancelledError:
                logger.info(f"Monitoring loop cancelled for equipment {equipment_id}")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop for equipment {equipment_id}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def _collect_performance_snapshot(self, equipment_id: str) -> PerformanceSnapshot:
        """Collect current performance snapshot for equipment."""
        snapshot_id = str(uuid4())
        timestamp = datetime.now().isoformat()
        
        # In real implementation, this would collect actual performance data
        # For now, we'll simulate performance data collection
        metrics = await self._simulate_performance_data(equipment_id)
        
        # Determine overall status
        status = self._determine_performance_status(metrics)
        
        # Calculate efficiency trend
        efficiency_trend = await self._calculate_efficiency_trend(equipment_id, metrics)
        
        # Determine maintenance status
        maintenance_status = await self._determine_maintenance_status(equipment_id, metrics)
        
        # Get current alerts
        alerts = self.active_alerts.get(equipment_id, [])
        
        snapshot = PerformanceSnapshot(
            snapshot_id=snapshot_id,
            equipment_id=equipment_id,
            timestamp=timestamp,
            metrics=metrics,
            status=status,
            alerts=alerts,
            efficiency_trend=efficiency_trend,
            maintenance_status=maintenance_status
        )
        
        return snapshot
    
    async def _simulate_performance_data(self, equipment_id: str) -> Dict[str, float]:
        """Simulate performance data collection (placeholder for real implementation)."""
        # In real implementation, this would collect actual sensor data
        import random
        
        base_metrics = {
            PerformanceMetric.APPLICATION_ACCURACY: random.uniform(0.7, 0.95),
            PerformanceMetric.COVERAGE_UNIFORMITY: random.uniform(0.7, 0.9),
            PerformanceMetric.SPEED_EFFICIENCY: random.uniform(0.6, 0.85),
            PerformanceMetric.FUEL_EFFICIENCY: random.uniform(0.6, 0.8),
            PerformanceMetric.LABOR_EFFICIENCY: random.uniform(0.7, 0.9),
            PerformanceMetric.MAINTENANCE_EFFICIENCY: random.uniform(0.6, 0.85),
            PerformanceMetric.DOWNTIME_HOURS: random.uniform(0, 8),
            PerformanceMetric.MAINTENANCE_COST: random.uniform(100, 1000)
        }
        
        # Calculate overall efficiency
        efficiency_metrics = [
            base_metrics[PerformanceMetric.APPLICATION_ACCURACY],
            base_metrics[PerformanceMetric.COVERAGE_UNIFORMITY],
            base_metrics[PerformanceMetric.SPEED_EFFICIENCY],
            base_metrics[PerformanceMetric.FUEL_EFFICIENCY],
            base_metrics[PerformanceMetric.LABOR_EFFICIENCY],
            base_metrics[PerformanceMetric.MAINTENANCE_EFFICIENCY]
        ]
        
        base_metrics[PerformanceMetric.OVERALL_EFFICIENCY] = sum(efficiency_metrics) / len(efficiency_metrics)
        
        return base_metrics
    
    def _determine_performance_status(self, metrics: Dict[str, float]) -> PerformanceStatus:
        """Determine overall performance status based on metrics."""
        overall_efficiency = metrics.get(PerformanceMetric.OVERALL_EFFICIENCY, 0)
        
        if overall_efficiency >= 0.9:
            return PerformanceStatus.EXCELLENT
        elif overall_efficiency >= 0.8:
            return PerformanceStatus.GOOD
        elif overall_efficiency >= 0.7:
            return PerformanceStatus.ACCEPTABLE
        elif overall_efficiency >= 0.6:
            return PerformanceStatus.POOR
        else:
            return PerformanceStatus.CRITICAL
    
    async def _calculate_efficiency_trend(self, equipment_id: str, current_metrics: Dict[str, float]) -> Dict[str, float]:
        """Calculate efficiency trend based on historical data."""
        historical_data = self.performance_data.get(equipment_id, [])
        
        if len(historical_data) < 2:
            return {metric: 0.0 for metric in current_metrics.keys()}
        
        # Calculate trend for each metric
        trends = {}
        for metric in current_metrics.keys():
            if metric in [PerformanceMetric.DOWNTIME_HOURS, PerformanceMetric.MAINTENANCE_COST]:
                # For these metrics, lower is better
                trend = self._calculate_declining_trend(historical_data, metric)
            else:
                # For efficiency metrics, higher is better
                trend = self._calculate_improving_trend(historical_data, metric)
            
            trends[metric] = trend
        
        return trends
    
    def _calculate_improving_trend(self, historical_data: List[PerformanceSnapshot], metric: str) -> float:
        """Calculate improving trend (higher values are better)."""
        if len(historical_data) < 2:
            return 0.0
        
        recent_values = [snapshot.metrics.get(metric, 0) for snapshot in historical_data[-5:]]
        
        if len(recent_values) < 2:
            return 0.0
        
        # Calculate simple linear trend
        x_values = list(range(len(recent_values)))
        y_values = recent_values
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Normalize slope to 0-1 range
        return max(-1.0, min(1.0, slope * 10))
    
    def _calculate_declining_trend(self, historical_data: List[PerformanceSnapshot], metric: str) -> float:
        """Calculate declining trend (lower values are better)."""
        if len(historical_data) < 2:
            return 0.0
        
        recent_values = [snapshot.metrics.get(metric, 0) for snapshot in historical_data[-5:]]
        
        if len(recent_values) < 2:
            return 0.0
        
        # Calculate simple linear trend
        x_values = list(range(len(recent_values)))
        y_values = recent_values
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # For declining trend, negative slope is good
        # Normalize slope to 0-1 range (inverted)
        return max(-1.0, min(1.0, -slope * 10))
    
    async def _determine_maintenance_status(self, equipment_id: str, metrics: Dict[str, float]) -> str:
        """Determine maintenance status based on metrics."""
        maintenance_efficiency = metrics.get(PerformanceMetric.MAINTENANCE_EFFICIENCY, 0.7)
        downtime_hours = metrics.get(PerformanceMetric.DOWNTIME_HOURS, 0)
        maintenance_cost = metrics.get(PerformanceMetric.MAINTENANCE_COST, 0)
        
        if maintenance_efficiency < 0.5 or downtime_hours > 24 or maintenance_cost > 2000:
            return "urgent_maintenance_required"
        elif maintenance_efficiency < 0.7 or downtime_hours > 12 or maintenance_cost > 1000:
            return "maintenance_recommended"
        elif maintenance_efficiency < 0.8 or downtime_hours > 4 or maintenance_cost > 500:
            return "maintenance_scheduled"
        else:
            return "maintenance_current"
    
    async def _check_performance_alerts(self, equipment_id: str, snapshot: PerformanceSnapshot) -> List[PerformanceAlert]:
        """Check for performance alerts based on current metrics."""
        alerts = []
        config = self.monitoring_configs.get(equipment_id)
        
        if not config:
            return alerts
        
        for metric, value in snapshot.metrics.items():
            if metric not in self.performance_thresholds:
                continue
            
            thresholds = self.performance_thresholds[metric]
            
            # Check each alert level
            for alert_level, threshold in thresholds.items():
                if self._should_trigger_alert(metric, value, threshold, alert_level):
                    alert = PerformanceAlert(
                        alert_id=str(uuid4()),
                        equipment_id=equipment_id,
                        metric=PerformanceMetric(metric),
                        alert_level=AlertLevel(alert_level),
                        current_value=value,
                        threshold_value=threshold,
                        message=self._generate_alert_message(metric, value, threshold, alert_level),
                        timestamp=snapshot.timestamp,
                        recommendations=self._generate_alert_recommendations(metric, alert_level)
                    )
                    alerts.append(alert)
        
        return alerts
    
    def _should_trigger_alert(self, metric: str, value: float, threshold: float, alert_level: str) -> bool:
        """Determine if an alert should be triggered."""
        if metric in [PerformanceMetric.DOWNTIME_HOURS, PerformanceMetric.MAINTENANCE_COST]:
            # For these metrics, higher values trigger alerts
            return value >= threshold
        else:
            # For efficiency metrics, lower values trigger alerts
            return value <= threshold
    
    def _generate_alert_message(self, metric: str, value: float, threshold: float, alert_level: str) -> str:
        """Generate alert message."""
        metric_name = metric.replace("_", " ").title()
        
        if metric in [PerformanceMetric.DOWNTIME_HOURS, PerformanceMetric.MAINTENANCE_COST]:
            return f"{alert_level.upper()}: {metric_name} is {value:.2f}, exceeding threshold of {threshold:.2f}"
        else:
            return f"{alert_level.upper()}: {metric_name} is {value:.2f}, below threshold of {threshold:.2f}"
    
    def _generate_alert_recommendations(self, metric: str, alert_level: str) -> List[str]:
        """Generate recommendations for alerts."""
        recommendations = {
            PerformanceMetric.APPLICATION_ACCURACY: [
                "Calibrate application equipment",
                "Check and replace worn nozzles or spreader components",
                "Verify application rates and patterns"
            ],
            PerformanceMetric.COVERAGE_UNIFORMITY: [
                "Adjust boom height or spreader settings",
                "Check for clogged nozzles or uneven distribution",
                "Consider field-specific calibration"
            ],
            PerformanceMetric.SPEED_EFFICIENCY: [
                "Optimize field routes to minimize turning time",
                "Adjust ground speed for optimal application",
                "Consider equipment upgrades for faster operation"
            ],
            PerformanceMetric.FUEL_EFFICIENCY: [
                "Perform engine tune-up and maintenance",
                "Optimize field routes to reduce fuel consumption",
                "Consider fuel-efficient equipment upgrades"
            ],
            PerformanceMetric.LABOR_EFFICIENCY: [
                "Improve operator training",
                "Optimize field routes",
                "Implement automation where possible"
            ],
            PerformanceMetric.MAINTENANCE_EFFICIENCY: [
                "Schedule regular maintenance",
                "Monitor efficiency metrics",
                "Implement predictive maintenance"
            ],
            PerformanceMetric.OVERALL_EFFICIENCY: [
                "Review all efficiency metrics",
                "Implement comprehensive optimization plan",
                "Consider equipment replacement"
            ],
            PerformanceMetric.DOWNTIME_HOURS: [
                "Schedule preventive maintenance",
                "Implement predictive maintenance",
                "Improve maintenance procedures"
            ],
            PerformanceMetric.MAINTENANCE_COST: [
                "Review maintenance procedures",
                "Consider maintenance contracts",
                "Implement cost-effective maintenance strategies"
            ]
        }
        
        return recommendations.get(metric, ["Review equipment performance"])
    
    async def _process_alerts(self, equipment_id: str, alerts: List[PerformanceAlert]):
        """Process and store alerts."""
        if not alerts:
            return
        
        # Add new alerts to active alerts
        if equipment_id not in self.active_alerts:
            self.active_alerts[equipment_id] = []
        
        self.active_alerts[equipment_id].extend(alerts)
        
        # Send notifications (placeholder for real implementation)
        for alert in alerts:
            await self._send_alert_notification(alert)
        
        logger.info(f"Processed {len(alerts)} alerts for equipment {equipment_id}")
    
    async def _send_alert_notification(self, alert: PerformanceAlert):
        """Send alert notification (placeholder for real implementation)."""
        # In real implementation, this would send actual notifications
        logger.warning(f"ALERT: {alert.message}")
    
    async def _cleanup_old_data(self, equipment_id: str, retention_days: int):
        """Clean up old performance data."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        if equipment_id in self.performance_data:
            # Remove old snapshots
            self.performance_data[equipment_id] = [
                snapshot for snapshot in self.performance_data[equipment_id]
                if datetime.fromisoformat(snapshot.timestamp) > cutoff_date
            ]
        
        if equipment_id in self.active_alerts:
            # Remove old alerts
            self.active_alerts[equipment_id] = [
                alert for alert in self.active_alerts[equipment_id]
                if datetime.fromisoformat(alert.timestamp) > cutoff_date
            ]
    
    async def get_current_performance(self, equipment_id: str) -> Optional[PerformanceSnapshot]:
        """Get current performance snapshot for equipment."""
        if equipment_id not in self.performance_data or not self.performance_data[equipment_id]:
            return None
        
        return self.performance_data[equipment_id][-1]
    
    async def get_performance_history(
        self, 
        equipment_id: str, 
        hours: int = 24
    ) -> List[PerformanceSnapshot]:
        """Get performance history for equipment."""
        if equipment_id not in self.performance_data:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            snapshot for snapshot in self.performance_data[equipment_id]
            if datetime.fromisoformat(snapshot.timestamp) > cutoff_time
        ]
    
    async def get_active_alerts(self, equipment_id: str) -> List[PerformanceAlert]:
        """Get active alerts for equipment."""
        return self.active_alerts.get(equipment_id, [])
    
    async def acknowledge_alert(self, equipment_id: str, alert_id: str) -> bool:
        """Acknowledge an alert."""
        if equipment_id not in self.active_alerts:
            return False
        
        for alert in self.active_alerts[equipment_id]:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                return True
        
        return False
    
    async def get_performance_trend(
        self, 
        equipment_id: str, 
        metric: PerformanceMetric,
        days: int = 7
    ) -> Optional[PerformanceTrend]:
        """Get performance trend analysis for a specific metric."""
        if equipment_id not in self.performance_data:
            return None
        
        cutoff_time = datetime.now() - timedelta(days=days)
        historical_data = [
            snapshot for snapshot in self.performance_data[equipment_id]
            if datetime.fromisoformat(snapshot.timestamp) > cutoff_time
        ]
        
        if len(historical_data) < 2:
            return None
        
        # Extract data points
        data_points = []
        for snapshot in historical_data:
            data_points.append({
                "timestamp": snapshot.timestamp,
                "value": snapshot.metrics.get(metric.value, 0),
                "status": snapshot.status.value
            })
        
        # Calculate trend
        trend_direction, trend_strength = self._analyze_trend(data_points)
        
        # Generate forecast
        forecast = self._generate_forecast(data_points, days=3)
        
        return PerformanceTrend(
            equipment_id=equipment_id,
            metric=metric,
            time_period=f"{days}_days",
            data_points=data_points,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            confidence=0.8,  # Placeholder confidence
            forecast=forecast
        )
    
    def _analyze_trend(self, data_points: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Analyze trend from data points."""
        if len(data_points) < 2:
            return "stable", 0.0
        
        values = [point["value"] for point in data_points]
        
        # Simple linear regression
        x_values = list(range(len(values)))
        y_values = values
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return "stable", 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        
        # Determine trend direction
        if slope > 0.01:
            trend_direction = "improving"
        elif slope < -0.01:
            trend_direction = "declining"
        else:
            trend_direction = "stable"
        
        # Calculate trend strength
        trend_strength = min(1.0, abs(slope) * 10)
        
        return trend_direction, trend_strength
    
    def _generate_forecast(self, data_points: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """Generate forecast based on historical data."""
        if len(data_points) < 2:
            return []
        
        values = [point["value"] for point in data_points]
        
        # Simple linear forecast
        x_values = list(range(len(values)))
        y_values = values
        
        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            slope = 0
            intercept = sum_y / n
        else:
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            intercept = (sum_y - slope * sum_x) / n
        
        # Generate forecast
        forecast = []
        last_timestamp = datetime.fromisoformat(data_points[-1]["timestamp"])
        
        for i in range(1, days + 1):
            forecast_timestamp = last_timestamp + timedelta(days=i)
            forecast_value = intercept + slope * (len(values) + i)
            
            forecast.append({
                "timestamp": forecast_timestamp.isoformat(),
                "value": max(0, min(1, forecast_value)),  # Clamp between 0 and 1
                "confidence": max(0, 1 - i * 0.1)  # Decreasing confidence over time
            })
        
        return forecast
    
    async def get_monitoring_status(self, equipment_id: str) -> Dict[str, Any]:
        """Get monitoring status for equipment."""
        config = self.monitoring_configs.get(equipment_id)
        is_monitoring = equipment_id in self.monitoring_tasks
        
        return {
            "equipment_id": equipment_id,
            "monitoring_enabled": is_monitoring,
            "configuration": config.__dict__ if config else None,
            "data_points": len(self.performance_data.get(equipment_id, [])),
            "active_alerts": len(self.active_alerts.get(equipment_id, [])),
            "last_update": self.performance_data[equipment_id][-1].timestamp if self.performance_data.get(equipment_id) else None
        }