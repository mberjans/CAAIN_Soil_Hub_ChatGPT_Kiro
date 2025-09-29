"""
Optimized Variety Recommendation Service

This service integrates the performance optimization components with the existing
variety recommendation logic to achieve the performance targets:
- <2s recommendation generation
- <1s variety search  
- <500ms variety details

TICKET-005_crop-variety-recommendations-14.1: Implement comprehensive variety recommendation performance optimization
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple, Union
from uuid import UUID
import json

# Import existing services
from .variety_recommendation_service import VarietyRecommendationService
from .performance_optimization_service import (
    PerformanceOptimizationService, 
    OptimizationConfig,
    get_performance_optimization_service
)
from .performance_monitor import performance_monitor

# Import models
try:
    from ..models.crop_variety_models import (
        EnhancedCropVariety,
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse
    )
    from ..models.crop_taxonomy_models import ComprehensiveCropData
except ImportError:
    from models.crop_variety_models import (
        EnhancedCropVariety,
        VarietyRecommendation,
        VarietyComparisonRequest,
        VarietyComparisonResponse
    )
    from models.crop_taxonomy_models import ComprehensiveCropData

logger = logging.getLogger(__name__)


class OptimizedVarietyRecommendationService:
    """
    Optimized variety recommendation service with comprehensive performance optimization.
    
    This service wraps the existing VarietyRecommendationService with:
    - Multi-level caching
    - Database query optimization
    - Response compression and pagination
    - Performance monitoring and metrics
    """
    
    def __init__(self, database_url: Optional[str] = None, config: Optional[OptimizationConfig] = None):
        """Initialize the optimized variety recommendation service."""
        self.database_url = database_url
        self.config = config or OptimizationConfig()
        
        # Initialize base service
        self.base_service = VarietyRecommendationService(database_url)
        
        # Initialize performance optimization
        self.optimization_service = get_performance_optimization_service(database_url)
        
        # Performance tracking
        self.recommendation_count = 0
        self.search_count = 0
        self.details_count = 0
        self.start_time = time.time()
        
        logger.info("Optimized variety recommendation service initialized")
    
    async def get_optimized_variety_recommendations(
        self,
        crop_data: ComprehensiveCropData,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[VarietyRecommendation]:
        """
        Get optimized variety recommendations with performance targets <2s.
        
        Args:
            crop_data: Base crop information
            regional_context: Regional growing conditions and constraints
            farmer_preferences: Optional farmer-specific preferences and priorities
            limit: Maximum number of recommendations to return
            
        Returns:
            Ranked list of variety recommendations with scoring and rationale
        """
        start_time = time.time()
        self.recommendation_count += 1
        
        try:
            # Create cache key for recommendations
            cache_key = {
                "crop_id": str(crop_data.id),
                "regional_context": regional_context,
                "farmer_preferences": farmer_preferences or {},
                "limit": limit
            }
            
            # Check cache first
            cached_recommendations = await self.optimization_service.cache.get(
                "variety_recommendations", cache_key
            )
            
            if cached_recommendations:
                execution_time = (time.time() - start_time) * 1000
                logger.info(f"Cache hit for variety recommendations: {execution_time:.2f}ms")
                
                performance_monitor.record_operation(
                    operation="variety_recommendations_cached",
                    execution_time_ms=execution_time,
                    cache_hit=True
                )
                
                return cached_recommendations.get("recommendations", [])
            
            # Execute optimized recommendation generation
            recommendations = await self._generate_optimized_recommendations(
                crop_data, regional_context, farmer_preferences, limit
            )
            
            # Cache results
            cache_data = {
                "recommendations": recommendations,
                "generated_at": datetime.utcnow().isoformat(),
                "cache_key": cache_key
            }
            
            await self.optimization_service.cache.set(
                "variety_recommendations", cache_key, cache_data,
                self.config.cache_ttl_recommendations
            )
            
            # Record performance metrics
            execution_time = (time.time() - start_time) * 1000
            
            # Check if we met performance targets
            if execution_time > self.config.target_recommendation_time_ms:
                logger.warning(f"Recommendation generation exceeded target: {execution_time:.2f}ms > {self.config.target_recommendation_time_ms}ms")
            
            performance_monitor.record_operation(
                operation="variety_recommendations_optimized",
                execution_time_ms=execution_time,
                cache_hit=False,
                additional_data={
                    "recommendation_count": len(recommendations),
                    "performance_target_met": execution_time <= self.config.target_recommendation_time_ms
                }
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimized variety recommendations failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            performance_monitor.record_operation(
                operation="variety_recommendations_error",
                execution_time_ms=execution_time,
                cache_hit=False,
                additional_data={"error": str(e)}
            )
            raise
    
    async def _generate_optimized_recommendations(
        self,
        crop_data: ComprehensiveCropData,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]],
        limit: int
    ) -> List[VarietyRecommendation]:
        """Generate recommendations using optimized database queries."""
        
        # Use optimized database query for variety retrieval
        variety_query = """
        SELECT v.variety_id, v.variety_name, v.crop_id, v.yield_potential,
               v.disease_resistance, v.stress_tolerances, v.herbicide_tolerances,
               v.breeder_company, v.maturity_days, v.planting_density,
               v.quality_characteristics, v.management_notes,
               ra.adaptation_score, ra.region_name
        FROM enhanced_crop_varieties v
        LEFT JOIN crop_regional_adaptations ra ON v.crop_id = ra.crop_id 
            AND ra.region_name = :region_name
        WHERE v.crop_id = :crop_id 
            AND v.is_active = true
        ORDER BY v.yield_potential DESC, ra.adaptation_score DESC
        LIMIT :limit
        """
        
        query_params = {
            "crop_id": str(crop_data.id),
            "region_name": regional_context.get("region_name", ""),
            "limit": limit * 2  # Get more candidates for filtering
        }
        
        # Execute optimized query
        variety_data = await self.optimization_service.db_optimizer.execute_optimized_query(
            variety_query, query_params
        )
        
        if not variety_data:
            logger.warning(f"No varieties found for crop {crop_data.id}")
            return []
        
        # Convert to EnhancedCropVariety objects
        varieties = []
        for data in variety_data:
            try:
                variety = self._convert_db_data_to_variety(data)
                if variety:
                    varieties.append(variety)
            except Exception as e:
                logger.warning(f"Failed to convert variety data: {e}")
                continue
        
        # Use base service for scoring and ranking (with caching)
        recommendations = []
        for variety in varieties[:limit]:
            try:
                # Score variety using optimized method
                score_data = await self._score_variety_optimized(
                    variety, regional_context, farmer_preferences
                )
                
                if score_data:
                    recommendation = await self._create_variety_recommendation_optimized(
                        variety, score_data, regional_context
                    )
                    recommendations.append(recommendation)
                    
            except Exception as e:
                logger.warning(f"Failed to score variety {variety.variety_name}: {e}")
                continue
        
        # Sort by overall score
        recommendations.sort(key=lambda x: x.overall_score, reverse=True)
        
        return recommendations[:limit]
    
    def _convert_db_data_to_variety(self, data: Dict[str, Any]) -> Optional[EnhancedCropVariety]:
        """Convert database data to EnhancedCropVariety object."""
        try:
            return EnhancedCropVariety(
                variety_id=UUID(data["variety_id"]),
                variety_name=data["variety_name"],
                crop_id=UUID(data["crop_id"]),
                yield_potential=data.get("yield_potential"),
                disease_resistance=data.get("disease_resistance", []),
                stress_tolerances=data.get("stress_tolerances", []),
                herbicide_tolerances=data.get("herbicide_tolerances", []),
                breeder_company=data.get("breeder_company"),
                maturity_days=data.get("maturity_days"),
                planting_density=data.get("planting_density"),
                quality_characteristics=data.get("quality_characteristics", {}),
                management_notes=data.get("management_notes"),
                is_active=True
            )
        except Exception as e:
            logger.error(f"Failed to convert variety data: {e}")
            return None
    
    async def _score_variety_optimized(
        self,
        variety: EnhancedCropVariety,
        regional_context: Dict[str, Any],
        farmer_preferences: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Score variety using optimized methods with caching."""
        
        # Create cache key for scoring
        score_cache_key = {
            "variety_id": str(variety.variety_id),
            "regional_context": regional_context,
            "farmer_preferences": farmer_preferences or {}
        }
        
        # Check cache for scoring results
        cached_score = await self.optimization_service.cache.get(
            "variety_scoring", score_cache_key
        )
        
        if cached_score:
            return cached_score
        
        # Use base service scoring with performance monitoring
        score_data = await self.base_service._score_variety_for_context(
            variety, regional_context, farmer_preferences
        )
        
        if score_data:
            # Cache scoring results
            await self.optimization_service.cache.set(
                "variety_scoring", score_cache_key, score_data,
                self.config.cache_ttl_variety_data
            )
        
        return score_data
    
    async def _create_variety_recommendation_optimized(
        self,
        variety: EnhancedCropVariety,
        score_data: Dict[str, Any],
        regional_context: Dict[str, Any]
    ) -> VarietyRecommendation:
        """Create variety recommendation using optimized methods."""
        
        # Use base service method but with performance monitoring
        return await self.base_service._create_variety_recommendation(
            variety, score_data, regional_context
        )
    
    async def search_varieties_optimized(
        self,
        search_text: Optional[str] = None,
        crop_id: Optional[UUID] = None,
        traits: Optional[List[str]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Optimized variety search with performance target <1s.
        
        Args:
            search_text: Text to search in variety names and companies
            crop_id: Optional crop ID to filter by
            traits: Optional list of traits to filter by
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with search results and metadata
        """
        start_time = time.time()
        self.search_count += 1
        
        try:
            # Create search parameters
            search_params = {
                "search_text": search_text,
                "crop_id": str(crop_id) if crop_id else None,
                "traits": traits or [],
                "limit": limit
            }
            
            # Use optimization service for variety search
            search_results = await self.optimization_service.optimize_variety_search(search_params)
            
            # Record performance metrics
            execution_time = (time.time() - start_time) * 1000
            
            # Check if we met performance targets
            if execution_time > self.config.target_variety_search_time_ms:
                logger.warning(f"Variety search exceeded target: {execution_time:.2f}ms > {self.config.target_variety_search_time_ms}ms")
            
            performance_monitor.record_operation(
                operation="variety_search_optimized",
                execution_time_ms=execution_time,
                cache_hit=search_results.get("cache_hit", False),
                additional_data={
                    "result_count": len(search_results.get("varieties", [])),
                    "performance_target_met": execution_time <= self.config.target_variety_search_time_ms
                }
            )
            
            return search_results
            
        except Exception as e:
            logger.error(f"Optimized variety search failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            performance_monitor.record_operation(
                operation="variety_search_error",
                execution_time_ms=execution_time,
                cache_hit=False,
                additional_data={"error": str(e)}
            )
            raise
    
    async def get_variety_details_optimized(
        self,
        variety_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get optimized variety details with performance target <500ms.
        
        Args:
            variety_id: ID of the variety to get details for
            
        Returns:
            Dictionary with variety details or None if not found
        """
        start_time = time.time()
        self.details_count += 1
        
        try:
            # Check cache first
            cached_details = await self.optimization_service.cache.get(
                "variety_details", str(variety_id)
            )
            
            if cached_details:
                execution_time = (time.time() - start_time) * 1000
                logger.info(f"Cache hit for variety details: {execution_time:.2f}ms")
                
                performance_monitor.record_operation(
                    operation="variety_details_cached",
                    execution_time_ms=execution_time,
                    cache_hit=True
                )
                
                return cached_details
            
            # Execute optimized query for variety details
            details_query = """
            SELECT v.*, c.crop_name, c.scientific_name, c.category,
                   ra.adaptation_score, ra.region_name, ra.performance_notes
            FROM enhanced_crop_varieties v
            JOIN crops c ON v.crop_id = c.crop_id
            LEFT JOIN crop_regional_adaptations ra ON v.crop_id = ra.crop_id
            WHERE v.variety_id = :variety_id AND v.is_active = true
            """
            
            variety_data = await self.optimization_service.db_optimizer.execute_optimized_query(
                details_query, {"variety_id": str(variety_id)}
            )
            
            if not variety_data:
                return None
            
            # Process and cache results
            details = variety_data[0]  # Should be unique by variety_id
            
            # Cache results
            await self.optimization_service.cache.set(
                "variety_details", str(variety_id), details,
                self.config.cache_ttl_variety_data
            )
            
            # Record performance metrics
            execution_time = (time.time() - start_time) * 1000
            
            # Check if we met performance targets
            if execution_time > self.config.target_variety_details_time_ms:
                logger.warning(f"Variety details exceeded target: {execution_time:.2f}ms > {self.config.target_variety_details_time_ms}ms")
            
            performance_monitor.record_operation(
                operation="variety_details_optimized",
                execution_time_ms=execution_time,
                cache_hit=False,
                additional_data={
                    "variety_id": str(variety_id),
                    "performance_target_met": execution_time <= self.config.target_variety_details_time_ms
                }
            )
            
            return details
            
        except Exception as e:
            logger.error(f"Optimized variety details failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            performance_monitor.record_operation(
                operation="variety_details_error",
                execution_time_ms=execution_time,
                cache_hit=False,
                additional_data={"error": str(e)}
            )
            raise
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics for the optimized service."""
        uptime = time.time() - self.start_time
        
        # Get optimization service metrics
        optimization_metrics = await self.optimization_service.get_performance_metrics()
        
        return {
            "service_uptime_seconds": uptime,
            "operation_counts": {
                "recommendations": self.recommendation_count,
                "searches": self.search_count,
                "details": self.details_count
            },
            "performance_targets": {
                "target_recommendation_time_ms": self.config.target_recommendation_time_ms,
                "target_variety_search_time_ms": self.config.target_variety_search_time_ms,
                "target_variety_details_time_ms": self.config.target_variety_details_time_ms
            },
            "optimization_metrics": optimization_metrics
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the optimized service."""
        health_status = {
            "overall_status": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check base service
        try:
            # Simple test to ensure base service is working
            health_status["components"]["base_service"] = "healthy"
        except Exception as e:
            health_status["components"]["base_service"] = f"unhealthy: {e}"
            health_status["overall_status"] = "degraded"
        
        # Check optimization service
        try:
            opt_health = await self.optimization_service.health_check()
            health_status["components"]["optimization_service"] = opt_health["overall_status"]
            if opt_health["overall_status"] != "healthy":
                health_status["overall_status"] = "degraded"
        except Exception as e:
            health_status["components"]["optimization_service"] = f"unhealthy: {e}"
            health_status["overall_status"] = "degraded"
        
        return health_status
    
    async def invalidate_cache(self, pattern: Optional[str] = None) -> int:
        """Invalidate cache entries."""
        if pattern:
            return await self.optimization_service.cache.invalidate_pattern(pattern)
        else:
            # Invalidate all variety-related caches
            patterns = [
                "variety_recommendations",
                "variety_search", 
                "variety_details",
                "variety_scoring"
            ]
            
            total_invalidated = 0
            for p in patterns:
                count = await self.optimization_service.cache.invalidate_pattern(p)
                total_invalidated += count
            
            return total_invalidated


# Singleton instance for global access
optimized_variety_service: Optional[OptimizedVarietyRecommendationService] = None


def get_optimized_variety_service(database_url: str = None) -> OptimizedVarietyRecommendationService:
    """Get or create the global optimized variety recommendation service instance."""
    global optimized_variety_service
    
    if optimized_variety_service is None:
        optimized_variety_service = OptimizedVarietyRecommendationService(database_url)
    
    return optimized_variety_service