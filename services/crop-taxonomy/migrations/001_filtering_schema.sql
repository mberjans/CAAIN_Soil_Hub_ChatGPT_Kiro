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
INSERT INTO crop_filtering_attributes (variety_id, pest_resistance_traits, disease_resistance_traits, market_class_filters, certification_filters, seed_availability_filters, drought_tolerance, heat_tolerance, cold_tolerance, management_complexity, yield_stability_score, drought_tolerance_score)
VALUES 
    (gen_random_uuid(), 
     '{"corn_borer": "resistant", "rootworm": "moderate"}',
     '{"gray_leaf_spot": "resistant", "northern_leaf_blight": "moderate"}',
     '{"market_class": "yellow_dent", "organic_certified": true}',
     '{"usda_organic": true, "non_gmo_project": false}',
     '{"availability": "high", "lead_time_days": 14, "supplier": "Pioneer"}',
     'moderate',
     'high',
     'moderate',
     'moderate',
     85, 75),
    (gen_random_uuid(),
     '{"aphids": "resistant", "corn_earworm": "susceptible"}',
     '{"rust": "resistant", "smut": "resistant"}',
     '{"market_class": "white_corn", "non_gmo": true}',
     '{"usda_organic": false, "non_gmo_project": true}',
     '{"availability": "medium", "lead_time_days": 21, "supplier": "Monsanto"}',
     'high',
     'moderate',
     'low',
     'low',
     90, 80),
    (gen_random_uuid(),
     '{"cutworm": "resistant", "wireworm": "moderate"}',
     '{"blight": "resistant", "mildew": "moderate"}',
     '{"market_class": "food_grade", "organic_certified": false}',
     '{"identity_preserved": true, "traceable": true}',
     '{"availability": "low", "lead_time_days": 30, "supplier": "Syngenta"}',
     'low',
     'high',
     'high',
     'high',
     70, 50),
    (gen_random_uuid(),
     '{"beetle": "moderate", "caterpillar": "susceptible"}',
     '{"powdery_mildew": "moderate", "downy_mildew": "resistant"}',
     '{"market_class": "feed_grade", "non_gmo": false}',
     '{"conventional": true}',
     '{"availability": "very_high", "lead_time_days": 7, "supplier": "Local Coop"}',
     'moderate',
     'moderate',
     'moderate',
     'low',
     75, 65),
    (gen_random_uuid(),
     '{"spider_mites": "resistant", "thrips": "moderate"}',
     '{"fusarium": "resistant", "anthracnose": "moderate"}',
     '{"market_class": "specialty", "organic_certified": true}',
     '{"specialty_crop_certified": true, "non_gmo_project": true}',
     '{"availability": "limited", "lead_time_days": 25, "supplier": "Specialty Seeds Inc"}',
     'high',
     'high',
     'moderate',
     'high',
     88, 82)
ON CONFLICT (variety_id) DO NOTHING;

-- Insert sample farmer preferences
INSERT INTO farmer_preferences (user_id, preferred_filters, filter_weights, selected_varieties, rejected_varieties)
VALUES 
    (gen_random_uuid(),
     '{"drought_tolerance": "high", "organic_certified": true, "market_class": "yellow_dent"}',
     '{"drought_tolerance": 0.9, "organic_certified": 0.8, "market_class": 0.7}',
     '["var_1", "var_2", "var_3"]',
     '["var_4", "var_5"]'),
    (gen_random_uuid(),
     '{"pest_resistance": {"corn_borer": "resistant"}, "yield_stability": {"min": 80}}',
     '{"pest_resistance": 0.95, "yield_stability": 0.85}',
     '["var_6", "var_7"]',
     '["var_8", "var_9", "var_10"]'),
    (gen_random_uuid(),
     '{"management_complexity": "low", "availability": "high"}',
     '{"management_complexity": 0.9, "availability": 0.7}',
     '["var_11", "var_12", "var_13"]',
     '[]'),
    (gen_random_uuid(),
     '{"certification": {"usda_organic": true}, "disease_resistance": {"rust": "resistant"}}',
     '{"certification": 0.9, "disease_resistance": 0.8}',
     '["var_14", "var_15"]',
     '["var_16", "var_17"]'),
    (gen_random_uuid(),
     '{"drought_tolerance": "moderate", "heat_tolerance": "high", "cold_tolerance": "low"}',
     '{"drought_tolerance": 0.7, "heat_tolerance": 0.8, "cold_tolerance": 0.6}',
     '["var_18", "var_19", "var_20"]',
     '["var_21"]')
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
     95),
    ('hash3',
     '{"crop_type": "corn", "certification": {"usda_organic": true}, "market_class": "food_grade"}',
     22,
     8,
     180),
    ('hash4',
     '{"crop_type": "wheat", "management_complexity": "low", "yield_stability_min": 80}',
     5,
     31,
     125),
    ('hash5',
     '{"crop_type": "corn", "pest_resistance": {"corn_borer": "resistant", "rootworm": "moderate"}, "disease_resistance": {"rust": "resistant"}}',
     42,
     17,
     210)
ON CONFLICT (combination_hash) DO NOTHING;