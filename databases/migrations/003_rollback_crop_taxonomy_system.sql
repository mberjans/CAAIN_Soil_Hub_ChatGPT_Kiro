-- Rollback Migration: Remove Comprehensive Crop Taxonomy System
-- Version: 003_rollback
-- Date: December 2024
-- Description: Removes crop taxonomy system tables and enhancements for TICKET-005

-- Remove foreign key columns from crops table first
DO $$
BEGIN
    -- Remove new columns from crops table
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'taxonomy_id') THEN
        ALTER TABLE crops DROP COLUMN taxonomy_id;
        RAISE NOTICE 'Removed taxonomy_id column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'agricultural_classification_id') THEN
        ALTER TABLE crops DROP COLUMN agricultural_classification_id;
        RAISE NOTICE 'Removed agricultural_classification_id column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'climate_adaptation_id') THEN
        ALTER TABLE crops DROP COLUMN climate_adaptation_id;
        RAISE NOTICE 'Removed climate_adaptation_id column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'soil_requirements_id') THEN
        ALTER TABLE crops DROP COLUMN soil_requirements_id;
        RAISE NOTICE 'Removed soil_requirements_id column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'nutritional_profile_id') THEN
        ALTER TABLE crops DROP COLUMN nutritional_profile_id;
        RAISE NOTICE 'Removed nutritional_profile_id column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'filtering_attributes_id') THEN
        ALTER TABLE crops DROP COLUMN filtering_attributes_id;
        RAISE NOTICE 'Removed filtering_attributes_id column from crops table';
    END IF;
    
    -- Remove enhanced search fields
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'crop_code') THEN
        ALTER TABLE crops DROP COLUMN crop_code;
        RAISE NOTICE 'Removed crop_code column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'fao_crop_code') THEN
        ALTER TABLE crops DROP COLUMN fao_crop_code;
        RAISE NOTICE 'Removed fao_crop_code column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'usda_crop_code') THEN
        ALTER TABLE crops DROP COLUMN usda_crop_code;
        RAISE NOTICE 'Removed usda_crop_code column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'search_keywords') THEN
        ALTER TABLE crops DROP COLUMN search_keywords;
        RAISE NOTICE 'Removed search_keywords column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'tags') THEN
        ALTER TABLE crops DROP COLUMN tags;
        RAISE NOTICE 'Removed tags column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'is_cover_crop') THEN
        ALTER TABLE crops DROP COLUMN is_cover_crop;
        RAISE NOTICE 'Removed is_cover_crop column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'is_companion_crop') THEN
        ALTER TABLE crops DROP COLUMN is_companion_crop;
        RAISE NOTICE 'Removed is_companion_crop column from crops table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'crop_status') THEN
        ALTER TABLE crops DROP COLUMN crop_status;
        RAISE NOTICE 'Removed crop_status column from crops table';
    END IF;
END
$$;

-- Drop taxonomy tables (in reverse dependency order)
DO $$
BEGIN
    -- Drop tables that reference crops
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_regional_adaptations') THEN
        DROP TABLE crop_regional_adaptations CASCADE;
        RAISE NOTICE 'Dropped crop_regional_adaptations table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'enhanced_crop_varieties') THEN
        DROP TABLE enhanced_crop_varieties CASCADE;
        RAISE NOTICE 'Dropped enhanced_crop_varieties table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_attribute_tags') THEN
        DROP TABLE crop_attribute_tags CASCADE;
        RAISE NOTICE 'Dropped crop_attribute_tags table';
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_filtering_attributes') THEN
        DROP TABLE crop_filtering_attributes CASCADE;
        RAISE NOTICE 'Dropped crop_filtering_attributes table';
    END IF;
    
    -- Drop standalone taxonomy tables
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_nutritional_profiles') THEN
        DROP TABLE crop_nutritional_profiles CASCADE;
        RAISE NOTICE 'Dropped crop_nutritional_profiles table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_soil_requirements') THEN
        DROP TABLE crop_soil_requirements CASCADE;
        RAISE NOTICE 'Dropped crop_soil_requirements table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_climate_adaptations') THEN
        DROP TABLE crop_climate_adaptations CASCADE;
        RAISE NOTICE 'Dropped crop_climate_adaptations table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_agricultural_classification') THEN
        DROP TABLE crop_agricultural_classification CASCADE;
        RAISE NOTICE 'Dropped crop_agricultural_classification table';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'crop_taxonomic_hierarchy') THEN
        DROP TABLE crop_taxonomic_hierarchy CASCADE;
        RAISE NOTICE 'Dropped crop_taxonomic_hierarchy table';
    END IF;
END
$$;

-- Drop functions that were created for the taxonomy system
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'search_crops_advanced') THEN
        DROP FUNCTION search_crops_advanced CASCADE;
        RAISE NOTICE 'Dropped search_crops_advanced function';
    END IF;
    
    IF EXISTS (SELECT 1 FROM pg_proc WHERE proname = 'get_crop_rotation_compatibility') THEN
        DROP FUNCTION get_crop_rotation_compatibility CASCADE;
        RAISE NOTICE 'Dropped get_crop_rotation_compatibility function';
    END IF;
END
$$;

-- Drop views that were created for the taxonomy system
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'comprehensive_crop_view') THEN
        DROP VIEW comprehensive_crop_view CASCADE;
        RAISE NOTICE 'Dropped comprehensive_crop_view';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'enhanced_crop_varieties_view') THEN
        DROP VIEW enhanced_crop_varieties_view CASCADE;
        RAISE NOTICE 'Dropped enhanced_crop_varieties_view';
    END IF;
    
    IF EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'regional_crop_suitability_view') THEN
        DROP VIEW regional_crop_suitability_view CASCADE;
        RAISE NOTICE 'Dropped regional_crop_suitability_view';
    END IF;
END
$$;

-- Note: Indexes are automatically dropped when tables are dropped

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Rollback 003_rollback_crop_taxonomy_system completed successfully';
    RAISE NOTICE 'All crop taxonomy system components have been removed';
END
$$;
