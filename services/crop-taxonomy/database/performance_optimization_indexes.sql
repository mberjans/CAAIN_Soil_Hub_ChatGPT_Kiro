-- Performance Optimization Database Indexes
-- TICKET-005_crop-variety-recommendations-14.1: Implement comprehensive variety recommendation performance optimization

-- ============================================================================
-- CROP VARIETY PERFORMANCE INDEXES
-- ============================================================================

-- Index for variety search by crop_id (most common query)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_crop_id_active 
ON enhanced_crop_varieties (crop_id, is_active) 
WHERE is_active = true;

-- Index for variety name search (text search optimization)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_name_search 
ON enhanced_crop_varieties USING gin (to_tsvector('english', variety_name));

-- Index for breeder company search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_breeder_search 
ON enhanced_crop_varieties USING gin (to_tsvector('english', breeder_company));

-- Index for yield potential sorting (common in recommendations)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_yield_potential 
ON enhanced_crop_varieties (yield_potential DESC) 
WHERE is_active = true;

-- Index for maturity days filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_maturity_days 
ON enhanced_crop_varieties (maturity_days) 
WHERE is_active = true;

-- Index for stress tolerances (array search optimization)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_stress_tolerances 
ON enhanced_crop_varieties USING gin (stress_tolerances);

-- Index for herbicide tolerances (array search optimization)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_herbicide_tolerances 
ON enhanced_crop_varieties USING gin (herbicide_tolerances);

-- Index for disease resistance (array search optimization)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_disease_resistance 
ON enhanced_crop_varieties USING gin (disease_resistance);

-- Composite index for common variety filtering combinations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_varieties_composite_filter 
ON enhanced_crop_varieties (crop_id, yield_potential DESC, maturity_days) 
WHERE is_active = true;

-- ============================================================================
-- CROP PERFORMANCE INDEXES
-- ============================================================================

-- Index for crop name search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crops_name_search 
ON crops USING gin (to_tsvector('english', crop_name));

-- Index for scientific name search
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crops_scientific_name_search 
ON crops USING gin (to_tsvector('english', scientific_name));

-- Index for crop status filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crops_status 
ON crops (crop_status) 
WHERE crop_status = 'active';

-- Index for crop category filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crops_category 
ON crops (category) 
WHERE crop_status = 'active';

-- Index for search keywords (array search optimization)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_crops_search_keywords 
ON crops USING gin (search_keywords);

-- ============================================================================
-- REGIONAL ADAPTATION PERFORMANCE INDEXES
-- ============================================================================

-- Index for regional adaptation lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_regional_adaptations_crop_region 
ON crop_regional_adaptations (crop_id, region_name);

-- Index for adaptation score filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_regional_adaptations_score 
ON crop_regional_adaptations (adaptation_score DESC);

-- Composite index for regional adaptation queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_regional_adaptations_composite 
ON crop_regional_adaptations (crop_id, region_name, adaptation_score DESC);

-- ============================================================================
-- RECOMMENDATION MANAGEMENT INDEXES
-- ============================================================================

-- Index for user recommendations lookup
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_saved_recommendations_user_id 
ON saved_variety_recommendations (user_id, created_at DESC);

-- Index for recommendation status filtering
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_saved_recommendations_status 
ON saved_variety_recommendations (status, created_at DESC);

-- Index for session-based recommendations
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_saved_recommendations_session 
ON saved_variety_recommendations (session_id, created_at DESC);

-- ============================================================================
-- PERFORMANCE MONITORING INDEXES
-- ============================================================================

-- Index for performance metrics by operation
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_operation 
ON performance_metrics (operation, timestamp DESC);

-- Index for slow query tracking
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_performance_metrics_slow_queries 
ON performance_metrics (execution_time_ms DESC, timestamp DESC) 
WHERE execution_time_ms > 1000;

-- ============================================================================
-- CACHE OPTIMIZATION INDEXES
-- ============================================================================

