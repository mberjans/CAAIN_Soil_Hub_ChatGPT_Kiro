-- Enhanced Crop Taxonomy Database Schema
-- Extends the existing crops table with comprehensive taxonomic classification
-- Version: 1.0 for TICKET-005 Crop Type Filtering Implementation

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

-- ============================================================================
-- UPDATE EXISTING CROPS TABLE TO REFERENCE NEW TAXONOMY SYSTEM
-- ============================================================================

-- Add foreign key relationships to existing crops table
ALTER TABLE crops ADD COLUMN IF NOT EXISTS taxonomy_id UUID REFERENCES crop_taxonomic_hierarchy(taxonomy_id);
ALTER TABLE crops ADD COLUMN IF NOT EXISTS agricultural_classification_id UUID REFERENCES crop_agricultural_classification(classification_id);
ALTER TABLE crops ADD COLUMN IF NOT EXISTS climate_adaptation_id UUID REFERENCES crop_climate_adaptations(adaptation_id);
ALTER TABLE crops ADD COLUMN IF NOT EXISTS soil_requirements_id UUID REFERENCES crop_soil_requirements(soil_req_id);
ALTER TABLE crops ADD COLUMN IF NOT EXISTS nutritional_profile_id UUID REFERENCES crop_nutritional_profiles(nutrition_id);
ALTER TABLE crops ADD COLUMN IF NOT EXISTS filtering_attributes_id UUID REFERENCES crop_filtering_attributes(filter_id);

-- Add enhanced search and classification fields to crops table
ALTER TABLE crops ADD COLUMN IF NOT EXISTS crop_code VARCHAR(20) UNIQUE;
ALTER TABLE crops ADD COLUMN IF NOT EXISTS fao_crop_code VARCHAR(10); -- FAO crop classification codes
ALTER TABLE crops ADD COLUMN IF NOT EXISTS usda_crop_code VARCHAR(10); -- USDA NASS crop codes
ALTER TABLE crops ADD COLUMN IF NOT EXISTS search_keywords TEXT[];
ALTER TABLE crops ADD COLUMN IF NOT EXISTS tags TEXT[];
ALTER TABLE crops ADD COLUMN IF NOT EXISTS is_cover_crop BOOLEAN DEFAULT false;
ALTER TABLE crops ADD COLUMN IF NOT EXISTS is_companion_crop BOOLEAN DEFAULT false;
ALTER TABLE crops ADD COLUMN IF NOT EXISTS crop_status VARCHAR(20) DEFAULT 'active' CHECK (crop_status IN ('active', 'deprecated', 'experimental', 'regional'));

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Taxonomic hierarchy indexes
CREATE INDEX idx_crop_taxonomy_family ON crop_taxonomic_hierarchy(family);
CREATE INDEX idx_crop_taxonomy_genus ON crop_taxonomic_hierarchy(genus);
CREATE INDEX idx_crop_taxonomy_species ON crop_taxonomic_hierarchy(species);
CREATE INDEX idx_crop_taxonomy_full_name ON crop_taxonomic_hierarchy(genus, species);

-- Agricultural classification indexes
CREATE INDEX idx_ag_classification_category ON crop_agricultural_classification(crop_category);
CREATE INDEX idx_ag_classification_use ON crop_agricultural_classification(primary_use);
CREATE INDEX idx_ag_classification_habit ON crop_agricultural_classification(growth_habit);
CREATE INDEX idx_ag_classification_type ON crop_agricultural_classification(plant_type);

-- Climate adaptation indexes
CREATE INDEX idx_climate_hardiness_zones ON crop_climate_adaptations USING GIN(hardiness_zones);
CREATE INDEX idx_climate_temp_range ON crop_climate_adaptations(optimal_temp_min_f, optimal_temp_max_f);
CREATE INDEX idx_climate_precipitation ON crop_climate_adaptations(annual_precipitation_min_inches, annual_precipitation_max_inches);
CREATE INDEX idx_climate_drought_tolerance ON crop_climate_adaptations(drought_tolerance);

