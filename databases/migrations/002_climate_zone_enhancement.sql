-- Climate Zone Database Schema Migration
-- TICKET-001_climate-zone-detection-4.3: Create climate zone database schema updates
-- Autonomous Farm Advisory System
-- Version: 1.1
-- Date: December 2024

-- This migration adds comprehensive climate zone support to the database
-- integrating with the enhanced weather service capabilities

BEGIN TRANSACTION;

-- ============================================================================
-- NEW CLIMATE ZONE TABLES
-- ============================================================================

-- Climate Zone Data Table - stores detailed climate information for locations
CREATE TABLE climate_zone_data (
    climate_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    
    -- USDA Hardiness Zone Information
    usda_zone VARCHAR(10) NOT NULL,
    usda_zone_confidence DECIMAL(3,2) CHECK (usda_zone_confidence BETWEEN 0 AND 1),
    
    -- Köppen Climate Classification
    koppen_classification VARCHAR(10),
    koppen_description TEXT,
    
    -- Temperature Profile (Fahrenheit)
    average_min_temp_f DECIMAL(6,2),
    average_max_temp_f DECIMAL(6,2),
    extreme_min_temp_f DECIMAL(6,2),
    extreme_max_temp_f DECIMAL(6,2),
    
    -- Precipitation Profile (inches)
    annual_precipitation_inches DECIMAL(6,2),
    wet_season_months INTEGER[], -- Array of months (1-12)
    dry_season_months INTEGER[], -- Array of months (1-12)
    
    -- Growing Season Information
    growing_season_length INTEGER, -- days
    last_frost_date DATE, -- typical last frost date (year-agnostic)
    first_frost_date DATE, -- typical first frost date (year-agnostic)
    frost_free_days INTEGER,
    
    -- Agricultural Suitability
    agricultural_suitability_score DECIMAL(3,2) CHECK (agricultural_suitability_score BETWEEN 0 AND 1),
    agricultural_category VARCHAR(20) CHECK (agricultural_category IN ('Excellent', 'Good', 'Moderate', 'Challenging', 'Difficult')),
    limiting_factors TEXT[], -- Array of limiting factors
    recommendations TEXT[], -- Array of agricultural recommendations
    
    -- Data Sources and Quality
    data_sources TEXT[], -- Array of data sources used
    historical_years_analyzed INTEGER, -- Number of years of historical data used
    data_quality_score DECIMAL(3,2) CHECK (data_quality_score BETWEEN 0 AND 1),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Caching and Performance
    cache_expires_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT valid_latitude CHECK (latitude >= -90 AND latitude <= 90),
    CONSTRAINT valid_longitude CHECK (longitude >= -180 AND longitude <= 180),
    CONSTRAINT valid_frost_dates CHECK (first_frost_date IS NULL OR last_frost_date IS NULL OR first_frost_date > last_frost_date)
);

