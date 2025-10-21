"""
Historical Data Service for fertilizer application method selection.

This service handles:
- Historical data collection and storage
- Outcome tracking and analysis
- Performance metrics calculation
- Continuous learning and model improvement
"""

import asyncio
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.fertilizer_db import (
    get_async_session, ApplicationMethodRecord, MethodOutcomeRecord,
    MethodPerformanceRecord, AlgorithmTrainingRecord
)
from src.models.application_models import ApplicationMethodType, ApplicationRequest, ApplicationResponse

logger = logging.getLogger(__name__)


class OutcomeType(str, Enum):
    """Types of outcomes for tracking."""
    SUCCESS = "success"
    PARTIAL_SUCCESS = "partial_success"
    FAILURE = "failure"
    UNKNOWN = "unknown"


class PerformanceMetric(str, Enum):
    """Performance metrics for evaluation."""
    EFFICIENCY_SCORE = "efficiency_score"
    COST_EFFECTIVENESS = "cost_effectiveness"
    ENVIRONMENTAL_IMPACT = "environmental_impact"
    YIELD_IMPACT = "yield_impact"
    FARMER_SATISFACTION = "farmer_satisfaction"


@dataclass
class OutcomeData:
    """Data structure for outcome tracking."""
    application_id: str
    method_used: ApplicationMethodType
    algorithm_used: str
    predicted_efficiency: float
    predicted_cost: float
    actual_efficiency: Optional[float] = None
    actual_cost: Optional[float] = None
    yield_impact: Optional[float] = None
    farmer_satisfaction: Optional[float] = None
    environmental_impact: Optional[str] = None
    outcome_type: OutcomeType = OutcomeType.UNKNOWN
    notes: Optional[str] = None
    timestamp: datetime = None


@dataclass
class PerformanceAnalysis:
    """Performance analysis results."""
    algorithm_name: str
    total_applications: int
    success_rate: float
    average_efficiency: float
    average_cost: float
    average_satisfaction: float
    performance_trend: str  # "improving", "stable", "declining"
    confidence_score: float
    recommendations: List[str]