-- Soil requirements indexes
CREATE INDEX idx_soil_ph_range ON crop_soil_requirements(optimal_ph_min, optimal_ph_max);
CREATE INDEX idx_soil_drainage ON crop_soil_requirements(drainage_requirement);
CREATE INDEX idx_soil_textures ON crop_soil_requirements USING GIN(preferred_textures);

-- Enhanced varieties indexes
CREATE INDEX idx_enhanced_varieties_crop_id ON enhanced_crop_varieties(crop_id);
CREATE INDEX idx_enhanced_varieties_maturity ON enhanced_crop_varieties(relative_maturity);
CREATE INDEX idx_enhanced_varieties_active ON enhanced_crop_varieties(is_active);
CREATE INDEX idx_enhanced_varieties_regions ON enhanced_crop_varieties USING GIN(adapted_regions);

-- Regional adaptations indexes
CREATE INDEX idx_regional_adaptations_crop_id ON crop_regional_adaptations(crop_id);
CREATE INDEX idx_regional_adaptations_region ON crop_regional_adaptations(region_name, region_type);
CREATE INDEX idx_regional_adaptations_bounds ON crop_regional_adaptations USING GIST(region_bounds);
CREATE INDEX idx_regional_adaptations_score ON crop_regional_adaptations(adaptation_score);

-- Filtering attributes indexes
CREATE INDEX idx_filtering_crop_id ON crop_filtering_attributes(crop_id);
CREATE INDEX idx_filtering_seasons ON crop_filtering_attributes USING GIN(planting_season);
CREATE INDEX idx_filtering_systems ON crop_filtering_attributes USING GIN(farming_systems);
CREATE INDEX idx_filtering_complexity ON crop_filtering_attributes(management_complexity);

-- Enhanced crops table indexes
CREATE INDEX idx_crops_taxonomy_id ON crops(taxonomy_id);
CREATE INDEX idx_crops_agricultural_classification ON crops(agricultural_classification_id);
CREATE INDEX idx_crops_climate_adaptation ON crops(climate_adaptation_id);
CREATE INDEX idx_crops_filtering_attributes ON crops(filtering_attributes_id);
CREATE INDEX idx_crops_code ON crops(crop_code);
CREATE INDEX idx_crops_tags ON crops USING GIN(tags);
CREATE INDEX idx_crops_keywords ON crops USING GIN(search_keywords);
CREATE INDEX idx_crops_cover_crop ON crops(is_cover_crop);
CREATE INDEX idx_crops_status ON crops(crop_status);

-- Full-text search indexes for enhanced search capabilities
CREATE INDEX idx_crop_taxonomy_name_search ON crop_taxonomic_hierarchy USING gin(
    (genus || ' ' || species) gin_trgm_ops
);
CREATE INDEX idx_enhanced_varieties_name_search ON enhanced_crop_varieties USING gin(
    variety_name gin_trgm_ops
);

-- ============================================================================
-- TRIGGERS FOR MAINTAINING DATA INTEGRITY
-- ============================================================================

-- Update timestamp triggers for new tables
CREATE TRIGGER update_crop_taxonomic_hierarchy_updated_at 
    BEFORE UPDATE ON crop_taxonomic_hierarchy
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crop_agricultural_classification_updated_at 
    BEFORE UPDATE ON crop_agricultural_classification
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crop_climate_adaptations_updated_at 
    BEFORE UPDATE ON crop_climate_adaptations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crop_soil_requirements_updated_at 
    BEFORE UPDATE ON crop_soil_requirements
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crop_nutritional_profiles_updated_at 
    BEFORE UPDATE ON crop_nutritional_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enhanced_crop_varieties_updated_at 
    BEFORE UPDATE ON enhanced_crop_varieties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crop_regional_adaptations_updated_at 
    BEFORE UPDATE ON crop_regional_adaptations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_crop_filtering_attributes_updated_at 
    BEFORE UPDATE ON crop_filtering_attributes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- VIEWS FOR COMMON CROP TAXONOMY QUERIES
