-- Create crop_filtering_attributes table
CREATE TABLE IF NOT EXISTS crop_filtering_attributes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    variety_id UUID NOT NULL UNIQUE,
    pest_resistance_traits JSONB DEFAULT '{}',
    disease_resistance_traits JSONB DEFAULT '{}',
    market_class_filters JSONB DEFAULT '{}',
    certification_filters JSONB DEFAULT '{}',
    seed_availability_filters JSONB DEFAULT '{}',
    drought_tolerance VARCHAR(20), -- low, moderate, high
    heat_tolerance VARCHAR(20),    -- low, moderate, high
    cold_tolerance VARCHAR(20),    -- low, moderate, high
    management_complexity VARCHAR(20), -- low, moderate, high
    yield_stability_score INTEGER,
    drought_tolerance_score INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_pest_resistance_gin ON crop_filtering_attributes USING GIN(pest_resistance_traits);
CREATE INDEX IF NOT EXISTS idx_disease_resistance_gin ON crop_filtering_attributes USING GIN(disease_resistance_traits);
CREATE INDEX IF NOT EXISTS idx_market_class_gin ON crop_filtering_attributes USING GIN(market_class_filters);
CREATE INDEX IF NOT EXISTS idx_certification_gin ON crop_filtering_attributes USING GIN(certification_filters);
CREATE INDEX IF NOT EXISTS idx_seed_availability_gin ON crop_filtering_attributes USING GIN(seed_availability_filters);

-- Create farmer_preferences table
CREATE TABLE IF NOT EXISTS farmer_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    preferred_filters JSONB DEFAULT '{}',
    filter_weights JSONB DEFAULT '{}',
    selected_varieties JSONB DEFAULT '[]',
    rejected_varieties JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_farmer_pref_user ON farmer_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_preferred_filters_gin ON farmer_preferences USING GIN(preferred_filters);
CREATE INDEX IF NOT EXISTS idx_filter_weights_gin ON farmer_preferences USING GIN(filter_weights);
CREATE INDEX IF NOT EXISTS idx_selected_varieties_gin ON farmer_preferences USING GIN(selected_varieties);
CREATE INDEX IF NOT EXISTS idx_rejected_varieties_gin ON farmer_preferences USING GIN(rejected_varieties);

-- Create filter_combinations table
CREATE TABLE IF NOT EXISTS filter_combinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    combination_hash VARCHAR(64) UNIQUE NOT NULL,
    filters JSONB NOT NULL,
    usage_count INTEGER DEFAULT 1,
    avg_result_count INTEGER,
    avg_response_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    last_used_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_filter_combo_hash ON filter_combinations(combination_hash);
CREATE INDEX IF NOT EXISTS idx_filter_combo_usage ON filter_combinations(usage_count);
CREATE INDEX IF NOT EXISTS idx_filters_gin ON filter_combinations USING GIN(filters);

-- Insert sample data
INSERT INTO crop_filtering_attributes (variety_id, pest_resistance_traits, disease_resistance_traits, market_class_filters, certification_filters, drought_tolerance, heat_tolerance, management_complexity, yield_stability_score, drought_tolerance_score)
VALUES 
    (gen_random_uuid(), 
     '{"corn_borer": "resistant", "rootworm": "moderate"}',
     '{"gray_leaf_spot": "resistant", "northern_leaf_blight": "moderate"}',
     '{"market_class": "yellow_dent", "organic_certified": true}',
     '{"usda_organic": true, "non_gmo_project": false}',
     'moderate',
     'high',
     'moderate',
     85, 75),
    (gen_random_uuid(),
     '{"aphids": "resistant", "corn_earworm": "susceptible"}',
     '{"rust": "resistant", "smut": "resistant"}',
     '{"market_class": "white_corn", "non_gmo": true}',
     '{"usda_organic": false, "non_gmo_project": true}',
     'high',
     'moderate',
     'low',
     90, 80)
ON CONFLICT (variety_id) DO NOTHING;

-- Insert sample farmer preferences
INSERT INTO farmer_preferences (user_id, preferred_filters, filter_weights, selected_varieties, rejected_varieties)
VALUES 
    (gen_random_uuid(),
     '{"drought_tolerance": "high", "organic_certified": true}',
     '{"drought_tolerance": 0.9, "organic_certified": 0.8}',
     '["var_1", "var_2"]',
     '["var_3"]'),
    (gen_random_uuid(),
     '{"pest_resistance": {"corn_borer": "resistant"}}',
     '{"pest_resistance": 0.95}',
     '["var_4"]',
     '["var_5", "var_6"]')
ON CONFLICT (id) DO NOTHING;

-- Insert sample filter combinations
INSERT INTO filter_combinations (combination_hash, filters, usage_count, avg_result_count, avg_response_time_ms)
VALUES 
    ('hash1',
     '{"crop_type": "corn", "drought_tolerance": "high"}',
     15,
     23,
     150),
    ('hash2',
     '{"crop_type": "soybean", "organic_certified": true, "pest_resistance": {"aphids": "resistant"}}',
     8,
     12,
     95)
ON CONFLICT (combination_hash) DO NOTHING;