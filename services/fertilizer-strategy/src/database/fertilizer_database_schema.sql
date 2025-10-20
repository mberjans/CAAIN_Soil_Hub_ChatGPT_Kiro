-- Fertilizer Database and Classification System Migration Script
-- Version: 1.0
-- Date: 2025-10-20
-- Description: Comprehensive fertilizer product database with advanced classification system

-- Create ENUM types for fertilizer classification
CREATE TYPE fertilizer_type_enum AS ENUM (
    'organic_solid',
    'organic_liquid',
    'synthetic_granular',
    'synthetic_liquid',
    'slow_release_coated',
    'slow_release_matrix',
    'specialty_micronutrient',
    'bio_stimulant',
    'custom_blend'
);

CREATE TYPE nutrient_release_pattern AS ENUM (
    'immediate',
    'slow_release_30_days',
    'slow_release_60_days',
    'slow_release_90_days',
    'controlled_release_temperature',
    'controlled_release_moisture',
    'stabilized'
);

-- Main fertilizer products table
CREATE TABLE IF NOT EXISTS fertilizer_products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(255),
    fertilizer_type fertilizer_type_enum NOT NULL,

    -- Nutrient Analysis (NPK and more)
    nitrogen_percent DECIMAL(5,2) DEFAULT 0.0,
    phosphorus_percent DECIMAL(5,2) DEFAULT 0.0,
    potassium_percent DECIMAL(5,2) DEFAULT 0.0,
    sulfur_percent DECIMAL(5,2) DEFAULT 0.0,
    calcium_percent DECIMAL(5,2) DEFAULT 0.0,
    magnesium_percent DECIMAL(5,2) DEFAULT 0.0,
    micronutrients JSONB DEFAULT '{}', -- {zinc, iron, manganese, copper, boron, molybdenum}

    -- Physical Properties
    physical_form VARCHAR(50), -- granular, liquid, powder, pellet
    particle_size VARCHAR(50), -- SGN rating or mesh size
    bulk_density DECIMAL(6,2), -- lbs/cubic foot
    solubility VARCHAR(50), -- highly soluble, moderately soluble, etc.
    release_pattern nutrient_release_pattern DEFAULT 'immediate',

    -- Application Methods
    application_methods TEXT[] DEFAULT '{}', -- broadcast, banded, foliar, fertigation, injection
    compatible_equipment TEXT[] DEFAULT '{}', -- spreader types, sprayers, etc.
    mixing_compatibility JSONB DEFAULT '{}', -- tank mixing compatibility information

    -- Environmental Impact
    environmental_impact JSONB DEFAULT '{}', -- {runoff_risk, volatilization_risk, leaching_risk, carbon_footprint}
    organic_certified BOOLEAN DEFAULT FALSE,
    sustainability_rating DECIMAL(3,2) DEFAULT 5.0, -- 0-10 scale

    -- Cost Data
    average_cost_per_unit DECIMAL(10,2), -- average market price
    cost_unit VARCHAR(50) DEFAULT 'ton', -- ton, gallon, lb, kg
    price_volatility DECIMAL(5,2) DEFAULT 0.0, -- standard deviation of price
    availability_score DECIMAL(3,2) DEFAULT 7.0, -- 0-10 scale

    -- Regulatory and Safety
    regulatory_status VARCHAR(100), -- approved, restricted, requires permit
    safety_data JSONB DEFAULT '{}', -- SDS information
    handling_requirements TEXT[] DEFAULT '{}', -- special handling needs
    storage_requirements TEXT[] DEFAULT '{}', -- storage conditions

    -- Crop Compatibility
    recommended_crops TEXT[] DEFAULT '{}', -- corn, wheat, soybeans, etc.
    not_recommended_crops TEXT[] DEFAULT '{}', -- crops to avoid
    growth_stage_suitability JSONB DEFAULT '{}', -- {vegetative: true, reproductive: false}

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    data_source VARCHAR(100), -- where this data came from
    last_verified TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,

    -- Constraints
    CONSTRAINT valid_nitrogen_percent CHECK (nitrogen_percent >= 0 AND nitrogen_percent <= 100),
    CONSTRAINT valid_phosphorus_percent CHECK (phosphorus_percent >= 0 AND phosphorus_percent <= 100),
    CONSTRAINT valid_potassium_percent CHECK (potassium_percent >= 0 AND potassium_percent <= 100),
    CONSTRAINT valid_sustainability_rating CHECK (sustainability_rating >= 0 AND sustainability_rating <= 10),
    CONSTRAINT valid_availability_score CHECK (availability_score >= 0 AND availability_score <= 10)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_fertilizer_type ON fertilizer_products(fertilizer_type);
CREATE INDEX IF NOT EXISTS idx_fertilizer_organic ON fertilizer_products(organic_certified);
CREATE INDEX IF NOT EXISTS idx_fertilizer_manufacturer ON fertilizer_products(manufacturer);
CREATE INDEX IF NOT EXISTS idx_fertilizer_application_methods ON fertilizer_products USING GIN(application_methods);
CREATE INDEX IF NOT EXISTS idx_fertilizer_recommended_crops ON fertilizer_products USING GIN(recommended_crops);
CREATE INDEX IF NOT EXISTS idx_fertilizer_release_pattern ON fertilizer_products(release_pattern);
CREATE INDEX IF NOT EXISTS idx_fertilizer_active ON fertilizer_products(is_active);

