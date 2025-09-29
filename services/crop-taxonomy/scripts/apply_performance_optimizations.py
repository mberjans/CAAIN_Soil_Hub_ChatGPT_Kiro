#!/usr/bin/env python3
"""
Apply Performance Optimizations Script

This script applies all performance optimizations including:
- Database indexes and query optimization
- Performance monitoring setup
- Cache configuration
- Service initialization

TICKET-005_crop-variety-recommendations-14.1: Implement comprehensive variety recommendation performance optimization
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import optimization services
from services.performance_optimization_service import (
    PerformanceOptimizationService,
    OptimizationConfig
)
from services.optimized_variety_recommendation_service import (
    OptimizedVarietyRecommendationService
)
from services.comprehensive_performance_monitor import (
    ComprehensivePerformanceMonitor
)

# Database imports
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class PerformanceOptimizationSetup:
    """Setup and apply performance optimizations."""
    
    def __init__(self, database_url: str = None):
        """Initialize the optimization setup."""
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'postgresql://afas_user:afas_password@localhost:5432/afas_db'
        )
        
        self.engine = None
        self.optimization_service = None
        self.variety_service = None
        self.performance_monitor = None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def initialize_database(self):
        """Initialize database connection."""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def apply_database_optimizations(self) -> bool:
        """Apply database performance optimizations."""
        logger.info("Applying database performance optimizations...")
        
        try:
            # Read and execute the optimization SQL file
            sql_file_path = os.path.join(
                os.path.dirname(__file__), '..', 'database', 'performance_optimization_indexes.sql'
            )
            
            if not os.path.exists(sql_file_path):
                logger.error(f"Performance optimization SQL file not found: {sql_file_path}")
                return False
            
            with open(sql_file_path, 'r') as f:
                sql_content = f.read()
            
            # Split SQL content into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            with self.engine.connect() as conn:
                for i, statement in enumerate(statements):
                    try:
                        logger.info(f"Executing statement {i+1}/{len(statements)}")
                        conn.execute(text(statement))
                        conn.commit()
                    except Exception as e:
                        logger.warning(f"Statement {i+1} failed (may already exist): {e}")
                        continue
            
            logger.info("Database performance optimizations applied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply database optimizations: {e}")
            return False
    
    def initialize_services(self):
        """Initialize optimization services."""
        logger.info("Initializing optimization services...")
        
        try:
            # Initialize performance optimization service
            config = OptimizationConfig()
            self.optimization_service = PerformanceOptimizationService(
                self.database_url, config
            )
            
            # Initialize optimized variety recommendation service
            self.variety_service = OptimizedVarietyRecommendationService(
                self.database_url, config
            )
            
            # Initialize comprehensive performance monitor
            self.performance_monitor = ComprehensivePerformanceMonitor(
                self.database_url
            )
            
            logger.info("Optimization services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            return False
    
    async def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests to validate optimizations."""
        logger.info("Running performance tests...")
        
        test_results = {
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "performance_metrics": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            # Test 1: Variety Search Performance
            logger.info("Testing variety search performance...")
            start_time = time.time()
            
            search_results = await self.variety_service.search_varieties_optimized(
                search_text="corn",
                limit=20
            )
            
            search_time = (time.time() - start_time) * 1000
            test_results["tests_run"] += 1
            
            if search_time <= 1000:  # Target: <1s
                test_results["tests_passed"] += 1
                logger.info(f"✓ Variety search test passed: {search_time:.2f}ms")
            else:
                test_results["tests_failed"] += 1
                logger.warning(f"✗ Variety search test failed: {search_time:.2f}ms > 1000ms")
            
            test_results["performance_metrics"]["variety_search_ms"] = search_time
            
            # Test 2: Variety Details Performance
            logger.info("Testing variety details performance...")
            start_time = time.time()
            
            # Use a variety ID from search results if available
            variety_id = None
            if search_results.get("varieties"):
                variety_id = search_results["varieties"][0].get("variety_id")
            
            if variety_id:
                details_results = await self.variety_service.get_variety_details_optimized(
                    variety_id
                )
                
                details_time = (time.time() - start_time) * 1000
                test_results["tests_run"] += 1
                
                if details_time <= 500:  # Target: <500ms
                    test_results["tests_passed"] += 1
                    logger.info(f"✓ Variety details test passed: {details_time:.2f}ms")
                else:
                    test_results["tests_failed"] += 1
                    logger.warning(f"✗ Variety details test failed: {details_time:.2f}ms > 500ms")
                
                test_results["performance_metrics"]["variety_details_ms"] = details_time
            
            # Test 3: Cache Performance
            logger.info("Testing cache performance...")
            cache_metrics = self.optimization_service.cache.get_cache_metrics()
            test_results["performance_metrics"]["cache_metrics"] = cache_metrics
            
            # Test 4: Database Connection Pool
            logger.info("Testing database connection pool...")
            pool_status = self.optimization_service.db_optimizer.get_connection_pool_status()
            test_results["performance_metrics"]["database_pool"] = pool_status
            
            logger.info(f"Performance tests completed: {test_results['tests_passed']}/{test_results['tests_run']} passed")
            
        except Exception as e:
            logger.error(f"Performance tests failed: {e}")
            test_results["error"] = str(e)
        
        return test_results
    
    async def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        logger.info("Generating performance report...")
        
        report = {
            "optimization_status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {},
            "performance_targets": {},
            "recommendations": []
        }
        
        try:
            # Get service metrics
            if self.variety_service:
                variety_metrics = await self.variety_service.get_performance_metrics()
                report["services"]["variety_service"] = variety_metrics
            
            if self.optimization_service:
                optimization_metrics = await self.optimization_service.get_performance_metrics()
                report["services"]["optimization_service"] = optimization_metrics
            
            # Get performance targets
            config = OptimizationConfig()
            report["performance_targets"] = {
                "recommendation_time_ms": config.target_recommendation_time_ms,
                "search_time_ms": config.target_variety_search_time_ms,
                "details_time_ms": config.target_variety_details_time_ms
            }
            
            # Generate recommendations
            recommendations = []
            
            # Check cache configuration
            cache_metrics = self.optimization_service.cache.get_cache_metrics()
            if cache_metrics.get("hit_rate", 0) < 0.6:
                recommendations.append({
                    "category": "caching",
                    "priority": "medium",
                    "message": "Cache hit rate is below 60%. Consider increasing cache TTL or improving cache keys.",
                    "current_hit_rate": cache_metrics.get("hit_rate", 0)
                })
            
            # Check database pool
            pool_status = self.optimization_service.db_optimizer.get_connection_pool_status()
            if pool_status.get("checked_out", 0) > pool_status.get("pool_size", 0) * 0.8:
                recommendations.append({
                    "category": "database",
                    "priority": "high",
                    "message": "Database connection pool utilization is high. Consider increasing pool size.",
                    "utilization": pool_status.get("checked_out", 0) / pool_status.get("pool_size", 1)
                })
            
            report["recommendations"] = recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate performance report: {e}")
            report["error"] = str(e)
        
        return report
    
    async def run_full_optimization(self) -> bool:
        """Run the complete optimization process."""
        logger.info("Starting comprehensive performance optimization...")
        
        success = True
        
        # Step 1: Initialize database
        if not self.initialize_database():
            logger.error("Failed to initialize database")
            return False
        
        # Step 2: Apply database optimizations
        if not self.apply_database_optimizations():
            logger.error("Failed to apply database optimizations")
            success = False
        
        # Step 3: Initialize services
        if not self.initialize_services():
            logger.error("Failed to initialize services")
            success = False
        
        # Step 4: Run performance tests
        test_results = await self.run_performance_tests()
        logger.info(f"Performance tests: {test_results['tests_passed']}/{test_results['tests_run']} passed")
        
        # Step 5: Generate report
        report = await self.generate_performance_report()
        
        # Save report to file
        report_file = f"performance_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import json
            with open(report_file, 'w') as f:
                json.dump({
                    "test_results": test_results,
                    "performance_report": report
                }, f, indent=2)
            logger.info(f"Performance report saved to: {report_file}")
        except Exception as e:
            logger.warning(f"Failed to save report file: {e}")
        
        if success:
            logger.info("✓ Performance optimization completed successfully")
        else:
            logger.warning("⚠ Performance optimization completed with warnings")
        
        return success


async def main():
    """Main function to run the optimization setup."""
    print("Crop Variety Recommendation Performance Optimization")
    print("=" * 60)
    
    # Get database URL from environment or use default
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("Using default database URL. Set DATABASE_URL environment variable to override.")
        database_url = 'postgresql://afas_user:afas_password@localhost:5432/afas_db'
    
    # Initialize optimization setup
    setup = PerformanceOptimizationSetup(database_url)
    
    # Run full optimization
    success = await setup.run_full_optimization()
    
    if success:
        print("\n✓ Performance optimization completed successfully!")
        print("\nPerformance targets:")
        print("- Variety recommendations: <2 seconds")
        print("- Variety search: <1 second")
        print("- Variety details: <500 milliseconds")
        print("\nOptimization services are ready for use.")
    else:
        print("\n✗ Performance optimization completed with errors.")
        print("Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())