-- Historical Climate Data Table - for storing historical weather patterns used in analysis
CREATE TABLE historical_climate_patterns (
    pattern_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    climate_id UUID NOT NULL REFERENCES climate_zone_data(climate_id) ON DELETE CASCADE,
    
    -- Temperature Patterns
    monthly_avg_temps DECIMAL(6,2)[], -- 12 values for each month
    monthly_min_temps DECIMAL(6,2)[], -- 12 values for each month
    monthly_max_temps DECIMAL(6,2)[], -- 12 values for each month
    
    -- Precipitation Patterns
    monthly_precipitation DECIMAL(6,2)[], -- 12 values for each month
    
    -- Growing Degree Days
    monthly_gdd_base_50 DECIMAL(8,2)[], -- 12 values
    monthly_gdd_base_86 DECIMAL(8,2)[], -- 12 values
    
    -- Extreme Weather Events
    heat_wave_frequency DECIMAL(5,2), -- Average heat waves per year
    cold_snap_frequency DECIMAL(5,2), -- Average cold snaps per year
    drought_frequency DECIMAL(5,2), -- Average droughts per decade
    
    -- Data Metadata
    years_analyzed INTEGER NOT NULL,
    data_start_year INTEGER,
    data_end_year INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Climate Zone Cache Table - for caching weather service responses
CREATE TABLE climate_zone_cache (
    cache_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_hash VARCHAR(64) UNIQUE NOT NULL, -- Hash of lat/lon for fast lookup
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    
    -- Cached Response Data
    climate_data_json JSONB NOT NULL, -- Full climate analysis response
    weather_service_response JSONB, -- Raw weather service response
    
    -- Cache Management
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Performance Metadata
    generation_time_ms INTEGER, -- Time taken to generate this data
    data_source VARCHAR(100) -- Source of the climate data
);

-- ============================================================================
-- UPDATE EXISTING TABLES
-- ============================================================================

-- Add enhanced climate zone fields to farms table
ALTER TABLE farms ADD COLUMN IF NOT EXISTS climate_zone_data_id UUID REFERENCES climate_zone_data(climate_id);
ALTER TABLE farms ADD COLUMN IF NOT EXISTS koppen_classification VARCHAR(10);
ALTER TABLE farms ADD COLUMN IF NOT EXISTS growing_season_length INTEGER;
ALTER TABLE farms ADD COLUMN IF NOT EXISTS agricultural_suitability_score DECIMAL(3,2) CHECK (agricultural_suitability_score BETWEEN 0 AND 1);
ALTER TABLE farms ADD COLUMN IF NOT EXISTS climate_analysis_date TIMESTAMP WITH TIME ZONE;

-- Add climate zone integration to farm_locations table (for location validation service)
ALTER TABLE farm_locations ADD COLUMN IF NOT EXISTS climate_zone_data_id UUID REFERENCES climate_zone_data(climate_id);
ALTER TABLE farm_locations ADD COLUMN IF NOT EXISTS koppen_classification VARCHAR(10);
ALTER TABLE farm_locations ADD COLUMN IF NOT EXISTS agricultural_suitability_score DECIMAL(3,2) CHECK (agricultural_suitability_score BETWEEN 0 AND 1);
ALTER TABLE farm_locations ADD COLUMN IF NOT EXISTS climate_analysis_json JSONB; -- Store full climate analysis for location validation
ALTER TABLE farm_locations ADD COLUMN IF NOT EXISTS climate_validated_at TIMESTAMP WITH TIME ZONE;

-- Update weather_data table to support climate zone analysis
ALTER TABLE weather_data ADD COLUMN IF NOT EXISTS climate_zone VARCHAR(10);
ALTER TABLE weather_data ADD COLUMN IF NOT EXISTS koppen_classification VARCHAR(10);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Climate Zone Data indexes
CREATE INDEX idx_climate_zone_data_coordinates ON climate_zone_data(latitude, longitude);
CREATE INDEX idx_climate_zone_data_usda_zone ON climate_zone_data(usda_zone);
CREATE INDEX idx_climate_zone_data_koppen ON climate_zone_data(koppen_classification);
CREATE INDEX idx_climate_zone_data_suitability ON climate_zone_data(agricultural_suitability_score);
CREATE INDEX idx_climate_zone_data_last_updated ON climate_zone_data(last_updated);
CREATE INDEX idx_climate_zone_data_cache_expires ON climate_zone_data(cache_expires_at);

-- Historical patterns indexes
CREATE INDEX idx_historical_patterns_climate_id ON historical_climate_patterns(climate_id);
CREATE INDEX idx_historical_patterns_years ON historical_climate_patterns(data_start_year, data_end_year);

-- Climate cache indexes
CREATE INDEX idx_climate_cache_hash ON climate_zone_cache(location_hash);
CREATE INDEX idx_climate_cache_coordinates ON climate_zone_cache(latitude, longitude);
CREATE INDEX idx_climate_cache_expires ON climate_zone_cache(expires_at);
CREATE INDEX idx_climate_cache_accessed ON climate_zone_cache(last_accessed);

-- Updated farm indexes
CREATE INDEX idx_farms_climate_zone_data ON farms(climate_zone_data_id);
CREATE INDEX idx_farms_koppen ON farms(koppen_classification);
CREATE INDEX idx_farms_agricultural_suitability ON farms(agricultural_suitability_score);

-- Updated farm_locations indexes
CREATE INDEX idx_farm_locations_climate_zone_data ON farm_locations(climate_zone_data_id);
CREATE INDEX idx_farm_locations_climate_validated ON farm_locations(climate_validated_at);

-- Updated weather_data indexes
CREATE INDEX idx_weather_data_climate_zone ON weather_data(climate_zone);
CREATE INDEX idx_weather_data_koppen ON weather_data(koppen_classification);

-- Composite indexes for common queries
CREATE INDEX idx_climate_zone_coords_zone ON climate_zone_data(latitude, longitude, usda_zone);
CREATE INDEX idx_farms_location_climate ON farms(state, county, usda_hardiness_zone);

-- GiST indexes for spatial queries (if PostGIS is available)
-- These will help with finding climate data for nearby locations
-- Note: This index creation is conditional and may fail gracefully
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN
        CREATE INDEX idx_climate_zone_data_spatial ON climate_zone_data USING GIST(
            ll_to_earth(latitude, longitude)
        );
        RAISE NOTICE 'Created PostGIS spatial index for climate zone data';
    ELSE
        RAISE NOTICE 'PostGIS not available, skipping spatial index creation';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not create spatial index (PostGIS may not be available): %', SQLERRM;
END $$;

-- ============================================================================
-- TRIGGERS FOR MAINTENANCE
-- ============================================================================

-- Trigger to update access count and last_accessed on cache access
CREATE OR REPLACE FUNCTION update_climate_cache_access()
RETURNS TRIGGER AS $$
BEGIN
    NEW.access_count = OLD.access_count + 1;
    NEW.last_accessed = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_climate_cache_access_trigger
    BEFORE UPDATE ON climate_zone_cache
    FOR EACH ROW
    WHEN (OLD.cache_id = NEW.cache_id) -- Only when not changing the primary key
    EXECUTE FUNCTION update_climate_cache_access();

-- Trigger to automatically expire old cache entries
CREATE OR REPLACE FUNCTION cleanup_expired_climate_cache()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM climate_zone_cache 
    WHERE expires_at < CURRENT_TIMESTAMP - INTERVAL '1 day';
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Run cache cleanup on INSERT (to avoid running too frequently)
CREATE TRIGGER cleanup_climate_cache_trigger
    AFTER INSERT ON climate_zone_cache
    FOR EACH STATEMENT
    EXECUTE FUNCTION cleanup_expired_climate_cache();

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- View for farms with complete climate information
CREATE VIEW farms_with_climate AS
SELECT 
    f.farm_id,
    f.farm_name,
    f.farm_size_acres,
    f.state,
    f.county,
    f.usda_hardiness_zone,
    f.climate_zone_data_id,
    f.koppen_classification,
    f.agricultural_suitability_score,
    
    -- Climate zone details
    czd.usda_zone as detailed_usda_zone,
    czd.usda_zone_confidence,
    czd.koppen_description,
    czd.average_min_temp_f,
    czd.average_max_temp_f,
    czd.annual_precipitation_inches,
    czd.growing_season_length,
    czd.agricultural_category,
    czd.limiting_factors,
    czd.recommendations,
    
    -- Farm owner
    u.first_name || ' ' || u.last_name as owner_name
FROM farms f
JOIN users u ON f.user_id = u.user_id
LEFT JOIN climate_zone_data czd ON f.climate_zone_data_id = czd.climate_id;

-- View for location validation with climate data
CREATE VIEW farm_locations_with_climate AS
SELECT 
    fl.id,
    fl.user_id,
    fl.name,
    fl.latitude,
    fl.longitude,
    fl.address,
    fl.county,
    fl.state,
    fl.climate_zone,
    fl.verified,
    fl.climate_zone_data_id,
    fl.koppen_classification,
    fl.agricultural_suitability_score,
    fl.climate_analysis_json,
    
    -- Climate zone details
    czd.usda_zone,
    czd.koppen_description,
    czd.growing_season_length,
    czd.agricultural_category,
    czd.limiting_factors,
    czd.average_min_temp_f,
    czd.average_max_temp_f,
    czd.annual_precipitation_inches
FROM farm_locations fl
LEFT JOIN climate_zone_data czd ON fl.climate_zone_data_id = czd.climate_id;

-- View for climate zone summary statistics
CREATE VIEW climate_zone_summary AS
SELECT 
    usda_zone,
    koppen_classification,
    COUNT(*) as location_count,
    AVG(agricultural_suitability_score) as avg_suitability,
    AVG(growing_season_length) as avg_growing_season,
    AVG(annual_precipitation_inches) as avg_precipitation,
    AVG(average_min_temp_f) as avg_min_temp,
    AVG(average_max_temp_f) as avg_max_temp
FROM climate_zone_data
GROUP BY usda_zone, koppen_classification;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to check if PostGIS is available
CREATE OR REPLACE FUNCTION postgis_available()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'postgis'
    );