-- Classification reference table
CREATE TABLE IF NOT EXISTS fertilizer_classifications (
    classification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    classification_type VARCHAR(50) NOT NULL, -- nutrient_based, source_based, release_based, application_based
    classification_name VARCHAR(100) NOT NULL,
    description TEXT,
    criteria JSONB DEFAULT '{}', -- JSON object with classification criteria
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT unique_classification UNIQUE(classification_type, classification_name)
);

CREATE INDEX IF NOT EXISTS idx_classification_type ON fertilizer_classifications(classification_type);

-- Fertilizer compatibility matrix
CREATE TABLE IF NOT EXISTS fertilizer_compatibility (
    compatibility_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id_1 UUID REFERENCES fertilizer_products(product_id) ON DELETE CASCADE,
    product_id_2 UUID REFERENCES fertilizer_products(product_id) ON DELETE CASCADE,
    compatibility_level VARCHAR(50) NOT NULL, -- compatible, caution, incompatible
    mixing_ratio_limits JSONB DEFAULT '{}', -- {max_ratio: 1.5, recommended_ratio: 1.0}
    notes TEXT,
    test_date TIMESTAMP,
    verified_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    CONSTRAINT valid_compatibility_level CHECK (compatibility_level IN ('compatible', 'caution', 'incompatible')),
    CONSTRAINT different_products CHECK (product_id_1 != product_id_2)
);

CREATE INDEX IF NOT EXISTS idx_compatibility_product1 ON fertilizer_compatibility(product_id_1);
CREATE INDEX IF NOT EXISTS idx_compatibility_product2 ON fertilizer_compatibility(product_id_2);
CREATE INDEX IF NOT EXISTS idx_compatibility_level ON fertilizer_compatibility(compatibility_level);

-- Nutrient analysis history table (for tracking changes over time)
CREATE TABLE IF NOT EXISTS fertilizer_nutrient_analysis_history (
    analysis_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES fertilizer_products(product_id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL,
    nitrogen_percent DECIMAL(5,2) DEFAULT 0.0,
    phosphorus_percent DECIMAL(5,2) DEFAULT 0.0,
    potassium_percent DECIMAL(5,2) DEFAULT 0.0,
    sulfur_percent DECIMAL(5,2) DEFAULT 0.0,
    calcium_percent DECIMAL(5,2) DEFAULT 0.0,
    magnesium_percent DECIMAL(5,2) DEFAULT 0.0,
    micronutrients JSONB DEFAULT '{}',
    analysis_method VARCHAR(100), -- lab analysis, manufacturer specification, etc.
    lab_name VARCHAR(255),
    certified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_nutrient_analysis_product ON fertilizer_nutrient_analysis_history(product_id);
CREATE INDEX IF NOT EXISTS idx_nutrient_analysis_date ON fertilizer_nutrient_analysis_history(analysis_date);

-- Application recommendations table
CREATE TABLE IF NOT EXISTS fertilizer_application_recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES fertilizer_products(product_id) ON DELETE CASCADE,
    crop_type VARCHAR(100) NOT NULL,
    growth_stage VARCHAR(100), -- vegetative, reproductive, pre_plant, etc.
    recommended_rate_min DECIMAL(8,2), -- lbs/acre or kg/ha
    recommended_rate_max DECIMAL(8,2),
    rate_unit VARCHAR(50) DEFAULT 'lbs/acre',
    application_method VARCHAR(100), -- broadcast, banded, foliar, etc.
    application_timing VARCHAR(255), -- timing description
    soil_condition_requirements JSONB DEFAULT '{}', -- pH, moisture, temperature
    expected_response JSONB DEFAULT '{}', -- yield increase, quality improvement
    notes TEXT,
    research_source VARCHAR(255), -- university study, field trial, etc.
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_application_rec_product ON fertilizer_application_recommendations(product_id);
CREATE INDEX IF NOT EXISTS idx_application_rec_crop ON fertilizer_application_recommendations(crop_type);

-- Update trigger for updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to all tables with updated_at
CREATE TRIGGER update_fertilizer_products_updated_at
    BEFORE UPDATE ON fertilizer_products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fertilizer_classifications_updated_at
    BEFORE UPDATE ON fertilizer_classifications
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fertilizer_compatibility_updated_at
    BEFORE UPDATE ON fertilizer_compatibility
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fertilizer_application_recommendations_updated_at
    BEFORE UPDATE ON fertilizer_application_recommendations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE fertilizer_products IS 'Comprehensive fertilizer product database with nutrient analysis, physical properties, and agronomic data';
COMMENT ON TABLE fertilizer_classifications IS 'Classification system for categorizing fertilizers by multiple criteria';
COMMENT ON TABLE fertilizer_compatibility IS 'Matrix of fertilizer product compatibility for tank mixing and blending';
COMMENT ON TABLE fertilizer_nutrient_analysis_history IS 'Historical nutrient analysis records for tracking product consistency';
COMMENT ON TABLE fertilizer_application_recommendations IS 'Crop-specific application recommendations and best practices';
