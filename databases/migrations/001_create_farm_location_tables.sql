-- Migration: Create Farm Location Input Tables
-- Version: 001
-- Date: December 2024
-- Description: Creates tables for farm location input feature

-- Check if migration has already been applied
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'farm_locations'
    ) THEN
        -- Create farm_locations table
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
        
        RAISE NOTICE 'Created farm_locations table';
    ELSE
        RAISE NOTICE 'farm_locations table already exists, skipping';
    END IF;
END
$$;

-- Check if farm_fields table needs to be created
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'farm_fields'
    ) THEN
        -- Create farm_fields table
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
        
        RAISE NOTICE 'Created farm_fields table';
    ELSE
        RAISE NOTICE 'farm_fields table already exists, skipping';
    END IF;
END
$$;

-- Check if geocoding_cache table needs to be created
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'geocoding_cache'
    ) THEN
        -- Create geocoding_cache table
        CREATE TABLE geocoding_cache (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            query_hash VARCHAR(64) UNIQUE NOT NULL,
            query_text TEXT NOT NULL,
            result_json JSONB NOT NULL,
            provider VARCHAR(50) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL
        );
        
        RAISE NOTICE 'Created geocoding_cache table';
    ELSE
        RAISE NOTICE 'geocoding_cache table already exists, skipping';
    END IF;
END
$$;

-- Create indexes if they don't exist
DO $$
BEGIN
    -- Farm Locations indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_user_id') THEN
        CREATE INDEX idx_farm_locations_user_id ON farm_locations(user_id);
        RAISE NOTICE 'Created index idx_farm_locations_user_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_coordinates') THEN
        CREATE INDEX idx_farm_locations_coordinates ON farm_locations(latitude, longitude);
        RAISE NOTICE 'Created index idx_farm_locations_coordinates';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_state_county') THEN
        CREATE INDEX idx_farm_locations_state_county ON farm_locations(state, county);
        RAISE NOTICE 'Created index idx_farm_locations_state_county';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_source') THEN
        CREATE INDEX idx_farm_locations_source ON farm_locations(source);
        RAISE NOTICE 'Created index idx_farm_locations_source';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_verified') THEN
        CREATE INDEX idx_farm_locations_verified ON farm_locations(verified);
        RAISE NOTICE 'Created index idx_farm_locations_verified';
    END IF;
    
    -- Farm Fields indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_fields_location_id') THEN
        CREATE INDEX idx_farm_fields_location_id ON farm_fields(location_id);
        RAISE NOTICE 'Created index idx_farm_fields_location_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_fields_type') THEN
        CREATE INDEX idx_farm_fields_type ON farm_fields(field_type);
        RAISE NOTICE 'Created index idx_farm_fields_type';
    END IF;
    
    -- Geocoding Cache indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_geocoding_cache_hash') THEN
        CREATE INDEX idx_geocoding_cache_hash ON geocoding_cache(query_hash);
        RAISE NOTICE 'Created index idx_geocoding_cache_hash';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_geocoding_cache_expires') THEN
        CREATE INDEX idx_geocoding_cache_expires ON geocoding_cache(expires_at);
        RAISE NOTICE 'Created index idx_geocoding_cache_expires';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_geocoding_cache_provider') THEN
        CREATE INDEX idx_geocoding_cache_provider ON geocoding_cache(provider);
        RAISE NOTICE 'Created index idx_geocoding_cache_provider';
    END IF;
END
$$;

-- Create triggers for updated_at columns
DO $$
BEGIN
    -- Create trigger function if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'update_updated_at_column') THEN
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $trigger$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $trigger$ language 'plpgsql';
        
        RAISE NOTICE 'Created update_updated_at_column function';
    END IF;
    
    -- Add triggers if they don't exist
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_farm_locations_updated_at') THEN
        CREATE TRIGGER update_farm_locations_updated_at 
            BEFORE UPDATE ON farm_locations
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_farm_locations_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_farm_fields_updated_at') THEN
        CREATE TRIGGER update_farm_fields_updated_at 
            BEFORE UPDATE ON farm_fields
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_farm_fields_updated_at';
    END IF;
END
$$;

-- Add comments for documentation
COMMENT ON TABLE farm_locations IS 'Farm location data for the location input feature';
COMMENT ON COLUMN farm_locations.source IS 'How the location was input: gps, address, map, or current location';
COMMENT ON COLUMN farm_locations.verified IS 'Whether the location has been verified by the user';
COMMENT ON COLUMN farm_locations.accuracy_meters IS 'GPS accuracy in meters if available';

COMMENT ON TABLE farm_fields IS 'Individual fields within a farm location';
COMMENT ON COLUMN farm_fields.field_type IS 'Type of field: crop, pasture, or other';

COMMENT ON TABLE geocoding_cache IS 'Cache for geocoding API results to improve performance';
COMMENT ON COLUMN geocoding_cache.query_hash IS 'SHA-256 hash of the geocoding query';
COMMENT ON COLUMN geocoding_cache.expires_at IS 'When this cache entry expires';

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_create_farm_location_tables completed successfully';
END
$$;