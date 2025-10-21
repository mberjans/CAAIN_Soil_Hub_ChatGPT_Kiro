"""
Economic Optimization Repository for Fertilizer Strategy Optimization Service.

This module provides database operations for storing and retrieving economic optimization results,
including scenario modeling, multi-objective optimization, risk assessment, sensitivity analysis,
and Monte Carlo simulation data.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date, timedelta
import json

from ..models.economic_optimization_models import (
    EconomicOptimizationResponse,
    EconomicScenario,
    MultiObjectiveOptimization,
    RiskAssessment,
    SensitivityAnalysis,
    MonteCarloSimulation,
    BudgetAllocation,
    InvestmentPrioritization
)
from ..database.database_connection import get_database_connection
from ..exceptions import EconomicOptimizationError, DatabaseError

logger = logging.getLogger(__name__)


class EconomicOptimizationRepository:
    """Repository for economic optimization data storage and retrieval."""

    def __init__(self):
        self.db_pool = None

    async def _get_connection(self):
        """Get database connection from pool."""
        if not self.db_pool:
            self.db_pool = await get_database_connection()
        return self.db_pool

    async def store_optimization_result(
        self,
        result: EconomicOptimizationResponse
    ) -> bool:
        """
        Store economic optimization result in database.
        
        Args:
            result: Economic optimization response to store
            
        Returns:
            True if stored successfully, False otherwise
            
        Raises:
            EconomicOptimizationError: If storage fails
        """
        try:
            conn = await self._get_connection()
            
            # Store optimization result
            query = """
            INSERT INTO economic_optimization_results (
                analysis_id, scenarios, optimization_results, risk_assessments,
                sensitivity_analysis, monte_carlo_simulation, budget_allocations,
                investment_priorities, recommendations, processing_time_ms,
                created_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            ON CONFLICT (analysis_id) DO UPDATE SET
                scenarios = EXCLUDED.scenarios,
                optimization_results = EXCLUDED.optimization_results,
                risk_assessments = EXCLUDED.risk_assessments,
                sensitivity_analysis = EXCLUDED.sensitivity_analysis,
                monte_carlo_simulation = EXCLUDED.monte_carlo_simulation,
                budget_allocations = EXCLUDED.budget_allocations,
                investment_priorities = EXCLUDED.investment_priorities,
                recommendations = EXCLUDED.recommendations,
                processing_time_ms = EXCLUDED.processing_time_ms,
                created_at = EXCLUDED.created_at
            """
            
            # Convert complex objects to JSON for storage
            scenarios_json = json.dumps([scenario.dict() for scenario in result.scenarios])
            optimization_results_json = json.dumps([opt.dict() for opt in result.optimization_results])
            risk_assessments_json = json.dumps([risk.dict() for risk in result.risk_assessments])
            sensitivity_analysis_json = json.dumps(result.sensitivity_analysis.dict())
            monte_carlo_simulation_json = json.dumps(result.monte_carlo_simulation.dict())
            budget_allocations_json = json.dumps([alloc.dict() for alloc in result.budget_allocations])
            investment_priorities_json = json.dumps([priority.dict() for priority in result.investment_priorities])
            recommendations_json = json.dumps(result.recommendations)
            
            await conn.execute(
                query,
                result.analysis_id,
                scenarios_json,
                optimization_results_json,
                risk_assessments_json,
                sensitivity_analysis_json,
                monte_carlo_simulation_json,
                budget_allocations_json,
                investment_priorities_json,
                recommendations_json,
                result.processing_time_ms,
                result.created_at
            )
            
            logger.info(f"Stored economic optimization result for analysis {result.analysis_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing economic optimization result: {e}")
            raise EconomicOptimizationError(f"Failed to store optimization result: {str(e)}")

    async def get_optimization_result(
        self,
        analysis_id: str
    ) -> Optional[EconomicOptimizationResponse]:
        """
        Retrieve economic optimization result from database.
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            Economic optimization response or None if not found
            
        Raises:
            EconomicOptimizationError: If retrieval fails
        """
        try:
            conn = await self._get_connection()
            
            query = """
            SELECT 
                analysis_id, scenarios, optimization_results, risk_assessments,
                sensitivity_analysis, monte_carlo_simulation, budget_allocations,
                investment_priorities, recommendations, processing_time_ms,
                created_at
            FROM economic_optimization_results
            WHERE analysis_id = $1
            """
            
            row = await conn.fetchrow(query, analysis_id)
            if not row:
                logger.info(f"No economic optimization result found for analysis {analysis_id}")
                return None
            
            # Convert JSON back to objects
            scenarios = [EconomicScenario(**scenario) for scenario in json.loads(row['scenarios'])]
            optimization_results = [MultiObjectiveOptimization(**opt) for opt in json.loads(row['optimization_results'])]
            risk_assessments = [RiskAssessment(**risk) for risk in json.loads(row['risk_assessments'])]
            
            sensitivity_analysis = SensitivityAnalysis(**json.loads(row['sensitivity_analysis']))
            monte_carlo_simulation = MonteCarloSimulation(**json.loads(row['monte_carlo_simulation']))
            
            budget_allocations = [BudgetAllocation(**alloc) for alloc in json.loads(row['budget_allocations'])]
            investment_priorities = [InvestmentPrioritization(**priority) for priority in json.loads(row['investment_priorities'])]
            
            result = EconomicOptimizationResponse(
                analysis_id=row['analysis_id'],
                scenarios=scenarios,
                optimization_results=optimization_results,
                risk_assessments=risk_assessments,
                sensitivity_analysis=sensitivity_analysis,
                monte_carlo_simulation=monte_carlo_simulation,
                budget_allocations=budget_allocations,
                investment_priorities=investment_priorities,
                recommendations=json.loads(row['recommendations']),
                processing_time_ms=row['processing_time_ms'],
                created_at=row['created_at']
            )
            
            logger.info(f"Retrieved economic optimization result for analysis {analysis_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving economic optimization result: {e}")
            raise EconomicOptimizationError(f"Failed to retrieve optimization result: {str(e)}")

    async def get_recent_optimization_results(
        self,
        user_id: UUID,
        limit: int = 10
    ) -> List[EconomicOptimizationResponse]:
        """
        Retrieve recent economic optimization results for user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of results to return
            
        Returns:
            List of recent economic optimization responses
            
        Raises:
            EconomicOptimizationError: If retrieval fails
        """
        try:
            conn = await self._get_connection()
            
            query = """
            SELECT 
                analysis_id, scenarios, optimization_results, risk_assessments,
                sensitivity_analysis, monte_carlo_simulation, budget_allocations,
                investment_priorities, recommendations, processing_time_ms,
                created_at
            FROM economic_optimization_results
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT $2
            """
            
            rows = await conn.fetch(query, user_id, limit)
            results = []
            
            for row in rows:
                # Convert JSON back to objects
                scenarios = [EconomicScenario(**scenario) for scenario in json.loads(row['scenarios'])]
                optimization_results = [MultiObjectiveOptimization(**opt) for opt in json.loads(row['optimization_results'])]
                risk_assessments = [RiskAssessment(**risk) for risk in json.loads(row['risk_assessments'])]
                
                sensitivity_analysis = SensitivityAnalysis(**json.loads(row['sensitivity_analysis']))
                monte_carlo_simulation = MonteCarloSimulation(**json.loads(row['monte_carlo_simulation']))
                
                budget_allocations = [BudgetAllocation(**alloc) for alloc in json.loads(row['budget_allocations'])]
                investment_priorities = [InvestmentPrioritization(**priority) for priority in json.loads(row['investment_priorities'])]
                
                result = EconomicOptimizationResponse(
                    analysis_id=row['analysis_id'],
                    scenarios=scenarios,
                    optimization_results=optimization_results,
                    risk_assessments=risk_assessments,
                    sensitivity_analysis=sensitivity_analysis,
                    monte_carlo_simulation=monte_carlo_simulation,
                    budget_allocations=budget_allocations,
                    investment_priorities=investment_priorities,
                    recommendations=json.loads(row['recommendations']),
                    processing_time_ms=row['processing_time_ms'],
                    created_at=row['created_at']
                )
                
                results.append(result)
            
            logger.info(f"Retrieved {len(results)} recent economic optimization results for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving recent economic optimization results: {e}")
            raise EconomicOptimizationError(f"Failed to retrieve recent optimization results: {str(e)}")

    async def delete_optimization_result(
        self,
        analysis_id: str
    ) -> bool:
        """
        Delete economic optimization result from database.
        
        Args:
            analysis_id: Analysis identifier
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            EconomicOptimizationError: If deletion fails
        """
        try:
            conn = await self._get_connection()
            
            query = """
            DELETE FROM economic_optimization_results
            WHERE analysis_id = $1
            """
            
            result = await conn.execute(query, analysis_id)
            deleted_rows = int(result.split()[1]) if result else 0
            
            if deleted_rows > 0:
                logger.info(f"Deleted economic optimization result for analysis {analysis_id}")
                return True
            else:
                logger.info(f"No economic optimization result found for deletion: {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting economic optimization result: {e}")
            raise EconomicOptimizationError(f"Failed to delete optimization result: {str(e)}")

    async def update_optimization_result(
        self,
        analysis_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update economic optimization result in database.
        
        Args:
            analysis_id: Analysis identifier
            updates: Dictionary of fields to update
            
        Returns:
            True if updated successfully, False otherwise
            
        Raises:
            EconomicOptimizationError: If update fails
        """
        try:
            conn = await self._get_connection()
            
            # Build dynamic update query
            set_clause = ", ".join([f"{key} = ${idx+2}" for idx, key in enumerate(updates.keys())])
            query = f"""
            UPDATE economic_optimization_results
            SET {set_clause}
            WHERE analysis_id = $1
            """
            
            # Execute query with parameters
            params = [analysis_id] + list(updates.values())
            result = await conn.execute(query, *params)
            updated_rows = int(result.split()[1]) if result else 0
            
            if updated_rows > 0:
                logger.info(f"Updated economic optimization result for analysis {analysis_id}")
                return True
            else:
                logger.info(f"No economic optimization result found for update: {analysis_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating economic optimization result: {e}")
            raise EconomicOptimizationError(f"Failed to update optimization result: {str(e)}")

    async def list_optimization_results(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[EconomicOptimizationResponse]:
        """
        List economic optimization results with filtering.
        
        Args:
            user_id: User identifier (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            limit: Maximum results to return
            offset: Offset for pagination
            
        Returns:
            List of economic optimization responses
            
        Raises:
            EconomicOptimizationError: If listing fails
        """
        try:
            conn = await self._get_connection()
            
            # Build query with filters
            query_parts = [
                "SELECT analysis_id, scenarios, optimization_results, risk_assessments,",
                "sensitivity_analysis, monte_carlo_simulation, budget_allocations,",
                "investment_priorities, recommendations, processing_time_ms, created_at",
                "FROM economic_optimization_results"
            ]
            
            conditions = []
            params = []
            param_index = 1
            
            if user_id:
                conditions.append(f"user_id = ${param_index}")
                params.append(user_id)
                param_index += 1
                
            if start_date:
                conditions.append(f"created_at >= ${param_index}")
                params.append(start_date)
                param_index += 1
                
            if end_date:
                conditions.append(f"created_at <= ${param_index}")
                params.append(end_date)
                param_index += 1
                
            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))
                
            query_parts.append("ORDER BY created_at DESC")
            query_parts.append(f"LIMIT ${param_index}")
            params.append(limit)
            param_index += 1
            
            query_parts.append(f"OFFSET ${param_index}")
            params.append(offset)
            
            query = " ".join(query_parts)
            
            rows = await conn.fetch(query, *params)
            results = []
            
            for row in rows:
                # Convert JSON back to objects
                scenarios = [EconomicScenario(**scenario) for scenario in json.loads(row['scenarios'])]
                optimization_results = [MultiObjectiveOptimization(**opt) for opt in json.loads(row['optimization_results'])]
                risk_assessments = [RiskAssessment(**risk) for risk in json.loads(row['risk_assessments'])]
                
                sensitivity_analysis = SensitivityAnalysis(**json.loads(row['sensitivity_analysis']))
                monte_carlo_simulation = MonteCarloSimulation(**json.loads(row['monte_carlo_simulation']))
                
                budget_allocations = [BudgetAllocation(**alloc) for alloc in json.loads(row['budget_allocations'])]
                investment_priorities = [InvestmentPrioritization(**priority) for priority in json.loads(row['investment_priorities'])]
                
                result = EconomicOptimizationResponse(
                    analysis_id=row['analysis_id'],
                    scenarios=scenarios,
                    optimization_results=optimization_results,
                    risk_assessments=risk_assessments,
                    sensitivity_analysis=sensitivity_analysis,
                    monte_carlo_simulation=monte_carlo_simulation,
                    budget_allocations=budget_allocations,
                    investment_priorities=investment_priorities,
                    recommendations=json.loads(row['recommendations']),
                    processing_time_ms=row['processing_time_ms'],
                    created_at=row['created_at']
                )
                
                results.append(result)
            
            logger.info(f"Listed {len(results)} economic optimization results")
            return results
            
        except Exception as e:
            logger.error(f"Error listing economic optimization results: {e}")
            raise EconomicOptimizationError(f"Failed to list optimization results: {str(e)}")

    async def get_optimization_statistics(
        self,
        user_id: Optional[UUID] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get statistics for economic optimization results.
        
        Args:
            user_id: User identifier (optional)
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            
        Returns:
            Dictionary of optimization statistics
            
        Raises:
            EconomicOptimizationError: If statistics retrieval fails
        """
        try:
            conn = await self._get_connection()
            
            # Build query with filters
            query_parts = [
                "SELECT COUNT(*) as total_analyses,",
                "AVG(processing_time_ms) as avg_processing_time,",
                "MIN(created_at) as first_analysis,",
                "MAX(created_at) as last_analysis"
            ]
            
            from_clause = "FROM economic_optimization_results"
            conditions = []
            params = []
            param_index = 1
            
            if user_id:
                conditions.append(f"user_id = ${param_index}")
                params.append(user_id)
                param_index += 1
                
            if start_date:
                conditions.append(f"created_at >= ${param_index}")
                params.append(start_date)
                param_index += 1
                
            if end_date:
                conditions.append(f"created_at <= ${param_index}")
                params.append(end_date)
                param_index += 1
                
            query_parts.append(from_clause)
            
            if conditions:
                query_parts.append("WHERE " + " AND ".join(conditions))
                
            query = " ".join(query_parts)
            
            row = await conn.fetchrow(query, *params)
            
            if not row:
                return {}
            
            statistics = {
                'total_analyses': row['total_analyses'],
                'avg_processing_time_ms': row['avg_processing_time'],
                'first_analysis': row['first_analysis'],
                'last_analysis': row['last_analysis']
            }
            
            logger.info(f"Retrieved economic optimization statistics")
            return statistics
            
        except Exception as e:
            logger.error(f"Error retrieving economic optimization statistics: {e}")
            raise EconomicOptimizationError(f"Failed to retrieve optimization statistics: {str(e)}")

    async def get_user_optimization_summary(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Get optimization summary for user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of user optimization summary
            
        Raises:
            EconomicOptimizationError: If summary retrieval fails
        """
        try:
            conn = await self._get_connection()
            
            query = """
            SELECT 
                COUNT(*) as total_analyses,
                AVG(processing_time_ms) as avg_processing_time,
                MIN(created_at) as first_analysis,
                MAX(created_at) as last_analysis,
                COUNT(DISTINCT field_id) as total_fields
            FROM economic_optimization_results
            WHERE user_id = $1
            """
            
            row = await conn.fetchrow(query, user_id)
            
            if not row:
                return {}
            
            summary = {
                'user_id': str(user_id),
                'total_analyses': row['total_analyses'],
                'avg_processing_time_ms': row['avg_processing_time'],
                'first_analysis': row['first_analysis'],
                'last_analysis': row['last_analysis'],
                'total_fields': row['total_fields']
            }
            
            logger.info(f"Retrieved user optimization summary for user {user_id}")
            return summary
            
        except Exception as e:
            logger.error(f"Error retrieving user optimization summary: {e}")
            raise EconomicOptimizationError(f"Failed to retrieve user optimization summary: {str(e)}")

    async def get_optimization_trends(
        self,
        user_id: Optional[UUID] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get optimization trends over time.
        
        Args:
            user_id: User identifier (optional)
            days: Number of days to analyze
            
        Returns:
            List of trend data points
            
        Raises:
            EconomicOptimizationError: If trend retrieval fails
        """
        try:
            conn = await self._get_connection()
            
            # Calculate date range
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days)
            
            # Build query with filters
            query_parts = [
                "SELECT DATE(created_at) as analysis_date,",
                "COUNT(*) as analyses_count,",
                "AVG(processing_time_ms) as avg_processing_time"
            ]
            
            from_clause = "FROM economic_optimization_results"
            conditions = [f"created_at >= '${start_date}' AND created_at <= '${end_date}'"]
            params = []
            param_index = 1
            
            if user_id:
                conditions.append(f"user_id = ${param_index}")
                params.append(user_id)
                param_index += 1
                
            query_parts.append(from_clause)
            query_parts.append("WHERE " + " AND ".join(conditions))
            query_parts.append("GROUP BY DATE(created_at)")
            query_parts.append("ORDER BY analysis_date ASC")
            
            query = " ".join(query_parts)
            
            rows = await conn.fetch(query, *params)
            trends = []
            
            for row in rows:
                trend_point = {
                    'analysis_date': row['analysis_date'],
                    'analyses_count': row['analyses_count'],
                    'avg_processing_time_ms': row['avg_processing_time']
                }
                trends.append(trend_point)
            
            logger.info(f"Retrieved optimization trends for {days} days")
            return trends
            
        except Exception as e:
            logger.error(f"Error retrieving optimization trends: {e}")
            raise EconomicOptimizationError(f"Failed to retrieve optimization trends: {str(e)}")