END;
$$ language 'plpgsql';

-- Function to find nearest climate zone data
CREATE OR REPLACE FUNCTION find_nearest_climate_zone(
    search_lat DECIMAL(10,8),
    search_lon DECIMAL(11,8),
    max_distance_km DECIMAL DEFAULT 50
)
RETURNS UUID AS $$
DECLARE
    nearest_climate_id UUID;
BEGIN
    SELECT climate_id INTO nearest_climate_id
    FROM climate_zone_data
    ORDER BY (
        6371 * acos(
            cos(radians(search_lat)) 
            * cos(radians(latitude)) 
            * cos(radians(longitude) - radians(search_lon)) 
            + sin(radians(search_lat)) 
            * sin(radians(latitude))
        )
    ) ASC
    LIMIT 1;
    
    RETURN nearest_climate_id;
END;
$$ language 'plpgsql';

-- Function to calculate distance between two lat/lon points
CREATE OR REPLACE FUNCTION calculate_distance_km(
    lat1 DECIMAL(10,8),
    lon1 DECIMAL(11,8),
    lat2 DECIMAL(10,8),
    lon2 DECIMAL(11,8)
)
RETURNS DECIMAL AS $$
BEGIN
    RETURN 6371 * acos(
        cos(radians(lat1)) 
        * cos(radians(lat2)) 
        * cos(radians(lon2) - radians(lon1)) 
        + sin(radians(lat1)) 
        * sin(radians(lat2))
    );
