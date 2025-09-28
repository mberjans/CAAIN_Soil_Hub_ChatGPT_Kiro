-- 005_expand_enhanced_crop_varieties.sql
-- Purpose: Expand enhanced_crop_varieties table with additional analytics fields and indexes
-- This migration aligns the physical schema with the expanded data model for crop variety intelligence.

-- Ensure yield stability constraint supports decimal precision
ALTER TABLE enhanced_crop_varieties
    DROP CONSTRAINT IF EXISTS check_yield_stability;

ALTER TABLE enhanced_crop_varieties
    ALTER COLUMN yield_stability_rating TYPE NUMERIC(4,2)
    USING CASE
        WHEN yield_stability_rating IS NULL THEN NULL
        ELSE yield_stability_rating::NUMERIC(4,2)
    END;

ALTER TABLE enhanced_crop_varieties
    ADD CONSTRAINT check_yield_stability
    CHECK (yield_stability_rating >= 0 AND yield_stability_rating <= 10);

-- Add new performance, availability, and provenance columns
ALTER TABLE enhanced_crop_varieties
    ADD COLUMN IF NOT EXISTS market_acceptance_score NUMERIC(4,2);

ALTER TABLE enhanced_crop_varieties
    ADD COLUMN IF NOT EXISTS seed_availability_status VARCHAR(50);

ALTER TABLE enhanced_crop_varieties
    ADD COLUMN IF NOT EXISTS seed_companies JSONB DEFAULT '[]'::jsonb;

ALTER TABLE enhanced_crop_varieties
    ADD COLUMN IF NOT EXISTS trait_stack JSONB DEFAULT '[]'::jsonb;

ALTER TABLE enhanced_crop_varieties
    ADD COLUMN IF NOT EXISTS regional_performance_data JSONB DEFAULT '[]'::jsonb;

ALTER TABLE enhanced_crop_varieties
    ADD COLUMN IF NOT EXISTS release_year INTEGER;

ALTER TABLE enhanced_crop_varieties
    ADD COLUMN IF NOT EXISTS patent_status VARCHAR(50);

-- Establish data quality constraints for new attributes
ALTER TABLE enhanced_crop_varieties
    ADD CONSTRAINT check_market_acceptance
    CHECK (market_acceptance_score IS NULL OR (market_acceptance_score >= 0 AND market_acceptance_score <= 5));

ALTER TABLE enhanced_crop_varieties
    ADD CONSTRAINT check_seed_availability_status
    CHECK (seed_availability_status IS NULL OR seed_availability_status IN (
        'in_stock', 'limited', 'preorder', 'retired', 'discontinued'
    ));

ALTER TABLE enhanced_crop_varieties
    ADD CONSTRAINT check_patent_status
    CHECK (patent_status IS NULL OR patent_status IN (
        'none', 'pending', 'active', 'expired', 'waived'
    ));

ALTER TABLE enhanced_crop_varieties
    ADD CONSTRAINT check_release_year
    CHECK (release_year IS NULL OR (release_year >= 1900 AND release_year <= 2100));

-- Normalise existing NULL JSON fields to empty collections for consistency
UPDATE enhanced_crop_varieties
SET seed_companies = '[]'::jsonb
WHERE seed_companies IS NULL;

UPDATE enhanced_crop_varieties
SET trait_stack = '[]'::jsonb
WHERE trait_stack IS NULL;

UPDATE enhanced_crop_varieties
SET regional_performance_data = '[]'::jsonb
WHERE regional_performance_data IS NULL;

-- Create supporting indexes for analytics and lookup performance
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_crop_id
    ON enhanced_crop_varieties(crop_id);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_active
    ON enhanced_crop_varieties(is_active);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_maturity
    ON enhanced_crop_varieties(relative_maturity);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_regions
    ON enhanced_crop_varieties USING GIN(adapted_regions);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_trait_stack
    ON enhanced_crop_varieties USING GIN(trait_stack);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_market_acceptance
    ON enhanced_crop_varieties(market_acceptance_score);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_yield_stability
    ON enhanced_crop_varieties(yield_stability_rating);

CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_name_search
    ON enhanced_crop_varieties USING gin((variety_name) gin_trgm_ops);
