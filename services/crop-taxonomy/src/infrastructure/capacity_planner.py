"""
Capacity Planning and Performance Forecasting System

This module implements capacity planning, traffic analysis, resource planning,
cost optimization, and performance forecasting for scalable operations.

TICKET-005_crop-variety-recommendations-14.2: Add comprehensive scalability improvements and infrastructure
"""

import asyncio
import logging
import time
import json
import math
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from uuid import UUID, uuid4
from dataclasses import dataclass, field
from enum import Enum
import aioredis
from aioredis import Redis
import numpy as np
from scipy import stats
import pandas as pd

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources to plan for."""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATABASE_CONNECTIONS = "database_connections"
    REDIS_CONNECTIONS = "redis_connections"


class ScalingTrigger(Enum):
    """Triggers for scaling decisions."""
    CPU_THRESHOLD = "cpu_threshold"
    MEMORY_THRESHOLD = "memory_threshold"
    RESPONSE_TIME_THRESHOLD = "response_time_threshold"
    QUEUE_LENGTH_THRESHOLD = "queue_length_threshold"
    ERROR_RATE_THRESHOLD = "error_rate_threshold"
    TRAFFIC_SPIKE = "traffic_spike"


@dataclass
class ResourceMetrics:
    """Resource utilization metrics."""
    resource_type: ResourceType
    current_usage: float
    max_capacity: float
    utilization_percent: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trend: str = "stable"  # "increasing", "decreasing", "stable"
    predicted_usage_1h: float = 0.0
    predicted_usage_24h: float = 0.0


@dataclass
class TrafficPattern:
    """Traffic pattern analysis."""
    pattern_type: str  # "daily", "weekly", "seasonal", "spike"
    peak_hours: List[int]
    peak_days: List[int]
    average_requests_per_minute: float
    peak_requests_per_minute: float
    growth_rate_percent: float
    seasonality_factor: float = 1.0


@dataclass
class CapacityRecommendation:
    """Capacity planning recommendation."""
    resource_type: ResourceType
    current_capacity: float
    recommended_capacity: float
    scaling_factor: float
    confidence: float
    reasoning: str
    cost_impact: float
    performance_impact: float
    urgency: str  # "low", "medium", "high", "critical"
    timeline: str  # "immediate", "1_week", "1_month", "3_months"


@dataclass
class CostAnalysis:
    """Cost analysis for capacity planning."""
    current_monthly_cost: float
    projected_monthly_cost: float
    cost_change_percent: float
    cost_per_request: float
    cost_per_user: float
    roi_break_even_months: float
    cost_optimization_opportunities: List[str]


class TrafficAnalyzer:
    """Analyzes traffic patterns and predicts future demand."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.traffic_data: List[Dict[str, Any]] = []
        
    async def analyze_traffic_patterns(self, days: int = 30) -> TrafficPattern:
        """Analyze traffic patterns from historical data."""
        try:
            # Get traffic data from Redis
            traffic_data = await self._get_traffic_data(days)
            
            if not traffic_data:
                return self._get_default_pattern()
                
            # Analyze patterns
            hourly_pattern = self._analyze_hourly_pattern(traffic_data)
            daily_pattern = self._analyze_daily_pattern(traffic_data)
            growth_trend = self._analyze_growth_trend(traffic_data)
            seasonality = self._analyze_seasonality(traffic_data)
            
            return TrafficPattern(
                pattern_type="daily",
                peak_hours=hourly_pattern["peak_hours"],
                peak_days=daily_pattern["peak_days"],
                average_requests_per_minute=hourly_pattern["avg_rpm"],
                peak_requests_per_minute=hourly_pattern["peak_rpm"],
                growth_rate_percent=growth_trend["growth_rate"],
                seasonality_factor=seasonality["factor"]
            )
            
        except Exception as e:
            logger.error(f"Traffic analysis error: {e}")
            return self._get_default_pattern()
            
    async def _get_traffic_data(self, days: int) -> List[Dict[str, Any]]:
        """Get traffic data from Redis."""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            # Get request timestamps
            timestamps = await self.redis.zrangebyscore(
                "request_timestamps",
                cutoff_time.timestamp(),
                "+inf"
            )
            
            # Convert to traffic data
            traffic_data = []
            for timestamp in timestamps:
                dt = datetime.fromtimestamp(float(timestamp))
                traffic_data.append({
                    "timestamp": dt,
                    "hour": dt.hour,
                    "day_of_week": dt.weekday(),
                    "requests": 1
                })
                
            return traffic_data
            
        except Exception as e:
            logger.error(f"Failed to get traffic data: {e}")
            return []
            
    def _analyze_hourly_pattern(self, traffic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze hourly traffic patterns."""
        hourly_counts = {}
        
        for data in traffic_data:
            hour = data["hour"]
            hourly_counts[hour] = hourly_counts.get(hour, 0) + data["requests"]
            
        # Find peak hours (top 25%)
        sorted_hours = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)
        peak_hours = [hour for hour, count in sorted_hours[:6]]  # Top 6 hours
        
        avg_rpm = sum(hourly_counts.values()) / (len(traffic_data) / 60) if traffic_data else 0
        peak_rpm = max(hourly_counts.values()) if hourly_counts else 0
        
        return {
            "peak_hours": peak_hours,
            "avg_rpm": avg_rpm,
            "peak_rpm": peak_rpm
        }
        
    def _analyze_daily_pattern(self, traffic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze daily traffic patterns."""
        daily_counts = {}
        
        for data in traffic_data:
            day = data["day_of_week"]
            daily_counts[day] = daily_counts.get(day, 0) + data["requests"]
            
        # Find peak days (top 50%)
        sorted_days = sorted(daily_counts.items(), key=lambda x: x[1], reverse=True)
        peak_days = [day for day, count in sorted_days[:4]]  # Top 4 days
        
        return {
            "peak_days": peak_days
        }
        
    def _analyze_growth_trend(self, traffic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze growth trend."""
        if len(traffic_data) < 7:
            return {"growth_rate": 0.0}
            
        # Group by day and count requests
        daily_counts = {}
        for data in traffic_data:
            day = data["timestamp"].date()
            daily_counts[day] = daily_counts.get(day, 0) + data["requests"]
            
        # Calculate growth rate
        days = sorted(daily_counts.keys())
        if len(days) < 2:
            return {"growth_rate": 0.0}
            
        first_week_avg = sum(daily_counts[d] for d in days[:7]) / min(7, len(days))
        last_week_avg = sum(daily_counts[d] for d in days[-7:]) / min(7, len(days))
        
        if first_week_avg > 0:
            growth_rate = ((last_week_avg - first_week_avg) / first_week_avg) * 100
        else:
            growth_rate = 0.0
            
        return {"growth_rate": growth_rate}
        
    def _analyze_seasonality(self, traffic_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze seasonal patterns."""
        # Simplified seasonality analysis
        # In production, use more sophisticated methods like STL decomposition
        
        monthly_counts = {}
        for data in traffic_data:
            month = data["timestamp"].month
            monthly_counts[month] = monthly_counts.get(month, 0) + data["requests"]
            
        if not monthly_counts:
            return {"factor": 1.0}
            
        avg_monthly = sum(monthly_counts.values()) / len(monthly_counts)
        max_monthly = max(monthly_counts.values())
        
        seasonality_factor = max_monthly / avg_monthly if avg_monthly > 0 else 1.0
        
        return {"factor": seasonality_factor}
        
    def _get_default_pattern(self) -> TrafficPattern:
        """Get default traffic pattern when no data is available."""
        return TrafficPattern(
            pattern_type="daily",
            peak_hours=[9, 10, 11, 14, 15, 16],  # Business hours
            peak_days=[0, 1, 2, 3],  # Monday-Thursday
            average_requests_per_minute=10.0,
            peak_requests_per_minute=50.0,
            growth_rate_percent=5.0,
            seasonality_factor=1.2
        )


class ResourcePlanner:
    """Plans resource requirements based on traffic patterns."""
    
    def __init__(self, redis: Redis):
        self.redis = redis
        self.resource_requirements: Dict[ResourceType, Dict[str, float]] = {
            ResourceType.CPU: {
                "requests_per_core": 1000,  # requests per minute per CPU core
                "base_cores": 2,
                "scaling_factor": 1.5
            },
            ResourceType.MEMORY: {
                "mb_per_request": 10,  # MB per request
                "base_mb": 2048,  # 2GB base
                "scaling_factor": 1.3
            },
            ResourceType.STORAGE: {
                "gb_per_user": 1,  # GB per user
                "base_gb": 100,  # 100GB base
                "scaling_factor": 1.2
            },
            ResourceType.DATABASE_CONNECTIONS: {
                "connections_per_request": 0.1,
                "base_connections": 20,
                "scaling_factor": 1.4
            },
            ResourceType.REDIS_CONNECTIONS: {
                "connections_per_request": 0.05,
                "base_connections": 10,
                "scaling_factor": 1.2
            }
        }
        
    async def calculate_resource_requirements(self, 
                                            traffic_pattern: TrafficPattern,
                                            current_users: int = 1000,
                                            growth_months: int = 6) -> Dict[ResourceType, ResourceMetrics]:
        """Calculate resource requirements based on traffic patterns."""
        try:
            # Project future traffic
            future_traffic = self._project_future_traffic(traffic_pattern, growth_months)
            
            # Calculate requirements for each resource type
            resource_metrics = {}
            
            for resource_type, requirements in self.resource_requirements.items():
                current_usage = await self._get_current_resource_usage(resource_type)
                max_capacity = await self._get_current_resource_capacity(resource_type)
                
                # Calculate required capacity
                required_capacity = self._calculate_required_capacity(
                    resource_type, requirements, future_traffic, current_users
                )
                
                # Predict future usage
                predicted_usage_1h = self._predict_usage_1h(resource_type, traffic_pattern)
                predicted_usage_24h = self._predict_usage_24h(resource_type, traffic_pattern)
                
                # Determine trend
                trend = self._determine_trend(current_usage, predicted_usage_24h)
                
                resource_metrics[resource_type] = ResourceMetrics(
                    resource_type=resource_type,
                    current_usage=current_usage,
                    max_capacity=max_capacity,
                    utilization_percent=(current_usage / max_capacity * 100) if max_capacity > 0 else 0,
                    predicted_usage_1h=predicted_usage_1h,
                    predicted_usage_24h=predicted_usage_24h,
                    trend=trend
                )
                
            return resource_metrics
            
        except Exception as e:
            logger.error(f"Resource planning error: {e}")
            return {}
            
    def _project_future_traffic(self, traffic_pattern: TrafficPattern, months: int) -> Dict[str, float]:
        """Project future traffic based on growth rate."""
        growth_factor = (1 + traffic_pattern.growth_rate_percent / 100) ** (months / 12)
        
        return {
            "avg_rpm": traffic_pattern.average_requests_per_minute * growth_factor,
            "peak_rpm": traffic_pattern.peak_requests_per_minute * growth_factor,
            "seasonality_factor": traffic_pattern.seasonality_factor
        }
        
    def _calculate_required_capacity(self, 
                                   resource_type: ResourceType,
                                   requirements: Dict[str, float],
                                   future_traffic: Dict[str, float],
                                   current_users: int) -> float:
        """Calculate required capacity for a resource type."""
        if resource_type == ResourceType.CPU:
            # CPU: based on peak requests per minute
            peak_rpm = future_traffic["peak_rpm"]
            requests_per_core = requirements["requests_per_core"]
            base_cores = requirements["base_cores"]
            scaling_factor = requirements["scaling_factor"]
            
            required_cores = max(base_cores, peak_rpm / requests_per_core * scaling_factor)
            return required_cores
            
        elif resource_type == ResourceType.MEMORY:
            # Memory: based on average requests and users
            avg_rpm = future_traffic["avg_rpm"]
            mb_per_request = requirements["mb_per_request"]
            base_mb = requirements["base_mb"]
            scaling_factor = requirements["scaling_factor"]
            
            required_mb = base_mb + (avg_rpm * mb_per_request * scaling_factor)
            return required_mb
            
        elif resource_type == ResourceType.STORAGE:
            # Storage: based on user count
            gb_per_user = requirements["gb_per_user"]
            base_gb = requirements["base_gb"]
            scaling_factor = requirements["scaling_factor"]
            
            required_gb = base_gb + (current_users * gb_per_user * scaling_factor)
            return required_gb
            
        elif resource_type == ResourceType.DATABASE_CONNECTIONS:
            # Database connections: based on peak requests
            peak_rpm = future_traffic["peak_rpm"]
            connections_per_request = requirements["connections_per_request"]
            base_connections = requirements["base_connections"]
            scaling_factor = requirements["scaling_factor"]
            
            required_connections = base_connections + (peak_rpm * connections_per_request * scaling_factor)
            return required_connections
            
        elif resource_type == ResourceType.REDIS_CONNECTIONS:
            # Redis connections: based on peak requests
            peak_rpm = future_traffic["peak_rpm"]
            connections_per_request = requirements["connections_per_request"]
            base_connections = requirements["base_connections"]
            scaling_factor = requirements["scaling_factor"]
            
            required_connections = base_connections + (peak_rpm * connections_per_request * scaling_factor)
            return required_connections
            
        return 0.0
        
    async def _get_current_resource_usage(self, resource_type: ResourceType) -> float:
        """Get current resource usage."""
        try:
            if resource_type == ResourceType.CPU:
                # Get CPU usage from system metrics
                import psutil
                return psutil.cpu_percent(interval=1)
                
            elif resource_type == ResourceType.MEMORY:
                # Get memory usage from system metrics
                import psutil
                memory = psutil.virtual_memory()
                return memory.used / (1024 * 1024)  # Convert to MB
                
            elif resource_type == ResourceType.STORAGE:
                # Get storage usage from system metrics
                import psutil
                disk = psutil.disk_usage('/')
                return disk.used / (1024 * 1024 * 1024)  # Convert to GB
                
            elif resource_type == ResourceType.DATABASE_CONNECTIONS:
                # Get database connection count from Redis
                return await self.redis.get("db_connection_count") or 0
                
            elif resource_type == ResourceType.REDIS_CONNECTIONS:
                # Get Redis connection count
                info = await self.redis.info("clients")
                return info.get("connected_clients", 0)
                
        except Exception as e:
            logger.error(f"Failed to get current usage for {resource_type}: {e}")
            
        return 0.0
        
    async def _get_current_resource_capacity(self, resource_type: ResourceType) -> float:
        """Get current resource capacity."""
        try:
            if resource_type == ResourceType.CPU:
                import psutil
                return psutil.cpu_count() * 100  # CPU percentage
                
            elif resource_type == ResourceType.MEMORY:
                import psutil
                memory = psutil.virtual_memory()
                return memory.total / (1024 * 1024)  # Convert to MB
                
            elif resource_type == ResourceType.STORAGE:
                import psutil
                disk = psutil.disk_usage('/')
                return disk.total / (1024 * 1024 * 1024)  # Convert to GB
                
            elif resource_type == ResourceType.DATABASE_CONNECTIONS:
                return 100  # Default max connections
                
            elif resource_type == ResourceType.REDIS_CONNECTIONS:
                return 1000  # Default max connections
                
        except Exception as e:
            logger.error(f"Failed to get capacity for {resource_type}: {e}")
            
        return 100.0
        
    def _predict_usage_1h(self, resource_type: ResourceType, traffic_pattern: TrafficPattern) -> float:
        """Predict resource usage in 1 hour."""
        # Simplified prediction based on current hour
        current_hour = datetime.utcnow().hour
        
        if current_hour in traffic_pattern.peak_hours:
            multiplier = 1.5
        else:
            multiplier = 0.8
            
        base_usage = await self._get_current_resource_usage(resource_type)
        return base_usage * multiplier
        
    def _predict_usage_24h(self, resource_type: ResourceType, traffic_pattern: TrafficPattern) -> float:
        """Predict resource usage in 24 hours."""
        # Average usage over 24 hours with peak adjustments
        base_usage = await self._get_current_resource_usage(resource_type)
        peak_multiplier = traffic_pattern.peak_requests_per_minute / traffic_pattern.average_requests_per_minute
        
        return base_usage * peak_multiplier
        
    def _determine_trend(self, current_usage: float, predicted_usage: float) -> str:
        """Determine usage trend."""
        if predicted_usage > current_usage * 1.1:
            return "increasing"
        elif predicted_usage < current_usage * 0.9:
            return "decreasing"
        else:
            return "stable"


class CapacityPlanner:
    """Main capacity planner coordinating all planning components."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis: Optional[Redis] = None
        self.traffic_analyzer = None
        self.resource_planner = None
        self.cost_analyzer = None
        
    async def initialize(self):
        """Initialize the capacity planner."""
        try:
            # Initialize Redis connection
            self.redis = await aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Redis connection established for capacity planner")
            
            # Initialize components
            self.traffic_analyzer = TrafficAnalyzer(self.redis)
            self.resource_planner = ResourcePlanner(self.redis)
            self.cost_analyzer = CostAnalyzer()
            
            logger.info("Capacity planner initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize capacity planner: {e}")
            raise
            
    async def generate_capacity_plan(self, 
                                   planning_horizon_months: int = 6,
                                   current_users: int = 1000) -> Dict[str, Any]:
        """Generate comprehensive capacity plan."""
        try:
            # Analyze traffic patterns
            traffic_pattern = await self.traffic_analyzer.analyze_traffic_patterns()
            
            # Calculate resource requirements
            resource_metrics = await self.resource_planner.calculate_resource_requirements(
                traffic_pattern, current_users, planning_horizon_months
            )
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(resource_metrics)
            
            # Perform cost analysis
            cost_analysis = await self.cost_analyzer.analyze_costs(
                resource_metrics, recommendations
            )
            
            return {
                "traffic_pattern": {
                    "pattern_type": traffic_pattern.pattern_type,
                    "peak_hours": traffic_pattern.peak_hours,
                    "peak_days": traffic_pattern.peak_days,
                    "avg_rpm": traffic_pattern.average_requests_per_minute,
                    "peak_rpm": traffic_pattern.peak_requests_per_minute,
                    "growth_rate": traffic_pattern.growth_rate_percent
                },
                "resource_metrics": {
                    resource_type.value: {
                        "current_usage": metrics.current_usage,
                        "max_capacity": metrics.max_capacity,
                        "utilization_percent": metrics.utilization_percent,
                        "predicted_usage_1h": metrics.predicted_usage_1h,
                        "predicted_usage_24h": metrics.predicted_usage_24h,
                        "trend": metrics.trend
                    }
                    for resource_type, metrics in resource_metrics.items()
                },
                "recommendations": [
                    {
                        "resource_type": rec.resource_type.value,
                        "current_capacity": rec.current_capacity,
                        "recommended_capacity": rec.recommended_capacity,
                        "scaling_factor": rec.scaling_factor,
                        "confidence": rec.confidence,
                        "reasoning": rec.reasoning,
                        "urgency": rec.urgency,
                        "timeline": rec.timeline
                    }
                    for rec in recommendations
                ],
                "cost_analysis": {
                    "current_monthly_cost": cost_analysis.current_monthly_cost,
                    "projected_monthly_cost": cost_analysis.projected_monthly_cost,
                    "cost_change_percent": cost_analysis.cost_change_percent,
                    "roi_break_even_months": cost_analysis.roi_break_even_months,
                    "optimization_opportunities": cost_analysis.cost_optimization_opportunities
                },
                "generated_at": datetime.utcnow().isoformat(),
                "planning_horizon_months": planning_horizon_months
            }
            
        except Exception as e:
            logger.error(f"Capacity planning error: {e}")
            raise
            
    async def _generate_recommendations(self, resource_metrics: Dict[ResourceType, ResourceMetrics]) -> List[CapacityRecommendation]:
        """Generate capacity recommendations."""
        recommendations = []
        
        for resource_type, metrics in resource_metrics.items():
            # Determine if scaling is needed
            if metrics.utilization_percent > 80:
                urgency = "critical"
                timeline = "immediate"
            elif metrics.utilization_percent > 70:
                urgency = "high"
                timeline = "1_week"
            elif metrics.utilization_percent > 60:
                urgency = "medium"
                timeline = "1_month"
            else:
                urgency = "low"
                timeline = "3_months"
                
            # Calculate recommended capacity
            if metrics.predicted_usage_24h > metrics.max_capacity * 0.8:
                scaling_factor = 1.5
                recommended_capacity = metrics.max_capacity * scaling_factor
            else:
                scaling_factor = 1.0
                recommended_capacity = metrics.max_capacity
                
            # Generate reasoning
            reasoning = self._generate_reasoning(resource_type, metrics, scaling_factor)
            
            # Calculate confidence
            confidence = self._calculate_confidence(metrics)
            
            # Estimate cost and performance impact
            cost_impact = self._estimate_cost_impact(resource_type, scaling_factor)
            performance_impact = self._estimate_performance_impact(scaling_factor)
            
            recommendation = CapacityRecommendation(
                resource_type=resource_type,
                current_capacity=metrics.max_capacity,
                recommended_capacity=recommended_capacity,
                scaling_factor=scaling_factor,
                confidence=confidence,
                reasoning=reasoning,
                cost_impact=cost_impact,
                performance_impact=performance_impact,
                urgency=urgency,
                timeline=timeline
            )
            
            recommendations.append(recommendation)
            
        return recommendations
        
    def _generate_reasoning(self, resource_type: ResourceType, metrics: ResourceMetrics, scaling_factor: float) -> str:
        """Generate reasoning for recommendation."""
        if scaling_factor > 1.0:
            return f"Current {resource_type.value} utilization is {metrics.utilization_percent:.1f}% with predicted usage of {metrics.predicted_usage_24h:.1f}. Scaling by {scaling_factor:.1f}x recommended to handle peak load."
        else:
            return f"Current {resource_type.value} utilization is {metrics.utilization_percent:.1f}% which is within acceptable limits. No immediate scaling required."
            
    def _calculate_confidence(self, metrics: ResourceMetrics) -> float:
        """Calculate confidence in recommendation."""
        # Higher confidence for resources with clear trends
        if metrics.trend == "increasing":
            return 0.9
        elif metrics.trend == "stable":
            return 0.7
        else:
            return 0.5
            
    def _estimate_cost_impact(self, resource_type: ResourceType, scaling_factor: float) -> float:
        """Estimate cost impact of scaling."""
        # Simplified cost model
        cost_per_unit = {
            ResourceType.CPU: 50.0,  # $50 per CPU core per month
            ResourceType.MEMORY: 0.1,  # $0.10 per GB per month
            ResourceType.STORAGE: 0.05,  # $0.05 per GB per month
            ResourceType.DATABASE_CONNECTIONS: 1.0,  # $1 per connection per month
            ResourceType.REDIS_CONNECTIONS: 0.5  # $0.50 per connection per month
        }
        
        return cost_per_unit.get(resource_type, 10.0) * (scaling_factor - 1.0)
        
    def _estimate_performance_impact(self, scaling_factor: float) -> float:
        """Estimate performance impact of scaling."""
        # Positive impact for scaling up
        return (scaling_factor - 1.0) * 0.5


class CostAnalyzer:
    """Analyzes costs and optimization opportunities."""
    
    def __init__(self):
        self.cost_models = {
            ResourceType.CPU: {"base_cost": 100.0, "cost_per_unit": 50.0},
            ResourceType.MEMORY: {"base_cost": 50.0, "cost_per_unit": 0.1},
            ResourceType.STORAGE: {"base_cost": 20.0, "cost_per_unit": 0.05},
            ResourceType.DATABASE_CONNECTIONS: {"base_cost": 30.0, "cost_per_unit": 1.0},
            ResourceType.REDIS_CONNECTIONS: {"base_cost": 15.0, "cost_per_unit": 0.5}
        }
        
    async def analyze_costs(self, 
                          resource_metrics: Dict[ResourceType, ResourceMetrics],
                          recommendations: List[CapacityRecommendation]) -> CostAnalysis:
        """Analyze costs and optimization opportunities."""
        try:
            # Calculate current costs
            current_cost = self._calculate_current_cost(resource_metrics)
            
            # Calculate projected costs
            projected_cost = self._calculate_projected_cost(recommendations)
            
            # Calculate cost change
            cost_change_percent = ((projected_cost - current_cost) / current_cost * 100) if current_cost > 0 else 0
            
            # Calculate cost per request/user
            cost_per_request = current_cost / 100000  # Assume 100k requests per month
            cost_per_user = current_cost / 1000  # Assume 1000 users
            
            # Calculate ROI break-even
            roi_break_even = self._calculate_roi_break_even(current_cost, projected_cost)
            
            # Identify optimization opportunities
            opportunities = self._identify_optimization_opportunities(resource_metrics, recommendations)
            
            return CostAnalysis(
                current_monthly_cost=current_cost,
                projected_monthly_cost=projected_cost,
                cost_change_percent=cost_change_percent,
                cost_per_request=cost_per_request,
                cost_per_user=cost_per_user,
                roi_break_even_months=roi_break_even,
                cost_optimization_opportunities=opportunities
            )
            
        except Exception as e:
            logger.error(f"Cost analysis error: {e}")
            return CostAnalysis(
                current_monthly_cost=0.0,
                projected_monthly_cost=0.0,
                cost_change_percent=0.0,
                cost_per_request=0.0,
                cost_per_user=0.0,
                roi_break_even_months=0.0,
                cost_optimization_opportunities=[]
            )
            
    def _calculate_current_cost(self, resource_metrics: Dict[ResourceType, ResourceMetrics]) -> float:
        """Calculate current monthly cost."""
        total_cost = 0.0
        
        for resource_type, metrics in resource_metrics.items():
            cost_model = self.cost_models.get(resource_type, {"base_cost": 0.0, "cost_per_unit": 0.0})
            cost = cost_model["base_cost"] + (metrics.max_capacity * cost_model["cost_per_unit"])
            total_cost += cost
            
        return total_cost
        
    def _calculate_projected_cost(self, recommendations: List[CapacityRecommendation]) -> float:
        """Calculate projected monthly cost."""
        total_cost = 0.0
        
        for rec in recommendations:
            cost_model = self.cost_models.get(rec.resource_type, {"base_cost": 0.0, "cost_per_unit": 0.0})
            cost = cost_model["base_cost"] + (rec.recommended_capacity * cost_model["cost_per_unit"])
            total_cost += cost
            
        return total_cost
        
    def _calculate_roi_break_even(self, current_cost: float, projected_cost: float) -> float:
        """Calculate ROI break-even in months."""
        if projected_cost <= current_cost:
            return 0.0
            
        # Simplified ROI calculation
        # Assume 20% performance improvement leads to 10% revenue increase
        revenue_increase = 0.1
        monthly_revenue = 10000  # Assume $10k monthly revenue
        
        additional_revenue = monthly_revenue * revenue_increase
        additional_cost = projected_cost - current_cost
        
        if additional_revenue > 0:
            return additional_cost / additional_revenue
        else:
            return float('inf')
            
    def _identify_optimization_opportunities(self, 
                                          resource_metrics: Dict[ResourceType, ResourceMetrics],
                                          recommendations: List[CapacityRecommendation]) -> List[str]:
        """Identify cost optimization opportunities."""
        opportunities = []
        
        for resource_type, metrics in resource_metrics.items():
            if metrics.utilization_percent < 30:
                opportunities.append(f"Consider downsizing {resource_type.value} - utilization only {metrics.utilization_percent:.1f}%")
                
            if metrics.trend == "decreasing":
                opportunities.append(f"Monitor {resource_type.value} trend - usage decreasing")
                
        # Check for over-provisioning
        for rec in recommendations:
            if rec.scaling_factor < 1.0:
                opportunities.append(f"Consider reducing {rec.resource_type.value} capacity")
                
        return opportunities


# Global capacity planner instance
capacity_planner = CapacityPlanner()


async def get_capacity_planner() -> CapacityPlanner:
    """Get the global capacity planner instance."""
    if not capacity_planner.redis:
        await capacity_planner.initialize()
    return capacity_planner