-- ============================================================================

-- Comprehensive crop view with all taxonomy data
CREATE VIEW comprehensive_crop_view AS
SELECT 
    c.crop_id,
    c.crop_name,
    c.scientific_name,
    c.crop_category,
    c.crop_family,
    c.crop_code,
    c.fao_crop_code,
    c.usda_crop_code,
    c.search_keywords,
    c.tags,
    c.is_cover_crop,
    c.is_companion_crop,
    c.crop_status,
    
    -- Taxonomic hierarchy
    th.kingdom,
    th.phylum,
    th.class,
    th.order_name,
    th.family,
    th.genus,
    th.species,
    th.subspecies,
    th.variety as botanical_variety,
    th.cultivar,
    th.common_synonyms,
    
    -- Agricultural classification
    ac.crop_subcategory,
    ac.primary_use,
    ac.secondary_uses,
    ac.growth_habit,
    ac.plant_type,
    ac.growth_form,
    ac.mature_height_min_inches,
    ac.mature_height_max_inches,
    ac.photosynthesis_type,
    ac.nitrogen_fixing,
    
    -- Climate adaptations
    ca.hardiness_zones,
    ca.optimal_temp_min_f,
    ca.optimal_temp_max_f,
    ca.drought_tolerance,
    ca.heat_tolerance,
    ca.frost_tolerance,
    ca.photoperiod_sensitivity,
    
    -- Soil requirements
    sr.optimal_ph_min,
    sr.optimal_ph_max,
    sr.preferred_textures,
    sr.drainage_requirement,
    sr.salinity_tolerance,
    
    -- Filtering attributes
    fa.planting_season,
    fa.growing_season,
    fa.harvest_season,
    fa.farming_systems,
    fa.management_complexity,
    fa.carbon_sequestration_potential,
    fa.pollinator_value,
    fa.water_use_efficiency
    
FROM crops c
LEFT JOIN crop_taxonomic_hierarchy th ON c.taxonomy_id = th.taxonomy_id
LEFT JOIN crop_agricultural_classification ac ON c.agricultural_classification_id = ac.classification_id
LEFT JOIN crop_climate_adaptations ca ON c.climate_adaptation_id = ca.adaptation_id
LEFT JOIN crop_soil_requirements sr ON c.soil_requirements_id = sr.soil_req_id
LEFT JOIN crop_filtering_attributes fa ON c.filtering_attributes_id = fa.filter_id
WHERE c.crop_status = 'active';

-- Crop varieties with enhanced details
CREATE VIEW enhanced_crop_varieties_view AS
SELECT 
    ev.variety_id,
    ev.variety_name,
    ev.variety_code,
    ev.breeder_company,
    ev.relative_maturity,
    ev.maturity_group,
    ev.yield_potential_percentile,
    ev.disease_resistances,
    ev.herbicide_tolerances,
    ev.adapted_regions,
    ev.seed_availability,
    ev.relative_seed_cost,
    ev.organic_approved,
    ev.non_gmo_certified,
    ev.is_active,
    
    -- Crop information
    c.crop_name,
    c.scientific_name,
    c.crop_category,
    
    -- Taxonomic information
    th.genus,
    th.species
    
FROM enhanced_crop_varieties ev
JOIN crops c ON ev.crop_id = c.crop_id
LEFT JOIN crop_taxonomic_hierarchy th ON c.taxonomy_id = th.taxonomy_id
WHERE ev.is_active = true AND c.crop_status = 'active';

