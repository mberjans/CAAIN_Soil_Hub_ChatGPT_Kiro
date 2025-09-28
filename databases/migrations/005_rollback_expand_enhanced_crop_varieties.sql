-- 005_rollback_expand_enhanced_crop_varieties.sql
-- Purpose: Roll back the enhancements applied in 005_expand_enhanced_crop_varieties.sql

-- Drop analytics indexes introduced in forward migration
DROP INDEX IF EXISTS idx_enhanced_varieties_name_search;
DROP INDEX IF EXISTS idx_enhanced_varieties_yield_stability;
DROP INDEX IF EXISTS idx_enhanced_varieties_market_acceptance;
DROP INDEX IF EXISTS idx_enhanced_varieties_trait_stack;
DROP INDEX IF EXISTS idx_enhanced_varieties_regions;
DROP INDEX IF EXISTS idx_enhanced_varieties_maturity;
DROP INDEX IF EXISTS idx_enhanced_varieties_active;
DROP INDEX IF EXISTS idx_enhanced_varieties_crop_id;

-- Remove constraint additions
ALTER TABLE enhanced_crop_varieties
    DROP CONSTRAINT IF EXISTS check_release_year;

ALTER TABLE enhanced_crop_varieties
    DROP CONSTRAINT IF EXISTS check_patent_status;

ALTER TABLE enhanced_crop_varieties
    DROP CONSTRAINT IF EXISTS check_seed_availability_status;

ALTER TABLE enhanced_crop_varieties
    DROP CONSTRAINT IF EXISTS check_market_acceptance;

ALTER TABLE enhanced_crop_varieties
    DROP CONSTRAINT IF EXISTS check_yield_stability;

-- Drop newly added columns
ALTER TABLE enhanced_crop_varieties
    DROP COLUMN IF EXISTS patent_status;

ALTER TABLE enhanced_crop_varieties
    DROP COLUMN IF EXISTS release_year;

ALTER TABLE enhanced_crop_varieties
    DROP COLUMN IF EXISTS regional_performance_data;

ALTER TABLE enhanced_crop_varieties
    DROP COLUMN IF EXISTS trait_stack;

ALTER TABLE enhanced_crop_varieties
    DROP COLUMN IF EXISTS seed_companies;

ALTER TABLE enhanced_crop_varieties
    DROP COLUMN IF EXISTS seed_availability_status;

ALTER TABLE enhanced_crop_varieties
    DROP COLUMN IF EXISTS market_acceptance_score;

-- Restore integer yield stability rating and original constraint
ALTER TABLE enhanced_crop_varieties
    ALTER COLUMN yield_stability_rating TYPE INTEGER
    USING CASE
        WHEN yield_stability_rating IS NULL THEN NULL
        ELSE ROUND(yield_stability_rating)::INTEGER
    END;

ALTER TABLE enhanced_crop_varieties
    ADD CONSTRAINT check_yield_stability
    CHECK (yield_stability_rating >= 1 AND yield_stability_rating <= 10);

-- Rebuild essential legacy indexes
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_crop_id
    ON enhanced_crop_varieties(crop_id);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_active
    ON enhanced_crop_varieties(is_active);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_maturity
    ON enhanced_crop_varieties(relative_maturity);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_regions
    ON enhanced_crop_varieties USING GIN(adapted_regions);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_name_search
    ON enhanced_crop_varieties USING gin((variety_name) gin_trgm_ops);
