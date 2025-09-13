-- AFAS PostgreSQL Database Schema
-- Autonomous Farm Advisory System
-- Version: 1.0
-- Date: December 2024

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database (run separately if needed)
-- CREATE DATABASE afas_db;

-- ============================================================================
-- CORE USER AND AUTHENTICATION TABLES
-- ============================================================================

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    role VARCHAR(50) DEFAULT 'farmer' CHECK (role IN ('farmer', 'consultant', 'admin', 'expert')),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE user_sessions (
    session_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address INET,
    user_agent TEXT
);

-- ============================================================================
-- FARM AND LOCATION TABLES
-- ============================================================================

CREATE TABLE farms (
    farm_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    farm_name VARCHAR(255) NOT NULL,
    farm_size_acres DECIMAL(10,2) NOT NULL CHECK (farm_size_acres > 0),
    location GEOGRAPHY(POINT, 4326) NOT NULL, -- PostGIS for GPS coordinates
    address TEXT,
    state VARCHAR(50),
    county VARCHAR(100),
    climate_zone VARCHAR(20),
    usda_hardiness_zone VARCHAR(10),
    elevation_feet INTEGER,
    irrigation_available BOOLEAN DEFAULT false,
    organic_certified BOOLEAN DEFAULT false,
    certification_body VARCHAR(100),
    certification_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fields (
    field_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(farm_id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    field_size_acres DECIMAL(8,2) NOT NULL CHECK (field_size_acres > 0),
    field_boundary GEOGRAPHY(POLYGON, 4326), -- Field boundaries if available
    soil_type VARCHAR(100),
    drainage_class VARCHAR(50) CHECK (drainage_class IN ('well_drained', 'moderately_well_drained', 'somewhat_poorly_drained', 'poorly_drained', 'very_poorly_drained')),
    slope_percent DECIMAL(5,2),
    erosion_risk VARCHAR(20) CHECK (erosion_risk IN ('low', 'moderate', 'high', 'severe')),
    conservation_practices TEXT[], -- Array of conservation practices
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- SOIL DATA TABLES
-- ============================================================================

CREATE TABLE soil_tests (
    test_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(field_id) ON DELETE CASCADE,
    test_date DATE NOT NULL,
    lab_name VARCHAR(255),
    lab_id VARCHAR(100),
    sampling_depth_inches INTEGER DEFAULT 6,
    sample_count INTEGER DEFAULT 1,
    
    -- Primary nutrients
    ph DECIMAL(3,1) NOT NULL CHECK (ph >= 3.0 AND ph <= 10.0),
    organic_matter_percent DECIMAL(4,2) CHECK (organic_matter_percent >= 0 AND organic_matter_percent <= 15),
    phosphorus_ppm DECIMAL(6,2) CHECK (phosphorus_ppm >= 0 AND phosphorus_ppm <= 200),
    potassium_ppm DECIMAL(6,2) CHECK (potassium_ppm >= 0 AND potassium_ppm <= 800),
    nitrogen_ppm DECIMAL(6,2) CHECK (nitrogen_ppm >= 0 AND nitrogen_ppm <= 100),
    
    -- Secondary nutrients
    calcium_ppm DECIMAL(8,2),
    magnesium_ppm DECIMAL(6,2),
    sulfur_ppm DECIMAL(6,2),
    
    -- Micronutrients
    iron_ppm DECIMAL(6,2),
    manganese_ppm DECIMAL(6,2),
    zinc_ppm DECIMAL(6,2),
    copper_ppm DECIMAL(6,2),
    boron_ppm DECIMAL(6,2),
    molybdenum_ppm DECIMAL(6,2),
    
    -- Soil properties
    cec_meq_per_100g DECIMAL(5,2) CHECK (cec_meq_per_100g >= 0 AND cec_meq_per_100g <= 50),
    base_saturation_percent DECIMAL(5,2),
    soil_texture VARCHAR(50),
    sand_percent DECIMAL(5,2),
    silt_percent DECIMAL(5,2),
    clay_percent DECIMAL(5,2),
    bulk_density DECIMAL(4,2),
    
    -- Test method information
    extraction_method VARCHAR(100) DEFAULT 'Mehlich-3',
    test_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure sand + silt + clay = 100% if all are provided
    CONSTRAINT texture_sum_check CHECK (
        (sand_percent IS NULL OR silt_percent IS NULL OR clay_percent IS NULL) OR
        (ABS(sand_percent + silt_percent + clay_percent - 100.0) < 0.1)
    )
);

-- ============================================================================
-- CROP AND ROTATION TABLES
-- ============================================================================

CREATE TABLE crops (
    crop_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_name VARCHAR(100) NOT NULL UNIQUE,
    scientific_name VARCHAR(150),
    crop_category VARCHAR(50) CHECK (crop_category IN ('grain', 'oilseed', 'forage', 'vegetable', 'fruit', 'specialty')),
    crop_family VARCHAR(100),
    nitrogen_fixing BOOLEAN DEFAULT false,
    typical_yield_range_min DECIMAL(8,2),
    typical_yield_range_max DECIMAL(8,2),
    yield_units VARCHAR(20) DEFAULT 'bu/acre',
    growing_degree_days INTEGER,
    maturity_days_min INTEGER,
    maturity_days_max INTEGER,
    optimal_ph_min DECIMAL(3,1),
    optimal_ph_max DECIMAL(3,1),
    drought_tolerance VARCHAR(20) CHECK (drought_tolerance IN ('low', 'moderate', 'high')),
    cold_tolerance VARCHAR(20) CHECK (cold_tolerance IN ('low', 'moderate', 'high')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crop_varieties (
    variety_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    crop_id UUID NOT NULL REFERENCES crops(crop_id) ON DELETE CASCADE,
    variety_name VARCHAR(150) NOT NULL,
    company VARCHAR(100),
    maturity_days INTEGER,
    yield_potential DECIMAL(8,2),
    disease_resistance TEXT[], -- Array of disease resistances
    herbicide_tolerance TEXT[], -- Array of herbicide tolerances
    special_traits TEXT[], -- Array of special traits
    regional_adaptation TEXT[], -- Array of regions where adapted
    release_year INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE crop_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(field_id) ON DELETE CASCADE,
    crop_year INTEGER NOT NULL,
    crop_id UUID NOT NULL REFERENCES crops(crop_id),
    variety_id UUID REFERENCES crop_varieties(variety_id),
    planting_date DATE,
    harvest_date DATE,
    actual_yield DECIMAL(8,2),
    yield_units VARCHAR(20) DEFAULT 'bu/acre',
    tillage_system VARCHAR(50) CHECK (tillage_system IN ('conventional', 'reduced_till', 'no_till', 'strip_till')),
    cover_crop_used BOOLEAN DEFAULT false,
    cover_crop_species VARCHAR(100),
    irrigation_used BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(field_id, crop_year)
);

-- ============================================================================
-- FERTILIZER AND NUTRIENT MANAGEMENT TABLES
-- ============================================================================

CREATE TABLE fertilizer_products (
    product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_name VARCHAR(255) NOT NULL,
    manufacturer VARCHAR(150),
    product_type VARCHAR(50) CHECK (product_type IN ('synthetic', 'organic', 'slow_release', 'liquid', 'granular')),
    
    -- Nutrient analysis (guaranteed analysis)
    nitrogen_percent DECIMAL(5,2) DEFAULT 0,
    phosphorus_percent DECIMAL(5,2) DEFAULT 0, -- P2O5
    potassium_percent DECIMAL(5,2) DEFAULT 0, -- K2O
    sulfur_percent DECIMAL(5,2) DEFAULT 0,
    calcium_percent DECIMAL(5,2) DEFAULT 0,
    magnesium_percent DECIMAL(5,2) DEFAULT 0,
    
    -- Micronutrients
    iron_percent DECIMAL(5,2) DEFAULT 0,
    manganese_percent DECIMAL(5,2) DEFAULT 0,
    zinc_percent DECIMAL(5,2) DEFAULT 0,
    copper_percent DECIMAL(5,2) DEFAULT 0,
    boron_percent DECIMAL(5,2) DEFAULT 0,
    
    -- Physical properties
    bulk_density DECIMAL(6,2), -- lbs/cubic foot
    particle_size VARCHAR(50),
    application_method TEXT[], -- Array of application methods
    
    -- Economic data
    typical_price_per_ton DECIMAL(8,2),
    price_currency VARCHAR(3) DEFAULT 'USD',
    price_date DATE,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE fertilizer_applications (
    application_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(field_id) ON DELETE CASCADE,
    crop_year INTEGER NOT NULL,
    product_id UUID REFERENCES fertilizer_products(product_id),
    custom_product_name VARCHAR(255), -- For products not in our database
    
    application_date DATE NOT NULL,
    application_method VARCHAR(50) CHECK (application_method IN ('broadcast', 'banded', 'side_dress', 'foliar', 'fertigation', 'injection')),
    application_timing VARCHAR(50) CHECK (application_timing IN ('pre_plant', 'at_plant', 'post_emerge', 'side_dress', 'split_application')),
    
    -- Application rates
    rate_lbs_per_acre DECIMAL(8,2) NOT NULL CHECK (rate_lbs_per_acre > 0),
    actual_n_lbs_per_acre DECIMAL(8,2),
    actual_p_lbs_per_acre DECIMAL(8,2),
    actual_k_lbs_per_acre DECIMAL(8,2),
    
    -- Application details
    incorporation_method VARCHAR(50),
    incorporation_depth_inches DECIMAL(4,1),
    weather_conditions TEXT,
    soil_conditions TEXT,
    
    -- Economic data
    cost_per_acre DECIMAL(8,2),
    total_cost DECIMAL(10,2),
    
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- RECOMMENDATION SYSTEM TABLES
-- ============================================================================

CREATE TABLE question_types (
    question_id INTEGER PRIMARY KEY,
    question_text TEXT NOT NULL,
    question_category VARCHAR(100) NOT NULL,
    priority_level INTEGER DEFAULT 1 CHECK (priority_level BETWEEN 1 AND 5),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recommendations (
    recommendation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    farm_id UUID REFERENCES farms(farm_id) ON DELETE CASCADE,
    field_id UUID REFERENCES fields(field_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES question_types(question_id),
    
    -- Request context
    request_data JSONB NOT NULL, -- Original request parameters
    location_data JSONB, -- Location context used
    soil_data JSONB, -- Soil data used
    crop_data JSONB, -- Crop data used
    
    -- Recommendation results
    recommendations JSONB NOT NULL, -- Array of recommendation items
    overall_confidence DECIMAL(3,2) NOT NULL CHECK (overall_confidence BETWEEN 0 AND 1),
    confidence_factors JSONB, -- Breakdown of confidence factors
    
    -- Metadata
    processing_time_ms INTEGER,
    data_sources_used TEXT[], -- Array of data sources
    agricultural_sources TEXT[], -- Array of agricultural references
    warnings TEXT[], -- Array of warnings
    
    -- User interaction
    user_feedback INTEGER CHECK (user_feedback BETWEEN 1 AND 5),
    feedback_text TEXT,
    implemented BOOLEAN,
    implementation_notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- EQUIPMENT AND FARM MANAGEMENT TABLES
-- ============================================================================

CREATE TABLE equipment_types (
    equipment_type_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    equipment_name VARCHAR(150) NOT NULL,
    equipment_category VARCHAR(50) CHECK (equipment_category IN ('tillage', 'planting', 'spraying', 'harvesting', 'fertilizer', 'other')),
    typical_capacity VARCHAR(100),
    power_requirements VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE farm_equipment (
    equipment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farm_id UUID NOT NULL REFERENCES farms(farm_id) ON DELETE CASCADE,
    equipment_type_id UUID REFERENCES equipment_types(equipment_type_id),
    custom_equipment_name VARCHAR(150), -- For equipment not in types table
    manufacturer VARCHAR(100),
    model VARCHAR(100),
    year_manufactured INTEGER,
    condition VARCHAR(20) CHECK (condition IN ('excellent', 'good', 'fair', 'poor')),
    capacity VARCHAR(100),
    is_operational BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- WEATHER AND ENVIRONMENTAL DATA TABLES
-- ============================================================================

CREATE TABLE weather_stations (
    station_id VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    elevation_feet INTEGER,
    data_provider VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE weather_data (
    weather_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    station_id VARCHAR(50) REFERENCES weather_stations(station_id),
    location GEOGRAPHY(POINT, 4326), -- For location-specific data
    observation_date DATE NOT NULL,
    
    -- Temperature data (Fahrenheit)
    temp_max_f DECIMAL(5,1),
    temp_min_f DECIMAL(5,1),
    temp_avg_f DECIMAL(5,1),
    
    -- Precipitation (inches)
    precipitation_inches DECIMAL(6,3),
    
    -- Other weather parameters
    humidity_percent DECIMAL(5,2),
    wind_speed_mph DECIMAL(5,1),
    wind_direction_degrees INTEGER,
    solar_radiation DECIMAL(8,2),
    
    -- Growing degree days
    gdd_base_50 DECIMAL(6,2),
    gdd_base_86 DECIMAL(6,2),
    
    data_source VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(station_id, observation_date)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- User and authentication indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- Farm and location indexes
CREATE INDEX idx_farms_user_id ON farms(user_id);
CREATE INDEX idx_farms_location ON farms USING GIST(location);
CREATE INDEX idx_fields_farm_id ON fields(farm_id);
CREATE INDEX idx_fields_boundary ON fields USING GIST(field_boundary);

-- Soil test indexes
CREATE INDEX idx_soil_tests_field_id ON soil_tests(field_id);
CREATE INDEX idx_soil_tests_test_date ON soil_tests(test_date);
CREATE INDEX idx_soil_tests_ph ON soil_tests(ph);

-- Crop and rotation indexes
CREATE INDEX idx_crop_varieties_crop_id ON crop_varieties(crop_id);
CREATE INDEX idx_crop_history_field_id ON crop_history(field_id);
CREATE INDEX idx_crop_history_crop_year ON crop_history(crop_year);

-- Fertilizer indexes
CREATE INDEX idx_fertilizer_applications_field_id ON fertilizer_applications(field_id);
CREATE INDEX idx_fertilizer_applications_crop_year ON fertilizer_applications(crop_year);
CREATE INDEX idx_fertilizer_applications_date ON fertilizer_applications(application_date);

-- Recommendation indexes
CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_farm_id ON recommendations(farm_id);
CREATE INDEX idx_recommendations_question_id ON recommendations(question_id);
CREATE INDEX idx_recommendations_created_at ON recommendations(created_at);
CREATE INDEX idx_recommendations_confidence ON recommendations(overall_confidence);

-- Equipment indexes
CREATE INDEX idx_farm_equipment_farm_id ON farm_equipment(farm_id);

-- Weather indexes
CREATE INDEX idx_weather_stations_location ON weather_stations USING GIST(location);
CREATE INDEX idx_weather_data_station_date ON weather_data(station_id, observation_date);
CREATE INDEX idx_weather_data_location ON weather_data USING GIST(location);

-- Full-text search indexes
CREATE INDEX idx_crops_name_trgm ON crops USING gin(crop_name gin_trgm_ops);
CREATE INDEX idx_fertilizer_products_name_trgm ON fertilizer_products USING gin(product_name gin_trgm_ops);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farms_updated_at BEFORE UPDATE ON farms
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fields_updated_at BEFORE UPDATE ON fields
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_recommendations_updated_at BEFORE UPDATE ON recommendations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA POPULATION
-- ============================================================================

-- Insert the 20 key questions
INSERT INTO question_types (question_id, question_text, question_category, priority_level) VALUES
(1, 'What crop varieties are best suited to my soil type and climate?', 'Crop Selection', 1),
(2, 'How can I improve soil fertility without over-applying fertilizer?', 'Soil Management', 1),
(3, 'What is the optimal crop rotation plan for my land?', 'Crop Management', 1),
(4, 'How do I know if my soil is deficient in key nutrients like nitrogen, phosphorus, or potassium?', 'Soil Testing', 1),
(5, 'Should I invest in organic, synthetic, or slow-release fertilizers?', 'Fertilizer Selection', 2),
(6, 'How do I decide between liquid vs. granular fertilizer applications?', 'Fertilizer Application', 2),
(7, 'What are the best times in the season to apply fertilizer for maximum uptake?', 'Fertilizer Timing', 2),
(8, 'How can I reduce fertilizer runoff and environmental impact?', 'Environmental Stewardship', 2),
(9, 'Should I use cover crops, and which ones would benefit my fields most?', 'Cover Crops', 2),
(10, 'How do I manage soil pH to optimize nutrient availability?', 'Soil Chemistry', 2),
(11, 'Which micronutrients (e.g., zinc, boron, sulfur) are worth supplementing in my fields?', 'Micronutrients', 3),
(12, 'How do I assess whether precision agriculture tools (drones, sensors, mapping) are worth the investment?', 'Technology Adoption', 3),
(13, 'What practices will help conserve soil moisture and reduce drought stress?', 'Water Management', 3),
(14, 'How can I detect early signs of crop nutrient deficiencies or toxicities?', 'Crop Monitoring', 3),
(15, 'Should I adopt no-till or reduced-till practices to maintain soil health?', 'Tillage Systems', 3),
(16, 'What is the most cost-effective fertilizer strategy given current input prices?', 'Economic Optimization', 4),
(17, 'How do weather patterns this year affect my fertilizer and crop choices?', 'Weather Integration', 4),
(18, 'How can I use soil testing or tissue testing to fine-tune nutrient management?', 'Testing Integration', 4),
(19, 'What practices will increase my yields without harming long-term soil health?', 'Sustainable Intensification', 4),
(20, 'How do government programs, subsidies, or regulations affect my fertilizer use and land management choices?', 'Policy Compliance', 5);

-- Insert common crop types
INSERT INTO crops (crop_name, scientific_name, crop_category, crop_family, nitrogen_fixing, typical_yield_range_min, typical_yield_range_max, yield_units, growing_degree_days, maturity_days_min, maturity_days_max, optimal_ph_min, optimal_ph_max, drought_tolerance, cold_tolerance) VALUES
('Corn', 'Zea mays', 'grain', 'Poaceae', false, 120, 220, 'bu/acre', 2700, 90, 120, 6.0, 6.8, 'moderate', 'low'),
('Soybean', 'Glycine max', 'oilseed', 'Fabaceae', true, 40, 80, 'bu/acre', 2500, 90, 130, 6.0, 7.0, 'moderate', 'moderate'),
('Wheat', 'Triticum aestivum', 'grain', 'Poaceae', false, 40, 100, 'bu/acre', 2000, 90, 120, 6.0, 7.0, 'moderate', 'high'),
('Cotton', 'Gossypium hirsutum', 'specialty', 'Malvaceae', false, 600, 1200, 'lbs/acre', 3000, 140, 200, 5.8, 8.0, 'high', 'low'),
('Alfalfa', 'Medicago sativa', 'forage', 'Fabaceae', true, 3, 8, 'tons/acre', 2200, 365, 365, 6.5, 7.5, 'high', 'high');

-- Insert common equipment types
INSERT INTO equipment_types (equipment_name, equipment_category, typical_capacity, power_requirements) VALUES
('Planter', 'planting', '4-24 rows', '100-300 HP'),
('Combine Harvester', 'harvesting', '20-40 ft header', '300-600 HP'),
('Field Sprayer', 'spraying', '60-120 ft boom', '150-350 HP'),
('Fertilizer Spreader', 'fertilizer', '1000-3000 lbs', '100-200 HP'),
('Disk Harrow', 'tillage', '15-30 ft', '150-400 HP'),
('No-Till Drill', 'planting', '10-30 ft', '150-300 HP');

-- Create views for common queries
CREATE VIEW farm_summary AS
SELECT 
    f.farm_id,
    f.farm_name,
    f.farm_size_acres,
    f.state,
    f.county,
    u.first_name || ' ' || u.last_name as owner_name,
    COUNT(DISTINCT fi.field_id) as field_count,
    COUNT(DISTINCT st.test_id) as soil_test_count,
    MAX(st.test_date) as latest_soil_test,
    COUNT(DISTINCT r.recommendation_id) as recommendation_count
FROM farms f
JOIN users u ON f.user_id = u.user_id
LEFT JOIN fields fi ON f.farm_id = fi.farm_id
LEFT JOIN soil_tests st ON fi.field_id = st.field_id
LEFT JOIN recommendations r ON f.farm_id = r.farm_id
GROUP BY f.farm_id, f.farm_name, f.farm_size_acres, f.state, f.county, u.first_name, u.last_name;

-- Grant permissions (adjust as needed for your environment)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO afas_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO afas_app;