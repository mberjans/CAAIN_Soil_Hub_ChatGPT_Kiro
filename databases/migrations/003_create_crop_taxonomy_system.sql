-- Migration: Create Comprehensive Crop Taxonomy System
-- Version: 003
-- Date: December 2024
-- Description: Extends existing crops table with comprehensive taxonomic classification for TICKET-005

-- Check if migration has already been applied
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'crop_taxonomic_hierarchy'
    ) THEN
        RAISE NOTICE 'Starting crop taxonomy system migration...';
        
        -- ============================================================================
        -- ENHANCED CROP TAXONOMY TABLES
        -- ============================================================================
        
        -- Botanical classification hierarchy table
        CREATE TABLE crop_taxonomic_hierarchy (
            taxonomy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            kingdom VARCHAR(50) NOT NULL DEFAULT 'Plantae',
            phylum VARCHAR(50) NOT NULL DEFAULT 'Magnoliophyta',
            class VARCHAR(50) NOT NULL,
            order_name VARCHAR(50) NOT NULL,
            family VARCHAR(100) NOT NULL,
            genus VARCHAR(100) NOT NULL,
            species VARCHAR(100) NOT NULL,
            subspecies VARCHAR(100),
            variety VARCHAR(100),
            cultivar VARCHAR(100),
            common_synonyms TEXT[],
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            -- Ensure unique scientific classification
            UNIQUE(kingdom, phylum, class, order_name, family, genus, species, subspecies, variety)
        );
        RAISE NOTICE 'Created crop_taxonomic_hierarchy table';
        
        -- Agricultural classification and characteristics
        CREATE TABLE crop_agricultural_classification (
            classification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            
            -- Primary agricultural categories
            crop_category VARCHAR(50) NOT NULL CHECK (crop_category IN (
                'grain', 'oilseed', 'forage', 'vegetable', 'fruit', 'specialty', 
                'legume', 'cereal', 'root_crop', 'leafy_green', 'herb_spice', 
                'fiber', 'sugar_crop', 'cover_crop', 'ornamental', 'medicinal'
            )),
            crop_subcategory VARCHAR(100),
            
            -- Agricultural use classifications
            primary_use VARCHAR(50) CHECK (primary_use IN (
                'food_human', 'feed_livestock', 'industrial', 'soil_improvement', 
                'ornamental', 'medicinal', 'fiber', 'biofuel', 'dual_purpose'
            )),
            secondary_uses TEXT[],
            
            -- Growth characteristics for filtering
            growth_habit VARCHAR(50) CHECK (growth_habit IN (
                'annual', 'biennial', 'perennial', 'semi_perennial'
            )),
            plant_type VARCHAR(50) CHECK (plant_type IN (
                'grass', 'herb', 'shrub', 'tree', 'vine', 'succulent'
            )),
            growth_form VARCHAR(50) CHECK (growth_form IN (
                'upright', 'spreading', 'climbing', 'trailing', 'rosette', 'bushy'
            )),
            
            -- Size classifications for space planning
            mature_height_min_inches INTEGER,
            mature_height_max_inches INTEGER,
            mature_width_min_inches INTEGER,
            mature_width_max_inches INTEGER,
            root_system_type VARCHAR(50) CHECK (root_system_type IN (
                'fibrous', 'taproot', 'rhizome', 'bulb', 'tuber', 'corm'
            )),
            
            -- Photosynthesis and metabolic characteristics
            photosynthesis_type VARCHAR(10) CHECK (photosynthesis_type IN ('C3', 'C4', 'CAM')),
            nitrogen_fixing BOOLEAN DEFAULT false,
            mycorrhizal_associations BOOLEAN DEFAULT true,
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Created crop_agricultural_classification table';
        
        -- Climate and environmental adaptations
        CREATE TABLE crop_climate_adaptations (
            adaptation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            
            -- Temperature requirements and tolerances
            optimal_temp_min_f DECIMAL(5,1),
            optimal_temp_max_f DECIMAL(5,1),
            absolute_temp_min_f DECIMAL(5,1),
            absolute_temp_max_f DECIMAL(5,1),
            frost_tolerance VARCHAR(20) CHECK (frost_tolerance IN ('none', 'light', 'moderate', 'heavy')),
            heat_tolerance VARCHAR(20) CHECK (heat_tolerance IN ('low', 'moderate', 'high', 'extreme')),
            
            -- USDA hardiness zones
            hardiness_zone_min VARCHAR(5),
            hardiness_zone_max VARCHAR(5),
            hardiness_zones TEXT[], -- Array of suitable zones
            
            -- Precipitation and water requirements
            annual_precipitation_min_inches DECIMAL(5,1),
            annual_precipitation_max_inches DECIMAL(5,1),
            water_requirement VARCHAR(20) CHECK (water_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
            drought_tolerance VARCHAR(20) CHECK (drought_tolerance IN ('none', 'low', 'moderate', 'high', 'extreme')),
            flooding_tolerance VARCHAR(20) CHECK (flooding_tolerance IN ('none', 'brief', 'moderate', 'extended')),
            
            -- Seasonal adaptations
            photoperiod_sensitivity VARCHAR(20) CHECK (photoperiod_sensitivity IN ('none', 'short_day', 'long_day', 'day_neutral')),
            vernalization_requirement BOOLEAN DEFAULT false,
            vernalization_days INTEGER,
            
            -- Altitude and geographic adaptations
            elevation_min_feet INTEGER,
            elevation_max_feet INTEGER,
            latitude_range_min DECIMAL(6,3),
            latitude_range_max DECIMAL(6,3),
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Created crop_climate_adaptations table';
        
        -- Soil requirements and tolerances
        CREATE TABLE crop_soil_requirements (
            soil_req_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            
            -- pH requirements
            optimal_ph_min DECIMAL(3,1) CHECK (optimal_ph_min >= 3.0 AND optimal_ph_min <= 10.0),
            optimal_ph_max DECIMAL(3,1) CHECK (optimal_ph_max >= 3.0 AND optimal_ph_max <= 10.0),
            tolerable_ph_min DECIMAL(3,1) CHECK (tolerable_ph_min >= 3.0 AND tolerable_ph_min <= 10.0),
            tolerable_ph_max DECIMAL(3,1) CHECK (tolerable_ph_max >= 3.0 AND tolerable_ph_max <= 10.0),
            
            -- Soil texture preferences
            preferred_textures TEXT[] DEFAULT ARRAY['loam', 'sandy_loam', 'clay_loam'],
            tolerable_textures TEXT[],
            
            -- Drainage requirements
            drainage_requirement VARCHAR(30) CHECK (drainage_requirement IN (
                'well_drained', 'moderately_well_drained', 'somewhat_poorly_drained', 
                'poorly_drained', 'very_poorly_drained', 'excessive_drained'
            )),
            drainage_tolerance TEXT[],
            
            -- Soil chemical tolerances
            salinity_tolerance VARCHAR(20) CHECK (salinity_tolerance IN ('none', 'low', 'moderate', 'high')),
            alkalinity_tolerance VARCHAR(20) CHECK (alkalinity_tolerance IN ('none', 'low', 'moderate', 'high')),
            acidity_tolerance VARCHAR(20) CHECK (acidity_tolerance IN ('none', 'low', 'moderate', 'high')),
            
            -- Nutrient preferences
            nitrogen_requirement VARCHAR(20) CHECK (nitrogen_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
            phosphorus_requirement VARCHAR(20) CHECK (phosphorus_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
            potassium_requirement VARCHAR(20) CHECK (potassium_requirement IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
            
            -- Soil structure preferences
            compaction_tolerance VARCHAR(20) CHECK (compaction_tolerance IN ('none', 'low', 'moderate', 'high')),
            organic_matter_preference VARCHAR(20) CHECK (organic_matter_preference IN ('low', 'moderate', 'high', 'very_high')),
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            -- Constraint to ensure pH ranges are logical
            CONSTRAINT soil_ph_ranges CHECK (
                optimal_ph_min <= optimal_ph_max AND
                tolerable_ph_min <= tolerable_ph_max AND
                tolerable_ph_min <= optimal_ph_min AND
                optimal_ph_max <= tolerable_ph_max
            )
        );
        RAISE NOTICE 'Created crop_soil_requirements table';
        
        -- Nutritional and composition data
        CREATE TABLE crop_nutritional_profiles (
            nutrition_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            
            -- Macronutrients (per 100g fresh weight)
            calories_per_100g DECIMAL(6,2),
            protein_g_per_100g DECIMAL(5,2),
            carbohydrates_g_per_100g DECIMAL(5,2),
            fiber_g_per_100g DECIMAL(5,2),
            fat_g_per_100g DECIMAL(5,2),
            sugar_g_per_100g DECIMAL(5,2),
            
            -- Minerals (mg per 100g unless specified)
            calcium_mg DECIMAL(7,2),
            iron_mg DECIMAL(6,2),
            magnesium_mg DECIMAL(6,2),
            phosphorus_mg DECIMAL(7,2),
            potassium_mg DECIMAL(8,2),
            sodium_mg DECIMAL(7,2),
            zinc_mg DECIMAL(5,2),
            
            -- Vitamins
            vitamin_c_mg DECIMAL(6,2),
            vitamin_a_iu INTEGER,
            vitamin_k_mcg DECIMAL(6,2),
            folate_mcg DECIMAL(6,2),
            
            -- Specialized compounds
            antioxidant_capacity_orac INTEGER,
            phenolic_compounds_mg DECIMAL(7,2),
            
            -- Feed value (for livestock crops)
            crude_protein_percent DECIMAL(5,2),
            digestible_energy_mcal_kg DECIMAL(4,2),
            neutral_detergent_fiber_percent DECIMAL(5,2),
            
            -- Industrial/commercial values
            oil_content_percent DECIMAL(5,2),
            starch_content_percent DECIMAL(5,2),
            cellulose_content_percent DECIMAL(5,2),
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Created crop_nutritional_profiles table';
        
        -- Enhanced crop varieties with detailed characteristics
        CREATE TABLE enhanced_crop_varieties (
            variety_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            crop_id UUID NOT NULL REFERENCES crops(crop_id) ON DELETE CASCADE,
            
            -- Variety identification
            variety_name VARCHAR(200) NOT NULL,
            variety_code VARCHAR(50),
            breeder_company VARCHAR(150),
            parent_varieties TEXT[],
            
            -- Maturity and timing
            relative_maturity INTEGER, -- Relative maturity units or days
            maturity_group VARCHAR(10),
            days_to_emergence INTEGER,
            days_to_flowering INTEGER,
            days_to_physiological_maturity INTEGER,
            
            -- Performance characteristics
            yield_potential_percentile INTEGER CHECK (yield_potential_percentile >= 0 AND yield_potential_percentile <= 100),
            yield_stability_rating INTEGER CHECK (yield_stability_rating >= 1 AND yield_stability_rating <= 10),
            standability_rating INTEGER CHECK (standability_rating >= 1 AND standability_rating <= 10),
            
            -- Resistance and tolerance traits
            disease_resistances JSONB, -- Structured disease resistance data
            pest_resistances JSONB, -- Structured pest resistance data
            herbicide_tolerances TEXT[],
            stress_tolerances TEXT[], -- drought, heat, cold, etc.
            
            -- Quality traits
            quality_characteristics JSONB, -- Structured quality data
            protein_content_range VARCHAR(20),
            oil_content_range VARCHAR(20),
            
            -- Adaptation and recommendations
            adapted_regions TEXT[],
            recommended_planting_populations JSONB, -- By region/conditions
            special_management_notes TEXT,
            
            -- Commercial information
            seed_availability VARCHAR(20) CHECK (seed_availability IN ('widely_available', 'limited', 'specialty', 'research_only')),
            relative_seed_cost VARCHAR(20) CHECK (relative_seed_cost IN ('low', 'moderate', 'high', 'premium')),
            technology_package VARCHAR(100), -- Associated tech package if any
            
            -- Regulatory and certification
            organic_approved BOOLEAN DEFAULT NULL,
            non_gmo_certified BOOLEAN DEFAULT NULL,
            registration_year INTEGER,
            patent_protected BOOLEAN DEFAULT false,
            
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            
            UNIQUE(crop_id, variety_name, breeder_company)
        );
        RAISE NOTICE 'Created enhanced_crop_varieties table';
        
        -- Regional crop adaptations and recommendations
        CREATE TABLE crop_regional_adaptations (
            adaptation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            crop_id UUID NOT NULL REFERENCES crops(crop_id) ON DELETE CASCADE,
            
            -- Geographic scope
            region_name VARCHAR(100) NOT NULL,
            region_type VARCHAR(50) CHECK (region_type IN (
                'state', 'multi_state', 'county', 'climate_zone', 'ecoregion', 'custom'
            )),
            country_code VARCHAR(3) DEFAULT 'USA',
            
            -- Geographic boundaries (can use polygon data or simple bounds)
            region_bounds GEOGRAPHY(POLYGON, 4326), -- PostGIS polygon for precise boundaries
            latitude_range NUMRANGE,
            longitude_range NUMRANGE,
            
            -- Adaptation ratings
            adaptation_score INTEGER CHECK (adaptation_score >= 1 AND adaptation_score <= 10),
            production_potential VARCHAR(20) CHECK (production_potential IN ('poor', 'fair', 'good', 'excellent')),
            risk_level VARCHAR(20) CHECK (risk_level IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
            
            -- Regional characteristics
            typical_planting_dates JSONB, -- Flexible date ranges by practice
            typical_harvest_dates JSONB,
            common_varieties TEXT[],
            regional_challenges TEXT[],
            management_considerations TEXT[],
            
            -- Economic factors
            market_demand VARCHAR(20) CHECK (market_demand IN ('very_low', 'low', 'moderate', 'high', 'very_high')),
            infrastructure_support VARCHAR(20) CHECK (infrastructure_support IN ('poor', 'fair', 'good', 'excellent')),
            
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Created crop_regional_adaptations table';
        
        -- Crop filtering and search attributes
        CREATE TABLE crop_filtering_attributes (
            filter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            crop_id UUID NOT NULL REFERENCES crops(crop_id) ON DELETE CASCADE,
            
            -- Seasonality attributes
            planting_season TEXT[] DEFAULT ARRAY['spring'], -- spring, summer, fall, winter
            growing_season TEXT[] DEFAULT ARRAY['summer'], -- primary growing seasons
            harvest_season TEXT[] DEFAULT ARRAY['fall'],
            
            -- Agricultural system compatibility
            farming_systems TEXT[] DEFAULT ARRAY['conventional'], -- conventional, organic, sustainable, no-till, etc.
            rotation_compatibility TEXT[], -- crops this works well with in rotation
            intercropping_compatible BOOLEAN DEFAULT false,
            cover_crop_compatible BOOLEAN DEFAULT true,
            
            -- Management intensity
            management_complexity VARCHAR(20) CHECK (management_complexity IN ('low', 'moderate', 'high')),
            input_requirements VARCHAR(20) CHECK (input_requirements IN ('minimal', 'moderate', 'intensive')),
            labor_requirements VARCHAR(20) CHECK (labor_requirements IN ('low', 'moderate', 'high')),
            
            -- Technology compatibility
            precision_ag_compatible BOOLEAN DEFAULT true,
            gps_guidance_recommended BOOLEAN DEFAULT false,
            sensor_monitoring_beneficial BOOLEAN DEFAULT false,
            
            -- Sustainability attributes
            carbon_sequestration_potential VARCHAR(20) CHECK (carbon_sequestration_potential IN ('none', 'low', 'moderate', 'high')),
            biodiversity_support VARCHAR(20) CHECK (biodiversity_support IN ('low', 'moderate', 'high')),
            pollinator_value VARCHAR(20) CHECK (pollinator_value IN ('none', 'low', 'moderate', 'high')),
            water_use_efficiency VARCHAR(20) CHECK (water_use_efficiency IN ('poor', 'fair', 'good', 'excellent')),
            
            -- Market and economic attributes
            market_stability VARCHAR(20) CHECK (market_stability IN ('volatile', 'moderate', 'stable')),
            price_premium_potential BOOLEAN DEFAULT false,
            value_added_opportunities TEXT[],

            -- Advanced filtering attributes
            pest_resistance_traits JSONB DEFAULT '{}'::jsonb,
            market_class_filters JSONB DEFAULT '{}'::jsonb,
            certification_filters JSONB DEFAULT '{}'::jsonb,
            seed_availability_filters JSONB DEFAULT '{}'::jsonb,

            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        RAISE NOTICE 'Created crop_filtering_attributes table';
        
        RAISE NOTICE 'All taxonomy tables created successfully';
    ELSE
        RAISE NOTICE 'Crop taxonomy tables already exist, skipping table creation';
    END IF;
END
$$;

-- Ensure advanced filtering attribute columns exist on crop_filtering_attributes
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'crop_filtering_attributes' AND table_schema = 'public'
    ) THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'crop_filtering_attributes' 
                AND column_name = 'pest_resistance_traits'
        ) THEN
            ALTER TABLE crop_filtering_attributes 
                ADD COLUMN pest_resistance_traits JSONB DEFAULT '{}'::jsonb;
            RAISE NOTICE 'Added pest_resistance_traits column to crop_filtering_attributes';
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'crop_filtering_attributes' 
                AND column_name = 'market_class_filters'
        ) THEN
            ALTER TABLE crop_filtering_attributes 
                ADD COLUMN market_class_filters JSONB DEFAULT '{}'::jsonb;
            RAISE NOTICE 'Added market_class_filters column to crop_filtering_attributes';
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'crop_filtering_attributes' 
                AND column_name = 'certification_filters'
        ) THEN
            ALTER TABLE crop_filtering_attributes 
                ADD COLUMN certification_filters JSONB DEFAULT '{}'::jsonb;
            RAISE NOTICE 'Added certification_filters column to crop_filtering_attributes';
        END IF;

        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'crop_filtering_attributes' 
                AND column_name = 'seed_availability_filters'
        ) THEN
            ALTER TABLE crop_filtering_attributes 
                ADD COLUMN seed_availability_filters JSONB DEFAULT '{}'::jsonb;
            RAISE NOTICE 'Added seed_availability_filters column to crop_filtering_attributes';
        END IF;
    END IF;
END
$$;

-- ============================================================================
-- UPDATE EXISTING CROPS TABLE TO REFERENCE NEW TAXONOMY SYSTEM
-- ============================================================================

-- Add foreign key relationships to existing crops table
DO $$
BEGIN
    -- Add new columns if they don't exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'taxonomy_id') THEN
        ALTER TABLE crops ADD COLUMN taxonomy_id UUID REFERENCES crop_taxonomic_hierarchy(taxonomy_id);
        RAISE NOTICE 'Added taxonomy_id column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'agricultural_classification_id') THEN
        ALTER TABLE crops ADD COLUMN agricultural_classification_id UUID REFERENCES crop_agricultural_classification(classification_id);
        RAISE NOTICE 'Added agricultural_classification_id column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'climate_adaptation_id') THEN
        ALTER TABLE crops ADD COLUMN climate_adaptation_id UUID REFERENCES crop_climate_adaptations(adaptation_id);
        RAISE NOTICE 'Added climate_adaptation_id column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'soil_requirements_id') THEN
        ALTER TABLE crops ADD COLUMN soil_requirements_id UUID REFERENCES crop_soil_requirements(soil_req_id);
        RAISE NOTICE 'Added soil_requirements_id column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'nutritional_profile_id') THEN
        ALTER TABLE crops ADD COLUMN nutritional_profile_id UUID REFERENCES crop_nutritional_profiles(nutrition_id);
        RAISE NOTICE 'Added nutritional_profile_id column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'filtering_attributes_id') THEN
        ALTER TABLE crops ADD COLUMN filtering_attributes_id UUID REFERENCES crop_filtering_attributes(filter_id);
        RAISE NOTICE 'Added filtering_attributes_id column to crops table';
    END IF;
END
$$;

-- Add enhanced search and classification fields
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'crop_code') THEN
        ALTER TABLE crops ADD COLUMN crop_code VARCHAR(20) UNIQUE;
        RAISE NOTICE 'Added crop_code column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'fao_crop_code') THEN
        ALTER TABLE crops ADD COLUMN fao_crop_code VARCHAR(10);
        RAISE NOTICE 'Added fao_crop_code column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'usda_crop_code') THEN
        ALTER TABLE crops ADD COLUMN usda_crop_code VARCHAR(10);
        RAISE NOTICE 'Added usda_crop_code column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'search_keywords') THEN
        ALTER TABLE crops ADD COLUMN search_keywords TEXT[];
        RAISE NOTICE 'Added search_keywords column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'tags') THEN
        ALTER TABLE crops ADD COLUMN tags TEXT[];
        RAISE NOTICE 'Added tags column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'is_cover_crop') THEN
        ALTER TABLE crops ADD COLUMN is_cover_crop BOOLEAN DEFAULT false;
        RAISE NOTICE 'Added is_cover_crop column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'is_companion_crop') THEN
        ALTER TABLE crops ADD COLUMN is_companion_crop BOOLEAN DEFAULT false;
        RAISE NOTICE 'Added is_companion_crop column to crops table';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'crops' AND column_name = 'crop_status') THEN
        ALTER TABLE crops ADD COLUMN crop_status VARCHAR(20) DEFAULT 'active' CHECK (crop_status IN ('active', 'deprecated', 'experimental', 'regional'));
        RAISE NOTICE 'Added crop_status column to crops table';
    END IF;
END
$$;

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

DO $$
BEGIN
    -- Taxonomic hierarchy indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crop_taxonomy_family') THEN
        CREATE INDEX idx_crop_taxonomy_family ON crop_taxonomic_hierarchy(family);
        RAISE NOTICE 'Created index idx_crop_taxonomy_family';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crop_taxonomy_genus') THEN
        CREATE INDEX idx_crop_taxonomy_genus ON crop_taxonomic_hierarchy(genus);
        RAISE NOTICE 'Created index idx_crop_taxonomy_genus';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crop_taxonomy_species') THEN
        CREATE INDEX idx_crop_taxonomy_species ON crop_taxonomic_hierarchy(species);
        RAISE NOTICE 'Created index idx_crop_taxonomy_species';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crop_taxonomy_full_name') THEN
        CREATE INDEX idx_crop_taxonomy_full_name ON crop_taxonomic_hierarchy(genus, species);
        RAISE NOTICE 'Created index idx_crop_taxonomy_full_name';
    END IF;
    
    -- Agricultural classification indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_ag_classification_category') THEN
        CREATE INDEX idx_ag_classification_category ON crop_agricultural_classification(crop_category);
        RAISE NOTICE 'Created index idx_ag_classification_category';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_ag_classification_use') THEN
        CREATE INDEX idx_ag_classification_use ON crop_agricultural_classification(primary_use);
        RAISE NOTICE 'Created index idx_ag_classification_use';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_ag_classification_habit') THEN
        CREATE INDEX idx_ag_classification_habit ON crop_agricultural_classification(growth_habit);
        RAISE NOTICE 'Created index idx_ag_classification_habit';
    END IF;
    
    -- Enhanced crops table indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_taxonomy_id') THEN
        CREATE INDEX idx_crops_taxonomy_id ON crops(taxonomy_id);
        RAISE NOTICE 'Created index idx_crops_taxonomy_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_agricultural_classification') THEN
        CREATE INDEX idx_crops_agricultural_classification ON crops(agricultural_classification_id);
        RAISE NOTICE 'Created index idx_crops_agricultural_classification';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_climate_adaptation') THEN
        CREATE INDEX idx_crops_climate_adaptation ON crops(climate_adaptation_id);
        RAISE NOTICE 'Created index idx_crops_climate_adaptation';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_filtering_attributes') THEN
        CREATE INDEX idx_crops_filtering_attributes ON crops(filtering_attributes_id);
        RAISE NOTICE 'Created index idx_crops_filtering_attributes';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_code') THEN
        CREATE INDEX idx_crops_code ON crops(crop_code);
        RAISE NOTICE 'Created index idx_crops_code';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_tags') THEN
        CREATE INDEX idx_crops_tags ON crops USING GIN(tags);
        RAISE NOTICE 'Created index idx_crops_tags';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_keywords') THEN
        CREATE INDEX idx_crops_keywords ON crops USING GIN(search_keywords);
        RAISE NOTICE 'Created index idx_crops_keywords';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_cover_crop') THEN
        CREATE INDEX idx_crops_cover_crop ON crops(is_cover_crop);
        RAISE NOTICE 'Created index idx_crops_cover_crop';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_crops_status') THEN
        CREATE INDEX idx_crops_status ON crops(crop_status);
        RAISE NOTICE 'Created index idx_crops_status';
    END IF;
    
    -- Climate adaptation indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_climate_hardiness_zones') THEN
        CREATE INDEX idx_climate_hardiness_zones ON crop_climate_adaptations USING GIN(hardiness_zones);
        RAISE NOTICE 'Created index idx_climate_hardiness_zones';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_climate_temp_range') THEN
        CREATE INDEX idx_climate_temp_range ON crop_climate_adaptations(optimal_temp_min_f, optimal_temp_max_f);
        RAISE NOTICE 'Created index idx_climate_temp_range';
    END IF;
    
    -- Soil requirements indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_soil_ph_range') THEN
        CREATE INDEX idx_soil_ph_range ON crop_soil_requirements(optimal_ph_min, optimal_ph_max);
        RAISE NOTICE 'Created index idx_soil_ph_range';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_soil_drainage') THEN
        CREATE INDEX idx_soil_drainage ON crop_soil_requirements(drainage_requirement);
        RAISE NOTICE 'Created index idx_soil_drainage';
    END IF;
    
    -- Enhanced varieties indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_enhanced_varieties_crop_id') THEN
        CREATE INDEX idx_enhanced_varieties_crop_id ON enhanced_crop_varieties(crop_id);
        RAISE NOTICE 'Created index idx_enhanced_varieties_crop_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_enhanced_varieties_active') THEN
        CREATE INDEX idx_enhanced_varieties_active ON enhanced_crop_varieties(is_active);
        RAISE NOTICE 'Created index idx_enhanced_varieties_active';
    END IF;
    
    -- Regional adaptations indexes
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_regional_adaptations_crop_id') THEN
        CREATE INDEX idx_regional_adaptations_crop_id ON crop_regional_adaptations(crop_id);
        RAISE NOTICE 'Created index idx_regional_adaptations_crop_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_regional_adaptations_region') THEN
        CREATE INDEX idx_regional_adaptations_region ON crop_regional_adaptations(region_name, region_type);
        RAISE NOTICE 'Created index idx_regional_adaptations_region';
    END IF;
    
    -- Filtering attributes indexes  
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_filtering_crop_id') THEN
        CREATE INDEX idx_filtering_crop_id ON crop_filtering_attributes(crop_id);
        RAISE NOTICE 'Created index idx_filtering_crop_id';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_filtering_seasons') THEN
        CREATE INDEX idx_filtering_seasons ON crop_filtering_attributes USING GIN(planting_season);
        RAISE NOTICE 'Created index idx_filtering_seasons';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_filtering_systems') THEN
        CREATE INDEX idx_filtering_systems ON crop_filtering_attributes USING GIN(farming_systems);
        RAISE NOTICE 'Created index idx_filtering_systems';
    END IF;
