"""
Database operations for Expert Validation System

This module handles all database operations for the agricultural expert validation
and field testing system for drought management recommendations.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
import json
import asyncpg
from decimal import Decimal

from .drought_db import DroughtManagementDB
from ..models.expert_validation_models import (
    ExpertProfile, ValidationRequest, ExpertReview, FieldTestResult, ValidationMetrics
)

logger = logging.getLogger(__name__)


class ExpertValidationDB(DroughtManagementDB):
    """Database operations for expert validation system."""
    
    async def create_expert_validation_tables(self):
        """Create database tables for expert validation system."""
        try:
            async with self.pool.acquire() as conn:
                # Expert profiles table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS expert_profiles (
                        expert_id UUID PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        credentials TEXT NOT NULL,
                        expertise_areas TEXT[] NOT NULL,
                        regions TEXT[] NOT NULL,
                        years_experience INTEGER NOT NULL,
                        certifications TEXT[] NOT NULL,
                        contact_info JSONB NOT NULL,
                        availability_status VARCHAR(50) DEFAULT 'available',
                        review_count INTEGER DEFAULT 0,
                        approval_rate DECIMAL(5,4) DEFAULT 0.0,
                        average_review_time_hours DECIMAL(8,2) DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT NOW(),
                        last_active TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Validation requests table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS validation_requests (
                        validation_id UUID PRIMARY KEY,
                        recommendation_id UUID NOT NULL,
                        farm_location JSONB NOT NULL,
                        field_conditions JSONB NOT NULL,
                        drought_assessment JSONB NOT NULL,
                        conservation_recommendations JSONB NOT NULL,
                        water_savings_estimates JSONB NOT NULL,
                        validation_criteria TEXT[] NOT NULL,
                        priority_level VARCHAR(50) NOT NULL,
                        requested_expert_types TEXT[] NOT NULL,
                        assigned_experts UUID[] DEFAULT '{}',
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT NOW(),
                        deadline TIMESTAMP NOT NULL,
                        completed_at TIMESTAMP
                    )
                """)
                
                # Expert reviews table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS expert_reviews (
                        review_id UUID PRIMARY KEY,
                        validation_id UUID NOT NULL REFERENCES validation_requests(validation_id),
                        expert_id UUID NOT NULL REFERENCES expert_profiles(expert_id),
                        expert_type VARCHAR(50) NOT NULL,
                        review_status VARCHAR(50) NOT NULL,
                        criteria_scores JSONB NOT NULL,
                        overall_score DECIMAL(5,4) NOT NULL,
                        comments TEXT NOT NULL,
                        recommendations TEXT[] NOT NULL,
                        concerns TEXT[] NOT NULL,
                        approval_status BOOLEAN NOT NULL,
                        review_time_hours DECIMAL(8,2) NOT NULL,
                        submitted_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Field tests table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS field_tests (
                        test_id UUID PRIMARY KEY,
                        farm_id UUID NOT NULL,
                        field_id UUID NOT NULL,
                        practice_implemented VARCHAR(200) NOT NULL,
                        implementation_date TIMESTAMP NOT NULL,
                        baseline_conditions JSONB NOT NULL,
                        monitoring_data JSONB DEFAULT '{}',
                        outcome_metrics JSONB DEFAULT '{}',
                        farmer_feedback JSONB DEFAULT '{}',
                        expert_observations TEXT[] DEFAULT '{}',
                        effectiveness_score DECIMAL(5,4) DEFAULT 0.0,
                        farmer_satisfaction_score DECIMAL(5,4) DEFAULT 0.0,
                        test_duration_days INTEGER NOT NULL,
                        status VARCHAR(50) DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT NOW(),
                        completed_at TIMESTAMP
                    )
                """)
                
                # Validation metrics table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS validation_metrics (
                        id SERIAL PRIMARY KEY,
                        total_validations INTEGER DEFAULT 0,
                        expert_approval_rate DECIMAL(5,4) DEFAULT 0.0,
                        recommendation_accuracy DECIMAL(5,4) DEFAULT 0.0,
                        farmer_satisfaction DECIMAL(5,4) DEFAULT 0.0,
                        average_review_time_hours DECIMAL(8,2) DEFAULT 0.0,
                        field_test_success_rate DECIMAL(5,4) DEFAULT 0.0,
                        expert_panel_size INTEGER DEFAULT 0,
                        active_field_tests INTEGER DEFAULT 0,
                        validation_period_days INTEGER DEFAULT 30,
                        calculated_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                
                # Create indexes for performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expert_profiles_availability 
                    ON expert_profiles(availability_status)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expert_profiles_expertise 
                    ON expert_profiles USING GIN(expertise_areas)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expert_profiles_regions 
                    ON expert_profiles USING GIN(regions)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_validation_requests_status 
                    ON validation_requests(status)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_validation_requests_deadline 
                    ON validation_requests(deadline)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expert_reviews_validation_id 
                    ON expert_reviews(validation_id)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_expert_reviews_expert_id 
                    ON expert_reviews(expert_id)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_field_tests_status 
                    ON field_tests(status)
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_field_tests_farm_id 
                    ON field_tests(farm_id)
                """)
                
                logger.info("Expert validation database tables created successfully")
                
        except Exception as e:
            logger.error(f"Failed to create expert validation tables: {e}")
            raise
    
    async def get_expert_panel(self) -> List[Dict[str, Any]]:
        """Get all expert profiles."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT expert_id, name, credentials, expertise_areas, regions,
                           years_experience, certifications, contact_info,
                           availability_status, review_count, approval_rate,
                           average_review_time_hours, created_at, last_active
                    FROM expert_profiles
                    ORDER BY approval_rate DESC, years_experience DESC
                """)
                
                experts = []
                for row in rows:
                    expert = {
                        'expert_id': row['expert_id'],
                        'name': row['name'],
                        'credentials': row['credentials'],
                        'expertise_areas': row['expertise_areas'],
                        'regions': row['regions'],
                        'years_experience': row['years_experience'],
                        'certifications': row['certifications'],
                        'contact_info': row['contact_info'],
                        'availability_status': row['availability_status'],
                        'review_count': row['review_count'],
                        'approval_rate': float(row['approval_rate']),
                        'average_review_time_hours': float(row['average_review_time_hours']),
                        'created_at': row['created_at'],
                        'last_active': row['last_active']
                    }
                    experts.append(expert)
                
                return experts
                
        except Exception as e:
            logger.error(f"Failed to get expert panel: {e}")
            raise
    
    async def get_active_field_tests(self) -> List[Dict[str, Any]]:
        """Get all active field tests."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT test_id, farm_id, field_id, practice_implemented,
                           implementation_date, baseline_conditions, monitoring_data,
                           outcome_metrics, farmer_feedback, expert_observations,
                           effectiveness_score, farmer_satisfaction_score,
                           test_duration_days, completed_at
                    FROM field_tests
                    WHERE status = 'active'
                    ORDER BY implementation_date DESC
                """)
                
                field_tests = []
                for row in rows:
                    field_test = {
                        'test_id': row['test_id'],
                        'farm_id': row['farm_id'],
                        'field_id': row['field_id'],
                        'practice_implemented': row['practice_implemented'],
                        'implementation_date': row['implementation_date'],
                        'baseline_conditions': row['baseline_conditions'],
                        'monitoring_data': row['monitoring_data'],
                        'outcome_metrics': row['outcome_metrics'],
                        'farmer_feedback': row['farmer_feedback'],
                        'expert_observations': row['expert_observations'],
                        'effectiveness_score': float(row['effectiveness_score']),
                        'farmer_satisfaction_score': float(row['farmer_satisfaction_score']),
                        'test_duration_days': row['test_duration_days'],
                        'completed_at': row['completed_at']
                    }
                    field_tests.append(field_test)
                
                return field_tests
                
        except Exception as e:
            logger.error(f"Failed to get active field tests: {e}")
            raise
    
    async def get_validation_metrics(self) -> Dict[str, Any]:
        """Get current validation metrics."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT total_validations, expert_approval_rate, recommendation_accuracy,
                           farmer_satisfaction, average_review_time_hours, field_test_success_rate,
                           expert_panel_size, active_field_tests, validation_period_days
                    FROM validation_metrics
                    ORDER BY calculated_at DESC
                    LIMIT 1
                """)
                
                if row:
                    return {
                        'total_validations': row['total_validations'],
                        'expert_approval_rate': float(row['expert_approval_rate']),
                        'recommendation_accuracy': float(row['recommendation_accuracy']),
                        'farmer_satisfaction': float(row['farmer_satisfaction']),
                        'average_review_time_hours': float(row['average_review_time_hours']),
                        'field_test_success_rate': float(row['field_test_success_rate']),
                        'expert_panel_size': row['expert_panel_size'],
                        'active_field_tests': row['active_field_tests'],
                        'validation_period_days': row['validation_period_days']
                    }
                else:
                    return {
                        'total_validations': 0,
                        'expert_approval_rate': 0.0,
                        'recommendation_accuracy': 0.0,
                        'farmer_satisfaction': 0.0,
                        'average_review_time_hours': 0.0,
                        'field_test_success_rate': 0.0,
                        'expert_panel_size': 0,
                        'active_field_tests': 0,
                        'validation_period_days': 30
                    }
                
        except Exception as e:
            logger.error(f"Failed to get validation metrics: {e}")
            raise
    
    async def save_validation_request(self, validation_request: ValidationRequest):
        """Save validation request to database."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO validation_requests (
                        validation_id, recommendation_id, farm_location, field_conditions,
                        drought_assessment, conservation_recommendations, water_savings_estimates,
                        validation_criteria, priority_level, requested_expert_types, deadline
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """, 
                validation_request.validation_id,
                validation_request.recommendation_id,
                json.dumps(validation_request.farm_location),
                json.dumps(validation_request.field_conditions),
                json.dumps(validation_request.drought_assessment.dict()),
                json.dumps([rec.dict() for rec in validation_request.conservation_recommendations]),
                json.dumps([est.dict() for est in validation_request.water_savings_estimates]),
                [criteria.value for criteria in validation_request.validation_criteria],
                validation_request.priority_level,
                [expert_type.value for expert_type in validation_request.requested_expert_types],
                validation_request.deadline
                )
                
        except Exception as e:
            logger.error(f"Failed to save validation request: {e}")
            raise
    
    async def assign_experts_to_validation(self, validation_id: UUID, expert_ids: List[UUID]):
        """Assign experts to validation request."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE validation_requests 
                    SET assigned_experts = $1, status = 'in_review'
                    WHERE validation_id = $2
                """, expert_ids, validation_id)
                
                # Update expert availability status
                for expert_id in expert_ids:
                    await conn.execute("""
                        UPDATE expert_profiles 
                        SET availability_status = 'assigned'
                        WHERE expert_id = $1
                    """, expert_id)
                
        except Exception as e:
            logger.error(f"Failed to assign experts to validation: {e}")
            raise
    
    async def save_expert_review(self, expert_review: ExpertReview):
        """Save expert review to database."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO expert_reviews (
                        review_id, validation_id, expert_id, expert_type, review_status,
                        criteria_scores, overall_score, comments, recommendations,
                        concerns, approval_status, review_time_hours
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                """,
                expert_review.review_id,
                expert_review.validation_id,
                expert_review.expert_id,
                expert_review.expert_type.value,
                expert_review.review_status.value,
                json.dumps({criteria.value: score for criteria, score in expert_review.criteria_scores.items()}),
                expert_review.overall_score,
                expert_review.comments,
                expert_review.recommendations,
                expert_review.concerns,
                expert_review.approval_status,
                expert_review.review_time_hours
                )
                
                # Update expert profile
                await conn.execute("""
                    UPDATE expert_profiles 
                    SET availability_status = 'available', last_active = NOW(),
                        review_count = review_count + 1
                    WHERE expert_id = $1
                """, expert_review.expert_id)
                
        except Exception as e:
            logger.error(f"Failed to save expert review: {e}")
            raise
    
    async def save_field_test(self, field_test: FieldTestResult):
        """Save field test to database."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO field_tests (
                        test_id, farm_id, field_id, practice_implemented,
                        implementation_date, baseline_conditions, test_duration_days,
                        completed_at
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                field_test.test_id,
                field_test.farm_id,
                field_test.field_id,
                field_test.practice_implemented,
                field_test.implementation_date,
                json.dumps(field_test.baseline_conditions),
                field_test.test_duration_days,
                field_test.completed_at
                )
                
        except Exception as e:
            logger.error(f"Failed to save field test: {e}")
            raise
    
    async def update_field_test_monitoring(
        self, 
        test_id: UUID, 
        monitoring_data: Dict[str, Any], 
        expert_observations: List[str]
    ):
        """Update field test monitoring data."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE field_tests 
                    SET monitoring_data = $1, expert_observations = $2
                    WHERE test_id = $3
                """, 
                json.dumps(monitoring_data), 
                expert_observations, 
                test_id
                )
                
        except Exception as e:
            logger.error(f"Failed to update field test monitoring: {e}")
            raise
    
    async def complete_field_test(self, field_test: FieldTestResult):
        """Complete field test with final results."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    UPDATE field_tests 
                    SET outcome_metrics = $1, farmer_feedback = $2, expert_observations = $3,
                        effectiveness_score = $4, farmer_satisfaction_score = $5,
                        status = 'completed', completed_at = $6
                    WHERE test_id = $7
                """,
                json.dumps(field_test.outcome_metrics),
                json.dumps(field_test.farmer_feedback),
                field_test.expert_observations,
                field_test.effectiveness_score,
                field_test.farmer_satisfaction_score,
                field_test.completed_at,
                field_test.test_id
                )
                
        except Exception as e:
            logger.error(f"Failed to complete field test: {e}")
            raise
    
    async def save_validation_metrics(self, metrics: ValidationMetrics):
        """Save validation metrics to database."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO validation_metrics (
                        total_validations, expert_approval_rate, recommendation_accuracy,
                        farmer_satisfaction, average_review_time_hours, field_test_success_rate,
                        expert_panel_size, active_field_tests, validation_period_days
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                metrics.total_validations,
                metrics.expert_approval_rate,
                metrics.recommendation_accuracy,
                metrics.farmer_satisfaction,
                metrics.average_review_time_hours,
                metrics.field_test_success_rate,
                metrics.expert_panel_size,
                metrics.active_field_tests,
                metrics.validation_period_days
                )
                
        except Exception as e:
            logger.error(f"Failed to save validation metrics: {e}")
            raise
    
    async def get_validation_request(self, validation_id: UUID) -> Dict[str, Any]:
        """Get validation request by ID."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT validation_id, recommendation_id, farm_location, field_conditions,
                           drought_assessment, conservation_recommendations, water_savings_estimates,
                           validation_criteria, priority_level, requested_expert_types,
                           assigned_experts, status, created_at, deadline, completed_at
                    FROM validation_requests
                    WHERE validation_id = $1
                """, validation_id)
                
                if row:
                    return {
                        'validation_id': row['validation_id'],
                        'recommendation_id': row['recommendation_id'],
                        'farm_location': row['farm_location'],
                        'field_conditions': row['field_conditions'],
                        'drought_assessment': row['drought_assessment'],
                        'conservation_recommendations': row['conservation_recommendations'],
                        'water_savings_estimates': row['water_savings_estimates'],
                        'validation_criteria': row['validation_criteria'],
                        'priority_level': row['priority_level'],
                        'requested_expert_types': row['requested_expert_types'],
                        'assigned_experts': row['assigned_experts'],
                        'status': row['status'],
                        'created_at': row['created_at'],
                        'deadline': row['deadline'],
                        'completed_at': row['completed_at']
                    }
                else:
                    return {}
                
        except Exception as e:
            logger.error(f"Failed to get validation request: {e}")
            raise
    
    async def get_validation_reviews(self, validation_id: UUID) -> List[Dict[str, Any]]:
        """Get all reviews for a validation request."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT review_id, expert_id, expert_type, review_status, criteria_scores,
                           overall_score, comments, recommendations, concerns, approval_status,
                           review_time_hours, submitted_at
                    FROM expert_reviews
                    WHERE validation_id = $1
                    ORDER BY submitted_at DESC
                """, validation_id)
                
                reviews = []
                for row in rows:
                    review = {
                        'review_id': row['review_id'],
                        'expert_id': row['expert_id'],
                        'expert_type': row['expert_type'],
                        'review_status': row['review_status'],
                        'criteria_scores': row['criteria_scores'],
                        'overall_score': float(row['overall_score']),
                        'comments': row['comments'],
                        'recommendations': row['recommendations'],
                        'concerns': row['concerns'],
                        'approval_status': row['approval_status'],
                        'review_time_hours': float(row['review_time_hours']),
                        'submitted_at': row['submitted_at']
                    }
                    reviews.append(review)
                
                return reviews
                
        except Exception as e:
            logger.error(f"Failed to get validation reviews: {e}")
            raise
    
    async def get_recent_reviews(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get recent expert reviews."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT review_id, expert_id, expert_type, approval_status, overall_score,
                           review_time_hours, submitted_at
                    FROM expert_reviews
                    WHERE submitted_at >= NOW() - INTERVAL '%s days'
                    ORDER BY submitted_at DESC
                """, days)
                
                reviews = []
                for row in rows:
                    review = {
                        'review_id': row['review_id'],
                        'expert_id': row['expert_id'],
                        'expert_type': row['expert_type'],
                        'approval_status': row['approval_status'],
                        'overall_score': float(row['overall_score']),
                        'review_time_hours': float(row['review_time_hours']),
                        'submitted_at': row['submitted_at']
                    }
                    reviews.append(review)
                
                return reviews
                
        except Exception as e:
            logger.error(f"Failed to get recent reviews: {e}")
            raise
    
    async def get_completed_field_tests(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get completed field tests."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT test_id, farm_id, field_id, practice_implemented,
                           effectiveness_score, farmer_satisfaction_score, completed_at
                    FROM field_tests
                    WHERE status = 'completed' 
                    AND completed_at >= NOW() - INTERVAL '%s days'
                    ORDER BY completed_at DESC
                """, days)
                
                field_tests = []
                for row in rows:
                    field_test = {
                        'test_id': row['test_id'],
                        'farm_id': row['farm_id'],
                        'field_id': row['field_id'],
                        'practice_implemented': row['practice_implemented'],
                        'effectiveness_score': float(row['effectiveness_score']),
                        'farmer_satisfaction_score': float(row['farmer_satisfaction_score']),
                        'completed_at': row['completed_at']
                    }
                    field_tests.append(field_test)
                
                return field_tests
                
        except Exception as e:
            logger.error(f"Failed to get completed field tests: {e}")
            raise
    
    async def initialize_expert_panel(self):
        """Initialize expert panel with sample data."""
        try:
            async with self.pool.acquire() as conn:
                # Check if expert panel already exists
                count = await conn.fetchval("SELECT COUNT(*) FROM expert_profiles")
                if count > 0:
                    logger.info("Expert panel already initialized")
                    return
                
                # Sample expert data
                experts_data = [
                    {
                        'expert_id': '550e8400-e29b-41d4-a716-446655440001',
                        'name': 'Dr. Sarah Johnson',
                        'credentials': 'PhD in Soil Science, Certified Crop Advisor',
                        'expertise_areas': ['drought_specialist', 'soil_scientist'],
                        'regions': ['IA', 'NE', 'KS', 'MO'],
                        'years_experience': 15,
                        'certifications': ['CCA', 'CPSS'],
                        'contact_info': {'email': 'sarah.johnson@university.edu', 'phone': '555-0101'},
                        'approval_rate': 0.95,
                        'average_review_time_hours': 4.5
                    },
                    {
                        'expert_id': '550e8400-e29b-41d4-a716-446655440002',
                        'name': 'Mike Rodriguez',
                        'credentials': 'MS in Agricultural Engineering, Extension Agent',
                        'expertise_areas': ['extension_agent', 'irrigation_specialist'],
                        'regions': ['TX', 'OK', 'NM'],
                        'years_experience': 12,
                        'certifications': ['CCA'],
                        'contact_info': {'email': 'mike.rodriguez@extension.edu', 'phone': '555-0102'},
                        'approval_rate': 0.92,
                        'average_review_time_hours': 3.8
                    },
                    {
                        'expert_id': '550e8400-e29b-41d4-a716-446655440003',
                        'name': 'Dr. Jennifer Chen',
                        'credentials': 'PhD in Crop Science, Conservation Professional',
                        'expertise_areas': ['conservation_professional', 'crop_specialist'],
                        'regions': ['CA', 'OR', 'WA'],
                        'years_experience': 18,
                        'certifications': ['CCA', 'CPSS'],
                        'contact_info': {'email': 'jennifer.chen@conservation.org', 'phone': '555-0103'},
                        'approval_rate': 0.97,
                        'average_review_time_hours': 5.2
                    },
                    {
                        'expert_id': '550e8400-e29b-41d4-a716-446655440004',
                        'name': 'Robert Thompson',
                        'credentials': 'MS in Water Resources, Irrigation Specialist',
                        'expertise_areas': ['irrigation_specialist', 'drought_specialist'],
                        'regions': ['CO', 'UT', 'AZ', 'NV'],
                        'years_experience': 10,
                        'certifications': ['CCA'],
                        'contact_info': {'email': 'robert.thompson@water.org', 'phone': '555-0104'},
                        'approval_rate': 0.89,
                        'average_review_time_hours': 3.2
                    },
                    {
                        'expert_id': '550e8400-e29b-41d4-a716-446655440005',
                        'name': 'Dr. Maria Garcia',
                        'credentials': 'PhD in Agricultural Economics, Extension Specialist',
                        'expertise_areas': ['extension_agent', 'crop_specialist'],
                        'regions': ['FL', 'GA', 'AL', 'SC'],
                        'years_experience': 14,
                        'certifications': ['CCA'],
                        'contact_info': {'email': 'maria.garcia@extension.edu', 'phone': '555-0105'},
                        'approval_rate': 0.94,
                        'average_review_time_hours': 4.1
                    }
                ]
                
                for expert_data in experts_data:
                    await conn.execute("""
                        INSERT INTO expert_profiles (
                            expert_id, name, credentials, expertise_areas, regions,
                            years_experience, certifications, contact_info, approval_rate,
                            average_review_time_hours
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    """,
                    expert_data['expert_id'],
                    expert_data['name'],
                    expert_data['credentials'],
                    expert_data['expertise_areas'],
                    expert_data['regions'],
                    expert_data['years_experience'],
                    expert_data['certifications'],
                    json.dumps(expert_data['contact_info']),
                    expert_data['approval_rate'],
                    expert_data['average_review_time_hours']
                    )
                
                logger.info(f"Initialized expert panel with {len(experts_data)} experts")
                
        except Exception as e:
            logger.error(f"Failed to initialize expert panel: {e}")
            raise