"""
Filter Analytics Service

Service for comprehensive filter usage analytics and insights generation.
Tracks filter usage patterns, effectiveness metrics, and generates actionable insights.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import UUID
import hashlib
import json
from collections import defaultdict, Counter

from ..models.filter_analytics_models import (
    FilterUsageRecord, FilterUsageSummary, FilterEffectiveness, FilterTrend,
    FilterAnalyticsRequest, FilterAnalyticsResponse, FilterInsight,
    FilterAnalyticsInsightsResponse, FilterPerformanceMetrics, FilterABTestResult
)

logger = logging.getLogger(__name__)


class FilterAnalyticsService:
    """Service for comprehensive filter analytics and insights."""
    
    def __init__(self):
        self.usage_records = []  # In production, this would be a database
        self.performance_metrics = {}  # In production, this would be a database or cache
        self.insights_cache = {}  # Cache for generated insights
        
    async def record_filter_usage(
        self, 
        user_id: UUID, 
        session_id: str, 
        filter_config: Dict[str, Any], 
        result_count: int, 
        search_duration_ms: float,
        interaction_type: str = "search"
    ) -> bool:
        """
        Record filter usage for analytics.
        
        Args:
            user_id: ID of the user applying the filter
            session_id: Session identifier
            filter_config: The filter configuration applied
            result_count: Number of results returned
            search_duration_ms: Duration of the search in milliseconds
            interaction_type: Type of interaction (search, filter, refine, etc.)
        
        Returns:
            True if successfully recorded, False otherwise
        """
        try:
            record = FilterUsageRecord(
                record_id=hashlib.sha256(f"{user_id}_{session_id}_{datetime.utcnow()}".encode()).hexdigest()[:16],
                user_id=user_id,
                session_id=session_id,
                filter_config=filter_config,
                applied_at=datetime.utcnow(),
                result_count=result_count,
                search_duration_ms=search_duration_ms,
                interaction_type=interaction_type
            )
            
            # In production, this would be stored in a database
            self.usage_records.append(record)
            
            # Update performance metrics
            await self._update_performance_metrics(filter_config, search_duration_ms, result_count)
            
            logger.info(f"Recorded filter usage for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error recording filter usage: {e}")
            return False
    
    async def _update_performance_metrics(
        self, 
        filter_config: Dict[str, Any], 
        execution_time: float, 
        result_count: int
    ) -> None:
        """Update performance metrics for a filter configuration."""
        # Create a hash of the filter config to identify unique configurations
        config_hash = hashlib.sha256(json.dumps(filter_config, sort_keys=True).encode()).hexdigest()
        
        if config_hash not in self.performance_metrics:
            self.performance_metrics[config_hash] = {
                'execution_count': 0,
                'total_execution_time': 0,
                'success_count': 0,
                'total_result_count': 0,
                'cache_hits': 0
            }
        
        metrics = self.performance_metrics[config_hash]
        metrics['execution_count'] += 1
        metrics['total_execution_time'] += execution_time
        if result_count >= 0:  # Assuming negative result_count indicates failure
            metrics['success_count'] += 1
            metrics['total_result_count'] += result_count
    
    async def get_filter_analytics(
        self, 
        request: FilterAnalyticsRequest
    ) -> FilterAnalyticsResponse:
        """
        Get comprehensive filter analytics for the specified period.
        
        Args:
            request: Request containing date range and criteria for analytics
            
        Returns:
            FilterAnalyticsResponse with comprehensive analytics data
        """
        try:
            # Filter records by date range
            filtered_records = [
                record for record in self.usage_records
                if request.start_date <= record.applied_at <= request.end_date
            ]
            
            if request.user_id:
                filtered_records = [
                    record for record in filtered_records
                    if record.user_id == request.user_id
                ]
            
            # Calculate usage summary
            usage_summary = await self._calculate_usage_summary(filtered_records)
            
            # Calculate effectiveness metrics
            effectiveness_metrics = await self._calculate_effectiveness_metrics(filtered_records)
            
            # Identify popular filters
            popular_filters = await self._identify_popular_filters(filtered_records)
            
            # Identify user behavior patterns
            user_behavior_patterns = await self._identify_user_behavior_patterns(filtered_records)
            
            # Calculate trend analysis
            trends = await self._calculate_trends(filtered_records)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(filtered_records)
            
            response = FilterAnalyticsResponse(
                request_id=request.request_id,
                usage_summary=usage_summary,
                effectiveness_metrics=effectiveness_metrics,
                popular_filters=popular_filters,
                user_behavior_patterns=user_behavior_patterns,
                trends=trends,
                recommendations=recommendations,
                metadata={
                    "date_range": {
                        "start": request.start_date.isoformat(),
                        "end": request.end_date.isoformat()
                    },
                    "record_count": len(filtered_records),
                    "filtered_by_user": request.user_id is not None
                }
            )
            
            logger.info(f"Generated filter analytics for request {request.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating filter analytics: {e}")
            raise
    
    async def _calculate_usage_summary(self, records: List[FilterUsageRecord]) -> FilterUsageSummary:
        """Calculate usage summary from filter usage records."""
        if not records:
            return FilterUsageSummary(
                total_applications=0,
                unique_users=0,
                most_popular_filters=[],
                average_result_count=0.0,
                average_search_duration=0.0,
                filter_efficiency_score=0.0,
                peak_usage_times=[]
            )
        
        user_ids = set(record.user_id for record in records)
        total_results = sum(record.result_count for record in records)
        total_duration = sum(record.search_duration_ms for record in records)
        
        # Count filter types and values
        filter_counts = Counter()
        for record in records:
            for key, value in record.filter_config.items():
                if isinstance(value, list):
                    for v in value:
                        filter_counts[(key, str(v))] += 1
                else:
                    filter_counts[(key, str(value))] += 1
        
        most_popular = []
        for (filter_type, filter_value), count in filter_counts.most_common(10):
            most_popular.append({
                "filter_type": filter_type,
                "filter_value": filter_value,
                "usage_count": count
            })
        
        # Calculate peak usage times (by hour)
        hourly_counts = Counter()
        for record in records:
            hour = record.applied_at.hour
            hourly_counts[hour] += 1
        
        peak_times = []
        for hour, count in hourly_counts.most_common(5):
            peak_times.append({
                "hour": hour,
                "usage_count": count
            })
        
        return FilterUsageSummary(
            total_applications=len(records),
            unique_users=len(user_ids),
            most_popular_filters=most_popular,
            average_result_count=total_results / len(records) if records else 0.0,
            average_search_duration=total_duration / len(records) if records else 0.0,
            filter_efficiency_score=min(1.0, len([r for r in records if r.result_count > 0]) / len(records)) if records else 0.0,
            peak_usage_times=peak_times
        )
    
    async def _calculate_effectiveness_metrics(self, records: List[FilterUsageRecord]) -> List[FilterEffectiveness]:
        """Calculate effectiveness metrics for different filter types and values."""
        if not records:
            return []
        
        # Group records by filter type and value
        effectiveness_data = defaultdict(lambda: {
            'count': 0, 
            'success_count': 0, 
            'total_results': 0,
            'total_duration': 0
        })
        
        for record in records:
            for key, value in record.filter_config.items():
                if isinstance(value, list):
                    for v in value:
                        eff_key = f"{key}:{v}"
                        effectiveness_data[eff_key]['count'] += 1
                        if record.result_count > 0:
                            effectiveness_data[eff_key]['success_count'] += 1
                        effectiveness_data[eff_key]['total_results'] += record.result_count
                else:
                    eff_key = f"{key}:{value}"
                    effectiveness_data[eff_key]['count'] += 1
                    if record.result_count > 0:
                        effectiveness_data[eff_key]['success_count'] += 1
                    effectiveness_data[eff_key]['total_results'] += record.result_count
        
        effectiveness_metrics = []
        for filter_key, data in effectiveness_data.items():
            parts = filter_key.split(':', 1)  # Split on first colon only to handle complex values
            if len(parts) < 2:
                continue
                
            filter_type = parts[0]
            filter_value = parts[1]
            
            effectiveness_metrics.append(FilterEffectiveness(
                filter_type=filter_type,
                filter_value=filter_value,
                application_count=data['count'],
                success_count=data['success_count'],
                average_result_count=data['total_results'] / data['count'] if data['count'] > 0 else 0,
                conversion_rate=data['success_count'] / data['count'] if data['count'] > 0 else 0
            ))
        
        return effectiveness_metrics
    
    async def _identify_popular_filters(self, records: List[FilterUsageRecord]) -> List[Dict[str, Any]]:
        """Identify the most popular filters."""
        if not records:
            return []
        
        filter_popularity = Counter()
        for record in records:
            for key, value in record.filter_config.items():
                if isinstance(value, list):
                    for v in value:
                        filter_popularity[(key, str(v))] += 1
                else:
                    filter_popularity[(key, str(value))] += 1
        
        popular_filters = []
        for (filter_type, filter_value), count in filter_popularity.most_common(20):
            popular_filters.append({
                "filter_type": filter_type,
                "filter_value": filter_value,
                "usage_count": count
            })
        
        return popular_filters
    
    async def _identify_user_behavior_patterns(self, records: List[FilterUsageRecord]) -> List[Dict[str, Any]]:
        """Identify user behavior patterns in filter usage."""
        if not records:
            return []
        
        # Group records by user to analyze individual patterns
        user_records = defaultdict(list)
        for record in records:
            user_records[record.user_id].append(record)
        
        # Find common patterns
        patterns = []
        
        # Pattern 1: Common filter combinations
        combination_counter = Counter()
        for user_id, user_records_list in user_records.items():
            for record in user_records_list:
                filter_keys = tuple(sorted(record.filter_config.keys()))
                combination_counter[filter_keys] += 1
        
        common_combinations = []
        for combo, count in combination_counter.most_common(10):
            common_combinations.append({
                "filter_combination": list(combo),
                "usage_count": count,
                "pattern_type": "common_combination"
            })
        
        # Pattern 2: Refinement patterns (same user applying filters multiple times in session)
        refinement_patterns = []
        session_records = defaultdict(list)
        for record in records:
            session_records[record.session_id].append(record)
        
        for session_id, session_data in session_records.items():
            if len(session_data) > 1:
                # Order records by time
                session_data.sort(key=lambda x: x.applied_at)
                
                # Look for progressive refinement (filter A -> filter B -> filter C with decreasing results)
                for i in range(1, len(session_data)):
                    if (session_data[i].result_count < session_data[i-1].result_count and
                        session_data[i].result_count > 0):  # Result count decreased but still positive
                        refinement_patterns.append({
                            "session_id": session_id,
                            "initial_result_count": session_data[i-1].result_count,
                            "refined_result_count": session_data[i].result_count,
                            "pattern_type": "progressive_refinement"
                        })
        
        patterns.extend(common_combinations)
        patterns.extend(refinement_patterns)
        
        return patterns
    
    async def _calculate_trends(self, records: List[FilterUsageRecord]) -> List[FilterTrend]:
        """Calculate trend analysis for filter usage."""
        if not records:
            return []
        
        # Group by date and filter type
        daily_filters = defaultdict(lambda: defaultdict(int))
        daily_results = defaultdict(lambda: defaultdict(float))
        
        for record in records:
            date_key = record.applied_at.date()
            for key, value in record.filter_config.items():
                if isinstance(value, list):
                    for v in value:
                        daily_filters[date_key][(key, str(v))] += 1
                        daily_results[date_key][(key, str(v))] += record.result_count
                else:
                    daily_filters[date_key][(key, str(value))] += 1
                    daily_results[date_key][(key, str(value))] += record.result_count
        
        trends = []
        for date_key, date_filters in daily_filters.items():
            for (filter_type, filter_value), usage_count in date_filters.items():
                avg_result_count = daily_results[date_key][(filter_type, filter_value)] / usage_count
                trends.append(FilterTrend(
                    filter_type=filter_type,
                    filter_value=filter_value,
                    date=datetime.combine(date_key, datetime.min.time()),
                    usage_count=usage_count,
                    average_result_count=avg_result_count
                ))
        
        return trends
    
    async def _generate_recommendations(self, records: List[FilterUsageRecord]) -> List[Dict[str, Any]]:
        """Generate recommendations based on filter usage data."""
        recommendations = []
        
        if not records:
            return recommendations
        
        # Recommendation 1: Popular filters that users might like
        filter_popularity = Counter()
        for record in records:
            for key, value in record.filter_config.items():
                if isinstance(value, list):
                    for v in value:
                        filter_popularity[(key, str(v))] += 1
                else:
                    filter_popularity[(key, str(value))] += 1
        
        top_filters = [f"{k[0]}: {k[1]}" for k, v in filter_popularity.most_common(3)]
        if top_filters:
            recommendations.append({
                "type": "popular_filters",
                "title": "Popular Filter Combinations",
                "description": f"Consider using these popular filter combinations: {', '.join(top_filters)}",
                "action": "apply_popular_filters"
            })
        
        # Recommendation 2: Performance optimization
        slow_filters = []
        for record in records:
            if record.search_duration_ms > 1000:  # More than 1 second
                for key, value in record.filter_config.items():
                    slow_filters.append(f"{key}: {value}")
        
        if slow_filters:
            recommendations.append({
                "type": "performance",
                "title": "Filter Performance Optimization",
                "description": f"These filters are taking longer than average: {', '.join(set(slow_filters[:5]))}",
                "action": "optimize_filters"
            })
        
        # Recommendation 3: Filter effectiveness
        effectiveness = await self._calculate_effectiveness_metrics(records)
        low_effectiveness = [e for e in effectiveness if e.conversion_rate < 0.2]  # Less than 20% success
        
        if low_effectiveness:
            filters = [f"{e.filter_type}: {e.filter_value}" for e in low_effectiveness[:3]]
            recommendations.append({
                "type": "effectiveness",
                "title": "Low Effectiveness Filters",
                "description": f"These filters rarely return results: {', '.join(filters)}. Consider alternatives.",
                "action": "avoid_low_effectiveness_filters"
            })
        
        return recommendations
    
    async def get_filter_insights(
        self, 
        request: FilterAnalyticsRequest
    ) -> FilterAnalyticsInsightsResponse:
        """
        Get comprehensive filter insights with actionable recommendations.
        
        Args:
            request: Request containing date range and criteria for insights
            
        Returns:
            FilterAnalyticsInsightsResponse with insights and visualization-ready data
        """
        try:
            # Get basic analytics
            analytics_response = await self.get_filter_analytics(request)
            
            # Generate insights
            insights = await self._generate_insights(analytics_response)
            
            # Prepare visualization data
            visualization_data = await self._prepare_visualization_data(analytics_response)
            
            response = FilterAnalyticsInsightsResponse(
                request_id=request.request_id,
                insights=insights,
                summary_metrics={
                    "total_applications": analytics_response.usage_summary.total_applications,
                    "unique_users": analytics_response.usage_summary.unique_users,
                    "average_result_count": analytics_response.usage_summary.average_result_count,
                    "filter_efficiency": analytics_response.usage_summary.filter_efficiency_score
                },
                visualization_data=visualization_data
            )
            
            logger.info(f"Generated filter insights for request {request.request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error generating filter insights: {e}")
            raise
    
    async def _generate_insights(self, analytics_response: FilterAnalyticsResponse) -> List[FilterInsight]:
        """Generate insights from analytics data."""
        insights = []
        
        summary = analytics_response.usage_summary
        
        # Insight 1: Usage volume
        if summary.total_applications > 100:
            insights.append(FilterInsight(
                insight_id="high_usage_volume",
                title="High Filter Usage Volume",
                description=f"Users applied filters {summary.total_applications} times, indicating high engagement with the filtering system.",
                impact_level="high",
                category="usage",
                data={"total_applications": summary.total_applications},
                recommendations=[
                    "Consider adding more filter customization options",
                    "Optimize filter performance for better user experience",
                    "Add advanced filter save/share features"
                ]
            ))
        elif summary.total_applications < 10:
            insights.append(FilterInsight(
                insight_id="low_usage_volume",
                title="Low Filter Usage Volume",
                description=f"Users applied filters only {summary.total_applications} times, indicating potential usability issues.",
                impact_level="high",
                category="usage",
                data={"total_applications": summary.total_applications},
                recommendations=[
                    "Evaluate filter interface usability",
                    "Add filter usage tutorials",
                    "Improve filter discoverability"
                ]
            ))
        
        # Insight 2: Filter effectiveness
        if summary.filter_efficiency_score > 0.8:
            insights.append(FilterInsight(
                insight_id="high_effectiveness",
                title="High Filter Effectiveness",
                description=f"Filters are successful {summary.filter_efficiency_score*100:.1f}% of the time, indicating good system performance.",
                impact_level="high",
                category="effectiveness",
                data={"success_rate": summary.filter_efficiency_score},
                recommendations=[
                    "Maintain current filter performance",
                    "Expand to new filter categories"
                ]
            ))
        elif summary.filter_efficiency_score < 0.5:
            insights.append(FilterInsight(
                insight_id="low_effectiveness",
                title="Low Filter Effectiveness",
                description=f"Filters only succeed {summary.filter_efficiency_score*100:.1f}% of the time, indicating potential issues.",
                impact_level="high",
                category="effectiveness",
                data={"success_rate": summary.filter_efficiency_score},
                recommendations=[
                    "Review filter logic and data quality",
                    "Add better filter validation",
                    "Improve error handling and user feedback"
                ]
            ))
        
        # Insight 3: Peak usage times
        if summary.peak_usage_times:
            peak_time = max(summary.peak_usage_times, key=lambda x: x['usage_count'])
            insights.append(FilterInsight(
                insight_id="peak_usage_time",
                title="Peak Filter Usage Time",
                description=f"Peak filter usage occurs at {peak_time['hour']}:00 with {peak_time['usage_count']} applications.",
                impact_level="medium",
                category="usage",
                data={"peak_hour": peak_time['hour'], "usage_count": peak_time['usage_count']},
                recommendations=[
                    f"Ensure system performance during {peak_time['hour']}:00-{peak_time['hour']+1}:00",
                    "Schedule maintenance outside peak hours"
                ]
            ))
        
        # Insight 4: Popular filters
        if analytics_response.popular_filters:
            popular = analytics_response.popular_filters[0]  # Most popular
            insights.append(FilterInsight(
                insight_id="popular_filter",
                title="Most Popular Filter",
                description=f"The most popular filter is '{popular['filter_type']} = {popular['filter_value']}' with {popular['usage_count']} applications.",
                impact_level="medium",
                category="usage",
                data={"popular_filter": popular},
                recommendations=[
                    "Highlight the most popular filters in the interface",
                    "Optimize performance for popular filter combinations"
                ]
            ))
        
        # Insight 5: User behavior patterns
        if analytics_response.user_behavior_patterns:
            pattern_counts = Counter([p['pattern_type'] for p in analytics_response.user_behavior_patterns])
            for pattern_type, count in pattern_counts.most_common(3):
                insights.append(FilterInsight(
                    insight_id=f"pattern_{pattern_type}",
                    title=f"Common {pattern_type.replace('_', ' ').title()} Pattern",
                    description=f"Users exhibit the '{pattern_type}' pattern {count} times in the data.",
                    impact_level="medium",
                    category="behavior",
                    data={"pattern_type": pattern_type, "pattern_count": count},
                    recommendations=[
                        f"Optimize the interface for {pattern_type} patterns",
                        f"Provide shortcuts for common {pattern_type} workflows"
                    ]
                ))
        
        return insights
    
    async def _prepare_visualization_data(self, analytics_response: FilterAnalyticsResponse) -> Dict[str, Any]:
        """Prepare data in visualization-ready format."""
        return {
            "usage_summary": {
                "total_applications": analytics_response.usage_summary.total_applications,
                "unique_users": analytics_response.usage_summary.unique_users,
                "average_result_count": analytics_response.usage_summary.average_result_count,
                "filter_efficiency": analytics_response.usage_summary.filter_efficiency_score * 100,
                "peak_usage_times": analytics_response.usage_summary.peak_usage_times
            },
            "popular_filters": [
                {
                    "name": f"{pf['filter_type']}: {pf['filter_value']}",
                    "count": pf['usage_count']
                }
                for pf in analytics_response.popular_filters[:10]
            ],
            "effectiveness_by_type": [
                {
                    "filter_type": ef.filter_type,
                    "success_rate": ef.conversion_rate * 100,
                    "usage_count": ef.application_count
                }
                for ef in analytics_response.effectiveness_metrics[:10]
            ],
            "user_behavior_patterns": [
                {
                    "type": p['pattern_type'],
                    "count": p.get('usage_count', 1)
                }
                for p in analytics_response.user_behavior_patterns
            ],
            "trends": [
                {
                    "date": t.date.isoformat()[:10],
                    "filter_type": t.filter_type,
                    "usage_count": t.usage_count,
                    "avg_result_count": t.average_result_count
                }
                for t in analytics_response.trends
            ]
        }
    
    async def get_filter_performance_metrics(self, config_hash: str) -> Optional[FilterPerformanceMetrics]:
        """Get performance metrics for a specific filter configuration."""
        if config_hash not in self.performance_metrics:
            return None
        
        metrics = self.performance_metrics[config_hash]
        
        return FilterPerformanceMetrics(
            filter_config_hash=config_hash,
            execution_count=metrics['execution_count'],
            average_execution_time_ms=metrics['total_execution_time'] / metrics['execution_count'] if metrics['execution_count'] > 0 else 0,
            success_rate=metrics['success_count'] / metrics['execution_count'] if metrics['execution_count'] > 0 else 0,
            result_quality_score=metrics['total_result_count'] / metrics['success_count'] if metrics['success_count'] > 0 else 0,
            cache_hit_rate=metrics['cache_hits'] / metrics['execution_count'] if metrics['execution_count'] > 0 else 0,
            user_engagement_score=0.7  # Placeholder - would come from actual user engagement data
        )
    
    async def run_filter_ab_test(self, test_id: str, filter_a: Dict[str, Any], filter_b: Dict[str, Any], 
                                metric: str = "result_quality") -> FilterABTestResult:
        """
        Run an A/B test between two filter configurations.
        
        Args:
            test_id: Unique identifier for the test
            filter_a: Configuration for filter version A
            filter_b: Configuration for filter version B
            metric: Metric to compare (result_quality, user_satisfaction, etc.)
        
        Returns:
            FilterABTestResult with test results
        """
        # In a real implementation, this would run actual A/B tests with real users
        # For this demo, we'll simulate results
        
        # Simulate some test results
        import random
        
        result_a = random.uniform(0.5, 1.0)  # Simulated result for version A
        result_b = random.uniform(0.5, 1.0)  # Simulated result for version B
        
        winner = None
        if result_a > result_b:
            winner = "A"
        elif result_b > result_a:
            winner = "B"
        # If equal, winner stays None (tie)
        
        return FilterABTestResult(
            test_id=test_id,
            filter_version_a=filter_a,
            filter_version_b=filter_b,
            metric=metric,
            result_a=result_a,
            result_b=result_b,
            confidence_level=0.85,  # Simulated confidence
            winner=winner,
            sample_size=100  # Simulated sample size
        )