END
$$;

-- ============================================================================
-- CREATE TRIGGERS FOR MAINTAINING DATA INTEGRITY
-- ============================================================================

DO $$
BEGIN
    -- Update timestamp triggers for new tables (reuse existing function)
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_crop_taxonomic_hierarchy_updated_at') THEN
        CREATE TRIGGER update_crop_taxonomic_hierarchy_updated_at 
            BEFORE UPDATE ON crop_taxonomic_hierarchy
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_crop_taxonomic_hierarchy_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_crop_agricultural_classification_updated_at') THEN
        CREATE TRIGGER update_crop_agricultural_classification_updated_at 
            BEFORE UPDATE ON crop_agricultural_classification
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_crop_agricultural_classification_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_crop_climate_adaptations_updated_at') THEN
        CREATE TRIGGER update_crop_climate_adaptations_updated_at 
            BEFORE UPDATE ON crop_climate_adaptations
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_crop_climate_adaptations_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_crop_soil_requirements_updated_at') THEN
        CREATE TRIGGER update_crop_soil_requirements_updated_at 
            BEFORE UPDATE ON crop_soil_requirements
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_crop_soil_requirements_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_crop_nutritional_profiles_updated_at') THEN
        CREATE TRIGGER update_crop_nutritional_profiles_updated_at 
            BEFORE UPDATE ON crop_nutritional_profiles
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_crop_nutritional_profiles_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_enhanced_crop_varieties_updated_at') THEN
        CREATE TRIGGER update_enhanced_crop_varieties_updated_at 
            BEFORE UPDATE ON enhanced_crop_varieties
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_enhanced_crop_varieties_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_crop_regional_adaptations_updated_at') THEN
        CREATE TRIGGER update_crop_regional_adaptations_updated_at 
            BEFORE UPDATE ON crop_regional_adaptations
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_crop_regional_adaptations_updated_at';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_crop_filtering_attributes_updated_at') THEN
        CREATE TRIGGER update_crop_filtering_attributes_updated_at 
            BEFORE UPDATE ON crop_filtering_attributes
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        RAISE NOTICE 'Created trigger update_crop_filtering_attributes_updated_at';
    END IF;
END
$$;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 003_create_crop_taxonomy_system completed successfully';
    RAISE NOTICE 'Crop taxonomy system is ready for data population and service implementation';
END
$$;