-- Index for cache entry expiration
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cache_expiration 
ON cache_entries (expires_at) 
WHERE expires_at < NOW();

-- Index for cache namespace lookups
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cache_namespace 
ON cache_entries (namespace, cache_key);

-- ============================================================================
-- QUERY OPTIMIZATION STATISTICS
-- ============================================================================

-- Update table statistics for better query planning
ANALYZE enhanced_crop_varieties;
ANALYZE crops;
ANALYZE crop_regional_adaptations;
ANALYZE saved_variety_recommendations;
ANALYZE performance_metrics;
ANALYZE cache_entries;

-- ============================================================================
-- PERFORMANCE MONITORING VIEWS
-- ============================================================================

-- View for variety performance metrics
CREATE OR REPLACE VIEW variety_performance_summary AS
SELECT 
    c.crop_name,
    COUNT(v.variety_id) as variety_count,
    AVG(v.yield_potential) as avg_yield_potential,
    MAX(v.yield_potential) as max_yield_potential,
    MIN(v.yield_potential) as min_yield_potential,
    AVG(v.maturity_days) as avg_maturity_days
FROM crops c
LEFT JOIN enhanced_crop_varieties v ON c.crop_id = v.crop_id AND v.is_active = true
WHERE c.crop_status = 'active'
GROUP BY c.crop_id, c.crop_name
ORDER BY variety_count DESC;

-- View for recommendation performance metrics
CREATE OR REPLACE VIEW recommendation_performance_summary AS
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as total_recommendations,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_recommendations,
    COUNT(CASE WHEN status = 'archived' THEN 1 END) as archived_recommendations,
    AVG(EXTRACT(EPOCH FROM (expires_at - created_at))/3600) as avg_lifetime_hours
FROM saved_variety_recommendations
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC;

-- ============================================================================
-- PERFORMANCE OPTIMIZATION FUNCTIONS
-- ============================================================================

