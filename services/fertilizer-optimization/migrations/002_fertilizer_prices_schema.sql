-- Migration: 002_fertilizer_prices_schema.sql
-- Description: Create database schema for fertilizer price tracking
-- Job: JOB2-003.5.impl - Fertilizer Optimization Price Tracking Schema

-- Create fertilizer_types table
CREATE TABLE fertilizer_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create fertilizer_prices table
CREATE TABLE fertilizer_prices (
    id SERIAL PRIMARY KEY,
    fertilizer_type_id INTEGER NOT NULL REFERENCES fertilizer_types(id) ON DELETE CASCADE,
    price NUMERIC(10,2) NOT NULL,
    price_date DATE NOT NULL,
    region VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for foreign keys and commonly queried columns
-- Index for fertilizer_types
CREATE INDEX idx_fertilizer_types_name ON fertilizer_types(name);
CREATE INDEX idx_fertilizer_types_category ON fertilizer_types(category);

-- Index for fertilizer_prices
CREATE INDEX idx_fertilizer_prices_fertilizer_type_id ON fertilizer_prices(fertilizer_type_id);
CREATE INDEX idx_fertilizer_prices_price_date ON fertilizer_prices(price_date);
CREATE INDEX idx_fertilizer_prices_region ON fertilizer_prices(region);
CREATE INDEX idx_fertilizer_prices_source ON fertilizer_prices(source);

-- Composite index for common queries (fertilizer_type_id + price_date + region)
CREATE INDEX idx_fertilizer_prices_composite ON fertilizer_prices(fertilizer_type_id, price_date, region);

-- Add comments for documentation
COMMENT ON TABLE fertilizer_types IS 'Stores different types of fertilizers with their categories and descriptions';
COMMENT ON TABLE fertilizer_prices IS 'Tracks historical fertilizer prices by region and date';

COMMENT ON COLUMN fertilizer_types.name IS 'Unique name of the fertilizer type (e.g., Urea 46-0-0, Ammonium Nitrate)';
COMMENT ON COLUMN fertilizer_types.category IS 'Category of fertilizer (e.g., Nitrogen, Phosphorus, Potassium, Compound)';
COMMENT ON COLUMN fertilizer_prices.price IS 'Price per unit (typically per ton or per bag)';
COMMENT ON COLUMN fertilizer_prices.price_date IS 'Date when the price was recorded';
COMMENT ON COLUMN fertilizer_prices.region IS 'Geographic region for the price (e.g., state, province, market area)';
COMMENT ON COLUMN fertilizer_prices.source IS 'Source of the price data (e.g., USDA, market report, supplier)';

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_fertilizer_types_updated_at 
    BEFORE UPDATE ON fertilizer_types 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_fertilizer_prices_updated_at 
    BEFORE UPDATE ON fertilizer_prices 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Add constraints for data integrity
ALTER TABLE fertilizer_prices ADD CONSTRAINT chk_fertilizer_prices_price_positive 
    CHECK (price > 0);

ALTER TABLE fertilizer_prices ADD CONSTRAINT chk_fertilizer_prices_date_not_future 
    CHECK (price_date <= CURRENT_DATE);

-- Add unique constraint to prevent duplicate price entries for the same fertilizer, date, region, and source
ALTER TABLE fertilizer_prices ADD CONSTRAINT uk_fertilizer_prices_unique 
    UNIQUE (fertilizer_type_id, price_date, region, source);