-- Regional crop suitability view
CREATE VIEW regional_crop_suitability_view AS
SELECT 
    cra.adaptation_id,
    cra.region_name,
    cra.region_type,
    cra.adaptation_score,
    cra.production_potential,
    cra.risk_level,
    cra.typical_planting_dates,
    cra.typical_harvest_dates,
    cra.common_varieties,
    cra.market_demand,
    
    -- Crop details
    c.crop_id,
    c.crop_name,
    c.crop_category,
    ac.primary_use,
    ac.growth_habit,
    
    -- Climate requirements
    ca.hardiness_zones,
    ca.drought_tolerance,
    ca.heat_tolerance
    
FROM crop_regional_adaptations cra
JOIN crops c ON cra.crop_id = c.crop_id
LEFT JOIN crop_agricultural_classification ac ON c.agricultural_classification_id = ac.classification_id
LEFT JOIN crop_climate_adaptations ca ON c.climate_adaptation_id = ca.adaptation_id
WHERE c.crop_status = 'active'
ORDER BY cra.region_name, cra.adaptation_score DESC;

-- ============================================================================
-- FUNCTIONS FOR CROP TAXONOMY OPERATIONS
-- ============================================================================

-- Function to search crops by multiple criteria with ranking
CREATE OR REPLACE FUNCTION search_crops_advanced(
    search_text TEXT DEFAULT NULL,
    category_filter TEXT DEFAULT NULL,
    hardiness_zone_filter TEXT DEFAULT NULL,
    drought_tolerance_filter TEXT DEFAULT NULL,
    planting_season_filter TEXT DEFAULT NULL,
    growth_habit_filter TEXT DEFAULT NULL,
    limit_results INTEGER DEFAULT 50
)
RETURNS TABLE (
    crop_id UUID,
    crop_name VARCHAR,
    scientific_name VARCHAR,
    relevance_score NUMERIC,
    category VARCHAR,
    hardiness_zones TEXT[],
    drought_tolerance VARCHAR,
    planting_seasons TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.crop_id,
        c.crop_name,
        c.scientific_name,
        -- Calculate relevance score based on text matching and filter alignment
        (
            CASE WHEN search_text IS NULL THEN 1.0
                 WHEN c.crop_name ILIKE '%' || search_text || '%' THEN 2.0
                 WHEN c.scientific_name ILIKE '%' || search_text || '%' THEN 1.8
                 WHEN EXISTS(SELECT 1 FROM unnest(c.search_keywords) AS kw WHERE kw ILIKE '%' || search_text || '%') THEN 1.5
                 WHEN EXISTS(SELECT 1 FROM unnest(c.tags) AS tag WHERE tag ILIKE '%' || search_text || '%') THEN 1.3
                 ELSE 0.0
            END +
            CASE WHEN category_filter IS NULL OR c.crop_category = category_filter THEN 0.5 ELSE 0.0 END +
            CASE WHEN hardiness_zone_filter IS NULL OR 
                      (ca.hardiness_zones IS NOT NULL AND hardiness_zone_filter = ANY(ca.hardiness_zones)) THEN 0.3 ELSE 0.0 END
        )::NUMERIC AS relevance_score,
        c.crop_category::VARCHAR,
        ca.hardiness_zones,
        ca.drought_tolerance::VARCHAR,
        fa.planting_season
    FROM crops c
    LEFT JOIN crop_climate_adaptations ca ON c.climate_adaptation_id = ca.adaptation_id
    LEFT JOIN crop_agricultural_classification ac ON c.agricultural_classification_id = ac.classification_id
    LEFT JOIN crop_filtering_attributes fa ON c.filtering_attributes_id = fa.filter_id
    WHERE c.crop_status = 'active'
      AND (category_filter IS NULL OR c.crop_category = category_filter)
      AND (hardiness_zone_filter IS NULL OR 
           (ca.hardiness_zones IS NOT NULL AND hardiness_zone_filter = ANY(ca.hardiness_zones)))
      AND (drought_tolerance_filter IS NULL OR ca.drought_tolerance = drought_tolerance_filter)
      AND (planting_season_filter IS NULL OR 
           (fa.planting_season IS NOT NULL AND planting_season_filter = ANY(fa.planting_season)))
      AND (growth_habit_filter IS NULL OR ac.growth_habit = growth_habit_filter)
      AND (search_text IS NULL OR 
           c.crop_name ILIKE '%' || search_text || '%' OR
           c.scientific_name ILIKE '%' || search_text || '%' OR
           EXISTS(SELECT 1 FROM unnest(c.search_keywords) AS kw WHERE kw ILIKE '%' || search_text || '%') OR
           EXISTS(SELECT 1 FROM unnest(c.tags) AS tag WHERE tag ILIKE '%' || search_text || '%'))
    ORDER BY relevance_score DESC, c.crop_name
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- Function to get crop compatibility for rotation planning
CREATE OR REPLACE FUNCTION get_crop_rotation_compatibility(
    primary_crop_id UUID,
    region_name_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    compatible_crop_id UUID,
    compatible_crop_name VARCHAR,
    compatibility_type VARCHAR,
    benefits TEXT[],
    considerations TEXT[]
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c2.crop_id,
        c2.crop_name,
        CASE 
            WHEN ac1.nitrogen_fixing = true AND ac2.nitrogen_fixing = false THEN 'nitrogen_provider'
            WHEN ac1.nitrogen_fixing = false AND ac2.nitrogen_fixing = true THEN 'nitrogen_recipient'
            WHEN ac1.crop_category != ac2.crop_category THEN 'diversification'
            ELSE 'general_compatibility'
        END::VARCHAR as compatibility_type,
        ARRAY[
            CASE WHEN ac1.nitrogen_fixing = true THEN 'provides nitrogen fixation' END,
            CASE WHEN fa2.carbon_sequestration_potential IN ('moderate', 'high') THEN 'builds soil carbon' END,
            CASE WHEN fa2.pollinator_value IN ('moderate', 'high') THEN 'supports pollinators' END
        ]::TEXT[] as benefits,
        ARRAY[
            CASE WHEN sr1.drainage_requirement != sr2.drainage_requirement THEN 'different drainage needs' END,
            CASE WHEN ABS(sr1.optimal_ph_min - sr2.optimal_ph_min) > 1.0 THEN 'different pH preferences' END
        ]::TEXT[] as considerations
    FROM crops c1
    JOIN crop_agricultural_classification ac1 ON c1.agricultural_classification_id = ac1.classification_id
    JOIN crop_soil_requirements sr1 ON c1.soil_requirements_id = sr1.soil_req_id
    JOIN crop_filtering_attributes fa1 ON c1.filtering_attributes_id = fa1.filter_id
    CROSS JOIN crops c2
    JOIN crop_agricultural_classification ac2 ON c2.agricultural_classification_id = ac2.classification_id
    JOIN crop_soil_requirements sr2 ON c2.soil_requirements_id = sr2.soil_req_id
    JOIN crop_filtering_attributes fa2 ON c2.filtering_attributes_id = fa2.filter_id
    WHERE c1.crop_id = primary_crop_id
      AND c2.crop_id != primary_crop_id
      AND c1.crop_status = 'active'
      AND c2.crop_status = 'active'
      -- Basic compatibility criteria
      AND NOT (ac1.crop_category = ac2.crop_category AND ac1.crop_category IN ('grain', 'oilseed'))
      AND ABS(sr1.optimal_ph_min - sr2.optimal_ph_min) <= 1.5
      AND (region_name_filter IS NULL OR 
           EXISTS(SELECT 1 FROM crop_regional_adaptations cra 
                  WHERE cra.crop_id = c2.crop_id 
                    AND cra.region_name = region_name_filter 
                    AND cra.adaptation_score >= 6))
    ORDER BY compatibility_type, c2.crop_name;
END;
$$ LANGUAGE plpgsql;

-- Grant appropriate permissions
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO afas_app;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO afas_app;

COMMENT ON SCHEMA public IS 'Enhanced crop taxonomy system supporting comprehensive filtering and agricultural decision-making';
