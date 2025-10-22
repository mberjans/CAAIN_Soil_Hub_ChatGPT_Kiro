-- Ensure PostGIS extension is enabled
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create farm_locations table
CREATE TABLE IF NOT EXISTS farm_locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    name VARCHAR(200) NOT NULL,
    address TEXT,
    coordinates GEOMETRY(POINT, 4326) NOT NULL,
    elevation_meters INTEGER,
    usda_zone VARCHAR(10),
    climate_zone VARCHAR(50),
    county VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'USA',
    total_acres DECIMAL(10,2),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create spatial index on coordinates
CREATE INDEX IF NOT EXISTS idx_farm_locations_coordinates ON farm_locations USING GIST(coordinates);
CREATE INDEX IF NOT EXISTS idx_farm_locations_user_id ON farm_locations(user_id);
CREATE INDEX IF NOT EXISTS idx_farm_locations_usda_zone ON farm_locations(usda_zone);

-- Create fields table
CREATE TABLE IF NOT EXISTS fields (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    farm_location_id UUID REFERENCES farm_locations(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    boundary GEOMETRY(POLYGON, 4326),
    acres DECIMAL(8,2) NOT NULL,
    soil_type VARCHAR(100),
    drainage_class VARCHAR(50),
    slope_percent DECIMAL(4,1),
    irrigation_available BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create spatial index on field boundaries
CREATE INDEX IF NOT EXISTS idx_fields_boundary ON fields USING GIST(boundary);
CREATE INDEX IF NOT EXISTS idx_fields_farm_location_id ON fields(farm_location_id);

-- Add sample data with PostGIS geometry functions
INSERT INTO farm_locations (
    user_id, 
    name, 
    address, 
    coordinates, 
    elevation_meters, 
    usda_zone, 
    climate_zone, 
    county, 
    state, 
    country, 
    total_acres, 
    is_primary
) VALUES (
    gen_random_uuid(),
    'Test Farm',
    '123 Main Street, Ames, Iowa',
    ST_GeomFromText('POINT(-93.6 42.0)', 4326),
    300,
    '5b',
    'Humid Continental',
    'Story',
    'Iowa',
    'USA',
    100.5,
    TRUE
) ON CONFLICT DO NOTHING;

-- Insert sample fields
INSERT INTO fields (
    farm_location_id,
    name,
    boundary,
    acres,
    soil_type,
    drainage_class,
    slope_percent,
    irrigation_available
)
SELECT 
    f.id,
    'North Field',
    ST_GeomFromText('POLYGON((-93.6 42.0, -93.5 42.0, -93.5 42.1, -93.6 42.1, -93.6 42.0))', 4326),
    25.75,
    'Loam',
    'Well Drained',
    2.5,
    TRUE
FROM farm_locations f 
WHERE f.name = 'Test Farm'
ON CONFLICT DO NOTHING;
