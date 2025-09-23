-- Farm Location Input Feature Schema
-- Autonomous Farm Advisory System
-- Version: 1.0
-- Date: December 2024

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- FARM LOCATION INPUT TABLES
-- ============================================================================

-- Farm Locations Table (for the location input feature)
CREATE TABLE farm_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    address TEXT,
    county VARCHAR(100),
    state VARCHAR(50),
    climate_zone VARCHAR(20),
    source VARCHAR(20) NOT NULL CHECK (source IN ('gps', 'address', 'map', 'current')),
    verified BOOLEAN DEFAULT FALSE,
    accuracy_meters INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_latitude CHECK (latitude >= -90 AND latitude <= 90),
    CONSTRAINT valid_longitude CHECK (longitude >= -180 AND longitude <= 180)
);

-- Farm Fields Table (extends locations for multiple fields per farm)
CREATE TABLE farm_fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    location_id UUID NOT NULL REFERENCES farm_locations(id) ON DELETE CASCADE,
    field_name VARCHAR(100) NOT NULL,
    field_type VARCHAR(20) DEFAULT 'crop' CHECK (field_type IN ('crop', 'pasture', 'other')),
    size_acres DECIMAL(10, 2),
    soil_type VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Geocoding Cache Table
CREATE TABLE geocoding_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_hash VARCHAR(64) UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    result_json JSONB NOT NULL,
    provider VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Farm Locations indexes
CREATE INDEX idx_farm_locations_user_id ON farm_locations(user_id);
CREATE INDEX idx_farm_locations_coordinates ON farm_locations(latitude, longitude);
CREATE INDEX idx_farm_locations_state_county ON farm_locations(state, county);
CREATE INDEX idx_farm_locations_source ON farm_locations(source);
CREATE INDEX idx_farm_locations_verified ON farm_locations(verified);

-- Farm Fields indexes
CREATE INDEX idx_farm_fields_location_id ON farm_fields(location_id);
CREATE INDEX idx_farm_fields_type ON farm_fields(field_type);

-- Geocoding Cache indexes
CREATE INDEX idx_geocoding_cache_hash ON geocoding_cache(query_hash);
CREATE INDEX idx_geocoding_cache_expires ON geocoding_cache(expires_at);
CREATE INDEX idx_geocoding_cache_provider ON geocoding_cache(provider);

-- ============================================================================
-- TRIGGERS FOR UPDATED_AT TIMESTAMPS
-- ============================================================================

-- Create trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at columns
CREATE TRIGGER update_farm_locations_updated_at 
    BEFORE UPDATE ON farm_locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farm_fields_updated_at 
    BEFORE UPDATE ON farm_fields
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE farm_locations IS 'Farm location data for the location input feature';
COMMENT ON COLUMN farm_locations.source IS 'How the location was input: gps, address, map, or current location';
COMMENT ON COLUMN farm_locations.verified IS 'Whether the location has been verified by the user';
COMMENT ON COLUMN farm_locations.accuracy_meters IS 'GPS accuracy in meters if available';

COMMENT ON TABLE farm_fields IS 'Individual fields within a farm location';
COMMENT ON COLUMN farm_fields.field_type IS 'Type of field: crop, pasture, or other';

COMMENT ON TABLE geocoding_cache IS 'Cache for geocoding API results to improve performance';
COMMENT ON COLUMN geocoding_cache.query_hash IS 'SHA-256 hash of the geocoding query';
COMMENT ON COLUMN geocoding_cache.expires_at IS 'When this cache entry expires';