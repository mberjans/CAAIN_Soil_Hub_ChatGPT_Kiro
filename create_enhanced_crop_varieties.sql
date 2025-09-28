-- Create Enhanced Crop Varieties Table
-- TICKET-005_crop-variety-recommendations-1.1

-- Create the enhanced_crop_varieties table
CREATE TABLE IF NOT EXISTS enhanced_crop_varieties (
    variety_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID NOT NULL REFERENCES crops(crop_id) ON DELETE CASCADE,
    
    -- Variety identification
    variety_name VARCHAR(200) NOT NULL,
    variety_code VARCHAR(50),
    breeder_company VARCHAR(150),
    parent_varieties TEXT[],
    seed_companies JSONB DEFAULT '[]'::jsonb,
    
    -- Maturity and timing
    relative_maturity INTEGER,
    maturity_group VARCHAR(10),
    days_to_emergence INTEGER,
    days_to_flowering INTEGER,
    days_to_physiological_maturity INTEGER,
    
    -- Performance characteristics
    yield_potential_percentile INTEGER CHECK (yield_potential_percentile >= 0 AND yield_potential_percentile <= 100),
    yield_stability_rating NUMERIC(4,2) CHECK (yield_stability_rating >= 0 AND yield_stability_rating <= 10),
    market_acceptance_score NUMERIC(4,2) CHECK (market_acceptance_score >= 0 AND market_acceptance_score <= 5),
    standability_rating INTEGER CHECK (standability_rating >= 1 AND standability_rating <= 10),
    
    -- Resistance and tolerance traits
    disease_resistances JSONB,
    pest_resistances JSONB,
    herbicide_tolerances TEXT[],
    stress_tolerances TEXT[],
    trait_stack JSONB DEFAULT '[]'::jsonb,
    
    -- Quality traits
    quality_characteristics JSONB,
    protein_content_range VARCHAR(20),
    oil_content_range VARCHAR(20),
    
    -- Adaptation and recommendations
    adapted_regions TEXT[],
    recommended_planting_populations JSONB,
    regional_performance_data JSONB DEFAULT '[]'::jsonb,
    special_management_notes TEXT,
    
    -- Commercial information
    seed_availability VARCHAR(20) CHECK (seed_availability IN ('widely_available', 'limited', 'specialty', 'research_only')),
    seed_availability_status VARCHAR(50) CHECK (seed_availability_status IS NULL OR seed_availability_status IN ('in_stock', 'limited', 'preorder', 'retired', 'discontinued')),
    relative_seed_cost VARCHAR(20) CHECK (relative_seed_cost IN ('low', 'moderate', 'high', 'premium')),
    technology_package VARCHAR(100),
    
    -- Regulatory and certification
    organic_approved BOOLEAN DEFAULT NULL,
    non_gmo_certified BOOLEAN DEFAULT NULL,
    registration_year INTEGER,
    release_year INTEGER CHECK (release_year IS NULL OR (release_year >= 1900 AND release_year <= 2100)),
    patent_protected BOOLEAN DEFAULT false,
    patent_status VARCHAR(50) CHECK (patent_status IS NULL OR patent_status IN ('none', 'pending', 'active', 'expired', 'waived')),
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(crop_id, variety_name, breeder_company)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_crop_id ON enhanced_crop_varieties(crop_id);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_maturity ON enhanced_crop_varieties(relative_maturity);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_active ON enhanced_crop_varieties(is_active);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_regions ON enhanced_crop_varieties USING GIN(adapted_regions);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_trait_stack ON enhanced_crop_varieties USING GIN(trait_stack);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_market_acceptance ON enhanced_crop_varieties(market_acceptance_score);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_yield_stability ON enhanced_crop_varieties(yield_stability_rating);
CREATE INDEX IF NOT EXISTS idx_enhanced_varieties_name_search ON enhanced_crop_varieties USING gin((variety_name) gin_trgm_ops);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_enhanced_crop_varieties_updated_at 
    BEFORE UPDATE ON enhanced_crop_varieties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();