END;
$$ language 'plpgsql';

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE climate_zone_data IS 'Comprehensive climate zone information for locations';
COMMENT ON COLUMN climate_zone_data.usda_zone IS 'USDA Hardiness Zone (e.g., 7b, 8a)';
COMMENT ON COLUMN climate_zone_data.koppen_classification IS 'Köppen climate classification (e.g., Cfa, Dfb)';
COMMENT ON COLUMN climate_zone_data.agricultural_suitability_score IS 'Overall agricultural suitability (0-1)';
COMMENT ON COLUMN climate_zone_data.limiting_factors IS 'Array of factors that limit agricultural production';
COMMENT ON COLUMN climate_zone_data.recommendations IS 'Array of agricultural recommendations for this climate';

COMMENT ON TABLE historical_climate_patterns IS 'Historical weather patterns used for climate zone analysis';
COMMENT ON COLUMN historical_climate_patterns.monthly_avg_temps IS 'Average temperature for each month (Jan-Dec)';
COMMENT ON COLUMN historical_climate_patterns.monthly_precipitation IS 'Average precipitation for each month (Jan-Dec)';

COMMENT ON TABLE climate_zone_cache IS 'Cache for weather service climate zone responses';
COMMENT ON COLUMN climate_zone_cache.location_hash IS 'SHA-256 hash of latitude,longitude for fast lookup';
COMMENT ON COLUMN climate_zone_cache.climate_data_json IS 'Complete climate analysis response as JSON';

COMMENT ON VIEW farms_with_climate IS 'Farms with complete climate zone information';
COMMENT ON VIEW farm_locations_with_climate IS 'Farm locations with climate validation data';
COMMENT ON VIEW climate_zone_summary IS 'Summary statistics for climate zones';

-- ============================================================================
-- INITIAL DATA AND VALIDATION
-- ============================================================================

-- Validate that the migration was successful
DO $$
BEGIN
    -- Check that new tables exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'climate_zone_data') THEN
        RAISE EXCEPTION 'Climate zone data table was not created successfully';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'historical_climate_patterns') THEN
        RAISE EXCEPTION 'Historical climate patterns table was not created successfully';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'climate_zone_cache') THEN
        RAISE EXCEPTION 'Climate zone cache table was not created successfully';
    END IF;
    
    -- Check that views were created
    IF NOT EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'farms_with_climate') THEN
        RAISE EXCEPTION 'Farms with climate view was not created successfully';
    END IF;
    
    RAISE NOTICE 'Climate zone database schema migration completed successfully';
END $$;

COMMIT;