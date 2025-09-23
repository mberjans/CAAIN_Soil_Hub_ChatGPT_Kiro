-- Rollback Migration: Remove Farm Location Input Tables
-- Version: 001_rollback
-- Date: December 2024
-- Description: Removes tables created for farm location input feature

-- WARNING: This will permanently delete all farm location data!
-- Make sure to backup data before running this rollback.

DO $$
BEGIN
    RAISE NOTICE 'Starting rollback of farm location tables migration';
    RAISE NOTICE 'WARNING: This will permanently delete all farm location data!';
END
$$;

-- Drop triggers first
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_farm_fields_updated_at') THEN
        DROP TRIGGER update_farm_fields_updated_at ON farm_fields;
        RAISE NOTICE 'Dropped trigger update_farm_fields_updated_at';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_farm_locations_updated_at') THEN
        DROP TRIGGER update_farm_locations_updated_at ON farm_locations;
        RAISE NOTICE 'Dropped trigger update_farm_locations_updated_at';
    END IF;
END
$$;

-- Drop indexes
DO $$
BEGIN
    -- Geocoding Cache indexes
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_geocoding_cache_provider') THEN
        DROP INDEX idx_geocoding_cache_provider;
        RAISE NOTICE 'Dropped index idx_geocoding_cache_provider';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_geocoding_cache_expires') THEN
        DROP INDEX idx_geocoding_cache_expires;
        RAISE NOTICE 'Dropped index idx_geocoding_cache_expires';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_geocoding_cache_hash') THEN
        DROP INDEX idx_geocoding_cache_hash;
        RAISE NOTICE 'Dropped index idx_geocoding_cache_hash';
    END IF;
    
    -- Farm Fields indexes
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_fields_type') THEN
        DROP INDEX idx_farm_fields_type;
        RAISE NOTICE 'Dropped index idx_farm_fields_type';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_fields_location_id') THEN
        DROP INDEX idx_farm_fields_location_id;
        RAISE NOTICE 'Dropped index idx_farm_fields_location_id';
    END IF;
    
    -- Farm Locations indexes
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_verified') THEN
        DROP INDEX idx_farm_locations_verified;
        RAISE NOTICE 'Dropped index idx_farm_locations_verified';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_source') THEN
        DROP INDEX idx_farm_locations_source;
        RAISE NOTICE 'Dropped index idx_farm_locations_source';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_state_county') THEN
        DROP INDEX idx_farm_locations_state_county;
        RAISE NOTICE 'Dropped index idx_farm_locations_state_county';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_coordinates') THEN
        DROP INDEX idx_farm_locations_coordinates;
        RAISE NOTICE 'Dropped index idx_farm_locations_coordinates';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_farm_locations_user_id') THEN
        DROP INDEX idx_farm_locations_user_id;
        RAISE NOTICE 'Dropped index idx_farm_locations_user_id';
    END IF;
END
$$;

-- Drop tables in correct order (child tables first)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'geocoding_cache'
    ) THEN
        DROP TABLE geocoding_cache;
        RAISE NOTICE 'Dropped table geocoding_cache';
    END IF;
    
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'farm_fields'
    ) THEN
        DROP TABLE farm_fields;
        RAISE NOTICE 'Dropped table farm_fields';
    END IF;
    
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'farm_locations'
    ) THEN
        DROP TABLE farm_locations;
        RAISE NOTICE 'Dropped table farm_locations';
    END IF;
END
$$;

-- Note: We don't drop the update_updated_at_column function as it might be used by other tables

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Rollback migration 001_rollback_farm_location_tables completed successfully';
    RAISE NOTICE 'All farm location data has been permanently deleted';
END
$$;