-- Function to get variety search suggestions with performance optimization
CREATE OR REPLACE FUNCTION get_variety_search_suggestions(
    search_text TEXT,
    crop_id_param UUID DEFAULT NULL,
    limit_param INTEGER DEFAULT 10
)
RETURNS TABLE (
    variety_id UUID,
    variety_name TEXT,
    breeder_company TEXT,
    yield_potential DECIMAL,
    maturity_days INTEGER,
    relevance_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.variety_id,
        v.variety_name,
        v.breeder_company,
        v.yield_potential,
        v.maturity_days,
        ts_rank(
            to_tsvector('english', v.variety_name || ' ' || COALESCE(v.breeder_company, '')),
            plainto_tsquery('english', search_text)
        ) as relevance_score
    FROM enhanced_crop_varieties v
    WHERE v.is_active = true
        AND (crop_id_param IS NULL OR v.crop_id = crop_id_param)
        AND (
            v.variety_name ILIKE '%' || search_text || '%'
            OR v.breeder_company ILIKE '%' || search_text || '%'
            OR to_tsvector('english', v.variety_name || ' ' || COALESCE(v.breeder_company, '')) 
               @@ plainto_tsquery('english', search_text)
        )
    ORDER BY relevance_score DESC, v.yield_potential DESC
    LIMIT limit_param;
END;
$$ LANGUAGE plpgsql;

-- Function to get optimized variety recommendations
CREATE OR REPLACE FUNCTION get_optimized_variety_recommendations(
    crop_id_param UUID,
    region_name_param TEXT DEFAULT NULL,
    min_yield_potential DECIMAL DEFAULT NULL,
    max_maturity_days INTEGER DEFAULT NULL,
    limit_param INTEGER DEFAULT 20
)
RETURNS TABLE (
    variety_id UUID,
    variety_name TEXT,
    breeder_company TEXT,
    yield_potential DECIMAL,
    maturity_days INTEGER,
    adaptation_score INTEGER,
    recommendation_score REAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.variety_id,
        v.variety_name,
        v.breeder_company,
        v.yield_potential,
        v.maturity_days,
        COALESCE(ra.adaptation_score, 0) as adaptation_score,
        (
            COALESCE(v.yield_potential, 0) * 0.4 +
            COALESCE(ra.adaptation_score, 0) * 0.3 +
            CASE 
                WHEN v.maturity_days IS NOT NULL AND max_maturity_days IS NOT NULL 
                THEN GREATEST(0, 100 - ABS(v.maturity_days - max_maturity_days)) * 0.3
                ELSE 50 * 0.3
            END
        ) as recommendation_score
    FROM enhanced_crop_varieties v
    LEFT JOIN crop_regional_adaptations ra ON v.crop_id = ra.crop_id 
        AND (region_name_param IS NULL OR ra.region_name = region_name_param)
    WHERE v.crop_id = crop_id_param
        AND v.is_active = true
        AND (min_yield_potential IS NULL OR v.yield_potential >= min_yield_potential)
        AND (max_maturity_days IS NULL OR v.maturity_days <= max_maturity_days)
    ORDER BY recommendation_score DESC, v.yield_potential DESC
    LIMIT limit_param;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PERFORMANCE MONITORING TRIGGERS
-- ============================================================================

-- Trigger to automatically update performance metrics
CREATE OR REPLACE FUNCTION update_performance_metrics()
RETURNS TRIGGER AS $$
BEGIN
    -- Log slow queries automatically
    IF NEW.execution_time_ms > 1000 THEN
        INSERT INTO performance_metrics (
            operation,
            execution_time_ms,
            cache_hit,
            database_query_count,
            timestamp
        ) VALUES (
            'slow_query_detected',
            NEW.execution_time_ms,
            NEW.cache_hit,
            NEW.database_query_count,
            NOW()
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CACHE MANAGEMENT FUNCTIONS
-- ============================================================================

-- Function to clean expired cache entries
CREATE OR REPLACE FUNCTION clean_expired_cache_entries()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM cache_entries WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get cache statistics
CREATE OR REPLACE FUNCTION get_cache_statistics()
RETURNS TABLE (
    namespace TEXT,
    total_entries BIGINT,
    expired_entries BIGINT,
    total_size_bytes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        namespace,
        COUNT(*) as total_entries,
        COUNT(CASE WHEN expires_at < NOW() THEN 1 END) as expired_entries,
        SUM(LENGTH(cache_data)) as total_size_bytes
    FROM cache_entries
    GROUP BY namespace
    ORDER BY total_entries DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PERFORMANCE OPTIMIZATION COMMENTS
-- ============================================================================

COMMENT ON INDEX idx_varieties_crop_id_active IS 'Optimizes variety lookups by crop with active status filter';
COMMENT ON INDEX idx_varieties_name_search IS 'Full-text search index for variety names';
COMMENT ON INDEX idx_varieties_yield_potential IS 'Optimizes variety sorting by yield potential';
COMMENT ON INDEX idx_varieties_stress_tolerances IS 'GIN index for array-based stress tolerance searches';
COMMENT ON INDEX idx_varieties_composite_filter IS 'Composite index for common variety filtering patterns';

COMMENT ON FUNCTION get_variety_search_suggestions IS 'Optimized variety search with relevance scoring';
COMMENT ON FUNCTION get_optimized_variety_recommendations IS 'Optimized variety recommendations with scoring algorithm';
COMMENT ON FUNCTION clean_expired_cache_entries IS 'Maintenance function to clean expired cache entries';
COMMENT ON FUNCTION get_cache_statistics IS 'Function to retrieve cache performance statistics';

-- ============================================================================
-- PERFORMANCE OPTIMIZATION COMPLETION
-- ============================================================================

-- Log completion of performance optimization setup
INSERT INTO performance_metrics (
    operation,
    execution_time_ms,
    cache_hit,
    database_query_count,
    timestamp,
    additional_data
) VALUES (
    'performance_optimization_setup',
    0,
    false,
    0,
    NOW(),
    '{"indexes_created": 15, "functions_created": 4, "views_created": 2}'::jsonb
);