class HistoricalDataService:
    """Service for managing historical data and outcome tracking."""
    
    def __init__(self):
        self.session_factory = get_async_session
        self.performance_cache = {}
        self.cache_ttl = 3600  # 1 hour
    
    async def record_application_outcome(self, outcome_data: OutcomeData) -> bool:
        """Record the outcome of a fertilizer application."""
        try:
            async with self.session_factory() as session:
                # Create outcome record
                outcome_record = MethodOutcomeRecord(
                    outcome_id=str(uuid4()),
                    application_id=outcome_data.application_id,
                    method_used=outcome_data.method_used.value,
                    algorithm_used=outcome_data.algorithm_used,
                    predicted_efficiency=outcome_data.predicted_efficiency,
                    predicted_cost=outcome_data.predicted_cost,
                    actual_efficiency=outcome_data.actual_efficiency,
                    actual_cost=outcome_data.actual_cost,
                    yield_impact=outcome_data.yield_impact,
                    farmer_satisfaction=outcome_data.farmer_satisfaction,
                    environmental_impact=outcome_data.environmental_impact,
                    outcome_type=outcome_data.outcome_type.value,
                    notes=outcome_data.notes,
                    recorded_at=outcome_data.timestamp or datetime.utcnow()
                )
                
                session.add(outcome_record)
                await session.commit()
                
                # Update performance metrics
                await self._update_performance_metrics(outcome_record)
                
                logger.info(f"Recorded outcome for application {outcome_data.application_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error recording application outcome: {e}")
            return False
    
    async def _update_performance_metrics(self, outcome_record: MethodOutcomeRecord):
        """Update performance metrics based on outcome."""
        try:
            async with self.session_factory() as session:
                # Calculate performance metrics
                efficiency_score = self._calculate_efficiency_score(outcome_record)
                cost_score = self._calculate_cost_score(outcome_record)
                satisfaction_score = outcome_record.farmer_satisfaction or 0.0
                
                # Check if performance record exists
                stmt = select(MethodPerformanceRecord).where(
                    and_(
                        MethodPerformanceRecord.method_used == outcome_record.method_used,
                        MethodPerformanceRecord.algorithm_used == outcome_record.algorithm_used
                    )
                )
                result = await session.execute(stmt)
                performance_record = result.scalar_one_or_none()
                
                if performance_record:
                    # Update existing record
                    performance_record.total_applications += 1
                    performance_record.total_efficiency += efficiency_score
                    performance_record.total_cost += cost_score
                    performance_record.total_satisfaction += satisfaction_score
                    performance_record.last_updated = datetime.utcnow()
                    
                    # Update averages
                    performance_record.average_efficiency = (
                        performance_record.total_efficiency / performance_record.total_applications
                    )
                    performance_record.average_cost = (
                        performance_record.total_cost / performance_record.total_applications
                    )
                    performance_record.average_satisfaction = (
                        performance_record.total_satisfaction / performance_record.total_applications
                    )
                else:
                    # Create new performance record
                    performance_record = MethodPerformanceRecord(
                        performance_id=str(uuid4()),
                        method_used=outcome_record.method_used,
                        algorithm_used=outcome_record.algorithm_used,
                        total_applications=1,
                        total_efficiency=efficiency_score,
                        total_cost=cost_score,
                        total_satisfaction=satisfaction_score,
                        average_efficiency=efficiency_score,
                        average_cost=cost_score,
                        average_satisfaction=satisfaction_score,
                        created_at=datetime.utcnow(),
                        last_updated=datetime.utcnow()
                    )
                    session.add(performance_record)
                
                await session.commit()
                
        except Exception as e:
            logger.error(f"Error updating performance metrics: {e}")
    
    def _calculate_efficiency_score(self, outcome_record: MethodOutcomeRecord) -> float:
        """Calculate efficiency score from outcome data."""
        if outcome_record.actual_efficiency is not None:
            return outcome_record.actual_efficiency
        
        # Fallback to predicted efficiency
        return outcome_record.predicted_efficiency
    
    def _calculate_cost_score(self, outcome_record: MethodOutcomeRecord) -> float:
        """Calculate cost score from outcome data."""
        if outcome_record.actual_cost is not None:
            return outcome_record.actual_cost
        
        # Fallback to predicted cost
        return outcome_record.predicted_cost
    
    async def get_historical_data_for_training(
        self,
        method_type: Optional[ApplicationMethodType] = None,
        algorithm: Optional[str] = None,
        days_back: int = 365
    ) -> List[Dict[str, Any]]:
        """Get historical data formatted for ML model training."""
        try:
            async with self.session_factory() as session:
                # Build query
                stmt = select(MethodOutcomeRecord).where(
                    MethodOutcomeRecord.recorded_at >= datetime.utcnow() - timedelta(days=days_back)
                )
                
                if method_type:
                    stmt = stmt.where(MethodOutcomeRecord.method_used == method_type.value)
                
                if algorithm:
                    stmt = stmt.where(MethodOutcomeRecord.algorithm_used == algorithm)
                
                result = await session.execute(stmt)
                records = result.scalars().all()
                
                # Convert to training format
                training_data = []
                for record in records:
                    training_data.append({
                        'application_id': record.application_id,
                        'method_used': record.method_used,
                        'algorithm_used': record.algorithm_used,
                        'predicted_efficiency': record.predicted_efficiency,
                        'predicted_cost': record.predicted_cost,
                        'actual_efficiency': record.actual_efficiency or record.predicted_efficiency,
                        'actual_cost': record.actual_cost or record.predicted_cost,
                        'yield_impact': record.yield_impact or 0.0,
                        'farmer_satisfaction': record.farmer_satisfaction or 0.5,
                        'outcome_type': record.outcome_type,
                        'recorded_at': record.recorded_at
                    })
                
                logger.info(f"Retrieved {len(training_data)} historical records for training")
                return training_data
                
        except Exception as e:
            logger.error(f"Error retrieving historical data: {e}")
            return []
    
    async def analyze_algorithm_performance(
        self,
        algorithm_name: str,
        days_back: int = 90
    ) -> PerformanceAnalysis:
        """Analyze performance of a specific algorithm."""
        try:
            async with self.session_factory() as session:
                # Get performance records
                stmt = select(MethodPerformanceRecord).where(
                    and_(
                        MethodPerformanceRecord.algorithm_used == algorithm_name,
                        MethodPerformanceRecord.last_updated >= datetime.utcnow() - timedelta(days=days_back)
                    )
                )
                result = await session.execute(stmt)
                performance_records = result.scalars().all()
                
                if not performance_records:
                    return PerformanceAnalysis(
                        algorithm_name=algorithm_name,
                        total_applications=0,
                        success_rate=0.0,
                        average_efficiency=0.0,
                        average_cost=0.0,
                        average_satisfaction=0.0,
                        performance_trend="unknown",
                        confidence_score=0.0,
                        recommendations=["Insufficient data for analysis"]
                    )
                
                # Calculate aggregate metrics
                total_applications = sum(record.total_applications for record in performance_records)
                avg_efficiency = np.mean([record.average_efficiency for record in performance_records])
                avg_cost = np.mean([record.average_cost for record in performance_records])
                avg_satisfaction = np.mean([record.average_satisfaction for record in performance_records])
                
                # Calculate success rate (satisfaction > 0.7)
                success_rate = sum(1 for record in performance_records if record.average_satisfaction > 0.7) / len(performance_records)
                
                # Determine performance trend
                performance_trend = self._calculate_performance_trend(performance_records)
                
                # Calculate confidence score
                confidence_score = min(total_applications / 100.0, 1.0)  # More data = higher confidence
                
                # Generate recommendations
                recommendations = self._generate_performance_recommendations(
                    avg_efficiency, avg_cost, avg_satisfaction, success_rate
                )
                
                return PerformanceAnalysis(
                    algorithm_name=algorithm_name,
                    total_applications=total_applications,
                    success_rate=success_rate,
                    average_efficiency=avg_efficiency,
                    average_cost=avg_cost,
                    average_satisfaction=avg_satisfaction,
                    performance_trend=performance_trend,
                    confidence_score=confidence_score,
                    recommendations=recommendations
                )
                
        except Exception as e:
            logger.error(f"Error analyzing algorithm performance: {e}")
            return PerformanceAnalysis(
                algorithm_name=algorithm_name,
                total_applications=0,
                success_rate=0.0,
                average_efficiency=0.0,
                average_cost=0.0,
                average_satisfaction=0.0,
                performance_trend="error",
                confidence_score=0.0,
                recommendations=[f"Error in analysis: {str(e)}"]
            )
    
    def _calculate_performance_trend(self, performance_records: List[MethodPerformanceRecord]) -> str:
        """Calculate performance trend from historical data."""
        if len(performance_records) < 2:
            return "insufficient_data"
        
        # Sort by last_updated
        sorted_records = sorted(performance_records, key=lambda x: x.last_updated)
        
        # Calculate trend in satisfaction scores
        satisfaction_scores = [record.average_satisfaction for record in sorted_records]
        
        # Simple trend calculation
        if len(satisfaction_scores) >= 3:
            recent_avg = np.mean(satisfaction_scores[-3:])
            earlier_avg = np.mean(satisfaction_scores[:3])
            
            if recent_avg > earlier_avg + 0.1:
                return "improving"
            elif recent_avg < earlier_avg - 0.1:
                return "declining"
            else:
                return "stable"
        
        return "stable"
    
    def _generate_performance_recommendations(
        self,
        avg_efficiency: float,
        avg_cost: float,
        avg_satisfaction: float,
        success_rate: float
    ) -> List[str]:
        """Generate recommendations based on performance metrics."""
        recommendations = []
        
        if avg_efficiency < 0.7:
            recommendations.append("Consider improving efficiency prediction models")
        
        if avg_cost > 30.0:
            recommendations.append("Focus on cost optimization algorithms")
        
        if avg_satisfaction < 0.6:
            recommendations.append("Improve farmer satisfaction through better recommendations")
        
        if success_rate < 0.7:
            recommendations.append("Review algorithm parameters and training data quality")
        
        if not recommendations:
            recommendations.append("Performance metrics are within acceptable ranges")
        
        return recommendations
    
    async def get_method_comparison_data(
        self,
        method_types: List[ApplicationMethodType],
        days_back: int = 90
    ) -> Dict[str, Dict[str, Any]]:
        """Get comparison data for multiple methods."""
        comparison_data = {}
        
        for method_type in method_types:
            try:
                async with self.session_factory() as session:
                    # Get performance records for this method
                    stmt = select(MethodPerformanceRecord).where(
                        and_(
                            MethodPerformanceRecord.method_used == method_type.value,
                            MethodPerformanceRecord.last_updated >= datetime.utcnow() - timedelta(days=days_back)
                        )
                    )
                    result = await session.execute(stmt)
                    records = result.scalars().all()
                    
                    if records:
                        comparison_data[method_type.value] = {
                            'total_applications': sum(record.total_applications for record in records),
                            'average_efficiency': np.mean([record.average_efficiency for record in records]),
                            'average_cost': np.mean([record.average_cost for record in records]),
                            'average_satisfaction': np.mean([record.average_satisfaction for record in records]),
                            'algorithms_used': list(set(record.algorithm_used for record in records))
                        }
                    else:
                        comparison_data[method_type.value] = {
                            'total_applications': 0,
                            'average_efficiency': 0.0,
                            'average_cost': 0.0,
                            'average_satisfaction': 0.0,
                            'algorithms_used': []
                        }
                        
            except Exception as e:
                logger.error(f"Error getting comparison data for {method_type}: {e}")
                comparison_data[method_type.value] = {
                    'error': str(e)
                }
        
        return comparison_data
    
    async def record_algorithm_training(
        self,
        algorithm_name: str,
        training_data_size: int,
        model_metrics: Dict[str, float],
        training_time_ms: float
    ) -> bool:
        """Record algorithm training session."""
        try:
            async with self.session_factory() as session:
                training_record = AlgorithmTrainingRecord(
                    training_id=str(uuid4()),
                    algorithm_name=algorithm_name,
                    training_data_size=training_data_size,
                    model_metrics=model_metrics,
                    training_time_ms=training_time_ms,
                    trained_at=datetime.utcnow()
                )
                
                session.add(training_record)
                await session.commit()
                
                logger.info(f"Recorded training session for {algorithm_name}")
                return True
                
        except Exception as e:
            logger.error(f"Error recording algorithm training: {e}")
            return False
    
    async def get_training_history(
        self,
        algorithm_name: Optional[str] = None,
        days_back: int = 30
    ) -> List[Dict[str, Any]]:
        """Get training history for algorithms."""
        try:
            async with self.session_factory() as session:
                stmt = select(AlgorithmTrainingRecord).where(
                    AlgorithmTrainingRecord.trained_at >= datetime.utcnow() - timedelta(days=days_back)
                )
                
                if algorithm_name:
                    stmt = stmt.where(AlgorithmTrainingRecord.algorithm_name == algorithm_name)
                
                result = await session.execute(stmt)
                records = result.scalars().all()
                
                training_history = []
                for record in records:
                    training_history.append({
                        'training_id': record.training_id,
                        'algorithm_name': record.algorithm_name,
                        'training_data_size': record.training_data_size,
                        'model_metrics': record.model_metrics,
                        'training_time_ms': record.training_time_ms,
                        'trained_at': record.trained_at
                    })
                
                return training_history
                
        except Exception as e:
            logger.error(f"Error retrieving training history: {e}")
            return []
    
    async def cleanup_old_data(self, days_to_keep: int = 365) -> int:
        """Clean up old historical data."""
        try:
            async with self.session_factory() as session:
                cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
                
                # Delete old outcome records
                stmt = delete(MethodOutcomeRecord).where(
                    MethodOutcomeRecord.recorded_at < cutoff_date
                )
                result = await session.execute(stmt)
                deleted_outcomes = result.rowcount
                
                # Delete old training records
                stmt = delete(AlgorithmTrainingRecord).where(
                    AlgorithmTrainingRecord.trained_at < cutoff_date
                )
                result = await session.execute(stmt)
                deleted_training = result.rowcount
                
                await session.commit()
                
                total_deleted = deleted_outcomes + deleted_training
                logger.info(f"Cleaned up {total_deleted} old records")
                return total_deleted
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return 0