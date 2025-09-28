"""Database optimization utility for crop filtering system with specialized indexes and query optimization."""
import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import text
import sys
import os

# Add the databases directory to the Python path
sys.path.append('/Users/Mark/Research/CAAIN_Soil_Hub/CAAIN_Soil_Hub_ChatGPT_Kiro/databases/python')

from ..database.crop_taxonomy_db import CropTaxonomyDatabase

logger = logging.getLogger(__name__)

class DatabaseOptimizer:
    """Database optimization utility for crop filtering operations."""
    
    def __init__(self, db: CropTaxonomyDatabase):
        self.db = db

    def create_specialized_indexes(self):
        """Create specialized indexes for common filter combinations."""
        try:
            with self.db.get_session() as session:
                # Index for climate zone filtering (hardiness zones)
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_climate_adaptations_hardiness_zones 
                    ON crop_climate_adaptations USING GIN (hardiness_zones);
                """))
                
                # Index for soil pH range filtering
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_soil_requirements_ph_range 
                    ON crop_soil_requirements (optimal_ph_min, optimal_ph_max);
                """))
                
                # Index for temperature range filtering
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_climate_adaptations_temp_range 
                    ON crop_climate_adaptations (optimal_temp_min_f, optimal_temp_max_f);
                """))
                
                # Index for drought tolerance filtering
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_climate_adaptations_drought_tolerance 
                    ON crop_climate_adaptations (drought_tolerance);
                """))
                
                # Index for management complexity filtering
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_filtering_attributes_complexity 
                    ON crop_filtering_attributes (management_complexity);
                """))
                
                # Index for agricultural classification category
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_agricultural_classification_category 
                    ON crop_agricultural_classification (crop_category);
                """))
                
                # Composite index for common filtering combinations
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_crop_composite_filters 
                    ON crops (crop_status) 
                    INCLUDE (crop_name, scientific_name);
                """))
                
                # Index for search keywords
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_crops_search_keywords 
                    ON crops USING GIN (search_keywords);
                """))
                
                # Index for tags
                session.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_attribute_tags_normalized 
                    ON crop_attribute_tags (normalized_tag, tag_category);
                """))
                
                session.commit()
                logger.info("Successfully created specialized indexes for crop filtering optimization")
                
        except Exception as e:
            logger.error(f"Error creating specialized indexes: {e}")
            raise

    def create_materialized_views(self):
        """Create materialized views for common filtering scenarios."""
        try:
            with self.db.get_session() as session:
                # Materialized view for climate-adapted crops
                session.execute(text("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS climate_adapted_crops AS
                    SELECT 
                        c.crop_id,
                        c.crop_name,
                        c.scientific_name,
                        ca.hardiness_zones,
                        ca.optimal_temp_min_f,
                        ca.optimal_temp_max_f,
                        ca.drought_tolerance,
                        ca.frost_tolerance,
                        ac.crop_category,
                        sr.optimal_ph_min,
                        sr.optimal_ph_max
                    FROM crops c
                    JOIN crop_climate_adaptations ca ON c.crop_id = ca.crop_id
                    JOIN crop_agricultural_classification ac ON c.crop_id = ac.crop_id
                    JOIN crop_soil_requirements sr ON c.crop_id = sr.crop_id
                    WHERE c.crop_status = 'active';
                    
                    CREATE INDEX IF NOT EXISTS idx_climate_adapted_crops_hardiness 
                    ON climate_adapted_crops USING GIN (hardiness_zones);
                    
                    CREATE INDEX IF NOT EXISTS idx_climate_adapted_crops_temp_range 
                    ON climate_adapted_crops (optimal_temp_min_f, optimal_temp_max_f);
                """))
                
                # Materialized view for soil-compatible crops
                session.execute(text("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS soil_compatible_crops AS
                    SELECT 
                        c.crop_id,
                        c.crop_name,
                        c.scientific_name,
                        sr.optimal_ph_min,
                        sr.optimal_ph_max,
                        sr.preferred_textures,
                        sr.drainage_requirement,
                        sr.salinity_tolerance,
                        ac.crop_category,
                        ca.drought_tolerance
                    FROM crops c
                    JOIN crop_soil_requirements sr ON c.crop_id = sr.crop_id
                    JOIN crop_agricultural_classification ac ON c.crop_id = ac.crop_id
                    JOIN crop_climate_adaptations ca ON c.crop_id = ca.crop_id
                    WHERE c.crop_status = 'active';
                    
                    CREATE INDEX IF NOT EXISTS idx_soil_compatible_crops_ph_range 
                    ON soil_compatible_crops (optimal_ph_min, optimal_ph_max);
                    
                    CREATE INDEX IF NOT EXISTS idx_soil_compatible_crops_drainage 
                    ON soil_compatible_crops (drainage_requirement);
                """))
                
                # Materialized view for management-compatible crops
                session.execute(text("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS management_compatible_crops AS
                    SELECT 
                        c.crop_id,
                        c.crop_name,
                        c.scientific_name,
                        fa.management_complexity,
                        fa.input_requirements,
                        fa.labor_requirements,
                        fa.precision_ag_compatible,
                        ac.crop_category,
                        ac.primary_use,
                        ca.drought_tolerance
                    FROM crops c
                    JOIN crop_filtering_attributes fa ON c.crop_id = fa.crop_id
                    JOIN crop_agricultural_classification ac ON c.crop_id = ac.crop_id
                    JOIN crop_climate_adaptations ca ON c.crop_id = ca.crop_id
                    WHERE c.crop_status = 'active';
                    
                    CREATE INDEX IF NOT EXISTS idx_management_compatible_complexity 
                    ON management_compatible_crops (management_complexity);
                    
                    CREATE INDEX IF NOT EXISTS idx_management_compatible_inputs 
                    ON management_compatible_crops (input_requirements);
                """))
                
                session.commit()
                logger.info("Successfully created materialized views for crop filtering optimization")
                
        except Exception as e:
            logger.error(f"Error creating materialized views: {e}")
            raise

    def refresh_materialized_views(self):
        """Refresh materialized views with latest data."""
        try:
            with self.db.get_session() as session:
                session.execute(text("REFRESH MATERIALIZED VIEW climate_adapted_crops;"))
                session.execute(text("REFRESH MATERIALIZED VIEW soil_compatible_crops;"))
                session.execute(text("REFRESH MATERIALIZED VIEW management_compatible_crops;"))
                session.commit()
                logger.info("Successfully refreshed materialized views")
        except Exception as e:
            logger.error(f"Error refreshing materialized views: {e}")
            raise

    def create_query_optimization_functions(self):
        """Create database functions for optimized filtering."""
        try:
            with self.db.get_session() as session:
                # Function for efficient climate zone filtering
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION filter_by_climate_zones(
                        target_hardiness_zones TEXT[]
                    )
                    RETURNS TABLE (
                        crop_id UUID,
                        crop_name VARCHAR,
                        compatible_zones TEXT[],
                        match_score DECIMAL
                    ) AS $$
                    BEGIN
                        RETURN QUERY
                        SELECT 
                            ca.crop_id,
                            c.crop_name,
                            ca.hardiness_zones,
                            array_length(
                                ARRAY(SELECT UNNEST(ca.hardiness_zones) 
                                     INTERSECT 
                                     SELECT UNNEST(target_hardiness_zones)), 1
                            )::DECIMAL / 
                            array_length(ca.hardiness_zones, 1)::DECIMAL as match_score
                        FROM crop_climate_adaptations ca
                        JOIN crops c ON ca.crop_id = c.crop_id
                        WHERE ca.hardiness_zones && target_hardiness_zones
                        AND c.crop_status = 'active'
                        ORDER BY match_score DESC;
                    END;
                    $$ LANGUAGE plpgsql;
                """))
                
                # Function for efficient soil pH filtering
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION filter_by_soil_ph(
                        min_ph DECIMAL,
                        max_ph DECIMAL,
                        strict BOOLEAN DEFAULT FALSE
                    )
                    RETURNS TABLE (
                        crop_id UUID,
                        crop_name VARCHAR,
                        ph_min DECIMAL,
                        ph_max DECIMAL,
                        compatibility_score DECIMAL
                    ) AS $$
                    BEGIN
                        IF strict THEN
                            RETURN QUERY
                            SELECT 
                                sr.crop_id,
                                c.crop_name,
                                sr.optimal_ph_min,
                                sr.optimal_ph_max,
                                CASE 
                                    WHEN sr.optimal_ph_min >= min_ph AND sr.optimal_ph_max <= max_ph THEN 1.0
                                    WHEN sr.optimal_ph_min <= max_ph AND sr.optimal_ph_max >= min_ph THEN
                                        GREATEST(0, LEAST(sr.optimal_ph_max, max_ph) - GREATEST(sr.optimal_ph_min, min_ph)) / 
                                        (max_ph - min_ph)
                                    ELSE 0.0
                                END as compatibility_score
                            FROM crop_soil_requirements sr
                            JOIN crops c ON sr.crop_id = c.crop_id
                            WHERE (sr.optimal_ph_min <= max_ph AND sr.optimal_ph_max >= min_ph)
                            AND c.crop_status = 'active'
                            ORDER BY compatibility_score DESC;
                        ELSE
                            RETURN QUERY
                            SELECT 
                                sr.crop_id,
                                c.crop_name,
                                COALESCE(sr.tolerable_ph_min, sr.optimal_ph_min) as ph_min,
                                COALESCE(sr.tolerable_ph_max, sr.optimal_ph_max) as ph_max,
                                CASE 
                                    WHEN COALESCE(sr.tolerable_ph_min, sr.optimal_ph_min) >= min_ph 
                                         AND COALESCE(sr.tolerable_ph_max, sr.optimal_ph_max) <= max_ph THEN 1.0
                                    WHEN COALESCE(sr.tolerable_ph_min, sr.optimal_ph_min) <= max_ph 
                                         AND COALESCE(sr.tolerable_ph_max, sr.optimal_ph_max) >= min_ph THEN
                                        GREATEST(0, LEAST(COALESCE(sr.tolerable_ph_max, sr.optimal_ph_max), max_ph) - 
                                               GREATEST(COALESCE(sr.tolerable_ph_min, sr.optimal_ph_min), min_ph)) / 
                                        (max_ph - min_ph)
                                    ELSE 0.0
                                END as compatibility_score
                            FROM crop_soil_requirements sr
                            JOIN crops c ON sr.crop_id = c.crop_id
                            WHERE (COALESCE(sr.tolerable_ph_min, sr.optimal_ph_min) <= max_ph 
                                   AND COALESCE(sr.tolerable_ph_max, sr.optimal_ph_max) >= min_ph)
                            AND c.crop_status = 'active'
                            ORDER BY compatibility_score DESC;
                        END IF;
                    END;
                    $$ LANGUAGE plpgsql;
                """))
                
                # Function for complex multi-filter operations
                session.execute(text("""
                    CREATE OR REPLACE FUNCTION complex_crop_filter(
                        climate_zones TEXT[] DEFAULT NULL,
                        min_ph DECIMAL DEFAULT NULL,
                        max_ph DECIMAL DEFAULT NULL,
                        drought_tolerance TEXT DEFAULT NULL,
                        management_complexity TEXT DEFAULT NULL,
                        crop_categories TEXT[] DEFAULT NULL
                    )
                    RETURNS TABLE (
                        crop_id UUID,
                        crop_name VARCHAR,
                        overall_score DECIMAL,
                        climate_match DECIMAL,
                        soil_match DECIMAL,
                        management_match DECIMAL
                    ) AS $$
                    DECLARE
                        climate_matches TABLE (crop_id UUID, score DECIMAL);
                        soil_matches TABLE (crop_id UUID, score DECIMAL);
                        management_matches TABLE (crop_id UUID, score DECIMAL);
                        category_matches TABLE (crop_id UUID, score DECIMAL);
                    BEGIN
                        -- Get climate matches if provided
                        IF climate_zones IS NOT NULL AND array_length(climate_zones, 1) > 0 THEN
                            INSERT INTO climate_matches
                            SELECT crop_id, match_score
                            FROM filter_by_climate_zones(climate_zones);
                        END IF;
                        
                        -- Get soil matches if provided
                        IF min_ph IS NOT NULL AND max_ph IS NOT NULL THEN
                            INSERT INTO soil_matches
                            SELECT crop_id, compatibility_score as score
                            FROM filter_by_soil_ph(min_ph, max_ph, FALSE);
                        END IF;
                        
                        -- Get management matches if provided
                        IF management_complexity IS NOT NULL THEN
                            INSERT INTO management_matches
                            SELECT 
                                crop_id,
                                CASE WHEN management_complexity <= management_complexity THEN 1.0 ELSE 0.0 END as score
                            FROM crop_filtering_attributes
                            WHERE management_complexity IS NOT NULL;
                        END IF;
                        
                        -- Get category matches if provided
                        IF crop_categories IS NOT NULL AND array_length(crop_categories, 1) > 0 THEN
                            INSERT INTO category_matches
                            SELECT 
                                crop_id,
                                CASE WHEN crop_category = ANY(crop_categories) THEN 1.0 ELSE 0.0 END as score
                            FROM crop_agricultural_classification
                            WHERE crop_category IS NOT NULL;
                        END IF;
                        
                        -- Combine all matches with weighted scoring
                        RETURN QUERY
                        SELECT 
                            c.crop_id,
                            c.crop_name,
                            COALESCE(cm.score, 0) * 0.3 + 
                            COALESCE(sm.score, 0) * 0.3 + 
                            COALESCE(mgm.score, 0) * 0.2 + 
                            COALESCE(catm.score, 0) * 0.2 as overall_score,
                            COALESCE(cm.score, 0) as climate_match,
                            COALESCE(sm.score, 0) as soil_match,
                            COALESCE(mgm.score, 0) as management_match
                        FROM crops c
                        LEFT JOIN climate_matches cm ON c.crop_id = cm.crop_id
                        LEFT JOIN soil_matches sm ON c.crop_id = sm.crop_id
                        LEFT JOIN management_matches mgm ON c.crop_id = mgm.crop_id
                        LEFT JOIN category_matches catm ON c.crop_id = catm.crop_id
                        WHERE c.crop_status = 'active'
                        AND (
                            (climate_zones IS NULL OR cm.crop_id IS NOT NULL) AND
                            (min_ph IS NULL OR sm.crop_id IS NOT NULL) AND
                            (management_complexity IS NULL OR mgm.crop_id IS NOT NULL) AND
                            (crop_categories IS NULL OR catm.crop_id IS NOT NULL)
                        )
                        ORDER BY overall_score DESC;
                    END;
                    $$ LANGUAGE plpgsql;
                """))
                
                session.commit()
                logger.info("Successfully created optimized database functions")
                
        except Exception as e:
            logger.error(f"Error creating database optimization functions: {e}")
            raise

    def optimize_query_execution_plan(self):
        """Optimize database query execution plans."""
        try:
            with self.db.get_session() as session:
                # Analyze tables to update statistics
                session.execute(text("ANALYZE crop_climate_adaptations;"))
                session.execute(text("ANALYZE crop_soil_requirements;"))
                session.execute(text("ANALYZE crop_agricultural_classification;"))
                session.execute(text("ANALYZE crop_filtering_attributes;"))
                session.execute(text("ANALYZE crops;"))
                session.execute(text("ANALYZE crop_attribute_tags;"))
                
                # Set query planner parameters for better performance
                session.execute(text("SET work_mem = '64MB';"))
                session.execute(text("SET effective_cache_size = '1GB';"))
                session.execute(text("SET random_page_cost = 1.1;"))  # SSD-optimized
                
                session.commit()
                logger.info("Successfully optimized query execution plans")
                
        except Exception as e:
            logger.error(f"Error optimizing query execution plans: {e}")
            raise

    def run_all_optimizations(self):
        """Run all database optimizations."""
        logger.info("Starting comprehensive database optimization for crop filtering system")
        self.create_specialized_indexes()
        self.create_materialized_views()
        self.create_query_optimization_functions()
        self.optimize_query_execution_plan()
        logger.info("Completed comprehensive database optimization for crop filtering system")